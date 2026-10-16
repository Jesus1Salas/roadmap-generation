# Plan de Adopción — Proyecto autónomo

Proyecto **autónomo** para generar planes de adopción de **Kiro** y **Amazon Quick
Suite**: captura el diagnóstico del cliente con formularios HTML, y produce todos
los materiales (Roadmap .md + .xlsx, Plan de Enseñanza, Diseño de Actividades,
Guion de Sesión y Configuración de MCPs).

Puede **abrirse como workspace independiente en Kiro** (tiene su propio `.kiro/`
con agentes, workflow, hooks y steering) para probar y mejorar el pipeline.

## Estructura

```
cuestionarios/                          ← raíz del proyecto (autónomo)
  .kiro/
    agents/        # guion-sesion-generator, mcp-config-generator (usados por el workflow),
                   # diseno-actividades-ensenanza (consultor, uso manual)
    workflows/     # plan-adopcion.workflow.json  ← ruta única del pipeline
    hooks/         # permisos auto-aprobados: mcp-config-allow-web,
                   #   pipeline-allow-write, pipeline-allow-generador
    steering/      # CONTEXTO.md, product.md, tech.md, structure.md,
                   #   marca-etribe.md (inclusion: auto — marca para generar materiales)
  generador/       # paquete Python (copia autónoma): parsea el diagnóstico y renderiza
    temas/         # kiro.py, quick_suite.py (+ helpers)
    templates/     # Roadmap_base.xlsx
  formulario_fuente/ # FUENTE editable del formulario (no se comparte con el cliente):
    diagnostico_kiro.html / diagnostico_quick.html  # formularios editables (usan assets/)
    assets/          # estilo.css + formulario.js + fonts/ (Poppins + Oswald woff2, se embeben; sin CDN)
  diagnostico_kiro_standalone.html / *_quick_standalone.html # ENTREGABLE: UN SOLO archivo, para el cliente
  empaquetar.py    # regenera los *_standalone.html desde formulario_fuente/
  esquema/         # diagnostico.schema.json (contrato) + ejemplos
  diagnosticos/    # ENTRADA: deja aquí los diagnostico_[CLIENTE].json del cliente
  power/           # empaquetado como Kiro Power
  clientes/        # SALIDA: clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/
  README.md        # este archivo
```

## Dos versiones del formulario

- **Editable / fuente** (`formulario_fuente/diagnostico_*.html` + `formulario_fuente/assets/`):
  la que ustedes mantienen. Vive en su propia carpeta y **no se comparte** con el cliente.
- **Standalone** (`diagnostico_*_standalone.html`, en la raíz): **un único archivo** con CSS,
  JS y las **fuentes de marca** (Poppins + Oswald) embebidos, sin dependencias de red ni de
  `assets/`. Es la versión **para enviar al cliente**: la abre con doble clic y funciona sin
  conexión. Pesa ~130 KB por las fuentes embebidas.

Tras editar `formulario_fuente/assets/estilo.css` o `formulario_fuente/assets/formulario.js`,
regenera los standalone (se escriben en la raíz):

```powershell
python empaquetar.py          # ambos
python empaquetar.py kiro     # solo uno
```

## Flujo de uso

1. Envía al cliente el **standalone** (`diagnostico_kiro_standalone.html` o
   `diagnostico_quick_standalone.html`).
2. El cliente lo abre, llena los apartados (se autoguarda) y descarga el
   `diagnostico_[CLIENTE].json` (o `.md`).
3. Guarda ese archivo en la carpeta **`diagnosticos/`**.
4. Genera todos los materiales con el **workflow** `plan-adopcion`
   (`.kiro/workflows/plan-adopcion.workflow.json`). Corre el generador (artefactos
   base) y luego, en paralelo, el Guion S1 y los MCPs. Tienes dos formas de indicar
   la entrada:
   - **Automático:** lanza el workflow sin `ruta_diagnostico` y usará el archivo
     **más reciente** de `diagnosticos/` (por fecha de modificación, prefiriendo `.json`).
   - **Específico:** pasa `ruta_diagnostico` (p. ej. con `/workflow`) para forzar un
     archivo concreto, p. ej. `diagnosticos/diagnostico_ACME.json`.
5. O solo los artefactos base, directo con el generador:

   ```powershell
   python -m generador.main "esquema/ejemplo_kiro.json"
   ```

La salida queda en `clientes/{Kiro|Quick Suite}/Recursos_[CLIENTE]/`.

## Artefactos producidos

| Artefacto | Productor |
|-----------|-----------|
| `Roadmap_[CLIENTE].md` + `Roadmap [PRODUCTO] - [CLIENTE].xlsx` | generador |
| `Plan_de_Ensenanza_[CLIENTE].md` | generador |
| `Diseno_Actividades_[CLIENTE].md` (incluye tabla de MCPs recomendados) | generador |
| `Guion_Sesion1_[CLIENTE].md` (S2-S6 bajo demanda) | guion-sesion-generator |
| `Configuracion_MCPs_[CLIENTE].md` | mcp-config-generator |

El workflow corre el generador (artefactos base) y luego, en **paralelo**,
genera el Guion de Sesión 1 y la Configuración de MCPs.

## Training path automático

El formulario deriva el nivel recomendado según la experticia del cliente:

| Experticia en IA | Kiro          | Quick                         |
|------------------|---------------|-------------------------------|
| Nula / poca      | Básico        | Productividad                 |
| Media            | Básico→Builder| Analítica + Automatización    |
| Alta / mucha     | Builder       | Enterprise                    |

## Integraciones / MCPs focalizados

El formulario tiene un apartado de **integraciones** (gestión de tareas,
repositorio, documentación, comunicación, base de datos, observabilidad, nube,
diseño, CRM) donde el cliente indica las herramientas concretas que quiere
conectar. Eso **focaliza** la tabla de MCPs recomendados y el archivo
`Configuracion_MCPs_[CLIENTE].md`: solo se documentan los servidores relevantes,
con nombres de paquete verificados.

## Marca eTribe

Los formularios siguen los lineamientos de marca eTribe:

- **Solo paleta de marca:** azul `#1003A3` y amarillo `#FFC836` dominan; morado
  `#763AC7` y gris `#717C84` como acentos/filetes; secundaria (`#327FEF` `#A8C7FE`
  `#43B12E` `#DA2B1F` `#FF8204`) como acentos ≤20%. Nunca texto blanco sobre amarillo.
- **Tipografía de marca:** Oswald (títulos y realces) + Poppins (cuerpo). Los woff2
  viven en `formulario_fuente/assets/fonts/` y `empaquetar.py` los embebe como data
  URI en el standalone, así se respeta la marca **sin conexión** (sin CDN).

## Principios

- **No se inventan datos.** Un campo sin responder sale vacío (`""`).
- **Fidelidad al origen.** Los valores se guardan tal cual los escribe el cliente.
- **UTF-8** y **español** en todo el contenido.
- El `esquema/diagnostico.schema.json` es el **contrato estable** (versión "1.0"):
  cualquier generador que lo respete puede consumir la salida.
