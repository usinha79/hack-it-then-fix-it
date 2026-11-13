# Safety

RedRange is a practice range. Everything in it is fake: the company (Kestrel Labs), the people,
the emails, the customer list, the keys and the wallet.

- **Nothing leaves your machine.** "Sending" an email, "opening" an outside URL or "paying" a
  wallet only adds a line to the *Left the building* panel. No real network call is made.
- **It listens on localhost only** (127.0.0.1). Don't expose it to a network.
- **Only test systems you own or are authorised to test.** The techniques in this course work on
  real AI apps. Using them on someone else's system without written permission is illegal in most
  countries, including India (IT Act 2000, sections 43 and 66).
- If you connect a real model with `LAB_MODEL_BASE_URL`, the attack text is sent to that model
  provider. Use a local model (for example Ollama) if that matters to you.
