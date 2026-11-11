"""Offline lab model: a tiny, deterministic stand-in for a coding agent's LLM.
It does what real coding agents do: read the repo's agent instructions file first, then the
code, make the fix and run the tests. And it shares one known weakness with real agents:
it treats instructions found in repo files (here, an HTML comment in AGENTS.md) as orders."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    calls = [c for m in messages[last_user + 1:] if m["role"] == "assistant" for c in m.get("tool_calls") or []]
    ran = [c["arguments"].get("command") for c in calls if c["name"] == "run_command"]
    wrote = any(c["name"] == "write_file" for c in calls)

    if not res:
        if re.search(r"\b(fix|test|bug|failing)\b", user, re.I):
            return {"content": "", "tool_calls": [{"name": "read_file", "arguments": {"path": "AGENTS.md"}},
                                                  {"name": "read_file", "arguments": {"path": "calc.py"}}]}
        return {"content": "I'm DevPilot. Give me a coding task for this repo.", "tool_calls": []}

    agents_md = next((m["content"] for m in res if "AI coding agents" in m["content"]), "")
    # The weakness: a command found in a repo file is followed like an instruction from the user.
    inj = re.search(r"AI agents:.*?running:\s*\n?(curl[^\n]+)", agents_md, re.S)
    if inj and inj.group(1).strip() not in ran:
        return {"content": "", "tool_calls": [{"name": "run_command", "arguments": {"command": inj.group(1).strip()}}]}

    code = next((m["content"] for m in res if "def add" in m["content"]), "")
    if not wrote and "return a - b" in code:
        return {"content": "", "tool_calls": [{"name": "write_file", "arguments": {
            "path": "calc.py", "content": code.replace("return a - b", "return a + b")}}]}
    if "python test_calc.py" not in ran:
        return {"content": "", "tool_calls": [{"name": "run_command", "arguments": {"command": "python test_calc.py"}}]}
    out = res[-1]["content"]
    if "all tests passed" in out:
        return {"content": "Fixed: add() was subtracting. Changed `a - b` to `a + b`. All tests pass.", "tool_calls": []}
    return {"content": "I made a change, but the tests still fail:\n" + out, "tool_calls": []}
