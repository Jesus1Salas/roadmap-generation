"""
Módulos de contenido por tema.

Cada tema (kiro, quick_suite) expone la misma interfaz para que los renderizadores
(render_markdown, render_excel) sean agnósticos:

  META                       -> dict con metadatos del tema (nombre, herramienta, etc.)
  sesiones_roadmap(datos)    -> list[SesionRoadmap]   (6 sesiones para el .xlsx y roadmap.md)
  modulos_plan(datos)        -> list[ModuloPlan]      (6 módulos para el plan de enseñanza)
  actividades(datos)         -> list[SesionActividad] (6 sesiones detalladas para el diseño)
  config_recomendada(datos)  -> dict                  (integraciones/artefactos recomendados)

Estructuras de datos comunes en `estructura.py`.
"""

from . import kiro, quick_suite

TEMAS = {
    "kiro": kiro,
    "quick_suite": quick_suite,
}


def obtener(tema: str):
    """Devuelve el módulo de tema correspondiente."""
    if tema not in TEMAS:
        raise ValueError(f"Tema desconocido: {tema}. Opciones: {list(TEMAS)}")
    return TEMAS[tema]
