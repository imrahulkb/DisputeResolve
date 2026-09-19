# BillResolve — AI-Powered Billing Dispute Resolution Engine

## Project Goal

BillResolve is a full-stack billing dispute resolution system that **detects, classifies, and deterministically resolves** billing disputes using a sophisticated 4-layer LLM pipeline. The system is engineered for real-world billing operations, combining LLM reasoning with deterministic execution for auditable, scalable dispute resolution.

**Core Objective:** Reduce manual dispute handling by 80%, achieve 95%+ resolution accuracy, and provide deterministic, auditable dispute resolution with real-time visibility.

---

## Architecture Overview

BillResolve operates as a **4-layer LLM pipeline** that separates reasoning (Layers 1-3) from deterministic execution (Layer 4):

```
┌──────────────────────────────────────────────────────┐
│      Natural Language Dispute Input                  │
│   "Customer claims they were overcharged for API use"│
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
            ╔══════════════════════════════════════╗
            ║  REASONING PHASE (Layers 1-3)        ║
            ║  Generate structured resolution plan ║
            ╚══════════════════════════════════════╝
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌─────────────┐ ┌──────────────┐ ┌───────────┐
    │   Layer 1   │ │   Layer 2    │ │  Layer 3  │
    │   INTENT    │─▶│   POLICY     │─▶│RESOLUTION│
    │ DETECTION   │ │  RETRIEVAL   │ │    PLAN   │
    │             │ │  (RAG)       │ │   (DSL)   │
    └─────────────┘ └──────────────┘ └───────────┘
         • Type        • Vector search   • Pydantic
         • Severity    • Top 3 policies  • Step DSL
         • Confidence  • ChromaDB        • Preconditions
                                         • Expected output
                           │
                           ▼
    ┌──────────────────────────────────────────────────┐
    │  Structured Resolution Plan (Pydantic DSL)       │
    │  [                                               │
    │    {"step": "verify_charge", "precondition": ...}│
    │    {"step": "apply_credit", "amount": 150.00}, │
    │    {"step": "notify_customer"},                 │
    │    {"step": "escalate_to_human" if risky}      │
    │  ]                                               │
    └──────────────────────────────────────────────────┘
                           │
            ╔══════════════════════════════════════╗
            ║  EXECUTION PHASE (Layer 4)           ║
            ║  Deterministic, no LLM in the loop   ║
            ╚══════════════════════════════════════╝
                           │
                           ▼
            ┌──────────────┬──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌─────────────┐ ┌──────────────┐ ┌───────────┐
    │  Execute    │ │  State       │ │ Real-time │
    │  DSL Steps  │ │  Machine     │ │   SSE     │
    │             │ │  Sequential  │ │ Status    │
    │             │ │  Execution   │ │ Updates   │
    └─────────────┘ └──────────────┘ └───────────┘
         • Verify       • Step tracking  • Client feed
         • Apply        • Precondition   • Failure reason
         • Notify         checks         • Audit trail
         • Escalate    • Halt on error
                           │
                           ▼
                 ┌───────────────────┐
                 │  RESOLUTION       │
                 │  COMPLETE         │
                 │  (Refund issued,  │
                 │  escalated, or    │
                 │  approved)        │
                 └───────────────────┘
```

### Layer Details

| Layer | Purpose | Tech | Primary Function |
|-------|---------|------|------------------|
| **1: Intent Detection** | Parse natural language dispute, extract type & severity | LangChain + GPT-4o-mini + Pydantic | User input → Structured intent |
| **2: Policy Retrieval (RAG)** | Vector search over billing policies → Top 3 relevant chunks | ChromaDB + OpenAI Embeddings + LangChain | Intent → Applicable policies |
| **3: Resolution Plan (DSL)** | LLM generates typed, executable resolution plan | Pydantic DSL + LangChain Structured Output | Policies → Resolution steps |
| **4: Deterministic Execution** | Execute each DSL step, emit status events, halt on failure | FastAPI SSE + Python State Machine | Steps → Real-time execution |

