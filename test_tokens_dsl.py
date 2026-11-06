
import pytest

from app import app
from analizadores.automatas import (
    TOKENS_RESERVADOS,
    construir_afnd_token,
    construir_afd_token,
    convertir_afnd_a_afd,
    cerradura_epsilon,
    mover,
    reconocer_afd
)
from analizadores.tablas import (
    construir_automatas,
    validar_con_automata
)


CASOS_INVALIDOS = {
    "TK_SECCION": [
        "",
        "DATOS",
        "DATOS_PERSONAL",
        "EDUCACIÓN",
        "EDUCACION ",
        "EXPERIENCI",
        "experiencia"
    ],
    "TK_CAMPO": [
        "",
        "NOMBR3",
        "NOMBR",
        "DN",
        "CORREOS",
        "INSTITUCIONES",
        "nombre",
        "PUESTO1"
    ],
    "TK_ABRE": [
        "",
        "}",
        ":",
        "{{",
        "{ "
    ],
    "TK_CIERRA": [
        "",
        "{",
        ":",
        "}}",
        " }"
    ],
    "TK_DOS_PUNTOS": [
        "",
        "{",
        "}",
        "::",
        ";",
        ": "
    ]
}


def reconocer_afnd(afnd, cadena):
    actuales = cerradura_epsilon(
        {afnd["q0"]},
        afnd["delta"]
    )

    for simbolo in cadena:
        if simbolo not in afnd["Sigma"]:
            return False

        siguientes = mover(
            actuales,
            simbolo,
            afnd["delta"]
        )

        actuales = cerradura_epsilon(
            siguientes,
            afnd["delta"]
        )

        if not actuales:
            return False

    return bool(
        actuales.intersection(afnd["F"])
    )


@pytest.mark.parametrize(
    "token,lexema",
    [
        (token, lexema)
        for token, lexemas in TOKENS_RESERVADOS.items()
        for lexema in lexemas
    ]
)
def test_lexemas_validos(token, lexema):
    afnd = construir_afnd_token(token)
    afd = construir_afd_token(token)

    assert reconocer_afnd(afnd, lexema)
    assert reconocer_afd(afd, lexema)
    assert validar_con_automata(token, lexema)


@pytest.mark.parametrize(
    "token,lexema",
    [
        (token, lexema)
        for token, lexemas in CASOS_INVALIDOS.items()
        for lexema in lexemas
    ]
)
def test_lexemas_invalidos(token, lexema):
    afnd = construir_afnd_token(token)
    afd = construir_afd_token(token)

    assert not reconocer_afnd(afnd, lexema)
    assert not reconocer_afd(afd, lexema)
    assert not validar_con_automata(token, lexema)


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
def test_afd_completo_y_determinista(token):
    afd = construir_afd_token(token)

    estados = afd["Q"]
    alfabeto = afd["Sigma"]
    delta = afd["delta"]

    assert afd["q0"] in estados
    assert afd["F"]
    assert afd["F"].issubset(estados)

    assert len(delta) == len(estados) * len(alfabeto)

    for estado in estados:
        for simbolo in alfabeto:
            assert (estado, simbolo) in delta

            destino = delta[(estado, simbolo)]

            assert isinstance(destino, str)
            assert destino in estados


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
def test_estructura_afnd(token):
    afnd = construir_afnd_token(token)

    assert afnd["q0"] in afnd["Q"]
    assert afnd["F"]
    assert afnd["F"].issubset(afnd["Q"])

    for (origen, simbolo), destinos in afnd["delta"].items():
        assert origen in afnd["Q"]
        assert simbolo == "ε" or simbolo in afnd["Sigma"]
        assert isinstance(destinos, set)
        assert destinos
        assert destinos.issubset(afnd["Q"])


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
def test_conversion_afnd_a_afd(token):
    afnd = construir_afnd_token(token)

    afd_convertido = convertir_afnd_a_afd(afnd)
    afd_directo = construir_afd_token(token)

    assert afd_convertido["Q"] == afd_directo["Q"]
    assert afd_convertido["Sigma"] == afd_directo["Sigma"]
    assert afd_convertido["F"] == afd_directo["F"]
    assert afd_convertido["delta"] == afd_directo["delta"]


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
def test_integracion_con_tablas(token):
    afnd, afd = construir_automatas(token)

    assert afnd["q0"] in afnd["Q"]
    assert afd["q0"] in afd["Q"]

    for lexema in TOKENS_RESERVADOS[token]:
        assert reconocer_afnd(afnd, lexema)
        assert reconocer_afd(afd, lexema)


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
@pytest.mark.parametrize(
    "tipo",
    ["afnd", "afd"]
)
def test_api_automatas_tokens(token, tipo):
    cliente = app.test_client()

    respuesta = cliente.get(
        f"/api/automatas/{token}/{tipo}"
    )

    assert respuesta.status_code == 200

    datos = respuesta.get_json()

    assert datos["campo"] == token
    assert datos["tipo"] == tipo.upper()
    assert datos["estados"]
    assert datos["alfabeto"]
    assert datos["transiciones"]
    assert datos["inicial"] in datos["estados"]

    for final in datos["finales"]:
        assert final in datos["estados"]


@pytest.mark.parametrize(
    "token",
    list(TOKENS_RESERVADOS)
)
def test_equivalencia_con_casos_invalidos(token):
    afnd = construir_afnd_token(token)
    afd = construir_afd_token(token)

    casos = (
        list(TOKENS_RESERVADOS[token])
        + CASOS_INVALIDOS[token]
    )

    for cadena in casos:
        resultado_afnd = reconocer_afnd(
            afnd,
            cadena
        )

        resultado_afd = reconocer_afd(
            afd,
            cadena
        )

        assert resultado_afnd == resultado_afd

def test_lexer_utiliza_afd_reservados(monkeypatch):
    import analizadores.lexico as lexico

    llamadas = []
    validador_original = lexico.validar_token_reservado

    def registrar_validacion(token, lexema):
        resultado = validador_original(token, lexema)
        llamadas.append((token, lexema, resultado))
        return resultado

    monkeypatch.setattr(
        lexico,
        "validar_token_reservado",
        registrar_validacion
    )

    contenido = """DATOS_PERSONALES {
NOMBRE: Juan Perez
DNI: 12345678
CORREO: juan@gmail.com
}

EDUCACION {
INSTITUCION: Universidad de Lima
}

EXPERIENCIA {
PUESTO: Asistente administrativo
}"""

    tokens, errores = lexico.analizar_lexico(contenido)

    assert errores == []
    assert len(tokens) == 24

    esperadas = {
        ("TK_SECCION", "DATOS_PERSONALES", True),
        ("TK_SECCION", "EDUCACION", True),
        ("TK_SECCION", "EXPERIENCIA", True),
        ("TK_CAMPO", "NOMBRE", True),
        ("TK_CAMPO", "DNI", True),
        ("TK_CAMPO", "CORREO", True),
        ("TK_CAMPO", "INSTITUCION", True),
        ("TK_CAMPO", "PUESTO", True),
        ("TK_ABRE", "{", True),
        ("TK_CIERRA", "}", True),
        ("TK_DOS_PUNTOS", ":", True)
    }

    assert esperadas.issubset(set(llamadas))
