from django.urls import path
from . import views
from .views.seller import seller_dashboard, add_product, edit_product, delete_product

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"), 

    path("seller/dashboard/", seller_dashboard, name="seller_dashboard", ),
    path("seller/products/add", add_product, name="add_product", ),
    path("seller/products/<int:pk>/edit/", edit_product, name="edit_product",),
    path("seller/products/<int:pk>/delete/", delete_product, name="delete_product",),

]