## API Contract

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Submit Dispute (Natural Language)

#### POST `/disputes/submit`
User submits a dispute in natural language. Triggers full 4-layer pipeline.

**Request:**
```json
{
  "customerId": "CUST-12345",
  "invoiceId": "INV-2026-04-001",
  "description": "I was charged $5000 for API usage this month, but I never made any API calls. Last month was only $50. This looks like an overcharge.",
  "attachments": []
}
```

**Response:**
```json
{
  "disputeId": "DISP-2026-04-001",
  "status": "PROCESSING",
  "pipelineId": "PIPE-2026-04-001",
  "statusUrl": "/disputes/DISP-2026-04-001/status"
}
```

---

### 2. Retrieve Dispute Status & Plan

#### GET `/disputes/{disputeId}`
Retrieve full dispute details, classification, and resolution plan.

**Response:**
```json
{
  "disputeId": "DISP-2026-04-001",
  "customerId": "CUST-12345",
  "invoiceId": "INV-2026-04-001",
  "status": "RESOLVED",
  "createdAt": "2026-04-21T10:15:00Z",
  "resolvedAt": "2026-04-21T10:17:30Z",
  
  "layer1_intent": {
    "type": "OVERCHARGE",
    "severity": "HIGH",
    "confidence": 0.96,
    "description": "User claims erroneous charge for unused API service"
  },
  
  "layer2_policies": [
    {
      "policyId": "POL-API-001",
      "title": "API Overcharge Procedure",
      "relevanceScore": 0.98,
      "summary": "If usage is zero but charges appear, automatic refund applies."
    },
    {
      "policyId": "POL-API-002",
      "title": "Billing Reconciliation Process",
      "relevanceScore": 0.85,
      "summary": "Cross-check billing logs with usage logs; apply credits if mismatch found."
    }
  ],
  
  "layer3_plan": {
    "steps": [
      {
        "stepId": 1,
        "action": "verify_charge",
        "parameters": {
          "invoiceId": "INV-2026-04-001",
          "checkUsageLogs": true
        },
        "precondition": "Invoice must exist",
        "expectedOutput": "Verification result"
      },
      {
        "stepId": 2,
        "action": "apply_credit",
        "parameters": {
          "amount": 4950.00,
          "reason": "Erroneous charge — zero API usage detected",
          "creditsToCustomerAccount": true
        },
        "precondition": "verification_result.chargeIsErroneous == true",
        "expectedOutput": "Credit issued"
      },
      {
        "stepId": 3,
        "action": "notify_customer",
        "parameters": {
          "template": "OVERCHARGE_RESOLVED",
          "creditAmount": 4950.00
        },
        "precondition": "credit applied",
        "expectedOutput": "Email sent"
      }
    ]
  },
  
  "layer4_execution": {
    "status": "COMPLETE",
    "executedAt": "2026-04-21T10:17:30Z",
    "stepResults": [
      {
        "stepId": 1,
        "action": "verify_charge",
        "status": "SUCCESS",
        "result": {
          "chargeIsErroneous": true,
          "usageFound": 0,
          "chargedAmount": 5000.00
        }
      },
      {
        "stepId": 2,
        "action": "apply_credit",
        "status": "SUCCESS",
        "result": {
          "creditApplied": true,
          "creditId": "CREDIT-2026-04-001",
          "amount": 4950.00
        }
      },
      {
        "stepId": 3,
        "action": "notify_customer",
        "status": "SUCCESS",
        "result": {
          "emailSent": true,
          "timestamp": "2026-04-21T10:17:25Z"
        }
      }
    ]
  },
  
  "resolution": {
    "type": "REFUND",
    "amount": 4950.00,
    "creditId": "CREDIT-2026-04-001",
    "reason": "Erroneous charge — zero API usage"
  }
}
```

