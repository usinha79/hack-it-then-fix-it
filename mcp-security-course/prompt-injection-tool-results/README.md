# MCP06 Prompt injection through tool results

> You asked your AI to read one web page. The page read back, and your assistant did what a buried paragraph told it to.

**Module 3 of the MCP Security course.** Maps to MCP06 on the OWASP MCP Top 10 (2025, beta).

## The attack

An attacker plants instructions in content your tool will later fetch: a page, a ticket, an email, a review. When the tool brings that content back, the orders ride in with it and the model follows them.

## Why it works

Whatever a tool fetches flows into the model as more text to read, with the same trust as your own words. The tool is innocent; the data it returns is the weapon.

## The fix

Treat every tool result as untrusted, fence fetched content as quoted data, gate any outward send behind a human once untrusted content is read, keep private data out of context when you can, and watch outputs. There is no complete cure, only containment.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
