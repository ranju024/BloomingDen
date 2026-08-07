from django.contrib import admin
from ..models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "seller",
        "category",
        "price",
        "stock",
        "status",
        "is_featured",
    )

    list_filter = (
        "status",
        "category",
        "is_featured",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "price",
        "stock",
        "status",
        "is_featured",
    )