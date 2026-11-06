const NS = "http://www.w3.org/2000/svg";
const DIGITOS = [..."0123456789"];

function html(tag, texto = "", clase = "") {
  const e = document.createElement(tag);
  e.textContent = texto;
  if (clase) e.className = clase;
  return e;
}

function svg(tag, attrs = {}, texto = null) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    e.setAttribute(k, String(v));
  }
  if (texto !== null) e.textContent = String(texto);
  return e;
}

function ordenar(a, b) {
  const x = /^q(\d+)$/.exec(a);
  const y = /^q(\d+)$/.exec(b);
  return x && y ? Number(x[1]) - Number(y[1]) : a.localeCompare(b, "es");
}

function simbolo(s) {
  return s === " " ? "␠ (espacio)" : s === "\t" ? "⇥ (tabulación)" : s;
}

function gruposDe(transiciones) {
  const m = new Map();

  for (const t of transiciones) {
    const k = JSON.stringify([t.origen, t.destino]);
    if (!m.has(k)) {
      m.set(k, {
        origen: t.origen,
        destino: t.destino,
        simbolos: new Set(),
      });
    }
    m.get(k).simbolos.add(t.simbolo);
  }

  return [...m.values()]
    .map((g) => ({
      ...g,
      simbolos: [...g.simbolos].sort(),
    }))
    .sort(
      (a, b) => ordenar(a.origen, b.origen) || ordenar(a.destino, b.destino),
    );
}

function etiqueta(g, i) {
  if (g.simbolos.length === 1) {
    return g.simbolos[0] === " " ? "␠" : g.simbolos[0];
  }

  if (
    g.simbolos.length === 10 &&
    DIGITOS.every((d) => g.simbolos.includes(d))
  ) {
    return "D";
  }

  if (g.simbolos.length <= 3) {
    return g.simbolos.join(", ");
  }

  return `C${i + 1}`;
}

function estilos() {
  if (!document.getElementById("automatas-estilos-fase-final")) {
    const e = html("style");
    e.id = "automatas-estilos-fase-final";

    e.textContent = `
      .comparacion-automatas {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0;
        align-items: start;
      }

      .tarjeta-automata {
        min-width: 0;
        background: #fff;
        border: 1px solid #bcd2e9;
        border-radius: 8px;
        overflow: hidden;
      }

      .tarjeta-automata > h3 {
        margin: 0;
        padding: 13px;
        background: #e7f2ff;
        text-align: center;
        font-size: 15px;
      }

      .tarjeta-automata > p {
        padding: 0 12px;
        font-size: 13px;
      }

      .tarjeta-automata .contenedor-automata {
        padding: 12px;
        border: 0;
        min-height: 0;
        overflow: visible;
      }

      .comparacion-automatas.correo-amplio
      .tarjeta-automata:nth-child(2) {
        grid-column: 1 / -1;
      }

      .lienzo-automata {
        overflow-x: auto;
        max-width: 100%;
      }

      .lienzo-automata svg {
        display: block;
        width: 100%;
        height: auto;
      }

      .lienzo-automata.correo svg {
        width: 1550px !important;
        min-width: 1550px !important;
        max-width: none !important;
      }

      .nota-automata {
        margin: 12px 0;
        padding: 10px;
        border-left: 3px solid #169868;
        background: #edf8f2;
        font-size: 12px;
        line-height: 1.6;
      }

      .leyenda-diagrama {
        margin: 12px 0;
        padding: 9px;
        border: 1px solid #cedff0;
        background: #f0f6fd;
        border-radius: 7px;
      }

      .leyenda-diagrama summary {
        font-weight: bold;
        cursor: pointer;
        color: #17365d;
      }

      .tabla-contenedor {
        margin-top: 10px;
        overflow-x: auto;
      }

      .leyenda-diagrama table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
      }

      .leyenda-diagrama th,
      .leyenda-diagrama td {
        padding: 7px;
        border-bottom: 1px solid #d4e1ef;
        text-align: left;
        overflow-wrap: anywhere;
      }

      .leyenda-diagrama th {
        background: #1b395d;
        color: #fff;
      }

      @media (max-width: 850px) {
        .comparacion-automatas {
          grid-template-columns: 1fr;
        }
      }
    `;

    document.head.appendChild(e);
  }

  if (document.getElementById("comparacion-automatas")) {
    return;
  }

  const afnd = document.getElementById("grafico-afnd");
  const afd = document.getElementById("grafico-afd");

  if (!afnd || !afd) return;

  const descA = afnd.previousElementSibling;
  const descB = afd.previousElementSibling;

  const tituloA = descA?.previousElementSibling;
  const tituloB = descB?.previousElementSibling;

  if (!tituloA || !tituloB) return;

  const grid = html("div", "", "comparacion-automatas");
  grid.id = "comparacion-automatas";

  tituloA.parentNode.insertBefore(grid, tituloA);

  for (const [t, d, g] of [
    [tituloA, descA, afnd],
    [tituloB, descB, afd],
  ]) {
    const card = html("section", "", "tarjeta-automata");
    card.append(t, d, g);
    grid.appendChild(card);
  }
}

