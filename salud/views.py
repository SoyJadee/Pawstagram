
from django.shortcuts import render

def servicios_salud(request):
	# Ejemplo de datos, reemplazar por consulta real a la base de datos si es necesario
	veterinarias = [
		{
			'id': 1,
			'name': 'Vet Feliz',
			'address': 'Av. Principal 123',
			'coords': {'lat': 10.4806, 'lon': -66.9036},
			'type': 'veterinaria',
			'email': 'contacto@vetfeliz.com',
			'services': 'Consulta, Vacunas, Cirugía',
			'description': 'Atención integral para tu mascota.',
			'consultprice': 'Bs. 10',
			'estado': 'abierto',
			'phone': '+58 123-4567'
		},
		{
			'id': 2,
			'name': 'Spa Peluditos',
			'address': 'Calle Secundaria 45',
			'coords': {'lat': 10.4810, 'lon': -66.9040},
			'type': 'spa',
			'email': 'info@spapeluditos.com',
			'services': 'Baño, Corte, Masajes',
			'description': 'Relajación y belleza para tu mascota.',
			'consultprice': 'Bs. 8',
			'estado': 'cerrado',
			'phone': '+58 987-6543'
		}
	]
	return render(request, 'salud.html', {'veterinarias': veterinarias})
