
from collections import deque

DIGITOS = tuple("0123456789")
EPSILON = "ε"

TOKENS_RESERVADOS = {
    "TK_SECCION": (
        "DATOS_PERSONALES",
        "EDUCACION",
        "EXPERIENCIA"
    ),
    "TK_CAMPO": (
        "NOMBRE",
        "DNI",
        "CORREO",
        "INSTITUCION",
        "PUESTO"
    ),
    "TK_LLAVE": ("{", "}"),
    "TK_DOS_PUNTOS": (":",)
}


def construir_afnd_dni():
    transiciones = {
        (0, EPSILON): {1}
    }

    for posicion in range(1, 9):
        for digito in DIGITOS:
            transiciones[(posicion, digito)] = {
                posicion + 1
            }

    return {
        "Q": set(range(10)),
        "Sigma": set(DIGITOS),
        "delta": transiciones,
        "q0": 0,
        "F": {9}
    }


def cerradura_epsilon(estados, transiciones):
    resultado = set(estados)
    pendientes = list(estados)

    while pendientes:
        actual = pendientes.pop()

        for destino in transiciones.get(
            (actual, EPSILON), set()
        ):
            if destino not in resultado:
                resultado.add(destino)
                pendientes.append(destino)

    return frozenset(resultado)


def mover(estados, simbolo, transiciones):
    resultado = set()

    for estado in estados:
        resultado.update(
            transiciones.get(
                (estado, simbolo), set()
            )
        )

    return resultado


def convertir_afnd_a_afd(afnd):
    inicial = cerradura_epsilon(
        {afnd["q0"]},
        afnd["delta"]
    )

    nombres = {
        inicial: "q0"
    }

    cola = deque([inicial])
    transiciones = {}
    finales = set()
    conjuntos = {}

    while cola:
        conjunto = cola.popleft()
        nombre = nombres[conjunto]

        conjuntos[nombre] = sorted(conjunto)

        if conjunto.intersection(afnd["F"]):
            finales.add(nombre)

        for simbolo in sorted(afnd["Sigma"]):
            alcanzables = mover(
                conjunto,
                simbolo,
                afnd["delta"]
            )

            destino = cerradura_epsilon(
                alcanzables,
                afnd["delta"]
            )

            if destino not in nombres:
                nombres[destino] = f"q{len(nombres)}"
                cola.append(destino)

            transiciones[
                (nombre, simbolo)
            ] = nombres[destino]

    return {
        "Q": set(nombres.values()),
        "Sigma": set(afnd["Sigma"]),
        "delta": transiciones,
        "q0": "q0",
        "F": finales,
        "conjuntos": conjuntos
    }


def reconocer_afd(afd, cadena):
    estado = afd["q0"]

    for simbolo in cadena:
        if simbolo not in afd["Sigma"]:
            return False

        estado = afd["delta"][
            (estado, simbolo)
        ]

    return estado in afd["F"]


def construir_afnd_token(token):
    token = token.upper()

    if token not in TOKENS_RESERVADOS:
        raise ValueError(
            f"Token reservado no reconocido: {token}"
        )

    estados = {0}
    alfabeto = set()
    transiciones = {}
    finales = set()
    siguiente_estado = 1

    for lexema in TOKENS_RESERVADOS[token]:
        inicio_rama = siguiente_estado
        siguiente_estado += 1
        estados.add(inicio_rama)

        transiciones.setdefault(
            (0, EPSILON), set()
        ).add(inicio_rama)

        actual = inicio_rama

        for caracter in lexema:
            destino = siguiente_estado
            siguiente_estado += 1

            estados.add(destino)
            alfabeto.add(caracter)

            transiciones.setdefault(
                (actual, caracter), set()
            ).add(destino)

            actual = destino

        finales.add(actual)

    return {
        "Q": estados,
        "Sigma": alfabeto,
        "delta": transiciones,
        "q0": 0,
        "F": finales
    }


def construir_afd_token(token):
    afnd = construir_afnd_token(token)

    return convertir_afnd_a_afd(afnd)


def mostrar_afnd(afnd):
    print("\n=== AFND DEL DNI ===")
    print("Q =", sorted(afnd["Q"]))
    print("Sigma =", sorted(afnd["Sigma"]))
    print("q0 =", afnd["q0"])
    print("F =", sorted(afnd["F"]))

    print("\nTRANSICIONES DEL AFND")

    for (origen, simbolo), destinos in sorted(
        afnd["delta"].items(),
        key=lambda item: (
            item[0][0],
            item[0][1]
        )
    ):
        print(
            f"δ(q{origen}, {simbolo}) = "
            f"{sorted(destinos)}"
        )


def mostrar_afd(afd):
    print("\n=== AFD DEL DNI ===")

    print(
        "Q =",
        sorted(
            afd["Q"],
            key=lambda estado: int(estado[1:])
        )
    )

    print("Sigma =", sorted(afd["Sigma"]))
    print("q0 =", afd["q0"])
    print("F =", sorted(afd["F"]))

    print("\nCONVERSION POR SUBCONJUNTOS")

    for estado, conjunto in sorted(
        afd["conjuntos"].items(),
        key=lambda item: int(item[0][1:])
    ):
        print(estado, "=", conjunto)


if __name__ == "__main__":
    afnd = construir_afnd_dni()
    afd = convertir_afnd_a_afd(afnd)

    mostrar_afnd(afnd)
    mostrar_afd(afd)

    print("\n=== PRUEBAS DE DNI ===")

    ejemplos = [
        "12345678",
        "87654321",
        "1234567",
        "123456789",
        "1234ABCD",
        ""
    ]

    for ejemplo in ejemplos:
        resultado = reconocer_afd(
            afd,
            ejemplo
        )

        print(
            repr(ejemplo),
            "=>",
            "ACEPTADO" if resultado else "RECHAZADO"
        )

    print("\n=== PRUEBAS DE TOKENS RESERVADOS ===")

    for token, lexemas in TOKENS_RESERVADOS.items():
        automata = construir_afd_token(token)

        print(f"\nTOKEN: {token}")
        print("Estados AFD:", len(automata["Q"]))

        for lexema in lexemas:
            resultado = reconocer_afd(
                automata,
                lexema
            )

            print(
                repr(lexema),
                "=>",
                "ACEPTADO" if resultado else "RECHAZADO"
            )
