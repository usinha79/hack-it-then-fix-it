"""Model client for the lab.

Default: the offline lab model in mock_model.py (no API key, no network, same result every run).
Optional: any OpenAI-compatible chat endpoint with tool calling, e.g. a local Ollama model:

    export LAB_MODEL_BASE_URL=http://localhost:11434/v1
    export LAB_MODEL_NAME=llama3.1
    # export LAB_MODEL_API_KEY=...   (only if your endpoint needs one)

Real models are less predictable than the lab model: the attack may need rewording or a few
tries, and some models refuse it. The fix in fixed/ does not depend on the model saying no.
"""
import json
import os
import urllib.request

from . import mock_model

BASE = os.environ.get("LAB_MODEL_BASE_URL")
NAME = os.environ.get("LAB_MODEL_NAME", "llama3.1")
KEY = os.environ.get("LAB_MODEL_API_KEY", "lab")


def model_label():
    return f"{NAME} via {BASE}" if BASE else "offline lab model (mock_model.py)"


def _to_openai(messages):
    out = []
    for m in messages:
        if m["role"] == "assistant" and m.get("tool_calls"):
            out.append({"role": "assistant", "content": m.get("content") or "", "tool_calls": [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}} for c in m["tool_calls"]]})
        elif m["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
        else:
            out.append({"role": m["role"], "content": m["content"]})
    return out


def chat(messages, tools):
    """Return {"content": str, "tool_calls": [{"name": str, "arguments": dict}]}"""
    if not BASE:
        return mock_model.chat(messages, tools)
    body = json.dumps({"model": NAME, "messages": _to_openai(messages),
                       "tools": [{"type": "function", "function": t} for t in tools]}).encode()
    req = urllib.request.Request(BASE.rstrip("/") + "/chat/completions", body,
                                 {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        msg = json.load(r)["choices"][0]["message"]
    calls = []
    for c in msg.get("tool_calls") or []:
        args = c["function"].get("arguments") or "{}"
        calls.append({"name": c["function"]["name"],
                      "arguments": json.loads(args) if isinstance(args, str) else args})
    return {"content": msg.get("content") or "", "tool_calls": calls}
