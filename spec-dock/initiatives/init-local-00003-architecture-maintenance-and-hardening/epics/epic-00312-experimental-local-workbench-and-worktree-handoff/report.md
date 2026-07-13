---
種別: レポート（Epic）
ID: "epic-00312"
タイトル: "Experimental Local Workbench And Worktree Handoff"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00312 Experimental Local Workbench And Worktree Handoff — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - Epic scaffold、GitHub sync、6件のuser-answer interview、baseline research、clarification synthesis、ChatGPT 5.6 Pro GitHub-synced analysis、canonical requirement draftを完了した。
  - Requirement、Design、Planは一度fresh `spec-reviewer`でpassしたが、新しいArtifact import decision evidenceとGPT-5.6 Pro分析によりstaleとなった。Issue node creationは未開始。
- 次のマイルストーン:
  - Artifact type互換判断をclarificationし、requirement→design→planを順に更新・fresh reviewして、改訂Issue分割をhuman approvalへ提示する。
- ブロッカー:
  - `chatgpt-output` type追加により、従来blank Artifactで有効だった`chatgpt-output-*` slugを予約prefixへ変更してよいかhuman decision待ち。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） | 6件のuser-answer interview、baseline research、clarification synthesis | `requirement.md` の配置、非正本境界、root運用、scoped copy、merge、rollout要件 | 8件のclarification evidenceを検証し、6件の明示回答をproduct decisionとして採用。session/manifest/TTL、root bulk copy、content filtering、sync、dogfood-only実装を禁止した | `artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md` から `artifacts/20260713t015912z-interview-unfiltered-filesystem-copy-without-content-classification.md` | fresh requirement review |
