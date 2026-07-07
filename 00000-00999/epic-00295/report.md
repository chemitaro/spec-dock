---
種別: レポート（Epic）
ID: "epic-00295"
タイトル: "ChatGPT Authoring Pack Installed Runtime"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00295 ChatGPT Authoring Pack Installed Runtime — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `epic-00295` を `init-local-00003` 配下に作成し、GitHub issue `#295` と連携した。
  - active scope を `init-local-00003` / `epic-00295` に設定した。
  - 先行分析として、ChatGPT workflow integration analysis と authoring-pack install architecture analysis を Epic-local `artifacts/` に移した。
  - 要件定義書には、仕切り直し理由、provider / consumer 境界、runtime / installed asset 化の seed を記録した。
  - ユーザー interview により、第一優先は Option A「大きな仕事を一括で計画し、実装可能な Issue へスライスする体験」であり、Option B「Issue 実行直前の正本化」は A の下流としてセットで扱う方針を確認した。
  - 人間の明示承認 checkpoint は Issue node 作成前の分解案承認に置き、Issue draft adoption / canonicalization は自動化対象にする方針を確認した。
  - 上記のユーザー回答と先行調査を含めて ChatGPT-Use / GPT-5.5 Pro Extended に全体 workflow と best practice の再分析を依頼し、最終分析 artifact を作成した。
  - 追加方針として、単一 skill ではなく human quality gate ごとに複数 skill / script を分ける可能性と、GitHub 同期 preflight を含む workflow を ChatGPT-Use / GPT-5.5 Pro Extended に再分析させ、追加 research artifact を作成した。
  - 追加インタビューは不要と判断し、ChatGPT-Use / GPT-5.5 Pro Extended に要件定義書・設計書・実装計画書の具体化案を作成させ、正本 `requirement.md` / `design.md` / `plan.md` へ部分採用した。
  - ユーザー回答により、同期できない場合の明示的な `local-context` evidence mode と、中間 Issue では PR を作らず final quality gate / PR delivery Issue で mergeable PR を作成する relay delivery policy を採用した。
- 次のマイルストーン:
  - 先行分析 artifact を採用判断し、Epic requirement / design / plan を具体化する。
  - 既存 `epic-00283` を dogfood helper 実験として位置づけ、新 Epic では installed runtime / workflow surface を正本スコープにする。
- ブロッカー:
  - なし。詳細要件の確定と reviewer gate は未実施。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 部分採用（`partially_adopted`） | 調査（`research`） | Epic 要件 seed / 後続設計判断 | ChatGPT authoring-pack を workflow に組み込む必要性は採用した。一方で、既存 gate を置換せず evidence lane として扱う境界は今後の requirement / design / plan で再確認する。 | `artifacts/20260707t140041z-01-research-chatgpt-workflow-integration-analysis.md` | Epic requirement / design / plan 具体化時に再採用判断する |
