from django.contrib import admin
from .category import *
from ..models import Product, Flower, Bouquet, Order, Plant, PlantListing, Conversation, Message

# Register your models here.
# admin.register(Category)
admin.site.register(Product)

admin.site.register(Flower)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Plant)
admin.site.register(PlantListing)
admin.site.register(Conversation)
admin.site.register(Message)