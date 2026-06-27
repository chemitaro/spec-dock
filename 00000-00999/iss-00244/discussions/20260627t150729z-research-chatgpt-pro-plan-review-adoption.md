---
種別: research
ID: "20260627t150729z-research"
タイトル: "ChatGPT Pro Plan Review Adoption"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "iss-00244"
  - "chatgpt-use"
  - "plan-centric-guidance"
authority: "synthesized"
derived_from:
  - "Oracle ChatGPT GPT-5.5 Pro Extended session: iss-00244-plan-centric-guidance"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260627t150729z-research ChatGPT Pro Plan Review Adoption

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- GPT-5.5 Pro Extended に `iss-00244` の要件定義書、設計書、実装計画書、関連 runtime/docs context を共有し、plan-centric issue-execution guidance への hard cutover 設計を外部助言としてレビューさせる。
- 回答は advisory として扱い、ローカル文書・実装事実と照合したうえで採用可否を決める。

## sources / 調査方法 (必須)
- 参照先:
  - Oracle ChatGPT GPT-5.5 Pro Extended session `iss-00244-plan-centric-guidance`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/discussions/20260627t*.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - relevant runtime files under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- 検証手順:
  - Oracle dry-run で bundle size を確認した。
  - GPT-5.5 Pro Extended browser run を実行した。
  - 回答をローカルの `requirement.md` / `design.md` / `plan.md` と照合した。
- 実験条件:
  - date: 2026-06-27
  - active issue: `iss-00244`
  - model: `gpt-5.5-pro`
  - browser thinking: `extended`

## facts / 観測できた事実 (必須)
- GPT-5.5 Pro は overall verdict を `needs revision before implementation` とした。
- ただし、回答中で「active issue の requirement/design/plan/report 本体を確認できなかった」と述べており、この点は Oracle bundle / symlink / file attachment interpretation の制約による可能性がある。ローカルでは該当文書は存在し、作成済みである。
- GPT-5.5 Pro は、現行 runtime に `step_assurance` / `context_packets` / `selected_step` / `_compile_execution_context()` / `workflow-plan-unselectable` が残っていることを critical / high risk と指摘した。
- GPT-5.5 Pro は、shipped skills が `selected step when present` を agent checklist に登録する文言を残すと dynamic guidance model が復活しやすいと指摘した。
- GPT-5.5 Pro は、`assurance classify/verify=standard` と `guidance issue-planning=strict` の不一致を、verified assurance contract と scaffold heuristic の authority precedence 問題として扱うべきだと指摘した。
- GPT-5.5 Pro は、`may_execute_approved_plan` 相当の明示、dynamic fields absence の negative tests、structured step selection 不要テスト、invalid assurance fail-closed test、projection refresh test、docs/skills grep check を推奨した。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 回答の「issue 本体を確認できなかった」は採用しない。ローカルで `spec-dock/active/issue/*.md` を確認済みで、Oracle dry-run でも bundle は作成されている。ただし、外部助言側の可視性制限として report に残す価値はある。
  - dynamic fields / shipped skill cleanup / profile authority consistency / negative tests の指摘は、既存の issue docs に概ね織り込まれているが、`may_execute_approved_plan` と invalid assurance fail-closed の明示は補強した方がよい。
  - `workflow-plan-unselectable` を明示的な削除対象 / regression guard にすることで、今回の「step 1 に残り続ける」系統の失敗をより直接に防げる。
- 推測の根拠:
  - `design.md` は `Runbook` から `step_assurance` / `context_packets` を削除する方針を既に持つ。
  - `plan.md` は tc-001..tc-010 を持つが、approved-plan permission boolean / invalid assurance fail-closed / no structured step heading の独立 test は薄かった。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Oracle が「active issue 本体を確認できなかった」と判断した根本原因。
  - 実装時に `may_execute_approved_plan` を Markdown と JSON の両方に出すか、JSON only にするか。
- 確認できない理由:
  - 本 artifact は planning review adoption であり、実装はまだ開始していないため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 現時点ではなし。hard cutover 方針はユーザー回答済み。
- pressure-test question として切り出すべき候補:
  - なし。
- 質問せずに解決できた候補:
  - Oracle の「互換 shim」提案はなく、hard cutover と整合する範囲で採用できる。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `authority`
  - `authorized_profile`
  - `scaffold`
  - `may_execute_approved_plan`
- 既存 docs / code / tests / discussions での使われ方:
  - guidance は現在 `STRICT_LEGACY_AUTHORITY` を fallback し、`authorized_profile=strict` を表示しうる。
  - assurance contract は `authorized_profile=standard` を current source binding として持ちうる。
  - `scaffold` は template-only と draft/reviewer-missing が混ざりやすい。
- 判断が必要な理由:
  - issue-execution guidance が agent-facing preflight である以上、実行可否と authority source を誤表示すると作業手順全体が不安定になる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Valid `assurance.json` が `standard` を示すが、guidance が draft/scaffold heuristic により `strict` を表示する。
  - Approved executable plan があるが、旧 `_STEP_HEADING_RE` に合う implementation heading がなく、旧 runtime なら `workflow-plan-unselectable` で block していた。
  - Invalid assurance contract のとき、runtime が strict fallback を authoritative profile として表示してしまう。
  - Projection files `current-runbook.*` が古い dynamic sections を残す。
- その edge case が requirement / design / plan に与える影響:
  - `may_execute_approved_plan` と fail-closed semantics を明示する。
  - `workflow-plan-unselectable` と dynamic fields を negative tests に入れる。
  - projection refresh / non-canonical output の検証を S05/S90 に入れる。

## implications / 判断への含意 (必須)
- 採用:
  - `may_execute_approved_plan` を output contract に追加する。
  - `workflow-plan-unselectable` を削除対象 / regression guard に明記する。
  - invalid assurance fail-closed と profile authority consistency を test closure として追加する。
  - projection refresh で dynamic sections が残らないことを explicit check にする。
- 既にカバー済み:
  - `step_assurance` / `context_packets` / `selected_step` の削除。
  - shipped skills から selected step 登録文を削除。
  - provider / dogfood parity。
- 採用しない / 参考止まり:
  - 「issue docs 本体が確認できないので planning readiness を直接検証できない」という外部助言は、Oracle 側の可視性制約として扱い、ローカル gate の追加理由としてのみ使う。

## リスク/制約 (任意)
- `may_execute_approved_plan` は単純な boolean に留める。新しい dynamic state machine や step selector にはしない。
- `context_packets.py` / `context_routing.py` の完全削除は、残存利用調査後に orphan-free で判断する。

## 反映先 (任意)
- reflected_to:
  - `requirement.md` AC-001 / AC-004 / AC-010
  - `design.md` output contract / test strategy
  - `plan.md` closure index / S01 / S02 / S05 / S90
  - `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- Oracle ChatGPT session: `iss-00244-plan-centric-guidance`
- Local command: `npx -y @steipete/oracle --engine browser --model gpt-5.5-pro --browser-thinking-time extended ...`
