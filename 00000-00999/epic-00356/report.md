---
種別: レポート（Epic）
ID: "epic-00356"
タイトル: "SpecDock Core Simplification and External Intelligence Boundary"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-08-13"
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
  - ChatGPT-use-strict で GitHub `chemitaro/spec-dock` の `main` SHA `2c75e0c02cb65a6e74040a72dc161d342d661091` を照合し、Epic正本候補、5件のIssue候補、Issue draft、説明資料を生成した。
  - validator-compatible ZIP は pack review と `epic-issue-candidates` validation の両方に合格した。候補5件のうち `iss-00357`〜`iss-00360` は既存node、`proposed-final-quality-integration-delivery` は人間承認前の新規候補である。
  - Epic Requirement、Design、Planはmain orchestratorがEAL-004から正本へ統合し、各phaseのfresh `spec-reviewer`で`pass`した。
  - Issue 357〜360へStrict draft requirement / design / planを各3件、合計12件、byte-exact copyした。
  - 初版HTMLへのユーザー指摘を受け、ChatGPT / Oracleを使用せず、現行正本R/D/Pから新メンバー向け詳細HTMLを再構成した。旧版は履歴証跡として保持し、delivery indexは詳細版を現在の推奨資料として案内する。
  - 2026-08-10、Product OwnerがEpicの要件定義書・設計書・計画書を採用し、ユーザーレビュー完了と判断した。3文書の状態を`approved`へ更新し、Issue 357 / 358のDraft 1正式化へ進む。
  - Issue 357、358、359はそれぞれPR #362、#361、#363でmainへmergeされ、GitHub Issueもclosedである。current mainは`a6ded0d9a838b40cdcd741fa473cd264b801f245`。
  - 2026-08-13、Epic Plan §6.1に従いIC-1 / IC-2をcurrent mainと各Issue reportへ再照合した。Fresh node / Storage Core / Authoring Kitは`4 + 23 + 3 passed`、二skill contract / finalizer / routeは`11 + 9 + 7 passed`で、Epic-local `disc` Artifactと本Reportに`pass`を記録した。
  - Issue 360はRequirement / Design / Planが各fresh reviewでP0 / P1なしとなり`approved`である。IC-1 / IC-2、direct dependency readiness、planning commit / push、formal `issue start`、active / deps / validateを完了し、ChatGPT-SpecReview-Strict round 2もexact upstream SHA `4b325885b82dbffa26cdd5cd372d3914e8d604ef`でP0 / P1なしの`pass`となった。Planはpromotion commitで`implementation-start-ready`へ昇格し、そのcommit自身のfresh exact-current Strict passを外部delivery evidenceとして要求する。
- 次のマイルストーン:
  - Issue 360 promotion commitのclean exact-current Strict passを外部delivery evidenceとして確認後、Plan S00から実装を開始する。
  - 新規の品質・統合・deliverable handoff Issue候補は、別途人間がnode作成を承認した場合だけ357〜360すべてへの直接依存を持つnodeとしてmaterializeする。
- ブロッカー:
  - Requirement phaseのブロッカーは解消済み。2026-08-07の旧findingは2026-08-09の正本revisionで解決し、fresh `spec-reviewer`が`pass`と判定した。
  - 新規の品質・統合・deliverable handoff Issue候補は、人間によるnode作成承認まで作成しない。

## Product Owner承認

| 対象 | 承認日 | 判断 | 承認範囲 | 残る人間判断 |
|---|---|---|---|---|
| Epic `epic-00356` Requirement / Design / Plan | 2026-08-10 | 採用、ユーザーレビュー完了 | 現行の3正本文書、Issue 357〜360の縦スライス、Issue 357 / 358の並行着手方針 | 品質・統合・deliverable handoff用の新規Issue nodeを作成するかは未承認のまま維持 |

## Integration checkpoint記録

