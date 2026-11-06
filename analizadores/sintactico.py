
GRAMATICA = {
    "S": [
        "DP",
        "ED",
        "EX"
    ],
    "DP": [
        ("TK_SECCION", "DATOS_PERSONALES"),
        ("TK_ABRE", "{"),
        "CN",
        "CD",
        "CC",
        ("TK_CIERRA", "}")
    ],
    "ED": [
        ("TK_SECCION", "EDUCACION"),
        ("TK_ABRE", "{"),
        "CI",
        ("TK_CIERRA", "}")
    ],
    "EX": [
        ("TK_SECCION", "EXPERIENCIA"),
        ("TK_ABRE", "{"),
        "CP",
        ("TK_CIERRA", "}")
    ],
    "CN": [
        ("TK_CAMPO", "NOMBRE"),
        ("TK_DOS_PUNTOS", ":"),
        ("TK_TEXTO", None)
    ],
    "CD": [
        ("TK_CAMPO", "DNI"),
        ("TK_DOS_PUNTOS", ":"),
        ("TK_DNI", None)
    ],
    "CC": [
        ("TK_CAMPO", "CORREO"),
        ("TK_DOS_PUNTOS", ":"),
        ("TK_CORREO", None)
    ],
    "CI": [
        ("TK_CAMPO", "INSTITUCION"),
        ("TK_DOS_PUNTOS", ":"),
        ("TK_TEXTO", None)
    ],
    "CP": [
        ("TK_CAMPO", "PUESTO"),
        ("TK_DOS_PUNTOS", ":"),
        ("TK_TEXTO", None)
    ]
}


def analizar_sintactico(tokens):
    raiz = {
        "simbolo": "S",
        "hijos": []
    }

    pila = [
        ("S", raiz)
    ]

    posicion = 0
    pasos = []

    while pila:
        simbolo, nodo = pila.pop()

        if isinstance(simbolo, str):
            produccion = GRAMATICA[simbolo]
            hijos = []

            for componente in produccion:
                if isinstance(componente, str):
                    etiqueta = componente
                else:
                    etiqueta = componente[1] or componente[0]

                hijo = {
                    "simbolo": etiqueta,
                    "hijos": []
                }

                hijos.append(hijo)

            nodo["hijos"] = hijos

            elementos = list(
                zip(produccion, hijos)
            )

            pila.extend(
                reversed(elementos)
            )

            pasos.append(
                f"Expandir {simbolo}"
            )

            continue

        tipo_esperado, lexema_esperado = simbolo

        if posicion >= len(tokens):
            return {
                "valido": False,
                "mensaje": (
                    "Fin de la entrada: falta "
                    f"{lexema_esperado or tipo_esperado}."
                ),
                "arbol": None,
                "pasos": pasos
            }

        actual = tokens[posicion]

        tipo_actual = actual["token"]
        lexema_actual = actual["lexema"]

        coincide_tipo = (
            tipo_actual == tipo_esperado
        )

        coincide_lexema = (
            lexema_esperado is None
            or lexema_actual == lexema_esperado
        )

        if not coincide_tipo or not coincide_lexema:
            return {
                "valido": False,
                "mensaje": (
                    f"Línea {actual['linea']}: "
                    f"se esperaba "
                    f"{lexema_esperado or tipo_esperado} "
                    f"y se encontró {lexema_actual}."
                ),
                "arbol": None,
                "pasos": pasos
            }

        nodo["simbolo"] = lexema_actual

        pasos.append(
            f"Reconocer {tipo_actual}: {lexema_actual}"
        )

        posicion += 1

    if posicion < len(tokens):
        actual = tokens[posicion]

        return {
            "valido": False,
            "mensaje": (
                f"Línea {actual['linea']}: "
                f"componente adicional "
                f"{actual['lexema']}."
            ),
            "arbol": None,
            "pasos": pasos
        }

    return {
        "valido": True,
        "mensaje": (
            "La postulación cumple el orden "
            "y los campos obligatorios de la gramática."
        ),
        "arbol": raiz,
        "pasos": pasos
    }
