# kabexport.com

Sitio web de KAB EXPORT: especias y cacao de comunidades productoras de Alta Verapaz, Guatemala, para Canadá y Estados Unidos. El inglés es el idioma principal y está en la raíz (`/`); el español está en `/es/`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | **El sitio publicado.** Es lo que se sube a GitHub Pages o Vercel. |
| `content/es/`, `content/en/` | El texto de cada página. Edita aquí. |
| `tools/build.py` | Genera las páginas de `docs/` a partir de `content/`. |
| `tools/render-images.mjs` | Genera las imágenes PNG (vista para redes sociales, iconos). |
| `design/preview.html` | Vista previa original con los tres conceptos de logo. |

## Cómo editar un texto

1. Abre el archivo de la página en `content/es/` o `content/en/`, por ejemplo `content/es/honey.html`.
2. Cambia el texto. La primera línea (`<!--meta ...-->`) tiene el título y la descripción que muestra Google.
3. Ejecuta `python3 tools/build.py`.
4. Sube los cambios. El sitio se actualiza solo.

## Páginas

| Inglés | Español |
|---|---|
| `/` | `/es/` |
| `/products/` | `/es/productos/` |
| `/products/cardamom/` | `/es/productos/cardamomo/` |
| `/products/allspice/` | `/es/productos/pimienta-gorda/` |
| `/products/black-pepper/` | `/es/productos/pimienta-negra/` |
| `/products/clove/` | `/es/productos/clavo/` |
| `/products/cinnamon/` | `/es/productos/canela/` |
| `/products/cacao/` | `/es/productos/cacao/` |
| `/products/honey/` (próximamente) | `/es/productos/miel/` |
| `/products/vanilla/` (próximamente) | `/es/productos/vainilla/` |
| `/producers/` | `/es/productores/` |
| `/about/` | `/es/nosotros/` |
| `/sustainability/` | `/es/sostenibilidad/` |
| `/quality/` | `/es/calidad/` |
| `/export/` | `/es/exportacion/` |
| `/contact/` | `/es/contacto/` |
| `/thanks/` | `/es/gracias/` |

Las direcciones de la versión anterior (`/productos/`, `/nosotros/`, `/en/...`, etc.) redirigen a su página nueva. `build.py` genera esas redirecciones como páginas en `docs/` y también las escribe en `vercel.json`.

## Formulario de contacto

El formulario usa [FormSubmit](https://formsubmit.co), que es gratis y no necesita cuenta. La primera vez que alguien lo envíe, FormSubmit manda un correo de activación a **info@kabexport.com**. Hay que abrir ese correo y hacer clic en el enlace. Desde ese momento, los mensajes llegan a esa bandeja.

## Publicación

- **GitHub Pages:** Settings → Pages → Branch `main`, carpeta `/docs`. El archivo `docs/CNAME` ya contiene `kabexport.com`.
- **Vercel:** importar el repositorio, sin comando de build, con **Output Directory** `docs`.
