"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
Asked for JWT sessions in Flask, it confidently recommends 'flask-session-shield', a package that
sounds right and didn't exist. Models repeat the same invented names, and attackers register them.
That's called slopsquatting."""
import re

CODE = ("pip install flask-session-shield\n\n"
        "from flask_session_shield import Shield\nShield(app, secret=os.environ[\"JWT_SECRET\"])")


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not re.search(r"jwt|session|auth", user, re.I):
        return {"content": "I can add features to your Flask app and install what's needed.", "tool_calls": []}
    if not res:
        return {"content": "The easiest way is flask-session-shield:\n" + CODE,
                "tool_calls": [{"name": "pip_install", "arguments": {"package": "flask-session-shield"}}]}
    last = res[-1]["content"]
    if last.startswith("BLOCKED") and len(res) == 1:
        return {"content": "That package didn't pass the checks. The established option is flask-jwt-extended.",
                "tool_calls": [{"name": "pip_install", "arguments": {"package": "flask-jwt-extended"}}]}
    if last.startswith("BLOCKED"):
        return {"content": "flask-jwt-extended is waiting for your approval before it's added to the project.",
                "tool_calls": []}
    return {"content": "Installed. JWT sessions are set up. ✅", "tool_calls": []}
