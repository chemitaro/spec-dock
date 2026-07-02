---
種別: 実装報告書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
関連GitHub: ["#264"]
状態: "in_progress"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00264 Future node scaffold artifacts default — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | implementation | orchestrator | Initial draft did not specify the real node scaffold seam. | Change node templates; change rules scaffold specs; migrate existing nodes. | Use existing `create_node.py` rules scaffold specs and switch node-local rules from `discussions/rules.md` to `artifacts/rules.md`; do not migrate existing nodes. | `create_node.py` owns relative rules symlink materialization for new nodes, while `create_artifact_doc.py` already owns on-demand old-node artifact setup. | promoted_to_design | `design.md` Current Structure / Change Policy; `create_node.py` inspection | none |
| D-002 | resolved | scope | orchestrator | AC-264-005 mentions old-only validity, but full validation parity belongs to `iss-00265`. | Implement validation parity now; add only regression/non-regression evidence; defer entirely. | Do not implement validation/sync/ADR mirror parity in this Issue; only verify this Issue does not make old-only/mixed layouts invalid. | Requirement scopes `legacy nodes without artifacts remain valid`; Epic plan keeps full parity for later Issue. | promoted_to_plan | `plan.md` CLOS-264-006 and S03; `requirement.md` scope/out-of-scope | `iss-00265` remains owner of full validation parity |
| D-003 | resolved | compatibility | orchestrator | New node default must stop creating `discussions/` while old-node `new artifact` still preserves discussions. | Delete/migrate `discussions`; keep default creation; stop default creation and preserve old paths. | Stop default scaffold creation only; never delete, move, or rewrite existing `discussions/`. | User explicitly required future-only adoption and no migration; AC-264-004 requires preservation. | promoted_to_design | `design.md` Safety Boundary; `plan.md` S03 | none |
| D-004 | resolved | follow-up | code-review | Built-in review found artifact ADR creation can produce ADR originals under `artifacts/`, while ADR mirror rebuild still scans only `discussions/`. | Fix ADR mirror now; remove `adr` from `new artifact`; defer to planned mirror parity Issue. | Defer implementation to `iss-00265` and keep this Issue focused on future node scaffold defaults. | `iss-00265` is already the planned owner for validation/sync/ADR mirror parity; implementing it here would expand `iss-00264` beyond its requirement and plan. Epic PR is created only after all Issues complete, so this is not released as a final Epic state. | converted_to_followup | code review output `/private/tmp/iss-00264-code-review.md`; `plan.md` D-002/S03/S99 | `iss-00265` must include artifacts + discussions ADR mirror collection before Epic PR |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | command / inspection | artifact | Active issue docs, `create_node.py`, `create_artifact_doc.py`, provider rules assets, and current scaffold tests were inspected before plan promotion. | `rg` / `nl` inspections; `design.md`; `plan.md` | fresh spec-reviewer |
| EAL-002 | adopted | sub-agent | artifact | Specialist sidecar results confirmed the `create_node.py` rule-spec switch, no validation expansion, no migration boundary, and highlighted `tests/unit/commands/test_runtime_new_s08.py` as required planned-path coverage. | system-architect `019f1d2a-8e23-7990-a277-4634c5c45e67`; implementation-planner `019f1d2a-c6ff-71d2-a2d5-186598177a82`; reflected in `design.md` / `plan.md` | fresh spec-reviewer |
| EAL-003 | adopted | dev-coder | implementation | Worker implemented the node-local rules source switch from `discussions.md` to `artifacts.md` and updated focused scaffold tests. | dev-coder `019f1d3d-4bb2-7af3-b542-ce56e691e43c`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`; focused pytest evidence below | code-reviewer / qa-reviewer |
| EAL-004 | adopted | dev-coder / doc-writer | tests / docs / dogfooding mirror | Follow-up workers aligned runtime fixture expectations, provider docs/rules, and dogfooding mirror assets with the artifacts default. | dev-coder `019f1d54-4398-7ec0-a5c3-44fadca74fdb`; doc-writer `019f1d54-ba79-7202-9b52-b365dc7a21fb`; `tests/cli_runtime`, `tests/unit/infra`, mirror parity evidence below | code-reviewer / qa-reviewer / spec-reviewer |
| EAL-005 | adopted | orchestrator | tests / templates | After `origin/main` merge, the PR repair batch template contract changed on `main`; artifacts-side template and catalog marker expectations were aligned to that merged contract. | `git merge --autostash origin/main`; `templates/artifacts/pr-repair-batch.md`; `tests/cli_runtime/test_new.py`; post-merge pytest evidence below | code-reviewer / qa-reviewer |
| EAL-006 | adopted | code-review | report / follow-up | Built-in code review identified ADR mirror parity as a valid P2 concern; orchestrator classified it as non-blocking for `iss-00264` because `iss-00265` owns ADR mirror parity before Epic PR. | `/private/tmp/iss-00264-code-review.md`; D-004 | custom reviewer confirmation / spec-reviewer |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is fixed in `design.md`: new node scaffold defaults to `artifacts/` and does not default-create `discussions/`. | Compatibility remains bounded to preserving existing `discussions/` and avoiding validation invalidation. | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `requirement.md` lines 15-53 inspected; active issue confirmed. | none | adopted | pass | no | execute approved plan |
| design | `create_node.py` rules scaffold, `create_artifact_doc.py` artifact setup, provider rules assets, tests, and specialist findings inspected. | none | adopted | pass | no | execute approved plan |
| plan | Closure IDs and Red/Green/update compatibility gates written from inspected code/test seams and specialist findings. | none | adopted | pass | no | execute approved plan |

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
  - filename: typed artifacts use timestamp plus type plus slug, with numeric same-second fallback; blank artifacts use timestamp plus slug, with numeric same-second fallback.
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
| 該当なし | iss-00264 | 該当なし（no delegated draft artifact was created） | `requirement.md`, `design.md`, `plan.md` | `design.md`, `plan.md` | not used | [`design.md`, `plan.md`] | not_applicable_manual_authoring | manual authoring from inspected repo evidence | none | none | pass | execute manual-authored canonical docs |

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
- New initiative / epic / issue nodes now scaffold node-local `artifacts/rules.md` symlinks from `docs/rules/{initiative,epic,issue}/artifacts.md` instead of defaulting to `discussions/rules.md`.
- Existing nodes remain preservation surfaces: old `discussions/` content is not migrated or deleted, and old nodes can still set up `artifacts/` on demand through `new artifact`.
- Provider docs, dogfooding mirror docs, runtime fixtures, and snapshot expectations were updated for the new future-node default.
- `origin/main` was merged during execution; the merged PR repair batch policy was synchronized into the artifacts template surface.

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 Planning Readiness）

#### 対象
- Step: S00
- AC/EC: AC-264-001 through AC-264-005
- 計画上の出典（Planned source）:
  - `plan.md` sections: S00, S01, S02, S03, S90, S99
  - closure ids: CLOS-264-001 through CLOS-264-008

#### 実施内容
- Active issue requirement, current scaffold flow, artifact setup helper, provider rules assets, and relevant tests were inspected.
- `design.md` and `plan.md` were promoted from draft-shaped content to executable planning artifacts.
- `system-architect` and `implementation-planner` read-only findings were verified and integrated.

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock active show
# active issue confirmed as iss-00264

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok, authorized_profile=standard

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok, authorized_profile=standard
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（planning inspection） | inspect-only | `create_node.py`, `create_artifact_doc.py`, tests, and provider rules assets inspected before plan promotion | `rg` / `nl` / sub-agent findings | pass | Implementation Red/Green for S01-S03 is recorded in the Implementation / Merge Integration session log |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | `tests/unit/commands/test_runtime_new_s08.py` should cover planned paths before materialization | implementation-planner | added to plan S02 as required planned-path coverage | CLOS-264-001 through CLOS-264-004 | yes | implementation-planner `019f1d2a-c6ff-71d2-a2d5-186598177a82` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | planning readiness | Approved substantive design/plan, assurance rebinding, specialist evidence, fresh spec-reviewer re-review | `design.md`, `plan.md`, EAL entries, `assurance verify: ok` | pass | Re-review failed only on stale wording; wording corrected |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CLOS-264-001 through CLOS-264-008 | S01-S03 | yes | red-required / covered-existing / inspect-only | planned in `plan.md` | focused scaffold tests, broad runtime/scaffold suites, reviewer gates | pass | Final implementation evidence recorded below; ADR mirror parity converted to `iss-00265` follow-up |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-264-001 through CLOS-264-008 | S01-S03/S99 | `create_node.py` rules source changed to `artifacts/rules.md`; docs/templates and dogfooding mirror updated; `tests/unit/infra -q`; `tests/cli_runtime -q`; `spec-dock validate`; `git diff --check`; code/QA/spec reviews | pass | `iss-00265` remains owner of full validation/sync/ADR mirror parity |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | CLOS-264-007 | missing-rules-source preflight coverage | CLOS-264-007 | specialist findings highlighted pre-GitHub rules preflight as a distinct closure obligation | yes | yes |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/b4d4/spec-dock` | iss-00264 | current session | system-architect / implementation-planner / spec-reviewer / dev-coder / code-reviewer / qa-reviewer | same repo, active issue, named role, bounded scope; no destructive action or per-Issue PR | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed with reviewer gate |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S03 | delegated | runtime scaffold, shipped behavior, tests, compatibility coverage | dev-coder | `create_node.py` and focused tests per `plan.md` | `requirement.md`, `design.md`, `plan.md` | files listed in S01-S03 allowed paths | migration, validation parity, `new doc` restoration, unrelated refactor | focused pytest commands in S02/S03 | scope expansion or destructive legacy migration | changed files, tests, risks, Ledger Note | implemented and adopted |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S03 | dev-coder | Switched new-node local rules scaffolding to `artifacts/rules.md`; preserved old-node on-demand artifact setup; updated focused runtime tests. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`; `tests/unit/commands/test_runtime_new_s08.py`; `tests/cli_runtime/test_wrappers.py`; `tests/cli_runtime/test_new.py`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/commands/test_runtime_new_s08.py -k "create_plan or rules or symlink" -q` => 9 passed; focused wrapper/new/init-update tests passed; `./spec-dock/scripts/spec-dock validate` => ok | pass | Broad suites exposed fixture/doc snapshot drift, handled by follow-up workers. | adopted |
| S90/S99 | dev-coder | Aligned CLI runtime fixtures with new artifacts rules setup while preserving explicit legacy discussions fixtures. | `tests/cli_runtime/test_delegated_authoring.py`; `tests/cli_runtime/test_import.py`; `tests/cli_runtime/test_runtime_import_s10.py`; `tests/cli_runtime/test_runtime_new_doc_s09.py`; `tests/cli_runtime/test_new.py` | `uv run pytest tests/cli_runtime -q` => 718 passed, 76 skipped after `main` merge | pass | none | adopted |
| S90/S99 | doc-writer | Updated shipped docs/rules and dogfooding mirror assets for artifacts default. | `src/spec_dock/assets/spec_dock/docs/**`; `src/spec_dock/assets/spec_dock/scripts/README.md`; `spec-dock/docs/**`; `spec-dock/scripts/**`; `spec-dock/templates/**` | focused `tests/unit/infra/test_init_update.py` docs/mirror checks passed; provider/mirror diff check passed | pass | checked-in initiative snapshot drift remained outside doc-writer scope and was resolved separately. | adopted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S03 | not applicable; core implementation delegation available | no local implementation exception requested | none | none | ordinary git diff revert if needed | delegated verification completed | code-reviewer / qa-reviewer / spec-reviewer passed | not applicable |
| S99 | sub-agent thread limit prevented another bounded worker for snapshot drift after broad tests | user requested continuing work and `main` merge when convenient; bounded test snapshot update was necessary to unblock verification | `tests/unit/infra/test_init_update.py` | update checked-in dogfooding snapshot constants for newly present `.meta.json` paths and dependency map entries | ordinary git diff revert if needed | focused dogfooding snapshot tests and `tests/unit/infra -q` | code-reviewer / qa-reviewer required | host limit recorded; no production runtime logic changed |
| post-merge | direct `git merge --autostash origin/main` introduced updated PR repair policy and artifacts template lag became an immediate merge-integration failure | user requested merging `main` into this branch at a convenient point | `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md`; `spec-dock/templates/artifacts/pr-repair-batch.md`; `tests/cli_runtime/test_new.py` | synchronize artifacts PR repair batch template with merged discussions template and update catalog marker | ordinary git diff revert if needed | targeted `test_new.py` tests and full `tests/cli_runtime -q` | code-reviewer / qa-reviewer required | no `new doc` restoration; template contract alignment only |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `lite` | not applicable | not applicable | Issue grade is standard | pass | ready |
| `standard` | system-architect and implementation-planner | used | system-architect `019f1d2a-8e23-7990-a277-4634c5c45e67`; implementation-planner `019f1d2a-c6ff-71d2-a2d5-186598177a82`; manual inspections reflected in `design.md` and `plan.md` | pass | execute approved plan |
| `strict` | not applicable | not applicable | Issue grade is standard | not applicable | not applicable |
| `critical` | not applicable | not applicable | Issue grade is standard | not applicable | not applicable |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S00 | planning reviewer | spec-reviewer | stale | failed | no | superseded by final pass | First review found incomplete S00 evidence and missing update-asset closure; fixes applied in `plan.md` / `report.md` |
| S00 | planning reviewer | spec-reviewer | stale | failed | no | superseded by final pass | Second review confirmed CLOS-264-008 and found only stale `assurance verify` wording; wording corrected |
| S00 | planning reviewer | spec-reviewer | fresh | passed | no | execute approved plan | Final re-review passed with no findings after CLOS-264-008 report slots were corrected |
| S01-S03/S90/S99 | implementation reviewer | built-in code-reviewer | fresh | conditional finding converted to follow-up | no | proceed after custom disposition | P2 ADR mirror parity finding is valid and assigned to `iss-00265`; not blocking for this scaffold-default Issue |
| S01-S03/S90/S99 | implementation reviewer | custom code-reviewer | fresh | passed | no | issue finish allowed | confirmed ADR mirror parity is outside `iss-00264` and owned by `iss-00265` before Epic PR |
| S01-S03/S90/S99 | QA reviewer | qa-reviewer | fresh | passed | no | issue finish allowed | residual risks recorded as non-blocking follow-ups |
| S01-S03/S90/S99 | final spec reviewer | spec-reviewer | fresh | passed | no | issue finish allowed | confirmed requirement/design/plan/report and implementation alignment |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S03/S90/S99 | implementation complete | final issue commit candidate after reviewer pass and `issue finish` | ready for final commit | not applicable before commit | not no-op | runtime scaffold, docs/templates mirror, tests, issue docs | `git diff --check`; pytest suites; `spec-dock validate` | current diff inspected |

