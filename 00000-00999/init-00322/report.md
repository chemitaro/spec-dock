---
種別: レポート（Initiative）
ID: "init-00322"
タイトル: "GPT 56 ChatGPT First Intelligence Architecture"
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-19"
依存: ["requirement.md", "design.md", "plan.md"]
---

# init-00322 GPT 56 ChatGPT First Intelligence Architecture — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Initiative の進捗、採用判断、reviewer state、blocking / next action、follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - GPT-5.6 Proとの議論から作成されたInitiative Planning Packの保存・安全検査・採用判断を完了した。
  - 29件のInitiative-scope artifactは`artifacts/`直下へ配置し、SpecDock validationを通過した。
  - 元Packの`requirement.md`を完全コピーした後のfresh reviewでP1を検出し、GPT-5.6 Proが三文書をcomplete bundleとして改訂した。
  - 改訂版`requirement.md`は回収済みファイルから完全コピーし、source／destination SHA-256一致を確認した。本文にP0/P1はなく、report evidence不足だけがP1として残ったため台帳を更新した。
  - 初回改訂版`design.md`のfresh review findingsは、同じGPT-5.6 Pro会話でcomplete-file revisionへ反映した。
  - 最終design V3とplanを完全コピーし、回収元／配置先SHA-256一致を確認した。Requirement／Design／Planのfresh reviewer gateはすべてPASSした。
  - Humanの明示指示により、`20260719t135413z-init-00322-architecture-aware-execution-brief-complete-replacement.zip`からcanonical三文書を完全置換し、9件のArtifactを追加した。現在の三文書はfresh Planning Review前のcomplete replacement candidateである。
- 次のマイルストーン:
  - fresh Requirement／Design／Plan Reviewを順に通過した後、Humanが更新後の7 Epicの名称・境界・依存を承認する。Epic Node／dependencyのmaterializeはその承認まで行わない。
- ブロッカー:
  - 今回のcomplete replacement candidateはfresh Requirement／Design／Plan Review未実行のため、review-passed、execution-ready、PR-ready、merge-ready、completedを主張できない。

## ChatGPT Planning Pack受入証跡

- output form: ZIP / tree
- evidence mode: `local-context`
- pack: `20260716t235120z-init-00322-chatgpt56-delegation-vnext-planning-pack-enriched.zip`
- pack SHA-256: `44ab64fdcf44e00af07bc8c6fa3ce11a31b2590ce23371afb59cff1920cfb078`
- 会話エクスポート SHA-256: `65b7f0aa274476198d613295ddbc48a87ff67f62e8b9e52bf8e4c2d05272099a`
- source snapshot: `chemitaro/spec-dock` commit `3ee6d9047506a40b938407ecfffbb341a3ca76af`
- target: `init-00322` / GitHub Issue `#322`
- built-in review: `rejected` (`wrong_root`と現行schemaのmetadata不足。内容の危険性判定ではない)
- manual quarantine review:
  - 35エントリはすべて通常ファイル。path traversal、absolute path、symlinkなし。
  - `CHECKSUMS.sha256`の33対象は全件一致。`MANIFEST.json`の対象repository、commit、Initiative ID、file countを確認。
  - artifactは29件。`20260716t131924z` slot重複を避けるためrepository baseline researchだけをruntimeのcollision grammarに従い`20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md`へ正規化し、artifact内参照を同期した。
