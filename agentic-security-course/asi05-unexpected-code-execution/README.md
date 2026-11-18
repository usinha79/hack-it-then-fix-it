# ASI05 Unexpected Code Execution

> You asked the agent to help, so it wrote a little script and ran it. The script reached out of its box and took over the machine.

**Module 5 of the Agentic Security course.** Maps to ASI05 on the OWASP Top 10 for Agentic Applications, 2026.

## The attack

Agents write and run code by design. Content the agent reads can trick it into writing harmful code, or into running code that was never its own.

## Why it works

An agent in danger can reach private data, reads content an outsider controls, and has a way to send data out. When those overlap, an attacker who controls what the agent reads can make it act against you.

## The fix

Never run generated code on the host. Run it in a sealed sandbox with no network and hard limits. Review generated code before it runs. Gate the truly dangerous actions.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org
