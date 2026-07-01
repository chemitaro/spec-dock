---
種別: 実装報告書（Issue）
ID: "iss-00262"
タイトル: "Artifact templates and rules"
関連GitHub: ["#262"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00262 Artifact templates and rules — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | orchestrator / system-architect | Whether draft-* should have physical `templates/artifacts/draft-*.md` files. | Physical routing files; README/rules routing documentation only. | Use README/rules routing documentation only; do not create dedicated draft-only artifact template files. | User instruction and Epic ADR require reuse of existing requirement/design/plan templates and Issue profile-aware selection. | applied | `design.md`; `plan.md`; system-architect evidence | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | system-architect | design.md | Read-only specialist confirmed `iss-00262` should be bounded to provider templates/rules/catalog guidance and structural tests, with runtime command/preflight/scaffold changes deferred. | sub-agent `019f1cab-dc4f-7391-8208-e750f3d9e95d`; `design.md` | Fresh spec-reviewer gate. |
| EAL-002 | partially_adopted | implementation-planner | plan.md | Planner proposal was adopted for executable step shape, allowed/forbidden paths, concrete tests, and review gates. The suggestion to use physical draft routing files was rejected in favor of README/rules routing documentation. | sub-agent `019f1cac-07a1-76b2-85b1-73e079c13876`; `plan.md`; `D-001` | Fresh spec-reviewer gate. |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Provider-side artifact template/rules catalog is prepared for downstream `new artifact` implementation. | Runtime command, preflight, scaffold, validation, sync, and broad workflow docs are explicitly deferred to later Issues. | low | pass by spec-reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic ADR, Epic requirement/design/plan, approved Issue requirement. | none | Existing approved requirement remains authoritative; fresh spec-reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8` found no consistency concern. | pass | no | execute approved plan. |
| design | Provider templates, existing discussion templates, issue profile templates, provider rules docs, tests, system-architect read-only evidence. | Draft-* physical routing file question resolved in D-001. | Rewrote design as approved candidate with explicit boundaries and test strategy; fresh spec-reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8` P2 report evidence gap fixed. | pass | no | execute approved plan. |
| plan | Issue requirement/design, phase_plan_issue, authoring/issue-plan, implementation-planner evidence, existing tests. | none | Rewrote plan as approved candidate with executable step schema, concrete tests, delegation contracts, and final gates; fresh spec-reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8` P2 report evidence gap fixed. | pass | no | execute approved plan. |

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
| manual authoring | iss-00262 | none | active requirement/design/plan, Epic ADR | requirement.md, design.md, plan.md | not used | [] | manual authoring path | manual authoring canonical docs | none | none | pass | execute manual-authored canonical docs |

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
- Provider-side `templates/artifacts/` catalog、artifact rules、template README guidance を追加し、future `new artifact` surface の source contract を用意した。
- Draft requirement/design/plan は独自 artifact template file を作らず、既存 requirement/design/plan template と Issue profile-aware templates を再利用する routing-only contract として固定した。
- Focused structural tests により direct catalog、blank filename contract、ADR authority fields、legacy `discussions/` preservation、`scratch` exclusion を検証した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 implementation）

#### 対象
- Step: S01, S02, S03, S90, S99 pre-review checks
- AC/EC: AC-262-001 through AC-262-006
- 計画上の出典（Planned source）:
  - `plan.md` section: S01, S02, S03, S90, S99
  - closure ids: CLOS-262-001 through CLOS-262-006

#### 実施内容
- `doc-writer` `019f1cba-6c73-7630-9abf-bcb76c4c4342` に S01/S02 を委任し、provider-side artifact templates、template README guidance、scope rules docs を追加した。
- `doc-writer` の Ledger Note for `decision-candidate` template field shape は採用した。理由: accepted authority を主張せず、ADR でも canonical docs でもない採用前判断候補として薄い template に留まっており、approved plan と Epic ADR に整合するため。
- `dev-coder` `019f1cc0-1765-7e80-9e64-6520883e307c` に S03 を委任し、focused structural tests を追加した。
- S90 は provider-side docs/templates の範囲で完了し、dogfooding mirror refresh と broad workflow/docs/skills migration は後続 Issue の担当範囲として残した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_artifact_templates.py
# 6 passed in 0.01s

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=171

git diff --check
# pass

./spec-dock/scripts/spec-dock assurance verify --issue iss-00262
# assurance verify: ok; authorized_profile: standard; reason: ok

./spec-dock/scripts/spec-dock guidance issue-execution
# state: ready; next_action: execute-approved-plan; may_execute_approved_plan: true
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | Red / alternative | inspect-only before template addition | approved design/plan recorded `templates/artifacts/` absent or incomplete before S01/S02 | docs inspection | pass | runtime command changes not required |
| S01 | Green | direct catalog present | `templates/artifacts/{blank,research,interview,disc,decision-candidate,pr-repair-batch,adr}.md` present; no `draft-*` or `scratch.md` | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | CLOS-262-001, CLOS-262-002, CLOS-262-003, CLOS-262-006 |
| S02 | Red / alternative | inspect-only before rules/guidance addition | approved design/plan recorded artifact rules absence and README migration need | docs inspection | pass | no broad workflow docs migration |
| S02 | Green | rules/README guidance present | README/rules mention future `artifacts/`, issue-only draft routing, initiative/epic no-write fail-closed boundary, legacy `discussions/` preservation, no future `scratch` | `uv run pytest tests/unit/infra/test_artifact_templates.py`; focused `rg` inspection | pass | CLOS-262-004, CLOS-262-005 |
| S03 | Red | focused structural assertions | first dev-coder run observed 2 test failures due over-specific test wording; provider docs/templates were unchanged | delegated worker report | pass | test-only correction, no spec change |
| S03 | Green | focused structural test passes | `6 passed in 0.01s` | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | CLOS-262-001 through CLOS-262-006 |
| S03 | Reviewer fix Red | P1/P2 reviewer findings | focused pytest failed once after P1 docs correction because tests still expected initiative/epic draft routing wording | delegated worker report | pass | tests updated to new fail-closed contract |
| S03 | Reviewer fix Green | P1/P2 reviewer findings fixed | exact catalog assertion, ADR draft default assertion, issue-only draft boundary assertions pass | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | QA P2 and spec-reviewer P1s addressed |
| S90 | Inspect | docs impact bounded | provider templates/rules changed; mirror refresh and broad docs/skills migration deferred to later Issues | `./spec-dock/scripts/spec-dock validate`; focused path inspection | pass | no plan amendment |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | `decision-candidate` had no existing discussion template source | doc-writer | accepted thin decision-candidate template as pre-adoption decision artifact | CLOS-262-001 | no | `templates/artifacts/decision-candidate.md` |
| S03 | Initial test assertions were too narrow for backtick wording and design/plan co-mentions | dev-coder | corrected tests only; provider docs/templates unchanged | tc-s03-001, tc-s03-002 | no | delegated worker report; final focused pytest pass |
| S03 | Catalog test allowed unsupported extra templates | qa-reviewer | changed test to exact-set assertion for direct artifact template files | CLOS-262-001, CLOS-262-006 | no | `test_provider_artifact_template_catalog_is_direct_only_for_supported_types`; focused pytest pass |
| S01/S02/S03 | Initiative/Epic draft-* rules contradicted issue-only fail-closed contract | spec-reviewer | updated initiative/epic rules to unsupported issue-only no-write fail-closed; updated tests to assert scope split | CLOS-262-004, CLOS-262-005 | no | focused pytest pass; spec re-review pending |
| S01/S03 | ADR template defaulted draft files to accepted authority | code-reviewer/spec-reviewer | changed ADR template defaults to draft/non-mirror and tests to assert accepted fields are fill-after-acceptance guidance | CLOS-262-003 | no | focused pytest pass; spec re-review pending |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | CLOS-262-001, CLOS-262-002, CLOS-262-003, CLOS-262-004, CLOS-262-006 | direct template files and routing documentation exist; no runtime command changes | provider templates added; focused structural tests pass | pass | no `draft-*` physical artifact templates; catalog exact-set enforced |
| S02 | CLOS-262-004, CLOS-262-005 | artifact rules and README guidance present and tested/inspected | provider rules docs and README updated; focused structural tests pass | pass | legacy `discussions/` preservation and non-Issue draft fail-closed documented |
| S03 | CLOS-262-001 through CLOS-262-006 | focused test passes and maps to all closure rows | `uv run pytest tests/unit/infra/test_artifact_templates.py` -> 6 passed | pass | closure delta none; reviewer P1/P2 tests integrated |
| S90 | CLOS-262-005 | docs/mirror status recorded; no blocking docs impact remains | provider-side changes validated; mirror refresh not required for this Issue | pass | broad docs/skills migration remains `iss-00267` |
| S99 pre-review | CLOS-262-001 through CLOS-262-006 | focused tests, validate, diff check, assurance verify pass | focused pytest/validate/diff check/assurance verify pass | pass | final reviewer gates pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01/S03 | yes | structural test | design/plan characterization | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | direct catalog exists; no future `scratch` |
| tc-s01-002 | S01/S03 | yes | structural test | design/plan characterization | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | blank template identity and filename guidance |
| tc-s01-003 | S01/S03 | yes | structural test | design/plan characterization | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | ADR draft default and accepted-after-acceptance authority guidance represented |
| tc-s02-001 | S02/S03 | yes | structural test / inspection | design/plan characterization | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | artifact rules describe future surface |
| tc-s02-002 | S02/S03 | yes | structural test / inspection | design/plan characterization | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | README documents draft reuse and no future scratch |
| tc-s03-001 | S03 | yes | red/green structural test | initial dev-coder test run failed due test wording only | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | CLOS-262-001, CLOS-262-002, CLOS-262-006 |
| tc-s03-002 | S03 | yes | red/green structural test | initial dev-coder test run failed due test wording only; reviewer-fix run failed once due stale initiative/epic routing expectation | `uv run pytest tests/unit/infra/test_artifact_templates.py` | pass | CLOS-262-003, CLOS-262-004, CLOS-262-005 |
| tc-s90-001 | S90 | yes | inspect-only | N/A | `./spec-dock/scripts/spec-dock validate`; focused `rg` inspection | pass | docs impact remains bounded |
| tc-s99-001 | S99 | yes | final focused checks | S03 green evidence | focused pytest; validate; diff check; assurance verify | pass | final reviewer gates pending |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-262-001 | S01/S03 | `test_provider_artifact_template_catalog_is_direct_only_for_supported_types`; README test | pass | direct catalog exact set and routing docs covered |
| CLOS-262-002 | S01/S03 | `test_blank_artifact_template_records_identity_without_filename_token` | pass | blank filename contract covered |
| CLOS-262-003 | S01/S03 | `test_adr_artifact_template_supports_accepted_authority_and_mirror_surfaces` | pass | ADR draft default plus accepted-after-acceptance authority guidance covered |
| CLOS-262-004 | S01/S02/S03 | README/rules structural tests; negative draft file assertions | pass | issue-only draft routing and non-Issue fail-closed contract covered |
| CLOS-262-005 | S02/S03/S90 | rules structural tests; validate; focused inspection | pass | artifact rules, legacy preservation, and scope fail-closed boundary covered |
| CLOS-262-006 | S01/S03 | negative structural assertion for `scratch.md`; README/rules wording | pass | future `scratch` exclusion covered |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | CLOS-262-001 through CLOS-262-006 | tc-s01-001 through tc-s99-001 | same closure ids | planned test aliases matched closure index | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction to use sub-agents where useful | `/Users/iwasawayuuta/.codex/worktrees/b4d4/spec-dock` | iss-00262 | current session | doc-writer, dev-coder, qa-reviewer, code-reviewer, spec-reviewer | same repo, active issue, named role, bounded paths; no destructive action, publishing, credentialed access, or scope expansion | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01/S02 | delegated | persistent provider docs/templates change | doc-writer | provider artifact templates, template README, artifact rules docs | requirement/design/plan/Epic ADR | allowed S01/S02 provider docs/templates paths | runtime code, tests, existing discussion removal, broad workflow docs | docs-only inspection and changed files summary | need runtime wiring or broad docs migration | worker summary, changed files, verification, risks, Ledger Note | pass |
| S03 | delegated | focused test implementation | dev-coder | structural tests only | requirement/design/plan/Epic ADR | `tests/unit/infra/**` | runtime code, provider docs/templates, mirror, broad harness rewrite | focused pytest and diff check | need runtime implementation | changed files, red/green evidence, closure coverage | pass |
| S90 | parent inspection | docs impact decision | N/A | docs/mirror status | plan S90 | report evidence only | broad workflow/skill/docs migration | validate and focused inspection | mirror refresh required | inspection result and residual risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01/S02 | doc-writer `019f1cba-6c73-7630-9abf-bcb76c4c4342` | added provider artifact templates, README guidance, and artifact rules docs | `src/spec_dock/assets/spec_dock/templates/README.md`; `src/spec_dock/assets/spec_dock/templates/artifacts/*.md`; `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/artifacts.md` | focused `rg` inspection -> pass; forbidden surface status check -> clean | pending final reviewers | S03 tests and mirror status were pending at return; now addressed | accepted |
| S03 | dev-coder `019f1cc0-1765-7e80-9e64-6520883e307c` | added focused structural tests for provider artifact templates/rules | `tests/unit/infra/test_artifact_templates.py` | `uv run pytest tests/unit/infra/test_artifact_templates.py` -> 6 passed; `git diff --check` -> pass | pass by final QA/code/spec re-review | runtime implementation and mirror were intentionally unchanged | accepted |
| S01/S02 reviewer fix | doc-writer `019f1cca-70dc-74c1-aca8-b20b83df323c` | resolved spec-reviewer P1s for non-Issue draft fail-closed rules and ADR draft authority defaults | `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/artifacts.md`; `src/spec_dock/assets/spec_dock/templates/artifacts/adr.md`; `src/spec_dock/assets/spec_dock/templates/README.md` | focused `rg` inspection -> pass; `git diff --check` -> pass | pass by spec re-review `019f1cd1-66fb-7c42-a494-c1bbd257c229` | tests needed update; now addressed | accepted |
| S03 reviewer fix | dev-coder `019f1cc8-bbbc-7370-82a7-30663c61dfb1`; dev-coder `019f1ccd-8412-7812-90c1-af1be4a6fa26` | resolved QA P2 exact catalog gap and updated tests for spec-reviewer P1 contracts | `tests/unit/infra/test_artifact_templates.py` | `uv run pytest tests/unit/infra/test_artifact_templates.py` -> 6 passed; `git diff --check` -> pass | pass by QA re-review `019f1cd0-faa1-7d01-bd8e-222d1f89c5cd`; code re-review `019f1cd1-2fc2-7701-aaee-f119a2a78e61`; spec re-review `019f1cd1-66fb-7c42-a494-c1bbd257c229` | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S03 | none | no exception | none | none | use git diff if rollback needed | focused pytest/validate/diff check/assurance verify pass | final QA/code/spec reviewer gates passed | none |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect / implementation-planner / manual fallback` | used | read-only specialist evidence from `019f1cab-dc4f-7391-8208-e750f3d9e95d` and `019f1cac-07a1-76b2-85b1-73e079c13876`; adopted via EAL-001/EAL-002; fresh spec-reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8` | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | reviewer `019f1cb1-c31d-7740-acec-9fa2c9b396e8`; P2 report evidence gap fixed |
| S99 | final QA gate | qa-reviewer | fresh | pass | no | execute approved plan | reviewer `019f1cd0-faa1-7d01-bd8e-222d1f89c5cd`; previous QA P2 exact catalog finding resolved |
| S99 | final code review gate | code-reviewer | fresh | pass | no | execute approved plan | reviewer `019f1cd1-2fc2-7701-aaee-f119a2a78e61`; previous ADR authority P2 resolved |
| S99 | final spec review gate | spec-reviewer | fresh | pass | no | execute approved plan | reviewer `019f1cd1-66fb-7c42-a494-c1bbd257c229`; previous P1 findings resolved |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S03/S90/S99 | closure complete | provider artifact templates/rules/README, focused tests, issue docs/assurance | included in final issue commit | post-commit `git status --short` -> clean after `issue finish` | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/README.md` - future artifact template catalog and routing guidance.
- `src/spec_dock/assets/spec_dock/templates/artifacts/blank.md` - blank artifact template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/research.md` - research artifact template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/interview.md` - interview artifact template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/disc.md` - discussion/synthesis artifact template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/decision-candidate.md` - pre-adoption decision candidate template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md` - PR repair batch artifact template.
- `src/spec_dock/assets/spec_dock/templates/artifacts/adr.md` - future artifact ADR original template.
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md` - initiative artifact rules.
- `src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md` - epic artifact rules.
- `src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md` - issue artifact rules.
- `tests/unit/infra/test_artifact_templates.py` - focused structural tests.
- `spec-dock/active/issue/design.md` - approved Issue design refined before execution.
- `spec-dock/active/issue/plan.md` - approved Issue plan refined before execution.
- `spec-dock/active/issue/report.md` - planning and implementation evidence ledger.
- `spec-dock/active/issue/.assurance.json` - authorized standard assurance binding.

#### コミット
- final issue commit; exact hash reported externally after commit/amend.

#### メモ
- `decision-candidate` template field shape was accepted as a thin pre-adoption artifact, not as accepted authority and not as an ADR replacement.
- Dogfooding mirror refresh is not required in this Issue because command/scaffold wiring and broad workflow/docs migration belong to later Issues.
- QA P2 exact catalog finding, code-reviewer P2 ADR authority finding, and spec-reviewer P1 findings were accepted and fixed before final re-review.

---

### セッションログ（2026-07-01 final review）

#### 対象
- Step: S99 final reviewer gates
- AC/EC: AC-262-001 through AC-262-006

#### 実施内容
- Final QA/code/spec reviewer gates passed after accepting and fixing QA P2, code-reviewer P2, and spec-reviewer P1 findings.
- Re-ran focused pytest, SpecDock validate, diff check, and assurance verify after fixes.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider templates / rules / README | yes | doc-writer | S01/S02 implemented; reviewer fixes applied; focused pytest/validate pass | pass |
| workflow docs / skills / broader migration notes | no in this Issue | N/A | deferred to later Issues by plan; no runtime/docs-wide migration required for CLOS-262 | pass |
| dogfooding mirror | no in this Issue | N/A | provider-side source validated; mirror/scaffold wiring belongs to later Issues | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer `019f1cd0-faa1-7d01-bd8e-222d1f89c5cd` | whole issue obligation coverage | added focused structural tests; exact catalog P2 resolved | `uv run pytest tests/unit/infra/test_artifact_templates.py` -> 6 passed; QA re-review no findings | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer `019f1cd1-2fc2-7701-aaee-f119a2a78e61` | issue-wide integrated diff | previous P2 ADR draft metadata resolved; no remaining findings | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer `019f1cd1-66fb-7c42-a494-c1bbd257c229` | requirement / design / plan / report / implementation / tests / docs alignment | previous P1 non-Issue draft fail-closed and ADR draft authority findings resolved; no remaining findings | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| this report after final gates | provider templates/rules/README, focused tests, issue design/plan/report, assurance binding | final response and next Issue handoff | committed |

## 遭遇した問題と解決 (任意)
- 問題: Initial final reviews found non-blocking and blocking contract gaps: catalog test allowed unsupported extra templates, ADR draft template looked accepted, and Initiative/Epic draft-* rules implied unsupported routing.
  - 解決: Accepted findings, updated docs/templates/tests, re-ran focused verification, and obtained QA/code/spec re-review pass.

## 学んだこと (任意)
- Future artifact template contracts need tests that reject unsupported extra files, not only tests that required files exist.
- ADR templates should distinguish draft/non-authoritative creation from accepted authority and mirror eligibility.

## 今後の推奨事項 (任意)
- Downstream `iss-00263` should consume this closed catalog and preserve issue-only/no-write fail-closed behavior for draft-*.

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
