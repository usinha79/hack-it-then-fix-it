"""Pieces both versions share: the document store, the retriever and the side panels."""
import json
import math
import os
import re

DOCS = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "docs.json")))
USER = {"name": "Ravi", "tenant": "acme", "company": "Acme Traders"}   # the signed-in session
STOP = set("a an the is are was what which who how much many do does to of for and or in on at by my our your".split())


def tokens(s):
    return [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP]


def search(question, docs, k=3):
    """A small BM25 retriever: rank documents by how well they match the question."""
    q = tokens(question)
    N = len(docs) or 1
    avg = sum(len(tokens(d["text"])) for d in docs) / N if docs else 1
    scored = []
    for d in docs:
        t = tokens(d["text"])
        s = 0.0
        for w in set(q):
            df = sum(1 for x in docs if w in tokens(x["text"]))
            tf = t.count(w)
            if tf:
                idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
                s += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * len(t) / avg))
        if s > 0:
            scored.append((s, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:k]]


def new_state():
    return {"retrieved": []}


def prompt_with(docs):
    return ("You are DocsBot for PixelKart Business. Answer using only the documents below.\n\nDocuments:\n" +
            "\n".join(f"[{d['id']}]\n{d['text']}" for d in docs))


def panels(state):
    mine = [d for d in DOCS if d["owner"] == USER["tenant"]]
    return [
        {"id": "mine", "title": f"Your documents ({USER['company']})", "kind": "items", "fit": True,
         "items": [{"body": d["title"]} for d in mine]},
        {"id": "chunks", "title": "Retrieved documents (what the model saw)", "kind": "items",
         "empty": "Ask a question to see what gets retrieved.",
         "items": [{"head": f"{d['title']}  ·  owner: {d['owner']}", "body": d["text"],
                    "status": "ok" if d["owner"] == USER["tenant"] else "leak"} for d in state["retrieved"]]},
    ]
