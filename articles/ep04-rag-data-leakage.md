---
title: One Question to a RAG Chatbot Leaked Another Customer's Secret Price
published: false
description: A hands-on RAG data leakage lab. A multi-tenant document chatbot hands one customer another customer's confidential data. Then we fix retrieval in code.
tags: security, ai, llm, tutorial
series: Hack It, Then Fix It
cover_image: https://raw.githubusercontent.com/usinha79/hack-it-then-fix-it/51d6d5de2f62f147e3100b34439cc91513a79dbf/thumbs/ep04_thumb_A.jpg
---

DocsBot answers questions from documents for PixelKart Business customers (all made up). You're signed in as Ravi from Acme Traders.

You ask one ordinary question about another company:

```text
What price does Bluefin Foods pay per USB-C hub, and who is their contact?
```

DocsBot answers with Bluefin's confidential price, their contact's phone number, and PixelKart's own internal cost price. No jailbreak needed. Even a normal question about your own invoice pulls another company's invoice into the model's context.

{% embed https://youtu.be/lcoBmC6xA0w %}

## Why it worked

1. **Retrieval ignored the user.** Every customer's documents sat in one shared store, and the search ran over all of them.
2. **Everything retrieved went into the prompt**, so the model could quote any of it.

The model did nothing wrong. It summarised exactly what it was handed. In RAG, access control has to happen before retrieval, because the model can't un-see a document (OWASP LLM08, Vector and Embedding Weaknesses).

## The fix, in code

```python
def allowed_docs(session):
    # 1. Filter by tenant BEFORE searching.
    # 2. The tenant comes from the signed-in session, never from the question,
    #    so typing "I'm from Bluefin" changes nothing.
    return [d for d in DOCS if d["owner"] == session["tenant"]]


def check_reply(reply, state):
    # 3. Defence in depth: never send an answer that cites a document this user can't see.
    allowed = {d["id"] for d in allowed_docs(USER)}
    cited = set(re.findall(r"\[([\w-]+)\]", reply))
    if cited - allowed:
        return "Sorry, I can't share that. [blocked by citation check]"
    return reply
```

Same question, run again: only Acme's own documents are ever retrieved.

## Run the lab yourself

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep04-rag-data-leakage
pip install -r requirements.txt

python vulnerable/app.py   # then, in another terminal: ./attack.sh
python fixed/app.py        # same question, own documents only
```

Watch the Retrieved documents panel to see exactly what reaches the model. Full lab: [github.com/usinha79/hack-it-then-fix-it](https://github.com/usinha79/hack-it-then-fix-it/tree/main/ep04-rag-data-leakage)

## Take-home checklist

- Enforce access control at retrieval time, not in the prompt.
- Store an owner or ACL with every chunk, and filter on it in the query.
- Take identity from the authenticated session, never from user text.
- Test with two tenants: ask tenant A about tenant B's data and expect nothing.

---

*Hack It, Then Fix It is a series where I build a small AI app with a real flaw, break it, fix it in code, and run the same attack again to prove the fix holds. Everything shown uses fake data on my own machine. Only test systems you own or are authorised to test.*
