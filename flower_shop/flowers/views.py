from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
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

def add_to_cart(request, pk):
    """
    View that handles adding a bouquet to the cart.
    """ 
    bouquet = get_object_or_404(Bouquet, pk=pk) # Get the bouquet from database    
    cart = Cart(request) # Create cart object
    cart.add(bouquet) # Add bouquet to cart    
    return redirect('bouquet_detail', pk=pk) # Redirect back to the bouquet page

def get_cart_data(request):
    """
    Returns cart items and total price.
    This avoids repeating the same code in multiple views.
    """
    cart = request.session.get('cart', {})
    items = cart.values()

    total_price = 0
    for item in items:
        total_price += float(item['price']) * item['quantity']
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
    total_price = 0

    #calculate subtotal for each item
    for item in items:
        item['subtotal'] = float(item['price']) * item['quantity']
        total_price += item['subtotal']

    # Send cart items to template    
    return render(request, "flowers/cart_detail.html", {  
        "items": items,
        "total_price": total_price
        })  

def remove_from_cart(request, product_id):
    ''' Remove a bouquet from the cart '''
    # cart = Cart(request)
    # cart.remove(pk) # remove bouquet using its id
    # item = Cart.objects.get(pk=pk)
    # item.delete()
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

def checkout(request):
    ''' Handles checkout form submission and saves the order'''