function marco(id, ancho, alto) {
  const dibujo = svg("svg", {
    viewBox: `0 0 ${ancho} ${alto}`,
    role: "img",
    "aria-label": id,
  });

  const defs = svg("defs");

  const marcador = svg("marker", {
    id: `punta-${id}`,
    markerWidth: 9,
    markerHeight: 9,
    refX: 8,
    refY: 4.5,
    orient: "auto",
    markerUnits: "strokeWidth",
  });

  marcador.appendChild(
    svg("path", {
      d: "M0 0 L9 4.5 L0 9 Z",
      fill: "#41688e",
    }),
  );

  defs.appendChild(marcador);
  dibujo.appendChild(defs);

  return dibujo;
}

function texto(d, x, y, s, tam = 13) {
  d.appendChild(
    svg(
      "text",
      {
        x,
        y,
        "text-anchor": "middle",
        "font-family": "Arial,sans-serif",
        "font-size": tam,
        fill: "#19385b",
        stroke: "white",
        "stroke-width": 4,
        "paint-order": "stroke",
      },
      s,
    ),
  );
}

function flecha(d, id, ruta, clase = "normal", epsilon = false) {
  const color = clase === "rechazo" ? "#c05a4b" : "#41688e";

  d.appendChild(
    svg("path", {
      d: ruta,
      fill: "none",
      stroke: color,
      "stroke-width": 2,
      ...(epsilon ? { "stroke-dasharray": "6 5" } : {}),
      "marker-end": `url(#punta-${id})`,
    }),
  );
}

function nodo(d, id, p, a, sumidero) {
  const final = a.finales.includes(id);
  const inicial = a.inicial === id;

  const borde = final || inicial ? "#16864b" : sumidero ? "#bd5047" : "#316a9c";

  const relleno = final
    ? "#ddf6e6"
    : inicial
      ? "#e1f6e8"
      : sumidero
        ? "#fde9e9"
        : "#e6f0fa";

  d.appendChild(
    svg("circle", {
      cx: p.x,
      cy: p.y,
      r: 30,
      fill: relleno,
      stroke: borde,
      "stroke-width": 2,
    }),
  );

  if (final) {
    d.appendChild(
      svg("circle", {
        cx: p.x,
        cy: p.y,
        r: 24,
        fill: "none",
        stroke: borde,
        "stroke-width": 2,
      }),
    );
  }

  texto(d, p.x, p.y + 5, id);

  if (sumidero) {
    texto(d, p.x, p.y + 53, "sumidero", 12);
  }
}

function sumideroDe(a) {
  if (a.tipo !== "AFD") return null;

  return (
    a.estados.find(
      (q) =>
        !a.finales.includes(q) &&
        a.alfabeto.length > 0 &&
        a.alfabeto.every((s) =>
          a.transiciones.some(
            (t) => t.origen === q && t.destino === q && t.simbolo === s,
          ),
        ),
    ) || null
  );
}

function posiciones(a) {
  const m = (entradas) => new Map(entradas.map(([id, x, y]) => [id, { x, y }]));

  if (a.campo === "DNI" && a.estados.length === 10) {
    return m([
      ["q0", 90, 120],
      ["q1", 260, 120],
      ["q2", 430, 120],
      ["q3", 430, 260],
      ["q4", 260, 260],
      ["q5", 90, 260],
      ["q6", 90, 400],
      ["q7", 260, 400],
      ["q8", 430, 400],
      ["q9", 430, 545],
    ]);
  }

  if (a.campo === "CORREO" && a.tipo === "AFND" && a.estados.length === 8) {
    return m([
      ["q0", 90, 125],
      ["q1", 260, 125],
      ["q2", 430, 125],
      ["q3", 430, 285],
      ["q4", 260, 285],
      ["q5", 90, 285],
      ["q6", 90, 450],
      ["q7", 260, 450],
    ]);
  }

  if (a.campo === "CORREO" && a.tipo === "AFD" && a.estados.length === 8) {
    return m([
      ["q0", 120, 210],
      ["q1", 400, 210],
      ["q3", 680, 210],
      ["q4", 960, 210],
      ["q5", 1240, 210],
      ["q6", 1240, 490],
      ["q7", 960, 490],
      ["q2", 670, 930],
    ]);
  }

  return m(
    [...a.estados]
      .sort(ordenar)
      .map((id, i) => [id, 100 + (i % 3) * 170, 125 + Math.floor(i / 3) * 155]),
  );
}

