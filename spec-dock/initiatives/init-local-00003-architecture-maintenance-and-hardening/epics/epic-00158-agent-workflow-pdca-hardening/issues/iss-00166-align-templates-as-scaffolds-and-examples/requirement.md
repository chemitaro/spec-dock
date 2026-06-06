---
種別: 要件定義書（Issue）
ID: "iss-00166"
タイトル: "Align Templates As Scaffolds And Examples"
関連GitHub: ["#166"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["epic-00158", "init-local-00003"]
---

# iss-00166 Align Templates As Scaffolds And Examples — 要件定義

## 目的

SpecDock の templates を、artifact を書き始めるための scaffold、reviewer / maintainer が追跡できる evidence slot、agent が模倣しやすい good example として整える。

この issue は `epic-00158` の T4 templates lane であり、`iss-00163` / `iss-00164` / `iss-00165` で整えた skill-owned workflow spine と docs-owned detail/reference boundary を、template surface でも矛盾なく読める状態にする。

## 背景・現状

- 現状の template surface:
  - `src/spec_dock/assets/spec_dock/templates/README.md` は template catalog、discussion doc catalog、naming / update guidance を説明する。
  - `templates/issue/plan.md` は executable plan scaffold、closure index、delegation contract、review gate slots を持つ。
  - `templates/issue/report.md` は observed evidence ledger、Spec Interpretation / Decision Ledger、Evidence Adoption Ledger、Spec Authoring Gate、Delegated Draft Evidence、step closure、final gate slots を持つ。
  - `templates/discussions/interview.md` / `research.md` / `disc.md` は clarification / research / synthesis の作業面を提供する。
- 現状の課題:
  - Template に detailed policy / required-looking headings が多い場合、template 自体が compliance authority / phase promotion authority と誤読される。
  - Template が古い docs-owned workflow 表現を残すと、skill-owned first-read spine と衝突する。
  - Discussion templates が `spec-dock-clarification` の source-grounded grill loop を支えられないと、正式質問、回答捕捉、採用判断、canonical reflection が分断される。
  - Report template の evidence slots が不足すると、sub-agent / research / discussion output を canonical authority と混同しやすくなる。
- 情報源:
  - Epic requirement / design / plan。
  - Accepted ADRs under `epic-00158/discussions/20260605t080509z-*.md`。
  - `iss-00162` context surface inventory。
  - Completed `iss-00163`, `iss-00164`, `iss-00165` evidence。
  - Current provider templates and dogfooding mirror templates。

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock artifacts を作成する coding agent / maintainer。
- 代表シナリオ:
  - Agent が template から canonical doc や discussion doc を作成し、必要な slots と examples を得る。
  - Agent は template を埋めるだけで reviewer pass、phase completion、issue completion を主張せず、skill / docs / reviewer gate / report ledger に従う。
  - Maintainer は generated artifact を見て、どこが proposed evidence で、どこが canonical adoption かを追跡できる。

## スコープ

- 必須:
  - Provider-side templates under `src/spec_dock/assets/spec_dock/templates/` の template-owned scaffold / evidence slot / example boundary を揃える。
  - Dogfooding mirror templates under `spec-dock/templates/` を検証対象として確認する。
  - Template README が templates を compliance authority ではなく starting scaffold / generated artifact surface として説明する。
  - Initiative / Epic / Issue report templates が evidence slots と gate ledger を提供しつつ、template 自体を policy owner にしない。
  - Issue plan template が workflow docs / authoring docs を detail/reference として参照しつつ、template 自体を policy owner にしない。
  - `interview` template が source grounding、one essential question、answer capture、adoption/reflection を支える。
  - `research` template が facts / inference / unverified / question candidates を分離する。
  - `disc` template が synthesis、reflection proposal、ADR candidate triage、adoption target を支える。
  - Provider / mirror parity、`validate` / `sync`、targeted wording inspection を report に残す。
- 禁止:
  - Templates を pass/fail rule、phase promotion、issue completion、reviewer gate の authority にする。
  - Skill-owned workflow を template に全文コピーして肥大化させる。
  - Docs が所有すべき field semantics、hard cases、lifecycle policy を template へ過剰移動する。
  - Runtime validation、CLI behavior、tests migration、regression harness をこの issue に吸収する。
  - Prior issue の skill/docs policy decision を reopen する。
- 対象外:
  - Skill rewrite。
  - Workflow docs rewrite。
  - Automated regression checks / manual harness。
  - GitHub Issue #167 `Migrate Tests To Pytest`。この issue は current `epic-00158` tree には含まれていないため、この issue の scope では扱わない。

## 境界

- 常に行う:
  - Provider-side templates を source of truth として変更し、dogfooding mirror は検証対象として扱う。
  - Template 文言は「write scaffold」「evidence slots」「examples」を示し、authority は skills / docs / accepted ADRs / canonical docs / reviewer gates / report ledger に置く。
  - Placeholder は完成証跡ではなく、agent が削除・統合・並べ替え可能な starting shape として扱う。
- 判断が必要:
  - Template に入れる example の量は、agent が正しい形を模倣できる最小限にする。
  - Report template の ledger slots は、現行 workflow の auditability を壊さない範囲で残す。
- 行わない:
  - Template を使っただけで `spec-reviewer` pass とみなさない。
  - Generated artifact の placeholder をそのまま completion とみなさない。

## 非交渉制約

- Templates are not compliance authorities.
- Templates are not workflow source of truth.
- Discussion docs are evidence / proposal surfaces until main orchestrator adoption.
- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` remain main-orchestrator-owned.
- `report.md` is observed evidence ledger; `plan.md` owns planned contract.

## 前提

- `iss-00163` completed the clarification skill-owned workflow lane.
- `iss-00164` completed hub / leaf routing alignment.
- `iss-00165` completed workflow docs boundary alignment.
- `iss-00162` inventory identified template rows and handed them to this issue.
- No user interview blocker remains; local docs and existing discussions answer scope / non-scope / acceptance.

## 受け入れ条件

- AC-001 template boundary:
  - アクター: agent。
  - 前提: Agent creates or reads a generated canonical / discussion artifact from a template。
  - 操作: Template wording and slots are inspected。
  - 期待結果: Templates read as scaffold / evidence slots / examples, not compliance authority or phase promotion authority。
  - 観測点: provider template diff, mirror diff / parity check, targeted `rg`。
- AC-002 discussion clarification support:
  - アクター: clarification を行う agent。
  - 前提: Important decision or pressure-test question needs a discussion artifact。
  - 操作: `interview`, `research`, and `disc` templates are inspected。
  - 期待結果: `interview` supports one-question source-grounded answer capture; `research` separates facts / inference / unverified / question candidates; `disc` supports synthesis / reflection proposal / ADR triage。
  - 観測点: discussion template diff and targeted inspection。
- AC-003 report evidence slots:
  - アクター: maintainer / reviewer。
  - 前提: Initiative / Epic / Issue report templates are used for planning / execution / closeout evidence。
  - 操作: Evidence ledgers and gate slots are inspected across report templates。
  - 期待結果: EAL, Delegated Draft Evidence, Spec Authoring Gate, reviewer state, blocking / next action, closure / commit / follow-up evidence can be recorded without claiming authority from the template itself。
  - 観測点: `templates/initiative/report.md`, `templates/epic/report.md`, `templates/issue/report.md` diff and report evidence。
- AC-004 issue plan scaffold:
  - アクター: implementation planner / executor。
  - 前提: Issue plan template is used。
  - 操作: Plan template wording and closure sections are inspected。
  - 期待結果: Template provides executable step scaffold and closure slots while routing detailed policy / field semantics to docs and skills。
  - 観測点: `templates/issue/plan.md` diff and targeted inspection。
- AC-005 provider / mirror validation:
  - アクター: maintainer。
  - 前提: Provider templates are changed。
  - 操作: Dogfooding mirror and generated projections are checked。
  - 期待結果: Provider source and mirror are aligned or any no-op / generated diff is recorded; `validate` / `sync` evidence is captured。
  - 観測点: `diff -q` / targeted `rg`, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync`, `report.md`。
- AC-006 scope containment:
  - アクター: reviewer。
  - 前提: Issue-wide diff is reviewed。
  - 操作: Changed files are inspected。
  - 期待結果: No skill, workflow docs, runtime, tests, or GitHub metadata changes are included except report evidence。
  - 観測点: `git diff --name-only` and reviewer gate。

## 例外・エッジケース

- EC-001 over-explaining templates:
  - 条件: Template wording starts duplicating docs-owned field semantics / hard cases / lifecycle policy。
  - 期待: Move detail back to docs reference; keep template as slot/example surface。
  - 観測点: diff review and spec-reviewer。
- EC-002 missing evidence slots:
  - 条件: Reducing template authority wording removes evidence capture needed by current workflow。
  - 期待: Keep or add evidence slots while avoiding authority claims。
  - 観測点: report template inspection。
- EC-003 stale source-of-truth wording:
  - 条件: Template or README still says templates / workflow docs are the sole source of truth for operational workflow。
  - 期待: Replace with skill-owned operational entrypoint and docs detail/reference wording where appropriate。
  - 観測点: negative `rg`。

## 用語

- Scaffold:
  - Artifact を書き始めるための最小構造。
- Evidence slot:
  - 後続 reviewer / maintainer が採用判断、blocking state、closure、commit を追えるようにする記録欄。
- Good example:
  - Agent が正しい書き方を模倣しやすくする最小例。
- Compliance authority:
  - pass/fail、phase promotion、completion を決める正本。Templates はこれを所有しない。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking defaults:
  - Templates は short scaffold を維持し、必要な examples は過剰に増やさない。
  - Detailed policy / field semantics は docs に残し、template からは参照する。
