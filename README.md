# AI Customer Support Ticket Resolution (OpenEnv)

An AI-powered support ticket system using AWS Bedrock for automatic ticket classification and resolution suggestions.

## Features

- **AI Classification** — Automatically categorizes tickets (billing, technical, account, shipping, general)
- **Priority Detection** — AI assigns priority (low / medium / high / critical)
- **Resolution Suggestions** — AI generates resolution drafts using AWS Bedrock (Titan)
- **Confidence Scoring** — High-confidence tickets auto-resolve; low-confidence tickets route to agent review
- **Agent Workflow** — Agents can review, add notes, override AI, and close tickets
- **Live Stats Dashboard** — Real-time metrics on resolution rates and ticket distribution

## Architecture

```
Customer → Submit Ticket → AI Engine (AWS Bedrock)
                               ↓
                    Classify + Generate Resolution
                               ↓
              confidence ≥ 0.8 → ai_resolved
              confidence < 0.8 → agent_review
                               ↓
                    Agent Reviews & Closes
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

### 3. AWS Bedrock Setup
- Enable **Amazon Titan Text Express** model in AWS Bedrock console
- Ensure your IAM user/role has `bedrock:InvokeModel` permission

### 4. Run
```bash
python main.py
```

Open http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tickets` | Submit new ticket (triggers AI analysis) |
| GET | `/tickets` | List tickets (filter by status/priority) |
| GET | `/tickets/{id}` | Get ticket details |
| PATCH | `/tickets/{id}` | Update ticket (agent actions) |
| DELETE | `/tickets/{id}` | Delete ticket |
| GET | `/stats` | Dashboard statistics |

## Project Structure

```
├── main.py          # FastAPI app & routes
├── ai_engine.py     # AWS Bedrock AI classification & resolution
├── models.py        # Pydantic data models
├── index.html       # Frontend UI
├── tickets.json     # Ticket storage
├── .env.example     # Environment config template
└── requirements.txt
```
