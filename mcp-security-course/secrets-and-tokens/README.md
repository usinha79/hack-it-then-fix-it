# MCP01 Secrets and tokens

> The most expensive breaches start with a key sitting in plain sight: in a log, a config file, a tool's own output, or the model's context.

**Module 6 of the MCP Security course.** Maps to MCP01 on the OWASP MCP Top 10 (2025, beta).

## The attack

Secrets leak into four places: server logs, config and code, tool descriptions or output, and the model's own running context. A read only foothold is enough to collect them.

## Why it works

A secret in the model's reach is one injection away from leaving, because the model's context gets logged, echoed and carried forward, and the model can be tricked into repeating it.

## The fix

Keep every secret out of the model's reach, store keys in a dedicated secrets store and never in code or committed config, redact logs, never echo keys in tools or errors, and use short lived tokens with fast rotation and an instant revoke path.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
