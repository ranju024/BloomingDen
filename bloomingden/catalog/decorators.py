from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        # User must have seller role
        if not hasattr(request.user, "profile") or request.user.profile.role != "seller":
            messages.error(request, "You need a seller account to access this page.")
            return redirect("home")

        # Seller must have a Vendor account
        vendor = getattr(request.user, "vendor", None)

        if vendor is None:
            messages.error(
                request,
                "Your seller account is not set up yet. Please contact the administrator."
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper