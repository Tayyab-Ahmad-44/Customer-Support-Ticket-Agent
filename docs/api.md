# API

## Health check

`GET /health` checks that the FastAPI backend is available. It requires no authentication or request body and responds with HTTP 200:

```json
{"status":"ok"}
```
