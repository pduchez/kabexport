# kabexport.com

Sitio web de KAB EXPORT: cardamomo, miel y vainilla orgánicos de Centroamérica. Está en español (`/`) y en inglés (`/en/`).

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

| Español | Inglés |
|---|---|
| `/` | `/en/` |
| `/productos/` | `/en/products/` |
| `/productos/cardamomo/` | `/en/products/cardamom/` |
| `/productos/miel/` | `/en/products/honey/` |
| `/productos/vainilla/` | `/en/products/vanilla/` |
| `/nosotros/` | `/en/about/` |
| `/sostenibilidad/` | `/en/sustainability/` |
| `/calidad/` | `/en/quality/` |
| `/exportacion/` | `/en/export/` |
| `/contacto/` | `/en/contact/` |
| `/gracias/` | `/en/thanks/` |

## Formulario de contacto

El formulario usa [FormSubmit](https://formsubmit.co), que es gratis y no necesita cuenta. La primera vez que alguien lo envíe, FormSubmit manda un correo de activación a **info@kabexport.com**. Hay que abrir ese correo y hacer clic en el enlace. Desde ese momento, los mensajes llegan a esa bandeja.

## Publicación

- **GitHub Pages:** Settings → Pages → Branch `main`, carpeta `/docs`. El archivo `docs/CNAME` ya contiene `kabexport.com`.
- **Vercel:** importar el repositorio, sin comando de build, con **Output Directory** `docs`.
