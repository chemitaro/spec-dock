# iss-00050 s03 triage resolution

Branch: `iss-00050-host-adapter-scaffold-and-final-parity`

## Summary

`iss-00050` の S03 差分について triage を実施し、`tests/test_init_update.py` の差分を A / B に分解して判定した。

結論は以下の通り。

- A 差分は `keep`
- B 差分も `keep`
- B は host adapter 固有の新規 behavior ではなく、既存 runtime contract への parity test 追随として扱う
- 現在の S03 implementation diff は review に出せる状態まで整理できている

## Scope of this note

このノートは、`tests/test_init_update.py` に混ざっている非 host-adapter 系に見える差分が、`iss-00050` に残すべきかどうかを整理するためのもの。

対象は次の観点に限定する。

- host adapter / metadata / parity に直接必要な差分
- import/runtime contract 追随に見える test 差分
- review scope に残す diff と外す diff の切り分け

## A / B classification

### A: host adapter / metadata / parity に直接必要な差分

判定: `keep`

対象:

- `.agents/host-adapters/meta.json`
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `tests/test_init_update.py` の host adapter asset parity 追加
- `tests/test_init_update.py` の host adapter metadata parity 追加
- `tests/test_init_update.py` の checked-in dogfooding parity 追加

理由:

- いずれも `iss-00050` の受け入れ条件である host adapter scaffold 配布、metadata contract、provider/dogfooding parity closure に直接対応している

### B: import/runtime 契約の既存テスト整合に見える差分

判定: `keep`

対象:

- `tests/test_init_update.py` における `issue_gateway.calls == (..., "example/repo")`
- `tests/test_init_update.py` における `git_gateway=_StubGitGateway()` の追加

理由:

- provider-side runtime
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
- checked-in dogfooding runtime
  - `spec-dock/scripts/spec_dock_runtime/application/import_node.py`

の両方で、すでに次の contract が共有されている。

- `current_repo_slug` を解決する
- `git_gateway` を `Ports` 経由で使用する
- `issue_view_minimal(..., repo_slug=...)` を呼ぶ

したがって、B 差分は host adapter のための新規仕様ではない。
既存 runtime contract に対して checked-in parity tests を追随させる修正であり、`iss-00050` S03 の dogfooding parity closure として扱うのが妥当。

## Keep / justify / drop

### Keep

- `.agents/host-adapters/meta.json`
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `tests/test_init_update.py` の A 差分
- `tests/test_init_update.py` の B 差分
- `spec-dock/scripts/spec_dock_runtime/presentation/json_state.py`
- 以下の stale mirror cleanup とみなせる docs deletion
  - `spec-dock/docs/spec-dock-guide-old.md`
  - `spec-dock/docs/spec-dock-guide.md`
  - `spec-dock/docs/sync.md`
  - `spec-dock/docs/workflow-adr.md`
  - `spec-dock/docs/workflow-issue.md`

### Justify

- `tests/test_init_update.py` の B 差分
  - 既存 runtime contract への parity test 追随
- `spec-dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - 現時点では provider/dogfooding parity 差分として説明可能
- `spec-dock/docs/*.md` deletion
  - provider-side asset 不在に伴う stale mirror cleanup として説明可能

### Drop

- 現時点で確定した drop 対象はなし

## Review-ready scope

S03 implementation review に出してよい対象:

- `.agents/*`
- `spec-dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `tests/test_init_update.py`
- `spec-dock/docs/*` の stale mirror cleanup
- `spec-dock/active/issue/report.md` の S03 triage note

S03 implementation correctness review の主対象から外してよいもの:

- `spec-dock/active/issue/discussions/20260403t160027z-note-iss-00050-status-report.md`
  - これは共有用 status report であり、implementation diff の correctness 判定対象ではない

## Impact on next step

この triage により、`tests/test_init_update.py` の B 差分を理由付きで残したまま、S03 diff を reviewer に回せる状態になった。

次の実務上のアクションは以下。

1. 現在の S03 diff を `code_reviewer` に回す
2. 同じ diff を `qa_reviewer` に回す
3. 両 reviewer の verdict が `pass` になったら `report.md` を更新する
4. その後、S03 を stage gate commit にまとめる