function vistaBasica(a, id, grupos, nombres) {
  const alto = a.campo === "DNI" ? 660 : a.campo === "CORREO" ? 570 : 320;

  const d = marco(id, 530, alto);

  const pos = posiciones(a);
  const destino = sumideroDe(a);

  const rutasCorreo = new Set([
    "q0/q1",
    "q1/q2",
    "q2/q2",
    "q2/q3",
    "q3/q4",
    "q4/q4",
    "q4/q5",
    "q5/q6",
    "q6/q7",
    "q7/q7",
  ]);

  const dibujados =
    a.campo === "CORREO"
      ? grupos.filter((g) => rutasCorreo.has(`${g.origen}/${g.destino}`))
      : grupos;

  const inicio = pos.get(a.inicial);

  if (inicio) {
    flecha(
      d,
      id,
      `M${inicio.x - 70} ${inicio.y} ` + `L${inicio.x - 35} ${inicio.y}`,
    );

    texto(d, inicio.x - 54, inicio.y - 15, "inicio", 11);
  }

  for (const g of dibujados) {
    const p = pos.get(g.origen);
    const q = pos.get(g.destino);

    if (!p || !q) continue;

    const et = nombres.get(g);

    if (g.origen === g.destino) {
      const signo = p.y < 220 ? -1 : 1;

      flecha(
        d,
        id,
        `M${p.x - 19} ${p.y + signo * 24} ` +
          `C${p.x - 72} ${p.y + signo * 95}, ` +
          `${p.x + 72} ${p.y + signo * 95}, ` +
          `${p.x + 19} ${p.y + signo * 24}`,
      );

      texto(d, p.x, p.y + signo * 82, et, 11);
    } else {
      const dx = q.x - p.x;
      const dy = q.y - p.y;
      const l = Math.hypot(dx, dy);

      if (!l) continue;

      const ux = dx / l;
      const uy = dy / l;

      const x1 = p.x + ux * 35;
      const y1 = p.y + uy * 35;
      const x2 = q.x - ux * 37;
      const y2 = q.y - uy * 37;

      flecha(
        d,
        id,
        `M${x1} ${y1} L${x2} ${y2}`,
        "normal",
        g.simbolos.includes("ε"),
      );

      texto(
        d,
        (x1 + x2) / 2 + (Math.abs(dy) > Math.abs(dx) ? 20 : 0),
        (y1 + y2) / 2 - (Math.abs(dy) > Math.abs(dx) ? 0 : 15),
        et,
        11,
      );
    }
  }

  for (const [q, p] of pos) {
    nodo(d, q, p, a, q === destino);
  }

  return { d, dibujados };
}

function vistaCorreoAFD(a, id, grupos, nombres) {
  const d = marco(id, 1450, 1080);
  const pos = posiciones(a);
  const sumidero = sumideroDe(a);

  const principales = new Set([
    "q0/q1",
    "q1/q1",
    "q1/q3",
    "q3/q4",
    "q4/q4",
    "q4/q5",
    "q5/q6",
    "q6/q7",
    "q7/q7",
  ]);

  const inicio = pos.get(a.inicial);

  if (inicio) {
    flecha(
      d,
      id,
      `M${inicio.x - 75} ${inicio.y} ` + `L${inicio.x - 36} ${inicio.y}`,
    );

    texto(d, inicio.x - 55, inicio.y - 20, "inicio", 12);
  }

  const normales = [];
  const rechazos = [];
  const extras = [];

  for (const g of grupos) {
    const par = `${g.origen}/${g.destino}`;

    if (g.destino === sumidero && g.origen !== sumidero) {
      rechazos.push(g);
    } else if (
      principales.has(par) ||
      (g.origen === sumidero && g.destino === sumidero)
    ) {
      normales.push(g);
    } else {
      extras.push(g);
    }
  }

  for (const g of normales) {
    const p = pos.get(g.origen);
    const q = pos.get(g.destino);
    const et = nombres.get(g);

    if (!p || !q) continue;

    if (g.origen === g.destino) {
      const signo = p.y > 800 ? 1 : -1;

      flecha(
        d,
        id,
        `M${p.x - 20} ${p.y + signo * 24} ` +
          `C${p.x - 90} ${p.y + signo * 122}, ` +
          `${p.x + 90} ${p.y + signo * 122}, ` +
          `${p.x + 20} ${p.y + signo * 24}`,
      );

      texto(d, p.x, p.y + signo * 97, et, 13);
    } else {
      const dx = q.x - p.x;
      const dy = q.y - p.y;
      const l = Math.hypot(dx, dy);
      if (!l) continue;

      const ux = dx / l;
      const uy = dy / l;

      flecha(
        d,
        id,
        `M${p.x + ux * 36} ${p.y + uy * 36} ` +
          `L${q.x - ux * 37} ${q.y - uy * 37}`,
        "normal",
        g.simbolos.includes("ε"),
      );

      texto(
        d,
        (p.x + q.x) / 2 + (Math.abs(dy) > Math.abs(dx) ? 22 : 0),
        (p.y + q.y) / 2 - (Math.abs(dy) > Math.abs(dx) ? 0 : 18),
        et,
        13,
      );
    }
  }

  extras.forEach((g, i) => {
    const p = pos.get(g.origen);
    const q = pos.get(g.destino);

    if (!p || !q) return;

    const x1 = p.x;
    const y1 = p.y + 34;
    const x2 = q.x;
    const y2 = q.y + 34;
    const altura = 640 + i * 52;

    flecha(
      d,
      id,
      `M${x1} ${y1} ` +
        `C${x1} ${altura}, ` +
        `${x2} ${altura}, ` +
        `${x2} ${y2}`,
    );

    texto(d, (x1 + x2) / 2, altura + 12, nombres.get(g), 12);
  });

  rechazos.forEach((g, i) => {
    const p = pos.get(g.origen);
    const q = pos.get(g.destino);

    if (!p || !q) return;

    const pista = 755 + i * 27;
    const entradaX = q.x - 25 + (i % 5) * 12;
    const entradaY = q.y - 20;

    flecha(
      d,
      id,
      `M${p.x} ${p.y + 32} ` +
        `C${p.x} ${pista}, ` +
        `${entradaX} ${pista}, ` +
        `${entradaX} ${entradaY}`,
      "rechazo",
    );

    texto(d, p.x + 16, p.y + 65, nombres.get(g), 12);
  });

  for (const [q, p] of pos) {
    nodo(d, q, p, a, q === sumidero);
  }

  texto(
    d,
    780,
    1030,
    "Azul: transición ordinaria | Rojo: hacia el sumidero | Cn: conjunto definido en la tabla",
    15,
  );

  return {
    d,
    dibujados: grupos,
  };
}

