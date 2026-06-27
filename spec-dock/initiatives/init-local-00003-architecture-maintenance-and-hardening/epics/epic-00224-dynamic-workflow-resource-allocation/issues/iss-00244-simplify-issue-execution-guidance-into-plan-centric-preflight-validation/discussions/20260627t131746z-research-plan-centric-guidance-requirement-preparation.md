---
種別: research
ID: "20260627t131746z-research"
タイトル: "Plan Centric Guidance Requirement Preparation"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "epic-00224"
  - "iss-00241"
  - "20260627t130116z-research"
authority: "synthesized"
derived_from:
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - "spec-dock/active/issue/discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - "spec-dock/docs/authoring/issue-plan.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py"
  - "src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json"
reflected_to: []
---

# 20260627t131746z-research Plan Centric Guidance Requirement Preparation

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00244` の要件定義書を作成する前に、現在の runtime / skill / docs / tests がどの責務を持っているかを確認する。
- `guidance issue-execution` を dynamic step selector から plan-centric preflight / consistency validator へ縮退する場合に、要件へ含めるべき範囲と含めない範囲を整理する。
- 人間判断が必要な未確定事項を、local source で解けるものと解けないものに分ける。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
  - `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `tests/cli_runtime/test_workflow.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
  - `tests/cli_runtime/test_assurance_compose.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で active context を確認した。
  - `./spec-dock/scripts/spec-dock guidance issue-planning` と `./spec-dock/scripts/spec-dock guidance issue-execution` を実行し、現 active issue が requirement scaffold で止まることを確認した。
  - `rg` / `sed` で runtime の `selected_step`、`step_assurance`、`context_packets`、context routing、assurance compose、skill 文面、既存 tests を確認した。
  - ChatGPT 5.5 Pro Extended へ Oracle CLI で second opinion を依頼中。結果は別途追記または sibling discussion へ記録する。
- 実験条件:
  - repo: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
  - branch: `iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation`
  - active issue: `iss-00244`

## facts / 観測できた事実 (必須)
- Active issue `iss-00244` の `requirement.md` / `design.md` / `plan.md` はまだ scaffold / placeholder 状態である。
- 現在の `guidance issue-planning` / `guidance issue-execution` は、scaffold requirement を検知して `requirement-capture-required` を返す。これは要件作成前の状態として妥当である。
- Epic requirement / design は当初設計として、runtime が current step、worker、reasoning effort、context policy、verification、reviewer を compile する `Step Assurance` / `Context Packet` 方向を含んでいる。
- `iss-00241` からの handoff research は、dogfooding で `guidance issue-execution` が完了済み step を誤って S01 と返し続けた問題を、単なる parser bug ではなく runtime step inference model の不安定性として整理している。
- `spec-dock/docs/phase_plan_issue.md` と `spec-dock/docs/authoring/issue-plan.md` は、`plan.md` を planned executable workflow contract / command queue、`report.md` を observed evidence ledger と位置づけている。
- 現行 runtime の `application/workflow.py` は、ready な `issue-execution` で `_compile_execution_context()` を呼び、`compile_step_assurance_projection()` と `compile_context_packet_projection()` を使って `step_assurance` / `context_packets` を生成している。
- 現行 runtime の `application/context_packets.py` は、`plan.md` から step heading を抽出し、`report.md` から完了済み step を推定し、最初の未完了 step を `selected_step` として選ぶ。
- 現行 runtime の `domain/context_routing.py` は、`docs-only` / `runtime` / `migration` / `security-sensitive` などの task kind から worker、reasoning effort、context mode、verification、reviewer を決める。
- 現行 `runbook.py` / `presentation/workflow.py` / `infra/runbook_store.py` は `step_assurance` と `context_packets` を Runbook payload / Markdown projection へ含める構造を持つ。
- 現行 `spec-dock-issue-planning` / `spec-dock-issue-execution` skill は、generated projection を authority としない一方で、「selected step when present」を task checklist に登録するよう記述している。
- `assurance compose` の profile fragment は現在薄く、`plan.step-contract` などを追加するだけで、Issue-level Quality Profile と Step-level Obligation Pattern を十分に作り込む scaffold にはなっていない。
- 既存 `tests/cli_runtime/test_workflow_context_routing.py` は、`guidance issue-execution` が `selected_step`、worker、context mode、verification、reviewers、context packet refs を返すことを期待している。今回の方向性では大きく置換が必要になる。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `iss-00244` の中心課題は、`_completed_step_ids()` の個別修正ではなく、runtime / skill / plan authoring の責務再配分である。
  - 実行時に `report.md` を control plane として parse し、current step や worker/reviewer を選ぶ方式は、report 更新漏れや guidance 再実行漏れに弱い。
  - `guidance issue-execution` は「次に何を実装するか」を決める authority ではなく、「実行してよい前提が揃っているか」を確認する preflight / consistency validator へ縮退するのが妥当である。
  - worker / reviewer / verification / no-op / amendment trigger などの判断は、`plan.md` 作成時に明示的に埋め込み、実行中は `plan.md` を上から順に実行するモデルが最も単純である。
  - `context_routing.py` の既存 matrix は完全削除候補というより、planning-time taxonomy / authoring guidance へ移す判断材料として再利用できる。
  - `ContextPacketStore` や `context-routing-policy.json` の扱いは、今回の issue で runtime authority から外す対象だが、将来の明示的な agent invocation packet 機能として残すかは別判断になり得る。
