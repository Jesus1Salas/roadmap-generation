---
inclusion: always
---

# CONTEXTO del proyecto — Plan de Adopción (cuestionarios/)

> Documento de contexto para continuar el desarrollo. Resume **qué es**, **cómo
> está construido**, **decisiones tomadas** y **cómo seguir**. Si cambias algo
> estructural, actualiza también este archivo.
> Última actualización: octubre 2026 (se agregó la carpeta de entrada `diagnosticos/`
> y la resolución automática del diagnóstico más reciente en el workflow).

## 1. Qué es este proyecto

Proyecto **autónomo** que genera planes de adopción para **Kiro** y **Amazon Quick
Suite** a partir de un diagnóstico del cliente. Flujo completo:

```
Formulario HTML (cliente lo llena)
   → diagnostico_[CLIENTE].json   (fuente de verdad; se guarda en diagnosticos/)
      → workflow plan-adopcion   (usa el más reciente de diagnosticos/, o el que indiques)
         → generador Python (Roadmap .md + .xlsx, Plan, Actividades)
         → en paralelo: Guion Sesión 1  ∥  Configuración de MCPs
```

Se puede **abrir como workspace independiente en Kiro**: tiene su propio `.kiro/`
(workflow, agentes, hooks, steering) y su copia del generador Python. El
generador corre con `python -m generador.main` desde esta carpeta.

## 2. Estructura real

```
cuestionarios/
  .kiro/
    agents/        guion-sesion-generator.md (Sonnet), mcp-config-generator.md (Haiku),
                   diseno-actividades-ensenanza.md (Sonnet; consultor, uso manual)
    workflows/     plan-adopcion.workflow.json   ← RUTA ÚNICA del pipeline
    hooks/         mcp-config-allow-web.json       (auto-aprueba web_search/web_fetch)
                   pipeline-allow-write.json       (auto-aprueba fs_write/str_replace/fs_append)
                   pipeline-allow-generador.json   (auto-aprueba solo python -m generador.main)
    steering/      CONTEXTO.md (este), product.md, tech.md, structure.md,
                   marca-etribe.md (inclusion: auto — marca para generar/auditar materiales)
  generador/       copia autónoma del paquete Python
    cuestionario.py  parser (JSON directo + PDF/DOCX/MD tolerante)
    modelo.py        DatosCliente, CasoUso
    render_markdown.py / render_excel.py
    main.py          CLI (base de salida = carpeta que contiene generador/)
    temas/           kiro.py, quick_suite.py (+ _kiro_*, _quick_*, estructura.py)
    templates/       Roadmap_base.xlsx
  formulario_fuente/  FUENTE editable (no se comparte con el cliente):
    diagnostico_kiro.html / diagnostico_quick.html          editables (usan assets/)
    assets/           estilo.css, formulario.js, fonts/ (Poppins + Oswald woff2)
  diagnostico_kiro_standalone.html / *_quick_standalone.html  ENTREGABLE: UN archivo, para el cliente
  empaquetar.py    regenera los *_standalone.html desde formulario_fuente/
  esquema/         diagnostico.schema.json (contrato) + ejemplo_kiro.json + ejemplo_quick.json
  diagnosticos/    ENTRADA: diagnostico_[CLIENTE].json (el workflow toma el más reciente)
  power/           empaquetado como Kiro Power (plugin.json, skill, steering)
  clientes/        SALIDA (se crea al generar): clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/
  README.md
```

## 3. Artefactos que produce (por cliente)

En `clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/`:

1. `Roadmap_[CLIENTE].md`
2. `Roadmap [PRODUCTO] - [CLIENTE].xlsx`  (PRODUCTO = "Kiro" o "Amazon Quick Suite")
3. `Plan_de_Ensenanza_[CLIENTE].md`
4. `Diseno_Actividades_[CLIENTE].md`  (incluye tabla "MCPs Recomendados")
5. `Guion_Sesion1_[CLIENTE].md`  (S1 obligatorio; S2-S6 bajo demanda)
6. `Configuracion_MCPs_[CLIENTE].md`

Los 4 primeros los produce el generador Python (determinista, una corrida). El 5 y
6 los producen los sub-agentes en paralelo tras el Diseño de Actividades.

## 4. Cómo correr

