---
種別: レポート（Epic）
ID: "epic-00324"
タイトル: "Delegation Foundation Asset Inventory and Thin ChatGPT Adapter"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-00322"]
---

# epic-00324 Delegation Foundation Asset Inventory and Thin ChatGPT Adapter — レポート

## 進捗サマリー

- 完了:
  - Humanが承認した7 Epicを `epic-00324`〜`epic-00330`としてmaterializeした。
  - Initiative Planの完全DAGを17件のdirect dependency edgeとして登録した。
  - Epic 1のPlanning Bundle候補をChatGPT Use（GPT-5.6 Pro）で一括生成した。
  - ChatGPT完全出力をbyte-exactなEvidence Artifactとして保存した。
  - ローカル実装と照合し、`requirement.md`、`design.md`、`plan.md`へ採用した。
  - Humanの補足指示により、Epic全体1 PR方式を撤回し、各Issueの専用branch／個別PR／review／Human merge方式へ改訂した。
- 現在地:
  - review target commit `a7051c57810bd24f5898391b733da4d997743e1a`へのfresh ChatGPT spec reviewは`fail`（P0=0、P1=2、P2=4、P3=1）だった。
  - P1/P2 findingsを正本3文書へ反映中。Issue単位PR方式そのものはreviewでacceptableと判定された。
- 未完:
  - repaired revisionをcommit／pushし、新しいexact HEADへfresh ChatGPT spec reviewを再実行する。
  - Human承認後にのみIssue candidateを実Issueへmaterializeする。
- ブロッカー:
  - E1-REV-001（Human Relay request再現性）とE1-REV-002（E1-I05／E1-I04の独立完了条件と依存）が再レビューpassまでblocking。

## Materialization証跡

- Parent Initiative: `init-00322` / GitHub Issue `#322`
- Epic nodes:
  - `epic-00324` / GitHub `#324`
  - `epic-00325` / GitHub `#325`
  - `epic-00326` / GitHub `#326`
  - `epic-00327` / GitHub `#327`
  - `epic-00328` / GitHub `#328`
  - `epic-00329` / GitHub `#329`
  - `epic-00330` / GitHub `#330`
- Direct dependency edges: 17件
- Validation: `nodes=219`
- Materialization commit: `abbd652c7d1e05fc269fff08be238e58cc6eef0a`
- Remote verification: local HEADとorigin branch HEADの一致を確認した。
- Boundary:
  - Epic 2〜7の正本文書はempty scaffoldを維持する。
  - Epic 1のIssue candidateは計画上のcandidate keyであり、実Issue IDではない。

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | blocking | next_action |
|---|---|---|---|---|---|---|---|
| EAL-001 | `partially_adopted` | ChatGPT Use session `init00322-epic1-planning` / GPT-5.6 Pro | `requirement.md`、`design.md`、`plan.md` | GitHub-synced revisionを参照したcomplete batchを初期候補として採用した。正本では不正なfrontmatter終端を正規化し、その後EAL-003のHuman指示でDelivery Topologyを改訂した。 | `artifacts/20260720t010710z-chatgpt-output-chatgpt-epic1-integrated-planning-bundle-candidate.md`; source revision `abbd652c7d1e05fc269fff08be238e58cc6eef0a`; SHA-256 `94ee25f8ec15c0d25d3d11c6690ff985ec17fd13f1f312fb2725c95cc693614c`; 141447 bytes | yes | 改訂後review targetをpushし、fresh ChatGPT spec reviewを実施する |
| EAL-002 | `adopted` | repository facts / Main verification | ChatGPT候補のbackend設定記述 | `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、互換`ORACLE_CHATGPT_COMMAND`の解決順をprovider codeとshipped docsで確認した。 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py`; `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md` | no | fresh reviewで整合性を再確認する |
| EAL-003 | `adopted` | Human補足指示 | Epic 1の`requirement.md`、`design.md`、`plan.md` | 既存候補がper-Issue PRを作らずE1-QAで一つのEpic PRへ集約する設計だったため、Issueごとのbranch／PR／review／Human mergeへ明示的に変更した。依存Issueは先行PRのmain merge後に更新済みmainから開始する。 | 本conversationの2026-07-20 Human指示、E-RQ-012、E-AC-013、design §20.4、plan §7.1／§22 | yes | 改訂revisionをfresh ChatGPT spec reviewへ回す |
| EAL-004 | `adopted` | ChatGPT Use session `init00322-epic1-spec-review` / GPT-5.6 Pro fresh review | review target `a7051c57810bd24f5898391b733da4d997743e1a` | exact GitHub revisionをverified後、requirement pass、design fail、plan fail、overall failと判定した。Issue単位PR topologyはacceptable。P1 2件と関連P2 4件をrepair対象として採用する。 | `artifacts/20260720t014540z-chatgpt-output-chatgpt-epic1-fresh-spec-review-a7051c57.md`; SHA-256 `f3aa510c42799e37407bca3ed29320473732a3b445a7780e587e48801e7b2184`; 27042 bytes; requested/resolved model verified | yes | findingsを修復し、新exact HEADでfresh re-review |
| EAL-005 | `partially_adopted` | E1-REV-001〜006 repair | `requirement.md`、`design.md`、`plan.md` | RelayPackageへ再現可能requestとlogical refsを追加し、E1-I03／E1-I05の並列後にI04が両者へ依存する形へ修正。external file、QA ownership、checkpoint merge gate、Executor図も明確化した。 | design §13／§20.4、plan §4〜§8／closure matrices、requirement §9.4 | yes | validate、commit／push、fresh re-review |

### Preservation receipt