- 推測の根拠:
  - 既存 docs はすでに plan-centric な思想へ寄っている一方、runtime / tests / skill の一部が旧 dynamic model を保持している。
  - ユーザーは、計画書・skill・script・report state を並行管理するモデルが複雑すぎ、AI agent が追随しづらいと判断している。
  - Dogfooding で step completion inference が実際に誤動作し、作業中に `guidance issue-execution` を十分活用できなかった。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `guidance issue-execution` の JSON / Markdown output から `step_assurance` と `context_packets` を即時削除してよいか、または明示 legacy option を短期間残すべきか。
  - `context-routing-policy.json` / `context_packets.py` / `domain/context_routing.py` をこの issue で削除するか、未使用化して future-use として残すか。
  - `assurance compose` の profile fragment をどこまで厚くし、Step-level Obligation Pattern の scaffold を自動合成するか。
  - `NoReview-ReadOnly` を正式な step obligation pattern として採用するか、単に `approved-no-op` / `inspect-only` の一形態として扱うか。
  - `S90` / `S99` は全 plan で必須とするか、明示 waiver を許すか。
  - Epic 正本の E-RQ-007 / E-RQ-008 / design component 記述をこの issue の完了時にどこまで更新するか。
- 確認できない理由:
  - これらはローカル実装だけでは確定できず、互換性、将来拡張、Epic 正本更新範囲に関わる設計判断であるため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `guidance issue-execution` output contract から `selected_step` / `step_assurance` / `context_packets` を互換期間なしで削除してよいか。
  - `context_routing` / `context_packets` 系のコードをこの issue で削除対象にするか、runtime からは外して planning-time taxonomy の参考実装として残すか。
  - `NoReview-ReadOnly` を正式な step-level pattern として要求に入れるか。
- pressure-test question として切り出すべき候補:
  - 最も影響が大きい質問は、互換性方針である。既存 PR には未マージでありユーザーは以前「互換性不要」と判断しているが、CLI JSON tests / output schema の破壊として扱うかどうかは requirement の受け入れ条件に直結する。
  - 次点は context packet 系の撤去深度である。完全削除なら差分は大きいが単純化効果が高く、未使用化なら安全だが旧概念が残る。
- 質問せずに解決できた候補:
  - `plan.md` を executable workflow contract とすること: 既存 docs とユーザー判断が一致している。
  - generated runbook projection を human/debug-only とし、agent handoff authority にしないこと: 既存 skill と runtime output で既に明記されている。
  - `lite_candidate` は authority ではなく、`authorized_profile` を obligation authority とすること: existing runtime / docs と一致している。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `guidance`
  - `Runbook`
  - `Step Assurance`
  - `Context Packet`
  - `selected_step`
  - `Assurance Profile`
  - `Step-level Obligation Pattern`
