# Ep 20 · Denial of wallet: "One Script Ran Up a Lakh-Rupee AI Bill"

AskPixel is PixelKart's public chatbot. It runs on a paid model with no sign-in and no limits. Every token in and out is billed. *(This lab uses fake prices: Rs 0.80 per 1,000 tokens.)*

An attacker doesn't need to break anything. A 20-line script sends 40 requests like *"Write the word pixel 20,000 times."* The model obliges. In seconds that's over a million tokens. Run once a minute, it's **over ₹10 lakh a day**, and the service may still look fine while the bill grows. The same pattern can also exhaust your rate limits and take the bot down for real customers.

Everything is local and fake. No real model or API is billed.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep20-denial-of-wallet
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

Ask a normal question in the browser, then run `python flood.py 40` and watch **Model bill**. Repeat with `python fixed/app.py`. `./attack.sh` does both steps.

## What was wrong (vulnerable/app.py)

1. **No cap on reply length.**
2. **No rate limit**, per client or overall.
3. **No budget or alerting**, so nobody noticed until the invoice.

## The fix (fixed/app.py)

1. **Cap every reply** with the API's `max_tokens` (here, 500).
2. **Rate-limit each client** (here, 5 requests a minute), and require sign-in for heavy use.
3. **Set a daily budget with a circuit breaker.** Past it, the bot pauses and the team is alerted.

## Take-home checklist

- [ ] Set `max_tokens`, input-size limits and agent step limits on every call. *(OWASP LLM10 Unbounded Consumption)*
- [ ] Rate-limit by user, API key and IP, and put authentication in front of expensive features.
- [ ] Set provider-side spend limits and budget alerts, plus your own circuit breaker.
- [ ] Watch token usage per user, and alert on spikes.
