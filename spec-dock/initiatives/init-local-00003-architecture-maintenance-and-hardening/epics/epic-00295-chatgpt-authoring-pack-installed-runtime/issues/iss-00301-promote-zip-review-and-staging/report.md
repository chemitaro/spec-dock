---
種別: 実装報告書（Issue）
ID: "iss-00301"
タイトル: "Zip Review Staging"
関連GitHub: ["#301"]
状態: "in-progress"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00301 Zip Review Staging — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | resolved | scope | orchestrator | ZIP/tree review と stage が canonical adoption と混同されるリスク | A: review/stage のみ実装; B: adoption まで含める | A を採用 | Epic requirement/design は ChatGPT output を evidence-only とし、adoption / approval / reviewer pass は後続 Issue の責務に分けている | promoted_to_design | `requirement.md`, `design.md` | none |
| D-002 | resolved | operation | orchestrator | tree fallback を ZIP review pass と同格に扱うか | A: 同格; B: lower authority fallback | B を採用 | ZIP central directory evidence がないため、安全証跡が弱い | promoted_to_design | `design.md#treefallbackreview` | none |
| D-003 | resolved | compatibility | spec-reviewer | Issue docs が metadata missing / source hash mismatch を `rejected` としており、親 Epic の `fail` / `stale` taxonomy と矛盾した | A: Issue 独自 status; B: parent Epic taxonomy に合わせる | B を採用 | Epic design が status taxonomy authority であり、downstream automation が status を読む | applied | spec-reviewer finding P1; `requirement.md`, `design.md`, `plan.md` | none |
| D-004 | resolved | test-strategy | spec-reviewer | implementation steps が executable step schema を満たしていない | A: global plan のまま; B: S01-S07 に step-local contract を追加 | B を採用 | Standard Issue の worker/reviewer が fixture、Red/Green、report destination を判断せず実行できる必要がある | applied | spec-reviewer finding P1; `plan.md` | none |
| D-005 | resolved | test-strategy | spec-reviewer | unsafe stage target の期待 status が `rejected or blocked` と曖昧だった | A: 複数 status を許容; B: unsafe stage target は `rejected` に統一 | B を採用 | deterministic diagnostics を守り、requirement/design の stage target rejection と一致させる | applied | spec-reviewer P2; `plan.md` tc-s05-003 | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| EAL-001 | adopted | draft-requirement | `requirement.md` | Scope、non-scope、acceptance seeds を正式要件へ統合した | `artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md` | spec-review |
| EAL-002 | adopted | draft-design | `design.md` | Target paths、failure modes、stage boundary を正式設計へ統合した | `artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md` | spec-review |
| EAL-003 | adopted | draft-plan | `plan.md` | Step sequence、verification seeds、relay policy を正式計画へ統合した | `artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md` | spec-review |
| EAL-004 | adopted | assurance-classify-compose | `.assurance.json` and docs | `assurance classify` で `standard` が確定し、`assurance compose` で設計・計画・report scaffold を生成した | `./spec-dock/scripts/spec-dock assurance classify --stage requirement`; `./spec-dock/scripts/spec-dock assurance compose --artifact all` | assurance verify |
| EAL-005 | adopted | implementation | provider runtime `authoring pack review/stage` | ZIP/tree review、status taxonomy、host-local path rejection、authority scan、safe stage output を runtime command として昇格した | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 171 passed | code/qa/spec re-review |
| EAL-006 | adopted | implementation | dogfood runtime mirror | provider-side runtime modules を `spec-dock/scripts/spec_dock_runtime/**` に反映し、installed path smoke で review/stage を検証した | `test_authoring_pack_dogfood_runtime_path_rejects_pr_delivery_claim_and_preserves_stage_text_boundary` included in 171 passed | code/qa/spec re-review |
| EAL-007 | adopted | implementation | compatibility scripts | `review_chatgpt_authoring_pack.py` / `stage_chatgpt_authoring_pack.py` を runtime application/presentation へ委譲する wrapper に変更し、provider と dogfood mirror の parity smoke を追加した | `test_authoring_pack_compatibility_scripts_delegate_to_runtime_contract`; legacy review-report stale/pass/output-dir/review-to-stage/encrypted fixtures included in 171 passed | code/qa/spec re-review |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
| --- | --- | --- | --- | --- |
| OAL-001 | `authoring pack review/stage` を安全検査・staging command として実装する | canonical adoption / approval / PR delivery は non-scope として後続 Issue へ分離 | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
| --- | --- | --- | --- | --- | --- | --- |
| requirement | Epic requirement/design/plan、Issue draft requirement、existing authoring command/tests | none | adopted into `requirement.md` | pass | no | promote |
| design | Issue requirement、Issue draft design、existing command and prompt pack contract | none | adopted into `design.md` | pass | no | promote |
| plan | Issue requirement/design、Issue draft plan、verification queue | none | adopted into `plan.md` | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft requirement path | `requirement.md` | adopted | [`requirement.md`] | pass: manual diff guard confirmed no unsupported adoption/reviewer/PR-ready self-claim was promoted | integrated | none | none | pass | promote |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft design path | `design.md` | adopted | [`design.md`] | pass: manual diff guard confirmed design boundaries remain evidence-only and non-scope commands are not promoted | integrated | none | none | pass | promote |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft plan path | `plan.md` | adopted | [`plan.md`] | pass: manual diff guard confirmed relay/no-per-Issue-PR policy remains deferred to `iss-00307` | integrated | none | none | pass | promote |