ICはRuntime gateではなく、Epic Plan §6.1に基づく文書上のhandoffである。Issue自身の自己承認ではなく、各ownerのreport / test / merged sourceをEpic main orchestratorが再照合して判定した。

| IC | 判定日 | Verdict | Exact source | Fresh verification | Evidence / transition |
|---|---|---|---|---|---|
| IC-1 Core / Kit | 2026-08-13 | `pass` | PR #361 head `5d1e3a4c…` / merge `3e166d4c…`、PR #362 head `55a7e41d…` / merge `8e10f255…`、current main `a6ded0d9…` | Storage Core `4 passed`、S09 Authoring Kit `23 passed`、Fresh node / Artifact `3 passed` | `artifacts/20260812t174542z-disc-ic-1-core-kit-contract.md`。Fresh node、thin Report、六Artifact、optional blank、Guide、provider / dogfood contractを固定し、IC-1をclosedとする |
| IC-2 Skills | 2026-08-13 | `pass` | PR #363 head `948d0cf0…` / merge `a6ded0d9…` | Static / collision `11 passed`、safe finalizer `9 passed`、four-route / zero-write `7 passed` | `artifacts/20260812t174548z-disc-ic-2-skill-contract.md`。二skill、Guide link、missing capability、旧18 + legacy 3 handoffを固定し、Issue 360への文書上のhandoffを承認する |

Passの範囲は親handoffだけである。Issue 360のformal lifecycle、R/D/P review、実装、IC-3、未承認の最終Issue候補、Epic完了は別途判定する。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は、現行のauthoring phase promotionと文書上のimplementation handoffを止める。Target Runtimeのdependency `ready`、`issue start`、`issue finish`はEALを読まず、EALをlifecycle gateとして扱わない。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | user-provided ZIP/tree evidence | `requirement.md`, `design.md`, `plan.md` | 添付 ZIP は current `main` HEAD と一致する baseline で作成され、親 Initiative、Epic 境界、4 Issue の分割、migration、検証方針を一体で提示している。ユーザーの whole-file copy 指示に従い、内容を再記述せず canonical 3文書へ採用した。 | ZIP SHA-256 `7be705a0c604c70934bdd26a2653b0830061f2172c8643a8a9d5a4a23bffdc10`; destination SHA-256: requirement `3b254c93a210bd56b693ab26f7136bef8cf637bf28cf5aee5d597f305c7fd37e`, design `af5826c02c641ec111853fb2721c064285a4a26e909d5bbce8ec810729f34d43`, plan `1fc709295627fbfc1fef31f158587d896dd68bdb518c2bc95b8104e3f5b2331a` | fresh `spec-reviewer` gate |
| EAL-002 | `adopted` | user-provided discussion and ZIP guide | `artifacts/20260807t114012z-disc-epic-materialization-guide.md`, `artifacts/20260807t114013z-disc-chatgpt-46-pro-core-simplification-discussion.md` | 親 Initiative 選定、既存 workflow 縮退、Storage Core / Authoring Kit / external intelligence 境界の検討経緯を evidence-only で保持する。 | guide SHA-256 `0aea921617f4e2ce5f62f13c24a73a0c9cc02ff7fd15f89afc4140a5cf6b45b2`; discussion SHA-256 `d09d56dd83fd4b2f4f1a49b67926c07b8e5999a3659596467b05646b7d933988` | canonical authority は3文書と reviewer gateに限定する |
| EAL-003 | `adopted` | user instruction and SpecDock commands | Issue scaffolds and dependency graph | requirement reviewer `fail` を認識したうえで、ユーザーがIssue具体化を行わず構造だけをmaterializeするよう明示承認した。これはplanning promotion、execution-ready、Issue startの承認ではない。 | `new issue` results `iss-00357`〜`iss-00360`; `deps add` 5辺; live `deps check --github --json` | 各Issueは後続のIssue planningまでtemplate状態を維持する |
| EAL-004 | `partially_adopted` | ChatGPT-use-strict GitHub-synced authoring pack | Epic `requirement.md`, `design.md`, `plan.md`; Issue 357〜360 draft artifacts; human guide artifacts | Product Ownerが採用したAD-001〜AD-009、vertical slice境界、shared-file ownership、integration checkpoint、品質専用の最終Issue候補を正本化の入力として採用する。候補のauthority自己主張と新規Issue node作成は採用しない。 | ZIP SHA-256 `073bbe7dc9bc7b95ef6ea04f5e85d0219b6e522076799799f3ab8ffcffabf9de`; source manifest `13910ad351ee8e1b2da6277893c0988fee68f2ccc7a849f49c2ba88ac25534ba`; pack tree digest `e5cabfb7c41d2436b753a237b6ce035e5218a012eb9b454243c7a58be35fa223`; pack review `pass`; candidate validation `5/5 pass` | main orchestratorがphaseごとに再記述し、各phaseでfresh `spec-reviewer`を実施する。新規最終Issueは人間承認まで作成しない |
| EAL-005 | `adopted` | ChatGPT-use-strict delivery files | Epic-local HTML / ZIP / delivery index artifacts | 新メンバー向け説明HTML、HTMLを含む完全ZIP、validator合格ZIPを原本のまま保持し、読み方と正本反映状態をMarkdown indexで説明する。 | HTML SHA `44df4267…`; full ZIP SHA `4e506696…`; validated ZIP SHA `073bbe7d…`; 3件ともsourceとの`cmp`一致 | 人間はHTMLを入口とし、実装agentはreviewer-pass済み正本R/D/PとIssue-local draft indexを使用する |
| EAL-006 | `adopted` | user feedback / Codex main-authored canonical rewrite | `artifacts/20260809t135756z-disc-epic-00356-detailed-onboarding-guide.html`; delivery index | 初版は日本語と英語が混在し説明を省略しすぎていたため、現行正本R/D/Pを直接読み直し、背景、用語、構造、Issue別作業、依存、検証、移行、失敗、オンボーディングを日本語主体で再説明する。ChatGPT / Oracleは使用しない。 | SHA-256 `d6cffa5d64ef2914c26cf33b24045d0e67240101bab08f6205f32a9e363137bb`; 832行 / 78,720 bytes; inline SVG 4件; PlantUML原文4件; newcomer reader review `pass`; canonical accuracy review `pass` confidence 0.98; Quick Look render確認; `git diff --check` pass | 詳細版を新メンバー向けの推奨入口とし、初版とZIPは履歴証跡として保持する |

