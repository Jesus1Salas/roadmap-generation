/* ===================================================================
   Lógica compartida de los formularios de diagnóstico.
   - Persistencia en localStorage
   - Progreso en vivo
   - Derivación del training path según experticia
   - Exportación a JSON (fuente de verdad) y Markdown (compatibilidad)
   Cada formulario define window.DIAGNOSTICO_CONFIG antes de cargar este script.
   =================================================================== */
(function () {
  "use strict";

  var CFG = window.DIAGNOSTICO_CONFIG;
  if (!CFG) { console.error("Falta DIAGNOSTICO_CONFIG"); return; }

  var ESQUEMA_VERSION = "1.0";
  var STORAGE_KEY = "diagnostico_" + CFG.tema;
  var form = document.getElementById("form");

  // ---------------------------------------------------------------
  // Persistencia
  // ---------------------------------------------------------------
  function guardar() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(recolectarCrudo()));
      marcarGuardado(true);
    } catch (e) { /* localStorage no disponible: seguimos sin persistir */ }
  }

  function restaurar() {
    var raw;
    try { raw = localStorage.getItem(STORAGE_KEY); } catch (e) { return; }
    if (!raw) return;
    var data;
    try { data = JSON.parse(raw); } catch (e) { return; }

    Object.keys(data).forEach(function (name) {
      var val = data[name];
      var campos = form.elements[name];
      if (!campos) return;
      if (campos instanceof RadioNodeList || (campos.length && !campos.tagName)) {
        // Grupo (radios o checkboxes)
        Array.prototype.forEach.call(campos, function (el) {
          if (el.type === "checkbox") {
            el.checked = Array.isArray(val) ? val.indexOf(el.value) !== -1 : false;
          } else if (el.type === "radio") {
            el.checked = el.value === val;
          } else { el.value = val; }
        });
      } else {
        campos.value = val;
      }
    });

    // Restaurar filas dinámicas de casos de uso
    if (Array.isArray(data.__casos)) {
      data.__casos.forEach(function (c, i) {
        if (i > 0) agregarCasoFila();
      });
      // rellenar valores
      data.__casos.forEach(function (c, i) {
        setCasoVal(i, c);
      });
    }
  }

  function recolectarCrudo() {
    // Snapshot plano {name: value|[values]} para localStorage.
    var out = {};
    var els = form.elements;
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (!el.name) continue;
      if (el.type === "checkbox") {
        if (!out[el.name]) out[el.name] = [];
        if (el.checked) out[el.name].push(el.value);
      } else if (el.type === "radio") {
        if (el.checked) out[el.name] = el.value;
      } else {
        out[el.name] = el.value;
      }
    }
    out.__casos = recolectarCasos();
    return out;
  }

  // ---------------------------------------------------------------
  // Casos de uso (filas dinámicas)
  // ---------------------------------------------------------------
  function contenedorCasos() { return document.getElementById("casos-tabla"); }

  function recolectarCasos() {
    var filas = contenedorCasos().querySelectorAll(".caso-fila");
    return Array.prototype.map.call(filas, function (fila) {
      return {
        proceso: val(fila, ".c-proceso"),
        dolor: val(fila, ".c-dolor"),
        frecuencia: val(fila, ".c-frecuencia"),
        prioridad: val(fila, ".c-prioridad"),
        capacidad: val(fila, ".c-capacidad")
      };
    });
  }
  function val(root, sel) { var e = root.querySelector(sel); return e ? e.value.trim() : ""; }

  function setCasoVal(i, c) {
    var fila = contenedorCasos().querySelectorAll(".caso-fila")[i];
    if (!fila) return;
    ["proceso", "dolor", "frecuencia", "prioridad", "capacidad"].forEach(function (k) {
      var e = fila.querySelector(".c-" + k);
      if (e && c[k] != null) e.value = c[k];
    });
  }

  function plantillaCasoFila() {
    var capacidadCol = CFG.tema === "quick_suite"
      ? '<div><div class="caso-head">Capacidad</div>' +
        '<select class="c-capacidad"><option value="">—</option>' +
        '<option>Agentes</option><option>Research</option><option>BI</option>' +
        '<option>Automate</option><option>Apps</option></select></div>'
      : '';
    return '' +
      '<div class="caso-fila">' +
        '<div><div class="caso-head">Proceso / tarea</div><textarea class="c-proceso" placeholder="Ej. Generar historias de usuario"></textarea></div>' +
        '<div><div class="caso-head">Dolor o cuello de botella</div><textarea class="c-dolor" placeholder="Ej. Toma mucho tiempo manual"></textarea></div>' +
        '<div><div class="caso-head">Frecuencia</div><input type="text" class="c-frecuencia" placeholder="Ej. Diaria"></div>' +
        '<div><div class="caso-head">Prioridad</div><select class="c-prioridad"><option value="">—</option><option>Alta</option><option>Media</option><option>Baja</option></select></div>' +
        capacidadCol +
        '<button type="button" class="caso-del" title="Eliminar fila" aria-label="Eliminar fila">&times;</button>' +
      '</div>';
  }

  function agregarCasoFila() {
    var cont = contenedorCasos();
    if (cont.querySelectorAll(".caso-fila").length >= 5) {
      toast("Máximo 5 casos de uso", true); return;
    }
    cont.insertAdjacentHTML("beforeend", plantillaCasoFila());
    bindCasoEventos();
    guardar();
  }

  function bindCasoEventos() {
    contenedorCasos().querySelectorAll(".caso-del").forEach(function (btn) {
      btn.onclick = function () {
        if (contenedorCasos().querySelectorAll(".caso-fila").length <= 1) {
          setCasoVal(0, {}); // vaciar en lugar de borrar la última
        } else {
          btn.closest(".caso-fila").remove();
        }
        actualizarProgreso(); guardar();
      };
    });
    contenedorCasos().querySelectorAll(".caso-fila textarea, .caso-fila input, .caso-fila select").forEach(function (el) {
      el.oninput = el.onchange = function () { actualizarProgreso(); guardar(); };
    });
  }

  // ---------------------------------------------------------------
  // Progreso
  // ---------------------------------------------------------------
  function camposContables() {
    // Un "campo" por name único + los casos cuentan como 1 bloque.
    var names = {};
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name) names[el.name] = true;
    });
    return Object.keys(names);
  }

  function estaLleno(name) {
    var campos = form.elements[name];
    if (!campos) return false;
    if (campos instanceof RadioNodeList || (campos.length && !campos.tagName)) {
      return Array.prototype.some.call(campos, function (el) {
        return (el.type === "checkbox" || el.type === "radio") ? el.checked : !!el.value.trim();
      });
    }
    return !!(campos.value && campos.value.trim());
  }

  function actualizarProgreso() {
    var names = camposContables();
    var total = names.length + 1; // +1 por el bloque de casos
    var llenos = names.filter(estaLleno).length;
    var algunCaso = recolectarCasos().some(function (c) { return c.proceso || c.dolor; });
    if (algunCaso) llenos++;
    var pct = total ? Math.round((llenos / total) * 100) : 0;
    document.getElementById("bar-fill").style.width = pct + "%";
    document.getElementById("count").innerHTML = pct + "% <small>completado</small>";
    actualizarTrainingPath();
  }

  // ---------------------------------------------------------------
  // Training path
  // ---------------------------------------------------------------
  function puntajeExperticia() {
    // 0-100 combinando las señales de la autoevaluación.
    var s = 0, max = 0;
    function radio(name, mapa) {
      max += 100;
      var el = form.elements[name];
      if (!el) return;
      var v = (el.value || (el.length ? valorGrupo(name) : "")) || "";
      if (mapa[v] != null) s += mapa[v];
    }
    function valorGrupo(name) {
      var campos = form.elements[name];
      var r = "";
      Array.prototype.forEach.call(campos, function (el) { if (el.checked) r = el.value; });
      return r;
    }
    var pesos = CFG.pesosExperticia;
    var n = 0;
    Object.keys(pesos).forEach(function (name) {
      var el = form.elements[name];
      if (!el) return;
      var v = (el.tagName ? el.value : valorGrupo(name)) || "";
      var mapa = pesos[name];
      if (mapa[v] != null) { s += mapa[v]; n++; }
    });
    if (!n) return 0;
    return Math.round(s / n); // promedio 0-100 de las señales respondidas
  }

  function nivelDesdePuntaje(p) {
    for (var i = 0; i < CFG.niveles.length; i++) {
      if (p <= CFG.niveles[i].max) return CFG.niveles[i];
    }
    return CFG.niveles[CFG.niveles.length - 1];
  }

  function actualizarTrainingPath() {
    var override = document.getElementById("tp-override");
    var p = puntajeExperticia();
    var nivel;
    if (override && override.value) {
      nivel = CFG.niveles.filter(function (n) { return n.id === override.value; })[0] || nivelDesdePuntaje(p);
    } else {
      nivel = nivelDesdePuntaje(p);
    }
    document.getElementById("tp-nombre").textContent = nivel.etiqueta;
    document.getElementById("tp-desc").textContent = nivel.desc;
    window.__tp = { nivel: nivel.id, etiqueta: nivel.etiqueta, puntaje: p, override: !!(override && override.value) };
  }

  // ---------------------------------------------------------------
  // Construcción del objeto de salida (según esquema)
  // ---------------------------------------------------------------
  function campo(name) {
    var el = form.elements[name];
    if (!el) return "";
    if (el instanceof RadioNodeList || (el.length && !el.tagName)) {
      var vals = [];
      Array.prototype.forEach.call(el, function (x) {
        if (x.type === "checkbox" && x.checked) vals.push(x.value);
        else if (x.type === "radio" && x.checked) vals.push(x.value);
      });
      return el[0] && el[0].type === "checkbox" ? vals.join(", ") : (vals[0] || "");
    }
    return (el.value || "").trim();
  }

  function construirSalida() {
    actualizarTrainingPath();
    var tp = window.__tp || { nivel: "", etiqueta: "", puntaje: 0, override: false };
    var casos = recolectarCasos().filter(function (c) {
      return c.proceso || c.dolor || c.frecuencia || c.prioridad || c.capacidad;
    });

    var secciones = CFG.construirSecciones(campo, casos);

    return {
      esquema_version: ESQUEMA_VERSION,
      tema: CFG.tema,
      generado_en: new Date().toISOString(),
      empresa: campo("empresa"),
      training_path: {
        nivel: tp.nivel, etiqueta: tp.etiqueta,
        puntaje_experticia: tp.puntaje, ajustado_por_usuario: tp.override
      },
      contacto: {
        fecha: campo("fecha"),
        perfil_tecnico: campo("perfil_tecnico"),
        perfil_negocio: campo("perfil_negocio"),
        champion: campo("champion"),
        proyecto: campo("proyecto")
      },
      secciones: secciones
    };
  }

  // ---------------------------------------------------------------
  // Validación mínima (solo empresa es obligatoria)
  // ---------------------------------------------------------------
  function validar() {
    var ok = true;
    var reqEmpresa = document.getElementById("field-empresa");
    if (!campo("empresa")) { reqEmpresa.classList.add("invalid"); ok = false; }
    else { reqEmpresa.classList.remove("invalid"); }
    if (!ok) {
      toast("Falta el nombre de la empresa", true);
      reqEmpresa.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    return ok;
  }

  // ---------------------------------------------------------------
  // Exportación
  // ---------------------------------------------------------------
  function nombreArchivo(ext) {
    var emp = (campo("empresa") || "Cliente").replace(/[^\w\sáéíóúñÁÉÍÓÚÑ-]/g, "").trim().replace(/\s+/g, "_");
    return "diagnostico_" + emp + "." + ext;
  }

  function descargar(contenido, nombre, mime) {
    var blob = new Blob([contenido], { type: mime + ";charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = nombre; document.body.appendChild(a); a.click();
    document.body.removeChild(a); setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function exportarJSON() {
    if (!validar()) return;
    var data = construirSalida();
    descargar(JSON.stringify(data, null, 2), nombreArchivo("json"), "application/json");
    toast("JSON descargado");
  }

  function exportarMD() {
    if (!validar()) return;
    var data = construirSalida();
    descargar(CFG.aMarkdown(data), nombreArchivo("md"), "text/markdown");
    toast("Markdown descargado");
  }

  // ---------------------------------------------------------------
  // UI helpers
  // ---------------------------------------------------------------
  var toastTimer;
  function toast(msg, err) {
    var t = document.getElementById("toast");
    t.textContent = msg; t.className = "toast show" + (err ? " err" : "");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.className = "toast"; }, 2600);
  }

  var guardadoTimer;
  function marcarGuardado(ok) {
    var s = document.getElementById("save-status");
    if (!s) return;
    s.classList.remove("warn");
    s.innerHTML = ok ? 'Guardado automático <b>activo</b>' : '';
  }

  // ---------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------
  function init() {
    // sembrar una fila de casos
    contenedorCasos().insertAdjacentHTML("beforeend", plantillaCasoFila());
    bindCasoEventos();

    restaurar();
    actualizarProgreso();

    form.addEventListener("input", function () { actualizarProgreso(); guardar(); });
    form.addEventListener("change", function () { actualizarProgreso(); guardar(); });

    var ov = document.getElementById("tp-override");
    if (ov) ov.addEventListener("change", function () { actualizarTrainingPath(); guardar(); });

    document.getElementById("btn-add-caso").addEventListener("click", agregarCasoFila);
    document.getElementById("btn-json").addEventListener("click", exportarJSON);
    document.getElementById("btn-md").addEventListener("click", exportarMD);
    document.getElementById("btn-reset").addEventListener("click", function () {
      if (!confirm("¿Borrar todas las respuestas de este formulario?")) return;
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
      location.reload();
    });

    marcarGuardado(true);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }

  // Exponer utilidades para los configs de cada formulario
  window.DIAG = { toast: toast };
})();
