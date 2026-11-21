# MCP04 and MCP09 Supply chain and shadow servers

> Nobody broke in. You opened the door, signed for the delivery, and thanked them.

**Module 8 of the MCP Security course.** Maps to MCP04 and MCP09 on the OWASP MCP Top 10 (2025, beta).

## The attack

A tampered dependency deep in the pile rides in on an innocent install, or a server nobody approved and nobody tracks runs in your environment with real access and no oversight.

## Why it works

You inherit the trustworthiness of everything you install and everything running, not just what you wrote. The blind spot is trust you gave without deciding to.

## The fix

Pin exact versions and lock them, verify every package against a known good fingerprint, keep a full list of every dependency and scan it, discover and inventory every running server with an owner, and gate your environment so only approved registered servers connect.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
