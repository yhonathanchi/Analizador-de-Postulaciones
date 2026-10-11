from analizadores.lexico import analizar_lexico

contenido = """
DATOS_PERSONALES {
NOMBRE: Juan Perez
DNI: 12345678
CORREO: juan@gmail.com
}

EDUCACION {
INSTITUCION: Universidad de Lima
}

EXPERIENCIA {
PUESTO: Asistente administrativo
}
"""

tokens, errores = analizar_lexico(contenido)

print("=== TOKENS RECONOCIDOS ===")

for token in tokens:
    print(token)

print("\n=== ERRORES LEXICOS ===")

if errores:
    for error in errores:
        print(error)
else:
    print("No se encontraron errores léxicos.")