## 実装記録（セッションログ）

### セッションログ（2026-07-08 planning）

#### 対象

- Step: Planning adoption
- AC/EC: AC-001..AC-015

#### 実施内容

- Active issue `iss-00301` の scaffold requirement / placeholder design / placeholder plan を確認した。
- Issue-local draft requirement/design/plan を読み、Epic requirement/design/plan と照合した。
- `requirement.md` を正式要件として作成した。
- `assurance classify --stage requirement` を実行し、`authorized_profile=standard` を確認した。
- `assurance compose --artifact all` を実行し、Standard profile の設計・計画・report scaffold を生成した。
- `design.md` と `plan.md` を正式版へ置き換えた。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# state: requirement-capture; reason_code: requirement-scaffold

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok
# authorized_profile: standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# assurance compose: ok
# changed_paths: design.md, plan.md, report.md
```

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable / host conflict reason | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user request to continue SpecDock workflow | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00301 | current session | spec-reviewer / code-reviewer / qa-reviewer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility | issue complete / session end / scope change / user revocation | none | continue |

## 実装委任ゲート（Implementation Delegation Gate）

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01-S07 | pending | runtime command / shipped scaffold / tests | dev-coder or parent exception | authoring pack review/stage implementation | `requirement.md`, `design.md`, `plan.md` | plan change surface | non-scope adoption / PR / `.assurance.json` mutation | focused pytest, CLI smoke, validate, assurance verify | unresolved spec-review finding | worker summary / changed files / verification | pending |
| S01-S07 | parent-exception | runtime command / shipped scaffold / tests | orchestrator direct implementation | authoring pack review/stage implementation | `requirement.md`, `design.md`, `plan.md` | provider runtime, dogfood runtime mirror, focused tests | non-scope adoption / PR / `.assurance.json` mutation | focused pytest, CLI smoke, validate, assurance verify | unresolved reviewer finding | this report ledger | pass: implementation completed and local verification passed |

### セッションログ（2026-07-08 implementation）

#### 対象

- Steps: S01-S07
- AC/EC: AC-001..AC-015

#### Parent Implementation Exception

- 通常は runtime / tests / scaffold behavior を `dev-coder` に委任する。
- このセッションでは、既に Red tests と runtime module scaffold が作成途中であり、差分が active worktree に存在していた。
- 追加の委任よりも、現在の approved plan に沿って未完了差分を閉じ、focused tests と dogfood mirror smoke まで一気に完了させる方が証跡の連続性を保てるため、parent exception として orchestrator が直接実装した。
- 範囲は `authoring pack review/stage` runtime command、provider-side shipped runtime、dogfood mirror、focused tests に限定した。

#### 実施内容

- `authoring pack review` を deferred command から実装済み command に昇格し、`--input` / `--format` / `--evidence-mode` / `--report-path` を公開した。
- `authoring pack stage` を deferred command から実装済み command に昇格し、`--input` / `--stage-dir` / `--format` / `--dry-run` を公開した。
- ZIP / tree input の evidence-only review contract を追加し、`authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を保持した。
- `wrong_root=rejected`、`missing_metadata=fail`、`source_hash_mismatch=stale` の status taxonomy を実装した。
- unsafe ZIP path / forbidden authority claim / tree fallback lower authority / unsafe stage target を focused tests で固定した。
- stage output は canonical docs を直接変更せず、`review-report.json`、`dry-run-diff.md`、`adoption/eal-candidates.json`、`.specdock-stage-owner.json` を stage dir に生成する形にした。
- provider-side runtime modules を dogfood `spec-dock/scripts/spec_dock_runtime/**` に反映し、dogfood runtime path で review/stage smoke を追加した。

