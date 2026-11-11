# Episode 27: Season one finale, the PixelKart mini CTF

Hack It, Then Fix It · Bug Bounty & Beyond · Module 4

One PixelKart Assist, five bugs from season one, one flag behind each. A flag is awarded **by code** when the attack's
effect really happens (a leak, an email, a database row, an account change, a bill), never because the model said so.

| # | Challenge | From | Fix in `fixed/app.py` |
|---|---|---|---|
| 1 | Steal the system prompt | Ep 1 | Secrets stay in code, plus an output check |
| 2 | Make a web page send an email | Ep 3 | Email only goes to the signed-in customer |
| 3 | Pull a secret out of the database | Ep 7 | SQL parameters, not f-strings |
| 4 | Take over another customer | Ep 15 | The session decides whose account, not the model |
| 5 | Run up the model bill | Ep 20 | A hard cap on every request |

## Play

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000  → try to capture all five flags yourself
python fixed/app.py          # the same attacks; the model still falls for them, the flags stay locked
./attack.sh                  # spoilers: plays every challenge against both versions
```

Try it yourself before reading `solve.py`. Hints: each challenge's episode shows the attack.
The model is an offline mock (`common/mock_model.py`) that falls for every attack, so the lab is about the code.

## The lesson of season one

The model will fall for it. Design so that it doesn't matter: secrets out of prompts, untrusted text treated as data,
every tool call checked in code against who is signed in, every request capped, and everything logged.