- preservation status: `pass-with-warning`
- warning: 原本ZIP自体は現行SpecDock authoring-pack schemaと非互換。リポジトリには検査済みMarkdown artifactと正本候補のみを配置する。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やInitiative判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） | GPT-5.6 Proとの議論および拡張版Planning Pack（`external-chatgpt-evidence`） | `requirement.md`、`design.md`、`plan.md`、`artifacts/` | Humanが既存`init-00322`の正本3文書をcomplete fileで差し替え、同梱artifactをInitiative配下へ配置するよう明示した。Codexは正本3文書の意味内容を再執筆しない。 | pack SHA-256、`CHECKSUMS.sha256`全件一致、`MANIFEST.json`、`artifacts/20260716t235120z-15-disc-enriched-artifact-set-internal-self-review.md` | 原本コピー後のSHA-256照合とfresh reviewer gate |
| EAL-002 | 採用（`adopted`） | GPT-5.6 Pro complete-bundle revisionおよびdesign V3（`external-chatgpt-authoring`） | `requirement.md`、`design.md`、`plan.md` | 元Pack requirementと改訂designのfresh review findingsをpartial patchではなくcomplete fileへ反映した。Humanの完全ファイル差し替え指示をadoption sourceとし、Mainは回収済み各ファイルを意味変更せず`cp`する。 | ChatGPT conversation `6a54785a-93e8-83ee-97d2-d502c17f2567`、Oracle sessions `init-00322-complete-planning-bundle`／`init-00322-design-v2-recovery`／`init-00322-design-v3-recovery`、初回model evidence `requested=Pro GPT-5.6 Sol / resolved=GPT-5.6 Sol + Pro / verified=yes`、改訂文書SHA-256: requirement `7f376478a4c7aa0e2cbd36700c7e57e04cd59711e0a96c5bf424bce1a2b6569f`、design V3 `4254abb32fb32f37c7b800e48bf2e40fa48a5c4e78e5914801bfd7f8431afbc9`、plan `3f0bd00fc553888ec71b50b112571c6d7a93da933b556e454b42680ef43414f1` | design V3 fresh review後、planを完全コピー・レビュー |
| EAL-003 | 採用候補（`partially_adopted`） | `20260719t135413z-init-00322-architecture-aware-execution-brief-complete-replacement.zip`（`external-chatgpt-evidence`） | `requirement.md`、`design.md`、`plan.md`、新規9 Artifact | Humanが対象branchへのcomplete-file replacementを明示指示したため、三文書を完全置換し、9 Artifactを同名追加した。Humanの直接承認により、意味を変えない16行の行末空白除去とPlantUML複数行ラベル9件の`\n`化だけを適用した。Artifact front matterの自己申告はcanonical authorityとせず、fresh三段Review完了まではcandidateとして扱う。 | package SHA-256 `53cf0ca4244ef64c9cdf344fac37dba0de6fac42e33311f5d355497ba6af8960`、source branch、baseline Git blob 4件一致、ZIP integrity pass、`CHECKSUMS.sha256`全件一致、`MANIFEST.json`、Internal Self-Review、PlantUML 1.2026.6 render検証 | Requirement、Design、Planの順でfresh Reviewを実行し、P0／P1がなければcurrent revisionの採用を確定する |
| EAL-004 | 置換済み（`superseded`） | `20260719t114039z-init-00322-architecture-aware-execution-brief-planning-update.zip`と対応prompt | 最終canonical文書・Artifactへの採用なし | Humanが新complete replacement packageを唯一のauthoritative inputと指定したため、旧delta型package／promptは使用・merge・copy対象から除外した。 | 新packageの`CODEX-APPLY-PROMPT.md`とHumanの上書き指示 | 再参照しない。fresh ReviewはEAL-003のcomplete replacementだけを対象にする |

### Complete-bundle revisionの転送・保存証跡

