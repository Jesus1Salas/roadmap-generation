"""
Renderizador agnóstico de Markdown.

Genera los 3 archivos .md (Roadmap, Plan de Enseñanza, Diseño de Actividades)
a partir de las estructuras que provee el módulo de tema. No tiene conocimiento
de Kiro ni de Quick Suite: solo consume SesionRoadmap, ModuloPlan y SesionActividad.
"""

from datetime import datetime
from .modelo import DatosCliente

DURACION_SESION = 2


# ─────────────────────────────────────────────────────────────────────────────
# ROADMAP (.md)
# ─────────────────────────────────────────────────────────────────────────────
def roadmap(d: DatosCliente, tema_mod) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y")
    meta = tema_mod.META
    sesiones = tema_mod.sesiones_roadmap(d)
    subtitulo = tema_mod.subtitulo_roadmap(d)

    md = []
    md.append(f"# Roadmap de {meta['titulo_programa']} — {d.empresa}")
    md.append("")
    md.append(f"> Generado el {fecha} a partir del Cuestionario de Diagnóstico")
    md.append(f"> Duración estimada: {d.duracion or meta['duracion_default']}")
    md.append("")
    md.append("---")
    md.append("")

    # Contexto del cliente — adaptado al tema
    md.append("## Contexto del Cliente")
    md.append("")
    md.append("| Campo | Valor |")
    md.append("|-------|-------|")
    md.append(f"| Empresa | {d.empresa} |")

    if d.tema == "kiro":
        md.append(f"| Proyecto | {d.proyecto or 'N/A'} |")
        md.append(f"| Stack | {(d.stack or 'N/A')[:100]} |")
        md.append(f"| Arquitectura | {d.arquitectura or 'N/A'} |")
        md.append(f"| Tipo de proyecto | {d.tipo_proyecto or 'N/A'} |")
        md.append(f"| Champion técnico | {d.champion_legible()} |")
        md.append(f"| Equipos | {d.num_equipos_paralelo or 'N/A'} |")
        md.append(f"| Personas | {(d.num_personas or 'N/A')[:80]} |")
        md.append(f"| Nivel de prompting | {d.nivel_madurez or 'N/A'}/5 |")
        md.append(f"| Herramientas IA actuales | {(d.herramientas_ia or 'Ninguna')[:80]} |")
        md.append(f"| Cultura de cambio | {d.cultura_cambio or 'N/A'} |")
    else:
        md.append(f"| Enfoque | {meta['titulo_programa']} como asistente de IA agéntica para el negocio |")
        md.append(f"| Áreas involucradas | {d.areas or 'N/A'} |")
        md.append(f"| Área de aplicación inicial | {d.proyecto or 'N/A'} |")
        md.append(f"| Champion | {d.champion_legible()} |")
        md.append(f"| Personas | {d.participantes_desc()} |")
        md.append(f"| Conocimiento organizacional | {d.conocimiento_org or 'N/A'} |")
        md.append(f"| Apps de negocio críticas | {d.apps_negocio or 'N/A'} |")
        md.append(f"| Herramienta IA actual | {d.herramientas_ia or 'Ninguna'} |")
        md.append(f"| Nivel de madurez en IA agéntica | {d.nivel_madurez or 'N/A'}/5 |")
        md.append(f"| Aprovisionamiento | {d.acceso_aws or 'N/A'} |")
        md.append(f"| Plan Quick evaluado | {d.plan_producto or 'N/A'} |")
        md.append(f"| Cultura de cambio | {d.cultura_cambio or 'N/A'} |")
        md.append(f"| Horizonte del programa | {d.timeline or d.duracion or 'N/A'} |")

    md.append("")
    md.append("---")
    md.append("")

    # Objetivos y métricas
    if d.objetivos or d.metricas_exito or d.piloto_mvp:
        md.append("## Objetivos y Métricas de Éxito")
        md.append("")
        md.append("| Elemento | Detalle |")
        md.append("|----------|---------| ")
        if d.objetivos:
            md.append(f"| Objetivo principal | {d.objetivos[:200]} |")
        if d.metricas_exito:
            md.append(f"| Métricas de éxito | {d.metricas_exito[:200]} |")
        if d.piloto_mvp:
            md.append(f"| Caso piloto/MVP | {d.piloto_mvp[:200]} |")
        md.append("")
        md.append("---")
        md.append("")

    # Casos de uso
    if d.casos_uso:
        md.append("## Casos de Uso Candidatos (Sección C del Diagnóstico)")
        md.append("")
        if d.tema == "quick_suite":
            md.append("| # | Proceso / tarea | Dolor | Frecuencia | Prioridad | Capacidad Quick sugerida |")
            md.append("|---|-----------------|-------|------------|-----------|--------------------------| ")
            for i, c in enumerate(d.casos_uso, 1):
                cap = c.capacidad or tema_mod.capacidad_sugerida(c.proceso)
                md.append(f"| {i} | {c.proceso} | {c.dolor or 'N/A'} | {c.frecuencia or 'N/A'} | {c.prioridad} | {cap} |")
        else:
            md.append("| # | Proceso / tarea | Dolor / cuello de botella | Frecuencia | Prioridad |")
            md.append("|---|-----------------|---------------------------|------------|-----------|")
            for i, c in enumerate(d.casos_uso, 1):
                md.append(f"| {i} | {c.proceso} | {c.dolor or 'N/A'} | {c.frecuencia or 'N/A'} | {c.prioridad} |")
        md.append("")
        if d.piloto_mvp:
            md.append(f"**Caso piloto/MVP:** {d.piloto_mvp}")
            md.append("")
        md.append("*Las sesiones 3-6 se diseñan alrededor de estos casos de uso.*")
        md.append("")
        md.append("---")
        md.append("")

    # Estructura del programa
    md.append("## Estructura del Programa (6 sesiones × 2 horas)")
    md.append("")
    md.append("| Bloque | Sesiones | Enfoque |")
    md.append("|--------|----------|---------|")
    md.append("| **Bloque 1: Fundamentos y Configuración** | Sesiones 1-3 | Setup, conexión de fuentes, capacidades avanzadas |")
    md.append("| **Bloque 2: Aplicación, Retro y Cierre** | Sesiones 4-6 | Casos reales, automatización, gobernanza y cierre |")
    md.append("")
    md.append("---")
    md.append("")

    # Sesiones
    for i, s in enumerate(sesiones):
        md.append(f"### {s.titulo_md}")
        md.append(f"*{s.descripcion_md}*")
        md.append("")
        md.append(f"**Semana:** {i + 1} | **Duración:** {DURACION_SESION} horas")
        md.append(f"**Participantes:** {d.participantes_desc()[:80]}")
        if d.tema == "quick_suite" and i >= 2:
            md.append(f"**Enfoque aplicado:** {d.piloto_mvp or 'caso piloto'}")
        md.append("")
        md.append("**Sub-actividades:**")
        for line in s.sub_actividades.split("\n"):
            md.append(_vineta(line))
        md.append("")
        md.append("---")
        md.append("")

    return "\n".join(md)


