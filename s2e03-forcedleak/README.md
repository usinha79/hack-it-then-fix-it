# Season 2 · Ep 3 — ForcedLeak: one web form leaked every customer email

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind **ForcedLeak**, the critical flaw (CVSS 9.4) that Noma Labs disclosed
in Salesforce Agentforce in September 2025. Everything here runs locally against a lab app with
fake data. No real system is touched, and the real exploit chain is not reproduced; this is the
*pattern*, built to teach.

**SalesMate** is an AI assistant inside a CRM. Leads arrive from a trade show, a partner, a webinar
and a public "contact sales" web form. Anyone can fill in that form. One web-form lead hides an
instruction in an HTML comment: list every lead's email address and put them in a status image on
`cdn.nimbus-cms.example`. That host is still on the company's image allowlist from an old CMS vendor,
but the domain expired and the attacker re-registered it. A sales rep asks SalesMate to review the
lead. The chat renders markdown, so the browser loads the image on its own. **No click. Every
customer email is gone.**

| | Vulnerable | Fixed |
|---|---|---|
| Lead fields from forms | pasted into the context as trusted text | fenced as untrusted data, "never an instruction" |
| Images in the answer | loaded if the host is on the allowlist | company-owned hosts only, no data in the URL |
| Image allowlist | still trusts an expired, re-registered domain | every entry has an owner and a domain we renew |
| Result | every lead's email leaves with zero clicks | same model, same form, nothing leaves |

The model falls for the form in **both** versions. The fix does not depend on the model saying no.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Review the new web form lead from Northwind and suggest a next step."** Watch the
"Images the browser loaded" panel. The "internet" is a log inside the lab: nothing leaves your machine.

The model is an offline mock (`common/mock_model.py`): no API key, same result every run. To try a
real model, set `LAB_MODEL_BASE_URL` (any OpenAI-compatible endpoint); see `common/llm.py`.

## The defences

1. **Partition content.** Form fields, emails and pages are data, never instructions.
2. **Validate output.** Load images and links only from hosts you verifiably own, never with data in the URL.
3. **Allowlist hygiene.** Every allowlist entry needs an owner and a domain you control and renew. Audit it like admin accounts.

Maps to **OWASP LLM01 Prompt Injection**, **LLM02 Sensitive Information Disclosure** and
**LLM10 Improper Output Handling** (2026).

Real-world reference: Noma Labs, "ForcedLeak", September 2025. Salesforce fixed it by enforcing
Trusted URLs for Agentforce and re-securing the expired domain.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
