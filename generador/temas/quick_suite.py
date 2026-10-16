"""
Tema: Adopción de Amazon Quick Suite.

Contenido de las 6 sesiones (roadmap, plan, diseño) para clientes que adoptan
Quick Suite como asistente de IA agéntica para el negocio. El roadmap es genérico
en contenido; el plan y el diseño bajan al detalle con las fuentes/casos del cliente.
"""

from ..modelo import DatosCliente
from .estructura import SesionRoadmap

META = {
    "tema": "quick_suite",
    "producto": "Amazon Quick Suite",
    "titulo_programa": "Adopción de Amazon Quick Suite",
    "duracion_default": "6 sesiones × 2h (programa acotado)",
    "audiencia": "Perfiles de negocio y operación",
}

DURACION_SESION = 2
TOTAL_SESIONES = 6

# Las 6 capacidades de Quick Suite (referencia usada en todo el contenido)
CAPACIDADES = [
    ("Quick Sight", "BI y dashboards en lenguaje natural"),
    ("Quick Flows", "automatización de flujos de trabajo"),
    ("Quick Automate", "procesos complejos multi-área"),
    ("Quick Index", "indexación y descubrimiento del conocimiento"),
    ("Quick Research", "investigación y reportes que combinan fuentes"),
    ("Apps in Quick", "creación de aplicaciones sin código"),
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _participantes(d: DatosCliente) -> str:
    areas = d.areas or "las áreas participantes"
    return f"Equipo {d.empresa} ({areas}) + eTribe"


def _casos(d: DatosCliente):
    casos = [{"proceso": c.proceso, "prioridad": c.prioridad or "Alta",
              "frecuencia": c.frecuencia} for c in d.casos_uso[:5]]
    return casos or [{"proceso": "Caso de uso principal del negocio", "prioridad": "Alta", "frecuencia": ""}]


def _fuente_conocimiento(d: DatosCliente) -> str:
    """Fuente principal de conocimiento a conectar a Quick Index."""
    return d.conocimiento_org or "el repositorio de conocimiento del equipo (Drive/SharePoint/Confluence)"


def _app_negocio(d: DatosCliente) -> str:
    """App de negocio crítica (conector de acción)."""
    return d.apps_negocio or "la aplicación de negocio crítica del equipo"


def config_recomendada(d: DatosCliente) -> dict:
    """Integraciones recomendadas para Quick: conocimiento, acción y estándares abiertos."""
    conocimiento = []
    fuente = _fuente_conocimiento(d)
    conocimiento.append((fuente, "Conocimiento (Quick Index)", "Alta",
                         "Indexar documentación y actas para responder con citas"))
    accion = []
    app = _app_negocio(d)
    if app:
        accion.append((app, "Acción (OAuth)", "Alta",
                       "Leer datos operativos que alimentan el caso piloto"))
    otros = [
        ("Google Drive / OneDrive / SharePoint", "Conocimiento", "Media (si aplica)", "Fuentes adicionales de documentos"),
        ("Servidor MCP (propio o de terceros)", "Estándar abierto", "Baja / a futuro", "Conectar sistemas internos vía MCP"),
        ("OpenAPI", "Estándar abierto", "Baja / a futuro", "Conectar APIs internas mediante especificación estándar"),
    ]
    spaces = [
        (f"{_slug(d.areas.split(',')[0] if d.areas else 'equipo')}-piloto",
         "Knowledge Base, agentes, flows", "Centro del caso piloto"),
    ]
    agentes = [
        (f"Agente del caso piloto", f"Genera el resultado del piloto combinando {fuente} + {app} con citas"),
    ]
    for c in _casos(d)[1:3]:
        agentes.append((f"Agente: {c['proceso'][:40]}", "Automatiza/estructura el proceso con Quick"))
    flows = [
        ("Flow del caso piloto", "Agendado / manual",
         f"{app} → Quick Research → documento del proceso"),
    ]
    return {"conocimiento": conocimiento, "accion": accion, "otros": otros,
            "spaces": spaces, "agentes": agentes, "flows": flows,
            "fuente": fuente, "app": app, "capacidades": CAPACIDADES}


def capacidad_sugerida(proceso: str) -> str:
    """Infiere la(s) capacidad(es) de Quick más adecuada(s) para un proceso.

    Heurística por palabras clave del nombre del proceso. Devuelve una sugerencia
    legible (ej. 'Quick Research + Quick Flows'). Si no hay señal clara, sugiere
    el combo genérico más común para trabajo de conocimiento.
    """
    p = (proceso or "").lower()
    sugerencias = []
    # Reportes / informes / research
    if any(k in p for k in ["informe", "reporte", "research", "investigac", "análisis", "analisis", "resumen"]):
        sugerencias.append("Quick Research")
    # Automatización / procesos recurrentes / seguimiento
    if any(k in p for k in ["flujo", "automatiz", "seguimiento", "recurrente", "cierre", "proceso"]):
        sugerencias.append("Quick Flows")
    # Presentaciones / apps / documentos entregables
    if any(k in p for k in ["presentaci", "app", "portal", "formulario", "tracker", "documento", "power point", "powerpoint"]):
        sugerencias.append("Apps in Quick")
    # Minutas / notas / actas / preguntas -> chat agent
    if any(k in p for k in ["minuta", "acta", "nota", "reunión", "reunion", "pregunta", "faq", "consulta"]):
        sugerencias.append("Chat agent")
    # BI / dashboards / métricas
    if any(k in p for k in ["dashboard", "bi ", "métrica", "metrica", "indicador", "kpi", "tablero"]):
        sugerencias.append("Quick Sight")
    # Dedup preservando orden
    vistos = []
    for s in sugerencias:
        if s not in vistos:
            vistos.append(s)
    if not vistos:
        return "Quick Research + Chat agent"
    return " + ".join(vistos[:2])


def _slug(s: str) -> str:
    s = (s or "equipo").strip().lower()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), (" ", "-")]:
        s = s.replace(a, b)
    return "".join(ch for ch in s if ch.isalnum() or ch == "-")[:24] or "equipo"


