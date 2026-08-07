---
種別: レポート（Epic）
ID: "epic-00356"
タイトル: "SpecDock Core Simplification and External Intelligence Boundary"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-08-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00356 SpecDock Core Simplification and External Intelligence Boundary — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `epic-00356` と GitHub Issue `#356` を作成した。
  - 2026-08-07 の `main` HEAD `ecdac90d157ac3bc3680bca833d7bdf88e46de45` を baseline とする ZIP から、`requirement.md`、`design.md`、`plan.md` を whole-file copy した。
  - ZIP の materialization guide と提供された ChatGPT 4.6 Pro ディスカッションを Epic-local `disc` Artifact として whole-file copy した。
  - 5ファイルは原本との `cmp` 一致と SHA-256 一致を確認済み。
  - requirement の fresh `spec-reviewer` は `fail`。exact-copy 制約により canonical 文書を変更せず、design / plan review は stop condition に従って未実施。
  - ユーザーの明示指示により、計画の4 Issueを具体化前の scaffold として作成し、5本の direct dependency edgeを登録した。
- 次のマイルストーン:
  - 各Issueの具体化前に、ユーザーが exact-copy の維持か、identity / lifecycle / cross-Initiative authority / optional external smoke 条件を反映した revised complete-file package の採用かを判断する。
- ブロッカー:
  - requirement reviewer finding: `<EPIC_ID>` / `<GITHUB_ISSUE_NUMBER_OR_URL>` と `.meta.json` / GitHub `#356` の identity 不一致。
  - requirement reviewer finding: retained `issue start` / `issue finish` / readiness projection の replacement semantics が未定義。
  - requirement reviewer finding: `init-00322` supersession の authority、対象 node、disposition が未確定。
  - requirement reviewer finding: optional external capabilities と E-AC-008 manual smoke の gating 条件が不整合。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | user-provided ZIP/tree evidence | `requirement.md`, `design.md`, `plan.md` | 添付 ZIP は current `main` HEAD と一致する baseline で作成され、親 Initiative、Epic 境界、4 Issue の分割、migration、検証方針を一体で提示している。ユーザーの whole-file copy 指示に従い、内容を再記述せず canonical 3文書へ採用した。 | ZIP SHA-256 `7be705a0c604c70934bdd26a2653b0830061f2172c8643a8a9d5a4a23bffdc10`; destination SHA-256: requirement `3b254c93a210bd56b693ab26f7136bef8cf637bf28cf5aee5d597f305c7fd37e`, design `af5826c02c641ec111853fb2721c064285a4a26e909d5bbce8ec810729f34d43`, plan `1fc709295627fbfc1fef31f158587d896dd68bdb518c2bc95b8104e3f5b2331a` | fresh `spec-reviewer` gate |
| EAL-002 | `adopted` | user-provided discussion and ZIP guide | `artifacts/20260807t114012z-disc-epic-materialization-guide.md`, `artifacts/20260807t114013z-disc-chatgpt-46-pro-core-simplification-discussion.md` | 親 Initiative 選定、既存 workflow 縮退、Storage Core / Authoring Kit / external intelligence 境界の検討経緯を evidence-only で保持する。 | guide SHA-256 `0aea921617f4e2ce5f62f13c24a73a0c9cc02ff7fd15f89afc4140a5cf6b45b2`; discussion SHA-256 `d09d56dd83fd4b2f4f1a49b67926c07b8e5999a3659596467b05646b7d933988` | canonical authority は3文書と reviewer gateに限定する |
| EAL-003 | `adopted` | user instruction and SpecDock commands | Issue scaffolds and dependency graph | requirement reviewer `fail` を認識したうえで、ユーザーがIssue具体化を行わず構造だけをmaterializeするよう明示承認した。これはplanning promotion、execution-ready、Issue startの承認ではない。 | `new issue` results `iss-00357`〜`iss-00360`; `deps add` 5辺; live `deps check --github --json` | 各Issueは後続のIssue planningまでtemplate状態を維持する |

