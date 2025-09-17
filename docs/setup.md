# Configuración Inicial de Pawstagram

Esta guía te ayudará a configurar el proyecto Pawstagram en tu entorno local.

## Prerrequisitos

- Node.js (versión 14 o superior)
- npm o yarn
- Cuenta en Supabase (para base de datos y autenticación)

## Pasos de Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/SoyJadee/Pawstagram.git
cd Pawstagram
```

### 2. Instalar Dependencias

```bash
npm install
```

### 3. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. En el panel de Supabase, ve a Settings > API
4. Copia la URL del proyecto y la clave anónima
5. Edita el archivo `config/config.js`:

```javascript
export const supabaseConfig = {
    url: 'TU_SUPABASE_URL_AQUI',
    anonKey: 'TU_SUPABASE_ANON_KEY_AQUI',
    // ... resto de la configuración
};
```

### 4. Configurar la Base de Datos

1. En Supabase, ve a la sección SQL Editor
2. Ejecuta las consultas SQL del archivo `database/schema.md` para crear las tablas necesarias
3. Ve a Storage y crea los buckets necesarios:
   - `profile-images`
   - `post-images`
   - `store-images`

### 5. Configurar Row Level Security (RLS)

En el SQL Editor de Supabase, ejecuta las políticas de seguridad incluidas en `database/schema.md`.

### 6. Compilar CSS

```bash
npm run build-css
```

### 7. Ejecutar el Servidor de Desarrollo

```bash
npm run dev
```

El proyecto estará disponible en `http://localhost:3000`

## Scripts Disponibles

- `npm run dev` - Ejecuta el servidor de desarrollo
- `npm run build-css` - Compila CSS en modo watch
- `npm run build-css-prod` - Compila CSS para producción (minificado)

## Estructura de Archivos Importantes

- `index.html` - Página principal
- `src/js/main.js` - Punto de entrada de JavaScript
- `src/css/input.css` - Estilos base de TailwindCSS
- `config/config.js` - Configuración de la aplicación
- `database/schema.md` - Esquema de la base de datos

## Próximos Pasos

1. Personaliza la configuración en `config/config.js`
2. Agrega tus propias imágenes en `src/assets/images/`
3. Modifica los colores del tema en `tailwind.config.js`
4. Implementa las funcionalidades de JavaScript para cada componente

## Solución de Problemas

### Error: "Supabase client not initialized"
- Verifica que hayas configurado correctamente las credenciales en `config/config.js`
- Asegúrate de que Supabase esté cargando correctamente desde el CDN

### CSS no se aplica
- Ejecuta `npm run build-css` para compilar los estilos
- Verifica que el archivo `src/css/output.css` se haya generado

### 404 en las rutas
- Asegúrate de que los archivos HTML existan en `src/pages/`
- Verifica que las rutas estén configuradas correctamente en `src/js/utils/router.js`

## Contacto

Si tienes problemas con la configuración, abre un issue en el repositorio de GitHub.