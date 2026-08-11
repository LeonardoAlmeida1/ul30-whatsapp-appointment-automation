import pandas as pd
import psycopg2

from System.config import logger

def conectar():
    try:
        conn = psycopg2.connect(
            host="IP_DO_SERVIDOR",
            port="PORTA_DO_SERVIDOR",
            database="LOGICA_DO_BANCO",
            user="USUARIO_DO_BANCO",
            password="SENHA_DO_BANCO"
        )
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco: {e}")
        return None
def executar_select(query, params=None):
    conn = conectar()
    if not conn:
        return None
    
    try:
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Erro ao executar consulta: {e}")
        conn.close()
        return None
def executar_update(query, params=None):
    conn = conectar()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao executar alteração: {e}")
        conn.close()
        return False 
def confirmar_agenda(prontuario, data):
    return executar_update(
        """
        UPDATE NOME_DA_TABELA_DA_CLINICA
        SET COLUNA_CONFIRMAR = %s
        WHERE COLUNA_PRONTUARIO = %s
          AND data::date = %s
        """,
        params=(1, prontuario, data)
    )
def mover_agendamento(prontuario, data):
    conn = conectar()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()

        # 1. Inserir na tabela destino
        cursor.execute("""
            INSERT INTO NOME_DA_TABELA_DESTINO_DESMARCAR (COLUNA_USUARIO, data, hora, nomepaciente, COLUNA_PRONTUARIO, COLUNA_TIPO_DE_TELEFONE, telefone, codigoprocprincipal, especialidade, COLUNA_CONFIRMAR, email, COLUNA_ADICIONAL)
            SELECT COLUNA_USUARIO, data, hora, nomepaciente, COLUNA_PRONTUARIO, COLUNA_TIPO_DE_TELEFONE, telefone, codigoprocprincipal, especialidade, COLUNA_CONFIRMAR, email, COLUNA_ADICIONAL
            FROM NOME_DA_TABELA_DA_CLINICA
            WHERE COLUNA_PRONTUARIO = %s
              AND data::date = %s
        """, (prontuario, data))

        # 2. Apagar da tabela origem
        cursor.execute("""
            DELETE FROM NOME_DA_TABELA_DA_CLINICA
            WHERE COLUNA_PRONTUARIO = %s
              AND data::date = %s
        """, (prontuario, data))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erro ao mover agendamento: {e}")
        conn.rollback()
        conn.close()
        return False
def atualizar_banco(prontuario, data, status):
    """
    Centraliza todas as decisões de atualização no banco.
    Aqui você só define 'o que fazer' para cada status.
    """

    status = status.upper().strip()

    if status == "CONFIRMED":
        logger.debug(f"✔ Confirmando agenda: {prontuario} | {data}")
        return confirmar_agenda(prontuario, data)

    elif status == "CANCELLED":
        logger.debug(f"❌ Movendo agendamento para desmarcadas: {prontuario} | {data}")
        return mover_agendamento(prontuario, data)

    else:
        logger.warning(f"⚠ Status não tratado: {status} — nada feito.")
        return False