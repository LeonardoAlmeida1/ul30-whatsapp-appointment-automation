#IMPORTANDO BIBLIOTECAS
import os.path
import gspread
from google.oauth2.service_account import Credentials

import os
import sys
import time
#import logging
import subprocess, shutil
import random
import keyboard
import requests
import traceback

import psycopg2

import pandas as pd
import urllib
from datetime import time as dt_time
from datetime import datetime
import math

from System.config import logger
from System import state

# LOGIN E VERIFICAÇÕES
SAMPLE_SPREADSHEET_ID = "ID_PLANILHA_GOOGLE"
CHAVE = "CÓDIGO_DE_AUTENTICAÇÃO"  # Substitua pelo valor real da chave

def verificar_cliente_ativo(chave):
    """
    Verifica na planilha se o cliente está ativo usando Service Account.
    """
    try:
        gc = gspread.service_account(filename="System/credentials.json")
        ws = gc.open_by_key(SAMPLE_SPREADSHEET_ID).sheet1

        dados = ws.get_all_values()

        # Percorre cada linha
        for row in dados:
            # Garante mínimo de colunas
            if len(row) > 4 and row[1] == chave:
                status = row[4].strip().lower()
                
                if status == "inativo":
                    logger.error("Erro1: Entre em contato com o suporte TELEFONE_SUPORTE")
                    sys.exit(0)  # Bloqueia o robô
                
                return True

        # Se não encontrou a chave
        logger.error("Erro2: Entre em contato com o suporte TELEFONE_SUPORTE.")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Erro3: Entre em contato com o suporte TELEFONE_SUPORTE. {e}")
        sys.exit(0)
        return False
verificar_cliente_ativo(CHAVE)
#FIM PROCESSO DE AUTENTICAÇÃO

codigos_consultas = ['10101012', '50000462', '50000560', '50001221']
API_URL = "http://SEU_SERVIDOR/messages/send"
CLINIC_ID = "ID_DA_CLINICA"

BATCH_SIZE = 50

