# Pawstagram

Pawstagram es una plataforma web tipo red social dedicada a los amantes de los animales, diseñada para conectar personas, tiendas, refugios y eventos relacionados con mascotas. El proyecto está construido con una arquitectura robusta y programación avanzada, integrando múltiples módulos para ofrecer una experiencia digital completa.

## Funcionalidades principales

- **Visualización de tiendas especializadas:**
  - Los usuarios pueden explorar tiendas de productos para mascotas.
  - Filtros por categoría, ubicación y disponibilidad.
  - Integración de APIs de mapas para mostrar ubicaciones.
  - Validación de datos en tiempo real y diseño responsivo.

- **Perfiles de mascotas en adopción:**
  - Cada mascota cuenta con un perfil propio (fotos, historia, estado de salud).
  - Contacto directo con refugios.
  - Base de datos relacional bien estructurada.
  - Validación de formularios y control de acceso seguro.

- **Geolocalización de tiendas, refugios y eventos:**
  - Visualización de ubicaciones cercanas mediante servicios de geolocalización.
  - Uso de la librería [Leaflet](https://leafletjs.com/) para mapas interactivos.
  - Lógica backend para manejo de coordenadas y agrupamiento de puntos.

- **Gestión de usuarios y eventos:**
  - Registro de usuarios.
  - Visualización de eventos y fechas importantes.
  - Notificaciones personalizadas.

## Instalación del proyecto

Sigue estos pasos para instalar y ejecutar Pawstagram en tu entorno local:

1. **Clona el repositorio:**
	```bash
	git clone https://github.com/SoyJadee/Pawstagram.git
	cd Pawstagram/pawstagram
	```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
	```bash
	python -m venv venv
	# En Windows
	venv\Scripts\activate
	# En Linux/Mac
	source venv/bin/activate
	```

3. **Instala las dependencias:**
	```bash
	pip install -r requirements.txt
	```
4. **Ejecuta el servidor de desarrollo:**
	```bash
	python manage.py runserver
	```

5. **Accede a la aplicación:**
	Abre tu navegador y visita [http://localhost:8000](http://localhost:8000)

## Notas adicionales

- Para la funcionalidad de mapas, asegúrate de tener acceso a internet para cargar Leaflet y los mapas base.
- Puedes personalizar la configuración de la base de datos y otros parámetros en `.env`.
- Si deseas contribuir, por favor abre un issue o un pull request en el repositorio.

---
Desarrollado por el equipo de Pawstagram.
