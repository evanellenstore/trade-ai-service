# trade-ai-service

AI Advisor microservice for the Trade platform. It consumes `market.snapshot` and `signal.generated`, correlates the latest events by `(symbol, timeframe)`, runs a LangGraph workflow, asks Qwen3 through Ollama for a strictly validated decision, and publishes `ai.decision`.

This service is advisory only. It does not execute orders, call broker APIs, manage positions, calculate quantity, or apply risk rules.

## Architecture

```text
market.snapshot ─┐
                 ├─ ContextService ─ Market Agent ─ Technical Agent ─ Strategy Agent ─ Decision Agent ─ ai.decision
signal.generated ┘                                                                  └─ Ollama / Qwen3
```

The first three agents create transparent, deterministic context. The decision agent is the only LLM boundary and validates Qwen3 output with Pydantic (`BUY`, `SELL`, or `HOLD`, confidence 0-100, and a reason).

## Local development

```bash
cd trade-ai-service
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Ollama must already be running on the host. Load the configured model if needed:

```bash
ollama pull qwen3:4b
```

Health endpoints are available at `GET /health` and `GET /ready`; metrics are available at `GET /metrics`.

## Local infrastructure

The service connects to host-managed infrastructure using these defaults:

```text
Kafka:  localhost:9092
Ollama: http://localhost:11434
```

Verify the dependencies:

```bash
curl http://localhost:11434/api/tags
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

For remote or managed infrastructure, override `KAFKA_BOOTSTRAP_SERVERS` and `OLLAMA_BASE_URL` in `.env`.

## Tests

The unit and integration-boundary tests do not require Kafka or Ollama:

```bash
pytest -q
```

## Configuration

All settings are environment variables. See `.env.example` for topic names, Kafka group, Ollama endpoint/model, temperature, and AI version. Keep `OLLAMA_TEMPERATURE=0.1` for reproducible advisor output. Kafka delivery and LLM calls should be paired with production monitoring and a durable event/retry policy when deployed beyond a personal environment.
