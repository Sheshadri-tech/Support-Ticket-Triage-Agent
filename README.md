# Support Ticket Triage Agent

An AI-powered support ticket classification and triage system that analyzes incoming support tickets, assigns a category and urgency, calculates priority, routes the ticket to the appropriate support team, and sends low-confidence tickets for human review.

---

## 1. Installation

### Prerequisites

Make sure the following are installed:

* Python 3.10 or higher
* Git
* pip
* Windows PowerShell / Command Prompt or a Linux/macOS terminal

### Clone the repository

```bash
git clone https://github.com/Sheshadri-tech/Support-Ticket-Triage-Agent.git
cd Support-Ticket-Triage-Agent
```

### Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Verify the installation

Run:

```bash
python --version
pip show fastapi
pip show uvicorn
```

The virtual environment should be active before running the application.

---

## 2. API Key Configuration

The current version of the project uses a local rule/logic-based triage engine and does **not require an external AI API key** to run the included demo.

Therefore, no OpenAI, Gemini, Anthropic, or other external API key is required for the current implementation.

The project can be executed locally without adding secrets or credentials.

If an external LLM provider is added in the future, API keys should be stored in environment variables rather than committed to GitHub.

Example:

```env
AI_API_KEY=your_api_key_here
```

Never commit `.env` files or API keys to the repository.

---

## 3. Run the Agent End to End

### Step 1 — Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### Step 2 — Start the FastAPI application

From the project root directory:

```bash
python -m uvicorn src.api:app --reload
```

The API will start at:

```text
http://127.0.0.1:8000
```

### Step 3 — Open the API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides an interactive Swagger UI where the complete agent can be tested.

### Step 4 — Verify the application

Open:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
  "message": "Support Ticket Triage Agent API",
  "status": "running",
  "version": "1.0.0"
}
```

### Step 5 — View processed tickets

Send:

```http
GET /tickets
```

This returns the processed ticket results.

### Step 6 — View tickets requiring human review

Send:

```http
GET /reviews
```

Low-confidence tickets are placed into the human-review workflow.

### Step 7 — Submit a new ticket

Use:

```http
POST /tickets/triage
```

Example request:

```json
{
  "ticket_id": "T006",
  "subject": "I cannot reset my password",
  "body": "The password reset email never arrives."
}
```

Example response:

```json
{
  "message": "Ticket triaged successfully",
  "result": {
    "ticket_id": "T006",
    "category": "Account Access",
    "urgency": "Medium",
    "confidence": 0.9,
    "routing_team": "Account Support",
    "human_review": false,
    "priority_score": 40,
    "priority_level": "Medium"
  }
}
```

### Step 8 — Review a low-confidence ticket

Tickets with low classification confidence are available through:

```http
GET /reviews
```

A reviewer can approve a ticket using:

```http
POST /reviews/{ticket_id}/approve?reviewer=human-agent
```

Example:

```text
POST /reviews/T005/approve?reviewer=human-agent
```

A ticket can also be rejected using:

```http
POST /reviews/{ticket_id}/reject
```

### Step 9 — View statistics

Use:

```http
GET /statistics
```

This provides:

* Total tickets
* Average confidence
* Number of tickets requiring human review
* Category distribution
* Urgency distribution
* Priority distribution

---

## 4. Design Choices

### FastAPI

FastAPI was selected to expose the triage engine through a lightweight REST API.

Benefits:

* Automatic API documentation
* Request validation
* Easy local testing
* Clear REST endpoints
* Good support for Python-based AI/ML services

### Pydantic Models

Pydantic models are used to validate incoming support tickets and structure triage results.

This prevents malformed ticket data from entering the processing pipeline.

### Modular Architecture

The application separates responsibilities into different modules:

```text
src/
├── api.py
├── config.py
├── ticket_model.py
├── triage_engine.py
├── priority.py
├── human_review.py
├── logger.py
└── process_tickets.py
```

The main responsibilities are separated as follows:

* `api.py` — REST API endpoints
* `ticket_model.py` — ticket and result data models
* `triage_engine.py` — ticket classification and triage logic
* `priority.py` — priority calculation
* `human_review.py` — human-review workflow
* `process_tickets.py` — ticket processing pipeline
* `config.py` — application configuration
* `logger.py` — application logging

### Confidence-Based Human Review

The system does not blindly accept every classification.

Tickets with low confidence are flagged for human review.

This provides a human-in-the-loop workflow:

```text
Support Ticket
      |
      v
Triage Engine
      |
      v
Classification
      |
      +------ High Confidence ------> Process Automatically
      |
      +------ Low Confidence -------> Human Review
                                         |
                              +----------+----------+
                              |                     |
                           Approve                Reject
