
from collections import defaultdict

from analizadores.automatas import (
    EPSILON,
    construir_afnd_dni,
    convertir_afnd_a_afd
)
from analizadores.patrones import (
    construir_afnd_campo,
    PATRONES
)
from analizadores.correo import (
    construir_afnd_correo,
    PATRON_CORREO
)


CAMPOS = ("DNI", "CORREO", "NOMBRE", "INSTITUCION", "PUESTO")

EXPRESIONES = {
    "DNI": r"[0-9]{8}",
    "CORREO": PATRON_CORREO,
    **PATRONES
}


def nombre_estado(estado):
    if isinstance(estado, int):
        return f"q{estado}"
    return str(estado)


def clave_estado(estado):
    nombre = nombre_estado(estado)
    if nombre.startswith("q") and nombre[1:].isdigit():
        return (0, int(nombre[1:]))
    return (1, nombre)


def ordenar_estados(estados):
    return sorted(estados, key=clave_estado)


def conjunto_estados(estados):
    return "{ " + ", ".join(
        nombre_estado(estado)
        for estado in ordenar_estados(estados)
    ) + " }"


def representar_simbolos(simbolos, alfabeto):
    simbolos = set(simbolos)
    alfabeto = set(alfabeto)

    if simbolos == alfabeto and simbolos:
        return "Σ"

    if simbolos == set("0123456789"):
        return "0–9"

    return ", ".join(
        repr(simbolo) for simbolo in sorted(simbolos)
    )


def normalizar_destinos(destinos):
    if destinos is None:
        return set()

    if isinstance(destinos, (set, frozenset, list, tuple)):
        return set(destinos)

    return {destinos}


def construir_automatas(campo):
    if campo not in CAMPOS:
        raise ValueError("Campo no reconocido")

    if campo == "DNI":
        afnd = construir_afnd_dni()
    elif campo == "CORREO":
        afnd = construir_afnd_correo()
    else:
        afnd = construir_afnd_campo(campo)

    afd = convertir_afnd_a_afd(afnd)

    return afnd, afd


def preparar_quintupla(automata):
    alfabeto = sorted(automata["Sigma"])

    return {
        "estados": conjunto_estados(automata["Q"]),
        "alfabeto": "{ " + ", ".join(
            repr(simbolo) for simbolo in alfabeto
        ) + " }",
        "inicial": nombre_estado(automata["q0"]),
        "finales": conjunto_estados(automata["F"]),
        "cantidad": len(automata["Q"])
    }


def preparar_transiciones(automata):
    grupos = defaultdict(set)

    for (origen, simbolo), destinos in automata["delta"].items():
        for destino in normalizar_destinos(destinos):
            grupos[(origen, destino)].add(simbolo)

    filas = []
    alfabeto = automata["Sigma"]

    for (origen, destino), simbolos in sorted(
        grupos.items(),
        key=lambda elemento: (
            clave_estado(elemento[0][0]),
            clave_estado(elemento[0][1])
        )
    ):
        simbolos_normales = set(simbolos) & set(alfabeto)
        simbolos_epsilon = set(simbolos) - set(alfabeto)

        if simbolos_epsilon:
            filas.append({
                "origen": nombre_estado(origen),
                "simbolos": "ε",
                "destino": nombre_estado(destino)
            })

        if simbolos_normales:
            filas.append({
                "origen": nombre_estado(origen),
                "simbolos": representar_simbolos(
                    simbolos_normales,
                    alfabeto
                ),
                "destino": nombre_estado(destino)
            })

    return filas


def obtener_datos_automatas(campo="DNI"):
    if campo not in CAMPOS:
        campo = "DNI"

    afnd, afd = construir_automatas(campo)

    return {
        "campo_actual": campo,
        "campos_disponibles": CAMPOS,
        "expresion_actual": EXPRESIONES[campo],
        "quintupla_afnd": preparar_quintupla(afnd),
        "quintupla_afd": preparar_quintupla(afd),
        "tabla_afnd": preparar_transiciones(afnd),
        "tabla_afd": preparar_transiciones(afd)
    }


if __name__ == "__main__":
    for campo in CAMPOS:
        datos = obtener_datos_automatas(campo)
        print(
            campo,
            "AFND:",
            datos["quintupla_afnd"]["cantidad"],
            "AFD:",
            datos["quintupla_afd"]["cantidad"]
        )
