---
種別: disc
ID: "20260529t000926z-disc"
タイトル: "Issue planning execution skill split scope memo"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00138"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260529t000926z-disc Issue planning execution skill split scope memo

## ユーザー入力
- 現在の `spec-dock-issue-execution` skill は、issue の要件定義、設計、計画、実装を一つの skill に含めている。
- Initiative / Epic には planning 専用 skill があるため、Issue も抽象度を揃えて planning と execution を分けたい。
- 直近で作成した、ユーザーと深い discussion を行う `spec-dock-clarification` 系 workflow / skill と、Issue planning skill を組み合わせることで、ユーザーと深く議論しながら `requirement.md` / `design.md` / `plan.md` を作れるようにしたい。
- その planning 成果物をもとに、別途 Issue execution skill で実装を依頼できるようにしたい。
- 必要に応じて `spec-dock-issue-planning` と `spec-dock-issue-execution` の両方を指定し、簡単な要件だけから半自動で planning から execution へ進める余地も残したい。
- 今回は要件定義書をまだ作らず、discussion メモに意図とやることを残す。

## 対象 scope
- 親 epic:
  - `epic-00112 Delegated Authoring Architecture for Spec Workflow`
- 新規 issue:
  - `iss-00138 Split Issue Planning and Execution Skills`
- 主な対象 asset:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - 新規候補: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - provider docs and dogfooding parity under `spec-dock/docs/` / `.agents/skills/`

## やりたいこと
- Issue planning skill を新設する。
  - Issue の `requirement.md` / `design.md` / `plan.md` 作成・改善・レビュー準備を担当する。
  - Initiative planning / Epic planning と同じ抽象度の leaf skill として扱う。
  - `spec-dock-clarification` と組み合わせ、ユーザーとの深い discussion を planning の入口として扱えるようにする。
- Issue execution skill を実装専用へ整理する。
  - `requirement.md` / `design.md` / `plan.md` が実装可能な状態にあることを前提に、実装・検証・report 更新・handoff readiness を担当する。
  - execution 中に requirement / design / plan gap を見つけた場合は、planning / clarification へ戻す。
- Hub / router skill の導線を整理する。
  - `spec-driven-tdd-workflow` が Initiative / Epic / Issue planning / Issue execution / clarification を適切に案内できるようにする。
  - planning と execution の両方を指定された場合に、簡単な要件から planning を行い、その成果を execution に渡す流れを表現できるようにする。

## 既存の整合性メモ
- すでに存在する planning skill:
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
- すでに存在する issue skill:
  - `spec-dock-issue-execution`
- 現状の不整合:
  - issue だけが planning と execution を一つの skill に寄せており、Initiative / Epic と抽象度が揃っていない。
  - `spec-dock-clarification` が first-class workflow になったことで、issue planning は clarification と組み合わせる独立 role として扱う方が自然になっている。

## 実装前に確認したい論点
- `spec-dock-issue-planning` の責務:
  - canonical docs を直接編集する skill なのか、orchestrator 向けの workflow reminder なのか。
  - `spec-dock-clarification` を必須にするのか、必要時に組み合わせる optional companion にするのか。
- `spec-dock-issue-execution` の縮小範囲:
  - 現在含んでいる planning guidance をどこまで削るか。
  - execution skill から planning phase へ戻す stop condition をどう明記するか。
- Hub skill の振り分け:
  - ユーザーが「issue を進めて」とだけ言った場合、planning から始めるのか、active issue の doc 状態で自動判定するのか。
  - planning + execution を同時指定した場合の sequencing と gate をどう表現するか。
- Shipped asset parity:
  - provider-side `install_root` を正本として更新し、dogfooding `.agents/skills` 側へどう反映・検証するか。
  - init/update tests で新規 skill asset を確認する必要があるか。

## 最初の成功条件案
- `spec-dock-issue-planning` skill が provider-side install assets に追加される。
- `spec-dock-issue-execution` skill が実装フェーズ中心の説明へ整理される。
- `spec-driven-tdd-workflow` や docs の skill 一覧が Issue planning / Issue execution の分離を示す。
- `spec-dock-clarification` との組み合わせ方が、skill または docs で明確になる。
- dogfooding workspace でも `.agents/skills/spec-dock-issue-planning/SKILL.md` が確認できる。
- `spec-dock validate` と、必要な init/update asset tests が通る。

## この issue ではまだ決めないこと
- canonical `requirement.md` / `design.md` / `plan.md` への正式反映。
- Issue planning skill がどの程度 canonical docs を直接書くか。
- planning + execution の完全自動化をどこまで許容するか。
- Permission profile や sub-agent callability の追加実装を同時に扱うか。

## 次アクション
- 既存の `spec-dock-issue-execution`、Initiative / Epic planning skill、`spec-dock-clarification`、hub skill を読み比べる。
- Issue planning / Issue execution の責務境界を小さく設計する。
- 必要なら、このメモをもとに `requirement.md` / `design.md` / `plan.md` へ正式化する。
