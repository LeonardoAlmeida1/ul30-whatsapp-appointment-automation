import pandas as pd

from services.phone import tratar_telefone_e_motivo


def test_processar_telefone_valido():

    resultado = tratar_telefone_e_motivo("11999999999")

    assert resultado == ("5511999999999", None)


def test_processar_telefone_sem_ddd():

    resultado = tratar_telefone_e_motivo("999999999")

    assert resultado == ("5511999999999", None)


def test_processar_telefone_ausente():

    resultado = tratar_telefone_e_motivo(pd.NA)

    assert resultado == (None, "telefone ausente")


def test_processar_telefone_fixo():

    resultado = tratar_telefone_e_motivo("1133334444")

    assert resultado == (None, "possível telefone fixo")


def test_processar_telefone_incompleto():

    resultado = tratar_telefone_e_motivo("12345678")

    assert resultado == (None, "incompleto ou sem DDD")


def test_processar_telefone_invalido():

    resultado = tratar_telefone_e_motivo("551199999999999")

    assert resultado == (None, "formato inválido ou dígitos extras")