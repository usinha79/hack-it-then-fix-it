"""Sync every article in articles/ to DEV (dev.to).

- Articles are matched by title, so editing a file updates the same post.
- articles/schedule.json sets each article's go-live time. Before that time it stays a draft;
  from that time on it is sent as published. Articles not in the schedule follow their own
  front matter.
- Live URLs are written to articles/published.json.
"""
import datetime as dt
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
        API + path, method=method,
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


schedule = json.load(open("articles/schedule.json")) if os.path.exists("articles/schedule.json") else {}
now = dt.datetime.now(dt.timezone.utc)

existing, page = {}, 1
while True:
    batch = call("GET", f"/articles/me/all?per_page=100&page={page}")
    if not batch:
        break
    for a in batch:
        existing[a["title"]] = a
    page += 1

published = {}
for path in sorted(glob.glob("articles/*.md")):
    name = os.path.basename(path)
    md = open(path, encoding="utf-8").read()
    title = title_of(md)
    if not title:
        print(f"skip {name}: no title")
        continue
    if name in schedule:
        due = dt.datetime.fromisoformat(schedule[name]) <= now
        md = re.sub(r"^published:\s*\w+", f"published: {'true' if due else 'false'}", md, count=1, flags=re.M)
    if title in existing:
        a = call("PUT", f"/articles/{existing[title]['id']}", {"article": {"body_markdown": md}})
    else:
        a = call("POST", "/articles", {"article": {"body_markdown": md}})
    live = a.get("published") or bool(a.get("published_at"))
    print(f"{'LIVE ' if live else 'draft'} {title} {a.get('url')}")
    if live:
        published[name] = {"title": title, "url": a.get("url"), "published_at": a.get("published_at")}

json.dump(published, open("articles/published.json", "w"), indent=1)