- 元Pack requirement SHA-256: `d3ab17f1c95933fd9836cca10f2c191f86d7709a6b234dc9d712e4ea1c7ae90c`。sourceと最初のdestinationで一致した。
- 元Pack requirementのfresh reviewは`fail`。P1はWhy now、MainのGit transaction ownershipとの矛盾、ADR disposition不足。P2/P3はtitle、metric、WHAT/HOW、report placeholderだった。
- GPT-5.6 ProはP0/P1をpartial patchせず、requirement／design／planのcomplete bundleを再生成した。
- ChatGPT sandbox downloadは再発行直後もHTTP 404となった。欠損した一括Base64 ZIP（SHA-256 `c7462e256b4b818127a69da88df49e5e6d1089ad6a75c2d24d4662505ae569cc`）はZIP整合性検査で`missing 9216 bytes`となったため棄却した。
- 同じChatGPT conversationから各文書をdeterministic gzip Base64で再取得し、gzip integrity、UTF-8、期待サイズを検査した。期待サイズはZIP中央ディレクトリに記録されたrequirement `23779` bytes、design `27539` bytes、plan `27527` bytesと一致した。
- 現行`requirement.md`は回収ファイルから`cp`し、source／destination SHA-256 `7f376478a4c7aa0e2cbd36700c7e57e04cd59711e0a96c5bf424bce1a2b6569f`の一致を確認した。
- design V2は同じChatGPT conversationでP1 3件をcomplete fileへ反映した。停止した思考ターンを同一conversationのfollow-upで回収し、gzip integrity、UTF-8、`29551` bytesを確認後に`cp`した。source／destination SHA-256 `44cb7e5001f2a9ceb8c90f45ec26b958807549d9b863aff4a17e2cbd874acba4`は一致した。
- design V3はV2 fresh reviewのlifecycle P1 1件だけをcomplete fileへ反映した。V2原本を同一conversationへ添付して回収し、gzip integrity、UTF-8、`30498` bytesを確認後に`cp`した。source／destination SHA-256 `4254abb32fb32f37c7b800e48bf2e40fa48a5c4e78e5914801bfd7f8431afbc9`は一致した。
- transfer recovery sessions: `required-repository-connector-context-github-32`、`-33`、`-35`、`-36`。転送の失敗・再試行は内容変更のadoption sourceにしていない。

### ADR採用判断

ZIP内frontmatterの`authority: accepted`はsource claimであり、それ自体をSpecDock上の権限根拠としない。以下は、HumanがGPT-5.6 Proとの議論からADRを抽出して本Initiativeで使うよう指示し、本ターンで配置を明示したことをadoption sourceとする。

| ID | adoption_status | source claim | local disposition | evidence path |
|---|---|---|---|---|
| ADR-01 | `adopted` | ChatGPT・Codex・SpecDock Runtimeの責務分離 | Initiative全体のactor / authority境界として採用 | `artifacts/20260716t123423z-01-adr-delegation-first-responsibility-boundary.md` |
| ADR-02 | `adopted` | 統合Planning Bundleと`plan.md` SSOT | complete-file planningと正本配置契約として採用 | `artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md` |
| ADR-03 | `adopted` | 薄い`spec-dock-chatgpt`とGitHub exact HEAD binding | Oracle / GitHub外部境界として採用 | `artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md` |
| ADR-04 | `adopted` | 契約駆動Review Protocol | Planning / Checkpoint / Delivery / Targeted Reviewの長期方針として採用 | `artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md` |
| ADR-05 | `adopted` | frozen Repair Batch | blocking repairの従属契約として採用 | `artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md` |
| ADR-06 | `adopted` | Main / Executor / Git transaction所有境界 | Executorはcommit / pushせず、Mainが明示的transitionでGit transactionを所有する方針として採用 | `artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md` |
| ADR-07 | `adopted` | Plan-driven Delivery Topology / Human Merge Gate | Issue / Epic / PR deliveryとfinish semanticsの上位方針として採用 | `artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md` |
| ADR-08 | `adopted` | 最小永続状態とWorkbench / `report.md`境界 | 新しいWorkflow databaseを追加しない方針として採用 | `artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md` |
| ADR-09 | `adopted` | 文書migrationなしの全Scope cutover | 既存Scope文書を一括変換せずWorkflow / Actorを切り替える方針として採用 | `artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md` |
| ADR-10 | `partially_adopted` | Architecture-Aware Execution Briefをfrozen subordinate contractとして扱う | Humanの明示指示に基づくcomplete replacement candidateとして採用。Artifact front matterの自己申告は採用根拠にせず、fresh三段Review完了後に確定する | `artifacts/20260719t135413z-05-adr-architecture-aware-execution-brief-as-frozen-subordinate-contract.md` |

