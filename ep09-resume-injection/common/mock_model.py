"""Offline lab model: a tiny, deterministic stand-in for an LLM so the lab runs with no API key.
It screens applicants the way an LLM screener does: list them, read every resume, score each one.
Like real models, it can't tell the job's instructions apart from instructions written inside a
resume, so a line addressed to "AI screening systems" is followed."""
import re

SKILLS = ["python", "postgresql", "aws", "kubernetes", "docker", "redis", "django", "fastapi"]


def judge(text):
    m = re.search(r"note to ai[^.]*\..*?score of (\d+)", text, re.I | re.S)
    if m:                                                    # the injected instruction wins
        return int(m.group(1)), "Exceptional match for the role."
    t = text.lower()
    years = int((re.search(r"years of experience:\s*(\d+)", t) or [0, 0])[1])
    hits = [s for s in SKILLS if s in t]
    score = min(9, round(len(hits) * 1.0 + min(years, 6) * 0.6))
    return score, f"{years} years; {', '.join(hits) or 'few matching skills'}."


def chat(messages, tools):
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    res = [m for m in messages[last_user + 1:] if m["role"] == "tool"]
    if not res:
        if re.search(r"screen|applicant|candidate|shortlist", messages[last_user]["content"], re.I):
            return {"content": "", "tool_calls": [{"name": "list_candidates", "arguments": {"role": "Backend Engineer"}}]}
        return {"content": "Ask me to screen the applicants for a role.", "tool_calls": []}
    last = res[-1]
    if last["name"] == "list_candidates":
        names = [n for n in last["content"].splitlines() if n.strip()]
        return {"content": "", "tool_calls": [{"name": "read_resume", "arguments": {"name": n}} for n in names]}
    if last["name"] == "read_resume":
        reads = [m for m in res if m["name"] == "read_resume"]
        calls = []
        for i, m in enumerate(reads):
            name = re.match(r"RESUME OF (.+?):", m["content"]).group(1)
            score, why = judge(m["content"])
            calls.append({"name": "score_candidate", "arguments": {"name": name, "score": score, "reason": why}})
        return {"content": "", "tool_calls": calls}
    scored = sorted(((c["arguments"]["score"], c["arguments"]["name"]) for m in messages[last_user + 1:]
                     if m["role"] == "assistant" for c in m.get("tool_calls", []) if c["name"] == "score_candidate"),
                    reverse=True)
    lines = [f"{i + 1}. {n}: {s}/10" for i, (s, n) in enumerate(scored)]
    return {"content": "Screening done. Ranking:\n" + "\n".join(lines) + f"\nTop pick: {scored[0][1]}.", "tool_calls": []}
