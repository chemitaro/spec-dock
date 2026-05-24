---
種別: 設計書（Issue）
ID: "iss-00126"
タイトル: "Write Capable Delegated Draft Authoring Correction"
関連GitHub: ["#126"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-24"
依存: ["requirement.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00126 Write Capable Delegated Draft Authoring Correction — 設計

## 目的・制約

この Issue は、Epic v1 の actual delegated draft authoring を成立させる correction slice である。中心は次の 5 点である。

1. main orchestrator 生成の task manifest / Permission Profile helper。
2. provider-first docs/templates/skills/adapters/config の契約整合。
3. artifact-level authority validation。
4. bounded depth=2 の安全な子委任。
5. dogfooding pilot による actual `design.md` / `plan.md` draft write 実証。

既存 fallback-only 実装は履歴として保持するが、acceptance の基準にはしない。

## 既存実装 / 規約の理解

- `src/spec_dock/assets/install_root/.codex/agents/*.toml` が shipped Codex adapter の provider source。
- `.codex/agents/*.toml` は dogfooding mirror。
- `src/spec_dock/assets/install_root/.agents/skills/*` が shipped role skill source。
- `.agents/skills/*` は dogfooding mirror。
- `src/spec_dock/assets/spec_dock/docs/...` と `src/spec_dock/assets/spec_dock/templates/...` が shipped spec-dock docs/templates source。
- runtime は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の layered architecture に従う。
- authority gate の既存 domain helper は `domain/authority.py` にある。
- active/context lifecycle は `application/set_active.py`、`application/issue_lifecycle.py`、`infra/active_store.py`、context-pack/status surfaces にまたがる。

## 採用方針

### D-001 CLI-first task manifest helper

`spec_dock_runtime` に delegated authoring manifest helper を追加する。helper は role / scope / target / host / upstream authority evidence を受け取り、manifest、Permission Profile TOML fragment、probe plan、diff gate plan を返す。

責務:

- dynamic exact path resolution。
- `input_authority` validation。
  - `stale_check` は literal `fresh` を唯一の pass 値とし、referenced promotion record と reviewer evidence が current approved revision/hash に一致することを表す。
- allowed / forbidden path contract。
- non-destructive probe plan generation。
- old sandbox settings の混在拒否。
- CLI command surface:
  - `spec-dock delegated-authoring manifest --role <system-architect|implementation-planner> --scope <node-id> --target <design|plan> --host-surface <cli|desktop> --input-authority-file <path>`
  - main orchestrator が実行時に呼び出す唯一の supported surface とする。
  - `--input-authority-file` は必須。main orchestrator が作成した TOML または JSON で、`source_revisions` と `input_authority` を含む。
  - command は `--scope` / `--target` から canonical target path を解決してよいが、raw artifact content だけから upstream approval を推定してはならない。
  - command は referenced promotion / reviewer evidence path と `input_authority` を照合し、一致しない場合は blocked result を返し、profile/probe を生成しない。
  - `input_authority.*.reviewer_evidence_path` は必須。helper は reviewer verdict/hash の自己申告を信用せず、promotion record と reviewer evidence の双方を読む。
  - command は generated manifest path、Permission Profile fragment path、probe plan path、diff gate plan、blocked reason を返す。
- Delegated write-session invocation:
  - helper は generated artifacts と同じ task directory に `session-invocation.toml` を生成する。
  - `session-invocation.toml` は actual author session で使う supported invocation contract を持つ。最低 fields は `executor`, `host_surface`, `role`, `scope_id`, `target_artifact_path`, `manifest_path`, `manifest_hash`, `permission_profile_name`, `permission_profile_hash`, `config_overrides`, `default_permissions`, `positive_probe_id`, `positive_probe_target`, `negative_probe_plan_path`, `diff_gate_plan_path`, `acceptance_counted`。
  - CLI-first verified path では `executor = "codex-cli"`、`host_surface = "cli"`、`default_permissions = <permission_profile_name>`、`config_overrides` に task-specific Permission Profile と old sandbox settings absence を記録する。
  - actual write session は generated profile を `default_permissions` として選んだ invocation だけを supported とする。manual edit、unprofiled sub-agent edit、static broad profile edit、Desktop fallback は `acceptance_counted=false`。
  - delegated draft artifact metadata は `manifest_hash`、`permission_profile_name`、`permission_profile_hash`、`write_session_invocation_hash`、`probe_run_id`、`positive_probe_result` を持ち、`positive_probe_result=pass` と一致しなければ incomplete / blocked とする。
  - S07 / dogfooding acceptance は、metadata だけではなく design body または frontmatter に対する non-metadata draft delta と、manifest / session invocation / positive-negative probe evidence の組を要求する。metadata-only edit は fallback evidence であり、S07 acceptance としては incomplete と扱う。
- Generated artifacts:
  - `discussions/delegated-authoring/<task-id>/manifest.toml`
  - `discussions/delegated-authoring/<task-id>/permission-profile.toml`
  - `discussions/delegated-authoring/<task-id>/probe-plan.md`
  - `discussions/delegated-authoring/<task-id>/session-invocation.toml`

配置案:

- domain: `domain/delegated_authoring.py`
  - dataclass / validation / result reason。
- application: `application/delegated_authoring.py`
  - manifest assembly use case。
- commands: `commands/delegated_authoring.py`
- CLI registry: `cli/registry.py`
  - CLI command adapter。
- presentation: 必要なら JSON / markdown rendering。
- tests: `tests/domain_runtime/test_delegated_authoring.py` または existing domain/runtime tests。

### D-002 Adapter は static fallback + success-path contract

Codex agent adapter は task-specific dynamic path を直接持たない。adapter は次を持つ。

- role identity。
- canonical role skill reference。
- default fallback profile。
- no old sandbox settings。
- verified manifest/profile/probe 成功時の exact target write success path。
- failure 時 proposal-only fallback。

これにより static TOML の broad write 化を避ける。

### D-003 Non-destructive negative probe

negative probe は real artifact へ書こうとしない。forbidden boundary category ごとに disposable sentinel path を使う。

例:

- forbidden `src`: `src/.spec-dock-permission-probe-denied`
- forbidden `tests`: `tests/.spec-dock-permission-probe-denied`
- forbidden `requirement.md`: same directory の dedicated denied sentinel。ただし real `requirement.md` は触らない。
- forbidden peer artifact: same directory の dedicated denied sentinel。ただし target ではない `design.md` / `plan.md` は触らない。
- forbidden `report.md`: same directory の dedicated denied sentinel。ただし real `report.md` は触らない。
- forbidden `.codex`: `.codex/.spec-dock-permission-probe-denied`
- forbidden `.agents`: `.agents/.spec-dock-permission-probe-denied`
- `.env*`: real `.env` ではなく `.env.spec-dock-permission-probe-denied` を使う。

sentinel が作成された場合は fail-open とし、cleanup evidence と dirty diff abort を report に残す。

### D-004 Runtime authority gate

artifact-level validator は `design.md` / `plan.md` metadata を読む。最低 fields:

- `status`
- `authority`
- `grants`
- `owner_role`
- `draft_author_role`
- `approval`
- `source_revision`
- `approved_revision`
- `approved_hash`
- `manifest_hash`
- `permission_profile_name`
- `permission_profile_hash`
- `write_session_invocation_hash`
- `probe_run_id`
- `positive_probe_result`

`authority: proposed` は review / planning input まで。implementation / issue ready / issue finish / phase completion は `authority: approved`、required grants、promotion record、fresh reviewer pass を要求する。

approved delegated artifact metadata は `positive_probe_result=pass` を要求する。欠落時は `incomplete_draft_metadata`、pass 以外は `positive_probe_not_passed`。

runtime authority gate は artifact metadata だけで完結しない。scope-local `report.md` の Evidence Adoption Ledger を読み、対象 artifact に紐づく unresolved `blocked` / `stale` entry がある場合は、次の操作を fail-closed で拒否する。

- `spec-dock validate`
- active context-pack rendering / context-pack inclusion for implementation or finish purpose
- draft promotion
- implementation start
- issue ready
- issue finish
- phase completion

拒否 result は blocked ledger entry ID、target artifact、required next action を含める。これにより、EAL が単なる観測証跡ではなく downstream authority gate の入力になる。

### D-005 Evidence Adoption Ledger 正本

candidate evidence は `discussions/delegated-authoring/<task-id>/...` に置けるが、正本の採否は scope-local `report.md` の Evidence Adoption Ledger に統合する。

ledger entry は `adopted` / `rejected` / `blocked` / `stale` を持つ。`blocked` / `stale` は解消されるまで runtime authority gate の blocking input として扱い、promotion / implementation start / issue ready / issue finish / phase completion の acceptance を満たさない。

### D-006 Depth=2

`agents.max_depth = 2` を provider / dogfooding config へ反映する。ただし許可する child は leaf-only evidence producer だけ。

allowed:

- `repo-analyst`
- `researcher`
- `consultant`
- `deep-consultant`
- advisory `spec-reviewer`

forbidden:

- depth=3
- `dev-coder` child
- peer author child
- canonical edit
- final reviewer pass claim

## 影響ファイル

```text
src/spec_dock/assets/install_root/.codex/config.toml
src/spec_dock/assets/install_root/.codex/agents/system-architect.toml
src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml
src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md
src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
src/spec_dock/assets/spec_dock/docs/phase_design.md
src/spec_dock/assets/spec_dock/docs/phase_plan.md
src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md
src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md
src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
tests/test_init_update.py
tests/domain_runtime/test_authority.py
tests/domain_runtime/test_delegated_authoring.py
tests/cli_runtime/test_issue_lifecycle.py
```

Dogfooding mirrors under `.codex/`, `.agents/`, `spec-dock/docs/`, `spec-dock/templates/`, and `spec-dock/system/active-none/` are validation surface and must be refreshed or intentionally matched.

## 要件 → 設計マッピング

- AC-001 -> D-001
- AC-002 -> D-001, D-004
- AC-003 -> D-002
- AC-004 -> D-006
- AC-005 -> D-003
- AC-006 -> D-004
- AC-007 -> D-004
- AC-008 -> D-005 and docs/templates
- AC-009 -> D-001..D-006 dogfooding pilot
- AC-010 -> final gate

## テスト戦略

- Domain unit:
  - manifest schema。
  - `input_authority` validation。
  - non-destructive negative probe plan。
  - artifact metadata validation。
- Managed asset:
  - adapter/config/skill/docs/template strings and TOML parsing。
  - no sandbox mixing。
  - `max_depth = 2` and child constraints。
- Runtime integration:
  - proposed artifact blocks issue finish / implementation purpose context。
- Dogfooding:
  - actual draft write evidence。
  - forbidden path diff gate。
  - `spec-dock validate`。
- Review:
  - fresh spec-reviewer / code-reviewer / qa-reviewer as appropriate。

## リスク / ロールバック

- Permission Profile exact file write が host で enforce できない:
  - proposal-only fallback。limited directory candidate draft は acceptance に数えない。
- Desktop App divergent:
  - Desktop path は `acceptance_counted=false`。
  - `--host-surface desktop` は manifest inspection / manual fallback までに限定し、CLI と同等の positive/negative probe が verified になるまで AC-009 / Epic acceptance へ算入しない。
- runtime authority gate が incomplete:
  - write-scoped canonical authoring を有効化しない。
- unexpected sentinel created:
  - cleanup evidence、dirty diff abort、report incident。

## 未確定事項

- なし。CLI injection の具体方式が実装中に成立しない場合は plan amendment と fresh spec-review を行う。

## Delegated Draft Pilot Metadata

- status=approved
- authority=approved
- owner_role=main-orchestrator
- draft_author_role=system-architect
- approval=fresh-reviewer-pass-main-promotion
- grants=review_input,planning_input,implementation_start,issue_ready,issue_finish,phase_completion
- source_revision=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- approved_revision=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- approved_hash=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- manifest_hash=898427a15c869b7fce26aee647c4537b1ed4f0dda98e9931d6f67b4ed530e9ab
- permission_profile_name=spec-dock-iss-00126-system-architect-design-cli-85455ab6a889
- permission_profile_hash=e4c7fa0f464ac3556cf7e0df8861b25e87c312a449f124f9a18d1b0f44accbdf
- write_session_invocation_hash=1659b5cbca0fbdf93d6328fe6b94925d08801b7bb61c306208f9f9bc7aed23f1
- probe_run_id=iss-00126-system-architect-design-cli-85455ab6a889-positive
- positive_probe_result=pass
- acceptance_counted=true
- stale_check=fresh
- promotion_record.status=approved
- promotion_record.authority=approved
- promotion_record.source_revision=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- promotion_record.approved_revision=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- promotion_record.approved_hash=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- promotion_record.reviewer_target_hash=3703cddbe1b119572b82b2c0a921db21dd4029732c00b0cc9a4d28e03e21576d
- promotion_record.promotion_decision=main_orchestrator_promotion_after_fresh_review
