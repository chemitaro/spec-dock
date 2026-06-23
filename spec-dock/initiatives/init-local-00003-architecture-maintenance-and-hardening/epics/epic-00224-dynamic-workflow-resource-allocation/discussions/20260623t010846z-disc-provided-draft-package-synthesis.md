---
種別: disc
ID: "20260623t010846z-disc"
タイトル: "Provided Draft Package Synthesis"
状態: "draft"
作成者: "Codex"
最終更新: "2026-06-23"
親: ["epic-00224"]
関連:
  - "20260623t010733z-draft-requirement"
  - "20260623t010737z-draft-design"
  - "20260623t010749z-draft-plan"
  - "20260623t010747z-disc"
  - "20260623t010748z-disc"
  - "20260623t010750z-research"
  - "20260623t010751z-research"
authority: "proposed"
derived_from:
  - "user-provided GPT discussion log and draft package"
reflected_to: []
---

# 20260623t010846z-disc Provided Draft Package Synthesis

## 保存した入力資料

- `20260623t010733z-draft-requirement-adaptive-assurance-draft-requirement.md`
  - Epic requirement draft.
- `20260623t010737z-draft-design-adaptive-assurance-draft-design.md`
  - Epic design draft.
- `20260623t010749z-draft-plan-adaptive-assurance-draft-plan.md`
  - Epic plan draft.
- `20260623t010747z-disc-issue-slice-handoff-seeds.md`
  - Issue planning handoff seeds for I01 through I07.
- `20260623t010748z-disc-epic-issue-selection-decision.md`
  - Decision record for using a new Epic plus multiple Issues.
- `20260623t010750z-research-draft-package-readme.md`
  - Package README and ingestion instructions.
- `20260623t010751z-research-gpt-discussion-full-log.md`
  - Full GPT discussion log provided by the user.

## 理解した目的

- この Epic は、軽量なタスクにも重い品質ゲートと review cycle がかかり、token と wall-clock time が過剰になる問題を解く。
- 解決方針は、Issue / step の risk facts から `lite / standard / strict / critical` の Assurance Profile と `routine / normal / complex / deep` の Complexity Tier を導出し、必要な workflow obligation だけを実行時に提示すること。
- 変更の中心は、`.agents/skills/**` を Issue 状態ごとに差し替えることではなく、固定された薄い Skill kernel から `spec-dock workflow next ...` を呼び、runtime が現在状態専用の complete Runbook を返す構造へ移すこと。
- `epic-00158-agent-workflow-pdca-hardening` は、skills / docs / templates の context surface ownership を安定化した前提 Epic として扱う。本 Epic はその後続として、Assurance Contract、Runbook compiler、artifact composer、step assurance、GitHub Codex review policy、blocker-centric repair semantics を実装する。

## 現在実装との対応

- 現行の `spec-dock-issue-planning` skill は、requirement / design / plan authoring、delegated draft、fresh reviewer gate などを skill 内に直接列挙している。
- 現行の `spec-dock-issue-execution` skill は、one-step-at-a-time、delegation、reviewer gate、commit gate などを固定的に持つ。
- `workflow next` / `workflow status` / `assurance classify` / `assurance compile` に相当する runtime command は、現時点の repo 検索では未実装。
- 既存実装には dependency graph の compiled projection、delegated authoring、PR observation / merge-preparer などの関連部品があるが、今回の Assurance Contract と current Runbook authority は新設領域。

## 採用済みの大枠判断

- 単一 Issue ではなく、新規 Epic + 複数 Issue を採用する。
- 既存 `epic-00158` へ直接追加しない。理由は、本変更が workflow authority、runtime state、generated instruction surface、review policy、rollout を横断し、既存 Epic の完了境界を肥大化させるため。
- Epic assurance は `strict / deep` として扱う。public CLI、generated state contract、GitHub review write boundary、merge-prepared predicate、installer/provider/dogfooding mirror を横断するため。
- Critical にはしない。最終 merge は人間判断であり、この Epic 自体が production credential、payment、PII を直接処理するわけではないため。

## 初期 Issue 分割理解

- I01: Assurance Contract と classification runtime を導入する。
- I02: `workflow status / next` と fixed Skill kernel を導入し、状態別 Runbook を compile する。
- I03: Profile に応じて design / plan / report の必要 section を安全に合成する。
- I04: step facts から worker、reasoning、context、verification、reviewer routing を含む Step Assurance を compile する。
- I05: PR base SHA に固定された `.github/codex/review-policy.md` から deterministic `@codex review` trigger を生成する。
- I06: P0 / P1 と machine-validated blocker を中心に PR repair / re-review を収束させ、P2 noise で loop しない merge-prepared semantics を導入する。
- I07: shadow、opt-in、new Issue Standard default へ段階 rollout し、legacy compatibility、telemetry、provider/mirror parity を閉じる。

## 次の作業で守ること

- Canonical `requirement.md` / `design.md` / `plan.md` へ反映する前に、保存済み draft を source として読み直す。
- Requirement -> design -> plan の promotion は fresh `spec-reviewer` pass を要求する。discussion draft の保存だけでは promotion ではない。
- Issue 作成時は `issue-slice-handoff-seeds` を Issue-local `draft-requirement` / `draft-design` の入力として使い、canonical Issue docs へ直接貼り付けない。
- Dependency は `.meta.json` を直接編集せず、Issue 作成後に `spec-dock deps add` で設定する。

## 未確定 / 次に確認したい点

- 現 Epic の canonical title は scaffold 作成時の `Dynamic Workflow Resource Allocation` のまま進めるか、draft package 推奨の `Adaptive Assurance And Compiled Agent Workflow` へ変更するか。
- `assurance.json` の保存先を Issue root にするか、`.agent/` generated state とどう分けるか。
- `workflow next` の command surface を Issue planning / execution のみに限定して始めるか、Epic planning / PR delivery まで初期 scope に含めるか。
- Lite profile の自動適用条件をどこまで保守的にするか。
