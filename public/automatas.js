const NS_AUTOMATAS = "http://www.w3.org/2000/svg";

const PATRONES_AUTOMATAS = {
  DNI: "[0-9]{8}",
  CORREO: "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}",
  NOMBRE: "[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+",
  INSTITUCION: "[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+",
  PUESTO: "[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+",
};

function crearSvg(nombre, atributos = {}, texto = null) {
  const elemento = document.createElementNS(NS_AUTOMATAS, nombre);

  Object.entries(atributos).forEach(([clave, valor]) => {
    elemento.setAttribute(clave, String(valor));
  });

  if (texto !== null) {
    elemento.textContent = texto;
  }

  return elemento;
}

function normalizarSimbolo(valor) {
  if (
    valor === null ||
    valor === undefined ||
    valor === "" ||
    ["epsilon", "eps", "ε"].includes(String(valor).toLowerCase())
  ) {
    return "ε";
  }

  return String(valor);
}

function compararEstados(a, b) {
  const aa = /^q(\d+)$/.exec(String(a));
  const bb = /^q(\d+)$/.exec(String(b));

  if (aa && bb) {
    return Number(aa[1]) - Number(bb[1]);
  }

  return String(a).localeCompare(String(b), "es");
}

function agruparTransiciones(transiciones) {
  const mapa = new Map();

  for (const t of transiciones || []) {
    const origen = String(t.origen);
    const destino = String(t.destino);
    const clave = JSON.stringify([origen, destino]);

    if (!mapa.has(clave)) {
      mapa.set(clave, {
        origen,
        destino,
        simbolos: new Set(),
      });
    }

    mapa.get(clave).simbolos.add(normalizarSimbolo(t.simbolo));
  }

  return [...mapa.values()]
    .map((grupo) => ({
      origen: grupo.origen,
      destino: grupo.destino,
      simbolos: [...grupo.simbolos].sort((a, b) => a.localeCompare(b, "es")),
    }))
    .sort(
      (a, b) =>
        compararEstados(a.origen, b.origen) ||
        compararEstados(a.destino, b.destino),
    );
}

function etiquetaSimbolos(simbolos, alfabeto) {
  const caracteres = [...new Set(simbolos)];
  const sigma = [...new Set((alfabeto || []).map(String))];

  if (caracteres.length === 1) {
    return caracteres[0];
  }

  if (
    caracteres.length === 10 &&
    "0123456789".split("").every((s) => caracteres.includes(s))
  ) {
    return "0-9";
  }

  if (
    caracteres.length === sigma.length &&
    sigma.every((s) => caracteres.includes(s))
  ) {
    return "Σ";
  }

  if (caracteres.length <= 5) {
    return caracteres.join(", ");
  }

  return `${caracteres.length} símbolos`;
}

function agregarFila(tbody, valores) {
  const tr = document.createElement("tr");

  for (const valor of valores) {
    const td = document.createElement("td");
    td.textContent = String(valor);
    tr.appendChild(td);
  }

  tbody.appendChild(tr);
}

function llenarQuintupla(id, automata) {
  const tbody = document.getElementById(id);

  if (!tbody) return;

  tbody.replaceChildren();

  agregarFila(tbody, [
    "Q - Estados",
    `{ ${(automata.estados || []).join(", ")} }`,
  ]);

  agregarFila(tbody, [
    "Σ - Alfabeto",
    `{ ${(automata.alfabeto || []).map((s) => `'${s}'`).join(", ")} }`,
  ]);

  agregarFila(tbody, ["δ - Transiciones", "Definidas en la tabla siguiente"]);

  agregarFila(tbody, ["q₀ - Estado inicial", automata.inicial]);

  agregarFila(tbody, [
    "F - Estados finales",
    `{ ${(automata.finales || []).join(", ")} }`,
  ]);
}

