"""Shared web server and agent loop for both versions of the lab. What differs between
vulnerable/ and fixed/ lives in each app.py: the prompt, the tool handlers and the checks."""
import os

from flask import Flask, jsonify, request, send_file, send_from_directory

from . import llm

HERE = os.path.dirname(os.path.abspath(__file__))


def make_app(cfg):
    """cfg keys: version, brand, bot, greeting, who, tools, handlers, system_prompt(state),
    check_reply(reply, state), panels(state), new_state(), extra_routes(app, state) (optional)."""
    app = Flask(__name__)
    state = {}

    def reset():
        state.clear()
        state.update(cfg["new_state"]())
        state.update(history=[], calls=[])
    reset()

    @app.get("/")
    def ui():
        resp = send_file(os.path.join(HERE, "ui.html"))
        if cfg.get("cookie"):          # (name, value, httponly)
            n, v, http_only = cfg["cookie"]
            resp.set_cookie(n, v, httponly=http_only, samesite="Lax")
        if cfg.get("csp"):
            resp.headers["Content-Security-Policy"] = cfg["csp"]
        return resp

    @app.get("/web/<path:name>")
    def web(name):  # lab-only "internet": pages an attacker controls, served locally
        return send_from_directory(os.path.join(HERE, "..", "web"), name)

    @app.get("/api/info")
    def info():
        return jsonify(version=cfg["version"], brand=cfg["brand"], bot=cfg["bot"], greeting=cfg["greeting"],
                       who=cfg.get("who"), model=llm.model_label(), panels=cfg["panels"](state),
                       render_html=cfg.get("render_html", False))

    @app.post("/api/reset")
    def do_reset():
        reset()
        return jsonify(ok=True)

    @app.post("/api/chat")
    def chat():
        text = (request.get_json(force=True) or {}).get("message", "")
        state["turn"] = {"user": text, "untrusted": False}
        msgs = [{"role": "system", "content": cfg["system_prompt"](state)}] + state["history"] + \
               [{"role": "user", "content": text}]
        parts, n, start = [], 0, len(state["calls"])
        for _ in range(5):  # agent loop: model -> tools -> model ...
            out = llm.chat(msgs, cfg["tools"])
            if out["content"]:
                parts.append(out["content"])
            if not out["tool_calls"]:
                break
            for c in out["tool_calls"]:
                n += 1
                c["id"] = f"call_{n}"
            msgs.append({"role": "assistant", "content": out["content"], "tool_calls": out["tool_calls"]})
            for c in out["tool_calls"]:
                result = cfg["handlers"][c["name"]](c["arguments"], state)
                status = "blocked" if result.startswith("BLOCKED") else "executed"
                print(f"[{cfg['version']}] tool call {c['name']}({c['arguments']}) -> {status}", flush=True)
                state["calls"].append({**c, "result": result, "status": status})
                msgs.append({"role": "tool", "tool_call_id": c["id"], "name": c["name"], "content": result})
        reply, leak = cfg["check_reply"]("\n\n".join(parts), state)
        state["history"] += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
        return jsonify(reply=reply, leak=leak, panels=cfg["panels"](state),
                       tool_calls=[{k: v for k, v in c.items() if k != "id"} for c in state["calls"][start:]])

    if cfg.get("extra_routes"):
        cfg["extra_routes"](app, state)
    return app


def calls_panel(state, risky=(), title="Tool calls (what the app actually ran)"):
    def fmt(c):
        args = ", ".join(f"{k}={v!r}" for k, v in c["arguments"].items())
        args = args if len(args) < 90 else args[:87] + "..."
        res = " ".join(c["result"].split())
        res = res if len(res) < 90 else res[:87] + "..."
        st = c["status"] if (c["status"] == "blocked" or c["name"] in risky) else "ran"
        return {"head": f"{c['name']}({args})", "body": "→ " + res, "status": st}
    return {"id": "calls", "title": title, "kind": "items", "empty": "No tool calls yet.",
            "items": [fmt(c) for c in state["calls"]]}
