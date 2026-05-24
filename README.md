# NL-to-SQL Data Agent

Natural Language to SQL (NL2SQL) application built for the Data Agents Software Developer take-home assignment.

The system allows users to ask questions in natural language, automatically generates SQL against a SQLite database, executes the query, and returns the results while enforcing strict department-level access controls.

---

# Key Features

- Natural Language → SQL using Llama 3.1
- SQLite query execution
- Mandatory department-level guardrails
- SQL validation before execution
- Automatic SQL repair and retry
- Console application
- Lightweight web application
- Local LLM execution through Ollama
- LangGraph workflow orchestration

---

# Problem Statement

The application allows users to query employee information using natural language instead of writing SQL manually.

Example questions:

```text
Who are the software engineers?

Which employees have AWS certification?

What is the average salary?

Who has the highest remaining benefits balance?

List employees who started after 2023 and their certifications.
```

The system:

1. Converts natural language into SQL
2. Validates generated SQL
3. Executes the query against SQLite
4. Returns formatted results

---

# Security Guardrail

When the application starts, a department is randomly selected:

```text
Sales
Marketing
Engineering
```

Example:

```text
[INFO] Department selected: Engineering
```

Every generated SQL query must contain:

```sql
Department = 'Engineering'
```

(or the selected department)

This guardrail is enforced through:

1. Prompt instructions
2. SQL validation
3. SQL repair before execution

This guarantees that data from other departments is never returned.

---

# Architecture

The final architecture prioritizes simplicity, reliability, and low latency.

```text
User Question
        ↓
SQL Generator (Llama 3.1)
        ↓
SQL Validator
        ↓
   +------------+
   |            |
 Valid      Invalid
   |            |
   |            ↓
   |      SQL Repair Agent
   |            |
   +------------+
        ↓
SQLite Execution
        ↓
Answer Formatter
        ↓
Response
```

---

# Components

## SQL Generator

Uses Llama 3.1 running locally through Ollama.

Responsibilities:

- Natural language understanding
- SQL generation
- Join generation
- Department filter enforcement

## SQL Validator

Validates:

- SELECT-only queries
- Department guardrail presence
- Allowed tables
- Safe SQL execution

## SQL Repair Agent

Automatically repairs:

- Missing department filters
- Invalid joins
- Invalid aliases
- Incorrect column references

## SQLite Database

Contains:

### Employee

- Employee details
- Salary
- Bonus
- Start date

### Certification

- Employee certifications
- Certification dates

### Benefits

- Benefits packages
- Remaining balances

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Language | Python 3.11 |
| LLM | Llama 3.1 |
| Local Model Runtime | Ollama |
| Workflow | LangGraph |
| LLM Framework | LangChain |
| Database | SQLite |
| Backend API | FastAPI |
| Frontend | HTML / CSS / JavaScript |

---

# Project Structure

```text
NLtoSql_project/

├── employees.db
├── README.md
├── DOC.md
├── requirements.txt

├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js

└── src/
    ├── api.py
    ├── main.py
    ├── graph.py
    ├── prompts.py
    ├── guardrails.py
    ├── db.py
    ├── state.py
    └── config.py
```

---

# Setup

## 1. Clone Repository

```bash
git clone <repository-url>
cd NLtoSql_project
```

## 2. Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Install Ollama

Download:

https://ollama.com

## 5. Pull Llama 3.1

```powershell
ollama pull llama3.1
```

Verify:

```powershell
ollama list
```

---

# Running the Console Application

Start Ollama:

```powershell
ollama serve
```

Run:

```powershell
python src/main.py
```

Example:

```text
[INFO] Department selected: Engineering

Ask a question:
Who are the software engineers?
```

---

# Running the Web Application

## Terminal 1 – Ollama

```powershell
ollama serve
```

## Terminal 2 – FastAPI Backend

```powershell
cd src

uvicorn api:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Terminal 3 – Frontend

```powershell
cd frontend

python -m http.server 5500
```

Frontend:

```text
http://localhost:5500
```

---

# API Endpoints

## Health Check

```http
GET /
```

Example response:

```json
{
  "status": "ok",
  "department": "Engineering"
}
```

---

## Ask a Question

```http
POST /ask
```

Request:

```json
{
  "question": "Who are the software engineers?"
}
```

Response:

```json
{
  "department": "Engineering",
  "sql": "SELECT Name FROM Employee WHERE Department='Engineering' AND Role='Software Engineer';",
  "answer": "..."
}
```

---

# Evaluation Approach

The system was evaluated using a benchmark dataset covering:

- Employee lookups
- Certifications
- Benefits
- Salary analytics
- Date filters
- Aggregations
- Multi-table joins

Metrics:

| Metric | Description |
|----------|-------------|
| SQL Validity | SQL syntax correctness |
| Guardrail Compliance | Department filter enforcement |
| Execution Success | Successful SQL execution |
| Result Accuracy | Business correctness |

Evaluation findings drove several improvements:

- Better schema grounding
- Improved certification matching
- Stronger validation
- SQL repair workflow
- Simplified architecture for lower latency
---

# Design Decisions

## Why Local LLM?

Benefits:

- No API costs
- Offline execution
- Easy reproducibility
- Fast iteration

## Why LangGraph?

Provides a clean workflow separating:

- Generation
- Validation
- Repair
- Execution

## Why Validation + Repair?

LLMs occasionally generate:

- Missing filters
- Invalid joins
- Incorrect columns

Validation and repair improve reliability while maintaining 100% guardrail compliance.

---

# Future Improvements

Potential next steps:

- Prompt caching
- SQL result caching
- Intent-specific prompting
- Observability dashboards
- Automated regression testing
- Fine-tuned NL-to-SQL models
- AgentOps tracing and monitoring

---

# Author

**Narges Vahdani**

Built for the Data Agents Software Developer take-home assignment.