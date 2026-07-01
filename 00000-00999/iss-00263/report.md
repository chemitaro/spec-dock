---
種別: 実装報告書（Issue）
ID: "iss-00263"
タイトル: "New artifact command and new doc removal"
関連GitHub: ["#263"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00263 New artifact command and new doc removal — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | implementation | orchestrator | `new artifact` domain could be confused with existing `artifact_store.py` / `artifact_writer.py` derived/planning artifacts. | Reuse existing artifact infra; add clearly named scope-local artifact doc use case. | Use `CreateArtifactDoc*`, `application/create_artifact_doc.py`, and `domain/artifacts.py`; do not overload planning/derived artifact infra. | Keeps command-time scope-local docs separate from assurance compose and sync output writers. | promoted_to_design | `design.md` sections 3, 4, 13; system-architect `019f1cd6-59b5-78a0-9c54-e2f48e8a35bb` | none |
| D-002 | resolved | scope | spec-review planning | Non-Issue `draft-*` must fail closed, but legacy `new doc` supported initiative/epic draft templates. | Preserve old non-Issue draft behavior; enforce issue-only fail-closed. | Enforce future `new artifact draft-*` as issue-only; initiative/epic fail before setup/write. | Accepted Epic ADR and `iss-00262` rules made draft-* safety-sensitive issue-only routing. | promoted_to_design | `design.md` sections 7-9; `plan.md` S04 | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | system-architect `019f1cd6-59b5-78a0-9c54-e2f48e8a35bb` | design.md | Architecture proposal matched existing runtime layering and clarified artifact/doc domain split. | design.md; plan.md; active issue docs; runtime code inspection | none |
| EAL-002 | adopted | implementation-planner `019f1cd6-88f3-7e12-80e9-ddd9dfe6366f` | plan.md | Step order, test mapping, and reviewer gates matched requirement closure needs. | plan.md; design.md; active issue docs; runtime tests inspection | none |
| EAL-003 | adopted | spec-reviewer `019f1cde-98b4-7f53-a7c1-7055a41d4a69` and `019f1ce2-384c-7941-9cd7-7c611f16fd1f` | requirement.md, plan.md | Review found and then confirmed closure of the `draft-requirement` profile-preflight ambiguity. | requirement.md purpose/scope/AC; plan.md CLOS-263-005; reviewer outputs | none |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Design/plan prioritize runtime `new artifact` command and `new doc` removal. | Docs impact, old-node setup, and legacy discussions preservation are bounded to command-time needs. | low | pass by spec-reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Approved requirement, Epic ADR, `iss-00262` completed templates/rules, runtime `new doc` code/tests. | `draft-requirement` profile preflight wording was ambiguous; fixed to canonical issue requirement template only. | Existing approved requirement remains authoritative after wording clarification; reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f`. | pass | no | execute approved plan |
| design | Runtime parser/commands/application/domain/tests inspected; system-architect evidence adopted in EAL-001. | none | Rewrote design as approved candidate with module ownership, flow, no-write boundaries, and test strategy; reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f`. | pass | no | execute approved plan |
| plan | Requirement/design, implementation-planner evidence, existing CLI tests and command surface inspected. | `CLOS-263-005` clarified to split requirement template reuse from design/plan profile template reuse. | Rewrote plan as approved candidate with S01-S99 contracts, closure ids, test cases, and delegation gates; reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f`. | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| manual authoring | iss-00263 | none | active requirement/design/plan, Epic ADR, runtime code/tests, specialist read-only evidence | requirement.md, design.md, plan.md | not used | [] | manual authoring path | manual authoring canonical docs | none | none | pass | execute manual-authored canonical docs |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- `spec-dock new artifact <type>` の runtime command、artifact domain/application use case、CLI rendering、template routing、old-node `artifacts/` setup、draft assurance/profile preflight を実装した。
- `new doc` は parser / help / command registry / command-facing use case から削除し、shipped command-facing docs を `new artifact` / `artifacts/` 前提へ更新した。
- 既存 `discussions/` validation/helper は legacy preservation 境界として残し、validate/sync/ADR mirror の artifacts-aware 化は後続 Issue に残した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 issue execution）

#### 対象
- Step: S01, S02, S03, S04, S90, S99
- AC/EC: AC-263-001 through AC-263-007
- 計画上の出典（Planned source）:
  - `plan.md` sections S01 through S99
  - closure ids: CLOS-263-001 through CLOS-263-007

#### 実施内容
- `CreateArtifactDocRequest` / `CreateArtifactDocResult` / `UseCases.create_artifact_doc` を追加し、`application/create_artifact_doc.py` と `domain/artifacts.py` で scope-local artifact creation を実装した。
- `new artifact` parser/command/output を追加し、`new doc` command surface を削除した。
- Direct catalog、routing-only draft catalog、unsupported type、filename/id allocation、malformed candidate detection、old-node `artifacts/` setup、relative `rules.md` symlink、legacy `discussions/` non-interference を実装した。
- `draft-requirement` は issue requirement template、`draft-design` / `draft-plan` は verified authorized profile template へ routing した。
- Code review / QA review で発見された ambiguous blank slug no-write regression を修正し、profile draft no-write と full direct catalog assertions を補強した。
- S90 docs impact として direct command-facing shipped docs / dogfooding docs を `new artifact` へ更新し、phase/delegated authoring / legacy `discussions.md` rule migration は non-blocking follow-up として記録した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_new.py -k 'ambiguous_supported_type_slug'
# 1 passed

uv run pytest tests/cli_runtime/test_new.py -k 'profile_drafts_fail_closed or new_artifact_full_direct_catalog_success'
# 4 passed

uv run pytest tests/cli_runtime/test_new.py -k 'new_artifact or new_doc or draft or assurance'
# 19 passed

uv run pytest tests/cli_runtime
# 717 passed, 76 skipped

uv run pytest tests/unit/infra/test_artifact_templates.py tests/unit/cli/test_cli.py
# 9 passed

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=171

./spec-dock/scripts/spec-dock assurance verify --issue iss-00263
# assurance verify: ok ... authorized_profile: standard

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01/S02/S03/S04 | Red / alternative | red-required where practical | Implementation inspection showed only legacy `new doc` command-facing surface existed; `new artifact` domain/application/CLI was absent. | repo inspection; initial focused tests during dev-coder work | pass | Pre-implementation gap established for command/use-case/domain surface. |
| S03 | Red | regression for discovered no-write bug | `new artifact blank --title "Research Notes"` reproduced typed reclassification / unsafe success before fix. | dev-coder red run `uv run pytest tests/cli_runtime/test_new.py -k 'ambiguous_supported_type_slug'` -> fail | pass | Closed by pre-write ambiguous blank slug rejection. |
| S01/S02/S03/S04 | Green | focused CLI/runtime tests | `uv run pytest tests/cli_runtime/test_new.py -k 'new_artifact or new_doc or draft or assurance'` -> 19 passed. | command | pass | Covers command surface, draft safety, no-write, and removal regressions. |
| S03/S04 | Green | discovered coverage strengthening | `uv run pytest tests/cli_runtime/test_new.py -k 'profile_drafts_fail_closed or new_artifact_full_direct_catalog_success'` -> 4 passed. | command | pass | Strengthened no-setup and full catalog assertions. |
| S99 | Green | broad runtime lane | `uv run pytest tests/cli_runtime` -> 717 passed, 76 skipped. | command | pass | Full CLI runtime regression lane. |
| S90/S99 | Refactor / docs | docs and formatting guard | `git diff --check` -> pass; `./spec-dock/scripts/spec-dock validate` -> ok. | command | pass | No formatting or SpecDock validation failures. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S03 | `blank` artifact slug beginning with supported type prefix could be reclassified after write. | code-reviewer `019f1d10-d7f1-74b1-9a40-846bc62c2e41`; QA reviewer prior pass | Added pre-write rejection and regression test `test_new_artifact_blank_rejects_ambiguous_supported_type_slug_before_setup`. | CLOS-263-001 / CLOS-263-003 | no | `ambiguous_supported_type_slug` -> 1 passed after fix. |
| S04 | Profile draft failure tests did not detect `artifacts/` setup / `rules.md` side effect. | QA reviewer | Strengthened helper to snapshot artifact tree and assert absent setup for old-node failures. | CLOS-263-005 | no | `profile_drafts_fail_closed or new_artifact_full_direct_catalog_success` -> 4 passed. |
| S03 | Full direct catalog test did not assert every type's id/path/content/template routing. | QA reviewer | Made full catalog test table-driven for all direct types. | CLOS-263-003 | no | `profile_drafts_fail_closed or new_artifact_full_direct_catalog_success` -> 4 passed. |
| S90 | Broad phase/delegated authoring and legacy discussions rules still contain `new doc`. | docs inspection / doc-writer | Updated direct command-facing scripts/guide/reference/workflow docs; deferred deep delegated authoring and legacy `discussions.md` rule migration. | CLOS-263-004 | no | `rg -n "new doc|new_doc" ...` remaining hits are deferred legacy/delegated policy surfaces. |
| S90 | Normal workflow docs still listed `scratch` in current `new artifact` catalog. | QA reviewer `019f1d19-4977-78b1-a3b3-9689a86a5328` | Removed `scratch`, added `blank` / `decision-candidate`, and kept draft-* Issue-only in provider and dogfooding workflow docs. | CLOS-263-003 / CLOS-263-004 | no | workflow docs grep for `current catalog.*scratch`, `new artifact.*scratch`, and literal `scratch` -> no matches. |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | CLOS-263-001, CLOS-263-002, CLOS-263-003, CLOS-263-005 | Artifact domain/application contract exists with catalog, filename/id parsing, routing, and no-write preflight. | New `domain/artifacts.py`, `application/create_artifact_doc.py`, contracts/wiring; focused tests 19 passed. | pass | Existing `discussion_docs.py` retained for legacy validation. |
| S02 | CLOS-263-004 | `new artifact` parser/command/output exists; `new doc` command surface removed. | Parser/command/rendering diff; help/removal tests in focused lane; code-review pass. | pass | No alias/shim/custom migration hint. |
| S03 | CLOS-263-001, CLOS-263-002, CLOS-263-003, CLOS-263-007 | Direct creation, full catalog, old-node setup, malformed/collision/no-write guards. | Full catalog/old-node/malformed/ambiguous slug tests; `tests/cli_runtime` 717 passed. | pass | `discussions/` left untouched. |
| S04 | CLOS-263-005, CLOS-263-006 | Issue-only draft routing and profile fail-closed behavior. | Draft success/failure tests; profile no-write helper strengthened; focused lane 19 passed. | pass | Initiative/epic draft-* fail before setup/write. |
| S90 | CLOS-263-003, CLOS-263-004, CLOS-263-007 | Command-facing docs updated or explicitly deferred. | doc-writer updates to provider and dogfooding docs; workflow catalog `scratch` mismatch fixed; `rg` residual analysis; `git diff --check` pass. | pass | Deferred hits are legacy `discussions` rules and phase/delegated authoring policy migration. |
| S99 | CLOS-263-001 through CLOS-263-007 | Final checks and reviewer gates. | CLI runtime 717 passed; unit docs/template checks 9 passed; validate and assurance passed; code-review pass; QA/spec pending at this point. | pass | Final reviewer rows below carry gate status. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CLOS-263-001 | S01/S02/S03 | yes | CLI test | `new artifact` absent before implementation | `test_new_artifact_blank_issue_omits_blank_token_and_uses_artifacts_dir`; ambiguous slug regression | pass | Blank filename/id omits `blank`; ambiguous typed-prefix slug rejected no-write. |
| CLOS-263-002 | S01/S02/S03 | yes | CLI test | `new artifact` absent before implementation | `test_new_artifact_typed_epic_success_and_scope_shorthand` | pass | Typed artifact path/id under `artifacts/`. |
| CLOS-263-003 | S01/S03 | yes | CLI test | catalog absent before implementation | `test_new_artifact_full_direct_catalog_success`; unsupported/unknown/malformed tests | pass | Direct catalog covered; `scratch` / `note` unsupported. |
| CLOS-263-004 | S02/S90 | yes | CLI/docs test | `new doc` parser existed before implementation | `test_new_help_exposes_artifact_and_removes_doc_entrypoint`; docs grep/deferred analysis | pass | `new doc` fails argparse without custom migration hint. |
| CLOS-263-005 | S04 | yes | CLI test | profile drafts existed via legacy `new doc` | draft requirement/design/plan success and fail-closed tests | pass | `draft-requirement` uses issue requirement template; design/plan use authorized profile templates. |
| CLOS-263-006 | S04 | yes | CLI test | non-Issue draft behavior existed in legacy `new doc` | `test_new_artifact_draft_scope_failures_do_not_setup_artifacts` | pass | Initiative/epic draft-* fail before setup/write. |
| CLOS-263-007 | S03/S90 | yes | CLI/filesystem test | old-node setup path absent before implementation | `test_new_artifact_old_node_setup_preserves_discussions`; validate | pass | Creates `artifacts/` and relative `rules.md`; leaves `discussions/` untouched. |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-263-001 | S01/S02/S03 | focused tests, ambiguous slug regression | pass | AC-263-001 satisfied. |
| CLOS-263-002 | S01/S02/S03 | focused tests | pass | AC-263-002 satisfied. |
| CLOS-263-003 | S01/S03 | full catalog/unsupported/malformed tests | pass | AC-263-003 satisfied. |
| CLOS-263-004 | S02/S90 | help/removal test, docs updates | pass | AC-263-004 satisfied for command-facing surface. |
| CLOS-263-005 | S04 | draft success/fail-closed tests | pass | AC-263-005 satisfied. |
| CLOS-263-006 | S04 | unsupported draft scope tests | pass | AC-263-006 satisfied. |
| CLOS-263-007 | S03/S90 | old-node setup test and validate | pass | AC-263-007 satisfied. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | CLOS-263-001 / CLOS-263-003 | `test_new_artifact_blank_rejects_ambiguous_supported_type_slug_before_setup` | CLOS-263-001 / CLOS-263-003 | Code/QA review found ambiguous blank slug no-write gap. | no | yes, completed by code/QA re-review |
| changed | CLOS-263-003 | `test_new_artifact_full_direct_catalog_success` | CLOS-263-003 | QA requested stronger per-type assertions. | no | yes, completed by QA pass `019f1d20-2050-7461-8c44-c92d3a9aa07e` |
| changed | CLOS-263-005 | `_assert_profile_draft_no_write_failure` | CLOS-263-005 | QA requested artifact setup/no-write assertions. | no | yes, completed by QA pass `019f1d20-2050-7461-8c44-c92d3a9aa07e` |
| deferred | CLOS-263-004 | phase/delegated authoring docs residual grep | CLOS-263-004 | Broad delegated authoring / legacy discussions rule migration is outside this Issue's direct command-facing docs scope. | no | yes, final spec review |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/b4d4/spec-dock` | iss-00263 | current session | system-architect, implementation-planner, dev-coder, doc-writer, code-reviewer, qa-reviewer, spec-reviewer | same repo, active issue, named role; no destructive action / publishing / credentialed access / scope expansion | issue complete / session end / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S04 | delegated | runtime command/application/domain/test changes | dev-coder `019f1ce5-0737-74f0-839b-b8fde5c52d52` | source/tests for `new artifact` and `new doc` removal | requirement/design/plan | runtime source and tests | canonical docs/report, PR, broad docs | focused and full runtime tests | scaffold defaults / validate-sync semantic expansion | changed files, tests, closure coverage | pass |
| S03 fix | delegated | code-review P1 no-write regression | dev-coder `019f1d08-768f-7650-b24c-ca36f5106be7` | ambiguous blank slug fix and regression | code-review finding, plan no-write guard | `domain/artifacts.py`, `create_artifact_doc.py`, `tests/cli_runtime/test_new.py` | canonical docs/report | focused regression and diff check | grammar redesign beyond issue | changed files, red/green evidence | pass |
| S03/S04 test strengthening | delegated | QA P2 coverage findings | dev-coder `019f1d0c-e10a-7481-86cf-e475c968f139` | `tests/cli_runtime/test_new.py` only | QA findings | tests only | source/docs/report | focused tests and diff check | uncovered implementation bug | changed files, test evidence | pass |
| S90 | delegated | persistent docs outside orchestrator direct-edit boundary | doc-writer `019f1d10-addc-7c70-ba87-c37ed61a1df4`, `019f1d16-1863-7791-ba78-ef26292be9ef`, `019f1d1c-354a-7743-9e61-f221c327b1ac` | shipped/dogfooding command-facing docs | requirement/design/plan S90 | docs only | source/tests/report | grep and diff check | broad delegated policy rewrite | changed files, deferred hits | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S04 | dev-coder | Added artifact use case/domain/CLI, removed `new doc`, updated runtime tests. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`, `src/spec_dock/cli.py`, `tests/**` | focused tests 18 then 19 passed; `tests/cli_runtime` 717 passed; unit checks 9 passed | code-review pass after P1 fix; QA pass | none blocking | accepted |
| S03 fix | dev-coder | Rejected ambiguous blank slugs before setup/write and added regression. | `domain/artifacts.py`, `create_artifact_doc.py`, `tests/cli_runtime/test_new.py` | ambiguous slug test 1 passed; focused lane 19 passed | code-review pass | none blocking | accepted |
| S03/S04 tests | dev-coder | Strengthened profile fail no-write and full direct catalog assertions. | `tests/cli_runtime/test_new.py` | strengthening lane 4 passed; focused lane 19 passed | QA pass | none blocking | accepted |
| S90 | doc-writer | Updated direct command-facing docs to `new artifact` / `artifacts/`, fixed workflow catalogs to exclude `scratch`, and deferred deeper delegated/legacy policy hits. | `src/spec_dock/assets/spec_dock/docs/**`, `src/spec_dock/assets/spec_dock/scripts/README.md`, `spec-dock/docs/**` | `rg` inspection; `git diff --check` pass | final spec review pending | deferred broad delegated authoring / legacy discussion rule docs | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect / implementation-planner / manual fallback` | used | read-only specialist evidence from `019f1cd6-59b5-78a0-9c54-e2f48e8a35bb` and `019f1cd6-88f3-7e12-80e9-ddd9dfe6366f`; adopted via EAL-001/EAL-002; reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f` | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | Initial reviewer `019f1cde-98b4-7f53-a7c1-7055a41d4a69` found a P1 ambiguity; requirement/plan were clarified; re-reviewer `019f1ce2-384c-7941-9cd7-7c611f16fd1f` returned pass with only non-blocking wording cleanup, which was applied. |
| implementation | code-review | code-reviewer | fresh | pass | no | proceed to final QA/spec gates | Reviewer `019f1d10-d7f1-74b1-9a40-846bc62c2e41` returned pass after P1 ambiguous blank slug fix; P2 docs finding handled in S90. |
| final | QA review | qa-reviewer | fresh | pass | no | proceed to final spec review | Reviewer `019f1d20-2050-7461-8c44-c92d3a9aa07e` returned pass after report evidence and `scratch` catalog fixes. |
| final | spec review | spec-reviewer | fresh | pass | no | execute approved plan | Reviewer `019f1d22-ff74-7ee0-b290-7a7f177a4ac9` returned pass; non-blocking stale Closure Delta marker was corrected; completion proceeds to commit candidate. |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S04/S90/S99 | pending final reviewers | runtime source, tests, shipped docs, dogfooding docs, issue docs | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` - new artifact use case.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py` - artifact catalog/parser/allocation/no-write guards.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - artifact request/result/use-case contract.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - use-case wiring.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` - `new artifact` parser and `new doc` removal.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` - command args/run path update.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - `new artifact` output.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py` - profile template symlink safety.
- `src/spec_dock/cli.py` - legacy template prune narrowed so `templates/artifacts/` remains installed.
- `tests/cli_runtime/test_new.py` and related runtime/unit tests - `new artifact` coverage and `new doc` removal expectations.
- `src/spec_dock/assets/spec_dock/docs/**`, `src/spec_dock/assets/spec_dock/scripts/README.md`, `spec-dock/docs/**` - command-facing docs update.

#### コミット
- pending final reviewer gates.

#### メモ
- Remaining `new doc` grep hits are documented as deferred surfaces: phase/delegated authoring docs and legacy `docs/rules/*/discussions.md` examples. They require coordinated delegated-authoring policy migration, not a narrow command-surface edit.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| direct command-facing docs / scripts README / guide / reference / workflow docs | yes | doc-writer `019f1d10-addc-7c70-ba87-c37ed61a1df4`, `019f1d16-1863-7791-ba78-ef26292be9ef`, `019f1d1c-354a-7743-9e61-f221c327b1ac` | updated provider and dogfooding docs; specified workflow files have no `new doc` hits and no current `new artifact` catalog `scratch` hit; `git diff --check` pass | pending final spec-reviewer |
| phase/delegated authoring docs and legacy `docs/rules/*/discussions.md` | deferred | N/A | remaining `rg -n "new doc|new_doc"` hits are legacy/delegated policy surfaces, not normal command-facing workflow after S90 updates | pending final spec-reviewer |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer `019f1d20-2050-7461-8c44-c92d3a9aa07e` | whole issue obligation coverage | added ambiguous slug regression, profile no-write tree snapshot, full catalog assertions; report evidence and workflow catalog `scratch` fix verified | focused tests 1/4/19 passed; full `tests/cli_runtime` 717 passed, 76 skipped | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer `019f1d10-d7f1-74b1-9a40-846bc62c2e41` | issue-wide integrated diff | Prior P1 ambiguous blank slug fixed; P2 workflow docs finding handled by S90 doc-writer updates. | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer `019f1d22-ff74-7ee0-b290-7a7f177a4ac9` | requirement / design / plan / report / implementation / tests / docs alignment | P2 stale QA pending markers in Closure Delta corrected. | 0 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| implementation/test/docs evidence recorded; code/QA/spec gates passed | issue diff for iss-00263 | final response after issue finish; Epic PR later | ready |

## 遭遇した問題と解決 (任意)
- 問題: `blank` artifact の slug が `research-...` / `adr-...` など supported type prefix に見える場合、typed artifact として再解釈され partial write risk があった。
  - 解決: setup/write 前に ambiguous blank slug を拒否し、derived title と explicit slug の regression test を追加した。
- 問題: `templates/artifacts/` が installer cleanup で pruning され、runtime command が direct templates を読めない可能性があった。
  - 解決: legacy node-scope template pruning に限定し、top-level `templates/artifacts/` を保持した。
- 問題: `new doc` removal 後も direct workflow docs が stale command を案内していた。
  - 解決: command-facing docs/workflow lines を `new artifact` / `artifacts/` に更新し、deeper delegated/legacy docs migration は deferred とした。
- 問題: direct workflow docs の current artifact catalog に unsupported `scratch` が残っていた。
  - 解決: workflow initiative/epic/issue docs から `scratch` を外し、`blank` / `decision-candidate` と issue-only draft routing を runtime catalog に合わせた。

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- Follow-up Issue で phase/delegated authoring docs と legacy `docs/rules/*/discussions.md` examples を artifact/delegated output policy と整合させる。

## 省略/例外メモ (必須)
- Broad delegated authoring / diff guard policy migration and legacy `discussions.md` rule rewrite are intentionally deferred; this Issue owns runtime command removal/addition and direct command-facing guidance only.

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
