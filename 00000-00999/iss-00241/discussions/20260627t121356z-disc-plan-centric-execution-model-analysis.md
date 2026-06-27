---
種別: discussion
ID: "20260627t121356z-disc"
タイトル: "plan-centric issue execution model analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連:
  - "20260627t112517z-research"
  - "20260627t114637z-disc"
authority: "synthesized"
derived_from:
  - "oracle: gpt-5.5-pro extended via chatgpt-use"
  - "user concern: dynamic guidance model is too complex for intended value"
  - "local active issue requirement/design/plan/report"
reflected_to: []
---

# plan-centric issue execution model analysis

## 位置づけ
- この artifact は、`guidance issue-execution` の動的 step selection / mutable report parsing / progress metadata 方向が、やりたいことに対して複雑すぎるのではないか、というユーザー懸念を受けた設計ディスカッションである。
- `chatgpt-use` skill により Oracle CLI browser mode で GPT-5.5 Pro Extended に分析を依頼し、その回答をローカル文脈へ統合した。
- 前回の `20260627t114637z-disc` は Hybrid metadata 方向を候補にしたが、本 artifact はそれをさらに simplification 方向へ pressure test する。

## 問題定義
- 現行の方向では、Issue execution agent は以下を横断する必要がある。
  - skill instructions
  - `guidance issue-execution` stdout
  - `plan.md`
  - `report.md`
  - generated projection / context packet
  - step completion parser の推定結果
- さらに、作業中に `report.md` を更新し、その `report.md` から runtime が次 step を推定するため、audit ledger と control plane が混ざっている。
- この複雑さは、軽量タスクの過剰 gate を減らすという Epic の目的に対して過大であり、AI agent の instruction-following を逆に難しくする可能性がある。

## Oracle 分析の結論
- 推奨は Option 3: Hybrid simplified model。
- 具体的には、`plan.md` を単一の executable workflow contract にし、step ごとの review / QA / resource allocation は Issue planning 時に明示的に埋め込む。
- `guidance issue-execution` は step selection engine ではなく、preflight / readiness / consistency validator に縮退する。
- `report.md` は audit / evidence ledger であり、次 step を決める control plane ではない。
- dynamic resource allocation の知識は捨てず、execution-time inference から planning-time authoring へ移す。

## 選択肢比較

| 選択肢 | 評価 | 採否 |
| --- | --- | --- |
| Option 1: 動的 step guidance を堅牢化する | 短期 bug fix には有効。ただし parser、progress metadata、reconciliation tooling が増え、複雑性が増す。 | 短期修復のみ |
| Option 2: `plan.md` だけを実行正本にする | 方向性は良いが、readiness / active context / missing gate の fail-closed 検査が弱くなる。 | 単独採用は弱い |
| Option 3: plan-centric + guidance preflight | 実装計画書へ workflow を集約しつつ、runtime は readiness / consistency のみ検査する。agent が理解しやすく、auditability も維持できる。 | 推奨 |

## 推奨モデル

```text
plan.md:
  実行順、step scope、worker、review pattern、QA obligations、verification、commit/no-op 条件を持つ executable contract。

report.md:
  実施結果、証跡、reviewer verdict、commit/no-op evidence、判断台帳。
  次 step を決める control plane ではない。

guidance issue-execution:
  active issue / artifact readiness / plan executability / missing final gate / consistency を検査する。
  selected_step を authority として返さない。
```

## Issue planning に移すべき知識
- Step ごとの risk / resource classification:
  - no-review
  - lite
  - standard
  - strict
  - critical
- Step ごとの worker routing:
  - parent-orchestration-only
  - dev-coder
  - doc-writer
  - read-only specialist
  - split-required
- Step ごとの review pattern:
  - no reviewer required
  - spec-reviewer only
  - code-reviewer only
  - qa-reviewer only
  - code + qa
  - code + spec
  - qa + code + spec
  - final three-reviewer gate
