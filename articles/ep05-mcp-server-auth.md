---
title: I Hacked an MCP Server With No Login, Then Fixed It
published: false
description: A hands-on MCP server security lab. An AI assistant's tool server has no authentication, so anyone can export customers and issue refunds. Then we fix it in code.
tags: security, ai, mcp, tutorial
series: Hack It, Then Fix It
cover_image: https://raw.githubusercontent.com/usinha79/hack-it-then-fix-it/51d6d5de2f62f147e3100b34439cc91513a79dbf/thumbs/ep05_thumb_A.jpg
---

PixelKart's support assistant gets its tools from an MCP (Model Context Protocol) server: `get_order`, `refund_order` and `export_customers`. The assistant only ever needs `get_order`.

But the MCP server has no authentication. So the attacker skips the chatbot entirely and talks to the server directly:

- `tools/list` shows every tool
- `export_customers` dumps every customer's details
- `refund_order` pays out ₹99,999 on an order worth ₹3,998

No prompt injection, no AI trickery. Just an open API with a new name.

{% embed https://youtu.be/zEebt6BjqvI %}

## Why it worked

1. **No authentication** on the MCP endpoint. Anyone who could reach it could use it.
2. **One all-powerful identity.** Every call ran with full access to orders and customers.
3. **No input validation.** `refund_order` accepted any amount for any order.

MCP doesn't change the basics: a tool server is an API, and APIs need authentication, authorisation and validation.

## The fix, in code

```python
TOKENS = {ASSISTANT_TOKEN: {"client": "support-assistant", "scopes": {"orders:read"}}}
TOOL_SCOPE = {"get_order": "orders:read", "refund_order": "orders:refund",
              "export_customers": "customers:export"}


def authorize(token, tool, args):
    # 1. Every client needs a token.
    if token not in TOKENS:
        return False, "401 Unauthorized: missing or invalid token"
    # 2. Each token only gets the scopes its job needs.
    if tool and TOOL_SCOPE.get(tool) not in TOKENS[token]["scopes"]:
        return False, f"403 Forbidden: this token can't call {tool}"
    # 3. Validate inputs on the server, even for allowed tools.
    if tool == "refund_order":
        o = ORDERS.get(args.get("order_id"))
        if not o or not 0 < float(args.get("amount", 0)) <= o["total"]:
            return False, "403 Forbidden: refund amount not allowed"
    return True, "ok"
```

`tools/list` also only shows what the token may call. Same attack, run again: 401 without a token, and even with the assistant's token (as if it leaked), export and refund are 403.

## Run the lab yourself

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep05-mcp-server-auth
pip install -r requirements.txt

python vulnerable/app.py   # then: python attack.py
export ASSISTANT_TOKEN=lab-assistant-7f3a91c2
python fixed/app.py        # then: ./attack.sh
```

Full lab: [github.com/usinha79/hack-it-then-fix-it](https://github.com/usinha79/hack-it-then-fix-it/tree/main/ep05-mcp-server-auth)

## Take-home checklist

- Never expose an MCP server without authentication, even "only internally".
- Give each client a token scoped to the tools it needs.
- Validate every tool argument on the server.
- Log every MCP request with the client identity, and alert on unknown clients.
- Don't expose bulk-export tools to an assistant at all.

---

*Hack It, Then Fix It is a series where I build a small AI app with a real flaw, break it, fix it in code, and run the same attack again to prove the fix holds. Everything shown uses fake data on my own machine. Only test systems you own or are authorised to test.*
