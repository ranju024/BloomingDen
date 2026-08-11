from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.urls import reverse
from decimal import Decimal, InvalidOperation

from ..decorators import seller_required
from ..forms import SignUpForm, PlantListingForm
from ..models import (OrderItem, Product, Order, Category, Profile, PlantListing, Conversation, Message, Vendor)
from ..cart import Cart

import json
import base64
from ..esewa import build_payment_data, verify_response_signature, ESEWA_FORM_URL

# Create your views here.

def home(request):
    products = Product.objects.filter(status="active")[:8]

    return render(request, "catalog/home.html", {
        "products": products,
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            phone=form.cleaned_data['phone']

            Profile.objects.create(
                user=user,
                role=role,
                phone=phone,
            )

            if role == "seller":
                Vendor.objects.create(
                    user=user,
                    shop_name=f"{user.username}'s Shop",
                    phone=phone,
                )
            auth_login(request, user)
            messages.success(request, "Welcome to BloomingDen!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, "catalog/signup.html", {"form": form})


@require_POST  # reject anything that isn't POST
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        status="active",
    )
    if request.user.profile.role != "buyer":
        messages.error(request, "Only buyers can add products to the cart.")
        return redirect("product_detail", slug=product.slug)

    if product.stock <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect("product_detail", slug=product.slug)

    cart = Cart(request)
    cart.add(product)

    messages.success(request, f"{product.name} added to cart.")
    return redirect("product_detail", slug=product.slug)

def get_cart_data(request):
    """
    Returns cart items and total price.
    This avoids repeating the same code in multiple views.
    """
    cart = Cart(request)

    items = list(cart.get_items())
    total_price = Decimal('0.00')
    for item in items:
        total_price += Decimal(item['price']) * item['quantity']
    return items, total_price

@login_required
def cart_detail(request):
    ''' Display the contents of the shopping cart and calculate total price '''
    if request.user.profile.role != "buyer":
        messages.error(request, "Only buyers can access the cart.")
        return redirect("seller_dashboard")
    
    cart = Cart(request)  # create cart object from session

    items = list(cart.get_items())
    total_price = Decimal('0.00')

    #calculate subtotal for each item
    for item in items:
        item['subtotal'] = Decimal(item['price']) * item['quantity']
        total_price += item['subtotal']

    # Send cart items to template    
    return render(request, "catalog/cart_detail.html", {  
        "items": items,
        "total_price": total_price
        })  

@require_POST
def increase_cart_item(request, key):
    cart = Cart(request)
    cart.increase(key)
    return redirect('cart_detail')

@require_POST
def decrease_cart_item(request, key):
    cart = Cart(request)
    cart.decrease(key)
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, key):
    ''' Remove an item from the cart '''
    cart = Cart(request)
    cart.remove(key)
    return redirect('cart_detail')

@login_required
def checkout(request):
    ''' Handles checkout form submission and creates an order from the current cart'''
    if request.user.profile.role != "buyer":
        messages.error(request, "Only buyers can checkout.")
        return redirect("home")
    
    items, total_price = get_cart_data(request)
    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect('home') # if nth to check out
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not name or not phone or not address:  
            messages.error(request, "Please fill in all delivery details.")
            return render(
                request, 
                "catalog/checkout.html", 
                {"items": items, "total_price": total_price},
            )
        
        with transaction.atomic():
            # Lock the products while checking stock
            product_ids = [item["id"] for item in items]
            products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(
                    id__in=product_ids,
                    status="active",
                )
            }

            # validate every cart item
            for item in items:
                product = products.get(item["id"])
                if not product:
                    messages.error(
                        request,
                        f"{item['name']} is no longer available.",
                    )
                if item["quantity"] > product.stock:
                    messages.error(
                        request, 
                        f"Only {product.stock} unit of "
                        f"{product.name} available.",
                    )
                    return redirect("cart_detail")
                
            calculated_total = Decimal("0.00")
            for item in items:
                product = products[item["id"]]
                calculated_total += (
                    product.price * item["quantity"]
                )


            order = Order.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                address=address,
                total_price=calculated_total, 
                payment_method=payment_method
            )

            # create a permanent record or every purchase product.
            for item in items:
                product = products[item["id"]]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    seller=product.seller,
                    product_name=product.name,
                    quantity=item["quantity"],
                    unit_price=product.price,
                    subtotal=product.price * item["quantity"],
                )

            # COD is considered 'ordered' immediately on checkout
            # Online payments will redice stock after successful payment
            if payment_method == "cod":
                for item in items:
                    product = products[item["id"]]
                    product.stock -= item["quantity"]
                    if product.stock == 0:
                        product.status = "out_of_stock"
                    product.save(
                        update_fields=["stock", "status", "updated_at"]
                    )
                order.order_status = "confirmed"
                order.save(update_fields=["order_status", "updated_at"])

                # cOD order is complete enough to clear the cart now
                request.session["cart"] = {}
                request.session.modified = True

                return redirect(
                    "order_success",
                    order_id=order.id,
                )
            
        # for esewa, we keep the cart until payment succeeds.
        if payment_method == "esewa":
            return redirect(
                "esewa_initiate",
                order_id=order.id,
            )

        #otherwise
        messages.error(request, "Invalid payment method.")
        order.delete() # order not successful so remove it
        return redirect("checkout")
                  
    return render(request, "catalog/checkout.html", {
        "items": items,
        "total_price": total_price
    })


