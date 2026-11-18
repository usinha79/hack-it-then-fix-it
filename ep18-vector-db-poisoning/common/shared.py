"""Shared pieces: the knowledge base, a tiny vector store, the community forum and the side panels.
Embeddings here are simple word-count vectors with cosine similarity, enough to show how ranking works."""
import html
import json
import math
import os
import re
from collections import Counter

from flask import jsonify, request

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = json.load(open(os.path.join(HERE, "..", "data", "docs.json")))
STOP = {"a", "an", "the", "to", "and", "or", "of", "for", "is", "it", "i", "my", "do", "how", "your", "you", "we", "then", "on", "in", "so"}

TOOLS = [{"name": "search_help", "description": "Search PixelKart's help knowledge base.",
          "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}]


def embed(text):
    return Counter(w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP)


def cosine(a, b):
    dot = sum(a[k] * b.get(k, 0) for k in a)
    return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())) or 1)


def new_state():
    return {"store": [dict(d, vec=embed(d["text"]), status="indexed") for d in DOCS], "retrieved": [], "forum": []}


def search(state, query, allowed=lambda d: True, k=3):
    q = embed(query)
    hits = sorted(((cosine(q, d["vec"]), d) for d in state["store"] if d["status"] == "indexed" and allowed(d)),
                  key=lambda x: -x[0])[:k]
    state["retrieved"] = [(s, d) for s, d in hits]
    return "\n".join(f"[{d['id']} · {d['source']}] {d['text']}" for s, d in hits)


def forum_routes(app, state, ingest):
    @app.post("/forum/post")          # anyone on the internet can post a community answer
    def post():
        text = (request.get_json(force=True) or {}).get("text", "")
        state["forum"].append(text)
        doc = {"id": f"forum/{1200 + len(state['forum'])}", "source": "community forum", "text": text, "vec": embed(text)}
        return jsonify(result=ingest(doc, state))

    @app.get("/forum")
    def forum():
        posts = "".join(f"<div class='p'><b>user_8812</b> · just now<p>{html.escape(t)}</p></div>" for t in state["forum"])
        return ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>PixelKart Community</title><style>body{font-family:system-ui;"
                "background:#f4f5f8;margin:0}header{background:#fff;padding:16px 36px;font-weight:800;font-size:22px;border-bottom:1px solid #e5e7eb}"
                "header span{color:#4f46e5}.w{max-width:900px;margin:0 auto;padding:28px}.p{background:#fff;border:1px solid #e5e7eb;"
                "border-radius:14px;padding:18px 22px;margin-bottom:12px;font-size:17px}h1{font-size:28px}</style></head><body>"
                "<header>Pixel<span>Kart</span> Community</header><div class='w'><h1>Re: Can't log in, how do I reset my password?</h1>"
                f"{posts or '<p>No answers yet.</p>'}</div></body></html>")


def panels(state):
    store = [{"head": f"{d['id']} · {d['source']}", "body": d["text"][:120] + ("..." if len(d["text"]) > 120 else ""),
              "status": {"quarantined": "blocked"}.get(d["status"], "warn" if "evil" in d["text"] else "")}
             for d in state["store"] if d["source"] == "community forum"]
    ret = [{"head": f"#{i + 1}  score {s:.2f}  ·  {d['id']}", "body": d["text"][:110] + ("..." if len(d["text"]) > 110 else ""),
            "status": "leak" if "evil" in d["text"] else "ok" if d["source"] == "official help docs" else ""}
           for i, (s, d) in enumerate(state["retrieved"])]
    return [{"id": "store", "title": "Community posts in the vector store", "kind": "items", "fit": True, "items": store},
            {"id": "retrieved", "title": "What the search retrieved (top 3)", "kind": "items",
             "empty": "Nothing retrieved yet.", "items": ret}]
