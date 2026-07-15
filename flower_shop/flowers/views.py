from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Flower, Bouquet, Order
from .cart import Cart

# Create your views here.
def home(request):
    return render(request, "home.html")

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
    else:
        return HttpResponse(status=404)
    cart = Cart(request) # Create cart object
    cart.add(item, item_type) # Add bouquet to cart 
    messages.success(request, f"{item.name} added to cart.")
    if item_type == 'bouquet':   
        return redirect('bouquet_detail', pk=pk) # Redirect back to the bouquet page
    return redirect('flower_detail', id=pk)

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
    # items = cart.get_items()  # get all items stored in the cart

    # Fix old cart items that don't have id
    # for key, item in list(cart.items()):
    #     if 'id' not in item:
    #         item['id'] = key

    # request.session['cart'] = cart

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
        return redirect('bouquet_list') # if nth to check out
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if name and phone and address:  # minimal server-side validation
            order = Order.objects.create(
                name=name,
                phone=phone,
                address=address,
                total_price=total_price
            )
            request.session['cart'] = {}  #empty the cart
            request.session.modified = True
            return redirect('order_success', order_id=order.id)
        
    return render(request, "flowers/checkout.html", {
        "items": items,
        "total_price": total_price
    })

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "flowers/order_success.html", {"order": order})

def shop(request):
    return render(request, "flowers/shop.html")