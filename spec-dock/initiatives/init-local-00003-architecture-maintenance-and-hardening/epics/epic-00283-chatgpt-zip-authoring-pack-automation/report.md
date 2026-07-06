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
  - ここまでの ChatGPT Use / GPT-5.5 Pro Extended による調査・議論 artifact を `epic-00283/artifacts/` へ集約済み。
  - `spec-dock-clarification` の source-grounded grill loop と ChatGPT Use manual dogfood により、追加の blocking interview は不要と判断した。
  - `requirement.md` / `design.md` / `plan.md` は具体化済みで、Epic canonical docs、9 Issue 配下の canonical docs、各 Issue の from-authoring-pack draft artifact、各 `.assurance.json` を含む fresh `spec-reviewer` re-review が pass した。
  - ChatGPT Use により、Epic design / plan draft と 9 Issue candidate draft を含む downloadable ZIP authoring pack を生成し、prompt / output / lightweight validation 結果を scope-local research artifact に保存した。
  - ZIP authoring pack の design / plan / Issue candidate draft は、main orchestrator が human-facing naming へ補正した上で `design.md` / `plan.md` と Issue-local draft artifacts へ採用した。
  - 9 Issue を作成し、各 Issue に draft requirement / draft-design / draft-plan artifact を配置済み。
  - local assurance は全 Issue `standard` / `provisional` であり、strict 推奨 Issue には `authorized_profile` を上書きせず strict 相当の追加 obligation を Issue readiness contract として課す。
- 次のマイルストーン:
  - 後続 Issue planning では、Issue-local draft artifacts を採否判断し、canonical Issue `design.md` / `plan.md` へ採用する場合は Issue scope で改めて fresh reviewer gate を通す。
- ブロッカー:
  - 現時点の Epic planning / Issue draft handoff package に対する fresh `spec-reviewer` blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 部分採用（`partially_adopted`） | research | `requirement.md` | ChatGPT Use / GPT-5.5 Pro Extended を SpecDock authoring backend として使う方向性、evidence-only boundary、reviewer gate 非置換を要件へ採用した。初期配置が `init-local-00002` だった前提は後続判断で superseded。 | `artifacts/20260706t090820z-research-chatgpt-oracle-advanced-analysis.md` | requirement reviewer gate で妥当性を確認する |
| EAL-002 | 部分採用（`partially_adopted`） | discussion | `requirement.md` | Spec Authoring Batch の workflow redesign、bundle generation と staged adoption の分離、candidate Issue slicing の方向性を要件へ採用した。 | `artifacts/20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md` | design phase で batch/ZIP lifecycle へ再整理する |
| EAL-003 | 部分採用（`partially_adopted`） | research | `requirement.md` | Reviewer gate の即時置換は行わず、ChatGPT output を advisory / shadow / authoring evidence として扱う制約を採用した。 | `artifacts/20260706t111806z-research-chatgpt-reviewer-gate-script-analysis.md` | reviewer replacement は v1 scope 外として維持する |
| EAL-004 | 採用（`adopted`） | research | `requirement.md` | Epic -> Issue / Issue bundle authoring automation の script candidates、dogfood-only placement、manual fallback、metrics を要件へ採用した。 | `artifacts/20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices.md` | design / plan で Issue slicing へ具体化する |
| EAL-005 | 採用（`adopted`） | research | `requirement.md` | ZIP は first-class delivery format だが authority format ではないこと、profile は local assurance authority に残すこと、safe intake / validation / staged adoption を要件へ採用した。 | `artifacts/20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control.md` | design phase で ZIP schema / validator contract を固定する |
| EAL-006 | 部分採用（`partially_adopted`） | artifact | `requirement.md` | 新メンバー向けオンボーディング資料の要約・用語整理を requirement wording の補助 evidence として使った。canonical requirement には要件として再記述した。 | `artifacts/20260706t133043z-chatgpt-zip-authoring-onboarding-brief.md` | design / docs phase で正式 onboarding docs が必要か再判断する |
| EAL-007 | 採用（`adopted`） | chatgpt-use research | `requirement.md` | Manual ChatGPT Use dogfood により `unresolved_user_questions: none`、requirement draft、candidate Issue seeds、dogfood observations が得られたため、要件具体化へ採用した。 | `artifacts/20260706t140325z-research-epic-requirement-clarification-dogfood.md` | requirement reviewer gate へ進める |
| EAL-008 | 採用（`adopted`） | chatgpt-use ZIP authoring pack | `design.md` / `plan.md` / Issue handoff draft artifacts | ChatGPT Use が Epic design / plan draft、9 Issue candidate draft、naming proposal を含む ZIP を生成できることを確認した。内容は main orchestrator が `oracle-*` provider-facing 名を避ける human-facing naming へ補正し、canonical Epic docs と Issue-local draft artifacts へ反映した。 | `artifacts/20260706t145350z-research-chatgpt-zip-authoring-pack-prompt-output-dogfood.md`; `/Users/iwasawayuuta/.oracle/sessions/specdock-epic-00283-zip-authoring/artifacts/specdock-epic-00283-authoring-pack-codex-chatgpt-2098110.zip`; `design.md`; `plan.md`; `issues/iss-00284-*`〜`issues/iss-00292-*` | fresh `spec-reviewer` gate を実行し、Issue planning で draft artifact の採否を個別に記録する |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は ChatGPT ZIP authoring pack を evidence-only delivery として扱い、SpecDock local authority を維持することを主目的にした。 | manual-tests dogfood、future runtime promotion、Issue seeds を副次要件として分離した。 | 低。reviewer gate replacement / shipped runtime 化を v1 scope 外に明記した。 | passed（fresh `spec-reviewer` re-review, agent `019f381a-7fa4-7e90-9557-f29ff8f9b2ea`） |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent initiative docs、workflow docs、`epic-00283/artifacts/`、ChatGPT Use manual dogfood output、ZIP authoring pack dogfood output、Issue-local draft artifacts、`.assurance.json` | Blocking question: none。Non-blocking design questions は raw ZIP storage、runtime promotion threshold、profile mismatch salvage、Strict/Critical specialist evidence path。 | EAL-001〜EAL-008 を採用 / 部分採用し、`requirement.md` と Issue draft requirements へ再記述した。 | passed（fresh `spec-reviewer` re-review, agent `019f381a-7fa4-7e90-9557-f29ff8f9b2ea`） | いいえ。 | Epic design / plan と Issue draft handoff package へ進める。 |
| design | ZIP authoring pack design draft、naming proposal、workflow docs、requirement seeds、local Issue creation result、Issue-local draft designs | Blocking question: none。`oracle-*` は provider detail とし、human-facing surface は `authoring-pack-*` に寄せる。 | EAL-008 を採用し、`design.md` へ control plane / data plane、ZIP lifecycle、profile boundary、failure design、test strategy を再記述した。Issue canonical `design.md` は placeholder に留めた。 | passed（fresh `spec-reviewer` re-review, agent `019f381a-7fa4-7e90-9557-f29ff8f9b2ea`） | いいえ。 | Epic plan と Issue draft handoff package へ進める。 |
| plan | ZIP authoring pack plan draft、Issue candidate drafts、Issue creation result、Issue-local draft artifact path index、Issue readiness contract | Blocking question: none。local assurance profile は現行 classifier で全 Issue `standard` / `provisional`。strict 推奨 Issue は `authorized_profile` を上書きせず strict 相当 obligation を追加する。 | EAL-008 を採用し、`plan.md` へ 9 Issue slicing、dependency order、dogfood scenarios、handoff path index、Issue readiness contract を再記述した。Issue canonical `plan.md` は placeholder に留めた。 | passed（fresh `spec-reviewer` re-review, agent `019f381a-7fa4-7e90-9557-f29ff8f9b2ea`） | いいえ。 | 後続 Issue planning では draft artifact 採否と Issue-scope reviewer gate を個別に行う。 |

