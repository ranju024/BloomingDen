from django.contrib import admin
from .models import Flower, Bouquet, Order, Category, Plant

# Register your models here.
admin.site.register(Flower)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Plant)