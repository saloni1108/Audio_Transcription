## Choices
- **ASR**: `faster-whisper` for CPU-friendly, quantized inference with word timestamps and language ID. This meets the half-duration performance target on commodity 1 vCPU / 4GB for many clips; larger models improve accuracy at a compute trade-off.
- **Diarization**: default `VAD + ECAPA (ONNX) + clustering` balances image size and accuracy without PyTorch. For higher accuracy, switch to `pyannote` by extending `audio_utils.py` to call `pyannote/speaker-diarization-3.1` (requires Torch + model download). The code isolates diarization so backends can be swapped.
- **Blog Pipeline**: hybrid retrieval→LLM ensures topical, on-brand titles; heuristic guards enforce <60 chars, no stop-word starts, concise slugs. SQLite corpus ships (generated at runtime) to keep repo small.
- **Queueing & Streaming**: Celery offloads long ASR; SSE endpoint polls DB and emits status + final JSON. WebSockets can be added via Channels if desired (bonus path).

## Scaling 100×
- **Compute**: Separate ASR workers pool with autoscaling (KEDA on Rabbit/Redis queue). Cache models per worker, shard by language/model size.
- **Storage**: Move MinIO to external S3; lifecycle policies to transition audio to IA/Glacier.
- **Data**: Partition Postgres tables by month; store transcript words in a JSONB column + GIN index for search; or offload to Elasticsearch/OpenSearch for analytics.
- **API**: Use presigned PUT for uploads; CloudFront/S3 for delivery; adopt gRPC for worker control. SSE/WebSocket via a dedicated events service using Redis pub/sub.
- **Observability**: Prometheus metrics for queue depth, RTF, error rates; OpenTelemetry tracing across web→worker→S3.

## Rate limiting, errors, retries
- **Rate limit**: fixed-window via Redis middleware (simple); production: token bucket + leaky bucket and per-endpoint weights.
- **Retries**: Celery `autoretry_for` on transient network/S3 errors; idempotent task keys.
- **Errors**: DRF exception handler returning structured JSON with correlation IDs; loguru for structured logs.

## Diarization Accuracy Path (Bonus)
- Add an evaluation script against AMI-SDM: compute DER and F1; plug in `pyannote` backend and tune VAD aggressiveness; cluster with PLDA or Bayesian HMM. Provide `scripts/score_ami.py`.