- EAL-001 detail:
  - source_role: external discussion / ChatGPT-generated ZIP supplied by user
  - claim: proposed Epic requirement / design / plan are the requested materialization source
  - target_section: whole canonical files
  - evidence_strength: baseline SHA matched current `main`; byte-exact copy verified
  - evidence_path: canonical 3文書および Epic-local materialization guide
  - adopter: main orchestrator
  - reviewer: fresh requirement `spec-reviewer` = `fail`
  - blocking: yes; requirement promotion is blocked
- EAL-002 detail:
  - source_role: user-provided external discussion evidence
  - claim: discussion and guide explain the proposed boundary and materialization intent
  - target_section: Epic-local Artifact evidence only
  - evidence_strength: byte-exact copy verified
  - evidence_path: 上記2つの Epic-local Artifact
  - adopter: main orchestrator
  - reviewer: requirement reviewer used both as context
  - blocking: no; preservation itself is complete
- EAL-003 detail:
  - source_role: human operator
  - claim: four planned Issue nodes and their direct dependency edges may be created before Issue specification authoring
  - target_section: Issue node structure and `.meta.json.depends_on`
  - evidence_strength: explicit user instruction plus live CLI receipts
  - evidence_path: `issues/iss-00357-*` through `issues/iss-00360-*` and each `.meta.json`
  - adopter: main orchestrator
  - reviewer: not applicable to structure-only materialization; requirement reviewer failure remains unresolved
  - blocking: no for node/dependency creation; yes for planning promotion and implementation start

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Storage Core と Authoring Kit を SpecDock の製品境界として残し、認知的 workflow を外部 intelligence へ分離する | 既存 node / docs / artifacts / dependency / Workbench data の保持、managed asset の安全な prune | 高: replacement lifecycle semantics と cross-Initiative authority が未定義 | fail（fresh requirement `spec-reviewer`） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | parent Initiative 3文書、sibling Epic 検索、ChatGPT discussion、ZIP baseline / SHA、current lifecycle / init-00322 state | ZIP は「未確定事項なし」だが、identity、replacement lifecycle、cross-Initiative supersession、optional external smoke の4論点を reviewer が未解決と判定 | `adopted` as exact-copy candidate | `failed` | yes | revised complete-file package または exact-copy 例外判断後に fresh re-review |
| design | reviewer-pass 前の requirement、current layered runtime / provider authority、ChatGPT discussion、ZIP design | requirement gate failed | `adopted` as exact-copy candidate | not run | yes | requirement gate pass 後に review |
| plan | reviewer-pass 前の requirement / design、Epic plan playbook、ZIP plan | requirement gate failed。4 Issue は未作成 | `adopted` as exact-copy candidate | not run | yes | requirement / design gate pass 後に review |

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
- なし。長期 architecture decision の ADR 化は fresh review 後に判断する。

## 完了した Issue / PR / Release (必須)
- 完了Issueはなし。次のscaffoldのみ作成済み:
  - `iss-00357 Reduce Runtime to Storage Core`（GitHub `#357`）
  - `iss-00358 Simplify Authoring Kit and Document Contracts`（GitHub `#358`）
  - `iss-00359 Replace Managed Workflow Skills with SpecDock Skills`（GitHub `#359`）
  - `iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces`（GitHub `#360`）

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001〜E-AC-009: 未実装。現時点は Epic planning artifact の配置段階。

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- `iss-00357`〜`iss-00360` の具体化は未実施。各Issue開始時のIssue planningで行う。
- direct dependency:
  - `iss-00359` depends on `iss-00357`, `iss-00358`
  - `iss-00360` depends on `iss-00357`, `iss-00358`, `iss-00359`

## 省略/例外メモ (必須)
- 2026-08-07のユーザー明示指示により、fresh requirement reviewer `fail` のままIssue nodeと依存関係だけを先行materializeした。
- scaffoldの`requirement.md`、`design.md`、`plan.md`、`report.md`は具体化していない。dependency `ready=true` は構造上のdependency-readyだけを意味し、planning完了、execution-ready、Issue start許可ではない。
