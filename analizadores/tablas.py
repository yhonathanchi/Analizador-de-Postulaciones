
import re

from analizadores.automatas import (
    construir_afnd_dni,
    construir_afnd_token,
    convertir_afnd_a_afd,
    reconocer_afd,
    TOKENS_RESERVADOS
)

from analizadores.patrones import construir_afnd_campo
from analizadores.correo import construir_afnd_correo
from analizadores.lexico import PATRONES


CAMPOS = (
    "DNI",
    "CORREO",
    "NOMBRE",
    "INSTITUCION",
    "PUESTO"
)

TOKENS = tuple(TOKENS_RESERVADOS.keys())

EXPRESIONES = {
    campo: PATRONES[campo]
    for campo in CAMPOS
}

EXPRESIONES.update({
    token: (
        "(?:" +
        "|".join(
            re.escape(lexema)
            for lexema in lexemas
        ) +
        ")"
    )
    for token, lexemas in TOKENS_RESERVADOS.items()
})


def construir_automatas(campo):
    campo = campo.upper().strip()

    if campo in TOKENS:
        afnd = construir_afnd_token(campo)

    elif campo == "DNI":
        afnd = construir_afnd_dni()

    elif campo == "CORREO":
        afnd = construir_afnd_correo()

    elif campo in CAMPOS:
        afnd = construir_afnd_campo(campo)

    else:
        raise ValueError(
            f"Campo o token no reconocido: {campo}"
        )

    afd = convertir_afnd_a_afd(afnd)

    return afnd, afd


def obtener_tabla_afnd(afnd):
    tabla = []

    estados = sorted(afnd["Q"])

    for estado in estados:
        transiciones_estado = []

        for (origen, simbolo), destinos in afnd["delta"].items():
            if origen != estado:
                continue

            transiciones_estado.append({
                "simbolo": simbolo,
                "destinos": sorted(destinos)
            })

        transiciones_estado.sort(
            key=lambda item: str(item["simbolo"])
        )

        tabla.append({
            "estado": f"q{estado}",
            "inicial": estado == afnd["q0"],
            "final": estado in afnd["F"],
            "transiciones": transiciones_estado
        })

    return tabla


def obtener_tabla_afd(afd):
    tabla = []

    estados = sorted(
        afd["Q"],
        key=lambda estado: int(estado[1:])
    )

    for estado in estados:
        transiciones_estado = []

        for simbolo in sorted(afd["Sigma"]):
            destino = afd["delta"].get(
                (estado, simbolo)
            )

            if destino is not None:
                transiciones_estado.append({
                    "simbolo": simbolo,
                    "destino": destino
                })

        tabla.append({
            "estado": estado,
            "inicial": estado == afd["q0"],
            "final": estado in afd["F"],
            "transiciones": transiciones_estado,
            "subconjunto": afd.get(
                "conjuntos", {}
            ).get(estado, [])
        })

    return tabla


def obtener_quintupla(automata, tipo):
    tipo = tipo.upper()

    if tipo not in ("AFND", "AFD"):
        raise ValueError(
            "El tipo debe ser AFND o AFD"
        )

    if tipo == "AFND":
        transiciones = {
            (origen, simbolo): sorted(destinos)
            for (origen, simbolo), destinos
            in automata["delta"].items()
        }
    else:
        transiciones = dict(
            automata["delta"]
        )

    return {
        "Q": sorted(
            automata["Q"],
            key=lambda estado: (
                int(estado[1:])
                if isinstance(estado, str)
                and estado.startswith("q")
                else estado
            )
        ),
        "Sigma": sorted(automata["Sigma"]),
        "delta": transiciones,
        "q0": automata["q0"],
        "F": sorted(
            automata["F"],
            key=lambda estado: (
                int(estado[1:])
                if isinstance(estado, str)
                and estado.startswith("q")
                else estado
            )
        )
    }


def validar_con_automata(campo, valor):
    campo = campo.upper().strip()

    _, afd = construir_automatas(campo)

    return reconocer_afd(
        afd,
        valor
    )


def obtener_informacion_campo(campo):
    campo = campo.upper().strip()

    afnd, afd = construir_automatas(campo)

    return {
        "campo": campo,
        "expresion_regular": EXPRESIONES[campo],
        "afnd": {
            "quintupla": obtener_quintupla(
                afnd,
                "AFND"
            ),
            "tabla": obtener_tabla_afnd(afnd)
        },
        "afd": {
            "quintupla": obtener_quintupla(
                afd,
                "AFD"
            ),
            "tabla": obtener_tabla_afd(afd)
        }
    }


if __name__ == "__main__":
    ejemplos = {
        "DNI": "12345678",
        "CORREO": "juan@gmail.com",
        "NOMBRE": "Juan Perez",
        "INSTITUCION": "Universidad de Lima",
        "PUESTO": "Asistente administrativo",
        "TK_SECCION": "DATOS_PERSONALES",
        "TK_CAMPO": "NOMBRE",
        "TK_ABRE": "{",
        "TK_CIERRA": "}",
        "TK_DOS_PUNTOS": ":"
    }

    for campo, ejemplo in ejemplos.items():
        informacion = obtener_informacion_campo(campo)
        afnd, afd = construir_automatas(campo)

        resultado = validar_con_automata(
            campo,
            ejemplo
        )

        print("\n" + "=" * 50)
        print("CAMPO O TOKEN:", campo)
        print("=" * 50)

        print(
            "Expresion regular:",
            informacion["expresion_regular"]
        )

        print("\nAFND")
        print("Estados:", len(afnd["Q"]))
        print("Alfabeto:", sorted(afnd["Sigma"]))
        print("Estado inicial:", afnd["q0"])
        print("Estados finales:", sorted(afnd["F"]))
        print("Transiciones:", len(afnd["delta"]))

        print("\nAFD")
        print("Estados:", len(afd["Q"]))
        print("Alfabeto:", sorted(afd["Sigma"]))
        print("Estado inicial:", afd["q0"])
        print("Estados finales:", sorted(afd["F"]))
        print("Transiciones:", len(afd["delta"]))

        print("\nPRUEBA")
        print(
            repr(ejemplo),
            "=>",
            "ACEPTADO" if resultado else "RECHAZADO"
        )
