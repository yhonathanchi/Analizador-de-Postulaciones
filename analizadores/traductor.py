
import json


def traducir_json(tokens):
    secciones = {
        "DATOS_PERSONALES": {},
        "EDUCACION": {},
        "EXPERIENCIA": {}
    }

    seccion = None

    for indice, token in enumerate(tokens):
        if token["token"] == "TK_SECCION":
            seccion = token["lexema"]

        elif token["token"] == "TK_CAMPO" and seccion is not None:
            valor = tokens[indice + 2]["lexema"]
            secciones[seccion][token["lexema"]] = valor

    return json.dumps(
        secciones,
        ensure_ascii=False,
        indent=2
    )
