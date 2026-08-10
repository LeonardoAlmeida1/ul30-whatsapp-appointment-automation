# UL30 WhatsApp Appointment Automation

Sistema de automação de processos desenvolvido em Python para tratamento de agendas, preparação e envio de confirmações de consultas e exames, acompanhamento de respostas e atualização dos registros da clínica.

O projeto foi desenvolvido com foco em **automação de processos, integração entre sistemas, tratamento de dados e redução de atividades operacionais repetitivas**.

> **Nota:** os arquivos de dados presentes neste repositório utilizam informações fictícias e foram disponibilizados exclusivamente para fins demonstrativos e de portfólio.

---

## 🎯 Problema

O processo de confirmação de consultas e exames envolvia diversas atividades manuais:

* Exportação da agenda;
* Tratamento e limpeza dos dados;
* Validação dos telefones;
* Identificação dos procedimentos;
* Agrupamento de pacientes;
* Envio das mensagens;
* Acompanhamento das respostas;
* Atualização do status dos agendamentos;
* Registro de históricos e erros.

Além de consumir tempo da equipe, processos manuais aumentam a possibilidade de erros e dificultam o acompanhamento dos resultados.

---

## 💡 Solução

O UL30 WhatsApp Appointment Automation automatiza grande parte desse fluxo.

A aplicação recebe os dados da agenda, realiza o tratamento e validação das informações, prepara os dados para envio, integra-se a uma API de mensagens e acompanha os retornos dos pacientes.

De acordo com o status recebido, o sistema também pode atualizar ou movimentar o respectivo agendamento no banco de dados.

---

## ⚙️ Principais funcionalidades

### Tratamento de dados

* Leitura de arquivos CSV utilizando Pandas;
* Conversão e padronização de datas e horários;
* Filtragem de agendamentos;
* Remoção de registros que não devem participar do processo;
* Validação de prontuários;
* Validação e normalização de telefones;
* Identificação de telefones inválidos;
* Geração de arquivo para revisão dos dados inconsistentes.

### Processamento de procedimentos

O sistema identifica diferentes tipos de procedimentos e monta uma descrição adequada para o envio.

Consultas podem ser identificadas como:

```text
Consulta Dr(a) Nome do Profissional
```

Enquanto exames podem ser apresentados como:

```text
Exame Nome do Procedimento
```

Também é realizado o agrupamento de procedimentos pelo número do prontuário para evitar o envio de múltiplas mensagens para o mesmo paciente.

### Integração com Google Sheets

A aplicação utiliza o Google Sheets como uma camada de controle dos agendamentos.

Os registros possuem status que permitem acompanhar o processamento:

```text
PENDING
QUEUED
SENT
DELIVERED
CONFIRMED
CANCELLED
ERROR
```

O sistema também realiza backup dos dados antes da atualização da planilha.

### Envio em lotes

Os dados preparados são enviados para o servidor em lotes, reduzindo a quantidade de requisições individuais.

O tamanho padrão configurado atualmente é:

```text
50 registros por lote
```

### Atualização do banco de dados

A partir do retorno do processo de confirmação, o sistema pode executar diferentes ações no banco de dados.

Por exemplo:

```text
CONFIRMED
    ↓
Atualização do agendamento

CANCELLED
    ↓
Movimentação do agendamento
```

### Dashboard

A aplicação possui uma interface gráfica desenvolvida com Tkinter/ttkbootstrap para acompanhamento da operação.

O dashboard apresenta:

* Total de pacientes;
* Pacientes confirmados;
* Pacientes cancelados;
* Pacientes pendentes;
* Próxima sincronização;
* Logs da aplicação.

### Logs

O sistema possui logging estruturado com:

* Logs exibidos na interface;
* Arquivos de log;
* Rotação automática dos arquivos;
* Retenção dos logs históricos.

---

## 🏗️ Arquitetura

O fluxo principal da aplicação pode ser representado da seguinte forma:

```text
┌──────────────────────┐
│    Agenda da Clínica │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Pandas         │
│ Tratamento dos dados │
└──────────┬───────────┘
           │
           ├──────────────► Validação de telefones
           │
           ├──────────────► Validação de prontuário
           │
           └──────────────► Identificação de procedimentos
           │
           ▼
┌──────────────────────┐
│    Google Sheets     │
│ Controle de status   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Servidor / API    │
│      Mensagens       │
└──────────┬───────────┘
           │
           ▼
      ┌─────────┐
      │Paciente │
      └────┬────┘
           │
           ▼
┌──────────────────────┐
│       Status         │
│ Confirmado/Cancelado │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      PostgreSQL      │
│ Atualização da agenda│
└──────────────────────┘
```

A aplicação também possui uma interface gráfica independente do processamento principal:

```text
┌──────────────────────┐
│      Interface       │
│   Tkinter/ttkbootstrap│
└──────────┬───────────┘
           │
           ▼
        STATE
           ▲
           │
┌──────────┴───────────┐
│  Automação Principal │
└──────────────────────┘
```

O processamento executado em background não atualiza diretamente os componentes do Tkinter. As mensagens de log são encaminhadas através de uma `Queue` e processadas pela thread principal da interface.

