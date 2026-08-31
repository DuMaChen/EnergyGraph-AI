# iFlytek Xingchen (讯飞星辰) Workflow Integration Guide

> Configuration, prompt architecture, and streaming protocol for iFlytek Xingchen Workflow RAG.

---

## 1. Workflow Architecture

The iFlytek Xingchen Workflow acts as the primary AI engine for EnergyGraph-AI:
- **Platform**: iFlytek Xingchen Agent & Workflow Engine.
- **Protocol**: OpenAI-compatible / custom chat completions HTTP endpoint with streaming chunk support.
- **Inputs**: `AGENT_USER_INPUT` (student query), user role, course context, and chat history.
- **Knowledge Base**: 20 courseware documents pre-ingested into the Xingchen Knowledge Base.

---

## 2. Environment Variables Configuration

Set in production `deploy/.env` (never commit):

```text
XINGCHEN_WORKFLOW_URL=https://xingchen-api.xf-yun.com/workflow/v1/chat/completions
XINGCHEN_FLOW_ID=your-xingchen-flow-id
XINGCHEN_API_KEY=your-api-key
XINGCHEN_API_SECRET=your-api-secret
XINGCHEN_INPUT_NAME=AGENT_USER_INPUT
XINGCHEN_TIMEOUT_SECONDS=90
```

---

## 3. Preflight Audit & Verification

Before deployment, run the preflight verification script to test live connectivity and citation compliance:

```bash
bash scripts/real_workflow_preflight.sh deploy/.env
```
