from django.shortcuts import render, redirect, get_object_or_404

from ..forms import ProductForm, ProductImageFormSet
from ..decorators import seller_required
from ..models import Product


@seller_required
def seller_dashboard(request):
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

@seller_required
def add_product(request):

    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.vendor
            product.save()

            formset = ProductImageFormSet(
                request.POST,
                request.FILES,
                instance=product,
            )

            if formset.is_valid():
                formset.save()
                return redirect("seller_dashboard")           

            return redirect("seller_dashboard")
        else:
            image_formset = ProductImageFormSet(
                request.POST,
                request.FILES
            )
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(
        request,
        "catalog/seller/add_product.html",
        {
            "form": form,
            "formset": formset,
        },
    )

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
            instance=product,
        )
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=product,
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("seller_dashboard")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(
        request,
        "catalog/seller/edit_product.html",
        {
            "form": form,
            "formset": formset,
            "product": product,
        },
    )


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