- Step ごとの verification obligation:
  - docs inspection
  - unit tests
  - integration tests
  - characterization / regression
  - security / privacy review evidence
  - migration / rollback evidence
  - manual verification
  - no-op evidence
- Step ごとの commit / no-op policy:
  - one step = one review scope = one commit
  - approved-no-op 条件
  - post-commit clean check
- Amendment triggers:
  - scope expansion
  - reviewer / QA obligation change
  - closure id change
  - locked expectation change
  - required evidence level change
  - unexpected dependency / design gap

## `guidance issue-execution` に残すべき役割
- active issue の解決。
- `requirement.md` / `design.md` / `plan.md` / `report.md` の存在と状態の preflight。
- `plan.md` が placeholder ではなく executable plan であることの確認。
- `plan.md` に必要な step fields が揃っていることの確認。
- step id の一意性確認。
- S90 / S99 などの docs impact / final quality gate の存在、または明示的 not-applicable の確認。
- 各 step が resource pattern、worker、verification、reviewer gate、report evidence destination、commit/no-op gate を持つことの確認。
- stop conditions と canonical artifact paths の提示。
- `selected_step`、runtime 推定 worker、runtime 推定 reviewer obligation は authority として返さない。

## 実用的な `plan.md` 構造案

```markdown
## Execution Policy Summary

- execution_mode: plan-centric
- step_selection: read this plan top-to-bottom; do not rely on runtime selected_step
- progress_authority: report.md evidence, but report.md is not a control plane
- amendment_required_when:
  - scope expands beyond allowed paths
  - reviewer/QA obligation changes
  - required closure id / locked expectation changes
  - step cannot satisfy close condition
  - unresolved requirement/design/plan gap appears

## Resource Allocation Matrix

| Pattern | Use when | Worker | Verification | Reviewers | Commit policy |
|---|---|---|---|---|---|
| R0 no-review | metadata/read-only/no-op confirmation | parent inspect only | inspection evidence | none or spec-reviewer if docs alignment risk | approved-no-op or evidence-only |
| R1 lite-docs | docs-only low risk | doc-writer | docs inspection | spec-reviewer optional/required per step | one commit |
| R2 standard-code | bounded runtime/tests | dev-coder | unit tests | code-reviewer | one commit |
| R3 strict-cross-layer | multi-layer/runtime+docs/compat | split as needed | unit + integration | code-reviewer + spec-reviewer | one commit per split step |
| R4 critical | security/migration/data/lifecycle/final gates | delegated workers or parent orchestration | targeted + integration + rollback/security/privacy as applicable | code-reviewer + qa-reviewer + spec-reviewer | one commit per gate |

## Step Queue

### S01 — <behavior slice title>

| Field | Value |
|---|---|
| resource_pattern | R2 standard-code |
| worker | dev-coder |
| allowed changes | `<paths>` |
| forbidden changes | `<paths / behavior>` |
| closure ids | C01 |
| Red / pre-implementation evidence | `<expected failing test or characterization>` |
| Green verification | `<exact command>` |
| report evidence destination | `report.md` Step Contract Closure / Test Contract Closure / Reviewer Gate / Step Commit Gate |
| reviewer gate | code-reviewer required |
| QA gate | none |
| commit gate | one commit after reviewer pass; post-commit clean check |
| no-op allowed | only with approved-no-op evidence |
| amendment trigger | if closure expectation / scope / gates change |
```

## `report.md` の位置づけ
- `report.md` に残す:
  - 実行した step id
  - 実際の worker / delegation decision
  - Red / characterization evidence
  - Green verification command and result
  - reviewer verdict
  - fix loop / re-review evidence
  - Step Commit Gate
  - approved-no-op evidence
  - material decision / deviation / follow-up
  - final QA / code / spec review evidence
  - PR delivery / merge preparation evidence
- `report.md` に持たせない:
  - 次 step を決める machine control state
  - mutable progress metadata authority
  - worker raw transcript
  - private reasoning
  - plan amendment へ昇格すべき durable decision の置き場

## failure modes

