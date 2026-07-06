---
種別: レポート（Epic）
ID: "epic-00283"
タイトル: "ChatGPT ZIP 仕様作成パック自動化"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00283 ChatGPT ZIP 仕様作成パック自動化 — レポート（進捗 / 決定 / 結果）

## 進捗サマリー

- 現在地:
  - `init-local-00003 Architecture Maintenance and Hardening` 配下に `epic-00283` を作成済み。
  - ChatGPT Use / GPT-5.5 Pro Extended による調査・議論・ZIP authoring pack dogfood artifact を `epic-00283/artifacts/` へ集約済み。
  - Epic `requirement.md` / `design.md` / `plan.md` は具体化済み。
  - `iss-00284`〜`iss-00292` の canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は、Issue-local draft artifacts を evidence-only input として main orchestrator が採否判断し、正本へ再記述済み。
  - `iss-00293` は、Epic 最後の品質ゲート、manual test evidence、PR 作成、CI / review 修正、mergeable 確認を担当する final gate Issue として作成済み。
  - local assurance は全 Issue `standard` / `provisional` であり、ChatGPT 推奨や Epic 側のリスク判断で `.assurance.json` / `authorized_profile` を上書きしない。strict 推奨 Issue には strict 相当の追加 obligation を Issue plan に記録済み。
  - 実装と dogfood scripts は未着手。この Epic report は spec authoring / planning package の現状を記録する。
- 次のマイルストーン:
  - 更新後スコープで fresh `spec-reviewer` gate を通し、`iss-00284`〜`iss-00293` を後続 Issue execution-ready な planning package として扱えるか確認する。
- ブロッカー:
  - 現時点で main orchestrator が把握している仕様 authoring blocker はない。fresh `spec-reviewer` gate の結果で P0/P1 が出た場合は、この report の correction ledger に追記して修正する。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 部分採用（`partially_adopted`） | research | `requirement.md` | ChatGPT Use / GPT-5.5 Pro Extended を SpecDock authoring backend として使う方向性、evidence-only boundary、reviewer gate 非置換を要件へ採用した。 | `artifacts/20260706t090820z-research-chatgpt-oracle-advanced-analysis.md` | fresh `spec-reviewer` gate で確認する |