---

### 3. Real-Time Status Stream (SSE)

#### GET `/disputes/{disputeId}/stream`
Subscribe to real-time execution status via Server-Sent Events.

**Example Event Stream:**
```
event: layer1_complete
data: {"type": "OVERCHARGE", "severity": "HIGH", "confidence": 0.96}

event: layer2_complete
data: {"policiesFound": 3, "topPolicy": "POL-API-001"}

event: layer3_complete
data: {"stepsGenerated": 3, "estimatedDuration": "30s"}

event: layer4_step_start
data: {"stepId": 1, "action": "verify_charge"}

event: layer4_step_complete
data: {"stepId": 1, "status": "SUCCESS", "result": {...}}

event: layer4_complete
data: {"status": "RESOLVED", "resolution": "REFUND", "amount": 4950.00}
```

---

### 4. Batch Submit Disputes

#### POST `/disputes/batch-submit`
Submit multiple disputes at once.

**Request:**
```json
{
  "disputes": [
    {
      "customerId": "CUST-12345",
      "invoiceId": "INV-2026-04-001",
      "description": "Overcharge on API usage..."
    },
    {
      "customerId": "CUST-12346",
      "invoiceId": "INV-2026-04-002",
      "description": "Missing credit for annual plan discount..."
    }
  ]
}
```

**Response:**
```json
{
  "batchId": "BATCH-2026-04-001",
  "totalDisputesSubmitted": 2,
  "disputes": [
    {
      "disputeId": "DISP-2026-04-001",
      "status": "PROCESSING"
    },
    {
      "disputeId": "DISP-2026-04-002",
      "status": "PROCESSING"
    }
  ]
}
```

---

### 5. Manual Review Endpoint (Escalations)

#### POST `/disputes/{disputeId}/escalate`
Manually escalate dispute to human review.

**Request:**
```json
{
  "reason": "High dollar amount — requires approval",
  "assignedTo": "agent@company.com"
}
```

**Response:**
```json
{
  "disputeId": "DISP-2026-04-001",
  "status": "ESCALATED",
  "escalatedAt": "2026-04-21T10:20:00Z",
  "assignedTo": "agent@company.com"
}
```

---

### 6. Dispute Analytics

#### GET `/analytics/dashboard`
High-level metrics and system health.

**Response:**
```json
{
  "period": {
    "startDate": "2026-04-21",
    "endDate": "2026-04-21"
  },
  "metrics": {
    "totalDisputesSubmitted": 450,
    "resolvedAutomatically": 425,
    "escalatedToHuman": 25,
    "autoResolutionRate": 0.944,
    "avgResolutionTimeSec": 2.3,
    "totalCreditsIssued": 45000.00,
    "topDisputeTypes": [
      { "type": "OVERCHARGE", "count": 200 },
      { "type": "WRONG_PLAN", "count": 120 }
    ]
  }
}
```

---

## Technology Stack

- **Runtime:** Python 3.11+
- **Framework:** FastAPI (REST + SSE)
- **LLM & Reasoning:** LangChain + OpenAI GPT-4o-mini
- **Vector DB & RAG:** ChromaDB + OpenAI Embeddings
- **Data Validation:** Pydantic (DSL schemas)
- **State Management:** Python StateMachine
- **ORM:** SQLAlchemy (database modeling & queries)
- **Database:** PostgreSQL (dispute history, audit logs)
- **Cache:** Redis (policy cache, session state)
- **Task Queue:** Celery + Redis (async pipeline processing)
- **Monitoring:** Prometheus + Grafana / OpenTelemetry
- **Testing:** pytest + Mock LLM responses

---

## Project Structure