#### 実行コマンド / 結果

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "pack_review or pack_stage or compatibility_stage" --tb=short
# 61 passed, 76 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "pack_review or pack_stage or compatibility_review or compatibility_stage" --tb=short
# 68 passed, 76 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "compatibility_review or compatibility_stage or local_context_evidence or pack_stage" --tb=short
# 17 passed, 131 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "compatibility_review or compatibility_stage" --tb=short
# 11 passed, 143 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "symlink_ancestor or symlink_parent or secret_and_raw_transcript_payloads or pack_stage or tree_fallback_rejects_unsafe_file_categories" --tb=short
# 24 passed, 135 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "secret-path or file_stage_target or rejected_oversized_zip or reviews_input_before_legacy_digest or unsafe_zip_entry_categories or compatibility_review or compatibility_stage" --tb=short
# 21 passed, 143 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "constraint_text or symlink_ancestor or external_report_path or external_stage_target or pack_stage" --tb=short
# 16 passed, 151 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "constraint_text or sensitive_constraint_text" --tb=short
# 2 passed, 166 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "sensitive_constraint_text or secret_and_raw_transcript_payloads" --tb=short
# 8 passed, 160 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "compatibility_stage" --tb=short
# 3 passed, 135 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q
# 168 passed

uv run pytest tests/cli_runtime/test_authoring.py -q -k "relative_canonical or sensitive_constraint_text" --tb=short
# 3 passed, 167 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "redacts_sensitive_findings or relative_canonical or sensitive_constraint_text" --tb=short
# 4 passed, 167 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q -k "unsafe_report_path or unsafe_stage_target or relative_canonical or sensitive_constraint_text or redacts_sensitive_findings or secret_and_raw_transcript_payloads" --tb=short
# 13 passed, 158 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q
# 171 passed

uv run pytest tests/unit/infra/test_init_update.py -q -k "authoring_pack or authoring-pack or authoring"
# 2 passed, 543 deselected

./spec-dock/scripts/spec-dock authoring pack review --help
# exit 0; --input / --format / --evidence-mode / --report-path exposed

./spec-dock/scripts/spec-dock authoring pack stage --help
# exit 0; --input / --stage-dir / --format / --dry-run exposed

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=202

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok; issue=iss-00301; authorized_profile=standard

