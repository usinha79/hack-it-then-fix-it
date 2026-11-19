# MCP07 and MCP02 Authentication and authorization

> This server said it was protected. Nobody logged in, nobody sent a token, and it handed over everything anyway.

**Module 4 of the MCP Security course.** Maps to MCP07 and MCP02 on the OWASP MCP Top 10 (2025, beta).

## The attack

Servers break two ways: they trust a token they never verified, so a forged slip walks straight in, and they check identity but never permission, so a low privilege user reaches admin only data.

## Why it works

A remote server has to guard itself, and that is two jobs: prove who you are, then decide what you may do. Skip either and the whole internet is a user.

## The fix

Verify every token four ways (signature, expiry, issuer, audience) on every request, keep authentication and authorization separate, gate every action with may this user do this on this data, deny by default, and keep tokens least privileged and short lived.

## Try it free, in your browser

There is no runnable code in this folder, by design. Run this exact attack yourself, then turn on the fix and watch it hold:

**https://bugbountybeyond.com**

No install, no sign up to start. One free lab per risk.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org
