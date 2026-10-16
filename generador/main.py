"""
Orquestador CLI del generador de planes de adopción.

Uso:
    python -m generador.main "ruta/al/diagnostico_CLIENTE.json"   (formulario HTML)
    python -m generador.main "ruta/al/Cuestionario.pdf"
    python -m generador.main "ruta/al/Cuestionario.docx" --tema quick_suite
    python -m generador.main            (sin args: lista cuestionarios disponibles)

Flujo:
    1. Parsea el cuestionario (detecta tema si no se fuerza).
    2. Genera Roadmap (.md + .xlsx), Plan de Enseñanza (.md) y Diseño de Actividades (.md).
    3. Los guarda en: clientes/{Kiro|Quick Suite}/Recursos_{empresa}/
"""

import os
import sys
import argparse

# Evitar UnicodeEncodeError al imprimir nombres con acentos en consolas cp1252 (Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

from . import cuestionario as C
from . import temas
from . import render_markdown as RM
from . import render_excel as RX

# Raíz del workspace = carpeta que contiene 'generador/'
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generar(ruta_cuestionario: str, tema: str = "", base: str = WORKSPACE) -> dict:
    """Genera los 4 artefactos para un cuestionario. Devuelve rutas escritas."""
    datos = C.parsear(ruta_cuestionario, tema=tema)
    tema_mod = temas.obtener(datos.tema)

    carpeta = datos.ruta_salida(base)
    os.makedirs(carpeta, exist_ok=True)
    emp = datos.empresa

    salidas = {}

    # Roadmap .md
    ruta = os.path.join(carpeta, f"Roadmap_{emp}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(RM.roadmap(datos, tema_mod))
    salidas["roadmap_md"] = ruta

    # Roadmap .xlsx
    producto = tema_mod.META["producto"]
    ruta = os.path.join(carpeta, f"Roadmap {producto} - {emp}.xlsx")
    RX.roadmap_excel(datos, tema_mod, ruta)
    salidas["roadmap_xlsx"] = ruta

    # Plan de Enseñanza .md
    ruta = os.path.join(carpeta, f"Plan_de_Ensenanza_{emp}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(RM.plan_ensenanza(datos, tema_mod))
    salidas["plan_md"] = ruta

    # Diseño de Actividades .md
    ruta = os.path.join(carpeta, f"Diseno_Actividades_{emp}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(RM.diseno_actividades(datos, tema_mod))
    salidas["diseno_md"] = ruta

    return {"datos": datos, "tema": datos.tema, "carpeta": carpeta, "salidas": salidas}


def _listar_cuestionarios(base: str):
    print("Cuestionarios disponibles (JSON/PDF/DOCX/MD) en el workspace:\n")
    encontrados = []
    for root, _dirs, files in os.walk(base):
        if os.sep + "clientes" + os.sep in root + os.sep:
            continue
        for fn in files:
            low = fn.lower()
            es_json = low.startswith("diagnostico") and low.endswith(".json")
            es_doc = low.startswith("cuestionario") and low.endswith((".pdf", ".docx", ".md"))
            if es_json or es_doc:
                encontrados.append(os.path.join(root, fn))
    for p in encontrados:
        print("  -", os.path.relpath(p, base))
    if not encontrados:
        print("  (ninguno)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generador de planes de adopción (Kiro / Quick Suite)")
    parser.add_argument("cuestionario", nargs="?", help="Ruta al cuestionario (.json, .pdf, .docx o .md)")
    parser.add_argument("--tema", choices=["kiro", "quick_suite"], default="",
                        help="Forzar el tema (por defecto se detecta automáticamente)")
    args = parser.parse_args(argv)

    if not args.cuestionario:
        _listar_cuestionarios(WORKSPACE)
        return 0

    if not os.path.isfile(args.cuestionario):
        print(f"ERROR: no existe el archivo: {args.cuestionario}")
        return 1

    print(f"Procesando: {os.path.basename(args.cuestionario)}")
    res = generar(args.cuestionario, tema=args.tema)
    print(f"Tema detectado: {res['tema']}")
    print(f"Cliente: {res['datos'].empresa}")
    print(f"Carpeta de salida: {os.path.relpath(res['carpeta'], WORKSPACE)}\n")
    print("Archivos generados:")
    for k, v in res["salidas"].items():
        print(f"  - {os.path.basename(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
