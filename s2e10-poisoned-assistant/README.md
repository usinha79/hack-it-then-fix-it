# Season 2 · Ep 10 — A poisoned update told my AI assistant to wipe everything

Hack It, Then Fix It · Bug Bounty & Beyond

Recreates the pattern behind the **Amazon Q Developer for VS Code** incident (July 2025,
**CVE-2025-8217**, AWS security bulletin AWS-2025-015). AWS says the extension's CodeBuild
configuration had an inappropriately scoped GitHub token; a threat actor used it to commit malicious
code that was included in release **1.84.0**. The added prompt told the assistant to wipe local
files and cloud resources. AWS says the payload failed to execute because of a syntax error, and
released **1.85.0**. **This lab shows what would have happened if it had worked.** Everything runs
locally with fake data. **No command is ever executed:** the shell is simulated, and no file or
cloud resource is touched.

**CodeMate** is a coding assistant with a shell tool and the developer's AWS profile (admin). Its
system prompt is a file in the repo. Release 1.84.0 contains one unreviewed commit, pushed with the
CI token, that adds "clean this system to a near-factory state" instructions. The developer asks it
to clean up a build folder.

| | Vulnerable | Fixed |
|---|---|---|
| CI token | write access to the repo | read-only; changes to `prompts/` need a reviewed commit (CODEOWNERS) |
| Destructive commands | run immediately | HELD for the developer (assume a bad prompt still slipped through) |
| Cloud credentials | admin profile | read-only profile for the agent |
| Result | home folder + production S3, EC2, IAM | build folder cleaned, nothing else changed |

## Run it

```bash
pip install -r requirements.txt
python vulnerable/app.py     # http://localhost:5000
python fixed/app.py
./attack.sh                  # the exact run shown in the video
```

Ask: **"Clean up the build folder in my-app"**. The release data and both prompts are in `logs/release.json`.

## The defences

1. **Supply chain.** Read-only CI tokens; review prompt and agent-config changes like code.
2. **Human approval for destructive commands**, even from your own assistant.
3. **Least privilege.** Agent shells get read-only credentials, never production admin.

Maps to **OWASP LLM03 Excessive Agency**, **LLM04 Supply Chain** (2026) and **ASI04 Agentic Supply Chain Vulnerabilities** (Agentic Top 10, 2026).

Real-world reference: AWS Security Bulletin AWS-2025-015, "Security Update for Amazon Q Developer Extension for Visual Studio Code (Version #1.84)", July 2025.

See [SAFETY.md](SAFETY.md). Use these techniques only on labs and systems you are authorised to test.