- evidence mode: `github-synced`
- source / Workbench / imported Artifact SHA-256: `94ee25f8ec15c0d25d3d11c6690ff985ec17fd13f1f312fb2725c95cc693614c`
- source / Workbench / imported Artifact size: `141447` bytes
- byte comparison: pass
- artifact import:
  - `committed=true`
  - `import_kind=chatgpt-output`
  - `storage_identity=blank`
  - `warning_codes=[]`
- complete output preservation: pass
- diff-check exception: byte-exact Artifactの2517行目にsource由来の行末空白1件を保持する。canonical 3文書とreportには行末空白なし。
- canonical adoption: partial until fresh review passes

### Fresh review preservation receipt

- source / Workbench / imported Artifact SHA-256: `f3aa510c42799e37407bca3ed29320473732a3b445a7780e587e48801e7b2184`
- source / Workbench / imported Artifact size: `27042` bytes
- byte comparison: pass
- artifact: `artifacts/20260720t014540z-chatgpt-output-chatgpt-epic1-fresh-spec-review-a7051c57.md`
- import receipt: `committed=true`、`import_kind=chatgpt-output`、`storage_identity=blank`、`warning_codes=[]`
- diff-check exception: byte-exact review Artifactの216行目にsource由来のMarkdown hard-break用行末空白2文字を保持する。canonical 3文書とreportには行末空白なし。

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| OAL-001 | 後続Epicが共用するDelegation Foundation、asset inventory、thin adapterへEpic 1を限定した。 | GitHub exact HEAD、no-hidden-Git、Human Relay、metrics baseline、provider／dogfood parityを受入条件化した。 | low | pending |
| OAL-002 | Epic 2〜7をJIT具体化のまま保持した。 | Epic 1計画には6 implementation candidateと1 final quality candidateだけを提案した。 | none | pending |
| OAL-003 | Issue責務とreview／rollback単位を一致させるため、各Issueを独立PRとしてdeliveryする。 | dependency merge後のmainからbranch作成、parallel branchのbase更新、E1-QA固有PRを定義した。 | low | pending |
| OAL-004 | E1-I03とE1-I05の安全な並列性を維持する。 | I05をmeasurement protocol／fixtureへ限定し、I04をI03＋I05 merge後に開始してactual backend evidenceを供給する。 | low | pending fresh re-review |

## 仕様authoringゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Initiative正本、承認済み7 Epic DAG、ADR、current provider／installed／dogfood構造、GitHub exact revision | open questionなし | ChatGPT complete batchから部分採用 | `pass` at `a7051c57` | no | repaired bundleとの整合をfresh re-review |
| design | requirement、layered runtime、authoring backend contract、Git ownership boundary、PlantUML | E1-REV-001 Relay request再現性をrepair | ChatGPT complete batch＋review findingsを部分採用 | `fail` at `a7051c57` | yes | repaired revisionをfresh re-review |
| plan | requirement／design、Issue slicing規則、final quality Issue、dependency／parallel lane、Human指定のper-Issue PR方式 | E1-REV-002 I05/I04 responsibilityをrepair。実Issue materializationはHumanの別承認待ち | ChatGPT complete batch＋Human指示＋review findingsを部分採用 | `fail` at `a7051c57` | yes | repaired revisionをfresh re-review |

## 委任ドラフト証跡（Delegated Draft Evidence）

- 使用: external ChatGPT authoring evidence laneを使用した。
- authorization source: HumanがEpic 1の一括具体化とspec reviewにChatGPT Useを代替利用するよう明示した。
- lifecycle: `produced` → `integrated` → fresh review failed → repair integrated → fresh re-review pending
- canonical authority: ChatGPT出力単独では成立しない。
- local sub-agentによるscope-local direct-write draft: not used
- raw evidence path: `artifacts/20260720t010710z-chatgpt-output-chatgpt-epic1-integrated-planning-bundle-candidate.md`
- intended targets: `requirement.md`、`design.md`、`plan.md`
- reflected_to: 正本3文書（frontmatter終端正規化と、Human指示によるIssue単位Delivery Topology改訂を実施）
- reviewer result: `fail` at `a7051c57`（P0=0、P1=2、P2=4、P3=1）
- promotion decision: blocked until repaired exact revision passes fresh re-review

## 決定事項

- Initiative ADR-01: ChatGPT、Main、Runtimeの責務分離を継承する。
- Initiative ADR-03: thin adapterとGitHub exact HEAD bindingを継承する。
- Initiative ADR-06: Git transactionはMainが所有し、adapter／executorは実行しない。
- Initiative ADR-08: Workbenchを一時証跡、Artifactと`report.md`を永続証跡とする。
- Epic 1では旧surface削除、global cutover、semantic Prompt完成、automatic canonical adoptionを行わない。
- Epic 2〜7はmaterialize済みだが、JIT Planningまで正本文書を具体化しない。

## Issue candidate状況

- `E1-I01`〜`E1-I06`: implementation Issue candidate。未materialize。
- `E1-QA`: 全implementation candidateに依存するfinal quality Issue candidate。未materialize。
- Human approval前にGitHub Issue、SpecDock Issue Node、Issue dependencyを作成しない。

## 受け入れ条件の達成状況

- E-AC-001〜E-AC-013: 実装前のため未達。
- Planning gate: fresh ChatGPT spec review待ち。
- Epic execution readiness: 未成立。
- Epic completion: 未成立。

## フォローアップ

- fresh ChatGPT spec reviewのblocking findingを正本へ反映し、必要なら新revisionで再レビューする。
- review pass後、HumanへIssue candidate構成の承認を求める。
- Epic 2〜7は各実施時点にJIT Planningする。

## 省略／例外メモ

- 「Epic仕様書」はSpecDock上の`requirement.md`、`design.md`、`plan.md`のPlanning Bundleとして管理する。独立した第4文書は作成しない。
