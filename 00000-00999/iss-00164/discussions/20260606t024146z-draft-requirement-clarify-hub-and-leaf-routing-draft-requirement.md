---
種別: draft-requirement
ID: "20260606t024146z-draft-requirement"
タイトル: "Clarify Hub And Leaf Routing Draft Requirement"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["iss-00164", "epic-00158", "init-local-00003"]
authority: "proposed"
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
intended_targets:
  - spec-dock/active/epic/issues/iss-00164-clarify-hub-and-leaf-skill-routing-surface/requirement.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00164 Clarify Hub And Leaf Skill Routing Surface — 要件定義ドラフト

## 目的

`spec-driven-tdd-workflow` hub skill を router + global invariant surface として整理し、task-specific operational workflow spine は leaf skills が所有する構造へ揃える。

この issue は、issue planning specimen と clarification exception が見えた後に、agent の入口である hub が古い docs-owned workflow 表現を再導入しないようにする。

## 背景・現状

- 現状の挙動:
  - Hub skill は `spec-dock/docs/` を source of truth とし、skills stay concise という表現を持つ。
  - Leaf skills には planning / execution / clarification / delegated authoring の入口がある。
- 現状の課題:
  - Hub が「mandatory workflow は docs にある」と読める場合、leaf skill の first-read workflow spine 方針と衝突する。
  - Hub が leaf skill の責務を説明しすぎると、routing と workflow ownership が混線する。
  - Clarification exception を hub が正しく route しないと、skill-owned clarification workflow が使われない。
- 観測点:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - Leaf skills under `src/spec_dock/assets/install_root/.agents/skills/`
  - Dogfooding mirror `.agents/skills/`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock work の entrypoint として hub skill を読む agent。
- 代表シナリオ:
  - Agent が hub を読んだ時、task type に応じて appropriate leaf skill へ route し、leaf skill が operational workflow spine を所有すると理解する。

## スコープ

- 必須:
  - Hub skill の役割を router + global invariants として明確化する。
  - Leaf skill が task-specific first-read workflow spine を所有することを hub から明示する。
  - `spec-dock-clarification` は skill-owned clarification workflow へ route する。
  - `spec-dock-issue-planning` / `spec-dock-issue-execution` / `spec-dock-epic-planning` / delegated authoring skills の routing boundary を整える。
  - Non-pass reviewer state / canonical ownership / evidence adoption の global invariant は hub に残す。
- 禁止:
  - Leaf skills の詳細 workflow を hub にコピーしない。
  - Hub を compliance authority にしない。
  - Workflow docs の詳細 semantics を hub に移さない。
  - Runtime gate / validation logic を追加しない。
- 対象外:
  - Individual leaf skill rewrite。
  - Templates alignment。
  - `workflow_clarification.md` bridge conversion。

## 境界

- 常に行う:
  - Hub は route selection と global invariant を持つ。
  - Leaf は task-specific runbook と docs routing を持つ。
  - Hub は docs/templates の詳細に誘導できるが、mandatory operational workflow を docs-only と表現しない。
- 判断が必要:
  - Hub に残す global invariant の最小量。
  - Leaf に移すべき wording の範囲。
- 行わない:
  - Hub から issue implementation details を説明しない。
  - Hub で phase promotion を許可したように書かない。

## 非交渉制約

- Fresh `spec-reviewer` pass だけが phase promotion の automatic gate。
- Canonical docs は main orchestrator-owned。
- Sub-agent drafts は evidence であり、leaf skills / report ledger を通じて採用される。

## 前提

- `iss-00159` の specimen outcome が採用済みである。
- `iss-00163` の clarification skill-owned workflow boundary が adopted / completed evidence として確認できる。
- `iss-00163` が未完了の場合、この issue で許されるのは hub surface の non-authoritative inventory までであり、hub routing wording の canonical/provider change は行わない。

## 受け入れ条件

- AC-001:
  - アクター: hub を読む agent
  - 前提: SpecDock task が与えられる
  - 操作: route 先 skill を選ぶ
  - 期待結果: task type に応じて correct leaf skill へ route できる
  - 観測点: hub skill first-read inspection
- AC-002:
  - アクター: reviewer
  - 前提: hub skill diff を確認する
  - 操作: hub と leaf の責務境界を確認する
  - 期待結果: hub は router + global invariant、leaf は workflow spine という境界が読める
  - 観測点: diff
- AC-003:
  - アクター: agent
  - 前提: ambiguous requirement / clarification task がある
  - 操作: hub から route する
  - 期待結果: `spec-dock-clarification` の skill-owned workflow へ route する
  - 観測点: hub wording
- AC-004:
  - アクター: maintainer
  - 前提: provider source を変更する
  - 操作: dogfooding mirror を確認する
  - 期待結果: provider/mirror relationship が report に残る
  - 観測点: `validate`, `sync`, targeted inspection

## 例外・エッジケース

- EC-001:
  - 条件: Hub に global invariant を残しすぎて leaf と重複する
  - 期待: Phase gate / canonical ownership などの cross-cutting invariant だけを hub に残す
  - 観測点: review finding
- EC-002:
  - 条件: Leaf skill が未整備で route 先が不安定
  - 期待: 先行 issue の completion / draft state を確認し、不安定なら blocking dependency として扱う
  - 観測点: issue dependency

## 用語（ドメイン語彙）

- TERM-001:
  - Hub skill: SpecDock work の入口で route selection と global invariant を担う skill。
- TERM-002:
  - Leaf skill: task-specific workflow spine と docs routing を担う skill。
- TERM-003:
  - Global invariant: どの route でも破ってはいけない phase gate / authority / evidence rule。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - Hub は route + global invariant に留め、leaf detail は各 leaf issue へ送る。
