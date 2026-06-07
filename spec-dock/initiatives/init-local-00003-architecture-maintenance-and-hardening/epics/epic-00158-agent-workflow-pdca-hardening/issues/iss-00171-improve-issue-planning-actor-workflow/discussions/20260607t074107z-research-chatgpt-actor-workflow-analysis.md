---
種別: research
ID: "20260607t074107z-research"
タイトル: "ChatGPT Actor Workflow Analysis"
状態: "completed"
作成者: "codex"
最終更新: "2026-06-07"
親: ["iss-00171", "epic-00158"]
関連:
  - "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a251a1b-5fcc-83a9-91c5-ed97c3874978"
authority: "evidence"
adoption_status: "adopted"
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# ChatGPT Actor Workflow Analysis

## 位置づけ

この文書は、`spec-dock-issue-planning` skill を実運用した結果、`system-architect` による設計ドラフトと `implementation-planner` による実装計画ドラフトが作成されなかった問題について、ChatGPT 5.5 Pro / じっくり思考 Pro に分析を依頼した結果を issue-local research として整理したものである。

Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の authority ではない。採用する内容は main orchestrator が Evidence Adoption Ledger に記録した上で canonical artifact へ再記述する。

## 調査目的

- 現行 `spec-dock-issue-planning/SKILL.md` が、なぜ `system-architect` / `implementation-planner` draft を実行ステップとして誘導できなかったのかを分析する。
- 親 skill にどの程度 actor / sequence / adoption / failure mode を書くべきかを整理する。
- Epic の方針である「skills = first-read workflow spine、docs = detailed semantics、templates = scaffolds/examples」を崩さずに、モデルが従える workflow 修正案を得る。

## ChatGPT へ渡した主な context

- 現行 `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` 全文。
- `spec-dock-system-architect/SKILL.md` の delegated design draft contract。
- `spec-dock-implementation-planner/SKILL.md` の delegated plan draft contract。
- `workflow_spec_authoring.md` の authority boundary / delegated evidence / authoring lifecycle 要点。
- `workflow_issue.md` の issue planning / discussions catalog / delegation consent / report evidence 要点。
- `phase_plan_issue.md` の issue plan entry focus / review gate / delegated plan draft 要点。

## ChatGPT の主結論

ChatGPT は、現行 `spec-dock-issue-planning/SKILL.md` を「レビュー付き phase order」ではあるが「actor-based authoring workflow spine」ではない、と評価した。

現行 skill は `requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff` を明示しているが、次が workflow 本体にない。

- `system-architect` をいつ呼ぶか。
- `system-architect` に何を作らせるか。
- `implementation-planner` をいつ呼ぶか。
- `implementation-planner` に何を作らせるか。
- main orchestrator が draft をどう handoff review / diff guard / adoption / canonical integration するか。
- gap が出た時にどの prior phase / clarification へ戻すか。

その結果、モデルは delegated draft を「任意の補助 evidence」または「存在した場合の扱い」と解釈し、draft 作成を実行ステップとして認識しにくい。

## 根本原因

### 1. phase graph であり task graph ではない

現行 workflow は artifact の昇格順序としては正しいが、各 phase の actor、delegation、draft artifact、handoff、adoption、gap routing が書かれていない。

そのため `design` は main orchestrator が直接 `design.md` を作る phase に読め、`plan` も main orchestrator が直接 `plan.md` を作る phase に読める。

### 2. delegated draft の trigger が親 workflow にない

`system-architect` と `implementation-planner` の skill は、どちらも「main orchestrator が依頼した時に使う」契約になっている。一方で親の `spec-dock-issue-planning` は「ここで依頼する」と書いていない。

この非対称性が、draft proposal が作成されなかった直接原因である。

### 3. Authority と Workflow が分離されすぎている

現行 skill は、canonical docs は main orchestrator owned、delegated draft は evidence only、fresh reviewer pass は必須、という authority boundary は明確である。

しかし、それが `Authority And Routing` に隔離され、workflow の実行 sequence に接続されていない。モデルに必要なのは次の動詞列である。

1. design phase に入ったら system-architect に draft を依頼する。
2. draft が返ったら main orchestrator が diff guard / handoff review を行う。
3. main orchestrator が採用 / 不採用を report に記録する。
4. 採用した evidence だけを canonical `design.md` に統合する。
5. その後に fresh `spec-reviewer` pass を走らせる。

Plan phase でも同様に `implementation-planner` についてこの動詞列が必要である。

### 4. `Leaf skill` description が実体と合わない

現行 front matter の `Leaf skill for issue requirement, design, and plan planning tasks in spec-dock` という description は、実際には issue planning の operational entrypoint / first-read spine である役割とずれている。sub-agent を呼ばず leaf として閉じるべきという誤誘導になり得る。

ChatGPT は、`Operational workflow spine for issue-level requirement, delegated design/plan draft adoption, review-gated planning, and execution handoff in spec-dock.` のような description を推奨した。

### 5. `draft-design` / `draft-plan` kind の扱いに衝突がある

`workflow_issue.md` の discussions catalog には `draft-design` / `draft-plan` が存在する。一方で `system-architect` / `implementation-planner` は「既存 kind such as research/disc/adr を使い、新 kind を導入しない」としている。

最小修正では親 skill に `Discussion Draft Path Compatibility` を置き、現行 repo の canonical discussions path rule に従うこと、unsupported kind を delegated role が勝手に作らないことを明示するのが安全である。

## 推奨 workflow rewrite

### 基本方針

`spec-dock-issue-planning/SKILL.md` には、reference doc の詳細 schema をコピーせず、first-read spine として最低限の operational sequence を置く。

Skill に置く粒度は次の 6 要素までに抑える。

