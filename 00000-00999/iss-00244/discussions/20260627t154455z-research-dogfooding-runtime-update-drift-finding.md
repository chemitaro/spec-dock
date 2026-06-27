---
種別: research
ID: "20260627t154455z-research"
タイトル: "Dogfooding Runtime Update Drift Finding"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "iss-00244"
  - "dogfooding"
  - "spec-dock update"
authority: "synthesized"
derived_from:
  - "uvx --from . spec-dock update ."
  - "./spec-dock/scripts/spec-dock guidance issue-execution"
  - "rg provider/dogfood workflow.py"
reflected_to:
  - "report.md"
---

# 20260627t154455z-research Dogfooding Runtime Update Drift Finding

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00244` 実装中の dogfooding/manual test として、provider 側 runtime 変更が dogfooding workspace の `./spec-dock/scripts/spec-dock guidance ...` に反映されるかを確認する。
- 反映されない場合の観測事実、暫定対応、今後の確認観点を記録する。

## sources / 調査方法 (必須)
- 参照先:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `spec-dock/scripts/spec_dock_runtime/application/workflow.py`
  - `./spec-dock/scripts/spec-dock guidance issue-execution`
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
  - `uvx --from . spec-dock update .`
- 検証手順:
  - provider 側 runtime を plan-centric guidance に変更した。
  - `uvx --from . spec-dock update .` を実行した。
  - dogfooding 側 `./spec-dock/scripts/spec-dock guidance issue-execution` を実行した。
  - provider / dogfood の `application/workflow.py` を grep し、判定ロジック差分を比較した。
  - dogfooding runtime の該当ファイルを provider 正本から同期した後、guidance を再実行した。
- 実験条件:
  - active issue: `iss-00244`
  - branch: `iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation`
  - date: 2026-06-28

## facts / 観測できた事実 (必須)
- `uvx --from . spec-dock update .` は `spec-dock: ok (update)` を返した。
- その直後、dogfooding 側 `guidance issue-execution` は `reason_code=plan-not-executable` を返し続けた。
- grep で確認すると、provider 側 `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py` は新しい `_classify_plan_text()` 判定順になっていたが、dogfooding 側 `spec-dock/scripts/spec_dock_runtime/application/workflow.py` は古い判定順のままだった。
- `.agents/skills` 側は update 後に `selected step when present` が消えていたため、少なくとも installed skill assets は更新されていた。
- provider runtime files を dogfooding runtime files へ同期した後、`guidance issue-execution` は `state=ready`、`next_action=execute-approved-plan`、`may_execute_approved_plan=true`、`authorized_profile=standard` を返した。
- 同期後の projection / runtime / skill grep では `selected_step`、`Step Assurance`、`Context Packets`、`context_packets`、`workflow-plan-unselectable` が対象範囲で残らなかった。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `spec-dock update .` が dogfooding workspace の全 runtime files を必ず上書きしているとは限らない、または対象 runtime file の更新条件に差分検出 / preserve ルールがある可能性がある。
  - 今回の PR では provider source と dogfooding workspace の両方を diff に含めて、実際の dogfooding command が新 contract を使うことを証跡化する必要がある。
  - この finding は `iss-00244` 実装そのものの主設計ではなく、dogfooding / update behavior の観測である。別途 update path の原因調査を行う余地はある。
- 推測の根拠:
  - update success 後も dogfooding runtime file が provider source と異なっていた。
  - 手動同期後に guidance output が期待通り変化した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `spec-dock update .` が runtime files を更新しなかった根本原因。
  - この drift が今回の local dogfooding workspace 固有なのか、一般 consumer repo でも再現するのか。
- 確認できない理由:
  - 本 Issue の主目的は issue-execution guidance hard cutover であり、installer/update behavior の深掘りは scope expansion になり得るため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 現時点ではなし。
- pressure-test question として切り出すべき候補:
  - なし。
- 質問せずに解決できた候補:
  - PR 前の dogfooding validation としては、provider と dogfood runtime の両方を確認し、必要な同期差分を含めることで解消できる。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `provider source`
  - `dogfooding workspace`
  - `update`
  - `projection`
- 既存 docs / code / tests / discussions での使われ方:
  - provider source は `src/spec_dock/assets/spec_dock/...`。
  - dogfooding workspace は `spec-dock/...`。
  - projection は `.agent/runbooks/current-runbook.*` と `active/current-runbook.*` で、人間/debug 用の non-canonical output。
- 判断が必要な理由:
  - `update` 成功だけを dogfooding parity の証跡にすると、実際の `./spec-dock/scripts/spec-dock` が古い runtime を使い続ける可能性がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - provider runtime は修正済みだが、dogfooding runtime が古いままのため、manual test では旧挙動が残る。
  - `.agents/skills` は更新済みだが `spec-dock/scripts/spec_dock_runtime` は更新されない。
- その edge case が requirement / design / plan に与える影響:
  - `AC-010` / `tc-010` の provider and dogfood validation を、`update` 成功だけではなく実コマンド出力と provider/dogfood grep で確認する必要がある。

## implications / 判断への含意 (必須)
- `report.md` の Dogfooding validation evidence に、`update` 後の drift と手動同期後の解消を記録する。
- 今回の PR では、provider source と dogfooding workspace の runtime / skill / projection の整合を最終確認する。
- update path の根本原因は、必要なら follow-up として扱う。

## リスク/制約 (任意)
- 手動同期は dogfooding validation のための対応であり、provider source が実装正本であることは変えない。
- root cause をこの Issue で深掘りしすぎると、installer/update behavior の別設計へ scope が広がる。

## 反映先 (任意)
- reflected_to:
  - `report.md`

## 参考（References） (任意)
- `uvx --from . spec-dock update .`
- `./spec-dock/scripts/spec-dock guidance issue-execution`
- `rg -n "selected_step|Step Assurance|Context Packets|context_packets|workflow-plan-unselectable" ...`
