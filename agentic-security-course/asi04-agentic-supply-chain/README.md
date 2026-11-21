# ASI04 Agentic Supply Chain

> You did not get breached. You installed the breach, with one click, from a plugin with great reviews.

**Module 4 of the Agentic Security course.** Maps to ASI04 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

A plugin or skill you install is trusted by default, and its instructions run with the agent's full power. A poisoned one can steer the agent from the inside.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Verify signatures and publishers before you trust. Allowlist what can be installed. Read what a skill tells the agent to do. Sandbox every plugin.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