| EAL-002 | 部分採用（`partially_adopted`） | discussion | `requirement.md` | Spec Authoring Batch の workflow redesign、bundle generation と staged adoption の分離、candidate Issue slicing の方向性を要件へ採用した。 | `artifacts/20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md` | fresh `spec-reviewer` gate で確認する |
| EAL-003 | 部分採用（`partially_adopted`） | research | `requirement.md` | Reviewer gate の即時置換は行わず、ChatGPT output を advisory / shadow / authoring evidence として扱う制約を採用した。 | `artifacts/20260706t111806z-research-chatgpt-reviewer-gate-script-analysis.md` | reviewer replacement は v1 scope 外として維持する |
| EAL-004 | 採用（`adopted`） | research | `requirement.md` | Epic -> Issue / Issue bundle authoring automation の script candidates、dogfood-only placement、manual fallback、metrics を要件へ採用した。 | `artifacts/20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices.md` | Issue slicing / dogfood plan で追跡する |
| EAL-005 | 採用（`adopted`） | research | `requirement.md` | ZIP は first-class delivery format だが authority format ではないこと、profile は local assurance authority に残すこと、safe intake / validation / staged adoption を要件へ採用した。 | `artifacts/20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control.md` | validator / profile boundary Issue で実装する |
| EAL-006 | 部分採用（`partially_adopted`） | artifact | `requirement.md` | 新メンバー向けオンボーディング資料の要約・用語整理を requirement wording の補助 evidence として使った。 | `artifacts/20260706t133043z-chatgpt-zip-authoring-onboarding-brief.md` | docs Issue で正式文書化の要否を判断する |
| EAL-007 | 採用（`adopted`） | chatgpt-use research | `requirement.md` | Manual ChatGPT Use dogfood により `unresolved_user_questions: none`、requirement draft、candidate Issue seeds、dogfood observations が得られたため、要件具体化へ採用した。 | `artifacts/20260706t140325z-research-epic-requirement-clarification-dogfood.md` | fresh `spec-reviewer` gate で確認する |
| EAL-008a | 採用（`adopted`） | chatgpt-use ZIP authoring pack | Epic `design.md` / `plan.md` | ChatGPT Use が生成した Epic design / plan draft と naming proposal を、main orchestrator が provider-facing 名を避ける human-facing naming へ補正し、Epic canonical docs へ再記述した。 | `artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md`; `design.md`; `plan.md` | fresh `spec-reviewer` gate で確認する |
| EAL-008b | 採用（`adopted`） | chatgpt-use ZIP authoring pack | Issue-local draft artifacts | ChatGPT Use が生成した 9 Issue candidate draft を、証跡専用 artifact として `issues/iss-00284-*`〜`issues/iss-00292-*` の `artifacts/` へ配置した。ZIP host-local path は canonical evidence に固定せず、research artifact の redacted reference と `zip_sha256` を参照する。 | `artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md`; `issues/iss-00284-*`〜`issues/iss-00292-*` の `artifacts/*from-authoring-pack.md` | evidence-only handoff として保持する |
| EAL-008c | 採用（`adopted`） | Issue-local draft artifacts | `issues/iss-00284-*`〜`issues/iss-00292-*` の canonical `requirement.md` / `design.md` / `plan.md` / `report.md` | Issue-local draft artifacts は正本ではない。main orchestrator が各 Issue の scope、non-scope、入出力、失敗時設計、検証、reviewer obligation を確認し、採用した内容だけを canonical Issue docs へ再記述した。 | `issues/iss-00284-*`〜`issues/iss-00292-*` の canonical docs と report | fresh `spec-reviewer` gate で確認する |
| EAL-009 | 採用（`adopted`） | user workflow decision | `plan.md` / `issues/iss-00293-*` | 個別 Issue ごとに PR を作成せず、Issue 完了後に `issue finish` して次 Issue を `issue start` するリレー実行方針を採用した。最終 Issue `iss-00293` が Epic 単位の品質ゲート、manual test evidence、PR 作成、review / CI 修正、mergeable 確認を担当する。 | user instruction 2026-07-07; `plan.md`; `issues/iss-00293-final-epic-quality-gate-and-mergeable-pr/*` | `iss-00293` 実行時に最終証跡を記録する |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は ChatGPT ZIP authoring pack を evidence-only delivery として扱い、SpecDock local authority を維持することを主目的にした。 | manual-tests dogfood、future runtime promotion、Issue seeds を副次要件として分離した。 | 低。reviewer gate replacement / shipped runtime 化を v1 scope 外に明記した。 | pending current fresh review |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent initiative docs、workflow docs、`epic-00283/artifacts/`、ChatGPT Use manual dogfood output、ZIP authoring pack dogfood output、Issue-local draft artifacts、`.assurance.json` | Blocking question: none。Non-blocking design questions は raw ZIP storage、runtime promotion threshold、profile mismatch salvage、Strict/Critical specialist evidence path。 | EAL-001〜EAL-008c を採用 / 部分採用し、Epic `requirement.md` と Issue canonical `requirement.md` へ再記述した。 | pending current fresh review | いいえ | fresh `spec-reviewer` gate を実行する |
| design-epic | ZIP authoring pack design draft、naming proposal、workflow docs、requirement seeds、local Issue creation result | Blocking question: none。provider detail は human-facing surface に出さない。 | EAL-008a を採用し、Epic `design.md` へ control plane / data plane、ZIP lifecycle、profile boundary、failure design、test strategy を再記述した。 | pending current fresh review | いいえ | fresh `spec-reviewer` gate を実行する |
| design-issues | Issue-local draft designs、Issue canonical requirements、Epic readiness contract | Blocking question: none。draft artifact は証跡専用であり正本ではない。 | EAL-008c を採用し、`iss-00284`〜`iss-00292` の canonical `design.md` へ scope、non-scope、入出力、失敗時設計、検証観点を再記述した。 | pending current fresh review | いいえ | fresh `spec-reviewer` gate を実行する |
| plan-epic | ZIP authoring pack plan draft、Issue candidate drafts、Issue creation result、Issue-local draft artifact path index、Issue readiness contract | Blocking question: none。local assurance profile は現行 classifier で全 Issue `standard` / `provisional`。strict 推奨 Issue は `authorized_profile` を上書きせず strict 相当 obligation を追加する。 | EAL-008a / EAL-009 を採用し、Epic `plan.md` へ 10 Issue slicing、dependency order、dogfood scenarios、handoff path index、Issue readiness contract、`iss-00293` の最終品質ゲートを再記述した。 | pending current fresh review | いいえ | fresh `spec-reviewer` gate を実行する |
| plan-issues | Issue-local draft plans、Issue canonical requirements / designs、Epic strict 相当 obligation | Blocking question: none。ChatGPT output は reviewer pass claim に使わない。 | EAL-008c を採用し、`iss-00284`〜`iss-00292` の canonical `plan.md` へ実装ステップ、検証計画、完了条件、Spec-Locked Closure Index、Assurance / reviewer obligation を再記述した。 | pending current fresh review | いいえ | fresh `spec-reviewer` gate を実行する |

