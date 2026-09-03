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
  label_lint.py --hook   read a SubagentStop hook JSON on stdin, take the stopped subagent's
                         last assistant message (from 'last_assistant_message', else the
                         'agent_transcript_path' JSONL — NOT 'transcript_path', which is the
                         parent session), lint it, emit {"systemMessage": ...} on findings,
                         and exit 0 ALWAYS.
"""
import sys, os, re, json, hashlib, time, tempfile

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


_DEDUP_TTL_SEC = 300
_DEDUP_PATH = os.path.join(tempfile.gettempdir(), "grok_bitch_label_lint_dedup.json")


def _recently_emitted(report):
    """Idempotency guard. The harness can fire SubagentStop more than once per stop, so emit
    a given advisory at most once per report body within a TTL window. Keyed on the report
    TEXT itself: an identical re-fire is suppressed; a genuinely different subagent's report
    still emits. Fail-OPEN: any dedup error falls straight through to emitting, because a
    missed warning is worse than a duplicated one — the linter's job outranks its manners."""
    key = hashlib.sha1(report.encode("utf-8")).hexdigest()
    now = time.time()
    try:
        seen = {}
        if os.path.exists(_DEDUP_PATH):
            with open(_DEDUP_PATH, encoding="utf-8") as f:
                seen = json.load(f)
        # prune stale keys so the file can't grow without bound
        seen = {k: t for k, t in seen.items()
                if isinstance(t, (int, float)) and now - t < _DEDUP_TTL_SEC}
        if key in seen:
            return True
        seen[key] = now
        tmp = _DEDUP_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(seen, f)
        os.replace(tmp, _DEDUP_PATH)  # atomic: never leave a half-written state file
        return False
    except Exception:
        return False


def _coerce_message_text(m):
    """Flatten a last-assistant-message field to plain text. Handles the three shapes a
    harness might hand us: a bare string, a message dict ({content|text: ...}), or a list of
    content blocks ([{type: text, text: ...}, ...])."""
    if isinstance(m, str):
        return m
    if isinstance(m, dict):
        return _coerce_message_text(m.get("content", m.get("text", "")))
    if isinstance(m, list):
        return "".join(b.get("text", "") for b in m
                       if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _hook_report(hook):
    """The stopped SUBAGENT's final assistant text, from whichever field this harness sets.
    Prefer 'last_assistant_message' (supplied directly, and immune to the subagent transcript
    not yet being flushed to disk when SubagentStop fires — an observed race). Fall back to the
    subagent transcript at 'agent_transcript_path'. Deliberately NOT 'transcript_path': on this
    harness that key is the PARENT session, and linting the orchestrator's own prose would fire
    false advisories against the wrong agent."""
    text = _coerce_message_text(hook.get("last_assistant_message"))
    if text.strip():
        return text
    atp = hook.get("agent_transcript_path")
    if atp:
        return last_assistant_text(atp)
    return ""


def main(argv):
    if "--hook" in argv:
        try:
            hook = json.loads(sys.stdin.read())
        except ValueError:
            return 0
        report = _hook_report(hook)
        findings = lint(report) if report else []
        if findings and not _recently_emitted(report):
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