def formatar_csv():
    logger.info("📂 Lendo novo CSV e Formatando...")
    #LENDO E TRATANDO AS INFORMAÇÕES DA D.F
    dados = pd.read_csv("./Arquivos/confirmacao.csv",encoding="ISO-8859-1",sep=";")
    # 👉 Converte EXPLICITAMENTE de yyyy-mm-dd para data
    dados['data'] = pd.to_datetime(dados['data'], format="%Y-%m-%d", errors="coerce")
    # 👉 Formata para dd/mm/yyyy (padrão brasileiro)
    dados['data'] = dados['data'].dt.strftime('%d/%m/%Y')
    linhas_antes = len(dados)
    convenios_para_excluir = ['Representantes',]  # adicione mais se necessário
    dados = dados[~dados['nome_do_convenio'].isin(convenios_para_excluir)]
    linhas_depois = len(dados)
    logger.debug(f"Removi os convênios que não são para enviar mensagem: {linhas_antes - linhas_depois}")
    # Lista das colunas a serem removidas
    colunas_para_excluir = [
        "nome_da_especialidade", "consulta", "exame",
        "faltou", "compareceu", "nome_do_convenio", "complemento", "tipo_de_telefone",
        "tipo_de_telefone_2", "telefone_2", "email"]
    # Remove as colunas
    dados = dados.drop(columns=colunas_para_excluir)
    logger.debug("Vou remover os recados das agendas e olhar só para o seu horário comercial")
    # Converte a coluna 'hora' de string para datetime (hora)
    dados['hora'] = pd.to_datetime(dados['hora'], format='%H:%M:%S', errors='coerce').dt.time
    # Define o intervalo desejado
    hora_inicio = dt_time(7, 0, 0)
    hora_fim = dt_time(18, 0, 0)
    # Filtra apenas os registros dentro do intervalo
    dados = dados[(dados['hora'] >= hora_inicio) & (dados['hora'] <= hora_fim)]
    logger.debug("Vou remover os agendamentos que não é para enviar mensagem...")
    # Filtra os dados conforme as condições
    linhas_antes = len(dados)
    dados = dados[dados["nao_enviar_sms"].str.lower() == "não"]
    linhas_depois = len(dados)
    logger.debug(f"Agendamentos removidos para não enviar sms: {linhas_antes - linhas_depois}")
    # Conta quantas linhas têm prontuário nulo
    linhas_antes = len(dados)
    dados = dados[dados['numero_do_prontuario'].notnull()]
    linhas_depois = len(dados)
    # Calcula quantas foram removidas
    removidas = linhas_antes - linhas_depois
    if removidas > 0:
        # Se houver prontuário nulo, avisa o usuário
        logger.debug(f"Encontrei {removidas} linha(s) com prontuário nulo e removi, peça que sempre façam o cadastro ou puxem o cadastro em todos os agendamentos!")
        time.sleep(0.1)
    # Agora remove o .0 dos prontuários restantes
    dados['numero_do_prontuario'] = dados['numero_do_prontuario'].astype(int).astype(str)
    logger.debug("Verificando se houve algum burlamento nos agendamentos...")
    linhas_antes = len(dados)
    # Remover linhas com código de procedimento nulo
    dados = dados[dados['codigo_do_procedimento'].notna()]
    linhas_depois = len(dados)
    logger.debug(f"Removi {linhas_antes - linhas_depois} agendamento(s) com código de procedimento nulo (burlado).")
    # Remover "." e "-" dos códigos (convertendo para string antes)
    dados['codigo_do_procedimento'] = dados['codigo_do_procedimento'].astype(str).str.replace(r"[.-]", "", regex=True)
    codigos_consultas = ['10101012', '50000462', '50000560', '50001221']
    logger.debug("Agora vou tomar o cuidado para não enviar mensagens mais de uma vez para o mesmo paciente, um momento...")
    # Cria uma nova coluna com o texto formatado
    dados['descricao_formatada'] = dados.apply(formatar_item, axis=1)
    # Agrupa por número do prontuário
    df_grouped = (
        dados.groupby("numero_do_prontuario")
        .agg({
            "data": "first",
            "hora": "first",
            "nome_do_paciente": "first",
            "telefone": "first",
            "descricao_formatada": lambda x: "\n".join(x)  # junta todos os exames
            })
            .reset_index()
            )
    df_grouped["hora"] = pd.to_datetime(df_grouped["hora"], format="%H:%M:%S").dt.time

    df_grouped = df_grouped.sort_values(by="hora", ascending=True)
    dados = df_grouped
    logger.debug("Vou tratar os telefones agora, se eu encontrar algum inválido, vou separar para revisar depois.")
    # Salvar telefone original antes do tratamento
    dados['telefone_original'] = dados['telefone']
    time.sleep(0.1)
    # Aplicar a função
    dados[['telefone_tratado', 'motivo_exclusao']] = dados['telefone'].apply(
        lambda t: pd.Series(tratar_telefone_e_motivo(t))
        )
    time.sleep(0.1)
    # ===> Exportar apenas os telefones inválidos para revisão
    dados_invalidos = dados[dados['telefone_tratado'].isna()][[
        'nome_do_paciente', 'numero_do_prontuario', 'telefone_original', 'motivo_exclusao', 'data', 'hora'
        ]]
    time.sleep(0.1)
    salvar_telefones_invalidos(dados_invalidos)
    # Remover da base principal os telefones inválidos
    dados = dados[dados['telefone_tratado'].notna()].reset_index(drop=True)
    time.sleep(0.1)
    logger.info(f"OK, tudo tratado e salvo. Total de números para envio da Confirmação: {len(dados)}")
    # Lista das colunas a serem removidas
    colunas_para_excluir = [ "telefone_original", "motivo_exclusao", "telefone"
                            ]
    # Remove as colunas
    dados = dados.drop(columns=colunas_para_excluir)
    dados = dados.rename(columns={
        "numero_do_prontuario": "Prontuário",
        "telefone_tratado": "Telefone",
        "descricao_formatada": "Exames",
        "data": "Data",
        "hora": "Hora",
        "nome_do_paciente": "Nome"
        })
    dados = dados[["Nome", "Telefone", "Prontuário", "Data", "Hora", "Exames"]]
    dados["Hora"] = dados["Hora"].apply(lambda x: x.strftime("%H:%M") if hasattr(x, "strftime") else x)
    time.sleep(2)
    return dados

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
def salvar_telefones_invalidos(dados_invalidos, arquivo="./Arquivos/Erros/telefones_para_revisao.xlsx"):
    # Se o arquivo já existe, lê e concatena
    if os.path.exists(arquivo):
        df_existente = pd.read_excel(arquivo)

        # Concatena mantendo o histórico
        df_final = pd.concat([df_existente, dados_invalidos], ignore_index=True)
    else:
        # Se não existe, o DataFrame final é apenas o atual
        df_final = dados_invalidos

    # Salva novamente com tudo junto
    df_final.to_excel(arquivo, index=False)
