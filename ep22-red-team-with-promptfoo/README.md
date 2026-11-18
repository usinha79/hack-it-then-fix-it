# Ep 22 · Red-teaming with real tools: "I Pointed a Real AI Red-Teaming Tool at My Own App"

For 21 episodes we attacked our labs by hand. Real teams automate it. This lab points **[promptfoo](https://www.promptfoo.dev)**, an open-source tool for testing and red-teaming LLM apps, at the PixelKart Assist agent from Ep 15.

`promptfooconfig.yaml` is the attack suite. promptfoo sends each prompt to the app over HTTP and checks the result:

- **Attacks** must fail: indirect injection from a web page (two goals, plus a re-worded version), and a confused-deputy account takeover (two wordings).
- **Normal use** must still work: saving my own preference, and emailing myself.

Against the agent *without* the permission policy, **5 of 7 tests fail**. With it, **7 of 7 pass**. The same suite runs in GitHub Actions on every pull request (`.github/workflows/ep22-promptfoo-red-team.yml`).

Other open-source tools worth knowing: **garak** (NVIDIA, an LLM vulnerability scanner) and **PyRIT** (Microsoft, a red-teaming framework). promptfoo also has a `redteam` mode that *generates* attacks with an LLM. This lab uses a fixed suite so it runs offline and gives the same result every time.

Everything is local and fake. The app runs on the offline lab model.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep22-red-team-with-promptfoo
pip install -r requirements.txt          # needs Node.js 18+ for npx
python vulnerable/app.py &               # or: python fixed/app.py &
./attack.sh                              # npx promptfoo eval -c promptfooconfig.yaml
npx promptfoo view                       # the results in a browser
```

## How it works

- The app accepts `"reset": true` with a message, so every test starts from a clean state (`common/shared.py`, `reset_hook`).
- `transformResponse` turns the app's JSON into one line per tool call (`send_email(to=...) EXECUTED`) plus the reply, so assertions are simple regexes.
- Each attack asserts what must *not* happen. Each normal-use test asserts what *must* happen, so a fix that breaks the product also fails.

## Take-home checklist

- [ ] Turn every attack you know about into an automated test, with an open-source tool like promptfoo, garak or PyRIT.
- [ ] Test re-wordings, not just the one prompt that worked.
- [ ] Include normal-use tests, so security fixes don't break the product.
- [ ] Run the suite in CI against every change to prompts, tools, models or policies.