def esewa_initiate(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    success_url = request.build_absolute_uri(reverse('esewa_success'))
    failure_url = request.build_absolute_uri(reverse('payment_failure'))

    payment_data = build_payment_data(order, success_url, failure_url)
    order.transaction_uuid = payment_data['transaction_uuid']
    order.save()

    return render(request, "catalog/esewa_redirect.html", {
        "payment_data": payment_data,
        "esewa_url": ESEWA_FORM_URL,
    })


def finalize_paid_order(order):
    ''' 
    Finalize an order after successful online payment.
    This reduces stock exactly once and marks the order as confirmed.
    '''
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)

        # prevent duplicate stock reduction if the payment callback is received more than once.
        if order.payment_status == 'paid':
            return True
        
        for item in order.items.select_related("product").all():
            product = item.product
            if not product:
                return False
            product = Product.objects.select_for_update().get(pk=product.pk)
            if product.stock < item.quantity:
                return False
            product.stock -= item.quantity
            if product.stock == 0:
                product.status = "out_of_stock"
            product.save(
                update_fields=[
                    "stock",
                    "status",
                    "updated_at",
                ]
            )
        order.payment_status = "paid"
        order.order_status = "confirmed"
        order.save(
            update_fields=[
                "payment_status",
                "order_status",
                "updated_at",
            ]
        )
    return True



def esewa_success(request):
    encoded_data = request.GET.get('data')
    if not encoded_data:
        return redirect('payment_failure')

    try:
        decoded_data = json.loads(base64.b64decode(encoded_data))
    except Exception:
        return redirect('payment_failure')

    if not verify_response_signature(decoded_data):
        messages.error(request, "Payment verification failed. Please contact support.")
        return redirect('payment_failure')

    if decoded_data.get('status') != 'COMPLETE':
        return redirect('payment_failure')

    order = get_object_or_404(Order, transaction_uuid=decoded_data.get('transaction_uuid'))

    # Compare as Decimal values, not strings. This handles "150.0" vs "150.00" vs "1,500.00"
    raw_amount = decoded_data.get('total_amount', '').replace(',', '')
    try:
        returned_amount = Decimal(raw_amount)
    except InvalidOperation:
        returned_amount = None

    if returned_amount != order.total_price:
        messages.error(request, "Payment amount mismatch. Please contact support.")
        return redirect('payment_failure')

    if not finalize_paid_order(order):
        messages.error(
            request,
            "Payment was successful, but the product stock is no longer available. " \
            "\nPlease contact support."
        )
        return redirect("payment_failure")
    
    # payment successful, so now cart is cleared
    request.session["cart"] = {}
    request.session.modified = True

    return redirect('order_success', order_id=order.id)


def payment_failure(request):
    return render(request, "catalog/payment_failure.html")

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "catalog/order_success.html", {"order": order})

def shop(request):
    return render(request, "catalog/shop.html")


def plants_list(request, category_slug=None):
    plants = Plant.objects.all()
    category = None
    subcategories = Category.objects.filter(name="Plants").first()
    subcategories = subcategories.children.all() if subcategories else []

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        plants = plants.filter(category=category)

    return render(request, "catalog/plants_list.html", {
        "plants": plants,
        "category": category,
        "subcategories": subcategories,
    })

