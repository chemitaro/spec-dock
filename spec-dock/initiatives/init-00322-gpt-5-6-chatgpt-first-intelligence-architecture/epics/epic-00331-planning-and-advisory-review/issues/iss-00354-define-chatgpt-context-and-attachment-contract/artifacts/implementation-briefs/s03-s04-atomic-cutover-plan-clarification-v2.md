# iss-00354 — S03/S04 atomic cutover plan clarification v2

## 位置づけ

これは `s03-s04-atomic-cutover-plan-clarification.md` を入力証跡として保持したまま、fresh Red Team review v1 の P1 指摘だけを反映した実装前の補正 addendum である。要件・設計の再設計、実装、レビューによる repository 変更を意味しない。

## 対象 identity

- repository: `chemitaro/spec-dock`
- branch: `codex/iss-00354-chatgpt-context-contract`
- review v1 の対象 HEAD: `dada1f403241f615340ae1f0f8fb28b047edae75`
- review v1: `reviews/red-team-review-s03-s04-plan-v1.md`（P0=0 / P1=3）
- v1 review identity SHA-256: `d660016800b378b9fbd689a18ed3d41af0a1c4aa5e380ada6bbdd064df3e2a05`

## P1 修正後の atomic scope

S03/S04 は引き続き、同一 deployable change-set、rollback unit、fresh review target とする。次の production resource と full-chain fixture を runtime union に含める。

- provider Review resource: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md`
- full-chain consumer test: `tests/integration/test_issue_planning_e2e.py`
- installed/dogfood の同名 Review resource projection は provider sync で再生成し、projection を手編集しない。

Review resource は、存在しない `reviewed-identity.json` と `reviewed-identity-sha256.txt` を要求せず、minimal body に deterministic に描画された `ReviewedPlanningIdentity.to_dict()` と `identity.sha256` を参照する。Review JSON の closed parser と typed identity equality は維持する。

`tests/integration/test_issue_planning_e2e.py` の fake Oracle は generated pack の identity files を読む旧契約から direct attachment paths と minimal-body identity を読む契約へ同じ atomic change-set 内で更新する。旧 generated-pack symbols の repository search gate は S03/S04 closure 条件として維持する。

## allowlist / forbidden boundary

- production runtime: `application/issue_planning_prompt.py`, `application/issue_planning.py`, `infra/issue_planning_chatgpt.py`
- production resource: 上記 provider Review resource instructions（identity contract の変更に限る）
- tests: application/infra unit tests、transport integration test、`tests/integration/test_issue_planning_e2e.py`
- generated projection: provider sync の出力として byte parity を検証する。手編集は禁止する。
- forbidden: domain contract、CLI/commands、Oracle profile/recovery、artifact reader、上記以外の resource wording/inventory、compatibility bridge、dual-write、generated input pack、copy/ZIP/hash/tree inspection、inline fallback、alternate backend

S03 は path-only application contract/callers、S04 は repeated direct `--file` transport を担当し、`cl-s03-path-input` と `cl-s04-direct-transport` は同一 resulting HEAD でのみ close する。

## 実装前ゲート

1. v2 addendum と修正済み `plan.md` / `report.md` を新しい exact HEAD で fresh defect-only Red Team review に渡す。
2. PASS（P0/P1=0）までは production implementation を開始しない。
3. PASS 後に S03/S04 専用ブリーフとこの addendumを入力として、同じ resulting HEAD の atomic implementation を実施する。
