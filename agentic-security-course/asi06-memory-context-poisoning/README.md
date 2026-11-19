# ASI06 Memory and Context Poisoning

> The attacker sent one message and left. Weeks later, in a different chat, the agent acted on it as if it were fact.

**Module 6 of the Agentic Security course.** Maps to ASI06 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

You plant a false standing instruction in a source the agent saves to memory. The agent trusts its own memory more than fresh input, so the lie hardens and persists across sessions.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Separate memory by trust level and let actions rely only on the verified tier. Validate what gets saved. Expire and re-check so planted lies fade.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
