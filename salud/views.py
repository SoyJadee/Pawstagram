import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def obtener_ruta_openrouteservice(request):
	if request.method == 'POST':
		import json
		data = json.loads(request.body.decode('utf-8'))
		origen = data.get('origen')  # [lon, lat]
		destino = data.get('destino')  # [lon, lat]
		if not origen or not destino:
			return JsonResponse({'error': 'Faltan coordenadas'}, status=400)
		api_key = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjQyYmI2ZGVmY2U5YzRlNTU5ZGIzMzA1OTgyODVjOTY4IiwiaCI6Im11cm11cjY0In0='
		url = 'https://api.openrouteservice.org/v2/directions/driving-car'
		body = {
			'coordinates': [origen, destino]
		}
		headers = {
			'Authorization': api_key,
			'Content-Type': 'application/json',
			'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
		}
		try:
			response = requests.post(url, json=body, headers=headers, timeout=10)
			if response.status_code == 200:
				return JsonResponse(response.json())
			else:
				return JsonResponse({'error': 'Error en OpenRouteService', 'status': response.status_code}, status=500)
		except Exception as e:
			return JsonResponse({'error': str(e)}, status=500)
	return JsonResponse({'error': 'Método no permitido'}, status=405)
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