function llenarTransiciones(id, automata) {
  const tbody = document.getElementById(id);

  if (!tbody) return;

  tbody.replaceChildren();

  const grupos = agruparTransiciones(automata.transiciones);

  for (const grupo of grupos) {
    agregarFila(tbody, [
      grupo.origen,
      etiquetaSimbolos(grupo.simbolos, automata.alfabeto),
      grupo.destino,
    ]);

    const fila = tbody.lastElementChild;

    fila.cells[1].title = grupo.simbolos.join(", ");

    if (grupo.origen === String(automata.inicial)) {
      fila.cells[0].textContent = `→ ${grupo.origen}`;
    }

    if ((automata.finales || []).map(String).includes(grupo.origen)) {
      fila.cells[0].textContent += " *";
    }
  }
}

function anadirTexto(svg, x, y, texto, tamano = 13, opciones = {}) {
  svg.appendChild(
    crearSvg(
      "text",
      {
        x,
        y,
        "text-anchor": opciones.ancla || "middle",
        "font-family": "Arial, sans-serif",
        "font-size": tamano,
        fill: opciones.color || "#17365d",
        "font-weight": opciones.negrita ? "bold" : "normal",
      },
      texto,
    ),
  );
}

function dibujarAutomata(contenedor, automata) {
  contenedor.replaceChildren();

  const estados = (automata.estados || []).map(String);

  if (!estados.length) {
    contenedor.textContent = "El autómata no contiene estados.";
    return;
  }

  const indice = new Map(estados.map((estado, i) => [estado, i]));

  const finales = new Set((automata.finales || []).map(String));

  const grupos = agruparTransiciones(automata.transiciones);

  const adelante = grupos.filter(
    (grupo) =>
      indice.has(grupo.origen) &&
      indice.has(grupo.destino) &&
      indice.get(grupo.destino) > indice.get(grupo.origen),
  );

  const bucles = grupos.filter((grupo) => grupo.origen === grupo.destino);

  const retornos = grupos.filter(
    (grupo) =>
      indice.has(grupo.origen) &&
      indice.has(grupo.destino) &&
      indice.get(grupo.destino) < indice.get(grupo.origen),
  );

  const espacio = estados.length > 12 ? 112 : 150;
  const radio = 25;
  const margen = 95;

  const ancho = Math.max(560, 2 * margen + (estados.length - 1) * espacio);

  const centroY = 215;

  const alto = Math.max(
    380,
    centroY + 105 + retornos.length * 34 + (retornos.length ? 70 : 0),
  );

  const posiciones = new Map(
    estados.map((estado, i) => [
      estado,
      {
        x: margen + i * espacio,
        y: centroY,
      },
    ]),
  );

  const svg = crearSvg("svg", {
    xmlns: NS_AUTOMATAS,
    viewBox: `0 0 ${ancho} ${alto}`,
    role: "img",
    "aria-label": automata.titulo || "Autómata",
    preserveAspectRatio: "xMidYMid meet",
  });

  const marcadorId = `flecha-${Math.random().toString(36).slice(2, 10)}`;

  const defs = crearSvg("defs");

  const marcador = crearSvg("marker", {
    id: marcadorId,
    viewBox: "0 0 10 10",
    refX: 9,
    refY: 5,
    markerWidth: 7,
    markerHeight: 7,
    orient: "auto-start-reverse",
  });

  marcador.appendChild(
    crearSvg("path", {
      d: "M0 0 L10 5 L0 10 Z",
      fill: "#2563eb",
    }),
  );

  defs.appendChild(marcador);
  svg.appendChild(defs);

  svg.appendChild(
    crearSvg("rect", {
      width: ancho,
      height: alto,
      fill: "white",
    }),
  );

  anadirTexto(svg, ancho / 2, 36, automata.titulo || "Autómata", 20, {
    negrita: true,
  });

  const inicio = posiciones.get(String(automata.inicial));

  if (!inicio) {
    contenedor.textContent = "Estado inicial no encontrado.";
    return;
  }

  svg.appendChild(
    crearSvg("path", {
      d:
        `M${inicio.x - 72} ${inicio.y} ` +
        `L${inicio.x - radio - 5} ${inicio.y}`,
      fill: "none",
      stroke: "#2563eb",
      "stroke-width": 2,
      "marker-end": `url(#${marcadorId})`,
    }),
  );

  function flecha(trazo, simbolos, etiqueta, tx, ty) {
    const linea = crearSvg("path", {
      d: trazo,
      fill: "none",
      stroke: "#2563eb",
      "stroke-width": 2,
      "marker-end": `url(#${marcadorId})`,
    });

    linea.appendChild(crearSvg("title", {}, simbolos.join(", ")));

    svg.appendChild(linea);

    if (etiqueta) {
      const texto = crearSvg(
        "text",
        {
          x: tx,
          y: ty,
          "text-anchor": "middle",
          "font-size": 12,
          "font-family": "Arial, sans-serif",
          fill: "#17365d",
        },
        etiqueta,
      );

      texto.appendChild(crearSvg("title", {}, simbolos.join(", ")));

      svg.appendChild(texto);
    }
  }

  for (const grupo of adelante) {
    const origen = posiciones.get(grupo.origen);
    const destino = posiciones.get(grupo.destino);

    const etiqueta = etiquetaSimbolos(grupo.simbolos, automata.alfabeto);

    const xMedio = (origen.x + destino.x) / 2;

    if (indice.get(grupo.destino) === indice.get(grupo.origen) + 1) {
      flecha(
        `M${origen.x + radio} ${origen.y} ` +
          `L${destino.x - radio - 6} ${destino.y}`,
        grupo.simbolos,
        etiqueta,
        xMedio,
        origen.y - 15,
      );
    } else {
      flecha(
        `M${origen.x} ${origen.y - radio} ` +
          `Q${xMedio} ${origen.y - 85} ` +
          `${destino.x} ${destino.y - radio}`,
        grupo.simbolos,
        etiqueta,
        xMedio,
        origen.y - 58,
      );
    }
  }

  for (const grupo of bucles) {
    const posicion = posiciones.get(grupo.origen);

    const etiqueta = etiquetaSimbolos(grupo.simbolos, automata.alfabeto);

    flecha(
      `M${posicion.x - 17} ${posicion.y - 20} ` +
        `C${posicion.x - 65} ${posicion.y - 125} ` +
        `${posicion.x + 65} ${posicion.y - 125} ` +
        `${posicion.x + 17} ${posicion.y - 20}`,
      grupo.simbolos,
      etiqueta,
      posicion.x,
      posicion.y - 108,
    );
  }

  const leyenda = [];

  retornos.forEach((grupo, i) => {
    const origen = posiciones.get(grupo.origen);
    const destino = posiciones.get(grupo.destino);

    const nivel = 70 + i * 34;
    const yCarril = centroY + nivel;

    const trazo =
      `M${origen.x} ${origen.y + radio} ` +
      `C${origen.x} ${yCarril} ` +
      `${origen.x} ${yCarril} ` +
      `${origen.x - 12} ${yCarril} ` +
      `L${destino.x + 12} ${yCarril} ` +
      `C${destino.x} ${yCarril} ` +
      `${destino.x} ${yCarril} ` +
      `${destino.x} ${destino.y + radio + 4}`;

    flecha(
      trazo,
      grupo.simbolos,
      `R${i + 1}`,
      (origen.x + destino.x) / 2,
      yCarril - 8,
    );

    leyenda.push({
      id: `R${i + 1}`,
      origen: grupo.origen,
      destino: grupo.destino,
      simbolos: grupo.simbolos.join(", "),
    });
  });

  for (const estado of estados) {
    const posicion = posiciones.get(estado);
    const esFinal = finales.has(estado);

    svg.appendChild(
      crearSvg("circle", {
        cx: posicion.x,
        cy: posicion.y,
        r: radio,
        fill: esFinal ? "#dcfce7" : "#eff6ff",
        stroke: esFinal ? "#15803d" : "#17365d",
        "stroke-width": 2,
      }),
    );

    if (esFinal) {
      svg.appendChild(
        crearSvg("circle", {
          cx: posicion.x,
          cy: posicion.y,
          r: radio - 5,
          fill: "none",
          stroke: "#15803d",
          "stroke-width": 2,
        }),
      );
    }

    anadirTexto(svg, posicion.x, posicion.y + 5, estado, 13, { negrita: true });
  }

  anadirTexto(
    svg,
    ancho / 2,
    alto - 25,
    "Doble círculo: estado de aceptación. R1, R2…: transiciones de retorno.",
    12,
    { color: "#64748b" },
  );

  const lienzo = document.createElement("div");
  lienzo.className = "automata-lienzo";

  lienzo.style.width = "100%";
  lienzo.style.maxWidth = "100%";
  lienzo.style.overflowX = "hidden";
  lienzo.style.overflowY = "hidden";

  svg.style.display = "block";
  svg.style.width = "100%";
  svg.style.maxWidth = "100%";
  svg.style.height = "auto";

  lienzo.appendChild(svg);
  contenedor.appendChild(lienzo);

  if (leyenda.length) {
    const details = document.createElement("details");
    details.className = "automata-leyenda";
    details.open = true;

    const summary = document.createElement("summary");

    summary.textContent = `Transiciones de retorno (${leyenda.length})`;

    details.appendChild(summary);

    const tabla = document.createElement("table");
    const thead = document.createElement("thead");
    const encabezado = document.createElement("tr");

    for (const texto of ["Referencia", "Origen", "Símbolos", "Destino"]) {
      const th = document.createElement("th");
      th.textContent = texto;
      encabezado.appendChild(th);
    }

    thead.appendChild(encabezado);
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");

    for (const grupo of leyenda) {
      agregarFila(tbody, [
        grupo.id,
        grupo.origen,
        grupo.simbolos,
        grupo.destino,
      ]);
    }

    tabla.appendChild(tbody);

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-contenedor";
    envoltorio.appendChild(tabla);

    details.appendChild(envoltorio);
    contenedor.appendChild(details);
  }
}