- EAL-001 detail:
  - source_role: external discussion / ChatGPT-generated ZIP supplied by user
  - claim: proposed Epic requirement / design / plan are the requested materialization source
  - target_section: whole canonical files
  - evidence_strength: baseline SHA matched current `main`; byte-exact copy verified
  - evidence_path: canonical 3文書および Epic-local materialization guide
  - adopter: main orchestrator
  - reviewer: 2026-08-07 fresh requirement `spec-reviewer` = `fail`。この判定とexact-copy candidateは、EAL-004に基づく2026-08-09の正本再記述とfresh requirement `pass`によりsupersededされた。
  - blocking: no。旧findingはidentity、lifecycle、親Initiative、external boundaryを現行正本へ固定して解消済み。
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
  - reviewer: structure-only materialization自体にはnot applicable。2026-08-07のrequirement failureは2026-08-09の正本再記述とfresh review `pass`で解消済み。
  - blocking: 既存4 node / dependencyはno。各phaseはそのfresh reviewまでblockし、新規最終Issueだけは人間承認までblockする。
- EAL-004 detail:
  - source_role: ChatGPT-use-strict planning evidence grounded in exact GitHub repository / branch / SHA
  - claim: adopted product decisions can be expressed as end-to-end vertical slices with explicit responsibility boundaries and validation contracts
  - target_section: Epic canonical R/D/P、existing Issue 357〜360 draft artifacts、Epic-local human guide artifacts
  - evidence_strength: exact SHA gate、ZIP integrity、manifest consistency、pack review pass、candidate validation pass
  - evidence_path: `artifacts/20260809t122849z-disc-epic-00356-authoring-pack-validated.zip`、`artifacts/20260809t122849z-disc-epic-00356-strict-planning-delivery-index.md`、Issue 357〜360のscope-local draft artifacts
  - adopter: main orchestrator
  - reviewer: phaseごとのfresh `spec-reviewer`を別途記録する
  - blocking: canonical phase promotionは各fresh reviewまでyes。新規最終Issue作成はhuman approvalまでyes
  - issue_draft_paths: `iss-00357`〜`iss-00360`それぞれの`artifacts/20260809t125145z`〜`20260809t125156z`にdraft requirement / design / planをbyte-exact copy。12件すべて`cmp`一致。
