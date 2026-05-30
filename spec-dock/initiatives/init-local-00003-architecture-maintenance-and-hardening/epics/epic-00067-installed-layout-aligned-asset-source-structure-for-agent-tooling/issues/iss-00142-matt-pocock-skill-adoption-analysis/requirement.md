---
種別: 要件定義書（Issue）
ID: "iss-00142"
タイトル: "Matt Pocock Skill Adoption Analysis"
関連GitHub: ["#142"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["epic-00067", "init-local-00003"]
---

# iss-00142 Matt Pocock Skill Adoption Analysis — 要件定義

## 目的
- Matt Pocock 氏の周辺スキルを、spec-dock の正本・phase gate・reviewer workflow を崩さずに採用するための方針を定義する。
- この Issue では直接移植や first-class skill 追加ではなく、低リスクな docs / skill guidance として「spec-dock phase discipline」に翻訳して反映する。
- Epic -> Issue slicing、bug diagnosis、Agent-Native TDD、architecture review の弱点を、実装前に計画可能な形へ改善する。

## 背景・現状
- 現状の強み:
  - spec-dock は `requirement.md`、`design.md`、`plan.md`、`report.md`、`discussions/` evidence、fresh reviewer gates を正本にしている。
  - `iss-00134` では Grill with docs の考え方を `spec-dock-clarification` に取り込み、source-grounded clarification と spec authoring handoff が整理された。
  - 既存の Issue planning には Agent-Native TDD、Spec-Locked Closure Index、step-local concrete test cases がある。
- 現状の課題:
  - Epic を複数 Issue に切る際の vertical slice / dependency order / integration checkpoint の基準が弱い。
  - bug / performance / unknown failure 系 Issue で、reproduction、hypothesis、instrumentation、regression evidence を実装前に固定する discipline が薄い。
  - TDD の原則は存在するが、public interface / observable behavior、one test -> minimal implementation、no horizontal batching の読み取りがまだ弱い。
  - architecture review で deep module、interface as test surface、deletion test、locality / leverage を使う語彙が体系化されていない。
- 情報源:
  - `discussions/20260529t154740z-research-initial-skill-adoption-research.md`
  - `discussions/20260530t081150z-interview-matt-pocock-adoption-issue-primary-scope.md`
  - `discussions/20260530t083404z-disc-matt-pocock-skills-spec-dock-integration-best-practice-proposal.md`
  - `discussions/20260530t094323z-adr-matt-pocock-skills-as-spec-dock-phase-discipline.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock で Issue planning / execution を行う人間ユーザー。
  - spec-dock の leaf skill を使って要件・設計・実装計画・実装を行う AI エージェント。
- 代表シナリオ:
  - ユーザーが大きな Epic を実行可能な Issue 群へ切るとき、vertical behavior slice と依存順で分解できる。
  - bug / performance Issue で、実装前に再現条件と仮説検証ループを計画に固定できる。
  - 実装者が TDD step を読むとき、内部実装ではなく public interface / observable behavior に向けたテストから始められる。
  - 設計者が architecture risk を見るとき、境界・依存・削除可能性・変更局所性を同じ語彙で扱える。

## スコープ
- 必須:
  - ADR に Option C の採用判断を記録し、後続仕様の判断根拠にする。
  - Matt Pocock skills を Core / Optional / Follow-up / Rejected の採用区分で整理する。
  - Core adoption を low-risk docs / skill guidance に反映できる要件・設計・実装計画へ落とす。
  - `diagnose` の feedback-loop-first discipline を Issue execution / plan evidence として扱う。
  - `tdd` の public interface / observable behavior と vertical tracer bullet を既存 Agent-Native TDD に接続する。
  - `to-issues` の vertical slice / dependency order / HITL-AFK annotation / integration checkpoint を Epic -> Issue slicing guidance として扱う。
  - `improve-codebase-architecture` / `zoom-out` の vocabulary を architecture review heuristic として扱う。
  - Provider-side source of truth を変更対象にし、dogfooding workspace への反映確認を実装計画に含める。
- 禁止:
  - Matt Pocock skills をそのまま spec-dock skill として直接輸入しない。
  - `CONTEXT.md`、PRD、temporary handoff doc を spec-dock の正本にしない。
  - GitHub label state machine を spec-dock readiness / approval / reviewer pass の代替にしない。
  - runtime / CLI behavior、domain model、GitHub sync contract をこの Issue で変更しない。
  - `triage`、`prototype`、first-class `spec-dock-diagnosis` skill をこの Issue で実装しない。
- 対象外:
  - 自動 issue slicing command / validator の新設。
  - prototype create / absorb / delete lifecycle。
  - GitHub label automation。
  - 既存 canonical docs 以外を source of truth にする handoff workflow。

## 境界
- 常に行う:
  - Provider-side docs / skill guidance を正本として設計する。
  - `spec-dock/` dogfooding workspace は反映確認対象として扱う。
  - Fresh `spec-reviewer` gate を requirement / design / plan の各 phase で通す。
- 判断が必要:
  - Content assertion test を追加するか、inspection / validate で十分か。
  - Provider-side 変更を dogfooding workspace に同期するタイミング。
  - Follow-up Issue 化する粒度。
- 行わない:
  - 実行時の status model、dependency resolver、GitHub integration の変更。
  - 新しい canonical artifact type の追加。

## 非交渉制約
- Canonical artifacts は `requirement.md` / `design.md` / `plan.md` / `report.md` とし、delegated draft や discussion は evidence に留める。
- 正本への反映は main orchestrator が行い、sub-agent の成果は採用判断を経て統合する。
- 各 phase は fresh `spec-reviewer` の `review_status: pass` を得てから次 phase に進める。
- 変更は low-risk docs / skill guidance に限定し、runtime / CLI / external integration を広げない。

## 前提
- ユーザーは Option C「spec-dock とうまく統合する」方針を採用済みである。
- `iss-00134` の Grill with docs adoption は既に存在し、本 Issue はその周辺 skill adoption 分析を扱う。
- Parent epic `epic-00067` の source authority に従い、installed agent tooling は `src/spec_dock/assets/install_root/`、spec-dock shipped scaffold docs は `src/spec_dock/assets/spec_dock/` を provider-side source of truth とする。

## 受け入れ条件
- AC-001: ADR に統合方針が記録される
  - アクター: Issue planning orchestrator
  - 前提: ユーザーが Option C を採用している
  - 操作: ADR を作成し、選択肢・判断理由・影響・follow-up を記録する
  - 期待結果: `discussions/20260530t094323z-adr-matt-pocock-skills-as-spec-dock-phase-discipline.md` が accepted decision として参照可能である
  - 観測点: ADR front matter / decision / references
- AC-002: Skill adoption classification が固定される
  - アクター: planner / future agent
  - 前提: Matt Pocock skills の research / proposal evidence が存在する
  - 操作: 要件・設計で Core / Optional / Follow-up / Rejected を明記する
  - 期待結果: 直接移植すべきもの、guidance として吸収するもの、後続 Issue に送るものが混同されない
  - 観測点: `requirement.md` / `design.md`
- AC-003: Epic -> Issue slicing guidance が改善される
  - アクター: Epic / Issue planner
  - 前提: 大きな Epic を複数 Issue に分解する
  - 操作: vertical behavior slice、dependency order、integration checkpoint、HITL/AFK annotation を使って Issue boundary を決める
  - 期待結果: 水平分割だけの Issue や readiness label 依存の Issue が計画されにくくなる
  - 観測点: `phase_plan_issue.md` / issue planning guidance / test or inspection evidence
- AC-004: TDD guidance が observable behavior に寄る
  - アクター: Issue executor / dev-coder
  - 前提: `plan.md` に Spec-Locked Closure Index と step-local concrete test cases がある
  - 操作: public interface / observable behavior で first test を固定し、vertical tracer bullet で実装する
  - 期待結果: private method や水平実装 batch に寄った TDD plan を避けられる
  - 観測点: `phase_plan_issue.md` / `docs/authoring/issue-plan.md` / skill guidance
- AC-005: Diagnosis guidance が feedback loop を先に固定する
  - アクター: Issue executor / dev-coder
  - 前提: bug / performance / unknown failure 系 Issue を実行する
  - 操作: reproduction、ranked hypotheses、targeted instrumentation、regression evidence を report evidence として扱う
  - 期待結果: 推測実装や無証跡修正を避け、検証可能な debug loop を残せる
  - 観測点: `workflow_issue.md` / `spec-dock-issue-execution/SKILL.md`
- AC-006: Architecture heuristic が spec-dock authority と整合する
  - アクター: system-architect / reviewer
  - 前提: 設計書で module boundary / dependency / interface を扱う
  - 操作: deep module、interface as test surface、deletion test、locality / leverage を設計観点として使う
  - 期待結果: `CONTEXT.md` authority を導入せず、既存 design / ADR / report evidence の範囲で architecture decision を記録できる
  - 観測点: `spec-dock-system-architect/SKILL.md` / `design.md`
- AC-007: Follow-up candidates が明確になる
  - アクター: future planner
  - 前提: この Issue では low-risk guidance だけを扱う
  - 操作: `triage`、`prototype`、first-class diagnosis、CLI slicing support を follow-up として記録する
  - 期待結果: この Issue の scope creep を避けつつ、次に検討するテーマを失わない
  - 観測点: ADR / design / plan / report
- AC-008: 変更対象と検証方針が実装可能である
  - アクター: implementation planner / executor
  - 前提: 要件と設計が reviewer pass 済みである
  - 操作: provider docs / skill guidance / tests / dogfooding validation を step 化する
  - 期待結果: plan.md が実装者にとって実行可能な command queue になっている
  - 観測点: `plan.md` / fresh spec-reviewer result

## 例外・エッジケース
- EC-001: Direct import pressure
  - 条件: 元 skill のファイル構造や wording をそのまま追加したくなる
  - 期待: spec-dock の canonical artifacts と phase gate に翻訳してから採用する
  - 観測点: ADR / design forbidden changes
- EC-002: GitHub label readiness conflict
  - 条件: `ready-for-agent` のような label state を spec-dock readiness とみなしたくなる
  - 期待: HITL/AFK は annotation に留め、approval / reviewer pass / plan readiness の代替にしない
  - 観測点: requirement forbidden scope / design contracts
- EC-003: Horizontal implementation batching
  - 条件: DB / API / UI / docs のような層別作業だけで Issue を切る
  - 期待: vertical behavior slice と integration checkpoint で Issue boundary を見直す
  - 観測点: phase planning guidance
- EC-004: Diagnosis without reproduction
  - 条件: bug / performance Issue で再現や仮説なしに修正へ進む
  - 期待: reproduction が不可能な場合も、観測点・仮説・instrumentation・代替 evidence を明記する
  - 観測点: issue execution guidance / report evidence
- EC-005: Prototype lifecycle scope creep
  - 条件: throwaway prototype をこの Issue で workflow 化したくなる
  - 期待: follow-up に送り、この Issue では guidance-level の採用に留める
  - 観測点: ADR follow-up / plan forbidden changes

## 用語（ドメイン語彙）
- Core adoption:
  - この Issue で low-risk docs / skill guidance に反映する対象。
- Optional adoption:
  - 既存 workflow の中で軽く参照できるが、この Issue の主要変更にはしない対象。
- Follow-up:
  - 価値はあるが、runtime / workflow / state model への影響が大きく別 Issue で扱う対象。
- Phase discipline:
  - 外部 skill の artifact や command を直接輸入せず、spec-dock の phase、artifact、review gate、report evidence の中で実行可能な判断規律へ翻訳したもの。
- Vertical behavior slice:
  - 一つの利用者価値または観測可能な振る舞いを、テスト・実装・検証まで薄く縦に閉じる Issue / step boundary。
- HITL / AFK annotation:
  - 人間判断が必要か、エージェントだけで進めやすいかを示す補助情報。spec-dock readiness の代替ではない。

## 未確定事項
- Q-001:
  - 質問: Content assertion test をどの程度まで追加するか
  - 推奨案: Provider docs / installed skill guidance の主要 marker を既存 unittest に最小追加し、詳細な文章一致は避ける
  - 影響範囲: design / plan の test strategy と実装時の差分量