```powershell
# pipeline completo (workflow): entrada OPCIONAL ruta_diagnostico
#   lanzar .kiro/workflows/plan-adopcion.workflow.json
#   - sin ruta_diagnostico -> usa el archivo más reciente de diagnosticos/
#   - con ruta_diagnostico  -> fuerza ese archivo (p. ej. diagnosticos/diagnostico_ACME.json)

# solo artefactos base (generador directo):
python -m generador.main "esquema/ejemplo_kiro.json"
python -m generador.main "esquema/ejemplo_quick.json"
python -m generador.main            # sin args: lista diagnósticos disponibles

# regenerar formularios standalone tras editar assets/:
python empaquetar.py                # ambos
python empaquetar.py kiro           # solo uno
```

Requisitos: Python 3.10+ y `openpyxl`. `PyPDF2` solo si se procesan PDFs.

## 5. Contrato de datos (NO romper a la ligera)

`esquema/diagnostico.schema.json`, `esquema_version: "1.0"`. Estructura:

- `tema` (`kiro` | `quick_suite`), `empresa`, `contacto`, `training_path`.
- `secciones`: `experticia`, `contexto_tecnico` (Kiro) / `contexto_negocio` (Quick),
  `casos_uso`, `integraciones_mcp`, `organizacion`, `objetivos`.

Regla de oro: **un campo vacío = "no reportado"; NO se inventan datos.** Fidelidad
al origen (valores tal cual los escribe el cliente).

### Si agregas o cambias una pregunta del formulario

Hay que tocar **cuatro** lugares, en orden, o algo queda desincronizado:

1. `esquema/diagnostico.schema.json` — declara el campo nuevo.
2. `formulario_fuente/diagnostico_kiro.html` y/o `formulario_fuente/diagnostico_quick.html`:
   - el `<input>/<select>` en el apartado correspondiente,
   - `construirSecciones(...)` (mapea el campo al JSON de salida),
   - `aMarkdown(...)` (si debe salir también en el `.md`).
3. `generador/cuestionario.py` → `_parsear_json` (y helpers `_mapear_json_kiro` /
   `_mapear_json_quick` / `_mapear_integraciones_mcp`) para leer el campo.
4. Regenerar standalone: `python empaquetar.py`. Actualizar `esquema/ejemplo_*.json`.

## 6. Decisiones de diseño (por qué está así)

- **JSON como fuente de verdad.** El formulario captura estructurado en el origen,
  eliminando el parseo heurístico frágil de PDF/DOCX. El `.md` es compatibilidad.
- **Training path automático.** Se deriva de la autoevaluación de experticia
  (`formulario.js`, pesos + umbrales). El cliente puede sobrescribirlo
  (`ajustado_por_usuario: true`). Mapa:
  - Kiro: Básico · Básico→Builder · Builder.
  - Quick: Productividad · Analítica+Automatización · Enterprise.
- **Integraciones MCP focalizadas.** El apartado "Integraciones" captura las
  herramientas concretas (Jira, GitHub, Postgres, Slack...). `_mapear_integraciones_mcp`
  las pliega en `d.integraciones` DESPUÉS de los mappers por tema, para que
  `config_recomendada` (en `temas/kiro.py`) arme la tabla de MCPs correcta.
- **Paralelismo real donde aporta.** El generador produce los 4 base juntos
  (rápido, determinista) — no se paraleliza eso. Lo que corre en paralelo es el
  Guion S1 (creativo) y los MCPs (investigación web).
- **Workflow como ruta única.** Se eliminó el agente orquestador y el viejo
  `plan-ensenanza-generator` para no tener caminos duplicados. El workflow usa
  `wf-coder` (built-in) + `guion-sesion-generator` + `mcp-config-generator`.
- **Nombres de paquete MCP verificados.** En `temas/kiro.py` se usan los oficiales
  (`@modelcontextprotocol/server-*`, Atlassian remoto, AWS Docs), no los inventados
  `@anthropic/mcp-*`. El agente de MCPs los re-verifica en la web al documentar.
- **Tipografía de marca embebida (sin CDN).** Los formularios usan las fuentes de
  marca eTribe: **Oswald** (títulos y realces) y **Poppins** (cuerpo), regla dura
  del manual de marca. Los woff2 (subconjunto latin) viven en
  `formulario_fuente/assets/fonts/`; `empaquetar.py` los convierte a data URI
  base64 al generar el standalone, así el archivo funciona **sin conexión y sin
  CDN**. El standalone pesa ~130 KB (antes ~60 KB) por las fuentes embebidas.
  Paleta eTribe (solo colores de marca): azul `#1003A3`, amarillo `#FFC836`, morado
  `#763AC7`, gris `#717C84` (filetes/divisores; sobre el papel `#F9F8FF` cae bajo AA,
  por eso el texto auxiliar va en azul de marca), secundaria `#327FEF` `#A8C7FE`
  `#43B12E` `#DA2B1F` `#FF8204` (acentos, tope 20%).
