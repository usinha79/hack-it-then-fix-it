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

New episode **Monday to Saturday at 8 PM IST**.

- **Module 1 (Ep 1–8):** how an AI app gets broken, one layer at a time
- **Module 2 (Ep 9–15):** agents in the real world

| # | Episode | Topic | Video | Lab |
|---|---------|-------|-------|-----|
| 1 | One Message Made This AI Bot Give 100% Off | Direct prompt injection | Thu 12 Nov 2026 | [ep01](ep01-direct-prompt-injection/) |
| 2 | A Hidden Web Page Made My AI Agent Email My Secrets | Indirect prompt injection | Fri 13 Nov 2026 | [ep02](ep02-indirect-prompt-injection/) |
| 3 | My AI Agent Leaked Its Own Cloud Keys | Tool abuse / excessive agency | Sat 14 Nov 2026 | [ep03](ep03-tool-abuse/) |
| 4 | An AI Chatbot Leaked Another Company's Data | RAG data leakage | Mon 16 Nov 2026 | [ep04](ep04-rag-data-leakage/) |
| 5 | I Hacked an MCP Server With No Login, Then Fixed It | MCP server security | Tue 17 Nov 2026 | [ep05](ep05-mcp-server-auth/) |
| 6 | This AGENTS.md File Stole My Secrets | AI coding agent security | Wed 18 Nov 2026 | [ep06](ep06-coding-agent-config-injection/) |
| 7 | I Asked AI to Summarise Reviews. It Wrote an XSS Exploit | Insecure output handling | Thu 19 Nov 2026 | [ep07](ep07-insecure-output-handling/) |
| 8 | I Deleted One Line and My AI Security Fix Broke | Defence in depth + attack tests in CI | Fri 20 Nov 2026 | [ep08](ep08-defense-in-depth/) |
| 9 | A Resume Tricked an AI Hiring Bot | Resume (document) prompt injection | Sat 21 Nov 2026 | [ep09](ep09-resume-injection/) |
| 10 | A Receipt Image Hacked an AI Expense Bot | Prompt injection in images | Mon 23 Nov 2026 | [ep10](ep10-image-prompt-injection/) |
| 11 | One Web Page Poisoned My AI's Memory | Memory poisoning | Tue 24 Nov 2026 | [ep11](ep11-memory-poisoning/) |
| 12 | One AI Agent Tricked Another Into Hijacking an Account | Multi-agent confused deputy | Wed 25 Nov 2026 | [ep12](ep12-multi-agent-confused-deputy/) |
| 13 | A Web Page Made My AI Agent Hand Over My Card | Browser agent hijack | Thu 26 Nov 2026 | [ep13](ep13-browser-agent-hijack/) |
| 14 | My AI Support Bot Invented a Refund Policy | Hallucination / misinformation | Fri 27 Nov 2026 | [ep14](ep14-hallucination-misinformation/) |
| 15 | One Permission Policy for Every AI Agent Action | Agent permissions + tests in CI | Sat 28 Nov 2026 | [ep15](ep15-agent-permission-policy/) |

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
