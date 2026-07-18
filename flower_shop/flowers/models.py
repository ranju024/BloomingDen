from django.db import models
from django.utils.text import slugify
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
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Plant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='plants')
    image = models.ImageField(upload_to="plants/", null=True, blank=True)

    def __str__(self):
        return self.name
    

class Flower(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="flowers/", null=True, blank=True)
    def __str__(self):
        return self.name

class Bouquet(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="bouquets/", null=True, blank=True)
    flowers = models.ManyToManyField('Flower')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    ''' Stores Customer Order Information'''
    name = models.CharField(max_length=200)  # customer's name
    phone = models.CharField(max_length=15)  # phone number
    address = models.TextField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} => {self.name}"