def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    return render(request, "catalog/plant_detail.html", {"plant": plant})

def listing_list(request):
    listings = PlantListing.objects.filter(status='available').order_by('-created_at')
    condition = request.GET.get('condition', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if condition:
        listings = listings.filter(condition=condition)

    if min_price:
        try:
            listings = listings.filter(price__gte=Decimal(min_price))
        except InvalidOperation:
            pass

    if max_price:
        try:
            listings = listings.filter(price__lte=Decimal(max_price))
        except InvalidOperation:
            pass

    return render(request, "catalog/listing_list.html", {
        "listings": listings,
        "condition": condition,
        "min_price": min_price,
        "max_price": max_price,
    })

def listing_detail(request, pk):
    listing = get_object_or_404(PlantListing, pk=pk)
    return render(request, "catalog/listing_detail.html", {"listing": listing})


@seller_required
def listing_create(request):
    if request.method == 'POST':
        form = PlantListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user.vendor
            listing.save()
            messages.success(request, "Your plant is now listed!")
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = PlantListingForm()
    return render(request, "catalog/listing_form.html", {"form": form})


@seller_required
def my_listings(request):
    vendor = request.user.vendor
    listings = PlantListing.objects.filter(seller=vendor).order_by('-created_at')
    return render(request, "catalog/my_listings.html", {"listings": listings})


@require_POST
@seller_required
def mark_sold(request, pk):
    vendor = request.user.vendor
    listing = get_object_or_404(PlantListing, pk=pk, seller=vendor)
    listing.status = 'sold'
    listing.save()
    messages.success(request, f"{listing.name} marked as sold.")
    return redirect('my_listings')


@login_required
def start_conversation(request, pk):

    # Only buyers can start a conversation
    if not hasattr(request.user, "profile") or request.user.profile.role != "buyer":
        messages.error(
            request,
            "Only buyers can message sellers."
        )
        return redirect("listing_detail", pk=pk)

    listing = get_object_or_404(
        PlantListing,
        pk=pk,
        status="available"
    )

    # Buyer cannot message themselves
    if hasattr(request.user, "vendor"):
        if listing.seller == request.user.vendor:
            messages.error(
                request,
                "You can't message yourself about your own listing."
            )
            return redirect("listing_detail", pk=pk)

    conversation, created = Conversation.objects.get_or_create(
        listing=listing,
        buyer=request.user,
        defaults={
            "seller": listing.seller,
        }
    )

    return redirect(
        "conversation_detail",
        pk=conversation.pk
    )


@login_required
def conversation_list(request):

    if not hasattr(request.user, "profile"):
        return redirect("home")

    if request.user.profile.role == "buyer":

        conversations = Conversation.objects.filter(
            buyer=request.user
        ).order_by("-created_at")

    elif request.user.profile.role == "seller":

        vendor = Vendor.objects.filter(
            user=request.user
        ).first()

        if not vendor:
            messages.error(
                request,
                "Your seller account is not set up yet."
            )
            return redirect("home")

        conversations = Conversation.objects.filter(
            seller=vendor
        ).order_by("-created_at")

    else:
        conversations = Conversation.objects.none()

    return render(
        request,
        "catalog/conversation_list.html",
        {
            "conversations": conversations,
        }
    )

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)

    is_buyer = conversation.buyer == request.user # buyer owns the conversation directly
    is_seller = (
        hasattr(request.user, 'vendor')
        and conversation.seller == request.user.vendor
    )

    if not is_buyer and not is_seller:
        return HttpResponse(status=403)
    

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(conversation=conversation, sender=request.user, body=body)
        return redirect('conversation_detail', pk=pk)

    # mark messages from the other person as read
    conversation.messages.exclude(sender=request.user).update(is_read=True)
    return render(request, "catalog/conversation_detail.html", {"conversation": conversation})


def search(request):
    query = request.GET.get("q", "").strip()
    products = []
    listings = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            status="active",
        )
        listings = PlantListing.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            status="available",
        )

    return render(
        request,
        "catalog/search_results.html",
        {
            "query": query,
            "products": products,
            "listings": listings,
        },
    )
