
import pytest

from analizadores.lexico import analizar_lexico


POSTULACION = """DATOS_PERSONALES {
NOMBRE: Ana Perez
DNI: 12345678
CORREO: ana@gmail.com
}

EDUCACION {
INSTITUCION: Universidad de Lima
}

EXPERIENCIA {
PUESTO: Analista
}"""


@pytest.mark.parametrize(
    "campo,valor_invalido,linea,tipo_valor",
    [
        ("NOMBRE", "Ana # Perez", 2, "TK_TEXTO"),
        ("DNI", "1234567", 3, "TK_DNI"),
        ("CORREO", "ana@ejemplo", 4, "TK_CORREO"),
    ],
)
def test_conserva_campo_y_separador_si_valor_es_invalido(
    campo,
    valor_invalido,
    linea,
    tipo_valor
):
    original = {
        "NOMBRE": "Ana Perez",
        "DNI": "12345678",
        "CORREO": "ana@gmail.com",
    }[campo]

    contenido = POSTULACION.replace(
        f"{campo}: {original}",
        f"{campo}: {valor_invalido}",
    )

    tokens, errores = analizar_lexico(contenido)

    assert len(tokens) == 23

    assert errores == [
        f"Línea {linea}: formato inválido para {campo}"
    ]

    assert [
        t["token"]
        for t in tokens
        if t["linea"] == linea
    ] == [
        "TK_CAMPO",
        "TK_DOS_PUNTOS",
    ]

    assert not any(
        t["token"] == tipo_valor
        and t["linea"] == linea
        for t in tokens
    )


def test_postulacion_valida_permanece_sin_cambios():
    tokens, errores = analizar_lexico(POSTULACION)

    assert errores == []
    assert len(tokens) == 24

    assert [
        t["token"]
        for t in tokens
        if t["linea"] == 2
    ] == [
        "TK_CAMPO",
        "TK_DOS_PUNTOS",
        "TK_TEXTO",
    ]
