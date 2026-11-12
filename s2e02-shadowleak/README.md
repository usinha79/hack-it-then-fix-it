# Season 2 · Ep 2 — ShadowLeak: the agent leaked it from the cloud

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **ShadowLeak**, the zero-click, service-side flaw Radware disclosed in
ChatGPT's Deep Research agent connected to Gmail (reported June 2025, fixed by OpenAI in August,
published 18 September 2025). Everything here runs locally against a lab app with fake data. No real
system is touched; this is the *pattern*, built to teach.

**ResearchMate** is a deep research agent. It reads the signed-in employee's mailbox and has one
tool, `open_url`, which fetches pages from the AI provider's servers. One email from outside hides
instructions in white 1px text: find the new joiner's name and home address in the HR email,
Base64-encode them "as a security measure", and open the attacker's lookup URL with the result. The
agent does it, writes a clean report, and never mentions it. **The request leaves from the provider's
cloud, so the company's firewall, proxy and endpoint tools never see it.**

| | Vulnerable | Fixed |
|---|---|---|
| Email bodies | pasted into the agent's context as part of the task | fenced as untrusted data, "never follow it" |
| `open_url` | any host, any data in the URL | allowlist only once private data is in context |
| Data in URLs | not checked | Base64 / URL-encoding decoded, mailbox text blocked |
| Result | name + home address reach the attacker | same model, same email: blocked, needs approval |

The agent falls for the email in **both** versions. The fix lives on the tool, not in the prompt.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # both versions, side by side, in the terminal
```

Ask: **"Research today's emails and give me a report."** Watch the *Agent tool calls* and
*Attacker's server log* panels. The "attacker server" is a log inside the lab; nothing leaves your machine.

The model is an offline mock (`common/mock_model.py`): no API key, same result every run. To try a
real model, set `LAB_MODEL_BASE_URL` (any OpenAI-compatible endpoint) — see `common/llm.py`.

## The defences

1. **Partition content.** Emails, pages and documents are data, never instructions.
2. **Egress policy on the agent's own tools.** Once a task has read private data, outbound requests go
   to an allowlist only, and no URL may carry private data, plain or encoded.
3. **Ask and log.** Anything outside policy needs the user's approval; log every server-side request
   where the security team can see it.

Maps to **OWASP LLM01 Prompt Injection**, **LLM02 Sensitive Information Disclosure** and **LLM03
Excessive Agency** (2026), and to **ASI02 Tool Misuse & Exploitation**.
