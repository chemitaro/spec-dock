---
種別: 要件定義書（Issue）
ID: "iss-00165"
タイトル: "Align Workflow Docs With Skill Spine Boundary"
関連GitHub: ["#165"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["epic-00158", "init-local-00003"]
---

# iss-00165 Align Workflow Docs With Skill Spine Boundary — 要件定義

## 目的

Workflow / phase / authoring / entry docs を、skill-owned workflow spine の詳細参照として再整理し、agent が守るべき mandatory operational workflow が docs にだけ隠れる状態を減らす。

この issue は、`iss-00163` の clarification skill-owned workflow と `iss-00164` の hub / leaf routing surface 完了後に、docs 側の authority wording、bridge wording、detail semantics を整える T3 docs boundary lane である。

## 背景・現状

- 現状の挙動:
  - `workflow_spec_authoring.md` は requirement -> design -> plan の phase promotion、fresh `spec-reviewer` gate、delegated draft evidence、discussion write gate を詳しく説明している。
  - `workflow_issue.md` は issue lifecycle、execution contract、delegation/reviewer/completion policy、report evidence requirements を詳しく説明している。
  - `workflow_clarification.md` はすでに `spec-dock-clarification` skill-owned workflow の bridge/reference に寄っているが、docs entrypoints には古い source-of-truth 表現が残り得る。
  - `docs/README.md` / `guide.md` は docs reading order と高頻度ルールの入口として使われる。
- 現状の課題:
  - Docs が詳細 authority と mandatory first action authority を同時に持つように読めると、skill spine 方針と矛盾する。
  - Skill 側で first-read workflow spine を整えても、docs 側に古い source-of-truth / mandatory runbook wording が残ると cross-surface contradiction になる。
  - Docs を薄くしすぎると、field semantics、hard cases、lifecycle policy、report evidence semantics が失われる。
- 観測点:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - Dogfooding mirror under `spec-dock/docs/`
- 情報源:
  - Epic requirement / design / plan。
  - Accepted ADRs under `epic-00158/discussions/20260605t080509z-*.md`。
  - `iss-00162` context surface inventory。
  - `iss-00163` and `iss-00164` completion evidence。
  - Draft requirement discussion `20260606t024150z-draft-requirement-align-workflow-docs-boundary-draft-requirement.md`。

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - Skill から detailed docs へ進む agent。
  - Workflow docs を参照して artifact semantics / lifecycle policy / hard cases を確認する maintainer / reviewer。
- 代表シナリオ:
  - Agent が skill で next action / stop condition / reviewer gate を把握し、docs で field meanings、policy details、hard-case criteria、report evidence semantics を確認する。

## スコープ

- 必須:
  - Workflow / phase / authoring / entry docs の authority wording を skill spine boundary と整合させる。
  - Docs に残すべき detail semantics、policy details、hard cases、field meanings、review criteria を保つ。
  - Docs が mandatory first-read workflow の唯一の置き場だと読める表現を bridge/reference wording に直す。
  - `workflow_clarification.md` と docs entrypoints を、`spec-dock-clarification` skill-owned workflow の bridge/reference として整合させる。
  - Docs から対応 skill への relationship / entrypoint を明示する。
  - Provider-side docs source と dogfooding mirror の validation / sync / targeted inspection evidence を残す。
- 禁止:
  - Docs から lifecycle policy、field semantics、hard-case criteria を削って空洞化しない。
  - Docs を skill の重複 reminder だけにしない。
  - Skill rewrite、template scaffold alignment、runtime enforcement、validation command logic をこの issue に吸収しない。
  - `workflow_clarification.md` を mandatory clarification runbook authority に戻さない。
  - Templates を compliance authority として扱わない。
- 対象外:
  - Individual leaf skill rewrite。
  - Templates alignment (`iss-00166`)。
  - Runtime gate / CLI enforcement / regression harness。
  - Full retirement of `workflow_clarification.md` link surface beyond safe bridge/reference wording。

## 境界

- 常に行う:
  - Docs は detail authority として残す。
  - Mandatory first-read action / stop condition / reviewer gate は対応 skill に存在することを確認する。
  - Docs 変更は provider-side source から行い、dogfooding mirror は validation target とする。
  - Evidence / delegated output / discussion を canonical authority と混同しない wording を維持する。
- 判断が必要:
  - Docs に残す workflow detail と skill に寄せる first-read runbook の境目。
  - `workflow_clarification.md` は bridge/reference としてどの程度説明を残すか。
  - Entry docs (`README.md`, `guide.md`) に skill-first routing をどの粒度で書くか。
- 行わない:
  - Docs だけを直して skill と矛盾したままにしない。
  - Lifecycle policy を暗黙に変更しない。
  - Later harness / runtime guard を first-wave blocker にしない。

## 非交渉制約

- Accepted ADR の responsibility split に従う。
- Skills own first-read operational workflow spine。
- Docs own detailed semantics / policy detail / hard cases。
- Templates own scaffolds / evidence slots / examples, not compliance authority。
- Fresh reviewer pass / non-pass state semantics は docs と skill で矛盾させない。
- Canonical docs remain main-orchestrator-owned; delegated / external outputs remain evidence until adopted in `report.md`。
- `iss-00163` and `iss-00164` must be completed before provider docs wording changes.

## 前提

- `iss-00159` completed the issue-planning specimen direction.
- `iss-00163` completed clarification skill-owned workflow / bridge direction.
- `iss-00164` completed hub / leaf routing and global invariant surface.
- `iss-00162` inventory provides handoff rows for workflow docs boundary alignment.

## 受け入れ条件

- AC-001:
  - アクター: reviewer
  - 前提: workflow / phase / authoring / entry docs を確認する
  - 操作: skill/docs authority boundary を確認する
  - 期待結果: docs が mandatory first-read workflow の唯一の置き場になっていない
  - 観測点: provider docs diff, targeted `rg`, spec-reviewer evidence
- AC-002:
  - アクター: agent
  - 前提: skill から docs へ進む
  - 操作: artifact semantics / hard cases / detailed policy を調べる
  - 期待結果: docs に詳細情報が残り、skill と矛盾しない
  - 観測点: manual read-through / targeted inspection
- AC-003:
  - アクター: maintainer
  - 前提: `workflow_clarification.md` と docs entrypoints を読む
  - 操作: clarification authority を判断する
  - 期待結果: `spec-dock-clarification` skill-owned workflow への bridge/reference として読める
  - 観測点: docs diff, targeted `rg`
- AC-004:
  - アクター: maintainer
  - 前提: docs を変更した
  - 操作: provider source と dogfooding mirror を検証する
  - 期待結果: provider source と dogfooding mirror の整合証跡が `report.md` に残る
  - 観測点: `sync`, `validate`, `git diff --check`, targeted mirror inspection
- AC-005:
  - アクター: reviewer
  - 前提: workflow docs boundary alignment の最終 diff を確認する
  - 操作: templates / runtime / skills へ scope が拡大していないか確認する
  - 期待結果: docs boundary alignment に閉じ、後続 `iss-00166` や later guard work を吸収していない
  - 観測点: `git diff --name-only`, report decision ledger

## 例外・エッジケース

- EC-001:
  - 条件: Docs の詳細 policy が長く、skill に移すと skill bloat になる
  - 期待: skill には stop condition / runbook spine、policy detail は docs に残す
  - 観測点: diff review
- EC-002:
  - 条件: Docs に古い link や source-of-truth 表現が残る
  - 期待: bridge wording または link update を行い、削除は link safety を確認してからにする
  - 観測点: link / wording inspection
- EC-003:
  - 条件: Docs にしか存在しない mandatory first action が見つかる
  - 期待: この issue で docs wording を bridge 化し、skill rewrite が必要なら scope absorption せず follow-up / prior owner issue へ記録する
  - 観測点: report decision ledger

## 用語

- Hidden mandatory workflow:
  - Skill にないが docs にだけある、agent が守るべき operational step。
- Detail authority:
  - Artifact semantics、policy detail、hard-case criteria、field meanings の source。
- Bridge doc:
  - Skill-owned workflow と detailed references をつなぐ navigation / reference doc。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - Docs は薄くしすぎず、詳細 authority を保持する。Mandatory first action / stop condition / reviewer gate だけを skill-first wording に寄せる。
