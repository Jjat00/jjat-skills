# Fuentes para la tarjeta, el cierre y las etiquetas

Todas son de Google Fonts con licencia **SIL Open Font License 1.1** (uso comercial libre, se pueden incluir en videos de clientes). Son instancias estáticas `.ttf`, listas para Pillow.

Se eligen en `params.json` con el nombre exacto del archivo:

```json
"font_title": "Montserrat-ExtraBold.ttf",
"font_body": "Montserrat-Medium.ttf"
```

`font_title` va en el título de la tarjeta, el título del cierre y las etiquetas (pills). `font_body` va en el subtítulo, el @ y el texto pequeño del área. Sin estas claves se usa Poppins Bold y Medium. Copia al KIT las dos que elijas.

## Combinaciones probadas por estilo

| Estilo | Título (`font_title`) | Texto (`font_body`) | Cuándo |
|---|---|---|---|
| Limpio (por defecto) | `Poppins-Bold` | `Poppins-Medium` | Locales, negocios, cualquier cosa |
| Inmobiliaria premium | `Montserrat-SemiBold` | `Montserrat-Light` | Casas, apartamentos, proyectos de vivienda |
| Lujo editorial | `PlayfairDisplay-Bold` o `CormorantGaramond-SemiBold` | `Montserrat-Regular` | Fincas, hoteles, haciendas, lotes campestres |
| Cinematográfico | `BebasNeue-Regular` o `Anton-Regular` | `Inter-Medium` | Reels, aperturas con impacto, títulos grandes |
| Técnico / topográfico | `BarlowCondensed-SemiBold` | `Inter-Regular` | Lotes con cotas, áreas y medidas |
| Deportivo / urbano | `Oswald-Bold` | `DMSans-Medium` | Polideportivos, canchas, gimnasios |
| Moderno tech | `SpaceGrotesk-Bold` o `Outfit-Bold` | `Manrope-Medium` | Oficinas, coworkings, parques empresariales |
| Elegante geométrico | `JosefinSans-Bold` o `Raleway-Bold` | `Raleway-Regular` | Restaurantes, boutiques, spas |
| Pesado de marca | `ArchivoBlack-Regular` o `Poppins-Black` | `Poppins-Regular` | Anuncios de venta con precio |

Reglas:
- Máximo dos familias por video. Las serif (Playfair, Cormorant) solo en el título.
- Las condensadas (Bebas, Anton, Oswald, Barlow Condensed) ganan ancho: sirven para nombres largos en la tarjeta.
- Bebas Neue solo tiene mayúsculas: no la uses en `font_body`.
- Si el cliente tiene tipografía de marca con licencia, úsala por encima de estas.

## Inventario

Poppins (Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black) · Montserrat (Light a ExtraBold) · Inter (Regular a Bold) · Bebas Neue · Anton · Oswald (Regular a Bold) · Barlow Condensed (Medium a Bold) · Raleway (Light, Regular, Medium, Bold) · Josefin Sans (Regular, SemiBold, Bold) · Playfair Display (Medium, Bold) · Cormorant Garamond (Medium a Bold) · DM Sans (Regular, Medium, Bold) · Space Grotesk (Regular, Medium, Bold) · Manrope (Medium, Bold, ExtraBold) · Outfit (Light, Regular, Medium, Bold) · Archivo Black.