`adopted`は上記decisionの採用を表し、各ADRに記載された将来の`reflected_to`がすでに実装・文書反映済みであることや、reviewer pass / readiness / completionを意味しない。

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | 高度認知処理をChatGPT、repository mutationとWorkflow制御をCodex、決定的処理をSpecDock Runtimeへ分離する | Human Gate、日本語ファースト、小さいPR、provider/installed/dogfood parity | 低（low） | requirement／design／plan fresh review `pass` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| 要件（requirement） | 会話export、元Pack 35 files／33 checksum、29 artifacts、既存`.meta.json`／Issue #322、GPT-5.5前提からGPT-5.6／ChatGPT Firstへの転換、actor／authority、7 Epic、改訂文書SHA | Human回答: 正本三文書は内容を書き写さずファイル自体をコピーして差し替える。open questionなし | EAL-001で元Pack evidenceを採用。初回review findingをEAL-002のcomplete-bundle revisionへ反映し、現行requirementを完全コピーで採用 | `pass` at `20260717t024212z`。fresh reviewer `/root/review_requirement_after_evidence`、approved／reviewer target SHA `7f376478a4c7aa0e2cbd36700c7e57e04cd59711e0a96c5bf424bce1a2b6569f`、P0/P1なし | いいえ | designへ昇格 |
| 設計（design） | V2 SHA `44cb7e5001f2a9ceb8c90f45ec26b958807549d9b863aff4a17e2cbd874acba4`のlifecycle findingをV3 SHA `4254abb32fb32f37c7b800e48bf2e40fa48a5c4e78e5914801bfd7f8431afbc9`へ反映。size `30498` bytes、gzip／UTF-8検査pass、`cp`後のsource／destination SHA一致 | Handoff Exitはcontrol／evidenceをEpicへ返すだけでfinishせず、Merge ExitだけがHuman mergeとreviewed head確認後にfinishするよう明確化。requirement再open不要 | 初回改訂designとV2を`superseded`とし、design V3を完全コピーで採用 | `pass` at `2026-07-17T13:20:17+0900 JST`。fresh reviewer `/root/review_design_v3_fresh`、target SHA `4254abb32fb32f37c7b800e48bf2e40fa48a5c4e78e5914801bfd7f8431afbc9`、P0/P1なし | いいえ | planへ昇格 |
| 計画（plan） | 改訂版SHA `3f0bd00fc553888ec71b50b112571c6d7a93da933b556e454b42680ef43414f1`、size `27527` bytes、gzip／UTF-8検査pass、`cp`後のsource／destination SHA一致。requirement／design fresh pass済み | open questionなし | complete-fileとして完全コピーで採用 | `pass` at `2026-07-17T13:23:16+0900 JST`。fresh reviewer `/root/review_plan_v1_fresh`、target SHA `3f0bd00fc553888ec71b50b112571c6d7a93da933b556e454b42680ef43414f1`、P0/P1なし。P2/P3: bootstrap textとline-item traceは非ブロッキング | いいえ | Humanの7 Epic承認待ち。Node materializationは本依頼の対象外 |

### Complete replacement fresh review gate（2026-07-19）

