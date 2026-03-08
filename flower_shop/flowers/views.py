from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Flower, Bouquet

# Create your views here.
def home(request):
    return render(request, "home.html")

def flowers_list(request):
    ''' get all flowers from the database and send them to 
    a template called flowers.html'''
    flowers = Flower.objects.all()
    return render(request, "flowers/flowers.html", {"flowers": flowers})

def flower_detail(request, id):
    flower = get_object_or_404(Flower, id=id)
    return render(request, "flowers/flower_detail.html", {"flower": flower})

def bouquet_list(request):
    ''' fetches all bouquets from the database and sends them to flowers/bouquet_list.html template'''
    bouquets = Bouquet.objects.all()
    return render(request, "flowers/bouquet_list.html", {"bouquets": bouquets})

def bouquet_detail(request, id):
    ''' Finds the bouquet using its ID and sends it to flowers/bouquet_detail.html'''
    bouquet = get_object_or_404(Bouquet, id=id)
    return render(request, "flowers/bouquet_detail.html", {"bouquet": bouquet})