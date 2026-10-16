"""
Generador de Planes de Adopción — eTribe.

Genera Roadmap (.xlsx + .md), Plan de Enseñanza (.md) y Diseño de Actividades (.md)
a partir de un cuestionario de diagnóstico, soportando dos temas:
  - "kiro"        → Adopción de Kiro IDE (desarrollo asistido por IA)
  - "quick_suite" → Adopción de Amazon Quick Suite (IA agéntica para el negocio)

Arquitectura:
  cuestionario.py   → extracción de PDF/DOCX, detección de tema y parseo a DatosCliente
  modelo.py         → estructura de datos común (DatosCliente)
  temas/kiro.py     → contenido de las 6 sesiones para Kiro
  temas/quick_suite.py → contenido de las 6 sesiones para Quick Suite
  render_markdown.py → construye los 3 .md a partir del contenido del tema
  render_excel.py   → construye el Roadmap .xlsx usando el template base
  main.py           → orquestador CLI
"""

__version__ = "2.0.0"
