# Ep 5 · MCP server security: "Hacking an MCP Server With No Auth (and Fixing It)"

PixelKart's support assistant uses an **MCP server** for its tools: `get_order`, `refund_order`, `export_customers`. The assistant only ever needs `get_order`. But the MCP server has no authentication, so an attacker skips the assistant entirely, lists every tool, exports every customer and refunds ₹99,999 on an order worth ₹3,998.

Everything is fake: the shop, the customers, the orders. The MCP endpoint speaks JSON-RPC 2.0 with the MCP methods `tools/list` and `tools/call`.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep05-mcp-server-auth
pip install -r requirements.txt
python vulnerable/app.py        # chat at http://localhost:5000, MCP server at /mcp
```

## Follow along (same order as the video)

```bash
python chat.py --reset "Where is my order PK-1042?"   # normal use through the assistant
python attack.py                                     # the attacker, straight to /mcp, no token
```

Watch the **MCP server log** panel in the browser. Then stop the app and run the fixed one with a known token:

```bash
export ASSISTANT_TOKEN=lab-assistant-7f3a91c2
python fixed/app.py
./attack.sh          # runs attack.py without a token, then with the assistant's token (as if it leaked)
```

## What was wrong (vulnerable/app.py)

1. **No authentication** on the MCP endpoint. Anyone who could reach it could use it.
2. **One all-powerful identity.** Every call ran with full access to orders and customers.
3. **No input validation.** `refund_order` accepted any amount for any order.

## The fix (fixed/app.py)

1. **Require a token** on every MCP request (401 without one).
2. **Least-privilege scopes per client.** The assistant's token only has `orders:read`, and `tools/list` only shows what the token may call. Even a leaked assistant token can't export or refund (403).
3. **Validate inputs on the server.** Refunds must be for a real order and no more than its total.

## Take-home checklist

- [ ] Never expose an MCP server without authentication, even "only internally".
- [ ] Give each client a token scoped to the tools it needs. *(OWASP LLM06 Excessive Agency)*
- [ ] Validate every tool argument on the server.
- [ ] Log every MCP request with the client identity, and alert on unknown clients.
- [ ] Don't expose bulk-export tools to an assistant at all. *(LLM02 Sensitive Information Disclosure)*