def _vineta(line: str) -> str:
    """Convierte una línea del contenido del tema en una viñeta Markdown con nivel.

    El contenido usa '—' para el primer nivel y '——' para el segundo (anidado).
    """
    line = line.strip()
    if not line:
        return ""
    if line.startswith("——"):
        return f"  - {line[2:].strip()}"   # sub-item anidado
    if line.startswith("—"):
        return f"- {line[1:].strip()}"     # item de primer nivel
    return f"- {line}"


# ─────────────────────────────────────────────────────────────────────────────
# PLAN DE ENSEÑANZA (.md)
# ─────────────────────────────────────────────────────────────────────────────
def plan_ensenanza(d: DatosCliente, tema_mod) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y")
    meta = tema_mod.META
    modulos = tema_mod.modulos_plan(d)
    recomendaciones = getattr(tema_mod, "RECOMENDACIONES", None)
    if recomendaciones is None:
        # Buscar en los sub-módulos del plan
        plan_mod = getattr(tema_mod, "_kiro_plan", None) or getattr(tema_mod, "_quick_plan", None)
        if plan_mod is None:
            from .temas import _kiro_plan, _quick_plan
            plan_mod = _quick_plan if d.tema == "quick_suite" else _kiro_plan
        recomendaciones = getattr(plan_mod, "RECOMENDACIONES", [])

    md = []
    md.append(f"# Plan de Enseñanza — {meta['titulo_programa']} para {d.empresa}")
    md.append("")
    md.append(f"> Generado el {fecha}")
    md.append("")
    md.append("---")
    md.append("")

    # Resumen
    md.append("## Resumen General")
    md.append("")
    md.append("| Elemento | Valor |")
    md.append("|----------|-------|")
    md.append(f"| Cliente | {d.empresa} |")
    md.append(f"| Total de Sesiones | 6 |")
    md.append(f"| Horas Estimadas | 12 horas (2h por sesión) |")
    md.append(f"| Bloque 1 (Fundamentos) | Sesiones 1-3 — Setup, conexión de fuentes, capacidades avanzadas |")
    md.append(f"| Bloque 2 (Aplicación) | Sesiones 4-6 — Automatización, retro, cierre |")
    md.append(f"| Distribución por sesión | 30% teoría · 50% práctica guiada · 20% cierre |")
    md.append(f"| Audiencia | {meta['audiencia']} |")
    nivel_label = "IA agéntica" if d.tema == "quick_suite" else "prompting"
    md.append(f"| Nivel inicial en {nivel_label} | {d.nivel_madurez or 'N/A'}/5 |")
    md.append(f"| Horizonte | {d.duracion or meta['duracion_default']} |")
    md.append("")
    md.append("---")
    md.append("")

    # Bloques
    md.append("## BLOQUE 1: Fundamentos y Configuración")
    md.append("")
    for i, m in enumerate(modulos[:3]):
        _render_modulo(md, m)
    md.append("## BLOQUE 2: Aplicación, Retro y Cierre")
    md.append("")
    for m in modulos[3:]:
        _render_modulo(md, m)

    # Recomendaciones
    if recomendaciones:
        md.append("## Recomendaciones Generales")
        md.append("")
        for i, r in enumerate(recomendaciones, 1):
            md.append(f"{i}. {r}")
        md.append("")

    return "\n".join(md)