### 動的 guidance model の failure modes
- report parser drift により、完了済み step が再選択される。
- false completion / false skip が起きる。
- `plan.md`、`report.md`、projection、context packet、runtime policy がそれぞれ authority に見える。
- agent が script-selected step と plan 上の step の不一致を解決できない。
- 毎回 guidance / plan / report / projection を読み、token と時間を消費する。
- parser repair の次に progress metadata、metadata の次に reconciliation tooling が必要になる。
- audit ledger である `report.md` が control plane に変質する。

### plan-centric model の failure modes
- planning-time under-classification により、本来 strict な step が lite に分類される。
- `plan.md` が verbose になりすぎると agent が読まない。
- 実装中に scope が変わったのに plan amendment を通さず続行する。
- `plan.md` に mutable checkbox を置くと、approved contract から progress tracker に変質する。
- guidance を削りすぎると、non-executable plan や missing final gate を実行時に止められない。

## `iss-00241` での近々アクション
- `iss-00241` では大きな architecture pivot は入れない。
- 現在の PR を mergeable にする目的では、既存 dynamic guidance の明白な bug を最小修復する。
- 修正対象:
  - current report ledger で S01-S99 completion evidence がある場合に S01 を再選択しない。
  - session log 形式だけでなく current global report ledgers を読む。
  - all steps completed の場合は implementation start を促さない。
  - parser confidence が低い場合は S01 を返さず、manual next-step confirmation / plan-report consistency check を促す。
- 入れない:
  - machine-readable progress metadata。
  - `guidance issue-execution` の全面再設計。
  - plan-centric execution への full cutover。

## follow-up Issue 候補
- Title:
  - `Simplify issue execution guidance into plan-centric preflight validation`
- Scope:
  - `plan.md` executable step schema に `resource_pattern` / `review_pattern` / QA gates を追加する。
  - issue planning template / prompt に risk/resource allocation matrix を追加する。
  - `guidance issue-execution` から selected_step authority を削除、または legacy/debug-only 化する。
  - `report.md` parser を step selection 用 control plane として使わない。
  - guidance は readiness / consistency validation に限定する。
  - 既存 Issue との migration note を用意する。

## 検証案
- 近々 parser repair:
  - current global report ledger 形式で S01-S99 完了済み fixture を作り、S01 が再選択されないことを確認する。
  - all steps completed 時に implementation worker / context packet を出さないことを確認する。
  - partial completion では legacy selected_step が残る間だけ次 step を返すことを確認する。
  - Red phase pass だけでは completed とみなさないことを確認する。
- follow-up simplified model:
  - 各 step に resource_pattern、worker、verification、reviewer gate、report evidence destination、commit/no-op gate がない場合、guidance が `issue-planning-required` を返す。
  - guidance output が selected_step authority を持たず、active plan path と readiness result を返す。
  - docs-only / runtime / strict / final gate の各 pattern が plan template で表現できる。
  - closure id / locked expectation / evidence level の変更が plan amendment required として検出される。
  - report.md completion evidence があっても guidance は next step を算出しない。

## 判断
- ユーザーが指摘した通り、複雑な dynamic step guidance と progress metadata を導入してまで、step ごとの review obligation を実行時に合成する必要性は高くない。
- より自然な責務分担は、Issue planning が resource / review / QA pattern を判断して `plan.md` に書き込み、Issue execution はその plan を上から順に実行する形である。
- `guidance issue-execution` は消すのではなく、step selection engine から preflight / consistency validator へ縮退させるのが最もバランスが良い。
- `iss-00241` では、現 PR の安全な mergeability のために最小 bug fix に留め、plan-centric model への移行は follow-up Issue として切るのが妥当である。

## Oracle session
- tool: `npx -y @steipete/oracle --engine browser`
- project: Codex-only ChatGPT Project
- model: `gpt-5.5-pro`
- thinking time: `extended`
- session: `spec-dock-plan-centric-execution`
- dry run token estimate: about 38.0k prompt tokens, 10 bundled files
- result: completed successfully
