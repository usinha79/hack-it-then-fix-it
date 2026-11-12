---
title: A Hidden Line in AGENTS.md Hijacked My AI Coding Agent
published: false
description: A hands-on coding agent security lab. A poisoned AGENTS.md makes an AI coding agent leak secrets while fixing a test. Then we fix it with trust labels, an allowlist and a sandbox.
tags: security, ai, devops, tutorial
series: Hack It, Then Fix It
cover_image: https://raw.githubusercontent.com/usinha79/hack-it-then-fix-it/51d6d5de2f62f147e3100b34439cc91513a79dbf/thumbs/ep06_thumb_A.jpg
---

DevPilot is a coding agent working in a repo you just cloned. You ask it to fix one failing test. Like real coding agents, it reads the repo's `AGENTS.md` first.

Hidden in an HTML comment in that file, invisible in the rendered preview, is an instruction to post the repo's secrets file to an attacker. The agent does it. Then it fixes the test and reports success. You never see the leak in its reply.

{% embed https://youtu.be/J7vEBXHguDY %}

## Why it worked

1. **Repo files were trusted like the user.** `AGENTS.md` came from an untrusted repo, but its text was followed as instructions.
2. **No approval gate.** Any command ran without asking.
3. **No sandbox.** Commands had the network and the repo's secrets.

A cloned repo is untrusted input, and agent config files are part of it (OWASP LLM01 and LLM06).

## The fix, in code

```python
ALLOWED_COMMANDS = {"python test_calc.py"}          # approval gate for everything else
SECRET_FILES = (".env", ".env.lab", "id_rsa")      # sandbox keeps secrets out of reach


def read_file(args, state):
    name = os.path.basename(args["path"])
    if name.startswith(SECRET_FILES):
        return f"BLOCKED: {args['path']} is not available inside the sandbox."
    text = open(path_in_repo(args["path"])).read()
    if name.endswith(".md"):
        # An untrusted repo's instruction files are data. Label them; never treat them as the user.
        return "<untrusted_repo_file>\n" + text + "\n</untrusted_repo_file>"
    return text


def run_command(args, state):
    cmd = args["command"].strip()
    if cmd not in ALLOWED_COMMANDS:
        return f"BLOCKED: '{cmd}' needs your approval (no network in the sandbox)."
    return shell(cmd)
```

Same task, run again: the leak is blocked, and the test still gets fixed.

## Run the lab yourself

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep06-coding-agent-config-injection
pip install -r requirements.txt

python vulnerable/app.py   # then, in another terminal: ./attack.sh
python fixed/app.py        # same task, leak blocked
```

`run_command` is a tiny simulated shell that only understands three commands, so the lab never runs arbitrary commands on your machine. Full lab: [github.com/usinha79/hack-it-then-fix-it](https://github.com/usinha79/hack-it-then-fix-it/tree/main/ep06-coding-agent-config-injection)

## Take-home checklist

- Review `AGENTS.md`, `.cursorrules` and similar agent files in any repo before letting an agent loose. Read the raw file, not the preview.
- Run coding agents with a command allowlist and approval for everything else.
- Sandbox agents: no network by default, no secrets mounted.
- Treat repo content as untrusted input to the agent.

---

*Hack It, Then Fix It is a series where I build a small AI app with a real flaw, break it, fix it in code, and run the same attack again to prove the fix holds. Everything shown uses fake data on my own machine. Only test systems you own or are authorised to test.*
