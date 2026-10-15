
from pathlib import Path
from html import escape
from collections import defaultdict


def ordenar_estado(estado):
    texto = str(estado)

    if texto.startswith("q") and texto[1:].isdigit():
        return int(texto[1:])

    if texto.isdigit():
        return int(texto)

    return texto


def nombre_estado(estado):
    if isinstance(estado, int):
        return f"q{estado}"

    return str(estado)


def normalizar_destinos(destinos):
    if destinos is None:
        return set()

    if isinstance(destinos, (set, frozenset, list, tuple)):
        return set(destinos)

    return {destinos}


def etiqueta_simbolos(simbolos, alfabeto):
    simbolos = set(simbolos)
    alfabeto = set(alfabeto)

    if not simbolos:
        return "∅"

    if simbolos == alfabeto:
        if alfabeto == set("0123456789"):
            return "0-9"

        return "Σ"

    if len(simbolos) == 1:
        simbolo = next(iter(simbolos))

        if simbolo is None or simbolo == "":
            return "ε"

        return str(simbolo)

    if simbolos == set("0123456789"):
        return "0-9"

    if simbolos == set("abcdefghijklmnopqrstuvwxyz"):
        return "a-z"

    if simbolos == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        return "A-Z"

    if len(simbolos) <= 8:
        return ", ".join(sorted(str(s) for s in simbolos))

    return f"{len(simbolos)} símbolos"


def obtener_transiciones(automata, es_afnd):
    grupos = defaultdict(set)
    alfabeto = set(automata["Sigma"])

    for (origen, simbolo), destinos in automata["delta"].items():
        for destino in normalizar_destinos(destinos):
            if destino is not None:
                grupos[(origen, destino)].add(simbolo)

    transiciones = []

    for (origen, destino), simbolos in grupos.items():
        normales = simbolos.intersection(alfabeto)
        especiales = simbolos.difference(alfabeto)

        if normales:
            transiciones.append({
                "origen": origen,
                "destino": destino,
                "etiqueta": etiqueta_simbolos(normales, alfabeto)
            })

        for simbolo in especiales:
            transiciones.append({
                "origen": origen,
                "destino": destino,
                "etiqueta": "ε" if simbolo is None or simbolo == "" or str(simbolo).lower() in ("epsilon", "eps", "ε") else str(simbolo)
            })

    return sorted(
        transiciones,
        key=lambda t: (
            ordenar_estado(t["origen"]),
            ordenar_estado(t["destino"]),
            t["etiqueta"]
        )
    )


def elemento_svg(etiqueta, atributos, contenido=""):
    atributos_texto = " ".join(
        f'{clave.replace("_", "-")}="{escape(str(valor), quote=True)}"'
        for clave, valor in atributos.items()
    )

    return f"<{etiqueta} {atributos_texto}>{contenido}</{etiqueta}>"


