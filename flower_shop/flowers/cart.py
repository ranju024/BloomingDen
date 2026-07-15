class Cart:
    def __init__(self, request):
        """
        Initialize the cart.

        The cart will be stored in the user's session.
        If the cart does not exist yet, we create an empty one.
        """
        self.session = request.session
 
        # Get cart from session if it exists
        cart = self.session.get('cart')

        # If no cart exists, create an empty dictionary
        if not cart:
            cart = self.session['cart'] = {}

        # Store the cart
        self.cart = cart

    def add(self, item, item_type):
        """
        Add an item (Flower or Bouquet) to the cart.
        item_type distinguishes them so IDs never collide.
        """

        key = f"{item_type}-{item.id}"

        # If the item is not already in the cart
        if key not in self.cart:
            self.cart[key] = {
                'key': key,
                'id': item.id,
                'type': item_type,
                'name': item.name,
                'price': str(item.price),
                'quantity': 1
            }
        else:
            # If already in cart, increase quantity
            self.cart[key]['quantity'] += 1

        # Save changes
        self.save()

    def increase(self, key): # increase quantity
        if key in self.cart:
            self.cart[key]['quantity'] += 1
        self.save()

    def decrease(self, key): # decrease quantity
        if key in self.cart:
            self.cart[key]['quantity'] -= 1
            if self.cart[key]['quantity'] <= 0:
                del self.cart[key]
        self.save()

    def remove(self, key):
        """
        Remove an item from the cart.
        """
        # check if the bouquet exists in the cart
        if key in self.cart:
            del self.cart[key]
        self.save()  # save updated cart

    def save(self):
        """
        Save the cart back into the session so Django remembers it.
        """
        self.session['cart'] = self.cart
        self.session.modified = True

    def get_items(self):
        ''' Returns items currently stored in the cart
    '''
        return self.cart.values()