---
種別: 実装報告書（Issue）
ID: "iss-00141"
タイトル: "Remove Local Only Node Creation Option Surface"
関連GitHub: ["#141"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00141 Remove Local Only Node Creation Option Surface — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | user | node creation `--no-github` を parser-level removal にするか、dedicated contract error として残すかが未確定だった | Option A parser-level removal; Option B hidden dedicated reject; Option C current compatibility option | Option A を採用し、入力 option と内部 `no_github` / `local_only` plumbing を削除 scope に含める | ユーザー回答で Option A が明示され、accepted ADR の GitHub mandatory linkage と整合するため | applied | `discussions/20260530t081243z-interview-node-creation-no-github-surface-policy.md`; `requirement.md` | なし |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | main-orchestrator | source-grounded read identified node creation `--no-github` runtime / docs / tests / internal contract surface | `requirement.md` | 背景・現状 / スコープ / 受け入れ条件 | 調査結果が親 Epic / ADR / runtime / tests / docs と整合し、requirement の As-Is と scope 固定に必要だったため | strong | `discussions/20260530t081132z-research-local-only-node-creation-option-surface-research.md` | main-orchestrator | spec-reviewer pass on 2026-05-30 | no | design phase |
| EAL-002 | adopted | interview | user | Option A parser-level removal and internal logic cleanup are required | `requirement.md` | スコープ / 境界 / 前提 / 受け入れ条件 / 例外・エッジケース | ユーザー回答で `--no-github` の扱いと内部ロジック整理 scope が確定したため | strong | `discussions/20260530t081243z-interview-node-creation-no-github-surface-policy.md` | main-orchestrator | spec-reviewer pass on 2026-05-30 | no | design phase |
| EAL-003 | adopted | system-architect | read-only consultation sub-agent | design recommendations for parser-level removal, `github_mode` narrowing, local-only planning branch cleanup, docs/tests strategy, and `app.py` stale wording classification | `design.md` | 既存実装 / 採用方針 / 依存関係分析 / インターフェース契約 / テスト戦略 / ファイル変更計画 | requirement pass 後の read-only consultation として採用した。scope-local discussion draft は作成しておらず、Delegated Draft Evidence ではなくこの EAL entry と sub-agent final response を consultation provenance とする | strong | sub-agent `019e7803-ecbb-7480-a6f9-4cc68c23a983` final response; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`; `spec-dock/scripts/spec_dock_runtime/app.py` | main-orchestrator | spec-reviewer pass on 2026-05-30 | no | plan phase |
| EAL-004 | adopted | implementation-planner | read-only consultation sub-agent | plan recommendations for S01 runtime contract cleanup, S90 docs/scaffold refresh, S99 final quality gate, closure index, delegation contracts, and verification commands | `plan.md` | 依存関係から導く実装順序 / ステップ一覧 / 仕様固定クロージャ索引 / 実装ステップ / 最終完了条件 | approved requirement/design 後の read-only consultation として採用した。scope-local discussion draft は作成しておらず、Delegated Draft Evidence ではなくこの EAL entry と sub-agent final response を consultation provenance とする | strong | sub-agent `019e7810-1181-7403-a603-79bfe2d55d2d` final response | main-orchestrator | spec-reviewer pass on 2026-05-30 | no | execution handoff |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は node creation `--no-github` option surface と internal local-only plumbing removal を主要目的にしている | `sync` / `deps` / `active` の cache/local `--no-github` は保護対象として non-scope 化した | low | pass on 2026-05-30 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active issue docs, parent initiative/epic docs, accepted ADR, issue scratch, research artifact, interview artifact, `commands/new.py`, `application/create_node.py`, `application/contracts.py`, `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_wrappers.py`, provider docs | answered: Option A parser-level removal and internal logic cleanup adopted in `20260530t081243z-interview` | adopted into `requirement.md`; reviewer P2 finding about EAL field completeness fixed in report | passed by fresh spec-reviewer on 2026-05-30 | no | promote to design |
| design | approved `requirement.md`, system-architect read-only consultation, target runtime files including `app.py`, target tests, provider/dogfooding docs, accepted ADR | none | adopted into `design.md`; design reviewer P1 app.py boundary finding fixed; P2 provenance finding fixed by classifying EAL-003 as non-draft consultation | passed by fresh spec-reviewer on 2026-05-30 | no | promote to plan |
| plan | approved `requirement.md`, approved `design.md`, implementation-planner read-only consultation, issue plan authoring docs, issue workflow docs | none | adopted into `plan.md`; implementation-planner consultation classified as non-draft consultation in EAL-004; reviewer P3 provenance wording finding fixed in Delegated Draft Evidence section | passed by fresh spec-reviewer on 2026-05-30 | no | ready for execution handoff |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - not used
- 未使用の場合:
  - `system-architect` と `implementation-planner` は read-only consultation として使用した。scope-local discussion draft は作成していないため、委任ドラフト昇格証跡としては扱わず、EAL-003 / EAL-004 に consultation provenance と採用判断を記録する。
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
- S01 では node creation runtime から `--no-github` option surface と internal `local_only` planning branch を削除した。
- Provider runtime と dogfooding mirror を同期し、explicit `--no-github` は parser-level unsupported option として扱う。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-05-30 S01 Runtime Contract Cleanup）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-005, EC-001
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01 — Runtime Contract Cleanup`
  - closure ids: tc-001, tc-002, tc-003, tc-004, tc-007

#### 実施内容
- `commands/new.py` から node creation `--no-github` parser registration、args field、args factory plumbing、handler-level dedicated rejection helper を削除した。
- `CreateNodeRequest.github_mode` と `create_node.py` の mode handling を GitHub-backed create / link-existing のみへ狭め、local-only id allocation branch を削除した。
- Provider runtime と checked-in dogfooding mirror の該当 runtime files を同期した。
- `app.py` の stale node creation local-only wording を GitHub-backed wording に更新した。
- `tests/cli_runtime/test_new.py` を parser-level unsupported option expectation と help absence expectation に更新した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_new -v

Ran 43 tests in 28.024s
OK

rg -n -- "no_github|--no-github|local_only|Cannot combine" <S01 target files>

pass: node creation runtime plumbing hit none for no_github/local_only/--no-github.
allowed hits: '--id' GitHub-backed error, cache/local sync --no-github hints, tests for parser-level unsupported option, existing local-only projection test name.

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=71

git diff --check

pass: no output
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required for help absence and parser-level unsupported option; inspect-only for internal plumbing | tests updated to assert parser-level unsupported option and help absence; source inspection target fixed | test update and targeted source inspection | pass | Exact pre-change red run was not preserved because the delegated worker produced the first patch before returning; existing pre-change behavior was captured in requirement/design and prior tests expected dedicated contract errors. |
| S01 | 緑フェーズ（Green） | `python -m unittest tests.cli_runtime.test_new -v` | 43 tests passed | command | pass | Runtime behavior tests cover help absence, parser-level unsupported option, no fake gh invocation, and mutual-exclusion regression. |
| S01 | リファクタリング（Refactor） | guardrail satisfied / orphan cleanup only | removed orphan `no_github`, `_github_mandatory_error`, `_next_id`, local-only mode branch; no non-scope command option removed | diff inspection / targeted `rg` | pass | Remaining `--no-github` hits are state/cache hints or tests. |
| S90 | 赤フェーズ / 代替証跡（Red / alternative） | wrapper/init tests and targeted docs search expose stale wording before docs change | `tests.cli_runtime.test_wrappers` assertion updated; reviewer search found extra stale top-level docs and checked-in wrappers | affected tests plus reviewer-guided targeted `rg` | pass | Exact pre-change docs red was represented by existing expected string and reviewer findings. |
| S90 | 緑フェーズ（Green） | wrapper/init tests and docs classification pass | `tests.cli_runtime.test_wrappers` passed; `tests.test_init_update` full suite passed; targeted search/validate/diff-check passed | command | pass | One mistyped nonexistent unittest target failed and is not counted as product regression. |
| S90 | リファクタリング（Refactor） | stale wording cleanup only | root README scope-local wrapper guidance removed; stale top-level GitHub integration/sync docs updated; checked-in stale dogfooding wrappers deleted; provider/dogfooding docs kept aligned | diff inspection / targeted `rg` | pass | State/cache `--no-github` docs/tests preserved. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | delegated worker did not return final summary before shutdown, but left S01 target changes in working tree | orchestration | parent inspected and completed S01 within approved target scope; Parent Implementation Exception recorded | tc-001..tc-007 | no | git diff and targeted tests |
| S90 | initial reviewer pass failed because report lacked S90 closure traceability | spec-reviewer | added S90 gate/closure/test evidence rows and reran reviewer | tc-005..tc-007 | no | spec-reviewer `019e7853-b2f1-7543-9113-a6f9add9ea01` P1 |
| S90 | stale user-facing docs and checked-in dogfooding wrappers still taught or executed node creation `--no-github` | code-reviewer | updated `docs/github-issue-integration.md`, removed README wrapper guidance, deleted stale checked-in dogfooding `new-epic` wrappers | tc-005..tc-007 | no | code-reviewer `019e7853-c806-7392-8ae4-60312d098e39` P1 |
| S99 | residual local-id creation helper remained in `domain/ids.py` and legacy shim | final code-reviewer | removed provider/mirror `normalize_local_id_input`, removed legacy shim export/import, narrowed domain test to title/slug helper | tc-004 | no | code-reviewer `019e7862-9b80-70b3-9dd8-f294353cb7c5` P2; `python -m unittest tests.domain_runtime.test_runtime_domain_s01 tests.cli_runtime.test_new -v` -> pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-003, tc-004, tc-007 | public parser/help tests pass; internal cleanup inspection pass; provider/mirror runtime target files aligned; code-reviewer fresh pass | tests pass; inspection pass; fresh code-reviewer pass | pass | code-reviewer `019e7846-ea5e-7250-b101-91ab72483acf` returned `review_status: pass`. |
| S90 | tc-005, tc-006, tc-007 | affected docs/tests pass; targeted search classifies remaining `--no-github` / local-only / compatibility wording; provider and dogfooding docs aligned; fresh reviewers pass | wrapper tests pass; full init/update tests pass; stale docs/wrappers fixed after reviewer findings; fresh spec/code reviewer reruns passed | pass | spec-reviewer `019e785d-cb70-76b3-8f01-78d87b34570f` and code-reviewer `019e785e-22a5-7243-917f-88292e9548ba` returned `review_status: pass`. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | help test updated from prior help exposure behavior | `python -m unittest tests.cli_runtime.test_new -v` | pass | `test_new_node_help_does_not_expose_no_github` |
| tc-002 | S01 | yes | red-required | prior tests expected dedicated contract error | `python -m unittest tests.cli_runtime.test_new -v` | pass | parser-level `unrecognized arguments: --no-github` |
| tc-003 | S01 | yes | red-required | prior tests expected mutually exclusive error | `python -m unittest tests.cli_runtime.test_new -v` | pass | parser-level `unrecognized arguments: --no-github` |
| tc-004 | S01 | yes | inspect-only | known source hits in `commands/new.py`, `contracts.py`, `create_node.py` | targeted `rg` across S01 target files | pass | no node creation runtime `no_github` / `local_only` plumbing remains |
| tc-007 | S01 | yes | inspect-only | provider and mirror previously diverged during partial patch | provider/mirror files copied after provider patch; targeted `rg` hit classification | pass | runtime provider/mirror share same removal contract |
| tc-005 | S90 | yes | inspect-only / regression | valid state/cache `--no-github` contexts must remain | `python -m unittest tests.cli_runtime.test_wrappers -v`; targeted docs/search classification | pass | state/cache contexts intentionally preserved in docs/tests. |
| tc-006 | S90 | yes | inspect-only / docs regression | stale docs/tests expected node creation `--no-github` compatibility wording | targeted `rg`; `tests.cli_runtime.test_wrappers` | pass | reviewer-found stale `docs/github-issue-integration.md` and checked-in wrappers fixed. |
| tc-007 | S90 | yes | inspect-only / scaffold parity | provider/dogfooding docs and checked-in dogfooding metadata must align | `python -m unittest tests.test_init_update -v` | pass | provider/dogfooding docs parity and dogfooding metadata snapshot passed after S90 fixes. |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | `python -m unittest tests.cli_runtime.test_new -v` | pass | help absence and create/link options covered |
| tc-002 | S01 | `python -m unittest tests.cli_runtime.test_new -v` | pass | parser-level unsupported option covered |
| tc-003 | S01 | `python -m unittest tests.cli_runtime.test_new -v` | pass | no mutually exclusive error for `--create-github-issue --no-github` |
| tc-004 | S01 | targeted `rg` across S01 target files | pass | no `no_github` or `local_only` node creation runtime plumbing |
| tc-007 | S01 | provider/mirror file sync and targeted `rg` | pass | S90 still owns docs parity |
| tc-005 | S90 | wrapper tests and targeted docs/search classification | pass | preserve sync/deps/active cache/local `--no-github` semantics |
| tc-006 | S90 | targeted docs/search classification and reviewer-guided stale-doc cleanup | pass | no node creation compatibility option / dedicated rejection docs outside accepted historical issue records |
| tc-007 | S90 | provider/dogfooding docs parity tests and full init/update run | pass | includes checked-in dogfooding metadata snapshot and stale wrapper deletion |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | tc-001..tc-007 | N/A | tc-001..tc-007 | S01 closure contract unchanged | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-remove-local-only-node-creation` | iss-00141 | current session | dev-coder, doc-writer, spec-reviewer, code-reviewer, qa-reviewer | same repo, active issue, session, named roles; no destructive action / publishing / credentialed access / scope expansion | issue complete / session end / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated, then parent implementation exception | runtime / CLI / shipped scaffold mirror / tests | dev-coder | S01 allowed paths | `plan.md` S01 | S01 runtime provider/mirror and `tests/cli_runtime/test_new.py` | S90 docs, state/cache `--no-github`, migration, GitHub redesign | `python -m unittest tests.cli_runtime.test_new -v`; targeted `rg`; `validate`; `diff --check` | requirement/design conflict, allowed path expansion, parser-level unsupported option impossible | worker summary, changed files, verification, risks, Ledger Note | worker unavailable before final output; parent integrated observed S01 diff and recorded exception |
| S90 | delegated, then parent implementation exception | shipped docs / README / dogfooding docs / scaffold expectations | doc-writer | S90 allowed paths plus reviewer-found stale docs/wrappers | `plan.md` S90 | S90 docs/tests/scaffold evidence only | runtime code, state/cache `--no-github` semantics, workflow redesign | `python -m unittest tests.cli_runtime.test_wrappers -v`; `python -m unittest tests.test_init_update -v`; targeted `rg`; `validate`; `diff --check` | stale node creation local-only guidance remains, state/cache option removal required, allowed path expansion | worker summary, changed files, docs/search classification, tests, risks, Ledger Note | worker did not produce final output; parent completed bounded docs/scaffold refresh and responded to reviewer findings |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | worker was started for S01 but did not return final output before shutdown; partial working-tree changes were present | S01 target runtime files and `tests/cli_runtime/test_new.py` | not reported by worker | unavailable | no worker-provided Ledger Note | accepted after parent inspection, mirror sync, tests, and pending code-reviewer gate |
| S90 | doc-writer | worker was started for S90 but did not return final output before shutdown; no usable final summary was produced | none reported by worker | not reported by worker | unavailable | no worker-provided Ledger Note | accepted only after parent implementation, targeted tests/search, and fresh reviewer reruns |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | delegated worker did not provide final output after progress check and was shut down; parent had enough observed S01 diff to complete bounded integration | user requested issue execution with named worker/reviewer workflow; no extra risk waiver beyond executing approved S01 scope | S01 allowed paths from `plan.md` only | inspect, complete mirror sync, run tests, update report | revert S01 commit or restore files from previous commit if reviewer fails | `python -m unittest tests.cli_runtime.test_new -v` -> pass; targeted `rg` -> pass; `validate` -> pass; `git diff --check` -> pass | code-reviewer `019e7846e...` -> pass | unavailable handled as parent implementation exception, not as reviewer pass |
| S90 | delegated worker did not provide final output; parent had to address docs/scaffold refresh and reviewer findings directly within S90 scope | user requested issue execution with named worker/reviewer workflow; no extra risk waiver beyond approved S90 scope | S90 allowed paths from `plan.md`, plus stale top-level `docs/github-issue-integration.md` and checked-in dogfooding legacy wrappers discovered by review as user-facing stale node creation surfaces | update stale docs, remove stale dogfooding wrappers, run affected tests/search, update report | revert S90 commit or restore deleted wrappers/docs if reviewer fails | `python -m unittest tests.cli_runtime.test_wrappers -v` -> pass; `python -m unittest tests.test_init_update -v` -> pass; targeted `rg` -> pass; `validate` -> pass; `diff --check` -> pass | pending fresh reviewer reruns | unavailable handled as parent implementation exception, not as reviewer pass |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | no | proceed to S01 commit gate | code-reviewer `019e7846-ea5e-7250-b101-91ab72483acf`; no findings |
| S90 | step reviewer | spec-reviewer | fresh | passed | no | proceed to S90 commit gate | spec-reviewer `019e785d-cb70-76b3-8f01-78d87b34570f`; no findings |
| S90 | step reviewer | code-reviewer | fresh | passed | no | proceed to S90 commit gate | code-reviewer `019e785e-22a5-7243-917f-88292e9548ba`; no findings |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 runtime provider/mirror, `tests/cli_runtime/test_new.py`, S01 report evidence | `323e6725eaa932c8ed2eec71a9f65cef4970875c` | `git status --short` -> clean before S90 changes | N/A | N/A | N/A | N/A |
| S90 | committed | S90 docs/scaffold/tests/report evidence | `e11220a` | `git status --short` -> clean before S99 final fixes | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` - node creation `--no-github` parser/args/handler removal
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `github_mode` contract narrowing
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - local-only planning branch removal
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - stale node creation wording update
- `spec-dock/scripts/spec_dock_runtime/...` - provider runtime mirror sync
- `tests/cli_runtime/test_new.py` - parser-level unsupported option and help absence expectations
- `README.md`, `docs/github-issue-integration.md`, `docs/sync-aggregation.md` - user-facing stale node creation local-only guidance removal
- `src/spec_dock/assets/spec_dock/docs/...`, `src/spec_dock/assets/spec_dock/scripts/README.md` - shipped docs guidance update
- `spec-dock/docs/...`, `spec-dock/scripts/README.md` - dogfooding docs mirror update
- `spec-dock/initiatives/.../epics/new-epic` - stale checked-in dogfooding wrappers deleted
- `tests/cli_runtime/test_wrappers.py`, `tests/test_init_update.py` - docs/scaffold expectation update and checked-in dogfooding metadata snapshot update

#### コミット
- S01 committed as `323e6725eaa932c8ed2eec71a9f65cef4970875c`

#### メモ
- No material implementation decisions beyond the approved plan.

---

### セッションログ（2026-05-30 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer delegated, then parent implementation exception | root README, top-level docs, provider docs, dogfooding docs, scripts README, stale checked-in wrappers, wrapper/scaffold tests updated; `python -m unittest tests.cli_runtime.test_wrappers -v` -> pass; `python -m unittest tests.test_init_update -v` -> pass; targeted `rg` classified remaining `--no-github` hits as state/cache, explicit unsupported-option guidance, absence assertions, obsolete-fixture tests, or historical issue records; `./spec-dock/scripts/spec-dock validate` -> pass; `git diff --check` -> pass | pass: spec-reviewer `019e785d-cb70-76b3-8f01-78d87b34570f` |

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
