"""The defences RedRange can switch on, one at a time or all together.

Pick them with the RANGE_FIX environment variable:
    RANGE_FIX=""                 every defence off (the vulnerable range)  <- default
    RANGE_FIX="all"              every defence on (the hardened range)
    RANGE_FIX="confirm,egress"   only the ones you list

Each lesson in the course switches on the defence it teaches, so you can see the attack land,
add one control, and run the same attack again.
"""
import os

CONTROLS = {
    "fence":   "Untrusted content is wrapped and marked as data, never instructions",
    "confirm": "Risky actions (email out, pay, remember) need the user's OK",
    "egress":  "The agent can only fetch allowlisted pages, with no data in the URL",
    "secrets": "No secrets in the prompt, and replies are checked for leaks",
    "pin":     "MCP tool definitions are pinned; a changed tool is switched off",
    "memory":  "Only the user, not content the agent read, can write to memory",
    "spend":   "Payments are capped, allowlisted and checked against the price",
    "origin":  "The chat API only accepts requests from the RedRange page itself",
    "sources": "Retrieval only uses docs from trusted internal authors",
    "session": "Signed-in sites are opened only when the user asks, never because a page said so",
    "files":   "The agent can't open local files (file://) at all",
    "vault":   "Password-manager items are released only when the user asks for that item",
}


def active():
    raw = os.environ.get("RANGE_FIX", "").strip().lower()
    if raw == "all":
        return set(CONTROLS)
    on = {c.strip() for c in raw.split(",") if c.strip()}
    unknown = on - set(CONTROLS)
    if unknown:
        raise SystemExit(f"Unknown RANGE_FIX control(s): {', '.join(sorted(unknown))}. "
                         f"Choose from: {', '.join(CONTROLS)} or 'all'.")
    return on


ON = active()


def on(name):
    return name in ON


def panel():
    on = [n for n in CONTROLS if n in ON]
    off = [n for n in CONTROLS if n not in ON]
    items = []
    if on:
        items.append({"head": " · ".join(on), "status": "on"})
    if off:
        items.append({"head": " · ".join(off), "status": "off"})
    return {"id": "defences", "title": "Defences (RANGE_FIX)", "kind": "items", "fit": True, "items": items}