def generar_svg(automata, titulo, archivo, es_afnd=False):
    estados = sorted(
        automata["Q"],
        key=ordenar_estado
    )

    if not estados:
        raise ValueError("El autómata no tiene estados")

    inicial = automata["q0"]
    finales = set(automata["F"])

    transiciones = obtener_transiciones(
        automata,
        es_afnd
    )

    radio = 24
    separacion = 108 if len(estados) > 6 else 190
    margen = 85

    ancho = max(
        680,
        margen * 2 + (len(estados) - 1) * separacion
    )

    alto = 270
    centro_y = 143

    posiciones = {
        estado: (
            margen + indice * separacion,
            centro_y
        )
        for indice, estado in enumerate(estados)
    }

    partes = []

    partes.append(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    partes.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}">'
    )

    partes.append(
        '<defs>'
        '<marker id="flecha" markerWidth="9" markerHeight="9" '
        'refX="8" refY="4.5" orient="auto">'
        '<path d="M0,0 L9,4.5 L0,9 Z" fill="#2563eb"/>'
        '</marker>'
        '</defs>'
    )

    partes.append(
        '<rect width="100%" height="100%" fill="white"/>'
    )

    partes.append(
        elemento_svg(
            "text",
            {
                "x": ancho / 2,
                "y": 30,
                "text_anchor": "middle",
                "font_family": "Arial",
                "font_size": 18,
                "font_weight": "bold",
                "fill": "#17365d"
            },
            escape(titulo)
        )
    )

    x_inicial, y_inicial = posiciones[inicial]

    partes.append(
        f'<path d="M{x_inicial - 65},{y_inicial} '
        f'L{x_inicial - radio - 3},{y_inicial}" '
        'stroke="#2563eb" stroke-width="2" '
        'fill="none" marker-end="url(#flecha)"/>'
    )

    for transicion in transiciones:
        origen = transicion["origen"]
        destino = transicion["destino"]
        etiqueta = transicion["etiqueta"]

        x1, y1 = posiciones[origen]
        x2, y2 = posiciones[destino]

        if origen == destino:
            camino = (
                f"M{x1 - 16},{y1 - 20} "
                f"C{x1 - 60},{y1 - 105} "
                f"{x1 + 60},{y1 - 105} "
                f"{x1 + 16},{y1 - 20}"
            )

            texto_x = x1
            texto_y = y1 - 92

        elif x2 > x1:
            camino = (
                f"M{x1 + radio},{y1} "
                f"L{x2 - radio - 3},{y2}"
            )

            texto_x = (x1 + x2) / 2
            texto_y = y1 - 13

        else:
            camino = (
                f"M{x1},{y1 + radio} "
                f"Q{(x1 + x2) / 2},{y1 + 95} "
                f"{x2},{y2 + radio}"
            )

            texto_x = (x1 + x2) / 2
            texto_y = y1 + 73

        partes.append(
            f'<path d="{camino}" fill="none" '
            'stroke="#2563eb" stroke-width="2" '
            'marker-end="url(#flecha)"/>'
        )

        partes.append(
            elemento_svg(
                "text",
                {
                    "x": texto_x,
                    "y": texto_y,
                    "text_anchor": "middle",
                    "font_family": "Arial",
                    "font_size": 12,
                    "fill": "#17365d"
                },
                escape(etiqueta)
            )
        )

    for estado in estados:
        x, y = posiciones[estado]
        es_final = estado in finales

        partes.append(
            elemento_svg(
                "circle",
                {
                    "cx": x,
                    "cy": y,
                    "r": radio,
                    "fill": "#dcfce7" if es_final else "#eff6ff",
                    "stroke": "#15803d" if es_final else "#17365d",
                    "stroke_width": 2
                }
            )
        )

        if es_final:
            partes.append(
                elemento_svg(
                    "circle",
                    {
                        "cx": x,
                        "cy": y,
                        "r": radio - 5,
                        "fill": "none",
                        "stroke": "#15803d",
                        "stroke_width": 2
                    }
                )
            )

        partes.append(
            elemento_svg(
                "text",
                {
                    "x": x,
                    "y": y + 5,
                    "text_anchor": "middle",
                    "font_family": "Arial",
                    "font_size": 13,
                    "font_weight": "bold",
                    "fill": "#17365d"
                },
                escape(nombre_estado(estado))
            )
        )

    partes.append(
        elemento_svg(
            "text",
            {
                "x": ancho / 2,
                "y": alto - 20,
                "text_anchor": "middle",
                "font_family": "Arial",
                "font_size": 12,
                "fill": "#64748b"
            },
            "Los estados con doble círculo son estados de aceptación."
        )
    )

    partes.append("</svg>")

    destino_archivo = Path(archivo)
    destino_archivo.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    destino_archivo.write_text(
        "\n".join(partes),
        encoding="utf-8"
    )

    return str(destino_archivo)


if __name__ == "__main__":
    from analizadores.automatas import (
        construir_afnd_dni,
        convertir_afnd_a_afd
    )

    from analizadores.patrones import (
        construir_afnd_campo,
        construir_afd_campo
    )

    carpeta = Path("ejemplos")

    afnd_dni = construir_afnd_dni()
    afd_dni = convertir_afnd_a_afd(afnd_dni)

    generar_svg(
        afnd_dni,
        "AFND del DNI",
        carpeta / "afnd_dni.svg",
        es_afnd=True
    )

    generar_svg(
        afd_dni,
        "AFD del DNI",
        carpeta / "afd_dni.svg"
    )

    for campo in ("NOMBRE", "INSTITUCION", "PUESTO"):
        afnd = construir_afnd_campo(campo)
        afd = construir_afd_campo(campo)

        generar_svg(
            afnd,
            f"AFND de {campo}",
            carpeta / f"afnd_{campo.lower()}.svg",
            es_afnd=True
        )

        generar_svg(
            afd,
            f"AFD de {campo}",
            carpeta / f"afd_{campo.lower()}.svg"
        )

        print(f"Gráficos generados: {campo}")

    print("Gráficos generados: DNI")
    print("Proceso completado")
