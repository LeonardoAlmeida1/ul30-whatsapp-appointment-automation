from ul30_diario import formatar_item


def test_formatar_consulta():

    row = {
        "descricao_do_procedimento": "Consulta",
        "codigo_do_procedimento": "10101012",
        "nome_do_usuario": "João"
    }

    resultado = formatar_item(row)

    assert resultado == "Consulta Dr(a) João"


def test_formatar_exame():

    row = {
        "descricao_do_procedimento": "Ressonância Magnética",
        "codigo_do_procedimento": "12345678",
        "nome_do_usuario": "João"
    }

    resultado = formatar_item(row)

    assert resultado == "Exame Ressonância Magnética"


def test_formatar_exame_com_codigo_diferente():

    row = {
        "descricao_do_procedimento": "Ultrassonografia",
        "codigo_do_procedimento": "99999999",
        "nome_do_usuario": "Maria"
    }

    resultado = formatar_item(row)

    assert resultado == "Exame Ultrassonografia"