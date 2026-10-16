"""Plan de Enseñanza — contenido de los 6 módulos para el tema Kiro."""

from ..modelo import DatosCliente
from .estructura import ModuloPlan


def _material(mods, MODULOS):
    out = []
    for mid in mods:
        m = MODULOS[mid]
        out.append(f"- **{mid} — {m['titulo']}** ({m['subtitulo']})")
        out.extend(f"  - {p}" for p in m["puntos"])
    return out


def modulos_plan(d: DatosCliente):
    from . import kiro
    tech = kiro._tecnologias(d.stack)
    fw, lang, fps = kiro._fw_lang(tech)
    stack_aplicado = ", ".join(fps[:4]) if fps else "el stack del equipo"
    num_eq = d.num_equipos_paralelo or "el equipo"
    aws = kiro._detectar_aws_tooling(d)
    M = kiro.MODULOS_ETRIBE

    mods = []

    # Módulo 1
    mods.append(ModuloPlan(
        titulo="Módulo 1: Setup y Catálogo Kiro", semana="1",
        contenido_tematico=[
            "Instalación de Kiro IDE / CLI", "Asignación de licencias y configuración AWS",
            "Presentación de interfaces: IDE y CLI", "Artefactos base: Vibe sessions",
            "Los 4 workflows del IDE: Spec, Plan, Bug Fix, Quick Spec",
            "Artefactos avanzados: Steering, Hooks, MCP/Powers, Skills/Agents",
            "Hands-on: mapeo de reglas de negocio a Steering"],
        objetivos=[
            "Instalar y configurar Kiro en su entorno de trabajo",
            "Identificar los 4 workflows principales y cuándo usar cada uno",
            "Distinguir entre artefactos base y avanzados",
            "Crear un primer Steering document basado en reglas de negocio reales",
            "Salir de la sesión listo para trabajar en su proyecto esa misma semana"],
        actividades=[
            "Instalación guiada de Kiro IDE en cada máquina",
            "Demo en vivo de cada workflow (Spec, Plan, Bug Fix, Quick Spec)",
            "Hands-on: cada equipo crea su primer Steering con reglas de negocio reales"],
        criterios=[
            "Kiro instalado y operativo en todas las máquinas del equipo",
            "El equipo identifica correctamente qué workflow usar para cada caso",
            "Al menos un Steering document creado por equipo"]))

    # Módulo 2
    mods.append(ModuloPlan(
        titulo="Módulo 2: Contexto y Navegación", semana="1-2",
        contenido_tematico=[
            "Fundamentos de prompt engineering", "Kiro más allá del código: casos de uso no-código",
            "Prompt socrático", "Construir buenos prompts (estructura completa)",
            "Generación de reportes y documentación desde plantillas",
            "Análisis de documentación existente → requerimientos técnicos",
            "Comunicación técnica → no-técnica"],
        objetivos=[
            "Construir prompts efectivos con la estructura rol-contexto-tarea-restricciones-formato",
            "Usar Kiro para tareas no-código (documentación, análisis, comunicación)",
            "Aplicar prompt socrático para estructurar problemas complejos",
            "Extraer requerimientos técnicos a partir de documentación existente",
            "Generar documentación técnica de calidad (READMEs, APIs, diagramas)"],
        actividades=[
            "Taller de prompt engineering con 5 niveles de complejidad",
            "Ejercicio: generar un reporte estandarizado desde plantilla del equipo",
            "Análisis de un documento real → extracción de tareas técnicas",
            "Hands-on: mapeo de reglas de negocio a Steering (continuación)",
            "Inicio del playbook del equipo"],
        criterios=[
            "Cada participante construye prompts con estructura completa",
            "Se ha generado al menos un documento no-código con Kiro",
            "Playbook del equipo iniciado con primeras entradas"],
        material_referencia=["Esta sesión cubre los **Módulos 1-4** del material eTribe:", ""]
                            + _material(["M01", "M02", "M03", "M04"], M)))

    # Módulo 3
    m3 = ModuloPlan(
        titulo="Módulo 3: Piezas Avanzadas y Mapeo", semana="2",
        subtitulo=f"**Stack aplicado:** {stack_aplicado}",
        contenido_tematico=[
            "Workflows avanzados con Kiro", "AI responsable: límites y buenas prácticas",
            f"Conexión de MCP: {(d.integraciones or 'herramientas del equipo')[:40]} vía OAuth",
            f"Diseño de Skills y Agents personalizados para {fw}",
            "Meta prompting: generar/refinar agentes especializados",
            "Check-in 15 días: qué artefactos se usan, cuáles se abandonaron",
            "Refactoring en vivo de un steering o hook que no funciona bien"],
        objetivos=[
            f"Conectar MCPs relevantes para su stack ({', '.join(fps[:3]) if fps else 'del equipo'})",
            f"Diseñar e implementar un Agent personalizado para tareas de {fw}",
            "Aplicar meta prompting para mejorar prompts existentes",
            "Evaluar críticamente qué artefactos aportan valor y cuáles descartar",
            "Refactorizar un steering o hook que no da buenos resultados"],
        actividades=[
            f"Configurar MCP de {(d.integraciones or 'Jira/GitHub')[:30]} vía OAuth",
            f"Crear un Agent especializado para {fw} (ej: generador de componentes)",
            f"Meta prompting: mejorar un prompt de {lang} que el equipo ya usa",
            "Check-in grupal: revisar artefactos creados en las 2 semanas previas",
            "Refactoring en vivo de un steering que no produce buenos resultados"],
        criterios=[
            "Al menos un MCP conectado y validado por equipo",
            "Un Agent personalizado funcional por equipo",
            "El equipo identifica qué artefactos mantener y cuáles descartar"],
        material_referencia=["Esta sesión cubre los **Módulos 5-6** del material eTribe:", ""]
                            + _material(["M05", "M06"], M))
    if aws["aplica"]:
        for h in aws["herramientas"]:
            m3.actividades.append(f"**[AWS]** Conectar `{h['nombre']}` — {h['descripcion']}")
    mods.append(m3)

    # Módulo 4
    mods.append(ModuloPlan(
        titulo="Módulo 4: Problemas Difíciles y Optimización", semana="3-4",
        subtitulo=f"**Stack aplicado:** {stack_aplicado}",
        contenido_tematico=[
            "Cada equipo presenta su caso más complejo/bloqueante",
            "Resolución en vivo con Kiro (1-2 casos de mayor valor)",
            "Extracción de patrones: ¿spec? ¿hook? ¿agente dedicado?",
            f"Patrones compartidos entre {num_eq}",
            "Steering/Hooks reutilizables entre equipos", "Plan de acción para casos no resueltos"],
        objetivos=[
            f"Resolver problemas complejos de {fw}/{lang} usando Kiro de forma autónoma",
            "Identificar si un problema se resuelve mejor con spec, hook o agente",
            "Compartir y reutilizar artefactos entre equipos",
            "Documentar casos borde con plan de acción claro"],
        actividades=[
            f"Cada equipo presenta su caso difícil de {fw} (5 min de contexto)",
            "Resolución en vivo: el facilitador guía pero el equipo opera Kiro",
            f"Identificar patrones de {lang} compartidos entre equipos",
            "Crear specs/hooks reutilizables a partir de los patrones encontrados",
            "Registro de casos borde y bloqueos reales"],
        criterios=[
            "Al menos 1 caso complejo resuelto por equipo usando Kiro",
            "Patrones compartidos identificados y documentados",
            "Casos no resueltos tienen plan de acción claro"]))

    # Módulo 5
    mods.append(ModuloPlan(
        titulo="Módulo 5: Retro y Gobernanza", semana="5-6",
        subtitulo=f"**Stack aplicado:** {stack_aplicado}",
        contenido_tematico=[
            "Retro/feedback: tiempos Kiro vs. método tradicional",
            "Revisión de casos borde documentados",
            "Retroalimentación abierta: confianza y seguridad con la herramienta",
            "Lecciones aprendidas: qué harían diferente",
            f"Gobernanza: reglas para compartir artefactos entre {num_eq}",
            "Ownership de artefactos compartidos", "Naming conventions y estructura de archivos",
            "Proceso de onboarding con artefactos existentes"],
        objetivos=[
            "Medir y reportar el impacto de Kiro con datos cuantitativos",
            f"Definir reglas de gobernanza para artefactos de {fw}/{lang}",
            "Establecer ownership y naming conventions para escalar",
            "Diseñar el proceso de onboarding para nuevos miembros",
            "Operar sin apoyo externo del facilitador"],
        actividades=[
            "Registro y comparativa de tiempos: Kiro vs. método tradicional por equipo",
            f"Revisión de hooks y steerings de {fw}: cuáles generaron valor, cuáles fricción",
            "Definir naming conventions para steerings, hooks, specs, agents",
            "Crear documento de onboarding: cómo un nuevo miembro arranca con los artefactos",
            "Definir ownership: quién mantiene cada artefacto compartido"],
        criterios=[
            "Datos de tiempos comparativos registrados por equipo",
            "Documento de gobernanza creado con naming y ownership",
            "Proceso de onboarding definido", "El equipo opera sin soporte del facilitador"]))

    # Módulo 6
    mods.append(ModuloPlan(
        titulo="Módulo 6: Cierre y Autonomía", semana="6-7",
        contenido_tematico=[
            "Análisis de ROI: tiempo ahorrado por tipo de tarea y por equipo",
            "Reporte de consumo de créditos y governance final",
            "Presentación de resultados al liderazgo",
            "Checklist de arranque post-programa", "Equipo autónomo con Kiro"],
        objetivos=[
            "Medir y presentar el ROI con datos reales",
            "Operar Kiro de forma 100% autónoma sin soporte externo",
            "Mantener y evolucionar los artefactos del equipo",
            "Incorporar nuevos miembros usando el proceso de onboarding"],
        actividades=[
            "Construcción del reporte de ROI con datos de las 6 semanas",
            "Presentación de resultados (5 min por equipo)",
            "Completar checklist post-programa: steerings, specs, hooks activos",
            "Demo final: un caso de punta a punta sin facilitador"],
        criterios=[
            "Reporte de ROI completo con datos cuantitativos",
            "Checklist de arranque post-programa completado por equipo",
            "El equipo ejecuta un caso completo sin intervención"]))

    return mods


RECOMENDACIONES = [
    "**Sesiones de 2 horas:** 30% teoría, 50% práctica guiada, 20% cierre/Q&A.",
    "**Desde la Sesión 1 se trabaja:** El equipo sale a construir desde el primer día.",
    "**Check-in a los 15 días:** La Sesión 3 incluye revisión de lo construido entre sesiones.",
    "**Casos reales siempre:** Nunca ejercicios ficticios — siempre el proyecto real del equipo.",
    "**Patrones compartidos:** Desde la Sesión 4, los equipos comparten artefactos entre sí.",
    "**Gobernanza antes del cierre:** La Sesión 5 estructura cómo escala la herramienta.",
    "**Autonomía progresiva:** En la Sesión 6 el facilitador no debería necesitar intervenir.",
]
