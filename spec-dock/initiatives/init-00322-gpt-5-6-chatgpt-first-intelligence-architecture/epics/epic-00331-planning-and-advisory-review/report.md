---
種別: レポート（Epic）
ID: "epic-00331"
タイトル: "ChatGPT Planning and Advisory Review"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-00322"]
---

# epic-00331 ChatGPT Planning and Advisory Review — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - Oracle製品依存境界をEpic Requirement／Designへ反映し、fresh defect-only spec reviewをPASSした。
  - iss-00334のS01〜S07実施履歴は保持し、修復実装はS08以降として未実施である。
- 次のマイルストーン:
  - iss-00334 S08 Provider-owned Direct Oracle Adapter。
- ブロッカー:
  - なし。実装後のissue-wide final review／Deliveryは別ゲートとして残る。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-20260729-ORACLE-BOUNDARY | adopted | Human指示、ChatGPT Pro Blue Team、Codex Main検証、fresh `spec-reviewer` | Epic `requirement.md`／`design.md`とiss-00334 amendment | 製品runtimeは個人`chatgpt-use`ではなくPATH Oracle本体へ依存し、operator planning toolとproduct dependencyを分離する必要がある。exact branch、Prompt/reference分離、ZIP-only Planner出力をEpic backboneとして閉じた | iss-00334 `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip`; `artifacts/20260729t020725z-review-oracle-boundary-planning-pass.json`; ZIP SHA-256 `9fc16cc1bc2e5ee45576a64e863448c9c1247e0ec31cce0a8d5912881ef2d552` | iss-00334 S08以降で実装し、sibling Issueの境界を変更しない |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| Oracle product dependency boundary | 配布可能なChatGPT-first Planning／Review workflowはprovider-owned adapterからPATH Oracleを直接利用する | operator-local `chatgpt-use`の既存知見はreference-onlyで再利用可能 | low。個人wrapperの便利さをproduct contractへ混入させない | pass。fresh defect-only `spec-reviewer` findings 0 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement — Oracle boundary amendment | current Epic／Issue docs、provider source／tests、Oracle境界調査、ChatGPT ZIP | planning作業は`chatgpt-use`利用可、product dependencyはOracle本体のみ | Epic requirementへ採用 | passed | no | design／iss-00334 implementationへhandoff |
| design — Oracle boundary amendment | PATH executable、direct argv、exact branch、Prompt/reference、Oracle file artifact／ZIP contract | 個人wrapperの知見は再実装可能だがruntime依存は禁止 | Epic designへ採用 | passed | no | iss-00334 S08から実装 |
| plan | current Epic plan | 今回はIssue実装計画への追加作業だけを要求 | no change | not rerun | no | existing Epic planを維持 |

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
| ChatGPT Pro Blue Team | epic-00331／iss-00334 | iss-00334 `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip` | current Epic／Issue docs、Oracle境界調査、source／tests、reference-only `chatgpt-use` Skill／wrapper | Epic Requirement／Design、Issue Requirement／Design／Plan | adopted | Epic Requirement／Design、Issue canonical planning、Issue Report | ZIP SHA／inventory、Plan prefix、PlantUML、SpecDock validate、assurance verify pass | Mainが検証済みclaimsだけをwhole-file統合 | transcript、個人環境値、default branch fallback、実装済みclaim | none | fresh defect-only `spec-reviewer` pass | iss-00334 S08 implementationへhandoff |

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
- 新規ADRなし。今回の判断はepic-00331とiss-00334のPlanning／Review実装境界に閉じる。

## 完了した Issue / PR / Release (必須)
- なし。iss-00334はOracle境界修復S08以降が未実施。

## 受け入れ条件（E-AC）の達成状況 (必須)
- Oracle直接依存／個人wrapper非依存の仕様化: Pass（Epic Requirement／Design、fresh spec review）。
- 製品実装とdistribution evidence: Pending（iss-00334 S08〜S14）。

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- iss-00334:
  - S08以降でprovider-owned Oracle adapter、Prompt／reference分離、ZIP artifact、projection／testsを実装する。

## 省略/例外メモ (必須)
- operator planningではユーザー指定の`chatgpt-use`を利用したが、product runtime dependencyとしては採用していない。