- EAL-005 detail:
  - source_role: ChatGPT-use-strict generated human / machine-readable delivery
  - claim: team onboarding material and the complete multi-file package can be preserved without treating them as canonical authority
  - target_section: Epic-local artifacts only
  - evidence_strength: exact-copy `cmp` and SHA-256 verification
  - evidence_path: `artifacts/20260809t122849z-disc-epic-00356-vertical-slice-planning-guide.html`、`artifacts/20260809t122849z-disc-epic-00356-vertical-slice-planning.zip`、`artifacts/20260809t122849z-disc-epic-00356-authoring-pack-validated.zip`
  - adopter: main orchestrator
  - reviewer: canonical Requirement / Design / Planの各fresh reviewerが`pass`
  - blocking: no。説明資料はevidenceであり、最終Issue作成のhuman gateは別に維持する
- EAL-006 detail:
  - source_role: Codex main orchestratorによる内容設計と正本照合。永続HTMLへのファイル反映はdoc-writerへ限定委任
  - claim: 今日参加したメンバーが詳細HTML単体からEpicの背景、用語、製品境界、4 Issueの縦スライス、並行作業、検証、移行、残る人間判断を具体的に理解できる
  - target_section: Epic-local detailed onboarding HTMLとdelivery index
  - evidence_strength: 現行canonical R/D/Pとの項目別照合、newcomer reader review、fresh accuracy review、構文・link・hash・render検証
  - evidence_path: `artifacts/20260809t135756z-disc-epic-00356-detailed-onboarding-guide.html`、`artifacts/20260809t122849z-disc-epic-00356-strict-planning-delivery-index.md`
  - adopter: main orchestrator
  - reviewer: newcomer usability review `pass`、fresh canonical accuracy review `pass`（findingsなし、confidence 0.98）
  - blocking: no。補助資料であり、正本authority、implementation readiness、最終Issue作成のhuman gateを変更しない

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Storage Core と Authoring Kit を SpecDock の製品境界として残し、認知的 workflow を外部 intelligence へ分離する | 既存 node / docs / artifacts / dependency / Workbench data の保持、managed asset の安全な prune | 中: shared-file ownershipとmechanical inventoryをDesign / Issue planningで固定する必要がある | pass（2026-08-09 fresh requirement `spec-reviewer`）。lifecycle、identity、親Initiative、external boundary、最終Issue人間ゲートを正本へ固定済み |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | parent Initiative 3文書、`.meta.json` / GitHub #356、current lifecycle、AD-001〜AD-009、Strict ZIP SHA / source manifest / pack review / candidate validation | 旧4 findingは現行正本で解消。最終Issueの作成承認だけを後段human gateとして維持 | EAL-004から目的、制約、互換性、vertical slice、E-ACを正本へ再記述 | `pass`（fresh `spec-reviewer`、2026-08-09、confidence 0.98） | no | Design phaseへ昇格。旧requirement failはsuperseded |
| design | reviewer-pass済みrequirement、current layered runtime / provider authority、Strict design candidate、現行`issue-plan.md` | 旧EAL block、Guide path、UML metadata、Final dependency labelを初回review後に修正 | EAL-004からproduct boundary、責務、file contract、migration、failure / verification designを正本へ再記述 | 初回`fail`後に4 findingを修正し、fresh re-review `pass`（2026-08-09、confidence 0.98） | no | Plan phaseへ昇格 |
| plan | reviewer-pass済みrequirement / design、Epic plan playbook、Strict plan candidate、Issue-local draft 12件 | 初回review後、E-RQ / E-AC closure map、IC owner / evidence / transition、Issue draft path index、EALとTarget lifecycleの分離を追加 | EAL-004からtranche、slice demonstration、handoff、test、rollout、rollback、final exitを正本へ再記述 | 初回`fail`後に4 findingを修正し、fresh re-review `pass`（2026-08-09、findingsなし、confidence 0.97）。最終report整合修正も回帰review `pass`（findingsなし、confidence 0.96） | no | Human guide / ZIPをEpic artifactsへ配置し、SpecDock `validate`合格。最終Issue候補の人間判断へ進む |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used。ChatGPT-use-strictのGitHub-synced evidence laneを使用し、非推奨`spec-dock-epic-planning-manual`は使用していない。
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
| ChatGPT-use-strict evidence lane | epic-00356 | Epic-local validated ZIP、delivery index、Issue 357〜360の12 draft artifacts | GitHub `chemitaro/spec-dock` `main` SHA `2c75e0c…`、Epic / Issue正本、採用済み判断 | Epic R/D/P、Issue draft artifacts、human guide artifacts | `partially_adopted` | Epic R/D/Pとreport EAL | pack review / candidate validation `pass` | main orchestratorがphaseごとに正本へ統合。非推奨`spec-dock-epic-planning-manual`は未使用 | authority自己主張、新規Issue node自動作成 | 人間による最終Issue承認 | Requirement / Design / Planすべてfresh review `pass` | 正本昇格済み。最終Issue候補だけ人間判断待ち |

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
- `iss-00357 Reduce Runtime to Storage Core`: PR #362 merged、GitHub #357 closed。
- `iss-00358 Simplify Authoring Kit and Document Contracts`: PR #361 merged、GitHub #358 closed。
- `iss-00359 Replace Managed Workflow Skills with SpecDock Skills`: PR #363 merged、GitHub #359 closed。
- `iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces`: GitHub #360 open。planning / formal start / Strict round 2は完了し、実装は未開始。Implementation-start-ready promotion commitはfresh exact-current Strict passを外部delivery evidenceとして要求する。
- Release publicationは未実施。

