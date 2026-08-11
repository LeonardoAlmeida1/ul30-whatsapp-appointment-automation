# UL30 WhatsApp Appointment Automation

A Python-based process automation system designed to streamline appointment confirmation workflows by integrating data processing, Google Sheets, messaging APIs, and PostgreSQL.

The project was developed with a focus on **process automation, system integration, data processing, operational monitoring, and reduction of repetitive manual tasks**.

> **Note:** All data included in this repository is fictional and provided exclusively for demonstration and portfolio purposes. No real patient or company data is exposed.

---

## 🎯 Problem

Appointment confirmation processes can involve several repetitive manual tasks:

* Exporting appointment schedules;
* Cleaning and transforming data;
* Validating phone numbers;
* Identifying procedures;
* Grouping appointments by patient;
* Preparing messages;
* Tracking responses;
* Updating appointment statuses;
* Maintaining operational history.

These activities can consume significant time and increase the risk of operational errors.

---

## 💡 Solution

The UL30 WhatsApp Appointment Automation automates a significant part of this workflow.

The application processes appointment data, validates and transforms records, prepares the information for messaging, integrates with an external API, and monitors the resulting statuses.

Based on the returned status, the system can also update or move the corresponding appointment records in the PostgreSQL database.

---

## ⚙️ Main Features

### Data Processing

* CSV data ingestion using Pandas;
* Date and time normalization;
* Appointment filtering;
* Removal of records that should not participate in the process;
* Patient record validation;
* Phone number validation and normalization;
* Identification of invalid phone numbers;
* Generation of files containing invalid records for later review.

### Procedure Processing

The system identifies different types of procedures and generates an appropriate description for messaging.

Appointments can be formatted as:

```text
Consultation with Dr. Professional Name
```

while examinations can be represented as:

```text
Exam Procedure Name
```

Procedures are also grouped by patient record number to avoid sending multiple messages to the same patient.

### Google Sheets Integration

Google Sheets is used as an operational control layer for appointment records.

The workflow uses statuses such as:

```text
PENDING
QUEUED
SENT
DELIVERED
CONFIRMED
CANCELLED
ERROR
```

The system also maintains historical records before updating the operational spreadsheet.

### Batch Processing

Patient data is sent to the server in batches instead of making one request per patient.

The current batch size is:

```text
50 records per batch
```

### Database Integration

Based on the resulting appointment status, the application can perform different operations against the PostgreSQL database.

For example:

```text
CONFIRMED
    ↓
Update appointment

CANCELLED
    ↓
Move appointment
```

### Desktop Dashboard

The application includes a desktop interface built with Tkinter and ttkbootstrap.

The dashboard provides:

* Total patients;
* Confirmed appointments;
* Cancelled appointments;
* Pending appointments;
* Next synchronization countdown;
* System logs.

### Logging

The application includes structured logging with:

* Logs displayed in the desktop interface;
* File-based logging;
* Automatic log rotation;
* Historical log retention.

---

## 🏗️ Architecture

The main workflow can be represented as follows:

```text
┌──────────────────────┐
│  Clinic Appointment  │
│       Schedule       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Pandas         │
│   Data Processing    │
└──────────┬───────────┘
           │
           ├──────────────► Phone validation
           │
           ├──────────────► Patient validation
           │
           └──────────────► Procedure processing
           │
           ▼
┌──────────────────────┐
│    Google Sheets     │
│   Status Management  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Server / API    │
│      Messaging       │
└──────────┬───────────┘
           │
           ▼
      ┌─────────┐
      │ Patient │
      └────┬────┘
           │
           ▼
┌──────────────────────┐
│        Status        │
│ Confirmed / Cancelled│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      PostgreSQL      │
│ Appointment Updates  │
└──────────────────────┘
```

The application also separates the graphical interface from the main automation process:

```text
┌──────────────────────┐
│    Desktop UI        │
│   Tkinter/ttkbootstrap│
└──────────┬───────────┘
           │
           ▼
        Application
          State
           ▲
           │
┌──────────┴───────────┐
│ Automation Process   │
└──────────────────────┘
```

Background tasks are executed separately from the Tkinter main loop, while communication with the interface is handled through a controlled state and logging mechanism.

---

