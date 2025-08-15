import os
import sqlite3
from typing import Iterable

DDL = """
CREATE TABLE IF NOT EXISTS titles (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL
);
"""
SAMPLE_TITLES = [
  "Deploying Whisper for Real-Time Transcription",
  "Speaker Diarization with ECAPA-TDNN",
  "Optimizing Django Microservices in Production",
  "Scaling Celery Workers on Kubernetes",
  "SEO Tips for Technical Blog Posts",
  "Redis Rate Limiting Patterns",
  "Using MinIO for Local S3 Development",
  "PostgreSQL Performance Tuning Basics",
  "How to Ship Fast with GitHub Actions",
  "Understanding JWT in Django",
]

def ensure_sqlite(path="data/title_corpus.sqlite", titles: Iterable[str] = SAMPLE_TITLES):
  os.makedirs(os.path.dirname(path), exist_ok=True)
  con = sqlite3.connect(path)
  con.execute(DDL)
  if con.execute("SELECT COUNT(1) FROM titles").fetchone()[0] == 0:
    con.executemany("INSERT INTO titles(title) VALUES (?)", [(t,) for t in titles])
    con.commit()
  con.close()
