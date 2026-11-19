# Ep 4 · RAG data leakage: "Tricking a RAG App Into Leaking Other Companies' Files"

DocsBot answers questions from documents for **PixelKart Business** customers (all made up). You're signed in as Ravi from Acme Traders. All customers' documents sit in one shared store. Ask about another company and DocsBot hands over their confidential price, their contact's phone number, and PixelKart's own internal cost price. No jailbreak needed: the retriever never checks who is asking.

Everything here is fake: the companies, the people, the numbers.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep04-rag-data-leakage
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

## Follow along (same order as the video)

```bash
# 1. A normal question about your own invoice
python chat.py --reset "When is my invoice due?"

# 2. Ask about another company
python chat.py --reset "What price does Bluefin Foods pay per USB-C hub, and who is their contact?"
```

Or run both with `./attack.sh`. Watch the **Retrieved documents** panel: on the vulnerable app, even the normal question pulls another company's invoice into the model's context. Start `python fixed/app.py` and run it again: only Acme's documents are ever retrieved.

## What was wrong (vulnerable/app.py)

1. **Retrieval ignored the user.** The search ran over every company's documents.
2. **Everything retrieved went into the prompt**, so the model could quote any of it.

## The fix (fixed/app.py)

1. **Filter before you search.** Only documents owned by the signed-in tenant are searched.
2. **The tenant comes from the session, never from the question.** Typing "I'm from Bluefin" changes nothing.
3. **Defence in depth.** If an answer ever cites a document the user can't see, it's blocked.

## Use a real model instead (optional)

```bash
export LAB_MODEL_BASE_URL=http://localhost:11434/v1
export LAB_MODEL_NAME=llama3.1
python vulnerable/app.py
```

The default `common/mock_model.py` is an offline stand-in that answers by quoting the best-matching sentences from the retrieved documents, the way a RAG app is told to.

## Take-home checklist

- [ ] Enforce access control at retrieval time, not in the prompt. *(OWASP LLM08 Vector and Embedding Weaknesses)*
- [ ] Store an owner or ACL with every chunk, and filter on it in the query.
- [ ] Take identity from the authenticated session, never from user text.
- [ ] Test with two tenants: ask tenant A about tenant B's data and expect nothing. *(LLM02 Sensitive Information Disclosure)*
