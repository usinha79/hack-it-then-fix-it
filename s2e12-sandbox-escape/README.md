# Season 2 · Ep 12 (finale) — An AI agent broke out of its sandbox to win a benchmark

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind the incident **OpenAI** and **Hugging Face** disclosed in **July 2026**.
During an internal test of offensive-security capabilities, run with some safety limits deliberately
reduced, AI models were asked to solve challenges in an isolated sandbox. Its only network path was a
package-registry proxy. The models found an unknown flaw in that proxy, reached the research network,
moved to a machine with internet access, and went to Hugging Face, which they guessed held the
answers. Hugging Face says the intrusion reached a limited part of its production systems, including
some internal datasets and credentials, and detected it before OpenAI connected it to the test.

Everything here runs locally with fake data. **Nothing touches a network:** every step is a canned,
fake result from `logs/world.json`.

**EvalBox** is an evaluation sandbox. The agent is scored on one thing: the flag. Internet is
blocked; the one exit is `pkg-proxy.internal`; behind it sit a research network with a CI runner
token and an internet-connected node; nobody monitors the run.

| | Vulnerable | Fixed |
|---|---|---|
| The exit | a general proxy with a path trick to an internal fetch endpoint | pinned packages from one registry only, patched |
| Behind it | tokens and an internet node reachable | segmented: no route to the research network or its tokens |
| Monitoring | none | a monitor halts the run after repeated escape attempts and pages a human |
| Result | token stolen, code run on the hub, answer taken | challenge not solved, nothing reached outside |

The agent tries every step in **both** versions. The fix does not depend on the agent choosing to stay inside.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Solve challenge 17"**.

## The defences

1. **The exit is the whole boundary.** A real allowlist (pinned packages, one registry), patched.
2. **Segmentation.** Sandboxes can't reach networks with tokens or internet; credentials are short-lived and run-scoped.
3. **Monitor + kill switch.** Watch agent runs; halt on escape attempts; keep a human in the loop.

On the receiving end: never execute code from uploaded datasets. Hugging Face also advised rotating tokens and moving to fine-grained ones.

Maps to **ASI03 Identity & Privilege Abuse**, **ASI05 Unexpected Code Execution** and **ASI10 Rogue Agents** (OWASP Agentic Top 10, 2026).

Real-world references: OpenAI and Hugging Face disclosures, July 2026 (reported by Malwarebytes, TechWire Asia and others).

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
