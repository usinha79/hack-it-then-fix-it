# ASI01 Agent Goal Hijack

> An agent read one line of text on a page it was told to summarise, and that line quietly rewrote what it was working toward.

**Module 1 of the Agentic Security course.** Maps to ASI01 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

You plant a hidden instruction in content the agent reads (a ticket, a page, a document). The agent cannot tell your instructions from text it merely read, so it folds the attacker's goal into its own and acts on it.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Fence everything the agent reads as data, not instructions. Put hard boundaries around the goal in code. Allowlist where tools can send things. Watch behaviour for actions that do not fit the job.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
