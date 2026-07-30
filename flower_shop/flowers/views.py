from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from .forms import SignUpForm, PlantListingForm
from .models import Flower, Bouquet, Order, Category, Plant, Profile, PlantListing, Conversation, Message
from .cart import Cart

import json
import base64
from .esewa import build_payment_data, verify_response_signature, ESEWA_FORM_URL
from .khalti import initiate_payment, verify_payment

# Create your views here.
def home(request):
    return render(request, "home.html")

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data['phone']
            )
            auth_login(request, user)
            messages.success(request, "Welcome to BloomingDen!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, "flowers/signup.html", {"form": form})

def flowers_list(request):
    ''' get all flowers from the database and send them to 
    a template called flowers.html'''
    flowers = Flower.objects.all()
    return render(request, "flowers/flowers.html", {"flowers": flowers})

def flower_detail(request, id):
    flower = get_object_or_404(Flower, id=id)
    return render(request, "flowers/flower_detail.html", {"flower": flower})

def bouquet_list(request):
    ''' fetches all bouquets from the database and sends them to flowers/bouquet_list.html template'''
    bouquets = Bouquet.objects.all()
    return render(request, "flowers/bouquet_list.html", {"bouquets": bouquets})

def bouquet_detail(request, pk):
    ''' Finds the bouquet using its ID and sends it to flowers/bouquet_detail.html'''
    bouquet = get_object_or_404(Bouquet, pk=pk)
    return render(request, "flowers/bouquet_detail.html", {"bouquet": bouquet})


@require_POST  # reject anything that isn't POST
def add_to_cart(request, item_type, pk):
    """
    View that handles adding an item to the cart.
    """ 
    if item_type == 'bouquet':
        item = get_object_or_404(Bouquet, pk=pk) # Get the bouquet from database    
    elif item_type == 'flower':
        item = get_object_or_404(Flower, pk=pk)
    elif item_type == 'plant':
        item = get_object_or_404(Plant, pk=pk)
    else:
        return HttpResponse(status=404)
    
    cart = Cart(request) # Create cart object
    cart.add(item, item_type) # Add item to cart 
    messages.success(request, f"{item.name} added to cart.")

    if item_type == 'bouquet':   
        return redirect('bouquet_detail', pk=pk) # Redirect back to the bouquet page
    elif item_type == 'flower':
        return redirect('flower_detail', id=pk)
    return redirect('plant_detail', pk=pk)

def get_cart_data(request):
    """
    Returns cart items and total price.
    This avoids repeating the same code in multiple views.
    """
    cart = request.session.get('cart', {})
    items = cart.values()

    total_price = Decimal('0.00')
    for item in items:
        total_price += Decimal(item['price']) * item['quantity']
    return items, total_price

def cart_detail(request):
    ''' Display the contents of the shopping cart and calculate total price '''
    # cart = Cart(request)  # create cart object from session
    cart = request.session.get('cart', {})

    items = cart.values()
    total_price = Decimal('0.00')

    #calculate subtotal for each item
    for item in items:
        item['subtotal'] = Decimal(item['price']) * item['quantity']
        total_price += item['subtotal']

    # Send cart items to template    
    return render(request, "flowers/cart_detail.html", {  
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
    cart = request.session.get('cart', {})
    if key in cart:
        del cart[key]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def checkout(request):
    ''' Handles checkout form submission and saves the order'''
    items, total_price = get_cart_data(request)
    if not items:
        return redirect('home') # if nth to check out
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if name and phone and address:  # minimal server-side validation
            order = Order.objects.create(
                name=name,
                phone=phone,
                address=address,
                total_price=total_price, 
                payment_method=payment_method
            )
            request.session['cart'] = {}  #empty the cart
            request.session.modified = True

            if payment_method == 'esewa':
                return redirect('esewa_initiate', order_id=order.id)
            elif payment_method == 'khalti':
                return redirect('khalti_initiate', order_id=order.id)           
            return redirect('order_success', order_id=order.id)
        
    return render(request, "flowers/checkout.html", {
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

    return render(request, "flowers/esewa_redirect.html", {
        "payment_data": payment_data,
        "esewa_url": ESEWA_FORM_URL,
    })


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

    order.payment_status = 'paid'
    order.save()
    return redirect('order_success', order_id=order.id)

def khalti_initiate(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return_url = request.build_absolute_uri(reverse('khalti_verify'))
    website_url = request.build_absolute_uri('/')

    try:
        data = initiate_payment(order, return_url, website_url)
    except Exception:
        messages.error(request, "Could not connect to Khalti. Please try again.")
        return redirect('checkout')

    order.transaction_uuid = data.get('pidx')
    order.save()
    return redirect(data.get('payment_url'))


def khalti_verify(request):
    pidx = request.GET.get('pidx')
    if not pidx:
        return redirect('payment_failure')

    order = get_object_or_404(Order, transaction_uuid=pidx)

    try:
        result = verify_payment(pidx)
    except Exception:
        messages.error(request, "Could not verify payment with Khalti.")
        return redirect('payment_failure')

    if result.get('status') != 'Completed':
        return redirect('payment_failure')

    paid_amount = Decimal(result.get('total_amount', 0)) / 100
    if paid_amount != order.total_price:
        messages.error(request, "Payment amount mismatch. Please contact support.")
        return redirect('payment_failure')

    order.payment_status = 'paid'
    order.save()
    return redirect('order_success', order_id=order.id)


def payment_failure(request):
    return render(request, "flowers/payment_failure.html")

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "flowers/order_success.html", {"order": order})

def shop(request):
    return render(request, "flowers/shop.html")


def plants_list(request, category_slug=None):
    plants = Plant.objects.all()
    category = None
    subcategories = Category.objects.filter(name="Plants").first()
    subcategories = subcategories.children.all() if subcategories else []

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        plants = plants.filter(category=category)

    return render(request, "flowers/plants_list.html", {
        "plants": plants,
        "category": category,
        "subcategories": subcategories,
    })

def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    return render(request, "flowers/plant_detail.html", {"plant": plant})

def listing_list(request):
    listings = PlantListing.objects.filter(status='available').order_by('-created_at')
    return render(request, "flowers/listing_list.html", {"listings": listings})

def listing_detail(request, pk):
    listing = get_object_or_404(PlantListing, pk=pk)
    return render(request, "flowers/listing_detail.html", {"listing": listing})


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = PlantListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            messages.success(request, "Your plant is now listed!")
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = PlantListingForm()
    return render(request, "flowers/listing_form.html", {"form": form})


@login_required
def my_listings(request):
    listings = PlantListing.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, "flowers/my_listings.html", {"listings": listings})


@require_POST
@login_required
def mark_sold(request, pk):
    listing = get_object_or_404(PlantListing, pk=pk, seller=request.user)
    listing.status = 'sold'
    listing.save()
    messages.success(request, f"{listing.name} marked as sold.")
    return redirect('my_listings')


@login_required
def start_conversation(request, pk):
    listing = get_object_or_404(PlantListing, pk=pk)
    if listing.seller == request.user:
        messages.error(request, "You can't message yourself about your own listing.")
        return redirect('listing_detail', pk=pk)

    conversation, created = Conversation.objects.get_or_create(
        listing=listing, buyer=request.user,
        defaults={'seller': listing.seller}
    )
    return redirect('conversation_detail', pk=conversation.pk)


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by('-created_at')
    return render(request, "flowers/conversation_list.html", {"conversations": conversations})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user != conversation.buyer and request.user != conversation.seller:
        return HttpResponse(status=403)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(conversation=conversation, sender=request.user, body=body)
        return redirect('conversation_detail', pk=pk)

    conversation.messages.exclude(sender=request.user).update(is_read=True)
    return render(request, "flowers/conversation_detail.html", {"conversation": conversation})