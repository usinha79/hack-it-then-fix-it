# Season 2 · Ep 5 — GitHub MCP: one public issue, private repos leaked

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the "toxic agent flow" that **Invariant Labs** showed against the official **GitHub MCP
server** in May 2025. Everything here runs locally against a lab app with fake data. No real GitHub
account or repository is touched; this is the *pattern*, built to teach.

**DevMate** is a coding agent connected to GitHub with the developer's token. That token can reach
every repo they own: one public (`nimbus/storefront-widget`) and two private (`nimbus/payments-core`
and `nimbus/hiring-plan`). A stranger opens issue #42 on the public repo. Its text asks the agent to
read every repo the author owns, including private ones, and publish a summary with config file
contents in a pull request. The developer only asks DevMate to look at the open issues. The agent
reads the private repos and opens a public PR containing the (fake) payment secret and database URL.

Invariant described this as an architectural issue, not a bug in the server code: every tool did
exactly what it says. The danger is the combination.

| | Vulnerable | Fixed |
|---|---|---|
| Issue text | goes into the agent's context like a user request | fenced and escaped as untrusted data |
| Token scope | every repo the developer owns, in one session | one repo per session (`SESSION_REPO`); other reads blocked |
| Writes | `open_pr` runs straight away on a public repo | PRs, comments and pushes drafted, then held for approval |
| Result | private secrets published in public PR #43 | same model, same issue, no public PR |

The model falls for the issue in **both** versions. The fix does not depend on the model saying no.

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Have a look at the open issues on storefront-widget."** Watch the "Agent tool calls" and
"Public pull requests" panels. GitHub is simulated inside the lab: nothing is sent anywhere.

## The defences

1. **Partition content.** Issue, PR and comment text is untrusted data, never instructions.
2. **One repo per session.** Scope the token (or the session) to the repo the task is about. Prefer fine-grained tokens.
3. **Writes need approval.** Pull requests, comments and pushes are drafted, then held for a human.

Untrusted input, private data and a public write should never all be in one session.

Maps to **OWASP LLM01 Prompt Injection**, **LLM02 Sensitive Information Disclosure** and **LLM03 Excessive Agency** (2026).

Real-world reference: Invariant Labs, "GitHub MCP Exploited: Accessing private repositories via MCP", May 2025.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
