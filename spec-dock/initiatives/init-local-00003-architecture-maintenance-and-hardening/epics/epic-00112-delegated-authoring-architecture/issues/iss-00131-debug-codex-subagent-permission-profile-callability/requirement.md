---
種別: 要件定義書（Issue）
ID: "iss-00131"
タイトル: "Restore guarded workspace-write authoring roles"
関連GitHub: ["#131"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-27"
親: ["epic-00112", "init-local-00003"]
---

# iss-00131 Restore guarded workspace-write authoring roles — 要件定義（何を、なぜ行うか）

## 目的
- `system-architect` / `implementation-planner` の fresh spawn 失敗を解消し、両 role を `spec-dock` の scope-local discussion authoring を担う write-capable static agent として復旧する。
- 失敗原因として最有力の custom Permission Profile と unsupported `write` glob を完全に削除し、Codex が公式に扱う `sandbox_mode = "workspace-write"` ベースの role contract へ置き換える。
- hard allow-list ではなく instruction、task-local consent、post-run diff guard、main orchestrator adoption、fresh reviewer gate を組み合わせ、workflow 価値と安全性の現実的なバランスを取る。

## 背景・現状
- 現状の挙動:
  - `fork_context=false` で `system-architect` / `implementation-planner` を fresh spawn すると `agent type is currently not available` になる。
  - 同じ project-local role でも `spec-manager` は legacy `sandbox_mode = "workspace-write"` を使って fresh spawn できる。
  - `fork_context=true` と `agent_type` の同時指定は Codex の full-history fork 仕様として拒否される。これは本 issue の修正対象ではない。
- 現状の課題:
  - `.codex/agents/system-architect.toml` と `.codex/agents/implementation-planner.toml` は `default_permissions` と `[permissions.*]` を持ち、`spec-dock/initiatives/*/.../discussions/*.md` 形式の `write` glob を含んでいる。
  - Codex Permission Profile 実装は `write` allow-list の arbitrary glob を表現できず、exact path または trailing `/**` subtree 以外の read/write glob を拒否する。
  - `read-only` 復旧だけでは、両 role が consultant と近い read-only advisory surface になり、research memo、discussion memo、draft proposal を role 単位で蓄積する delegated authoring workflow の価値が落ちる。
  - `workspace-write` は hard path allow-list ではないため、canonical docs、source、tests、config も技術的には編集可能になる。安全境界は sandbox だけではなく workflow guard と reviewer gate に移る。
- 再現手順:
  1. 現行 `.codex/agents/system-architect.toml` または `.codex/agents/implementation-planner.toml` を持つ worktree で multi-agent fresh spawn を行う。
  2. `fork_context=false` と対象 `agent_type` を指定する。
  3. `agent type is currently not available` が返ることを確認する。
- 観測点:
  - Codex multi-agent tool result:
    - fresh spawn が unavailable になるか。
  - role TOML:
    - `default_permissions` / `[permissions.*]` / unsupported `write` glob が残っていないか。
    - `sandbox_mode = "workspace-write"` と `[sandbox_workspace_write] network_access = false` があるか。
  - Git diff:
    - delegated role の run 後、許可された scope-local `discussions/` direct-child Markdown 以外の変更がないか。
  - report:
    - consent、diff guard、manual smoke、reviewer gate、adoption decision が記録されているか。
- 情報源:
  - ChatGPT 4.5 Pro との外部分析レポート（2026-05-26）。
  - OpenAI Codex docs:
    - https://developers.openai.com/codex/subagents
    - https://developers.openai.com/codex/config-reference
    - https://developers.openai.com/codex/agent-approvals-security
  - Codex source:
    - https://github.com/openai/codex/blob/main/codex-rs/core/src/config/permissions.rs
    - https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_common.rs
  - `spec-dock/active/issue/discussions/20260526t105722z-research-subagent-permission-profile-callability.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/active/epic/requirement.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `spec-dock` dogfooding repo で issue / epic / initiative の設計・計画 authoring を進める main orchestrator。
  - shipped scaffold を導入した consumer repo の Codex operator。
- 代表シナリオ:
  - main orchestrator が `system-architect` を起動し、対象 scope の `discussions/` 直下に architecture research、alternatives memo、design draft proposal を作成させる。
  - main orchestrator が `implementation-planner` を起動し、対象 scope の `discussions/` 直下に implementation breakdown、dependency memo、validation strategy draft を作成させる。
  - main orchestrator は run 後の diff guard を実行し、許可外 diff があれば delegated output を採用しない。
  - canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映、phase promotion、fresh `spec-reviewer` gate は main orchestrator が所有する。
  - 親 Epic が掲げる actual `design.md` / `plan.md` の delegated draft authoring は、本 issue では完了させない。まず fresh spawn できる discussion authoring surface を復旧し、canonical draft authoring は後続 issue / Epic amendment で再設計する。

## スコープ
- 必須:
  - `system-architect` / `implementation-planner` の static role TOML から `default_permissions` と `[permissions.*]` を完全に削除する。
  - 両 role に `sandbox_mode = "workspace-write"` を設定する。
  - 両 role に `[sandbox_workspace_write] network_access = false` を設定し、write-capable role と external web/network research を分離する。
  - 両 role の developer instructions / skill / `.codex/AGENTS.md` / shipped workflow docs を、guarded workspace-write authoring contract に合わせる。
  - 両 role の許可 write を「task-local consent で指定された target scope `discussions/` direct-child Markdown の新規作成」に限定する。
  - provider authority の `src/spec_dock/assets/install_root/` と dogfooding mirror の `.codex/` / `.agents/` を同期させる。
  - workflow docs / phase docs / role skills / tests が、Permission Profile による hard allow-list ではなく instruction + diff guard + adoption ledger による guarded authoring であることを明示する。
  - fresh spawn smoke、expected discussion write probe、forbidden path probe または代替 host limitation evidence を `report.md` に記録する。
  - `delegated-authoring scoped-context` はこの issue で復活させない。
- 禁止:
  - `default_permissions` または `[permissions.*]` を `system-architect` / `implementation-planner` に残すこと。
  - unsupported `write` glob を別の形で維持すること。
  - `sandbox_workspace_write.writable_roots` を workspace write の縮小境界として扱うこと。これは additional writable roots であり、workspace root の write を狭めるものではない。
  - `danger-full-access`、network access、credentialed access、GitHub mutation、destructive command を両 role の通常 path に含めること。
  - 両 role に canonical docs、implementation files、tests、package/config、`.agents`、`.codex`、`.github`、`.env*` を編集させること。
  - subagent の作成物を reviewer pass や canonical authority と自己主張させること。
  - `fork_context=true` + `agent_type` の拒否をこの issue の失敗として扱うこと。
  - actual `design.md` / `plan.md` の delegated draft authoring をこの issue の完了条件に含めること。
  - 既存 discussion draft の更新をこの issue の delegated authoring 成功 path に含めること。
- 対象外:
  - Codex upstream の Permission Profile 実装修正。
  - Codex docs / diagnostics の upstream issue 作成。
  - generated exact-file Permission Profile の復活。
  - separate worktree / branch isolation の新規実装。
  - issue lifecycle / active store / GitHub issue 作成フローの変更。
  - 親 Epic の E-RQ-002 / E-RQ-008 が掲げる actual canonical draft authoring と Permission Profile / task manifest 設計の完了。

## 境界
- 常に行う:
  - canonical docs は main orchestrator single-writer authority とする。
  - delegated role の file write は proposal/evidence の記録であり、採用ではないと扱う。
  - delegated role invocation ごとに target node、role、allowed discussion path rule、forbidden paths、stop condition、report evidence destination を明示する。
  - run 後に main orchestrator が `git status` / `git diff --name-status` / content inspection を行い、許可外 diff を fail-closed で扱う。
  - final phase promotion には fresh `spec-reviewer` pass を必須にする。
  - 親 Epic の canonical draft authoring 要件は未充足として扱い、この issue の report に限定修正であることを残す。
- 判断が必要:
  - parent permission profile override により role-level `workspace-write` が有効にならない場合、parent session の permission を変えて再試行するか、manual path に fallback するか。
  - forbidden path write probe を実行する場合、repo 内で安全に破棄できる probe path と rollback 手順をどう定義するか。
  - out-of-scope diff が出た delegated output を破棄するか、main orchestrator が手動で safe portion だけ採用するか。
  - 親 Epic の canonical draft authoring を後続 issue で guarded workspace-write に寄せるか、別の exact-target / worktree isolation 設計へ戻すか。
- 行わない:
  - instruction following を hard sandbox boundary と同一視しない。
  - subagent 自身に phase promotion、reviewer pass claim、issue ready / finish claim をさせない。
  - external web research と workspace-write authoring を同じ delegated role run に混ぜない。

## 非交渉制約
- `system-architect` / `implementation-planner` の custom Permission Profile は完全削除する。
- 両 role は guarded `workspace-write` role として復旧する。`read-only` は fallback / degraded mode としてのみ扱う。
- 両 role の network access は disabled にする。
- delegated output の許可先は scope-local `discussions/` direct-child Markdown に限る。
- provider side と dogfooding mirror の片側だけを修正して完了にしてはならない。
- `delegated-authoring scoped-context` を workaround として復活させてはならない。
- current issue の requirement/design/plan authoring は、故障対象の両 role へ委譲せず main orchestrator が代行する。
- この issue は親 Epic の delegated canonical draft authoring 全体を完了しない。Epic requirement との gap は report に残し、後続 issue / amendment の対象にする。

## 前提
- Codex custom agent file は spawned session の configuration layer として扱われ、通常 config と同じ settings を override できる。
- Codex config reference は `sandbox_mode = "workspace-write"` と `[sandbox_workspace_write] network_access` を official config として扱っている。
- Codex Permission Profile の current implementation は arbitrary read/write glob allow-list を supported path として扱わない。
- multi-agent fresh spawn flow では parent turn の permission profile が child config に再適用される可能性があるため、role TOML の `workspace-write` が final effective permission になるかは manual smoke / probe で確認する必要がある。
- GPT-5.5 の instruction following は強いが、workflow 上は soft control として扱い、diff guard と reviewer gate で補強する。

## 受け入れ条件
- AC-001: custom Permission Profile が完全に削除される
  - アクター: maintainer
  - 前提: provider role TOML と dogfooding mirror role TOML を読める
  - 操作: `system-architect.toml` / `implementation-planner.toml` を構造検査する
  - 期待結果: `default_permissions`、`[permissions.*]`、unsupported `write` glob が存在しない
  - 観測点: unit test、text inspection、provider/mirror parity
- AC-002: 両 static role が guarded workspace-write contract を持つ
  - アクター: maintainer
  - 前提: provider role TOML と dogfooding mirror role TOML を読める
  - 操作: role TOML を構造検査する
  - 期待結果: `sandbox_mode = "workspace-write"`、`approval_policy = "never"`、`web_search = "disabled"`、`[sandbox_workspace_write] network_access = false` が設定されている
  - 観測点: unit test、text inspection
- AC-003: fresh spawn が unavailable で拒否されない
  - アクター: main orchestrator
  - 前提: updated dogfooding role TOML が存在する
  - 操作: `fork_context=false` で `system-architect` / `implementation-planner` を fresh spawn する
  - 期待結果: `agent type is currently not available` ではなく、role が応答を返す
  - 観測点: multi-agent tool result、`report.md` manual smoke evidence
- AC-004: scope-local discussion authoring が可能である
  - アクター: delegated authoring role
  - 前提: target scope と allowed discussion path rule が task-local consent として明示されている
  - 操作: target scope `discussions/` direct child に新規 Markdown draft を 1 件作成する
  - 期待結果: allowed path の新規 draft だけが作成され、filename は discussion naming rule に一致する。既存 draft の更新は行われない
  - 観測点: `git status --short`、`git diff --name-status`、draft content inspection、`report.md`
- AC-005: forbidden path edits は採用されない
  - アクター: main orchestrator
  - 前提: delegated role run 後の diff を確認できる
  - 操作: diff guard で changed files を検査する
  - 期待結果: canonical docs、source、tests、config、`.agents`、`.codex`、`.github`、`.env*`、nested discussion dirs、non-Markdown、renames、deletes、out-of-scope discussions が変更されていた場合、その delegated output は adoption-ineligible と記録される
  - 観測点: diff guard output、Evidence Adoption Ledger、Delegated Draft Evidence
- AC-006: docs / skills / tests が guarded workspace-write 方針を一貫して説明する
  - アクター: maintainer / reviewer
  - 前提: shipped docs、dogfooding docs、role skills、tests を読める
  - 操作: static write path、read-only advisory path、scoped-context workaround の説明を点検する
  - 期待結果: 両 role は `workspace-write` による write-capable discussion authoring role として説明され、Permission Profile hard allow-list や `scoped-context` 復活を current success path として案内しない
  - 観測点: `rg` inspection、unit test、spec-reviewer
- AC-007: provider authority と dogfooding mirror が同期している
  - アクター: maintainer
  - 前提: provider assets と dogfooding mirror を比較できる
  - 操作: affected `.codex` / `.agents` / docs assets の parity test を実行する
  - 期待結果: provider と mirror が同じ role contract と guidance を持つ
  - 観測点: parity tests、diff inspection
- AC-008: final validation が通る
  - アクター: maintainer
  - 前提: implementation changes が working tree にある
  - 操作: targeted tests、`./spec-dock/scripts/spec-dock validate`、`git diff --check`、fresh reviewer gates を実行する
  - 期待結果: 自動検証と reviewer gates が pass し、manual-required evidence は `report.md` に残る
  - 観測点: command output、reviewer result、report closure ledger
- AC-009: 親 Epic との scope gap が明示される
  - アクター: maintainer / reviewer
  - 前提: active epic requirement と this issue requirement / report を読める
  - 操作: 親 Epic の delegated canonical draft authoring 要件と this issue の scope を比較する
  - 期待結果: this issue は discussion authoring surface の復旧に限定され、actual `design.md` / `plan.md` delegated draft authoring と Permission Profile / task manifest 設計は未充足の後続対象として明記されている
  - 観測点: `requirement.md` scope / non-scope、`report.md` decision ledger、spec-reviewer

## 例外・エッジケース
- EC-001: parent permission profile override により child が write できない
  - 条件: role TOML は `workspace-write` だが child write probe が permission error になる
  - 期待: AC-004 を pass にせず、parent permission / host limitation として `report.md` に記録し、manual path または fresh session retry を判断する
  - 観測点: tool error、manual smoke evidence
- EC-002: child が forbidden path を編集できてしまう
  - 条件: workspace-write のため canonical docs / source / tests などへ write 可能であることが確認される
  - 期待: これは想定リスクであり、diff guard の fail-closed と adoption-ineligible 記録により安全側に倒す。hard boundary として扱わない
  - 観測点: diff guard、report incident entry
- EC-003: network disabled により notify / helper command が失敗する
  - 条件: role TOML の `notify` が network-dependent helper を呼ぶ、または package fetch が必要になる
  - 期待: role callability の blocker か optional notify failure かを切り分け、必要なら role config / docs に limitation を記録する
  - 観測点: app/server log、manual smoke evidence
- EC-004: role remains unavailable after Permission Profile removal
  - 条件: `default_permissions` / `[permissions.*]` を削除しても fresh spawn が unavailable のまま
  - 期待: role registry / host reload / other TOML config error として追加調査し、AC-003 を pass にしない
  - 観測点: manual smoke evidence、report blocker
- EC-005: historical docs に old Permission Profile / scoped-context wording が残る
  - 条件: past issue / discussion artifacts に旧方針が残る
  - 期待: historical evidence として残し、current shipped docs / role skills / tests に残る stale guidance と区別する
  - 観測点: `rg` inspection classification

## 入力→出力例
- EX-001: `system-architect` discussion draft run
  - 入力: target issue `iss-00131`、allowed path `spec-dock/.../issues/iss-00131.../discussions/<ts>-disc-architecture-options.md`、source docs `requirement.md` / epic requirement / workflow docs
  - 出力: allowed path に Markdown draft 1 件。canonical docs、source、tests は変更しない。
- EX-002: forbidden diff が出た場合
  - 入力: delegated role run 後の diff に `spec-dock/active/issue/design.md` 変更が含まれる
  - 出力: main orchestrator は delegated output を adoption-ineligible とし、safe portion が必要なら手動で別 diff として採用する。subagent output 自体は reviewer pass / canonical authority と扱わない。

## 用語（ドメイン語彙）
- TERM-001: guarded workspace-write authoring role
  - `sandbox_mode = "workspace-write"` を持つが、許可された write は instruction、task-local consent、post-run diff guard、main orchestrator adoption により scope-local `discussions/` direct-child Markdown に限定される delegated role。
- TERM-002: custom Permission Profile
  - `default_permissions` と `[permissions.*]` により Codex filesystem permissions を定義する config。今回の対象 role からは完全削除する。
- TERM-003: unsupported write glob
  - `spec-dock/initiatives/*/.../discussions/*.md` のように、Codex Permission Profile の read/write allow-list としては exact path または trailing `/**` subtree になっていない glob。
- TERM-004: post-run diff guard
  - delegated role run 後に main orchestrator が changed files と content を確認し、許可外 diff を adoption-ineligible とする workflow boundary。
- TERM-005: task-local consent
  - 1 回の delegated authoring run ごとに target node、role、allowed discussion path rule、forbidden paths、stop condition、report evidence destination を明示する同意・実行境界。
- TERM-006: adoption-ineligible
  - delegated output が canonical docs や phase promotion の根拠として採用できない状態。許可外 diff、missing consent、stale source、reviewer unavailable などで発生する。
- TERM-007: discussion authoring surface
  - role が scope-local `discussions/` direct-child Markdown を新規作成し、main orchestrator が後で採否を判断できる evidence を残すための authoring surface。actual `design.md` / `plan.md` の delegated canonical draft authoring とは別物。

## 未確定事項
- Q-001:
  - 質問: role TOML の `sandbox_mode = "workspace-write"` は current Codex Desktop/API session の fresh spawn child で final effective permission として残るか。
  - 選択肢:
    - A: 残る。
      - role-level `workspace-write` で expected discussion write probe を実行できる。
    - B: parent permission profile により上書きされる。
      - parent session permission または fresh session の扱いを report に記録し、manual path / retry / follow-up を判断する。
  - 推奨案:
    - implementation 中に manual smoke と harmless write probe で確認し、結果を AC-003 / AC-004 の pass/fail に反映する。
  - 影響範囲:
    - role TOML contract、manual smoke、report blocker、future workflow guidance。
- Q-002:
  - 質問: forbidden path write probe を実際に行うか、diff guard inspection だけにするか。
  - 選択肢:
    - A: 安全な temporary probe path を明示して negative probe を行う。
    - B: forbidden path への実 write は行わず、workspace-write の soft-boundary risk と diff guard contract で閉じる。
  - 推奨案:
    - B。実 write probe は accidental diff のリスクがあり、今回の受け入れ条件は forbidden write が技術的に不可能であることではなく、許可外 diff を採用しないことに置く。
  - 影響範囲:
    - manual test design、report evidence、reviewer focus。
