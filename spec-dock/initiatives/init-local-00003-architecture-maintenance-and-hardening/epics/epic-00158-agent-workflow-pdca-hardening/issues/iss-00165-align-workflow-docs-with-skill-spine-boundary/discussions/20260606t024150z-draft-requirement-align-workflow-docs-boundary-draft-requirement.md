---
種別: draft-requirement
ID: "20260606t024150z-draft-requirement"
タイトル: "Align Workflow Docs Boundary Draft Requirement"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["iss-00165", "epic-00158", "init-local-00003"]
authority: "proposed"
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
intended_targets:
  - spec-dock/active/epic/issues/iss-00165-align-workflow-docs-with-skill-spine-boundary/requirement.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00165 Align Workflow Docs With Skill Spine Boundary — 要件定義ドラフト

## 目的

Workflow / phase / reference docs を、skill-owned workflow spine の詳細参照として再整理し、agent が守るべき mandatory operational workflow が docs にだけ隠れる状態をなくす。

この issue は、skills と hub の authority boundary が見えた後に、docs 側の source-of-truth wording と detailed semantics を整える docs boundary lane である。

## 背景・現状

- 現状の挙動:
  - `workflow_spec_authoring.md`、`workflow_issue.md`、`workflow_epic.md`、`phase_*` docs は詳細 policy と workflow を多く持つ。
  - 一部 skill は docs を source of truth とし、mandatory workflow を docs 側へ委ねる。
- 現状の課題:
  - Docs が詳細 authority と mandatory first action authority を同時に持つと、agent が docs を読まない場合に required workflow を知らない。
  - Skill-owned spine を整えた後も、docs が古い source-of-truth 表現を残すと cross-surface contradiction になる。
  - `workflow_clarification.md` は ADR 01 により bridge/reference 化が必要。
- 観測点:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_*.md`
  - Related references under `src/spec_dock/assets/spec_dock/docs/`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - Skill から詳細 docs へ進む agent / maintainer / reviewer。
- 代表シナリオ:
  - Agent が skill で workflow spine を把握し、docs で artifact semantics / detailed policy / hard cases を確認する。

## スコープ

- 必須:
  - Workflow docs の authority wording を skill spine boundary と整合させる。
  - Docs に残すべき details / meanings / hard cases / phase review criteria を保つ。
  - Skill が所有すべき mandatory first action が docs にだけ存在する箇所を洗い出す。
  - `workflow_clarification.md` を bridge/reference として整える。
  - Docs から対応 skill への routing / relationship を明示する。
- 禁止:
  - Docs から必要な lifecycle policy / field semantics を消さない。
  - Docs を単なる skill の重複 reminder にしない。
  - Runtime policy を新しく変更しない。
  - Templates を compliance authority として扱わない。
- 対象外:
  - Skill rewrite 本体。
  - Template scaffold alignment。
  - Runtime enforcement / validation command。

## 境界

- 常に行う:
  - Docs は meanings/details/source-of-truth for policy detail を担う。
  - Mandatory first-read action は対応 skill に存在することを確認する。
  - Docs 変更は provider-side source から行い、dogfooding mirror で検証する。
- 判断が必要:
  - Docs に残す workflow detail と skill に移す runbook の境目。
  - `workflow_clarification.md` を bridge 以上に薄くするかどうか。
- 行わない:
  - Docs だけを直して skill と矛盾したままにしない。
  - Lifecycle policy を暗黙に変更しない。

## 非交渉制約

- Accepted ADR の責務分担に従う。
- `workflow_clarification.md` は mandatory clarification runbook authority にしない。
- Fresh reviewer pass / non-pass state semantics は docs と skill で矛盾させない。

## 前提

- `iss-00159` と `iss-00163` の skill-owned workflow direction を参照できる。
- `iss-00164` の hub / leaf routing boundary が adopted / completed evidence として確認できる。
- `iss-00164` が未完了の場合、この issue で許されるのは workflow docs の non-authoritative inventory までであり、provider docs wording の変更は行わない。

## 受け入れ条件

- AC-001:
  - アクター: reviewer
  - 前提: workflow docs を確認する
  - 操作: skill/docs authority boundary を確認する
  - 期待結果: docs が mandatory first-read workflow の唯一の置き場になっていない
  - 観測点: docs diff, targeted `rg`
- AC-002:
  - アクター: agent
  - 前提: skill から docs へ進む
  - 操作: artifact semantics / hard cases を調べる
  - 期待結果: docs に詳細情報が残り、skill と矛盾しない
  - 観測点: manual read-through
- AC-003:
  - アクター: maintainer
  - 前提: `workflow_clarification.md` を読む
  - 操作: clarification authority を判断する
  - 期待結果: skill-owned workflow への bridge/reference として読める
  - 観測点: docs diff
- AC-004:
  - アクター: maintainer
  - 前提: docs を変更した
  - 操作: provider/mirror validation を行う
  - 期待結果: provider source と dogfooding mirror の検証が report に残る
  - 観測点: `validate`, `sync`, targeted inspection

## 例外・エッジケース

- EC-001:
  - 条件: Docs の詳細 policy が長く、skill に移すと肥大化する
  - 期待: skill には stop condition / runbook だけ、policy detail は docs に残す
  - 観測点: diff review
- EC-002:
  - 条件: Docs に古い link や source-of-truth 表現が残る
  - 期待: bridge wording または link update を行い、削除は link safety を確認してからにする
  - 観測点: link inventory

## 用語（ドメイン語彙）

- TERM-001:
  - Hidden mandatory workflow: skill にないが docs にだけある、agent が守るべき operational step。
- TERM-002:
  - Detail authority: artifact semantics、policy detail、hard-case criteria の source。
- TERM-003:
  - Bridge doc: skill-owned workflow と detailed references をつなぐ navigation / reference doc。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - Docs は薄くしすぎず、詳細 authority を保持する。Mandatory first action だけを skill へ寄せる。
