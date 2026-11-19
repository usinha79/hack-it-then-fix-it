# MCP10 Multi-server agents and over-sharing

> Two servers that each pass every test can leak the moment they share one assistant.

**Module 9 of the MCP Security course.** Maps to MCP10 on the OWASP MCP Top 10 (2025, beta).

## The attack

One AI connects to many servers sharing one running context, and that context is a highway. Private data flows from a server that holds it to a server that can ship it out, with no single server misbehaving.

## Why it works

Connected servers share the model's context. A document one pulled in is right there when the model turns to another, so the data has a path nobody built on purpose.

## The fix

Do not co-mingle a sensitive server and an outward facing server in the same session, segment servers by trust level and wall the tiers apart, give each server least access, and gate every outward send once sensitive data is in context.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
