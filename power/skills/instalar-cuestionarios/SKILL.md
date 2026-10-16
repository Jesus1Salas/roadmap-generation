---
name: instalar-cuestionarios
description: "Instala los formularios HTML de diagnóstico de adopción (Kiro y Quick Suite) en el workspace destino. Úsala cuando el usuario pida 'instala los cuestionarios', 'prepara los formularios de diagnóstico', o cuando la carpeta cuestionarios/ aún no exista en el workspace. Copia los formularios, los assets (CSS/JS) y el esquema JSON desde este Power al workspace. Solo instala; no llena ni procesa cuestionarios."
---

# Skill: Instalar Formularios de Diagnóstico

Objetivo único: **dejar operativos los formularios HTML** en el workspace destino,
copiando los archivos del Power. Esta skill **solo instala**: no llena formularios,
no ejecuta el generador, no procesa JSON.

## Archivos a instalar (desde la raíz del Power)

El Power entrega **el producto**: los formularios listos para enviar (standalone)
y el esquema (contrato). Copia estos archivos al workspace, bajo `cuestionarios/`:

```
cuestionarios/
  diagnostico_kiro_standalone.html     # un solo archivo, para enviar al cliente
  diagnostico_quick_standalone.html    # un solo archivo, para enviar al cliente
  esquema/diagnostico.schema.json
  esquema/ejemplo_kiro.json
  esquema/ejemplo_quick.json
  README.md
```

Los standalone son autocontenidos (CSS, JS y las fuentes de marca Poppins + Oswald
embebidos): no requieren `assets/` ni conexión. Las fuentes editables
(`diagnostico_*.html`, `assets/` con `fonts/`, `empaquetar.py`)
viven **fuera del producto**, en `cuestionarios_fuente/`, y solo se necesitan si se
va a modificar el diseño o la lógica. Si el entorno no resuelve rutas relativas del
Power, pide al usuario la ruta de la carpeta origen.

## Procedimiento

1. Verifica si `cuestionarios/` ya existe en el workspace. Si existe y tiene los
   formularios, informa que ya está instalado y termina (no sobrescribas sin
   confirmar).
2. Crea la carpeta `cuestionarios/` y su subcarpeta `esquema/`.
3. Copia cada archivo listado arriba conservando su contenido tal cual (UTF-8).
4. Informa en **una sola frase** qué se instaló y cómo abrir los formularios.

## Verificación

- Abrir `cuestionarios/diagnostico_kiro_standalone.html` con doble clic debe
  mostrar el formulario estilizado (paleta eTribe) y funcionar sin conexión.
- Si el generador Python está presente, el JSON de salida debe procesarse con
  `python -m generador.main "ruta/al/diagnostico_[CLIENTE].json"`.

## Reglas

- **Solo instala.** No ofrezcas menús ni proceses datos tras instalar.
- **No inventes contenido** de los formularios: cópialos tal cual del Power.
- Mantén el esquema JSON intacto (es el contrato con el generador).
