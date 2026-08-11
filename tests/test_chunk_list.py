from ul30_diario import chunk_list


def test_chunk_list_divide_corretamente():

    dados = list(range(10))

    resultado = list(chunk_list(dados, 3))

    assert resultado == [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [9]
    ]


def test_chunk_list_tamanho_exato():

    dados = list(range(6))

    resultado = list(chunk_list(dados, 3))

    assert resultado == [
        [0, 1, 2],
        [3, 4, 5]
    ]


def test_chunk_list_lista_vazia():

    dados = []

    resultado = list(chunk_list(dados, 3))

    assert resultado == []