from pathlib import Path
import re
import pytest
from analizadores.lexico import analizar_lexico
from analizadores.tablas import construir_automatas, EXPRESIONES
from analizadores.automatas import reconocer_afd

CASOS = [
    ('DNI', '12345678', True),
    ('DNI', '00000000', True),
    ('DNI', '1234567', False),
    ('DNI', '123456789', False),
    ('DNI', '1234ABCD', False),
    ('CORREO', 'juan@gmail.com', True),
    ('CORREO', 'maria@usil.edu.pe', True),
    ('CORREO', 'juangmail.com', False),
    ('CORREO', 'juan@gmail.c', False),
    ('CORREO', 'juan@@gmail.com', False),
    ('NOMBRE', 'Juan Perez', True),
    ('NOMBRE', 'María López', True),
    ('NOMBRE', 'Juan123', False),
    ('NOMBRE', '', False),
    ('INSTITUCION', 'Universidad de Lima', True),
    ('INSTITUCION', 'Instituto 2026', True),
    ('INSTITUCION', 'Universidad @ Lima', False),
    ('INSTITUCION', '', False),
    ('PUESTO', 'Asistente administrativo', True),
    ('PUESTO', 'Analista 2', True),
    ('PUESTO', 'Desarrollador @ Python', False),
    ('PUESTO', '', False),
]

@pytest.mark.parametrize('campo,valor,esperado', CASOS)
def test_afd_y_expresion_regular(campo, valor, esperado):
    _, afd = construir_automatas(campo)
    assert bool(re.fullmatch(EXPRESIONES[campo], valor)) == esperado
    assert reconocer_afd(afd, valor) == esperado

@pytest.mark.parametrize('texto,esperado', [
    ('DNI: 12345678', True),
    ('DNI: 1234567', False),
    ('CORREO: juan@gmail.com', True),
    ('CORREO: juangmail.com', False),
    ('NOMBRE: Juan Perez', True),
    ('NOMBRE: Juan123', False),
    ('CAMPO_DESCONOCIDO: valor', False),
])
def test_analizador_lexico(texto, esperado):
    _, errores = analizar_lexico(texto)
    assert (len(errores) == 0) == esperado

def test_ejemplo_completo():
    ruta = Path(__file__).resolve().parent / "ejemplos" / "postulacion.txt"
    texto = ruta.read_text(encoding="utf-8")
    tokens, errores = analizar_lexico(texto)
    assert len(tokens) == 24
    assert errores == []