## 委任ドラフト証跡（Delegated Draft Evidence）

- 委任 authoring の使用:
  - used as evidence-only dogfood.
- 使用内容:
  - ChatGPT Use で downloadable ZIP authoring pack を生成し、Epic design / plan draft と 9 Issue candidate draft を取得した。
  - ZIP output は authority ではなく delegated draft evidence として扱い、main orchestrator が source / scope / naming / profile boundary を確認してから canonical Epic docs、Issue-local draft artifacts、Issue canonical docs へ採用した。
- lifecycle state:
  - `produced` -> `locally_reviewed_by_main_orchestrator` -> `adopted_to_draft_artifacts` -> `adopted_to_canonical_issue_docs`。
- 昇格判断:
  - canonical Epic docs と Issue canonical docs へ採用した内容は EAL-008a / EAL-008c として記録した。
  - Issue-local draft artifacts と redacted ZIP evidence は EAL-008b として evidence-only のまま保持する。

## Spec reviewer correction ledger

| ID | reviewer verdict | finding | correction | status |
|---|---|---|---|---|
| SR-20260707-001 | failed / P1 -> passed | Issue-local draft artifact に delegated draft provenance fields が不足していた。 | 27 個の `*from-authoring-pack.md` に provenance / adoption metadata を追加した。 | fixed in prior review cycle |
| SR-20260707-002 | failed / P1 -> passed | strict 推奨 Issue と local `authorized_profile=standard` の関係が不明確だった。 | Epic `plan.md` と各 Issue `plan.md` に、local assurance は上書きせず strict 相当 obligation を追加する方針を明記した。 | fixed |
| SR-20260707-003 | failed / P1 -> passed | 各 Issue の AC が共通 trace 確認に偏り、成果物固有の検証条件が不足していた。 | 9 Issue の canonical `requirement.md` と draft requirement artifact に、成果物固有の AC-005 / AC-006 を追加した。 | fixed in prior review cycle |
| SR-20260707-004 | failed / P1 -> passed | C07 の profile mismatch probe が C04 / `iss-00287` に依存することが Epic plan の依存グラフに反映されていなかった。 | `plan.md` の依存グラフに `C04 -> C07 -> C09` を追加した。 | fixed in prior review cycle |
| SR-20260707-005 | chatgpt-use review -> fixed | Child Issue canonical `design.md` / `plan.md` が未具体化のままだと、current request の spec-reviewer readiness に不足する。 | `iss-00284`〜`iss-00292` の canonical `design.md` / `plan.md` / `report.md` を Issue-local draft artifacts から main orchestrator が採否判断した内容として作成した。 | fixed; current fresh `spec-reviewer` gate pending |
| SR-20260707-006 | spec-reviewer failed / P1 -> fixed | Issue reports と Epic report に adopted-vs-candidate contradiction が残っていた。 | EAL-008c、Spec Authoring Gate、Issue EAL / SID を採用済み状態に統一した。 | fixed; current fresh `spec-reviewer` gate pending |
| SR-20260707-007 | spec-reviewer failed / P1 -> fixed | Issue plans が memo 状態で、executable closure contract が不足していた。 | `iss-00284`〜`iss-00293` の `plan.md` に canonical implementation plan、Spec-Locked Closure Index、S90、S99、Final Exit Contract を追加した。 | fixed; current fresh `spec-reviewer` gate pending |
| SR-20260707-008 | spec-reviewer failed / P2 -> fixed | ZIP evidence artifact に host-local absolute path が残っていた。 | research artifact 内の ChatGPT generated ZIP path を redacted evidence reference へ置換し、`zip_sha256` を正本証跡として使う方針へ寄せた。 | fixed; current fresh `spec-reviewer` gate pending |

## Relay execution correction ledger

