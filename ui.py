class UIController:

    def __init__(self):
        self.lbl_pacientes = None
        self.lbl_confirmados = None
        self.lbl_cancelados = None
        self.lbl_pendentes = None

    def atualizar_pacientes(self, quantidade):
        self.lbl_pacientes.config(text=str(quantidade))

    def atualizar_confirmados(self, quantidade):
        self.lbl_confirmados.config(text=str(quantidade))

    def atualizar_cancelados(self, quantidade):
        self.lbl_cancelados.config(text=str(quantidade))

    def atualizar_pendentes(self, quantidade):
        self.lbl_pendentes.config(text=str(quantidade))