| EAL-002 | 部分採用（`partially_adopted`） | ChatGPT 5.6 Pro GitHub-synced research | `requirement.md` の候補要件、AC、3-Issue分割seed | GitHub `main@081ba648` を参照したarchitecture分析を採用。exact CLI spelling、error名、port分割、symlink/collision/preflight/partial fieldはdesign候補へ分離し、親制約とcopy policyはhuman dispositionを優先した | `artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md` | fresh requirement review |
| EAL-003 | 採用（`adopted`） | product-owner interview | 親 Initiative と `requirement.md` のlocal-only境界 | local-only廃止対象はInitiative/Epic/Issue等のnodeであり、Workbenchは非永続の一時fileであるとの回答で親trace blockerを解消した | `artifacts/20260713t013008z-interview-local-only-node-prohibition-and-disposable-workbench-boundary.md` | fresh `spec-reviewer` で親整合を再確認 |
| EAL-004 | 採用（`adopted`） | product-owner interview | `requirement.md` のunfiltered copy boundary | extension、language、purpose、content、filename、special-entry分類を含む独自copy対象判定を作らず、通常のfilesystem copyへ委ねる回答を採用した | `artifacts/20260713t015912z-interview-unfiltered-filesystem-copy-without-content-classification.md` | fresh `spec-reviewer` で採用済みcopy policyとの整合を再確認 |
| EAL-005 | 採用（`adopted`） | fresh `spec-reviewer` findings | requirement phase correction/promotion | 5回のfail findingを全て反映し、親node境界、unfiltered copy、WHAT/HOW分離、AC trace、report observed stateを閉じた | 6回目 fresh reviewer `sixth_review_epic_00312_requirement`、2026-07-13、`review_status: pass` | requirementをpromoteしdesign phaseへ進む |
| EAL-006 | 採用（`adopted`） | fresh design `spec-reviewer` findings | `design.md` / design promotion | Exact `.workbench` authoring source拒否、source symlink非dereference、destination ancestry containment、source Workbench missing=`no_source`/no mutationを採用。内容classifierではなくsemantic/path/CLI境界として限定し、2回目fresh reviewerで閉じた | reviewer `rereview_epic_00312_design`、2026-07-13、`review_status: pass` | designをpromoteしplan phaseへ進む |
| EAL-007 | 採用（`adopted`） | fresh plan `spec-reviewer` findings | `plan.md` | W1/W2/W3のclosure ownershipを実scopeへ合わせ、E-AC-003をW2、E-RQ-016/E-AC-009をW2 CLI surfaceとW3 docs surfaceへ分担した | reviewer `review_epic_00312_plan`、2026-07-13、`review_status: fail` | fresh plan reviewerを再実行 |
| EAL-008 | 採用（`adopted`） | fresh plan re-review finding | `requirement.md` handoff seed / `design.md` DS and AC trace | Planで発見したownership gapを上流へ戻し、E-AC-003をW2へ、E-AC-009をW2 CLI/no-syncとW3 docsへ分担した。Product requirement/design mechanismは変更していない | requirement reviewer `ownership_rereview_epic_00312_requirement`: pass、design reviewer `ownership_rereview_epic_00312_design`: pass、2026-07-13 | stale解除。Fresh plan reviewerを再実行 |
| EAL-009 | 採用（`adopted`） | fresh plan `spec-reviewer` finding | `report.md` observed state | Plan本体のownership/dependency/final quality/deferred PR/human approval/draft lifecycleは整合。Reportに上流re-passを記録してからfresh plan verdictを取得する | reviewer `third_review_epic_00312_plan`、2026-07-13、`review_status: fail` | report修正後にfresh plan reviewer |
| EAL-010 | 採用（`adopted`） | fresh plan `spec-reviewer` | `plan.md` / plan promotion | W1/W2/W3 ownership、W1→W2、W3 depends on W1+W2、W3 final quality/PR、deferred PR、human approval、draft lifecycleがreviewed requirement/designと整合した | reviewer `fourth_review_epic_00312_plan`、2026-07-13、`review_status: pass` | planをpromoteしhuman Issue decomposition approval gateへ進む |
| EAL-011 | blocked（`blocked`） | user-proposed decision + GPT-5.6 Pro GitHub-synced research | Epic 00312 requirement/design/plan revision | Byte-preserving `artifact import chatgpt-output`はWorkbench→durable evidence境界を閉じるため同一Epicへ統合する方向を支持。W3 import runtime、W4 workflow、W5 final qualityへの5-Issue再分割候補を採用検討する。一方typed token追加はblank prefix互換とaccepted Artifact ADRを変更するためhuman dispositionとsuperseding ADRが必要 | `artifacts/20260713t023439z-decision-candidate-chatgpt-output-artifact-import-contract.md`; `artifacts/20260713t031057z-research-chatgpt-5-6-pro-artifact-import-integration-analysis.md`; transcript SHA-256 `3729ae71031219be3eb2507cd2c7da84dc3306821ebb646b39c7144dd3a1e7d5` | one-question clarification後、EAL disposition、superseding ADR candidate、canonical phase refresh |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Git-ignored、non-canonical、disposableな低摩擦scratchを、分類/管理systemなしで提供する | scoped copyの境界安全、failure transparency、provider/dogfood parity | 低。独自classifier/preflightをrequirementから除外し、標準copy boundaryを維持した | pass。6回目fresh requirement reviewer |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Previous pass + new Artifact import decision/research | typed token/blank prefix互換のhuman answer待ち | new evidenceはunreviewed/blocked | stale-pass | yes | clarification後にcanonical refresh + fresh reviewer |
| design | Previous pass + new Artifact import decision/research | requirement refresh待ち | new evidenceはunreviewed/blocked | stale-pass | yes | requirement pass後にrefresh + fresh reviewer |
| plan | Previous 3-Issue pass + proposed 5-Issue split | requirement/design refresh待ち | new evidenceはunreviewed/blocked | stale-pass | yes | design pass後にrefresh + fresh reviewer + human approval |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used。ChatGPT 5.6 ProをGitHub-synced evidence producerとして使用した。
- canonical adoption:
  - ChatGPT outputはraw research evidenceのまま保存し、main orchestratorが採否をEALへ記録してrequirementを再記述した。delegated output自体をcanonicalへ昇格していない。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: role, phase, scope, authorization source, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT 5.6 Pro evidence producer | epic-00312 | `artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md` | GitHub `chemitaro/spec-dock` `main@081ba648`、Epic clarification artifacts | Epic requirement/design/plan candidates、Issue slicing evidence | 部分採用（partially_adopted） | `requirement.md`、EAL | GitHub-sync preflight pass | orchestratorが候補を検証・再記述 | 親制約の未承認解釈、special-entry独自preflight、exact CLI/mechanismのauthority claim | なし | 5回fail findingsを反映し6回目pass | requirement promoted。design/plan候補は各phaseで別途採否・fresh review |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)
- adr-xxxx-...: <1行要約>
- ...

## 完了した Issue / PR / Release (必須)
- iss-xxxx-...: Done（PR: ...）
- ...

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: Pass / Fail（証拠: ...）
- E-AC-002: ...

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- iss-xxxx-...:
  - ...

## 省略/例外メモ (必須)
- 該当なし
