---
種別: レポート（Epic）
ID: "epic-00283"
タイトル: "ChatGPT ZIP 仕様作成パック自動化"
状態: "approved"
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
  - `iss-00292` で dogfood metrics report、runtime promotion criteria draft、defer / reject rationale template を Issue-local evidence として作成済み。runtime promotion 自体は未決定で、現時点の推奨 stance は `defer_formal_runtime_promotion` として `iss-00293` final gate へ引き継ぐ。
  - `iss-00293` は、Epic 最後の品質ゲート、manual test evidence、PR 作成、CI / review 修正、mergeable 確認を担当する final gate Issue として作成済み。
  - 2026-07-07 のユーザー補足に基づき、`iss-00293` の PR 作成前 gate に ChatGPT Use / Oracle backend command adapter / invocation contract の実装・検証を追加し、S04 として実装 / focused verification 済み。
  - local assurance は全 Issue `standard` / `provisional` であり、ChatGPT 推奨や Epic 側のリスク判断で `.assurance.json` / `authorized_profile` を上書きしない。strict 推奨 Issue には strict 相当の追加 obligation を Issue plan に記録済み。
  - authoring-pack helper、dogfood scenarios、workflow docs、metrics decision material は `iss-00284`〜`iss-00292` で段階的に実装 / 記録済み。backend command adapter は `iss-00293` S04 で実装 / focused verification 済み。
  - `iss-00293` で先行 Issue 完了 matrix、Epic manual test matrix、final local verification を記録済み。full baseline は snapshot 修正後に `1910 passed, 74 skipped` で通過した。PR #294 は作成済みで、Provider CI / mypy failure は修正済み。再観測では CI pass を確認したが、Codex review の carryover P1 thread 4件が残ったため、安全境界修正を local repair として実施済み。CI / review / mergeable の再観測は残作業。
- 次のマイルストーン:
  - fresh `spec-reviewer` gate `019f3999-911a-7381-8155-3cda5fcf3403` が pass し、`iss-00284`〜`iss-00293` を後続 Issue execution-ready に向けた reviewable planning package として扱える状態になった。
- ブロッカー:
  - 現時点の Epic package 全体には仕様 authoring を止める blocker はない。
  - `iss-00284` の current planning refresh に対する fresh `spec-reviewer` gate は別途 Issue report に記録する。過去の Epic/package review pass は current `iss-00284` execution-ready pass ではない。
  - 2026-07-07 の `iss-00284` fresh review chain では `report.md` の current reviewer gate / closure ledger に stale pass evidence が残る P1 が検出された。P1 修正は適用済みで、post-fix fresh re-review `019f387a-e7c2-73b3-ae10-89d8dd487cfb` は P0/P1/P2 findings なしで pass した。

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

