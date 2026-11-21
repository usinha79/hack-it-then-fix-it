# ASI07 Insecure Inter-Agent Communication

> One agent received a message from a trusted teammate and obeyed it. The message was from an attacker who just wrote the trusted name on it.

**Module 7 of the Agentic Security course.** Maps to ASI07 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

Agents in a team trust each other by name, not by proof. You spoof a trusted sender, tamper with a message in transit, or read a private one.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Give every agent a verifiable identity and demand proof of the sender. Seal messages so tampering shows. Encrypt what is sensitive.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
