#!/usr/bin/env bash
# live-matrix.sh — run the OpenCode live integration matrix on a COLD host
# (`opencode run --standalone` starts a private server that cold-loads every plugin).
#
# Requires: opencode, the plugins installed (scripts/opencode-install.sh).
# Prints raw JSON evidence. See opencode/tests/INTEGRATION-REPORT.md.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODEL="${OPENCODE_MATRIX_MODEL:-opencode/space-bunny-free}"
VALIDATE_CMD="${OPENCODE_MATRIX_VERIFY:-python3 $ROOT/scripts/opencode-validate.py}"

echo "== host =="; opencode --version; node --version

echo "== 1. fresh host-attested verification (pass) =="
opencode run --standalone --auto --model "$MODEL" "Do exactly this. Print raw JSON per step prefixed by RESULT:.
1. const s=await tools[\"grok-bitch\"].workflow_start({name:\"live-fresh\"}); parse runId.
2. const p=await tools[\"grok-bitch\"].workflow_verify_prepare({runId, verifyId:\"adapter-validate\"}); parse challengeId.
3. Use your shell tool to run EXACTLY: ${VALIDATE_CMD}
4. const v=await tools[\"grok-bitch\"].workflow_verify({runId, verifyId:\"adapter-validate\", challengeId}); print JSON.stringify(v).
5. const f=await tools[\"grok-bitch\"].workflow_finish({runId}); print JSON.stringify(f)." 2>&1 | grep -E "^RESULT:"

echo "== 2. no-attestation => fail (challenge, command not run) =="
opencode run --standalone --auto --model "$MODEL" "Do exactly this. Print raw JSON per step prefixed by RESULT:.
1. const s=await tools[\"grok-bitch\"].workflow_start({name:\"live-noattest\"}); parse runId.
2. const p=await tools[\"grok-bitch\"].workflow_verify_prepare({runId, verifyId:\"adapter-validate\"}); parse challengeId.
3. const v=await tools[\"grok-bitch\"].workflow_verify({runId, verifyId:\"adapter-validate\", challengeId}); print JSON.stringify(v).
4. const f=await tools[\"grok-bitch\"].workflow_finish({runId}); print JSON.stringify(f)." 2>&1 | grep -E "^RESULT:"

echo "== 3. stale pre-challenge attestation => rejected =="
opencode run --standalone --auto --model "$MODEL" "Do exactly this. Print raw JSON per step prefixed by RESULT:.
1. Use your shell tool to run EXACTLY: ${VALIDATE_CMD}
2. const s=await tools[\"grok-bitch\"].workflow_start({name:\"live-stale\"}); parse runId.
3. const p=await tools[\"grok-bitch\"].workflow_verify_prepare({runId, verifyId:\"adapter-validate\"}); parse challengeId.
4. const v=await tools[\"grok-bitch\"].workflow_verify({runId, verifyId:\"adapter-validate\", challengeId}); print JSON.stringify(v)." 2>&1 | grep -E "^RESULT:"

echo "== 3b. requested verifier skipped => finish fails (verify-missing) =="
opencode run --standalone --auto --model "$MODEL" "Do exactly this. Print raw JSON per step prefixed by RESULT:.
1. const s=await tools[\"grok-bitch\"].workflow_start({name:\"live-debt-skip\"}); const a=await tools[\"grok-bitch\"].workflow_agent({runId:s.runId, agentType:\"grok-bitch:morty\", prompt:\"Reply with one word: aye\", verifyId:\"adapter-validate\"});
2. const f=await tools[\"grok-bitch\"].workflow_finish({runId:s.runId}); print JSON.stringify(f)." 2>&1 | grep -E "^RESULT:"

echo "== 4. four-plugin coexistence (one job per namespace, cold host) =="
opencode run --standalone --auto --model "$MODEL" "Run all steps, then print EXACTLY one final line beginning RESULT:.
A: const s=await tools[\"grok-bitch\"].workflow_start({name:\"co\"}); const r=await tools[\"grok-bitch\"].workflow_agent({runId:s.runId,prompt:\"Reply one word: aye\",agentType:\"grok-bitch:morty\"}); gb=r.agentID.
B: const z=await tools[\"project-zion\"].workflow_start({name:\"co\"}); const b=await Promise.all([tools[\"project-zion\"].workflow_agent({runId:z.runId,prompt:\"Reply one word: aye\",agentType:\"project-zion:oracle\"}),tools[\"project-zion\"].workflow_agent({runId:z.runId,prompt:\"Reply one word: aye\",agentType:\"project-zion:smith\"})]); pz=b.map(x=>x.agentID).
C: const e=await tools[\"project-euler\"].workflow_start({name:\"co\"}); const d=await tools[\"project-euler\"].workflow_agent({runId:e.runId,prompt:\"Reply one word: aye\",agentType:\"project-euler:daniel\"}); pe=d.agentID.
D: shell-run EXACTLY: uppermanagement packet --repo $ROOT --seed 7 --format json --output /tmp/um-coexist.json
Final: RESULT: {\"gb\":gb,\"pz\":pz,\"pe\":pe,\"um\":<true if D exit 0>}" 2>&1 | grep -E "^RESULT:"

echo "done."
