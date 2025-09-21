from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
@csrf_exempt
def guardar_comentario_salud(request):
	if request.method == 'POST':
		user = request.POST.get('user')
		comment = request.POST.get('comment')
		rating = request.POST.get('rating')
		service_id = request.POST.get('service_id')
		if not (user and comment and rating and service_id):
			return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios'})
		try:
			review = Reviews.objects.create(
				user=user,
				comment=comment,
				rating=rating,
				service_id=service_id,
				created_at=timezone.now()
			)
			return JsonResponse({'success': True})
		except Exception as e:
			return JsonResponse({'success': False, 'error': str(e)})
	return JsonResponse({'success': False, 'error': 'Método no permitido'})


from django.shortcuts import render
from .models import ServicesHealth, Reviews
from django.http import JsonResponse
def obtener_comentarios_salud(request):
	service_id = request.GET.get('service_id')
	comentarios = []
	if service_id:
		reviews = Reviews.objects.filter(service_id=service_id).order_by('-created_at')
		for r in reviews:
			comentarios.append({
				'user': r.user,
				'rating': float(r.rating),
				'comment': r.comment,
				'created_at': r.created_at.isoformat()
			})
	return JsonResponse({'success': True, 'comentarios': comentarios})

def servicios_salud(request):
	servicios = ServicesHealth.objects.all()
	veterinarias = []
	from datetime import datetime
	now = datetime.now().time()
	for s in servicios:
		# Parsear coordenadas si existen
		coords = None
		if s.coordinates:
			try:
				lat, lon = map(float, s.coordinates.split(','))
				coords = {'lat': lat, 'lon': lon}
			except:
				coords = None
		# Determinar estado abierto/cerrado
		estado = 'cerrado'
		if s.horarioStart and s.horarioEnd:
			if s.horarioStart <= now <= s.horarioEnd:
				estado = 'abierto'
		veterinarias.append({
			'id': s.id,
			'name': s.name,
			'address': s.address,
			'coords': coords,
			'type': s.type,
			'email': s.email,
			'services': s.services,
			'description': s.description,
			'consultprice': s.consultPrice,
			'estado': estado,
			'phone': s.phone
		})
	return render(request, 'salud.html', {'veterinarias': veterinarias})
