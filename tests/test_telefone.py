from ul30_diario import tratar_telefone_e_motivo


def test_telefone_completo():

    telefone, motivo = tratar_telefone_e_motivo(
        "11999999999"
    )

    assert telefone == "5511999999999"
    assert motivo is None


def test_telefone_sem_ddd():

    telefone, motivo = tratar_telefone_e_motivo(
        "999999999"
    )

    assert telefone == "5511999999999"
    assert motivo is None


def test_telefone_ausente():

    telefone, motivo = tratar_telefone_e_motivo(None)

    assert telefone is None
    assert motivo == "telefone ausente"


def test_telefone_fixo():

    telefone, motivo = tratar_telefone_e_motivo(
        "1133334444"
    )

    assert telefone is None
    assert motivo == "possível telefone fixo"


def test_telefone_incompleto():

    telefone, motivo = tratar_telefone_e_motivo(
        "12345678"
    )

    assert telefone is None
    assert motivo == "incompleto ou sem DDD"