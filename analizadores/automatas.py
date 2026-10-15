
from collections import deque

DIGITOS = tuple("0123456789")
EPSILON = "ε"


def construir_afnd_dni():
    estados = set(range(17))
    transiciones = {}

    for i in range(8):
        transiciones[(2 * i, EPSILON)] = {2 * i + 1}

        for digito in DIGITOS:
            transiciones[(2 * i + 1, digito)] = {2 * i + 2}

    return {
        "Q": estados,
        "Sigma": set(DIGITOS),
        "delta": transiciones,
        "q0": 0,
        "F": {16}
    }


def cerradura_epsilon(estados, transiciones):
    resultado = set(estados)
    pendientes = list(estados)

    while pendientes:
        actual = pendientes.pop()

        for destino in transiciones.get((actual, EPSILON), set()):
            if destino not in resultado:
                resultado.add(destino)
                pendientes.append(destino)

    return frozenset(resultado)


def mover(estados, simbolo, transiciones):
    resultado = set()

    for estado in estados:
        resultado.update(transiciones.get((estado, simbolo), set()))

    return resultado


def convertir_afnd_a_afd(afnd):
    inicial = cerradura_epsilon({afnd["q0"]}, afnd["delta"])

    nombres = {inicial: "q0"}
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
            alcanzables = mover(conjunto, simbolo, afnd["delta"])
            destino = cerradura_epsilon(alcanzables, afnd["delta"])

            if destino not in nombres:
                nombres[destino] = f"q{len(nombres)}"
                cola.append(destino)

            transiciones[(nombre, simbolo)] = nombres[destino]

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

        estado = afd["delta"][(estado, simbolo)]

    return estado in afd["F"]


def mostrar_afnd(afnd):
    print("\n=== AFND DEL DNI ===")
    print("Q =", sorted(afnd["Q"]))
    print("Sigma =", sorted(afnd["Sigma"]))
    print("q0 =", afnd["q0"])
    print("F =", sorted(afnd["F"]))

    print("\nTABLA DE TRANSICIONES DEL AFND")
    print("Estado | ε | 0-9")

    for estado in sorted(afnd["Q"]):
        epsilon = afnd["delta"].get((estado, EPSILON), set())
        digitos = afnd["delta"].get((estado, "0"), set())

        print(
            estado,
            "|",
            sorted(epsilon),
            "|",
            sorted(digitos)
        )


def mostrar_afd(afd):
    print("\n=== AFD DEL DNI ===")
    print("Q =", sorted(afd["Q"], key=lambda x: int(x[1:])))
    print("Sigma =", sorted(afd["Sigma"]))
    print("q0 =", afd["q0"])
    print("F =", sorted(afd["F"]))

    print("\nESTADOS OBTENIDOS POR SUBCONJUNTOS")

    for nombre, estados in afd["conjuntos"].items():
        print(nombre, "=", estados)

    print("\nTABLA DE TRANSICIONES DEL AFD")
    print("Estado | 0-9")

    for estado in sorted(afd["Q"], key=lambda x: int(x[1:])):
        print(estado, "|", afd["delta"][(estado, "0")])


if __name__ == "__main__":
    afnd = construir_afnd_dni()
    afd = convertir_afnd_a_afd(afnd)

    mostrar_afnd(afnd)
    mostrar_afd(afd)

    print("\n=== PRUEBAS ===")

    ejemplos = [
        "12345678",
        "87654321",
        "1234567",
        "123456789",
        "1234ABCD",
        ""
    ]

    for ejemplo in ejemplos:
        resultado = reconocer_afd(afd, ejemplo)
        print(repr(ejemplo), "=>", "ACEPTADO" if resultado else "RECHAZADO")
