# RevenueOS-AI

## Autonomous Merchant Risk Investigation & Human Review Platform

RevenueOS-AI is an AI-assisted merchant risk investigation platform that moves beyond simple risk scoring. It takes a merchant through **risk assessment → decision → investigation → recommended action → human review → audit** in a closed-loop workflow.

## Problem

A risk score can identify that a merchant may be risky, but it does not by itself explain why the merchant is risky, what evidence supports the risk, what action should be taken, or whether that action should be automated or reviewed by a human.

RevenueOS-AI addresses this by combining risk assessment, investigation agents, evidence analysis, action policy, human review, case management, and audit logging.

## Solution

```text
Merchant Data
     ↓
Risk Assessment
     ↓
Decision Agent
     ↓
Investigation Agent
     ↓
Evidence Analysis
     ↓
Confidence Scoring
     ↓
Action Policy
     ↓
Human Review (when required)
     ↓
Case Management
     ↓
Audit Logging
```

## Key Features

- **Risk Assessment** using risk scores, risk categories, and transaction failure behaviour.
- **Decision Agent** producing `NO_ACTION`, `MONITOR`, `INVESTIGATE`, or `ESCALATE`.
- **Autonomous Investigation** using merchant profile, failure, payment-method, hourly, and transaction analysis tools.
- **Evidence-Based Findings** identifying failure reasons, problematic payment methods, and time-based patterns.
- **Confidence Scoring** for investigation results.
- **Human-in-the-Loop Control** for critical escalation cases.
- **Case Management** with case IDs and lifecycle status.
- **Audit Trail** covering risk, decision, investigation, action, case, and review events.
- **Interactive Streamlit Dashboard** with risk queue, case details, investigation evidence, review controls, and audit information.

## Decision Policy

The current policy uses this hierarchy:

1. Critical risk → `ESCALATE`
2. High risk → `INVESTIGATE`
3. Failure rate ≥ 10% → `INVESTIGATE`
4. Medium risk → `MONITOR`
5. Failure rate ≥ 5% → `MONITOR`
6. Otherwise → `NO_ACTION`

Both `INVESTIGATE` and `ESCALATE` trigger investigation. Critical escalation cases additionally require human approval.

## Example

### Critical Merchant — M00005

```text
Risk Score: 100.00
Risk Category: Critical
Failure Rate: 11.50%

Decision: ESCALATE
Confidence: 100 / HIGH
Human Approval: REQUIRED
```

Example findings:

- Dominant failure reason: Insufficient Funds
- Highest payment-method failure rate: Net Banking
- Highest failure rate occurs around 3:00

### High-Risk Merchant — M00007

```text
Risk Score: 62.68
Risk Category: High
Failure Rate: 11.40%

Decision: INVESTIGATE
Confidence: 85 / HIGH
Human Approval: NOT REQUIRED
```

## Evaluation

RevenueOS-AI was evaluated against 20 defined evaluation cases.

| Metric | Result |
|---|---:|
| Decision Accuracy | 100% |
| False Negative Rate | 0% |
| False Positive Rate | 0% |
| Investigation Coverage | 100% |
| Investigation Quality | 100% |
| Risk-Weighted Score | 100% |
| Overall Agent Score | 100% |

These results represent **decision-policy compliance across the defined 20-case evaluation set**, not 100% generalization accuracy of an ML model.

## Architecture

```text
                    RevenueOS-AI
                         │
                  ┌──────▼──────┐
                  │ Risk        │
                  │ Assessment  │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Decision    │
                  │ Agent       │
                  └──────┬──────┘
                         │
              INVESTIGATE / ESCALATE
                         │
                  ┌──────▼──────┐
                  │ Investigation│
                  │ Agent        │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Evidence    │
                  │ Analyzer     │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Confidence  │
                  │ Scorer      │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Action      │
                  │ Policy      │
                  └──────┬──────┘
                         │
                ┌────────┴────────┐
                │                 │
          Human Review       Automated Path
                │                 │
                └────────┬────────┘
                         │
                  ┌──────▼──────┐
                  │ Case        │
                  │ Manager     │
                  └──────┬──────┘
                         │
                  ┌──────▼──────┐
                  │ Audit       │
                  │ Logger      │
                  └─────────────┘
```

## Technology Stack

- Python
- FastAPI
- Streamlit
- Pandas
- Scikit-learn
- Pydantic
- Requests
- Uvicorn

## Project Structure

```text
RevenueOS-AI/
├── data/
├── docs/
├── evaluation/
├── models/
├── notebooks/
├── src/
│   ├── agents/
│   ├── services/
│   ├── tools/
│   ├── api.py
│   └── streamlit_app.py
├── tests/
├── .gitignore
├── app.py
├── Readme.md
└── requirements.txt
```

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
python -m uvicorn src.api:app --reload
```

Start the Streamlit dashboard in another terminal:

```bash
streamlit run src/streamlit_app.py
```

## API Endpoints

```text
GET  /
GET  /health
GET  /cases
GET  /cases/{case_id}
GET  /merchant/{merchant_id}

POST /review/{review_id}/approve
POST /review/{review_id}/reject
POST /review/{review_id}/hold
```

## Security

Environment variables and secrets belong in `.env` and should never be committed to GitHub. The repository `.gitignore` excludes `.env`.

## Buildathon Demo

The demonstration focuses on a critical merchant moving through:

```text
Risk Detection
     ↓
AI Decision
     ↓
Investigation
     ↓
Evidence
     ↓
Human Review
     ↓
Approval
     ↓
Audit Trail
```

Primary demo merchant: `M00005`.

## Status

**Functional prototype**

The core risk decision, investigation, action, human-review, case-management, audit, API, dashboard, and evaluation workflows have been implemented and tested locally.
