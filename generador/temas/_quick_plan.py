"""Plan de Enseñanza — contenido de los 6 módulos para el tema Quick Suite."""

from ..modelo import DatosCliente
from .estructura import ModuloPlan


def modulos_plan(d: DatosCliente):
    from . import quick_suite as Q
    fuente = Q._fuente_conocimiento(d)
    app = Q._app_negocio(d)
    piloto = d.piloto_mvp or "el caso de uso piloto"
    casos = Q._casos(d)
    plan = d.plan_producto or "Pro"
    areas = d.areas or "las áreas participantes"

    mods = []

    mods.append(ModuloPlan(
        titulo="Módulo 1: Setup y Catálogo de Quick Suite", semana="1",
        contenido_tematico=[
            "Qué es Amazon Quick Suite y su valor de negocio (IA agéntica que ancla respuestas en datos y ejecuta acciones)",
            f"Aprovisionamiento en AWS: licencias del plan {plan} e IAM Identity Center / SSO",
            "Las 6 capacidades: Quick Sight, Quick Flows, Quick Automate, Quick Index, Quick Research, Apps in Quick",
            "La interfaz de chat: preguntas en lenguaje natural con citas a la fuente",
            "Concepto de Spaces como centro de conocimiento del equipo",
            "Governance inicial: ownership de Spaces y agentes"],
        objetivos=[
            "Explicar qué es Quick Suite y en qué se diferencia de un chatbot tradicional",
            "Acceder a Quick mediante SSO / IAM Identity Center",
            "Identificar las 6 capacidades y para qué sirve cada una",
            "Reconocer cuándo usar chat, Research, Flows, Automate, Sight o Apps",
            "Crear su primer Space de equipo"],
        actividades=[
            "Recorrido guiado de acceso a Quick vía SSO",
            "Demo en vivo de cada capacidad con un ejemplo de negocio",
            "Hands-on: cada participante hace su primera pregunta con citas y crea un Space"],
        criterios=[
            "Todos los participantes acceden a Quick con su cuenta",
            "El equipo identifica correctamente qué capacidad usar para cada necesidad",
            "Al menos un Space creado por el equipo"]))

    mods.append(ModuloPlan(
        titulo="Módulo 2: Contexto, Conexión de Fuentes y Prompting", semana="2",
        contenido_tematico=[
            f"Fuentes de conocimiento: conectar {fuente} (y Drive/SharePoint/S3 si aplica) a Quick Index",
            "Knowledge Bases y control de acceso \"coarse-grained\"",
            "Fundamentos de prompt engineering para trabajo de conocimiento",
            "Prompt socrático para estructurar problemas",
            "Chat con citas: preguntar sobre documentos internos y validar fuentes",
            "Generación de documentación y resúmenes desde el conocimiento de la empresa"],
        objetivos=[
            f"Conectar una fuente de conocimiento ({fuente}) a Quick Index",
            "Crear una Knowledge Base y entender su control de acceso",
            "Construir prompts efectivos con estructura rol-contexto-tarea-restricciones-formato",
            "Obtener respuestas ancladas en datos con citas verificables",
            "Generar un documento o resumen a partir del conocimiento indexado"],
        actividades=[
            f"Conexión guiada de {fuente} a Quick Index",
            "Creación de la primera Knowledge Base y prueba de acceso",
            "Taller de prompt engineering con niveles de complejidad creciente",
            "Ejercicio: preguntar sobre un documento real y verificar las citas",
            "Inicio del playbook del equipo"],
        criterios=[
            "Al menos una fuente de conocimiento conectada y sincronizada",
            "Cada participante construye prompts con estructura completa",
            "Se genera al menos un documento/resumen con citas a la fuente"],
        material_referencia=[
            "Esta sesión se apoya en fundamentos de prompt engineering aplicados a Quick Suite:", "",
            "- **Un prompt es una instrucción, no magia** — la ambigüedad produce respuestas impredecibles.",
            "- **El contexto es tuyo** — Quick responde mejor cuando la Knowledge Base está bien conectada.",
            "- **Estructura del prompt** — ROL, CONTEXTO, TAREA, RESTRICCIONES y FORMATO.",
            "- **Verificar las citas** — la ventaja de Quick es que ancla en datos; siempre revisar la fuente."]))

    mods.append(ModuloPlan(
        titulo="Módulo 3: Piezas Avanzadas — Agentes, Conectores y BI", semana="2-3",
        subtitulo=f"**Aplicado a:** conectores {app}/{fuente} y el caso piloto ({piloto[:50]})",
        contenido_tematico=[
            "Chat agents personalizados: instrucciones, fuentes y capacidades",
            "Autonomous agents (modos Fast / Pro / Custom) y ejecución agendada",
            f"Conectores de acción: {app} vía OAuth",
            "Datasets y Topics: capa semántica multi-dataset para métricas",
            "Quick Research: investigación y reportes estructurados combinando fuentes",
            "MCP y OpenAPI: extensibilidad para casos futuros"],
        objetivos=[
            "Crear un chat agent personalizado para un caso de uso concreto",
            f"Conectar el conector de {app} y ejecutar consultas",
            "Explicar la diferencia entre chat agents y autonomous agents",
            "Usar Quick Research para generar un reporte estructurado",
            "Entender cuándo conviene un Topic multi-dataset"],
        actividades=[
            f"Conectar el conector de acción de {app} vía OAuth y validar con una consulta",
            f"Crear un chat agent para el caso piloto ({piloto[:50]})",
            f"Generar un reporte con Quick Research combinando {app} + {fuente}",
            "Check-in grupal: revisar lo construido en las 2 semanas previas"],
        criterios=[
            f"Conector de {app} conectado y validado",
            "Un chat agent personalizado funcional para el caso piloto",
            "Al menos un reporte de Quick Research generado"],
        material_referencia=[
            "- **Chat agents vs. autonomous agents** — unos conversan, otros ejecutan y se agendan.",
            "- **Modos de agente autónomo** — Fast (tareas simples), Pro (razonamiento), Custom (control fino).",
            "- **Conectores de conocimiento vs. de acción** — unos leen datos, otros ejecutan tareas.",
            "- **Principio de mínimo privilegio** — dar a cada agente solo los permisos que necesita."]))

    mods.append(ModuloPlan(
        titulo="Módulo 4: Problemas Difíciles y Automatización", semana="4",
        subtitulo=f"**Aplicado a:** {'; '.join(c['proceso'][:40] for c in casos[:3])}",
        contenido_tematico=[
            "Resolución en vivo del caso piloto con Quick",
            f"Quick Flows: automatizar {piloto[:50]} ({app} → Research → documento)",
            "Quick Automate: procesos de varios pasos y multi-área",
            "Apps in Quick: generar entregables sin código",
            "Chat agent + flujo para los procesos recurrentes",
            "Extracción de patrones y registro de casos borde"],
        objetivos=[
            f"Automatizar {piloto[:50]} con un Quick Flow",
            "Crear una app sencilla en Apps in Quick",
            "Estructurar procesos recurrentes con un agente + flujo",
            "Identificar qué se resuelve con chat agent, flow, automate o app",
            "Documentar casos borde con plan de acción"],
        actividades=[
            "Cada participante presenta su caso más engorroso (5 min de contexto)",
            f"Construcción en vivo del Quick Flow del caso piloto",
            "Prototipo de app en Apps in Quick para un entregable del equipo",
            "Prototipo de flujo para un proceso recurrente",
            "Registro de casos borde y límites de datos"],
        criterios=[
            f"El caso piloto automatizado con un Flow",
            "Al menos un prototipo funcional de app o flujo para los otros casos",
            "Casos no resueltos con plan de acción claro"]))

    mods.append(ModuloPlan(
        titulo="Módulo 5: Retro y Gobernanza", semana="5",
        subtitulo=f"**Aplicado a:** {'; '.join(c['proceso'][:40] for c in casos[:3])}",
        contenido_tematico=[
            "Retro: tiempos Quick vs. método manual por caso de uso",
            "Calidad de la información entregada (métrica de éxito del cliente)",
            "Definición de autonomía de los agentes",
            "Gobernanza: ownership de Spaces/agentes, naming conventions",
            "Control de acceso por Knowledge Base al escalar a más áreas",
            "Proceso de onboarding para nuevas personas"],
        objetivos=[
            "Medir y reportar tiempo ahorrado y calidad de la información",
            "Decidir el nivel de autonomía adecuado para cada agente",
            "Definir reglas de ownership y naming para Spaces, agentes y flows",
            "Configurar control de acceso al compartir recursos entre áreas",
            "Diseñar el proceso de onboarding"],
        actividades=[
            "Registro y comparativa de tiempos Quick vs. manual por caso",
            "Evaluación de calidad de los outputs",
            "Definición de naming conventions y ownership",
            "Documento de onboarding: cómo arranca una persona nueva",
            "Decisión de autonomía por agente"],
        criterios=[
            "Datos de tiempo y calidad registrados por caso",
            "Documento de gobernanza con naming y ownership",
            "Nivel de autonomía definido por agente",
            "Proceso de onboarding documentado"]))

    mods.append(ModuloPlan(
        titulo="Módulo 6: Cierre y Autonomía", semana="6",
        contenido_tematico=[
            "Análisis de ROI: tiempo ahorrado y calidad por caso de uso",
            f"Reporte de consumo del plan {plan} y governance final",
            "Presentación de resultados al liderazgo: validar qué tan funcional resultó Quick",
            "Checklist de arranque post-programa", "Equipo autónomo con Quick"],
        objetivos=[
            "Presentar el ROI con datos reales (tiempo y calidad)",
            "Operar Quick de forma autónoma sin soporte externo",
            "Mantener y evolucionar Spaces, agentes y flows",
            "Incorporar nuevas personas usando el onboarding"],
        actividades=[
            "Construcción del reporte de ROI con datos de las 6 semanas",
            f"Presentación de resultados al liderazgo de {d.empresa}",
            "Completar checklist post-programa: Spaces, Knowledge Bases, agentes, flows, conectores",
            "Demo final: un caso de punta a punta sin facilitador"],
        criterios=[
            "Reporte de ROI completo (tiempo ahorrado + calidad)",
            "Checklist de arranque post-programa completado",
            "El equipo ejecuta un caso completo sin intervención"]))

    return mods


RECOMENDACIONES = [
    "**Sesiones de 2 horas:** 30% teoría, 50% práctica guiada, 20% cierre/Q&A.",
    "**Audiencia de negocio:** el lenguaje y los ejemplos se orientan a las áreas participantes, no a desarrollo.",
    "**Desde la Sesión 1 se trabaja:** el equipo empieza a usar Quick desde el primer día.",
    "**Casos reales siempre:** los casos del diagnóstico son el hilo conductor.",
    "**Verificar citas:** la ventaja de Quick es anclar en datos; enfatizar la validación de fuentes.",
    "**Gobernanza antes del cierre:** la Sesión 5 estructura cómo escala a más áreas.",
    "**Autonomía progresiva:** en la Sesión 6 el facilitador no debería necesitar intervenir.",
]
