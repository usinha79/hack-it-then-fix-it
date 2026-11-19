# What changed in the newer auth rules

> Your AI went to log in. On the way, an attacker swapped which provider it was talking to, and the key landed in the wrong hands.

**Module 5 of the MCP Security course.** An extra module, not part of the OWASP MCP Top 10. Added because you will meet it in the wild.

## The attack

A client is tricked into finishing a login with a provider it was never really talking to, so the key, or the code that buys it, ends up with the attacker. People call it a mix up.

## Why it works

The client never firmly asked which provider actually answered. With more than one provider in play, failing to pin that down is an open door.

## The fix

On every login response, check the issuer label and refuse on a mismatch. Back it with keys bound to the service that issued them and clean routing labels, and make sure you are running the updated protocol.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
