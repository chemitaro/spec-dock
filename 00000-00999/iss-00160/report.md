---
種別: 実装報告書（Issue）
ID: "iss-00160"
タイトル: "Reduce Test Runtime Followup"
関連GitHub: ["#160"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00160 Reduce Test Runtime Followup — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

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
| D-001 | resolved | test-strategy | orchestrator + user | 日常 unit run の成功判定が未固定だった | Option A: 60 秒以内; Option B: 120 秒以内; Option C: 秒数なし | Option B を採用し、`tests/unit/` local runtime target を 120 秒以内に固定する | ユーザーが Option B を明示採用した。現状 full run 10:00.07 total から十分な改善を要求しつつ、1 issue の差分肥大化を避けやすい | applied | `discussions/20260605t075347z-interview-unit-runtime-target-clarification.md`; `requirement.md` | design / plan に同じ threshold を反映する |
| D-002 | resolved | test-strategy | user-shared external-agent discussion + ADR | Unit / integration 境界と heavy fixture 扱いを durable decision にする必要があった | Unit を純粋 in-process test のみに狭める; Unit を local/no external-service tests と定義する | Unit は local subprocess、tempdir、local git、stub `gh` を含む local/no external-service suite とし、real GitHub / remote git / network/auth は integration とする | ユーザー共有方針と ADR で採用済み。現状の遅延要因は外部通信ではなく local heavy fixture に集中している | promoted_to_adr | `discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`; `requirement.md` | なし |
| D-003 | resolved | implementation | dev-coder + orchestrator | S01 で空の `tests/unit` / `tests/integration` package だけを置くと Python 3.12 `unittest discover` が `NO TESTS RAN` で exit 5 になり、S01 の valid command 条件を満たせない | 空 package のまま exit 5 を許容する; S01 内の最小 discovery smoke test を追加する | `tests/unit/test_discovery.py` と `tests/integration/test_discovery.py` に package marker 存在確認だけの最小 smoke test を置く | S01 の目的は suite boundary と discovery command を有効化すること。production behavior や S02+ の実装には触れず、exit 0 の客観証跡を作れる | applied | `python -m unittest discover -s tests/unit`; `python -m unittest discover -s tests/integration`; code-reviewer `019e977f-71c7-7232-8bed-6e15b2fcf9f5` | なし |
| D-004 | resolved | implementation | dev-coder | S02 で `UNKNOWN` GitHub state を minimal fixture に含めたとき、既存 domain behavior は non-`CLOSED` GitHub state を effective `open` として扱う | Production status semantics を変更する; S02 では既存 semantics を明示して fixture contract だけを固定する | S02 では production behavior を変えず、`UNKNOWN` snapshot は `source=github` / `effective_status=open`、missing issue は `source=unknown` / `effective_status=unknown` としてテストに固定する | S02 は fake `gh` fixture contract の step であり、status semantics 変更はスコープ外。既存 behavior を明示することで coverage loss を防ぐ | applied | `tests/unit/infra/test_fake_gh_harness.py::TestFakeGhHarness.test_state_variations_use_minimal_fixture` | なし |
| D-005 | resolved | implementation | dev-coder + orchestrator | S03 で `tests/test_init_update.py` を `tests/unit/infra/test_init_update.py` に移動した後、既知の checked-in dogfooding `.meta.json` snapshot divergence が unit/infra failure として表面化した | failure を EC-004 として残す; assertion を弱める; 現行 checked-in dogfooding tree に snapshot baseline を同期する | `tests/unit/infra/test_init_update.py` の fixed snapshot だけを現行 checked-in dogfooding `.meta.json` path set / `depends_on` baseline に同期する | AC-002 で unit suite を 120 秒以内に pass させる必要があり、snapshot同期は既存 contract を弱めず現物と baseline を一致させる最小修正 | applied | `python -m unittest tests.unit.infra.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`; `python -m unittest discover -s tests/unit` | なし |
| D-006 | resolved | test-strategy | code-reviewer + orchestrator | S05 の初回レビューで、一部 CLI tests が direct unit replacement より広い integration semantics を持つまま skip されていた | Unit coverage を増やして skip を維持する; 該当 CLI tests を smoke として残す | semantic coverage が unit replacement だけで同等でない 18 件の CLI skip を解除し、該当 behavior は retained CLI smoke として残す | S05 の目的は heavy coverage split であり、coverage loss は許容しない。重いが意味的に固有な CLI behavior は削らず、明確に smoke として維持する | applied | code-reviewer initial fail / re-review pass; `python -m unittest tests.cli_runtime.test_delegated_authoring tests.cli_runtime.test_active` -> OK, skipped=53 | S06 以降も overbroad skip を避ける |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | source_role | claim | 対象（target） | target_section | 判断理由（rationale） | evidence_strength | 証跡（evidence_path） | adopter | reviewer | blocking | 次アクション（next_action） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | `20260605t045222z-research-test-runtime-measurement-analysis.md` | research | Full suite が 10:00.07 total で、slow files と fixture hotspots は local heavy fixture / subprocess に集中する | `requirement.md` / `design.md` / `plan.md` | 背景・現状; AC; implementation priority | Local measurement は現状 runtime、slow file、fixture hotspot の客観証跡であり、scope / AC / implementation priority の根拠に使える | high | `discussions/20260605t045222z-research-test-runtime-measurement-analysis.md` | orchestrator | spec-reviewer requirement pass | no | design / plan に反映 |
| EAL-002 | adopted | `20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md` | sub-agent: deep-consultant | Root cause は post-mutation sync、default 10000 fake `gh`、repeated init/subprocess が中心である | `requirement.md` / `design.md` / `plan.md` | 背景・現状; 設計方針; step priority | Deep consultant の root cause 分析は local measurement と整合し、優先対象にする根拠になる | medium-high | `discussions/20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md` | orchestrator | spec-reviewer requirement pass | no | design / plan に反映 |
| EAL-003 | adopted | `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md` | discussion + ADR | Unit / integration 境界と fixture strategy を issue-wide decision として固定する | `requirement.md` / `design.md` / `plan.md` | スコープ; 非交渉制約; design structure | User-shared 方針を ADR として受け入れ、Unit / integration 境界と fixture strategy を issue-wide contract として採用した | high | `discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md` | orchestrator | spec-reviewer requirement pass | no | design / plan に反映 |
| EAL-004 | adopted | `20260605t075347z-interview-unit-runtime-target-clarification.md` | discussion: interview | Option B を採用し、`tests/unit/` target を 120 秒以内にする | `requirement.md` / `design.md` / `plan.md` | AC-002; verification threshold; final gate | ユーザーが Option B を採用し、unit runtime target を 120 秒以内に固定した | high | `discussions/20260605t075347z-interview-unit-runtime-target-clarification.md` | orchestrator | spec-reviewer requirement pass | no | design / plan に反映 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective は日常 test feedback loop の短縮であり、`tests/unit/` 120 秒以内を AC-002 に固定した | Test directory reorganization、fixture strategy、CLI smoke/direct logic split は速度目標を満たすための副次要件として AC-001/003/004 に固定した | low | requirement / design / plan review pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `20260605t045222z-research-test-runtime-measurement-analysis.md`; `20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md`; `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`; active initiative/epic/issue docs | `20260605t075347z-interview-unit-runtime-target-clarification.md` answered: Option B, 120 秒以内 | adopted | passed: spec-reviewer `019e96d7-12e9-7940-aeb9-ba9107caa1bd`; non-blocking P2 EAL completeness fixed in this report revision | no | promote to design |
| design | `requirement.md`; `design.md`; runtime layer inventory; test inventory; `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md` | requirement phase completed | adopted | initial failed: spec-reviewer `019e96db-3b7c-72e1-8f2b-f73b6c7cf465`; re-review passed: spec-reviewer `019e96dd-e9df-7b00-ba1e-a01872969515` | no | promote to plan |
| plan | `requirement.md`; `design.md`; `plan.md`; closure index; S01-S06/S90/S99 contracts | design phase completed | adopted | initial failed: spec-reviewer `019e96e1-3a61-7f33-8795-ef43091e40d7`; re-review passed: spec-reviewer `019e96e3-cb79-7873-ad06-bd86c36e5050`; non-blocking mapping suggestion applied | no | promote to implementation |

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
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-05 S01）

#### 対象
- Step: S01 — Unit / Integration Discovery Boundary
- AC/EC: AC-001, AC-005 partial
- 計画上の出典（Planned source）:
  - `plan.md` section:
    - `実装ステップ S01 — Unit / Integration Discovery Boundary`
  - closure ids:
    - `tc-s01-001`
    - `tc-s01-002`

#### 実施内容
- `tests/unit/{cli,commands,application,domain,infra,presentation}` と `tests/integration/{github,git_remote}` の discoverable package boundary を追加した。
- Python 3.12 の empty suite が exit 5 になるため、S01 の範囲内で `tests/unit/test_discovery.py` と `tests/integration/test_discovery.py` に最小 discovery smoke test を追加した。
- 直前の中途委任で混入した S03 相当の test move は戻し、既存 `tests/domain_runtime/**`、`tests/presentation_runtime/**`、`tests/test_cli.py`、`tests/test_init_update.py` が元の位置で動作することを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -s tests/unit
# Ran 1 test in 0.000s
# OK

python -m unittest discover -s tests/integration
# Ran 1 test in 0.000s
# OK

python -m unittest discover -s tests -p 'test_cli.py'
# Ran 3 tests in 0.232s
# OK

python -m unittest discover -s tests/domain_runtime
# Ran 83 tests in 0.138s
# OK

python -m unittest discover -s tests/presentation_runtime
# Ran 49 tests in 0.294s
# OK

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | `tc-s01-001` red-required | empty `tests/unit` / `tests/integration` は `NO TESTS RAN` で exit 5 | `python -m unittest discover -s tests/unit`; `python -m unittest discover -s tests/integration` | pass | 最小 smoke test が必要と判断 |
| S01 | 緑フェーズ（Green） | `tc-s01-001` | unit / integration discovery が各 1 test で exit 0 | `python -m unittest discover -s tests/unit`; `python -m unittest discover -s tests/integration` | pass | package marker smoke のみ |
| S01 | 緑フェーズ（Green） | `tc-s01-002` covered-existing | root fallback の代表 test discovery が維持される | `python -m unittest discover -s tests -p 'test_cli.py'` | pass | full run は S99 で実施 |
| S01 | リファクタリング（Refactor） | guardrail satisfied | production code / existing assertions / S02+ scope 変更なし | `git diff --check`; diff inspection | pass | S01 のみ |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | Python 3.12 `unittest discover` は empty suite を exit 5 にする | dev-coder / orchestrator | discovery smoke test を追加 | `tc-s01-001` | no | `tests/unit/test_discovery.py`; `tests/integration/test_discovery.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `tc-s01-001` | unit / integration discover command が valid | `python -m unittest discover -s tests/unit` -> OK; `python -m unittest discover -s tests/integration` -> OK | pass | 各 suite に最小 smoke test 1 件 |
| S01 | `tc-s01-002` | full fallback remains available | `python -m unittest discover -s tests -p 'test_cli.py'` -> OK | pass | full fallback 全体は S99 で再確認 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s01-001` | S01 | yes | red-required | empty suite は exit 5 | `python -m unittest discover -s tests/unit`; `python -m unittest discover -s tests/integration` | pass | 最小 smoke test 追加後 exit 0 |
| `tc-s01-002` | S01 | yes | covered-existing | existing root `test_cli.py` | `python -m unittest discover -s tests -p 'test_cli.py'` | pass | fallback command remains available |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s01-001` | S01 | unit / integration discovery commands | pass | no import/discovery error |
| `tc-s01-002` | S01 | root targeted discovery | pass | full fallback preserved |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s01-001` | `tests/unit/test_discovery.py`; `tests/integration/test_discovery.py` | `tc-s01-001` | S01 の valid discovery command を満たす最小 smoke | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction: implementation by plan; step-by-step with review then commit | `/Users/iwasawayuuta/.codex/worktrees/af4e/spec-dock` | iss-00160 | current session | dev-coder, code-reviewer | same repo, active issue, S01 only; no destructive action / publishing before PR step / credentialed access | issue complete / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | test suite boundary implementation | dev-coder | S01 only | `plan.md` S01 | `tests/unit/**`, `tests/integration/**` | production code, S02+ work, existing test moves | unit/integration discovery, diff check | discovery cannot be valid without scope expansion | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | unit / integration discover boundary と最小 smoke test を追加 | `tests/unit/**`; `tests/integration/**` | unit/integration discovery -> pass; `git diff --check` -> pass | code-reviewer `019e977f-71c7-7232-8bed-6e15b2fcf9f5` pass | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit | reviewer `019e977f-71c7-7232-8bed-6e15b2fcf9f5` |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | `tests/unit/**`, `tests/integration/**`, `report.md` S01 evidence | `94334fba7057bb5bd7eeb0476858cd6874af48af` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/unit/__init__.py` - Unit suite package marker。
- `tests/unit/{cli,commands,application,domain,infra,presentation}/__init__.py` - Unit layer package markers。
- `tests/unit/test_discovery.py` - Unit discovery smoke。
- `tests/integration/__init__.py` - Integration suite package marker。
- `tests/integration/{github,git_remote}/__init__.py` - Integration boundary package markers。
- `tests/integration/test_discovery.py` - Integration discovery smoke。
- `report.md` - S01 evidence ledger。

#### コミット
- `94334fba7057bb5bd7eeb0476858cd6874af48af` `test(spec): テスト境界の計画とS01足場を追加`

#### メモ
- No material implementation decisions beyond D-003.

---

### セッションログ（2026-06-05 S02）

#### 対象
- Step: S02 — fake `gh` Fixture Contract
- AC/EC: AC-003, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section:
    - `実装ステップ S02 — fake gh Fixture Contract`
  - closure ids:
    - `tc-s02-001`
    - `tc-s02-002`
    - `tc-s02-003`
    - `tc-s02-004`

#### 実施内容
- `CliRuntimeHarness._make_default_gh_issue_list_stub` の default `gh issue list` を 1..10000 生成から 3 件の static fixture に変更した。
- `--gh-limit=10000` は `sync --gh-limit 10000` と `issue_index_raw(..., limit=10000)` の argv capture で検証した。
- Large issue number は `number: 10000` の 1 件 fixture で検証した。
- open / closed / unknown / missing は 3 件 fixture と missing node で検証した。

#### 実行コマンド / 結果
```bash
python -m unittest discover -s tests/unit/infra
# Ran 4 tests in 1.445s
# OK

python -m unittest tests.cli_runtime.test_sync.TestCliSync.test_sync_github_passes_gh_limit_to_gh
# Ran 1 test in 1.400s
# OK

python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_github_index_incomplete_warns_and_blocks tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_github_blocked_when_dep_open
# Ran 2 tests in 2.990s
# OK

python -m unittest discover -s tests/unit
# Ran 5 tests in 1.521s
# OK

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S02 | 赤フェーズ / 代替証跡（Red / alternative） | `tc-s02-001` red-required | 旧 default fake `gh` は `range(1, 10001)` で 10000 件を生成 | code inspection; targeted test before fix | pass | dev-coder が旧 harness で targeted test failure を確認 |
| S02 | 緑フェーズ（Green） | `tc-s02-001`〜`tc-s02-004` | fake `gh` fixture contract tests 4 件 OK | `python -m unittest discover -s tests/unit/infra` | pass | small fixture / argv / large number / state variations |
| S02 | 緑フェーズ（Green） | `tc-s02-002` | CLI `sync --gh-limit 10000` が `--limit 10000` を渡す | `python -m unittest tests.cli_runtime.test_sync.TestCliSync.test_sync_github_passes_gh_limit_to_gh` | pass | 既存 CLI contract を 10000 に更新 |
| S02 | 緑フェーズ（Green） | regression guard | deps GitHub incomplete / open blocker tests OK | `python -m unittest tests.cli_runtime.test_deps...` | pass | default fixture shrink の周辺回帰確認 |
| S02 | リファクタリング（Refactor） | guardrail satisfied | production code 変更なし、S03+ 移動なし | `git diff --check`; diff inspection | pass | S02 のみ |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | `UNKNOWN` GitHub state は既存 semantics では effective `open` になる | dev-coder | D-004 として既存 behavior を明示し、production semantics は変更しない | `tc-s02-004` | no | `tests/unit/infra/test_fake_gh_harness.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | `tc-s02-001` | default fake `gh issue list` returns small fixture, not 10000 records | `test_default_fake_gh_issue_list_returns_small_fixture` | pass | 3 件 fixture |
| S02 | `tc-s02-002` | `--gh-limit=10000` is verified by captured argv | `test_issue_index_raw_captures_large_limit_argv`; `test_sync_github_passes_gh_limit_to_gh` | pass | `--limit 10000` |
| S02 | `tc-s02-003` | issue `number: 10000` behavior uses minimal fixture | `test_large_issue_number_uses_minimal_fixture` | pass | 1 件 fixture |
| S02 | `tc-s02-004` | missing / unknown / open / closed behavior represented with minimal fixtures | `test_state_variations_use_minimal_fixture` | pass | 3 件 fixture + missing node |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s02-001` | S02 | yes | red-required | old default 10000 records | `python -m unittest discover -s tests/unit/infra` | pass | routine default no longer 10000 |
| `tc-s02-002` | S02 | yes | red-required | old CLI limit test used 123, not 10000 | unit infra + CLI sync focused test | pass | captured argv contract |
| `tc-s02-003` | S02 | yes | red-required | large number coverage was implicit in large fixture | `python -m unittest discover -s tests/unit/infra` | pass | `number: 10000` one fixture |
| `tc-s02-004` | S02 | yes | red-required | state variation not explicit in default small fixture contract | `python -m unittest discover -s tests/unit/infra` | pass | open / closed / unknown / missing |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s02-001` | S02 | `tests/unit/infra/test_fake_gh_harness.py` | pass | default small fixture |
| `tc-s02-002` | S02 | `tests/unit/infra/test_fake_gh_harness.py`; `tests/cli_runtime/test_sync.py` | pass | argv capture |
| `tc-s02-003` | S02 | `tests/unit/infra/test_fake_gh_harness.py` | pass | large number minimal |
| `tc-s02-004` | S02 | `tests/unit/infra/test_fake_gh_harness.py` | pass | state variations minimal |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s02-001`〜`tc-s02-004` | `tests/unit/infra/test_fake_gh_harness.py` | `tc-s02-001`〜`tc-s02-004` | S02 計画通りの fixture contract closure | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | fake `gh` fixture contract implementation | dev-coder | S02 only | `plan.md` S02 | harness and targeted fake gh tests | production code, S03+ moves, unrelated rewrites | unit infra, focused sync/deps, unit discover, diff check | production behavior change required | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | default fake `gh` を small fixture 化し、limit / large number / state variation tests を追加 | `tests/cli_runtime/harness.py`; `tests/cli_runtime/test_sync.py`; `tests/unit/infra/test_fake_gh_harness.py` | unit infra, focused sync/deps, unit discover, diff check -> pass | initial code-reviewer `019e9788-e963-7ab2-a686-e075db0a8215` failed due report missing | none | accepted after report evidence added; re-review required |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | failed | no | re-review required | reviewer `019e9788-e963-7ab2-a686-e075db0a8215`; code diff acceptable, report evidence missing |
| S02 | step reviewer re-review | code-reviewer | fresh | passed | N/A | proceed to commit | reviewer `019e978d-b1a3-70d2-bc32-ab638a603e2c`; non-blocking P2 Windows skip fixed before commit |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S02 | committed | `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_sync.py`, `tests/unit/infra/test_fake_gh_harness.py`, `report.md` S02 evidence | `e4e95547c630ca77cef5a0da3dd39414ec970328` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/harness.py` - default fake `gh issue list` を small fixture 化。
- `tests/cli_runtime/test_sync.py` - `--gh-limit=10000` argv contract へ更新。
- `tests/unit/infra/test_fake_gh_harness.py` - S02 fixture contract tests。
- `report.md` - S02 evidence ledger。

#### コミット
- `e4e95547c630ca77cef5a0da3dd39414ec970328` `test(runtime): fake gh fixtureを軽量化`

#### メモ
- No material implementation decisions beyond D-004.
- Reviewer P2 の Windows portability 指摘は `tests/unit/infra/test_fake_gh_harness.py` の `setUp()` skip で解消し、`python -m unittest discover -s tests/unit/infra`、`python -m unittest discover -s tests/unit`、`git diff --check` が pass。

---

### セッションログ（2026-06-05 S03）

#### 対象
- Step: S03 — Low-Risk Layer Placement
- AC/EC: AC-001, AC-005 partial
- 計画上の出典（Planned source）:
  - `plan.md` section:
    - `実装ステップ S03 — Low-Risk Layer Placement`
  - closure ids:
    - `tc-s03-001`

#### 実施内容
- `tests/domain_runtime/**` を `tests/unit/domain/**` へ移動した。
- `tests/presentation_runtime/**` を `tests/unit/presentation/**` へ移動した。
- `tests/test_cli.py` を `tests/unit/cli/test_cli.py` へ移動した。
- `tests/test_init_update.py` を `tests/unit/infra/test_init_update.py` へ移動した。
- 移動後に表面化した checked-in dogfooding snapshot divergence を、`tests/unit/infra/test_init_update.py` の fixed snapshot 期待値だけ現行 data に同期して解消した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.unit.infra.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json
# Ran 1 test in 0.043s
# OK

python -m unittest discover -s tests/unit/domain
# Ran 83 tests in 0.150s
# OK

python -m unittest discover -s tests/unit/presentation
# Ran 49 tests in 0.323s
# OK

python -m unittest discover -s tests/unit/cli
# Ran 3 tests in 0.243s
# OK

python -m unittest discover -s tests/unit/infra
# Ran 214 tests in 61.431s
# OK

python -m unittest discover -s tests/unit
# Ran 350 tests in 62.253s
# OK

git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=79
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S03 | 赤フェーズ / 代替証跡（Red / alternative） | `tc-s03-001` inspect-only | 低リスク tests は旧配置に存在 | file layout inspection | pass | move 前の配置確認 |
| S03 | 赤フェーズ / 代替証跡（Red / alternative） | unit infra verification | moved infra suite で dogfooding snapshot divergence が失敗 | targeted unittest before snapshot sync | pass | D-005 として記録 |
| S03 | 緑フェーズ（Green） | `tc-s03-001` | domain / presentation / cli / infra が unit 配下で pass | unit layer discover commands | pass | `tests/unit` 全体も 62.253s で OK |
| S03 | リファクタリング（Refactor） | guardrail satisfied | assertion weakening / skip / production change なし | diff inspection; `git diff --check` | pass | snapshot baseline の現行 data 同期のみ |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S03 | moved `test_init_update.py` で checked-in dogfooding snapshot divergence が unit infra failure になる | dev-coder / orchestrator | `tests/unit/infra/test_init_update.py` の snapshot baseline を現行 tree に同期 | `tc-s03-001` | no | +2 paths, -0 paths, +2 `depends_on: []` baseline entries |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S03 | `tc-s03-001` | domain/presentation/installer tests live under mapped Unit paths | `tests/unit/domain`, `tests/unit/presentation`, `tests/unit/cli`, `tests/unit/infra` discover all pass | pass | unit suite 350 tests OK |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s03-001` | S03 | yes | inspect-only | old paths under `tests/domain_runtime`, `tests/presentation_runtime`, root test files | unit layer discovery commands | pass | placement and behavior preserved |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s03-001` | S03 | unit/domain, unit/presentation, unit/cli, unit/infra, unit discover | pass | `tests/unit` 62.253s |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s03-001` | unit layer discover commands | `tc-s03-001` | S03 計画通りの placement closure | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | low-risk test placement | dev-coder | S03 only | `plan.md` S03 | listed test moves and import/package fixes | production code, fake gh, S04+ split | unit layer discover, diff check | assertions must be weakened | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S03 | dev-coder | low-risk tests を unit layer へ移動し、dogfooding snapshot baseline を現行 tree に同期 | `tests/unit/domain/**`; `tests/unit/presentation/**`; `tests/unit/cli/test_cli.py`; `tests/unit/infra/test_init_update.py` | unit layer discover, unit discover, diff check -> pass | code-reviewer `019e979f-f8ee-7080-bf38-d98044fd78ae` pass | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit | reviewer `019e979f-f8ee-7080-bf38-d98044fd78ae` |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S03 | committed | moved test files and `report.md` S03 evidence | `16d97a2dcbcc54ae87baa5ab0af14e985047d292` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/unit/domain/**` - domain runtime tests moved from `tests/domain_runtime/**`。
- `tests/unit/presentation/test_runtime_sync_s07.py` - presentation runtime tests moved from `tests/presentation_runtime/**`。
- `tests/unit/cli/test_cli.py` - CLI/test inventory contract moved from root tests。
- `tests/unit/infra/test_init_update.py` - installer/scaffold tests moved from root tests; dogfooding snapshot baseline synchronized。
- `report.md` - S03 evidence ledger。

#### コミット
- `16d97a2dcbcc54ae87baa5ab0af14e985047d292` `test(runtime): unit配下へ低リスクテストを配置`

#### メモ
- No material implementation decisions beyond D-005.

---

### セッションログ（2026-06-05 S04）

#### 対象
- Step: S04 - `deps` / `validate` Heavy Coverage Split
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S04 - deps / validate Heavy Coverage Split`
  - closure ids: `tc-s04-001`, `tc-s04-002`

#### 実施内容
- `deps check` の branch-heavy CLI tests 10 件を、application direct unit coverage へ移し、CLI 側は `@skip("S04: covered by Class.method")` で根拠先を明示した。
- `validate` の branch-heavy CLI tests 6 件を、application / domain / presentation direct unit coverage へ移し、CLI 側は `@skip("S04: covered by Class.method")` で根拠先を明示した。
- New unit tests:
  - `tests/unit/application/test_check_deps.py`
  - `tests/unit/application/test_validate.py`
  - `tests/unit/domain/test_deps.py`
- Production code changes: none.

#### 実行コマンド / 結果
```bash
$ git diff --check
# pass

$ python -m unittest tests.unit.application.test_check_deps tests.unit.application.test_validate tests.unit.domain.test_deps tests.unit.domain.test_runtime_domain_s03
# Ran 31 tests in 0.084s
# OK

$ python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_validate
# Ran 127 tests in 144.560s
# OK (skipped=16)

$ python -m unittest discover -s tests/unit
# Ran 362 tests in 58.125s
# OK

$ ./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=79
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S04 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing | split 前の `deps` / `validate` CLI characterization が存在 | diff / test file inspection | pass | 既存 CLI tests を heavy behavior の characterization として使用 |
| S04 | 緑フェーズ（Green） | `tc-s04-001`, `tc-s04-002` | direct unit coverage and retained CLI smoke pass | targeted unittest commands | pass | focused unit 31 tests 0.084s; CLI 127 tests 144.560s skipped=16 |
| S04 | リファクタリング（Refactor） | guardrail satisfied | production code change なし; skip refs all resolve | code-reviewer; mechanical skip reference check; `git diff --check` | pass | previous conditional_pass finding fixed |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S04 | skipped CLI tests require explicit replacement traceability | code-reviewer | each skip reason now uses `Class.method` and all 16 refs resolve to real tests | `tc-s04-001`, `tc-s04-002` | no | mechanical skip reference check 16/16 OK |
| S04 | `deps effective_depends_on` skip needed application-level coverage, not only domain coverage | code-reviewer | added application direct tests for issue/epic/initiative effective deps merge | `tc-s04-001` | no | `TestCheckDepsApplication.test_effective_depends_on_*` pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S04 | `tc-s04-001`, `tc-s04-002` | branch-heavy `deps` / `validate` behavior covered below CLI while representative CLI contract remains | direct unit tests pass; CLI smoke suite pass with 16 explicit skips; code-reviewer pass | pass | production unchanged |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s04-001` | S04 | yes | covered-existing + direct unit | existing `deps` CLI characterization | `python -m unittest tests.unit.application.test_check_deps tests.unit.domain.test_deps`; `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_validate` | pass | cache, github warning, status, blockers, effective deps coverage moved below CLI |
| `tc-s04-002` | S04 | yes | covered-existing + direct unit | existing `validate` CLI characterization | `python -m unittest tests.unit.application.test_validate tests.unit.domain.test_runtime_domain_s03`; `python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_validate` | pass | artifact/meta/linkage validation coverage moved below CLI |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s04-001` | S04 | `tests/unit/application/test_check_deps.py`; `tests/unit/domain/test_deps.py`; retained `tests/cli_runtime/test_deps.py` smoke | pass | CLI skip refs point to `TestCheckDepsApplication.*` |
| `tc-s04-002` | S04 | `tests/unit/application/test_validate.py`; `tests/unit/domain/test_runtime_domain_s03.py`; `tests/unit/presentation/test_runtime_sync_s07.py`; retained `tests/cli_runtime/test_validate.py` smoke | pass | CLI skip refs point to real `Class.method` tests |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s04-001` | deps direct unit coverage | `tc-s04-001` | S04 計画通りの deps heavy coverage split | no | yes, completed |
| none | `tc-s04-002` | validate direct unit coverage | `tc-s04-002` | S04 計画通りの validate heavy coverage split | no | yes, completed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S04 | delegated | test restructure and coverage split | dev-coder | S04 only | `plan.md` S04 | listed test files only | production code, S05+ changes, removing CLI smoke without replacement | targeted unit, targeted CLI, unit discover, diff check, validate | missing replacement coverage or reviewer fail | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S04 | dev-coder | deps/validate branch-heavy CLI tests を lower-layer direct tests へ分割し、skip reason で置換先を明示 | `tests/cli_runtime/test_deps.py`; `tests/cli_runtime/test_validate.py`; `tests/unit/application/test_check_deps.py`; `tests/unit/application/test_validate.py`; `tests/unit/domain/test_deps.py` | focused unit, targeted CLI, unit discover, diff check, validate -> pass | code-reviewer pass | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S04 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit | Findings none; skip references 16/16 OK; production unchanged |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S04 | committed | deps/validate test split and `report.md` S04 evidence | `c0c3fd5904f8cfc5fa0ef91d9ac481af47554cf9` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_deps.py` - heavy branch tests 10 件に replacement-aware skip を追加。
- `tests/cli_runtime/test_validate.py` - heavy branch tests 6 件に replacement-aware skip を追加。
- `tests/unit/application/test_check_deps.py` - deps check application direct coverage を追加。
- `tests/unit/application/test_validate.py` - validate tree / graph application direct coverage を追加。
- `tests/unit/domain/test_deps.py` - dependency domain direct coverage を追加。
- `report.md` - S04 evidence ledger。

#### コミット
- `c0c3fd5904f8cfc5fa0ef91d9ac481af47554cf9` `test(runtime): depsとvalidateのheavy coverageを分割`

#### メモ
- No production behavior changes.
- S04 は code-reviewer pass 後に最終確認コマンドを再実行済み。

---

### セッションログ（2026-06-05 S05）

#### 対象
- Step: S05 - delegated authoring / active Heavy Coverage Split
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S05 - delegated authoring / active Heavy Coverage Split`
  - closure ids: `tc-s05-001`, `tc-s05-002`

#### 実施内容
- `active set` の branch-heavy CLI tests を application / domain / infra direct unit coverage へ分割した。
- `delegated-authoring diff-guard` の branch-heavy CLI tests を domain direct unit coverage へ分割した。
- 初回 code-reviewer で 14 件の overbroad skip が指摘されたため、該当 CLI tests を smoke として復帰した。
- 再レビュー前に追加で 4 件の overbroad skip が指摘されたため、該当 CLI tests も smoke として復帰した。
- New unit tests:
  - `tests/unit/application/test_set_active.py`
  - `tests/unit/domain/test_active.py`
  - `tests/unit/infra/test_active_store.py`
- Production code changes: none.

#### 実行コマンド / 結果
```bash
$ git diff --check
# pass

$ python -m unittest tests.cli_runtime.test_delegated_authoring tests.cli_runtime.test_active
# Ran 86 tests in 29.674s
# OK (skipped=53)

$ python -m unittest tests.unit.application.test_set_active tests.unit.domain.test_active tests.unit.infra.test_active_store tests.unit.domain.test_delegated_authoring tests.unit.domain.test_deps
# Ran 35 tests in 0.094s
# OK

$ python -m unittest discover -s tests/unit
# Ran 372 tests in 58.635s
# OK

$ ./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=79
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S05 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing | split 前の active / delegated-authoring CLI characterization が存在 | diff / test file inspection | pass | 既存 CLI tests を heavy behavior の characterization として使用 |
| S05 | 緑フェーズ（Green） | `tc-s05-001`, `tc-s05-002` | direct unit coverage and retained CLI smoke pass | targeted unittest commands | pass | focused unit 35 tests 0.094s; CLI 86 tests 29.674s skipped=53 |
| S05 | リファクタリング（Refactor） | guardrail satisfied | production code change なし; overbroad skips restored to CLI smoke | code-reviewer fail then pass; `git diff --check` | pass | D-006: coverage loss prevention |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S05 | Some skipped CLI tests had broader semantics than the cited direct unit replacement | code-reviewer | 18 件の skip を解除し、該当 behavior を CLI smoke として保持 | `tc-s05-001`, `tc-s05-002`, D-006 | no | initial review fail; re-review pass |
| S05 | Remaining skip refs require semantic review, not only existence check | code-reviewer | remaining skips を code-reviewer が semantic adequacy review し pass | `tc-s05-001`, `tc-s05-002` | no | re-review pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S05 | `tc-s05-001`, `tc-s05-002` | branch-heavy active / delegated-authoring behavior covered below CLI while representative CLI contract remains | direct unit tests pass; retained CLI smoke suite pass with 53 explicit skips; code-reviewer pass | pass | production unchanged |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s05-001` | S05 | yes | covered-existing + direct unit | existing active CLI characterization | `python -m unittest tests.unit.application.test_set_active tests.unit.domain.test_active tests.unit.infra.test_active_store`; `python -m unittest tests.cli_runtime.test_active` | pass | active target resolution, deps guard, branch decision, active store coverage moved below CLI; unique CLI semantics retained |
| `tc-s05-002` | S05 | yes | covered-existing + direct unit | existing delegated-authoring CLI characterization | `python -m unittest tests.unit.domain.test_delegated_authoring`; `python -m unittest tests.cli_runtime.test_delegated_authoring` | pass | diff-guard domain coverage moved below CLI; unique CLI/baseline semantics retained |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s05-001` | S05 | `tests/unit/application/test_set_active.py`; `tests/unit/domain/test_active.py`; `tests/unit/infra/test_active_store.py`; retained `tests/cli_runtime/test_active.py` smoke | pass | overbroad active skips restored |
| `tc-s05-002` | S05 | `tests/unit/domain/test_delegated_authoring.py`; retained `tests/cli_runtime/test_delegated_authoring.py` smoke | pass | overbroad delegated-authoring skips restored |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s05-001` | active direct unit coverage + retained CLI smoke | `tc-s05-001` | S05 計画通りの active heavy coverage split | no | yes, completed |
| none | `tc-s05-002` | delegated-authoring direct domain coverage + retained CLI smoke | `tc-s05-002` | S05 計画通りの delegated-authoring heavy coverage split | no | yes, completed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S05 | delegated | test restructure and coverage split | dev-coder | S05 only | `plan.md` S05 | listed test files only | production code, S06+ changes, removing CLI smoke without replacement | targeted unit, targeted CLI, unit discover, diff check, validate | missing replacement coverage or reviewer fail | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S05 | dev-coder | active / delegated-authoring branch-heavy CLI tests を lower-layer direct tests へ分割し、semantic gap がある CLI tests は smoke として復帰 | `tests/cli_runtime/test_active.py`; `tests/cli_runtime/test_delegated_authoring.py`; `tests/unit/application/test_set_active.py`; `tests/unit/domain/test_active.py`; `tests/unit/infra/test_active_store.py` | focused unit, targeted CLI, unit discover, diff check, validate -> pass | code-reviewer pass after initial fail | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S05 | step reviewer | code-reviewer | fresh | failed | no | fix overbroad skips | initial review found 14 overbroad skips |
| S05 | step reviewer re-review | code-reviewer | fresh | failed | no | fix remaining overbroad skips | second review found 4 additional overbroad skips |
| S05 | step reviewer final re-review | code-reviewer | fresh | passed | N/A | proceed to commit | Findings none; production unchanged; remaining skips semantically adequate |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S05 | committed | active/delegated-authoring test split and `report.md` S05 evidence | `67e0bae10bebf57cdade446961f38a1ffb5efd34` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_active.py` - replacement-aware skip を追加し、semantic gap のある active CLI tests は smoke として保持。
- `tests/cli_runtime/test_delegated_authoring.py` - replacement-aware skip を追加し、semantic gap のある delegated-authoring CLI tests は smoke として保持。
- `tests/unit/application/test_set_active.py` - active set application direct coverage を追加。
- `tests/unit/domain/test_active.py` - active domain direct coverage を追加。
- `tests/unit/infra/test_active_store.py` - active store direct coverage を追加。
- `report.md` - S05 evidence ledger。

#### コミット
- `67e0bae10bebf57cdade446961f38a1ffb5efd34` `test(runtime): activeとdelegated authoringのheavy coverageを分割`

#### メモ
- No production behavior changes.
- S05 は code-reviewer pass 後に最終確認コマンドを再実行済み。

---

### セッションログ（2026-06-05 S06）

#### 対象
- Step: S06 - sync / new Split and 120 Second Measurement
- AC/EC: AC-001, AC-002, AC-004, EC-001
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S06 - sync / new Split and 120 Second Measurement`
  - closure ids: `tc-s06-001`, `tc-s06-002`, `tc-s06-003`, `tc-s06-004`

#### 実施内容
- `tests/cli_runtime/test_runtime_new_s08.py` を `tests/unit/commands/test_runtime_new_s08.py` へ移動し、移動先に合わせて runtime module root 計算を `parents[3]` に更新した。
- `tests/unit/cli/test_cli.py` の critical inventory / import を、移動後の `tests.unit.commands.test_runtime_new_s08` に合わせた。
- `tests/cli_runtime/test_new.py` の重い CLI runtime tests 5 件を replacement-aware skip に変更し、pre-GitHub validation / missing rules preflight / rules symlink materialization / default GitHub create mode / create-lock guidance は移動後 S08 の direct tests で受けた。
- `tests/cli_runtime/test_sync.py` の重い sync CLI runtime tests 2 件を replacement-aware skip に変更し、ADR mirror rebuild / artifact projection は既存 `tests/unit/presentation/test_runtime_sync_s07.py` で受けた。
- CLI parser / subprocess / filesystem 固有の代表 smoke、`new doc` 系、sync deps/status/GitHub stub/active integration smoke は CLI runtime 側に残した。
- Production code changes: none.

#### 実装前 / 実装後の測定
```bash
$ python -m unittest tests.cli_runtime.test_sync
# before S06: Ran 26 tests in 35.113s
# OK

$ python -m unittest tests.cli_runtime.test_new
# before S06: Ran 43 tests in 30.744s
# OK

$ python -m unittest tests.cli_runtime.test_runtime_new_s08
# before S06: Ran 47 tests in 0.769s
# OK

$ python -m unittest tests.unit.presentation.test_runtime_sync_s07
# before S06: Ran 49 tests in 0.302s
# OK
```

#### 実行コマンド / 結果
```bash
$ python -m unittest tests.unit.commands.test_runtime_new_s08 tests.unit.presentation.test_runtime_sync_s07 tests.unit.cli.test_cli
# Ran 99 tests in 1.129s
# OK

$ python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_sync
# Ran 69 tests in 53.177s
# OK (skipped=7)

$ /usr/bin/time -p python -m unittest discover -s tests/unit
# Ran 419 tests in 58.374s
# OK
# real 58.44
# user 25.33
# sys 23.52

$ rg -n "requests|urllib|httpx|socket|git fetch|git pull|git push|git ls-remote|ls-remote|gh issue (list|view|create)|subprocess\.|Popen|check_call|check_output|os\.system" tests/unit
# hits: existing local subprocess / fake gh harness tests only
# no real GitHub, remote git, auth, or network requirement found

$ ./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=79

$ git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S06 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing + measurement | split 前の `test_sync` / `test_new` runtime を測定 | targeted unittest measurement | pass | sync 35.113s; new 30.744s |
| S06 | 緑フェーズ（Green） | `tc-s06-001`, `tc-s06-002` | new S08 moved to unit/commands; sync S07 lower-layer coverage retained; CLI smoke pass | targeted unit + CLI commands | pass | lower-layer 99 tests 1.129s; CLI 69 tests 53.177s skipped=7 |
| S06 | 緑フェーズ（Green） | `tc-s06-003` | `tests/unit` local runtime <= 120s | `/usr/bin/time -p python -m unittest discover -s tests/unit` | pass | 419 tests, real 58.44s |
| S06 | リファクタリング（Refactor） | `tc-s06-004`, guardrail satisfied | production code change なし; unit external-boundary grep reviewed | diff inspection; `rg`; code-reviewer pass | pass | subprocess hits are local/unit-allowed tests |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S06 | `test_runtime_new_s08.py` は CLI runtime path にあったが、実体は fake ports / stub gateways による command/application direct coverage だった | dev-coder / code-reviewer | `tests/unit/commands/test_runtime_new_s08.py` へ移動し、path root のみ更新 | `tc-s06-002`, `tc-s06-004` | no | old/new diff は `parents[2]` -> `parents[3]` のみ |
| S06 | unit external-boundary grep は `subprocess.run` を検出する | orchestrator | Unit 定義上許可された CLI/local harness subprocess であり、real GitHub / remote git / auth / network の直接要求ではないことを確認 | `tc-s06-004` | no | `rg` inspection; code-reviewer pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S06 | `tc-s06-001` | sync split with representative CLI smoke retained | `tests/cli_runtime/test_sync.py` skip 2 件; `tests/unit/presentation/test_runtime_sync_s07.py` pass; `tests.cli_runtime.test_sync` included in CLI smoke pass | pass | ADR mirror / artifact projection moved below CLI |
| S06 | `tc-s06-002` | new split with representative CLI smoke retained | `tests/unit/commands/test_runtime_new_s08.py` pass; `tests.cli_runtime.test_new` included in CLI smoke pass | pass | preflight / default mode / lock guidance moved below CLI |
| S06 | `tc-s06-003` | unit runtime <= 120 seconds | `python -m unittest discover -s tests/unit` -> 419 tests, real 58.44s | pass | threshold 120s |
| S06 | `tc-s06-004` | no real external operations required by unit suite | `rg` inspection + code-reviewer pass | pass | subprocess hits are local/unit-allowed tests |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s06-001` | S06 | yes | covered-existing + direct unit | existing sync CLI characterization | `python -m unittest tests.unit.presentation.test_runtime_sync_s07`; `python -m unittest tests.cli_runtime.test_sync` | pass | sync direct coverage remains under unit/presentation; CLI smoke retained |
| `tc-s06-002` | S06 | yes | covered-existing + direct unit | existing new S08 characterization | `python -m unittest tests.unit.commands.test_runtime_new_s08`; `python -m unittest tests.cli_runtime.test_new` | pass | new S08 moved to unit/commands; CLI smoke retained |
| `tc-s06-003` | S06 | yes | measurement-required | S05 unit suite was 372 tests / 58.635s | `/usr/bin/time -p python -m unittest discover -s tests/unit` | pass | 419 tests / real 58.44s |
| `tc-s06-004` | S06 | yes | inspect-only + reviewer | unit suite boundary from requirement | `rg` inspection; code-reviewer review | pass | no real GitHub / remote git / auth / network requirement found |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s06-001` | S06 | `tests/unit/presentation/test_runtime_sync_s07.py`; retained `tests/cli_runtime/test_sync.py` smoke | pass | skipped CLI tests cite replacement-aware coverage |
| `tc-s06-002` | S06 | `tests/unit/commands/test_runtime_new_s08.py`; retained `tests/cli_runtime/test_new.py` smoke | pass | moved file is otherwise unchanged except path root |
| `tc-s06-003` | S06 | timed unit discover | pass | real 58.44s |
| `tc-s06-004` | S06 | external-boundary grep and code-reviewer pass | pass | subprocess usage is local/unit-allowed |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s06-001` | sync lower-layer coverage + retained CLI smoke | `tc-s06-001` | S06 計画通りの sync split | no | yes, completed |
| none | `tc-s06-002` | new S08 moved unit coverage + retained CLI smoke | `tc-s06-002` | S06 計画通りの new split | no | yes, completed |
| none | `tc-s06-003` | timed unit discover | `tc-s06-003` | S06 計画通りの 120 秒測定 | no | yes, completed |
| none | `tc-s06-004` | external-boundary grep | `tc-s06-004` | Unit boundary check completed | no | yes, completed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S06 | delegated | test restructure and runtime measurement | dev-coder | S06 only | `plan.md` S06 | sync/new tests and remaining hotspots | production code, S90/S99 changes, moving real external tests into unit | targeted unit, targeted CLI, unit discover timing, external-boundary grep, diff check, validate | missing replacement coverage, runtime > 120s, reviewer fail | changed files, commands, closure evidence, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S06 | dev-coder | new S08 を unit/commands へ移動し、sync/new の重い CLI tests を replacement-aware skip に整理 | `tests/cli_runtime/test_new.py`; `tests/cli_runtime/test_sync.py`; `tests/cli_runtime/test_runtime_new_s08.py`; `tests/unit/commands/test_runtime_new_s08.py`; `tests/unit/cli/test_cli.py` | targeted unit, targeted CLI, unit discover timing, external-boundary grep, diff check -> pass | code-reviewer pass | full discovery fallback は S99 で実行予定 | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S06 | step reviewer | code-reviewer | fresh | passed | N/A | proceed to commit | findings none; production unchanged; unit runtime 58.26s in reviewer run |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S06 | committed | sync/new test split and `report.md` S06 evidence | `bde4c597c87c3eaae86831c73f24ee43aa24b3e7` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_new.py` - replacement-aware skip 5 件を追加し、代表 CLI smoke は保持。
- `tests/cli_runtime/test_sync.py` - replacement-aware skip 2 件を追加し、代表 CLI smoke は保持。
- `tests/cli_runtime/test_runtime_new_s08.py` - unit/commands へ移動。
- `tests/unit/commands/test_runtime_new_s08.py` - 移動後の runtime root 計算を更新。
- `tests/unit/cli/test_cli.py` - critical inventory / import を移動後 path に更新。
- `report.md` - S06 evidence ledger。

#### コミット
- `bde4c597c87c3eaae86831c73f24ee43aa24b3e7` `test(runtime): syncとnewのheavy coverageを分割`

#### メモ
- No production behavior changes.
- S06 は code-reviewer pass 後に最終確認コマンドを再実行済み。

---

### セッションログ（2026-06-05 S90）

#### 対象
- Step: S90 - docs impact resolution / docs refresh
- AC/EC: AC-001, AC-005
- 計画上の出典（Planned source）:
  - `plan.md` section: `ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）`
  - closure ids: `tc-s90-001`

#### 実施内容
- `rg -n "unittest discover|tests/unit|tests/integration|python -m unittest" README.md docs src spec-dock tests` と reviewer follow-up の workflow-inclusive search を実行し、永続的な command guidance、workflow、履歴 issue records を分類した。
- 履歴 `spec-dock/initiatives/**/{requirement,design,plan,report,discussions}.md` の過去コマンド証跡は S90 更新対象外と判断した。
- 永続的な Testing guidance として `README.md` が stale で、旧 `python -m unittest discover -v` だけを案内していた。
- doc-writer に S90 限定で `README.md` Testing 節の最小更新を委任し、daily unit command、optional integration command、full regression fallback を記載した。
- 初回 spec-reviewer で `.github/workflows/provider-ci.yml` の stale provider CI command が指摘されたため、provider CI を daily unit command に合わせ、既存 assertion を更新した。
- Production code changes: none.

#### 実行コマンド / 結果
```bash
$ rg -n "unittest discover|tests/unit|tests/integration|python -m unittest" README.md docs src spec-dock tests
# README.md:182 had only `python -m unittest discover -v`
# historical spec-dock issue records also matched; classified as past evidence, not persistent command guidance

$ rg -n "python -m unittest discover -v|python -m unittest discover -s tests/unit|python -m unittest discover(\s|$)" README.md .github/workflows/provider-ci.yml docs src tests
# README.md:183:python -m unittest discover -s tests/unit
# README.md:186:python -m unittest discover -s tests/integration
# README.md:189:python -m unittest discover
# .github/workflows/provider-ci.yml:20:run: python -m unittest discover -s tests/unit
# tests/unit/infra/test_init_update.py:9564 asserts the same workflow command

$ rg -n "Testing|python -m unittest discover|tests/unit|tests/integration" README.md
# README.md:179:## Testing
# README.md:183:python -m unittest discover -s tests/unit
# README.md:186:python -m unittest discover -s tests/integration
# README.md:189:python -m unittest discover

$ git diff --check
# pass

$ python -m unittest tests.unit.infra.test_init_update.TestInitUpdate.test_issue_68_provider_only_workflow_is_not_shipped_via_install_root
# Ran 1 test in 0.000s
# OK
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S90 | 赤フェーズ / 代替証跡（Red / alternative） | `tc-s90-001` inspect-only | README Testing が full fallback 旧コマンドのみを案内 | `rg` inspection | pass | stale persistent docs found |
| S90 | 緑フェーズ（Green） | `tc-s90-001` | README Testing が unit / integration / full fallback を案内し、provider CI が unit command を実行する | README / workflow diff; `rg` inspection | pass | doc-writer updated README; dev-coder fixed workflow command |
| S90 | リファクタリング（Refactor） | guardrail satisfied | historical issue records は未変更; workflow assertion updated only for changed command | diff inspection; `git diff --check`; targeted unittest | pass | production source code changes none |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S90 | `rg` scope は historical issue records の古い commands を大量に検出する | orchestrator | 履歴 issue records は past evidence として分類し、永続 guidance の更新対象外とした | `tc-s90-001` | no | `rg` output classification |
| S90 | `.github/workflows/provider-ci.yml` が provider CI で旧 full discover command を使っていた | spec-reviewer | provider CI を `python -m unittest discover -s tests/unit` に更新し、既存 workflow assertion を同じ文字列に更新 | `tc-s90-001` | no | initial spec-review fail; targeted unittest pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S90 | `tc-s90-001` | docs/templates/workflow files mentioning test commands are consistent or no update needed | README updated; provider CI workflow updated; docs/src/spec-dock/templates command guidance had no stale persistent hits requiring change | pass | historical issue records left unchanged |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s90-001` | S90 | yes | inspect-only | README Testing and provider CI used old full discover guidance | `rg` inspection; README/workflow diff; targeted workflow assertion test; `git diff --check` | pass | README documents daily unit, optional integration, and full fallback; provider CI uses daily unit |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s90-001` | S90 | `README.md` Testing update; `.github/workflows/provider-ci.yml` update; `rg` verification; targeted workflow assertion test | pass | docs/workflow changed, spec-reviewer re-review required |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `tc-s90-001` | README Testing and provider CI command guidance | `tc-s90-001` | S90 計画通りの docs/workflow command consistency | no | yes, completed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S90 | delegated | persistent non-issue docs update | doc-writer | S90 only | `plan.md` S90 | README Testing command guidance | source code, tests, issue docs, historical issue records | README `rg`; `git diff --check` | stale docs require broader scope | changed files, validation, risks | pass |
| S90 | delegated | workflow reviewer fix | dev-coder | S90 reviewer fix only | `plan.md` S90 + spec-reviewer finding | `.github/workflows/provider-ci.yml`; one matching assertion in `tests/unit/infra/test_init_update.py` | README/report/source code/historical records/unrelated tests | targeted unittest; workflow-inclusive `rg`; `git diff --check` | stale workflow command remains | changed files, validation, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S90 | doc-writer | README Testing 節に daily unit / optional integration / full fallback commands を最小追記 | `README.md` | `rg` README command check; `git diff --check` -> pass | spec-reviewer re-review pass | none | accepted |
| S90 | dev-coder | provider CI の stale full discover command を daily unit command に更新し、既存 assertion を同期 | `.github/workflows/provider-ci.yml`; `tests/unit/infra/test_init_update.py` | targeted workflow assertion test; workflow-inclusive `rg`; `git diff --check` -> pass | spec-reviewer re-review pass | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S90 | docs reviewer | spec-reviewer | fresh | failed | no | fix workflow command guidance | initial review found stale `.github/workflows/provider-ci.yml` command and incomplete report inspection scope |
| S90 | docs reviewer re-review | spec-reviewer | fresh | passed | N/A | proceed to commit | findings none; previous workflow command finding fixed |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S90 | committed | README/workflow command updates, workflow assertion update, and `report.md` S90 evidence | `cf4115dcc270a99702b0b423c4c8405fc1fed75c` | `git status --short` -> clean after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `README.md` - Testing 節に daily unit / optional integration / full fallback commands を記載。
- `.github/workflows/provider-ci.yml` - provider CI を daily unit command に更新。
- `tests/unit/infra/test_init_update.py` - provider CI command assertion を更新。
- `report.md` - S90 evidence ledger。

#### コミット
- `cf4115dcc270a99702b0b423c4c8405fc1fed75c` `docs(test): unit実行コマンドの案内を更新`

#### メモ
- Production code changes none; one workflow assertion test was updated to match the S90 workflow command.
- Historical issue records の過去コマンド証跡は更新対象外。

### セッションログ（2026-06-05 S99）

#### 対象
- Step: S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004

#### 実施内容
- 最終品質ゲートとして whitespace / SpecDock validate / unit suite / full fallback discover を実行した。
- final QA / code / spec review は validation evidence 記録後に fresh reviewer で実施する。

#### 実行コマンド / 結果
```bash
git diff --check
# OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=79

/usr/bin/time -p python -m unittest discover -s tests/unit
# Ran 419 tests in 57.922s
# OK
# real 57.98
# user 24.89
# sys 22.89

python -m unittest tests.unit.cli.test_cli_smoke
# Ran 2 tests in 1.019s
# OK

python -m unittest discover -s tests/unit
# Ran 421 tests in 60.045s
# OK

/usr/bin/time -p python -m unittest discover
# Ran 1063 tests in 402.264s
# OK (skipped=76)
# real 402.35
# user 207.70
# sys 113.01
```

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| README / workflow / workflow assertion test | yes | doc-writer + dev-coder | `README.md` Testing section updated; `.github/workflows/provider-ci.yml` uses `python -m unittest discover -s tests/unit`; `tests/unit/infra/test_init_update.py` assertion updated; workflow-inclusive `rg` confirmed no stale default `discover -v` guidance | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | already sufficient; additional CLI smoke improves daily unit gate | QA reviewer pass; S99 validation: unit 419 tests / 57.98s; post-fix unit 421 tests / 60.045s; QA independent unit 419 tests / 62.96s; QA delta `tests.unit.cli.test_cli_smoke` 2 tests / 0.989s; full fallback 1063 tests / 427.542s; validate OK; diff check OK | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial fail: provider CI daily run executes `tests/unit`, while retained representative CLI subprocess smoke assertions remained only under `tests/cli_runtime`; fixed by adding focused `tests/unit/cli/test_cli_smoke.py` with argparse stderr/exit and successful runtime subprocess behavior using temp repo + stubbed `gh`; re-review findings none | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | findings none; non-blocking residual: `tests/cli_runtime` wording can be refined in a later cleanup issue | 0 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S99 validation evidence recorded; final reviewer evidence recorded | `tests/unit/cli/test_cli_smoke.py` and report final evidence | final response / PR | committed in final S99 commit |

### S99 Code Review Fail Fix Evidence
- 変更:
  - `tests/unit/cli/test_cli_smoke.py` を追加し、`CliRuntimeHarness` 経由で runtime subprocess smoke を `tests/unit` 配下から実行可能にした。
  - production code / README / CI workflow は変更していない。
- 検証:
  - `python -m unittest tests.unit.cli.test_cli_smoke` -> OK, 2 tests, 1.019s。
  - `python -m unittest discover -s tests/unit` -> OK, 421 tests, 60.045s。
  - `git diff --check` -> OK。
- 残リスク:
  - code-reviewer re-review pass。qa-reviewer delta re-review pass。spec-reviewer final pass。

### S99 Final Spec Review Evidence
- 判定:
  - spec-reviewer final review -> PASS。
- spec-reviewer 実行確認:
  - `git diff --check` -> OK。
  - `./spec-dock/scripts/spec-dock validate` -> OK, nodes=79。
  - `python -m unittest tests.unit.cli.test_cli_smoke` -> OK, 2 tests。
  - `/usr/bin/time -p python -m unittest discover -s tests/unit` -> OK, 421 tests, real 60.31s。
  - `python -m unittest discover -s tests/integration` -> OK, 1 test。
  - `/usr/bin/time -p python -m unittest discover` -> OK, 1065 tests, real 425.69s, skipped=76。
- 残リスク:
  - `design.md` には `tests/cli_runtime` 退役方向の文言が残る一方、実際には full fallback / retained CLI smoke として残っている。受け入れ条件上の blocker ではなく、次の整理 issue で文書表現を現運用へ寄せる候補。

## 遭遇した問題と解決 (任意)
- 問題: final code-review で、provider CI の daily unit gate が `tests/unit` のみを実行する一方、代表的な CLI subprocess smoke が `tests/cli_runtime` に残っていると指摘された。
  - 解決: `tests/unit/cli/test_cli_smoke.py` を追加し、argparse error contract と successful runtime subprocess contract を unit discovery で検証できるようにした。
- 問題: S90 spec-review で README と provider CI workflow の案内が不一致と指摘された。
  - 解決: `.github/workflows/provider-ci.yml` と対応 assertion を更新し、`README.md` の Testing 節と整合させた。

## 学んだこと (任意)
- daily unit gate を高速化する場合でも、CLI の代表 smoke は inventory/import だけではなく subprocess contract として unit 側に残す必要がある。

## 今後の推奨事項 (任意)
- full fallback は 6-7 分台まで短縮されたが、integration candidate の isolation と追加分割は別 issue で継続検討する。

## 省略/例外メモ (必須)
- 該当なし
