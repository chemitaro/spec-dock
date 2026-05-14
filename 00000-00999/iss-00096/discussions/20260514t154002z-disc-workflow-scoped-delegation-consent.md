---
種別: disc
ID: "20260514t154002z-disc"
タイトル: "Workflow Scoped Delegation Consent"
状態: "adopted"
作成者: "iwasawayuuta"
最終更新: "2026-05-15"
親: ["iss-00096"]
関連: ["workflow_spec_authoring.md", "workflow_issue.md", "spec-dock-issue-execution"]
---

# 20260514t154002z-disc Workflow Scoped Delegation Consent

## 議題
- spec-dock の issue workflow で、`requirement -> design -> plan -> implementation` の各 phase gate に必要な reviewer sub-agent を、ユーザーの都度承認なしに orchestrator が自律実行できるようにする。
- Codex host policy を repo 側で上書きせず、ユーザー同意、workflow docs、skills、reviewer gate の責務を分離して、今回のような `spec-reviewer` gate skip を再発させない。

## 背景
- `workflow_spec_authoring.md` は、仕様書作成を `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` と定義している。
- 今回の self-update issue では、`requirement.md` / `design.md` / `plan.md` をまとめて作成し、fresh `spec-reviewer` gate を挟まないまま実装へ進みかけた。
- 直接原因の一つは、Codex host の sub-agent 起動制約と spec-dock の必須 reviewer gate の衝突を、`blocked` ではなく `degraded mode` と誤処理したこと。
- ユーザーの期待は、workflow の途中で毎回承認を求めることではなく、workflow 開始時に限定された同意を与え、その範囲で orchestrator が `spec-reviewer` / `code-reviewer` / `qa-reviewer` / specialist agent を自律起動することである。
- consultant / deep-consultant の分析はいずれも、`workflow-scoped delegation consent` または `issue-scoped workflow consent` を既定にし、reviewer gate は fail-closed に扱うべきという結論で一致した。

## 原則
- Reviewer gate は hard gate:
  - fresh reviewer pass がない phase は次工程へ進めない。
- Degraded mode は必須 gate を満たさない:
  - reviewer unavailable / denied / stale / failed を `degraded success` として扱わない。
- Consent は bounded:
  - 既定は active issue scope。repo-wide standing consent は広すぎるため既定にしない。
- Host policy は上書きしない:
  - repo docs / skills は host tool policy を弱めず、ユーザーの workflow-scoped consent を明示的な実行権限として扱う。
- Safety boundary は分ける:
  - sub-agent 起動の同意は、破壊的操作、外部公開、credentialed access、scope expansion の同意ではない。

## 選択肢
- Option A: phase ごとに毎回ユーザー承認を求める
  - Pros:
    - host policy との衝突が最も少ない。
    - ユーザーが毎回明示的に状況を把握できる。
  - Cons:
    - workflow が interrupt-driven になり、spec-dock の自律実行価値が落ちる。
    - reviewer gate が増えるほど user intervention が増え、実務上の完遂性が下がる。
- Option B: repo-wide standing consent を AGENTS.md / skill に書く
  - Pros:
    - 毎回の承認が不要になる。
    - agent は reviewer gate を自律的に回しやすい。
  - Cons:
    - repo / session / issue をまたいで同意が stale になりやすい。
    - host policy を repo 側で上書きするように見え、安全境界が曖昧になる。
- Option C: issue-scoped workflow delegation consent を導入する
  - Pros:
    - active issue の workflow 完了に必要な reviewer/specialist delegation を一括で許可できる。
    - scope、role、action、expiry を限定でき、監査可能性が高い。
    - host policy を上書きせず、現在のユーザー依頼を delegation の根拠として扱える。
  - Cons:
    - issue start 時に consent state を確認・記録する必要がある。
    - scope expansion や新 role 追加時の再確認ルールが必要。

