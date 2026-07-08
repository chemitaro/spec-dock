---
種別: 要件定義書（Issue）
ID: "iss-00307"
タイトル: "Final Quality Gate PR Delivery"
関連GitHub: ["#307"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00307 Final Quality Gate PR Delivery — Issue 要件定義

## 1. 目的

このIssueは、`epic-00295 ChatGPT Authoring Pack Installed Runtime` の最終delivery Issueとして、C01〜C11で導入・変更されたinstalled runtime、installed skills、docs、workflow guidance、evidence-only authoring contractをEpic単位で検証し、必要な修正を行い、reviewer / CI / PR review repair loopを通してmergeable PR deliveryに必要な証跡を整える。

このIssueは、ChatGPT / Oracle output、runtime validation、ZIP review、candidate validationの `pass` をcanonical adoption、reviewer pass、execution-ready、PR-ready、merge-readyとして扱わない。正本採用、reviewer gate、PR readiness判断はmain orchestratorと該当workflow gateが所有する。

## 2. 背景

Epic 00295では、ChatGPT authoring pack workflowをSpecDockのinstalled runtime surfaceとinstalled skill surfaceへ昇格した。これまでのC01〜C11で、provider-side assets、`authoring` runtime command group、GitHub sync / `local-context` evidence mode、prompt pack、backend invocation、ZIP review / stage、candidate validators、Issue draft adoption validators、approval check、installed skill、docs / workflow guidanceを実装している。

中間Issueでは個別PRを作成せず、final delivery IssueであるこのIssueにEpic-wide final quality gateとmergeable PR deliveryを集約する。したがって、このIssueでは個別機能の追加よりも、Epic全体のclosure、修正、検証、PR delivery evidenceを重視する。

## 3. スコープ

- C01〜C11のcanonical docs、report、finish evidence、deferred PR delivery rationale、dependency closureを確認する。
- Epic 00295の変更範囲全体をclosure indexとして棚卸しする。
- provider-side source of truthとdogfooding / installed mirrorの境界を検証する。
- `src/spec_dock/assets/...` 由来のinstalled runtime / docs / skillsが `spec-dock init` または同等のinstalled asset simulationでconsumer repoへ届くことを確認する。
- `authoring` command groupのhelp、dispatch、status taxonomy、machine-readable output、human-readable diagnosticsを確認する。
- GitHub sync preflight、explicit `local-context` evidence mode、backend command resolution、ZIP/tree review、stage、candidate validators、Issue draft adoption validator、approval checkをpositive / negative fixtureで確認する。
- local wrapper dependency concernを監査し、正式workflow / shipped docs / runtimeが `/Users/...` や特定の `.codex/skills/chatgpt-use/scripts/oracle-chatgpt` を必須依存としてhard-codeしていないことを確認する。
- deferred / unsupported commandsが実装済みbehaviorとして露出しない、またはfail-closedすることを確認する。
- docs / skills / runtime helpのsupported command inventoryとauthority boundaryを一致させる。
- `git diff --check`、`./spec-dock/scripts/spec-dock validate`、関連pytest、manual dogfood scenario、installed asset simulationを実行・記録する。
- branchが`main`からbehindまたはdivergedしている場合、main取り込み後にfull final gateを再実行する。
- reviewer / CI / PR review findingsを修復し、残リスクとdeferred itemsをfinal evidenceに記録する。
- PR URL、CI/check status、reviewer findings、repair result、mergeable readiness evidenceを`report.md`に残す。

## 4. 非スコープ

- C01〜C11でdeferredと定義された新commandの追加実装。
- `authoring adopt`。
- `authoring create-issues-from-zip`。
- `authoring mark-reviewer-pass`。
- `authoring set-authorized-profile`。
- `authoring issue-execution-ready`。
- `authoring pr-ready`。
- ChatGPT outputによるcanonical docs直接更新。
- ChatGPT outputによる`.assurance.json` mutation。
- ChatGPT self-reviewをfresh reviewer passとして扱うこと。
- 中間IssueごとのPR delivery。
- PR mergeそのもの。
- generic external AI provider registry beyond configurable backend command。
- old workspace in-place migration guarantee。

## 5. 受け入れ条件

- AC-001: C01〜C11のIssue report / finish evidence / deferred PR delivery rationale / dependency edgeがclosure indexに記録され、未完了またはblocking gapがある場合はPR deliveryに進まない。
- AC-002: `./spec-dock/scripts/spec-dock validate` がpassする。未通過があればrepair queueに入り、解消後に再実行される。
- AC-003: `git diff --check` がpassする。
- AC-004: branchが`main`からbehind / divergedしている場合、main取り込み後にfull gateを再実行する。
- AC-005: `./spec-dock/scripts/spec-dock authoring --help` と各subcommand helpがsupported commandだけを案内し、deferred commandをimplemented usageとして示さない。
- AC-006: backend commandは `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の順に解決され、未設定時はfail-closedする。
- AC-007: shipped runtime / docs / skillsにuser-specific absolute pathやhard-coded local wrapper pathがない。既存local wrapperは利用者が指定できるbackend exampleに限る。
- AC-008: `local-context` modeは明示指定、`unsynced_reason`、provided contextまたはdiff summaryを要求し、`github_sync: not_verified` とEAL disposition requirementを記録する。
- AC-009: ZIP reviewはsafe extraction前にwrong root、path traversal、absolute / host-local path、hidden / secret-looking path、raw transcript、credential / token / private key、nested archive、executable、symlink、binary、oversized、unsupported suffix、encrypted entry、metadata missing、source hash mismatch、forbidden authority claimを拒否またはstale / failとして分類する。
- AC-010: pack stage / validators / approval checkはcanonical docs、`.assurance.json`、Issue node、authorized profile、reviewer pass、execution-ready、PR-readyを変更または主張しない。
- AC-011: candidate validationはparent trace、scope / non-scope、duplicate / overlap diagnostics、advisory-only profile recommendation、`authorized_profile` 禁止を確認する。
- AC-012: Issue draft adoption validationはIssue node作成後のdraft adoption input integrityのみを検証し、execution-readyを主張しない。
- AC-013: approval checkはmissing approvalをblockし、valid approvalでもnode creation / canonical write / assurance mutationを行わない。
- AC-014: installed asset simulationで `spec-dock-chatgpt-authoring` skill、updated planning skills、runtime docs、authoring runtime filesがconsumer repoに導入される。
- AC-015: docs / skills / runtime help / testsのsupported command inventoryが一致する。
- AC-016: reviewer / CI / PR review指摘はrepair loopに入り、修復・再検証・残リスク記録が完了してからPR readiness evidenceに進む。
- AC-017: final reportはtest summary、manual scenario summary、closure index、Evidence Adoption Ledger、Known residual risks、deferred items、PR URL、CI / reviewer observationを記録する。

## 6. 証跡期待

- finish evidenceはmachine-readableまたはreviewer-readableにする。
- ChatGPT-derived draft / ZIP / staged evidence / validation reportは `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を維持する。
- command-local `pass` とcanonical adoption / reviewer pass / PR readinessを分離して記録する。
- raw transcript、secret、credential、host-local absolute pathはdurable docsに保存しない。
- PR readinessは、PR作成、CI状態、reviewer指摘、repair result、残リスクを観測した証跡として記録する。ChatGPT evidence単独でreadinessを主張しない。

## 7. Grade / assurance

Issue gradeは `final-quality-gate / PR-delivery` とする。runtime assurance profileが既存分類のみを受け付ける場合は `standard` profileを使いつつ、requirement / design / plan / report内でfinal-quality-gate overlayを明示する。

リスク事実:

- docs_only_change: false
- runtime_behavior_change: possible repair-only
- public_contract_change: final verification / PR delivery contract
- security_or_privacy_sensitive: true, because backend command and secret/path redaction must be audited
- migration_or_persistence_change: false unless repair finds otherwise
- rollback_difficulty_high: medium, because final PR delivery aggregates the Epic
