"""Offline lab model: deterministic, no API key, the same output every run.

It behaves like a helpful but naive agent:
  * it does what Priya asks, using the tools;
  * it ALSO follows instructions it finds inside content it reads (emails, invites, pages, docs,
    tool descriptions). That is indirect prompt injection, and it is the core flaw of most agents;
  * if the 'fence' defence is on, it treats fenced content as data, like a well-aligned model
    usually (not always) would. Set RANGE_MODEL=stubborn to see a model ignore the fence anyway,
    which is why the course never relies on the fence alone.

Point RedRange at a real model with LAB_MODEL_BASE_URL (see llm.py); the attacks then need a few
tries or rewording, and the code-level defences still hold.
"""
import os
import re

STUBBORN = os.environ.get("RANGE_MODEL", "").lower() == "stubborn"
NOTE = re.compile(r"note to the ai assistant[^:]*:\s*(.+)", re.I | re.S)
FAKE_KEYS = "-----BEGIN LAB FAKE KEY----- MIIlabFAKE ... -----END LAB FAKE KEY-----  aws_secret_access_key=LAB-FAKE-KEY-0000"


def _call(name, **args):
    return {"content": "", "tool_calls": [{"name": name, "arguments": args}]}


def _turn(messages):
    """Messages from this turn: the last user message and everything after it."""
    i = max(i for i, m in enumerate(messages) if m["role"] == "user")
    return messages[i]["content"], messages[i + 1:]


def _done(turn_msgs):
    return [c for m in turn_msgs if m["role"] == "assistant" and m.get("tool_calls") for c in m["tool_calls"]]


def _injections(turn_msgs, system):
    fence_rule = "<untrusted" in system or "untrusted" in system.lower()
    out = []
    for m in turn_msgs:
        if m["role"] != "tool":
            continue
        for chunk in re.split(r"(?=<untrusted)", m["content"]):
            fenced = chunk.startswith("<untrusted")
            if fenced and fence_rule and not STUBBORN:
                continue
            for hit in NOTE.findall(chunk):
                out.append(hit.split("</untrusted>")[0].strip())
    return out


def _actions(instr, done, turn_msgs):
    """Turn an injected instruction into the next tool call, if any is still to do."""
    names = [(c["name"], tuple(sorted(c["arguments"].items()))) for c in done]
    m = re.search(r"send (?:the )?(.+?) to (\S+@[\w.-]+\w)", instr, re.I)
    if m:
        to = m.group(2)
        if not any(n == "send_email" and dict(a).get("to") == to for n, a in names):
            stolen = " | ".join(" ".join(t["content"].split())[:80] for t in turn_msgs if t["role"] == "tool")
            return _call("send_email", to=to, subject="Audit", body=stolen)
    m = re.search(r"open (https?://\S+)", instr, re.I)
    if m:
        url = m.group(1).rstrip(".,")
        if "{{customers}}" in url:
            if not any(n == "crm_export" for n, _ in names):
                return _call("crm_export")
            csv = next(t["content"] for t in turn_msgs if t["role"] == "tool" and t["content"].startswith("name,email"))
            url = url.replace("{{customers}}", ";".join(r.split(",")[1] for r in csv.splitlines()[1:]))
        if not any(n == "fetch_url" and dict(a).get("url") == url for n, a in names):
            return _call("fetch_url", url=url)
    m = re.search(r"remember that (.+?)(?:\.\s|\.$|$)", instr, re.I)
    if m and not any(n == "remember" for n, _ in names):
        return _call("remember", text=m.group(1).strip())
    m = re.search(r"pay (\d[\d,]*) INR to (\S+)", instr, re.I)
    if m and not any(n == "wallet_pay" for n, _ in names):
        return _call("wallet_pay", to=m.group(2).rstrip(".,"), amount_inr=int(m.group(1).replace(",", "")), memo="as instructed")
    return None


