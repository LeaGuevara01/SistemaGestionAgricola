# Elorza Frontend

## Descripción

Elorza es un sistema de gestión agrícola diseñado para facilitar el manejo de inventarios, compras, proveedores y máquinas. Esta aplicación frontend está construida con React y utiliza Vite como herramienta de construcción.

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de archivos:

```
elorza-frontend
├── public
│   ├── index.html          # Archivo HTML principal
│   └── fotos               # Directorio para imágenes
├── src
│   ├── App.jsx             # Componente principal de la aplicación
│   ├── main.jsx            # Punto de entrada de la aplicación React
│   ├── components          # Componentes reutilizables
│   ├── config              # Configuración de la aplicación
│   ├── hooks               # Hooks personalizados
│   ├── pages               # Páginas de la aplicación
│   ├── services            # Servicios para manejar la lógica de negocio
│   ├── styles              # Estilos globales y específicos
│   └── utils               # Utilidades y constantes
├── .env                    # Variables de entorno
├── package.json            # Configuración de npm
├── vite.config.js          # Configuración de Vite
└── start.sh                # Script para iniciar el entorno de desarrollo
```

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   ```
2. Navega al directorio del proyecto:
   ```
   cd elorza-frontend
   ```
3. Instala las dependencias:
   ```
   npm install
   ```

## Uso

Para iniciar la aplicación en modo desarrollo, ejecuta:

```
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.