git diff --check
# exit 0
```

#### 未完了ゲート

- fresh `code-reviewer` pass: re-review pending after P1 fixes
- fresh `qa-reviewer` pass: re-review pending after P1/P2 fixes
- final `spec-reviewer` alignment pass: re-review pending after P1 fixes
- commit / push / issue finish: pending

### レビュー指摘対応ログ（2026-07-08 implementation rework）

| reviewer | initial status | finding | fix | verification | re-review |
| --- | --- | --- | --- | --- | --- |
| qa-reviewer | fail | unsafe ZIP negative fixtures が path traversal のみ | absolute / host-local / hidden / unsupported suffix / oversized / encrypted / symlink / binary / nested archive fixtures を追加 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 105 passed | pending |
| qa-reviewer | fail | secret / token / private key / raw transcript と manifest authority boundary の scanner coverage 不足 | scanner negative tests と invalid manifest authority/adoption/bundle tests を追加 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 105 passed | pending |
| qa-reviewer | fail | compatibility scripts の runtime contract parity が未検証 | provider / dogfood の `review_chatgpt_authoring_pack.py` と `stage_chatgpt_authoring_pack.py` を runtime wrapper 化し parity smoke を追加 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 105 passed | pending |
| qa-reviewer | fail | canonical no-mutation snapshot が `requirement.md` のみ | active initiative / epic / issue の requirement/design/plan と `.assurance.json` の snapshot guard に拡張 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 105 passed | pending |
| spec-reviewer | fail | host-local path rejection が runtime reviewer にない | `Users` / `home` / `Volumes` / `private` / `.oracle` / `.ssh` marker を `host_local_path` として rejected に分類 | `test_authoring_pack_review_rejects_unsafe_zip_entry_categories` -> pass | pending |
| spec-reviewer | fail | compatibility scripts が legacy contract のまま | runtime application/presentation へ委譲する wrapper に置換し、legacy hidden args は compatibility input として扱う | provider / dogfood compatibility script smoke -> pass | pending |
| code-reviewer | fail | encrypted entry が `archive.read()` で crash しうる | encrypted / symlink entry は payload read を skip し deterministic `encrypted_entry:*` finding を返す | encrypted CLI fixture -> pass | pending |
| code-reviewer | fail | owned stage dir 内 symlink descendant に書ける | existing stage dir 内 symlink descendant を `unsafe_stage_target:symlink_descendant` として reject | symlink descendant stage fixture -> pass | pending |
| spec-reviewer | pass with P2 | staged tree creation assertion が弱い | valid stage test で `specdock-authoring-pack/manifest.json` と `payload["staged_files"]` を検証 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 107 passed | pending |
| qa-reviewer | fail | direct canonical issue path under `spec-dock/initiatives/**` への stage target が未検査 | `spec-dock/initiatives/**` を `unsafe_stage_target:canonical-docs` として reject し、direct canonical issue target test を追加 | `test_authoring_pack_stage_rejects_direct_canonical_issue_target` -> pass | pending |
| code-reviewer | fail | tree fallback の file symlink が通常ファイル扱いになり外部 content を取り込みうる | tree review の走査を symlink-aware にし、`symlink_entry:*` として reject する fixture を追加 | `test_authoring_pack_review_tree_fallback_rejects_symlink_file` -> pass | pending |
| qa-reviewer | fail | `PR delivery` claim が forbidden authority claim として未検査 / 未拒否 | `authority_boundary.py` が `prompt_pack_contract.FORBIDDEN_AUTHORITY_CLAIMS` を取り込み、`PR delivery` fixture と dogfood mirror fixture を追加 | `test_authoring_pack_review_rejects_forbidden_authority_claim_contract`; dogfood PR delivery fixture -> pass | pending |
| qa-reviewer | fail | stage text output が review authority boundary を表示しない | `pack_stage_renderer.py` の text output に `review_authority` / `review_adoption_status` / `review_bundle_generation_not_promotion` などを追加 | `test_authoring_pack_stage_text_output_preserves_review_boundary_fields`; dogfood text fixture -> pass | pending |
| qa-reviewer | P2 | non-pass review input stage rejection test が不足 | rejected pack を `stage` に渡し、`review_not_pass` と staged tree 未作成を検証 | `test_authoring_pack_stage_rejects_non_pass_review_input_without_staging_tree` -> pass | pending |
| spec-reviewer | fail | tree fallback が unsupported suffix / binary / nested / oversized を検査せず stage しうる | tree entry に `_validate_tree_entry` を適用し、unsupported / binary / nested / oversized fixtures を追加 | `test_authoring_pack_review_tree_fallback_rejects_unsafe_file_categories` -> pass | pending |
| spec-reviewer | fail | required JSON metadata の一部だけを parse していた | `REQUIRED_METADATA` の JSON ファイル全件を parse し、invalid JSON を `fail` に分類する fixtures を追加 | `test_authoring_pack_review_fails_for_invalid_required_json_metadata` -> pass | pending |
| spec-reviewer | fail | `--report-path` が active/canonical/assurance/symlink parent に書ける | report path に canonical docs / `.assurance.json` / symlink guard を追加し unsafe path fixture を追加 | `test_authoring_pack_review_rejects_unsafe_report_path` -> pass | pending |
| spec-reviewer | P2 | stale と rejected finding が併存すると stale が優先される | rejected-class finding を source hash mismatch より優先する status precedence に変更 | `test_authoring_pack_review_rejected_findings_take_precedence_over_stale` -> pass | pending |
| code-reviewer | P2 | owned stage dir 再利用時に stale staged files が残る | owned stage dir は marker を残して既存 content を削除してから copy する | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 144 passed | pending |
| code-reviewer | P2 | legacy wrapper invocation の default stdout が text へ変わる | legacy args 使用時は明示 `--format` なしでも JSON stdout を維持する | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 144 passed | pending |
| qa-reviewer | P2 | `.assurance.json` stage target の focused regression がない | `.assurance.json` stage target rejection fixture を追加 | `test_authoring_pack_stage_rejects_assurance_target` -> pass | pending |
| spec-reviewer | P2 | `.specdock-stage-owner.json` の provenance fields が不足 | marker に `created_at`、`input_path`、`input_sha256`、`input_kind`、`issue_id`、authority boundary を記録し test assertion を追加 | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 144 passed | pending |
| code-reviewer | P1 | malformed owned marker の stage dir を cleanup してから拒否する可能性 | owner marker を authority / adoption_status / bundle_generation_not_promotion / created_at / input_path / input_kind まで検証してから cleanup し、invalid marker では user file を保持する | `test_authoring_pack_stage_rejects_malformed_owned_marker_without_cleanup` included in 144 passed | pending |
| code-reviewer | P1 | legacy `--review-report` が pass なら別 tree も stage できる | legacy report の `pack_digest.content_sha256` と pack tree digest を照合し、mismatch は `stale` として拒否、matching pass は受理する fixtures を追加 | `test_authoring_pack_compatibility_stage_rejects_stale_legacy_review_report`; `test_authoring_pack_compatibility_stage_accepts_matching_legacy_review_report` -> pass | pending |
| code-reviewer | P2 | symlinked tree input root が fallback review で通常 directory 扱いになる | input path 自体と root `specdock-authoring-pack` の symlink を `symlink_input_root` / `symlink_entry:specdock-authoring-pack` として reject | `test_authoring_pack_review_rejects_symlinked_tree_input_root` included in 144 passed | pending |
| qa-reviewer | P1 | staged evidence が static placeholder でも tests が通る | `dry-run-diff.md` に staged pack の相対パス・hash・preview を出し、`adoption/eal-candidates.json` を pack 由来にし、content-sensitive fixture で検証 | `test_authoring_pack_stage_valid_zip_writes_stage_outputs_and_preserves_canonical_docs`; focused 68 passed | pending |
| code-reviewer | P1 | prepare が生成する manifest に `source_manifest_hash` がなく valid pack が `stale` になる | review freshness を `source-manifest.json` と `stale-if.json` の `source_manifest_hash_changes` / legacy `source_manifest_hash` で照合するよう修正 | `test_authoring_pack_review_accepts_prepare_contract_without_manifest_source_hash`; focused 68 passed | pending |
| spec-reviewer | P1 | executable ZIP/tree entries が review pass しうる | ZIP external mode と tree stat mode の executable bit を `executable_entry:*` として reject し、ZIP/tree 両方の negative fixture を追加 | `test_authoring_pack_review_rejects_executable_zip_entry`; `test_authoring_pack_review_tree_fallback_rejects_executable_file`; focused 68 passed | pending |
| spec-reviewer | P2 | `--evidence-mode local-context` が review report に残らない | `PackReviewResult` に `evidence_mode` を追加し、review output/report に保持する fixture を追加 | `test_authoring_pack_review_report_preserves_local_context_evidence_mode`; focused 68 passed | pending |
| qa-reviewer | P2 | `--dry-run` stage branch の regression coverage がない | dry-run stage で stage dir が作成されず、`dry_run=true` と synthetic staged files、canonical snapshot preservation を検証 | `test_authoring_pack_stage_dry_run_does_not_write_stage_outputs`; focused 17 passed | pending |
| code-reviewer | P1 | legacy review wrapper が書いた `validation-report.json` を stage wrapper が digest 不足で拒否する | review wrapper の legacy `--output-dir` report に `pack_digest.content_sha256` を記録し、stage wrapper は ZIP/tree 共通 digest で stale 判定する | `test_authoring_pack_compatibility_legacy_review_report_can_stage_same_tree`; focused 17 passed | pending |
| spec-reviewer | P2 | text review output が `evidence_mode` を表示しない | text renderer に `evidence_mode` を追加し、default text path の local-context 出力を検証 | `test_authoring_pack_review_text_preserves_local_context_evidence_mode`; focused 17 passed | pending |
| spec-reviewer | P1 | legacy `--output-dir` が runtime report path guard を迂回する | legacy output-dir report も `_unsafe_report_path` で検査し、canonical / symlink parent を拒否する fixtures を追加 | `test_authoring_pack_compatibility_review_rejects_unsafe_legacy_output_dir`; `test_authoring_pack_compatibility_review_rejects_symlink_legacy_output_dir`; focused 11 passed | pending |
| code-reviewer | P1 | encrypted ZIP を legacy digest が `archive.read()` して traceback しうる | review/stage wrapper の legacy digest helper で `RuntimeError` を deterministic `None` として扱い、rejected/stale 経路へ流す | `test_authoring_pack_compatibility_review_handles_encrypted_zip_without_traceback`; `test_authoring_pack_compatibility_stage_handles_encrypted_zip_digest_without_traceback`; focused 11 passed | pending |
| spec-reviewer | P1 | report/stage guard が nested symlink ancestor を見落とす | repo 配下の symlink ancestor を path / resolved path の両方で検査し、macOS temp root symlink は誤検知しない形に修正 | `test_authoring_pack_review_rejects_nested_symlink_ancestor_report_path`; `test_authoring_pack_stage_rejects_nested_symlink_ancestor_stage_target`; focused 24 passed | pending |
| code-reviewer | P1 | structured JSON/YAML token / secret fields が scanner を通過する | `token:`, `"token":`, `secret:`, `api_key:` などの structured secret fields を検出し、長文 payload では keyword precheck で regex cost を抑制 | `test_authoring_pack_review_rejects_secret_and_raw_transcript_payloads`; focused 24 passed | pending |
| spec-reviewer | P1 | secret-looking path entries が Epic contract と未整合 | path parts に `secret` / `secrets` / `token` / `credential` / `password` / `api_key` 系が含まれる場合を `secret_path:*` として reject | `test_authoring_pack_review_rejects_unsafe_zip_entry_categories`; focused 21 passed | pending |
| spec-reviewer | P1 | tree fallback の status が Epic と Issue で矛盾 | Epic design の failure mode を `pass` with `fallback=true` and lower authority に修正し、stageable evidence-only fallback と明記 | Epic design updated; existing tree fallback tests included in focused/full authoring suite | pending |
| code-reviewer | P1 | rejected legacy ZIP でも digest が unsafe entry を読む | legacy review wrapper は result.status が `pass` の場合だけ digest を計算し、rejected report は `pack_digest.content_sha256=null` にする | `test_authoring_pack_compatibility_review_skips_digest_for_rejected_oversized_zip`; focused 21 passed | pending |
| code-reviewer | P1 | legacy stage digest が bounded review 前に stale malicious ZIP を読む | legacy stage gate は `review_pack_input(input_path).status == pass` を確認してから digest を計算する | `test_authoring_pack_compatibility_stage_reviews_input_before_legacy_digest`; focused 21 passed | pending |
| code-reviewer | P2 | existing file stage target が structured JSON で reject されない | `stage_dir.exists() and not is_dir()` を `unsafe_stage_target:not_directory` として reject | `test_authoring_pack_stage_rejects_file_stage_target`; focused 21 passed | pending |
| code-reviewer | P1 | constraint file が forbidden claim と誤判定される | `safe-output-constraints.md` / prompt / expected-output contract を achieved claim scan 対象外にし、candidate payload scanning と分離 | `test_authoring_pack_review_does_not_treat_constraint_text_as_authority_claim`; focused 16 passed | pending |
| code-reviewer | P1 | repo 外 symlink stage target が許可される | report/stage target guard は cwd 到達までの symlink ancestor を拒否し、repo 配下 symlink が外部へ向く場合も block | `test_authoring_pack_review_rejects_symlink_ancestor_to_external_report_path`; `test_authoring_pack_stage_rejects_symlink_ancestor_to_external_stage_target`; focused 16 passed | pending |
| code-reviewer | P1 | constraint file 除外が secret/raw transcript scan まで迂回する | achieved authority claim scan と sensitive payload scan を分離し、constraint files でも token/raw transcript は reject | `test_authoring_pack_review_rejects_sensitive_constraint_text`; focused 2 passed | pending |
| code-reviewer | P1 | constraint file の spaced `api key:` field が secret scan を通過する | structured secret regex を `api key:` / `api_key:` / `api-key:` に対応し、constraint file の concrete API key leak を reject | `test_authoring_pack_review_rejects_sensitive_constraint_text`; focused 8 passed | pending |
| code-reviewer | P1 | constraint policy text の `api key:` label without value が secret と誤判定される | structured secret scanner が値を capture し、constraint-sensitive scan では secret-like value がある場合だけ reject するように修正。policy-only `api key:` は許容し、concrete `api key: sk-live-example` は reject する | `uv run pytest tests/cli_runtime/test_authoring.py -q -k "constraint_text or sensitive_constraint_text or secret_and_raw_transcript_payloads" --tb=short` -> 9 passed; `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 168 passed | pending |
| code-reviewer | P1 | `spec-dock/` 配下 cwd から相対 report path を指定すると canonical guard を迂回できる | report path を `Path.cwd()` 基準の absolute / resolved parts で検査し、raw relative path に `spec-dock` component がなくても `spec-dock/active` / `spec-dock/initiatives` を reject する | `test_authoring_pack_review_rejects_relative_canonical_report_path_from_specdock_cwd`; focused 13 passed; full 171 passed | pending |
| code-reviewer | P1 | `spec-dock/` 配下 cwd から相対 stage target を指定すると canonical guard を迂回できる | stage target を `Path.cwd()` 基準の absolute / resolved parts で検査し、canonical / active docs 配下への staging を reject する | `test_authoring_pack_stage_rejects_relative_canonical_target_from_specdock_cwd`; focused 13 passed; full 171 passed | pending |
| code-reviewer | P1 | constraint file 内の concrete `private_key:` field が structured secret scan を通過する | structured secret scanner に `private_key` / `private-key` / `private key` field を追加し、constraint-sensitive scan でも secret-like value がある private key field を reject する | `test_authoring_pack_review_rejects_sensitive_constraint_text`; focused 13 passed; full 171 passed | pending |
| qa-reviewer | P2 | rejected secret/raw transcript pack の durable report redaction coverage がない | `--report-path` 付き rejected review で finding category は記録し、raw token/private key value/transcript body は report に残らない regression test を追加した | `test_authoring_pack_review_redacts_sensitive_findings_in_report_path`; focused 4 passed; full 171 passed | pending |

### Closure Coverage Map

| Closure ID | Plan-defined closure | Evidence |
| --- | --- | --- |
| CL-001 | `authoring pack review --help` implemented contract | `test_authoring_pack_review_help_exposes_implemented_contract` |
| CL-002 | `authoring pack stage --help` implemented contract | `test_authoring_pack_stage_help_exposes_implemented_contract` |
| CL-003 | valid ZIP review pass and evidence-only authority retained | `test_authoring_pack_review_valid_zip_passes_with_evidence_only_authority`; prepare-contract hash fixture |
| CL-004 | valid ZIP stage output includes report, dry-run diff, EAL candidate, owner marker | `test_authoring_pack_stage_valid_zip_writes_stage_outputs_and_preserves_canonical_docs`; dry-run no-write fixture |
| CL-005 | unsafe ZIP is rejected before extraction | path traversal fixture; encrypted / oversized / rejected legacy digest fixtures |
| CL-006 | unsafe entry categories are rejected | parameterized unsafe fixtures for host-local, hidden, secret path, unsupported suffix, binary, nested archive, executable, symlink, oversized, aggregate size |
| CL-007 | secret / raw transcript payloads are rejected | structured token / secret / API key fixtures, private key, credential, raw transcript fixtures |
| CL-008 | forbidden authority claims are rejected, not warnings | forbidden claim matrix, `PR delivery`, reviewer/ready/mergeable claim fixtures |
| CL-009 | wrong root=`rejected`, metadata missing=`fail`, source hash mismatch=`stale` | root metadata classification tests; invalid JSON metadata; rejected-over-stale precedence |
| CL-010 | tree fallback reports lower authority and missing central directory evidence | `test_authoring_pack_review_tree_fallback_reports_lower_authority`; unsafe tree fallback fixtures |
| CL-011 | stage does not change canonical docs / active docs / `.assurance.json` | protected SpecDock snapshot assertion; canonical/active/assurance stage target rejection |
| CL-012 | output distinguishes local validation from adoption/reviewer/ready claims | text/json report tests, review/stage boundary fields, evidence_mode text/json fixtures |
| CL-013 | provider and dogfood runtime smoke pass | dogfood runtime review/stage smoke; dogfood `PR delivery` rejection fixture |
| CL-014 | compatibility scripts have no hardcoded personal path and match runtime contract | provider/dogfood wrapper parity, legacy output-dir report, legacy review-to-stage digest, unsafe output-dir rejection, encrypted digest fixtures |
| CL-015 | no PR delivery; `iss-00307` defer evidence recorded | report scope notes; forbidden PR/mergeable claim rejection; no per-Issue PR created for `iss-00301` |

## レビューゲート状態（Reviewer Gate Status）

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| planning | spec authoring review | spec-reviewer | fresh | pass | no | promote | re-review resolved P1 blockers; P2 unsafe stage target status made deterministic |
| planning | spec authoring review | spec-reviewer | fresh first review | failed | no | re-review required | P1 executable step contract and status taxonomy findings fixed in docs; P2 draft provenance tightened |
| implementation | final code review | code-reviewer | fresh | pass | no | complete | P1 relative canonical report/stage guard and private key constraint scan findings resolved; no remaining blocking findings |
| implementation | final QA review | qa-reviewer | fresh | pass | no | complete | AC/CL coverage confirmed, including report redaction regression |
| implementation | final spec review | spec-reviewer | fresh | pass | no | complete | no remaining spec/doc inconsistency; only expected commit/push/finish bookkeeping remained |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
| --- | --- | --- | --- | --- | --- |
| `standard` | manual fallback | manual fallback | manual authoring fallback evidence: Epic docs、Issue draft artifacts、existing runtime/tests を orchestrator が照合して正式 docs へ採用 | pass | ready: final local gates passed; commit/push/finish pending |

## 最終品質ゲート（Final Quality Gate）

### ドキュメント影響の解消ステップ S90

| 対象 | 更新要否 | owner | evidence | spec-reviewer result |
| --- | --- | --- | --- | --- |
| runtime command docs / compatibility scripts | yes | orchestrator | Epic design amended to align tree fallback with `pass` + `fallback=true` + lower authority; compatibility scripts updated as shipped wrappers; no user-facing canonical adoption docs changed in this Issue | pass |

### 最終 QA ゲート

| reviewer | 範囲 | integration test decision | evidence | result |
| --- | --- | --- | --- | --- |
| qa-reviewer | issue-wide obligation coverage | provider/dogfood focused CLI runtime tests sufficient; no additional live integration required for non-network local command surface | `review_status: pass`; `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 171 passed; `uv run pytest tests/unit/infra/test_init_update.py -q -k "authoring_pack or authoring-pack or authoring"` -> 2 passed; `./spec-dock/scripts/spec-dock validate` -> ok; `./spec-dock/scripts/spec-dock assurance verify` -> ok | pass |

### 最終コードレビューゲート

| reviewer | 範囲 | findings / fixes | re-review count | result |
| --- | --- | --- | --- | --- |
| code-reviewer | issue-wide integrated diff | prior P1 findings resolved: relative canonical report/stage guard from `spec-dock/` cwd, structured private key fields in constraint-sensitive scan; QA P2 redaction coverage added | fresh re-review pass after fixes | pass |

### 最終 spec review ゲート

| reviewer | 範囲 | findings / fixes | re-review count | result |
| --- | --- | --- | --- | --- |
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | no remaining inconsistency for evidence-only authority, tree fallback lower authority, no per-Issue PR, no canonical adoption, or status taxonomy | fresh re-review pass after report/evidence update | pass |

### 最終 commit

| final report ledger | final commit scope | post-commit external evidence destination | result |
| --- | --- | --- | --- |
| final gate ledger complete; commit candidate ready | provider runtime, dogfood mirror, compatibility scripts, authoring CLI tests, Epic design amendment, Issue report | final response / later `iss-00307` PR | ready for commit, push, and `issue finish` |

## 省略/例外メモ

- この Issue では PR を作成しない。Epic 単位の PR は final quality gate Issue `iss-00307` で作成する。
