from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Order, Vendor
from ..decorators import seller_required


@login_required
def my_orders(request):
    orders = (
        Order.objects.filter(user=request.user).prefetch_related("items").order_by("-created_at")
        )
    return render(request, "catalog/orders/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk, user=request.user)
    return render(
        request, "catalog/orders/order_detail.html", {"order": order}
    )

@seller_required
def seller_orders(request):
    vendor = request.user.vendor
    orders = (
        Order.objects
        .filter(items__seller=vendor)
        .prefetch_related("items")
        .distinct()
        .order_by("-created_at")
    )
    return render(
        request, "catalog/orders/seller_orders.html", {"orders": orders}
    )

@seller_required
def seller_order_detail(request, pk):
    vendor = request.user.vendor
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=pk,
        items__seller=vendor,
    )

    if request.method == "POST":
        new_status = request.POST.get("order_status")
        valid_statuses = dict(Order.ORDER_STATUS_CHOICES)
        
        if new_status not in valid_statuses:
            messages.error(request, "Invalid order status.")
            return redirect("seller_order_detail", pk=order.pk)
        
        order.order_status = new_status
        order.save(update_fields=["order_status", "updated_at"])

        messages.success(
            request, f"Order #{order.id} status updated to {valid_statuses[new_status]}."
        )
        return redirect("seller_order_detail", pk=order.pk)
    
    return render(
        request,
        "catalog/orders/seller_order_detail.html",
        {
            "order": order,
            "status_choices": Order.ORDER_STATUS_CHOICES,
            "vendor": vendor,
        },
    )
