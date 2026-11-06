
import re
import unicodedata


CAMPOS_REQUERIDOS = (
    "NOMBRE",
    "DNI",
    "CORREO",
    "INSTITUCION",
    "PUESTO"
)

SECCIONES = (
    (
        "DATOS_PERSONALES",
        ("NOMBRE", "DNI", "CORREO")
    ),
    (
        "EDUCACION",
        ("INSTITUCION",)
    ),
    (
        "EXPERIENCIA",
        ("PUESTO",)
    )
)


def normalizar_clave(clave):
    valor = unicodedata.normalize(
        "NFD",
        clave.strip().upper()
    )

    valor = "".join(
        caracter
        for caracter in valor
        if unicodedata.category(caracter) != "Mn"
    )

    return re.sub(r"\s+", "_", valor)


def construir_dsl(datos):
    lineas = []

    for seccion, campos in SECCIONES:
        if lineas:
            lineas.append("")

        lineas.append(f"{seccion} {{")

        for campo in campos:
            lineas.append(
                f"{campo}: {datos[campo]}"
            )

        lineas.append("}")

    return "\n".join(lineas)


def procesar_campos(datos):
    errores = []
    salida = {}

    for campo in CAMPOS_REQUERIDOS:
        valor = datos.get(campo, "")

        if not isinstance(valor, str):
            errores.append(
                f"El campo {campo} tiene un valor inválido."
            )
            continue

        valor = valor.strip()

        if not valor:
            errores.append(
                f"Falta completar el campo obligatorio {campo}."
            )

        elif "\n" in valor or "\r" in valor:
            errores.append(
                f"El campo {campo} debe ocupar una sola línea."
            )

        else:
            salida[campo] = valor

    if errores:
        return None, errores

    return construir_dsl(salida), []


def procesar_plantilla_txt(contenido):
    datos = {}
    errores = []

    encabezados = {
        seccion
        for seccion, _ in SECCIONES
    }

    for numero, linea in enumerate(
        contenido.splitlines(),
        start=1
    ):
        linea = linea.strip()

        if not linea:
            continue

        clave_normal = normalizar_clave(
            linea.removesuffix(":").strip()
        )

        es_encabezado = (
            clave_normal in encabezados
            or (
                linea.startswith("[")
                and linea.endswith("]")
                and normalizar_clave(
                    linea[1:-1]
                ) in encabezados
            )
        )

        if es_encabezado:
            continue

        if ":" not in linea:
            errores.append(
                f"Línea {numero}: se esperaba CAMPO: valor."
            )
            continue

        clave, valor = linea.split(":", 1)
        campo = normalizar_clave(clave)

        if campo not in CAMPOS_REQUERIDOS:
            errores.append(
                f"Línea {numero}: campo desconocido '{clave.strip()}'."
            )

        elif campo in datos:
            errores.append(
                f"Línea {numero}: el campo {campo} está duplicado."
            )

        else:
            datos[campo] = valor.strip()

    dsl, errores_campos = procesar_campos(datos)
    errores.extend(errores_campos)

    if errores:
        return None, errores

    return dsl, []


PLANTILLA_EJEMPLO = """DATOS PERSONALES
NOMBRE: Juan Perez
DNI: 12345678
CORREO: juan@gmail.com

EDUCACION
INSTITUCION: Universidad de Lima

EXPERIENCIA
PUESTO: Asistente administrativo
"""


PLANTILLA_VACIA = """DATOS PERSONALES
NOMBRE:
DNI:
CORREO:

EDUCACION
INSTITUCION:

EXPERIENCIA
PUESTO:
"""