function tablaDetalles(grupos, nombres, dibujados) {
  const details = html("details", "", "leyenda-diagrama");

  details.appendChild(html("summary", "Ver símbolos y todas las transiciones"));

  const cont = html("div", "", "tabla-contenedor");

  const table = html("table");
  const thead = html("thead");
  const tr = html("tr");

  for (const c of [
    "Origen",
    "Etiqueta",
    "Símbolos exactos",
    "Destino",
    "En el diagrama",
  ]) {
    tr.appendChild(html("th", c));
  }

  thead.appendChild(tr);
  table.appendChild(thead);

  const body = html("tbody");

  for (const g of grupos) {
    const fila = html("tr");

    const valores = [
      g.origen,
      nombres.get(g),
      g.simbolos.map(simbolo).join(", "),
      g.destino,
      dibujados.includes(g) ? "Sí" : "Solo tabla",
    ];

    for (const v of valores) {
      fila.appendChild(html("td", v));
    }

    body.appendChild(fila);
  }

  table.appendChild(body);
  cont.appendChild(table);
  details.appendChild(cont);

  return details;
}

function dibujarAutomata(a, id) {
  const cont = document.getElementById(id);

  if (!cont) return;

  cont.replaceChildren();

  const grupos = gruposDe(a.transiciones);

  const nombres = new Map(grupos.map((g, i) => [g, etiqueta(g, i)]));

  const completo =
    a.campo === "CORREO" && a.tipo === "AFD" && a.estados.length === 8;

  const dibujo = completo
    ? vistaCorreoAFD(a, id, grupos, nombres)
    : vistaBasica(a, id, grupos, nombres);

  const lienzo = html(
    "div",
    "",
    "lienzo-automata" + (completo ? " correo" : ""),
  );

  lienzo.appendChild(dibujo.d);
  cont.appendChild(lienzo);

  let nota =
    "Los símbolos C1, C2, etc. se definen " + "en la tabla de transiciones.";

  if (a.campo === "DNI") {
    nota =
      "D = {0,1,2,3,4,5,6,7,8,9}. " +
      "Cada D consume un dígito; " +
      "ε no consume caracteres.";
  }

  if (a.campo === "CORREO" && a.tipo === "AFND") {
    nota =
      "AFND: ruta principal visible. " +
      "Todas las transiciones figuran " +
      "en la tabla completa.";
  }

  if (completo) {
    nota =
      `AFD: ${dibujo.dibujados.length} de ` +
      `${grupos.length} grupos dibujados ` +
      "en el mismo grafo. Usa la barra " +
      "horizontal para recorrerlo.";
  }

  cont.appendChild(html("div", nota, "nota-automata"));

  cont.appendChild(tablaDetalles(grupos, nombres, dibujo.dibujados));
}

function filaQuintupla(tabla, izquierda, derecha) {
  const tr = html("tr");

  tr.appendChild(html("td", izquierda));
  tr.appendChild(html("td", derecha));

  tabla.appendChild(tr);
}

function mostrarQuintupla(a, id) {
  const t = document.getElementById(id);

  if (!t) return;

  t.replaceChildren();

  filaQuintupla(
    t,
    "Q (estados)",
    `{ ${[...a.estados].sort(ordenar).join(", ")} }`,
  );

  filaQuintupla(t, "Σ (alfabeto)", `{ ${a.alfabeto.map(simbolo).join(", ")} }`);

  filaQuintupla(
    t,
    "δ (transiciones)",
    "Definidas en la tabla de transiciones completa",
  );

  filaQuintupla(t, "q₀ (inicial)", a.inicial);

  filaQuintupla(
    t,
    "F (finales)",
    `{ ${[...a.finales].sort(ordenar).join(", ")} }`,
  );
}

function mostrarTablaTransiciones(a, id) {
  const t = document.getElementById(id);

  if (!t) return;

  t.replaceChildren();

  for (const g of gruposDe(a.transiciones)) {
    const tr = html("tr");

    for (const v of [g.origen, g.simbolos.map(simbolo).join(", "), g.destino]) {
      tr.appendChild(html("td", v));
    }

    t.appendChild(tr);
  }
}

async function obtenerAutomata(campo, tipo) {
  const r = await fetch(`/api/automatas/${encodeURIComponent(campo)}/${tipo}`, {
    headers: {
      Accept: "application/json",
    },
  });

  if (!r.ok) {
    throw new Error(`No se pudo cargar el ${tipo.toUpperCase()} de ${campo}`);
  }

  return r.json();
}

let solicitudActual = 0;

