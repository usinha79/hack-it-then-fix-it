"""A tiny threat-model checker for AI apps. It reads a design (apps/*.yaml), works out which of the
OWASP Top 10 for LLM Applications (2025) apply, and checks the controls for each one.

    python threatmodel.py apps/pixelkart-assist.yaml          # exit code 1 if any risk is uncovered
"""
import sys

import yaml

RISKS = [
    ("LLM01", "Prompt Injection", "Ep 1, 2, 9, 10, 13",
     lambda a: any(i["trust"] == "untrusted" for i in a["inputs"]),
     lambda c: c["untrusted_content_labelled"] and c["side_effects_need_approval"]),
    ("LLM02", "Sensitive Information Disclosure", "Ep 3, 19",
     lambda a: bool(a.get("data")),
     lambda c: c["pii_redaction"] and c["log_retention_days"] <= 30),
    ("LLM03", "Supply Chain", "Ep 16, 17",
     lambda a: bool(a.get("supply_chain")),
     lambda c: c["model_hash_pinning"] and c["dependency_lockfile"]),
    ("LLM04", "Data and Model Poisoning", "Ep 11, 18",
     lambda a: any(i["trust"] in ("untrusted", "derived") and ("RAG" in i["name"] or "memory" in i["name"]) for i in a["inputs"]),
     lambda c: c["ingestion_screening"] and c["memory_writes_need_user"]),
    ("LLM05", "Improper Output Handling", "Ep 7",
     lambda a: bool(a.get("outputs")),
     lambda c: c["output_encoding"] and c["parameterised_queries"]),
    ("LLM06", "Excessive Agency", "Ep 3, 5, 12, 15",
     lambda a: any(t["risk"] in ("money", "external", "account", "write") for t in a["tools"]),
     lambda c: c["permission_policy"] and c["identity_from_session"]),
    ("LLM07", "System Prompt Leakage", "Ep 1",
     lambda a: True,
     lambda c: not c["secrets_in_system_prompt"]),
    ("LLM08", "Vector and Embedding Weaknesses", "Ep 4, 18",
     lambda a: any("RAG" in i["name"] for i in a["inputs"]),
     lambda c: c["retrieval_trust_filter"] and c["tenant_isolation"]),
    ("LLM09", "Misinformation", "Ep 14",
     lambda a: a["exposure"] == "public",
     lambda c: c["grounded_citations"] and c["decisions_in_code"]),
    ("LLM10", "Unbounded Consumption", "Ep 20",
     lambda a: a["exposure"] == "public",
     lambda c: bool(c["max_tokens"] and c["rate_limit"] and c["budget_cap"])),
]


def check(path):
    a = yaml.safe_load(open(path))
    out = []
    for rid, name, eps, applies, covered in RISKS:
        if applies(a):
            out.append((rid, name, eps, "covered" if covered(a["controls"]) else "GAP"))
    return a["app"], out


if __name__ == "__main__":
    app, findings = check(sys.argv[1])
    print(f"Threat model: {app}  ({sys.argv[1]})")
    for rid, name, eps, st in findings:
        print(f"  {st:<8} {rid}  {name:<34} see {eps}")
    gaps = sum(st == "GAP" for *_, st in findings)
    print(f"{len(findings)} risks apply · {len(findings) - gaps} covered · {gaps} gaps")
    sys.exit(1 if gaps else 0)