## 推奨案
- Option C を採用する。
- spec-dock は `issue-scoped workflow delegation consent` を標準モデルとして docs / skills に追加する。
- ユーザーが active issue workflow に対して delegation consent を明示した場合、orchestrator は同じ issue / session / role scope 内で、phase ごとの再確認なしに reviewer/specialist sub-agent を起動してよい。
- reviewer gate は次の状態を区別して report に残す。
  - `passed`: reviewer が実行され、fresh pass を返した。
  - `failed`: reviewer が実行され、blocking finding を返した。
  - `unavailable`: tool / host / agent capability の都合で起動できない。
  - `denied`: consent が得られていない。
  - `waived`: ユーザーが明示的に gate bypass risk を受け入れた。
  - `provisional`: orchestrator self-check はあるが reviewer pass ではない。
- `passed` または明示的な `waived` 以外は、implementation readiness / finish / release / merge の gate として fail-closed に扱う。

## Consent Scope
- 既定 scope:
  - active issue。
  - current repo / current worktree。
  - current session。
  - named reviewer roles: `spec-reviewer`, `code-reviewer`, `qa-reviewer` と、issue plan が必要とする read-only specialist。
- 許可される action:
  - active docs / repo files / diffs / test output の read。
  - findings / pass-fail verdict / risk / correction proposal の返却。
  - report へ記録するための evidence を orchestrator に返すこと。
- 再確認が必要な action:
  - active issue 以外への scope expansion。
  - named role 以外の agent 起動。
  - file write を sub-agent に委譲すること。
  - destructive operation。
  - GitHub comment / PR creation / push / merge など外部可視操作。
  - credentials、browser session、private external system へのアクセス。
- consent expiry:
  - active issue が変わる。
  - issue が finish される。
  - session が終了する。
  - ユーザーが明示的に revoke する。
  - repo / worktree / branch が task scope を変える形で変わる。

## Docs / Skill 修正文言案

```md
### Workflow-scoped delegation consent

At issue start, the orchestrator may obtain one workflow-scoped delegation consent for the active issue.
When this consent is present, the orchestrator may invoke the required reviewer and specialist agents
within the consent scope without asking for per-phase confirmation.

The consent must name the active issue, repository/worktree, allowed agent roles, read/write boundary,
and expiry condition. It does not authorize destructive actions, external publishing, credentialed access,
or scope expansion.
```

```md
### Mandatory reviewer gates

Each issue phase must have a fresh `spec-reviewer` pass before the workflow may advance:

- `requirement` must pass before entering `design`.
- `design` must pass before entering `plan`.
- `plan` must pass before implementation starts.

A reviewer pass is fresh only when it was produced after the latest material change to the corresponding
phase document. Stale, missing, failed, unavailable, or partial reviewer results must block the workflow.
They must not be treated as degraded success.
```

```md
### Degraded mode boundary

Degraded mode may be used only for optional assistance that does not affect required workflow correctness.
Mandatory reviewer gates, dependency checks, active issue guards, implementation readiness checks, and final
quality gates are not degradable.

Self-review by the executing agent may be recorded as provisional evidence, but it does not satisfy
`spec-reviewer`, `code-reviewer`, or `qa-reviewer` completion.
```

## 反映候補
- Provider-side authority:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- Dogfooding mirror / validation target:
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`

## Self-update Issue 再開前の順序
1. この discussion を判断材料として確定する。
2. workflow / skill の正本に、issue-scoped delegation consent と degraded gate semantics を追加する。
3. dogfooding mirror へ同期し、この repo の active workflow でも同じ instruction を参照できるようにする。
4. reviewer gate status の語彙を `passed` / `failed` / `unavailable` / `denied` / `waived` / `provisional` に分ける。
5. その後に self-update issue の requirement gate から再開する。
6. gate が起動できない場合は `blocked` または `provisional` として記録し、`passed` として扱わない。

## 未決事項
- consent state をどこに記録するか。
  - 候補: issue `report.md` の `Workflow Delegation Consent` 節。
  - 将来候補: `.agent/active.json` または dedicated runtime state。ただし v1 は docs/report 記録で十分。
- reviewer pass freshness をどう機械化するか。
  - v1: report に対象 file / phase / reviewer run timestamp / summary を記録。
  - v2: file content hash または git blob hash を reviewer evidence に含める。
- user waiver を許す範囲。
  - v1: finish / release / merge は原則 fail-closed。waiver は explicit risk acceptance として report に記録。