#### 変更したファイル
- `design.md` - promoted substantive design for `artifacts/` scaffold default.
- `plan.md` - promoted executable step contract.
- `report.md` - recorded planning evidence.
- `.assurance.json` - rebound assurance source hashes.

#### 実装セッションログ（2026-07-01 Implementation / Merge Integration）

##### 実行コマンド / 結果
```bash
uv run pytest tests/unit/commands/test_runtime_new_s08.py -k 'create_plan or rules or symlink' -q
# 9 passed, 38 deselected

uv run pytest tests/unit/infra/test_init_update.py -k 'checked_in_dogfooding' -q
# 45 passed, 499 deselected

uv run pytest tests/unit/infra -q
# 584 passed

uv run pytest tests/cli_runtime -q
# 718 passed, 76 skipped

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=171

git diff --check
# pass
```

##### main merge 証跡
```bash
git fetch origin main
# fetched origin/main

git merge --autostash origin/main
# merge succeeded; autostash applied
```

##### post-merge 修正
- `origin/main` changed `pr-repair-batch` policy wording and template structure.
- Artifacts-side `pr-repair-batch.md` was synchronized to the merged discussions-side contract so `new artifact pr-repair-batch` emits the current policy.
- `tests/cli_runtime/test_new.py` marker expectations were updated to the new stable wording.

