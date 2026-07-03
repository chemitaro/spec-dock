---
種別: 実装報告書（Issue）
ID: "iss-00274"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow"
関連GitHub: ["#274"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00274 Epic execution handoff と Issue readiness workflow 更新 — レポート

## 進捗サマリー
- Issue scaffold を作成した。
- 正規 `requirement.md` を作成した。
- 旧 canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifact へ移した。
- Canonical `design.md` / `plan.md` は `awaiting-assurance-compose` placeholder に戻した。
- Issue Start 後に `assurance classify` / `assurance compose` を実行し、正規 `design.md` / `plan.md` を `iss-00274` 固有の設計・計画へ正本化した。
- system-architect / implementation-planner の専門ドラフトを Issue-local artifact として作成し、正規設計・計画へ採用した。
- 実装、テスト、Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-274-001 | resolved | scope | この Issue の正本は `requirement.md` であり、`design.md` / `plan.md` は実行時に正規化する先行ドラフトである。 | ユーザー指示、Issue Planning workflow | applied | `issue start` 後に `iss-00272` / `iss-00273` の結果を取り込み、正規設計・正規計画へ更新する。 |
| D-274-002 | resolved | operation | この Issue では PR を作成せず、完了後に `issue finish` で `iss-00275` へバトンを渡す。 | Epic plan の1PR delivery方針、dependency chain | applied | final PR delivery は `iss-00276` が扱う。 |
| D-274-003 | resolved | interpretation | Epic execution handoff inspection は structural blocker と reviewer finding を分け、semantic reviewer を置き換えない。 | `epic-00270` design decision D-006、user interview | applied | 実行時に skill / docs wording と tests へ反映する。 |
| D-274-004 | resolved | grade | この Issue は `assurance classify` では `standard` と判定されたが、要件上の `strict` grade と shared workflow / skill contract 変更の性質を優先し、specialist evidence gate を必須として扱う。 | `requirement.md`, `assurance classify --stage requirement`, system-architect / implementation-planner draft | applied | fresh reviewer gate で grade / obligation の扱いを確認する。 |
| D-274-005 | resolved | scope | runtime behavior 変更は現時点では仮定せず、S02 characterization で不足が確認された場合だけ focused runtime / test step を追加する。 | system-architect draft, implementation-planner draft, 現行 `new artifact draft-*` surface | applied | 実行時に docs / skills-only で足りるかを report evidence として記録する。 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-274-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Epic の Slice 04 handoff を Issue 要件と pre-start seed へ落とした。要件は正本として採用し、design / plan seed は evidence-only artifact として保持する。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | Issue開始時に前段 reference / template 結果を反映する。 |
| EAL-274-002 | adopted | user decision / interview | `requirement.md` | Option B handoff inspection を structural blockers と reviewer findings の分離として採用した。 | `artifacts/20260702t030615z-interview-phase3-handoff-package-inspection-strength.md` | 実行時の skill / docs wording に反映する。 |
| EAL-274-003 | adopted | Epic EAL-023 / local validation commands | `report.md` | Batch planning artifact の検証は Epic-level evidence として記録済みであり、この Issue では実装検証とは分けて参照する。 | `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`); `deps check epic-00270` / `deps check iss-00276` -> expected blocked | Issue固有の実装検証は `issue start` 後に行う。 |
| EAL-00274-DESIGN | integrated | migrated pre-start canonical body | `artifacts/20260702t081006z-draft-design-epic-execution-readiness-workflow-pre-start-seed.md` | 旧 canonical `design.md` body は pre-start handoff seed として保持した。Issue Start 後の採用判断は EAL-274-004 に統合済みである。 | old `design.md` before placeholder restore | closed by EAL-274-004。 |
| EAL-00274-PLAN | integrated | migrated pre-start canonical body | `artifacts/20260702t081007z-draft-plan-epic-execution-readiness-workflow-pre-start-seed.md` | 旧 canonical `plan.md` body は pre-start handoff seed として保持した。Issue Start 後の採用判断は EAL-274-005 に統合済みである。 | old `plan.md` before placeholder restore | closed by EAL-274-005。 |
| EAL-274-004 | adopted | `artifacts/20260702t081006z-draft-design-epic-execution-readiness-workflow-pre-start-seed.md` | `design.md` | pre-start seed の Epic execution coordinator、structural blocker / reviewer finding、no per-Issue PR、Issue relay の考え方は要件・Epic設計と整合するため採用した。 | pre-start draft-design artifact | 正規 `design.md` の `D274-001..011` と readiness model に反映済み。 |
| EAL-274-005 | adopted | `artifacts/20260702t081007z-draft-plan-epic-execution-readiness-workflow-pre-start-seed.md` | `plan.md` | pre-start seed の S00/S01/S02/S03/S99 構造を、現行Issue実行向けに Red / characterization / implementation / verification / review / finish へ再構成して採用した。 | pre-start draft-plan artifact | 正規 `plan.md` の `S01..S08` に反映済み。 |
| EAL-274-006 | adopted | `artifacts/20260702t111140z-draft-design-system-architect-design-draft-epic-execution-readiness-workflow.md` | `design.md` | `I274-AC-001..009` / `I274-EC-001..004` の設計マッピング、handoff-ready / execution-ready 分離、command責務境界、risk / verification 戦略が正規設計に必要だったため採用した。 | system-architect draft artifact | 正規 `design.md` に統合済み。 |
| EAL-274-007 | adopted | `artifacts/20260702t111145z-draft-plan-implementation-planner-plan-draft.md` | `plan.md` | closure index、allowed / forbidden paths、S02 runtime要否判定、reviewer focus、`iss-00275` へのhandoff evidence が正規計画に必要だったため採用した。draft frontmatter の diff guard 注意は、draft作成時に同一Issueの正本 `design.md` / `plan.md` / `report.md` 変更と別artifact作成が同時に存在したための global dirty guard であり、draft本文の provenance / scope / canonical self-claim の失敗ではない。main orchestrator が artifact本文を正規 `plan.md` へ再記述し、採用後に `assurance verify`、`validate`、`git diff --check` を通したため harmless として disposition する。 | implementation-planner draft artifact; `assurance verify` -> ok; `validate` -> ok (`nodes=178`); `git diff --check` -> ok | 正規 `plan.md` に統合済み。fresh spec-review で disposition 妥当性を確認済み。 |
| EAL-274-008 | integrated | `./spec-dock/scripts/spec-dock assurance classify --stage requirement` | `report.md` | 現行 runtime は `authorized_profile: standard` と判定したが、Issue要件の `strict` obligation を上書きするものではない。 | command output: `authorized_profile: standard`, `lite_candidate: false` | 設計・計画では strict specialist gate を維持する。 |
| EAL-274-009 | integrated | `./spec-dock/scripts/spec-dock assurance compose --artifact all` | `design.md` / `plan.md` / `report.md` | 汎用 Standard template が生成されたため、そのままでは execution-ready ではない。specialist draft と Issue要件に基づいて正本化した。 | compose changed `design.md`, `plan.md`, `report.md` | fresh review 前の planning docs として扱う。 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）
| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Epic handoff、Issue要件、ADR、dependency chain を確認した。 | none | Epic handoff から正規 `requirement.md` へ採用した。 | pass | no | execute approved plan |
| design | pre-start seed、system-architect draft、Epic設計、accepted ADR、現行 workflow docs を確認した。 | none | 正規 `design.md` を Issue固有の設計契約へ統合した。 | pass | no | execute approved plan |
| plan | pre-start seed、implementation-planner draft、Closure Index、allowed / forbidden paths、reviewer focus を確認した。 | none | 正規 `plan.md` を `S01..S08` の実装ステップへ統合した。 | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
| role | scope | draft path | source paths | intended targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00274 | artifacts/20260702t111140z-draft-design-system-architect-design-draft-epic-execution-readiness-workflow.md | active issue / epic docs, ADRs, workflow docs, epic execution skill | design.md | adopted | design.md | passed | EAL-274-006 により設計契約へ統合した。 | none | none | pass | execute approved plan |
| implementation-planner | iss-00274 | artifacts/20260702t111145z-draft-plan-implementation-planner-plan-draft.md | active issue / epic docs, seed artifacts, workflow docs, epic execution skill | plan.md | adopted | plan.md | ok by main-orchestrator disposition and post-adoption checks passed | EAL-274-007 により実装ステップへ統合した。 | none | resolved | pass | execute approved plan |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner | used | Runtime `authorized_profile=standard` に対し、system-architect draft and implementation-planner draft integrated through EAL-274-006 / EAL-274-007 | pass | ready |
| strict | system-architect / implementation-planner | used | Issue requirement / design の strict override に対し、system-architect draft and implementation-planner draft integrated through EAL-274-006 / EAL-274-007 | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | Initial P1/P2 findings were resolved in EAL disposition and re-review passed. |

