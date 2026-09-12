# Flowise bootstrap

`bootstrap_flowise.py` creates or updates the three course Chatflows through
Flowise's authenticated API. It expects an exported Flowise RAG template so
the node schema matches the installed Flowise release.

Export a template from Flowise and run a safe graph-only check first:

```bash
FLOWISE_QDRANT_CREDENTIAL_ID=qdrant-credential-id \
python3 flowise/bootstrap_flowise.py \
  --template flowise/Conversational-Retrieval-QA-Chain.json --dry-run
```

For a real update, provide an API token and existing encrypted Credential IDs.
The model and Qdrant secrets must remain in Flowise credentials or the Model
Gateway environment, never in the exported `flowData`:

```bash
FLOWISE_BASE_URL=http://127.0.0.1:3000 \
FLOWISE_API_TOKEN='provided-out-of-band' \
FLOWISE_OPENAI_CREDENTIAL_ID='...' \
FLOWISE_QDRANT_CREDENTIAL_ID='...' \
python3 flowise/bootstrap_flowise.py \
  --template flowise/Conversational-Retrieval-QA-Chain.json
```

Flowise documents `POST /chatflows`, `PUT /chatflows/{id}` and
`POST /prediction/{id}` as API operations. The bootstrap is idempotent by
Chatflow name, marks only the three prediction flows public for the browser,
and does not expose the Flowise administration route through Caddy.
