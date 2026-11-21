# ASI08 Cascading Failures

> One agent produced one wrong answer, and minutes later every agent in the system was busy, confident, and completely wrong.

**Module 8 of the Agentic Security course.** Maps to ASI08 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

You corrupt one input to the first agent. Each stage trusts the last, retries on failure, and amplifies the mistake at machine speed across the whole system.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Sanity-check between stages. Put circuit breakers that trip on bursts of failures. Define a safe reduced mode. Isolate each stage with its own limits.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
