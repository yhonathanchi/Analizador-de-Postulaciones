
import re
from functools import lru_cache


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
    "DNI": r"[0123456789]{8}",
    "CORREO": r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._%+\-]+@[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.\-]+\.[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]{2,}",
    "NOMBRE": r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñÜü ]+",
    "INSTITUCION": r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñÜü0123456789 .,]+",
    "PUESTO": r"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóúÑñÜü0123456789 .,]+"
}


@lru_cache(maxsize=5)
def obtener_afd_campo(campo):
    from analizadores.tablas import construir_automatas

    if campo not in CAMPOS:
        raise ValueError(
            f"Campo no reconocido: {campo}"
        )

    _, afd = construir_automatas(campo)

    return afd


@lru_cache(maxsize=5)
def obtener_afd_token(token):
    from analizadores.automatas import construir_afd_token
    from analizadores.automatas import TOKENS_RESERVADOS

    if token not in TOKENS_RESERVADOS:
        raise ValueError(
            f"Token no reconocido: {token}"
        )

    return construir_afd_token(token)


def validar_token_reservado(token, lexema):
    from analizadores.automatas import reconocer_afd

    afd = obtener_afd_token(token)

    return reconocer_afd(
        afd,
        lexema
    )


def validar_valor(campo, valor):
    from analizadores.automatas import reconocer_afd

    if campo not in CAMPOS:
        raise ValueError(
            f"Campo no reconocido: {campo}"
        )

    afd = obtener_afd_campo(campo)

    resultado_afd = reconocer_afd(
        afd,
        valor
    )

    resultado_regex = (
        re.fullmatch(
            PATRONES[campo],
            valor
        ) is not None
    )

    return {
        "campo": campo,
        "valor": valor,
        "aceptado": resultado_afd and resultado_regex,
        "resultado_afd": resultado_afd,
        "resultado_regex": resultado_regex,
        "coinciden": resultado_afd == resultado_regex
    }


def analizar_lexico(contenido):
    tokens = []
    errores = []

    for numero_linea, linea in enumerate(
        contenido.splitlines(),
        start=1
    ):
        linea = linea.strip()

        if not linea:
            continue

        if linea in SECCIONES:
            if validar_token_reservado(
                "TK_SECCION",
                linea
            ):
                tokens.append({
                    "token": "TK_SECCION",
                    "lexema": linea,
                    "linea": numero_linea
                })
                continue

        if linea == "{":
            if validar_token_reservado(
                "TK_ABRE",
                linea
            ):
                tokens.append({
                    "token": "TK_ABRE",
                    "lexema": linea,
                    "linea": numero_linea
                })
                continue

        if linea == "}":
            if validar_token_reservado(
                "TK_CIERRA",
                linea
            ):
                tokens.append({
                    "token": "TK_CIERRA",
                    "lexema": linea,
                    "linea": numero_linea
                })
                continue

        if linea.endswith("{"):
            seccion = linea[:-1].strip()

            if (
                seccion in SECCIONES
                and validar_token_reservado(
                    "TK_SECCION",
                    seccion
                )
                and validar_token_reservado(
                    "TK_ABRE",
                    "{"
                )
            ):
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
            campo, valor = linea.split(
                ":",
                1
            )

            campo = campo.strip()
            valor = valor.strip()

            if (
                campo not in CAMPOS
                or not validar_token_reservado(
                    "TK_CAMPO",
                    campo
                )
            ):
                errores.append(
                    f"Línea {numero_linea}: "
                    f"campo desconocido '{campo}'"
                )
                continue

            if not validar_token_reservado(
                "TK_DOS_PUNTOS",
                ":"
            ):
                errores.append(
                    f"Línea {numero_linea}: "
                    f"separador no reconocido"
                )
                continue

            resultado = validar_valor(
                campo,
                valor
            )

            if not resultado["coinciden"]:
                errores.append(
                    f"Línea {numero_linea}: "
                    f"inconsistencia interna entre "
                    f"el AFD y la expresión regular "
                    f"de {campo}"
                )
                continue

            if not resultado["aceptado"]:
                errores.append(
                    f"Línea {numero_linea}: "
                    f"formato inválido para {campo}"
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
                "TK_DNI"
                if campo == "DNI"
                else "TK_CORREO"
                if campo == "CORREO"
                else "TK_TEXTO"
            )

            tokens.append({
                "token": tipo_valor,
                "lexema": valor,
                "linea": numero_linea
            })

            continue

        errores.append(
            f"Línea {numero_linea}: "
            f"contenido no reconocido '{linea}'"
        )

    return tokens, errores
