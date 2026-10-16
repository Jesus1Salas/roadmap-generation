---
inclusion: auto
name: marca-etribe
description: Lineamientos de marca eTribe (paleta de color, tipografía Oswald + Poppins, jerarquía, tono y patrón de composición) para generar o revisar cualquier material con identidad eTribe — formularios HTML, documentos, one-pagers, propuestas, diagramas, gráficas o assets. Actívalo siempre que generes o audites una pieza con marca eTribe.
---

# Marca eTribe — lineamientos para generar documentos

Versión operativa del manual *ETRIBE | Lineamientos de Marca, v1, junio 2023*,
destilada para la generación de materiales en este proyecto. Cubre color,
tipografía, tono y composición. **No cubre logotipado**: en este workspace no
viven los assets de logo (SVG/PNG del isotipo), así que no se generan ni se
redibujan logotipos. Si una pieza necesita el logo, pídelo a quien lleva la marca
en lugar de aproximarlo.

Si algo aquí contradice el manual original (PDF), gana el PDF.

---

## 1. Reglas duras (inviolables)

Cualquier salida que rompa una de estas se rechaza y se rehace:

1. **Solo colores de marca.** Nada de paletas inventadas, "azul parecido", ni los
   colores por defecto de Tailwind, Matplotlib, python-pptx o Google Slides.
2. **Azul `#1003A3` y amarillo `#FFC836` predominan** en cualquier aplicación gráfica.
3. **Prohibido texto o elementos en blanco sobre fondo amarillo `#FFC836`.** Sobre
   amarillo, el texto va en azul `#1003A3`.
4. **La paleta secundaria no excede el 20%** del color del diseño, y **nunca** se usa
   como fondo, título ni párrafo. Solo acentos, subtítulos y elementos gráficos.
5. **Solo Oswald y Poppins.** Oswald exclusivamente en títulos y realces; Poppins en
   cuerpo y subtítulos. Ninguna tercera tipografía.

---

## 2. Color

### 2.1 Paleta principal

| Rol | HEX | Uso |
|---|---|---|
| Azul de marca (dominante) | `#1003A3` | Fondos, títulos, cuerpo, elementos clave |
| Amarillo de marca (dominante) | `#FFC836` | Acentos de alto impacto, realces, pills |
| Morado (acentos/fondos) | `#763AC7` | Acentos, degradados, subtítulos, elementos gráficos |
| Gris | `#717C84` | Filetes, divisores, tablas — **no** cuerpo largo (ver §2.4) |

### 2.2 Paleta secundaria (acentos, tope 20%, nunca fondo/título/párrafo)

| HEX | Uso sugerido |
|---|---|
| `#327FEF` | Azul medio — series de datos, subtítulos |
| `#A8C7FE` | Azul claro — fondos de celda, rellenos suaves |
| `#43B12E` | Verde — estado positivo, "cumple", alza |
| `#DA2B1F` | Rojo — alerta, riesgo, veto, baja |
| `#FF8204` | Naranja — advertencia, estado intermedio |

### 2.3 Combinaciones autorizadas (siempre con azul y/o amarillo de marca)

Naranja + Morado + Azul medio · Morado + Azul medio + Azul claro · Azul medio +
Azul claro + Verde · Azul claro + Verde + Rojo · Verde + Rojo + Naranja · Rojo +
Naranja + Morado.

### 2.4 Neutro sancionado y contraste