async function cargarCampoAutomatas(campo) {
  estilos();

  const pedido = ++solicitudActual;

  const grid = document.getElementById("comparacion-automatas");

  if (grid) {
    grid.classList.toggle("correo-amplio", campo === "CORREO");
  }

  for (const id of ["grafico-afnd", "grafico-afd"]) {
    const e = document.getElementById(id);

    if (e) {
      e.replaceChildren(html("p", "Cargando autómata..."));
    }
  }

  try {
    const [afnd, afd] = await Promise.all([
      obtenerAutomata(campo, "afnd"),
      obtenerAutomata(campo, "afd"),
    ]);

    if (pedido !== solicitudActual) return;

    const titulo = document.getElementById("titulo-expresion");

    const expresion = document.getElementById("expresion-actual");

    if (titulo) {
      titulo.textContent = `Expresión regular de ${campo}`;
    }

    if (expresion) {
      expresion.textContent = afnd.expresion;
    }

    dibujarAutomata(afnd, "grafico-afnd");
    if (campo === "CORREO") {
      visualizarAFDCorreoInteractivo(afd);
    } else {
      dibujarAutomata(afd, "grafico-afd");
    }

    mostrarQuintupla(afnd, "quintupla-afnd");

    mostrarQuintupla(afd, "quintupla-afd");

    mostrarTablaTransiciones(afnd, "transiciones-afnd");

    mostrarTablaTransiciones(afd, "transiciones-afd");
  } catch (e) {
    if (pedido !== solicitudActual) return;

    for (const id of ["grafico-afnd", "grafico-afd"]) {
      const destino = document.getElementById(id);

      if (destino) {
        destino.replaceChildren(html("p", e.message, "resultado-error"));
      }
    }
  }
}

window.cargarCampoAutomatas = cargarCampoAutomatas;

const ordenarEstados = ordenar;
const agruparTransiciones = gruposDe;
const etiquetaTransicion = etiqueta;
const simboloVisible = simbolo;

function instalarVistaCorreoInteractiva() {
  if (document.getElementById("estilos-correo-interactivo")) return;

  const estilos = document.createElement("style");
  estilos.id = "estilos-correo-interactivo";

  estilos.textContent = `
    .comparacion-automatas.correo-amplio {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) !important;
      gap: 20px !important;
    }

    .comparacion-automatas.correo-amplio .tarjeta-automata {
      grid-column: 1 / -1 !important;
      width: 100% !important;
      box-sizing: border-box;
    }

    .comparacion-automatas.correo-amplio .lienzo-automata {
      width: 100%;
      overflow: visible !important;
    }

    .comparacion-automatas.correo-amplio .lienzo-automata svg {
      display: block !important;
      width: 100% !important;
      min-width: 0 !important;
      max-width: 100% !important;
      height: auto !important;
    }

    .controles-correo {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin: 12px 0;
    }

    .controles-correo button {
      padding: 8px 13px;
      background: #e8f2ff;
      border: 1px solid #b7d0e8;
      border-radius: 6px;
      color: #17365d;
      cursor: pointer;
      font-weight: 600;
    }

    .controles-correo button.activo {
      background: #17365d;
      color: white;
    }

    .resumen-estado-correo {
      padding: 12px;
      margin: 12px 0;
      background: #eef8f2;
      border-left: 3px solid #16875b;
      font-size: 13px;
      line-height: 1.6;
    }

    .correo-diagrama-interactivo {
      background: white;
      border: 1px solid #d5e2f0;
      border-radius: 8px;
      padding: 12px;
    }
  `;

  document.head.appendChild(estilos);
}