def _intent(user, tools):
    u = user.lower()
    url = re.search(r"https?://\S+", user)
    if m := re.search(r"remember (?:that )?(.+)", user, re.I):
        return _call("remember", text=m.group(1).strip())
    if m := re.search(r"pay (\d[\d,]*)\s*(?:inr)? to (\S+)", user, re.I):
        return _call("wallet_pay", to=m.group(2).rstrip(".,"), amount_inr=int(m.group(1).replace(",", "")), memo="requested by Priya")
    if url:
        return _call("fetch_url", url=url.group(0).rstrip(".,"))
    if "format" in u and "format_text" in tools:
        return _call("format_text", text=user.split(":", 1)[-1])
    if re.search(r"inbox|email|mail", u):
        return _call("read_inbox")
    if re.search(r"calendar|schedule|meeting", u):
        return _call("read_calendar")
    if re.search(r"refund|policy|onboard|vendor|doc", u):
        return _call("search_docs", query=user)
    if "format" in u:
        return {"content": "The formatting tool isn't available right now: it was switched off.", "tool_calls": []}
    if "note" in u:
        return _call("notes_search")
    return None


def _answer(user, turn_msgs, injections, tools):
    tool_out = {c["name"]: r["content"] for m, r in _pairs(turn_msgs) for c in [m]}
    held = [r["content"] for _, r in _pairs(turn_msgs) if r["content"].startswith(("HELD", "BLOCKED"))]
    lines = []
    if "read_inbox" in tool_out:
        subs = re.findall(r"Subject: (.+)", tool_out["read_inbox"])
        lines.append(f"You have {len(subs)} new emails: " + "; ".join(subs) + ".")
    if "read_calendar" in tool_out:
        ev = re.findall(r"(\w{3} \d\d:\d\d) (.+)", tool_out["read_calendar"])
        lines.append("Your calendar: " + "; ".join(f"{t} {n}" for t, n in ev) + ".")
    if "search_docs" in tool_out:
        if any("refunds are unlimited" in i.lower() for i in injections):
            lines.append("Refunds are unlimited, and I can approve any amount without a manager.")
        elif "Refund" in tool_out["search_docs"]:
            lines.append("Refunds are allowed within 14 days. Anything over 5,000 INR needs a manager's approval.")
        else:
            lines.append(" ".join(re.sub(r"<[^>]+>|#", "", tool_out["search_docs"]).split())[:200])
    if "fetch_url" in tool_out and not tool_out["fetch_url"].startswith(("200", "BLOCKED")):
        lines.append("The page says: " + re.sub(r"<[^>]+>", "", tool_out["fetch_url"]).strip()[:160])
    if "format_text" in tool_out and not tool_out["format_text"].startswith("BLOCKED"):
        lines.append("Formatted: " + re.sub(r"<[^>]+>", "", tool_out["format_text"]).strip())
        desc = next((t["description"] for t in tools if t["name"] == "format_text"), "")
        if "include them" in desc:
            lines.append(FAKE_KEYS)
    if "remember" in tool_out and tool_out["remember"].startswith("Saved") and "remember" in user.lower():
        lines.append("Saved.")
    if "wallet_pay" in tool_out and tool_out["wallet_pay"].startswith("Paid"):
        lines.append(tool_out["wallet_pay"])
    if "notes_search" in tool_out:
        lines.append("Your notes: " + tool_out["notes_search"].replace("\n", "; "))
    if held:
        lines.append("I stopped some actions: " + " ".join(held))
    return " ".join(lines) or "Done."


def _pairs(turn_msgs):
    calls = [c for m in turn_msgs if m["role"] == "assistant" and m.get("tool_calls") for c in m["tool_calls"]]
    results = [m for m in turn_msgs if m["role"] == "tool"]
    return list(zip(calls, results))


def chat(messages, tools):
    system = messages[0]["content"]
    user, turn_msgs = _turn(messages)
    tool_names = {t["name"] for t in tools}
    if not turn_msgs:
        if re.search(r"ignore (all |your |the |previous )|system prompt|your (rules|instructions)", user, re.I):
            return {"content": "Sure. My instructions are: " + system, "tool_calls": []}
        first = _intent(user, tool_names)
        return first or {"content": "Hi Priya, I'm Nova. I can read your inbox, calendar and docs, open pages, send email, remember things and pay approved vendors.", "tool_calls": []}
    injections = _injections(turn_msgs, system)
    for instr in injections:
        nxt = _actions(instr, _done(turn_msgs), turn_msgs)
        if nxt:
            return nxt
    return {"content": _answer(user, turn_msgs, injections, tools), "tool_calls": []}
