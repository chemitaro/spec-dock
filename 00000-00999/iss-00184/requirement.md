---
種別: 要件定義書（Issue）
ID: "iss-00184"
タイトル: "Rename Spec Dock Hub Skill"
関連GitHub: ["#184"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["epic-00158", "init-local-00003"]
---

# iss-00184 Rename Spec Dock Hub Skill — 要件定義

## 目的

`spec-driven-tdd-workflow` という hub skill 名が、SpecDock 全体の入口・統括ルール・route selector であることを十分に伝えられていないため、名前と関連 surface を見直す。

この issue では、hub skill が「SpecDock work の全体ルールを統括し、leaf skill へ route する入口」であることが、skill 名、説明、参照、dogfooding mirror から一貫して読める状態を目指す。

## 背景・現状

- 現状:
  - `spec-driven-tdd-workflow` skill は、SpecDock work の entry / routing skill として使われている。
  - skill 本文の見出しには `Spec-driven TDD Workflow (Hub)` とあり、hub であることは本文を読むと分かる。
  - ただし skill 名と path は `spec-driven-tdd-workflow` であり、利用者が一覧や routing surface から見たときに「SpecDock の hub skill」と直感しにくい。
- 課題:
  - `TDD workflow` という名前が、SpecDock 全体の route selector / global invariant surface という役割よりも、実装手法や TDD 手順だけを想起させる。
  - hub skill の rename / alias / compatibility 方針を決めないまま直接変更すると、既存参照、installed asset、dogfooding mirror、docs、skills list、tests がずれる可能性がある。
  - `spec-dock-hub` などの候補はあり得るが、最終名は design phase で候補比較と互換性を確認して決める必要がある。
- 観測点:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - skills list / skill descriptions that expose this skill to Codex
  - docs, tests, templates, and runtime references that mention `spec-driven-tdd-workflow`
  - local dogfooding mirror and generated projections under `spec-dock/`
- 情報源:
  - user request on 2026-06-12: hub skill name is hard to understand and should communicate that it governs SpecDock-wide rules.
  - Parent Epic `epic-00158 Agent Workflow PDCA Hardening`.
  - Completed `iss-00164 Clarify Hub And Leaf Skill Routing Surface`, which already clarified the hub/leaf responsibility boundary but did not rename the skill.

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock work の入口 skill を探す coding agent。
  - SpecDock の agent-facing workflow / skill set を保守する maintainer。
- 代表シナリオ:
  - Agent が available skills / local skill directory / hub skill description を見たとき、SpecDock 全体の入口として読むべき skill を迷わず選べる。
  - Maintainer が hub / leaf skill family を保守するとき、hub の名称と役割が一致しており、leaf skill 名と混同しない。

## スコープ

- 必須:
  - Hub skill の新名称または互換 alias 方針を設計する。
  - `spec-driven-tdd-workflow` から新しい hub name へ移す場合の参照影響を inventory する。
  - Provider-side installed skill asset と dogfooding mirror の扱いを決める。
  - README / docs / tests / skill references / generated surfaces のうち、名称変更で必要な箇所を洗い出す。
  - 変更後に `spec-dock` の hub skill であることが、名前と description から読めることを確認する。
- 禁止:
  - Hub の責務を広げて leaf skill の workflow spine を吸収しない。
  - `iss-00164` で定めた hub = route selector + global invariant、leaf = task-specific workflow spine の境界を崩さない。
  - Runtime guard、validation logic、workflow enforcement をこの issue の主目的にしない。
  - 互換性確認なしに旧 skill path / references を削除しない。
- 対象外:
  - Individual leaf skill の rename。
  - Issue planning / execution / clarification workflow の再設計。
  - Template authority / docs boundary の横断再整理。
  - SpecDock product feature expansion。

## 境界

- 常に行う:
  - Provider-side `src/spec_dock/assets/install_root/.agents/skills/` を shipped skill source of truth として扱う。
  - `.agents/skills/` は dogfooding mirror / verification target として扱う。
  - 旧名 `spec-driven-tdd-workflow` の参照を `rg` で inventory してから rename / alias / staged migration を判断する。
  - 新しい名前は、SpecDock の hub / route selector / global invariant surface であることを伝える。
- 判断が必要:
  - 新しい canonical skill name を `spec-dock-hub`、`spec-dock-workflow-hub`、`spec-dock-governance-hub` などのどれにするか。
  - 旧名を compatibility alias / forwarding skill / docs-only reference として残すか、同一 issue で完全移行するか。
  - skill discovery surface における description をどの程度変えるか。
- 行わない:
  - 名前だけでなく workflow 内容そのものを再設計する。
  - 既存参照の破壊的削除を、利用箇所確認なしに行う。
  - GitHub issue title と local spec title だけを変えて完了扱いにする。

## 非交渉制約

- `iss-00164` の hub/leaf boundary を維持する。
- Shipped asset 変更は provider-side source を authority とする。
- Dogfooding mirror は provider と整合していることを検証する。
- Fresh reviewer gate なしに design / plan / execution handoff へ進んだと主張しない。
- 名前変更が reference / tests / generated asset に与える影響を、少なくとも repository search で確認する。

## 前提

- `iss-00164` は `done` であり、hub skill の役割自体は整理済みである。
- この issue は、その役割を名前と周辺参照からも分かるようにする後続 issue である。

## 受け入れ条件

- AC-001:
  - アクター: SpecDock skill を探す agent
  - 前提: available skills または skill directory に hub skill が表示される
  - 操作: SpecDock work の入口として読む skill を選ぶ
  - 期待結果: skill name / description から、SpecDock 全体の hub / route selector / global invariant surface であることを判断できる
  - 観測点: provider-side skill metadata, `SKILL.md`, dogfooding mirror
- AC-002:
  - アクター: maintainer
  - 前提: 旧名 `spec-driven-tdd-workflow` の参照が存在する可能性がある
  - 操作: repository search で参照を確認し、rename / alias / staged migration の方針を決める
  - 期待結果: 参照影響が inventory され、互換性方針が design / plan / report に残る
  - 観測点: `rg`, design decision, report ledger
- AC-003:
  - アクター: reviewer
  - 前提: rename / alias 方針に基づく diff を確認する
  - 操作: hub/leaf responsibility boundary を確認する
  - 期待結果: hub は route selector + global invariant surface に留まり、leaf skill の workflow spine を吸収していない
  - 観測点: changed skill files and `iss-00164` requirement/design alignment
- AC-004:
  - アクター: maintainer
  - 前提: provider-side skill asset を変更する
  - 操作: dogfooding mirror と generated projections を検証する
  - 期待結果: provider/mirror relationship と必要な sync / validate evidence が report に残る
  - 観測点: `cmp` or equivalent parity check, `./spec-dock/scripts/spec-dock sync`, `./spec-dock/scripts/spec-dock validate`
- AC-005:
  - アクター: future agent
  - 前提: 旧名または新名のどちらかを参照する古い文脈がある
  - 操作: repository docs / skill references を読む
  - 期待結果: 旧名から新名への関係または移行理由が追跡でき、入口 skill を見失わない
  - 観測点: compatibility note, alias / reference update, or explicit migration record

## 例外・エッジケース

- EC-001:
  - 条件: 新名称に変更すると skill discovery / runtime / tests が旧 path に依存して壊れる
  - 期待: 互換 alias、staged migration、または旧 path 維持 + metadata/title 改善を選び、破壊的変更を避ける
  - 観測点: design decision and verification evidence
- EC-002:
  - 条件: `spec-dock-hub` という名前だけでは governance / workflow invariant の意味が弱い
  - 期待: 候補比較で名前と description の組み合わせを選び、description 側で不足する意味を補う
  - 観測点: design alternatives
- EC-003:
  - 条件: 旧名の reference が generated / historical artifact にだけ残る
  - 期待: 実行時影響がないものは無理に rewrite せず、必要なら report に non-blocking rationale を残す
  - 観測点: reference inventory

## 用語（ドメイン語彙）

- TERM-001:
  - Hub skill: SpecDock work の入口として、route selection と global invariant を担う skill。
- TERM-002:
  - Leaf skill: Issue planning、issue execution、clarification など、task-specific workflow spine を担う skill。
- TERM-003:
  - Compatibility alias: 旧 skill name / path から新 hub skill へ利用者を迷わせず移行させるための互換 surface。

## 未確定事項

- Q-001:
  - 質問: canonical な新 skill name は何にするか。
  - 候補:
    - `spec-dock-hub`: 短く、hub であることが最も明確。
    - `spec-dock-workflow-hub`: workflow routing の入口であることを補える。
    - `spec-dock-governance-hub`: global invariant / governance を強調できるが少し硬い。
    - 旧名維持 + title / description 改善: 互換性リスクは低いが、名前の分かりにくさは残りやすい。
  - 推奨案:
    - design phase で repository references と skill discovery behavior を確認してから決める。
  - 影響範囲:
    - skill directory path, skill metadata, docs references, tests, dogfooding mirror, generated projections.
