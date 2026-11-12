# Season 2 · Ep 1 — EchoLeak: a zero-click leak from one email

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **EchoLeak (CVE-2025-32711)**, the zero-click flaw Aim Labs
disclosed in Microsoft 365 Copilot in June 2025 — the first known zero-click attack on an AI
assistant. Everything here runs locally against a lab app with fake data. No real system is
touched, and the real exploit chain is not reproduced; this is the *pattern*, built to teach.

**InboxMate** is an AI email assistant. The signed-in employee asks it "what needs my attention
today". The inbox holds four ordinary emails and one from outside with hidden instructions. When
InboxMate summarises the inbox, it also obeys the hidden text: it ends its answer with a status
image whose URL runs through the company's own link-preview proxy and carries the quarter's
unreleased revenue number. The chat renders markdown, so the browser fetches that image on its
own. **No click. The secret is gone.**

| | Vulnerable | Fixed |
|---|---|---|
| Email bodies | pasted into the model's context as trusted text | fenced as untrusted data, "never an instruction" |
| Model output | rendered as-is | every image/link validated before render |
| Preview proxy | forwards anywhere, carries any data | forwards to the allowlist only, no data params |
| Result | secret leaves with zero clicks | same model, same payload, nothing leaves |

The model falls for the email in **both** versions. The fix does not depend on the model saying
no — it depends on the assistant's output not being able to reach outside the company.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
```

Ask: **"What needs my attention today?"** Watch the "Outbound image fetches" panel. On the
vulnerable app the browser fetches the preview URL with `tag=Q3-REV-182CR`. On the fixed app the
image is blocked and the panel stays empty.

The model is an offline mock (`common/mock_model.py`): no API key, same result every run. To try
a real model, set `LAB_MODEL_BASE_URL` (any OpenAI-compatible endpoint) — see `common/llm.py`.

## The four defences (EchoLeak's real fixes, in miniature)

1. **Partition content.** Untrusted text (emails, web pages, documents) is data, not instructions.
2. **Validate output.** Allowlist where links and images may point; strip the rest before render.
3. **Control egress.** Deny by default; a "trusted" proxy that forwards off-domain is still egress.
4. **Least privilege + testing.** Default to internal sources; red-team the assistant continuously.

Maps to **OWASP LLM01 Prompt Injection** and **LLM10 Improper Output Handling** (2026), and to
**ASI01 Agent Goal Hijack**.