async function obtenerAutomata(campo, tipo) {
  const respuesta = await fetch(
    `/api/automatas/${encodeURIComponent(campo)}/${tipo}`,
  );

  if (!respuesta.ok) {
    throw new Error(
      `Error HTTP ${respuesta.status} al cargar ${tipo.toUpperCase()}`,
    );
  }

  return respuesta.json();
}

let solicitudActual = 0;

async function cargarCampoAutomatas(campo) {
  const numero = ++solicitudActual;

  const campoNormalizado = String(campo || "DNI").toUpperCase();

  const contenedorAFND = document.getElementById("grafico-afnd");

  const contenedorAFD = document.getElementById("grafico-afd");

  if (!contenedorAFND || !contenedorAFD) return;

  contenedorAFND.textContent = "Cargando AFND...";
  contenedorAFD.textContent = "Cargando AFD...";

  [
    "quintupla-afnd",
    "quintupla-afd",
    "transiciones-afnd",
    "transiciones-afd",
  ].forEach(function (id) {
    const elemento = document.getElementById(id);

    if (elemento) {
      elemento.replaceChildren();
    }
  });

  const titulo = document.getElementById("titulo-expresion");

  const expresion = document.getElementById("expresion-actual");

  const descripcionAFND = document.getElementById("descripcion-afnd");

  const descripcionAFD = document.getElementById("descripcion-afd");

  if (titulo) {
    titulo.textContent = `Expresión regular de ${campoNormalizado}`;
  }

  if (expresion) {
    expresion.textContent = PATRONES_AUTOMATAS[campoNormalizado] || "";
  }

  if (descripcionAFND) {
    descripcionAFND.textContent = `El AFND reconoce los valores que cumplen la expresión regular de ${campoNormalizado}.`;
  }

  if (descripcionAFD) {
    descripcionAFD.textContent = `El AFD reconoce los valores de ${campoNormalizado} mediante transiciones deterministas.`;
  }

  try {
    const [afnd, afd] = await Promise.all([
      obtenerAutomata(campoNormalizado, "afnd"),
      obtenerAutomata(campoNormalizado, "afd"),
    ]);

    if (numero !== solicitudActual) return;

    dibujarAutomata(contenedorAFND, afnd);
    dibujarAutomata(contenedorAFD, afd);

    llenarQuintupla("quintupla-afnd", afnd);
    llenarQuintupla("quintupla-afd", afd);

    llenarTransiciones("transiciones-afnd", afnd);
    llenarTransiciones("transiciones-afd", afd);
  } catch (error) {
    if (numero !== solicitudActual) return;

    contenedorAFND.textContent = error.message;
    contenedorAFD.textContent = error.message;
  }
}

window.cargarCampoAutomatas = cargarCampoAutomatas;
