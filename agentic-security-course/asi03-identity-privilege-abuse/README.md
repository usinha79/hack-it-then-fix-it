# ASI03 Identity and Privilege Abuse

> A low-privilege user asked an agent a simple question, and the agent answered it with a key that opens the whole building.

**Module 3 of the Agentic Security course.** Maps to ASI03 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

The agent acts on its own broad identity instead of the user's. The user's real permissions never travel with the request, so a small user borrows the agent's giant access.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Carry the real user's identity all the way down and check it at the data. Scope every token to one task. Keep tokens short-lived so a leak expires fast.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
