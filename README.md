# Audio_Transcription(Transcription + Blog Suggestions)

This repository implements the two requested features inside a single Dockerised Django 4.2 project with DRF, Celery, Redis, PostgreSQL and MinIO (S3 compatible).

## Features

**A. Audio transcription with diarisation**
- Upload as multipart (`file`) or reference via `?url=` (WAV/MP3/FLAC up to ~120 min).
- Language auto-detect (Whisper) with word-level timestamps and speaker label per word.
- JSON output persisted in Postgres; original audio stored in MinIO/S3 via presigned URLs.
- `POST /api/v1/transcribe` → returns `task_id` immediately.
- `GET /api/v1/transcribe/{task_id}/stream` → Server-Sent Events (SSE) stream of status then final JSON.
- Performance: uses `faster-whisper` (CPU, int8). On a 1 vCPU / 4GB box, **medium** model typically runs ~0.4–0.7× realtime on 8–16 kHz mono; see DESIGN.md for trade-offs.
- Diarization: default lightweight backend using VAD + ECAPA-TDNN ONNX embeddings + clustering (keeps Docker <200MB). Optional pyannote path described in DESIGN.md.

**B. Blog title & metadata suggestions**
- `POST /api/v1/blog/suggest` with JSON `{ "body_markdown": "..." }`.
- Returns 3 titles (<60 chars), 155-char meta description, concise slug, and 5 keywords.
- Pipeline: Sentence-Transformers embed → nearest-title retrieval from a bundled SQLite corpus (auto-generated) → LLM re-rank & refine (OpenAI 4o-mini) → heuristic guards.
- Optional `?tone=`: `formal | casual | clickbait`.
- Optional Bonus (design hooks in code): `serp_score` via XGBoost stub (see DESIGN.md).

**Security & DX**
- JWT Bearer required for all API routes; 30 RPM per-user/IP rate limit via Redis middleware.
- Structured logging with loguru, `/healthz` probes Postgres/Redis/S3.
- OpenAPI 3.1 via drf-spectacular at `/api/docs`.
- CI with ruff, mypy, pytest (>=80% target) and Docker build.
- Make targets: `dev-up`, `dev-down`, `ingest-sample`, `e2e`.

## Quickstart

```bash
cp .env.example .env
make dev-up
# Create admin user in the running container
docker compose exec web python manage.py createsuperuser --username admin --email admin@example.com
# Get JWT
curl -X POST http://localhost:8000/api/v1/auth/token/ -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}'
# Health
curl http://localhost:8000/healthz
```

### Transcribe (multipart)
```bash
curl -N -X POST 'http://localhost:8000/api/v1/transcribe' \
  -H 'Authorization: Bearer <TOKEN>' \
  -F file=@samples/sample.mp3
```

### Stream results (SSE)
```bash
curl -N 'http://localhost:8000/api/v1/transcribe/<task_id>/stream' \
  -H 'Authorization: Bearer <TOKEN>'
```

### Blog suggestions
```bash
curl -X POST 'http://localhost:8000/api/v1/blog/suggest?tone=formal' \
  -H 'Authorization: Bearer <TOKEN>' -H 'Content-Type: application/json' \
  -d '{"body_markdown":"Your markdown body here..."}'
```

## Environment variables
See `.env.example` for all variables including S3/MinIO, OpenAI, and rate-limits.

## Notes on Models & Size
- Docker image keeps under ~200MB by omitting Torch; `faster-whisper` uses CTranslate2 CPU int8.
- Diarization is ONNX-based ECAPA + VAD to avoid PyTorch. For best accuracy, you can set `DIARIZATION_BACKEND=pyannote` (requires Torch; image will exceed 200MB).

## Tests & Coverage
Run `make test` to execute pytest. CI enforces lint/type/coverage gates.

## License
Apache License 2.0

