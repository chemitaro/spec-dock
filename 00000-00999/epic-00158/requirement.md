---
種別: 要件定義書（Epic）
ID: "epic-00158"
タイトル: "Agent Workflow PDCA Hardening"
関連GitHub: ["#158"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["init-local-00003"]
---

# epic-00158 Agent Workflow PDCA Hardening — 要件定義（何を、なぜ行うか）

## 目的（Initiative との紐づき）

- Initiative 目標 / 指標:
  - `init-local-00003 Architecture Maintenance and Hardening` のうち、SpecDock を dogfooding し続けるための agent-facing workflow / governance / context surface を改善する。
  - source-of-truth、workflow authority、artifact authority、dogfooding verification の境界を曖昧にしない。
- この epic が提供する能力:
  - Coding agent が最初に読む skill / docs / templates から、守るべき workflow と参照すべき詳細情報の住み分けを読み取れるようにする。
  - 必須 workflow が複数 docs に埋もれて見落とされる状態を減らし、phase gate、reviewer gate、evidence adoption、clarification handoff を安定して運用できるようにする。
  - 一度の修正で完結させず、first wave の context-surface cleanup、dogfooding、観測、後続 guard / harness / runtime check へつなぐ PDCA 改善レーンを作る。

## 背景・現状

- 現状:
  - SpecDock の skill は軽量で、詳細 docs を参照する構造になっている。
  - 役割分担自体は有効だが、agent に必ず守ってほしい作業順序や停止条件が docs 側に埋もれ、複数文書に分散している。
  - agent が linked docs を開かない、または一部だけ読むと、必須 workflow を知らないまま作業を進めるリスクがある。
- 観測された failure mode:
  - requirement / design / plan の phase order を飛ばす。
  - fresh `spec-reviewer` pass なしに次 phase や execution handoff へ進む。
  - missing / stale / failed / unavailable / denied / waived / provisional を pass 相当として扱う。
  - sub-agent、ChatGPT、Deep Research、discussion draft の出力を、main orchestrator の採用証跡なしに canonical artifact と誤認する。
  - 未解決の requirement / design / plan gap を execution assumption として吸収する。
  - clarification が単なる質問応答になり、source-grounded な一問一答の圧力テストと artifact capture に結び付かない。
- 採用済み判断:
  - 問題の主因は「ルール不足」だけではなく、モデルが読む context surface が薄い、分散している、お手本として弱いことにある。
  - first wave は runtime gate や regression checks ではなく、skills / docs / templates を整理して「どこを読んでも正しい住み分けが見える」状態にする。
  - `spec-dock-clarification` は例外的に skill-owned workflow とし、SpecDock 版 source-grounded grill loop を `SKILL.md` の first-read surface に置く。

## ユースケース

- 正常系:
  - Agent が SpecDock の issue / epic / clarification / execution 関連 skill を読んだ時点で、次に守るべき operational workflow spine、停止条件、reviewer gate、evidence obligation を把握できる。
  - Agent は詳細な field semantics、schema、hard-case criteria、artifact の意味を docs へ読みに行き、skill や templates に全文コピーされた長い説明へ依存しない。
  - Maintainer は first wave の issue を順番に dogfooding し、各修正の結果から次の PDCA issue を選べる。
- 例外 / 運用シナリオ:
  - Requirement / design / plan に未解決 gap が見つかった場合、execution assumption として吸収せず、clarification または該当 phase へ戻す。
  - Reviewer state が fresh `passed` 以外の場合、次 phase / execution handoff / phase completion を blocked または incomplete として扱い、再レビューまたは追加調査へ戻す。
  - Sub-agent、ChatGPT、Deep Research、discussion draft は evidence として扱い、canonical artifact へ反映する場合は main orchestrator が採否を判断し `report.md` に Evidence Adoption Ledger を残す。
  - Runtime gate、manual harness、regression checks は、context surface cleanup 後に期待 contract が安定してから設計する。

## エピック要件（Epic requirements）

- E-RQ-001: Context surface ownership を固定する。
  - Skills は、agent が最初に守る operational workflow spine を所有する。
  - Docs は、concept、field meanings、policy details、references、hard-case decision criteria を所有する。
  - Templates は、薄い final-artifact scaffolds と evidence slots を所有し、good examples や compliance authority は所有しない。具体例や判断基準は docs が所有する。
- E-RQ-002: First-read executable な skill surface を作る。
  - 主要 skill は、linked docs を読む前でも、作業順序、停止条件、reviewer gate、evidence obligation、次に読む docs を判断できる状態にする。
  - 詳細 schema や長い policy は skill に複製せず、docs へ誘導する。Templates は完成 artifact に残る最小 scaffold に留める。
- E-RQ-003: `spec-dock-clarification` を skill-owned source-grounded grill workflow として扱う。
  - `spec-dock-clarification/SKILL.md` は、sources を読む、provisional understanding を作る、一つの essential pressure-test question を選ぶ、artifact に回答を捕捉する、iterate / handoff を判断する workflow を所有する。
  - `workflow_clarification.md` は残す場合も thin bridge / reference とし、必須 clarification runbook の authority にしない。
- E-RQ-004: Spec authoring gate の可視性を上げる。
  - Requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> downstream handoff の順序を、agent-facing surface で見落としにくくする。
  - missing / stale / failed / unavailable / denied / waived / provisional は pass ではないことを明示する。
- E-RQ-005: Evidence と canonical authority の境界を固定する。
  - Research、discussion、ADR、sub-agent output、ChatGPT / Deep Research output は、採用判断まで evidence として扱う。
  - Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映は main orchestrator が所有し、採用証跡を `report.md` に残す。
- E-RQ-006: First wave の issue decomposition を ADR に従って進める。
  - `iss-00159` を first concrete specimen として扱う。
  - その後、skills / docs / templates の横断整理、clarification skill-owned workflow、hub / leaf routing、workflow docs、templates の整理へ進む。
  - Regression checks、manual harness、runtime gate は後段へ延期する。
- E-RQ-007: Provider source と dogfooding mirror の境界を守る。
  - Shipped asset の変更は provider-side source を authority とし、dogfooding mirror は検証対象として扱う。
  - 変更後は local dogfooding workspace で validate / sync / targeted inspection を行う。

## エピック受け入れ条件（Epic acceptance criteria）

- E-AC-001: Context surface ownership が矛盾なく見える。
  - 前提: first wave の対象 skill / docs / templates を読む。
  - 操作: skill / docs / templates の責務分担を確認する。
  - 期待結果: Skills は workflow spine、docs は詳細意味と具体例、templates は薄い scaffold / evidence slots という境界が矛盾なく読める。
  - 観測点: provider-side skill / docs / templates の diff と dogfooding mirror inspection。
- E-AC-002: First wave issue が scope 通りに分割されている。
  - 前提: `20260605t080509z-02-adr` が accepted である。
  - 操作: Epic 配下の issue set と各 issue scope を確認する。
  - 期待結果: ADR の first-wave issue decomposition と整合し、deferred guard / harness / runtime work が first-wave blocker になっていない。
  - 観測点: Epic `plan.md`、Epic `report.md`、Issue requirement / design / plan。
- E-AC-003: `spec-dock-clarification` が skill-owned workflow として読める。
  - 前提: Agent が `spec-dock-clarification/SKILL.md` を読む。
  - 操作: clarification task の進め方を判断する。
  - 期待結果: linked workflow doc を authority として読まなくても、source-grounded grill loop、artifact routing、one-question discipline、handoff を理解できる。
  - 観測点: `spec-dock-clarification/SKILL.md`、`workflow_clarification.md`、discussion templates。
- E-AC-004: Reviewer gate と non-pass state の扱いが明示されている。
  - 前提: Requirement / design / plan の phase promotion を行う。
  - 操作: reviewer verdict と次 action を確認する。
  - 期待結果: fresh `passed` 以外は pass と扱われず、blocked / incomplete / re-review / prior phase return のいずれかとして判断できる。
  - 観測点: skill surface、workflow docs、scope report の Spec Authoring Gate。
- E-AC-005: Evidence adoption boundary が実運用に残る。
  - 前提: Discussion、research、ChatGPT / Deep Research、sub-agent output が存在する。
  - 操作: canonical artifact へ反映する。
  - 期待結果: main orchestrator の採否判断、採用先、blocking / non-blocking、next action が `report.md` の Evidence Adoption Ledger に残る。
  - 観測点: Epic / Issue `report.md`。
- E-AC-006: Provider source と dogfooding mirror の検証が行われる。
  - 前提: Shipped asset に影響する変更を行う。
  - 操作: provider-side source と dogfooding mirror を確認する。
  - 期待結果: authority は provider-side source にあり、dogfooding mirror は validate / sync / targeted inspection の証跡を持つ。
  - 観測点: `src/spec_dock/assets/...`、`.agents/...`、`spec-dock/...`、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock sync`。
- E-AC-007: Requirement phase に blocking question が残っていない。
  - 前提: この requirement を design review へ渡す。
  - 操作: scope / non-scope / acceptance criteria / priority の未確定事項を確認する。
  - 期待結果: ユーザー確認が必要な blocking question は残っていない。非 blocking な設計判断は design / plan へ送られている。
  - 観測点: この `requirement.md` の `未確定事項` と `report.md` の Spec Authoring Gate。

## スコープ

- 必須:
  - Provider-side installed skills: `src/spec_dock/assets/install_root/.agents/skills/`
  - Provider-side docs / templates: `src/spec_dock/assets/spec_dock/docs/`, `src/spec_dock/assets/spec_dock/templates/`
  - Dogfooding mirror verification: `.agents/`, `spec-dock/`
  - Epic-level ADR adoption、first-wave issue decomposition、PDCA sequencing。
- 禁止:
  - Runtime gate、CLI enforcement、validation logic を first fix として前面に出す。
  - Automated regression checks / manual harness を、context surface cleanup 前の独立 blocker にする。
  - Docs の全文を skill にコピーして skill を肥大化させる。
  - Templates を compliance authority として扱う。
  - Delegated / external research output を main orchestrator の採用証跡なしに canonical として扱う。
  - `spec-dock-clarification` を SpecDock artifact から切り離された generic coaching skill にする。
- 対象外:
  - SpecDock の product feature expansion。
  - External / multi-repo strategy。
  - Full runtime gate design / implementation。
  - Matt Pocock 氏の original skill text の exact copy。
  - Agent-facing context surface と無関係な広範 refactor。

## 境界

- 常に行う:
  - ユーザーに聞く前に、active docs、parent docs、discussions、ADR、関連 source を確認する。
  - Shipped asset は provider-side source を authority とし、dogfooding mirror は検証対象として扱う。
  - Agent が必ず守る作業順序、停止条件、evidence obligation は skill の first-read surface に置く。
  - Artifact の意味、field semantics、schema、hard-case criteria、具体例は docs に置く。Templates には完成 artifact に残る最小 scaffold だけを置く。
  - Evidence を canonical artifact へ採用する場合は `report.md` に採用証跡を残す。
- 判断が必要:
  - `workflow_clarification.md` を bridge として残すか、後段で retire するか。
  - 横断 cleanup issue をどこまで一つにまとめ、どこで skill family / artifact family に分割するか。
  - Deferred した regression / harness / runtime check を、どの観測結果を条件に次 wave へ上げるか。
- 行わない:
  - Fresh `spec-reviewer` pass なしに design / plan / downstream handoff へ phase promotion したと主張しない。
  - Runtime guardrail work で first-wave context cleanup を置き換えない。
  - Local source から答えられる事実をユーザー質問で代替しない。
  - 未解決 gap を execution assumption として隠さない。
  - ユーザーが破棄指示した research output を採用しない。

## 非機能要件

- 性能:
  - First wave は runtime performance を変更対象にしない。
  - Skill は first-read surface として読める密度を保ち、詳細説明の過剰コピーを避ける。
- 信頼性 / 一貫性:
  - Skills / docs / templates 間で authority boundary、phase order、reviewer gate、evidence adoption の表現が矛盾しない。
  - Provider-side source と dogfooding mirror の関係が検証できる。
- セキュリティ:
  - Documentation / skill work では secrets、tokens、credentialed external side effects を扱わない。
  - External analysis は source / adoption status を記録し、canonical authority と混同しない。
- 運用:
  - 各 issue は小さく reviewable で、dogfooding 後に次の PDCA 判断を残せる。
  - Later guard / harness / runtime checks は、cleaned surfaces が安定してから drift detection / enforcement として設計する。

## 依存 / 影響範囲

- 影響する component:
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `.agents/`
  - `spec-dock/`
- 外部依存:
  - First-wave implementation に外部 service は必須ではない。
  - ChatGPT / Deep Research outputs は evidence としてのみ扱い、採用時は `report.md` に記録する。
- 互換性:
  - `workflow_clarification.md` への既存 link があるため、即時削除ではなく bridge / staged retirement を既定とする。
  - Shipped asset の変更は、新規 init / update される consumer repo に影響する。
- 採用済み ADR:
  - `spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md`

## 未確定事項

- Blocking question:
  - なし。
  - Local docs、discussions、accepted ADR、ユーザー補正により、requirement phase の scope / non-scope / acceptance criteria は design review へ渡せる粒度で確定している。
- Non-blocking design questions:
  - `workflow_clarification.md` を first wave で bridge 化に留めるか、link cleanup と合わせて retire まで進めるか。
  - `Align Skill Docs Template Context Surfaces` を一つの横断 issue とするか、skill family / docs / templates に分けるか。
  - Manual smoke probe をどの粒度で first-wave issue の検証に含めるか。
