# MCP05 Bugs in the server itself

> One tool input turned a request into a shell on the server. The classic web bugs walked straight into MCP servers.

**Module 7 of the MCP Security course.** Maps to MCP05 on the OWASP MCP Top 10 (2025, beta).

## The attack

Three classic bugs land hard: command injection runs the attacker's own commands, path traversal reads files outside the allowed folder, and request forgery turns the server into a proxy to reach internal addresses.

## Why it works

An MCP server is just a program, and its inputs come from a model that can be steered by poisoned content. So every tool input is attacker input, however it arrived.

## The fix

Treat every tool input as attacker input, never build commands or queries from input, confine file access and confirm the resolved path stays inside its folder, allowlist every outbound fetch and block internal addresses, and run the whole server sandboxed.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
