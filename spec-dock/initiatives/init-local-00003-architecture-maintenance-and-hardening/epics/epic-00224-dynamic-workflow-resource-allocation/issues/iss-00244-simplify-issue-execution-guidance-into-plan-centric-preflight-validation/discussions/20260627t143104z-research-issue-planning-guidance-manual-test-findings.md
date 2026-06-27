---
種別: research
ID: "20260627t143104z-research"
タイトル: "Issue Planning Guidance Manual Test Findings"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "iss-00244"
  - "spec-dock-issue-planning"
  - "guidance issue-planning"
authority: "synthesized"
derived_from:
  - "manual command: ./spec-dock/scripts/spec-dock guidance issue-planning"
  - "manual command: ./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json"
  - "spec-dock/scripts/spec_dock_runtime/domain/workflow_state.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py"
reflected_to: []
---

# 20260627t143104z-research Issue Planning Guidance Manual Test Findings

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00244` の Issue Planning 作業を manual test として実行し、`spec-dock-issue-planning` skill と `guidance issue-planning` が期待通りに動作しているか確認する。
- 要件定義書作成後の runtime guidance / assurance classification の挙動差分を記録し、必要なら本 Issue の設計・計画へ取り込む。

## sources / 調査方法 (必須)
- 参照先:
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
  - `./spec-dock/scripts/spec-dock workflow status --format json`
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/scripts/spec_dock_runtime/domain/workflow_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
- 検証手順:
  - scaffold 状態の requirement で `guidance issue-planning` を実行した。
  - substantive な requirement 本文を書いた後に再度 `guidance issue-planning` を実行した。
  - 同じ requirement に対して `assurance classify --dry-run` を実行した。
  - provider source と dogfooding runtime の `classify_requirement_text()` を比較した。
- 実験条件:
  - active issue: `iss-00244`
  - branch: `iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation`
  - date: 2026-06-27

## facts / 観測できた事実 (必須)
- scaffold requirement では `guidance issue-planning` が `state=requirement-capture`、`next_action=requirement-capture-required`、`reason_code=requirement-scaffold` を返した。これは期待通り。
- substantive な requirement 本文へ更新した後も、frontmatter の `状態: "draft"` により dogfooding runtime の `classify_requirement_text()` は `scaffold` を返した。
- 同じ substantive requirement に対して `assurance classify --stage requirement --dry-run --format json` は `ok=true`、`status=valid`、`authorized_profile=standard` を返した。
- `assurance classify --stage requirement --format json` 実行後も、`guidance issue-planning` は `authority: authorized_profile=strict` を表示した。
- provider source の `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py` には draft status を scaffold 扱いする正規表現がなく、同じ requirement を `substantive` と分類した。
- dogfooding runtime の `spec-dock/scripts/spec_dock_runtime/domain/workflow_state.py` には `状態: "draft"` / `status: "draft"` を scaffold 扱いする正規表現がある。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `guidance issue-planning` は「未記入 scaffold」と「substantive だが draft / reviewer 未通過」を同じ `requirement-scaffold` reason_code で表現している。
  - これは execution safety としては保守的だが、manual test / user-facing guidance としては状態名が不正確で、agent が「本文がまだ未記入」と誤解する可能性がある。
  - `guidance issue-planning` が表示する `authorized_profile=strict` は、最新の `assurance classify` 結果である `authorized_profile=standard` と不一致であり、guidance が読んでいる profile source または fallback が stale / inconsistent である可能性がある。
  - provider source と dogfooding runtime に drift がある可能性があり、今回の hard cutover 実装では provider / dogfood parity を必ず確認する必要がある。
- 推測の根拠:
  - `workflow_state.py` の実装差分と CLI 出力。
  - `assurance classify` は本文を読めており、要件の中身自体は substantive として扱える。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - draft status を scaffold 扱いする挙動が、意図した policy なのか dogfooding runtime だけの drift なのか。
  - `guidance issue-planning` の reason_code を `requirement-draft` / `review-required` などへ分けるべきか。
  - `guidance issue-planning` の `authorized_profile=strict` が、古い `assurance.json`、fallback policy、または別の profile calculation のどれに由来するか。
- 確認できない理由:
  - 本 Issue の現在の主目的は issue-execution guidance の hard cutover であり、issue-planning status taxonomy の修正をこの Issue に含めるかは設計で判断するため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 現時点ではなし。`hard cutover` 方針はユーザー回答済み。
- pressure-test question として切り出すべき候補:
  - なし。draft/scaffold reason_code の扱いは、今回の設計内で不具合または follow-up として分類できる。
- 質問せずに解決できた候補:
  - substantive requirement を書いても `guidance issue-planning` が次へ進まない理由は、dogfooding runtime が `状態: "draft"` を scaffold 扱いするため。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `scaffold`
  - `draft`
  - `substantive`
  - `requirement-capture`
- 既存 docs / code / tests / discussions での使われ方:
  - docs では scaffold / template-only / unresolved / reviewer 未通過をいずれも次 phase へ進めない状態として扱う。
  - dogfooding runtime では draft status が scaffold reason_code に畳まれている。
  - assurance classification は draft requirement でも provisional contract を生成できる。
- 判断が必要な理由:
  - guidance が manual test / agent-facing handoff として意味を持つなら、reason_code は agent が次に何をすべきか誤解しない粒度である必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - requirement 本文は substantive だが frontmatter `状態: "draft"` のため `guidance issue-planning` が `requirement-scaffold` を返す。
  - `assurance classify` が `standard` を返した直後でも、`guidance issue-planning` が `strict` を表示する。
  - provider source では substantive、dogfooding runtime では scaffold と分類される。
- その edge case が requirement / design / plan に与える影響:
  - `iss-00244` の design / plan では provider / dogfood parity、guidance output semantics、authorized profile source consistency を確認対象に含める。
  - issue-planning guidance の reason_code 修正をこの Issue に含めるか、follow-up にするかを設計で明記する。

## implications / 判断への含意 (必須)
- `requirement.md` の AC-009 / AC-010 に、issue-planning guidance dogfood evidence と provider/dogfood consistency を入れる。
- `design.md` では、issue-execution hard cutover だけでなく、guidance output semantics が agent を誤誘導しないことを確認する。
- `plan.md` では、manual test findings を S99 または planning validation step の確認項目に入れる。
- guidance が表示する assurance profile と `assurance classify` の source binding が一致することを S05/S99 の確認項目に入れる。

## リスク/制約 (任意)
- draft/scaffold reason_code の修正をこの Issue に含めすぎると scope が広がる。一方で、今回の Issue は guidance simplification を扱うため、agent-facing guidance semantics の改善として含める余地がある。

## 反映先 (任意)
- reflected_to:
  - `requirement.md` AC-009 / AC-010
  - `design.md` guidance state semantics / provider-dogfood parity
  - `plan.md` manual test validation

## 参考（References） (任意)
- `./spec-dock/scripts/spec-dock guidance issue-planning`
- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json`
