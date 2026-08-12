import pandas as pd

from ul30_diario import formatar_csv


def test_formatar_csv_com_dados_validos(monkeypatch, tmp_path):

    arquivo_csv = tmp_path / "Arquivos" / "confirmacao.csv"
    arquivo_csv.parent.mkdir()

    dados = pd.DataFrame([
        {
            "data": "2026-08-11",
            "hora": "10:00:00",
            "nome_do_paciente": "João Silva",
            "telefone": "11999999999",
            "numero_do_prontuario": "1001",
            "codigo_do_procedimento": "10101012",
            "descricao_do_procedimento": "Consulta",
            "nome_do_usuario": "Carlos",
            "nao_enviar_sms": "não",
            "nome_da_especialidade": "Cardiologia",
            "consulta": "",
            "exame": "",
            "faltou": "",
            "compareceu": "",
            "nome_do_convenio": "Particular",
            "complemento": "",
            "tipo_de_telefone": "Celular",
            "tipo_de_telefone_2": "",
            "telefone_2": "",
            "email": ""
        }
    ])

    dados.to_csv(
        arquivo_csv,
        index=False,
        encoding="ISO-8859-1",
        sep=";"
    )

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "ul30_diario.salvar_telefones_invalidos",
        lambda dados: None
    )

    resultado = formatar_csv()

    assert len(resultado) == 1
    assert resultado.iloc[0]["Nome"] == "João Silva"
    assert resultado.iloc[0]["Telefone"] == "5511999999999"
    assert resultado.iloc[0]["Prontuário"] == "1001"
    assert resultado.iloc[0]["Data"] == "11/08/2026"
    assert resultado.iloc[0]["Hora"] == "10:00"
    assert resultado.iloc[0]["Exames"] == "Consulta Dr(a) Carlos"