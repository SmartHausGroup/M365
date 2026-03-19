#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

import yaml

HEADER = """# Generated from registry/agents.yaml. Do not edit manually.
package agents.{agent_key}

default allow_actions = {{}}
default approval_required = {{}}
"""


def sanitize_key(k: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", k)


def parse_condition(expr: str) -> str:
    # Very naive parser: supports 'field op value' joined by && equivalents
    # Converts to: input.data.field <op> <value>
    expr = expr.strip()
    # Allow and/or via '&&'/'and' and '||'/'or'
    expr = expr.replace(" and ", " && ").replace(" or ", " || ")
    tokens = re.split(r"(\|\||&&)", expr)
    parts = []
    for tok in tokens:
        t = tok.strip()
        if not t:
            continue
        if t in ("&&", "||"):
            parts.append(t)
            continue
        m = re.match(r"^([a-zA-Z0-9_\.]+)\s*(==|!=|>=|<=|>|<)\s*(.+)$", t)
        if not m:
            # Fallback: include raw
            parts.append(t)
            continue
        field, op, value = m.groups()
        # Coerce booleans and numbers
        value = value.strip()
        if value.lower() in ("true", "false"):
            pass
        elif re.match(r"^\d+(\.\d+)?$", value):
            pass
        else:
            # quote string
            if not (value.startswith('"') and value.endswith('"')):
                cleaned_value = value.strip("\"'")
                value = f'"{cleaned_value}"'
        # Map field -> input.data.<field>
        field_path = ".".join([p for p in field.split(".") if p])
        if not field_path.startswith("input."):
            field_path = f"input.data.{field_path}"
        parts.append(f"{field_path} {op} {value}")
    return " ".join(parts)


def generate_agent_rego(agent_key: str, agent_def: dict) -> str:
    allow_actions = agent_def.get("allowed_actions", []) or []
    approval_rules = agent_def.get("approval_rules", []) or []

    lines = [HEADER.format(agent_key=agent_key)]
    if allow_actions:
        lines.append("allow_actions = {")
        for a in allow_actions:
            lines.append(f'  "{a}",')
        lines.append("}")
        lines.append("")

    unconditional = [
        r.get("action")
        for r in approval_rules
        if not r.get("condition") and not r.get("conditions")
    ]
    if unconditional:
        lines.append("approval_required = {")
        for a in unconditional:
            lines.append(f'  "{a}",')
        lines.append("}")
        lines.append("")

    # Conditional rules
    for r in approval_rules:
        action = r.get("action")
        cond = r.get("condition")
        conds = r.get("conditions") or []
        exprs = []
        if cond:
            exprs.append(parse_condition(cond))
        for c in conds:
            exprs.append(parse_condition(c))
        if not exprs:
            continue
        cond_expr = "\n  " + "\n  ".join(exprs) if len(exprs) > 1 else " " + exprs[0]
        block = f"""
approval_required[action] {{
  action := "{action}"{cond_expr}
}}
"""
        lines.append(block.strip("\n"))
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="registry/agents.yaml")
    ap.add_argument("--outdir", default="policies/agents")
    args = ap.parse_args()

    reg = yaml.safe_load(Path(args.registry).read_text())
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    agents = reg.get("agents", {})
    for key, agent in agents.items():
        agent_key = sanitize_key(key.replace("-", "_"))
        rego = generate_agent_rego(agent_key, agent)
        (outdir / f"{agent_key}.rego").write_text(rego)
        print(f"Generated policy for {key} -> {outdir}/{agent_key}.rego")


if __name__ == "__main__":
    main()