function visualizarAFDCorreoInteractivo(automata) {
  const contenedor = document.getElementById("grafico-afd");

  if (!contenedor) return;

  instalarVistaCorreoInteractiva();

  const grid = document.getElementById("comparacion-automatas");

  if (grid) {
    grid.classList.add("correo-amplio");
  }

  const estados = [...automata.estados].sort(ordenarEstados);
  const grupos = agruparTransiciones(automata.transiciones);

  const posiciones = new Map([
    ["q0", { x: 110, y: 180 }],
    ["q1", { x: 340, y: 180 }],
    ["q3", { x: 570, y: 180 }],
    ["q4", { x: 800, y: 180 }],
    ["q5", { x: 1030, y: 180 }],
    ["q6", { x: 1030, y: 440 }],
    ["q7", { x: 800, y: 440 }],
    ["q2", { x: 340, y: 440 }],
  ]);

  const controles = document.createElement("div");
  controles.className = "controles-correo";

  const titulo = document.createElement("strong");
  titulo.textContent = "Selecciona un estado:";
  controles.appendChild(titulo);

  const botones = new Map();

  for (const estado of estados) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = estado;
    controles.appendChild(boton);
    botones.set(estado, boton);
  }

  const resumen = document.createElement("div");
  resumen.className = "resumen-estado-correo";

  const lienzo = document.createElement("div");
  lienzo.className = "correo-diagrama-interactivo";

  contenedor.replaceChildren(controles, resumen, lienzo);

  const svgNS = "http://www.w3.org/2000/svg";

  function elementoSVG(tipo, atributos = {}, contenido = null) {
    const e = document.createElementNS(svgNS, tipo);

    for (const [clave, valor] of Object.entries(atributos)) {
      e.setAttribute(clave, String(valor));
    }

    if (contenido !== null) {
      e.textContent = String(contenido);
    }

    return e;
  }

  function escribir(dibujo, x, y, valor, tamano = 15) {
    dibujo.appendChild(
      elementoSVG(
        "text",
        {
          x,
          y,
          "text-anchor": "middle",
          "font-family": "Arial, sans-serif",
          "font-size": tamano,
          fill: "#17365d",
          stroke: "#fff",
          "stroke-width": 5,
          "paint-order": "stroke",
        },
        valor,
      ),
    );
  }

  function dibujarEstado(dibujo, estado, seleccionado) {
    const p = posiciones.get(estado);
    if (!p) return;

    const final = automata.finales.includes(estado);
    const sumidero = estado === "q2";

    const relleno = final
      ? "#dff7e8"
      : sumidero
        ? "#ffe7e7"
        : seleccionado
          ? "#d9e9ff"
          : "#edf4fc";

    const borde = final
      ? "#16814a"
      : sumidero
        ? "#c4514a"
        : seleccionado
          ? "#135fa6"
          : "#35669b";

    dibujo.appendChild(
      elementoSVG("circle", {
        cx: p.x,
        cy: p.y,
        r: 35,
        fill: relleno,
        stroke: borde,
        "stroke-width": seleccionado ? 4 : 2,
      }),
    );

    if (final) {
      dibujo.appendChild(
        elementoSVG("circle", {
          cx: p.x,
          cy: p.y,
          r: 29,
          fill: "none",
          stroke: borde,
          "stroke-width": 2,
        }),
      );
    }

    escribir(dibujo, p.x, p.y + 5, estado, 17);

    if (sumidero) {
      escribir(dibujo, p.x, p.y + 57, "sumidero", 14);
    }
  }

  function actualizar(estadoSeleccionado) {
    botones.forEach((boton, estado) => {
      boton.classList.toggle("activo", estado === estadoSeleccionado);
    });

    const salidas = grupos.filter(
      (grupo) => grupo.origen === estadoSeleccionado,
    );

    resumen.textContent =
      `Estado ${estadoSeleccionado}: ${salidas.length} ` +
      `grupo(s) de transiciones salientes. ` +
      `Se muestran sus conexiones reales. ` +
      `La tabla completa conserva las transiciones ` +
      `de todos los estados.`;

    const dibujo = elementoSVG("svg", {
      viewBox: "0 0 1160 620",
      role: "img",
      "aria-label": `Transiciones del estado ${estadoSeleccionado} del AFD de CORREO`,
    });

    dibujo.style.width = "100%";
    dibujo.style.height = "auto";
    dibujo.style.display = "block";

    const definiciones = elementoSVG("defs");

    for (const [nombre, color] of [
      ["azul", "#35669b"],
      ["rojo", "#c4514a"],
    ]) {
      const marcador = elementoSVG("marker", {
        id: `correo-flecha-${nombre}`,
        markerWidth: 10,
        markerHeight: 10,
        refX: 9,
        refY: 5,
        orient: "auto",
      });

      marcador.appendChild(
        elementoSVG("path", {
          d: "M0 0 L10 5 L0 10 Z",
          fill: color,
        }),
      );

      definiciones.appendChild(marcador);
    }

    dibujo.appendChild(definiciones);

    const inicial = posiciones.get(automata.inicial);

    if (inicial) {
      dibujo.appendChild(
        elementoSVG("path", {
          d: `M${inicial.x - 78} ${inicial.y} L${inicial.x - 40} ${inicial.y}`,
          stroke: "#35669b",
          "stroke-width": 2,
          fill: "none",
          "marker-end": "url(#correo-flecha-azul)",
        }),
      );

      escribir(dibujo, inicial.x - 58, inicial.y - 18, "inicio", 13);
    }

    salidas.forEach((grupo, indice) => {
      const origen = posiciones.get(grupo.origen);
      const destino = posiciones.get(grupo.destino);

      if (!origen || !destino) return;

      const indiceGlobal = grupos.indexOf(grupo);

      const etiqueta = etiquetaTransicion(grupo, indiceGlobal);

      const rechazo = grupo.destino === "q2" && grupo.origen !== "q2";

      const color = rechazo ? "#c4514a" : "#35669b";

      const marcador = rechazo
        ? "url(#correo-flecha-rojo)"
        : "url(#correo-flecha-azul)";

      let ruta;
      let tx;
      let ty;

      if (grupo.origen === grupo.destino) {
        const signo = origen.y < 300 ? -1 : 1;

        const altura = 90 + indice * 12;

        ruta =
          `M${origen.x - 20} ${origen.y + signo * 29} ` +
          `C${origen.x - 85} ${origen.y + signo * altura}, ` +
          `${origen.x + 85} ${origen.y + signo * altura}, ` +
          `${origen.x + 20} ${origen.y + signo * 29}`;

        tx = origen.x;
        ty = origen.y + signo * (altura - 15);
      } else {
        const dx = destino.x - origen.x;
        const dy = destino.y - origen.y;
        const distancia = Math.hypot(dx, dy);

        const ux = dx / distancia;
        const uy = dy / distancia;

        const x1 = origen.x + ux * 41;
        const y1 = origen.y + uy * 41;

        const x2 = destino.x - ux * 43;
        const y2 = destino.y - uy * 43;

        const separacion =
          salidas.length === 1 ? 0 : (indice - (salidas.length - 1) / 2) * 38;

        const mx = (x1 + x2) / 2 - uy * separacion;

        const my = (y1 + y2) / 2 + ux * separacion;

        ruta = `M${x1} ${y1} Q${mx} ${my} ${x2} ${y2}`;

        tx = (x1 + 2 * mx + x2) / 4;
        ty = (y1 + 2 * my + y2) / 4 - 14;
      }

      dibujo.appendChild(
        elementoSVG("path", {
          d: ruta,
          fill: "none",
          stroke: color,
          "stroke-width": 2.5,
          "marker-end": marcador,
          ...(grupo.simbolos.includes("ε")
            ? { "stroke-dasharray": "6 5" }
            : {}),
        }),
      );

      escribir(dibujo, tx, ty, etiqueta, 15);
    });

    for (const estado of estados) {
      dibujarEstado(dibujo, estado, estado === estadoSeleccionado);
    }

    const total = salidas.length;

    escribir(
      dibujo,
      580,
      575,
      `Transiciones salientes de ${estadoSeleccionado}: ${total}`,
      15,
    );

    lienzo.replaceChildren(dibujo);
  }

  for (const [estado, boton] of botones) {
    boton.addEventListener("click", () => actualizar(estado));
  }

  actualizar(automata.inicial);

  const nota = document.createElement("p");
  nota.className = "nota-automata";
  nota.textContent =
    `AFD de CORREO: ${estados.length} estados y ` +
    `${grupos.length} grupos de transiciones. ` +
    `Selecciona un estado para visualizar únicamente ` +
    `sus transiciones salientes y evitar superposiciones.`;

  contenedor.appendChild(nota);

  const detalles = document.createElement("details");
  detalles.className = "leyenda-diagrama";

  const sumario = document.createElement("summary");
  sumario.textContent = "Ver las 22 transiciones del AFD";
  detalles.appendChild(sumario);

  const tabla = document.createElement("table");
  const encabezado = document.createElement("thead");
  const filaCabecera = document.createElement("tr");

  for (const titulo of ["Origen", "Etiqueta", "Símbolos exactos", "Destino"]) {
    const th = document.createElement("th");
    th.textContent = titulo;
    filaCabecera.appendChild(th);
  }

  encabezado.appendChild(filaCabecera);
  tabla.appendChild(encabezado);

  const cuerpo = document.createElement("tbody");

  grupos.forEach((grupo, indice) => {
    const fila = document.createElement("tr");

    for (const valor of [
      grupo.origen,
      etiquetaTransicion(grupo, indice),
      grupo.simbolos.map(simboloVisible).join(", "),
      grupo.destino,
    ]) {
      const celda = document.createElement("td");
      celda.textContent = valor;
      fila.appendChild(celda);
    }

    cuerpo.appendChild(fila);
  });

  tabla.appendChild(cuerpo);

  const area = document.createElement("div");
  area.className = "tabla-contenedor";
  area.appendChild(tabla);

  detalles.appendChild(area);
  contenedor.appendChild(detalles);
}

