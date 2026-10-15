from flask import Flask, render_template, request, send_from_directory
from analizadores.lexico import analizar_lexico

# Inicializamos Flask
app = Flask(__name__)

# Tamaño máximo de solicitud: 1 MB
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


# Archivo CSS
@app.route("/style.css")
def estilos():
    return send_from_directory("public", "style.css")


# Página principal
@app.route("/", methods=["GET", "POST"])
def inicio():

    tokens = []
    errores = []
    analizado = False
    nombre_archivo = ""
    contenido_ingresado = ""
    modo_actual = "archivo"

    if request.method == "POST":

        modo_actual = request.form.get("modo", "archivo")

        contenido = None

        # OPCIÓN 1: ANALIZAR ARCHIVO .TXT
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

        # OPCIÓN 2: ANALIZAR TEXTO DIGITADO
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

        # Ejecutamos el analizador léxico
        if not errores and contenido is not None:

            tokens, errores_lexicos = analizar_lexico(contenido)

            errores.extend(errores_lexicos)

            analizado = True

    return render_template(
        "index.html",
        tokens=tokens,
        errores=errores,
        analizado=analizado,
        nombre_archivo=nombre_archivo,
        contenido_ingresado=contenido_ingresado,
        modo_actual=modo_actual
    )


# Ejecución local
if __name__ == "__main__":
    app.run(debug=True, port=5001)