
import re

from analizadores.automatas import (
    EPSILON,
    convertir_afnd_a_afd,
    reconocer_afd
)


LETRAS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
)

DIGITOS = "0123456789"

CARACTERES_USUARIO = set(
    LETRAS + DIGITOS + "._%+-"
)

CARACTERES_DOMINIO = set(
    LETRAS + DIGITOS + ".-"
)

CARACTERES_EXTENSION = set(LETRAS)

ALFABETO = (
    CARACTERES_USUARIO
    | CARACTERES_DOMINIO
    | CARACTERES_EXTENSION
    | {"@"}
)

EXPRESION_CORREO = (
    r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._%+\-]+"
    r"@"
    r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.\-]+"
    r"\."
    r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]{2,}"
)

PATRON_CORREO = EXPRESION_CORREO


def agregar_transicion(transiciones, origen, simbolo, destino):
    clave = (origen, simbolo)

    if clave not in transiciones:
        transiciones[clave] = set()

    transiciones[clave].add(destino)


def construir_afnd_correo():
    transiciones = {}

    agregar_transicion(
        transiciones,
        0,
        EPSILON,
        1
    )

    for simbolo in CARACTERES_USUARIO:
        agregar_transicion(
            transiciones,
            1,
            simbolo,
            2
        )

        agregar_transicion(
            transiciones,
            2,
            simbolo,
            2
        )

    agregar_transicion(
        transiciones,
        2,
        "@",
        3
    )

    for simbolo in CARACTERES_DOMINIO:
        agregar_transicion(
            transiciones,
            3,
            simbolo,
            4
        )

        agregar_transicion(
            transiciones,
            4,
            simbolo,
            4
        )

    agregar_transicion(
        transiciones,
        4,
        ".",
        5
    )

    for simbolo in CARACTERES_EXTENSION:
        agregar_transicion(
            transiciones,
            5,
            simbolo,
            6
        )

        agregar_transicion(
            transiciones,
            6,
            simbolo,
            7
        )

        agregar_transicion(
            transiciones,
            7,
            simbolo,
            7
        )

    return {
        "Q": set(range(8)),
        "Sigma": ALFABETO.copy(),
        "delta": transiciones,
        "q0": 0,
        "F": {7}
    }


def construir_afd_correo():
    afnd = construir_afnd_correo()
    return convertir_afnd_a_afd(afnd)


def reconocer_afnd_correo(cadena):
    afd = construir_afd_correo()
    return reconocer_afd(afd, cadena)


def validar_correo(correo):
    afd = construir_afd_correo()

    resultado_afd = reconocer_afd(
        afd,
        correo
    )

    resultado_regex = (
        re.fullmatch(
            EXPRESION_CORREO,
            correo
        ) is not None
    )

    return {
        "correo": correo,
        "aceptado": resultado_afd,
        "coincide_regex": resultado_afd == resultado_regex
    }


def mostrar_automatas():
    afnd = construir_afnd_correo()
    afd = construir_afd_correo()

    print("\n=== EXPRESION REGULAR ===")
    print(EXPRESION_CORREO)

    print("\n=== AFND DEL CORREO ===")
    print("Q =", sorted(afnd["Q"]))
    print("Sigma =", sorted(afnd["Sigma"]))
    print("q0 =", afnd["q0"])
    print("F =", sorted(afnd["F"]))

    print("\n=== TRANSICIONES DEL AFND ===")

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

    print("\n=== AFD DEL CORREO ===")
    print("Q =", sorted(afd["Q"]))
    print("Sigma =", sorted(afd["Sigma"]))
    print("q0 =", afd["q0"])
    print("F =", sorted(afd["F"]))

    print("\n=== SUBCONJUNTOS ===")

    for estado, conjunto in sorted(
        afd["conjuntos"].items(),
        key=lambda item: int(item[0][1:])
    ):
        print(
            estado,
            "=",
            conjunto
        )

    print("\n=== TRANSICIONES DEL AFD ===")

    for (origen, simbolo), destino in sorted(
        afd["delta"].items(),
        key=lambda item: (
            int(item[0][0][1:]),
            item[0][1]
        )
    ):
        print(
            f"δ({origen}, {simbolo}) = {destino}"
        )


if __name__ == "__main__":
    ejemplos = [
        "juan@gmail.com",
        "maria.lopez@outlook.com",
        "usuario123@universidad.edu",
        "nombre+trabajo@gmail.com",
        "juan@gmail",
        "juan@",
        "@gmail.com",
        "juan@gmail.c",
        "juan gmail.com",
        ""
    ]

    print("\n=== PRUEBAS DE CORREO ===")

    for ejemplo in ejemplos:
        resultado = validar_correo(ejemplo)

        estado = (
            "ACEPTADO"
            if resultado["aceptado"]
            else "RECHAZADO"
        )

        print(
            repr(ejemplo),
            "=>",
            estado
        )

        if not resultado["coincide_regex"]:
            raise AssertionError(
                f"Inconsistencia entre AFD y ER: {ejemplo}"
            )
