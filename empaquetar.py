"""
Empaqueta los formularios de diagnóstico en un único archivo HTML autocontenido.

Toma un formulario modular (que referencia assets/estilo.css y assets/formulario.js)
y embebe el CSS y el JS en línea, produciendo `*_standalone.html`: un solo archivo
que el cliente abre con doble clic y funciona completo, sin carpeta `assets/` ni
conexión a internet.

Uso (desde la carpeta cuestionarios/):
    python empaquetar.py         (empaqueta ambos formularios)
    python empaquetar.py kiro    (solo Kiro)
    python empaquetar.py quick   (solo Quick)

Las fuentes editables (diagnostico_*.html + assets/) viven en la carpeta
formulario_fuente/; la salida (*_standalone.html) se escribe en la raíz del
proyecto, lista para enviar. Vuelve a correrlo cada vez que edites estilo.css o
formulario.js para regenerar los standalone.
"""

import base64
import os
import re
import sys

# Carpeta de este script. La FUENTE (editables + assets/) vive en formulario_fuente/;
# la SALIDA (*_standalone.html) se escribe en la raíz, listos para compartir.
AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_FUENTE = os.path.join(AQUI, "formulario_fuente")
DIR_SALIDA = AQUI

FORMULARIOS = {
    "kiro": "diagnostico_kiro.html",
    "quick": "diagnostico_quick.html",
}


def _leer(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as f:
        return f.read()


# Tipos MIME por extensión para las fuentes embebidas como data URI.
_MIME_FUENTES = {
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
}


def _embeber_fuentes(css: str, base_css: str) -> str:
    """Convierte cada `url(ruta.woff2)` del CSS a un data URI base64.

    `base_css` es la carpeta donde vive el CSS; las rutas de `url(...)` se
    resuelven relativas a ella (igual que un navegador). Así el standalone
    no depende de la carpeta assets/fonts/ para cargar las tipografías.
    """
    def reemplazar_url(m):
        comillas = m.group(1) or ""
        ruta_rel = m.group(2).strip()
        ext = os.path.splitext(ruta_rel)[1].lower()
        mime = _MIME_FUENTES.get(ext)
        if mime is None:
            return m.group(0)  # no es una fuente conocida: dejar tal cual
        ruta_abs = os.path.join(base_css, ruta_rel.replace("/", os.sep))
        with open(ruta_abs, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"url({comillas}data:{mime};base64,{b64}{comillas})"

    # url(fonts/x.woff2), url('fonts/x.woff2'), url("fonts/x.woff2")
    return re.sub(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)', reemplazar_url, css)


def empaquetar(nombre_html: str) -> str:
    """Devuelve la ruta del archivo standalone generado."""
    ruta_html = os.path.join(DIR_FUENTE, nombre_html)
    html = _leer(ruta_html)

    # 1) Embeber el CSS: <link rel="stylesheet" href="assets/estilo.css"> → <style>…</style>
    def reemplazar_css(m):
        href = m.group(1)
        ruta_css = os.path.join(DIR_FUENTE, href.replace("/", os.sep))
        css = _leer(ruta_css)
        # Las url(fonts/*.woff2) del CSS son relativas a la carpeta del CSS.
        css = _embeber_fuentes(css, os.path.dirname(ruta_css))
        return "<style>\n" + css + "\n</style>"

    html = re.sub(
        r'<link\s+rel=["\']stylesheet["\']\s+href=["\'](assets/[^"\']+)["\']\s*/?>',
        reemplazar_css, html, count=1)

    # 2) Embeber el JS: <script src="assets/formulario.js"></script> → <script>…</script>
    def reemplazar_js(m):
        src = m.group(1)
        ruta_js = os.path.join(DIR_FUENTE, src.replace("/", os.sep))
        js = _leer(ruta_js)
        # Evitar que un "</script>" dentro del JS cierre el bloque antes de tiempo.
        js = js.replace("</script>", "<\\/script>")
        return "<script>\n" + js + "\n</script>"

    html = re.sub(
        r'<script\s+src=["\'](assets/[^"\']+)["\']\s*></script>',
        reemplazar_js, html, count=1)

    # 3) Marca de archivo autocontenido (comentario informativo para quien lo abra).
    marca = ("<!-- Archivo autocontenido: CSS, JS y fuentes de marca (Poppins + "
             "Oswald) embebidos. Funciona sin conexión y sin la carpeta assets/. "
             "Generado por empaquetar.py -->\n")
    html = html.replace("<!doctype html>", "<!doctype html>\n" + marca, 1)

    os.makedirs(DIR_SALIDA, exist_ok=True)
    salida = os.path.splitext(nombre_html)[0] + "_standalone.html"
    ruta_salida = os.path.join(DIR_SALIDA, salida)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html)
    return ruta_salida


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    claves = argv if argv else list(FORMULARIOS.keys())
    for clave in claves:
        if clave not in FORMULARIOS:
            print(f"ERROR: formulario desconocido '{clave}'. Usa: {', '.join(FORMULARIOS)}")
            return 1
        ruta = empaquetar(FORMULARIOS[clave])
        tam_kb = os.path.getsize(ruta) / 1024
        print(f"  generado: {os.path.basename(ruta)}  ({tam_kb:.0f} KB)")
    print("\nListo. Comparte el/los archivo(s) *_standalone.html con el cliente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
