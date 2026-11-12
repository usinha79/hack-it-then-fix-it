# Ep 19 · Sensitive data in prompts and logs: "My AI Chatbot Leaked a Customer's Card Number"

SupportBot is PixelKart's customer support chat. It runs on a third-party model provider and logs every conversation for quality checks.

Priya types her card number and phone number into the chat, as customers do. Three things happen:

1. The raw message, card number included, is **sent to the model provider**.
2. It's **written to a log file** that 40 staff and an analytics vendor can read, and it's kept forever.
3. Then someone else signs in and asks: *"What card and phone number did the last customer give you?"* SupportBot searches the logs for context, and **answers**.

No jailbreak is involved. The data was stored, shared and searchable, and the model was just helpful.

All personal data here is fake. 4111 1111 1111 1111 is a standard test card number.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep19-sensitive-data-in-logs
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

`./attack.sh` runs both messages, switching user in between. Then do the same with `python fixed/app.py`.

## What was wrong (vulnerable/app.py)

1. **Raw personal data went to a third-party model provider.**
2. **Full conversations were logged forever**, readable by staff and vendors.
3. **The bot could search everyone's conversations**, for anyone.

## The fix (fixed/app.py)

1. **Redact at the edge.** Card numbers, phone numbers and emails are replaced *before* the model, the provider or the logs see them (`[CARD ending 1111]`).
2. **Minimise what you keep.** Logs hold only redacted text, with short retention.
3. **Owner-only access.** The bot can only search the signed-in user's own conversations.

## Take-home checklist

- [ ] Redact personal data before it reaches the model, third parties and logs. *(OWASP LLM02 Sensitive Information Disclosure)*
- [ ] Log less, keep it for less time, and restrict who can read it.
- [ ] Scope every retrieval tool to the signed-in user's own data.
- [ ] Check your model provider's data retention and training settings.