- **Modelo por agente (bajo consumo sin perder calidad).** Cada agente declara su
  `model` en el frontmatter:
  - `mcp-config-generator` → `claude-haiku-4.5`: su tarea es mecánica (extraer la
    tabla, investigar en la web, rellenar plantilla JSON/MD) y es la de mayor
    volumen de llamadas; un modelo liviano basta.
  - `guion-sesion-generator` y `diseno-actividades-ensenanza` → `claude-sonnet-4`:
    producen redacción larga y contextualizada (el guion y el diseño instruccional
    SON el producto), donde la calidad de escritura importa; Haiku se notaría pobre.
  Formato del ID: punto para la versión menor (`claude-haiku-4.5`); el guion entre
  números falla ("Invalid model ID"). Si un ID no está disponible en el entorno,
  Kiro lo rechaza — ajustar a `claude-haiku-4`/`auto` según corresponda.

## 7. Seguridad

- El agente `mcp-config-generator` trata el contenido web como **no confiable**:
  ignora instrucciones embebidas, solo extrae datos técnicos, no ejecuta código
  descargado, marca con ⚠️ fuentes sospechosas/typosquatting. Solo documenta
  comandos estándar (`npx -y`, `uvx`, `pip install`) desde dominios verificados.
- Los formularios **no envían datos**: todo vive en `localStorage` hasta que el
  usuario descarga el archivo.

### Permisos auto-aprobados (para correr el pipeline sin confirmaciones)

El pipeline corre de punta a punta sin pedir confirmación gracias a tres hooks
`PreToolUse` en `.kiro/hooks/`. Importante: **los hooks no filtran por agente**;
aplican a cualquier invocación de esas tools en el workspace (es el mismo modelo
del hook de web ya existente).

- `mcp-config-allow-web` — auto-aprueba `remote_web_search` y `web_fetch` (el
  agente de MCPs investiga en la web).
- `pipeline-allow-write` — auto-aprueba `fs_write` / `str_replace` / `fs_append`
  (los agentes escriben los `.md` en `clientes/`).
- `pipeline-allow-generador` — **acotado**: auto-aprueba comandos de terminal solo
  cuando invocan `python -m generador.main` o la detección del diagnóstico más
  reciente (`Get-ChildItem` sobre `diagnosticos/`). Cualquier OTRO comando de
  terminal NO lo aprueba este hook y sigue pidiendo confirmación. Se dejó acotado a
  propósito: auto-aprobar todo el shell abriría demasiada superficie.

## 8. Verificación antes de dar por terminado un cambio

1. `python -m generador.main "esquema/ejemplo_kiro.json"` y `..._quick.json` →
   confirmar que se producen los 4 archivos base sin error.
2. Si tocaste el esquema/parser: validar los ejemplos contra el esquema
   (`jsonschema.validate`) y confirmar que `_parsear_json` mapea sin perder datos.
3. Si tocaste formularios/assets: `python empaquetar.py` y confirmar que los
   standalone quedan autocontenidos: sin `href="assets/"`, sin `url(fonts/`, sin
   CDNs ni refs `http(s)://`, y con las fuentes de marca embebidas como
   `data:font/woff2`. Si tocaste el estilo, valida la marca (solo paleta eTribe,
   Oswald en títulos / Poppins en cuerpo, nada blanco sobre amarillo).
4. **Limpia la salida demo** (`clientes/`) que generes al probar; no la commitees.
5. Mantén la **interfaz uniforme entre temas**: si agregas un método a `kiro.py`,
   agrégalo también a `quick_suite.py` (los renderizadores son agnósticos al tema).

## 9. Pendientes / ideas futuras

- Guiones S2-S6: hoy bajo demanda vía `guion-sesion-generator`; podría añadirse una
  entrada opcional al workflow para generar un rango de sesiones.
- `generador/PENDIENTES.md` documenta casos conocidos del parseo de PDF/DOCX
  (normalización de nombres, typos). El flujo JSON los evita, pero el fallback
  PDF/DOCX sigue sujeto a esos límites.
- El `tema` se puede forzar con `--tema kiro|quick_suite` si la detección falla;
  con JSON el `tema` viene explícito y no hace falta.
