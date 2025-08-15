import os
import re
import sqlite3
from typing import List

from sentence_transformers import SentenceTransformer, util

_model = None

def get_model():
    global _model
    if _model is None:
        name = os.getenv("SENTENCE_TRANSFORMER", "sentence-transformers/all-MiniLM-L6-v2")
        _model = SentenceTransformer(name)
    return _model

STOP_WORDS = set("a an the and or but of with to in for on at from by how why what when where is are be can".split())

def clean_title(t: str) -> str:
    t = t.strip()
    # Capitalize first letter, remove leading stop-words
    words = [w for w in re.split(r"\s+", t) if w]
    while words and words[0].lower() in STOP_WORDS:
        words.pop(0)
    t = " ".join(words)
    return t[:58].rstrip(" -")

def slugify(t: str) -> str:
    t = re.sub(r"[^a-zA-Z0-9\s-]","", t).strip().lower()
    t = re.sub(r"\s+","-", t)
    tokens = t.split("-")[:8]
    return "-".join([tok for tok in tokens if tok])

TONE_PREFIX = {
  "formal": "Write concise, professional, authoritative titles.",
  "casual": "Make titles friendly and simple.",
  "clickbait": "Make titles curiosity-driven but not misleading.",
}

PROMPT_TMPL = (
  "You are a helpful editor. Given candidate blog titles and a post body, return the 3 best titles (<60 chars), an SEO meta description (~155 chars), a concise slug (<=8 tokens), and 5 keywords.\n"
  "Candidates: {cands}\nBody: {body}\nStyle hint: {tone}\nReturn JSON keys: titles (list of 3), meta_description, slug, keywords (5)."
)

def nearest_titles(body: str, k: int = 10) -> List[str]:
    from .corpus import ensure_sqlite
    ensure_sqlite()
    con = sqlite3.connect("data/title_corpus.sqlite")
    titles = [r[0] for r in con.execute("SELECT title FROM titles").fetchall()]
    con.close()
    model = get_model()
    emb_corpus = model.encode(titles, normalize_embeddings=True)
    emb_q = model.encode([body], normalize_embeddings=True)[0]
    scores = util.cos_sim(emb_q, emb_corpus)[0].tolist()
    ranked = [t for _, t in sorted(zip(scores, titles), reverse=True)]
    return ranked[:k]

def call_llm_huggingface(prompt: str) -> dict:
    import json
    import os

    import requests

    key = os.getenv("HUGGINGFACE_API_KEY", "")
    if not key:
        return {}

    model_id = "meta-llama/Llama-2-13b-chat-hf"
    url = f"https://api-inference.huggingface.co/models/{model_id}"

    headers = {"Authorization": f"Bearer {key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        try:
            return json.loads(data[0]["generated_text"])
        except Exception:
            return {}
    return {}

def suggest(body_md: str, tone: str | None) -> dict:
    cands = nearest_titles(body_md, k=10)
    tone_txt = TONE_PREFIX.get((tone or "").lower(), "Neutral style.")
    prompt = PROMPT_TMPL.format(cands=cands, body=body_md[:2000], tone=tone_txt)
    llm = call_llm_huggingface(prompt)

    # Heuristic fallback if LLM disabled
    if not llm:
        titles = [clean_title(cands[i]) for i in range(3)]
        desc = (body_md.strip().replace("\n"," ")[:155]).rstrip()
        slug = slugify(titles[0])
        kw = list({w.lower() for w in re.findall(r"[a-zA-Z]{4,}", body_md)})[:5]
        return {"titles": titles, "meta_description": desc, "slug": slug, "keywords": kw}

    titles = [clean_title(t) for t in llm.get("titles", [])][:3]
    meta = llm.get("meta_description", "")[:160].rstrip()
    slug = slugify(llm.get("slug", "-"))
    kw = llm.get("keywords", [])[:5]
    return {"titles": titles, "meta_description": meta, "slug": slug, "keywords": kw}