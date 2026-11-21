# Agentic Security: The Complete Course

A hands-on tour of the ten biggest ways an AI agent can be turned against you, and how to stop each one. Companion to the **Agentic Security: The Complete Course** on the Bug Bounty and Beyond channel.

Every risk maps to the **OWASP Top 10 for Agentic Applications, 2026**. For each one you watch the attack land, understand why it worked, and build the fix.

> There is no runnable attack code in this folder, by design. Each risk has a free, safe, in-browser lab where you run the attack yourself and then watch the fix hold. No install, no sign up to start.

## Try every attack free, in your browser

All labs live here: **https://bugbountybeyond.com**

One free lab per risk. Watch the module, then go break it yourself. That is where it sticks.

## The ten risks

| Module | Risk | What you do in the lab |
|--------|------|------------------------|
| 1 | [ASI01 Agent Goal Hijack](asi01-agent-goal-hijack/) | Hijack an agent's goal through content it reads, then turn on the fences and watch it hold. |
| 2 | [ASI02 Tool Misuse and Exploitation](asi02-tool-misuse-exploitation/) | Make an agent abuse its own tools, then constrain them with least privilege. |
| 3 | [ASI03 Identity and Privilege Abuse](asi03-identity-privilege-abuse/) | Abuse a delegated identity to see what you should not, then scope the token. |
| 4 | [ASI04 Agentic Supply Chain](asi04-agentic-supply-chain/) | Install a poisoned plugin, then verify and sandbox it. |
| 5 | [ASI05 Unexpected Code Execution](asi05-unexpected-code-execution/) | Escape through generated code, then sandbox and gate it. |
| 6 | [ASI06 Memory and Context Poisoning](asi06-memory-context-poisoning/) | Plant a memory that lasts across chats, then validate what gets saved. |
| 7 | [ASI07 Insecure Inter-Agent Communication](asi07-insecure-inter-agent-communication/) | Spoof an agent-to-agent message, then authenticate every sender. |
| 8 | [ASI08 Cascading Failures](asi08-cascading-failures/) | Trigger a chain reaction, then add circuit breakers. |
| 9 | [ASI09 Human-Agent Trust Exploitation](asi09-human-agent-trust-exploitation/) | Approve a convincing malicious suggestion, then add labelling and checks. |
| 10 | [ASI10 Rogue Agents](asi10-rogue-agents/) | Detect and kill a rogue agent, then run the full red team of all ten attacks. |

## The one idea to keep

An agent is in danger when three things are true at once: it can reach **private data**, it reads **untrusted content**, and it has a **way to send data out**. Almost every attack here needs that overlap. Break it, and most attacks have nowhere to go.

## References

- OWASP Top 10 for Agentic Applications, 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026
- OWASP: https://owasp.org

Watch the course, then run the labs free at **https://bugbountybeyond.com**.