```

### Priority Calculation

Priority is calculated separately from classification so that ticket severity and routing decisions remain modular.

The system considers the ticket's urgency and other triage information to produce:

* Priority score
* Priority level

### JSON-Based Persistence

The current implementation uses JSON files for storing processed results, human-review information, and statistics.

This keeps the project simple and easy for a reviewer to run locally without requiring database installation or configuration.

---

## 5. Sample Inputs and Outputs

The project was tested with multiple support-ticket examples covering different categories and confidence levels.

### Example 1 — Account Access

Input:

```json
{
  "ticket_id": "T001",
  "subject": "Unable to log in",
  "body": "I cannot access my account because I forgot my password and need access urgently."
}
```

Output:

```json
{
  "ticket_id": "T001",
  "category": "Account Access",
  "urgency": "High",
  "confidence": 0.9,
  "routing_team": "Account Support",
  "human_review": false,
  "priority_score": 70,
  "priority_level": "High"
}
```

### Example 2 — Billing

Input:

```json
{
  "ticket_id": "T002",
  "subject": "Charged twice",
  "body": "I was charged twice for the same subscription."
}
```

Output:

```json
{
  "ticket_id": "T002",
  "category": "Billing",
  "urgency": "Medium",
  "confidence": 0.9,
  "routing_team": "Billing Support",
  "human_review": false,
  "priority_score": 40,
  "priority_level": "Medium"
}
```

### Example 3 — Technical Issue

Input:

```json
{
  "ticket_id": "T003",
  "subject": "Application crashes",
  "body": "The application crashes whenever I upload a large PDF."
}
```

Output:

```json
{
  "ticket_id": "T003",
  "category": "Technical Issue",
  "urgency": "Medium",
  "confidence": 0.9,
  "routing_team": "Technical Support",
  "human_review": false,
  "priority_score": 40,
  "priority_level": "Medium"
}
```

### Example 4 — Account Management

Input:

```json
{
  "ticket_id": "T004",
  "subject": "Update profile name",
  "body": "I want to change the name displayed on my account."
}
```

Output:

```json
{
  "ticket_id": "T004",
  "category": "Account Access",
  "urgency": "Low",
  "confidence": 0.9,
  "routing_team": "Account Support",
  "human_review": false,
  "priority_score": 20,
  "priority_level": "Low"
}
```

### Example 5 — Ambiguous Ticket

Input:

```json
{
  "ticket_id": "T005",
  "subject": "Something is wrong",
  "body": "It is not working."
}
```

Output:

```json
{
  "ticket_id": "T005",
  "category": "Technical Issue",
  "urgency": "Medium",
  "confidence": 0.4,
  "routing_team": "Technical Support",
  "human_review": true,
  "priority_score": 60,
  "priority_level": "High"
}
```

Because the confidence is low, the ticket is placed into the human-review queue.

Example approval:

```text
POST /reviews/T005/approve?reviewer=human-agent
```

Result:

```json
{
  "message": "Ticket review approved successfully",
  "result": {
    "ticket_id": "T005",
    "review_status": "APPROVED",
    "reviewed_by": "human-agent"
  }
}
```

---

## 6. Tradeoffs and Limitations

### Current Approach

The current implementation prioritizes:

* Simple setup
* Easy reproducibility
* No external API dependency
* Fast local execution
* Clear modular architecture
* Human-in-the-loop handling
* Easy API testing

### Limitations

The current version has several limitations:

1. The triage logic is local and does not use a production-grade LLM.
2. JSON files are used instead of a production database.
3. Authentication and authorization are not implemented.
4. The system is designed primarily for demonstration and evaluation rather than high-volume production workloads.
5. Classification accuracy depends on the implemented classification rules.
6. The system does not currently include a frontend dashboard.
7. Review decisions are stored locally rather than in a centralized database.

### Improvements With More Time

A production version could be improved by adding:

* LLM-based classification
* PostgreSQL or another production database
* Authentication and role-based authorization
* Redis/Celery for asynchronous processing
* Docker containerization
* Production monitoring
* More sophisticated confidence scoring
* Automated evaluation metrics
* Frontend dashboard for support agents
* Model/version tracking
* Audit trails and persistent review history

---

## 7. Reproducibility

A reviewer can reproduce the project using the following sequence:

```bash
git clone https://github.com/Sheshadri-tech/Support-Ticket-Triage-Agent.git
cd Support-Ticket-Triage-Agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The complete API can be tested directly through the Swagger interface.

Run the automated tests with:

```bash
python -m pytest tests/test_api.py -v
```

Expected result:

```text
5 passed
```
