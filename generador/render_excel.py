"""
Renderizador del Roadmap en Excel (.xlsx).

Usa `templates/Roadmap_base.xlsx` como plantilla de formato (colores, fuentes,
anchos de columna, merges) y escribe el contenido del tema en las filas de sesiones.
Es agnóstico al tema: solo consume SesionRoadmap + metadatos.
"""

import os
import openpyxl

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(DIR, "templates", "Roadmap_base.xlsx")

# Filas de las 6 sesiones en el template
FILA_INICIO = 5
FILA_NOTA = 12


def roadmap_excel(d, tema_mod, ruta_salida: str) -> str:
    """Genera el Roadmap .xlsx en `ruta_salida`. Devuelve la ruta escrita."""
    meta = tema_mod.META
    sesiones = tema_mod.sesiones_roadmap(d)
    subtitulo = tema_mod.subtitulo_roadmap(d)
    nota = tema_mod.nota_roadmap(d)

    wb = openpyxl.load_workbook(TEMPLATE)
    ws = wb["Roadmap General"]

    # Título y subtítulo
    ws.cell(row=1, column=1).value = f"Roadmap de {meta['titulo_programa']} — {d.empresa}"
    ws.cell(row=2, column=1).value = subtitulo

    # Participantes (col E) — mismo texto para todas las sesiones
    if d.tema == "quick_suite":
        participantes = f"Equipo {d.empresa} ({d.areas or 'áreas participantes'}) + eTribe"
    else:
        participantes = f"Equipo de desarrollo {d.empresa} + eTribe"

    # Escribir las 6 sesiones
    for i, s in enumerate(sesiones):
        row = FILA_INICIO + i
        ws.cell(row=row, column=1).value = s.fase_semana
        ws.cell(row=row, column=2).value = s.sesion_track
        ws.cell(row=row, column=3).value = s.fase_actividad
        ws.cell(row=row, column=4).value = s.sub_actividades
        ws.cell(row=row, column=5).value = participantes
        ws.cell(row=row, column=6).value = 2

    # Nota al pie
    ws.cell(row=FILA_NOTA, column=1).value = nota

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    wb.save(ruta_salida)
    wb.close()
    return ruta_salida
