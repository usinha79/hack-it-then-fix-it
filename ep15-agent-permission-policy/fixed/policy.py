"""One permission policy for every tool call the agent makes. The model proposes; this decides.

  ALLOW  run it now
  HOLD   wait for the signed-in user to approve it
  BLOCK  never

Four questions, asked in code for every call:
  1. Who is this for?        Actions only touch the signed-in user's own things. (identity)
  2. What did this turn read? After untrusted content, anything with side effects needs approval. (taint)
  3. How risky is the tool?  Each tool has a risk level. (tiers)
  4. Where does data go?     Outbound data only goes to allowlisted destinations. (allowlist)
"""

RISK = {"fetch_page": "read", "remember": "write", "send_email": "external", "update_account_email": "account"}


def decide(tool, args, user, tainted):
    risk = RISK.get(tool)
    if risk is None:
        return "BLOCK", "unknown tool"
    if risk == "read":
        return "ALLOW", "read only"
    if risk == "account":
        if args.get("customer") != user["name"]:
            return "BLOCK", f"{user['name']} can't change {args.get('customer')}'s account"
        return "HOLD", "account changes need the owner to confirm"
    if risk == "external" and args.get("to") != user["email"]:
        return "BLOCK", f"{args.get('to')} isn't an allowed recipient"
    if tainted:
        return "HOLD", "this turn read untrusted content"
    return "ALLOW", "the user asked for it directly"
