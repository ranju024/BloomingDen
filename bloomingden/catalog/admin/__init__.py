from django.contrib import admin
from .category import *
from .product import *
from ..models import Vendor, ProductImage, PlantDetails, Order, PlantListing, Conversation, Message

# Register your models here.
# admin.register(Category)
# admin.site.register(Product)

admin.site.register(Vendor)
admin.site.register(ProductImage)
admin.site.register(PlantDetails)


admin.site.register(Order)
admin.site.register(PlantListing)
admin.site.register(Conversation)
admin.site.register(Message)