def formatar_item(row):
    """Recebe uma linha e retorna o texto formatado conforme o tipo."""
    
    procedimento = row['descricao_do_procedimento']
    if row['codigo_do_procedimento'] in codigos_consultas: # Exemplo: "EXAME" ou "CONSULTA"
        tipo = "CONSULTA"
    else:
        tipo = "EXAME"
    medico = row.get('nome_do_usuario', "")

    if tipo.upper() == "CONSULTA":
        return f"Consulta Dr(a) {medico}"
    else:
        return f"Exame {procedimento}"
    
def enviar_agenda_do_dia_para_sheets(df: pd.DataFrame,
                                     nome_planilha: str = "NOME_DA_PLANILHA",
                                     aba: str = None,
                                     credenciais: str = r"System\credentials.json") -> bool:
    """
    Envia a agenda do dia para o Google Sheets:
    - Adiciona coluna Status = PENDING
    - Limpa a aba
    - Reescreve tudo do zero

    :param df: DataFrame já tratado (Nome, Telefone, Prontuário, Data, Hora, Exames)
    :param nome_planilha: Nome da planilha no Google Sheets
    :param aba: Nome da aba (se None, usa sheet1)
    :param credenciais: Caminho do credentials.json
    :return: True se deu certo, False se falhou
    """

    try:
        # 1) Garante coluna Status
        if "Status" not in df.columns:
            df["Status"] = "PENDING"

        # 2) Conecta no Google Sheets
        gc = gspread.service_account(filename=credenciais)
        sh = gc.open(nome_planilha)

        ws = sh.worksheet(aba) if aba else sh.sheet1

        # 3) Limpa a aba (sua escolha)
        ws.clear()

        # 4) Envia cabeçalho + dados
        ws.update(
            [df.columns.values.tolist()] + df.values.tolist()
        )

        logger.info(
            f"Agenda do dia enviada com sucesso — {len(df)} pacientes."
        )

        return True

    except Exception as e:
        logger.error(f"Erro ao enviar agenda para Sheets: {e}")
        return False

def atualizar_via_csv():
    salvar_no_historico()
    logger.info("🔄 Atualizando dados via CSV...")
    dados = formatar_csv()
    sucesso = enviar_agenda_do_dia_para_sheets(dados)
    if sucesso:
        logger.info("✅ Dados atualizados com sucesso via CSV!")
    else:
        logger.error("❌ Falha ao atualizar dados via CSV.")
    enviar_payload_servidor(dados)

    logger.info("🔁 Retornando para leitura automática...")
def ler_planilha_do_google(sheet: str = "NOME_DA_PLANILHA",
                           aba: str = None,
                           credenciais: str = r"System\credentials.json"):
    logger.info("🔄 Lendo Google Sheets...")
    gc = gspread.service_account(filename=credenciais)
    sh = gc.open(sheet)
    ws = sh.worksheet(aba) if aba else sh.sheet1
    registros = ws.get_all_records()
    return registros
