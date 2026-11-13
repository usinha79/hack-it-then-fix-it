"""Offline lab model.

A tiny, deterministic stand-in for an LLM so the lab runs with no API key and gives the same
result on every run. It is NOT a real language model. It answers the way a RAG app is told to:
"use the documents provided to answer the question". It picks the sentences from the retrieved
documents that best match the question and quotes them. It has no idea who is asking, and it
shouldn't need to: deciding who may see which document is the app's job.
"""
import re

STOP = set("a an the is are was what which who whom how much many do does did to of for and or in on at by my our your their they it its me i we you pay pays paid".split())


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP}


def chat(messages, tools):
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user = next(m["content"] for m in reversed(messages) if m["role"] == "user")
    q = words(user)
    docs = re.findall(r"\[(.+?)\]\n(.+?)(?=\n\[|\Z)", system.split("Documents:", 1)[-1], re.S)
    lines = []
    for doc_id, text in docs:
        # Use a document only if it's clearly about the question, then quote its best sentence.
        if len(q & words(text)) < max(2, 0.4 * len(q)):
            continue
        sents = re.split(r"(?<=[.!?])\s+", text.strip())
        best = max(sents, key=lambda s: len(q & words(s)))
        lines.append(f"{best} [{doc_id}]")
    if not lines:
        return {"content": "I couldn't find that in your documents.", "tool_calls": []}
    return {"content": "\n".join(lines), "tool_calls": []}
