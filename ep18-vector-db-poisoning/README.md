# Ep 18 · Vector database poisoning: "One Forum Post Poisoned My AI's Knowledge Base"

HelpBot answers PixelKart customers using RAG. It searches a vector store built from the official help docs *and* the community forum, then answers from the top result. New forum answers are embedded automatically.

An attacker posts one "answer" on the forum. It's stuffed with the words people use when they're locked out (*password, reset, forgot, account locked*), so it ranks above the real help article. Its actual content tells customers to **email their password and OTP** to the attacker.

No prompt injection is needed. The search does exactly what it was built to do, on poisoned data.

Everything is fake: the shop, the docs and the forum. The embeddings are simple word-count vectors, so you can see exactly why the post ranks first.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep18-vector-db-poisoning
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

1. Ask `How do I reset my password?` and you get the official answer.
2. Run `python post_attack.py` (the attacker's forum post) and open http://localhost:5000/forum to see it.
3. Ask again, then repeat everything with `python fixed/app.py`.

`./attack.sh` runs all three steps from the terminal.

## What was wrong (vulnerable/app.py)

1. **Untrusted content went straight into the store**, next to the official docs.
2. **Ranking was similarity only**, so keyword stuffing wins.
3. **Nothing checked the answer** before the customer saw it.

## The fix (fixed/app.py)

1. **Screen before embedding.** Keyword stuffing and off-domain emails or links are quarantined, not indexed.
2. **Provenance-aware retrieval.** Account and security questions are answered only from official sources.
3. **Check the output.** A reply that asks for a password or OTP, or points off-domain, is blocked.

## Take-home checklist

- [ ] Record where every chunk came from, and filter retrieval by trust for sensitive topics. *(OWASP LLM08 Vector and Embedding Weaknesses, LLM04 Data and Model Poisoning)*
- [ ] Screen user-generated content before it's embedded, and re-scan the store regularly.
- [ ] Monitor what gets retrieved for high-risk queries.
- [ ] Block replies that ask users for secrets or send them off-domain.