def salvar_no_historico():
    """
    Salva todos os dados atuais da planilha da clínica
    no arquivo Histórico_Geral.xlsx antes de limpar.
    """
    try:
        dados = ler_planilha_do_google()

        if not dados:
            logger.info("Nenhum dado para salvar no histórico.")
            return

        df_novo = pd.DataFrame(dados)

        # Adiciona data de backup
        df_novo["Data_Backup"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        arquivo_historico = "./Arquivos/Relatorios/Historico_Geral.xlsx"

        if os.path.exists(arquivo_historico):
            df_existente = pd.read_excel(arquivo_historico)
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        else:
            df_final = df_novo

        df_final.to_excel(arquivo_historico, index=False)

        logger.info("Backup salvo no Histórico_Geral.xlsx com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao salvar histórico: {e}")

def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]
def enviar_payload_servidor(dados):

    logger.info("📤 Iniciando envio de payloads para servidor...")

    payload = []

    for _, row in dados.iterrows():

        paciente = {
            "clinic_id": CLINIC_ID,
            "name": str(row["Nome"]).strip(),
            "phone": str(row["Telefone"]).strip(),
            "prontuario": str(row["Prontuário"]).strip(),
            "date": str(row["Data"]).strip(),
            "time": str(row["Hora"]).strip(),
            "exams": str(row["Exames"]).strip()
        }

        payload.append(paciente)

    logger.info(f"📦 Total de pacientes para envio: {len(payload)}")

    lote_atual = 1

    for batch in chunk_list(payload, BATCH_SIZE):

        logger.info(f"🚀 Enviando lote {lote_atual} ({len(batch)} pacientes)")

        try:

            response = requests.post(
                API_URL,
                json=batch,
                timeout=30
            )

            if response.status_code == 200:

                data = response.json()

                logger.info(
                    f"✅ Lote enviado | "
                    f"Recebidos={data.get('received')} "
                    f"Fila={data.get('queued')}"
                )

            else:

                logger.error(f"❌ Erro servidor: {response.text}")

        except Exception as e:

            logger.error(f"❌ Erro enviando lote: {e}")

        lote_atual += 1

        time.sleep(2)

    logger.info("🏁 Envio de payload finalizado.")

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
# INÍCIO DO SCRIPT PRINCIPAL
def iniciar_automacao():
    logger.info("🚀 Sistema iniciado!")
    logger.info("""
    ========================================
    Status: Online
    ========================================""")
    pessoas_processadas = {}
    while state.sistema_ativo:
        try:
            # PASSO 1 — Ler planilha inteira
            linhas = ler_planilha_do_google()
            confirmados = sum(1 for linha in linhas if linha["Status"].upper() == "CONFIRMED")
            cancelados = sum(1 for linha in linhas if linha["Status"].upper() == "CANCELLED")
            pendentes = sum(1 for linha in linhas if linha["Status"].upper() == "PENDING")
            total = len(linhas)
            state.confirmados = confirmados
            state.cancelados = cancelados
            state.pendentes = pendentes
            state.pacientes = total
                        
            # PASSO 2 — Filtrar só quem NÃO é PENDING
            linhas_para_processar = []

            for linha in linhas:
                if linha["Status"] != "PENDING":
                    linhas_para_processar.append(linha)

            logger.debug(f"Encontrados {len(linhas_para_processar)} registros Não Pendentes.")

            # PASSO 3 — Percorrer cada linha filtrada
            for linha in linhas_para_processar:

                prontuario = linha["Prontuário"]
                data = linha["Data"]
                data = pd.to_datetime(data,format="%d/%m/%Y",errors="coerce").strftime("%Y-%m-%d")
                status = linha["Status"]

                chave = (prontuario, data)   # <-- você mesmo disse que quer usar isso 👍

                # PASSO 4 — Ver se já foi processado antes
                if chave in pessoas_processadas:
                    #logger.debug(f"⏭️ Já atualizado antes: {chave}, ignorando...")
                    continue   # pula e vai para a próxima pessoa

                # PASSO 5 — Atualizar banco (só primeira vez)
                atualizar_banco(prontuario, data, status)

                # PASSO 6 — Marcar como processado
                pessoas_processadas[chave] = status

            logger.debug("✅ Ciclo finalizado. Aguardando próximo check...")

            # ---- ESPERA INTELIGENTE PARA ATUALIZAÇÃO ----
            state.tempo_restante = state.TEMPO_TOTAL
            while state.tempo_restante > 0:
                if not state.sistema_ativo:
                    break

                time.sleep(1)
                state.tempo_restante -= 1

        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}")
            logger.debug(traceback.format_exc())
            time.sleep(5)  # espera um pouco antes de tentar novamente
            logger.warning("Ocorreu um erro, mas o sistema continuará rodando. Peça que Verifiquem os logs para detalhes.")