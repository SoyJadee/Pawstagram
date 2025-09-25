from django.shortcuts import render
from .models import Store
from .models import Product, Store
from django.shortcuts import get_object_or_404
from django_smart_ratelimit import rate_limit
from django.conf import settings

RL = getattr(settings, 'RATE_LIMITS', {})
RL_TIENDA_IP = RL.get('tienda_ip', '120/m')


@rate_limit(key='ip', rate=RL_TIENDA_IP)
def catalogo(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store_id=store_id).order_by('-id')
    return render(request, 'catalogo.html', {'products': products, 'store': store})


@rate_limit(key='ip', rate=RL_TIENDA_IP)
def tienda(request):
    stores = Store.objects.all().order_by('-created_at')
    return render(request, 'Tienda.html', {'stores': stores})
