# Diagnósticos de entrada

Carpeta de **entrada** del pipeline. Deja aquí los archivos de respuestas del
cuestionario que exporta el cliente:

- `diagnostico_[CLIENTE].json` — formato preferido (lo exporta el formulario).
- `.pdf` / `.docx` / `.md` — fallback con parseo tolerante.

## Cómo la usa el workflow

Al lanzar el workflow `plan-adopcion`:

- **Si pasas `ruta_diagnostico`** (con `/workflow`), se usa exactamente ese archivo.
- **Si lo dejas vacío**, el workflow toma automáticamente el archivo **más
  reciente** de esta carpeta (por fecha de modificación), prefiriendo `.json`.

Así puedes ir acumulando diagnósticos aquí y, en la corrida normal, el pipeline
usa el último que cargaste, sin tener que escribir la ruta cada vez.

> Esta carpeta es solo de entrada; no se commitean los diagnósticos reales de
> clientes (pueden contener datos sensibles).
