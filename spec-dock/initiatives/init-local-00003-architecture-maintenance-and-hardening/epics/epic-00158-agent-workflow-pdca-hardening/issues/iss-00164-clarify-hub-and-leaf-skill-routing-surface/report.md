---
種別: 実装報告書（Issue）
ID: "iss-00164"
タイトル: "Clarify Hub And Leaf Skill Routing Surface"
関連GitHub: ["#164"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00164 Clarify Hub And Leaf Skill Routing Surface — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

この issue では material な scope / operation decision が発生したため、D-001..D-003 に記録する。

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
| D-001 | resolved | scope | orchestrator | Hub route matrix and leaf rewrite boundary needed to be fixed before design | Option A: keep generic route wording; Option B: define route matrix in requirement; Option C: defer routes to design | Define route matrix in requirement and keep leaf skill rewrites out of this issue | Requirement reviewer found route correctness was not externally verifiable without the matrix | applied | requirement reviewer `019e9b85-b01f-7c41-8e7b-0df677ceb964`; requirement.md | none |
| D-002 | superseded | operation | orchestrator | S01 edits two shipped/dogfooding skill text files and plan requires Parent Implementation Exception evidence if parent-local edit is used | Option A: delegate to doc-writer; Option B: bounded parent-local edit with exception evidence; Option C: block for user interview | A bounded parent-local edit was considered, but its approval source was too ambiguous to satisfy the plan contract after S01 review | Fresh S01 reviewer rejected the parent-local approval evidence; the issue can continue without a user interview by using the planned doc-writer fallback | superseded | S01 reviewer `019e9b99-6228-7aa0-94f2-056f6f1dd13f`; user follow-up "作業を続けてください"; plan S01 Parent Implementation Exception | Superseded by D-003 |
| D-003 | resolved | operation | orchestrator | S01 reviewer required removal of leaf-owned clarification procedure and explicit delegation evidence | Option A: block for user interview; Option B: reattempt parent-local edit; Option C: delegate remaining hub wording repair to doc-writer | Delegate remaining hub skill wording repair to `doc-writer` and integrate the bounded result after parent verification | This follows the approved fallback when parent-local approval is absent or ambiguous, keeps the change inside the two hub skill files, and does not require user intent clarification | applied | doc-writer `019e9b9b-a2c0-7793-aaec-1ba8ef85437a`; provider/mirror `cmp`; stale clarification procedure negative `rg`; clarification route positive `rg`; S01 diff | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | draft requirement discussion | `requirement.md` | Draft captured hub router/global invariant scope and was adopted, then tightened after requirement review with explicit route matrix and leaf rewrite boundary | `discussions/20260606t024146z-draft-requirement-clarify-hub-and-leaf-routing-draft-requirement.md`; requirement reviewer `019e9b87-c12b-7a02-a3bd-6543b0ebebfb` | promoted to design |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is hub route selection and global invariant clarity | Secondary requirements cover provider/mirror verification and leaf rewrite boundary | low | requirement/design/plan reviewers passed |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic docs/ADR; draft requirement; current hub/leaf skills; `iss-00163` completion state | none | adopted draft and reviewer fixes into canonical requirement | fresh pass by `019e9b87-c12b-7a02-a3bd-6543b0ebebfb`; prior fail by `019e9b85-b01f-7c41-8e7b-0df677ceb964` | no | promoted to design |
| design | approved requirement; provider/mirror hub skill; Epic design | none | design authored with two-file hub skill boundary and route matrix contract | fresh pass by `019e9b8a-c7cc-7720-88dd-e670504fbc76` | no | promoted to plan |
| plan | approved requirement/design; issue plan workflow; route target existence; delegation policy | none | plan authored with S01/S90/S99, cl-001..cl-007, route target checks, and parent exception contract; P2 approval-source precision fixed | fresh pass by `019e9b92-1216-7531-a7d0-87ed1a8b2af2`; prior fail by `019e9b8e-2c99-7be2-9a76-ab247d871fe8` | no | promoted to execution |

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
- S01 で `spec-driven-tdd-workflow` hub skill に route selector / global invariant surface と skill-owned clarification route を明示した。
- Provider と dogfooding mirror は byte-equivalent に保ち、leaf skill / docs / templates / runtime は変更していない。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-06 15:18 - 15:35）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-006, EC-001, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: 実装ステップ S01 — Hub route and invariant surface
  - closure ids: cl-001, cl-002, cl-003, cl-004, cl-005

#### 実施内容
- Provider and mirror `spec-driven-tdd-workflow/SKILL.md` の opening bullets に `route selector` / `global invariant surface` を追加した。
- Clarification route を `spec-dock-clarification` の skill-owned source-grounded clarification として明示し、`workflow_clarification.md` は artifact semantics / reference details として位置付けた。
- Canonical docs / evidence adoption の global invariant を hub skill に明記した。
- Leaf skills、workflow docs、templates、runtime は変更していない。

#### 実行コマンド / 結果
```bash
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md
test -f src/spec_dock/assets/install_root/.agents/skills/spec-dock-adr-facilitation/SKILL.md
test -f .agents/skills/spec-dock-initiative-planning/SKILL.md
test -f .agents/skills/spec-dock-epic-planning/SKILL.md
test -f .agents/skills/spec-dock-issue-planning/SKILL.md
test -f .agents/skills/spec-dock-issue-execution/SKILL.md
test -f .agents/skills/spec-dock-clarification/SKILL.md
test -f .agents/skills/spec-dock-system-architect/SKILL.md
test -f .agents/skills/spec-dock-implementation-planner/SKILL.md
test -f .agents/skills/spec-dock-adr-facilitation/SKILL.md

pass: all route target skill files exist in provider and mirror.
```

```bash
gh issue view 163 --json state --jq '.state'
git log --oneline --grep 'final gate証跡を記録'

pass: GitHub issue #163 is CLOSED; local history includes `8d9d62c docs(clarification): final gate証跡を記録`.
```

```bash
rg -n 'entry/routing skill|route selector|global invariant' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md
rg -n 'leaf skills own the first-read spine|docs own detailed semantics|templates.*not compliance authorities' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md
rg -n 'spec-dock-initiative-planning|spec-dock-epic-planning|spec-dock-issue-planning|spec-dock-issue-execution|spec-dock-clarification|spec-dock-system-architect|spec-dock-implementation-planner|spec-dock-adr-facilitation|workflow_clarification' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md
rg -n 'skill-owned|source-grounded clarification|source-grounded ambiguity' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md
rg -n 'fresh .*spec-reviewer|Missing, stale, failed, unavailable, denied, waived, or provisional|canonical docs.*main orchestrator|evidence.*canonical' src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md

pass: all required positive terms found in provider and mirror.
```

```text
negative stale-authority inspection:
- checked both provider and mirror hub skill files for old docs-as-compliance-authority phrasing.
- checked both provider and mirror hub skill files for the old hub-owned clarification interview procedure.
- result: no matches; the inspection command exited 1.
```

```bash
cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md .agents/skills/spec-driven-tdd-workflow/SKILL.md
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets
git diff --check

pass: cmp exited 0; unittest OK; diff-check had no output.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | inspect-only | pre-change hub lacked explicit `route selector`, `global invariant surface`, and `skill-owned` clarification wording required by plan checks | pre-change planned `rg` commands | pass | docs-only skill text change |
| S01 | 緑フェーズ（Green） | route target/prerequisite checks, hub wording checks, negative stale-authority check, parity | all required route targets exist; #163 CLOSED; positive terms found; stale authority negative returned no matches; parity passed | `test -f`, `gh issue view`, `git log`, `rg`, `cmp`, `python -m unittest`, `git diff --check` | pass | cl-001..cl-005 evidence recorded |
| S01 | リファクタリング（Refactor） | no outside-path changes | diff limited to two hub skill files before report update | `git diff --stat`, diff inspection | pass | no leaf/docs/templates/runtime changes in S01 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none | implementation | no action | cl-001..cl-005 | no | S01 commands above |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | cl-001, cl-002, cl-003, cl-004, cl-005 | route matrix, clarification route, hub/leaf boundary, global invariants, provider/mirror parity, route target/prerequisite evidence, doc-writer fallback evidence, fresh spec-reviewer | implementation evidence passes; fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` passed with no findings | pass | ready for S01 commit |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01 | yes | inspect-only | route target wording partially present pre-change | route target `test -f` commands and route target `rg` | pass | resolves cl-001 |
| tc-s01-002 | S01 | yes | inspect-only | clarification route lacked explicit `skill-owned` wording | clarification positive `rg` and stale authority negative `rg` | pass | resolves cl-002 |
| tc-s01-003 | S01 | yes | inspect-only | hub boundary/global invariant wording incomplete | ownership and global invariant `rg` commands | pass | resolves cl-003, cl-004 |
| tc-s01-004 | S01 | yes | covered-existing | provider/mirror parity existed before S01 | `cmp`; targeted agent-tooling parity unittest | pass | resolves cl-005 |
| tc-s01-005 | S01 | yes | inspect-only | `iss-00163` prerequisite needed confirmation | `gh issue view 163`; `git log --grep 'final gate証跡を記録'` | pass | resolves EC-002 prerequisite evidence |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-001 | S01 | route target existence commands and route target `rg` | pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass |
| cl-002 | S01 | skill-owned clarification positive `rg` and stale authority negative `rg` | pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass |
| cl-003 | S01 | ownership wording `rg` and diff scope inspection | pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass |
| cl-004 | S01 | global invariant `rg` | pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass |
| cl-005 | S01 | provider/mirror `cmp` and targeted parity unittest | pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| alias-mapped | cl-001 | tc-s01-001 | cl-001 | plan concrete test id used as test id | no | no |
| alias-mapped | cl-002 | tc-s01-002, tc-s01-005 | cl-002 | plan concrete test ids used as test ids | no | no |
| alias-mapped | cl-003, cl-004 | tc-s01-003 | cl-003, cl-004 | plan concrete test id used as test id | no | no |
| alias-mapped | cl-005 | tc-s01-004 | cl-005 | plan concrete test id used as test id | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| workflow-scoped execution consent plus plan fallback after rejected parent-local evidence | `/Users/iwasawayuuta/.codex/worktrees/8d9b/spec-dock` | iss-00164 | current session | spec-reviewer, doc-writer, code-reviewer, qa-reviewer, read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use; doc-writer limited to the two hub skill files for S01 wording repair | issue complete / session end / scope change / host policy conflict / user revocation | parent-local approval evidence was ambiguous and rejected by S01 reviewer; user interview not required because doc-writer fallback is covered by plan | S01 reviewer pass; proceed to S01 commit |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated-execution | parent-local edit evidence was rejected; remaining hub skill wording repair delegated to doc-writer under the approved fallback | doc-writer | provider/mirror hub skill wording | `requirement.md`; `design.md`; `plan.md`; provider source under `src/spec_dock/assets/install_root/.agents/skills/` | two S01 target hub skill files only | leaf skills, docs, templates, runtime, tests | S01 Green commands, negative inspection, `cmp`, targeted parity unittest, diff inspection | route target missing; leaf rewrite needed; provider/mirror parity cannot be preserved; user-intent clarification blocking | changed files, verification result, unresolved risks, Ledger Note or no-material-decision statement | doc-writer completed bounded repair; parent verification pass; S01 spec-reviewer pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | Removed leaf-owned clarification procedure from hub quick reminders, kept hub wording as route selector / global invariant surface, and verified provider/mirror parity. No material implementation decisions beyond the approved plan. | `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`; `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | `cmp` pass; stale clarification procedure negative `rg` pass; `spec-dock-clarification` / `workflow_clarification` positive `rg` pass | fresh S01 spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass | none identified | integrated by parent in D-003; reviewer accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | parent-local exception not used after reviewer rejected ambiguous approval evidence | no parent-local risk acceptance claimed; doc-writer fallback used instead | `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`; `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | N/A after fallback | revert the two hub skill files to pre-S01 state if reviewer fails | doc-writer verification and parent S01 planned commands -> pass | spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` pass | no waiver; rejected parent-local evidence superseded by D-003 doc-writer delegation |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | spec-reviewer `019e9ba0-fe42-75f3-ba65-a04439bdf61d` | fresh | pass | no | proceed to S01 commit | no findings |
| S90 | docs impact reviewer | spec-reviewer `019e9ba5-fb61-7611-b700-66099b094af7` | fresh | pass | no | proceed to S90 commit | sync / validate / diff-check passed; no generated diff remained; no findings |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | pass | two hub skill files + report S01 evidence | `0c16edb2 docs(hub-routing): hub skillの経路選択面を明確化` | `git status --short` clean before S90 report update | not applicable | not applicable | not applicable | not applicable |
| S90 | pass | report S90 evidence only; `sync` produced no persisted generated diff | `3fb0864a docs(hub-routing): docs impact証跡を記録` | `git status --short` clean before S99 validation | generated projections already matched after sync | `spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md` | `git status --short`; `git diff --name-only` | clean before S90 report update; S90 spec-reviewer pass |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` - Provider hub route selector / global invariant wording.
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md` - Dogfooding mirror hub skill parity update.
- `spec-dock/active/issue/report.md` - S01 evidence and reviewer pass records.

#### コミット
- S01: `0c16edb2 docs(hub-routing): hub skillの経路選択面を明確化`
- S90: `3fb0864a docs(hub-routing): docs impact証跡を記録`

#### メモ
- No user interview blocker was found for S01.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| generated projections (`spec-dock/.agent/*`, `spec-dock/*.puml`, `spec-dock/dashboard.md`) | no persisted diff | N/A | `./spec-dock/scripts/spec-dock sync` exited 0 and reported generated outputs; `git status --short`, `git diff --stat`, and `git diff --name-only` were clean afterward | spec-reviewer `019e9ba5-fb61-7611-b700-66099b094af7` pass |
| docs / templates / README / workflow docs / leaf skills / runtime / migration notes | no | N/A | S01 changed only hub skill provider/mirror text; no leaf/docs/templates/runtime diff remained after sync; `./spec-dock/scripts/spec-dock validate` exited 0 (`nodes=84`); `git diff --check` exited 0 | spec-reviewer `019e9ba5-fb61-7611-b700-66099b094af7` pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer `019e9bab-a1c1-7a13-aab6-8d9a038815d9` | whole issue obligation coverage | already sufficient after report ledger repair | initial fail by `019e9ba8-bd6a-76a2-a3cb-cca4ce7bcb05`: S90 commit evidence was stale / pending in Step Commit Gate; fixed by recording `3fb0864a` and post-commit clean evidence; re-review found no remaining findings | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer `019e9baf-0e28-7df2-af3e-fbdc7ea352a4` | issue-wide integrated diff | initial fail by `019e9ba8-dbca-7da0-9cfe-0de0f514d182`: S90 commit evidence was stale / pending in Step Commit Gate; second fail by `019e9bab-b6c3-7ac2-8e46-1aac8101c77c`: Decision Ledger summary omitted D-003; fixed both | 2 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer `019e9bab-ceed-7323-8ad3-157c78369224` | requirement / design / plan / report / implementation / tests / docs alignment | initial fail by `019e9ba9-3616-7962-b995-677cc5c95453`: S99 final gate rows still had template placeholders; fixed by replacing placeholders with actual reviewer findings and final pass evidence | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| final reviewer gates pass; final report ledger ready to commit | report final gate evidence only | final response and `issue finish` evidence | ready |

## 遭遇した問題と解決 (任意)
- 問題: Initial final QA/code reviews found stale S90 commit evidence in Step Commit Gate.
  - 解決: Recorded `3fb0864a docs(hub-routing): docs impact証跡を記録` and post-commit clean evidence in the S90 row.
- 問題: Initial final spec review found S99 final gate placeholders.
  - 解決: Replaced placeholders with actual reviewer findings, fixes, and final pass evidence.

## 学んだこと (任意)
- Final report rows must be updated after intermediate commits before final reviewers can verify issue finish readiness.

## 今後の推奨事項 (任意)
- Keep final gate rows in `pending` with concrete reviewer evidence instead of template placeholders while re-review is in progress.

## 省略/例外メモ (必須)
- 該当なし
