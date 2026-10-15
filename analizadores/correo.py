
import re
from pathlib import Path

from analizadores.automatas import (
    EPSILON,
    convertir_afnd_a_afd,
    reconocer_afd
)
from analizadores.graficos import generar_svg


LETRAS = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
)

DIGITOS = set("0123456789")

USUARIO = LETRAS | DIGITOS | set("._%+-")
DOMINIO = LETRAS | DIGITOS | set(".-")

PATRON_CORREO = (
    r"[A-Za-z0-9._%+-]+"
    r"@"
    r"[A-Za-z0-9.-]+"
    r"\."
    r"[A-Za-z]{2,}"
)


def construir_afnd_correo():
    sigma = USUARIO | DOMINIO | LETRAS | {"@"}

    delta = {
        (0, EPSILON): {1}
    }

    for simbolo in USUARIO:
        delta[(1, simbolo)] = {2}
        delta[(2, simbolo)] = {2}

    delta[(2, "@")] = {3}

    for simbolo in DOMINIO:
        delta[(3, simbolo)] = {4}
        delta[(4, simbolo)] = {4}

    delta[(4, ".")].add(5)

    for simbolo in LETRAS:
        delta[(5, simbolo)] = {6}
        delta[(6, simbolo)] = {7}
        delta[(7, simbolo)] = {7}

    return {
        "Q": set(range(8)),
        "Sigma": sigma,
        "delta": delta,
        "q0": 0,
        "F": {7}
    }


def construir_afd_correo():
    afnd = construir_afnd_correo()
    return convertir_afnd_a_afd(afnd)


def validar_correo(correo):
    afd = construir_afd_correo()

    aceptado_afd = reconocer_afd(afd, correo)
    aceptado_regex = re.fullmatch(
        PATRON_CORREO,
        correo
    ) is not None

    return {
        "correo": correo,
        "aceptado": aceptado_afd,
        "coincide_regex": aceptado_afd == aceptado_regex
    }


def generar_graficos_correo():
    carpeta = Path("ejemplos")

    afnd = construir_afnd_correo()
    afd = convertir_afnd_a_afd(afnd)

    generar_svg(
        afnd,
        "AFND del CORREO",
        carpeta / "afnd_correo.svg",
        es_afnd=True
    )

    generar_svg(
        afd,
        "AFD del CORREO",
        carpeta / "afd_correo.svg"
    )

    return afnd, afd


if __name__ == "__main__":
    afnd, afd = generar_graficos_correo()

    print("=== AUTOMATAS DEL CORREO ===")
    print("Expresion regular:", PATRON_CORREO)
    print("Estados AFND:", len(afnd["Q"]))
    print("Estados AFD:", len(afd["Q"]))

    pruebas = [
        ("juan@gmail.com", True),
        ("maria.lopez@usil.edu.pe", True),
        ("usuario123@empresa.org", True),
        ("juan+test@gmail.com", True),
        ("a@b.co", True),
        ("juan@gmail", False),
        ("juan@gmail.c", False),
        ("juangmail.com", False),
        ("juan@@gmail.com", False),
        ("@gmail.com", False),
        ("juan@.com", False),
        ("juan@gmail.123", False),
        ("", False)
    ]

    print("\n=== PRUEBAS ===")

    for correo, esperado in pruebas:
        resultado = validar_correo(correo)

        estado = (
            "ACEPTADO"
            if resultado["aceptado"]
            else "RECHAZADO"
        )

        print(repr(correo), "=>", estado)

        if resultado["aceptado"] != esperado:
            raise AssertionError(
                f"Resultado inesperado: {correo}"
            )

        if not resultado["coincide_regex"]:
            raise AssertionError(
                f"El AFD no coincide con la ER: {correo}"
            )

    print("\nTodas las pruebas fueron correctas.")
    print("Graficos generados:")
    print("ejemplos/afnd_correo.svg")
    print("ejemplos/afd_correo.svg")
