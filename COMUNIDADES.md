# Fichas por comunidad

Una página por comunidad productora, en inglés y en español:

- `/producers/<comunidad>/` y `/es/productores/<comunidad>/`
- Se anuncian solas en la página de productores (sección «Community files»).
- Cada ficha trae su propia imagen para compartir (`og.jpg`), botones de WhatsApp,
  LinkedIn, correo, copiar enlace e imprimir o guardar en PDF.

## La regla de la ficha: cada afirmación lleva su estado

| Estado | Qué quiere decir | Cuándo usarlo |
|---|---|---|
| `seen` · *Seen on site / Visto en campo* | Lo vimos nosotros en una visita y la foto es de ahí | Solo con foto de la comunidad |
| `pending` · *Being documented / En documentación* | Lo sabemos, pero la prueba aún no está publicada | Certificados, cifras, perfiles |

Un comprador va a recorrer la ficha para comprobar lo que decimos. Por eso:

- **Ninguna cifra se publica estimada.** Si el campo `value` está vacío, la página
  muestra «En documentación».
- **Ningún productor se publica sin consentimiento.** La página solo muestra los
  productores con `"consent": true`.
- **Ningún precio** se publica en la ficha.
- **Las fotos salen sin metadatos** (GPS incluido). Placas, rostros o logotipos de
  terceros se difuminan con `blur` antes de publicar.

## Cómo se agrega o se actualiza una comunidad

1. **Fotos.** Los originales quedan fuera del repositorio, que es público. Escribe
   un mapa `nombre-de-la-foto → original` y corre:

   ```bash
   python3 tools/community_photos.py <slug> <carpeta-de-originales> <mapa.json>
   ```

   Esto escribe `docs/assets/img/communities/<slug>/` y `content/communities/<slug>/photos.json`.

2. **Textos y datos.** Copia `content/communities/nimlajacoc/community.json` como
   plantilla y edítalo. Toda cadena va en `en` y en `es`.

3. **Construye:** `python3 tools/build.py`. La página, el sitemap, las migas de pan,
   el hreflang y la tarjeta en «Productores» salen solos.

## Campos de `community.json`

| Campo | Qué es |
|---|---|
| `slug`, `name` | Ruta y nombre de la comunidad |
| `updated` | Fecha de la última actualización (AAAA-MM-DD) |
| `field_record` | Mes de la visita, en los dos idiomas |
| `place` | Ubicación tal como se publica |
| `meta` | Título y descripción para buscadores |
| `hero` | Foto principal, foto pequeña, frase y párrafo de entrada |
| `ledger` | Las afirmaciones, cada una con `status`, foto, título y texto |
| `journey` | El recorrido de la mata al saco, paso por paso |
| `figures` | Cifras: `value: null` publica «En documentación» |
| `producers` | Perfiles (ver abajo) |
| `gallery` | Orden de las fotos de la galería |
| `captions` | Pie de cada foto, que también es su texto alternativo |

### Perfil de productor

```json
{
  "name": "Nombre como la familia quiere aparecer",
  "role": {"en": "Cardamom grower since 1998", "es": "Cultiva cardamomo desde 1998"},
  "photo": "nombre-de-la-foto",
  "facts": [
    {"en": "Plot: 4 manzanas (2.8 ha)", "es": "Parcela: 4 manzanas (2.8 ha)"},
    {"en": "About 9,000 plants", "es": "Unas 9,000 matas"},
    {"en": "Typical harvest: 1,200 kg dried", "es": "Cosecha normal: 1,200 kg en seco"}
  ],
  "quote": {"en": "…", "es": "…"},
  "consent": true
}
```

`consent` va en `true` solo cuando la familia aceptó, en persona, que su nombre,
su foto y sus datos se publiquen.