## 🛠️ Technologies

| Technology              | Purpose                            |
| ----------------------- | ---------------------------------- |
| Python                  | Main programming language          |
| Pandas                  | Data processing and transformation |
| Google Sheets / gspread | Operational data management        |
| PostgreSQL              | Database persistence               |
| Requests                | HTTP API communication             |
| Tkinter                 | Desktop graphical interface        |
| ttkbootstrap            | UI styling                         |
| Threading               | Background task execution          |
| Queue                   | Comunicação segura entre threads e interface |
| PyInstaller             | Application packaging              |
| Git                     | Version control                    |

---

## 📁 Project Structure

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

Sensitive credentials, logs, build artifacts, and other environment-specific files are excluded from version control.

---

## 🔐 Security

Sensitive information should never be committed to the repository.

This includes:

* Service account credentials;
* Database passwords;
* API tokens;
* Real client identifiers;
* Patient information.

The repository contains only fictional demonstration data.

In a production environment, credentials and secrets should be managed through appropriate configuration and secret-management mechanisms.

---

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/LeonardoAlmeida1/ul30-whatsapp-appointment-automation.git
cd ul30-whatsapp-appointment-automation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure integrations

To run the complete workflow in a custom environment, the following components must be configured:

* Google Sheets credentials;
* Google Spreadsheet;
* PostgreSQL database;
* Messaging API endpoint;
* Clinic identifier;
* Environment-specific parameters.

Sensitive configuration should remain outside version control.

---

## 🔄 Operational Flow

The main workflow follows these steps:

```text
1. Start application
        ↓
2. Validate client
        ↓
3. Read appointment data
        ↓
4. Process and clean data
        ↓
5. Validate records
        ↓
6. Group patient procedures
        ↓
7. Update Google Sheets
        ↓
8. Send data to API
        ↓
9. Monitor returned statuses
        ↓
10. Process confirmations/cancellations
        ↓
11. Update PostgreSQL
        ↓
12. Store history and logs
```

---

## 🧩 Technical Decisions

During development, certain decisions were made to improve the application's stability.

### Background Processing

Long-running operations are executed using background threads to prevent the graphical interface from becoming unresponsive.

### Thread-safe Logging

Log messages generated by background tasks are placed into a queue.Queue. The Tkinter event loop periodically consumes the queue using app.after(), preventing worker threads from directly manipulating UI widgets.

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

### Batch Processing

Patient records are sent to the server in batches, reducing the number of individual HTTP requests.

### Separation of State and UI

Application state is separated from the graphical interface components, reducing coupling between the automation logic and the UI.

### Logging and Monitoring

The system uses Python's logging infrastructure with separate handlers for file persistence and UI presentation.

Logs are rotated automatically and historical files are retained for operational troubleshooting.

---

## 🔄 Future Improvements

Possible future improvements include:

* [ ] Centralize application configuration;
* [ ] Improve credential management;
* [ ] Add automated tests;
* [ ] Implement retry strategies for temporary API failures;
* [ ] Improve API error handling;
* [ ] Add operational metrics;
* [ ] Further separate database, API, and Google Sheets services;
* [ ] Add integration tests;
* [ ] Improve queue management;
* [ ] Create API documentation;
* [ ] Improve dashboard analytics;
* [ ] Add structured configuration for different clients.

---

## 📌 Project Status

**Functional project / continuously evolving.**

This repository represents a demonstration version of an automation solution originally developed for a real operational scenario.

All company identifiers, credentials, and sensitive data have been replaced or removed for portfolio purposes.

The project is being continuously improved with a focus on:

* Code quality;
* Software architecture;
* Security;
* Testing;
* Observability;
* Documentation;
* Scalability.

---

## 👨‍💻 Author

**Leonardo Silva de Almeida**

Python Developer focused on **Automation and Data**, with hands-on experience in process automation, data processing, system integration, APIs, databases, and business intelligence.

### Career Focus

* Junior Python Developer
* Junior Data / BI Analyst
* Process Automation
* Data Analysis
* System Integration

🔗 [GitHub](https://github.com/LeonardoAlmeida1)

🔗 [LinkedIn](https://www.linkedin.com/in/leonardo-silva-de-almeida-8416221b5/)
