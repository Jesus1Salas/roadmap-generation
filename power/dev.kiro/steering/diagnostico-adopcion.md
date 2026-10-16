---
inclusion: manual
---

# Diagnóstico de Adopción — Formularios HTML

Este Power provee formularios HTML para capturar el Cuestionario de Diagnóstico
de forma estructurada y producir un `diagnostico_[CLIENTE].json`.

## Cuándo usarlo

- Cuando se inicia el diagnóstico de un cliente nuevo y se quiere capturar sus
  respuestas sin depender de PDF/DOCX (que requieren parseo heurístico).
- Cuando se necesita que el cliente llene el cuestionario por su cuenta.

## Cómo

1. Entrega al cliente el formulario **standalone**
   (`diagnostico_kiro_standalone.html` o `diagnostico_quick_standalone.html`).
2. Al recibir el `diagnostico_[CLIENTE].json`, genera todos los materiales con el
   workflow `.kiro/workflows/plan-adopcion.workflow.json`, que corre el generador
   y luego delega en paralelo el Guion de Sesión 1 y los MCPs.
3. Para solo los artefactos base, invoca directo el generador:
   `python -m generador.main "ruta/al/diagnostico_[CLIENTE].json"`.

## Contrato (no romper)

- La salida respeta `esquema/diagnostico.schema.json` (`esquema_version: "1.0"`).
- Un campo vacío significa "no reportado"; **no se inventan datos**.
- El `tema` del JSON (`kiro` | `quick_suite`) determina el generador de salida.
- El `training_path.nivel` es una recomendación derivada de la experticia; el
  cliente puede sobrescribirla (`ajustado_por_usuario: true`).

## Reglas al modificar los formularios

- Mantén el esquema JSON como fuente de verdad: si agregas una pregunta, agrégala
  también al esquema y al parser `_parsear_json` del generador.
- Las fuentes editables viven en `cuestionarios_fuente/`; tras editar
  `assets/estilo.css` o `assets/formulario.js`, regenera los standalone con
  `python cuestionarios_fuente/empaquetar.py`.
- Conserva la marca eTribe (`assets/estilo.css`): paleta azul `#1003A3`, amarillo
  `#FFC836`, morado `#763AC7`, gris `#717C84`; tipografía Oswald (títulos) + Poppins
  (cuerpo). Las fuentes se embeben al empaquetar, así el standalone funciona sin CDN.
- Todo el contenido visible en **español**, UTF-8, con acentos correctos.
