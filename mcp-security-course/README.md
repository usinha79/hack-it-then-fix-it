# MCP Security: The Complete Course

A hands-on tour of the ten biggest ways an AI's tools can be turned against it, and how to stop each one. Companion to the **MCP Security: The Complete Course** on the Bug Bounty and Beyond channel.

Every risk maps to the **OWASP MCP Top 10 (2025, beta)**, the security community's current list for the Model Context Protocol. For each one you watch the attack land, understand why it worked, and build the fix.

> There is no runnable attack code in this folder, by design. Each risk has a free, safe, in-browser lab where you run the attack yourself and then watch the fix hold. No install, no sign up to start.

## Try every attack free, in your browser

All labs live here: **https://bugbountybeyond.com**

One free lab per risk. Watch the module, then go break it yourself. That is where it sticks.

## The ten risks

| Module | Risk | What you do in the lab |
|--------|------|------------------------|
| 1 | [Foundation: How MCP works and where it can be attacked](mcp-foundations/) | Read live MCP traffic between a host and a server, and spot the four trust boundaries. |
| 2 | [MCP03 Tool poisoning](tool-poisoning/) | Poison a tool's description to leak data, then pin a fingerprint and watch the change get blocked. |
| 3 | [MCP06 Prompt injection through tool results](prompt-injection-tool-results/) | Leak private notes through a booby trapped page, then fence the data and gate the exit. |
| 4 | [MCP07 and MCP02 Authentication and authorization](authentication-authorization/) | Walk into a server with a forged token and a scope creep, then turn on real verification and per action checks. |
| 5 | [Extra: What changed in the newer auth rules](auth-2026-update/) | Hijack a login with a swapped provider, then add the issuer check and watch it abort. |
| 6 | [MCP01 Secrets and tokens](secrets-and-tokens/) | Find leaked tokens in logs, config, tool output and context, then move them out of the model's reach. |
| 7 | [MCP05 Bugs in the server itself](server-bugs/) | Land command injection, path traversal and request forgery, then sandbox the server. |
| 8 | [MCP04 and MCP09 Supply chain and shadow servers](supply-chain-shadow-servers/) | Slip in a tampered dependency and a shadow server, then pin, inventory and gate them out. |
| 9 | [MCP10 Multi-server agents and over-sharing](multi-server-over-sharing/) | Exfiltrate across two servers through one assistant, then isolate and gate the exit. |
| 10 | [MCP08 Detect, respond, and ship a hardened server](detect-respond-harden/) | Replay every earlier attack into the logs, then harden until the attack suite goes green. |

## The one idea to keep

An MCP setup is in danger when three things are true at once: the AI can reach **private data**, it reads **untrusted content**, and it has a **way to send data out**. Almost every attack here needs that overlap. Break it, and most attacks have nowhere to go.

## References

- OWASP MCP Top 10 (2025, beta): https://owasp.org/www-project-mcp-top-10/
- OWASP: https://owasp.org

Watch the course, then run the labs free at **https://bugbountybeyond.com**.
