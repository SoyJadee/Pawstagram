# Pawstagram 🐾

Una red social moderna para mascotas donde puedes compartir momentos especiales, encontrar tu compañero perfecto para adoptar y conectar con la comunidad de amantes de los animales.

## 🌟 Características

- **Perfiles de Mascotas**: Crea perfiles únicos con fotos y descripciones
- **Feed Social**: Comparte fotos y videos de tus mascotas
- **Sistema de Adopción**: Conecta mascotas con familias amorosas
- **Notificaciones**: Mantente al día con likes, comentarios y adopciones
- **Tiendas Locales**: Descubre tiendas de mascotas cerca de ti con mapas interactivos
- **Comunidad**: Conecta con otros amantes de las mascotas

## 🛠️ Tecnologías

- **Frontend**: HTML5, TailwindCSS, JavaScript (ES6+)
- **Backend**: Supabase (PostgreSQL, Auth, Storage)
- **Mapas**: Leaflet.js
- **Estilos**: TailwindCSS con componentes personalizados
- **Autenticación**: Supabase Auth

## 📁 Estructura del Proyecto

```
Pawstagram/
├── config/                 # Configuración de la aplicación
│   └── config.js           # Config de Supabase y app
├── database/               # Documentación de base de datos
│   └── schema.md          # Esquema de la base de datos
├── public/                # Archivos públicos estáticos
│   ├── images/            # Imágenes públicas
│   ├── icons/             # Iconos de la aplicación
│   └── uploads/           # Uploads temporales
├── src/                   # Código fuente principal
│   ├── components/        # Componentes reutilizables
│   │   ├── common/        # Componentes comunes (navbar, footer)
│   │   ├── auth/          # Componentes de autenticación
│   │   ├── profile/       # Componentes de perfil
│   │   ├── posts/         # Componentes de posts
│   │   ├── adoption/      # Componentes de adopción
│   │   ├── notifications/ # Componentes de notificaciones
│   │   ├── stores/        # Componentes de tiendas
│   │   └── maps/          # Componentes de mapas
│   ├── css/               # Estilos
│   │   ├── input.css      # CSS de entrada para TailwindCSS
│   │   └── output.css     # CSS compilado (generado)
│   ├── js/                # JavaScript
│   │   ├── components/    # Lógica de componentes
│   │   ├── services/      # Servicios (auth, API, etc.)
│   │   ├── utils/         # Utilidades
│   │   └── main.js        # Punto de entrada de la aplicación
│   ├── assets/            # Assets del proyecto
│   │   ├── images/        # Imágenes de la aplicación
│   │   ├── icons/         # Iconos
│   │   └── uploads/       # Directorio de uploads
│   └── pages/             # Páginas HTML
│       ├── auth/          # Páginas de autenticación
│       ├── profile/       # Páginas de perfil
│       ├── posts/         # Páginas de posts
│       ├── adoption/      # Páginas de adopción
│       ├── notifications/ # Páginas de notificaciones
│       └── stores/        # Páginas de tiendas
├── docs/                  # Documentación
├── index.html             # Página principal
├── package.json           # Dependencias y scripts
├── tailwind.config.js     # Configuración de TailwindCSS
└── .gitignore            # Archivos ignorados por Git
```

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
npm install
```

### 2. Configurar Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Copia las credenciales en `config/config.js`:
   ```javascript
   export const supabaseConfig = {
       url: 'TU_SUPABASE_URL',
       anonKey: 'TU_SUPABASE_ANON_KEY'
   };
   ```

### 3. Configurar Base de Datos

Ejecuta las consultas SQL del archivo `database/schema.md` en tu proyecto de Supabase.

### 4. Configurar Storage

En Supabase, crea los siguientes buckets:
- `profile-images`
- `post-images`
- `store-images`

### 5. Compilar CSS

```bash
npm run build-css
```

### 6. Ejecutar en Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

## 📱 Características Principales

### Autenticación
- Registro e inicio de sesión para dueños de mascotas
- Perfiles específicos para cada mascota
- Información de contacto para adopciones

### Feed Social
- Publicación de fotos y videos
- Sistema de likes y comentarios
- Feed personalizado

### Sistema de Adopción
- Marcado de mascotas disponibles para adopción
- Modal con información de contacto
- Sistema de solicitudes de adopción

### Notificaciones
- Notificaciones en tiempo real
- Diferentes tipos: likes, comentarios, adopciones
- Marcado de leído/no leído

### Tiendas y Mapas
- Directorio de tiendas de mascotas
- Mapa interactivo con ubicaciones
- Sistema de reseñas y calificaciones

## 🎨 Diseño y UI

- **Diseño Responsivo**: Optimizado para móviles y desktop
- **TailwindCSS**: Framework de utilidades CSS
- **Tema Personalizado**: Colores y tipografías específicas
- **Componentes Reutilizables**: Botones, cards, modales consistentes

## 🔧 Scripts Disponibles

- `npm run dev`: Servidor de desarrollo
- `npm run build-css`: Compilar CSS de TailwindCSS
- `npm run build-css-prod`: Compilar CSS para producción (minificado)

## 📄 Licencia

MIT License - ver el archivo LICENSE para más detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes preguntas o necesitas ayuda, puedes:
- Abrir un issue en el repositorio
- Contactar a través de email: info@pawstagram.com