# ─────────────────────────────────────────────────────────────────────────────
# ROADMAP (6 sesiones) — genérico en contenido
# ─────────────────────────────────────────────────────────────────────────────
def sesiones_roadmap(d: DatosCliente):
    fuente = _fuente_conocimiento(d)
    app = _app_negocio(d)
    piloto = d.piloto_mvp or "el caso de uso piloto"
    casos = _casos(d)
    casos_lineas = "".join(f"—— [{c['prioridad']}] {c['proceso'][:60]}"
                           + (f" — {c['frecuencia']}" if c['frecuencia'] else "") + ".\n"
                           for c in casos[:3])
    plan = d.plan_producto or "Pro"
    caps = "\n".join(f"—— {n} ({desc})" for n, desc in CAPACIDADES)

    S = []
    S.append(SesionRoadmap(
        "Fase 0 /\n (Sem. 1)", "Sesión 1 /\n Setup y catálogo /\n Quick Suite",
        "Fase 1: Setup y catálogo de Quick Suite\n\nPunto de partida. Aprovisionamiento en AWS, primer contacto y las 6 capacidades.",
        "— Revisión del contexto actual: dónde vive el conocimiento y qué procesos son manuales.\n"
        "— Aprovisionamiento de Quick en AWS con IAM Identity Center / SSO.\n"
        f"— Asignación de licencias del plan {plan}.\n— Presentación de las 6 capacidades de Quick Suite:\n"
        + caps + "\n"
        "— La interfaz de chat: preguntas en lenguaje natural ancladas en datos, con citas a la fuente.\n"
        "— Concepto de Spaces como centro de conocimiento del equipo.\n"
        "— Hands-on: primera pregunta con citas + creación del primer Space.\n"
        "— Governance inicial: ownership de Spaces/agentes y política de uso.\n"
        "— Cierre: el equipo sale usando Quick esta misma semana.",
        "Sesión 1: Setup y Catálogo de Quick Suite",
        "Aprovisionamiento en AWS, primer contacto y presentación de las 6 capacidades"))
    S.append(SesionRoadmap(
        "Fase 1 /\n (Sem. 2)", "Sesión 2 /\n Contexto, fuentes /\n y prompting",
        "Fase 2: Contexto, conexión de fuentes y prompting\n\nEl equipo conecta el conocimiento del negocio y obtiene resultados con citas.",
        f"— Conexión de fuentes de conocimiento a Quick Index:\n—— {fuente} como fuente principal.\n"
        "— Creación de la primera Knowledge Base y validación del control de acceso por base.\n"
        "— Fundamentos de prompt engineering para trabajo de conocimiento:\n"
        "—— Estructura ROL, CONTEXTO, TAREA, RESTRICCIONES y FORMATO.\n—— Prompt socrático.\n"
        "— Chat con citas: preguntar sobre documentos internos y verificar las fuentes.\n"
        "— Generación de documentación y resúmenes desde el conocimiento indexado.\n"
        "— Inicio del playbook del equipo con los primeros prompts efectivos.",
        "Sesión 2: Contexto, Conexión de Fuentes y Prompting",
        "Conectar el conocimiento del negocio, prompting efectivo y primeros resultados con citas"))
    S.append(SesionRoadmap(
        "Fase 2 /\n (Sem. 3)", "Sesión 3 /\n Agentes, conectores /\n y BI",
        f"Fase 3: Piezas avanzadas — Agentes, conectores y BI\n\nEl equipo conecta {app}, crea su primer agente y genera reportes con Quick Research.",
        "— Chat agents vs. autonomous agents (modos Fast / Pro / Custom) y ejecución agendada.\n"
        f"— Conexión del conector de acción de {app} vía OAuth.\n"
        f"— Creación de un chat agent orientado al caso piloto: {piloto[:60]}.\n"
        "— Introducción a datasets y Topics (capa semántica multi-dataset).\n"
        f"— Quick Research: reporte estructurado combinando {app} y {fuente}.\n"
        "— MCP y OpenAPI: extensibilidad para casos futuros (mínimo privilegio).\n"
        "— Check-in de los primeros 15 días: qué agentes/flows crearon y cuáles ajustar.",
        "Sesión 3: Piezas Avanzadas — Agentes, Conectores y BI",
        "Chat agents, conectores de acción, datasets/topics y Quick Research"))
    S.append(SesionRoadmap(
        "Fase 3 /\n (Sem. 4)", "Sesión 4 /\n Problemas difíciles /\n y automatización",
        "Fase 4: Problemas difíciles y automatización\n\nResolución en vivo del caso piloto y automatización con Quick Flows / Automate.",
        "— Casos de uso a trabajar (del diagnóstico):\n" + casos_lineas +
        f"— Resolución en vivo del caso piloto: automatizar {piloto[:50]} con un Quick Flow ({app} → Research → documento).\n"
        "— Apps in Quick: generar entregables sin código.\n"
        "— Chat agent + flujo para los procesos recurrentes del equipo.\n"
        "— Extracción de enfoques: ¿chat agent? ¿Quick Flow? ¿Automate? ¿App?\n"
        "— Registro de casos borde, límites de datos y bloqueos.",
        "Sesión 4: Problemas Difíciles y Automatización",
        "Resolución en vivo del caso piloto y automatización con Quick Flows / Automate"))
    S.append(SesionRoadmap(
        "Fase 4 /\n (Sem. 5)", "Sesión 5 /\n Retro y /\n gobernanza",
        "Fase 5: Retro y gobernanza\n\nRetrospectiva (tiempo y calidad) y reglas para escalar entre áreas.",
        "— Retro/feedback:\n—— Registro de tiempos por caso de uso: Quick vs. método manual.\n"
        f"—— Medición sobre: {'; '.join(c['proceso'][:40] for c in casos[:3])}.\n"
        "—— Calidad de la información entregada.\n—— Revisión de qué agentes/flows/Spaces generaron valor.\n"
        "—— Definición de autonomía de los agentes: aprobación paso a paso vs. autonomía media.\n"
        "— Gobernanza:\n—— Ownership de Spaces/agentes.\n—— Naming conventions.\n"
        "—— Control de acceso por Knowledge Base al compartir entre áreas.\n"
        "—— Proceso de onboarding con los recursos existentes.",
        "Sesión 5: Retro y Gobernanza",
        "Tiempos comparativos, calidad de la información y reglas para escalar entre áreas"))
    S.append(SesionRoadmap(
        "Fase 5 /\n (Sem. 6)", "Sesión 6 /\n Cierre y /\n autonomía",
        "Fase 6: Cierre y autonomía\n\nCierre del programa con datos reales: ROI, presentación a liderazgo y checklist.",
        "— Análisis de ROI: tabla comparativa de tiempo ahorrado y calidad de la información (Quick vs. manual).\n"
        f"— Reporte de consumo del plan {plan} y ajuste final de governance.\n"
        f"— Presentación de resultados al liderazgo de {d.empresa}: ¿qué tan funcional resultó Quick?\n"
        "— Checklist post-programa: Spaces, Knowledge Bases, chat agents, flows y conectores activos.\n"
        "— Demo final: un caso de punta a punta sin facilitador.\n"
        "— Equipo autónomo con Quick: opera sin soporte de eTribe.",
        "Sesión 6: Cierre y Autonomía",
        "ROI, presentación a liderazgo y checklist post-programa"))
    return S


def nota_roadmap(d: DatosCliente) -> str:
    areas = d.areas or "las áreas participantes"
    return (f"Nota: sesiones conjuntas para {areas} ({d.num_personas or 'el equipo inicial'}). "
            "El hilo conductor son los casos del diagnóstico. La ventaja de Quick es anclar las "
            "respuestas en datos con citas — verificar siempre las fuentes.")


def subtitulo_roadmap(d: DatosCliente) -> str:
    piloto = d.piloto_mvp or "el caso de uso piloto"
    areas = d.areas or "las áreas participantes"
    return (f"Caso piloto: {piloto[:50]} | Áreas: {areas} | "
            f"Duración estimada: {d.duracion or META['duracion_default']}")


from ._quick_plan import modulos_plan          # noqa: E402
from ._quick_actividades import actividades     # noqa: E402
