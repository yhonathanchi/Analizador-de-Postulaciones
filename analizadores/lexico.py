import re

SECCIONES = {
    "DATOS_PERSONALES",
    "EDUCACION",
    "EXPERIENCIA"
}

CAMPOS = {
    "NOMBRE",
    "DNI",
    "CORREO",
    "INSTITUCION",
    "PUESTO"
}

PATRONES = {
    "DNI": r"[0-9]{8}",
    "CORREO": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "NOMBRE": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+",
    "INSTITUCION": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+",
    "PUESTO": r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9 .,-]+"
}


def analizar_lexico(contenido):
    tokens = []
    errores = []

    for numero_linea, linea in enumerate(
        contenido.splitlines(), start=1
    ):
        linea = linea.strip()

        if not linea:
            continue

        if linea in SECCIONES:
            tokens.append({
                "token": "TK_SECCION",
                "lexema": linea,
                "linea": numero_linea
            })
            continue

        if linea in ("{", "}"):
            tokens.append({
                "token": "TK_ABRE" if linea == "{" else "TK_CIERRA",
                "lexema": linea,
                "linea": numero_linea
            })
            continue

        if linea.endswith("{") and linea[:-1].strip() in SECCIONES:
            seccion = linea[:-1].strip()

            tokens.append({
                "token": "TK_SECCION",
                "lexema": seccion,
                "linea": numero_linea
            })

            tokens.append({
                "token": "TK_ABRE",
                "lexema": "{",
                "linea": numero_linea
            })
            continue

        if ":" in linea:
            campo, valor = linea.split(":", 1)
            campo = campo.strip()
            valor = valor.strip()

            if campo not in CAMPOS:
                errores.append(
                    f"Línea {numero_linea}: campo desconocido '{campo}'"
                )
                continue

            if not re.fullmatch(PATRONES[campo], valor):
                errores.append(
                    f"Línea {numero_linea}: formato inválido para {campo}"
                )
                continue

            tokens.append({
                "token": "TK_CAMPO",
                "lexema": campo,
                "linea": numero_linea
            })

            tokens.append({
                "token": "TK_DOS_PUNTOS",
                "lexema": ":",
                "linea": numero_linea
            })

            tipo_valor = (
                "TK_DNI" if campo == "DNI"
                else "TK_CORREO" if campo == "CORREO"
                else "TK_TEXTO"
            )

            tokens.append({
                "token": tipo_valor,
                "lexema": valor,
                "linea": numero_linea
            })
            continue

        errores.append(
            f"Línea {numero_linea}: contenido no reconocido '{linea}'"
        )

    return tokens, errores