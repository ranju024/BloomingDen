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

    def add(self, bouquet):
        """
        Add a bouquet to the cart. We use the bouquet ID as the key.
        """
        bouquet_id = str(bouquet.id)

        # If the bouquet is not already in the cart
        if bouquet_id not in self.cart:
            self.cart[bouquet_id] = {
                'id': bouquet.id,
                'name': bouquet.name,
                'price': str(bouquet.price),
                'quantity': 1
            }
        else:
            # If already in cart, increase quantity
            self.cart[bouquet_id]['quantity'] += 1

        # Save changes
        self.save()
    
    def remove(self, bouquet_id):
        """
        Remove a bouquet from the cart. bouquet_id is converted to string because
        we stored IDs as strings in the cart dictionary.
        """
        bouquet_id = str(bouquet_id)
        # check if the bouquet exists in the cart
        if bouquet_id in self.cart:
            del self.cart[bouquet_id]
        self.save()  # save updated cart

    def save(self):
        """
        Save the cart back into the session so Django remembers it.
        """
        self.session['cart'] = self.cart
        self.session.modified = True

    def get_items(self):
        ''' Returns items currently stored in the cart
        Each item represents a bouquet added by the user. '''
        return self.cart.values()