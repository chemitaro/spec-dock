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

`spec-driven-tdd-workflow` という hub skill 名が、SpecDock 全体の入口・統括ルール・route selector であることを十分に伝えられていないため、canonical skill name と関連 surface を刷新する。

この issue では、旧 `spec-driven-tdd-workflow` を実行時 / discovery / docs の現行 surface から退役し、hub skill が「SpecDock work の全体ルールを統括し、leaf skill へ route する入口」であることが、新しい skill 名、説明、参照、dogfooding mirror から一貫して読める状態へ完全移行する。

## 背景・現状

- 現状:
  - `spec-driven-tdd-workflow` skill は、SpecDock work の entry / routing skill として使われている。
  - skill 本文の見出しには `Spec-driven TDD Workflow (Hub)` とあり、hub であることは本文を読むと分かる。
  - ただし skill 名と path は `spec-driven-tdd-workflow` であり、利用者が一覧や routing surface から見たときに「SpecDock の hub skill」と直感しにくい。
- 課題:
  - `TDD workflow` という名前が、SpecDock 全体の route selector / global invariant surface という役割よりも、実装手法や TDD 手順だけを想起させる。
  - hub skill の canonical rename 方針を決めないまま直接変更すると、既存参照、installed asset、dogfooding mirror、docs、skills list、tests がずれる可能性がある。
  - ユーザー確認により、中途半端な互換入口は残さず、新しい名前へ統合的に移行する方針が採用済みである。
  - ユーザー確認により、新しい canonical skill name は `spec-dock-hub` とする。
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
  - Research `discussions/20260612t072453z-research-spec-dock-hub-rename-surface-inventory.md`, which classifies current surfaces, tests, dogfooding mirror, and historical evidence.

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock work の入口 skill を探す coding agent。
  - SpecDock の agent-facing workflow / skill set を保守する maintainer。
- 代表シナリオ:
  - Agent が available skills / local skill directory / hub skill description を見たとき、SpecDock 全体の入口として読むべき skill を迷わず選べる。
  - Maintainer が hub / leaf skill family を保守するとき、hub の名称と役割が一致しており、leaf skill 名と混同しない。

## スコープ

- 必須:
  - Hub skill の新しい canonical name を `spec-dock-hub` とする。
  - `spec-driven-tdd-workflow` から `spec-dock-hub` へ移すための参照影響を inventory する。
  - Provider-side installed skill asset と dogfooding mirror の扱いを決める。
  - README / docs / tests / skill references / generated surfaces のうち、名称変更で必要な箇所を洗い出す。
  - 現行 surface から旧 `spec-driven-tdd-workflow` の実行時 / discovery 入口を削除し、新名に統合する。
  - 変更後に `spec-dock` の hub skill であることが、名前と description から読めることを確認する。
- 禁止:
  - Hub の責務を広げて leaf skill の workflow spine を吸収しない。
  - `iss-00164` で定めた hub = route selector + global invariant、leaf = task-specific workflow spine の境界を崩さない。
  - Runtime guard、validation logic、workflow enforcement をこの issue の主目的にしない。
  - 旧 `spec-driven-tdd-workflow` を compatibility alias / forwarding skill として残さない。
  - 過去の evidence / historical spec を、実行時 surface と同列に機械 rewrite しない。
- 対象外:
  - Individual leaf skill の rename。
  - Issue planning / execution / clarification workflow の再設計。
  - Template authority / docs boundary の横断再整理。
  - SpecDock product feature expansion。

## 境界

- 常に行う:
  - Provider-side `src/spec_dock/assets/install_root/.agents/skills/` を shipped skill source of truth として扱う。
  - `.agents/skills/` は dogfooding mirror / verification target として扱う。
  - 旧名 `spec-driven-tdd-workflow` の参照を `rg` で inventory してから full migration の変更対象と historical evidence として残す対象を分ける。
  - 新しい名前は、SpecDock の hub / route selector / global invariant surface であることを伝える。
