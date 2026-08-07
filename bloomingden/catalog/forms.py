from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, PlantListing, Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "description",
            "price",
            "stock",
            "condition",
            "status",
            "is_featured",
        ]

class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.RadioSelect, initial='buyer')
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone']

class PlantListingForm(forms.ModelForm):
    class Meta:
        model = PlantListing
        fields = ['name', 'description', 'price', 'condition', 'location', 'image']

