# Finance App LLM Processor

A Python service that categorizes finance transactions with Azure OpenAI and exchanges jobs and results with the backend through RabbitMQ queues.

## Request flow

```text
Backend -> request queue -> LLM processor -> result queue -> Backend
                                  |                            |
                                  v                            v
                              Azure OpenAI             applies categories
```

The backend publishes PDF imports to `financeapp.transactions.pdf.requests`. The processor submits the PDF to an Azure OpenAI vision capable deployment using the Responses API, requests strict statement JSON, and publishes the result to `financeapp.transactions.pdf.results`. The backend checks amounts against any statement totals, creates transactions, and then publishes the existing category matching request. PDF extraction requires a deployment that accepts PDF file input and structured outputs. PDFs are limited to 10 MB, and uploaded statement bytes travel through RabbitMQ; restrict broker access accordingly.

The backend publishes matching jobs to `financeapp.transactions.match.requests`. The processor validates each job and publishes the transaction-to-category mapping in its result message on `financeapp.transactions.match.results`. The backend applies and saves those categories on the transactions. Invalid request messages are routed to their respective dead letter queues.

Producers publish directly to named queues through RabbitMQ's default exchange; there are no custom exchanges or bindings. `/wakeup` is a liveness endpoint.

## Run locally

Install [uv](https://docs.astral.sh/uv/) and the Python version declared in `pyproject.toml`, then:

```bash
uv sync
uv pip install --python .venv/bin/python -r requirements-dev.txt
cp .env.example .env.local
```

Set local values in `.env.local`. Leave `KEY_VAULT_URI` empty to use local secrets without Azure Key Vault. If Key Vault is enabled, sign in with an Azure developer credential and grant the identity access to the configured vault. The service also needs reachable RabbitMQ and Azure OpenAI endpoints.

Start the service with the local environment file explicitly loaded:

```bash
uv run --env-file .env.local --no-sync uvicorn main:app --host 127.0.0.1 --port 8000
```

The production image includes the tracked `.env.production` file for non-secret settings and loads it when the container starts. Secrets are read from Azure Key Vault using `DefaultAzureCredential`; the Container App's managed identity needs the **Key Vault Secrets User** role. Azure supplies `AZURE_CLIENT_ID` so the SDK selects the user-assigned identity.

## Configuration

Configuration is parsed once at startup into a typed settings object. Local development uses the ignored `.env.local`; the production image uses the non-secret, tracked `.env.production`.

The OpenAI key is read from `AZURE_OPENAI_API_KEY` or `OPENAI_API_KEY`. Set `AZURE_OPENAI_PDF_DEPLOYMENT_NAME` when PDF extraction uses a different vision capable deployment; otherwise it uses `AZURE_OPENAI_DEPLOYMENT_NAME`. Key Vault secret names map to application environment variables:

| Key Vault secret | Environment variable |
| --- | --- |
| `llm-processor-api-token` | `API_TOKEN` |
| `openai-api-key` | `OPENAI_API_KEY` |
| `rabbitmq-password` | `RABBITMQ_PASS` |


## Development checks

```bash
uv run --no-sync ruff check .
uv run --no-sync mypy
uv run --no-sync pytest
```

GitHub Actions runs those checks on pull requests. Container publishing and the infrastructure deployment trigger run only after checks pass on a push to `main` or a manual workflow dispatch.

Runtime dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Development tool versions are pinned in `requirements-dev.txt`. After changing runtime dependencies, run `uv lock` and commit both files.

## Deployment

The service is containerized in `LLMProcessor.Dockerfile` and deployed to Azure Container Apps through the repository's GitHub Actions workflow. Configure the Container App managed identity for Key Vault access and provide the runtime settings above.

## Related projects

- [FinanceApp.Backend](https://github.com/Sziszka90/FinanceApp.Backend)
- [FinanceApp.Frontend](https://github.com/Sziszka90/FinanceApp.Frontend)
