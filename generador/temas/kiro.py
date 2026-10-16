"""
Tema: Adopción de Kiro IDE.

Contenido de las 6 sesiones (roadmap, plan de enseñanza, diseño de actividades)
para clientes de desarrollo asistido por IA con Kiro. Migrado del script original
`generar_plan_desde_diagnostico.py`, parametrizado por el stack del cliente.
"""

import re
from ..modelo import DatosCliente
from .estructura import SesionRoadmap, ModuloPlan, SesionActividad

META = {
    "tema": "kiro",
    "producto": "Kiro",
    "titulo_programa": "Adopción de Kiro",
    "duracion_default": "6-7 semanas (programa estándar)",
    "audiencia": "Equipos de desarrollo",
}

DURACION_SESION = 2
TOTAL_SESIONES = 6

# ─────────────────────────────────────────────────────────────────────────────
# MATERIAL DIDÁCTICO eTribe
# ─────────────────────────────────────────────────────────────────────────────
MODULOS_ETRIBE = {
    "M01": {"titulo": "Fundamentos de Prompt Engineering", "subtitulo": "Aprender a hablarle al modelo",
            "puntos": ["Un prompt es una instrucción — no magia ni sintaxis secreta.",
                       "La ambigüedad en el prompt produce outputs impredecibles.",
                       "El contexto es tuyo: el modelo no recuerda nada entre sesiones.",
                       "Dos capas de instrucción: System Prompt (global) y Prompt del usuario (puntual)."]},
    "M02": {"titulo": "Kiro más allá del código", "subtitulo": "De herramienta a capa de inteligencia",
            "puntos": ["Usar Kiro solo para código es el 20% del potencial.",
                       "Kiro puede estar en ideación, planeación, arquitectura, ejecución, docs y revisión.",
                       "Cambio de mentalidad: de asistente de código a capa de inteligencia del proyecto.",
                       "Todos los casos de uso son implementables esta semana."]},
    "M03": {"titulo": "El Prompt Socrático", "subtitulo": "Conversar para pensar mejor",
            "puntos": ["El prompt socrático pide guía, no respuesta directa.",
                       "El output es criterio propio, no texto del modelo.",
                       "Úsalo cuando haya ambigüedad, múltiples opciones, impacto alto o trabajo en equipo.",
                       "No es más lento: el tiempo se recupera en precisión de ejecución."]},
    "M04": {"titulo": "Construir Buenos Prompts", "subtitulo": "Las variables que controlas",
            "puntos": ["Un prompt tiene partes: ROL, CONTEXTO, TAREA, RESTRICCIONES y FORMATO.",
                       "El rol activa un modo de respuesta — no es decorativo.",
                       "Las restricciones reducen variabilidad: decir qué NO hacer es tan útil como qué hacer.",
                       "Itera una variable a la vez para entender qué cambió.",
                       "La trazabilidad da visibilidad sobre el razonamiento, no solo el resultado."]},
    "M05": {"titulo": "Flujos de Trabajo con Kiro", "subtitulo": "Planeación, ejecución y meta prompting",
            "puntos": ["El costo oculto más alto en proyectos es el malentendido, no el código.",
                       "Flujo 1 (Planeación): recuperar contexto → sesión socrática → documento de definición.",
                       "Flujo 2 (Ejecución): el documento alimenta agentes especializados y meta prompts.",
                       "El ciclo se retroalimenta: cada iteración enriquece el contexto disponible."]},
    "M06": {"titulo": "IA Responsable", "subtitulo": "Criterio, validación y riesgo",
            "puntos": ["La IA no es responsable — tú sí. El modelo simplifica trabajo, no desplaza responsabilidad.",
                       "Tres niveles de revisión: Lectura (siempre), Validación (antes de usar), Auditoría (alto impacto).",
                       "Discriminar por riesgo: bajo (leer), medio (leer+validar), alto (leer+validar+auditar).",
                       "Filtro de 3 preguntas: ¿resuelve MI problema? ¿puedo explicar por qué? ¿lo firmaría como mío?",
                       "Con MCP aplica el principio de mínimo privilegio a los agentes."]},
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE STACK
# ─────────────────────────────────────────────────────────────────────────────
def _tecnologias(stack: str) -> dict:
    tech = {"frontend": [], "backend": [], "lenguajes": [], "bases_datos": [], "cloud": [], "ci_cd": []}
    s = (stack or "").lower()
    for t in ["react native", "reactjs", "react", "angular", "vue", "next.js", "nextjs", "svelte", "vite", "tailwind"]:
        if t in s:
            tech["frontend"].append("ReactJS" if t == "reactjs" else t.title())
    for t in ["node.js", "nodejs", "express", "fastapi", "django", "flask", ".net", "spring", "nestjs", "laravel"]:
        if t in s:
            tech["backend"].append(t if "." in t else t.title())
    for t in ["typescript", "javascript", "python", "java", "c#", "go", "rust", "php", "ruby"]:
        if t in s:
            tech["lenguajes"].append("C#" if t == "c#" else t.title())
    for t in ["mysql", "postgresql", "mongodb", "redis", "dynamodb", "sql server", "sqlite"]:
        if t in s:
            tech["bases_datos"].append(t.title())
    for t in ["aws", "azure", "gcp", "google cloud"]:
        if t in s:
            tech["cloud"].append(t.upper() if len(t) <= 3 else t.title())
    for t in ["github actions", "azure pipelines", "jenkins", "gitlab", "terraform", "docker"]:
        if t in s:
            tech["ci_cd"].append(t.title())
    # Dedup preservando orden
    for k in tech:
        seen = []
        for v in tech[k]:
            if v not in seen:
                seen.append(v)
        tech[k] = seen
    return tech


def _fw_lang(tech: dict):
    fps = tech.get("frontend", []) + tech.get("backend", [])
    fw = fps[0] if fps else "el framework"
    lang = tech.get("lenguajes", ["TypeScript"])[0] if tech.get("lenguajes") else "TypeScript"
    return fw, lang, fps


def _detectar_aws_tooling(d: DatosCliente) -> dict:
    campos = [d.stack, d.fricciones, d.objetivos, d.piloto_mvp, d.arquitectura,
              d.repositorios_ci_cd, d.integraciones,
              " ".join(c.proceso for c in d.casos_uso)]
    txt = " ".join(campos).lower()
    kw_diag = ["diagrama de arquitectura", "diagramas de arquitectura", "architecture diagram",
               "diagrama de infraestructura", "diagrama de flujo"]
    kw_iac = ["iac", "infrastructure as code", "infraestructura como código", "infraestructura como codigo",
              "cloudformation", "terraform", "cdk", "aws cdk", "provisioning"]
    nec_diag = any(k in txt for k in kw_diag)
    nec_iac = any(k in txt for k in kw_iac)
    usa_aws = "aws" in txt or "bedrock" in txt or "cloudformation" in txt
    tools = []
    if nec_diag:
        tools.append({"nombre": "aws-diagram-mcp-server", "tipo": "skill/mcp",
                      "descripcion": "Genera diagramas de arquitectura AWS con el paquete Python 'diagrams'",
                      "comando": "uvx awslabs.aws-diagram-mcp-server",
                      "requisitos": "Python 3.10+, uv y Graphviz",
                      "fuente": "https://github.com/awslabs/mcp/tree/main/src/aws-diagram-mcp-server"})
    if nec_iac or (usa_aws and nec_diag):
        tools.append({"nombre": "Agent Toolkit for AWS", "tipo": "agent-toolkit",
                      "descripcion": "Suite oficial de AWS con tools y guardrails para CDK, CloudFormation e IaC",
                      "comando": "Instalar plugin desde Kiro / AWS CLI",
                      "requisitos": "AWS CLI y credenciales configuradas",
                      "fuente": "https://github.com/aws/agent-toolkit-for-aws"})
    return {"necesita_diagramas": nec_diag, "necesita_iac": nec_iac, "herramientas": tools, "aplica": bool(tools)}


def _casos(d: DatosCliente):
    casos = [{"proceso": c.proceso[:80], "prioridad": c.prioridad or "Alta"} for c in d.casos_uso[:5]]
    return casos or [{"proceso": "Caso de uso principal del equipo", "prioridad": "Alta"}]


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN RECOMENDADA (MCPs, agentes, hooks, steerings)
# ─────────────────────────────────────────────────────────────────────────────
def config_recomendada(d: DatosCliente) -> dict:
    tech = _tecnologias(d.stack)
    integ = (d.integraciones or "").lower()
    # Nombres de paquete verificados en fuentes oficiales (no inventados). El
    # agente mcp-config-generator los verifica de nuevo en la web al documentarlos.
    mcps = []
    if "jira" in integ or "confluence" in integ or "atlassian" in integ:
        mcps.append(("Atlassian MCP (remoto)", "npx -y mcp-remote https://mcp.atlassian.com/v1/sse", "Jira/Confluence: tickets, HU, sprints y páginas desde Kiro (servidor remoto oficial)"))
    if "github" in integ or any("github" in t.lower() for t in tech["ci_cd"]):
        mcps.append(("GitHub MCP", "npx -y @modelcontextprotocol/server-github", "PRs, issues, code review y búsqueda de código"))
    if "gitlab" in integ:
        mcps.append(("GitLab MCP", "npx -y @modelcontextprotocol/server-gitlab", "Repos, MRs e issues de GitLab"))
    if any("aws" in c.lower() for c in tech["cloud"]) or "aws" in integ:
        mcps.append(("AWS Documentation MCP", "uvx awslabs.aws-documentation-mcp-server@latest", "Documentación oficial de AWS desde Kiro"))
    if tech["bases_datos"] or "postgres" in integ or "sql" in integ:
        mcps.append(("Database MCP", "uvx mcp-server-sqlite  /  npx -y @modelcontextprotocol/server-postgres", "Consultas y modelado de datos desde Kiro"))
    if "slack" in integ:
        mcps.append(("Slack MCP", "npx -y @modelcontextprotocol/server-slack", "Leer/publicar en canales de Slack desde Kiro"))
    if "notion" in integ:
        mcps.append(("Notion MCP", "npx -y @notionhq/notion-mcp-server", "Leer y escribir páginas de Notion"))
    if "sentry" in integ:
        mcps.append(("Sentry MCP (remoto)", "npx -y mcp-remote https://mcp.sentry.dev/sse", "Consultar errores e issues de Sentry"))
    mcps.append(("Filesystem MCP", "npx -y @modelcontextprotocol/server-filesystem", "Navegación y lectura avanzada del proyecto (sandbox por directorio)"))

    steerings = [("project-context.md", "always", f"Contexto general del proyecto: {d.proyecto[:60]}"),
                 ("coding-standards.md", "always", "Estándares de código: naming, estructura, patrones preferidos")]
    if tech["frontend"]:
        steerings.append(("frontend-patterns.md", "fileMatch: **/*.tsx, **/*.jsx, **/*.vue",
                          f"Patrones de componentes {tech['frontend'][0]}: estructura, state, testing"))
    if tech["backend"]:
        steerings.append(("api-conventions.md", "fileMatch: **/routes/**, **/controllers/**",
                          f"Convenciones de API en {tech['backend'][0]}: endpoints, errores, validación"))
    steerings.append(("testing-guidelines.md", "fileMatch: **/*.test.*, **/*.spec.*",
                      "Guía de testing: qué testear, naming, fixtures, mocks"))

    hooks = [("Lint on Save", "PostFileSave", "npm run lint" if tech["frontend"] else "python -m flake8"),
             ("Test Runner on Task Complete", "PostTaskExec", "npm test -- --run" if tech["frontend"] else "pytest"),
             ("Security Check pre-commit", "PreToolUse", "agent prompt")]

    agentes = []
    if tech["frontend"]:
        agentes.append(("Agente de Componentes UI", f"Genera componentes {'/'.join(tech['frontend'][:2])} siguiendo el design system"))
    if tech["backend"]:
        agentes.append(("Agente de API/Endpoints", f"Crea endpoints REST/GraphQL en {'/'.join(tech['backend'][:2])} con validación"))
    fr = (d.fricciones or "").lower()
    if any(k in fr for k in ["test", "prueba", "qa"]):
        agentes.append(("Agente de Testing", "Genera casos de prueba (unitarios, integración, e2e) desde specs o código"))
    if any(k in fr for k in ["historia", "hu", "requerimiento"]):
        agentes.append(("Agente de Análisis de Requerimientos", "Analiza documentación y genera HU con criterios de aceptación"))
    agentes.append(("Agente de Code Review", "Revisa código según estándares, detecta bugs y sugiere mejoras"))

    return {"tech": tech, "mcps": mcps, "steerings": steerings, "hooks": hooks,
            "agentes": agentes, "aws_tooling": _detectar_aws_tooling(d)}


# ─────────────────────────────────────────────────────────────────────────────
# ROADMAP (6 sesiones)
# ─────────────────────────────────────────────────────────────────────────────
def sesiones_roadmap(d: DatosCliente):
    part = f"Equipo de desarrollo {d.empresa} + eTribe"
    tech = _tecnologias(d.stack)
    fw, lang, fps = _fw_lang(tech)
    num_eq = d.num_equipos_paralelo or "el equipo"
    piloto = (d.piloto_mvp or "caso principal del equipo")[:80]
    integ = (d.integraciones or "herramientas del equipo")[:40]
    casos = _casos(d)
    casos_lineas = "".join(f"—— [{c['prioridad']}] {c['proceso'][:60]}.\n" for c in casos[:3])
    metricas = (d.metricas_exito or "tiempo ahorrado por tipo de tarea y por equipo")[:100]

    S = []
    S.append(SesionRoadmap(
        "Fase 0 /\n (Sem. 1)", "Sesión 1 /\n Setup y /\n catálogo Kiro",
        "Fase 1: Setup y catálogo Kiro\n\nPunto de partida del equipo. Instalación, primer contacto y catálogo de artefactos/workflows.",
        f"— Instalación de Kiro IDE / CLI para {num_eq}.\n— Asignación de licencias y configuración en consola AWS.\n"
        "— Presentación de interfaces: IDE y CLI.\n— Artefactos base: Vibe sessions (chat libre).\n"
        "— Los 4 workflows del IDE:\n—— Spec\n—— Plan\n—— Bug Fix\n—— Quick Spec\n"
        "— Artefactos avanzados:\n—— Steering\n—— Hooks\n—— MCP / Powers\n—— Skills / Agents.\n"
        "— Hands-on en el proyecto real: mapeo de reglas de negocio a Steering.\n"
        "— Cierre: el equipo sale a trabajar sobre su proyecto esa misma semana.",
        "Sesión 1: Setup y Catálogo Kiro",
        "Instalación, primer contacto con la herramienta y presentación de artefactos y workflows"))
    S.append(SesionRoadmap(
        "Fase 1 /\n (Sem. 1–2)", "Sesión 2 /\n Contexto y /\n navegación",
        "Fase 2: Contexto y navegación\n\nEl equipo profundiza en prompt engineering y casos no-código.",
        "— Módulos 1–4 del material eTribe:\n—— Fundamentos de prompt engineering\n—— Kiro más allá del código\n"
        "—— Prompt socrático\n—— Construir buenos prompts.\n— Casos de uso no-código:\n"
        "—— Generación de reportes/documentos desde plantillas.\n—— Análisis de documentación → requerimientos técnicos.\n"
        "—— Documentación técnica (READMEs, diagramas, APIs).\n—— Comunicación técnica → no-técnica.\n"
        "— Hands-on: mapeo de reglas de negocio a Steering.\n— Creación del playbook del equipo.",
        "Sesión 2: Contexto y Navegación",
        "Prompt engineering, casos no-código y mapeo de reglas de negocio"))
    S.append(SesionRoadmap(
        "Fase 2 /\n (Sem. 2)", "Sesión 3 /\n Piezas avanzadas /\n y mapeo",
        "Fase 3: Piezas avanzadas y mapeo\n\nEl equipo completa la teoría y hace el primer check-in de 15 días.",
        f"— Módulos 5–6 del material eTribe:\n—— Workflows con Kiro\n—— AI responsable.\n"
        f"— Conexión de MCP: {integ} vía OAuth.\n— Diseño de Skills y Agents orientados al caso piloto: {piloto}.\n"
        "— Meta prompting aplicado al caso de uso del equipo.\n"
        "— Check-in de los primeros 15 días: qué artefactos crearon, cuáles usan, cuáles abandonaron.\n"
        "— Refactoring en vivo de un steering o hook que no funciona bien.",
        "Sesión 3: Piezas Avanzadas y Mapeo",
        "MCPs, Skills, Agents personalizados y check-in de primeros 15 días"))
    S.append(SesionRoadmap(
        "Fase 3 /\n (Sem. 3–4)", "Sesión 4 /\n Problemas difíciles /\n y optimización",
        "Fase 4: Problemas difíciles y optimización\n\nCada equipo trae el caso más complejo y se resuelve en vivo.",
        "— Casos de uso a trabajar (del diagnóstico):\n" + casos_lineas +
        f"— Resolución en vivo del caso piloto: {piloto}.\n"
        "— Extracción de patrones: ¿spec? ¿hook? ¿agente dedicado?\n"
        f"— Patrones compartidos entre {num_eq}.\n"
        "— Casos no resueltos con plan de acción claro.\n— Registro de casos borde y bloqueos.",
        "Sesión 4: Problemas Difíciles y Optimización",
        "Cada equipo trae su caso complejo, resolución en vivo con Kiro"))
    S.append(SesionRoadmap(
        "Fase 4 /\n (Sem. 5–6)", "Sesión 5 /\n Retro y /\n gobernanza",
        "Fase 5: Retro y gobernanza\n\nRetro sobre la confianza ganada y reglas para escalar.",
        "— Retro/feedback:\n—— Registro de tiempos por caso de uso: Kiro vs. método tradicional.\n"
        f"—— Medición sobre: {'; '.join(c['proceso'][:40] for c in casos[:3])}.\n"
        "—— Revisión de casos borde documentados.\n—— Lecciones aprendidas.\n— Gobernanza:\n"
        f"—— Reglas para compartir artefactos entre {num_eq}.\n—— Ownership y naming conventions.\n"
        "—— Proceso de onboarding con artefactos existentes.",
        "Sesión 5: Retro y Gobernanza",
        "Retroalimentación, tiempos comparativos y reglas para compartir artefactos"))
    S.append(SesionRoadmap(
        "Fase 5 /\n (Sem. 6–7)", "Sesión 6 /\n Cierre y /\n autonomía",
        "Fase 6: Cierre y escalabilidad\n\nCierre del programa con datos reales.",
        f"— Análisis de ROI: tabla comparativa de {metricas} (Kiro vs. método tradicional).\n"
        "— Reporte de consumo de créditos y ajuste final de governance.\n"
        f"— Presentación de resultados al liderazgo de {d.empresa}.\n"
        "— Checklist post-programa: steerings, specs, hooks activos por equipo.\n"
        "— Equipo autónomo con Kiro: opera sin soporte de eTribe.",
        "Sesión 6: Cierre y Autonomía",
        "ROI, presentación a liderazgo y checklist post-programa"))
    return S


def nota_roadmap(d: DatosCliente) -> str:
    num_eq = d.num_equipos_paralelo or "el equipo"
    return (f"Nota: sesiones conjuntas para {num_eq} con bloques rotativos. "
            "Si algún equipo lo prefiere, se pueden coordinar sesiones dedicadas por separado.")


def subtitulo_roadmap(d: DatosCliente) -> str:
    caso = (d.proyecto or "Adopción de Kiro")[:80]
    return f"Caso de uso: {caso} | Duración estimada: {d.duracion or META['duracion_default']}"


# El plan de enseñanza y el diseño de actividades son extensos; se construyen en
# funciones dedicadas que devuelven listas de ModuloPlan / SesionActividad.
from ._kiro_plan import modulos_plan          # noqa: E402
from ._kiro_actividades import actividades     # noqa: E402