- 既存 docs / code / tests / discussions での使われ方:
  - `guidance` は stdout の current handoff であり、projection は non-canonical とされている。
  - `Runbook` は human/debug projection を含むが、skill は projection を authority としない。
  - `Step Assurance` は Epic 初期設計と runtime では stepごとの worker/reviewer/context compile を意味するが、plan-centric 方向では planning-time obligation pattern へ移る。
  - `Context Packet` は現行 runtime では自動生成されるが、ユーザーの問題定義では agent が毎回参照するべき二段階ファイルではない。
  - `selected_step` は現行 runtime が推定する current step だが、plan-centric 方向では runtime が選ぶ概念自体をなくす。
- 判断が必要な理由:
  - 同じ語が runtime authority と planning contract の両方に残ると、後続 agent が再び report parsing や generated projection を正本として扱う可能性がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - `report.md` の Step Contract Closure が完全に更新されているが、runtime parser が読み落として古い step を返す。
  - `plan.md` が構造化不足でも、runtime が issue-wide fallback で ready 扱いし、実行者が plan gap を見落とす。
  - docs-only step が `NoReview-ReadOnly` と誤分類され、spec-reviewer が必要な workflow/docs 変更まで review なしになる。
  - runtime + docs mixed step が分割されず、code-reviewer と spec-reviewer のどちらかが抜ける。
  - `security` / `migration` などの語が forbidden scope にだけ出て false escalation する。
  - 実際には security/privacy impact があるのに Lite / NoReview 系に落ちる。
  - `context-routing-policy.json` が壊れているだけで、実行 preflight が過剰に block される。
  - generated `current-context-packets.json` が古いのに agent が読み続ける。
- その edge case が requirement / design / plan に与える影響:
  - runtime は report completion を次 step 選択に使わない、という要件が必要である。
  - plan readiness は「選択可能 step があるか」ではなく、approved / reviewer-pass / executable plan / assurance freshness / scaffold absence / unresolved marker absence を見る必要がある。
  - `plan.md` authoring / assurance compose に、quality profile と obligation pattern の判断テンプレートを置く必要がある。
  - context packet 自動生成は default execution path から外し、少なくとも agent-facing guidance では参照先として出さない必要がある。

## implications / 判断への含意 (必須)
- 要件定義では、`guidance issue-execution` の責務を `preflight / readiness / consistency` に限定し、`selected_step` / `step_assurance` / `context_packets` を agent-facing authority から外すことを明記する。
- 要件定義では、実装順、worker、reviewer、verification、no-op、amendment trigger は `plan.md` の planned contract に置くことを明記する。
- 要件定義では、`report.md` は observed evidence ledger であり、runtime が次 step を決める control plane ではないことを明記する。
- 要件定義では、`assurance compose` / plan authoring docs / skills / tests を対象に含め、単なる runtime parser 修正に閉じないことを明記する。
- 設計では、`workflow.py` から `_compile_execution_context()` を default guidance path から外し、Runbook schema / Markdown / JSON output / projection store の `step_assurance` と `context_packets` の扱いを整理する必要がある。
- 設計では、既存 `context_routing.py` の情報を削除するか planning-time reference に移すかを明確にする必要がある。

## リスク/制約 (任意)
- provider source が正本であり、`spec-dock/` dogfooding mirror は検証対象である。provider 側の skill / runtime / templates / docs を先に整える必要がある。
- 既存 `test_workflow_context_routing.py` は旧 dynamic model を強く期待しているため、削除・置換・再配置を計画に入れる必要がある。
- Epic 正本にはまだ当初設計の `Step Assurance Compiler` / `Context Packet Compiler` が残るため、`iss-00244` で Epic requirement/design/report への反映を行うか、別 follow-up とするかを判断する必要がある。
- 互換性不要とする場合、破壊的な CLI JSON output 変更を受け入れ条件に明記する必要がある。

## 反映先 (任意)
- reflected_to:
  - `iss-00244/requirement.md`（未反映）
  - `iss-00244/design.md`（未反映）
  - `iss-00244/plan.md`（未反映）

## 参考（References） (任意)
- `20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
- `20260627t121356z-disc-plan-centric-execution-model-analysis.md`
- `20260627t122855z-disc-plan-pattern-taxonomy-and-guidance-simplification.md`
