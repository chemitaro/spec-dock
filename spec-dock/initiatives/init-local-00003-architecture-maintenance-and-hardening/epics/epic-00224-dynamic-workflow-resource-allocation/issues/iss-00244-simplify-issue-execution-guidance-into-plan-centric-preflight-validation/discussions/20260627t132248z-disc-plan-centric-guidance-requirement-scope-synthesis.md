---
種別: disc
ID: "20260627t132248z-disc"
タイトル: "Plan Centric Guidance Requirement Scope Synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00244"]
関連:
  - "iss-00244"
  - "iss-00241"
  - "20260627t131746z-research"
  - "oracle:iss-00244-requiremen-prep-analysis"
authority: "proposed"
derived_from:
  - "20260627t131746z-research-plan-centric-guidance-requirement-preparation.md"
  - "20260627t130116z-research-plan-centric-execution-guidance-handoff.md"
  - "oracle: gpt-5.5-pro extended via chatgpt-use, session iss-00244-requiremen-prep-analysis"
reflected_to: []
---

# 20260627t132248z-disc Plan Centric Guidance Requirement Scope Synthesis

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - `iss-00244` の要件定義書に入れるべき範囲、入れない範囲、受け入れ条件テーマ、未確定判断を整理する。
  - `guidance issue-execution` を runtime-selected execution から plan-centric execution + runtime preflight validation へ切り替える場合の責務境界を整理する。
- この synthesis が必要な理由:
  - `iss-00241` で発見された step selection regression は個別 parser bug ではなく、runtime が report / plan を読んで次 step と worker / reviewer / context を動的に推定する model 全体の不安定性を示している。
  - 要件定義前に、dynamic selector を改善する issue ではなく、default authority path から外す issue であることを固定する必要がある。

## derived question sheets / research (必須)
- `interview`:
  - 未作成。必要なら互換性 / context packet 撤去深度について 1 問だけ作成する。
- `research`:
  - `20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
  - `20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`
- その他の根拠:
  - Oracle / ChatGPT 5.5 Pro Extended: `iss-00244-requiremen-prep-analysis`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`

## synthesis (必須)
- 合意済みのこと:
  - `plan.md` は planned executable workflow contract / command queue であり、実装順、worker、reviewer、verification、closure、commit/no-op、amendment trigger を保持する。
  - `report.md` は observed evidence ledger / decision ledger であり、runtime が次 step を決める control plane ではない。
  - `guidance issue-execution` は active issue、artifact readiness、assurance freshness、plan executability、stop conditions を確認する preflight / consistency validator に縮退する。
  - `selected_step` / `step_assurance` / runtime worker-reviewer-verification inference / default context packet auto generation は、default issue-execution authority path から外す。
  - 既存 dynamic selector を改善するのではなく、default path から取り除く。
  - ユーザー回答により、`hard cutover` を採用する。旧 dynamic guidance fields / interface は互換期間なしで削除対象にする。
- 未合意 / 未確定のこと:
  - `context_packets.py` / `context_routing.py` の削除範囲は、残存利用の有無を provider source / tests で確認したうえで design に落とす。ただし旧 dynamic guidance interface としての互換維持はしない。
  - `NoReview-ReadOnly` を正式な step obligation pattern として採用するか、`inspect-only` / `approved-no-op` の rationale として扱うか。
  - S90 / S99 を常時必須にするか、明示 waiver syntax を認めるか。
- source-grounded に解決できたこと:
  - Existing docs は plan-centric authority split をすでに支持している。
  - Current runtime / tests / skills は旧 dynamic model を保持しており、要件範囲に含める必要がある。
  - `assurance compose` の現 profile fragment は薄いため、planning-time obligation allocation を支える scaffold / authoring guidance の強化が必要である。

## 選択肢 / tradeoff (必須)
- Option A: hard cutover / default output から dynamic fields を削除する（採用）
  - Pros:
    - agent-facing authority が単純になり、古い `selected_step` や stale context packet を読み続ける余地が小さい。
    - tests も新 contract に明確に置換できる。
    - ユーザーが求める「実装計画書に一本化する」方向と最も一致する。
  - Cons:
    - JSON output consumer がある場合は破壊的変更になる。
    - `context_routing.py` など既存実装の削除 / 未使用化範囲が大きくなる。
- Option B: deprecated fields を短期互換として残す
  - Pros:
    - 既存 tests / consumer の段階移行がしやすい。
    - context packet 系を後続 issue へ切り離しやすい。
  - Cons:
    - agent が deprecated field を authority と誤認するリスクが残る。
    - 今回の主目的である単純化が弱くなる。
    - 「生成された古い workflow / context を読み続ける」問題を完全には断てない。