| EAL-010 | `adopted` | ChatGPT Use / GPT-5.5 Pro Extended readiness review | Epic / Issue specs | P1 findings を修正対象として採用した。ChatGPT output は reviewer pass ではなく、canonical docs の更新 input として扱う。 | `artifacts/20260706t164600z-research-chatgpt-authoring-pack-readiness-review.md` | 修正後に fresh `spec-reviewer` review |
| EAL-011 | `adopted` | user supplemental requirement | Epic `plan.md`; `iss-00293` specs | SpecDock 正式ワークフローやスクリプトが個人環境固有の ChatGPT Use / Oracle wrapper 絶対パスに依存しないよう、backend command adapter / invocation contract を `iss-00293` の PR 作成前品質ゲートへ追加した。 | user instruction 2026-07-07; Epic `plan.md`; `issues/iss-00293-final-epic-quality-gate-and-mergeable-pr/*`; `scripts/authoring-pack/invoke_chatgpt_backend.py`; `tests/manual_tests/test_invoke_chatgpt_backend.py` | implemented in `iss-00293` S04; include in final reviewer / PR gate |
| EAL-012 | `partially_adopted` | `iss-00292` dogfood metrics / runtime criteria artifacts | Epic `report.md`; `iss-00293` handoff | dogfood metrics と promote / defer / reject criteria は判断材料として採用するが、runtime promotion approval は採用しない。backend adapter readiness、manual fallback exercise、human edit burden、aggregate reviewer loop は `iss-00293` または後続判断へ残す。 | `issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/`; `issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/report.md` | `iss-00293` final quality gate で再評価する |
| EAL-013 | `adopted` | `iss-00293` final local verification | Epic `report.md`; PR readiness evidence | `iss-00293` final gate で、先行 Issue 完了、manual matrix、backend adapter、snapshot correction、full baseline を確認した。PR #294 の Provider CI / mypy failure は修正済みで、再観測では CI pass を確認した。Codex review carryover P1 4件も local repair 済みで、再 push / 再観測へ進める。 | `issues/iss-00293-final-epic-quality-gate-and-mergeable-pr/report.md`; `tests/unit/infra/test_init_update.py`; `uv run pytest` -> `1910 passed, 74 skipped`; `make lint` -> pass; focused manual tests -> `215 passed` | push P1 repair and record merge preparation evidence |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は ChatGPT ZIP authoring pack を evidence-only delivery として扱い、SpecDock local authority を維持することを主目的にした。 | dogfood-only script、future runtime promotion、Issue seeds を副次要件として分離した。 | 低。reviewer gate replacement / shipped runtime 化を v1 scope 外に明記した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent initiative docs、workflow docs、`epic-00283/artifacts/`、ChatGPT Use manual dogfood output、ZIP authoring pack dogfood output、Issue-local draft artifacts、`.assurance.json` | Blocking question: none。Non-blocking design questions は raw ZIP storage、runtime promotion threshold、profile mismatch salvage、Strict/Critical specialist evidence path。 | EAL-001〜EAL-008c を採用 / 部分採用し、Epic `requirement.md` と Issue canonical `requirement.md` へ再記述した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 | いいえ | 後続 Issue execution-ready 確認へ進める |
| design-epic | ZIP authoring pack design draft、naming proposal、workflow docs、requirement seeds、local Issue creation result | Blocking question: none。provider detail は human-facing surface に出さない。 | EAL-008a を採用し、Epic `design.md` へ control plane / data plane、ZIP lifecycle、profile boundary、failure design、test strategy を再記述した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 | いいえ | 後続 Issue execution-ready 確認へ進める |
| design-issues | Issue-local draft designs、Issue canonical requirements、Epic readiness contract | Blocking question: none。draft artifact は証跡専用であり正本ではない。 | EAL-008c を採用し、`iss-00284`〜`iss-00292` の canonical `design.md` へ scope、non-scope、入出力、失敗時設計、検証観点を再記述した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 | いいえ | 後続 Issue execution-ready 確認へ進める |
| plan-epic | ZIP authoring pack plan draft、Issue candidate drafts、Issue creation result、Issue-local draft artifact path index、Issue readiness contract | Blocking question: none。local assurance profile は現行 classifier で全 Issue `standard` / `provisional`。strict 推奨 Issue は `authorized_profile` を上書きせず strict 相当 obligation を追加する。 | EAL-008a / EAL-009 を採用し、Epic `plan.md` へ 10 Issue slicing、dependency order、dogfood scenarios、handoff path index、Issue readiness contract、`iss-00293` の最終品質ゲートを再記述した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 | いいえ | 後続 Issue execution-ready 確認へ進める |
| plan-issues | Issue-local draft plans、Issue canonical requirements / designs、Epic strict 相当 obligation | Blocking question: none。ChatGPT output は reviewer pass claim に使わない。 | EAL-008c を採用し、`iss-00284`〜`iss-00292` の canonical `plan.md` へ実装ステップ、検証計画、完了条件、Spec-Locked Closure Index、Assurance / reviewer obligation を再記述した。 | passed: fresh `spec-reviewer` 019f3999-911a-7381-8155-3cda5fcf3403 | いいえ | 後続 Issue execution-ready 確認へ進める |

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
| SR-20260707-001 | failed / P1 -> fixed | Issue-local draft artifact に delegated draft provenance fields が不足していた。 | 27 個の `*from-authoring-pack.md` に provenance / adoption metadata を追加した。 | fixed in prior review cycle |
| SR-20260707-002 | failed / P1 -> fixed | strict 推奨 Issue と local `authorized_profile=standard` の関係が不明確だった。 | Epic `plan.md` と各 Issue `plan.md` に、local assurance は上書きせず strict 相当 obligation を追加する方針を明記した。 | fixed |
| SR-20260707-003 | failed / P1 -> fixed | 各 Issue の AC が共通 trace 確認に偏り、成果物固有の検証条件が不足していた。 | 9 Issue の canonical `requirement.md` と draft requirement artifact に、成果物固有の AC-005 / AC-006 を追加した。 | fixed in prior review cycle |
| SR-20260707-004 | failed / P1 -> fixed | C07 の profile mismatch probe が C04 / `iss-00287` に依存することが Epic plan の依存グラフに反映されていなかった。 | `plan.md` の依存グラフに `C04 -> C07 -> C09` を追加した。 | fixed in prior review cycle |
| SR-20260707-005 | chatgpt-use review -> fixed | Child Issue canonical `design.md` / `plan.md` が未具体化のままだと、current request の spec-reviewer readiness に不足する。 | `iss-00284`〜`iss-00292` の canonical `design.md` / `plan.md` / `report.md` を Issue-local draft artifacts から main orchestrator が採否判断した内容として作成した。 | fixed; current `iss-00284` post-fix re-review passed（agent `019f387a-e7c2-73b3-ae10-89d8dd487cfb`） |
| SR-20260707-006 | spec-reviewer failed / P1 -> fixed | Issue reports と Epic report に adopted-vs-candidate contradiction が残っていた。 | EAL-008c、Spec Authoring Gate、Issue EAL / SID を採用済み状態に統一した。 | fixed; current `iss-00284` post-fix re-review passed（agent `019f387a-e7c2-73b3-ae10-89d8dd487cfb`） |
| SR-20260707-007 | spec-reviewer failed / P1 -> fixed | Issue plans が memo 状態で、executable closure contract が不足していた。 | `iss-00284`〜`iss-00293` の `plan.md` に canonical implementation plan、Spec-Locked Closure Index、S90、S99、Final Exit Contract を追加した。 | fixed; current `iss-00284` post-fix re-review passed（agent `019f387a-e7c2-73b3-ae10-89d8dd487cfb`） |
| SR-20260707-008 | spec-reviewer failed / P2 -> fixed | ZIP evidence artifact に host-local absolute path が残っていた。 | research artifact 内の ChatGPT generated ZIP path を redacted evidence reference へ置換し、`zip_sha256` を正本証跡として使う方針へ寄せた。 | fixed; current `iss-00284` post-fix re-review passed（agent `019f387a-e7c2-73b3-ae10-89d8dd487cfb`） |
| SR-20260707-009 | ChatGPT readiness review / P1 -> fixed | Epic `report.md` は Issue canonical docs を採用済みと記録していたが、Epic `plan.md` の Issue 引き渡し paragraph が「採用は後続 Issue planning」と古い状態を残していた。 | `plan.md` の Issue 引き渡し paragraph を、Issue-local draft artifacts は evidence-only、`iss-00284`〜`iss-00292` の canonical docs は main orchestrator が採否判断して再記述済み、後続 execution では fresh reviewer result と Issue report evidence を readiness 確認する、という current state へ更新した。 | fixed; fixed; fresh `spec-reviewer` re-review passed |