- phase precondition
- actor
- delegated request / canonical authoring action
- output artifact
- review / diff guard / adoption gate
- gap routing / stop condition

詳細な field semantics、plan schema、phase checklist は引き続き `workflow_issue.md`、`workflow_spec_authoring.md`、`phase_plan_issue.md`、`authoring/issue-plan.md` に残す。

### 推奨順序

1. main orchestrator が canonical `requirement.md` を作る。
2. `requirement.md` に fresh `spec-reviewer` pass を得る。
3. main orchestrator が `system-architect` に scope-local draft design proposal を原則依頼する。
4. main orchestrator が post-run diff guard / handoff review を行う。
5. main orchestrator が draft findings の採用 / 部分採用 / 棄却 / stale / superseded を `report.md` に記録する。
6. 採用した evidence だけを canonical `design.md` に統合する。
7. canonical `design.md` に fresh `spec-reviewer` pass を得る。
8. main orchestrator が `implementation-planner` に scope-local draft plan proposal を原則依頼する。
9. main orchestrator が post-run diff guard / handoff review を行う。
10. main orchestrator が draft findings の採用判断を `report.md` に記録する。
11. 採用した evidence だけを canonical `plan.md` に統合する。
12. canonical `plan.md` に fresh `spec-reviewer` pass を得る。
13. executable plan であることを確認して execution handoff する。

## 推奨 section outline

ChatGPT は次の section 構成を推奨した。

- `Purpose And References`
- `Actor Model And Canonical Authority`
- `Mandatory Actor-Based Issue Authoring Workflow`
- `Delegated Draft Invocation Contract`
- `Draft Adoption And Report Evidence`
- `Gap Routing And Stop Conditions`
- `Execution Handoff Gate`
- `Authority And Routing`
- `Discussion Draft Path Compatibility`

## 推奨 bullet の要点

### Design phase

- Preconditions: canonical `requirement.md` exists and has a fresh `spec-reviewer` pass after its latest substantive change.
- Default path: main orchestrator requests a `system-architect` delegated architecture analysis / draft design proposal before authoring canonical `design.md`.
- The request must specify target node/scope, role, source requirement path and revision, reviewer pass evidence, allowed discussions path rule, forbidden paths/actions, expected output, leaf evidence permission, stop/invalidation conditions, and report ledger destination.
- `system-architect` output is one new flat Markdown discussion draft under target scope `discussions/`.
- Main orchestrator performs handoff review and post-run diff guard before adoption.
- Main orchestrator adopts only verified evidence and integrates it into canonical `design.md`.
- Run fresh `spec-reviewer` on canonical `design.md`.

### Plan phase

- Preconditions: canonical `requirement.md` and `design.md` both have fresh `spec-reviewer` pass.
- Default path: main orchestrator requests an `implementation-planner` delegated implementation planning analysis / draft plan proposal before authoring canonical `plan.md`.
- The request must specify source requirement/design revisions and reviewer pass evidence.
- `implementation-planner` output is one new flat Markdown discussion draft under target scope `discussions/`.
- Missing/stale/contradictory/insufficient design evidence is a blocker and routes back to design authoring or clarification.
- Main orchestrator performs handoff review, diff guard, adoption, and canonical integration.
- Run fresh `spec-reviewer` on canonical `plan.md`.

## Guardrails

- Delegated draft should be default path, not absolute prerequisite in every case.
- Role unavailable, runtime unsupported, consent missing, denied, or trivial/manual path may use fallback, but `report.md` must record skip/blocker and reviewer gates must not be weakened.
- Draft existence is not pass.
- Handoff review is not pass.
- Adoption is not pass.
- Canonical artifact after integration must receive fresh `spec-reviewer` pass.
- Diff guard should confirm that only allowed discussion evidence was created and record the result in `report.md`.
- `draft-design` / `draft-plan` kind should not be hard-coded until subordinate skill / docs policy is aligned.

## 最小 patch 方針

1. Provider-side source of truth を更新する。
   - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
2. Dogfooding mirror を同期する。
   - `.agents/skills/spec-dock-issue-planning/SKILL.md`
3. 最小変更範囲は description、`Mandatory Issue Authoring Workflow`、`Authority And Routing` の置換。
4. 必要なら `Discussion Draft Path Compatibility` を追加する。
5. `system-architect` / `implementation-planner` skill の kind policy 調整は follow-up にできるが、今回の修正で明らかに矛盾が残る場合は補正対象にする。

## 推奨検証

- Provider-side source と dogfooding mirror の exact match。
- `system-architect` と `implementation-planner` が authority section だけでなく workflow 本体の design / plan phase に登場すること。
- `diff guard`、`adoption`、`fresh spec-reviewer`、`unavailable` が skill 本体に明示されること。
- Dogfooding dry-run scenario:
  - happy path: requirement pass 後に design phase で `system-architect` draft request が計画される。
  - plan happy path: design pass 後に `implementation-planner` draft request が計画される。
  - role unavailable fallback: skip/blocker が report に記録され、reviewer gate は緩まない。
  - stale source blocker: draft が stale/source-mismatched として not adopted になる。
  - forbidden write / diff guard failure: adoption が拒否される。
  - reviewer fail: draft 存在で reviewer fail を上書きしない。
  - gap routing: requirement gap / design gap が prior phase へ戻る。

## 未検証事項

- ChatGPT は supplied context のみで分析しており、実 repo の全文、test suite、multi-agent runtime の実際の呼び出し API、failure object、既存 lint/doc validation は確認していない。
- この research を実装へ採用する場合は、Codex 側で provider/mirror diff、grep/static check、SpecDock validate/sync、dogfooding scenario を実行する必要がある。
