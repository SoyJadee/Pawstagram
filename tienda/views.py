from .models import Product

def catalogo(request):
	products = Product.objects.select_related('store').all().order_by('-id')
	return render(request, 'catalogo.html', {'products': products})

from django.shortcuts import render

from .models import Store

def tienda(request):
	stores = Store.objects.all().order_by('-created_at')
	return render(request, 'Tienda.html', {'stores': stores})
