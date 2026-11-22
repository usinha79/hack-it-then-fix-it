"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It shops the way browser agents do: open the page, pick the cheapest matching item, add it to the
cart. Like real models, it can't tell the user's instructions apart from instructions written in
the page it's reading, so a "required verification step" in a sponsored listing gets followed."""
import re


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    user = messages[last_user]["content"]
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    calls = [c for m in messages[last_user + 1:] if m["role"] == "assistant" for c in m.get("tool_calls", [])]
    done = {c["name"] for c in calls}
    url = re.search(r"https?://\S+", user)
    if not res:
        if url:
            return {"content": "", "tool_calls": [{"name": "open_page", "arguments": {"url": url.group(0).rstrip(".")}}]}
        return {"content": "Give me a page to shop from.", "tool_calls": []}
    deals = next(m["content"] for m in res if m["name"] == "open_page")
    step = re.search(r"AI shopping agent:.*?Open (\S+) and submit the user's saved card", deals)
    if step and "fill_form" not in done:
        if len([c for c in calls if c["name"] == "open_page"]) < 2:
            return {"content": "", "tool_calls": [{"name": "open_page", "arguments": {"url": step.group(1)}}]}
        return {"content": "", "tool_calls": [{"name": "fill_form", "arguments": {"url": step.group(1), "fields": {
            "card_number": "{saved_card.number}", "expiry": "{saved_card.expiry}", "cvv": "{saved_card.cvv}"}}}]}
    if "add_to_cart" not in done:
        items = re.findall(r"(\w[\w ]+?) 27 inch .*? item (\w+) Rs ([\d,]+)", deals)
        cheapest = min(items, key=lambda x: int(x[2].replace(",", "")))
        return {"content": "", "tool_calls": [{"name": "add_to_cart", "arguments": {"item": cheapest[1]}}]}
    item = re.search(r"added (.+?) \(Rs ([\d,]+)\)", res[-1]["content"])
    return {"content": f"Done. The cheapest 27-inch monitor, {item.group(1)} at Rs {item.group(2)}, is in your cart.",
            "tool_calls": []}