## Relay execution correction ledger

| ID | correction | status |
|---|---|---|
| RELAY-20260707-001 | `iss-00284`〜`iss-00292` のリレー実行方針は、各 Issue の canonical `plan.md` と Issue-local `artifacts/*draft-plan*from-authoring-pack.md` の両方に、証跡として矛盾しない形で残す方針へ修正した。 | fixed; fresh re-review passed |
| RELAY-20260707-002 | `iss-00293` は final gate Issue 自体の正本 requirement / design / plan / report として作成し、`assurance classify --stage requirement --issue iss-00293` で `standard` / `provisional` を確認した。 | fixed; `spec-dock validate` passed |
| RELAY-20260707-003 | `iss-00284`〜`iss-00292` の Issue-local draft-design / draft-plan は evidence-only handoff として保持しつつ、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | fixed; fresh re-review passed |

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-epic-00283-001 | `iss-00284`〜`iss-00292` の Issue-local draft artifacts は evidence-only handoff であり、採否判断済みの内容だけを canonical Issue docs へ再記述する。 | accepted | EAL-008b / EAL-008c; Issue report SID entries | 後続 Issue execution-ready 確認へ進める |
| SID-epic-00283-002 | 個別 Issue ごとに Pull Request を作成せず、実装完了後は `issue finish` して次 Issue を `issue start` するリレー実行とする。 | accepted | EAL-009; Epic `plan.md` リレー実行 / PR 方針; `iss-00293` specs | `iss-00284` から順番に実行し、PR は `iss-00293` に集約する |
| SID-epic-00283-003 | `iss-00293` は Epic 最後の品質ゲート、manual test evidence、PR 作成、CI / review 修正、mergeable 確認を担当する。 | accepted | `iss-00293` requirement / design / plan / report; assurance classify result | `iss-00292` 完了後に開始する |
| SID-epic-00283-004 | ChatGPT Use / Oracle 実行の backend command は SpecDock repo に直書きされた個人環境絶対パスではなく、設定で差し替え可能な invocation contract として扱う。 | accepted | EAL-011; amended Epic `plan.md`; amended `iss-00293` docs; `invoke_chatgpt_backend.py`; adapter focused tests | implemented in `iss-00293` S04; include in final reviewer / PR gate |
| SID-epic-00283-005 | `iss-00292` の runtime promotion criteria は decision material であり、runtime promotion を承認しない。formal runtime promotion の現時点 stance は defer とし、final gate / backend adapter / manual fallback / human edit burden の確認後に再評価する。 | accepted | EAL-012; `iss-00292` artifacts and report | `iss-00293` final quality gate へ引き継ぐ |

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
  - PR #294: `https://github.com/chemitaro/spec-dock/pull/294`
  - 初回 PR 観測では Provider CI / mypy が失敗したため、`iss-00293` の修正ループで manual test helper の型修正を実施した。再観測で CI pass を確認したが、Codex review carryover P1 が4件残ったため、安全境界修正を実施した。再 push / 再観測後に merge preparation gate を更新する。

