# Power: Diagnóstico de Adopción (Kiro / Quick Suite)

Empaqueta los **formularios HTML de diagnóstico** para capturar el Cuestionario
de Diagnóstico de cada cliente de forma estructurada, y producir la **fuente de
verdad** (`diagnostico_[CLIENTE].json`) que consume el generador de planes de
adopción.

## Qué incluye

- **Formularios HTML** con la identidad de marca eTribe (paleta azul/amarillo y
  tipografía Oswald + Poppins embebida) para Kiro y Amazon Quick Suite, con apartado
  de **integraciones/MCPs** que focaliza la configuración por cliente.
- **Esquema JSON** (`esquema/diagnostico.schema.json`) como contrato estable con
  cualquier generador que respete `esquema_version: "1.0"`.
- **Derivación automática del training path** según la experticia del cliente:
  - Kiro: Básico · Básico→Builder · Builder.
  - Quick: Productividad · Analítica + Automatización · Enterprise.
- **Skill `instalar-cuestionarios`**: copia los formularios al workspace destino.

> El proyecto completo (`cuestionarios/`) es **autónomo**: incluye el generador
> Python, un `.kiro/` propio (agentes, workflow, hooks, steering) y la salida en
> `clientes/`. Puede abrirse como workspace independiente para probar el pipeline
> completo, no solo los formularios.

## Flujo

1. Instala el Power (o copia la carpeta `cuestionarios/` al workspace).
2. Envía al cliente el archivo **standalone** (`diagnostico_kiro_standalone.html`
   o `diagnostico_quick_standalone.html`): un solo HTML, sin dependencias ni
   conexión. La versión modular (en `formulario_fuente/`: `diagnostico_*.html` + `assets/`) es para editar.
3. El cliente lo abre con doble clic y llena los apartados; se autoguarda.
4. Descarga el `JSON` (y opcionalmente el `Markdown`) y te lo regresa; guárdalo en
   la carpeta `diagnosticos/`.
5. Genera los materiales con el workflow `plan-adopcion` (usa el `.json` más reciente
   de `diagnosticos/`, o el que indiques con `ruta_diagnostico`), o corre solo los
   artefactos base con el generador directo:

   ```powershell
   python -m generador.main "diagnosticos/diagnostico_[CLIENTE].json"
   ```

## Reutilización en otro equipo

Este Power es portable: los formularios standalone son HTML estáticos **sin
ninguna dependencia de red** (las fuentes de marca Poppins y Oswald van embebidas
en el propio archivo). El contrato es el
esquema JSON. Un equipo que no use el generador Python de eTribe puede aun así
consumir el JSON con su propio pipeline, siempre que respete el esquema.

## Nota de seguridad

Los formularios **no envían datos a ningún servidor**: todo vive en el navegador
(localStorage) hasta que el usuario descarga el archivo. No hay telemetría ni
llamadas externas de datos.
