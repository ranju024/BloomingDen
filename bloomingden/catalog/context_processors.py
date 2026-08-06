def cart_item_count(request):
    ''' Counts total items in the cart. It will run automatically on every page.'''
    cart = request.session.get('cart', {})
    total_items = 0

    # count quantity of each product
    for item in cart.values():
        total_items += item['quantity']
    return {
        'cart_item_count': total_items
    }