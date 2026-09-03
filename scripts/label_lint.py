#!/usr/bin/env python3
"""label_lint.py — the non-LLM oracle for grok-bitch's OWN claim class.

The cast's product is text: agent reports, labels, verdicts, gates. Lean/z3 verify
claims about a proof or a compiler; *this* verifies whether a cast report obeyed its
own grammar. Deterministic pattern match — it cannot be talked into a false pass.

Two rules it never breaks, so the rigor never turns the prose mechanical:
  1. It reads ONLY the fenced ```outcome block — never the prose above it. The voice
     is untouchable; the machine lives in six lines under it.
  2. It WARNS; it never blocks. A gate that wedges the cast is bureaucracy, not rigor.

No block present → no findings. A scratch probe or a lookup carries no load-bearing
claim and owes no block; the linter stays silent. It only grades a block that exists.

Modes:
  label_lint.py [FILE]   lint a report file (or stdin); human output; exit 1 on findings.
  label_lint.py --hook   read a SubagentStop hook JSON on stdin, pull the last assistant
                         message from transcript_path (JSONL), lint it, emit
                         {"systemMessage": ...} on findings, and exit 0 ALWAYS.
"""
import sys, os, re, json

TOP_TIER = r"Verified|Disclosed|Demonstrated|Confirmed"
CORE_KEYS = ("outcome", "dissent", "open-debts")


def extract_block(text):
    """Return the body of the ```outcome block, or None if there isn't one."""
    m = re.search(r"```outcome[ \t]*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1)
    # tolerant fallback: any fenced block whose first content line is 'outcome:'
    for mm in re.finditer(r"```[^\n]*\n(.*?)```", text, re.DOTALL):
        if re.match(r"\s*outcome\s*:", mm.group(1)):
            return mm.group(1)
    return None


def parse_block(body):
    d = {}
    for line in body.splitlines():
        m = re.match(r"\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            d[m.group(1).lower()] = m.group(2).strip()
    return d


def is_template(d):
    """A spec/example block, not a real claim: an options list, or bare <placeholder> values.
    A real report has ONE concrete outcome and no unfilled angle-bracket templates."""
    if " | " in d.get("outcome", ""):
        return True
    return any(re.fullmatch(r"<.*>", v.strip()) for v in d.values())


def lint(text):
    """Return a list of advisory findings for the outcome block in `text` (may be empty)."""
    body = extract_block(text)
    if body is None:
        return []  # no load-bearing footer -> nothing to grade; prose stays free
    d = parse_block(body)
    if is_template(d):
        return []  # the spec that defines the format is not a claim to grade
    out = []

    for k in CORE_KEYS:
        if k not in d:
            out.append(f"outcome block is missing required key '{k}:'")

    if d.get("outcome") == "done":
        vexit = d.get("verify-exit", "")
        if vexit != "0":
            out.append(
                f"outcome: done but verify-exit is '{vexit or 'missing'}' — "
                f"a 'done' is a claim; only a green verify (exit 0) is proof"
            )

    od = d.get("open-debts", "")
    od_int = None
    if od != "":
        if re.fullmatch(r"\d+", od):
            od_int = int(od)
        else:
            out.append(f"open-debts '{od}' is not an integer")

    label = d.get("label", "")
    if label and label.lower() not in ("n/a", "na", "none", ""):
        top = re.search(rf"\b({TOP_TIER})\b", label)
        if top:
            two_routes = re.search(rf"\b(?:{TOP_TIER})\b\s*\[[^\]|]*\|[^\]]*\]", label)
            if not two_routes:
                out.append(
                    f"top-tier label '{top.group(1)}' names no two routes — write "
                    f"Verified[route-A | route-B]; all-LLM agreement caps at Observed"
                )
            if od_int:
                out.append(
                    f"top-tier label with open-debts={od_int}: nonzero debts block any Verified"
                )

    if d.get("dissent", "") == "":
        out.append("dissent is blank — silence is not consent; write 'none' as a claim if truly nothing")

    return out


def last_assistant_text(transcript_path):
    """Extract the final non-empty assistant text message from a JSONL transcript."""
    text = ""
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                if obj.get("type") != "assistant":
                    continue
                content = obj.get("message", {}).get("content")
                parts = []
                if isinstance(content, list):
                    parts = [b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text"]
                elif isinstance(content, str):
                    parts = [content]
                joined = "".join(parts).strip()
                if joined:
                    text = joined  # keep the last non-empty assistant text
    except OSError:
        return ""
    return text


def main(argv):
    if "--hook" in argv:
        try:
            hook = json.loads(sys.stdin.read())
        except ValueError:
            return 0
        report = last_assistant_text(hook.get("transcript_path", ""))
        findings = lint(report) if report else []
        if findings:
            msg = "grok-bitch label-lint (advisory) — " + "; ".join(findings)
            print(json.dumps({"continue": True, "systemMessage": msg}))
        return 0  # advisory only: NEVER block a subagent

    args = [a for a in argv if not a.startswith("--")]
    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    findings = lint(text)
    if findings:
        print("label-lint: FINDINGS")
        for f in findings:
            print("  - " + f)
        return 1
    print("label-lint: clean (block valid, or no outcome block to grade)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