## 委任ドラフト証跡（Delegated Draft Evidence）

- 委任 authoring の使用:
  - used as evidence-only dogfood.
- 使用内容:
  - ChatGPT Use で downloadable ZIP authoring pack を生成し、Epic design / plan draft と 9 Issue candidate draft を取得した。
  - ZIP output は authority ではなく delegated draft evidence として扱い、main orchestrator が source / scope / naming / profile boundary を確認してから canonical docs と Issue-local draft artifacts へ採用した。
- lifecycle state:
  - `produced` -> `locally_reviewed_by_main_orchestrator` -> `adopted_to_draft_artifacts`。
- 昇格判断:
  - canonical `requirement.md` へ採用した内容は EAL-007 として記録した。
  - canonical `design.md` / `plan.md` と Issue-local draft artifacts へ採用した内容は EAL-008 として記録した。

## Spec reviewer correction ledger

| ID | reviewer verdict | finding | correction | status |
|---|---|---|---|---|
| SR-20260707-001 | failed / P1 -> passed | Issue-local draft artifact に delegated draft provenance fields が不足していた。 | 27 個の `*from-authoring-pack.md` に `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []`、`diff_guard_result`、report evidence destination を追加した。 | fixed; fresh re-review passed |
| SR-20260707-002 | failed / P1 -> passed | strict 推奨 Issue と local `authorized_profile=standard` の関係が不明確だった。 | `plan.md` に Issue readiness contract を追加し、local assurance は `standard` / `provisional` のまま保持しつつ、該当 Issue に strict 相当の追加 obligation を課すことを明記した。 | fixed; fresh re-review passed |
| SR-20260707-003 | failed / P1 -> passed | 各 Issue の AC が共通 trace 確認に偏り、成果物固有の検証条件が不足していた。 | 9 Issue の canonical `requirement.md` と draft requirement artifact に、成果物固有の AC-005 / AC-006 を追加した。 | fixed; fresh re-review passed |
| SR-20260707-004 | failed / P1 -> passed | C07 の profile mismatch probe が C04 / `iss-00287` に依存することが Epic plan の依存グラフに反映されていなかった。 | `plan.md` の依存グラフに `C04 -> C07 -> C09` を追加した。 | fixed; fresh re-review passed |


## 決定事項（ADRリンク）

- 該当なし。

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
  - 各 Issue に `draft-requirement` / `draft-design` / `draft-plan` artifact を配置済み。

## 受け入れ条件（E-AC）の達成状況

- E-AC-001〜E-AC-012:
  - 未実施。Requirement authoring phase であり、implementation / dogfood scripts は未着手。

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

## 省略/例外メモ

- `epic-00283` の作成時、runtime が GitHub issue `#283` を自動作成した。
- ChatGPT ZIP dogfood run では、GitHub connector が `codex/chatgpt` 上の対象 file / expected commit を参照できた一方、branch head SHA の直接 observation は limited と記録された。local preflight では `HEAD == origin/codex/chatgpt == 209811098dc3067a94a3894cb89f9c6f5f6eae31` を確認済みだが、ZIP output 自体は引き続き advisory evidence として扱う。