#### コミット
- Ready for `issue finish` and final issue commit after final validation.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| shipped docs / templates / README / workflow / skill / migration notes | yes | doc-writer + orchestrator merge integration | provider docs/rules, dogfooding mirror docs/templates/runtime, and artifacts `pr-repair-batch` template updated; `git diff --check`; `tests/unit/infra -q`; `tests/cli_runtime -q` | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | broad runtime and scaffold suites passed after `origin/main` merge | `tests/unit/infra -q` => 584 passed; `tests/cli_runtime -q` => 718 passed, 76 skipped; `spec-dock validate` => ok; `git diff --check` => pass | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | built-in P2 ADR mirror parity finding converted to `iss-00265`; custom disposition confirmed non-blocking for `iss-00264` | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | no blocking findings; stale placeholder wording corrected in final ledger | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| implementation / merge integration ledger updated | issue branch commit after reviewer pass and `issue finish` | final response; Epic PR later after Epic quality gate | ready |

## 遭遇した問題と解決 (任意)
- 問題: `guidance issue-planning` blocked on stale assurance and report scaffold placeholders.
  - 解決: assurance was rebound after doc edits; report placeholder rows were replaced with concrete planning evidence and final gates.

## 学んだこと (任意)
- `plan.md` must include executable schema headings and concrete test-case cards, not only a reasonable narrative plan.

## 今後の推奨事項 (任意)
- Keep `iss-00265` validation parity scope separate unless implementation proves a blocking dependency.

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- S00 planning evidence recorded in Spec Authoring Gate, Evidence Adoption Ledger, Grade Specialist Evidence Gate, and the Planning Readiness session log above.
- S01-S03 implementation evidence: new node local rules now target `artifacts/rules.md`; focused scaffold rules tests passed.
- S90 evidence: shipped docs/rules/templates and dogfooding mirror updated; provider/mirror checks covered by `tests/unit/infra`.
- S99 evidence: after `origin/main` merge, `tests/unit/infra -q` passed with 584 tests, `tests/cli_runtime -q` passed with 718 passed / 76 skipped, `spec-dock validate` passed with 171 nodes, and `git diff --check` passed.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
