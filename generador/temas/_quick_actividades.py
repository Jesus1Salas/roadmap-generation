"""Diseño de Actividades — contenido detallado de las 6 sesiones para el tema Quick Suite."""

from ..modelo import DatosCliente
from .estructura import SesionActividad


def actividades(d: DatosCliente):
    from . import quick_suite as Q
    fuente = Q._fuente_conocimiento(d)
    app = Q._app_negocio(d)
    piloto = d.piloto_mvp or "el caso de uso piloto"
    casos = Q._casos(d)
    nivel = d.nivel_madurez or "3"
    champion = d.champion or "el champion designado"
    caps = "\n".join(f"   - **{n}**: {desc}" for n, desc in Q.CAPACIDADES)

    S = []

    # ── Sesión 1 ──
    s1 = SesionActividad("Sesión 1: Setup y Catálogo de Quick Suite (2 horas)", agenda=[
        ("Warm-up", "10 min", "Pregunta: ¿Qué proceso manual les gustaría eliminar primero?"),
        ("Setup", "25 min", f"Acceso a Quick vía SSO / IAM Identity Center + licencias {d.plan_producto or 'Pro'}"),
        ("Catálogo", "25 min", "Demo de las 6 capacidades con ejemplos de negocio"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica", "30 min", "Hands-on: primera pregunta con citas + creación de un Space"),
        ("Cierre", "20 min", "El equipo sale usando Quick esta misma semana"),
        ("Buffer", "5 min", "Imprevistos")])
    s1.bloques = [
        "### Actividad 1: Acceso y Aprovisionamiento\n- **Tipo:** Individual (hands-on)\n"
        "- **Materiales:** Acceso a consola AWS, IAM Identity Center, licencias activas\n\n"
        "**Instrucciones:**\n1. Acceder a Quick con la cuenta de la organización (SSO / IAM Identity Center)\n"
        f"2. Validar que la licencia {d.plan_producto or 'Pro'} está activa\n3. Recorrer la página de inicio y el menú de Spaces",
        "### Actividad 2: Catálogo de las 6 Capacidades\n- **Tipo:** Grupal (demo + discusión)\n\n"
        "**Instrucciones:**\n1. El facilitador muestra cada capacidad con un ejemplo cercano al negocio:\n"
        + caps + f"\n2. El equipo identifica qué capacidad usaría para {piloto[:50]}",
        f"### Actividad 3: Primer Space del Equipo\n- **Tipo:** Por equipo\n\n**Instrucciones:**\n"
        f"1. Crear un Space del área piloto desde el menú Spaces\n"
        "2. Subir un documento de ejemplo o conectar un recurso existente\n"
        "3. Hacer la primera pregunta en lenguaje natural y revisar las citas\n\n**Prompt de ejemplo:**\n```\n"
        "Resume los puntos clave de este documento y cita las secciones exactas\nde donde sale cada punto.\n```",
        f"### Tips para el facilitador\n- La audiencia es de negocio — evitar jerga técnica de AWS\n"
        "- El objetivo es que salgan USANDO Quick, no solo conociéndolo\n"
        f"- Nivel del equipo: {nivel}/5 en IA agéntica — ir con calma en el concepto de \"agente que ejecuta\""]
    S.append(s1)

    # ── Sesión 2 ──
    s2 = SesionActividad("Sesión 2: Contexto, Conexión de Fuentes y Prompting (2 horas)", agenda=[
        ("Warm-up", "10 min", "¿Qué lograron con Quick esta semana? Compartir wins"),
        ("Práctica 1", "30 min", f"Conectar {fuente} a Quick Index + crear Knowledge Base"),
        ("Teoría", "20 min", "Prompt engineering: estructura completa + prompt socrático"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica 2", "30 min", "Chat con citas sobre documentos reales"),
        ("Cierre", "20 min", "Inicio del playbook + registro de dudas"),
        ("Buffer", "5 min", "Imprevistos")])
    s2.bloques = [
        f"### Actividad 1: Conexión de {fuente} a Quick Index\n- **Tipo:** Parejas (o guiado por el champion)\n\n"
        "**Instrucciones:**\n1. Ir a las integraciones de conocimiento de Quick\n"
        f"2. Conectar {fuente} y seleccionar el contenido a indexar\n"
        "3. Crear una Knowledge Base y validar el control de acceso\n4. Esperar la sincronización y confirmar que el contenido es consultable\n\n"
        "**Prompt de prueba tras la conexión:**\n```\n¿Qué acuerdos se tomaron en las últimas actas del equipo?\n"
        "Cita el documento y la fecha de cada acuerdo.\n```",
        "### Actividad 2: Taller de Prompt Engineering\n- **Tipo:** Individual → Parejas\n\n"
        "**Prompts con complejidad creciente:**\n\n**Nivel 1 — Pregunta directa:**\n```\n"
        "¿Cuáles fueron los principales bloqueos del último periodo?\n```\n\n**Nivel 2 — Con contexto:**\n```\n"
        f"Con base en la documentación de {fuente}, resume el estado actual\ny los riesgos abiertos. Cita las fuentes.\n```\n\n"
        "**Nivel 3 — Prompt socrático:**\n```\nQuiero estandarizar cómo documentamos este proceso.\n"
        "Antes de proponer un formato, hazme las 5 preguntas más importantes\npara entender qué necesita el equipo.\n```",
        "### Actividad 3: Inicio del Playbook\n- **Tipo:** Por equipo\n\n**Instrucciones:**\n"
        f"1. Crear un documento \"Playbook Quick — {d.empresa}\" (en {fuente} o en un Space)\n"
        "2. Registrar: mejores prompts, qué fuentes funcionan, formatos de salida útiles\n"
        "3. Este documento se alimenta en cada sesión",
        _buenas_practicas_quick(fuente),
        f"### Tips para el facilitador\n- Confirmar que la sincronización de {fuente} terminó antes de la práctica\n"
        "- Enfatizar la verificación de citas — es el diferenciador de Quick\n- El playbook es un documento vivo"]
    S.append(s2)

    # ── Sesión 3 ──
    s3 = SesionActividad("Sesión 3: Piezas Avanzadas — Agentes, Conectores y BI (2 horas)",
                         subtitulo=f"*Enfoque: conectores {app}/{fuente} y el caso piloto ({piloto[:50]})*", agenda=[
        ("Warm-up", "10 min", "Check-in 15 días: qué crearon y qué usan"),
        ("Teoría", "15 min", "Chat agents vs. autonomous agents + Quick Research"),
        ("Práctica 1", "30 min", f"Conectar {app} (OAuth) + probar consulta"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica 2", "30 min", "Crear chat agent del caso piloto + reporte con Quick Research"),
        ("Cierre", "25 min", "Decisión: qué agentes mantener y qué ajustar"),
        ("Buffer", "5 min", "Imprevistos")])
    s3.bloques = [
        "### Material de Referencia: Agentes y Extensibilidad en Quick\n"
        "- Chat agents conversan; autonomous agents ejecutan y se agendan.\n"
        "- Modos de agente autónomo: Fast (simple), Pro (razonamiento), Custom (control fino).\n"
        "- Conectores de conocimiento leen datos; conectores de acción ejecutan tareas.\n"
        "- MCP y OpenAPI permiten extender Quick a sistemas propios.\n"
        "- Principio de mínimo privilegio: dar a cada agente solo los permisos necesarios.",
        f"### Actividad 1: Conexión del Conector de {app}\n- **Tipo:** Parejas (guiado por el champion)\n"
        f"- **Conector:** {app} (acción, vía OAuth)\n\n**Instrucciones:**\n1. Ir a los conectores de acción de Quick\n"
        f"2. Conectar {app} mediante OAuth\n3. Validar con un prompt de prueba\n4. Documentar la configuración en el playbook\n\n"
        f"**Prompt de prueba:**\n```\nUsando {app}, lista los elementos activos del periodo actual\ncon su estado y responsable.\n```",
        f"### Actividad 2: Crear Chat Agent para el Caso Piloto\n- **Tipo:** Por equipo\n- **Caso de uso:** {piloto[:60]}\n\n"
        "**Instrucciones:**\n1. Crear un chat agent personalizado conversando con Quick\n"
        f"2. Definir instrucciones, fuentes ({app} + Knowledge Base de {fuente}) y capacidades\n"
        f"3. Asignar ownership ({champion})\n\n**Instrucciones de ejemplo para el agente:**\n```\n"
        f"Eres un asistente que prepara: {piloto[:60]} para {d.empresa}.\n\nFuentes:\n- {app} (datos operativos)\n"
        f"- {fuente} (actas y acuerdos)\n\nGenera un entregable con:\n1. Resumen ejecutivo\n2. Métricas / datos clave\n"
        "3. Riesgos y bloqueos\n4. Próximos pasos\nCita siempre la fuente de cada dato.\n```",
        f"### Actividad 3: Reporte con Quick Research\n- **Tipo:** Individual\n\n**Prompt de Quick Research:**\n```\n"
        f"Genera un reporte de {piloto[:50]}.\nCombina los datos de {app} con las actas de {fuente}.\n"
        "Estructura: resumen, métricas, logros, riesgos, próximos pasos.\nCita cada fuente.\n```",
        _mapeo_enfoques_quick(casos, piloto),
        f"### Tips para el facilitador\n- Esta sesión es el check-in de los 15 días\n"
        "- Si un agente no da buenos resultados, revisar instrucciones y fuentes antes de descartarlo\n"
        f"- Nivel {nivel}/5: reforzar la diferencia entre \"responder\" y \"ejecutar acciones\""]
    S.append(s3)

    # ── Sesión 4 ──
    s4 = SesionActividad("Sesión 4: Problemas Difíciles y Automatización (2 horas)",
                         subtitulo=f"*Casos aplicados: {'; '.join(c['proceso'][:35] for c in casos[:3])}*", agenda=[
        ("Warm-up", "10 min", "Cada participante presenta su caso más engorroso (5 min)"),
        ("Automatización", "40 min", f"Construir el Quick Flow del caso piloto"),
        ("Pausa", "5 min", "Break"),
        ("Casos restantes", "30 min", "Prototipar los demás casos (Apps / agent + flow)"),
        ("Cierre", "30 min", "Registro de casos borde y plan de acción"),
        ("Buffer", "5 min", "Imprevistos")])
    casos_lista = "\n".join(f"{i}. **[{c['prioridad']}]** {c['proceso']}"
                            + (f" — {c['frecuencia']}" if c['frecuencia'] else "")
                            for i, c in enumerate(casos[:4], 1))
    s4.bloques = [
        "### Casos de Uso a Trabajar en Esta Sesión\n\n*Priorizados desde el diagnóstico:*\n\n" + casos_lista,
        "### Actividad 1: Presentación de Casos Difíciles\n- **Tipo:** Grupal\n\n**Formato por persona (5 min):**\n"
        "1. ¿Qué caso intentaron resolver con Quick?\n2. ¿Qué salió engorroso o no funcionó?\n3. ¿Qué ya intentaron?",
        f"### Actividad 2: Automatizar el Caso Piloto con Quick Flow\n- **Tipo:** Grupal (el equipo opera)\n"
        f"- **Caso:** {piloto[:60]}\n\n**Instrucciones:**\n"
        f"1. Crear un Quick Flow con pasos: leer {app} → Quick Research → generar documento\n"
        "2. Configurar disparo agendado o manual\n3. Opcional: paso final de notificación\n4. Probar de punta a punta\n\n"
        f"**Descripción del Flow:**\n```\nCrea un flujo que, para el periodo dado:\n"
        f"1. Obtenga de {app} los datos relevantes\n2. Use Quick Research para redactar el entregable con citas\n"
        "3. Genere un documento con el formato estándar del equipo\nDebe poder ejecutarse periódicamente o bajo demanda.\n```",
        "### Actividad 3: Abordar los Casos Restantes\n- **Tipo:** Por caso (repartir entre participantes)\n\n"
        + _prompts_casos_restantes(casos, app, fuente),
        "### Actividad 4: Registro de Casos Borde\n- **Tipo:** Grupal\n\n**Instrucciones:**\n"
        f"1. Registrar límites encontrados (datos faltantes en {app}, formato de actas, permisos)\n"
        "2. Para cada bloqueo, definir un plan de acción\n3. Documentar en el playbook qué funcionó por caso",
        "### Tips para el facilitador\n- NO resolver por ellos — guiar para que el equipo opere Quick\n"
        "- Los casos no resueltos deben tener plan de acción escrito\n- Registrar TODOS los casos borde"]
    S.append(s4)

    # ── Sesión 5 ──
    s5 = SesionActividad("Sesión 5: Retro y Gobernanza (2 horas)",
                         subtitulo="*Retrospectiva sobre los casos trabajados y reglas para escalar entre áreas*", agenda=[
        ("Retro", "15 min", "Registro de tiempos y calidad por caso: Quick vs. manual"),
        ("Feedback", "20 min", "Revisión: qué agentes/flows funcionaron y cuáles no"),
        ("Autonomía", "15 min", "Definir nivel de autonomía por agente"),
        ("Pausa", "5 min", "Break"),
        ("Gobernanza", "30 min", "Ownership, naming, control de acceso, onboarding"),
        ("Cierre", "20 min", "Documento de gobernanza acordado"),
        ("Buffer", "5 min", "Imprevistos")])
    tabla_t = "| Caso de Uso | Tiempo sin Quick | Tiempo con Quick | % Ahorro | Calidad (1-5) |\n|---|---|---|---|---|\n"
    tabla_t += "\n".join(f"| {c['proceso'][:45]} | ___ min | ___ min | ___% | ___ |" for c in casos[:4])
    aut = "| Agente / Flow | Aprobación paso a paso | Autonomía media | Autonomía amplia |\n|---|---|---|---|\n"
    aut += "\n".join(f"| {c['proceso'][:40]} | | | |" for c in casos[:3])
    s5.bloques = [
        "### Actividad 1: Registro de Tiempos y Calidad\n- **Tipo:** Por equipo\n\n" + tabla_t
        + "\n\n*La calidad de la información es una métrica de éxito explícita del cliente.*",
        "### Actividad 2: Revisión de Recursos por Caso\n- **Tipo:** Grupal\n\n**Instrucciones:**\n"
        "1. ¿Qué recursos se usaron por caso? (chat agent, flow, app, Research)\n"
        "2. Clasificar: ✅ genera valor | ⚠️ necesita ajuste | ❌ genera fricción\n"
        "3. Identificar qué recursos sirven a más de un caso",
        "### Actividad 3: Definir Autonomía de los Agentes\n- **Tipo:** Grupal\n\n"
        f"*Autonomía reportada en el diagnóstico: {d.autonomia_agentes or 'aún no definida'}. Decidir aquí:*\n\n" + aut
        + f"\n\n**Recomendación inicial:** empezar con aprobación paso a paso o autonomía media, dado el nivel {nivel}/5.",
        "### Actividad 4: Definir Gobernanza\n- **Tipo:** Grupal\n\n"
        "1. **Naming conventions:**\n   - Spaces: `[área]-[proceso]`\n   - Agentes: `[proceso]-agente`\n   - Flows: `[proceso]-flow`\n"
        f"2. **Ownership:** {champion}; definir responsable por recurso\n"
        "3. **Control de acceso:** por Knowledge Base al compartir entre áreas\n"
        "4. **Onboarding:** qué Space abrir primero, qué agentes usar, cómo contribuir al playbook",
        "### Tips para el facilitador\n- El facilitador en silencio el 80% de la sesión\n"
        "- La gobernanza debe ser LIGERA — evitar burocracia\n- Reforzar el control de acceso al escalar a más áreas"]
    S.append(s5)

    # ── Sesión 6 ──
    s6 = SesionActividad("Sesión 6: Cierre y Autonomía (2 horas)", agenda=[
        ("Warm-up", "10 min", "El equipo presenta lo logrado (sin facilitador)"),
        ("ROI", "30 min", "Construcción del reporte de ROI (tiempo + calidad)"),
        ("Pausa", "5 min", "Break"),
        ("Checklist", "25 min", "Checklist post-programa"),
        ("Demo", "25 min", "Demo final: caso punta a punta sin ayuda"),
        ("Cierre", "20 min", "Presentación a liderazgo + decisión de continuidad"),
        ("Buffer", "5 min", "Imprevistos")])
    s6.bloques = [
        "### Actividad 1: Reporte de ROI\n- **Tipo:** Grupal\n- **Métricas:** tiempo ahorrado + calidad de la información\n\n"
        "**Prompt para generar el reporte:**\n```\n"
        f"Genera un reporte de resultados de la adopción de Quick en {d.empresa}.\nÁreas: {d.areas or 'las participantes'}.\n"
        f"Casos trabajados: {'; '.join(c['proceso'][:40] for c in casos[:3])}.\nDatos:\n"
        "- Tiempo manual promedio por caso: [X]\n- Tiempo con Quick por caso: [Y]\n- Calidad percibida (1-5): [Z]\n\n"
        "Genera: tabla comparativa, % de ahorro, valoración de calidad y recomendación sobre continuar.\n```",
        "### Actividad 2: Checklist Post-Programa\n- **Tipo:** Por equipo\n\n**Cada equipo completa:**\n"
        "- [ ] Spaces activos: [listar]\n- [ ] Knowledge Bases conectadas: [listar]\n- [ ] Chat agents en uso: [listar]\n"
        "- [ ] Quick Flows / Automate configurados: [listar]\n- [ ] Conectores activos: [listar]\n"
        "- [ ] Apps in Quick publicadas: [listar]\n- [ ] Playbook actualizado: sí/no\n- [ ] Ownership definido: sí/no",
        "### Actividad 3: Demo Final\n- **Tipo:** Por equipo (sin facilitador)\n\n**Instrucciones:**\n"
        f"1. Tomar un caso real\n2. Generar el entregable de punta a punta con Quick\n"
        "3. El facilitador observa pero NO interviene\n4. ¿El equipo es autónomo? Sí/No",
        f"### Tips para el facilitador\n- Esta sesión la lidera el equipo\n"
        f"- El sponsor debe estar presente para el ROI\n- Objetivo del cliente: {(d.objetivos or 'validar qué tan funcional resulta usar Quick')[:80]}"]
    S.append(s6)

    return S


def _buenas_practicas_quick(fuente):
    return (
        "### Buenas Prácticas de Prompting\n\n"
        "| # | Práctica | Ejemplo |\n|---|----------|---------|\n"
        f"| 1 | Dar contexto antes de la tarea | \"Con base en las actas de {fuente}...\" |\n"
        "| 2 | Definir el rol | \"Actúa como analista preparando el reporte\" |\n"
        "| 3 | Ser específico en restricciones | \"Máximo 1 página. Solo datos, sin opiniones\" |\n"
        "| 4 | Pedir formato de salida | \"Responde con: 1) resumen, 2) métricas, 3) riesgos\" |\n"
        "| 5 | Pedir citas | \"Cita el documento y la fecha de cada dato\" |\n"
        "| 6 | Iterar, no reescribir | \"Ajusta el informe para incluir la tendencia\" |\n"
        "| 7 | Prompt socrático para problemas complejos | \"Antes de resolver, hazme 5 preguntas\" |\n"
        "| 8 | Documentar lo que funciona | Guardar prompts exitosos en el playbook |\n\n"
        "**Anti-patrones a evitar:**\n- Prompts de una línea sin contexto\n- Pedir todo en un prompt gigante\n"
        "- No revisar las citas de la respuesta\n- No conectar la Knowledge Base y esperar respuestas precisas")


def _mapeo_enfoques_quick(casos, piloto):
    filas = "\n".join(f"| {c['proceso'][:35]} | ¿Cómo se resuelve? | ¿Cómo se resuelve? | ¿Cómo se resuelve? | ¿Cómo se resuelve? |"
                      for c in casos[:4])
    return (
        "### Actividad 4: Mapeo de Enfoques por Caso de Uso\n- **Tipo:** Grupal\n\n"
        "**Objetivo:** Explorar cómo Quick puede abordar cada caso del diagnóstico.\n\n"
        "| Caso de Uso | Chat Agent | Quick Flows | Apps in Quick | Quick Research |\n"
        "|---|---|---|---|---|\n" + filas + "\n\n"
        f"**Ejemplos de enfoques para el caso piloto ({piloto[:40]}):**\n\n"
        "| Enfoque | Cómo funciona | Cuándo usarlo |\n|---|---|---|\n"
        "| **Chat agent** | Un agente dedicado que genera el entregable bajo demanda | Para pedirlo en cualquier momento |\n"
        "| **Quick Research** | Un reporte estructurado que combina fuentes | Para un informe completo con citas |\n"
        "| **Quick Flow** | Un flujo agendado que lo genera solo | Para que se genere automáticamente |\n"
        "| **Apps in Quick** | Una app donde el equipo lo genera sin pensar | Para autoservicio del equipo |")


def _prompts_casos_restantes(casos, app, fuente):
    if len(casos) < 2:
        return "*El diagnóstico registró un solo caso; profundizar en el piloto.*"
    out = ["**Objetivo:** Aplicar lo aprendido del piloto a los demás casos.\n"]
    for c in casos[1:3]:
        out.append(f"**Caso — {c['proceso'][:50]}:**\n```\nCrea un agente/flujo en Quick para: {c['proceso']}\n"
                   f"Combina los datos de {app} y {fuente}. Genera el entregable estructurado\n"
                   "y guárdalo en el Space del equipo. Cita las fuentes.\n```\n")
    return "\n".join(out)
