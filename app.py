
import re
from flask import Flask, render_template, request, send_from_directory, jsonify, Response
from analizadores.lexico import analizar_lexico, PATRONES
from analizadores.tablas import CAMPOS, TOKENS, construir_automatas, EXPRESIONES
from analizadores.sintactico import analizar_sintactico
from analizadores.traductor import traducir_json
from analizadores.plantilla import CAMPOS_REQUERIDOS, procesar_campos, procesar_plantilla_txt, PLANTILLA_VACIA


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


def reentrada_dsl(contenido):
    return bool(re.search(r"(?m)^\s*(?:DATOS_PERSONALES|EDUCACION|EXPERIENCIA)\s*\{", contenido))


ORDEN_CAMPOS = ["DNI", "CORREO", "NOMBRE", "INSTITUCION", "PUESTO"]

OPCIONES_AUTOMATAS = ORDEN_CAMPOS + list(TOKENS)

EJEMPLOS = {
    "DNI": "12345678",
    "CORREO": "juan@gmail.com",
    "NOMBRE": "Juan Perez",
    "INSTITUCION": "Universidad de Lima",
    "PUESTO": "Asistente administrativo"
}

DESCRIPCIONES = {
    "DNI": "Exactamente ocho dígitos",
    "CORREO": "Formato básico de correo electrónico",
    "NOMBRE": "Letras y espacios",
    "INSTITUCION": "Letras, números y signos permitidos",
    "PUESTO": "Descripción del puesto laboral"
}


def nombre_estado(estado):
    if isinstance(estado, int):
        return f"q{estado}"
    return str(estado)


def clave_estado(estado):
    nombre = nombre_estado(estado)

    if nombre.startswith("q") and nombre[1:].isdigit():
        return 0, int(nombre[1:])

    return 1, nombre


def convertir_a_json(automata, tipo, campo):
    estados = sorted(
        automata["Q"],
        key=clave_estado
    )

    es_afnd = tipo == "afnd"
    transiciones = []

    for (origen, simbolo), destinos in automata["delta"].items():
        if es_afnd and isinstance(
            destinos,
            (set, frozenset, list, tuple)
        ):
            lista_destinos = destinos
        else:
            lista_destinos = [destinos]

        if simbolo is None or str(simbolo).lower() in (
            "",
            "epsilon",
            "eps",
            "ε"
        ):
            simbolo_texto = "ε"
        else:
            simbolo_texto = str(simbolo)

        for destino in lista_destinos:
            if destino is None:
                continue

            transiciones.append({
                "origen": nombre_estado(origen),
                "simbolo": simbolo_texto,
                "destino": nombre_estado(destino)
            })

    transiciones.sort(
        key=lambda t: (
            clave_estado(t["origen"]),
            clave_estado(t["destino"]),
            t["simbolo"]
        )
    )

    return {
        "titulo": f"{tipo.upper()} de {campo}",
        "tipo": tipo.upper(),
        "campo": campo,
        "expresion": EXPRESIONES[campo],
        "estados": [
            nombre_estado(estado)
            for estado in estados
        ],
        "alfabeto": sorted(
            str(simbolo)
            for simbolo in automata["Sigma"]
        ),
        "inicial": nombre_estado(
            automata["q0"]
        ),
        "finales": [
            nombre_estado(estado)
            for estado in sorted(
                automata["F"],
                key=clave_estado
            )
        ],
        "transiciones": transiciones
    }


@app.route("/style.css")
def estilos():
    return send_from_directory(
        "public",
        "style.css"
    )


@app.route("/automatas.js")
def javascript_automatas():
    return send_from_directory(
        "public",
        "automatas.js",
        mimetype="text/javascript"
    )


@app.route("/api/automatas/<campo>/<tipo>")
def api_automata(campo, tipo):
    campo = campo.upper().strip()
    tipo = tipo.lower().strip()

    if campo not in OPCIONES_AUTOMATAS:
        return jsonify({
            "error": "Campo o token no reconocido"
        }), 404

    if tipo not in ("afnd", "afd"):
        return jsonify({
            "error": "Tipo de automata no reconocido"
        }), 404

    afnd, afd = construir_automatas(campo)

    automata = (
        afnd
        if tipo == "afnd"
        else afd
    )

    return jsonify(
        convertir_a_json(
            automata,
            tipo,
            campo
        )
    )


@app.route("/descargar-plantilla")
def descargar_plantilla():
    return Response(
        PLANTILLA_VACIA,
        mimetype="text/plain; charset=utf-8",
        headers={
            "Content-Disposition":
                "attachment; filename=plantilla_postulacion.txt"
        }
    )


