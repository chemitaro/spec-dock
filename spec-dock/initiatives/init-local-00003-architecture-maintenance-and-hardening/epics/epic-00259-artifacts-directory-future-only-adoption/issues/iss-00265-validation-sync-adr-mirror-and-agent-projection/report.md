---
種別: 実装報告書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
関連GitHub: ["#265"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00265 Validation sync ADR mirror and agent projection — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | implementation | orchestrator / system-architect | validation に artifact filename guard をどこで接続するか | `validate_tree.py` use case; `domain/validation.py` graph validation; artifact parser rewrite | `domain/validation.py` に artifact validator を追加し、既存 discussion validation の後に接続する | `domain/artifacts.py` に filename / duplicate scan helper があり、validation layer が graph-level diagnostics を集約しているため | promoted_to_design | `design.md` DES-265-001..004 / `plan.md` S01-S02 | follow-up なし |
| D-002 | resolved | implementation | orchestrator / system-architect | ADR mirror の future artifact ADR をどう既存 mirror と統合するか | mirror writer rewrite; source collector expansion; artifact ADR migration | source collector を `discussions/` + `artifacts/` に広げ、writer/preflight contract は維持する | original を移動しない AC を守りつつ、既存 basename collision preflight を source 全体に適用できる | promoted_to_design | `design.md` DES-265-005..007 / `plan.md` S03 | follow-up なし |
| D-003 | resolved | compatibility | orchestrator / implementation-planner | `.agent` projection で canonical docs / artifacts / discussions をどう区別するか | existing key rename; separate top-level index; additive node field | node payload に additive `document_surfaces` field を追加する | 既存 consumers を壊さず AC-265-005 の distinct labels を満たせる | promoted_to_design | `design.md` Projection schema / `plan.md` S04 | `iss-00267` で docs/skills guidance に反映 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | sub-agent `system-architect` | `design.md`, `plan.md` | design が薄いという fail 判定を受け、artifact validation seam、ADR mirror source expansion、projection additive schema、non-goals を採用した | `/private/tmp/iss-00265-system-architect.md` / `design.md` DES-265-001..010 | fresh spec-reviewer |
| EAL-002 | adopted | sub-agent `implementation-planner` | `plan.md` | executable plan と stop conditions を採用し、S00..S99、closure index、focused tests、delegation contract へ反映した | `/private/tmp/iss-00265-implementation-planner.md` / `plan.md` S00..S99 | fresh spec-reviewer |
| EAL-003 | adopted | command / source inspection | `design.md`, `plan.md` | current runtime の validation / artifact parser / sync ADR mirror / JSON projection structure を自力確認し、specialist output を repo reality に照合した | `sed` inspection of `validation.py`, `artifacts.py`, `sync_state.py`, `json_state.py`, focused tests | fresh spec-reviewer |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | validate / sync / ADR mirror / projection を artifacts-aware にし、canonical docs / artifacts / discussions を混同しない設計を `design.md` と `plan.md` に固定 | docs/skills guidance 全面更新は `iss-00267` に残し、この Issue は runtime surface と tests に集中 | low | conditional_pass; procedural report row update only |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `requirement.md` approved; Epic ADR and dependencies `iss-00263` / `iss-00264`確認 | なし | adopted | passed | no | execute approved plan |
| design | `validation.py`, `artifacts.py`, `sync_state.py`, `json_state.py`, focused tests; system-architect evidence | projection field name and ADR mirror source boundary を design で確定 | adopted | passed | no | execute approved plan |
| plan | implementation-planner evidence; closure/test mapping; stop conditions | なし | adopted | passed | no | execute approved plan |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | passed | execute manual-authored canonical docs |

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
- `validate` に artifact filename / duplicate validation を接続し、legacy `discussions/` validation と future `artifacts/` validation を独立した diagnostics として扱うようにした。
- ADR mirror source discovery を `discussions/` と `artifacts/` の両方へ拡張し、`.agent` / sync projection には additive `document_surfaces` を追加して canonical docs / future artifacts / legacy discussions を区別した。
- current-future projection の raw dependency exposure は広げず、full-history projection の既存 `depends_on` 契約は維持した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 implementation / review）

#### 対象
- Step: S01, S02, S03, S04, S90, S99
- AC/EC: AC-265-001, AC-265-002, AC-265-003, AC-265-004, AC-265-005
- 計画上の出典（Planned source）:
  - `plan.md` section: 実装ステップ S00..S99 / Spec-Locked Closure Index
  - closure ids: CLOS-265-001..CLOS-265-011

#### 実施内容
- S01: `domain/validation.py` に artifact filename / duplicate validation を接続し、`artifacts/` がある node だけを対象に `scan_artifact_duplicate_state()` を実行した。
- S02: old-only / new-only / mixed layout validate pass と artifact malformed / duplicate diagnostics の CLI runtime tests を追加した。
- S03: `application/sync_state.py` の ADR mirror source collector を `discussions/` と `artifacts/` の独立走査へ拡張し、artifact ADR のみ mirror source に採用した。
- S04: `presentation/json_state.py` の node payload に additive `document_surfaces` を追加し、projection tests で canonical docs / future artifacts / legacy discussions の区別を確認した。
- S90/S99: docs/skills guidance 全面更新は計画どおり後続 `iss-00267` に残し、code-reviewer / qa-reviewer が pass した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_validate.py -q
# 38 passed, 6 skipped

uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror or projection or index" -q
# 9 passed, 49 deselected

uv run pytest tests/cli_runtime/test_sync.py -q
# 26 passed, 2 skipped

git diff --check
# pass

./spec-dock/scripts/spec-dock assurance verify
# ok

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=171

uv run pytest tests/cli_runtime -q
# 721 passed, 76 skipped
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing + new negative diagnostics | artifact validation 未接続なら malformed / duplicate artifact tests が fail する | `tests/cli_runtime/test_validate.py` inspection / focused pytest | pass | CLI runtime negative tests added |
| S01 | 緑フェーズ（Green） | artifact filename / duplicate guard connected | malformed artifact filename and duplicate artifact id fail with artifact diagnostics | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | 38 passed, 6 skipped |
| S02 | 緑フェーズ（Green） | old-only / new-only / mixed validate pass | three layout cases pass validate | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | AC-265-001 |
| S03 | 緑フェーズ（Green） | ADR mirror reads discussions and artifacts | legacy discussion ADR and future artifact ADR are mirrored; originals remain | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror or projection or index" -q` | pass | 9 passed, 49 deselected |
| S04 | 緑フェーズ（Green） | additive projection schema | `document_surfaces` separates canonical docs, future artifacts, legacy discussions | `uv run pytest tests/cli_runtime/test_sync.py -q` and focused unit lane | pass | dependency exposure boundary preserved |
| S01-S04 | リファクタリング（Refactor） | guardrail satisfied | no unrelated source surface changed beyond approved files | code-reviewer r2 / `git diff --check` | pass | reviewer_status: pass |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S04 | full-history projection の既存 `depends_on` 契約を追加テストが誤って `[]` と期待 | code-reviewer r1 | `index_todo` では raw `depends_on` 非露出、`index_all` では `["iss-local-00002"]` 維持へ assertion を修正 | CLOS-265-010 | no | code-reviewer r1 fail, dev-coder fix, r2 pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01-S02 | CLOS-265-001, CLOS-265-002, CLOS-265-003 | old-only / new-only / mixed layouts validate | `tests/cli_runtime/test_validate.py -q` | pass | 38 passed, 6 skipped |
| S01-S02 | CLOS-265-004, CLOS-265-005, CLOS-265-006 | malformed artifact, duplicate artifact, and legacy discussion diagnostics are distinct and strict | `validation.py`; `tests/cli_runtime/test_validate.py -q` | pass | artifact validator connected after discussion validator |
| S03 | CLOS-265-007, CLOS-265-008, CLOS-265-009 | ADR mirror reads both surfaces, preserves originals, and fails mixed-source basename collision before write | `tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror or projection or index" -q` | pass | 9 passed, 49 deselected |
| S04 | CLOS-265-010, CLOS-265-011 | additive `document_surfaces`; dependency exposure not expanded | `tests/cli_runtime/test_sync.py -q`; focused unit lane; code-reviewer r2 | pass | full-history existing raw `depends_on` preserved |
| S99 | CLOS-265-001..011 | broader CLI runtime and reviewers pass | `uv run pytest tests/cli_runtime -q`; code-reviewer pass; qa-reviewer pass | pass | 721 passed, 76 skipped |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CLOS-265-001 | S01-S02 | yes | red-required | old-only layout case added | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | `discussions/` without `artifacts/` validates |
| CLOS-265-002 | S01-S02 | yes | red-required | new-only layout case added | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | `artifacts/` without `discussions/` validates |
| CLOS-265-003 | S01-S02 | yes | red-required | mixed layout case added | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | both surfaces validate |
| CLOS-265-004 | S01-S02 | yes | red-required | malformed artifact negative case added | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | artifact diagnostic wording verified |
| CLOS-265-005 | S01-S02 | yes | red-required | duplicate artifact negative case added | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | duplicate artifact id diagnostic verified |
| CLOS-265-006 | S01-S02 | yes | covered-existing | legacy discussion tests existed and still pass | `uv run pytest tests/cli_runtime/test_validate.py -q` | pass | strictness unchanged |
| CLOS-265-007 | S03 | yes | covered-existing + extended | legacy discussion ADR mirror remains covered | focused unit lane | pass | legacy source remains mirrored and original remains |
| CLOS-265-008 | S03 | yes | red-required | artifact ADR source added to collector/mirror tests | focused unit lane | pass | future artifact ADR mirrored and original remains |
| CLOS-265-009 | S03 | yes | red-required | mixed-source basename collision test updated | focused unit lane | pass | preflight prevents write |
| CLOS-265-010 | S04 | yes | red-required | projection label assertions added | `uv run pytest tests/cli_runtime/test_sync.py -q` | pass | canonical docs / artifacts / discussions separated |
| CLOS-265-011 | S04/S99 | yes | regression boundary | reviewer r1 found expectation mismatch; fixed | code-reviewer r2 / focused unit lane / `uv run pytest tests/cli_runtime -q` | pass | todo hides raw `depends_on`; all preserves it |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-265-001 | S01-S02 | `test_validate.py::test_validate_accepts_old_new_and_mixed_document_surfaces` | pass | old-only case |
| CLOS-265-002 | S01-S02 | `test_validate.py::test_validate_accepts_old_new_and_mixed_document_surfaces` | pass | new-only case |
| CLOS-265-003 | S01-S02 | `test_validate.py::test_validate_accepts_old_new_and_mixed_document_surfaces` | pass | mixed case |
| CLOS-265-004 | S01-S02 | `test_validate.py::test_validate_rejects_malformed_artifact_filename_with_artifact_diagnostic` | pass | artifact diagnostic |
| CLOS-265-005 | S01-S02 | `test_validate.py::test_validate_rejects_duplicate_artifact_id_with_artifact_diagnostic` | pass | duplicate artifact id |
| CLOS-265-006 | S01-S02 | legacy discussion malformed/duplicate tests | pass | strictness unchanged |
| CLOS-265-007 | S03 | ADR mirror source/symlink tests | pass | legacy discussion ADR mirrored and original remains |
| CLOS-265-008 | S03 | ADR mirror source/symlink tests | pass | future artifact ADR mirrored and original remains |
| CLOS-265-009 | S03 | ADR basename collision test | pass | mixed-source before-write failure |
| CLOS-265-010 | S04 | sync projection tests | pass | `document_surfaces` separates surfaces |
| CLOS-265-011 | S04/S99 | code-reviewer r2, projection assertions, broader CLI runtime | pass | dependency boundary preserved |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | CLOS-265-001..011 | test names in changed files | CLOS-265-001..011 | plan closure index unchanged | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/b4d4/spec-dock` | iss-00265 | current session | system-architect / implementation-planner / spec-reviewer / dev-coder / code-reviewer / qa-reviewer | same repo, active issue, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S04 | delegated | multi-layer runtime / shipped scaffold / validation + sync + projection integration | dev-coder | implement `plan.md` S01-S04 only | `requirement.md`, `design.md`, `plan.md` | validation.py, sync_state.py, json_state.py, focused tests | node migration, `new artifact` semantics, `SpecNode` / `.meta.json`, broad docs/skills rewrite | focused validation / ADR mirror / sync tests, then broader cli runtime as needed | any stop condition in `plan.md`; reviewer fail | worker summary / changed files / verification / risks / integration decision | passed; one reviewer-found test expectation fixed by bounded dev-coder follow-up |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S04 | dev-coder | artifact validation hook, ADR mirror source expansion, additive `document_surfaces`, focused tests | `src/.../domain/validation.py`; `src/.../application/sync_state.py`; `src/.../presentation/json_state.py`; `tests/cli_runtime/test_validate.py`; `tests/cli_runtime/test_sync.py`; `tests/unit/presentation/test_runtime_sync_s07.py` | focused tests all pass; broader `tests/cli_runtime` pass | code-reviewer pass; qa-reviewer pass | none | accepted |
| S04-fix | dev-coder | code-reviewer r1 の指摘により full-history `depends_on` expectation を既存契約へ修正 | `tests/unit/presentation/test_runtime_sync_s07.py` | targeted test `1 passed` | code-reviewer r2 pass | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| 該当なし | implementation was delegated | no parent implementation exception | none | none | revert delegated commit/diff if needed | delegated tests and reviewers passed | code-reviewer / qa-reviewer passed | no waiver |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect / implementation-planner / manual fallback` | used | `/private/tmp/iss-00265-system-architect.md` and `/private/tmp/iss-00265-implementation-planner.md`; both integrated into design/plan | passed | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S00 | planning reviewer | spec-reviewer | fresh | passed | no | execute approved plan | Reviewer returned conditional_pass with no substantive requirement/design/plan blocker; procedural report row update completed |
| S01-S04 | implementation review r1 | code-reviewer | fresh | failed | no | fix reviewer finding | test expectation for full-history `depends_on` contradicted existing contract |
| S04-fix | implementation review r2 | code-reviewer | fresh | passed | no | complete implementation | no findings; focused and broader tests passed |
| S01-S04 | QA review | qa-reviewer | fresh | passed | no | complete implementation | AC coverage complete; broader CLI runtime passed |
| S99 | final spec review r1 | spec-reviewer | fresh | conditional_pass | no | fix report ledger mapping then re-review | implementation pass; report CLOS mapping and pending final rows required update |
| S99 | final spec review r2 | spec-reviewer | fresh | conditional_pass | no | update stale final spec review row then re-review | CLOS mapping resolved; no implementation/report mismatch; only final spec row freshness remained |
| S99 | final spec review r3 | spec-reviewer | fresh | passed | no | issue finish | no findings; stale pending row resolved; commit pending treated as non-blocking before commit |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S04/S99 | committed | issue 265 implementation + tests + issue report/design/plan evidence | final commit hash reported in final response | post-commit clean check after amend | N/A | N/A | N/A | reviewers passed |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - artifact filename / duplicate validation hook.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - ADR mirror source collection from `discussions/` and `artifacts/`.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - additive `document_surfaces` projection.
- `tests/cli_runtime/test_validate.py` - old/new/mixed layout and artifact diagnostics tests.
- `tests/cli_runtime/test_sync.py` - CLI sync projection assertions.
- `tests/unit/presentation/test_runtime_sync_s07.py` - ADR mirror and projection unit coverage.
- `spec-dock/.../iss-00265-.../{design.md,plan.md,report.md,.assurance.json}` - Issue planning/evidence updates.

#### コミット
- `feat(runtime): artifacts対応の検証と同期投影を追加`
- Final commit hash is reported in the orchestrator final response because amending the report changes the hash.

#### メモ
- `origin/main` merge request was checked during implementation; `git merge --autostash origin/main` reported already up to date.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no in this issue | N/A | broad docs/skills guidance is explicitly scoped to `iss-00267`; this issue changed runtime projection/validation only | conditional_pass; non-blocking deferral accepted |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added and sufficient | `/private/tmp/iss-00265-qa-review.md`; focused lanes and `uv run pytest tests/cli_runtime -q` | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | r1 found incorrect full-history `depends_on` test expectation; dev-coder fixed assertion; r2 no findings | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | r1 fixed CLOS ledger mapping; r2 confirmed mapping and implementation alignment; r3 no findings | 3 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| this report | issue 265 implementation, tests, planning evidence | final response / issue finish | ready |

## 遭遇した問題と解決 (任意)
- 問題: code-reviewer r1 で full-history projection の `depends_on` 期待値が既存契約と衝突していることを検出した。
  - 解決: current-future (`index.json`) では raw `depends_on` を出さず、full-history (`index-all.json`) では既存 `["iss-local-00002"]` を保持する assertion に修正した。

## 学んだこと (任意)
- dependency exposure boundary は projection 種別ごとの契約として明示的にテストする必要がある。

## 今後の推奨事項 (任意)
- `iss-00267` で docs/skills guidance を更新するとき、`document_surfaces` と ADR mirror source の説明を agent-facing docs に反映する。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
