from io import BytesIO

import pytest

from app import app
from analizadores.plantilla import construir_dsl, PLANTILLA_EJEMPLO


DATOS = {
    "NOMBRE": "Juan Perez",
    "DNI": "12345678",
    "CORREO": "juan@gmail.com",
    "INSTITUCION": "Universidad 2026",
    "PUESTO": "Asistente administrativo",
}


@pytest.fixture
def cliente():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_pagina_inicio(cliente):
    r = cliente.get("/")
    assert r.status_code == 200
    assert "Mini compilador" in r.get_data(as_text=True)
    assert 'value="TK_SECCION"' in r.get_data(as_text=True)


def test_postulacion_valida_formulario(cliente):
    r = cliente.post("/", data={"modo": "plantilla", **DATOS})
    texto = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Postulación válida" in texto
    assert "24" in texto
    assert "Universidad 2026" in texto
    assert "Descargar resultado JSON" in texto


def test_dni_invalido_formulario(cliente):
    r = cliente.post("/", data={"modo": "plantilla", **DATOS, "DNI": "1234567"})
    texto = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "formato inválido para DNI" in texto
    assert "Descargar resultado JSON" not in texto


def test_campo_vacio(cliente):
    r = cliente.post("/", data={"modo": "plantilla", **DATOS, "NOMBRE": ""})
    texto = r.get_data(as_text=True)
    assert "Falta completar el campo obligatorio NOMBRE" in texto
    assert "Descargar resultado JSON" not in texto


def test_entrada_dsl_valida(cliente):
    r = cliente.post("/", data={"modo": "texto", "contenido": construir_dsl(DATOS)})
    texto = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Postulación válida" in texto
    assert "Descargar resultado JSON" in texto


def test_entrada_dsl_desordenada(cliente):
    dsl = construir_dsl(DATOS).replace("NOMBRE: Juan Perez\nDNI: 12345678", "DNI: 12345678\nNOMBRE: Juan Perez")
    r = cliente.post("/", data={"modo": "texto", "contenido": dsl})
    texto = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Error sintáctico" in texto
    assert "Descargar resultado JSON" not in texto


def test_plantilla_txt_valida(cliente):
    r = cliente.post("/", data={"modo": "archivo", "archivo": (BytesIO(PLANTILLA_EJEMPLO.encode("utf-8")), "postulacion.txt")}, content_type="multipart/form-data")
    assert r.status_code == 200
    assert "Postulación válida" in r.get_data(as_text=True)


def test_archivo_extension_invalida(cliente):
    r = cliente.post("/", data={"modo": "archivo", "archivo": (BytesIO(b"datos"), "documento.pdf")}, content_type="multipart/form-data")
    assert r.status_code == 200
    assert "Solo se admiten archivos .txt" in r.get_data(as_text=True)


def test_descarga_plantilla(cliente):
    r = cliente.get("/descargar-plantilla")
    assert r.status_code == 200
    assert "attachment" in r.headers.get("Content-Disposition", "")
    assert "NOMBRE:" in r.get_data(as_text=True)


@pytest.mark.parametrize("campo", ["DNI", "CORREO", "TK_SECCION", "TK_CAMPO", "TK_ABRE", "TK_CIERRA", "TK_DOS_PUNTOS"])
@pytest.mark.parametrize("tipo", ["afnd", "afd"])
def test_api_automatas(cliente, campo, tipo):
    r = cliente.get(f"/api/automatas/{campo}/{tipo}")
    assert r.status_code == 200
    data = r.get_json()
    assert data["tipo"] == tipo.upper()
    assert data["inicial"] in data["estados"]
    assert data["transiciones"]


def test_api_automata_desconocido(cliente):
    assert cliente.get("/api/automatas/TK_INVENTADO/afd").status_code == 404