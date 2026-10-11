# Importamos las herramientas necesarias de Flask
from flask import Flask, render_template, request, send_from_directory

# Importamos nuestro analizador léxico
from analizadores.lexico import analizar_lexico

# Creamos la aplicación Flask
app = Flask(__name__)


# Ruta para mostrar el archivo CSS
@app.route("/style.css")
def estilos():
    return send_from_directory("public", "style.css")


# Ruta principal de nuestra plataforma
@app.route("/", methods=["GET", "POST"])
def inicio():

    tokens = []
    errores = []
    analizado = False
    nombre_archivo = ""

    # Cuando el usuario presiona Analizar postulación
    if request.method == "POST":

        archivo = request.files.get("archivo")

        # Verificamos que haya seleccionado un archivo
        if archivo is None or archivo.filename == "":
            errores.append("Debes seleccionar un archivo .txt.")

        # Verificamos la extensión
        elif not archivo.filename.lower().endswith(".txt"):
            errores.append("Solo se permiten archivos .txt.")

        else:
            try:
                # Leemos el archivo sin guardarlo permanentemente
                contenido = archivo.read().decode("utf-8-sig")

                # Ejecutamos el analizador léxico
                tokens, errores = analizar_lexico(contenido)

                analizado = True
                nombre_archivo = archivo.filename

            except UnicodeDecodeError:
                errores.append(
                    "El archivo debe estar guardado en formato UTF-8."
                )

    # Enviamos los resultados a nuestra página HTML
    return render_template(
        "index.html",
        tokens=tokens,
        errores=errores,
        analizado=analizado,
        nombre_archivo=nombre_archivo
    )


# Ejecutamos Flask en nuestra computadora
if __name__ == "__main__":
    app.run(debug=True, port=5001)