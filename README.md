<div align="center">

# 🐾 Pawstagram (Pawly)

### *Conectando corazones, cambiando vidas* 💙

[![Django](https://img.shields.io/badge/Django-5.2.6-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Backend-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Plataforma social integral para adopción responsable de mascotas y bienestar animal** 🏠🐕🐈

[English](#english-version) | [Características](#-características-principales) | [Instalación](#-instalación-y-configuración) | [Tecnologías](#-stack-tecnológico)

</div>

---

## 🌟 Características Principales

<table>
<tr>
<td width="50%">

### 🏡 Adopción de Mascotas
- **Perfiles completos** con fotos, historias y estado de salud
- **Sistema de solicitudes** con seguimiento en tiempo real
- **Notificaciones automáticas** sobre el proceso de adopción
- **Gestión de mascotas** adoptadas y disponibles

</td>
<td width="50%">

### 🏥 Directorio de Salud Animal
- **Búsqueda geolocalizada** de veterinarias y servicios
- **Reseñas y calificaciones** de la comunidad
- **Mapas interactivos** con rutas optimizadas
- **Integración con OpenRouteService** para navegación

</td>
</tr>
<tr>
<td width="50%">

### 🛒 Tienda y Catálogo
- **Directorio de tiendas** especializadas en mascotas
- **Catálogo de productos** con filtros avanzados
- **Búsqueda por categoría** y ubicación
- **Información detallada** de comercios locales

</td>
<td width="50%">

### �� Red Social y Comunidad
- **Feed dinámico** con publicaciones y comentarios
- **Sistema de likes** y reacciones
- **Perfil personalizable** para usuarios
- **Calendario de eventos** y campañas animalistas

</td>
</tr>
</table>

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.10 o superior
- PostgreSQL 12+ (o Supabase para backend en la nube)
- Redis (opcional, para caché y rate limiting)
- Git

### Instalación Rápida (Desarrollo)

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/SoyJadee/Pawstagram.git
   cd Pawstagram
   ```

2. **Crea y activa el entorno virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   
   Crea un archivo `.env` en la raíz del proyecto con:
   ```ini
   # Django Configuration
   SECRET_KEY=tu-clave-secreta-super-segura-aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
   CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
   
   # Admin Configuration
   ADMIN_URL=secure-admin-8a9f3d/
   
   # Supabase Configuration
   SUPABASE_URL=tu-url-de-supabase
   SUPABASE_KEY=tu-clave-publica-de-supabase
   SUPABASE_SERVICE_ROLE_KEY=tu-clave-service-role
   
   # OpenRouteService (opcional, para mapas)
   OPENROUTESERVICE_API_KEY=tu-api-key-de-openrouteservice
   ```

5. **Ejecuta las migraciones de base de datos**
   ```bash
   python manage.py migrate
   ```

6. **Crea un superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicia el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

8. **Accede a la aplicación**
   - Frontend: http://localhost:8000
   - Admin: http://localhost:8000/secure-admin-8a9f3d/ (o tu ADMIN_URL personalizada)

---

## 📦 Stack Tecnológico

### Backend
- **Framework:** Django 5.2.6
- **Lenguaje:** Python 3.10+
- **Base de datos:** PostgreSQL (vía Supabase)
- **ORM:** Django ORM con soporte para PostgreSQL
- **Autenticación:** JWT (PyJWT) + Django Auth
- **API REST:** Django REST Framework patterns
- **Rate Limiting:** django-smart-ratelimit

### Frontend
- **Template Engine:** Django Templates
- **JavaScript:** Vanilla JS + AJAX
- **UI/UX:** HTML5, CSS3 con diseño responsivo
- **Mapas:** Leaflet.js (django-leaflet) + OpenRouteService

### Infraestructura
- **BaaS:** Supabase (Auth, Storage, Database)
- **Caché:** Redis 6.4.0
- **WSGI Server:** Gunicorn (producción)
- **Almacenamiento:** Supabase Storage para imágenes
- **Despliegue:** Compatible con Heroku, Railway, Render

### Seguridad
- **HTTPS:** Configuración de seguridad Django
- **CSRF Protection:** Token-based
- **Rate Limiting:** Protección contra brute force
- **Admin Oculto:** django-hide-admin para protección adicional

---

## 🏗️ Arquitectura del Proyecto

```
Pawstagram/
├── adopcion/          # App de adopción de mascotas
├── common/            # Utilidades compartidas
├── Front/             # Archivos HTML/CSS/JS frontend
├── index/             # App de página principal
├── mascota/           # App de gestión de mascotas
├── pawstagram/        # Configuración principal del proyecto
│   ├── settings.py    # Configuraciones de Django
│   ├── urls.py        # URLs principales
│   └── wsgi.py        # WSGI application
├── salud/             # App de directorio de salud animal
├── tienda/            # App de tiendas y catálogo
├── usuarios/          # App de gestión de usuarios
├── manage.py          # Django management script
├── requirements.txt   # Dependencias de Python
├── Procfile           # Configuración para Heroku/Railway
└── README.md          # Este archivo
```

### Apps Django

| App | Descripción |
|-----|-------------|
| **adopcion** | Gestión de solicitudes y procesos de adopción |
| **mascota** | CRUD de mascotas, perfiles y fotos |
| **salud** | Directorio de veterinarias y servicios de salud |
| **tienda** | Catálogo de tiendas y productos para mascotas |
| **usuarios** | Autenticación, perfiles y gestión de usuarios |
| **index** | Página principal y feed social |
| **common** | Middlewares, utilidades y funciones compartidas |

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Requerida | Default |
|----------|-------------|-----------|---------|
| `SECRET_KEY` | Clave secreta de Django | ✅ Sí | - |
| `DEBUG` | Modo debug (solo desarrollo) | ❌ No | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (CSV) | ❌ No | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF (CSV) | ❌ No | `http://localhost:8000` |
| `ADMIN_URL` | URL personalizada del admin | ❌ No | `secure-admin-8a9f3d/` |
| `SUPABASE_URL` | URL del proyecto Supabase | ✅ Sí | - |
| `SUPABASE_KEY` | Clave pública Supabase | ✅ Sí | - |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave service role | ✅ Sí | - |
| `OPENROUTESERVICE_API_KEY` | API key para mapas | ❌ No | `''` |

### Despliegue en Producción

#### Heroku / Railway / Render

El proyecto incluye un `Procfile` configurado para deployment:

```bash
# El Procfile ya está configurado
web: gunicorn pawstagram.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-file -
```

**Pasos para desplegar:**

1. Configura todas las variables de entorno en tu plataforma
2. Asegúrate de establecer `DEBUG=False` en producción
3. Configura `ALLOWED_HOSTS` con tu dominio
4. Configura `CSRF_TRUSTED_ORIGINS` con tu URL completa (https://)
5. Utiliza una base de datos PostgreSQL (Supabase recomendado)

**Nota de seguridad:** Nunca hagas commit del archivo `.env` con credenciales reales.

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test mascota
python manage.py test adopcion

# Con coverage (instalar python-coverage)
coverage run manage.py test
coverage report
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este proyecto está construido con amor por la comunidad animalista.

### Cómo contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guidelines

- Sigue las convenciones de código de Django y PEP 8
- Escribe tests para nuevas funcionalidades
- Actualiza la documentación cuando sea necesario
- Sé respetuoso y constructivo en las discusiones

---

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "ModuleNotFoundError: No module named 'django'"**
```bash
# Asegúrate de tener el entorno virtual activado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstala las dependencias
pip install -r requirements.txt
```

**Error: "ImproperlyConfigured: Set the SUPABASE_URL environment variable"**
```bash
# Verifica que tu archivo .env existe y tiene las variables correctas
# El archivo debe estar en la raíz del proyecto
```

**Error al cargar mapas (app salud)**
```bash
# Configura OPENROUTESERVICE_API_KEY en tu .env
# O déjalo vacío si no necesitas la funcionalidad de mapas
OPENROUTESERVICE_API_KEY=
```

**Puerto 8000 ya en uso**
```bash
# Usa un puerto diferente
python manage.py runserver 8080
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Esto significa que puedes usar, modificar y distribuir este código libremente, siempre que mantengas el aviso de copyright original.

---

## 💖 Agradecimientos

- A todos los desarrolladores que contribuyen con su tiempo y talento
- A la comunidad open-source de Django
- A los refugios de animales que inspiraron este proyecto
- A todos los que trabajan por el bienestar animal

---

## 📞 Contacto y Comunidad

- **GitHub Issues:** Para reportar bugs o solicitar features
- **Pull Requests:** Para contribuir con código
- **Discussions:** Para ideas y discusiones generales

---

<div align="center">

### Desarrollado con ❤️ y Django

**Porque cada mascota merece un hogar y cada persona un amigo fiel** 🐶🐱🐰

⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐

</div>

---

## English Version

### 🌍 About Pawstagram (Pawly)

Pawstagram (Pawly) is a comprehensive social platform designed to facilitate responsible pet adoption and promote animal welfare. Built with Django and modern web technologies, it connects shelters, pet owners, stores, and animal lovers in a unified community.

### ✨ Key Features

- **Pet Adoption System:** Complete profiles, application tracking, and automated notifications
- **Health Directory:** Find veterinarians, groomers, and pet services with interactive maps
- **Store Catalog:** Browse pet stores and products with advanced filtering
- **Social Network:** Share posts, like, comment, and participate in community events

### 🚀 Quick Start

See the detailed installation instructions above. The project requires Python 3.10+, PostgreSQL (Supabase), and Redis.

### 🛠️ Tech Stack

Built with Django 5.2.6, Python 3.10+, Supabase (PostgreSQL), Redis, Leaflet.js, and deployed with Gunicorn.

### 📖 Documentation

The application is primarily in Spanish, but the codebase follows Django best practices and is well-documented. All API endpoints and models use clear, self-documenting naming conventions.

---

<div align="center">

Made with passion for animals and technology 🐾

</div>
