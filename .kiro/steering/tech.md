# Stack Técnico y Convenciones del Generador

## Stack

- **Python 3.10+** (probado con 3.11). El paquete principal es `generador/`.
- **Dependencias:** `openpyxl` (Excel); `PyPDF2` solo si se procesan PDFs. La
  entrada preferida es `diagnostico_[CLIENTE].json` (de los formularios HTML);
  también acepta `.pdf`, `.docx` y `.md`.
- **SO objetivo:** Windows / PowerShell. Todo I/O de texto usa `encoding="utf-8"` para evitar `UnicodeEncodeError` con acentos.

## Comandos

Entrada JSON (preferida, estructurada en el origen):

```powershell
python -m generador.main "esquema/ejemplo_kiro.json"
```

Detección automática de tema (también acepta PDF/DOCX/MD):

```powershell
python -m generador.main "ruta/al/diagnostico_CLIENTE.json"
```

Forzar tema si la detección falla:

```powershell
python -m generador.main "ruta/al/Cuestionario.pdf" --tema quick_suite
python -m generador.main "ruta/al/Cuestionario.pdf" --tema kiro
```

Listar cuestionarios disponibles (sin argumentos):

```powershell
python -m generador.main
```

## Arquitectura de `generador/`

El diseño separa **datos**, **contenido por tema** y **renderizado**, de forma que los renderizadores son agnósticos al tema.

- `main.py` — orquestador CLI. `WORKSPACE` = carpeta que contiene `generador/`.
- `cuestionario.py` — parsea la entrada a `DatosCliente`. Para `.json` usa
  `_parsear_json` (mapeo directo del esquema, sin heurísticas); para PDF/DOCX/MD
  usa los parsers tolerantes. `_mapear_integraciones_mcp` pliega el bloque de
  integraciones focalizadas en `d.integraciones` para afinar la tabla de MCPs.
- `modelo.py` — `DatosCliente` (estructura unificada, agnóstica al tema) y `CasoUso`. Un campo vacío significa "no reportado en el cuestionario".
- `render_markdown.py` — construye los 3 `.md`.
- `render_excel.py` — construye el `.xlsx` usando `templates/Roadmap_base.xlsx`.
- `temas/__init__.py` — registro `TEMAS` y `obtener(tema)`.
- `temas/kiro.py`, `temas/quick_suite.py` — cada uno expone la MISMA interfaz:
  - `META` (dict de metadatos, incluye `producto`)
  - `sesiones_roadmap(datos)`, `modulos_plan(datos)`, `actividades(datos)`, `config_recomendada(datos)`
- `temas/estructura.py` — estructuras de datos compartidas de las sesiones.
- `templates/Roadmap_base.xlsx` — plantilla Excel (formato visual estándar).

## Reglas al modificar el generador

- **Mantén la interfaz uniforme entre temas.** Si agregas un método a un tema, agrégalo a ambos (`kiro` y `quick_suite`) para que los renderizadores sigan siendo agnósticos.
- **No inventes datos.** Si un campo no viene en el cuestionario, déjalo vacío; no rellenes con supuestos. Repórtalo en el resumen para que el usuario lo complete.
- **Fidelidad al origen.** Los nombres y valores se toman tal cual del cuestionario (ver `generador/PENDIENTES.md` para casos conocidos de casing/typos). No autocorrijas de forma silenciosa.
- **El `.xlsx` conserva el formato visual** para ambos temas (colores, fuente Arial, columnas, merges). No cambies el layout sin pedirlo.
- Nuevos artefactos de salida van dentro de `clientes/{tema}/Recursos_[CLIENTE]/`.
- Antes de dar por terminado un cambio, corre el generador sobre un cuestionario de ejemplo y verifica que se produzcan los 4 archivos.

## Pendientes conocidos

Consulta `generador/PENDIENTES.md` antes de tocar parseo de cuestionarios: normalización de nombres, extracción de perfiles con texto-guía, truncado de casos de uso y migración de carpetas `Recursos_*` antiguas de la raíz.
