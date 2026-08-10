import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import random
import threading
import time
from ui import UIController
import ui
from ul30_diario import iniciar_automacao, atualizar_via_csv, salvar_no_historico
from System.config import log_queue
from System import state

# ----------------------------
# Funções
# ----------------------------

def iniciar_sistema():

    if state.sistema_ativo:
        adicionar_log("O sistema já está em execução.")
        return

    state.sistema_ativo = True

    status.config(
        text="🟢 Online",
        bootstyle="success"
    )

    threading.Thread(target=iniciar_automacao, daemon=True).start()

    #lbl_pacientes.config(text="312")
    #lbl_confirmados.config(text="251")
    #lbl_cancelados.config(text="18")
    #lbl_pendentes.config(text="43")

    #adicionar_log("Sistema iniciado com sucesso.")
    #adicionar_log("Planilha de pacientes carregada.")
    #adicionar_log("312 pacientes encontrados para hoje.")

def parar_sistema():
    if not state.sistema_ativo:
        adicionar_log("O sistema já está parado.")
        return

    state.sistema_ativo = False

     # Reinicia o temporizador
    state.tempo_restante = state.TEMPO_TOTAL
    atualizar_interface_temporizador()

    status.config(
        text="🔴 Offline",
        bootstyle="danger"
    )

    lbl_pacientes.config(text="0")
    lbl_confirmados.config(text="0")
    lbl_cancelados.config(text="0")
    lbl_pendentes.config(text="0")

    adicionar_log("Sistema parado.")

def atualizar_dados():
    if not state.sistema_ativo:
        adicionar_log("O sistema está offline. Inicie o sistema para atualizar os dados.")
        return

    adicionar_log("Atualizando dados...")
    # Aqui você pode adicionar a função de leitura do Google Sheets e atualização do dashboard
    threading.Thread(target=executar_atualizacao, daemon=True).start()

def executar_atualizacao():
    try:
        atualizar_via_csv()
        app.after(0, lambda: adicionar_log("Dados atualizados com sucesso."))
    except Exception as e:
        app.after(0, lambda: adicionar_log(f"Erro ao atualizar dados: {e}"))

def adicionar_log(mensagem):
    logs.insert(END, mensagem + "\n")
    logs.see(END)
    #horario = datetime.now().strftime("%H:%M:%S")
    #logs.insert(END, f"[{horario}] {mensagem}\n")
    #logs.see(END)  # Rola para o final do log

def processar_logs():
    while not log_queue.empty():
        mensagem = log_queue.get()
        logs.insert(END, mensagem + "\n")
        logs.see(END)
    app.after(100, processar_logs)  # Verifica a cada 100ms

def atualizar_interface_temporizador():
    barra['value'] = state.TEMPO_TOTAL - state.tempo_restante

    minutos = state.tempo_restante // 60
    segundos = state.tempo_restante % 60

    lbl_tempo.config(text=f"{minutos:02d}:{segundos:02d}")

def atualizar_temporizador():
    if state.sistema_ativo:
        atualizar_interface_temporizador()
    app.after(1000, atualizar_temporizador)  # Atualiza a cada segundo

def atualizar_dashboard():
    if state.sistema_ativo:
        lbl_pacientes.config(text=str(state.pacientes))
        lbl_confirmados.config(text=str(state.confirmados))
        lbl_cancelados.config(text=str(state.cancelados))
        lbl_pendentes.config(text=str(state.pendentes))

    app.after(5000, atualizar_dashboard)  # Atualiza a cada 5 segundos

# ----------------------------
# Janela
# ----------------------------

app = ttk.Window(
    title="UL30 Automação & Processos",
    themename="darkly",
    size=(1000, 650),
    resizable=(False, False)
)

# ==========================
# CABEÇALHO
# ==========================

header = ttk.Frame(app)
header.pack(fill=X)

titulo = ttk.Label(
    header,
    text="UL30 Automação & Processos",
    font=("Segoe UI", 20, "bold")
)

titulo.pack(pady=15)

