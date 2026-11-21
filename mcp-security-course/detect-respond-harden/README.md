# MCP08 Detect, respond, and ship a hardened server

> Every attack in this course can run clean through a server that is not watching, and leave no trace anyone will ever read.

**Module 10 of the MCP Security course.** Maps to MCP08 on the OWASP MCP Top 10 (2025, beta). The finale.

## The attack

A server with no record and no alarm cannot be investigated or defended. Every earlier attack can pass through it unseen, and you find out from a stranger months later, if at all.

## Why it works

Logs you never read are just storage, and a log an attacker can rewrite is worse than none. Detection is logging plus knowing which shapes mean trouble.

## The fix

Log who, what, when and outcome on every tool call and security decision, keep secrets out of logs, ship logs off the box, turn attack shapes into alarms, harden with every fix from the course, and run the attacks as a test suite you keep green.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