| EAL-002 | 採用（`adopted`） | 調査（`research`） | Epic スコープ / architecture boundary | root `scripts/authoring-pack/` だけでは導入先 product repo に届かないという欠陥を、この Epic の主要問題として採用した。正本実装は provider-side installed runtime / assets へ移す方向で検討する。 | `artifacts/20260707t140041z-research-authoring-pack-install-architecture-analysis.md` | Epic design で target layout と migration plan を具体化する |
| EAL-003 | 採用（`adopted`） | ユーザー回答（`interview`） | Epic priority / workflow objective | 第一優先は Option A「大きな仕事を一括で計画する体験」。Option B は A の下流としてセットで扱う。大きな仕事を Initiative / Epic / Issue へスライスし、各 Issue の実装前に正式な仕様・設計・計画へ整える workflow をこの Epic の主軸にする。 | `artifacts/20260707t143000z-interview-workflow-first-chatgpt-authoring-redesign-interview-1.md` | requirement / design / plan 具体化時に primary objective として採用する |
| EAL-004 | 部分採用（`partially_adopted`） | 調査（`research`) | workflow taxonomy / skill modes | ChatGPT の pre-interview 暫定分析は workflow-first、ChatGPT Batch Evidence Lane、Issue Planning の `zero-base` / `draft-adoption` mode、handoff-ready と execution-ready の分離を採用候補として扱う。ただし最優先体験はユーザー回答により A -> B の一連 workflow へ補正する。 | `artifacts/20260707t143719z-research-workflow-first-chatgpt-authoring-redesign-provisional-analysis.md` | 次回 ChatGPT 分析ではユーザー回答を含めて再依頼する |
| EAL-005 | 採用（`adopted`） | ユーザー回答（`interview`） | Human approval checkpoint / automation boundary | Issue node 作成前の分解案承認を human approval checkpoint とする。Issue draft pack は人間が分解案確認済みの前提で扱い、Issue start 後の canonical docs 正本化は自動化する。Epic requirement 作成には ChatGPT-generated path と human/Codex-authored path の両方を許容する。 | `artifacts/20260707t144547z-interview-human-approval-checkpoint-for-batch-planning-workflow.md` | requirement / design / plan 具体化時に approval gate と automation boundary として採用する |
| EAL-006 | 部分採用（`partially_adopted`） | 調査（`research`） | ChatGPT authoring workflow best practices / Epic design and plan seed | ユーザー回答を含めた ChatGPT 最終分析として、二車線設計、Issue Decomposition Approval Gate、`spec-dock-chatgpt-authoring` skill、Issue Planning mode、ZIP handling、runtime command boundary を採用候補にする。一方で、正式な requirement / design / plan への反映、schema 決定、runtime command 採用範囲、reviewer gate は未実施のため authority は evidence-only のままにする。 | `artifacts/20260707t150325z-research-chatgpt-workflow-best-practices-final-analysis.md` | Epic design / plan 具体化時に採用範囲を明示し、必要に応じて追加 interview または reviewer gate を通す |
| EAL-007 | 部分採用（`partially_adopted`） | 調査（`research`） | skill taxonomy / authoring command taxonomy / GitHub sync preflight | 複数 skill 案に対する ChatGPT 追加分析として、scope 別 planning skill を入口に残し、共通 evidence lane として `spec-dock-chatgpt-authoring` を追加する hybrid taxonomy を採用候補にする。`spec-dock-issue-planning` は初期では split せず `zero-base` / `requirement-first` / `draft-adoption` modes とし、`authoring preflight github-sync` は dirty / untracked / unpushed / branch missing / connector failure を block する方針を採用候補にする。正式な design / plan への反映と reviewer gate は未実施。 | `artifacts/20260707t152834z-research-chatgpt-multi-skill-authoring-workflow-analysis.md` | Epic design / plan で skill boundary、command list、preflight block 条件、deferred command を具体化する |
| EAL-008 | 部分採用（`partially_adopted`） | 調査（`research`） | Epic requirement / design / plan concretization | ChatGPT の具体化案から、installed runtime / installed skill への昇格、既存 planning skill 名維持、`spec-dock-chatgpt-authoring` 追加、`authoring` command group、GitHub sync preflight、ZIP contract、deferred command、Issue sequence を正本 `requirement.md` / `design.md` / `plan.md` へ採用した。一方で、ChatGPT の exact wording、current branch が GitHub connector で見えないことに基づく推測、Issue ID などは authority として採用していない。 | `artifacts/20260707t155254z-research-chatgpt-requirement-design-plan-concretization.md` | spec-reviewer を通し、必要なら reviewer finding を正本 docs に反映する |
| EAL-009 | 採用（`adopted`） | ユーザー回答（`interview`） | local-context evidence mode / relay PR delivery policy | `-f` / `--force` のような安易な bypass ではなく、同期できない場合は明示的な `local-context` evidence mode として ChatGPT authoring を許容する。Epic に属する複数 Issue は中間 Issue ごとに PR を作らず、Issue を一つずつリレーして finish し、最後の final quality gate / PR delivery Issue で Epic 単位の品質ゲート、修正、mergeable PR 作成を行う。 | `artifacts/20260707t161305z-interview-offline-authoring-mode-and-relay-pr-delivery-policy.md` | requirement / design / plan に採用済み。Issue node 作成は Issue Decomposition Approval Gate 後に行う |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ... | ... | なし / 低 / 中 / 高（none / low / medium / high） | 合格 / 不合格 / blocked（pass / fail / blocked） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| 要件 / 設計 / 計画（requirement / design / plan） | 文書 / コード / artifacts / legacy discussions / 外部証跡（docs / code / artifacts / legacy discussions / external evidence） | なし / `artifacts/...` / legacy `discussions/...`（none / `artifacts/...` / legacy `discussions/...`） | 採用 / 部分採用 / 棄却 / 延期 / なし（adopted / partially_adopted / rejected / deferred / none） | 合格 / 不合格 / 利用不可 / 拒否 / waiver / provisional（passed / failed / unavailable / denied / waived / provisional） | はい / いいえ（yes / no） | 昇格 / clarification へ戻す / 再レビュー / フォローアップ（promote / return to clarification / re-review / follow-up） |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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
