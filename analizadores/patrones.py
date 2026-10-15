
import re

from analizadores.automatas import (
    EPSILON,
    convertir_afnd_a_afd,
    reconocer_afd
)


LETRAS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "ÁÉÍÓÚáéíóúÑñÜü"
)

DIGITOS = "0123456789"

PATRONES = {
    "NOMBRE": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+",
    "INSTITUCION": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+",
    "PUESTO": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+"
}

ALFABETOS = {
    "NOMBRE": set(LETRAS + " "),
    "INSTITUCION": set(LETRAS + DIGITOS + " .,-"),
    "PUESTO": set(LETRAS + DIGITOS + " .,-")
}


def construir_afnd_campo(campo):
    if campo not in ALFABETOS:
        raise ValueError("Campo no reconocido")

    alfabeto = ALFABETOS[campo]

    transiciones = {
        (0, EPSILON): {1}
    }

    for simbolo in alfabeto:
        transiciones[(1, simbolo)] = {2}
        transiciones[(2, simbolo)] = {2}

    return {
        "Q": {0, 1, 2},
        "Sigma": alfabeto,
        "delta": transiciones,
        "q0": 0,
        "F": {2}
    }


def construir_afd_campo(campo):
    afnd = construir_afnd_campo(campo)
    return convertir_afnd_a_afd(afnd)


def validar_campo(campo, texto):
    if campo not in PATRONES:
        raise ValueError("Campo no reconocido")

    afd = construir_afd_campo(campo)

    resultado_afd = reconocer_afd(afd, texto)
    resultado_regex = re.fullmatch(PATRONES[campo], texto) is not None

    return {
        "campo": campo,
        "texto": texto,
        "aceptado": resultado_afd,
        "coincide_regex": resultado_afd == resultado_regex
    }


if __name__ == "__main__":
    pruebas = {
        "NOMBRE": [
            "Juan Perez",
            "María López",
            "Juan123",
            ""
        ],
        "INSTITUCION": [
            "Universidad de Lima",
            "Instituto 2026",
            "Universidad @ Lima",
            ""
        ],
        "PUESTO": [
            "Asistente administrativo",
            "Analista 2",
            "Desarrollador @ Python",
            ""
        ]
    }

    for campo, ejemplos in pruebas.items():
        afnd = construir_afnd_campo(campo)
        afd = construir_afd_campo(campo)

        print(f"\n=== {campo} ===")
        print("Expresion regular:", PATRONES[campo])
        print("Estados AFND:", len(afnd["Q"]))
        print("Estados AFD:", len(afd["Q"]))

        for ejemplo in ejemplos:
            resultado = validar_campo(campo, ejemplo)

            estado = (
                "ACEPTADO"
                if resultado["aceptado"]
                else "RECHAZADO"
            )

            print(repr(ejemplo), "=>", estado)

            if not resultado["coincide_regex"]:
                raise AssertionError(
                    f"Inconsistencia entre AFD y regex: {campo}"
                )
