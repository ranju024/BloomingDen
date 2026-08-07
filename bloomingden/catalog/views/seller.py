from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import ProductForm
from ..decorators import seller_required
from ..models import Product

@login_required
def seller_dashboard(request):
    # products = Product.objects.filter(
    #     seller=request.user
    # ).order_by("-created_at")
    products = request.user.vendor.products.all()
    context = {
        "products": products,
        "total_products": products.count(),
        "active_products": products.filter(status="active").count(),
        "draft_products": products.filter(status="draft").count(),
        "out_of_stock": products.filter(status="out_of_stock").count(),
    }

    return render(
        request,
        "catalog/seller/dashboard.html",
        context,
    )

@login_required
@seller_required
def add_product(request):

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.vendor
            product.save()

            return redirect("seller_dashboard")

    else:
        form = ProductForm()

    return render(
        request,
        "catalog/seller/add_product.html",
        {
            "form": form,
        },
    )

@login_required
@seller_required
def edit_product(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        seller=request.user.vendor,
    )
    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )
        if form.is_valid():
            form.save()
            return redirect("seller_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "catalog/seller/edit_product.html",
        {
            "form": form,
            "product": product,
        },
    )

@login_required
@seller_required
def delete_product(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        seller=request.user.vendor,
    )
    if request.method == "POST":
        product.delete()
        return redirect("seller_dashboard")

    return render(
        request,
        "catalog/seller/delete_product.html",
        {
            "product": product,
        },
    )