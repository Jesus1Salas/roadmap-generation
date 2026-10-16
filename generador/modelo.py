"""
Modelo de datos común para ambos temas (Kiro y Quick Suite).

`DatosCliente` es la estructura unificada que produce el parser del cuestionario y
consume el renderizador. Los campos que no aplican a un tema simplemente quedan vacíos.
"""

from dataclasses import dataclass, field
from typing import List, Dict


def _nombre_valido(valor: str) -> str:
    """Devuelve el valor si parece un nombre de persona/rol real; '' si es texto-guía.

    Rechaza fragmentos del formulario como '(administrador de la plataforma...)' o
    frases con paréntesis de guía y sin un nombre reconocible.
    """
    v = (valor or "").strip()
    if not v or len(v) < 3:
        return ""
    # Rechazar si empieza con paréntesis (típico de texto-guía) o contiene frases guía
    if v.startswith("(") or v.startswith("["):
        return ""
    guia = ["administrador de la plataforma", "líder de datos", "lider de datos",
            "dueño de proceso", "sponsor)", "perfil ", "y un", "idealmente"]
    low = v.lower()
    if any(g in low for g in guia):
        return ""
    return v


@dataclass
class CasoUso:
    """Un caso de uso candidato extraído de la Sección C del cuestionario."""
    proceso: str = ""
    dolor: str = ""
    frecuencia: str = ""
    prioridad: str = ""  # Alta / Media / Baja
    capacidad: str = ""  # (solo Quick) Agentes / Research / BI / Automate / Apps


@dataclass
class DatosCliente:
    """Estructura unificada del cliente, agnóstica al tema.

    Campos comunes a ambos cuestionarios + campos específicos de cada tema.
    Un campo vacío significa "no reportado en el cuestionario".
    """

    # ── Tema detectado ──
    tema: str = "kiro"  # "kiro" | "quick_suite"

    # ── Identidad / contacto (común) ──
    empresa: str = ""
    fecha: str = ""
    perfil_tecnico: str = ""
    perfil_negocio: str = ""
    champion: str = ""

    # ── Alcance / organización (común) ──
    proyecto: str = ""            # Kiro: proyecto | Quick: área(s) de aplicación
    areas: str = ""              # áreas/departamentos participantes
    num_personas: str = ""
    num_equipos_paralelo: str = ""
    cultura_cambio: str = ""
    resistencias: str = ""

    # ── Contexto técnico (Kiro) ──
    stack: str = ""
    arquitectura: str = ""
    repositorios_ci_cd: str = ""
    tipo_proyecto: str = ""
    disenos_specs: str = ""
    acceso_aws: str = ""

    # ── Contexto de negocio (Quick) ──
    herramientas_colaboracion: str = ""   # Slack/Teams/Outlook/Google/Otro
    conocimiento_org: str = ""            # dónde vive el conocimiento (Confluence, etc.)
    apps_negocio: str = ""                # apps críticas (Jira, Salesforce, etc.)
    procesos_manuales: str = ""           # procesos manuales/repetitivos
    fuentes_datos: str = ""               # fuentes a conectar a Quick Index
    seguridad_compliance: str = ""        # requisitos de seguridad/privacidad
    iniciativas_previas: str = ""         # RPA/chatbots/BI previos
    apps_sin_codigo: str = ""             # necesidad de apps internas
    autonomia_agentes: str = ""           # aprobación paso a paso / media / amplia
    plan_producto: str = ""               # Free/Plus/Pro/Enterprise (Quick) o tier licencias

    # ── IA / madurez (común, distinto label por tema) ──
    herramientas_ia: str = ""             # herramienta IA actual del equipo
    nivel_madurez: str = ""               # 1-5 (Kiro: prompting | Quick: IA agéntica)
    integraciones: str = ""               # integraciones/sistemas a conectar

    # ── Casos de uso (común, Sección C) ──
    casos_uso: List[CasoUso] = field(default_factory=list)
    piloto_mvp: str = ""

    # ── Objetivos / métricas (común, Sección E) ──
    fricciones: str = ""
    objetivos: str = ""
    metricas_exito: str = ""
    timeline: str = ""
    duracion: str = ""
    comentarios: str = ""

    # ── Extra / libre ──
    extra: Dict[str, str] = field(default_factory=dict)

    # ── Helpers ──
    def nombre_carpeta(self) -> str:
        """Nombre de la carpeta del cliente: Recursos_{empresa}."""
        emp = self.empresa.strip() or "Cliente"
        return f"Recursos_{emp}"

    def subcarpeta_tema(self) -> str:
        """Subcarpeta del tema dentro de clientes/: 'Kiro' o 'Quick Suite'."""
        return "Quick Suite" if self.tema == "quick_suite" else "Kiro"

    def ruta_salida(self, base: str) -> str:
        """Ruta completa de salida: {base}/clientes/{tema}/{Recursos_empresa}.

        Args:
            base: directorio raíz del workspace (donde vive generador/).
        """
        import os
        return os.path.join(base, "clientes", self.subcarpeta_tema(), self.nombre_carpeta())

    def nivel_int(self, default: int = 3) -> int:
        """Nivel de madurez como entero (1-5), con fallback."""
        try:
            return int(str(self.nivel_madurez).strip()[0])
        except (ValueError, IndexError):
            return default

    def participantes_desc(self) -> str:
        """Descripción legible de participantes: combina áreas y personas.

        Ej: 'Operaciones, RRHH (2 personas)' o '4 equipos, 16 personas'.
        """
        areas = (self.areas or "").strip()
        personas = (self.num_personas or "").strip()
        if areas and personas:
            # Si personas es solo un número, formatearlo como "(N personas)"
            if personas.isdigit():
                return f"{areas} ({personas} personas)"
            return f"{areas} — {personas}"
        if areas:
            return areas
        if personas:
            return personas
        return "Equipo completo"

    def champion_legible(self) -> str:
        """Nombre del champion; si es ambiguo ('ambas', 'ambos'), usa un perfil válido."""
        champ = (self.champion or "").strip()
        ambiguos = {"ambas", "ambos", "los dos", "las dos", "ambas personas", "n/a", ""}
        if champ.lower() in ambiguos:
            # Preferir un perfil que parezca un nombre real (no texto-guía del formulario)
            for perfil in (self.perfil_tecnico, self.perfil_negocio):
                nombre = _nombre_valido(perfil)
                if nombre:
                    # Conservar la nota original si aportaba matiz (ej. "ambas")
                    return f"{nombre} ({champ})" if champ and champ.lower() not in {"n/a", ""} else nombre
            return champ or "N/A"
        # Champion explícito y válido
        if _nombre_valido(champ):
            return champ
        # Champion con ruido: intentar un perfil válido; si tampoco, "Por definir"
        for perfil in (self.perfil_tecnico, self.perfil_negocio):
            nombre = _nombre_valido(perfil)
            if nombre:
                return nombre
        return "Por definir"
