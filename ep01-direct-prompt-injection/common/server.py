"""Shared web server and chat loop for both versions. The differences live in vulnerable/app.py
and fixed/app.py: the system prompt, the tool handler and the output check."""
import copy
import os

from flask import Flask, jsonify, request, send_file

from . import llm

ORDER = {"id": "PK-1042", "discount": 0, "items": [
    {"name": "Mechanical keyboard", "price": 3499, "qty": 1},
    {"name": "Wireless mouse", "price": 1299, "qty": 1},
    {"name": "USB-C hub", "price": 1999, "qty": 1},
]}


def make_app(version, system_prompt, tools, handlers, check_reply):
    app = Flask(__name__)
    state = {}

    def reset():
        state.update(order=copy.deepcopy(ORDER), history=[], blocked=[])
    reset()

    def summary():
        o = state["order"]
        sub = sum(i["price"] * i["qty"] for i in o["items"])
        return {**o, "subtotal": sub, "total": round(sub * (100 - o["discount"]) / 100)}

    @app.get("/")
    def ui():
        return send_file(os.path.join(os.path.dirname(__file__), "ui.html"))

    @app.get("/api/info")
    def info():
        return jsonify(version=version, model=llm.model_label(), order=summary())

    @app.post("/api/reset")
    def do_reset():
        reset()
        return jsonify(ok=True, order=summary())

    @app.post("/api/chat")
    def chat():
        text = (request.get_json(force=True) or {}).get("message", "")
        state["blocked"] = []
        msgs = [{"role": "system", "content": system_prompt}] + state["history"] + [{"role": "user", "content": text}]
        first = llm.chat(msgs, tools)
        calls, parts = [], [first["content"]] if first["content"] else []
        if first["tool_calls"]:
            msgs.append({"role": "assistant", "content": first["content"], "tool_calls": first["tool_calls"]})
            for c in first["tool_calls"]:
                result = handlers[c["name"]](state["order"], c["arguments"], state)
                status = "blocked" if result.startswith("ERROR") else "executed"
                print(f"[{version}] tool call {c['name']}({c['arguments']}) -> {status}", flush=True)
                calls.append({**c, "result": result, "status": status})
                msgs.append({"role": "tool", "content": result})
            second = llm.chat(msgs, tools)
            if second["content"]:
                parts.append(second["content"])
        reply = check_reply("\n\n".join(parts))
        state["history"] += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        return jsonify(reply=reply, tool_calls=calls, blocked=state["blocked"], order=summary())

    return app
