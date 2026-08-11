"""
URL configuration for bloomingden project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from catalog import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("signup/", views.signup, name='signup'),
    path("login/", auth_views.LoginView.as_view(template_name='catalog/login.html'), name='login'),
    path("logout/", auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # path("catalog/", views.catalog_list, name='catalog_list'),
    # path("catalog/<int:id>/", views.flower_detail, name='flower_detail'),
    # path("bouquets/", views.bouquet_list, name='bouquet_list'),
    # path("bouquets/<int:pk>/", views.bouquet_detail, name='bouquet_detail'),
    path("cart/add/<str:item_type>/<int:pk>/", views.add_to_cart, name='add_to_cart'),
    path("cart/", views.cart_detail, name='cart_detail'),
    path("cart/remove/<str:key>/", views.remove_from_cart, name='remove_from_cart'),
    path("checkout/", views.checkout, name='checkout'),
    path("order/success/<int:order_id>/", views.order_success, name='order_success'),
    path("shop/", views.shop, name='shop'),
    path("cart/increase/<str:key>/", views.increase_cart_item, name='increase_cart_item'),
    path("cart/decrease/<str:key>/", views.decrease_cart_item, name='decrease_cart_item'),
    # path("plants/", views.plants_list, name='plants_list'),
    # path("plants/category/<slug:category_slug>/", views.plants_list, name='plants_by_category'),
    # path("plants/<int:pk>/", views.plant_detail, name='plant_detail'),
    path("payment/esewa/initiate/<int:order_id>/", views.esewa_initiate, name='esewa_initiate'),
    path("payment/esewa/success/", views.esewa_success, name='esewa_success'),
    path("payment/esewa/failure/", views.payment_failure, name='payment_failure'),   
    path("marketplace/", views.listing_list, name='listing_list'),
    path("marketplace/new/", views.listing_create, name='listing_create'),
    path("marketplace/mine/", views.my_listings, name='my_listings'),
    path("marketplace/<int:pk>/", views.listing_detail, name='listing_detail'),
    path("marketplace/<int:pk>/message/", views.start_conversation, name='start_conversation'),
    path("marketplace/<int:pk>/sold/", views.mark_sold, name='mark_sold'),
    path("inbox/", views.conversation_list, name='conversation_list'),
    path("inbox/<int:pk>/", views.conversation_detail, name='conversation_detail'),
    path("search/", views.search, name='search'),
]

if settings.DEBUG:  # configure URLs for media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