const PALABRAS_TOKEN = {
  TK_SECCION: ["DATOS_PERSONALES", "EDUCACION", "EXPERIENCIA"],
  TK_CAMPO: ["NOMBRE", "DNI", "CORREO", "INSTITUCION", "PUESTO"],
  TK_ABRE: ["{"],
  TK_CIERRA: ["}"],
  TK_DOS_PUNTOS: [":"],
};

let automatasTokenActuales = {};
let palabraTokenActual = "";

function rutaAceptadaToken(a, palabra) {
  const primero = {
    estado: a.inicial,
    indice: 0,
    anterior: null,
    letra: null,
  };

  const cola = [primero];
  const vistos = new Set([`${primero.estado}:0`]);
  const salidas = new Map();

  for (const t of a.transiciones) {
    if (!salidas.has(t.origen)) {
      salidas.set(t.origen, []);
    }
    salidas.get(t.origen).push(t);
  }

  for (let i = 0; i < cola.length; i++) {
    const actual = cola[i];

    if (actual.indice === palabra.length && a.finales.includes(actual.estado)) {
      const camino = [];
      for (let p = actual; p; p = p.anterior) {
        camino.push(p);
      }
      return camino.reverse();
    }

    for (const t of salidas.get(actual.estado) || []) {
      const epsilon = t.simbolo === "ε";

      if (!epsilon && palabra[actual.indice] !== t.simbolo) {
        continue;
      }

      const indice = actual.indice + (epsilon ? 0 : 1);
      const clave = `${t.destino}:${indice}`;

      if (vistos.has(clave)) continue;

      vistos.add(clave);

      cola.push({
        estado: t.destino,
        indice,
        anterior: actual,
        letra: t.simbolo,
      });
    }
  }

  return null;
}

