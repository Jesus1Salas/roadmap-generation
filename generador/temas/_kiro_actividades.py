"""Diseño de Actividades — contenido detallado de las 6 sesiones para el tema Kiro."""

import re
from ..modelo import DatosCliente
from .estructura import SesionActividad


def _nombre_agente(piloto: str) -> str:
    s = piloto[:50].lower()
    for w in ["la ", "el ", "los ", "las ", "de ", "del ", "y ", "a ", "en ", "para ", "por ", "con "]:
        s = s.replace(w, "")
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9 ]", "", s).strip().replace(" ", "-")[:30] or "caso-piloto"


def actividades(d: DatosCliente):
    from . import kiro
    cfg = kiro.config_recomendada(d)
    tech = cfg["tech"]
    fw, lang, fps = kiro._fw_lang(tech)
    mcps = cfg["mcps"]
    hooks = cfg["hooks"]
    steerings = cfg["steerings"]
    integ = (d.integraciones or "").lower()
    piloto = (d.piloto_mvp or "caso de uso piloto")
    casos = kiro._casos(d)
    nivel = d.nivel_madurez or "?"

    S = []

    # ── Sesión 1 ──
    s1 = SesionActividad("Sesión 1: Setup y Catálogo Kiro (2 horas)", agenda=[
        ("Warm-up", "10 min", "Pregunta: ¿Qué esperan lograr con Kiro esta semana?"),
        ("Setup", "20 min", "Instalación de Kiro IDE/CLI + licencias AWS"),
        ("Catálogo", "25 min", "Demo de workflows: Spec, Plan, Bug Fix, Quick Spec"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica", "35 min", "Hands-on: mapeo de reglas de negocio → primer Steering"),
        ("Cierre", "20 min", "El equipo sale a trabajar con Kiro esta misma semana"),
        ("Buffer", "5 min", "Imprevistos")])
    s1.bloques = [
        "### Actividad 1: Instalación y Configuración\n- **Tipo:** Individual (hands-on)\n"
        "- **Materiales:** Acceso a consola AWS, licencias pre-aprovisionadas\n\n"
        "**Instrucciones:**\n1. Instalar Kiro IDE en cada máquina\n2. Conectar licencia via consola AWS\n"
        "3. Validar que Kiro arranca y se conecta al repositorio",
        "### Actividad 2: Catálogo de Workflows y Artefactos\n- **Tipo:** Grupal (demo + discusión)\n\n"
        "**Instrucciones:**\n1. El facilitador muestra cada workflow en vivo:\n"
        "   - **Spec**: features nuevas (requirements → design → tasks)\n   - **Plan**: planificación de trabajo\n"
        "   - **Bug Fix**: resolver bugs con contexto\n   - **Quick Spec**: cambios pequeños y rápidos\n"
        "2. Mostrar artefactos avanzados: Steering, Hooks, MCP, Skills, Agents\n"
        "3. El equipo identifica qué workflow usaría para su tarea de esta semana",
        "### Actividad 3: Primer Steering Document\n- **Tipo:** Por equipo\n\n**Prompt de ejemplo:**\n```\n"
        f"Ayúdame a crear un steering document para mi proyecto de {fw}.\n"
        f"El proyecto se llama '{d.proyecto[:40]}' y las reglas de negocio principales son:\n"
        "- [Regla 1 del equipo]\n- [Regla 2 del equipo]\n"
        "Genera el archivo .kiro/steering/project-context.md con inclusion: always\n```",
        "### Tips para el facilitador\n- El objetivo es que salgan USANDO Kiro, no solo conociéndolo\n"
        f"- No profundizar en teoría — eso viene en la Sesión 2\n- Nivel del equipo: {nivel}/5 — ajustar velocidad"]
    S.append(s1)

    # ── Sesión 2 ──
    s2 = SesionActividad("Sesión 2: Contexto y Navegación (2 horas)", agenda=[
        ("Warm-up", "10 min", "¿Qué lograron con Kiro esta semana? Compartir wins"),
        ("Teoría", "25 min", "Prompt engineering: estructura completa + prompt socrático"),
        ("Práctica 1", "25 min", "Taller de prompts (5 niveles)"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica 2", "30 min", "Kiro más allá del código: documentación y análisis"),
        ("Cierre", "20 min", "Inicio del playbook + registro de dudas"),
        ("Buffer", "5 min", "Imprevistos")])
    s2.bloques = [
        "### Actividad 1: Taller de Prompt Engineering\n- **Tipo:** Individual → Parejas\n\n"
        "**5 prompts con complejidad creciente:**\n\n**Nivel 1 — Pregunta directa:**\n```\n"
        f"¿Cómo manejo errores async en {lang}?\n```\n\n**Nivel 2 — Con contexto:**\n```\n"
        f"En mi proyecto de {fw} necesito validar formularios.\nYa tengo un componente Form pero no valida en tiempo real.\n"
        "¿Cómo agrego validación reactiva sin romper los tests existentes?\n```\n\n**Nivel 3 — Prompt socrático:**\n```\n"
        f"Necesito rediseñar el módulo de autenticación de mi app {fw}.\nAntes de proponer soluciones, hazme las 5 preguntas más importantes\n"
        "para entender bien el problema y diseñar algo robusto.\n```",
        "### Actividad 2: Kiro Más Allá del Código\n- **Tipo:** Individual\n\n"
        "**Instrucciones (elegir 2):**\n1. Generar un README técnico para un módulo existente\n"
        "2. Extraer requerimientos técnicos de un documento del cliente\n"
        "3. Crear un resumen ejecutivo (no-técnico) de un PR complejo\n4. Generar documentación de API desde el código",
        "### Actividad 3: Inicio del Playbook\n- **Tipo:** Por equipo\n\n**Instrucciones:**\n"
        "1. Crear un documento `playbook.md` en el repo del equipo\n"
        "2. Registrar: mejores prompts, patrones que funcionan, errores comunes\n"
        "3. Este documento se alimentará en cada sesión",
        _tabla_buenas_practicas(),
        "### Tips para el facilitador\n- Recoger dudas acumuladas de la primera semana\n"
        "- Enfatizar que los prompts se iteran\n- Imprimir la tabla de buenas prácticas\n"
        "- El playbook es un documento vivo"]
    S.append(s2)

    # ── Sesión 3 ──
    mcp0 = mcps[0] if mcps else ("MCP relevante", "npx -y @mcp/server", "")
    prueba_mcp = ("Usando Jira, lista los tickets del sprint actual asignados a mi equipo." if "jira" in integ
                  else "Usando GitHub, muestra los PRs abiertos del repositorio principal." if "github" in integ
                  else "Usando el MCP configurado, muestra la información más relevante del proyecto.")
    s3 = SesionActividad(f"Sesión 3: Piezas Avanzadas y Mapeo (2 horas)",
                         subtitulo=f"*Enfoque en el stack: {', '.join(fps[:4]) if fps else 'del equipo'}*",
                         agenda=[
        ("Warm-up", "10 min", "Check-in 15 días: qué artefactos crearon y cuáles usan"),
        ("Teoría", "15 min", "Workflows avanzados + AI responsable"),
        ("Práctica 1", "30 min", f"Conectar MCP + crear Agent para {fw}"),
        ("Pausa", "5 min", "Q&A"),
        ("Práctica 2", "30 min", f"Meta prompting + refactoring de steering en {lang}"),
        ("Cierre", "25 min", "Decisión: qué artefactos mantener, cuáles descartar"),
        ("Buffer", "5 min", "Imprevistos")])
    s3.bloques = [
        f"### Actividad 1: Conexión de MCP\n- **Tipo:** Parejas\n- **MCP a conectar:** {mcp0[0]}\n\n"
        f"**Instrucciones:**\n1. Abrir `.kiro/settings/mcp.json`\n2. Configurar: `{mcp0[1]}`\n"
        "3. Validar con un prompt de prueba\n4. Documentar la configuración\n\n"
        f"**Prompt de prueba:**\n```\n{prueba_mcp}\n```",
        "### Actividad 2: Crear Agent Personalizado para el Caso Piloto\n- **Tipo:** Por equipo\n"
        f"- **Caso de uso:** {piloto[:80]}\n\n**Prompt para crear el agente:**\n```\n"
        f"Crea un agente personalizado en .kiro/agents/ que ayude con:\n{piloto[:120]}\n\n"
        f"El agente debe:\n- Nombre: 'agente-{_nombre_agente(piloto)}.md'\n- Estar optimizado para {fw} / {lang}\n"
        "- Tener tools: read, write, shell\n- Incluir instrucciones específicas del caso\n- Definir el formato de salida\n```",
        "### Actividad 3: Meta Prompting Aplicado al Caso de Uso\n- **Tipo:** Individual\n\n**Prompt de meta prompting:**\n```\n"
        f"Revisa este prompt que uso para: {piloto[:60]}\n[pegar prompt actual]\n\nMejóralo para que:\n"
        f"- Sea más específico para nuestro caso ({piloto[:40]})\n- Considere el stack ({fw}/{lang})\n"
        "- Incluya restricciones y criterios de calidad\n- Genere resultados más completos\n```",
        "### Actividad 4: Refactoring de Steering/Hook\n- **Tipo:** Por equipo\n\n"
        "**Steerings recomendados para refinar:**\n" + "\n".join(f"- `{s[0]}` ({s[1]})" for s in steerings[:3]),
        _mapeo_enfoques(casos, piloto),
        "### Tips para el facilitador\n- Esta sesión es el check-in de los 15 días\n"
        "- Si un artefacto se abandonó, entender por qué\n- El meta prompting es el skill más valioso"]
    if cfg["aws_tooling"]["aplica"]:
        s3.bloques.insert(4, _actividad_aws(cfg["aws_tooling"]))
    S.append(s3)

    # ── Sesión 4 ──
    s4 = SesionActividad("Sesión 4: Problemas Difíciles y Optimización (2 horas)",
                         subtitulo=f"*Casos complejos aplicados a: {piloto[:60]}*", agenda=[
        ("Warm-up", "10 min", "Cada equipo presenta su caso difícil (5 min contexto)"),
        ("Resolución", "40 min", "Atacar 1-2 casos en vivo con Kiro"),
        ("Pausa", "5 min", "Break"),
        ("Patrones", "30 min", "Extracción de patrones compartidos entre equipos"),
        ("Cierre", "30 min", "Plan de acción para casos no resueltos"),
        ("Buffer", "5 min", "Imprevistos")])
    casos_lista = "\n".join(f"{i}. **[{c['prioridad']}]** {c['proceso']}" for i, c in enumerate(casos[:4], 1))
    s4.bloques = [
        "### Casos de Uso a Trabajar en Esta Sesión\n\n*Priorizados desde el diagnóstico:*\n\n" + casos_lista,
        "### Actividad 1: Presentación de Casos Difíciles\n- **Tipo:** Grupal\n\n**Formato por equipo (5 min):**\n"
        "1. ¿Qué caso de uso intentaron resolver con Kiro?\n2. ¿Qué salió mal?\n3. ¿Qué ya intentaron?",
        "### Actividad 2: Resolución en Vivo del Caso Piloto\n- **Tipo:** Grupal (el equipo opera)\n"
        f"- **Caso:** {piloto[:100]}\n\n**Prompt de ejemplo:**\n```\n"
        f"Necesito resolver el siguiente problema relacionado a:\n{piloto[:120]}\n\n"
        f"Contexto: proyecto {fw}/{lang}\nLo que ya intenté: [describir]\n\nAntes de proponer una solución:\n"
        "1. ¿Necesitas ver algún archivo?\n2. ¿Qué restricciones debo considerar?\n3. Propón un approach paso a paso.\n```",
        "### Actividad 3: Extracción de Patrones Compartidos\n- **Tipo:** Grupal\n\n**Instrucciones:**\n"
        "1. ¿Se resolvió con un spec? ¿Un hook? ¿Un agente?\n2. Identificar patrones que aplican a más de un caso\n"
        "3. Crear steering o hook reutilizable\n4. Documentar en el playbook compartido",
        "**Hooks recomendados derivados de patrones comunes:**\n\n"
        + "\n".join(f"- **{h[0]}** (`{h[1]}`): {h[2]}" for h in hooks),
        "### Tips para el facilitador\n- NO resolver por ellos — guiar\n"
        "- Los casos no resueltos deben tener plan de acción escrito\n- Registrar TODOS los casos borde"]
    S.append(s4)

    # ── Sesión 5 ──
    s5 = SesionActividad("Sesión 5: Retro y Gobernanza (2 horas)",
                         subtitulo="*Retrospectiva sobre los casos de uso trabajados y reglas para escalar*", agenda=[
        ("Retro", "10 min", "Registro de tiempos por caso: Kiro vs. método tradicional"),
        ("Feedback", "20 min", "Revisión: qué casos funcionaron y cuáles no"),
        ("Lecciones", "15 min", "¿Qué harían diferente si arrancaran de cero?"),
        ("Pausa", "5 min", "Break"),
        ("Gobernanza", "35 min", "Naming, ownership, onboarding"),
        ("Cierre", "20 min", "Documento de gobernanza firmado por equipo"),
        ("Buffer", "5 min", "Imprevistos")])
    tabla_t = "| Caso de Uso | Tiempo sin Kiro | Tiempo con Kiro | % Ahorro |\n|---|---|---|---|\n"
    tabla_t += "\n".join(f"| {c['proceso'][:50]} | ___ min | ___ min | ___% |" for c in casos[:4])
    s5.bloques = [
        "### Actividad 1: Registro de Tiempos por Caso de Uso\n- **Tipo:** Por equipo\n\n" + tabla_t,
        "### Actividad 2: Revisión de Artefactos por Caso de Uso\n- **Tipo:** Grupal\n\n**Instrucciones:**\n"
        "1. ¿Qué artefactos se usaron por caso? (spec/agent/hook/steering)\n"
        "2. Clasificar: ✅ genera valor | ⚠️ necesita ajuste | ❌ genera fricción\n"
        "3. Identificar qué artefactos aplican a TODOS los casos",
        f"### Actividad 3: Definir Gobernanza\n- **Tipo:** Grupal\n\n**Reglas a definir:**\n\n"
        f"1. **Naming conventions** para artefactos de {lang}:\n"
        "   - Steerings: `[dominio]-[tema].md`\n   - Hooks: `[trigger]-[accion].json`\n   - Agents: `[rol]-[tarea].md`\n\n"
        "2. **Ownership**: quién mantiene cada artefacto compartido\n\n"
        "3. **Onboarding**: qué steerings leer primero, qué agents usar, cómo contribuir al playbook",
        "### Tips para el facilitador\n- El facilitador en silencio el 80% de la sesión\n"
        "- La gobernanza debe ser LIGERA — evitar burocracia"]
    S.append(s5)

    # ── Sesión 6 ──
    s6 = SesionActividad("Sesión 6: Cierre y Autonomía (2 horas)", agenda=[
        ("Warm-up", "10 min", "El equipo presenta lo logrado (sin facilitador)"),
        ("ROI", "30 min", "Construcción del reporte de ROI"),
        ("Pausa", "5 min", "Break"),
        ("Checklist", "25 min", "Checklist post-programa por equipo"),
        ("Demo", "25 min", "Demo final: caso punta a punta sin ayuda"),
        ("Cierre", "20 min", "Presentación a liderazgo + decisión de escala"),
        ("Buffer", "5 min", "Imprevistos")])
    s6.bloques = [
        f"### Actividad 1: Reporte de ROI\n- **Tipo:** Grupal\n- **Métricas:** {(d.metricas_exito or 'tiempos, calidad, adopción')[:80]}\n\n"
        "**Prompt para generar el reporte:**\n```\n"
        f"Genera un reporte de ROI de nuestra adopción de Kiro en {d.empresa}.\n"
        f"Datos de {d.num_equipos_paralelo or 'el equipo'}:\n- Tiempo promedio antes: [X horas/tarea]\n"
        "- Tiempo promedio con Kiro: [Y horas/tarea]\n- Tareas completadas: [N]\n- Créditos consumidos: [Z]\n\n"
        "Genera: tabla comparativa, % ahorro, proyección mensual, recomendación.\n```",
        "### Actividad 2: Checklist Post-Programa\n- **Tipo:** Por equipo\n\n**Cada equipo completa:**\n"
        "- [ ] Steerings activos: [listar]\n- [ ] Hooks configurados: [listar]\n- [ ] Agents en uso: [listar]\n"
        "- [ ] MCPs conectados: [listar]\n- [ ] Playbook actualizado: sí/no\n- [ ] Onboarding documentado: sí/no",
        "### Actividad 3: Demo Final\n- **Tipo:** Por equipo (sin facilitador)\n\n**Instrucciones:**\n"
        "1. Tomar una tarea nueva del backlog\n2. Resolverla de punta a punta: spec → desarrollo → validación\n"
        "3. El facilitador observa pero NO interviene\n4. ¿El equipo es autónomo? Sí/No",
        f"### Tips para el facilitador\n- Esta sesión la lidera el equipo\n"
        f"- El sponsor debe estar presente para el ROI\n- Objetivo: {(d.objetivos or 'validar adopción permanente')[:80]}"]
    S.append(s6)

    return S


def _tabla_buenas_practicas():
    return (
        "### Buenas Prácticas de Prompting\n\n"
        "| # | Práctica | Ejemplo |\n|---|----------|---------|\n"
        "| 1 | **Dar contexto antes de la tarea** | \"Estoy en un proyecto React con TypeScript...\" |\n"
        "| 2 | **Definir el rol** | \"Actúa como un senior backend developer...\" |\n"
        "| 3 | **Ser específico en restricciones** | \"No uses clases, solo funciones puras\" |\n"
        "| 4 | **Pedir formato de salida** | \"Responde con: 1) código, 2) decisiones, 3) tests\" |\n"
        "| 5 | **Iterar, no reescribir** | \"Ajusta la función para manejar array vacío\" |\n"
        "| 6 | **Prompt socrático para problemas complejos** | \"Antes de resolver, hazme 5 preguntas\" |\n"
        "| 7 | **Referenciar archivos existentes** | Usar #File o #Folder |\n"
        "| 8 | **Documentar lo que funciona** | Guardar prompts exitosos en el playbook |\n\n"
        "**Estructura recomendada de un buen prompt:**\n```\n"
        "[ROL] Actúa como un [rol] con experiencia en [dominio].\n"
        "[CONTEXTO] Estoy trabajando en [proyecto] que usa [stack]. El estado actual es [...].\n"
        "[TAREA] Necesito que [acción específica].\n[RESTRICCIONES] - No hacer [X] - Mantener [Y]\n"
        "[FORMATO] Responde con: 1) código, 2) decisiones, 3) edge cases\n```")


def _mapeo_enfoques(casos, piloto):
    filas = "\n".join(f"| {c['proceso'][:35]} | ¿Cómo se resuelve? | ¿Cómo se resuelve? | ¿Cómo se resuelve? | ¿Cómo se resuelve? |"
                      for c in casos[:4])
    return (
        "### Actividad 5: Mapeo de Enfoques por Caso de Uso\n- **Tipo:** Grupal\n\n"
        "**Objetivo:** Explorar las formas en que Kiro puede abordar cada caso.\n\n"
        "| Caso de Uso | Enfoque con Spec | Enfoque con Vibe | Enfoque con Agent | Enfoque con Hook/Steering |\n"
        "|---|---|---|---|---|\n" + filas + "\n\n"
        f"**Prompt para explorar enfoques:**\n```\nTengo el siguiente caso de uso: {piloto[:80]}\n\n"
        "Dame 3 formas de abordarlo con Kiro:\n1. Spec workflow\n2. Agent personalizado\n3. Steering + Hook\n"
        "Para cada uno: pasos, ventajas, desventajas y cuándo elegirlo.\n```")


def _actividad_aws(aws):
    motivo = []
    if aws["necesita_diagramas"]:
        motivo.append("diagramas de arquitectura")
    if aws["necesita_iac"]:
        motivo.append("IaC (CloudFormation/CDK/Terraform)")
    pasos = "\n".join(f"{i}. Configurar **{h['nombre']}**: `{h['comando']}` ({h['requisitos']})"
                      for i, h in enumerate(aws["herramientas"], 1))
    return (f"### Actividad AWS: Herramientas de Diagramas / IaC\n- **Tipo:** Por equipo (hands-on)\n"
            f"- **Contexto:** El cuestionario menciona {' y '.join(motivo)}\n\n**Instrucciones:**\n" + pasos)