def _render_modulo(md, m):
    md.append(f"### {m.titulo}")
    md.append("")
    md.append(f"**Duración:** 2 horas | **Semana:** {m.semana}")
    if m.subtitulo:
        md.append(f"\n{m.subtitulo}")
    md.append("")
    if m.contenido_tematico:
        md.append("#### Contenido Temático")
        md.append("")
        for c in m.contenido_tematico:
            md.append(f"1. {c}")
        md.append("")
    if m.objetivos:
        md.append("#### Objetivos de Aprendizaje")
        md.append("")
        md.append("Al finalizar, el participante será capaz de:")
        for o in m.objetivos:
            md.append(f"- {o}")
        md.append("")
    if m.actividades:
        md.append("#### Actividades Prácticas")
        md.append("")
        for a in m.actividades:
            md.append(f"- {a}")
        md.append("")
    if m.criterios:
        md.append("#### Criterios de Evaluación")
        md.append("")
        for c in m.criterios:
            md.append(f"- {c}")
        md.append("")
    if m.material_referencia:
        md.append("#### Material de Referencia")
        md.append("")
        for line in m.material_referencia:
            md.append(line)
        md.append("")
    md.append("---")
    md.append("")


# ─────────────────────────────────────────────────────────────────────────────
# DISEÑO DE ACTIVIDADES (.md)
# ─────────────────────────────────────────────────────────────────────────────
def diseno_actividades(d: DatosCliente, tema_mod) -> str:
    fecha = datetime.now().strftime("%d/%m/%Y")
    meta = tema_mod.META
    acts = tema_mod.actividades(d)
    cfg = tema_mod.config_recomendada(d)

    md = []
    md.append(f"# Diseño de Actividades — {meta['titulo_programa']} para {d.empresa}")
    md.append("")
    md.append(f"> Cliente: {d.empresa}")
    md.append(f"> Nivel {('IA agéntica' if d.tema == 'quick_suite' else 'prompting')}: {d.nivel_madurez or 'N/A'}/5"
              f" | Áreas: {d.areas or d.num_personas or 'N/A'}")
    md.append(f"> Generado el {fecha}")
    md.append("")
    md.append("---")
    md.append("")

    # Contexto
    md.append("## Contexto del Cliente")
    md.append("")
    md.append(f"- **Enfoque:** {meta['titulo_programa']}")
    md.append(f"- **Áreas:** {d.areas or d.num_personas or 'N/A'}")
    md.append(f"- **Champion:** {d.champion_legible()}")
    if d.tema == "quick_suite":
        md.append(f"- **Conocimiento organizacional:** {d.conocimiento_org or 'N/A'}")
        md.append(f"- **Apps de negocio críticas:** {d.apps_negocio or 'N/A'}")
        md.append(f"- **Herramienta IA actual:** {d.herramientas_ia or 'N/A'}")
        md.append(f"- **Aprovisionamiento:** {d.acceso_aws or 'N/A'}")
        md.append(f"- **Plan:** {d.plan_producto or 'N/A'}")
    else:
        md.append(f"- **Stack:** {(d.stack or 'N/A')[:120]}")
        md.append(f"- **Herramientas IA:** {d.herramientas_ia or 'Ninguna'}")
    md.append(f"- **Horizonte:** {d.timeline or d.duracion or 'N/A'}")
    md.append(f"- **Objetivo:** {(d.objetivos or 'N/A')[:120]}")
    md.append(f"- **Métricas:** {(d.metricas_exito or 'N/A')[:120]}")
    md.append("")
    md.append("---")
    md.append("")

    # Casos de uso
    if d.casos_uso:
        md.append("## Casos de Uso Candidatos para el Programa (del Diagnóstico)")
        md.append("")
        md.append("| # | Proceso / tarea | Dolor | Frecuencia | Prioridad |")
        md.append("|---|-----------------|-------|------------|-----------|")
        for i, c in enumerate(d.casos_uso, 1):
            md.append(f"| {i} | {c.proceso} | {c.dolor or 'N/A'} | {c.frecuencia or 'N/A'} | {c.prioridad} |")
        md.append("")
        if d.piloto_mvp:
            md.append(f"**Caso piloto/MVP:** {d.piloto_mvp}")
        md.append("")
        md.append("*Las sesiones 3-6 se diseñan alrededor de estos casos de uso.*")
        md.append("")
        md.append("---")
        md.append("")

    # Sesiones detalladas
    for s in acts:
        md.append(f"## {s.titulo}")
        md.append("")
        if s.subtitulo:
            md.append(s.subtitulo)
            md.append("")
        if s.agenda:
            md.append("### Agenda")
            md.append("")
            md.append("| Bloque | Duración | Actividad |")
            md.append("|--------|----------|-----------|")
            for bloque, dur, act in s.agenda:
                md.append(f"| {bloque} | {dur} | {act} |")
            md.append("")
        for bloque in s.bloques:
            md.append(bloque)
            md.append("")
        md.append("---")
        md.append("")

    # Resumen de configuración recomendada
    md.append("## Resumen de Configuración Recomendada")
    md.append("")
    _render_config(md, d, cfg)
    md.append("")
    md.append("---")
    md.append("")
    md.append(f"*Diseño de actividades generado a partir del Cuestionario de Diagnóstico de {d.empresa} ({meta['producto']})*")
    md.append("")

    return "\n".join(md)


