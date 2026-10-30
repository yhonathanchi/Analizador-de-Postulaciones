
import random
import re

from analizadores.automatas import reconocer_afd
from analizadores.correo import construir_afd_correo, PATRON_CORREO


def ejecutar_pruebas():
    afd = construir_afd_correo()
    generador = random.Random(2026)

    casos = [
        "juan@gmail.com",
        "maria.lopez@usil.edu.pe",
        "usuario123@empresa.org",
        "juan+test@gmail.com",
        "a@b.co",
        "juan@gmail",
        "juan@gmail.c",
        "juangmail.com",
        "juan@@gmail.com",
        "@gmail.com",
        "juan@.com",
        "juan@gmail.123",
        "",
        "a@b..co",
        "a@b.cóm",
        "usuario con espacios@gmail.com",
        "a@b.com.",
        "a@b.com123",
        "a@b.COM",
        "123@456.pe"
    ]

    alfabeto = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "._%+-@"
    )

    for _ in range(5000):
        longitud = generador.randint(0, 25)
        texto = "".join(
            generador.choice(alfabeto)
            for _ in range(longitud)
        )
        casos.append(texto)

    fallos = []

    for caso in casos:
        esperado = re.fullmatch(
            PATRON_CORREO,
            caso
        ) is not None

        obtenido = reconocer_afd(afd, caso)

        if esperado != obtenido:
            fallos.append((caso, esperado, obtenido))

    print("PRUEBA DE EQUIVALENCIA DEL CORREO")
    print("Casos analizados:", len(casos))
    print("Coincidencias:", len(casos) - len(fallos))
    print("Inconsistencias:", len(fallos))

    for caso, esperado, obtenido in fallos[:20]:
        print(
            repr(caso),
            "Regex:", esperado,
            "AFD:", obtenido
        )

    if fallos:
        raise AssertionError(
            "El AFD no coincide con la expresion regular"
        )

    print("EQUIVALENCIA VERIFICADA EN LOS CASOS PROBADOS")


if __name__ == "__main__":
    ejecutar_pruebas()
