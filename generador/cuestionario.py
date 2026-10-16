"""
Extracción y parseo del cuestionario de diagnóstico.

Responsabilidades:
  1. Extraer texto de PDF o DOCX.
  2. Detectar el tema del cuestionario (kiro | quick_suite).
  3. Parsear el texto a un DatosCliente según el tema.

El parser es tolerante a texto desestructurado (típico de PDFs). Cada campo que
no se logra extraer queda vacío en lugar de romper la generación.
"""

import os
import re
import json
import zipfile

from .modelo import DatosCliente, CasoUso

try:
    import PyPDF2
except ImportError:  # pragma: no cover
    PyPDF2 = None


# ─────────────────────────────────────────────────────────────────────────────
# EXTRACCIÓN DE TEXTO
# ─────────────────────────────────────────────────────────────────────────────
def extraer_texto(ruta: str) -> str:
    """Extrae texto de un PDF o DOCX. Detecta el tipo por extensión."""
    ext = os.path.splitext(ruta)[1].lower()
    if ext == ".pdf":
        return _extraer_pdf(ruta)
    if ext == ".docx":
        return _extraer_docx(ruta)
    if ext in (".md", ".txt"):
        with open(ruta, encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Formato no soportado: {ext} (usa .pdf, .docx o .md)")


def _extraer_pdf(ruta: str) -> str:
    if PyPDF2 is None:
        raise ImportError("PyPDF2 no está instalado. Ejecuta: pip install PyPDF2")
    with open(ruta, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join((p.extract_text() or "") for p in reader.pages)


def _extraer_docx(ruta: str) -> str:
    """Extrae texto de un .docx leyendo word/document.xml (sin dependencias extra)."""
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    # Convertir saltos de párrafo y tabulaciones a texto plano
    xml = xml.replace("</w:p>", "\n").replace("</w:tr>", "\n").replace("</w:tc>", "\t")
    texto = re.sub(r"<[^>]+>", "", xml)
    # Desescapar entidades XML comunes
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")]:
        texto = texto.replace(a, b)
    return texto


# ─────────────────────────────────────────────────────────────────────────────
# DETECCIÓN DE TEMA
# ─────────────────────────────────────────────────────────────────────────────
_KW_QUICK = [
    "amazon quick", "quick suite", "quick sight", "quicksight", "quick index",
    "quick flows", "quick automate", "quick research", "ia agéntica", "ia agentica",
    "spaces/agentes", "asistente de ia", "apps sin código", "apps sin codigo",
]
_KW_KIRO = [
    "kiro", "spec", "steering", "hooks", "vibe", "ide / cli", "workflows del ide",
    "prompt engineering", "stack tecnológico", "greenfield", "brownfield",
]


def detectar_tema(texto: str, nombre_archivo: str = "") -> str:
    """Devuelve 'quick_suite' o 'kiro'. Usa nombre de archivo + contenido."""
    base = (nombre_archivo + " " + texto).lower()

    # 1) Señal fuerte por nombre de archivo
    if "quick" in nombre_archivo.lower():
        return "quick_suite"
    if "kiro" in nombre_archivo.lower():
        return "kiro"

    # 2) Conteo de keywords en el contenido
    score_quick = sum(base.count(kw) for kw in _KW_QUICK)
    score_kiro = sum(base.count(kw) for kw in _KW_KIRO)
    return "quick_suite" if score_quick > score_kiro else "kiro"


def es_cuestionario_tecnico(texto: str) -> bool:
    """Detecta el formato 'Cuestionario Técnico para la demo' (tema Kiro).

    Este cuestionario NO usa el esquema estándar de adopción (Empresa/Organización,
    preguntas '¿...?' numeradas 1..21, checkboxes). En su lugar tiene 4 secciones
    con numeración por punto (1.1, 2.3, 4.2...) y encabezados en mayúsculas:
    CONTEXTO DEL EQUIPO · STACK TECNOLÓGICO · ARQUITECTURA Y PROYECTO · FLUJO DE
    TRABAJO. Se reconoce por esos encabezados + la numeración por punto.
    """
    base = texto.lower()
    tiene_secciones = (
        "contexto del equipo" in base
        and "stack tecnol" in base
        and ("flujo de trabajo" in base or "arquitectura y proyecto" in base)
    )
    tiene_numeracion_punto = bool(re.search(r"\b1\.1\b.*\b2\.1\b", texto, re.DOTALL))
    return tiene_secciones and tiene_numeracion_punto


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE PARSEO
# ─────────────────────────────────────────────────────────────────────────────
def _normalizar(texto: str) -> str:
    """Une líneas, normaliza acentos a NFC y colapsa espacios para el regex."""
    import unicodedata
    texto = unicodedata.normalize("NFC", texto)
    lineas = [l.strip() for l in texto.split("\n") if l.strip()]
    return " ".join(lineas)


def _limpiar(valor: str, max_len: int = 400) -> str:
    """Limpia una respuesta: quita markup Markdown, guiones bajos de relleno y trunca."""
    # Artefactos de Markdown (blockquotes, negritas, checkboxes escapados, tablas)
    valor = valor.replace(">", " ").replace("**", " ")
    valor = valor.replace("\\[", "[").replace("\\]", "]")
    valor = re.sub(r"\[\s*[xX ]?\s*\]", " ", valor)   # checkboxes vacíos o marcados
    valor = re.sub(r"\|+", " ", valor)                  # celdas de tabla
    valor = re.sub(r":-{2,}", " ", valor)               # separadores de tabla
    valor = valor.replace("_", " ")
    valor = re.sub(r"\s+", " ", valor).strip(" .:-\t")
    return valor[:max_len].strip()


def _marcado(texto: str, opciones: list) -> str:
    """Devuelve la primera opción que aparezca marcada con [x]/[X]."""
    for op in opciones:
        # [x] Opcion  (tolerante a espacios)
        if re.search(r"\[\s*[xX]\s*\]\s*" + re.escape(op), texto):
            return op
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# PARSER QUICK SUITE (23 preguntas, secciones A-E)
# ─────────────────────────────────────────────────────────────────────────────
def _parsear_quick(texto: str) -> DatosCliente:
    d = DatosCliente(tema="quick_suite")
    t = _normalizar(texto)

    # ── Datos de contacto ──
    d.empresa = _extraer_entre(t, r"Empresa\s*/?\s*Organizaci[oó]n", r"Fecha de llenado", 60)
    d.fecha = _extraer_entre(t, r"Fecha de llenado", r"Nombre y rol", 40)
    d.perfil_tecnico = _extraer_entre(t, r"Perfil t[eé]cnico\s*/?\s*IT", r"Nombre y rol|Perfil de", 80)
    d.perfil_negocio = _extraer_entre(t, r"Perfil de\s*negocio\s*/?\s*sponsor", r"[ÁA]rea\(s\)|Secci[oó]n", 80)
    d.proyecto = _extraer_entre(t, r"que se aplicar[ií]a Quick", r"Secci[oó]n A|1\.", 120)

    # ── Sección A ──
    d.areas = _resp_pregunta(t, 1, r"[ÁA]reas o departamentos", 120)
    d.herramientas_colaboracion = _marcado(t, ["Slack", "Microsoft Teams", "Outlook", "Google Workspace", "Otro"])
    d.conocimiento_org = _resp_pregunta(t, 3, r"vive hoy el conocimiento", 120)
    d.apps_negocio = _resp_pregunta(t, 4, r"aplicaciones de negocio", 120)
    d.procesos_manuales = _resp_pregunta(t, 5, r"procesos hoy son manuales", 160)
    d.fricciones = d.procesos_manuales
    d.acceso_aws = "Cuenta AWS con IAM Identity Center" if "IAM Identity Center" in t else _marcado(
        t, ["Cuenta AWS con IAM Identity Center", "registro individual"])

    # ── Sección B ──
    d.herramientas_ia = _resp_pregunta(t, 7, r"herramienta de IA generativa", 80)
    d.nivel_madurez = _nivel_15(t)
    d.fuentes_datos = _resp_pregunta(t, 9, r"fuentes de datos", 120)
    d.integraciones = ", ".join(x for x in [d.apps_negocio, d.conocimiento_org] if x)
    d.seguridad_compliance = _resp_pregunta(t, 10, r"seguridad, privacidad o compliance", 120)
    d.iniciativas_previas = _resp_pregunta(t, 11, r"iniciativas de automatizaci[oó]n", 120)

    # ── Sección C: casos de uso (tabla) + piloto ──
    d.casos_uso = _casos_uso_quick(texto)
    d.piloto_mvp = _resp_pregunta(t, 12, r"elegir[ií]an como piloto", 120)
    d.apps_sin_codigo = _resp_pregunta(t, 13, r"aplicaciones internas simples", 80)

    # ── Sección D ──
    d.num_personas = _resp_pregunta(t, 14, r"personas y qu[eé] [áa]reas", 80)
    d.champion = _resp_pregunta(t, 15, r"champion", 80)
    d.autonomia_agentes = _marcado(t, [
        "Aprobación paso a paso", "Autonomía media", "Autonomía\namplia",
        "Autonomía amplia", "Aún no definido", "A\u00fan no definido"]) or "Aún no definido"
    d.cultura_cambio = _marcado(t, ["Muy abierta / entusiasta", "Neutral", "Resistente"]) or "No especificado"
    d.resistencias = _resp_pregunta(t, 18, r"resistencia o preocupaci[oó]n", 120)
    d.num_equipos_paralelo = _marcado(t, ["Una sola [áa]rea", "2-3 [áa]reas", "4 o m[áa]s [áa]reas"]) \
        or _marcado(t, ["Una sola área", "2-3 áreas", "4 o más áreas"]) or "No especificado"

    # ── Sección E ──
    d.objetivos = _resp_pregunta(t, 20, r"esperan lograr al final", 160)
    d.metricas_exito = _resp_pregunta(t, 21, r"medir el [eé]xito", 160)
    d.timeline = _resp_pregunta(t, 22, r"fecha l[ií]mite, evento", 60)
    d.plan_producto = _marcado(t, ["Free / Plus", "Pro", "Enterprise"]) or "Pro"
    d.duracion = _marcado(t, ["4-5 semanas", "6-7 semanas", "8+ semanas"]) or (
        d.timeline if d.timeline else "programa acotado")

    return d


def _casos_uso_quick(texto: str) -> list:
    """Extrae la tabla de casos de uso de la Sección C del cuestionario de Quick.

    La tabla tiene columnas: Proceso | Dolor | Frecuencia | Prioridad.
    En el PDF llega desestructurada, así que buscamos por marcadores de prioridad.
    """
    t = _normalizar(texto)
    # Aislar el bloque entre "Sección C" y la pregunta 12
    m = re.search(r"Secci[oó]n C(.+?)12\.", t, re.DOTALL | re.IGNORECASE)
    bloque = m.group(1) if m else t

    casos = []
    # Cada fila termina en una prioridad; capturamos el texto previo
    for match in re.finditer(r"([A-ZÁÉÍÓÚ][^|]{5,80}?)\s*(?:Es manual|Manual)?\s*"
                             r"(Cada[^A-Z]{0,40}|Al finalizar[^A-Z]{0,40})?\s*(Alta|Media|Baja)", bloque):
        proceso = _limpiar(match.group(1), 80)
        frecuencia = _limpiar(match.group(2) or "", 60)
        prioridad = match.group(3)
        proc_low = proceso.lower()
        # Filtrar ruido: encabezados de la tabla ("Prioridad (Alta/Media/Baja)"),
        # celdas vacías y fragmentos sin contenido real.
        es_ruido = (
            not proceso
            or "prioridad" in proc_low
            or proc_low.startswith("proceso")
            or "media/" in proc_low
            or "alta/media" in proc_low
            or len(re.sub(r"[^a-záéíóúñ ]", "", proc_low).strip()) < 5
        )
        if not es_ruido:
            casos.append(CasoUso(proceso=proceso, dolor="Es manual", frecuencia=frecuencia, prioridad=prioridad))
    return casos[:5]


def _nivel_15(t: str) -> str:
    """Extrae el nivel 1-5 marcado (pregunta 8 de Quick)."""
    for n in range(5, 0, -1):
        if re.search(r"\[\s*[xX]\s*\]\s*" + str(n) + r"\b", t):
            return str(n)
    return ""


def _extraer_entre(t: str, ini_pat: str, fin_pat: str, max_len: int) -> str:
    # Añadimos una barrera implícita para números de pregunta pegados ("2.¿")
    barrera = fin_pat + r"|\d{1,2}\.\s*[¿A-ZÁÉÍÓÚ]"
    m = re.search(ini_pat + r"\s*(.+?)\s*(?:" + barrera + r")", t, re.IGNORECASE)
    return _limpiar(m.group(1), max_len) if m else ""


def _resp_pregunta(t: str, num: int, pregunta_pat: str, max_len: int) -> str:
    """Extrae la respuesta de una pregunta numerada del cuestionario de Quick.

    Estrategia: localizar la pregunta N y capturar el texto hasta la siguiente
    pregunta numerada (N+1, N+2...) o sección, removiendo enunciado y ejemplos.
    """
    # El texto normalizado pega el número a la pregunta sin espacio: "2.¿Qué..."
    # Boundary: cualquier "<numero>." o "Sección" o "Comentarios" que siga.
    m = re.search(rf"(?:^|\D){num}\.\s*(.+?)(?=\d{{1,2}}\.\s*[¿A-ZÁÉÍÓÚ]|Secci[oó]n\s|Comentarios\s|$)",
                  t, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    bloque = m.group(1)
    # Quitar el enunciado (hasta el primer '?') — el enunciado siempre es una pregunta
    if "?" in bloque:
        bloque = bloque.split("?", 1)[1]
    # Quitar ejemplos "Ej. ..." (hasta el siguiente marcador de relleno o fin)
    bloque = re.sub(r"Ej\.[^_\[\n]*", "", bloque, flags=re.IGNORECASE)
    # Quitar frases-guía comunes que no son respuesta
    bloque = re.sub(r"Indicar si[^_.]*\.?", "", bloque, flags=re.IGNORECASE)
    bloque = re.sub(r"Quick permite[^_.]*\.?", "", bloque, flags=re.IGNORECASE)
    bloque = re.sub(r"Idealmente[^_)]*\)?", "", bloque, flags=re.IGNORECASE)
    # Quitar líneas de ejemplo que enumeran opciones y terminan en "etc."
    bloque = re.sub(r"Documentos,\s*wikis[^.]*etc\.?", "", bloque, flags=re.IGNORECASE)
    bloque = re.sub(r"[A-ZÁÉÍÓÚ][^.]*\betc\.", "", bloque)
    # Quitar checkboxes
    bloque = re.sub(r"\[\s*[xX ]\s*\][^\[\n]*", "", bloque)
    return _limpiar(bloque, max_len)


# ─────────────────────────────────────────────────────────────────────────────
# PARSER KIRO (21 preguntas) — reutiliza la lógica probada del script original
# ─────────────────────────────────────────────────────────────────────────────
def _parsear_kiro(texto: str) -> DatosCliente:
    d = DatosCliente(tema="kiro")
    t = _normalizar(texto)

    # Preguntas numeradas → dict {num: respuesta cruda (sin el enunciado)}
    respuestas, pre = _indexar_preguntas_kiro(t)

    # ── Anclado por CONTENIDO del enunciado (robusto a la numeración) ──
    # El cuestionario estándar de Kiro tiene 21 preguntas; algunas variantes
    # insertan una sección extra ("Tipos de Usuario") que corre la numeración.
    # Por eso localizamos cada campo por el texto distintivo de su pregunta,
    # no por su número.
    def q(patrones, max_len, quitar_ej=False):
        """Busca la 1ª pregunta cuyo enunciado casa alguno de los patrones.

        La limpieza de texto-guía y de ejemplos 'Ej. ...' la realiza
        `_limpiar_kiro_resp`; el parámetro `quitar_ej` se conserva por
        compatibilidad pero ya no aplica un recorte propio (que truncaba mal).
        """
        num = _pregunta_por_texto(t, patrones)
        if num is None or num not in respuestas:
            return ""
        return _limpiar_kiro_resp(respuestas[num], max_len)

    d.empresa = _extraer_entre(pre, r"Empresa\s*/?\s*Organizaci[oó]n", r"Fecha|\d{1,2}\s+de", 60)
    d.fecha = _extraer_entre(pre, r"Fecha de llenado", r"Nombre", 40)
    d.perfil_tecnico = _extraer_entre(pre, r"Perfil t[eé]cnico", r"Nombre y rol|Perfil de negocio", 80)
    d.perfil_negocio = _extraer_entre(pre, r"Perfil de negocio\s*/?\s*sponsor", r"Proyecto|Secci[oó]n", 80)
    d.champion = d.perfil_tecnico
    d.proyecto = _extraer_entre(pre + t[:3000], r"aplicar[ií]a Kiro", r"Secci[oó]n|A completar|1\.", 120)

    d.stack = q([r"stack tecnol[oó]gico"], 500, quitar_ej=True)
    d.arquitectura = _marcado(t, ["Monolito distribuido", "Microservicios", "Serverless", "Monolito"])
    d.repositorios_ci_cd = q([r"D[oó]nde vive el c[oó]digo", r"flujo de trabajo actual"], 300, quitar_ej=True)
    d.tipo_proyecto = _marcado(t, ["Greenfield", "Brownfield", "Mixto"])
    d.disenos_specs = q([r"dise[ñn]os o especificaciones", r"Figma"], 300, quitar_ej=True)
    d.integraciones = q([r"integraciones o sistemas externos"], 300, quitar_ej=True)
    d.acceso_aws = _acceso_aws_kiro(t)

    d.herramientas_ia = q([r"herramienta de IA para desarrollo", r"herramienta de IA"], 200, quitar_ej=True)
    d.nivel_madurez = _nivel_15(t)
    d.fricciones = q([r"consumen m[aá]s tiempo", r"generan m[aá]s fricci[oó]n"], 500, quitar_ej=True)
    exp = q([r"experiencia previa"], 500, quitar_ej=True)
    if exp:
        d.extra["experiencia_ia"] = exp

    d.casos_uso = _casos_uso_kiro(t)
    d.piloto_mvp = q([r"elegir[ií]an como piloto", r"piloto o MVP"], 400, quitar_ej=True)

    d.num_personas = q([r"personas conforman el equipo", r"Cu[aá]ntas personas"], 300, quitar_ej=True)
    d.champion = q([r"champion\(s\) t[eé]cnico", r"champion"], 200, quitar_ej=True) or d.champion
    d.cultura_cambio = _marcado(t, ["Muy abierta", "Neutral", "Resistente"]) or "No especificado"
    d.resistencias = q([r"resistencia o preocupaci[oó]n"], 500, quitar_ej=True)
    d.num_equipos_paralelo = _equipos_kiro(t)

    d.objetivos = q([r"esperan lograr al final"], 500, quitar_ej=True)
    d.metricas_exito = q([r"medir el [eé]xito"], 500, quitar_ej=True)
    d.timeline = q([r"fecha l[ií]mite, evento", r"hito de negocio"], 100, quitar_ej=True)
    d.duracion = _marcado(t, ["6-7 semanas", "4-5 semanas", "8+"]) or "6-7 semanas (programa estándar)"

    return d


def _indexar_preguntas_kiro(t: str):
    """Indexa las preguntas numeradas del cuestionario Kiro.

    Devuelve (respuestas, pre) donde `respuestas` mapea número → texto de la
    respuesta (con el enunciado ya removido) y `pre` es el bloque previo a la
    primera pregunta (datos de contacto).
    """
    respuestas = {}
    matches = list(re.finditer(r"(?:^|\s|>)(\d{1,2})\.\s*(?:\*\*)?\s*(?:¿|[A-Z])", t))
    for i, mt in enumerate(matches):
        num = int(mt.group(1))
        fin = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        contenido = t[mt.start():fin]
        if "?" in contenido:
            contenido = contenido.split("?", 1)[1]
        else:
            contenido = re.sub(r"^\s*>?\s*\d{1,2}\.\s*\*{0,2}", "", contenido)
        contenido = contenido.strip()
        # Rango amplio (hasta 25) para soportar variantes con secciones extra.
        if 1 <= num <= 25 and len(contenido) > 2:
            respuestas[num] = contenido
    pre = t[: matches[0].start()] if matches else t[:2000]
    return respuestas, pre


def _pregunta_por_texto(t: str, patrones):
    """Devuelve el número de la pregunta cuyo enunciado casa algún patrón.

    Recorre los enunciados "N. ¿...?" del texto normalizado y devuelve el N
    de la primera pregunta que contenga alguno de los `patrones` (regex).
    """
    for mt in re.finditer(r"(?:^|\s|>)(\d{1,2})\.\s*(?:\*\*)?\s*(¿[^?]{0,160}\?)", t):
        enunciado = mt.group(2)
        for pat in patrones:
            if re.search(pat, enunciado, re.IGNORECASE):
                return int(mt.group(1))
    return None


# Texto-guía (boilerplate) que el formulario Kiro coloca bajo ciertas preguntas,
# entre el enunciado y la respuesta del cliente. Se elimina de forma LITERAL para
# no tocar la respuesta real (fidelidad al origen). Cada entrada es el prefijo-guía
# tal cual aparece tras normalizar el texto.
_GUIA_KIRO = [
    "Lenguajes, frameworks (frontend/backend), base de datos, infraestructura "
    "(cloud, contenedores, etc.).",
    "Repositorio(s), ramas, ambientes (dev/staging/prod), proceso de CI/CD si existe.",
    "Si aplica Figma: indicar si los componentes están bien nombrados y organizados "
    "con auto-layout.",
]


def _quitar_ejemplo_kiro(valor: str) -> str:
    """Elimina una cláusula-guía 'Ej. ...' que precede a la respuesta real.

    El texto-guía va desde 'Ej.' hasta el final de esa oración. Se respetan las
    abreviaturas internas ('vs.', 'Ej.') para no cortar la guía a mitad. Si tras
    'Ej.' no hay respuesta real, se conserva el texto original (no se inventa).
    """
    m = re.search(r"Ej\.", valor, flags=re.IGNORECASE)
    if not m:
        return valor
    i = m.end()
    # Avanzar hasta un '.' que termine oración (no seguido de abreviatura conocida).
    resto = valor[i:]
    for pm in re.finditer(r"\.", resto):
        j = pm.end()
        # Palabra previa al punto: si es abreviatura común, no es fin de oración.
        prev = resto[max(0, pm.start() - 3):pm.start()].strip().lower()
        if prev in {"vs", "ej"}:
            continue
        cola = resto[j:].strip()
        # Solo recortamos si detrás del punto hay contenido (la respuesta real).
        if cola:
            return cola
        break
    return valor


def _quitar_guia_kiro(valor: str) -> str:
    """Elimina, si está presente al inicio, un texto-guía conocido del formulario."""
    v = valor.lstrip(" .:-–")
    for guia in _GUIA_KIRO:
        if v.startswith(guia):
            return v[len(guia):].lstrip(" .:-–")
    return valor


def _limpiar_kiro_resp(valor: str, max_len: int) -> str:
    """Limpia respuestas de Kiro removiendo el enunciado residual y frases-guía."""
    # Quitar enunciado hasta el primer '?'
    if "?" in valor:
        valor = valor.split("?", 1)[1]
    # Quitar el texto-guía del formulario (boilerplate del cuestionario, no del
    # cliente). Se elimina de forma literal para no alterar la respuesta real.
    valor = _quitar_guia_kiro(valor)
    # Quitar frases-guía comunes (aparecen tras el enunciado, antes de la respuesta):
    #   "Ej. ... etc." · "Idealmente ..." · "Indicar si ..." · "Si aplica ...:"
    valor = _quitar_ejemplo_kiro(valor)
    valor = re.sub(r"Idealmente[^.]*\.", "", valor, flags=re.IGNORECASE)
    valor = re.sub(r"Indicar si[^.]*\.", "", valor, flags=re.IGNORECASE)
    valor = re.sub(r"Si aplica[^:]*:", "", valor, flags=re.IGNORECASE)
    # Quitar un paréntesis-guía inicial suelto del tipo "(frontend, backend, etc.)."
    valor = re.sub(r"^\s*\([^)]*\)\.?", "", valor)
    # Quitar fragmentos huérfanos al inicio (ej. ") .", "). ", ") - " restos del enunciado)
    valor = re.sub(r"^[\s\)\.\,;:\-–]+", "", valor)
    return _limpiar(valor, max_len)


def _acceso_aws_kiro(t: str) -> str:
    if re.search(r"\[\s*[xX]\s*\]\s*S[ií],?\s*acceso completo", t, re.IGNORECASE):
        return "Acceso completo"
    if re.search(r"\[\s*[xX]\s*\]\s*Acceso parcial", t, re.IGNORECASE):
        return "Acceso parcial"
    return "No especificado"


def _equipos_kiro(t: str) -> str:
    if re.search(r"\[\s*[xX]\s*\]\s*4\s+o\s+m[aá]s", t, re.IGNORECASE):
        return "4 o más equipos"
    if re.search(r"\[\s*[xX]\s*\]\s*2-3", t, re.IGNORECASE):
        return "2-3 equipos"
    if re.search(r"\[\s*[xX]\s*\]\s*Un\s+solo", t, re.IGNORECASE):
        return "Un solo equipo"
    return "No especificado"


def _separar_proceso_dolor(texto: str):
    """Separa la columna 'Proceso/tarea' de la de 'Dolor' en una fila aplanada.

    El PDF junta ambas columnas sin delimitador. Heurística fiel al origen: el
    proceso es la etiqueta corta inicial (una palabra, o dos si la segunda es
    parte del nombre) y el dolor es la descripción que sigue, que suele arrancar
    con un lead-in típico ("Tiempos largos", "Falta de", "Creación de"...).

    Si no se puede separar con confianza, se devuelve todo como proceso y dolor
    vacío (no se inventa una división).
    """
    palabras = texto.split()
    if len(palabras) <= 1:
        return texto, ""
    # Lead-ins habituales de la columna de dolor: al encontrarlos, todo lo previo
    # es el proceso y desde ahí empieza el dolor.
    lead_ins = r"^(Tiempos?|Falta|Creaci[oó]n|Demora|Retraso|Exceso|Dificultad|" \
               r"Errores?|Bugs?|Proceso|Ausencia|Carencia|Poca|Poco|Muchos?|" \
               r"Muchas?|No\s|Se\s|Lentitud|Cuello)"
    for i in range(1, len(palabras)):
        cola = " ".join(palabras[i:])
        if re.match(lead_ins, cola, re.IGNORECASE):
            return " ".join(palabras[:i]), cola
    # Fallback: proceso = primera palabra; dolor = resto.
    return palabras[0], " ".join(palabras[1:])


def _casos_uso_kiro(t: str) -> list:
    """Extrae la tabla de casos de uso candidatos del cuestionario Kiro.

    La tabla tiene columnas: Proceso/tarea | Dolor | Frecuencia | Prioridad.
    En unas variantes está bajo "Sección C" y en otras bajo "Sección D" (cuando
    hay una sección extra de "Tipos de Usuario"). Anclamos por el encabezado de
    la tabla ("Prioridad (Alta/Media/Baja)") en lugar de por la letra de sección,
    y cortamos en la pregunta que sigue (piloto/MVP).
    """
    # Localizar el encabezado de la tabla; el contenido real empieza justo después.
    hdr = re.search(r"Prioridad\s*\(Alta\s*/?\s*Media\s*/?\s*Baja\)", t, re.IGNORECASE)
    if hdr:
        inicio = hdr.end()
    else:
        m = re.search(r"Secci[oó]n C", t, re.IGNORECASE)
        inicio = m.end() if m else 0
    # Cortar en la pregunta de piloto/MVP o en la siguiente sección.
    fin_m = re.search(r"cu[aá]l elegir[ií]an|piloto o MVP|Secci[oó]n [E-F]",
                      t[inicio:], re.IGNORECASE)
    bloque = t[inicio:inicio + fin_m.start()] if fin_m else t[inicio:]

    casos = []
    # Cada fila real es: Proceso/tarea + Dolor + Frecuencia + Prioridad, donde
    # Frecuencia y Prioridad son dos tokens consecutivos (Alta/Media/Baja). Ese par
    # marca el fin de fila; capturamos "proceso+dolor" antes de él.
    filas = re.findall(r"(.{10,240}?)\s+(Alta|Media|Baja)\s+(Alta|Media|Baja)\b",
                       bloque, re.IGNORECASE)
    if filas:
        for contenido, frecuencia, prioridad in filas[:5]:
            texto_fila = _limpiar(contenido, 240)
            low = texto_fila.lower()
            if not texto_fila or "prioridad" in low or low.startswith("proceso"):
                continue
            proceso, dolor = _separar_proceso_dolor(texto_fila)
            casos.append(CasoUso(proceso=proceso,
                                 dolor=dolor,
                                 frecuencia=frecuencia.capitalize(),
                                 prioridad=prioridad.capitalize()))
        return casos
    # Fallback: variante con una sola columna de prioridad al final de la fila.
    for contenido, prioridad in re.findall(r"(.{15,220}?)\s+(Alta|Media|Baja)\b",
                                           bloque, re.IGNORECASE)[:5]:
        proceso = _limpiar(contenido, 200)
        low = proceso.lower()
        if not proceso or "prioridad" in low or low.startswith("proceso"):
            continue
        casos.append(CasoUso(proceso=proceso, prioridad=prioridad.capitalize()))
    return casos


# ─────────────────────────────────────────────────────────────────────────────
# PARSER "CUESTIONARIO TÉCNICO" (formato demo, tema Kiro) — 4 secciones, 22 preguntas
# ─────────────────────────────────────────────────────────────────────────────
#
# Este cuestionario usa numeración por punto (S.Q) y NO trae checkboxes ni tabla
# de casos de uso. Cada bloque S.Q contiene: enunciado (+ ejemplos-guía) + respuesta
# del cliente. Los enunciados/guías son boilerplate del formulario y se remueven de
# forma LITERAL (fidelidad al origen): NO se autocorrige ni se inventan datos.

# Enunciado + ejemplos-guía tal cual aparecen tras normalizar, por número de pregunta.
# Se eliminan como prefijo literal para dejar solo la respuesta del cliente.
_GUIA_TECNICO = {
    "1.1": "Nombre de la organización / equipo que participará en la demo.",
    "1.3": "Desarrolladores, tech leads, arquitectos, QA, PM/PO.",
    "1.4": "Nivel general de experiencia del equipo con asistentes de IA para "
           "codificar (ninguna, básica, avanzada).",
    "1.5": "Evaluar la herramienta, capacitar al equipo, resolver una duda técnica "
           "puntual, etc.",
    "2.1": "Lenguajes de programación que usa el equipo en el día a día (ordenar "
           "por frecuencia de uso).",
    "2.2": "Frameworks / librerías principales. Ej. React, Spring Boot, Django, "
           ".NET, Express, etc.",
    "2.3": "IDE(s) que usan actualmente. VS Code, JetBrains, Visual Studio, Eclipse, otro.",
    "2.4": "Control de versiones y hosting de código. GitHub, GitLab, Bitbucket, "
           "Azure DevOps, on-prem.",
    "2.5": "Gestor de tareas / metodología. Jira, Azure Boards, Trello, Scrum, "
           "Kanban, ad hoc.",
    "2.6": "CI/CD actual. Jenkins, GitHub Actions, GitLab CI, CodePipeline, ninguno formal.",
    "2.9": "Copilot, Q Developer, Cursor, ninguno.",
    "4.1": 'Describan brevemente cómo pasa una tarea de "idea" a "código en '
           'producción" hoy.',
}


def _indexar_tecnico(texto: str) -> dict:
    """Indexa las respuestas del cuestionario técnico por número de punto (S.Q).

    Devuelve {"1.1": "respuesta", "2.3": "respuesta", ...} con el enunciado y los
    ejemplos-guía ya removidos.
    """
    t = _normalizar(texto)
    # Cada bloque va desde "S.Q " hasta el siguiente "S.Q " o un encabezado de
    # sección en mayúsculas ("2STACK...", "3ARQUITECTURA...").
    pat = re.compile(
        r"(\d)\.(\d)\s+(.+?)(?=\s\d\.\d\s|\s\d[A-ZÁÉÍÓÚ]{3,}|$)", re.DOTALL)
    res = {}
    for m in pat.finditer(t):
        clave = f"{m.group(1)}.{m.group(2)}"
        res[clave] = _limpiar_tecnico(clave, m.group(3).strip())
    return res


def _limpiar_tecnico(clave: str, bloque: str, max_len: int = 800) -> str:
    """Remueve enunciado y ejemplos-guía de una respuesta del cuestionario técnico."""
    b = bloque
    # Quitar bullets de PDF (glyph privado) y flechas de diagramas de flujo.
    b = b.replace("\uf0b7", " ").replace("→", " ")
    # 1) Si el enunciado termina en pregunta(s), la respuesta va tras el último '?'.
    if "?" in b:
        b = b.rsplit("?", 1)[1]
    # 2) Quitar el prefijo-guía literal del formulario (enunciado declarativo o
    #    lista de opciones-ejemplo que precede a la respuesta real). Fidelidad al
    #    origen: se elimina solo si coincide como prefijo exacto.
    guia = _GUIA_TECNICO.get(clave)
    if guia:
        gnorm = re.sub(r"\s+", " ", guia).strip()
        bstrip = b.lstrip()
        if bstrip.startswith(gnorm):
            b = bstrip[len(gnorm):]
    # 3) Quitar cualquier 'Ej. ... etc.' residual (ejemplo-guía del formulario).
    b = re.sub(r"Ej\.[^.]*?etc\.", "", b, flags=re.IGNORECASE)
    b = re.sub(r"Ej\.[^.]*\.", "", b, flags=re.IGNORECASE)
    return _limpiar(b, max_len)


def _parsear_tecnico(texto: str) -> DatosCliente:
    """Parsea el 'Cuestionario Técnico' (formato demo) a DatosCliente (tema Kiro)."""
    d = DatosCliente(tema="kiro")
    r = _indexar_tecnico(texto)

    def g(clave):
        return r.get(clave, "")

    # ── Sección 1: Contexto del equipo ──
    org = g("1.1")                              # "Grupo Dico / Desarrollo Web"
    d.empresa = org.split("/")[0].strip() if org else ""
    d.areas = org.split("/", 1)[1].strip() if "/" in org else ""
    d.num_personas = g("1.2")                   # "3 del mismo equipo"
    # Roles: el enunciado lista roles-guía y luego los del cliente; nos quedamos
    # con la respuesta (tras la lista-guía separada por punto).
    d.perfil_tecnico = g("1.3")
    # Nivel de experiencia con IA: el cuestionario técnico lo pide de forma
    # cualitativa (ninguna/básica/avanzada), no en escala 1-5. Se conserva el
    # texto literal y se mapea al 1-5 que usan los renderizadores.
    exp_ia = g("1.4")                           # p.ej. "Basica, intermedia"
    if exp_ia:
        d.extra["nivel_experiencia_ia"] = exp_ia
    d.nivel_madurez = _nivel_desde_texto(exp_ia)
    d.objetivos = g("1.5")

    # ── Sección 2: Stack tecnológico ──
    lenguajes = g("2.1")
    frameworks = g("2.2")
    d.stack = ", ".join(x for x in [lenguajes, frameworks] if x)
    ides = g("2.3")
    vcs = g("2.4")
    gestor = g("2.5")
    cicd = g("2.6")
    contenedores = g("2.7")
    nube = g("2.8")
    # Repos / CI/CD / infra: se agrupan en el campo de flujo técnico.
    partes_infra = []
    if vcs:
        partes_infra.append(f"VCS: {vcs}")
    if cicd:
        partes_infra.append(f"CI/CD: {cicd}")
    if contenedores:
        partes_infra.append(f"Infraestructura: {contenedores}")
    if nube:
        partes_infra.append(f"Nube: {nube}")
    d.repositorios_ci_cd = " · ".join(partes_infra)
    if ides:
        d.extra["ides"] = ides
    if gestor:
        d.extra["gestor_tareas"] = gestor
    d.herramientas_ia = g("2.9")                # "Cursor"

    # ── Sección 3: Arquitectura y proyecto candidato ──
    d.tipo_proyecto = "Brownfield"              # Magento legacy → proyecto existente
    repo = g("3.1")
    proyecto = g("3.2")
    d.proyecto = proyecto
    if repo:
        d.extra["repositorio_demo"] = repo
    documentacion = g("3.3")
    estandares = g("3.4")
    d.disenos_specs = " · ".join(x for x in [documentacion, estandares] if x)
    restricciones = g("3.5")
    if restricciones:
        d.extra["restricciones_codigo"] = restricciones
    # Acceso AWS: la nube es AWS pero el cuestionario no reporta nivel de acceso.
    d.acceso_aws = "No especificado"

    # ── Sección 4: Flujo de trabajo (para el hands-on) ──
    flujo = g("4.1")
    if flujo:
        d.extra["flujo_trabajo"] = flujo
    d.fricciones = g("4.2")
    tareas = g("4.3")
    if tareas:
        d.extra["tareas_repetitivas"] = tareas

    # ── Casos de uso: derivados de las fricciones/tareas repetitivas reportadas ──
    d.casos_uso = _casos_uso_tecnico(d.fricciones, tareas)
    # Piloto: el proyecto candidato es el MVP natural.
    d.piloto_mvp = proyecto

    d.duracion = "6-7 semanas (programa estándar)"
    d.cultura_cambio = "No especificado"
    d.num_equipos_paralelo = "Un solo equipo"
    return d


def _nivel_desde_texto(texto: str) -> str:
    """Mapea el nivel cualitativo de experiencia con IA a la escala 1-5.

    El cuestionario técnico usa términos (ninguna/básica/intermedia/avanzada/experta).
    Se toma el término MÁS ALTO mencionado. Si no hay término reconocible, se deja
    vacío (no se inventa un nivel).
    """
    if not texto:
        return ""
    low = texto.lower()
    escala = [
        ("expert", "5"), ("avanzad", "4"), ("intermedi", "3"),
        ("b[aá]sic", "2"), ("ningun", "1"),
    ]
    mejor = ""
    for patron, nivel in escala:
        if re.search(patron, low):
            if not mejor or nivel > mejor:
                mejor = nivel
    return mejor


def _casos_uso_tecnico(fricciones: str, tareas: str) -> list:
    """Deriva casos de uso candidatos de las fricciones y tareas repetitivas.

    El cuestionario técnico no trae una tabla de casos de uso; usamos las áreas de
    fricción numeradas ("1. Troubleshooting...", "2. Compatibilidad...") como casos
    candidatos de prioridad alta, fieles al texto del cliente.
    """
    casos = []
    if fricciones:
        # Las fricciones vienen como "1. Titulo ... 2. Titulo ...". Extraer títulos.
        for m in re.finditer(r"\d+\.\s*([^.]{6,120})", fricciones):
            titulo = m.group(1).strip()
            # El título de la fricción es la 1ª cláusula; recortar la descripción
            # que le sigue (arranca con lead-ins típicos "Especialmente", "Durante",
            # "Algunos", "Los", "Existen"...).
            titulo = re.split(
                r"\s+(?:Especialmente|Durante|Algunos|Algunas|Los|Las|Existen|Esto|"
                r"Por lo tanto)\b",
                titulo, maxsplit=1)[0]
            titulo = _limpiar(titulo, 90)
            if titulo and not titulo[0].isdigit():
                casos.append(CasoUso(proceso=titulo, dolor="Fricción reportada en el flujo",
                                     frecuencia="Recurrente", prioridad="Alta"))
            if len(casos) >= 5:
                break
    return casos


# ─────────────────────────────────────────────────────────────────────────────
# PARSER JSON (formularios HTML) — mapeo directo del esquema a DatosCliente
# ─────────────────────────────────────────────────────────────────────────────
#
# El `.json` lo producen los formularios de `cuestionarios/` y respetan
# `cuestionarios/esquema/diagnostico.schema.json` (esquema_version "1.0"). Al venir
# ya estructurado, el mapeo es directo y fiel al origen: un campo vacío queda vacío,
# nunca se inventa. Si el esquema evoluciona, ampliar aquí con tolerancia a claves
# ausentes (se usa `.get(...)` en todo el recorrido).

_ESQUEMA_SOPORTADO = {"1.0"}


def _parsear_json(ruta: str, tema: str = "") -> DatosCliente:
    """Mapea el JSON de los formularios HTML a DatosCliente (agnóstico al tema)."""
    with open(ruta, encoding="utf-8") as f:
        raw = json.load(f)

    version = str(raw.get("esquema_version", "")).strip()
    if version and version not in _ESQUEMA_SOPORTADO:
        # No rompemos: avisamos y seguimos con best-effort (tolerancia a versiones).
        print(f"AVISO: esquema de diagnóstico '{version}' no reconocido; "
              f"soportados: {sorted(_ESQUEMA_SOPORTADO)}. Se intenta mapear igual.")

    t = (tema or raw.get("tema") or "kiro").strip()
    sec = raw.get("secciones", {}) or {}
    contacto = raw.get("contacto", {}) or {}
    exp = sec.get("experticia", {}) or {}
    cu = sec.get("casos_uso", {}) or {}
    org = sec.get("organizacion", {}) or {}
    obj = sec.get("objetivos", {}) or {}

    d = DatosCliente(tema="quick_suite" if t == "quick_suite" else "kiro")

    # ── Identidad / contacto (común) ──
    d.empresa = (raw.get("empresa") or "").strip()
    d.fecha = (contacto.get("fecha") or "").strip()
    d.perfil_tecnico = (contacto.get("perfil_tecnico") or "").strip()
    d.perfil_negocio = (contacto.get("perfil_negocio") or "").strip()
    d.champion = (contacto.get("champion") or "").strip()
    d.proyecto = (contacto.get("proyecto") or "").strip()

    # ── IA / madurez (común) ──
    d.herramientas_ia = (exp.get("herramientas_ia_actuales") or "").strip()
    # Nivel de madurez: Kiro prioriza prompting; Quick usa el agéntico.
    if d.tema == "quick_suite":
        d.nivel_madurez = (exp.get("nivel_agentico") or "").strip()
    else:
        d.nivel_madurez = (exp.get("nivel_prompting") or exp.get("nivel_agentico") or "").strip()
    if exp.get("experiencia_previa"):
        d.extra["experiencia_ia"] = exp["experiencia_previa"].strip()

    # ── Casos de uso (común) ──
    d.casos_uso = []
    for c in (cu.get("casos") or [])[:5]:
        proc = (c.get("proceso") or "").strip()
        dolor = (c.get("dolor") or "").strip()
        if not (proc or dolor):
            continue  # fila vacía: no se inventa
        d.casos_uso.append(CasoUso(
            proceso=proc, dolor=dolor,
            frecuencia=(c.get("frecuencia") or "").strip(),
            prioridad=(c.get("prioridad") or "").strip(),
            capacidad=(c.get("capacidad") or "").strip(),
        ))
    d.piloto_mvp = (cu.get("piloto_mvp") or "").strip()

    # ── Organización (común) ──
    d.num_personas = (org.get("num_personas") or "").strip()
    d.num_equipos_paralelo = (org.get("num_equipos_paralelo") or "No especificado").strip()
    d.cultura_cambio = _legible_cultura(org.get("cultura_cambio"))
    d.resistencias = (org.get("resistencias") or "").strip()

    # ── Objetivos / métricas (común) ──
    d.objetivos = (obj.get("objetivos") or "").strip()
    d.metricas_exito = (obj.get("metricas_exito") or "").strip()
    d.timeline = (obj.get("timeline") or "").strip()
    d.duracion = (obj.get("duracion") or "").strip()
    d.comentarios = (obj.get("comentarios") or "").strip()

    # ── Training path recomendado (metadato nuevo) ──
    tp = raw.get("training_path", {}) or {}
    if tp.get("nivel"):
        d.extra["training_path"] = tp.get("nivel", "")
        d.extra["training_path_etiqueta"] = tp.get("etiqueta", "")

    if d.tema == "quick_suite":
        _mapear_json_quick(d, sec, exp, org, obj)
    else:
        _mapear_json_kiro(d, sec, exp, obj)

    # ── Integraciones MCP focalizadas (bloque nuevo del formulario) ──
    # Se aplica DESPUÉS de los mappers por tema, que fijan d.integraciones desde el
    # contexto; aquí se pliegan las herramientas concretas para focalizar los MCPs.
    _mapear_integraciones_mcp(d, sec.get("integraciones_mcp", {}) or {})

    return d


def _mapear_integraciones_mcp(d: DatosCliente, mcp: dict) -> None:
    """Pliega las integraciones MCP focalizadas en d.integraciones y d.extra.

    El cliente indica herramientas concretas por categoría (Jira, GitHub, Slack,
    Postgres...). Esas cadenas se concatenan en `d.integraciones` para que la
    detección por palabra clave de `config_recomendada` arme la tabla de MCPs
    correcta, y se guardan en `d.extra` para referencia del agente de MCPs.
    """
    if not mcp:
        return
    campos = ["gestion_tareas", "repositorio", "documentacion", "comunicacion",
              "base_datos", "observabilidad", "nube", "diseno", "crm", "otros"]
    valores = [str(mcp.get(c, "")).strip() for c in campos]
    valores = [v for v in valores if v]
    if valores:
        extra_integ = ", ".join(valores)
        d.integraciones = ", ".join(x for x in [d.integraciones, extra_integ] if x)
        d.extra["integraciones_mcp"] = extra_integ
    if mcp.get("categorias"):
        d.extra["integraciones_mcp_categorias"] = str(mcp["categorias"]).strip()
    if mcp.get("restricciones"):
        d.extra["integraciones_mcp_restricciones"] = str(mcp["restricciones"]).strip()


def _mapear_json_kiro(d: DatosCliente, sec: dict, exp: dict, obj: dict) -> None:
    """Campos específicos de Kiro desde el JSON."""
    ct = sec.get("contexto_tecnico", {}) or {}
    d.stack = (ct.get("stack") or "").strip()
    d.arquitectura = (ct.get("arquitectura") or "").strip()
    d.repositorios_ci_cd = (ct.get("repositorios_ci_cd") or "").strip()
    d.tipo_proyecto = (ct.get("tipo_proyecto") or "").strip().capitalize()
    d.disenos_specs = (ct.get("disenos_specs") or "").strip()
    d.integraciones = (ct.get("integraciones") or "").strip()
    d.acceso_aws = (ct.get("acceso_aws") or "").strip() or "No especificado"
    # Señales nuevas útiles para afinar contenido (anexo AWS, testing, estructura).
    for clave in ("usa_git_fluido", "prefiere_estructura", "trabaja_sobre_aws", "tiene_tests"):
        val = (ct.get(clave) or "").strip()
        if val:
            d.extra[clave] = val
    # Fricciones: en el nuevo formulario no hay una pregunta directa; se derivan de
    # los casos de uso si existen (fidelidad al origen, sin inventar).
    d.fricciones = ", ".join(c.proceso for c in d.casos_uso if c.proceso)
    if not d.duracion:
        d.duracion = "6-7 semanas (programa estándar)"


def _mapear_json_quick(d: DatosCliente, sec: dict, exp: dict, org: dict, obj: dict) -> None:
    """Campos específicos de Quick Suite desde el JSON."""
    cn = sec.get("contexto_negocio", {}) or {}
    d.areas = (cn.get("areas") or "").strip()
    d.herramientas_colaboracion = (cn.get("herramientas_colaboracion") or "").strip()
    d.conocimiento_org = (cn.get("conocimiento_org") or "").strip()
    d.apps_negocio = (cn.get("apps_negocio") or "").strip()
    d.procesos_manuales = (cn.get("procesos_manuales") or "").strip()
    d.fricciones = d.procesos_manuales
    d.fuentes_datos = (cn.get("fuentes_datos") or "").strip()
    d.seguridad_compliance = (cn.get("seguridad_compliance") or "").strip()
    d.iniciativas_previas = (cn.get("iniciativas_previas") or "").strip()
    d.apps_sin_codigo = (cn.get("requiere_apps_sin_codigo") or "").strip()
    d.acceso_aws = (cn.get("acceso_aws") or "").strip() or "No especificado"
    d.integraciones = ", ".join(x for x in [d.apps_negocio, d.conocimiento_org] if x)
    d.autonomia_agentes = (org.get("autonomia_agentes") or "Aún no definido").strip()
    d.plan_producto = (obj.get("plan_producto") or "Pro").strip()
    for clave in ("audiencia", "objetivo_principal", "manejo_datos", "incluye_linux"):
        val = (cn.get(clave) or "").strip()
        if val:
            d.extra[clave] = val
    if not d.duracion:
        d.duracion = "programa acotado"


def _legible_cultura(valor) -> str:
    """Normaliza el código de cultura del formulario a texto legible."""
    mapa = {
        "abierta": "Muy abierta / entusiasta",
        "neutral": "Neutral, se adapta con acompañamiento",
        "resistente": "Resistente, requiere gestión del cambio",
    }
    v = (valor or "").strip()
    return mapa.get(v, v or "No especificado")


# ─────────────────────────────────────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────────────────────────────────────
def parsear(ruta: str, tema: str = "") -> DatosCliente:
    """Extrae, detecta el tema (si no se fuerza) y parsea el cuestionario.

    Soporta dos orígenes:
      - `.json` producido por los formularios HTML (fuente estructurada, sin
        heurísticas): mapeo directo esquema → DatosCliente.
      - `.pdf` / `.docx` / `.md`: extracción de texto + parseo tolerante.
    """
    nombre = os.path.basename(ruta)

    # Fuente estructurada (formularios HTML): no requiere heurísticas de texto.
    if os.path.splitext(ruta)[1].lower() == ".json":
        datos = _parsear_json(ruta, tema)
        datos.empresa = _sanear_empresa(datos.empresa) or _empresa_desde_archivo(nombre)
        return datos

    texto = extraer_texto(ruta)
    if not tema:
        tema = detectar_tema(texto, nombre)
    # El "Cuestionario Técnico" (formato demo) es un esquema distinto del estándar
    # de adopción; se detecta por estructura y se parsea con su parser dedicado.
    if tema == "kiro" and es_cuestionario_tecnico(texto):
        datos = _parsear_tecnico(texto)
    elif tema == "quick_suite":
        datos = _parsear_quick(texto)
    else:
        datos = _parsear_kiro(texto)
    datos.tema = tema
    # Sanear la empresa extraída; si es inválida (vacía o markup del cuestionario),
    # derivar un nombre limpio a partir del archivo.
    datos.empresa = _sanear_empresa(datos.empresa) or _empresa_desde_archivo(nombre)
    return datos


def _sanear_empresa(valor: str) -> str:
    """Devuelve la empresa si es un nombre real; '' si es markup o una etiqueta del form."""
    v = (valor or "").strip()
    if not v:
        return ""
    # Rechazar restos de tablas Markdown / celdas vacías / asteriscos de negrita
    if any(tok in v for tok in ["|", ":----", ":--", "*"]):
        return ""
    # Rechazar cuando lo capturado es otra etiqueta del formulario o el propio título
    # del cuestionario (empresa quedó en blanco en el origen).
    etiquetas = ["fecha de llenado", "nombre y rol", "perfil técnico", "perfil tecnico",
                 "perfil de negocio", "área(s)", "area(s)", "sponsor", "cuestionario"]
    low = v.lower()
    if any(low.startswith(e) or e in low[:40] for e in etiquetas):
        return ""
    return v


def _empresa_desde_archivo(nombre: str) -> str:
    """Deriva un nombre de cliente limpio desde el nombre del archivo del cuestionario."""
    import unicodedata
    # Normalizar a NFC: en algunos sistemas de archivos el nombre llega en NFD
    # (acentos combinados), lo que rompe los regex con caracteres acentuados.
    nombre = unicodedata.normalize("NFC", nombre)
    base = os.path.splitext(nombre)[0]
    # Normalizar separadores primero para que los \b funcionen
    base = base.replace("_", " ")
    # Quitar prefijos de tema/tipo comunes. Usamos '.' para el carácter acentuado
    # (diagnóstico) para ser robustos ante diferencias de codificación.
    base = re.sub(r"(?i)cuestionario\s*(de\s+)?diagn.stico", "", base)
    base = re.sub(r"(?i)amazon\s+quick(\s+suite)?", "", base)
    base = re.sub(r"(?i)\bquick\s+suite\b", "", base)
    base = re.sub(r"(?i)\bquick\b", "", base)
    base = re.sub(r"(?i)\bkiro\b", "", base)
    base = re.sub(r"^[\s\-–]+", "", base)
    base = re.sub(r"[\s\-–]+$", "", base)
    base = re.sub(r"\s+", " ", base).strip(" -–_")
    return base or "Cliente"