```
BillResolve/
├── src/
│   ├── app.py                          # FastAPI application
│   ├── config.py                       # Configuration & env vars
│   ├── models/
│   │   ├── dispute.py                  # Dispute entity
│   │   ├── resolution.py               # Resolution plan DSL
│   │   └── event.py                    # Domain events
│   ├── layers/
│   │   ├── layer1_intent_detector.py   # Layer 1: Intent detection
│   │   ├── layer2_policy_retriever.py  # Layer 2: RAG engine
│   │   ├── layer3_plan_generator.py    # Layer 3: DSL generation
│   │   └── layer4_executor.py          # Layer 4: Deterministic execution
│   ├── services/
│   │   ├── dispute_service.py          # Orchestrates pipeline
│   │   ├── rag_service.py              # RAG initialization & search
│   │   └── billing_service.py          # Mock billing data access
│   ├── repository/
│   │   └── dispute_repository.py       # PostgreSQL persistence
│   ├── api/
│   │   ├── routes.py                   # API endpoints
│   │   └── schemas.py                  # Request/response DTOs
│   ├── state_machine/
│   │   └── dispute_state_machine.py    # Pipeline state machine
│   ├── events/
│   │   └── sse_events.py               # SSE event streaming
│   ├── policies/                       # Billing policy knowledge base
│   │   └── api_policies.md
│   │   └── refund_policies.md
│   └── tests/
│       ├── test_layer1.py
│       ├── test_layer2.py
│       ├── test_layer3.py
│       ├── test_layer4.py
│       └── fixtures/
│           ├── mock_disputes.json
│           └── mock_policies.json
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # PostgreSQL, Redis, ChromaDB
├── .env.example                        # Environment variables template
├── README.md                           # This file
├── SETUP.md                            # Detailed setup guide
└── DATABASE_SCHEMA.sql                 # PostgreSQL schema
```

---

## Quick Start

```bash
# 1. Clone and install dependencies
git clone <repo>
cd BillResolve
pip install -r requirements.txt

# 2. Start services (PostgreSQL, Redis, ChromaDB)
docker-compose up -d

# 3. Initialize database and vector store
python -m scripts.init_db
python -m scripts.load_policies

# 4. Run the application
uvicorn src.app:app --reload --port 8000

# 5. Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## Pipeline Flow Example

**User Input:**
```
"I was charged $5000 for API usage this month, but I never made any API calls."
```

**Layer 1 Output (Intent):**
```json
{
  "type": "OVERCHARGE",
  "severity": "HIGH",
  "confidence": 0.96
}
```

**Layer 2 Output (Policies):**
```json
[
  "POL-API-001: Zero Usage = Automatic Refund",
  "POL-API-002: Usage Log Reconciliation",
  "POL-ESCALATE-001: High Dollar Amounts Require Approval"
]
```

**Layer 3 Output (Plan):**
```json
{
  "steps": [
    {"action": "verify_charge", "check": "usage vs. billing"},
    {"action": "apply_credit", "amount": 4950.00},
    {"action": "notify_customer"},
    {"action": "create_audit_log"}
  ]
}
```

**Layer 4 Output (Execution):**
```json
{
  "status": "COMPLETE",
  "steps_executed": 4,
  "resolution": {"type": "REFUND", "amount": 4950.00},
  "auditTrail": [...]
}
```

---

## Key Features

✅ **Natural Language Input** — Customers describe disputes; LLM understands context  
✅ **Policy-Driven Resolution** — RAG retrieves applicable policies every time  
✅ **Deterministic Execution** — No randomness after Layer 3; auditable step-by-step  
✅ **Real-Time Status** — SSE streaming shows progress in real-time  
✅ **Automatic Escalation** — High-confidence disputes resolve instantly; others escalate  
✅ **Full Audit Trail** — Every step, decision, and outcome is logged  
✅ **Batch Processing** — Submit multiple disputes; process in parallel via Celery  

---

## Status

🚧 **Under Development** — Layers 1-4 to be implemented sequentially.

---

## Contributing

See [SETUP.md](./SETUP.md) for development environment setup.