## 受け入れ条件（E-AC）の達成状況

- E-AC-001〜E-AC-010:
  - 実施済み。`iss-00284`〜`iss-00291` の実装 / dogfood / docs Issue で evidence を記録済み。
- E-AC-011〜E-AC-012:
  - 判断材料は作成済み。`iss-00292` の dogfood metrics / runtime criteria artifacts に成功・失敗・ブロック理由と promote / defer / reject criteria を記録した。
  - runtime promotion 自体は未決定。現時点では formal runtime promotion を defer し、`iss-00293` の final quality gate へ引き継ぐ。
  - backend adapter verification は `iss-00293` S04 で実施済み。`SPECDOCK_CHATGPT_COMMAND` / `ORACLE_CHATGPT_COMMAND` による差し替え、未設定 fail-closed、`shell=False` argv ABI、local wrapper hardcode guard を確認した。
- Final local gate:
  - `iss-00284`〜`iss-00292` は GitHub 上で CLOSED、`iss-00293` は OPEN で PR delivery を担当する。
  - `./spec-dock/scripts/spec-dock deps check iss-00293` は `ready=true` / `blockers=0`。
  - `uv run pytest` は初回、checked-in dogfooding `.meta.json` snapshot に `epic-00283` / `iss-00284`〜`iss-00293` が未登録だったため 1 failed。snapshot を更新後、targeted rerun は `1 passed`、full rerun は `1910 passed, 74 skipped`。
  - PR #294 を作成済み。初回観測では `validate` check は pass、Provider CI は `make lint` / mypy で fail。local repair 後の再観測では CI pass。Codex review carryover P1 4件に対し、symlink extract dir、unsafe text payload、provenance/preflight binding、nested `authorized_profile` claim の修正と回帰テストを追加した。再 push / 再観測で CI / review / mergeable status を確定する。

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

## Local Path Evidence Boundary

- Historical local wrapper paths that remain in older research artifacts are host-local invocation evidence only. Canonical adoption evidence uses redacted references, repo-relative paths, and `zip_sha256`; host-local paths are not adoption targets or shipped documentation.
