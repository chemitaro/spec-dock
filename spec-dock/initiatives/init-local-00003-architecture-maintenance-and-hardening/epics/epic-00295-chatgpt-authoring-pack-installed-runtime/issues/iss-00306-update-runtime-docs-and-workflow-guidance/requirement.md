---
種別: 要件定義書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
関連GitHub: ["#306"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00306 Runtime Workflow Guidance — Issue 要件定義

## 1. 目的

このIssueは、ChatGPT authoring pack installed runtime の user-facing docs と workflow guidance を、現在実装済みの runtime command / installed skill / evidence contract と一致させる。

SpecDock 利用者と agent が、ChatGPT / Oracle 出力を「正本ではなく evidence」として扱い、`github-synced` と `local-context` の authority 差分、ZIP/tree output の安全な取り扱い、候補 validator、human approval gate、Issue draft adoption、relay-style PR delivery policy を誤読しない状態を作る。

## 2. 背景

`epic-00295` では、ChatGPT に大きな planning work を委任し、ZIP/tree 形式の複数 artifact を evidence として受け取り、SpecDock の Initiative / Epic / Issue planning に取り込む installed runtime と skill surface を追加している。

前段Issueで runtime command group、GitHub sync preflight、prompt pack、backend invocation、ZIP review/stage、candidate validators、Issue draft adoption validator、`spec-dock-chatgpt-authoring` skill、approval check は実装済みである。一方で、docs / workflow guidance は runtime / skill の現行 surface を体系的に説明しておらず、以下の誤運用リスクが残っている。

- ChatGPT output、ZIP/tree/staged evidence、validation `pass` が canonical adoption、reviewer pass、execution-ready、PR-ready と誤解される。
- `local-context` mode が `github-synced` と同等の authority を持つように読める。
- 未実装または意図的に deferred の command が supported workflow として案内される。
- provider-side source of truth と dogfooding mirror の更新境界が曖昧になる。
- 中間IssueでPRを作成せず、最終Issue `iss-00307` でEpic単位の品質ゲートとmergeable PR deliveryを行う relay policy が docs から読み取りにくい。

## 3. スコープ

このIssueで行うこと:

- provider-side docs under `src/spec_dock/assets/spec_dock/docs/` を追加・更新する。
- dogfooding mirror docs under `spec-dock/docs/` を provider docs と対応する内容へ更新する。
- ChatGPT authoring pack workflow guide、backend invocation reference、prompt pack / ZIP / staged evidence reference を追加または更新する。
- `workflow_spec_authoring.md`、`workflow_initiative.md`、`workflow_epic.md`、`workflow_issue.md` に、ChatGPT evidence lane、draft adoption、human approval、relay PR delivery policy への薄い導線を追加する。
- supported `authoring` commands と deferred / unsupported commands を区別して説明する。
- `github-synced` default と explicit `local-context` evidence mode の authority 差分を説明する。
- ZIP/tree/candidate/stage/validation outputs は `authority: evidence_only` であり、main orchestrator の Evidence Adoption Ledger と fresh reviewer gate を経るまで正本 authority を持たないことを説明する。
- human approval before node creation と Issue draft adoption after node creation の順序を説明する。
- C11 は中間Issueであり、PR delivery は `iss-00307` / C12 へ defer することを明記する。

## 4. 非スコープ

このIssueで行わないこと:

- 新しい runtime behavior の追加。
- automatic Issue creation の実装。
- ChatGPT output から canonical docs への自動 mutation。
- `.assurance.json` mutation。
- reviewer pass、execution-ready、PR-ready、merge-ready の自動設定。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` の実装または usage example 化。
- 中間IssueでのPR作成またはPR delivery。
- raw transcript、secret、credential、host-local absolute path を durable docs に保存する運用の追加。

## 5. Actor / Trigger

| Actor | 役割 | このIssueとの関係 |
|---|---|---|
| SpecDock operator | installed runtime と planning skills の利用者 | docs から supported command と authority boundary を理解する |
| main orchestrator | canonical docs の single-writer | ChatGPT evidence を採否判断し、正本へ再記述する |
| `spec-dock-chatgpt-authoring` skill | ChatGPT / Oracle evidence lane | evidence 生成を支援するが、canonical docs / reviewer gate / readiness / PR delivery は所有しない |
| Initiative / Epic / Issue planning skills | scope別 planning authority | ChatGPT evidence の採用先とfresh reviewer gateを所有する |
| spec-reviewer | 仕様レビュー | docs / workflow guidance がEpic要件とruntime surfaceに一致するか確認する |

主なtrigger:

- `./spec-dock/scripts/spec-dock authoring` command group の利用前にdocsを参照する。
- Initiative / Epic / Issue planning で ChatGPT-generated ZIP/tree/candidate/draft evidence を採用する。
- GitHub syncが使える場合と、明示的に `local-context` で進める場合を切り分ける。
- Epic relay execution で中間Issueをfinishし、最終IssueでPR deliveryする。

## 6. 受け入れ条件

- AC-001: provider-side docs と dogfooding mirror docs が、ChatGPT authoring pack workflow、backend invocation、prompt pack / ZIP / staged evidence を説明している。
- AC-002: docs に記載された supported `authoring` commands が runtime help / parser と一致している。
- AC-003: deferred / unsupported commands は supported usage example として案内されず、使用不可または初期スコープ外として明記されている。
- AC-004: `github-synced` は default repo-aware evidence mode、`local-context` は explicit lower-authority evidence mode として説明されている。
- AC-005: ChatGPT output、ZIP/tree/staged evidence、candidate validation、draft adoption validation、approval check の `pass` は command-local validation pass であり、canonical adoption、reviewer pass、execution-ready、PR-ready ではないと説明されている。
- AC-006: human approval before Epic/Issue node creation と Issue draft adoption after node creation の順序が説明されている。
- AC-007: C11 は中間IssueとしてPR deliveryを行わず、final quality gate / mergeable PR delivery は `iss-00307` へ defer すると説明されている。
- AC-008: provider-side source of truth と dogfooding mirror の境界がdocs / reportに記録されている。
- AC-009: `git diff --check`、`./spec-dock/scripts/spec-dock validate`、authoring help smoke、deferred command wording check、forbidden authority claim check が実行され、結果が `report.md` に残っている。

## 7. リスク事実 / Issue grade

Issue grade は `standard` とする。

このIssueは主にdocs / workflow guidance変更だが、installed runtime command surface、installed skill taxonomy、authority boundary、relay PR delivery policy を説明するため、誤記は実行時の誤運用につながる。特に canonical adoption、reviewer pass、execution-ready、PR-ready の authority leakage は重大なレビュー対象である。

リスク事実:

- docs_only_change: mostly true
- runtime_behavior_change: false unless help text wording only is corrected
- public_contract_change: docs/reference contract change
- security_or_privacy_sensitive: indirect; raw transcript / secret / host-local path persistence を避ける必要がある
- rollback_difficulty_high: false
- migration_or_persistence_change: false

## 8. 証跡期待

`report.md` に以下を残す。

- ChatGPT draft artifacts と ChatGPT Use analysis の採否判断。
- provider docs changed inventory。
- dogfooding mirror docs changed inventory。
- supported command source（runtime help / parser / Epic design）。
- deferred command wording check。
- forbidden authority claim inspection。
- `github-synced` / `local-context` wording inspection。
- verification command output summary。
- fresh `spec-reviewer` verdict。
- no-per-Issue-PR rationale と `iss-00307` へのPR delivery defer evidence。
