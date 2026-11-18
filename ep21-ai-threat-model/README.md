# Ep 21 · Module 3 wrap-up: "Threat-Model Any AI App in 10 Questions"

Over 20 episodes, we broke one AI app in every way the OWASP Top 10 for LLM Applications lists. This lab turns all of it into a **threat model you can run**.

`apps/pixelkart-assist.yaml` describes an AI app's *design*:

- what the model reads, and how much each source is trusted
- what data it touches
- where its output goes
- what tools it can call
- what it pulls in from outside
- which controls are in place

[`threatmodel.py`](threatmodel.py) works out which OWASP risks apply to that design, checks the controls for each, and points to the episode that fixes each gap.

```text
GAP      LLM01  Prompt Injection                   see Ep 1, 2, 9, 10, 13
...
10 risks apply · 1 covered · 9 gaps          (exit code 1)
```

`apps/pixelkart-assist.fixed.yaml` is the same app with the series' fixes, and it scores **10 of 10 covered**. The check runs in CI on every pull request (`.github/workflows/ep21-threat-model.yml`), so a design change that drops a control fails the build.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep21-ai-threat-model
pip install -r requirements.txt
python threatmodel.py apps/pixelkart-assist.yaml          # before
python threatmodel.py apps/pixelkart-assist.fixed.yaml    # after
python vulnerable/app.py    # or fixed/app.py: the same check as a chat, at http://localhost:5000
```

## The 10 questions

| | Ask | If yes, you need |
|---|---|---|
| LLM01 | Does the model read anything you don't control? | Label it untrusted; side effects need approval |
| LLM02 | Does it touch personal or secret data? | Redaction, short retention, scoped access |
| LLM03 | Do models or packages come from outside? | Hash pinning, lockfiles, data-only formats |
| LLM04 | Can outsiders write to its memory or knowledge base? | Screen ingestion; the user confirms memory |
| LLM05 | Does its output reach HTML, SQL or a shell? | Encode for the destination; parameterise |
| LLM06 | Can it act: money, email, accounts? | One permission policy; identity from the session |
| LLM07 | Are there secrets in the system prompt? | Move them out |
| LLM08 | Does it retrieve from a mixed-trust store? | Trust and tenant filters |
| LLM09 | Do people act on its answers? | Grounded citations; decisions in code |
| LLM10 | Can anyone send it unlimited work? | max_tokens, rate limits, a budget breaker |

## Take-home checklist

- [ ] Describe your AI app as a design: inputs and trust, data, outputs, tools, supply chain and controls.
- [ ] Ask the 10 questions, and write down the control for every yes.
- [ ] Run the check in CI, so removing a control fails the build.
- [ ] Re-run the threat model whenever you add a tool, a data source or a model.
