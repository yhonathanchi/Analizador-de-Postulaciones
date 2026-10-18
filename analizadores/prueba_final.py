
import re

from analizadores.automatas import reconocer_afd
from analizadores.tablas import construir_automatas, EXPRESIONES
from analizadores.lexico import analizar_lexico


pruebas = {
    "DNI": [
        "12345678", "00000000", "1234567",
        "123456789", "1234ABCD", ""
    ],
    "CORREO": [
        "juan@gmail.com", "maria@usil.edu.pe",
        "a@b.co", "juan@gmail", "juan@gmail.c",
        "juan@@gmail.com", "juan@.com", ""
    ],
    "NOMBRE": [
        "Juan Perez", "María López", "Ñora",
        "Juan123", "Juan@", ""
    ],
    "INSTITUCION": [
        "Universidad de Lima", "Instituto 2026",
        "Universidad @ Lima", ""
    ],
    "PUESTO": [
        "Asistente administrativo", "Analista 2",
        "Desarrollador @ Python", ""
    ]
}

fallos = []
total = 0

for campo, ejemplos in pruebas.items():
    afnd, afd = construir_automatas(campo)

    for valor in ejemplos:
        total += 1

        esperado = re.fullmatch(
            EXPRESIONES[campo],
            valor
        ) is not None

        obtenido = reconocer_afd(afd, valor)

        if esperado != obtenido:
            fallos.append((campo, valor, esperado, obtenido))

    print(f"{campo}: pruebas ejecutadas")


casos_lexicos = [
    ("DNI: 12345678", True),
    ("DNI: 1234567", False),
    ("CORREO: juan@gmail.com", True),
    ("CORREO: juangmail.com", False),
    ("NOMBRE: Juan Perez", True),
    ("NOMBRE: Juan123", False),
    ("CAMPO_DESCONOCIDO: valor", False)
]

for texto, esperado in casos_lexicos:
    total += 1
    tokens, errores = analizar_lexico(texto)
    obtenido = len(errores) == 0

    if obtenido != esperado:
        fallos.append(("LEXICO", texto, esperado, obtenido))


print(f"\nTotal de pruebas: {total}")
print(f"Fallos: {len(fallos)}")

for fallo in fallos:
    print("ERROR:", fallo)

if fallos:
    raise AssertionError("Se encontraron inconsistencias")

print("TODAS LAS PRUEBAS FUERON CORRECTAS")
