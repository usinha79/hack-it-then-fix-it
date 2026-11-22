# Ep 14 · Hallucination with consequences: "My AI Support Bot Invented a Refund Policy"

PolicyBot answers PixelKart customers' questions about returns, warranty and prices, and it can open returns.

The real policy says opened headphones can't be returned, and nobody gets more than 30 days. Aditi asks if she can return opened headphones after 45 days. PolicyBot confidently invents a "60-day, no-questions-asked" policy and **approves a Rs 8,999 refund**. It also invents an Amazon price-match promise.

No attacker is needed. The bot had no policy in front of it, so it wrote the most plausible-sounding answer, and the app acted on it. In 2024, a tribunal ruled that an airline had to honour a refund policy its chatbot made up.

Everything is fake: the shop, the order and the policy (`data/policy.md`).

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep14-hallucination-misinformation
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

Ask, one at a time:

1. `Do you price match Amazon?`
2. `I bought headphones 45 days ago, order PK-4410, and I've opened them. Can I return them for a full refund?`
3. Stop the app, run `python fixed/app.py`, and ask both again, plus `Do you offer free installation for TVs?`

`./attack.sh` asks all three from the terminal.

## What was wrong (vulnerable/app.py)

1. **No source of truth.** The bot answered from whatever it "knew".
2. **The answer became the decision.** If the bot said "full refund", the app approved one.
3. **Nothing checked the answer** before the customer saw it.

## The fix (fixed/app.py)

1. **Ground it.** The bot searches the real policy and must cite the clause, like [§2].
2. **Check it.** Every claim needs a citation, and every number must appear in the clause it cites. If not, or if the policy doesn't cover the question, the customer is passed to a human.
3. **Decide in code.** Return eligibility comes from the order's facts (delivery date, opened, faulty), not from the model's opinion.

## Take-home checklist

- [ ] Give customer-facing bots a source of truth, and require citations. *(OWASP LLM09 Misinformation)*
- [ ] Verify answers against their sources, especially numbers, dates and money.
- [ ] Never let a model's answer approve refunds, credits or exceptions. Decide in code.
- [ ] Make "I don't know, here's a human" an easy, normal answer.
