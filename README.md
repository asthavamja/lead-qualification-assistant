# Lead Qualification Assistant

A conversational assistant that answers project questions from an approved knowledge base, collects lead details, qualifies potential leads, and can notify a team through Slack.

## Features

- Streamlit chat interface
- LangGraph workflow for routing, qualification, Q&A, scoring, and handoff
- Retrieval-augmented answers using a Chroma vector store and Hugging Face embeddings
- SQLite for structured company information
- CSV lead export and optional Slack lead notifications

## Requirements

- Python 3.10 or later
- A Groq API key
- Optional: a Slack incoming webhook URL for lead notifications

## Setup

Run these commands from the `phase_9` project folder in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```dotenv
GROQ_API_KEY=your_groq_api_key
SLACK_LEADS_WEBHOOK=your_slack_incoming_webhook_url
```

`SLACK_LEADS_WEBHOOK` is optional if you do not need Slack notifications. The model names can also be customized with `GROQ_MODEL` and `GROQ_REPLY_MODEL`; otherwise, the app uses its defaults.

## Initialize the data

Create or refresh the SQLite database from the supplied schema and seed data:

```powershell
python docs/database/setup_db.py
```

Build the local Chroma knowledge index:

```powershell
python rag.py
```

The first index build downloads the configured embedding model. The generated database and Chroma files are local data and are excluded from Git.

## Run the app

```powershell
streamlit run app.py
```

Streamlit prints a local URL in the terminal; open it in your browser to use the assistant.

## Project files

- `app.py` — Streamlit user interface
- `lead_qualification_workflow.py` — LangGraph conversation workflow
- `qualifying.py` — routing, qualification, and scoring logic
- `qa_test.py` — retrieval-backed question answering
- `rag.py` — knowledge-index builder
- `company_data.py` — structured SQLite data access
- `leads.py` — lead CSV persistence
- `slack_alert.py` — Slack notification formatting and delivery
- `docs/technova_knowledge_base.md` — retrieval knowledge source
- `docs/database/` — SQLite schema, seed data, and setup script

See [`docs/README.md`](docs/README.md) for guidance on maintaining the knowledge sources and structured data.
