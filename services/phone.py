import pandas as pd
import time

def tratar_telefone_e_motivo(telefone):
    if pd.isna(telefone):
        time.sleep(0.1)
        return None, "telefone ausente"

    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))

    if len(telefone_limpo) == 11:
        time.sleep(0.1)
        return '55' + telefone_limpo, None  # válido

    elif len(telefone_limpo) == 9 and telefone_limpo.startswith('9'):
        # Número sem DDD, mas válido — assume DDD 11
        time.sleep(0.1)
        return '5511' + telefone_limpo, None

    elif len(telefone_limpo) == 10:
        time.sleep(0.1)
        return None, "possível telefone fixo"

    elif len(telefone_limpo) < 9:
        time.sleep(0.1)
        return None, "incompleto ou sem DDD"

    else:
        return None, "formato inválido ou dígitos extras"