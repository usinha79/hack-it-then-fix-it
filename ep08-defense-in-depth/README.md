# Ep 8 · Defence in depth: "Defending AI Agents: Guardrails, Least Privilege and Attack Tests in CI"

PixelKart Assist combines this week's tools (discounts, web pages, email, help docs) with this week's fixes, layer by layer: secrets out of the prompt, policy checks in every tool, untrusted-content tainting, path confinement and an output check. The model is still trivially trickable (see `common/mock_model.py`). The app holds anyway.

Then the real-world twist: fixes rot. `vulnerable/` is the same app after a "harmless" refactor deleted one line, the discount limit check. Code review missed it. The **attack regression tests** in `tests/test_attacks.py` catch it.

## Run it

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep08-defense-in-depth
pip install -r requirements.txt
python fixed/app.py            # http://localhost:5000
./attack.sh                    # this week's attacks against the running app
```

## Run the attack tests

```bash
APP=fixed python -m pytest -v tests        # 5 passed
APP=vulnerable python -m pytest -v tests   # 1 failed: the 100% discount works again
```

The repo's GitHub Actions workflow (`.github/workflows/ep08-attack-tests.yml`) runs the suite on every push and pull request, so a red test blocks the merge.

## The layers

1. **The model is not a security boundary.** Assume it will be tricked.
2. **Policy in code, per tool.** Limits, recipients, paths, destinations.
3. **Untrusted content taints the turn.** After reading a web page, side effects need approval.
4. **Least data and least privilege.** No secrets in prompts or within tool reach.
5. **Check the output** before it reaches users or other systems.
6. **Test the attacks.** Every attack you've seen becomes a regression test in CI.

## Take-home checklist

- [ ] Write one test per attack you know about, asserting the attack fails.
- [ ] Also test that normal use still works, so a fix can't break the product.
- [ ] Run the suite in CI on every pull request, and block merges on red.
- [ ] Use the offline lab model (or a pinned model) in CI so results are repeatable.
