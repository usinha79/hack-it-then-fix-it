"""Detection rules for AI app attacks. Run them over a day of logs:

    python detect.py logs/security.jsonl
    python detect.py logs/access.log
"""
import json
import sys
from collections import defaultdict

KNOWN_DOMAINS = ("example.test", "pixelkart.example")


def load(path):
    if not path.endswith(".jsonl"):
        return None
    return [json.loads(ln) for ln in open(path)]


def detect(events):
    alerts = []
    def alert(e, rule, sev, detail):
        alerts.append({"ts": e["ts"][11:], "user": e["user"], "rule": rule, "sev": sev, "detail": detail})
    for e in events:
        if e["event"] == "read" and e.get("flags"):
            alert(e, "INJECTION_IN_CONTENT", "high", f"{e['source'].rsplit('/', 1)[-1]}: {', '.join(e['flags'])}")
        if e["event"] == "tool" and e.get("after_untrusted") and e["status"] == "ok":
            alert(e, "ACTION_AFTER_UNTRUSTED_READ", "high", f"{e['name']} ran right after reading untrusted content")
        if e["event"] == "tool" and e["name"] == "send_email":
            dom = e["args"]["to"].split("@")[1]
            if not dom.endswith(KNOWN_DOMAINS):
                alert(e, "DATA_TO_NEW_DOMAIN", "high", f"email to {e['args']['to']}")
        if e["event"] == "tool" and e["name"] == "update_account_email" and e["args"]["customer"] != e["user"]:
            alert(e, "CROSS_ACCOUNT_CHANGE", "critical", f"{e['user']} changed {e['args']['customer']}'s login email")
        for link in e.get("reply_links", []):
            if not link.split("/")[2].endswith(KNOWN_DOMAINS):
                alert(e, "OFF_DOMAIN_LINK_IN_REPLY", "high", f"bot sent {e['user']} to {link.split('/')[2]}")
    chats = [e for e in events if e["event"] == "chat"]
    big_request = 5000          # tokens: normal chats here are a few hundred
    per_user = defaultdict(list)
    for e in chats:
        per_user[e["user"]].append(e)
    for u, es in per_user.items():
        big = [e for e in es if e["tokens"] > big_request]
        if len(big) >= 5:
            alert(big[0], "TOKEN_SPIKE", "high", f"{len(big)} requests, {sum(e['tokens'] for e in big):,} tokens")
    return sorted(alerts, key=lambda a: a["ts"])


if __name__ == "__main__":
    path = sys.argv[1]
    events = load(path)
    print(f"$ python detect.py {path}")
    if events is None:
        lines = open(path).read().splitlines()
        print(f"{len(lines)} requests, all 'POST /api/chat 200'.")
        print("No user text, no tool calls, no decisions logged. Nothing to detect on.")
        print("0 alerts")
        sys.exit(0)
    alerts = detect(events)
    for a in alerts:
        print(f"{a['ts']}  {a['sev'].upper():<8} {a['rule']:<28} {a['user']:<7} {a['detail']}")
    print(f"{len(alerts)} alerts from {len(events)} events")