Essa abordagem evita operações inseguras diretamente nos widgets do Tkinter.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia              | Utilização                                   |
| ----------------------- | -------------------------------------------- |
| Python                  | Linguagem principal                          |
| Pandas                  | Tratamento e transformação de dados          |
| Google Sheets / gspread | Controle e armazenamento operacional         |
| PostgreSQL              | Persistência e atualização dos agendamentos  |
| Requests                | Comunicação com APIs HTTP                    |
| Tkinter                 | Interface gráfica                            |
| ttkbootstrap            | Estilização da interface                     |
| Threading               | Execução de tarefas em background            |
| Queue                   | Comunicação segura entre threads e interface |
| PyInstaller             | Empacotamento da aplicação                   |
| Git                     | Controle de versão                           |

---

## 📁 Estrutura do projeto

```text
ul30-whatsapp-appointment-automation/
│
├── Arquivos/
│   ├── Erros/
│   │   └── telefones_para_revisao.xlsx
│   │
│   ├── Relatorios/
│   │   └── Historico_Geral.xlsx
│   │
│   └── confirmacao.csv
│
├── System/
│   ├── config.py
│   └── state.py
│
├── .gitignore
├── icon.ico
├── interface.py
├── interface.spec
├── requirements.txt
├── ui.py
├── ul30_diario.py
└── ul30_diario.spec
```

Os arquivos `credentials.json`, logs e outras informações sensíveis não fazem parte do repositório.

---

## 🔐 Segurança

Informações sensíveis utilizadas pela aplicação não devem ser versionadas no Git.

Entre elas:

* Credenciais de Service Account;
* Senhas de banco de dados;
* Tokens de APIs;
* IDs reais de clientes;
* Dados reais de pacientes.

Para o repositório de demonstração, foram utilizados dados fictícios.

Em um ambiente de produção, essas informações devem ser armazenadas através de mecanismos apropriados de configuração e gerenciamento de segredos.

---

## 🚀 Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/LeonardoAlmeida1/ul30-whatsapp-appointment-automation.git
cd ul30-whatsapp-appointment-automation
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as integrações

Para executar o sistema completo em um ambiente próprio, é necessário configurar:

* Credenciais do Google Sheets;
* Planilha utilizada pela aplicação;
* Banco PostgreSQL;
* Endpoint da API de mensagens;
* Identificador da clínica;
* Demais parâmetros específicos do ambiente.

As informações sensíveis devem permanecer fora do controle de versão.

---

## 📊 Fluxo operacional

O processo principal segue aproximadamente este fluxo:

```text
1. Iniciar aplicação
        ↓
2. Verificar cliente
        ↓
3. Ler agenda
        ↓
4. Processar dados
        ↓
5. Validar registros
        ↓
6. Agrupar pacientes
        ↓
7. Atualizar Google Sheets
        ↓
8. Enviar dados para API
        ↓
9. Aguardar retorno dos status
        ↓
10. Processar confirmações/cancelamentos
        ↓
11. Atualizar banco de dados
        ↓
12. Registrar histórico e logs
```

---

## 🧩 Decisões técnicas

Durante o desenvolvimento foram adotadas algumas decisões para melhorar a estabilidade da aplicação.

### Processamento em background

Operações que podem levar tempo são executadas utilizando `threading`, evitando o bloqueio da interface gráfica.

### Comunicação entre threads

Os logs produzidos pela automação são enviados para uma `Queue`.

A interface utiliza `after()` para consumir essas mensagens dentro da thread principal do Tkinter.

```text
Worker
  │
  ▼
Logger
  │
  ▼
Queue
  │
  ▼
Tkinter.after()
  │
  ▼
Interface
```

### Processamento em lotes

O envio dos pacientes para o servidor utiliza lotes de registros para reduzir o número de requisições individuais.

### Separação de estado e interface

O estado operacional do sistema foi separado dos componentes visuais da aplicação, reduzindo o acoplamento entre a automação e a interface gráfica.

---

## 🔄 Melhorias futuras

Possíveis evoluções do projeto:

* [ ] Centralizar configurações em arquivo seguro;
* [ ] Melhorar gerenciamento de credenciais;
* [ ] Implementar testes automatizados;
* [ ] Adicionar tratamento mais detalhado de erros de API;
* [ ] Implementar retry automático para falhas temporárias;
* [ ] Melhorar observabilidade e métricas;
* [ ] Criar camada de serviços para integrações externas;
* [ ] Separar módulos de banco, API e Google Sheets;
* [ ] Criar testes de integração;
* [ ] Melhorar o sistema de filas;
* [ ] Criar documentação técnica da API;
* [ ] Evoluir o dashboard com métricas operacionais.

---

## 📌 Status do projeto

**Projeto funcional / em evolução.**

Este repositório representa uma versão de demonstração baseada em uma automação desenvolvida para um cenário real de operação, com dados e identificadores substituídos para fins de portfólio.

O projeto continua em evolução com foco em:

* qualidade de código;
* arquitetura;
* segurança;
* testes;
* observabilidade;
* documentação;
* escalabilidade.

---

## 👨‍💻 Autor

**Leonardo Silva de Almeida**

Desenvolvedor Python Júnior com experiência em automação de processos, integração de sistemas, tratamento de dados e desenvolvimento de aplicações.

**Interesses profissionais:**

* Desenvolvimento Python;
* Automação de processos;
* Engenharia de dados;
* BI e análise de dados;
* Integração de APIs;
* Desenvolvimento de sistemas.

[GitHub](https://github.com/LeonardoAlmeida1)

[LinkedIn](https://www.linkedin.com/in/leonardo-silva-de-almeida-8416221b5/)