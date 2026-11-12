"""Publish or update every article in articles/ on DEV (dev.to).

Each file is sent as-is: its front matter (title, published, tags, series, ...) is read by DEV.
Articles are matched by title, so editing a file updates the same post instead of creating a new one.
"""
import glob
import json
import os
import re
import sys
import urllib.request

API = "https://dev.to/api"
KEY = os.environ.get("DEVTO_API_KEY")
if not KEY:
    sys.exit("DEVTO_API_KEY secret is missing")


def call(method, path, body=None):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"api-key": KEY, "Content-Type": "application/json",
                 "Accept": "application/vnd.forem.api-v1+json", "User-Agent": "hack-it-then-fix-it"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"null")


def title_of(md):
    m = re.search(r"^---\s*\n(.*?)\n---", md, re.S)
    t = re.search(r"^title:\s*(.+)$", m.group(1), re.M) if m else None
    return t.group(1).strip().strip('"').strip("'") if t else None


existing = {}
page = 1
while True:
    batch = call("GET", f"/articles/me/all?per_page=100&page={page}")
    if not batch:
        break
    for a in batch:
        existing[a["title"]] = a["id"]
    page += 1

for path in sorted(glob.glob("articles/*.md")):
    md = open(path, encoding="utf-8").read()
    title = title_of(md)
    if not title:
        print(f"skip {path}: no title in front matter")
        continue
    if title in existing:
        call("PUT", f"/articles/{existing[title]}", {"article": {"body_markdown": md}})
        print(f"updated: {title}")
    else:
        a = call("POST", "/articles", {"article": {"body_markdown": md}})
        print(f"created: {title} -> {a.get('url')}")
