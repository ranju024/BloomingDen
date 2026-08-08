class Cart:
    def __init__(self, request):
        """
        Initialize the cart using the user's session.
        """
        self.session = request.session

        cart = self.session.get("cart")

        if not cart:
            cart = self.session["cart"] = {}

        self.cart = cart

    def add(self, product):
        """
        Add a Product to the cart.
        If it already exists, increase its quantity.
        """

        key = f"product-{product.id}"

        if key not in self.cart:
            self.cart[key] = {
                "key": key,
                "id": product.id,
                "type": "product",
                "name": product.name,
                "price": str(product.price),
                "quantity": 1,
            }
        else:
            self.cart[key]["quantity"] += 1

        self.save()

    def increase(self, key):
        if key in self.cart:
            self.cart[key]["quantity"] += 1

        self.save()

    def decrease(self, key):
        if key in self.cart:
            self.cart[key]["quantity"] -= 1

            if self.cart[key]["quantity"] <= 0:
                del self.cart[key]

        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]

        self.save()

    def save(self):
        self.session["cart"] = self.cart
        self.session.modified = True

    def get_items(self):
        return self.cart.values()