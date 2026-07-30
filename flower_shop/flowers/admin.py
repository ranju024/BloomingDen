from django.contrib import admin
from .models import Flower, Bouquet, Order, Category, Plant, PlantListing, Conversation, Message

# Register your models here.
admin.site.register(Flower)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Plant)
admin.site.register(PlantListing)
admin.site.register(Conversation)
admin.site.register(Message)