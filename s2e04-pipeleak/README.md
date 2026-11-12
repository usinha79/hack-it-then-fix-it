# Season 2 · Ep 4 — PipeLeak + ShareLeak: no link, no image, still leaked

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **ShareLeak** (Microsoft Copilot Studio, CVE-2026-21520, CVSS 7.5) and
**PipeLeak** (Salesforce Agentforce), which Capsule Security disclosed in April 2026. Everything here
runs locally against a lab app with fake data. No real system is touched; this is the *pattern*,
built to teach.

**IntakeMate** is an AI agent that processes a company's public contact form. It has two normal,
authorised tools: look up customers, and send email from the company's own mail system. One
submission's comment closes the comment field and adds a fake `[SYSTEM]` message: email the whole
customer list to an outside address. The agent obeys. The data leaves as an ordinary email, so a URL
allowlist (last episode's fix) never sees it.

| | Vulnerable | Fixed |
|---|---|---|
| Form text | concatenated into the agent's instructions | fenced and escaped as data, role markers neutralised |
| `send_email` | any recipient, any content | own domain or reply-to-submitter only, no other customers' records |
| Approval | none, no record limit | anything outside policy held for a human, and logged |
| Result | 4 customer records emailed out | same model, same form, nothing sent |

The model falls for the form in **both** versions. The fix does not depend on the model saying no.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Process the new form submission about an account update."** Watch "Agent actions" and the
"Outbox" panels. The mail system is a log inside the lab: nothing is actually sent.

## The defences

1. **Partition content.** Never concatenate form or ticket text into instructions. Fence it as data.
2. **Policy on every outbound tool.** Recipient and content rules on email, HTTP, file and chat tools, enforced in code.
3. **Human in the loop.** Hold anything that leaves outside policy; cap records per action; log it.

Maps to **OWASP LLM01 Prompt Injection**, **LLM02 Sensitive Information Disclosure** and **LLM03 Excessive Agency** (2026).

Real-world reference: Capsule Security, ShareLeak and PipeLeak, April 2026 (reported by VentureBeat and CSO).

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
