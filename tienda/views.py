from .models import Product, Store
from django.shortcuts import get_object_or_404
from django_smart_ratelimit import rate_limit

@rate_limit(key='ip', rate='5/m',)
def catalogo(request, store_id):
	store = get_object_or_404(Store, id=store_id)
	products = Product.objects.filter(store_id=store_id).order_by('-id')
	return render(request, 'catalogo.html', {'products': products, 'store': store})

from django.shortcuts import render

from .models import Store
@rate_limit(key='ip', rate='5/m',)
def tienda(request):
	stores = Store.objects.all().order_by('-created_at')
	return render(request, 'Tienda.html', {'stores': stores})
