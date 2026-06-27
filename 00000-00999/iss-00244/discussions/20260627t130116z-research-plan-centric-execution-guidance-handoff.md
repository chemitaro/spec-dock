---
種別: research
ID: "20260627t130116z-research"
タイトル: "Plan Centric Execution Guidance Handoff"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "iss-00241"
  - "20260627t112517z-research"
  - "20260627t114637z-disc"
  - "20260627t121356z-disc"
  - "20260627t122855z-disc"
authority: "synthesized"
derived_from:
  - "iss-00241 discussions"
  - "oracle: gpt-5.5-pro extended via chatgpt-use"
reflected_to: []
---

# 20260627t130116z-research Plan Centric Execution Guidance Handoff

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00241` で発見・分析した `guidance issue-execution` の複雑性問題を、follow-up `iss-00244` の調査材料として移管する。
- まだ requirement / design / plan を具体化しない段階で、次に読むべき根拠、採用済み方向性、未検証事項、想定 failure mode を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - `../iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps/discussions/20260627t112517z-research-guidance-step-selection-regression-analysis.md`
  - `../iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps/discussions/20260627t114637z-disc-guidance-execution-model-stability-analysis.md`
  - `../iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps/discussions/20260627t121356z-disc-plan-centric-execution-model-analysis.md`
  - `../iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps/discussions/20260627t122855z-disc-plan-pattern-taxonomy-and-guidance-simplification.md`
  - `../iss-00241-resolve-epic-traceability-and-review-policy-gate-gaps/report.md`
- 検証手順:
  - `iss-00241` の dynamic guidance regression analysis と plan-centric model analysis を確認した。
  - ユーザー判断として、`iss-00241` では本体実装せず、別 Issue に分離する方針が明示された。
  - この artifact は移管用の research であり、`iss-00244` の要件定義書・設計書・計画書はまだ作成しない。
- 実験条件:
  - repo: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
  - source issue: `iss-00241`
  - target issue: `iss-00244`

## facts / 観測できた事実 (必須)
- `guidance issue-execution` は `plan.md` と `report.md` を読み、completed step を推定し、`selected_step` と step assurance / context packet を返す実装方向だった。
- Dogfooding では、`report.md` 上に S01-S99 の完了証跡があるにもかかわらず、`guidance issue-execution` が `selected_step: S01` を返し続けた。
- regression analysis では、`report.md` の global ledger を parser が読めず、session-log 形式に依存していたことが直接原因として整理された。
- その後の設計分析では、`report.md` を control plane として parse し続けるより、`plan.md` を executable workflow contract として一本化する方向が支持された。
- ユーザーは plan-centric 方向を支持し、`iss-00241` では本格実装せず、follow-up Issue へ分ける判断を明示した。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `iss-00244` の主題は、個別 parser bug の修正ではなく、issue planning / issue execution の責務再分配である。
  - dynamic resource allocation の知識は runtime step inference から planning-time plan authoring へ移すのが妥当である。
  - `guidance issue-execution` は step selector ではなく preflight / consistency validator へ縮退するのが妥当である。
- 推測の根拠:
  - Oracle 分析は、`selected_step`、`report.md` completion parsing、runtime worker/reviewer inference、context packet auto generation を削除または deprecated 化する方向を推奨した。
  - ユーザーも、計画書・skill・script・report state の多重管理が AI agent にとって複雑すぎると判断した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `assurance classify / compose` と plan-centric `plan.md` schema の具体的な統合点。
  - `guidance issue-execution` の v2 stdout / JSON contract を既存 CLI consumers とどう互換させるか。
  - `selected_step` / `step_assurance` / `context_packets` を即時削除するか、legacy opt-in として段階移行するか。
  - plan contract lint をどの command に置くか。
- 確認できない理由:
  - `iss-00244` の要件定義・設計・計画はまだ開始しておらず、正式な仕様決定は次工程で行うため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - legacy JSON compatibility を残す必要があるか。
  - `NoReview-ReadOnly` を正式 pattern として採用するか。
  - context packet generation を完全に退役するか、明示 `--step Sxx` utility として残すか。
- pressure-test question として切り出すべき候補:
  - Lite / Standard / Strict / Critical を issue-level profile とし、step-level obligation pattern を別に持つ二層 taxonomy で十分か。
  - S90 / S99 を全 plan に必須にするか、明示 waiver を許すか。
- 質問せずに解決できた候補:
  - `iss-00241` に本体実装を混ぜない判断: ユーザーが明示的に別 Issue 分離を指示した。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `guidance`
  - `selected_step`
  - `step_assurance`
  - `context_packets`
  - `Lite / Standard / Strict / Critical`
- 既存 docs / code / tests / discussions での使われ方:
  - 既存 runtime では `guidance issue-execution` が selected step と assurance/context を返す。
  - plan-centric 方向では `guidance issue-execution` は preflight に縮退し、step selection authority を持たない。
  - Lite 等は runtime で obligation を縮減する authority ではなく、planning-time profile として扱う方向が提案された。
- 判断が必要な理由:
  - 同じ単語が runtime authority と planning contract の両方に見えると、後続 agent が再び多重正本として扱うため。

## edge cases / 具体シナリオ (必須)
- edge case:
  - `report.md` に完了証跡があるが、`plan.md` は legacy schema のまま。
  - docs-only step が `NoReview-ReadOnly` と誤分類される。
  - runtime + docs mixed step が split されず、code-reviewer か spec-reviewer の片方だけになる。
  - security/privacy という語が forbidden scope にだけ出る場合に false escalation する。
  - actual security/privacy impact があるのに Lite profile のままになる。
- その edge case が requirement / design / plan に与える影響:
  - plan contract lint と escalation trigger を設計する必要がある。
  - `NoReview-ReadOnly` は canonical artifact 変更なしに限定する必要がある。
  - code + docs は split-first、不可なら `CodePlusSpec` と両 reviewer 明示にする必要がある。

## implications / 判断への含意 (必須)
- `iss-00244` では、Issue-level Quality Profile と Step-level Obligation Pattern の二層 taxonomy を requirement / design / plan に落とす候補とする。
- `plan.md` を executable workflow contract とし、reviewer / QA / verification / no-op / amendment trigger を step に明記する方向で設計する。
- `guidance issue-execution` は readiness / consistency preflight に限定し、`selected_step` / runtime inference を削除または deprecated 化する方向で設計する。
- `report.md` は audit/evidence ledger として残し、次 step を決める control plane にしない。

## リスク/制約 (任意)
- `iss-00241` の PR を壊さないため、`iss-00244` での本体実装までは existing runtime behavior を大きく変更しない。
- provider source と dogfooding mirror の両方に影響するため、follow-up 実装時は parity tests / sync / validate が必要になる。
- plan-centric 化は tests の期待値を大きく変えるため、既存 dynamic selection tests はまとめて置換する必要がある。

## 反映先 (任意)
- reflected_to:
  - `iss-00244` requirement/design/plan（未作成）

## 参考（References） (任意)
- `20260627t112517z-research`: guidance step selection regression の直接原因。
- `20260627t114637z-disc`: dynamic model stability / Hybrid metadata 案の検討。
- `20260627t121356z-disc`: plan-centric execution model の採用方向。
- `20260627t122855z-disc`: pattern taxonomy と guidance simplification の具体案。
