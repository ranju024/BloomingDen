from django.contrib import admin
from .models import Flower, Bouquet, Order

# Register your models here.
admin.site.register(Flower)
admin.site.register(Bouquet)
admin.site.register(Order)