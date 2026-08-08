from django.urls import path
from . import views
from .views.seller import seller_dashboard, add_product, edit_product, delete_product

urlpatterns = [
    path("", views.home, name="home"),

    #Products
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),

    # cart
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/increase/<str:key>/", views.increase_cart_item, name="increase_cart_item"),
    path("cart/decrease/<str:key>/", views.decrease_cart_item, name="decrease_cart_item"),
    path("cart/remove/<str:key>/", views.remove_from_cart, name="remove_from_cart"),

    # Seller
    path("seller/dashboard/", seller_dashboard, name="seller_dashboard", ),
    path("seller/products/add", add_product, name="add_product", ),
    path("seller/products/<int:pk>/edit/", edit_product, name="edit_product",),
    path("seller/products/<int:pk>/delete/", delete_product, name="delete_product",),

]