## 受け入れ条件（E-AC）の達成状況 (必須)
- Issue 357〜359のslice-local acceptanceは各Issue reportに記録済みで、IC-1 / IC-2は上記Artifactに`pass`を記録した。
- E-AC-001〜E-AC-009のEpic-level closureはIssue 360のdistribution / consumer / preservation / parity結果とIC-3が未完了のため、まだ完了を宣言しない。
- E-AC-010は未実装かつ最終Issue nodeの人間承認待ち。承認された場合は357〜360すべてへの直接依存、full regression、cross-slice integration、defect-only repair、diff audit、handoff evidenceを追跡する。

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- `iss-00360`のR/D/P review、formal `issue start`、distribution実装、IC-3 inputを完了する。
- direct dependency:
  - `iss-00359` depends on `iss-00357`, `iss-00358`
  - `iss-00360` depends on `iss-00357`, `iss-00358`, `iss-00359`

## 省略/例外メモ (必須)
- 2026-08-07のユーザー明示指示により、fresh requirement reviewer `fail` のままIssue nodeと依存関係だけを先行materializeした。この初期状態は後続の正本revisionとreviewでsupersededされた。
- 2026-08-13時点で357〜359は実装・merge・close済み、360はplanning中である。Dependency `ready=true`、IC-1 / IC-2 pass、R/D/P review、formal `issue start`は別の条件として維持する。
