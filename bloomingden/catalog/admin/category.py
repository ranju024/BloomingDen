from django.contrib import admin
from ..models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "sort_order",
        "is_featured",
        "is_active",
    )
    list_filter = (
        "is_active",
        "is_featured",
    )
    search_fields = (
        "name",
        "description",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }
    ordering = (
        "sort_order",
        "name",
    )