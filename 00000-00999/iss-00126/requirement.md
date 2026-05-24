---
種別: 要件定義書（Issue）
ID: "iss-00126"
タイトル: "Write Capable Delegated Draft Authoring Correction"
関連GitHub: ["#126"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-24"
親: ["epic-00112", "init-local-00003"]
---

# iss-00126 Write Capable Delegated Draft Authoring Correction — 要件定義

## 目的

`epic-00112` の v1 要件を満たすため、現在の proposal-only / read-only fallback 固定を是正し、`system-architect` と `implementation-planner` が検証済み task manifest / Permission Profile / probe の下で actual `design.md` / `plan.md` draft を作成・更新できる状態にする。

この Issue は、前回までの fallback-only 実装に無理に合わせるための修正ではない。ユーザーが指摘した要件未達を解消し、Epic v1 の本来の目的である write-capable delegated draft authoring を安全に成立させる。

## 背景・現状

- Epic v1 requirement は、`system-architect` が actual `design.md` を、`implementation-planner` が actual `plan.md` を `status: draft` / `authority: proposed` として作成・更新できることを要求している。
- 現在の `.codex/agents/system-architect.toml` と `implementation-planner.toml` は `Read-only`、`proposal-only mode and do not write`、`Do not implement write-capable delegation` を含み、actual draft write を実質的に禁止している。
- 現在の Permission Profile は `.codex/permission-probe-evidence` だけを書ける static fallback であり、actual `design.md` / `plan.md` を書けない。
- `tests/test_init_update.py` は probe-only / not write-capable を正しい挙動として固定している。
- `.codex/config.toml` と provider copy は `agents.max_depth = 1` であり、Epic v1 の bounded depth=2 delegation と衝突している。
- `workflow_issue.md`、report template、issue-plan authoring contract は read-only specialist と write-scoped delegated draft authoring の consent / evidence を十分に分けられていない。

## 情報源

- `epic-00112/requirement.md`
- `epic-00112/design.md`
- `epic-00112/plan.md`
- `discussions/20260523t235448z-disc-write-capable-draft-authoring-gap-analysis.md`
- `discussions/20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2.md`
- OpenAI Codex Permissions: https://developers.openai.com/codex/permissions
- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Config Reference: https://developers.openai.com/codex/config-reference

## スコープ

### 必須

- task manifest / task-specific Permission Profile helper を追加し、main orchestrator が actual write session の権限境界を生成できるようにする。
- `input_authority` を manifest の必須項目にし、upstream requirement / design の approval 証跡、approved revision/hash、fresh reviewer verdict/hash、required grants、stale check が不一致または欠落する場合は profile/probe を生成しない。
- `input_authority` は reviewer verdict/hash の自己申告を信用しない。`reviewer_evidence_path` を必須にし、promotion record と reviewer evidence の双方を照合する。
- Permission Profile と旧 `sandbox_mode` / `[sandbox_workspace_write]` の混在を禁止する。
- `system-architect` / `implementation-planner` adapter を proposal-only 固定から、verified manifest/profile/probe 成功時だけ exact target write を許す fail-closed 契約に更新する。
- `agents.max_depth = 2` とし、child delegation を leaf-only evidence producer に限定する。
- child allowlist、no-grandchild、no peer-author child、no implementation child、no canonical edit を docs/skills/tests で固定する。
- `workflow_spec_authoring.md`、`workflow_issue.md`、phase docs、report templates、`docs/authoring/issue-plan.md` を更新する。
- artifact-level authority gate を runtime に追加し、`authority: proposed` artifact が implementation / issue ready / issue finish / phase completion に使われないことを検証する。
- actual `design.md` / `plan.md` draft は E-AC-001 metadata fields を持つことを必須にする。
- non-destructive sentinel negative probe と diff gate を導入し、fail-open 時に実 artifact / source / tests / secrets を汚さない。
- negative probe は forbidden boundary category ごとに検査対象を持つ。最低カテゴリは `requirement.md`、peer artifact、`report.md`、`src/`、`tests/`、`.codex/`、`.agents/`、`.env*` 相当とし、実 protected file ではなく disposable sentinel で検証する。
- dogfooding pilot で actual `design.md` と `plan.md` の draft write、negative probe、diff gate、ledger adoption、reviewer gate を実証する。
- 完了済み issue report は過去に実行していない内容へ改ざんしない。

### 禁止

- broad `spec-dock/initiatives` write や repo-wide write を許可して要件達成と見なす。
- limited directory write や discussions-only output を actual canonical draft write の代替として E-AC-003 / E-AC-004 pass に数える。
- sub-agent が自分で task-specific Permission Profile を生成する。
- `sandbox_mode` と Permission Profile を同じ delegated authoring path で混在させる。
- child specialist に canonical edit、implementation edit、promotion、final reviewer authority を与える。
- real `requirement.md`、peer artifact、`report.md`、source/test/config/secret file に対して破壊的 negative probe を行う。

### 対象外

- `.github/agents` / Copilot agent support。
- Desktop App を CLI と同等の verified path として閉じること。Desktop は同等 probe まで fallback とする。
- depth=3 以上の nested delegation。
- PR merge 自体。

## 非交渉制約

- Provider-first: shipped assets は `src/spec_dock/assets/...` を先に更新し、dogfooding copy を検証 surface として扱う。
- Main ownership: `requirement.md`、final promotion、fresh reviewer gate、user dialogue、report ledger は main orchestrator が所有する。
- Authority separation: `status: draft` / `authority: proposed` は downstream authority ではない。
- Fail closed: manifest / profile / probe / authority / ledger / reviewer evidence が不足する場合は proposal-only fallback に戻す。
- Historical integrity: 完了済み issue report を actual write 成功として書き換えない。

## 受け入れ条件

- AC-001 Task manifest helper:
  - 前提: role、scope、target artifact、host surface、upstream approval evidence を入力する。
  - 操作: `spec-dock delegated-authoring manifest ... --input-authority-file <path>` が task manifest と Permission Profile fragment を生成する。
  - 期待結果: input authority file の `source_revisions` / `input_authority` と referenced promotion / reviewer evidence が照合され、`stale_check` は literal `fresh` として検証され、`input_authority`、allowed paths、forbidden paths、positive probe、boundary-specific non-destructive negative probe、diff gate、fallback、generated artifact paths が出力される。
  - 観測点: helper unit test / CLI command test / generated manifest evidence。

- AC-002 Upstream authority gate:
  - 前提: upstream requirement/design の approval evidence が欠落、不一致、stale、または required grant 不足である。
  - 操作: helper を実行する。
  - 期待結果: profile/probe を生成せず blocked result を返す。
  - 観測点: domain/runtime test。

- AC-003 Adapter contract:
  - 前提: shipped adapter を確認する。
  - 操作: adapter TOML と tests を検査する。
  - 期待結果: proposal-only 固定文言はなく、verified manifest/profile/probe 成功時の exact target write path と fail-closed fallback を持つ。
  - 観測点: `tests/test_init_update.py`。

- AC-004 Bounded depth=2:
  - 前提: provider / dogfooding config と role skills を確認する。
  - 操作: `agents.max_depth` と child constraints を検査する。
  - 期待結果: `max_depth = 2`、allowed child role、max child calls、leaf-only、no-grandchild、no peer-author、no dev-coder child が固定される。
  - 観測点: config / skill / docs tests。

- AC-005 Non-destructive probe:
  - 前提: forbidden boundary を検証する。
  - 操作: negative probe plan を生成 / 検査する。
  - 期待結果: real artifact を触らず、`requirement.md`、peer artifact、`report.md`、`src/`、`tests/`、`.codex/`、`.agents/`、`.env*` 相当の各 forbidden boundary category に disposable sentinel / cleanup / dirty diff abort を要求する。
  - 観測点: tests / report evidence。

- AC-006 Draft artifact metadata:
  - 前提: actual `design.md` / `plan.md` draft write が行われる。
  - 操作: artifact metadata を検証する。
  - 期待結果: `status`、`authority`、`grants`、`owner_role`、`draft_author_role`、`approval`、`source_revision`、`approved_revision`、`approved_hash`、`manifest_hash`、`permission_profile_name`、`permission_profile_hash`、`write_session_invocation_hash`、`probe_run_id`、`positive_probe_result` を持つ。欠落時は blocked / incomplete。
  - 期待結果: approved delegated artifact metadata は `positive_probe_result=pass` だけを downstream authority として受け付ける。`positive_probe_result` が欠落する場合は incomplete、`fail` / `failed` / 空文字列など pass 以外の場合は blocked とする。
  - 観測点: validate / context-pack / lifecycle tests。

- AC-007 Authority runtime gate:
  - 前提: artifact が `authority: proposed` である。
  - 操作: `spec-dock validate`、active context-pack rendering / context-pack inclusion、implementation / finish purpose gate、issue finish 相当の gate を通す。
  - 期待結果: proposed artifact は authoritative input にならず、implementation / issue ready / issue finish / phase completion を通らない。
  - 観測点: validate / context-pack / lifecycle runtime tests。

- AC-008 Workflow and report evidence:
  - 前提: write-scoped delegated draft authoring を使う。
  - 操作: workflow docs、report templates、issue-plan authoring contract を確認する。
  - 期待結果: consent、manifest、probe、diff gate、candidate evidence、canonical Evidence Adoption Ledger、fallback decision、report evidence destination が追跡できる。
  - 観測点: managed asset tests。

- AC-009 Dogfooding pilot:
  - 前提: corrective issue の dogfooding target がある。
  - 操作: actual `design.md` / `plan.md` draft write と probe / diff gate / ledger adoption を実行する。
  - 期待結果: design pilot は approved requirement を入力にして proposed `design.md` を作る。main orchestrator が design を採用・fresh review・promotion した後、plan pilot は approved requirement/design を入力にして proposed `plan.md` を作る。actual write session は generated task-specific Permission Profile を `default_permissions` として選択した supported Codex CLI invocation または verified host-equivalent invocation で実行され、invocation command/config override、profile identity/hash、positive probe binding が report に残る。exact target draft write は `authority: proposed` と full metadata を持ち、forbidden path 差分はなく、downstream gate は proposed を拒否する。manual / unprofiled edit は AC-009 pass に数えない。
  - 観測点: report evidence / tests / spec-reviewer。

- AC-010 Epic-wide quality gate:
  - 前提: 全実装が終わった。
  - 操作: development branch との差分全体を deep-consultant と fresh spec-reviewer で確認する。
  - 期待結果: 指摘があれば修正し、fresh reviewer pass 後に PR 更新可能になる。
  - 観測点: final report evidence。

## 例外・エッジケース

- EC-001 CLI Permission Profile が exact file write を enforce できない:
  - 期待: limited directory candidate draft へ fallback し、v1 acceptance には数えない。
- EC-002 Desktop App が CLI と divergent:
  - 期待: Desktop path は `acceptance_counted=false` として proposal-only / manual fallback。
- EC-003 negative sentinel が unexpectedly created:
  - 期待: fail-open として cleanup evidence を残し、dirty diff が残る場合は abort。
- EC-004 unresolved `blocked` / `stale` ledger entry がある:
  - 期待: promotion / implementation start / issue finish を止める。

## 未確定事項

- なし。実装中に helper injection の実現方法が CLI 制約で変わる場合は、plan amendment と fresh spec-review を行う。
