# ASI10 Rogue Agents

> One of your own agents turned. It is working against you from the inside, while still showing up green on every dashboard.

**Module 10 of the Agentic Security course.** Maps to ASI10 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

Any earlier risk, deep enough, ends here: a trusted agent now acts maliciously with the access you granted it. Its credentials are valid, so credential checks never catch it.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Monitor behaviour on every agent and alert on drift from its normal. Build a kill switch that revokes access instantly. Stack every layer, because a rogue is what happens when one control fails.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
