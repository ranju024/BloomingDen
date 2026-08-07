from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import Product, Category


def product_list(request):
    products = Product.objects.filter(
        status="active"
    ).select_related(
        "category",
        "seller",
    )

    q = request.GET.get("q")

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    category = request.GET.get("category")

    if category:
        products = products.filter(category__slug=category)

    sort = request.GET.get("sort")

    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    categories = Category.objects.filter(
        parent=None,
        is_active=True,
    ).prefetch_related("children")

    return render(
        request,
        "catalog/products.html",
        {
            "products": products,
            "categories": categories,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        status="active",
    )

    related_products = Product.objects.filter(
        category=product.category,
        status="active",
    ).exclude(
        pk=product.pk,
    )[:4]

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )