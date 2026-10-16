# Pendientes — Generador de Planes de Adopción

Elementos identificados para trabajar más adelante. No bloquean el uso actual del
generador; son mejoras de calidad y robustez.

---

## 1. Normalización del nombre de cliente (casing / typos)

**Contexto:** El nombre del cliente se toma tal cual del cuestionario (cuerpo del PDF
o del nombre de archivo). Esto produce resultados fieles al origen pero a veces con:
- **Casing no canónico:** el cuestionario de TecnoAP trae "Tecnoap" en el cuerpo del
  PDF, por lo que la carpeta y los títulos salen como "Tecnoap" en vez de "TecnoAP".
- **Typos del origen:** el mismo cuestionario reporta la herramienta IA como "Coude"
  (typo de "Claude"); el generador lo respeta en vez de corregirlo.

**Estado:** Decidido dejarlo fiel al cuestionario por ahora.

**Propuesta futura:** Añadir un diccionario de alias/correcciones por cliente
(ej. `alias.json` o un dict en `cuestionario.py`) que mapee:
- Nombre detectado → nombre canónico (ej. "Tecnoap" → "TecnoAP").
- Correcciones de valores conocidos (ej. "Coude" → "Claude") de forma opt-in.

Debe ser explícito y auditable (no autocorrección silenciosa), para no alterar datos
del diagnóstico sin que el usuario lo sepa.

**Archivos afectados:** `generador/cuestionario.py` (parseo/derivación de empresa),
posiblemente `generador/modelo.py` (helper de nombre canónico).

---

## 2. Extracción de perfiles en cuestionarios con texto-guía

**Contexto:** En algunos cuestionarios, los campos "Perfil técnico" / "Perfil de
negocio" quedan en blanco y el parser captura el texto-guía del formulario
(ej. "(administrador de la plataforma o líder de datos) y un").

**Estado:** Mitigado. `modelo._nombre_valido()` descarta ese texto-guía y
`champion_legible()` cae a "Por definir" cuando no hay un nombre real.

**Propuesta futura:** Mejorar la extracción en `_parsear_kiro` / `_parsear_quick`
para no capturar el texto-guía de origen (detectar celdas vacías con más precisión),
de modo que `perfil_tecnico` / `perfil_negocio` queden vacíos en lugar de con ruido.

**Archivos afectados:** `generador/cuestionario.py`.

---

## 3. Casos de uso truncados a mitad de palabra (tema Kiro)

**Contexto:** En cuestionarios Kiro con descripciones largas de casos de uso, la
tabla de la Sección C a veces corta el texto a mitad de palabra
(ej. "a QA La preparación...", "artir de documentación...").

**Estado:** Pendiente. Existía también en el script original.

**Propuesta futura:** Mejorar `_casos_uso_kiro()` para segmentar por filas reales de
la tabla en lugar de por longitud/prioridad, y cortar en límites de palabra.

**Archivos afectados:** `generador/cuestionario.py` (`_casos_uso_kiro`).

---

## 4. Cuestionarios plantilla sin respuestas

**Contexto:** Los cuestionarios `eTribe ENKI` (.md) y `etribe` (.docx) están
parcialmente vacíos (plantilla sin llenar del todo). El generador produce los 4
archivos pero con secciones incompletas donde no hay datos.

**Estado:** Comportamiento correcto (fiel al origen). Documentado por visibilidad.

**Propuesta futura:** Opcional — que `main.py` advierta en el resumen cuántos campos
clave quedaron vacíos, para avisar al usuario que el cuestionario venía incompleto.

**Archivos afectados:** `generador/main.py`.

---

## 5. Migración de las carpetas `Recursos_*` antiguas (raíz)

**Contexto:** Existen carpetas `Recursos_*` en la raíz del workspace (salida previa
al refactor). La nueva estructura vive en `clientes/{Kiro|Quick Suite}/Recursos_*`.

**Estado:** Pendiente de decisión del usuario.

**Propuesta futura:** Una vez validada la nueva estructura, eliminar o archivar las
carpetas `Recursos_*` de la raíz y el script antiguo
`generar_plan_desde_diagnostico.py` para dejar `generador/` como fuente única.

---

## 6. Soporte para el "Cuestionario Técnico" (formato demo, tema Kiro)

**Contexto:** Además del cuestionario estándar de adopción, existe un
**Cuestionario Técnico para la demo** con un esquema distinto: 4 secciones
(CONTEXTO DEL EQUIPO · STACK TECNOLÓGICO · ARQUITECTURA Y PROYECTO · FLUJO DE
TRABAJO), numeración por punto (1.1, 2.3, 4.2…), sin checkboxes y sin tabla de
casos de uso. El parser estándar (`_parsear_kiro`) dejaba casi todos los campos
vacíos porque busca "Empresa/Organización", preguntas "¿…?" numeradas 1..21 y
checkboxes. Ejemplo real: `Cuestionario de Diagnóstico - Grupo Dico.pdf`.

**Estado:** Resuelto. Se agregó:
- `es_cuestionario_tecnico(texto)` — detección por estructura (encabezados de
  sección + numeración por punto).
- `_parsear_tecnico(texto)` — parser dedicado que mapea las 22 preguntas a
  `DatosCliente` (stack, IDEs, VCS/CI-CD, nube, herramienta IA, fricciones,
  tareas repetitivas, etc.). Los enunciados/guías del formulario se eliminan de
  forma **literal** (`_GUIA_TECNICO`), fiel al origen; no se autocorrige.
- Los casos de uso se **derivan** de las áreas de fricción numeradas de la P4.2
  (el cuestionario técnico no trae tabla de casos), con prioridad "Alta".
- El nivel de experiencia con IA es cualitativo (ninguna/básica/…); se conserva
  el texto en `extra["nivel_experiencia_ia"]` y se mapea a 1-5 con
  `_nivel_desde_texto` para los renderizadores.
- Campos sin equivalente en este formato (arquitectura, cultura de cambio,
  acceso AWS) quedan vacíos / "No especificado" (fiel al origen).

Regresión verificada: los cuestionarios estándar (Avansys, TecnoAP, Grupo Luthe)
siguen usando `_parsear_kiro` (`es_cuestionario_tecnico` devuelve `False`).

**Pendiente menor:** En el render de sub-actividades por sesión
(`temas/kiro.py`, líneas ~198 y ~247) los títulos de caso de uso se recortan a
`[:60]` / `[:40]`, lo que puede cortar a mitad de palabra (ej.
"…infraestructur"). Es un tope de presentación previo a este cambio y aplica a
ambos temas. La tabla de "Casos de Uso Candidatos" sí muestra el título completo.
Propuesta futura: recortar en límite de palabra (similar a PENDIENTES #3).

**Archivos afectados:** `generador/cuestionario.py` (detección + parser técnico).
