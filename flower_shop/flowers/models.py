from django.db import models

# Create your models here.
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