@app.route("/", methods=["GET", "POST"])
def inicio():
    tokens = []
    errores = []
    sintaxis = None
    salida_json = None
    analizado = False
    nombre_archivo = ""
    contenido_ingresado = ""
    modo_actual = "plantilla"

    datos_plantilla = {
        campo: ""
        for campo in CAMPOS_REQUERIDOS
    }

    dsl_generado = None

    campo_actual = request.values.get(
        "campo",
        "DNI"
    ).upper()

    if campo_actual not in OPCIONES_AUTOMATAS:
        campo_actual = "DNI"

    if request.method == "POST":
        modo_actual = request.form.get(
            "modo",
            "plantilla"
        )

        contenido = None

        if modo_actual == "plantilla":
            datos_plantilla = {
                campo: request.form.get(campo, "")
                for campo in CAMPOS_REQUERIDOS
            }

            contenido, errores_formulario = procesar_campos(
                datos_plantilla
            )

            errores.extend(
                errores_formulario
            )

            nombre_archivo = "Plantilla web de postulación"

        elif modo_actual == "archivo":
            archivo = request.files.get(
                "archivo"
            )

            if archivo is None or not archivo.filename:
                errores.append(
                    "Selecciona un archivo .txt de la plantilla."
                )

            elif not archivo.filename.lower().endswith(".txt"):
                errores.append(
                    "Solo se admiten archivos .txt; no se extraen datos de CV en PDF o Word."
                )

            else:
                try:
                    original = archivo.read().decode(
                        "utf-8-sig"
                    )

                    nombre_archivo = archivo.filename

                    if reentrada_dsl(original):
                        contenido = original

                    else:
                        contenido, errores_plantilla = procesar_plantilla_txt(
                            original
                        )

                        errores.extend(
                            errores_plantilla
                        )

                except UnicodeDecodeError:
                    errores.append(
                        "El archivo debe tener codificación UTF-8."
                    )

        elif modo_actual == "texto":
            contenido_ingresado = request.form.get(
                "contenido",
                ""
            )

            contenido = contenido_ingresado

            nombre_archivo = "DSL ingresado manualmente"

            if not contenido.strip():
                errores.append(
                    "Escribe una postulación en el lenguaje DSL."
                )

        else:
            errores.append(
                "Modalidad de ingreso no válida."
            )

            modo_actual = "plantilla"

        if contenido is not None:
            dsl_generado = contenido

        if not errores and contenido is not None:
            tokens, errores_lexicos = analizar_lexico(
                contenido
            )

            errores.extend(
                errores_lexicos
            )

            analizado = True

            if not errores:
                sintaxis = analizar_sintactico(
                    tokens
                )

                if sintaxis["valido"]:
                    salida_json = traducir_json(
                        tokens
                    )

    reglas = [
        {
            "campo": campo,
            "expresion": PATRONES[campo],
            "ejemplo": EJEMPLOS[campo],
            "descripcion": DESCRIPCIONES[campo]
        }
        for campo in ORDEN_CAMPOS
    ]

    agrupadores = [
        (
            "TK_SECCION",
            "DATOS_PERSONALES, EDUCACION, EXPERIENCIA",
            "Secciones"
        ),
        (
            "TK_CAMPO",
            "NOMBRE, DNI, CORREO, INSTITUCION, PUESTO",
            "Identificadores"
        ),
        (
            "TK_ABRE",
            "{",
            "Delimitador"
        ),
        (
            "TK_CIERRA",
            "}",
            "Delimitador"
        ),
        (
            "TK_DOS_PUNTOS",
            ":",
            "Separador"
        ),
        (
            "TK_DNI",
            "Valores de ocho dígitos",
            "Valor numérico"
        ),
        (
            "TK_CORREO",
            "Valores de correo",
            "Valor"
        ),
        (
            "TK_TEXTO",
            "Valores de texto",
            "Valor"
        )
    ]

    tokens_agrupados = [
        {
            "token": token,
            "definicion": definicion,
            "funcion": funcion,
            "cantidad": sum(
                t["token"] == token
                for t in tokens
            ),
            "lexemas": list(
                dict.fromkeys(
                    t["lexema"]
                    for t in tokens
                    if t["token"] == token
                )
            )
        }
        for token, definicion, funcion in agrupadores
    ]

    return render_template(
        "index.html",
        tokens=tokens,
        datos_plantilla=datos_plantilla,
        dsl_generado=dsl_generado,
        tokens_agrupados=tokens_agrupados,
        sintaxis=sintaxis,
        salida_json=salida_json,
        errores=errores,
        analizado=analizado,
        nombre_archivo=nombre_archivo,
        contenido_ingresado=contenido_ingresado,
        modo_actual=modo_actual,
        campo_actual=campo_actual,
        campos=OPCIONES_AUTOMATAS,
        reglas=reglas,
        expresion_actual=EXPRESIONES[campo_actual]
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )
