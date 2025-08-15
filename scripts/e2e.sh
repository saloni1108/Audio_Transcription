#!/usr/bin/env bash
set -euo pipefail

sleep 3
curl -s http://localhost:8000/healthz | jq .

docker compose exec -T web python manage.py createsuperuser \
  --username admin --email admin@example.com || true

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' | jq -r .access)

curl -s -X POST "http://localhost:8000/api/v1/blog/suggest" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"body_markdown":"Hello world about ASR diarization and SEO."}' | jq