- 判断が必要:
  - skill discovery surface における description をどの程度変えるか。
  - historical spec / discussion / report に残る旧名をどこまでそのまま保存し、どこから migration note にするか。
- 行わない:
  - 名前だけでなく workflow 内容そのものを再設計する。
  - 既存参照の削除・更新を、利用箇所確認なしに行う。
  - GitHub issue title と local spec title だけを変えて完了扱いにする。

## 非交渉制約

- `iss-00164` の hub/leaf boundary を維持する。
- Shipped asset 変更は provider-side source を authority とする。
- Dogfooding mirror は provider と整合していることを検証する。
- Fresh reviewer gate なしに design / plan / execution handoff へ進んだと主張しない。
- 名前変更が reference / tests / generated asset に与える影響を、少なくとも repository search で確認する。
- 旧 `spec-driven-tdd-workflow` は実行時 / discovery / docs の現行入口として残さない。

## 前提

- `iss-00164` は `done` であり、hub skill の役割自体は整理済みである。
- この issue は、その役割を名前と周辺参照からも分かるようにする後続 issue である。

## 受け入れ条件

- AC-001:
  - アクター: SpecDock skill を探す agent
  - 前提: available skills または skill directory に hub skill が表示される
  - 操作: SpecDock work の入口として読む skill を選ぶ
  - 期待結果: `spec-dock-hub` という skill name / description から、SpecDock 全体の hub / route selector / global invariant surface であることを判断できる
  - 観測点: provider-side skill metadata, `SKILL.md`, dogfooding mirror
- AC-002:
  - アクター: maintainer
  - 前提: 旧名 `spec-driven-tdd-workflow` の参照が存在する可能性がある
  - 操作: repository search で参照を確認し、現行 surface の更新対象と historical evidence として保存する対象を分ける
  - 期待結果: 参照影響が inventory され、完全移行方針と対象外 rationale が design / plan / report に残る
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
  - 前提: historical spec / discussion などに旧名を参照する古い文脈がある
  - 操作: repository docs / skill references を読む
  - 期待結果: 現行入口は新名に統一され、旧名は historical evidence または migration rationale としてのみ追跡できる
  - 観測点: new hub references, negative `rg` for current surfaces, report migration record
- AC-006:
  - アクター: maintainer
  - 前提: `spec-dock update` が既存 consumer repo の managed `.agents/skills/` を更新する
  - 操作: old managed hub skill path と new hub skill path の扱いを確認する
  - 期待結果: `spec-dock-hub` が installed current hub として存在し、旧 `spec-driven-tdd-workflow` は current managed entry / compatibility alias として残らない
  - 観測点: `src/spec_dock/cli.py`, installer/update tests, dogfooding mirror, negative path inspection

## 例外・エッジケース

- EC-001:
  - 条件: 新名称に変更すると skill discovery / runtime / tests が旧 path に依存して壊れる
  - 期待: 旧 path 依存を新名へ更新し、互換 alias ではなく tests / docs / bundled asset references を修正して統合する
  - 観測点: design decision and verification evidence
- EC-002:
  - 条件: `spec-dock-hub` という名前だけでは governance / workflow invariant の意味が弱い
  - 期待: skill description / heading / first-read bullets で route selector と global invariant surface であることを補う
  - 観測点: provider-side and dogfooding mirror `SKILL.md`
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
  - Historical reference: 過去の spec / discussion / report に残る旧 skill name の記録。現行の実行時入口や互換 surface ではない。

## 未確定事項

- Q-001:
  - 質問: canonical な新 skill name は何にするか。
  - 回答:
    - `spec-dock-hub` を採用する。
  - 理由:
    - シンプルでわかりやすく、SpecDock の hub であることが最も伝わる。
  - 影響範囲:
    - skill directory path, skill metadata, docs references, tests, dogfooding mirror, generated projections.
- Q-002:
  - 質問: 旧名互換を残すか。
  - 回答:
    - 残さない。ユーザー回答により、新しい名前へ完全移行する。
  - 影響範囲:
    - design / plan で、互換 alias ではなく full migration と negative inspection を計画する。
