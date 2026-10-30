
from flask import Flask, render_template, request, send_from_directory, jsonify
from analizadores.lexico import analizar_lexico, PATRONES
from analizadores.tablas import CAMPOS, construir_automatas


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

ORDEN_CAMPOS = ["DNI", "CORREO", "NOMBRE", "INSTITUCION", "PUESTO"]

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
    estados = sorted(automata["Q"], key=clave_estado)
    es_afnd = tipo == "afnd"

    transiciones = []

    for (origen, simbolo), destinos in automata["delta"].items():
        if es_afnd and isinstance(destinos, (set, frozenset, list, tuple)):
            lista_destinos = destinos
        else:
            lista_destinos = [destinos]

        if simbolo is None or str(simbolo).lower() in (
            "", "epsilon", "eps", "ε"
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
        "estados": [nombre_estado(e) for e in estados],
        "alfabeto": sorted(str(s) for s in automata["Sigma"]),
        "inicial": nombre_estado(automata["q0"]),
        "finales": [
            nombre_estado(e)
            for e in sorted(automata["F"], key=clave_estado)
        ],
        "transiciones": transiciones
    }


@app.route("/style.css")
def estilos():
    return send_from_directory("public", "style.css")


@app.route("/automatas.js")
def javascript_automatas():
    return send_from_directory(
        "public",
        "automatas.js",
        mimetype="text/javascript"
    )


@app.route("/api/automatas/<campo>/<tipo>")
def api_automata(campo, tipo):
    campo = campo.upper()
    tipo = tipo.lower()

    if campo not in CAMPOS or tipo not in ("afnd", "afd"):
        return jsonify({"error": "Autómata no encontrado"}), 404

    afnd, afd = construir_automatas(campo)
    automata = afnd if tipo == "afnd" else afd

    return jsonify(convertir_a_json(automata, tipo, campo))


@app.route("/", methods=["GET", "POST"])
def inicio():
    tokens = []
    errores = []
    analizado = False
    nombre_archivo = ""
    contenido_ingresado = ""
    modo_actual = "archivo"

    campo_actual = request.values.get("campo", "DNI").upper()

    if campo_actual not in CAMPOS:
        campo_actual = "DNI"

    if request.method == "POST":
        modo_actual = request.form.get("modo", "archivo")
        contenido = None

        if modo_actual == "archivo":
            archivo = request.files.get("archivo")

            if archivo is None or archivo.filename == "":
                errores.append("Debes seleccionar un archivo .txt.")

            elif not archivo.filename.lower().endswith(".txt"):
                errores.append("Solo se permiten archivos .txt.")

            else:
                try:
                    contenido = archivo.read().decode("utf-8-sig")
                    nombre_archivo = archivo.filename
                except UnicodeDecodeError:
                    errores.append(
                        "El archivo debe estar guardado en formato UTF-8."
                    )

        elif modo_actual == "texto":
            contenido_ingresado = request.form.get("contenido", "")
            contenido = contenido_ingresado

            if not contenido.strip():
                errores.append("Debes escribir una postulación.")
            else:
                nombre_archivo = "Texto ingresado manualmente"

        else:
            errores.append("Modalidad de ingreso no válida.")
            modo_actual = "archivo"

        if not errores and contenido is not None:
            tokens, errores_lexicos = analizar_lexico(contenido)
            errores.extend(errores_lexicos)
            analizado = True

    reglas = [
        {
            "campo": campo,
            "expresion": PATRONES[campo],
            "ejemplo": EJEMPLOS[campo],
            "descripcion": DESCRIPCIONES[campo]
        }
        for campo in ORDEN_CAMPOS
    ]

    return render_template(
        "index.html",
        tokens=tokens,
        errores=errores,
        analizado=analizado,
        nombre_archivo=nombre_archivo,
        contenido_ingresado=contenido_ingresado,
        modo_actual=modo_actual,
        campo_actual=campo_actual,
        campos=ORDEN_CAMPOS,
        reglas=reglas,
        expresion_actual=PATRONES[campo_actual]
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