# ==========================
# CORPO
# ==========================

body = ttk.Frame(app)
body.pack(fill=BOTH, expand=True)

# Menu esquerdo

menu = ttk.Frame(body, width=220)
menu.pack(side=LEFT, fill=Y, padx=10, pady=10)

# Área principal

conteudo = ttk.Frame(body)
conteudo.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

# ==========================
# COMPONENTES DO MENU
# ==========================

status = ttk.Label(
    menu,
    text="🔴 Offline",
    font=("Segoe UI", 11),
    bootstyle="danger"
)

status.pack(pady=20)

ttk.Button(
    menu,
    text="▶ Iniciar Sistema",
    bootstyle="success",
    command=iniciar_sistema
).pack(fill=X, pady=5)

ttk.Button(
    menu,
    text="■ Parar Sistema",
    bootstyle="danger",
    command=parar_sistema
).pack(fill=X, pady=5)

ttk.Button(
    menu,
    text="🔄 Atualizar Dados",
    bootstyle="info",
    command=atualizar_dados
).pack(fill=X, pady=5)

# ==========================
# COMPONENTES DO CONTEÚDO
# ==========================

# ==========================
# CARDS
# ==========================

cards = ttk.Frame(conteudo)
cards.pack(fill=X, pady=20)

# ---------- Card 1 ----------

card1 = ttk.Labelframe(cards, text="Total de Pacientes", bootstyle="info")
card1.pack(side=LEFT, padx=10, ipadx=40, ipady=15)

lbl_pacientes = ttk.Label(
    card1,
    text="0",
    font=("Segoe UI", 24, "bold")
)
lbl_pacientes.pack()

# ---------- Card 2 ----------

card2 = ttk.Labelframe(cards, text="Confirmados", bootstyle="success")
card2.pack(side=LEFT, padx=10, ipadx=40, ipady=15)

lbl_confirmados = ttk.Label(
    card2,
    text="0",
    font=("Segoe UI", 24, "bold")
)
lbl_confirmados.pack()

# ---------- Card 3 ----------

card3 = ttk.Labelframe(cards, text="Cancelados", bootstyle="danger")
card3.pack(side=LEFT, padx=10, ipadx=40, ipady=15)

lbl_cancelados = ttk.Label(
    card3,
    text="0",
    font=("Segoe UI", 24, "bold")
)
lbl_cancelados.pack()

# ---------- Card 4 ----------

card4 = ttk.Labelframe(cards, text="Pendentes", bootstyle="warning")
card4.pack(side=LEFT, padx=10, ipadx=40, ipady=15)

lbl_pendentes = ttk.Label(
    card4,
    text="0",
    font=("Segoe UI", 24, "bold")
)
lbl_pendentes.pack()

# ==========================
# SINCRONIZAÇÃO
# ==========================

sync_frame = ttk.Labelframe(
    conteudo,
    text="Próxima sincronização",
    bootstyle="info"
)

sync_frame.pack(fill=X, padx=10)

barra = ttk.Progressbar(
    sync_frame,
    length=600,
    maximum=600,
    mode="determinate",
    bootstyle="info-striped"
)

barra.pack(padx=15, pady=10)

lbl_tempo = ttk.Label(
    sync_frame,
    text="10:00",
    font=("Segoe UI", 12)
)

lbl_tempo.pack(pady=(0,10))

# ==========================
# PAINEL DE LOGS
# ==========================

logs_frame = ttk.Labelframe(
    conteudo,
    text="Logs do Sistema",
    bootstyle="primary"
)
logs_frame.pack(fill=BOTH, expand=True, padx=10, pady=20)

logs = ttk.Text(
    logs_frame,
    height=18,
    font=("Consolas", 10)
)

logs.pack(fill=BOTH, expand=True, padx=10, pady=10)

atualizar_dashboard()  # Inicia a atualização do dashboard
atualizar_temporizador()  # Inicia o temporizador
processar_logs()  # Inicia o processamento dos logs
app.mainloop()