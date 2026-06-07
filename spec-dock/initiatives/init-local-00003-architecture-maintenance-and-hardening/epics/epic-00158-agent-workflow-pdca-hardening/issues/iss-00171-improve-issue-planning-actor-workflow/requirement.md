---
種別: 要件定義書（Issue）
ID: "iss-00171"
タイトル: "Improve Issue Planning Actor Workflow"
関連GitHub: ["#171"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-07"
親: ["epic-00158", "init-local-00003"]
---

# iss-00171 Improve Issue Planning Actor Workflow — 要件定義

## 目的

`spec-dock-issue-planning` skill を、抽象的な phase order ではなく、actor-based な issue authoring workflow spine として読めるように修正する。

今回の修正は、ChatGPT 5.5 Pro の分析で明確化された「親 skill に `system-architect` / `implementation-planner` の draft 作成・採用・統合ルートがない」という問題を直接解消する。

加えて、追加で観測された問題として、`spec-dock-system-architect` と `spec-dock-implementation-planner` を skill として維持していること自体を解消する。この2つは skill ではなく agent role として完全にカプセル化し、role 固有知識を `.agents/skills/` に移さない。

## 背景・現状

### 現状の挙動

- 現行 `spec-dock-issue-planning/SKILL.md` は、`requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff` という phase order を明示している。
- しかし workflow 本体には、design phase で `system-architect` に draft design proposal を依頼することが書かれていない。
- plan phase でも、`implementation-planner` に draft plan proposal を依頼することが書かれていない。
- `system-architect` / `implementation-planner` の draft は `Authority And Routing` で evidence only として言及されるが、いつ作るか、どう採用するか、どう canonical artifact に統合するかが実行順に接続されていない。

### 観測された問題

- ユーザーが更新後の skill を実際に使ったところ、設計書の draft proposal が `system-architect` によって作成されなかった。
- 実装計画書の draft proposal も `implementation-planner` によって作成されなかった。
- ChatGPT 分析は、現行 skill が「phase graph」であり「task graph」ではないことを根本原因とした。

### 情報源

- `discussions/20260607t074107z-research-chatgpt-actor-workflow-analysis.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- `.codex/agents/system-architect.toml`
- `.codex/agents/implementation-planner.toml`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/phase_plan_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock の issue planning workflow を実行する Codex / coding agent。
  - SpecDock の shipped agent-tooling assets を保守する maintainer。
- 代表シナリオ:
  - Agent が issue-level requirement / design / plan を作成する。
  - Agent が design phase に入った時、`system-architect` draft を作るべきことを skill 本体から判断する。
  - Agent が plan phase に入った時、`implementation-planner` draft を作るべきことを skill 本体から判断する。
  - Draft を evidence として扱い、main orchestrator が adoption ledger を通して canonical docs に統合する。
  - `system-architect` / `implementation-planner` agent が起動した時、role contract を skill 参照ではなく agent instruction だけで完結して実行する。

## スコープ

- 必須:
  - Provider-side source of truth:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - Dogfooding mirror:
    - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - Provider-side agent instruction source of truth:
    - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
    - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - Dogfooding agent mirror:
    - `.codex/agents/system-architect.toml`
    - `.codex/agents/implementation-planner.toml`
  - 削除対象:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/`
    - `.agents/skills/spec-dock-system-architect/`
    - `.agents/skills/spec-dock-implementation-planner/`
  - 必要に応じた周辺補正:
    - `spec-driven-tdd-workflow/SKILL.md`
    - `spec-dock/docs/workflow_spec_authoring.md`
    - `spec-dock/docs/workflow_issue.md`
    - `spec-dock/docs/phase_design.md`
    - `spec-dock/docs/phase_plan_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - Provider-side source と dogfooding mirror の整合確認。
  - `validate` / `sync` / targeted inspection による dogfooding confirmation。
- 禁止:
  - ChatGPT research の要旨を薄め、抽象的な「改善する」だけの要件に戻す。
  - Runtime gate / CLI enforcement / regression harness をこの issue の主目的にする。
  - Delegated draft を reviewer pass や phase promotion の代替にする。
  - Canonical `design.md` / `plan.md` を sub-agent 直接編集可能にする。
  - Skill に docs の詳細 schema や長い policy を全文コピーして肥大化させる。
  - `system-architect` / `implementation-planner` の role contract を skill として残す。
  - Agent role 固有知識を `.agents/skills/spec-dock-system-architect/` または `.agents/skills/spec-dock-implementation-planner/` に移す。
- 対象外:
  - Multi-agent runtime API の実装変更。
  - 新しい CLI command / validator / hard gate の追加。
  - Full workflow docs rewrite。
  - `draft-design` / `draft-plan` kind policy の大規模再設計。ただし明らかな矛盾を残さない最小補正は対象。

## 境界

- 常に行う:
  - `spec-dock-issue-planning` の workflow 本体に actor / delegated request / adoption / review gate / gap routing を入れる。
  - `system-architect` と `implementation-planner` を `Authority And Routing` だけでなく design / plan phase の実行順に登場させる。
  - `system-architect` / `implementation-planner` の詳細 role behavior は `.codex/agents/*.toml` に閉じ、`spec-dock-issue-planning` skill からは agent role を呼び出す契約だけにする。
  - Draft は default path として扱い、main orchestrator が handoff review / diff guard / Evidence Adoption Ledger / canonical integration を所有する。
  - Provider-side source を先に更新し、dogfooding mirror を同期確認する。
  - Shipped docs を補正する場合は `src/spec_dock/assets/spec_dock/docs/` を正本として変更し、`spec-dock/docs/` は dogfooding mirror / validation target として扱う。
- 判断が必要:
  - Delegated draft を「default path」と書くか、「non-trivial issue design/plan では normally request」と書くか。
  - `draft-design` / `draft-plan` kind policy を今回どこまで揃えるか。
  - 周辺 docs / hub skill の補正が必要最小限か、follow-up に分けるべきか。
- 行わない:
  - Role unavailable / consent missing / runtime unsupported の場合に workflow 全体を不必要に hard block しすぎない。
  - Manual fallback を消さない。
  - Review gate を waiver / provisional / unavailable で満たしたことにしない。

## 非交渉制約

- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator single-writer authority のままにする。
- Delegated draft は scope-local `discussions/` evidence であり、canonical artifact ではない。
- Draft existence、handoff review、adoption のいずれも fresh `spec-reviewer` pass の代替にしない。
- Fresh `spec-reviewer` pass 以外は phase promotion の pass ではない。
- Skill は first-read workflow spine とし、詳細 semantics は docs に残す。
- `system-architect` / `implementation-planner` は skill ではなく agent role として扱う。
- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml` と `implementation-planner.toml` が provider-side role contract の正本になる。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/` と `spec-dock-implementation-planner/` は削除され、dogfooding mirror からも削除される。
- `spec-dock-issue-planning` skill は role details をコピーせず、agent invocation contract、input/output boundary、adoption route、fallback/reporting obligation だけを書く。

## 前提

- `epic-00158` は skills / docs / templates の ownership boundary を採用済みである。
- `system-architect` と `implementation-planner` は、scope-local discussion draft を作る delegated authoring agent role として存在する。
- 現行の `.codex/agents/system-architect.toml` と `.codex/agents/implementation-planner.toml` は、それぞれ skill を正本として参照する thin adapter になっているため、今回の修正で agent instruction 自体を正本化する必要がある。
- 今回のユーザー指示は、この issue scope で必要な authoring / reviewer / specialist role を workflow に沿って使う同意を含む。

## 受け入れ条件

- AC-001:
  - アクター: issue planning を実行する agent。
  - 前提: `spec-dock-issue-planning/SKILL.md` を読む。
  - 操作: issue requirement / design / plan authoring の次 action を判断する。
  - 期待結果: requirement phase、design phase、plan phase、execution handoff が actor-based sequence として読め、design phase では `system-architect` draft request、plan phase では `implementation-planner` draft request が default path として明示されている。
  - 観測点: Provider-side skill と dogfooding mirror の本文。
- AC-002:
  - アクター: main orchestrator。
  - 前提: design phase に入り、requirement が fresh `spec-reviewer` pass 済み。
  - 操作: skill の design phase 手順を読む。
  - 期待結果: `system-architect` request に含める source artifacts、allowed discussion path rule、forbidden paths/actions、expected output、leaf evidence permission、stop/invalidation condition、report ledger destination が分かる。
  - 観測点: `spec-dock-issue-planning/SKILL.md` の design phase / delegated invocation contract。
- AC-003:
  - アクター: main orchestrator。
  - 前提: plan phase に入り、requirement/design が fresh `spec-reviewer` pass 済み。
  - 操作: skill の plan phase 手順を読む。
  - 期待結果: `implementation-planner` request と、design evidence missing/stale/contradictory/insufficient 時の blocker route が分かる。
  - 観測点: `spec-dock-issue-planning/SKILL.md` の plan phase / gap routing。
- AC-004:
  - アクター: reviewer / maintainer。
  - 前提: delegated draft が作成された。
  - 操作: draft の採用可否を確認する。
  - 期待結果: draft は handoff review、post-run diff guard、Evidence Adoption Ledger、canonical integration を経るまで authority にならないことが明示されている。
  - 観測点: `Authority And Routing` / `Draft Adoption And Report Evidence` / `report.md` evidence slots。
- AC-005:
  - アクター: agent。
  - 前提: `system-architect` または `implementation-planner` が unavailable / denied / consent missing / runtime unsupported。
  - 操作: skill の fallback 手順を読む。
  - 期待結果: manual fallback / blocker recording は可能だが、reviewer gate は緩まず、skip/blocker reason を `report.md` に残す必要がある。
  - 観測点: fallback / stop condition wording。
- AC-006:
  - アクター: maintainer。
  - 前提: provider-side source を更新する。
  - 操作: dogfooding mirror を確認する。
  - 期待結果: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` と `.agents/skills/spec-dock-issue-planning/SKILL.md` が意図どおり同期している。
  - 観測点: `diff -u` / targeted `rg` / `validate` / `sync` evidence。
- AC-007:
  - アクター: maintainer。
  - 前提: 周辺 docs / hub skill / runtime reference checks / delegated agent TOML に矛盾がある。
  - 操作: 今回の actor workflow rewrite と照合する。
  - 期待結果: `draft-design` / `draft-plan` kind policy、hub routing、workflow docs の hidden mandatory workflow など、今回の修正を妨げる矛盾が必要最小限で補正される、または non-blocking follow-up として明示される。
  - 観測点: diff / report decision ledger。
- AC-008:
  - アクター: delegated `system-architect` agent。
  - 前提: agent が起動される。
  - 操作: provider-side と dogfooding mirror の `.codex/agents/system-architect.toml` を読む。
  - 期待結果: role contract、allowed output path、forbidden changes、diff guard 前提、output sections、stop conditions が agent instruction 内で完結しており、`.agents/skills/spec-dock-system-architect/SKILL.md` を読む必要がない。
  - 観測点: `.codex/agents/system-architect.toml` と provider-side source、削除済み skill path。
- AC-009:
  - アクター: delegated `implementation-planner` agent。
  - 前提: agent が起動される。
  - 操作: provider-side と dogfooding mirror の `.codex/agents/implementation-planner.toml` を読む。
  - 期待結果: role contract、allowed output path、forbidden changes、design evidence gap routing、output sections、stop conditions が agent instruction 内で完結しており、`.agents/skills/spec-dock-implementation-planner/SKILL.md` を読む必要がない。
  - 観測点: `.codex/agents/implementation-planner.toml` と provider-side source、削除済み skill path。
- AC-010:
  - アクター: maintainer。
  - 前提: agent roles are encapsulated in `.codex/agents/*.toml`。
  - 操作: shipped install_root と dogfooding mirror を確認する。
  - 期待結果: `spec-dock-system-architect` / `spec-dock-implementation-planner` skill directories が provider-side と dogfooding mirror の両方から削除され、hub / issue-planning / docs に残る参照は agent role 参照であり skill 参照ではない。
  - 観測点: `rg` / `find` / provider-mirror comparison。
- AC-011:
  - アクター: maintainer。
  - 前提: delegated authoring runtime validates discussion front matter。
  - 操作: runtime delegated authoring domain を agent-only model と照合する。
  - 期待結果: `created_by_role` の runtime許可値と generated provenance は deleted skill names ではなく agent role names `system-architect` / `implementation-planner` へ移行する。互換値を残す場合は migration rationale と focused tests が明記される。
  - 観測点: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`、該当 tests / targeted `rg`。
- AC-012:
  - アクター: maintainer。
  - 前提: role skill directories の削除と runtime provenance の移行を実装する。
  - 操作: 既存テストを確認し、古い role skill / provenance contract を固定しているテストを更新する。
  - 期待結果: installer/update asset tests、delegated authoring domain tests、CLI runtime delegated authoring tests が agent-only model を期待するよう更新され、focused pytest が plan/report に記録される。
  - 観測点: `tests/unit/infra/test_init_update.py`, `tests/unit/domain/test_delegated_authoring.py`, `tests/cli_runtime/test_delegated_authoring.py`, `tests/cli_runtime/harness.py`, focused pytest output。

## 例外・エッジケース

- EC-001:
  - 条件: `system-architect` role が unavailable。
  - 期待: role unavailable を delegated draft evidence / report に記録し、manual fallback または blocker に分類する。Reviewer pass は代替されない。
  - 観測点: skill fallback wording / report evidence。
- EC-002:
  - 条件: `implementation-planner` が design evidence stale / insufficient を返す。
  - 期待: plan で吸収せず design authoring または clarification に戻す。
  - 観測点: skill plan phase / gap routing。
- EC-003:
  - 条件: delegated draft が canonical docs や implementation file を変更した。
  - 期待: diff guard failure として not adopted / rejected にし、canonical integration に使わない。
  - 観測点: diff guard wording / report EAL。
- EC-004:
  - 条件: `draft-design` / `draft-plan` kind が delegated agent instruction や workflow docs と衝突する。
  - 期待: supported discussion path rule を invocation に明示し、unsupported kind を delegated role が勝手に作らない。必要最小限の compatibility wording を入れる。
  - 観測点: Discussion Draft Path Compatibility。
- EC-005:
  - 条件: 既存 docs / runtime / generated index が `spec-dock-system-architect` または `spec-dock-implementation-planner` skill 名を参照している。
  - 期待: skill としての参照は削除または agent role 参照に置換する。Runtime delegated authoring command が role 名を扱う場合は、skill path 依存を残さない。
  - 観測点: targeted `rg` / report decision ledger。
- EC-006:
  - 条件: Existing discussion artifacts or tests still expect `created_by_role: spec-dock-system-architect` / `spec-dock-implementation-planner`。
  - 期待: New runtime contract は agent role names を正とする。既存 artifact 互換が必要なら migration / backward compatibility を明記し、fresh delegated output は agent role name で生成・検証される。
  - 観測点: runtime tests / fixtures / report decision ledger。
- EC-007:
  - 条件: Existing installer/update tests still expect deleted role skill files to be copied into installed workspaces。
  - 期待: Tests are updated to assert deleted skill files are absent and agent TOML files contain self-contained role contracts.
  - 観測点: focused pytest / test diff。

## 用語

- `Actor-based workflow spine`:
  - phase 名だけでなく、main orchestrator、delegated role、reviewer、evidence producer がいつ何をするかを first-read skill に書いた workflow。
- `Delegated draft`:
  - `system-architect` / `implementation-planner` agent が target scope `discussions/` に作成する draft evidence。
- `Canonical integration`:
  - main orchestrator が adopted evidence を canonical `design.md` / `plan.md` へ再記述する行為。
- `Default path`:
  - 通常は実行する経路。ただし unavailable / denied / consent missing / trivial manual path などを記録付きで扱える。

## 未確定事項

- Blocking question:
  - なし。ユーザーは ChatGPT research に沿って修正すること、抽象化しすぎず essence を薄めないことを明示した。
- Non-blocking design decisions:
  - `draft-design` / `draft-plan` kind policy を agent instruction まで揃えるか、parent skill の compatibility clause に留めるか。
  - Manual dogfooding dry-run をどの粒度で今回の verification に含めるか。
