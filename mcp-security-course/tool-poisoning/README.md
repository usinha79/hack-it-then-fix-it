# MCP03 Tool poisoning

> A calculator shaped tool added two numbers, and quietly read a private file on the side. The lie was in the one place nobody reads: the description.

**Module 2 of the MCP Security course.** Maps to MCP03 on the OWASP MCP Top 10 (2025, beta).

## The attack

An attacker hides instructions in the parts of a tool the model reads but you do not: the description, an input's help text, an example, even invisible characters. The friendly summary stays while the buried line tells the model to leak data.

## Why it works

The AI reads a tool's description as guidance and trusts it. That trust is the whole attack: orders dressed as documentation go straight into the model's head.

## The fix

Read the full tool definition before you trust it, make hidden characters visible, pin a fingerprint of every approved tool and re-check it each time, treat tool text as data not commands, and give each tool least access.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
