#!/usr/bin/env bash
set -euo pipefail

mkdir -p samples
if [ ! -f samples/sample.mp3 ]; then
  curl -L -o samples/sample.mp3 https://file-examples.com/storage/fe6f9e2d5a5d8a/audio/2017/11/file_example_MP3_700KB.mp3
fi
if [ ! -f samples/post.md ]; then
  cat > samples/post.md <<'MD'
# Multilingual AI Models in Production

This post explores strategies for deploying multilingual ASR and diarization at scale, comparing Whisper and wav2vec2. We also cover cost/perf trade-offs.
MD
fi

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' | jq -r .access)

curl -N -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "Authorization: Bearer $TOKEN" \
  -F file=@samples/sample.mp3

curl -s -X POST "http://localhost:8000/api/v1/blog/suggest?tone=formal" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"body_markdown\": \"$(${PWD}/scripts/escape_md.sh samples/post.md)\"}" | jq