| フェーズ | 対象revision | fresh reviewer | verdict | findings | blocking | 次アクション |
|---|---|---|---|---|---|---|
| requirement | commit `b58f74c7a7ec6cef4e8f915cc9a2ab6e5ffcaef2` | `/root/review_requirement_b58f74c7` | `pass` at `2026-07-19T14:44:57Z` | P0=0、P1=0。P2=1: `20260719t135413z-06-disc-full-bundle-traceability.md`のAC-023要約に非blocking不一致。P2だけを理由にbranch変更しない | いいえ | design fresh Reviewへ進む |
| design | commit `1aa6c28e634d10185e564a64f068eacea77bd2b2`（design SHA-256 `93dfbcfd8c14439ea6da439d2fa40413888f5d9739abd468dd9af1a87c95c9d0`） | `/root/review_design_1aa6c28e` | `pass` at `2026-07-19T14:50:45Z` | P0=0、P1=0。P2=2: cutover rollback詳細の§14への昇格候補、requirementと同じTraceability Artifact AC-023要約不一致。P2だけを理由にbranch変更しない | いいえ | requirement再open不要。plan fresh Reviewへ進む |
| plan | pending | pending | pending | pending | はい | design gate evidence確定後に実行 |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used: GPT-5.6 Proによるexternal ChatGPT complete-bundle authoringを使用した。
  - local sub-agentのscope-local direct-write delegated draftは使用していない。ChatGPT出力はMainが安全な一時領域へ回収し、Human指示とEAL disposition後に完全ファイルコピーする。
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
| GPT-5.6 Pro（external ChatGPT authoring） | `init-00322` | Oracle sessions `init-00322-complete-planning-bundle`／`init-00322-design-v2-recovery`／`init-00322-design-v3-recovery`で生成し、安全な一時領域へ回収 | 元Pack三文書、29 artifacts、会話export、SpecDock authoring docs、fresh reviewer findings | `requirement.md`、`design.md`、`plan.md` | `integrated`（requirement）、`integrated`（design V3）、`integrated`（plan） | requirement: `requirement.md`; design: `design.md`; plan: `plan.md` | source／destination SHA一致、gzip integrity、UTF-8、size確認。欠損ZIPは棄却 | complete-fileの内容をMainが意味変更せず順次コピー | `report.md`置換、reviewer pass／readiness自己申告、欠損ZIP、初回改訂design、design V2 | なし | 三phase fresh review PASS。HumanのEpic承認まではNode materializationしない |

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
- `artifacts/20260716t123423z-01-adr-delegation-first-responsibility-boundary.md`: ChatGPT／Main／Executor／Runtimeの責務を分離する。
- `artifacts/20260716t123423z-02-adr-integrated-planning-bundle-and-plan-ssot.md`: complete Planning Bundleとcanonical `plan.md`を採用する。
- `artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md`: 薄いadapterとGitHub exact HEAD bindingを採用する。
- `artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md`: 契約駆動のFormal／Targeted Reviewを採用する。
- `artifacts/20260716t123423z-05-adr-frozen-repair-batch-contract.md`: Source HEAD固定のRepair Batchを採用する。
- `artifacts/20260716t123423z-06-adr-main-executor-git-ownership.md`: Mainだけが明示的Git transactionを所有する。
- `artifacts/20260716t123423z-07-adr-plan-driven-delivery-topology-and-human-merge-gate.md`: Plan-driven DeliveryとHuman Merge Gateを採用する。
- `artifacts/20260716t123423z-08-adr-minimal-persistent-state-and-workbench-boundary.md`: 最小永続状態とWorkbench境界を採用する。
- `artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md`: 文書migrationなしのglobal cutoverを採用する。

## 成功指標の状況 (必須)
- Baseline: 未計測。PlanではEpic 1で旧Workflow直近3件以上を計測する。
- Target: Plan §4.3のHuman intervention、Main handoff payload、旧local cognitive route、parity、Workflow reliability各目標。
- Current/Actual: Planning artifact adoptionのみ完了。実装・dogfood前のため実測値なし。
- 判断: 未判定。Epic 7で最低4週間かつ代表5 Workflowを評価する。

## 変更点/差分（Planとの差分） (任意)
- 予定の変更:
  - なし。Epic Node／dependencyはHuman承認後にmaterializeする計画どおり未作成。
- やらないことにしたもの（理由）:
  - 原本ZIPの現行authoring-pack schema化は行わない。検査済みMarkdownを直接配置し、原本は転送証跡として扱う。

## ロールアウト/運用観測（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値の変化（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## 実装結果の要約（完了後） (任意)
- ...

## 学び (任意)
- よかったこと:
  - ...
- 改善点:
  - ...

## フォローアップ（別Issue化） (必須)
- Epic/Issue links:
  - 未作成。Humanの7 Epic承認後にPlan §6のportfolioをNode化する。

## 省略/例外メモ (必須)
- 該当なし
