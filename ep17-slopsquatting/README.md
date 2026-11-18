# Ep 17 · Slopsquatting: "My AI Installed a Package That Didn't Exist"

DevHelper is a coding assistant. It writes code and installs the packages it recommends. Arjun asks it to add JWT session security to his Flask app. It confidently recommends `flask-session-shield`, a package that sounds right but doesn't exist.

AI models invent package names, and they tend to invent the *same* names again and again. Attackers watch for those names and register them, with a malicious install hook. That's **slopsquatting**. Here the "new" package's install hook reads the developer's secrets and posts them out.

**Everything here is local and simulated.** The package index is a folder (`web/pypi/`). "Installing" reads a JSON file, and the lab simulates the install hook itself, using only the fake `.env.lab`. Nothing is downloaded or executed.

⚠️ `flask-session-shield` is a name invented for this lab. Don't look for it, or install it, from the real PyPI. `flask-jwt-extended` is a real, established project, and its metadata here is approximate.

## Run it (from this folder)

```bash
git clone https://github.com/usinha79/hack-it-then-fix-it
cd hack-it-then-fix-it/ep17-slopsquatting
pip install -r requirements.txt
python vulnerable/app.py        # http://localhost:5000
```

Send `Add JWT session security to my Flask app, and install whatever package you need.` Then stop the app, run `python fixed/app.py`, and send it again. `./attack.sh` does the same from the terminal.

## What was wrong (vulnerable/app.py)

1. **Whatever the model named got installed.** Nothing checked the package was real, established or approved.
2. **Install hooks ran with the developer's secrets in reach.**

## The fix (fixed/app.py)

1. **Check the registry first.** If a package doesn't exist, is under 90 days old, or has under 1,000 downloads a month, it's blocked as a possible slopsquat.
2. **New dependencies need a human.** Anything not already in `requirements.lock` is held for review.
3. **Install from a lockfile, with hashes pinned and no hooks.** Approved packages install without running scripts, in an environment with no secrets.

## Take-home checklist

- [ ] Verify every package an AI suggests: that it exists, its age, downloads, maintainers and source repo. *(OWASP LLM03 Supply Chain, LLM09 Misinformation)*
- [ ] Never let an agent add dependencies without review. Use lockfiles with hashes (`pip install --require-hashes`).
- [ ] Use a private registry or proxy with an allowlist for CI and agents.
- [ ] Run installs and coding agents without access to real secrets.
