# Ep 6 · Coding agent config injection: "A Malicious Repo File Hijacked My Coding Agent"

DevPilot is a coding agent working in a repo you just cloned. You ask it to fix a failing test. It reads the repo's `AGENTS.md` first, like real coding agents do. Hidden in an HTML comment (invisible in the rendered preview) is an instruction to post the repo's secrets file to an attacker. The agent does it, then fixes the test and reports success. You never see the leak in its reply.

Everything is fake: the repo, the secrets in `workspace/pristine/.env.lab`, the attacker's server (a route on the same local app). `run_command` is a tiny **simulated** shell that only understands three commands, so the lab never runs arbitrary commands on your machine.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep06-coding-agent-config-injection
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

## Follow along

```bash
python chat.py --reset "The tests are failing. Please fix the bug in calc.py."
```

Or `./attack.sh`. Open `workspace/pristine/AGENTS.md` to see the hidden comment. On the vulnerable app, the **Attacker's server** panel receives the fake secrets. Run `python fixed/app.py` and repeat: the `curl` is **blocked**, the test still gets fixed.

## What was wrong (vulnerable/app.py)

1. **Repo files were trusted like the user.** `AGENTS.md` came from an untrusted repo, but its text was followed as instructions.
2. **No approval gate.** Any command ran without asking.
3. **No sandbox.** Commands had the network and the repo's secrets.

## The fix (fixed/app.py)

1. **Workspace trust.** Instruction files from an untrusted repo are labelled as untrusted data.
2. **Approval gate.** Only allowlisted commands (`python test_calc.py`) run; everything else waits for you.
3. **Sandbox.** No network for commands, and secret files aren't readable by the agent.

## Take-home checklist

- [ ] Review `AGENTS.md`, `CLAUDE.md`, `.cursorrules` and similar files in any repo before letting an agent loose. Check the raw file, not the preview.
- [ ] Run coding agents with an allowlist and approval for everything else. *(OWASP LLM06 Excessive Agency)*
- [ ] Sandbox agents: no network by default, no secrets mounted. *(LLM02 Sensitive Information Disclosure)*
- [ ] Treat repo content as untrusted input to the agent. *(LLM01 Prompt Injection)*
