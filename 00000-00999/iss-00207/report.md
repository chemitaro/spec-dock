---
種別: 実装報告書（Issue）
ID: "iss-00207"
タイトル: "Fix dependency projections for node level blockers"
関連GitHub: ["#207"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00207 Fix dependency projections for node level blockers — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | compatibility | orchestrator / system-architect draft | `DepsEvaluation.blockers` の互換 field 形 | A: `blockers` を issue-only 維持; B: `blockers` を all blocker node ids とし typed fields を追加 | B を採用。`blockers` は CLI/legacy readability 用の全 blocker id list、`issue_blockers` / `node_blockers` を typed contract にする。 | CLI output の有用性を残しつつ JSON consumer の曖昧さを減らすため。 | promoted_to_design | `design.md` の `データ / インターフェース契約`、`discussions/20260618t151109z-draft-design-node-level-dependency-projection.md` | なし |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research discussion | `requirement.md` | 3 deep-consultant 調査と親確認で、問題が renderer のみではなく readiness / projection contract mismatch であることを確認したため。 | `discussions/20260618t145427z-research-node-level-dependency-projection-failure-analysis.md`; requirement reviewer pass by `spec-reviewer` | design / plan へ継続反映 |
| EAL-002 | adopted | delegated design draft by `system-architect` | `design.md` | post-run diff guard で許可された discussion file だけが追加されたこと、内容が要件 AC/EC と runtime layer 境界に整合したことを確認したため。 | `discussions/20260618t151109z-draft-design-node-level-dependency-projection.md`; `git status --short` showed only existing requirement/design changes plus this new discussion before adoption | fresh design spec-reviewer を再実行 |
| EAL-003 | adopted | spec-reviewer finding | `design.md` / `report.md` | design reviewer の P1 指摘に従い、provider docs path を正しい source-of-truth path に修正し、delegated draft adoption evidence をこの report に記録した。 | design reviewer `Mencius` finding: docs path and adoption ledger blockers | fresh design spec-reviewer を再実行 |
| EAL-004 | adopted | delegated plan draft by `implementation-planner` | `plan.md` | post-run diff guard で許可された plan discussion file だけが追加されたこと、step order / closure index / concrete tests が reviewed design に整合したことを確認したため。 | `discussions/20260618t152507z-draft-plan-node-level-dependency-projection.md`; `git status --short` showed existing canonical diffs plus this new discussion before adoption | fresh plan spec-reviewer を実行 |
| EAL-005 | adopted | spec-reviewer finding | `plan.md` | plan reviewer の P1 指摘に従い、各 step の acceptance / output required / closure / gate を補強し、high-level status enrichment の所有を S03/S04 application layer に固定した。 | plan reviewer `Hilbert` findings: incomplete step contracts and unassigned status enrichment | fresh plan spec-reviewer を再実行 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は node-level blocker の readiness 誤判定修正を主要目的として固定。 | `deps-issues` / `deps-raw` rendering と docs/tests 更新は主要目的を観測可能にする副次要件。 | low | requirement / design / plan reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active issue docs、research discussion、runtime deps/readiness/presentation files、parent specs | human blocking question なし | adopted | passed by fresh `spec-reviewer`; first pass P2 fixed, second pass P2 fixed, final pass no findings | no | promoted to design drafting |
| design | `requirement.md` pass、system-architect draft、runtime/docs path inspection、reviewer findings | human blocking question なし | adopted after diff guard and report ledger update | first `spec-reviewer` failed on P1; fixes applied; fresh `spec-reviewer` pass with no findings | no | promoted to plan drafting |
| plan | reviewed `requirement.md` / `design.md`, implementation-planner draft, runtime/test path inspection, authoring docs, reviewer findings | human blocking question なし | adopted after diff guard and report ledger update | first `spec-reviewer` failed on P1; fixes applied; fresh `spec-reviewer` pass with no findings | no | ready for issue execution handoff |

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
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
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

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00207 | `discussions/20260618t151109z-draft-design-node-level-dependency-projection.md` | `requirement.md`; parent specs; research discussion; runtime deps/check/active/sync/presentation files; provider docs | `design.md` | adopted | [`design.md`] | pass: only the allowed discussion file was newly added; existing `requirement.md` was pre-existing orchestrator diff | partially integrated into canonical design by orchestrator | ADR candidates were not promoted in this issue phase | none | fresh design `spec-reviewer` pass with no findings after P1 fixes | promoted to plan drafting |
| implementation-planner | iss-00207 | `discussions/20260618t152507z-draft-plan-node-level-dependency-projection.md` | `requirement.md`; `design.md`; `report.md`; authoring docs; runtime/test path inspection | `plan.md` | adopted | [`plan.md`] | pass: only the allowed plan discussion file was newly added; existing canonical docs and design draft were pre-existing orchestrator diffs | integrated into canonical plan by orchestrator | none material; wording condensed into canonical step contract | none | fresh plan `spec-reviewer` pass with no findings after P1 fixes | promoted to issue execution handoff |

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
- S01 では `DepsTopologyLoadResult` に raw node dependency context を保持する互換 field を追加し、empty high-level dependency expansion を warning-only ではなく後続 domain evaluation が参照できる topology fact として残した。
- 既存の `issue_depends_on_map` と `warnings`、`.meta.json.depends_on` storage format は維持した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-19 S01）

#### 対象
- Step: S01 Contract / Topology Facts
- AC/EC: AC-003, EC-003 partial; S02/S03 用の AC-001 / EC-001 topology prerequisite
- 計画上の出典（Planned source）:
  - `plan.md` section: `S01 — Contract / Topology Facts`
  - closure ids:
    - `cl-ac-003`
    - `cl-ec-003` partial
    - `tc-s01-001`
    - `tc-s01-002`
    - `tc-s01-003`

#### 実施内容
- `DepsDependencyContext` を追加し、`DepsTopologyLoadResult` に `raw_node_depends_on_map` と `dependency_contexts_by_issue_id` を互換 field として追加した。
- `load_issue_depends_on_map()` が compiled issue dependency に加えて raw node dependency context を保持するようにした。
- empty high-level dependency は引き続き `deps_ref_expanded_to_empty` warning を出しつつ、`expansion="empty"` の context として残す。
- non-empty epic dependency は既存どおり child issue へ展開し、raw direct edge context も残す。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_deps_reader_topology.py -q
# 2 passed

uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/cli_runtime/test_sync.py -k "empty or expands or effective_deps or cycle"
# 5 passed, 40 deselected

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | Red | red-required | 新規 infra test が実装前に `AttributeError: 'DepsTopologyLoadResult' object has no attribute 'raw_node_depends_on_map'` で失敗 | dev-coder reported red run | pass | empty high-level dependency context が未実装であることを検出 |
| S01 | Green | red-required / covered-existing | `tests/unit/infra/test_deps_reader_topology.py -q` -> 2 passed; required slice -> 5 passed, 40 deselected | command | pass | 親 orchestrator でも同じ Green を再実行済み |
| S01 | Refactor | guardrail satisfied | 差分は S01 allowed paths のみ。readiness / CLI / sync / rendering / docs には未着手 | diff inspection / `git diff --check` | pass | no behavioral refactor beyond S01 topology |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | new focused infra topology tests | dev-coder | added | `tc-s01-001`, `tc-s01-002` | no | `tests/unit/infra/test_deps_reader_topology.py` |
| S01 | Later S02/S03 must interpret `expansion="empty"` with high-level status | dev-coder | recorded as planned downstream risk | S02/S03 | no | plan already assigns status interpretation to S02/S03 |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `tc-s01-001`, `tc-s01-002`, `tc-s01-003`, `cl-ac-003`, `cl-ec-003` partial | S01 tests pass, reader exposes raw context without changing storage semantics, reviewer pass recorded | tests pass; `code-reviewer` pass; storage unchanged; committed as `6d29cd22` | pass | post-commit clean check passed before S02 work |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s01-001` | S01 | yes | red-required | missing `raw_node_depends_on_map` caused red failure | `uv run pytest tests/unit/infra/test_deps_reader_topology.py -q` | pass | empty high-level dependency retained as topology context |
| `tc-s01-002` | S01 | yes | red-required | same red test file before implementation | `uv run pytest tests/unit/infra/test_deps_reader_topology.py -q` | pass | non-empty epic expansion and raw context both preserved |
| `tc-s01-003` | S01 | yes | covered-existing | existing cycle tests | `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/cli_runtime/test_sync.py -k "empty or expands or effective_deps or cycle"` | pass | raw cycle remains fail-closed in selected compatibility slice |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac-003` | S01 | non-empty epic expansion test; required compatibility slice | pass | child issue expansion remains intact |
| `cl-ec-003` | S01 | existing cycle selected tests | pass | S01 did not weaken fail-closed cycle path |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S01 | N/A | N/A | plan の S01 closure ids で対応 | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/7d89/spec-dock` | iss-00207 | current session | dev-coder, code-reviewer, later doc-writer / qa-reviewer / spec-reviewer | same repo, active issue, plan-bounded step scope; no destructive action / secrets / GitHub mutation outside PR flow | issue complete / session end / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime/test mutation under issue execution workflow | dev-coder | Contract / Topology Facts | `plan.md` S01 | `infra/contracts.py`, `infra/deps_reader.py`, `tests/unit/infra/**`, `tests/unit/domain/test_runtime_domain_s03.py` | app/command/presentation/docs/storage format/legacy `app.py` | S01 required pytest slice and `git diff --check` | compatibility impossible or storage change required | changed files, fields, tests, risks, ledger note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added topology context fields while preserving compiled issue map and warnings. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`; `tests/unit/infra/test_deps_reader_topology.py` | infra test 2 passed; required selected slice 5 passed, 40 deselected; `git diff --check` pass | code-reviewer pass | S02/S03 must interpret `expansion="empty"` with high-level status | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit gate | No findings; patch preserves compiled map/warnings and adds deterministic context facts |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | closed | S01 allowed paths plus report evidence | `6d29cd22` | `git status --short` clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py` - topology result context field definitions
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py` - raw node dependency context collection
- `tests/unit/infra/test_deps_reader_topology.py` - S01 topology regression tests
- `spec-dock/active/issue/report.md` - S01 observed evidence ledger

#### コミット
- `6d29cd22 feat(deps): raw依存トポロジー文脈を保持する`

#### メモ
- ...

---

### セッションログ（2026-06-19 S02）

#### 対象
- Step: S02 Domain Readiness Evaluation
- AC/EC: AC-001, AC-002, AC-003, EC-001, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `S02 — Domain Readiness Evaluation`
  - closure ids:
    - `cl-ac-001`
    - `cl-ac-002`
    - `cl-ac-003`
    - `cl-ec-001`
    - `cl-ec-002`

#### 実施内容
- `DepsEvaluation` に `issue_blockers`、`node_blockers`、`satisfied_dependencies`、`debug_context` を追加し、既存の `blockers` / `blockers_top` / `closure` は互換 field として維持した。
- domain model に `DepsDependencyContext`、`DepsHighLevelStatus`、`DepsNodeBlocker` を追加した。
- `evaluate_readiness()` / `inspect_target_deps()` が明示的な topology context と high-level status context を受け取り、empty open high-level dependency を blocker、empty closed/done high-level dependency を satisfied、empty unknown high-level dependency を fail-closed blocker として評価するようにした。
- domain は GitHub / cache へ直接アクセスせず、S03/S04 application layer から渡される status context を評価する境界に留めた。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py
# 31 passed

git diff --check
# pass

rg -n "github|cache|gh\b|subprocess|requests|urllib|http" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py
# domain/deps.py に該当なし。domain/models.py は既存の github metadata field 名のみ。
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S02 | Red | red-required | 新規 domain tests が実装前に missing model / behavior で失敗したことを dev-coder が報告 | dev-coder reported red run | pass | `DepsDependencyContext` など S02 domain contract 未実装を検出 |
| S02 | Green | red-required | `tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py` -> 31 passed | command | pass | 親 orchestrator でも同じ Green を再実行済み |
| S02 | Refactor | guardrail satisfied | 差分は S02 allowed paths のみ。GitHub/cache I/O、command guard、sync、presentation には未着手 | diff inspection / `git diff --check` / `rg` inspection | pass | S03/S04 に status context construction を残す |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | explicit high-level status context must be supplied by later application/sync layers | dev-coder / orchestrator | recorded as planned downstream risk | S03/S04 | no | design and plan already assign status context owner to application layer |
| S02 | structural conversion is needed so S01 infra context can be passed without domain depending on infra | dev-coder | implemented structural context normalization | S01/S02 compatibility | no | `domain/deps.py` accepts dataclass-like or dict context inputs |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | `tc-s02-001`, `tc-s02-002`, `tc-s02-003`, `tc-s02-004`, `cl-ac-001`, `cl-ac-002`, `cl-ac-003`, `cl-ec-001`, `cl-ec-002` | S02 domain tests pass for open/closed/unknown/descendant-derived status context and reviewer pass recorded | tests pass; `code-reviewer` pass; no domain I/O found; S02 commit confirmed by post-commit `git log --oneline -3` | pass | post-commit clean check passed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s02-001` | S02 | yes | red-required | missing domain model / behavior caused red failure | `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py` | pass | empty open epic blocks with `node_blockers.reason=="empty_open"` |
| `tc-s02-002` | S02 | yes | red-required | same red test file before implementation | same command | pass | empty closed epic is recorded as satisfied and does not block |
| `tc-s02-003` | S02 | yes | red-required | same red test file before implementation | same command | pass | empty unknown epic fails closed with `guard_reason=="unknown"` |
| `tc-s02-004` | S02 | yes | red-required | same red test file before implementation | same command | pass | done descendant aggregate remains non-blocking and visible as satisfied context |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac-001` | S02 | domain empty open high-level dependency test | pass | command guards remain for S03 |
| `cl-ac-002` | S02 | domain empty closed high-level dependency test | pass | sync/presentation visibility remains for S04 |
| `cl-ac-003` | S02 | existing issue expansion compatibility slice plus S02 done-child test | pass | S02 keeps issue blocker path intact |
| `cl-ec-001` | S02 | domain empty unknown high-level dependency test | pass | fail-closed at domain level |
| `cl-ec-002` | S02 | domain done descendant high-level dependency test | pass | satisfied context retained |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S02 | N/A | N/A | plan の S02 closure ids で対応 | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | runtime/test mutation under issue execution workflow | dev-coder | Domain Readiness Evaluation | `plan.md` S02 | `domain/models.py`, `domain/deps.py`, `tests/unit/domain/test_runtime_domain_s03.py`, `tests/unit/domain/test_deps.py` | GitHub I/O in domain, renderer-side readiness computation, removal of existing `DepsEvaluation` fields | S02 required pytest lane and `git diff --check` | high-level status priority cannot be represented with explicit status context, or blockers compatibility must change beyond design | changed files, model fields, status input shape, tests, risks, ledger note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | Added typed domain evaluation fields and high-level status-context evaluation while preserving existing blockers compatibility. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `tests/unit/domain/test_deps.py` | required domain lane 31 passed; `git diff --check` pass; domain I/O inspection pass | code-reviewer pass | S03/S04 must construct authoritative high-level statuses; domain intentionally does not fetch GitHub/cache | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit gate | No findings; reviewer confirmed fail-closed unknown behavior, typed blocker compatibility, no domain I/O, structural context compatibility, and S02 test adequacy |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S02 | closed | S02 allowed paths plus this report evidence | current S02 commit confirmed by `git log --oneline -3` after commit | `git status --short` clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py` - typed dependency evaluation models
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - issue/node blocker and satisfied dependency evaluation
- `tests/unit/domain/test_deps.py` - S02 high-level dependency readiness tests
- `spec-dock/active/issue/report.md` - S01/S02 observed evidence ledger

#### コミット
- `feat(deps): high-level依存のreadiness評価を追加` committed; final hash confirmed by post-commit `git log --oneline -3`

---

### セッションログ（2026-06-19 S03）

#### 対象
- Step: S03 Command Guards And CLI Output
- AC/EC: AC-001, AC-002, EC-001, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `S03 — Command Guards And CLI Output`
  - closure ids:
    - `cl-ac-001`
    - `cl-ac-002`
    - `cl-ec-001`
    - `cl-ec-002`

#### 実施内容
- `deps check` と `active set` が S01/S02 の topology context / high-level status context を domain evaluation へ渡すようにした。
- command-time high-level status context builder を追加し、GitHub snapshot、cache、descendant aggregate、unknown の順で high-level node state を解決する。
- `deps check --json` を schema v2 にし、`issue_blockers`、`node_blockers`、`satisfied_dependencies` を出力するようにした。
- `active set --force` は既存 issue-level blocker の警告継続互換を維持しつつ、node-level blocker がある場合は force でも拒否するようにした。
- `issue start --force` は `set_active(... force=False ...)` 経由の dependency guard を維持し、node-blocked issue を開始しないことを CLI test で固定した。
- reviewer follow-up として、high-level node の default local open が empty unknown / descendant aggregate を隠さないように補正した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/application/test_check_deps.py -k "local_empty_high_level_dependency_without_cache_fails_unknown or local_high_level_default_open_does_not_mask_done_descendant_aggregate"
# 2 passed, 10 deselected

uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py -k "deps_check or active or issue_start or node"
# 61 passed, 8 skipped, 85 deselected

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S03 | Red | red-required | required command が実装前に 7 failures。empty open epic が ready/exit 0、`issue start --force` が node-blocked issue を開始、JSON が schema v1 / typed fields なし | dev-coder reported red run | pass | command guard level の未実装を検出 |
| S03 | Red follow-up | reviewer finding | local empty high-level / done descendant aggregate tests が実装修正前に 2 failed | dev-coder reported follow-up red run | pass | default local open が unknown / descendant aggregate を隠すことを検出 |
| S03 | Green | red-required | required S03 slice -> 61 passed, 8 skipped, 85 deselected | command | pass | 親 orchestrator でも同じ Green を再実行済み |
| S03 | Refactor | guardrail satisfied | 差分は S03 allowed paths plus this report のみ。GitHub mutation、storage format、sync artifact behavior には未着手 | diff inspection / `git diff --check` | pass | JSON v2 command rendering は S04 で presentation artifact と整合確認する |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S03 | `deps check --json` v2 serialization は S03 では command output に限定 | dev-coder / orchestrator | S04 で presentation artifact contract と再確認するリスクとして記録 | S04 | no | `commands/deps.py` |
| S03 | high-level default local open が unknown / descendant aggregate を隠す | code-reviewer | follow-up fix and tests added | `cl-ec-001`, `cl-ec-002` | no | `tests/unit/application/test_check_deps.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S03 | `tc-s03-001`, `tc-s03-002`, `tc-s03-003`, `tc-s03-004`, `cl-ac-001`, `cl-ac-002`, `cl-ec-001`, `cl-ec-002` | S03 command tests pass, node-blocked issues fail consistently across `deps check`, `active set`, and `issue start`, reviewer pass recorded | tests pass; first `code-reviewer` failed on missing report evidence and local high-level status edge; follow-up fix applied; fresh `code-reviewer` pass; S03 commit confirmed by post-commit `git log --oneline -4` | pass | post-commit clean check passed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s03-001` | S03 | yes | red-required | command tests failed before implementation | required S03 pytest slice | pass | `deps check --json` exits non-zero and returns schema v2 node blocker fields |
| `tc-s03-002` | S03 | yes | red-required | application/CLI guard failed before implementation | required S03 pytest slice | pass | `active set` rejects node-blocked issue and keeps active pointer unchanged |
| `tc-s03-003` | S03 | yes | red-required | `issue start --force` started node-blocked issue before implementation | required S03 pytest slice | pass | force does not bypass dependency guard |
| `tc-s03-004` | S03 | yes | red-required | schema v1 / missing satisfied context before implementation | required S03 pytest slice | pass | satisfied high-level context exits zero and remains visible |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac-001` | S03 | CLI/application node blocker tests for `deps check`, `active set`, `issue start --force` | pass | command guard level closed pending fresh review |
| `cl-ac-002` | S03 | `deps check --json` satisfied closed high-level context test | pass | satisfied-only context exits zero |
| `cl-ec-001` | S03 | local empty high-level unknown follow-up test | pass | no default local open mask |
| `cl-ec-002` | S03 | done descendant aggregate follow-up test | pass | descendant aggregate remains satisfied |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| reviewer follow-up | `cl-ec-001`, `cl-ec-002` | local high-level status tests | same | reviewer P2 が EC-001/EC-002 の説明性不足を指摘したため | no | yes |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | runtime/test mutation under issue execution workflow | dev-coder | Command Guards And CLI Output | `plan.md` S03 | S03 application/command/tests allowed paths | dependency guard bypass via force, GitHub mutation, storage/presentation artifact behavior outside command output | S03 required pytest slice and `git diff --check` | lifecycle redesign or JSON schema strategy beyond design | changed files, command examples, status source path evidence, tests, risks, ledger note | pass after reviewer follow-up |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S03 | dev-coder | Added high-level status context wiring for deps check / active set and JSON schema v2 command output. | `application/check_deps.py`; `application/set_active.py`; `commands/deps.py`; S03 tests | required S03 slice passed; `git diff --check` pass | first code-reviewer fail | S04 may consolidate command JSON and presentation ownership | accepted after follow-up |
| S03 follow-up | dev-coder | Prevented default local-open high-level status from masking unknown/descendant aggregate behavior. | `application/check_deps.py`; `tests/unit/application/test_check_deps.py` | focused 2-test run passed; required S03 slice passed; `git diff --check` pass | pending fresh review | none beyond S04 presentation alignment | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | code-reviewer | fresh after follow-up | passed | N/A | proceed to commit gate | First review failed on P1/P2; follow-up fixed local high-level status edge and report evidence; fresh re-review returned no findings |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S03 | closed | S03 allowed paths plus this report evidence | current S03 commit confirmed by `git log --oneline -4` after commit | `git status --short` clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py` - high-level status context builder and deps check wiring
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` - active set readiness wiring and node blocker force guard
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` - deps check JSON schema v2 command output
- `tests/cli_runtime/test_deps.py` - CLI deps check node blocker / satisfied context tests
- `tests/cli_runtime/test_issue_lifecycle.py` - issue start force dependency guard test
- `tests/unit/application/test_check_deps.py` - application status context and follow-up edge tests
- `tests/unit/application/test_set_active.py` - active set node blocker force guard test
- `spec-dock/active/issue/report.md` - S03 observed evidence ledger

#### コミット
- `feat(deps): node依存をcommand guardに反映` committed; final hash confirmed by post-commit `git log --oneline -4`

---

### セッションログ（2026-06-19 S04）

#### 対象
- Step: S04 Sync State And Presentation Artifacts
- AC/EC: AC-002, AC-004, AC-005, EC-001, EC-002, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `S04 — Sync State And Presentation Artifacts`
  - closure ids:
    - `cl-ac-004`
    - `cl-ac-005`
    - sync/presentation portions of `cl-ac-002`, `cl-ec-001`, `cl-ec-002`, `cl-ec-003`

#### 実施内容
- `SyncStateResult` が `dependency_contexts_by_issue_id` と `high_level_statuses_by_node_id` を保持するようにした。
- `sync_state.py` が S03 の high-level status context builder を再利用し、sync 中の `evaluate_readiness()` に topology context / high-level status context を渡すようにした。
- `.agent/deps-issues.json` を schema v2 / `issue-readiness-with-dependency-context` projection に変更し、`SyncStateResult` の readiness evaluation から生成するようにした。
- `deps-issues` の edge に `state: blocking | satisfied` と `relation: compiled_issue | raw_direct` を持たせた。
- `deps-raw.puml` が payload の high-level `state` / `state_source` を package label / color に反映し、raw/debug artifact であることを legend に表示するようにした。
- raw dependency preflight failure 時は deps disabled payload / PUML を維持し、stale partial graph を描画しないことを確認した。
- reviewer follow-up として、historical done issue の unrelated satisfied high-level context が `deps-issues` に混入しないよう include 境界を絞った。
- broader CLI regression follow-up として、S04 v2 contract に追随して `test_new.py` / `test_deps.py` の stale source/projection expectations を更新した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k historical_satisfied_high_level_context -q
# 1 passed, 56 deselected

uv run pytest tests/cli_runtime/test_new.py::TestCliNew::test_new_issue_auto_syncs_index_and_dashboard tests/cli_runtime/test_deps.py::TestCliDeps::test_sync_force_sets_deps_valid_false_and_emits_placeholders tests/cli_runtime/test_deps.py::TestCliDeps::test_sync_deps_empty_open_epic_blocks_with_node_context tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_add_updated_path_auto_syncs_dependency_projection tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_remove_updated_path_auto_syncs_dependency_projection -q
# 5 passed

uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_deps.py -k "deps_issues or force or cycle or sync or new"
# 63 passed, 6 skipped, 83 deselected

uv run pytest tests/cli_runtime/test_sync.py tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py
# 91 passed, 2 skipped

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S04 | Red | red-required | focused tests failed on missing `SyncStateResult.high_level_statuses_by_node_id` and deps-issues schema v1 | dev-coder reported red run | pass | carrier field and old todo-only projection path were missing |
| S04 | Red follow-up | reviewer finding | historical satisfied high-level regression failed because done issue / closed high-level node were pulled into deps-issues | dev-coder reported focused red run | pass | all-history dump boundary risk reproduced |
| S04 | Red follow-up | reviewer finding | focused CLI tests failed on old `index.json` source / `open-issues-dependency-view` projection expectations | dev-coder reported focused red run | pass | stale tests outside required S04 subset detected |
| S04 | Green | red-required | required S04 lane -> 91 passed, 2 skipped | command | pass | 親 orchestrator でも同じ Green を再実行済み |
| S04 | Refactor | guardrail satisfied | runtime/presentation diff stays in S04 source paths; test expectation updates include S04 contract consumers outside original required subset | diff inspection / `git diff --check` | pass | no storage format or docs changes |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S04 | satisfied high-level context from historical done issue could become all-history dump | code-reviewer | bounded follow-up fix and regression test | `cl-ac-004`, `cl-ac-002`, `cl-ec-002` | no | `tests/unit/presentation/test_runtime_sync_s07.py` |
| S04 | stale deps-issues v1 source/projection expectations remained in broader CLI tests | code-reviewer | bounded test expectation update | `cl-ac-004`, `cl-ec-003` | no | `tests/cli_runtime/test_new.py`; `tests/cli_runtime/test_deps.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S04 | `tc-s04-001`, `tc-s04-002`, `tc-s04-003`, `tc-s04-004`, `cl-ac-004`, `cl-ac-005`, `cl-ac-002`, `cl-ec-001`, `cl-ec-002`, `cl-ec-003` | S04 sync/presentation tests pass, `deps-issues` no longer derives from todo-only `index.json`, `deps-raw` renders supplied high-level state, reviewer pass recorded | tests pass; first review pass with P2; P2 boundary fixed; second review failed on stale CLI expectations and missing report; P1 test expectations fixed; fresh `code-reviewer` pass; S04 commit confirmed by post-commit `git log --oneline -5` | pass | post-commit clean check passed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s04-001` | S04 | yes | red-required | deps-issues was schema v1 / todo-index source | required S04 pytest lane | pass | v2 blocker context includes high-level nodes |
| `tc-s04-002` | S04 | yes | red-required | satisfied context absent or over-inclusive before follow-up | required S04 pytest lane plus historical regression | pass | satisfied context visible only from displayed readiness context |
| `tc-s04-003` | S04 | yes | red-required | deps-raw high-level packages lacked payload state/source | required S04 pytest lane | pass | high-level package state/source rendered from payload |
| `tc-s04-004` | S04 | yes | covered-existing + updated expectation | stale v1 disabled deps-issues expectation remained | CLI focused and required lanes | pass | disabled path emits v2 invalid payload and DEPS_DISABLED PUML |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac-004` | S04 | deps-issues v2 tests and stale expectation follow-up | pass | source is sync_state readiness evaluation, not todo-only index |
| `cl-ac-005` | S04 | deps-raw high-level state rendering test | pass | renderer uses supplied payload state/source |
| `cl-ac-002` | S04 | satisfied context tests and historical boundary regression | pass | satisfied dependencies remain visible but scoped |
| `cl-ec-001` | S04 | unknown high-level blocker context in sync artifact | pass | unknown node blocker visible in deps-issues |
| `cl-ec-002` | S04 | done/satisfied context visibility tests | pass | done dependency does not block but remains visible when connected to displayed context |
| `cl-ec-003` | S04 | forced cycle disabled artifact tests | pass | invalid deps payload / DEPS_DISABLED remain fail-closed |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| reviewer follow-up | `cl-ac-004`, `cl-ac-002`, `cl-ec-002` | historical satisfied high-level context | same | reviewer P2 が all-history dump boundary risk を指摘したため | no | yes |
| reviewer follow-up | `cl-ac-004`, `cl-ec-003` | stale CLI deps-issues expectations | same | reviewer P1 が broader CLI suite の stale contract を指摘したため | no | yes |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S04 | delegated | runtime/test mutation under issue execution workflow | dev-coder | Sync State And Presentation Artifacts | `plan.md` S04 | S04 application/contracts/presentation/tests | renderer-side readiness inference, todo-only index source, all-history graph dump, storage/docs changes | required S04 pytest lane and `git diff --check` | SyncStateResult cannot carry typed contexts without duplicating readiness rules | changed files, deps-issues v2 snippet, deps-raw rendering evidence, tests, risks, ledger note | pass after follow-ups |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S04 | dev-coder | Added sync/presentation carriers and deps-issues v2 / deps-raw state rendering. | S04 application/contracts/presentation/tests | required S04 lane 90 passed, 2 skipped; `git diff --check` pass | first code-reviewer pass with P2 | satisfied context could over-include historical done issue | accepted after follow-up |
| S04 follow-up P2 | dev-coder | Limited satisfied high-level context to displayed include set and added regression. | `presentation/json_state.py`; `tests/unit/presentation/test_runtime_sync_s07.py` | focused 1 passed; required S04 lane 91 passed, 2 skipped; `git diff --check` pass | second code-reviewer failed on P1/P1 | broader CLI stale expectations; report missing | accepted |
| S04 follow-up P1 | dev-coder | Updated stale CLI expectations to S04 deps-issues v2 contract. | `tests/cli_runtime/test_new.py`; `tests/cli_runtime/test_deps.py` | focused 5 passed; CLI subset 63 passed, 6 skipped, 83 deselected; `git diff --check` pass | fresh code-reviewer pass | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S04 | step reviewer | code-reviewer | fresh after follow-ups | passed | N/A | proceed to commit gate | First review P2 fixed; second review P1 stale tests and missing report fixed; fresh re-review returned no findings |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S04 | closed | S04 allowed paths plus broader stale CLI expectation tests and this report evidence | current S04 commit confirmed by `git log --oneline -5` after commit | `git status --short` clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - sync dependency context carrier fields
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - sync readiness context wiring
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - deps-issues v2 payload and deps-raw high-level state payload
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py` - blocker/satisfied/raw state rendering
- `tests/cli_runtime/test_sync.py` - sync artifact v2 regression tests
- `tests/cli_runtime/test_new.py` - auto-sync deps-issues v2 expectation
- `tests/cli_runtime/test_deps.py` - deps auto-sync / disabled artifact v2 expectations
- `tests/unit/presentation/test_runtime_sync_s07.py` - sync presentation regression tests
- `tests/unit/presentation/test_deps_raw_puml.py` - raw PUML high-level state tests
- `spec-dock/active/issue/report.md` - S04 observed evidence ledger

#### コミット
- `feat(deps): sync依存ビューをreadiness文脈で生成` committed; final hash confirmed by post-commit `git log --oneline -5`

---

### セッションログ（2026-06-19 S90）

#### 対象
- Step: S90 Docs Impact Resolution And Dogfooding Mirror
- AC/EC: AC-006, EC-004
- 計画上の出典（Planned source）:
  - `plan.md` section: `S90 — Docs Impact Resolution And Dogfooding Mirror`
  - closure ids:
    - `cl-ac-006`
    - `cl-ec-004`

#### 実施内容
- provider docs `src/spec_dock/assets/spec_dock/docs/reference_deps.md` / `reference_sync.md` に node blocker、satisfied dependency、schema v2 `deps-issues`、raw/debug `deps-raw` の authority 境界を反映した。
- dogfooding mirror docs `spec-dock/docs/reference_deps.md` / `reference_sync.md` を provider docs と同一内容に揃えた。
- `.meta.json.depends_on` が raw storage であり storage format は変更しないことを明記した。
- empty high-level dependency は保存可能だが open/unknown では node blocker、done/closed/all-descendant-done では satisfied dependency として扱うことを明記した。
- disabled/cycle path は fail-closed placeholder であり partial readiness authority として読まないことを明記した。

#### 実行コマンド / 結果
```bash
git diff --name-only
# S90 allowed docs 4 files only

diff -u src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md
# no diff

diff -u src/spec_dock/assets/spec_dock/docs/reference_sync.md spec-dock/docs/reference_sync.md
# no diff

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S90 | Red / Inspect | inspect-only | docs previously described `deps-issues` as todo issue-only and `deps_ref_expanded_to_empty` as warning-only context | `rg` inspection | pass | S04 contract was not reflected in docs |
| S90 | Green | inspect-only + reviewer | provider/mirror docs aligned; spec-reviewer pass with no findings | `diff -u`; `git diff --check`; spec-reviewer | pass | docs-only step, runtime tests not run |
| S90 | Refactor | guardrail satisfied | diff limited to provider docs and dogfooding mirror docs | `git diff --name-only` | pass | no workflow/source/test changes |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S90 | `tc-s90-001`, `tc-s90-002`, `cl-ac-006`, `cl-ec-004` | provider docs explain node blockers/satisfied dependencies/authority boundary, mirror status recorded, spec-reviewer pass recorded | provider/mirror docs aligned; spec-reviewer pass; S90 commit confirmed by post-commit `git log --oneline -6` | pass | post-commit clean check passed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s90-001` | S90 | yes | inspect-only | stale docs wording before S90 | docs diff inspection and spec-reviewer | pass | provider docs define readiness authority |
| `tc-s90-002` | S90 | yes | inspect-only | mirror docs stale before S90 | provider/mirror `diff -u` | pass | dogfooding mirror intentionally aligned |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac-006` | S90 | provider/mirror docs diff and spec-reviewer | pass | docs and tests fix the new contract |
| `cl-ec-004` | S90 | docs wording for `deps-raw` raw/debug authority | pass | `deps-raw` is not readiness authority |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S90 | N/A | N/A | plan の S90 closure ids で対応 | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S90 | delegated | docs mutation under issue execution workflow | doc-writer | Docs Impact Resolution And Dogfooding Mirror | `plan.md` S90 | provider docs and generated mirror docs | workflow/source/test changes, broad unrelated docs rewrite | docs diff inspection and `git diff --check` | docs require workflow semantics or broad scaffold refresh | changed files, provider/mirror alignment, verification, risks, ledger note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S90 | doc-writer | Updated dependency and sync reference docs for node blockers, satisfied dependencies, deps-issues v2, deps-raw raw/debug boundary, and mirror alignment. | `src/.../reference_deps.md`; `src/.../reference_sync.md`; `spec-dock/docs/reference_deps.md`; `spec-dock/docs/reference_sync.md` | `git diff --check` pass; provider/mirror `diff -u` no diff | spec-reviewer pass | runtime tests not run for docs-only step | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S90 | step reviewer | spec-reviewer | fresh | passed | N/A | proceed to commit gate | No findings; reviewer confirmed storage/readiness/raw authority wording and mirror alignment |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S90 | closed | S90 docs plus this report evidence | current S90 commit confirmed by `git log --oneline -6` after commit | `git status --short` clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md` - provider dependency semantics
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md` - provider sync artifact contract
- `spec-dock/docs/reference_deps.md` - dogfooding mirror dependency semantics
- `spec-dock/docs/reference_sync.md` - dogfooding mirror sync artifact contract
- `spec-dock/active/issue/report.md` - S90 observed evidence ledger

#### コミット
- `docs(deps): 依存ビューのauthority境界を更新` committed; final hash confirmed by post-commit `git log --oneline -6`

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider docs and dogfooding mirror docs | yes | doc-writer | `reference_deps.md` / `reference_sync.md` provider and mirror aligned; `git diff --check` pass | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