## 実装記録
- S01 Red / characterization baseline:
  - `rg -n "handoff-ready|execution-ready|structural blocker|reviewer finding|draft-plan|draft-design|iss-00276|issue finish" ...` を実行した。
  - 現行 `workflow_epic.md` は Issue-local `draft-design` / `draft-plan` primitive を持つが、Epic execution skill は `handoff-ready` / `execution-ready`、structural blocker / reviewer finding、`iss-00276` final delivery 集約を十分に案内していなかった。
  - 期待どおり docs / skill guidance の不足を Red / characterization evidence として固定した。
- S02 Runtime change 要否判定:
  - 現行 `new artifact draft-design` / `draft-plan` surface は存在し、今回の欠落は command behavior ではなく workflow / skill guidance の不足である。
  - `assurance compose` の canonical compose 専用境界も docs / skill guidance で明示すれば足りるため、runtime code / tests の変更は不要と判断した。
  - S03 / S04 は `doc-writer` に委譲し、provider skill、dogfooding skill、workflow docs の更新に限定する。
- S03 Epic execution skill 更新:
  - `doc-writer` に委譲し、provider-side `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` と dogfooding `.agents/skills/spec-dock-epic-execution/SKILL.md` を更新した。
  - reviewer-gated Epic docs / report と downstream Issue handoff package の first-read、`handoff-ready` / `execution-ready` 分離、structural blocker / reviewer finding 境界、Issue-local `draft-design` / `draft-plan` primitive、plan-aware no per-Issue PR / `iss-00276` final delivery、日本語ファースト guidance を追加した。