| ID | correction | status |
|---|---|---|
| RELAY-20260707-001 | `iss-00284`〜`iss-00292` のリレー実行方針は、各 Issue の canonical `plan.md` と Issue-local `artifacts/*draft-plan*from-authoring-pack.md` の両方に、証跡として矛盾しない形で残す方針へ修正した。 | fixed; current fresh `spec-reviewer` gate pending |
| RELAY-20260707-002 | `iss-00293` は final gate Issue 自体の正本 requirement / design / plan / report として作成し、`assurance classify --stage requirement --issue iss-00293` で `standard` / `provisional` を確認した。 | fixed; `spec-dock validate` passed |
| RELAY-20260707-003 | `iss-00284`〜`iss-00292` の Issue-local draft-design / draft-plan は evidence-only handoff として保持しつつ、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | fixed; current fresh `spec-reviewer` gate pending |

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-epic-00283-001 | `iss-00284`〜`iss-00292` の Issue-local draft artifacts は evidence-only handoff であり、採否判断済みの内容だけを canonical Issue docs へ再記述する。 | accepted | EAL-008b / EAL-008c; Issue report SID entries | fresh `spec-reviewer` gate を実行する |
| SID-epic-00283-002 | 個別 Issue ごとに Pull Request を作成せず、実装完了後は `issue finish` して次 Issue を `issue start` するリレー実行とする。 | accepted | EAL-009; Epic `plan.md` リレー実行 / PR 方針; `iss-00293` specs | `iss-00284` から順番に実行し、PR は `iss-00293` に集約する |
| SID-epic-00283-003 | `iss-00293` は Epic 最後の品質ゲート、manual test evidence、PR 作成、CI / review 修正、mergeable 確認を担当する。 | accepted | `iss-00293` requirement / design / plan / report; assurance classify result | `iss-00292` 完了後に開始する |

## 完了した Issue / PR / Release

- Issue 作成:
  - `iss-00284` / GitHub `#284`: Build Authoring Pack Preflight And Prompt Pack
  - `iss-00285` / GitHub `#285`: Implement Safe Authoring Pack Review And Schema Validation
  - `iss-00286` / GitHub `#286`: Implement Authoring Pack Diff And Staged Artifact Rendering
  - `iss-00287` / GitHub `#287`: Implement Profile Controlled Selected Skeleton Fill Validation
  - `iss-00288` / GitHub `#288`: Dogfood Candidate Only Epic To Issue Authoring Pack
  - `iss-00289` / GitHub `#289`: Dogfood Existing Issue Selected Profile Authoring Pack
  - `iss-00290` / GitHub `#290`: Dogfood Authoring Pack Mismatch And Stale Probe
  - `iss-00291` / GitHub `#291`: Document Authoring Pack Workflow And Adoption Ledger Examples
  - `iss-00292` / GitHub `#292`: Evaluate Dogfood Metrics And Runtime Promotion Criteria
  - `iss-00293` / GitHub `#293`: 最終品質ゲートとマージ可能な Pull Request を作成する
- `iss-00284`〜`iss-00292`:
  - Issue-local `draft-requirement` / `draft-design` / `draft-plan` artifact を配置済み。
  - canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を具体化済み。
- PR / Release:
  - 未作成。PR 作成は `iss-00293` の execution scope に集約する。

## 受け入れ条件（E-AC）の達成状況

- E-AC-001〜E-AC-012:
  - 未実施。Spec authoring / planning phase であり、implementation / dogfood scripts は未着手。

## フォローアップ（別Issue化）

- 作成済み:
  - `iss-00284` Build Authoring Pack Preflight And Prompt Pack
  - `iss-00285` Implement Safe Authoring Pack Review And Schema Validation
  - `iss-00286` Implement Authoring Pack Diff And Staged Artifact Rendering
  - `iss-00287` Implement Profile Controlled Selected Skeleton Fill Validation
  - `iss-00288` Dogfood Candidate Only Epic To Issue Authoring Pack
  - `iss-00289` Dogfood Existing Issue Selected Profile Authoring Pack
  - `iss-00290` Dogfood Authoring Pack Mismatch And Stale Probe
  - `iss-00291` Document Authoring Pack Workflow And Adoption Ledger Examples
  - `iss-00292` Evaluate Dogfood Metrics And Runtime Promotion Criteria
  - `iss-00293` 最終品質ゲートとマージ可能な Pull Request を作成する

## 省略/例外メモ

- `epic-00283` の作成時、runtime が GitHub issue `#283` を自動作成した。
- ChatGPT ZIP dogfood run では、GitHub connector が `codex/chatgpt` 上の対象 file / expected commit を参照できた一方、branch head SHA の直接 observation は limited と記録された。local preflight では `HEAD == origin/codex/chatgpt == 209811098dc3067a94a3894cb89f9c6f5f6eae31` を確認済みだが、ZIP output 自体は引き続き advisory evidence として扱う。
- ZIP の raw host-local path は canonical evidence として扱わない。research artifact には redacted reference と `zip_sha256` を残す。