- `#F9F8FF` es el único neutro claro permitido (fondo de lámina/página). Cuenta como
  "blanco". Si un neutro no está declarado aquí, no se usa (ni siquiera "oscurecer
  el gris").
- **Contraste:** azul `#1003A3` sobre blanco/`#F9F8FF` es seguro para cuerpo. El gris
  `#717C84` cae por debajo de AA sobre `#F9F8FF` (4.05:1): **el texto auxiliar
  (descripciones, hints, leyendas) va en azul de marca**, no en gris. El gris se
  reserva a filetes y divisores. Sobre amarillo, solo texto azul.

---

## 3. Tipografía

- **Oswald** (condensada) — **solo** títulos y realces. Pesos: Light, Regular, Bold.
  Usarla en párrafos rompe la marca.
- **Poppins** — cuerpo y subtítulos. Pesos: Light (300), Regular (400), Bold (700),
  Black (900). No uses pesos intermedios (500/600/800) que estas familias no traen;
  elige el peso real más cercano para evitar fallback sintético.

### 3.1 Jerarquía (referencia)

| Nivel | Fuente | Caja |
|---|---|---|
| Encabezados y títulos grandes | Oswald Bold | MAYÚSCULAS |
| Subtítulos | Poppins Bold | MAYÚSCULAS |
| Títulos menores / kickers | Oswald o Poppins Bold | MAYÚSCULAS, tracking abierto |
| Cuerpo | Poppins Regular | Caja normal |
| Leyendas / notas | Poppins Regular | Caja normal |

Interlineado: ~1.1× en títulos Oswald, ~1.2× en cuerpo Poppins.

### 3.2 Entrega sin conexión (HTML)

Para materiales HTML que se comparten como archivo suelto, **embebe las fuentes**
(Poppins + Oswald, subconjunto latin) como `@font-face` con data URI; no dependas de
Google Fonts por CDN. En este proyecto los woff2 viven en
`formulario_fuente/assets/fonts/` y `empaquetar.py` los inlinea al generar el
standalone. Deja fallbacks del sistema solo como respaldo.

---

## 4. Tono de marca

eTribe se inclina a: **divertido, juvenil, audaz, simple, moderno**. En la práctica:
títulos que afirman una postura (no etiquetas neutras), lenguaje directo sin jerga
corporativa de relleno, densidad baja por sección, y disposición a recomendar en
lugar de enumerar opciones neutras. Todo el contenido en **español**, UTF-8, con
acentos correctos.

---

## 5. Patrón de composición

Replica este sistema para consistencia inmediata:

- **Encabezado:** marca `ETRIBE | ...` arriba a la izquierda, Poppins, azul, tracking
  amplio, tamaño chico.
- **Marcador de sección:** cuadro azul sólido con el número/etiqueta, seguido del
  título en Oswald Bold mayúsculas con tracking abierto. (Sobre fondo azul, el cuadro
  va amarillo con número azul.)
- **Kicker:** etiqueta de sección corta en mayúsculas, tracking amplio, morado o
  amarillo según el fondo.
- **Hero / portada:** degradado azul→morado con texto blanco y realces amarillos.
- **Cuerpo:** Poppins sobre fondo claro `#F9F8FF` o blanco, texto en azul de marca.
- **Pie / contraportada:** fondo azul sólido `#1003A3`, texto blanco, acentos amarillos.

---

## 6. Checklist antes de entregar

Renderiza la pieza a imagen y revisa:

- [ ] Todos los HEX pertenecen a la paleta de este documento (§2).
- [ ] Azul y/o amarillo de marca predominan visualmente.
- [ ] Ningún texto/elemento blanco sobre fondo amarillo.
- [ ] Secundarios ≤ 20% de la superficie, nunca como fondo ni en títulos.
- [ ] Oswald solo en títulos y realces; cuerpo en Poppins; sin terceras fuentes.
- [ ] Títulos en mayúsculas donde corresponde.
- [ ] Texto auxiliar sobre `#F9F8FF` en azul de marca, no en gris (contraste AA).
- [ ] Sin texto desbordado ni cortado.
- [ ] HTML: fuentes embebidas (sin `url(fonts/...)` ni refs a CDN); sin `http(s)://`.

### Verificación por comando (HTML)

```powershell
# Todos los HEX de la pieza (deben estar en §2):
[regex]::Matches((Get-Content pieza.html -Raw), '#[0-9A-Fa-f]{6}') |
  ForEach-Object { $_.Value.ToUpper() } | Sort-Object -Unique
# Debe dar 0: refs de red y fuentes sin embeber
(Get-Content pieza.html -Raw | Select-String 'https?://|url\(fonts/|googleapis|gstatic' -AllMatches).Matches.Count
```
