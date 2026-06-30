---
種別: 実装報告書（Issue）
ID: "iss-00251"
タイトル: "Enforce Fail Closed Issue Artifact Readiness Preflight"
関連GitHub: ["#251"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00251 Enforce Fail Closed Issue Artifact Readiness Preflight — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | spec-reviewer | R0 と G3 の evidence policy 境界が曖昧 | R0でevidence gateを実装する; R0はreadiness preflightに限定する | R0はartifact readiness preflightに限定し、grade-aware evidence policyはG3へ委譲する | Epic plan slices R0/G3 responsibilities separately | applied | plan.md; final spec re-review Kant pass | none |
| D-002 | resolved | operation | Epic final spec-reviewer | report scaffold / pending commit gate が Epic E-AC-006 closure evidence と矛盾 | Epic report claimを下げる; R0 reportを実績値へ補正する | R0 reportを実績値へ補正し、E-AC-006 closure evidenceとして使う | Issue #251 is implemented, committed, finished, and GitHub issue closed | applied | `c799ab93`; `issue finish`; Epic final spec review finding | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | spec-reviewer | requirement/design/plan/report | planning artifacts required R0/G3 scope clarification and executable closure evidence before implementation | Avicenna/Hilbert/Herschel findings; Kant pass | implemented and closed |
| EAL-002 | adopted | command/test evidence | report.md | Red/Green/focused/lint/validate evidence closes C-001〜C-099 | focused pytest rows; `make lint`; `git diff --check`; `spec-dock validate` | Epic final review |
| EAL-003 | adopted | Epic final spec-reviewer | report.md | stale scaffold / pending commit gate was valid P1 finding against Epic E-AC-006 closure claim | Pascal finding | repaired in this report |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | R0 fail-closed readiness classifier prevents unfinished artifacts from becoming execution-ready | G3 grade-aware evidence policy remains in separate issue | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement/design/plan | Epic #224 requirement/design/plan、`iss-00247` manual test follow-up、root-cause analysis、R0 issue draft一式、`./spec-dock/scripts/spec-dock guidance issue-planning` | blocking question なし。`REQ-XXX` / `CON-...` / `artifact_state: awaiting-assurance-compose` は未置換 placeholder ではなく、readiness detector が検出すべき sentinel 例として本文に残す。 | R0 scope を fail-closed artifact readiness preflight に限定し、G1〜G4 の guidance / draft routing / evidence / smoke を非対象として確定。requirement/design/plan を approved candidate として昇格。 | failed: fresh `spec-reviewer` returned two P1 findings. R0/G3 evidence-policy boundary was ambiguous and plan lacked executable step / closure evidence contract. | no | requirement/design/plan を修正し、fresh re-review を実行する |
| requirement/design/plan rework | Fresh spec-reviewer P1 findings、Epic R0/G1/G2/G3/G4 responsibility map、`plan.md` executable step contract requirement | blocking question なし。R0 は existing contract が必須化する evidence 欠落を generic block reason にできるだけで、grade-aware evidence policy 自体は G3 に残す。 | AC-006 / Evidence Readiness Predicate / M4 / B-005 を generic hook / no-op rationale に修正し、plan に S00〜S99 と C-001〜C-099 の executable step / closure contract を追加した。 | passed: fresh `spec-reviewer` returned findings none / `review_status: pass` / confidence 0.88. Runtime `guidance issue-execution` returned state ready after plan marker fix. | no | promote to issue execution |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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
- workflow readiness の fail-closed 判定を補強し、requirement の `REQ-XXX` / `CON-...` sentinel と、実装ステップを持たない品質ゲートのみの plan を execution ready にしないようにした。
- plan readiness では executable marker と quality/supporting marker を分離し、design readiness では本文中の ordinary word `template` / `placeholder` を block しない regression を追加した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 R0 実装）

#### 対象
- Step: S00, S01, S02, S03, S04, S90, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007
- 計画上の出典（Planned source）:
  - `plan.md` section: `7. 実装ステップ / 実行ステップ契約（Executable Step Contract）`
  - closure ids: C-001, C-002, C-003, C-004, C-090, C-099

#### 実施内容
- S00: `workflow.py` / `workflow_state.py` / 既存 workflow tests を確認し、readiness 判定が `_classify_plan_text`、`_classify_design_text`、`classify_requirement_text` に分散していることを確認した。
- S01: `classify_requirement_text` の placeholder markers に `REQ-XXX` と `CON-...` を追加した。
- S02: `_classify_plan_text` の executable marker から `validation gate` / `報告証跡` を外し、品質ゲート見出しだけの plan を executable と扱わないようにした。
- S02: fresh spec review の P1 指摘を受け、plan frontmatter の `artifact_state: awaiting-assurance-compose` と composite code-span placeholder を block する regression を追加した。
- S02: fresh re-review の P1 指摘を受け、table/list 内だけでなく standalone code span の `AC-...` も block する regression を追加した。
- S02: fresh re-review 2 の P1 指摘を受け、bare `...` code span は普通の記法として許容し、code span block は ID placeholder token に限定した。
- S03: design 本文・title 中の ordinary word `template` / `placeholder` が ready を妨げない regression test を追加した。既存の `artifact_state: awaiting-assurance-compose` block test は維持した。
- S04: R0 では grade-aware evidence policy を追加せず、既存 contract の readiness classifier に閉じる判断を維持した。
- S90: provider / dogfooding docs と active issue docs を `rg` で点検し、今回の R0 は runtime classifier と tests の更新で足りると判断した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

3 failed, 31 passed in 33.98s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

34 passed in 34.45s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

34 passed in 34.65s
```

```bash
uv run pytest tests/cli_runtime/test_workflow.py

3 failed, 30 passed in 38.24s
```

```bash
uv run pytest tests/cli_runtime/test_workflow.py

33 passed in 38.16s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

37 passed in 38.47s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

38 passed in 39.87s
```

```bash
uv run pytest tests/cli_runtime/test_workflow.py::TestCliWorkflow::test_guidance_blocks_standalone_plan_placeholder_code_span

1 failed in 1.26s
```

```bash
uv run pytest tests/cli_runtime/test_workflow.py::TestCliWorkflow::test_guidance_blocks_standalone_plan_placeholder_code_span

1 passed in 1.21s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

39 passed in 41.07s
```

```bash
uv run pytest tests/cli_runtime/test_workflow.py::TestCliWorkflow::test_guidance_allows_executable_plan_with_bare_ellipsis_code_span tests/cli_runtime/test_workflow.py::TestCliWorkflow::test_guidance_blocks_standalone_plan_placeholder_code_span

2 passed in 2.72s
```

```bash
uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py

40 passed in 41.91s
```

```bash
make lint

ruff check: pass
ruff format check: pass
mypy: pass
```

```bash
git diff --check

pass
```

```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=160
```

```bash
rg -n "REQ-XXX|CON-\\.\\.\\.|quality gate|Validation Gate|plan-not-executable|artifact_state: awaiting-assurance-compose|template|placeholder|readiness" src/spec_dock/assets/spec_dock/docs spec-dock/docs src/spec_dock/assets/spec_dock/templates spec-dock/templates spec-dock/active/issue

pass: active issue docs と provider/dogfooding docs/templates の関連記述を確認。追加 docs 更新は不要。
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（inspect-only） | 現行 readiness 判定の配置確認 | `_classify_plan_text`、`_classify_design_text`、`classify_requirement_text` を確認 | inspection | pass | 実装変更なし |
| S01 | 赤フェーズ（Red） | requirement sentinel block test | `REQ-XXX` / `CON-...` tests が `substantive` で失敗 | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | 2 件の想定 Red を確認 |
| S01 | 緑フェーズ（Green） | requirement sentinel block test | `REQ-XXX` / `CON-...` が `scaffold` になる | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | `workflow_state.py` markers 追加 |
| S02 | 赤フェーズ（Red） | quality-marker-only plan block test | test fixture title 制約修正後、旧実装では quality marker が executable marker に混在していた | test / inspection | pass | `validation gate` は supporting marker 扱いに変更 |
| S02 | 緑フェーズ（Green） | quality-marker-only plan block test | `plan-not-executable` で block | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | 実装ステップなし plan を ready にしない |
| S02 | 赤フェーズ（Red） | composite placeholder code-span block test / plan `artifact_state` block test | 追加 regression が `ready` で失敗 | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | fresh spec review P1-2 / P1-3 の再現 |
| S02 | 緑フェーズ（Green） | composite placeholder code-span block test / plan `artifact_state` block test | 追加 regression が `plan-not-executable` で pass | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | code-span token scan と plan frontmatter marker を追加 |
| S02 | 赤フェーズ（Red） | standalone code-span placeholder block test | `AC-...` を含む narrative code span が `ready` で失敗 | targeted pytest | pass | fresh re-review P1 の再現 |
| S02 | 緑フェーズ（Green） | standalone code-span placeholder block test | `AC-...` code span が `plan-not-executable` で pass | targeted pytest | pass | `_has_placeholder_code_spans` を追加 |
| S02 | 緑フェーズ（Green） | bare ellipsis code-span non-block regression | literal `...` code span と `AC-...` code span の境界を確認 | targeted pytest | pass | ID placeholder token のみに限定 |
| S03 | 赤フェーズ（Red） | title ordinary word non-block regression | substantive design title の `template` / `placeholder` が `design-not-substantive` で失敗 | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | fresh spec review P1-1 の再現 |
| S03 | 緑フェーズ（Green） | ordinary word non-block regression | substantive design body/title の `template` / `placeholder` が ready を妨げない | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | frontmatter の ordinary words を scaffold marker から除外 |
| S04 | 代替証跡（inspect-only） | G3 policy を R0 に持ち込まない | grade-aware evidence policy の新規定義なし | diff inspection | approved-no-op | runtime readiness predicate の範囲に閉じた |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | `--title` は hyphen を許可しないため、test fixture title を `Quality Only Plan` に修正する必要があった | implementation | test data correction | C-002 | no | Red run failure output |
| S95 | design title / plan artifact_state / composite code-span placeholder の 3 点に P1 指摘 | spec-reviewer | tests と runtime classifier を追加修正 | C-002 / C-003 | no | Avicenna review fail output |
| S95 | standalone code-span placeholder に P1 指摘 | spec-reviewer | targeted regression と `_has_placeholder_code_spans` を追加 | C-002 | no | Hilbert re-review fail output |
| S95 | bare ellipsis code span の過剰 block に P1 指摘 | spec-reviewer | code span detector を ID placeholder token のみに限定 | C-002 | no | Herschel re-review fail output |
| S04 | evidence policy の深掘りは G3 範囲に広がる | spec boundary | R0 では no-op として記録 | C-004 | no | `git diff` inspection |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | C-001〜C-004 | 現行判定の配置と既存 coverage を確認 | source / tests inspection | pass | 実装変更前調査完了 |
| S01 | C-001 | requirement placeholder sentinel block test | focused pytest 34 passed | pass | `REQ-XXX` / `CON-...` を追加 |
| S02 | C-002 | plan quality-marker-only and placeholder-cell block tests | focused pytest 40 passed | pass | composite / standalone code-span と plan `artifact_state` block、bare `...` non-block |
| S03 | C-003 | design explicit scaffold block and ordinary-word non-block regression | focused pytest 37 passed | pass | title/body ordinary words と `artifact_state` block を確認 |
| S04 | C-004 | G3 policy out-of-scope no-op rationale | diff inspection | approved-no-op | 新規 grade-aware evidence policy なし |
| S90 | C-090 | docs parity inspection and validate | `rg` inspection | pass | runtime/test 変更のみで docs 追加不要 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| C-001 | S01 | yes | red-required | 2 failing unit tests | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | Red: `REQ-XXX` / `CON-...` が substantive |
| C-002 | S02 | yes | red-required | quality marker が executable marker に含まれていた | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | `plan-not-executable` を確認 |
| C-003 | S03 | yes | regression | existing explicit scaffold block tests plus reviewer Red | `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` | pass | ordinary word non-block / plan `artifact_state` block tests 追加 |
| C-004 | S04 | yes | inspect-only | G3 境界の spec review 指摘 | diff inspection | approved-no-op | R0 は policy を追加しない |
| C-090 | S90 | yes | inspect-only | docs / templates related wording | `rg` inspection | pass | docs 更新不要 |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| C-001 | S01 | focused pytest | pass | requirement sentinel |
| C-002 | S02 | focused pytest | pass | quality-only plan block / placeholder code-span block |
| C-003 | S03 | focused pytest | pass | design false-positive prevention / plan `artifact_state` block |
| C-004 | S04 | diff inspection | approved-no-op | G3 policy out of scope |
| C-090 | S90 | `rg` inspection | pass | docs parity |
| C-099 | S99 | `make lint`; focused pytest; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | pass | final handoff gate |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | C-001〜C-090 | pytest / inspection | C-001〜C-090 | 計画された closure で充足 | no | S95 で fresh spec review を実行 |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S95 | final spec review | spec-reviewer | fresh | failed | no | rework completed; re-review required | reviewer: Avicenna / `019f1942-9b18-7882-9ff6-b4446d2eacf9`; P1 x3 |
| S95 | final spec re-review | spec-reviewer | fresh | failed | no | rework completed; re-review required | reviewer: Hilbert / `019f1949-51d1-7f30-95c7-0ab310c394d0`; P1 x1 |
| S95 | final spec re-review 2 | spec-reviewer | fresh | failed | no | rework completed; re-review required | reviewer: Herschel / `019f194e-0c9d-7531-af0b-4207efa67558`; P1 x1 |
| S95 | final spec re-review 3 | spec-reviewer | fresh | passed | no | proceed | reviewer: Kant / `019f1952-41b5-7001-9542-8971defe0330`; findings none |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S99 | committed | readiness classifier、regression tests、report evidence | `c799ab93` `fix(workflow): issue成果物の未完成判定をfail-closedに強化` | `git status --short` -> clean after commit / `issue finish` completed | N/A | N/A | N/A | N/A |

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no | N/A | runtime/test scoped change; docs parity inspection recorded in S90 | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | focused readiness regression sufficient for R0 | `make lint`; focused pytest; `git diff --check`; `./spec-dock/scripts/spec-dock validate`; final reviewer pass | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | no remaining blocker recorded in final issue handoff | 0 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | Avicenna/Hilbert/Herschel findings repaired; Kant final re-review had no findings | 3 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S00〜S99 closure, reviewer pass, verification commands, and commit gate recorded | `c799ab93` | Epic branch baton / final Epic PR evidence; GitHub Issue #251 closed by `issue finish` | committed |

## 遭遇した問題と解決 (任意)
- 問題: Epic final spec review で、R0 report に古い scaffold / pending commit gate が残っているため E-AC-006 closure evidence と矛盾すると指摘された。
  - 解決: 古い scaffold tail を削除し、S99 commit hash、post-commit clean / issue finish evidence、final quality gate を実績値へ更新した。

## 学んだこと (任意)
- Issue report の scaffold row は、Epic-level closure evidence では false blocker になる。Issue finish 後に commit gate と final gate を実績値へ閉じる必要がある。

## 今後の推奨事項 (任意)
- R0〜G4 のように Epic final gate で横断参照する Issue は、PR 前に report scaffold / pending row の残存を `rg` で検査する。

## 省略/例外メモ (必須)
- 該当なし
