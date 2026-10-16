# Estructura del Proyecto (workspace autónomo)

Este directorio es **autónomo**: puede abrirse como workspace independiente en Kiro
para probar y mejorar el pipeline de materiales de adopción, sin depender del
proyecto padre.

## Idioma

Todo el contenido (código, comentarios, artefactos y respuestas) se escribe en
**español**. Respeta acentos y usa UTF-8.

## Layout

```
cuestionarios/                         ← raíz de este workspace
  .kiro/
    agents/            # guion-sesion-generator, mcp-config-generator (usados por el workflow),
                       # diseno-actividades-ensenanza (consultor, uso manual)
    workflows/         # plan-adopcion.workflow.json  ← ruta única del pipeline
    hooks/             # permisos auto-aprobados para el pipeline:
                       #   mcp-config-allow-web     (web_search / web_fetch)
                       #   pipeline-allow-write     (fs_write / str_replace / fs_append)
                       #   pipeline-allow-generador (solo el comando python -m generador.main)
    steering/          # este directorio (CONTEXTO, product, tech, structure +
                       #   marca-etribe.md: lineamientos de marca, inclusion auto)
  generador/           # paquete Python (copia autónoma): parsea el diagnóstico y renderiza
    temas/             # contenido por tema (kiro, quick_suite)
    templates/         # Roadmap_base.xlsx
  formulario_fuente/   # FUENTE editable (no se comparte): diagnostico_*.html + assets/
    diagnostico_kiro.html / diagnostico_quick.html     # formularios editables (usan assets/)
    assets/            # estilo.css + formulario.js + fonts/ (Poppins + Oswald, se embeben; sin CDN)
  diagnostico_kiro_standalone.html / *_quick_standalone.html  # ENTREGABLE: un solo archivo, para el cliente
  empaquetar.py        # regenera los *_standalone.html desde formulario_fuente/
  esquema/             # diagnostico.schema.json (contrato) + ejemplos
  diagnosticos/        # ENTRADA: diagnostico_[CLIENTE].json (el workflow usa el más reciente)
  power/               # empaquetado como Kiro Power
  clientes/            # SALIDA: clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/
```

## Entrada y salida

- **Entrada:** `diagnostico_[CLIENTE].json` (de los formularios HTML). El generador
  también acepta `.pdf`/`.docx`/`.md`. Se dejan en la carpeta `diagnosticos/`.
- **Salida:** `clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/` (dentro de este
  directorio; la base es la carpeta que contiene `generador/`).

### Carpeta de entrada `diagnosticos/`

El cliente entrega su `diagnostico_[CLIENTE].json`; se guarda en `diagnosticos/`.
Al lanzar el workflow `plan-adopcion`:

- Si pasas `ruta_diagnostico`, se usa ese archivo exacto.
- Si lo omites, el primer paso resuelve el archivo **más reciente** de
  `diagnosticos/` por fecha de modificación (mtime), prefiriendo `.json` sobre
  `.pdf/.docx/.md`. Ignora `README.md`, `.gitkeep` y ocultos.

## Convención de nombres de salida

- `Roadmap_[CLIENTE].md`
- `Roadmap [PRODUCTO] - [CLIENTE].xlsx`  (PRODUCTO = "Kiro" o "Amazon Quick Suite")
- `Plan_de_Ensenanza_[CLIENTE].md`  (sin ñ ni acentos en el nombre de archivo)
- `Diseno_Actividades_[CLIENTE].md`  (sin ñ ni acentos en el nombre de archivo)
- `Guion_Sesion[N]_[CLIENTE].md`  (S1 obligatorio; S2-S6 bajo demanda)
- `Configuracion_MCPs_[CLIENTE].md`  (generado por el agente de MCPs)

El `[CLIENTE]` se deriva del diagnóstico tal cual (fidelidad al origen).

## Pipeline de orquestación

```
diagnostico_[CLIENTE].json
   │  python -m generador.main  (determinista, una corrida)
   ▼
Roadmap.md + Roadmap.xlsx + Plan_de_Ensenanza.md + Diseno_Actividades.md
   │
   ├──────────────┬───────────────   (paralelo, tras Diseño de Actividades)
   ▼              ▼
Guion_Sesion1   Configuracion_MCPs   (S2-S6 del guion: bajo demanda)
```

Dispáralo con el workflow `.kiro/workflows/plan-adopcion.workflow.json`
(entrada **opcional** `ruta_diagnostico`: si se omite, usa el más reciente de
`diagnosticos/`). Es la ruta única del pipeline.

## Cómo probar aquí

```powershell
# generar artefactos base de un ejemplo
python -m generador.main "esquema/ejemplo_kiro.json"
# regenerar formularios standalone tras editar estilo/lógica
python empaquetar.py
```

## Reglas

- **No inventes datos.** Campo vacío = "no reportado".
- **Fidelidad al origen.** Valores tal cual del diagnóstico.
- Mantén la **interfaz uniforme entre temas** (kiro y quick_suite exponen los mismos métodos).
- El `.xlsx` conserva el formato de la plantilla.
- Si agregas una pregunta al formulario, edítala en `formulario_fuente/diagnostico_*.html`,
  actualízala también en `esquema/` y en el parser `_parsear_json` de
  `generador/cuestionario.py`, y regenera los standalone con `python empaquetar.py`.
- **Estilo = marca eTribe.** Solo paleta de marca (azul/amarillo dominan, nada blanco
  sobre amarillo) y tipografía Oswald (títulos) + Poppins (cuerpo), embebidas por
  `empaquetar.py` para funcionar sin conexión.
