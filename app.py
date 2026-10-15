
from pathlib import Path
from tempfile import TemporaryDirectory

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    Response
)

from analizadores.lexico import analizar_lexico
from analizadores.tablas import (
    CAMPOS,
    construir_automatas,
    obtener_datos_automatas
)
from analizadores.graficos import generar_svg


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


@app.route("/style.css")
def estilos():
    return send_from_directory("public", "style.css")


@app.route("/automatas/<campo>/<tipo>.svg")
def mostrar_automata(campo, tipo):
    campo = campo.upper()

    if campo not in CAMPOS or tipo not in ("afnd", "afd"):
        return "Autómata no encontrado", 404

    afnd, afd = construir_automatas(campo)
    automata = afnd if tipo == "afnd" else afd

    titulo = f"{tipo.upper()} de {campo}"

    with TemporaryDirectory() as directorio:
        ruta = Path(directorio) / f"{tipo}_{campo.lower()}.svg"

        generar_svg(
            automata,
            titulo,
            ruta,
            es_afnd=(tipo == "afnd")
        )

        contenido_svg = ruta.read_bytes()

    return Response(
        contenido_svg,
        mimetype="image/svg+xml",
        headers={"Cache-Control": "no-cache"}
    )


@app.route("/", methods=["GET", "POST"])
def inicio():
    tokens = []
    errores = []
    analizado = False
    nombre_archivo = ""
    contenido_ingresado = ""
    modo_actual = "archivo"

    campo = request.values.get("campo", "DNI").upper()

    if campo not in CAMPOS:
        campo = "DNI"

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

    datos = obtener_datos_automatas(campo)

    return render_template(
        "index.html",
        tokens=tokens,
        errores=errores,
        analizado=analizado,
        nombre_archivo=nombre_archivo,
        contenido_ingresado=contenido_ingresado,
        modo_actual=modo_actual,
        **datos
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
