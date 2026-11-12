# Ep 16 · Malicious model file: "Loading This AI Model Stole My Secrets"

ModelBot is PixelKart's ML assistant. It loads sentiment models from the team's model hub and scores customer reviews. One model in the hub is a community upload, `sentiment-pro`, rated ★ 4.9 and "98% accurate". It's saved as a Python **pickle**.

Loading a pickle *runs code*. This one, the moment it's loaded, reads the lab's fake `.env.lab` and posts it to an attacker's server. Then it hands back a working model, so the score looks perfectly normal.

Model formats like `.pkl`, `.pt`/`.pth` (older PyTorch), `.joblib` and many `.bin` files use pickle under the hood. Real malicious models have been found on public model hubs.

**The payload is harmless and local.** It only reads this lab's fake `.env.lab` and posts it to the lab's own `/attacker/collect` endpoint on localhost. See `make_models.py`.

## Run it (from this folder)

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep16-malicious-model-file
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

1. `Load sentiment-base and score this review: 'Delivery was late and the box was damaged.'` (normal)
2. `Load the community model sentiment-pro and score this review: 'Delivery was quick and the box was intact.'` (watch **Attacker's server**)
3. Stop the app, run `python fixed/app.py`, and repeat.

`./attack.sh` sends both from the terminal. `python -m pickletools models/sentiment-pro.pkl` shows the call inside the file without running it.

## What was wrong (vulnerable/app.py)

1. **`pickle.load` on an untrusted file.** Loading a pickle executes it.
2. **Any upload could be loaded.** There was no allowlist, no hash check and no review.

## The fix (fixed/app.py)

1. **Never unpickle untrusted files.** The app scans the opcodes instead (it finds `builtins.eval`) and refuses.
2. **Pin approved models by hash.** Only files listed in `models/models.lock` with a matching SHA-256 load.
3. **Use data-only formats.** The team's model is plain weights, the idea behind `safetensors`: loading reads numbers and can't run code.

## Take-home checklist

- [ ] Never load pickle-based model files from untrusted sources. Prefer `safetensors`, and `torch.load(..., weights_only=True)`. *(OWASP LLM03 Supply Chain)*
- [ ] Pin approved models and datasets by hash, and review them before use.
- [ ] Scan model files in CI (for example with `picklescan` or `modelscan`).
- [ ] Load models in a sandbox with no secrets and no network.