def _render_config(md, d, cfg):
    """Renderiza la sección de configuración recomendada según el tema."""
    if d.tema == "quick_suite":
        # Spaces
        if cfg.get("spaces"):
            md.append("### Spaces")
            md.append("")
            md.append("| Space | Contenido | Descripción |")
            md.append("|-------|-----------|-------------|")
            for name, cont, desc in cfg["spaces"]:
                md.append(f"| `{name}` | {cont} | {desc} |")
            md.append("")
        # Knowledge Bases
        if cfg.get("conocimiento"):
            md.append("### Knowledge Bases")
            md.append("")
            md.append("| Fuente | Tipo | Prioridad | Uso |")
            md.append("|--------|------|-----------|-----|")
            for fuente, tipo, prio, uso in cfg["conocimiento"]:
                md.append(f"| {fuente} | {tipo} | {prio} | {uso} |")
            md.append("")
        # Conectores de acción
        if cfg.get("accion"):
            md.append("### Conectores de Acción")
            md.append("")
            md.append("| Conector | Tipo | Prioridad | Uso |")
            md.append("|----------|------|-----------|-----|")
            for app, tipo, prio, uso in cfg["accion"]:
                md.append(f"| {app} | {tipo} | {prio} | {uso} |")
            md.append("")
        # Agentes
        if cfg.get("agentes"):
            md.append("### Chat Agents / Autonomous Agents")
            md.append("")
            md.append("| Agente | Descripción |")
            md.append("|--------|-------------|")
            for name, desc in cfg["agentes"]:
                md.append(f"| {name} | {desc} |")
            md.append("")
        # Flows
        if cfg.get("flows"):
            md.append("### Quick Flows / Automate")
            md.append("")
            md.append("| Flow | Disparo | Acción |")
            md.append("|------|---------|--------|")
            for name, disp, acc in cfg["flows"]:
                md.append(f"| {name} | {disp} | {acc} |")
            md.append("")
    else:
        # Kiro config: MCPs, steerings, hooks, agentes
        if cfg.get("mcps"):
            md.append("### MCPs Recomendados")
            md.append("")
            md.append("| MCP | Comando | Uso |")
            md.append("|-----|---------|-----|")
            for name, cmd, uso in cfg["mcps"]:
                md.append(f"| {name} | `{cmd}` | {uso} |")
            md.append("")
        if cfg.get("steerings"):
            md.append("### Steerings Recomendados")
            md.append("")
            md.append("| Archivo | Inclusión | Propósito |")
            md.append("|---------|-----------|-----------|")
            for name, incl, prop in cfg["steerings"]:
                md.append(f"| `{name}` | {incl} | {prop} |")
            md.append("")
        if cfg.get("hooks"):
            md.append("### Hooks Recomendados")
            md.append("")
            md.append("| Hook | Trigger | Acción |")
            md.append("|------|---------|--------|")
            for name, trig, acc in cfg["hooks"]:
                md.append(f"| {name} | `{trig}` | {acc} |")
            md.append("")
        if cfg.get("agentes"):
            md.append("### Agents Personalizados")
            md.append("")
            md.append("| Agente | Descripción |")
            md.append("|--------|-------------|")
            for name, desc in cfg["agentes"]:
                md.append(f"| {name} | {desc} |")
            md.append("")
