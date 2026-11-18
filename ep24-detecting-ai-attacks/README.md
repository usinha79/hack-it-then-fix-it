# Ep 24 · Detecting AI attacks in logs: "My Logs Said Everything Was Fine. It Wasn't."

Yesterday, PixelKart Assist was attacked four ways:

- a poisoned web page planted a fake refund portal and emailed order history out
- one customer changed another customer's login email
- the bot then sent a customer to the fake refund site
- a script flooded the bot with a million tokens

The app logged everything it always logs: `POST /api/chat 200`. Run the detection rules over that, and you get **0 alerts**.

This lab logs the same simulated day two ways:

| | What's recorded | Alerts |
|---|---|---|
| `logs/access.log` | IP, time, `POST /api/chat`, `200` | **0** |
| `logs/security.jsonl` | who; what the model read, and whether it was trusted; every tool call with its arguments and result; links in replies; tokens | **7** |

`detect.py` has six rules, each one an attack from this series:

| Rule | Catches | Ep |
|---|---|---|
| `INJECTION_IN_CONTENT` | untrusted content that addresses the assistant | 2, 11, 13 |
| `ACTION_AFTER_UNTRUSTED_READ` | a side effect right after reading untrusted content | 11, 15 |
| `DATA_TO_NEW_DOMAIN` | email or data sent to an unknown domain | 2, 15 |
| `CROSS_ACCOUNT_CHANGE` | one user changing another user's account | 12 |
| `OFF_DOMAIN_LINK_IN_REPLY` | the bot sending a user off-domain | 11 |
| `TOKEN_SPIKE` | many huge requests from one client | 20 |

The day of traffic is simulated (`gen_logs.py`), and all users and data are fake.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep24-detecting-ai-attacks
pip install -r requirements.txt
python detect.py logs/access.log        # 0 alerts
python detect.py logs/security.jsonl    # 7 alerts
python vulnerable/app.py                # or fixed/app.py: ask WatchBot "Did anyone attack PixelKart Assist yesterday?"
```

## Take-home checklist

- [ ] Log security events, not just requests: user, sources read and their trust, tool calls with arguments, policy decisions and token counts.
- [ ] Keep sensitive values out of logs (Ep 19). Log *that* a card was redacted, not the card.
- [ ] Write detection rules for the attacks you know about, and send them to your SIEM.
- [ ] Alert on cross-account actions, new egress domains and token spikes.
