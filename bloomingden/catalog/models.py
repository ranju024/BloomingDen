from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Vendor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vendor",
    )
    shop_name = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to="vendors/logos/",
        blank=True,
        null=True,
    )
    cover_image = models.ImageField(
        upload_to="vendors/covers/",
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.shop_name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.shop_name

    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True) #SEO-friendly URL
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children') # supports unlimited nesting

    image = models.ImageField(upload_to="categories/", blank=True, null=True, )
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)  #control display order
    is_active = models.BooleanField(default=True)  # hide categories without deleting
    is_featured = models.BooleanField(default=False)  # show on homepage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("out_of_stock", "Out of Stock"),
        ("archived", "Archived"),
    ]
    CONDITION_CHOICES = [
        ("new", "New"),
        ("used", "Used"),
    ]
    seller = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products", )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products",)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, )
    stock = models.PositiveIntegerField(default=0)
    # image = models.ImageField(upload_to="products/", blank=True, null=True, )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft",)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default="new",)
    is_featured = models.BooleanField(default=False)   
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    review_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()

        if primary:
            return primary

        return self.images.first()
    
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} Image"


class PlantDetails(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="plant_details",
    )
    scientific_name = models.CharField(
        max_length=200,
        blank=True,
    )
    sunlight = models.CharField(
        max_length=100,
        blank=True,
    )
    watering_frequency = models.CharField(
        max_length=100,
        blank=True,
    )
    humidity = models.CharField(
        max_length=100,
        blank=True,
    )
    difficulty = models.CharField(
        max_length=50,
        blank=True,
    )
    pet_safe = models.BooleanField(default=False)
    indoor = models.BooleanField(default=True)
    height = models.CharField(
        max_length=50,
        blank=True,
    )
    pot_size = models.CharField(
        max_length=50,
        blank=True,
    )
    def __str__(self):
        return self.product.name

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.product.name} - {self.rating}"


# class Plant(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='plants')
#     image = models.ImageField(upload_to="plants/", null=True, blank=True)

#     def __str__(self):
#         return self.name
    

# class Flower(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     image = models.ImageField(upload_to="catalog/", null=True, blank=True)
#     def __str__(self):
#         return self.name

# class Bouquet(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     image = models.ImageField(upload_to="bouquets/", null=True, blank=True)
#     catalog = models.ManyToManyField('Flower')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.name
    
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
    ]
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    payment_status = models.CharField(max_length=10, default='pending')
    transaction_uuid = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} => {self.name}"

class PlantListing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
    ]
    seller = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='plant_listings')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='good')
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='listings/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.seller.username}"


class Conversation(models.Model):
    listing = models.ForeignKey(PlantListing, on_delete=models.CASCADE, related_name='conversations')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_buyer')
    seller = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='conversations_as_seller')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'buyer')

    def __str__(self):
        return f"{self.buyer.username} ↔ {self.seller.username} about {self.listing.name}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']