- S04 Workflow docs 更新:
  - `doc-writer` に委譲し、`workflow_epic.md` と `workflow_issue.md` を更新した。
  - `assurance compose` は canonical compose 専用であり draft artifact 作成 command ではないこと、actor / specialist / depth 別 draft command を作らないこと、handoff-ready は実装開始許可ではないことを明示した。
  - `workflow_issue.md` には execution-ready 条件、structural blocker / reviewer finding 分離、日本語ファースト guidance を追加した。

## 検証
- 実施済み:
  - Batch planning artifact validation: Epic EAL-023 に従い `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - Dependency-chain confirmation: Epic EAL-023 に従い `deps check epic-00270` / `deps check iss-00276` は前段Issue未完了で blocked となり、リレー依存どおりであることを確認した。
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement` により、現行 runtime profile が `standard`、lite候補ではないことを確認した。
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all` により、canonical `design.md` / `plan.md` / `report.md` の compose surface を実行した。
  - system-architect / implementation-planner draft artifact を作成し、正規 `design.md` / `plan.md` へ採用した。
  - 正本化直後の `./spec-dock/scripts/spec-dock assurance verify` は `stale_source_binding` で失敗した。`assurance compose` 後に正規 `design.md` / `plan.md` を統合編集したため、`.assurance.json` の source binding が古くなったことが原因である。
  - 正本化後に `./spec-dock/scripts/spec-dock assurance classify --stage requirement` を再実行し、source binding を更新した。
  - `./spec-dock/scripts/spec-dock assurance verify` が成功した。
  - `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - `git diff --check` が成功した。
  - fresh `spec-reviewer` 初回レビューは fail。P1: implementation-planner draft の `diff_guard_result: failed` に対する明示的 disposition 不足、P2: superseded seed EAL 行が `deferred` のまま残っていたこと。
  - P1/P2 を `report.md` の EAL で修正した。EAL-00274-DESIGN / PLAN は `integrated` として EAL-274-004 / 005 で閉じ、EAL-274-007 は `adopted` 行の判断理由として harmless disposition と検証結果を明記した。
  - 修正後に `./spec-dock/scripts/spec-dock assurance verify`、`./spec-dock/scripts/spec-dock validate`、`git diff --check` が成功した。
  - fresh `spec-reviewer` 再レビューが `review_status: pass`。前回P1/P2は解消され、Issue実行前の残ブロッカーなしと判定された。
  - `design.md` / `plan.md` の状態を `approved` に更新し、placeholder判定に引っかかる省略パスを実パスに置換した。
  - `report.md` の Evidence Adoption Ledger / Spec Authoring Gate / Delegated Draft Evidence / Grade Specialist Evidence Gate / Reviewer Gate Status を `guidance issue-execution` の report evidence gate に合わせて正規化した。
  - `./spec-dock/scripts/spec-dock guidance issue-execution` が `state: ready`、`reason_code: assurance-valid`、`may_execute_approved_plan: true` を返した。
  - S01 baseline grep により、Epic execution skill / workflow docs の guidance gap を確認した。
  - S02 scope decision として runtime behavior / tests は変更せず、docs / skills-only で進める判断を記録した。
  - `doc-writer` が S03 / S04 の skill / workflow docs 更新を実施した。
  - 指定 grep 2本が成功し、`structural blocker`、`reviewer finding`、`handoff-ready`、`execution-ready`、`draft-design`、`draft-plan`、`assurance compose`、`iss-00276`、`semantic reviewer`、`spec-reviewer`、`raw artifact`、`decision-only`、`日本語ファースト` の導線を確認した。
  - `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - `git diff --check` が成功した。
  - `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md` が成功し、provider skill と dogfooding skill copy の一致を確認した。
- 未実施:
  - S06 runtime / test verification は docs / skills-only 判定により not applicable。runtime code、tests、template behavior は変更していない。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
| Step | Closure | Evidence | Result |
|---|---|---|---|
| S01 | `C274-001..008` | baseline `rg` で Epic execution skill / workflow docs の handoff-ready、execution-ready、structural blocker、reviewer finding、`iss-00276` 導線不足を確認した。 | pass |
| S02 | `C274-007`, `C274-008` | 既存 `new artifact draft-design` / `draft-plan` surface と `assurance compose` 境界を確認し、今回の不足は docs / skill guidance と判定した。 | approved-no-op for runtime |
| S03 | `C274-001`, `C274-002`, `C274-003`, `C274-005`, `C274-006`, `C274-007`, `C274-008` | `doc-writer` が provider / dogfooding `spec-dock-epic-execution` skill を更新し、provider copy と `.agents` copy の `cmp -s` が成功した。 | pass |
| S04 | `C274-001`, `C274-002`, `C274-004`, `C274-007`, `C274-008` | `doc-writer` が `workflow_epic.md` / `workflow_issue.md` を更新し、draft artifact primitive、canonical compose、readiness境界を明記した。 | pass |
| S05 | `C274-001..008` | 指定 grep 2本、`./spec-dock/scripts/spec-dock validate`、`git diff --check` が成功した。 | pass |
| S06 | `C274-007`, `C274-008` | runtime / tests は変更なし。docs / skills-only 判定により `uv run pytest` は not applicable。 | approved-no-op |
| S07 | `C274-001..008` | fresh `spec-reviewer` が実装diffをreviewし、`review_status: pass`。P2 report cleanup はこの追記で対応した。 | pass |
<!-- spec-dock:managed-section end id="report.step-evidence" -->
