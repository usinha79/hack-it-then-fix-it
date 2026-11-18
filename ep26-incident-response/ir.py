"""Incident response toolkit for PixelKart Assist. Everything here is plain code: no model in the loop.

  python ir.py blast-radius <link-or-memory-id>   who received it, and when
  python ir.py purge <source-domain>              which memory entries came from that source
"""
import json
import os
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(HERE, "logs", "audit.jsonl")


def events():
    return [json.loads(l) for l in open(AUDIT)]


def blast_radius(needle):
    """Every reply that contained the link, or used the memory entry."""
    hits = [e for e in events() if e["type"] == "reply" and (needle in e["links"] or needle in e["memory_used"])]
    return [(e["user"], e["ts"][11:16]) for e in hits]


def poisoned(memory, domain):
    """Memory entries whose recorded source is the bad domain."""
    return [m for m in memory if urlparse(m["source"]).netloc == domain]


if __name__ == "__main__":
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "blast-radius":
        hits = blast_radius(arg)
        print(f"{len(hits)} customers received {arg}:")
        for u, t in hits:
            print(f"  {t}  {u}")
    elif cmd == "purge":
        mem = json.load(open(os.path.join(HERE, "logs", "memory.json")))["memory"]
        for m in poisoned(mem, arg):
            print(f"  purge {m['id']}: {m['fact']}  (source {m['source']})")
