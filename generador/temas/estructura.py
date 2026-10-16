"""
Estructuras de datos compartidas por los módulos de tema.

Estas dataclasses son el "contrato" entre los temas y los renderizadores:
un tema produce estas estructuras y los renderizadores las convierten a .md / .xlsx.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class SesionRoadmap:
    """Una fila del Roadmap (Excel + roadmap.md)."""
    fase_semana: str        # col A: "Fase 0 /\n (Sem. 1)"
    sesion_track: str       # col B: "Sesión 1 /\n Setup..."
    fase_actividad: str     # col C: "Fase 1: ... / descripción"
    sub_actividades: str    # col D: bloque con "— ..." por línea
    titulo_md: str = ""     # título para el roadmap.md (ej. "Sesión 1: Setup...")
    descripcion_md: str = ""  # subtítulo en cursiva para el roadmap.md


@dataclass
class ModuloPlan:
    """Un módulo del Plan de Enseñanza."""
    titulo: str
    semana: str
    subtitulo: str = ""                  # línea opcional bajo el título (ej. stack aplicado)
    contenido_tematico: List[str] = field(default_factory=list)
    objetivos: List[str] = field(default_factory=list)
    actividades: List[str] = field(default_factory=list)
    criterios: List[str] = field(default_factory=list)
    material_referencia: List[str] = field(default_factory=list)  # bloques markdown ya formateados


@dataclass
class SesionActividad:
    """Una sesión del Diseño de Actividades (detallada)."""
    titulo: str
    subtitulo: str = ""
    agenda: List[Tuple[str, str, str]] = field(default_factory=list)  # (bloque, duración, actividad)
    bloques: List[str] = field(default_factory=list)  # secciones markdown ya formateadas (actividades, prompts, tips)
