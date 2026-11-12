# Episode 26: Incident response for an AI app

Hack It, Then Fix It · Bug Bounty & Beyond · Module 4

Yesterday a forum page planted a fake refund link in PixelKart Assist's memory (the Ep 13 attack). All day, every
customer who asked about refunds was sent to `pixelkart-refunds.example` and told to enter card details.
Today you're on call. Three questions decide how bad this gets: **can you stop it, who was hit, and can you clean it up?**

| | Vulnerable Assist | Fixed Assist |
|---|---|---|
| Stop it | No kill switch. Only option: take the whole site down | `kill_switch`: memory and agent actions off, FAQ answers only |
| Who was hit | No audit log. Nobody knows | `logs/audit.jsonl`: each reply records links and memory used → **13 customers** |
| Clean up | Memory has no sources. Delete everything, or guess | Each memory entry records its source → purge only `deals-forum.example` |
| Tell people | Email every customer, or no one | Notice to the 13, with what to do |

## Run it

```bash
pip install -r requirements.txt
./attack.sh                 # the audit-log search and the purge from the video
python vulnerable/app.py    # http://localhost:5000
python fixed/app.py
```

In the chat, ask **"How do I get a refund?"**, then report the incident:
**"Incident: you're sending customers a fake refund link. Run the playbook."**, then ask about refunds again.

`python gen_logs.py` rebuilds `logs/` (same result every run). The model is an offline mock (`common/mock_model.py`).
The incident tools are plain code in `ir.py`: the model calls them but can't change what they find.

## The lesson

Build the off switch, the record and the provenance before the incident, not during it. A kill switch that keeps a
safe FAQ running, an audit log of what the AI said and which memory it used, and a source on every memory entry turn
a day of guessing into four commands.
