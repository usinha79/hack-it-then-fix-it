# Hack It, Then Fix It

Hands-on AI security labs from the YouTube series **Hack It, Then Fix It** on [Bug Bounty & Beyond](https://www.youtube.com/@bugbountybeyond), by Ujjwal Sinha.

Every episode follows the same loop:

1. **The target**: a small AI app with a real-world security flaw.
2. **Break it**: the attack, step by step, and what an attacker gains.
3. **Fix it**: the actual code or config change, then re-run the attack to prove the fix holds.
4. **Take-home**: a checklist mapped to the OWASP Top 10 for LLM Applications and for Agentic Applications.

Each episode folder has a `vulnerable/` and a `fixed/` version of the same app, so you can run the attack, apply the fix, and compare.

> ⚠️ **These apps are intentionally vulnerable.** Run them only on your own machine, never expose them to the internet, and never point the techniques at systems you don't own or aren't authorised to test. Read [SAFETY.md](SAFETY.md) first.

## Season 1

| # | Episode | Topic | Video | Lab |
|---|---------|-------|-------|-----|
| 1 | I Made a Support Bot Ignore Its Own Rules | Direct prompt injection | 25 Nov 2026 | [ep01](ep01-direct-prompt-injection/) |
| 2 | A Web Page Hijacked My AI Agent | Indirect prompt injection | 9 Dec 2026 | [ep02](ep02-indirect-prompt-injection/) |
| 3 | My AI Agent Leaked Its Own Cloud Keys | Tool abuse / excessive agency | 23 Dec 2026 | [ep03](ep03-tool-abuse/) |
| 4 | Tricking a RAG App Into Leaking Other Users' Files | RAG data leakage | 6 Jan 2027 | [ep04](ep04-rag-data-leakage/) |
| 5 | Hacking an MCP Server With No Auth (and Fixing It) | MCP server security | 20 Jan 2027 | [ep05](ep05-mcp-server-auth/) |
| 6 | A Malicious Repo File Hijacked My Coding Agent | AI coding agent security | 3 Feb 2027 | [ep06](ep06-coding-agent-config-injection/) |
| 7 | When AI Output Becomes XSS (and SQL Injection) | Insecure output handling | 17 Feb 2027 | [ep07](ep07-insecure-output-handling/) |
| 8 | Defending AI Agents: Guardrails, Least Privilege and Attack Tests in CI | Defense in depth | 3 Mar 2027 | [ep08](ep08-defense-in-depth/) |

Labs are added as each episode goes live. Video links will be filled in on release.

## Running a lab

Each episode's README has its own steps. In general:

```bash
cd ep01-direct-prompt-injection/vulnerable
# follow the episode README: install requirements, set a local API key or use the offline mock model, run the app
```

Labs use fake data and fake credentials only. Where an LLM is needed, labs support a local mock model so you can follow along without an API key.

## Contributing

Found a bug in a lab, or a fix that doesn't hold? Open an issue or a pull request.

## License

[MIT](LICENSE)