- Option C: selected_step だけ削除し、context packet utility は明示 command に移す
  - Pros:
    - 将来の bounded packet / clean-room reviewer packet の価値を残せる。
    - default execution は単純化できる。
  - Cons:
    - この issue 内で別 command 設計まで含めると scope が広がる。
    - user-facing guidance と utility の authority 境界をさらに設計する必要がある。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `requirement.md`: default `guidance issue-execution` は preflight / consistency validator であり、次 step / worker / reviewer / verification を選ばない。
  - `requirement.md`: `plan.md` は executable workflow contract、`report.md` は observed evidence ledger として扱う。
  - `requirement.md`: runtime は `report.md` の completion evidence を読んで next step を算出しない。
  - `requirement.md`: `selected_step` / `step_assurance` / `context_packets` は default agent-facing authority から外す。
  - `design.md`: `_compile_execution_context()`、`compile_step_assurance_projection()`、`compile_context_packet_projection()`、Runbook schema、presentation、tests の移行方針を具体化する。
  - `plan.md`: plan schema / assurance compose / skill / runtime / tests / dogfooding validation を step 分割する。
- まだ proposal に留める理由:
  - 互換性方針と context packet 系の撤去深度は、人間の判断により実装範囲が変わるため。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - 目的、背景、スコープ、非交渉制約、受け入れ条件、例外 / edge cases、用語。
- `design.md`:
  - runtime path、Runbook schema、plan lint、assurance compose、skill text、test replacement、provider / dogfood mirror 境界。
- `plan.md`:
  - S01: plan authoring / assurance compose contract。
  - S02: guidance preflight output。
  - S03: dynamic selector / context packet default path removal。
  - S04: skills / docs。
  - S05: tests / dogfooding validation。
  - S90 / S99。
- `ADR`:
  - 現時点では不要。Epic 内の既存議論で方向性は十分に説明されており、Issue-local design に落とせる。
- `report.md` Evidence Adoption Ledger:
  - この disc と research を要件定義へ採用したことを、後続 planning / authoring gate で記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md` / `design.md` / `plan.md`

## 推奨案 (必須)
- 推奨案:
  - `iss-00244` は hard cutover 寄りの plan-centric model を採用する。
  - default `guidance issue-execution` は `execute-approved-plan` / `planning-required` / `blocked` などの preflight result だけを返し、authoritative `selected_step` / `step_assurance` / `context_packets` を返さない。
  - context packet / context routing 系は default issue-execution から切り離し、不要な interface / field は削除する。将来の明示 utility が必要なら別 issue へ送る。
  - plan authoring / assurance compose 側に Issue-level Quality Profile と Step-level Obligation Pattern を埋め込む。
- 理由:
  - ユーザーの問題定義は、動的 selector の精度不足ではなく、実行計画書・skill・script・report state の多重管理そのものの複雑性である。
  - 既存 docs はすでに plan-centric authority split を支持している。
  - 旧 field を残すと agent が再び generated state を authority として扱うリスクが残る。

## 推奨反映先 (必須)
- `requirement.md`:
  - AC: ready guidance has contract source / evidence ledger / stop conditions and no authoritative selected step.
  - AC: report completion evidence does not affect guidance output.
  - AC: non-executable plan blocks execution.
  - AC: plan contract lint validates step pattern / worker / paths / verification / reviewer / evidence / commit-no-op / amendment trigger.
  - AC: skill text no longer tells agents to register selected step as execution authority.
  - AC: hard cutover により `selected_step` / `step_assurance` / `context_packets` は default Markdown / JSON / runbook projection から削除される。
- `design.md`:
  - Remove default call from `workflow_next()` to `_compile_execution_context()`.
  - Remove or ignore `step_assurance` / `context_packets` fields in Runbook output.
  - Replace `test_workflow_context_routing.py` dynamic tests with plan-centric preflight tests.
- `plan.md`:
  - Separate provider runtime, provider assets, skill docs, tests, dogfooding validation, Epic reflection update.
- `ADR`:
  - 不要。Issue design と Epic report / discussions で十分。
- `report.md` Evidence Adoption Ledger:
  - 要件作成時に this disc / Oracle result / local research の採用を記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - `_completed_step_ids()` の堅牢化だけで閉じる案: 根本問題が control-plane 多重化であるため不採用。
  - runtime が worker / reviewer / verification を推定し続ける案: planning-time contract へ一本化する目的と矛盾するため不採用。
- deferred:
  - 明示 `--step Sxx` context packet utility: default execution path の単純化後、必要性を別 issue で判断する。
  - workflow-runbook schema version bump の詳細: 互換性方針の回答後に design で具体化する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - 人間判断が必要な 1 問を interview artifact として作成し、回答後に requirement authoring へ進む。
- 追加で作る discussion docs:
  - 互換性 / context packet 撤去深度の interview artifact。
