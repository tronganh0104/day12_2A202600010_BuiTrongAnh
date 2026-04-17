# Deployment Information

## Public URL

https://day12-2a202600010-buitronganh.onrender.com

## Platform

Render

## Test Commands

### Health Check

```bash
curl https://day12-2a202600010-buitronganh.onrender.com/health
```

Expected response:

```json
{"status":"ok","version":"1.0.0","environment":"production","uptime_seconds":86.1,"total_requests":4,"checks":{"llm":"mock"},"timestamp":"2026-04-17T09:18:36.052362+00:00"}
```

### Readiness Check

```bash
curl https://day12-2a202600010-buitronganh.onrender.com/ready
```

Expected response:

```json
{"ready":true}
```

### API Test (with authentication)

```bash
curl https://day12-2a202600010-buitronganh.onrender.com/ask -X POST \
  -H "X-API-Key: buitronganh" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is deployment?"}'
```

Expected response:

```json
{"question":"What is deployment?","answer":"Deployment moves your application from development into a usable environment.","model":"gpt-4o-mini","timestamp":"2026-04-17T09:20:34.905862+00:00"}
```

## Environment Variables Set

- `ENVIRONMENT=production`
- `APP_VERSION=1.0.0`
- `AGENT_API_KEY` set on Render
- `JWT_SECRET` set on Render
- `DAILY_BUDGET_USD=5.0`
- `RATE_LIMIT_PER_MINUTE=20`
- `OPENAI_API_KEY` left empty, so the app uses the mock LLM

## Notes

- The final project was deployed from the `06-lab-complete` directory.
- Public endpoints `/health` and `/ready` work correctly.
- Protected endpoint `/ask` returns `401 Unauthorized` when no API key is provided.
- Protected endpoint `/ask` works correctly when called with the configured API key.