function rutaTokenSVG(a, palabra) {
  const camino = rutaAceptadaToken(a, palabra);

  if (!camino) {
    return html(
      "p",
      `No existe recorrido válido para ${palabra}.`,
      "resultado-error",
    );
  }

  const columnas = 6;
  const filas = Math.ceil(camino.length / columnas);

  const dibujo = svg("svg", {
    viewBox: `0 0 920 ${filas * 135 + 65}`,
    role: "img",
    "aria-label": `Recorrido de ${palabra} en ${a.tipo}`,
  });

  const idFlecha = `flecha-${a.tipo}-token`;
  const defs = svg("defs");

  const marcador = svg("marker", {
    id: idFlecha,
    markerWidth: 8,
    markerHeight: 8,
    refX: 7,
    refY: 4,
    orient: "auto",
  });

  marcador.appendChild(
    svg("path", {
      d: "M0 0 L8 4 L0 8 Z",
      fill: "#376da1",
    }),
  );

  defs.appendChild(marcador);
  dibujo.appendChild(defs);

  const puntos = camino.map((_, i) => {
    const fila = Math.floor(i / columnas);
    const columna = i % columnas;

    return {
      x: 95 + (fila % 2 ? columnas - columna - 1 : columna) * 148,
      y: 85 + fila * 135,
    };
  });

  for (let i = 1; i < camino.length; i++) {
    const p = puntos[i - 1];
    const q = puntos[i];

    const longitud = Math.hypot(q.x - p.x, q.y - p.y);

    const ux = (q.x - p.x) / longitud;
    const uy = (q.y - p.y) / longitud;

    dibujo.appendChild(
      svg("path", {
        d: `M${p.x + ux * 31} ${p.y + uy * 31} L${q.x - ux * 33} ${q.y - uy * 33}`,
        fill: "none",
        stroke: "#376da1",
        "stroke-width": 2,
        ...(camino[i].letra === "ε" ? { "stroke-dasharray": "5 4" } : {}),
        "marker-end": `url(#${idFlecha})`,
      }),
    );

    const dx = Math.abs(q.x - p.x);

    dibujo.appendChild(
      svg(
        "text",
        {
          x: (p.x + q.x) / 2 + (dx < 10 ? 20 : 0),
          y: (p.y + q.y) / 2 - (dx < 10 ? 0 : 13),
          "font-size": 14,
          "text-anchor": "middle",
          fill: "#1b395b",
        },
        camino[i].letra,
      ),
    );
  }

  for (let i = 0; i < camino.length; i++) {
    const p = puntos[i];
    const final = a.finales.includes(camino[i].estado);

    dibujo.appendChild(
      svg("circle", {
        cx: p.x,
        cy: p.y,
        r: 27,
        fill: final ? "#ddf8e6" : "#e6f1fc",
        stroke: final ? "#16834a" : "#376da1",
        "stroke-width": 2,
      }),
    );

    if (final) {
      dibujo.appendChild(
        svg("circle", {
          cx: p.x,
          cy: p.y,
          r: 22,
          fill: "none",
          stroke: "#16834a",
          "stroke-width": 2,
        }),
      );
    }

    dibujo.appendChild(
      svg(
        "text",
        {
          x: p.x,
          y: p.y + 5,
          "font-size": 13,
          "text-anchor": "middle",
          fill: "#1b395b",
        },
        camino[i].estado,
      ),
    );
  }

  const panel = html("div", "", "recorrido-token");
  panel.appendChild(dibujo);

  panel.appendChild(
    html(
      "div",
      `Recorrido válido de «${palabra}». Se muestran ${camino.length} estados visitados de los ${a.estados.length} del autómata. La tabla inferior contiene todas las transiciones.`,
      "nota-automata",
    ),
  );

  return panel;
}

function actualizarRutaToken() {
  for (const [tipo, id] of [
    ["AFND", "grafico-afnd"],
    ["AFD", "grafico-afd"],
  ]) {
    const a = automatasTokenActuales[tipo];

    if (!a) continue;

    const cont = document.getElementById(id);

    if (!cont) continue;

    const controles = cont.querySelector(".selector-lexema-token");

    const panel = rutaTokenSVG(a, palabraTokenActual);

    const grupos = gruposDe(a.transiciones);

    const etiquetas = new Map(grupos.map((g, i) => [g, etiqueta(g, i)]));

    cont.replaceChildren();

    if (controles) {
      cont.appendChild(controles);
    }

    cont.appendChild(panel);

    cont.appendChild(tablaDetalles(grupos, etiquetas, []));
  }
}

const dibujarAutomataAnterior = dibujarAutomata;

dibujarAutomata = function (a, id) {
  if (!Object.prototype.hasOwnProperty.call(PALABRAS_TOKEN, a.campo)) {
    return dibujarAutomataAnterior(a, id);
  }

  if (automatasTokenActuales.campo !== a.campo) {
    automatasTokenActuales = {
      campo: a.campo,
    };

    palabraTokenActual = PALABRAS_TOKEN[a.campo][0];
  }

  automatasTokenActuales[a.tipo] = a;

  const destino = document.getElementById(id);

  if (!destino) return;

  if (a.tipo === "AFND") {
    const controles = html("div", "", "selector-lexema-token");

    const titulo = html("label", "Lexema para visualizar: ");

    const selector = html("select");

    for (const palabra of PALABRAS_TOKEN[a.campo]) {
      const opcion = html("option", palabra);
      opcion.value = palabra;
      selector.appendChild(opcion);
    }

    selector.value = palabraTokenActual;

    selector.addEventListener("change", () => {
      palabraTokenActual = selector.value;
      actualizarRutaToken();
    });

    titulo.appendChild(selector);
    controles.appendChild(titulo);
    destino.replaceChildren(controles);
  }

  actualizarRutaToken();
};

const cargarCampoAutomatasAnterior = cargarCampoAutomatas;

cargarCampoAutomatas = function (campo) {
  estilos();

  const grid = document.getElementById("comparacion-automatas");

  if (grid) {
    grid.classList.toggle("token-amplio", campo.startsWith("TK_"));
  }

  if (!campo.startsWith("TK_")) {
    automatasTokenActuales = {};
  }

  return cargarCampoAutomatasAnterior(campo);
};

window.cargarCampoAutomatas = cargarCampoAutomatas;

const estilosTokens = document.createElement("style");

estilosTokens.textContent = `
  .comparacion-automatas.token-amplio {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .comparacion-automatas.token-amplio .tarjeta-automata {
    grid-column: 1 / -1;
  }

  .recorrido-token svg {
    display: block;
    width: 100%;
    height: auto;
  }

  .selector-lexema-token {
    padding: 12px 0;
  }

  .selector-lexema-token select {
    margin-left: 8px;
    padding: 7px;
  }
`;

document.head.appendChild(estilosTokens);
