---
種別: research
ID: "20260702t054322z-research"
タイトル: "Epic Planning における Issue 設計・計画ドラフト運用分析"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "iss-00271"
  - "iss-00272"
  - "iss-00273"
  - "iss-00274"
  - "iss-00275"
  - "iss-00276"
authority: "synthesized"
derived_from:
  - "deep-consultant:019f214d-3d10-7833-a4dc-3bb85bc15e8f"
  - "ChatGPT-5.5 Pro Oracle session:specdock-issue-planning-policy"
  - "public repository URL supplied to ChatGPT: https://github.com/chemitaro/spec-dock"
reflected_to: []
---

# Epic Planning における Issue 設計・計画ドラフト運用分析

## 調査目的

`epic-00270` の計画具体化で、Epic Planning 段階に downstream Issue の `requirement.md` / `design.md` / `plan.md` をどこまで作成すべきかを判断する。

特に、今回のように Issue Start 前に Issue の canonical `design.md` / `plan.md` へ「ドラフト本文」を一括配置する運用が、SpecDock の `issue start`、assurance classify/compose、`.assurance.json` / `authorized_profile`、artifact evidence、fresh reviewer gate と整合するかを分析する。

## sources / 調査方法

参照先:

- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_plan_epic.md`
- `spec-dock/docs/phase_plan_issue.md`
- `spec-dock/docs/reference_naming.md`
- `spec-dock/templates/issue/design.md`
- `spec-dock/templates/issue/plan.md`
- `.agents/skills/spec-dock-epic-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-epic-execution/SKILL.md`
- `epic-00270` の `requirement.md` / `design.md` / `plan.md` / `report.md`
- 代表 Issue として `iss-00271` / `iss-00276` の `requirement.md` / `design.md` / `plan.md` / `report.md`
- Deep consultant 分析: `019f214d-3d10-7833-a4dc-3bb85bc15e8f`
- ChatGPT-5.5 Pro 分析: Oracle session `specdock-issue-planning-policy`
- 公開 GitHub URL: `https://github.com/chemitaro/spec-dock`

検証手順:

- `./spec-dock/scripts/spec-dock active show` で active Initiative / Epic / Issue を確認した。
- `git remote -v` で公開 GitHub URL を確認し、ChatGPT-5.5 Pro へのプロンプトに含めた。
- `find` と代表 Issue のファイル読解で、`iss-00271` から `iss-00276` に `.meta.json` はあるが `.assurance.json` はないこと、かつ `issue start` は実施されていないことを確認した。
- Issue template と workflow docs を読み、canonical Issue `design.md` / `plan.md` が compose 前 placeholder として扱われる前提を確認した。
- Deep consultant と ChatGPT-5.5 Pro に同じ論点を別系統で分析させ、結論の一致点と差分を統合した。

実験条件:

- ChatGPT-5.5 Pro にはローカル添付ファイルを controlling evidence として扱い、公開 GitHub URL は補助情報として扱うよう指示した。
- ChatGPT 実行では約 79k tokens / 23 files の bundle を渡した。
- ChatGPT は回答内で、添付したローカル状態を根拠とし、web は使っていないと明記した。

## facts / 観測できた事実

- 現在の active context は Initiative `init-local-00003` と Epic `epic-00270` であり、active Issue は存在しない。
- `iss-00271` から `iss-00276` は downstream Issue として作成済みだが、今回の一括作成時点で `issue start` は実施されていない。
- 各 Issue には canonical `requirement.md` / `design.md` / `plan.md` / `report.md` が存在する。
- 各 Issue の canonical `design.md` / `plan.md` には、Issue Start 前のドラフト本文が配置されている。
- Issue `design.md` / `plan.md` template は `artifact_state: awaiting-assurance-compose` を持つ compose 前 placeholder であり、本文を直接書き始める状態ではないことを示している。
- `workflow_issue.md` は、Issue planning で `authorized_profile` が missing / ambiguous / inconsistent の場合に停止すること、かつ design/plan obligations が profile に依存することを前提にしている。
- `workflow_spec_authoring.md` は canonical docs を main orchestrator single-writer authority とし、artifact は evidence surface であり canonical authority ではないと扱っている。
- `reference_naming.md` は issue-only artifact type として `draft-requirement` / `draft-design` / `draft-plan` を定義している。
- `workflow_epic.md` は Epic Planning の handoff package に、downstream Issue の draft requirement / draft design artifact path、または明示的な skip/fallback evidence を含める方向をすでに持っている。ただし `draft-plan` の明示が弱い箇所が残る。
- Deep consultant と ChatGPT-5.5 Pro はどちらも、Issue Start 前の design/plan 本文を canonical path に置くことを authority leak と見なした。

## inference / 推測

事実から推測したこと:

- Epic Planning が Issue の canonical `design.md` / `plan.md` を一括作成する運用は、現行 SpecDock の assurance compose model と整合しない。
- 一方で、Epic Planning が downstream Issue の分割、責務境界、依存順、handoff constraints をまとめて管理する価値は高い。
- したがって、Epic Planning は Issue の「分割品質」と「handoff evidence」を持ち、Issue Planning は `issue start` 後に canonical design/plan を確定する、という責務分離が最も安定する。
- Issue の canonical `requirement.md` は、scope / non-scope / acceptance criteria / parent trace / dependencies / suggested grade / open questions が十分安定している場合に限り、Epic Planning 段階で固定してよい。
- Issue の design / implementation plan は、Issue Start 前には Issue-local `draft-design` / `draft-plan` artifact に置き、canonical `design.md` / `plan.md` は compose placeholder のまま保持するべきである。

推測の根拠:

- Issue `design.md` / `plan.md` の canonical 本文は `.assurance.json` / `authorized_profile` によって要求される template と obligations が変わる。
- `issue start` 前は active Issue としての最新 repo 状態、前段 Issue の完了結果、assurance profile、fresh reviewer target が揃っていない。
- pre-start design/plan を canonical path に置くと、下流 agent が「draft」と書かれた canonical file を実質 authority と誤読する。
- artifact は非 authority evidence として扱えるため、pre-start handoff と canonical authoring を分離できる。

## best practice / 推奨方針

推奨は **制約付き B/B+ hybrid** とする。

- Epic Planning は downstream Issue shell と dependency edge を作成してよい。
- Epic Planning は、Issue requirement が reviewer-gated handoff に耐えるほど安定している場合に限り、canonical Issue `requirement.md` を作成してよい。
- Issue requirement が未確定なら canonical `requirement.md` ではなく Issue-local `draft-requirement` artifact に留める。
- Epic Planning は、Issue Start 前に canonical Issue `design.md` / `plan.md` へ本文を一括配置してはならない。
- Issue Start 前の design / implementation plan 情報は Issue-local `draft-design` / `draft-plan` artifact に置く。
- canonical Issue `design.md` / `plan.md` は `issue start` 後、assurance classify/compose、`.assurance.json` / `authorized_profile`、draft artifact adoption、fresh spec-reviewer gate を経て作成・確定する。
- Epic report / handoff package は、各 Issue について `requirement state`、`draft-design path`、`draft-plan path`、`canonical design/plan state`、`handoff-ready` か `execution-ready` かを区別して記録する。

推奨 policy wording:

```md
Epic planning may create downstream Issue shells and dependency edges after the
Epic requirement/design/plan have passed their required Spec Authoring Gates.

Epic planning may promote canonical Issue requirement.md only when the Issue
purpose, scope/non-scope, acceptance criteria, parent trace, allowed local
delta, forbidden parent boundary changes, suggested grade, dependencies, and
open-question state are stable enough for fresh reviewer-gated handoff. If
they are not stable, Epic planning must create an Issue-local draft-requirement
artifact instead.

Epic planning must not batch-author canonical Issue design.md or plan.md
content before issue start. Before Issue planning, canonical Issue design.md
and plan.md must remain compose placeholders, not hand-written draft bodies.

Pre-start design and implementation-plan material belongs in Issue-local
draft-design and draft-plan artifacts. These artifacts are handoff evidence
only; they do not imply phase promotion, execution readiness, reviewer pass,
issue readiness, or issue finish.

After issue start, Issue Planning must run the current guidance, classify
assurance, read .assurance.json / authorized_profile, run assurance compose,
integrate relevant draft artifacts through the Evidence Adoption Ledger, and
obtain fresh spec-reviewer passes before the Issue can become execution-ready.
```

## option comparison / 選択肢比較

| 選択肢 | 評価 | 利点 | 主な破綻点 | 採否 |
| --- | --- | --- | --- | --- |
| A: Epic Planning が Issue requirement/design/plan canonicals を一括作成 | upfront の整合性は高く見えるが、draft evidence と canonical authority を混同する。 | Epic 時点で全体像を見やすい。 | `issue start` / assurance compose / authorized_profile と衝突し、stale plan や偽の execution readiness を生む。 | 不採用 |
| B: canonical requirement + Issue-local draft-design/draft-plan artifact | Issue の分割品質と canonical boundary を両立しやすい。 | handoff 品質を保ちつつ design/plan authority leak を防ぐ。 | requirement の安定性を過信すると canonical requirement も stale になる。 | 採用ベース |
| C: Issue shell のみ作成し、すべて JIT | pre-start stale risk は最小になる。 | 不確実性が極端に高い Epic では有効。 | cross-Issue の抜け漏れ、重複、依存順破綻を検出しにくく、agent handoff が弱い。 | デフォルト不採用 |
| D: controlled B/B+ hybrid | B に requirement stability 条件と skip/fallback evidence を加える。 | handoff 品質、freshness、canonical authority、assurance gate のバランスが最もよい。 | draft artifact を canonical と誤読しない validation が必要。 | 推奨 |

## deep-consultant / ChatGPT-5.5 Pro 比較

一致点:

- どちらも、Issue Start 前に canonical Issue `design.md` / `plan.md` へドラフト本文を置くことを不適切と判断した。
- どちらも、pre-start design/plan は Issue-local `draft-design` / `draft-plan` artifact として保持すべきと判断した。
- どちらも、canonical Issue `requirement.md` は Epic Planning で固定しうるが、安定性と reviewer-gated handoff に耐えることが条件だとした。
- どちらも、現 `epic-00270` は Issue shell と requirement を維持し、design/plan 本文を artifact へ退避し、canonical design/plan を placeholder に戻す migration が妥当だとした。
- どちらも、この判断は ADR 化に値すると判断した。

差分:

- Deep consultant は「B を正式ポリシー化」と表現した。
- ChatGPT-5.5 Pro は「Option D: constrained B/B+ hybrid」と表現し、canonical requirement を作る条件をより明示した。
- 統合判断としては、B を基本形としつつ、requirement stability と skip/fallback evidence の条件を加えた D/B+ hybrid を採用候補とする。

## unverified / 未検証事項

まだ確認していないこと:

- この研究結果を正式 ADR として採用するか。
- 現在 canonical path にある `iss-00271` から `iss-00276` の `design.md` / `plan.md` 本文を、どのタイミングで Issue-local `draft-design` / `draft-plan` artifact へ migration するか。
- migration 後の fresh spec-reviewer gate を、Epic Planning の再レビューとして実施するか、最初の Issue Start 直前 gate として実施するか。
- `workflow_epic.md` の handoff package 例に `draft-plan` を明示追加する具体的な文言。
- `spec-dock validate` や smoke test で、pre-start canonical `design.md` / `plan.md` の authority leak を検出するかどうか。

確認できない理由:

- これらは技術的に自動決定できる部分もあるが、workflow governance と既存 Epic migration 方針に関わるため、ADR 採用または migration Issue の scope として扱うのが適切である。

## question candidates / 質問候補

source-grounded に解けず、人間判断が必要な候補:

- この方針を ADR として採用するか。
- 現 `epic-00270` の不整合を、このまま本 Epic の一部として即時 migration するか、先に ADR 化してから Issue scope へ反映するか。

pressure-test question として切り出すべき候補:

- canonical Issue `requirement.md` を Epic Planning で固定してよい安定性条件を、workflow docs と template にどの粒度で埋め込むか。
- final delivery Issue のように前段結果に強く依存する Issue では、`draft-plan` をどれほど薄くするべきか。
- `handoff-ready` と `execution-ready` の状態名を workflow docs / report templates / validation に明示するか。

質問せずに解決できた候補:

- Issue Start 前に canonical `design.md` / `plan.md` を本文入りにするべきかどうか。
  - 結論: すべきではない。Issue-local draft artifact に置く。
- Epic Planning が Issue の分割と依存順を管理すべきかどうか。
  - 結論: 管理すべき。shell / dependency / requirement stability / draft artifacts / handoff package は Epic 側の責務に含める。

## terminology conflicts / 用語衝突

衝突している用語:

- `draft design.md` / `draft plan.md`
- `canonical docs`
- `artifact`
- `handoff-ready`
- `execution-ready`
- `reviewer pass`
- `phase promotion`

既存 docs / code / tests / artifacts / primary sources での使われ方:

- `design.md` / `plan.md` は canonical doc path であり、Issue template では compose 前 placeholder として扱われる。
- `draft-design` / `draft-plan` は artifact type であり、Issue-local evidence surface として扱われる。
- reviewer pass は、何を review target としたかによって意味が変わる。draft artifact handoff package への pass は、composed canonical Issue `design.md` / `plan.md` の phase promotion pass ではない。
- `handoff-ready` は Epic Planning が次の Issue Planning へ渡せる状態であり、`execution-ready` は Issue Planning が canonical design/plan と reviewer gate を満たした状態である。

判断が必要な理由:

- canonical path に「draft」と書かれた本文があると、agent や workflow が authority を誤認する。
- report が draft artifact review と canonical phase promotion を混同すると、Issue Start 後の assurance compose / fresh review が省略される危険がある。

## edge cases / 具体シナリオ

edge case:

- 要件自体がまだ不確実な Issue。

影響:

- canonical `requirement.md` も固定せず、Issue-local `draft-requirement` artifact に留める。Epic report には open question と skip/fallback evidence を残す。

edge case:

- final delivery / PR 作成 / manual test Issue のように、前段 Issue の実装結果に強く依存する Issue。

影響:

- `draft-plan` は checklist / gate / expected evidence までに留め、具体的な実装手順や検証コマンドは Issue Start 後に確定する。

edge case:

- Epic Planning 中に cross-Issue の重複や抜け漏れを検出したい。

影響:

- Epic plan は Issue matrix、dependency chain、parent trace、allowed local delta、forbidden parent boundary change、required evidence を持つ。ただし design/plan canonical body は持たない。

edge case:

- Issue Start 後に authorized profile が想定と違った。

影響:

- draft-design / draft-plan は EAL 経由で採用・部分採用・棄却・supersede を記録する。canonical `design.md` / `plan.md` は profile template に合わせて再構成する。

## implications / 判断への含意

Requirement への含意:

- Epic requirement / plan から downstream Issue requirement へ渡すべき情報は明確化する。
- ただし Issue requirement を Epic Planning で canonical 化する条件として、安定性と reviewer-gated handoff readiness を明示する必要がある。

Design への含意:

- canonical Issue `design.md` は `issue start` 後、assurance compose と current repo investigation を経て作成する。
- Epic Planning 中の design draft は artifact として扱い、canonical design への採用は EAL で追跡する。

Plan への含意:

- canonical Issue `plan.md` は `issue start` 後、latest state と authorized profile を踏まえて作成する。
- Epic Planning 中の implementation plan draft は artifact として扱い、step-level 実行順や TDD cadence を過剰に固定しない。

ADR への含意:

- この判断は長期的な workflow governance、canonical authority、artifact evidence、`issue start` の責務境界に関わるため ADR 化が適切である。

Workflow docs / skills への含意:

- `workflow_epic.md` は `draft-plan` を handoff package に明示追加する。
- Epic Planning skill は canonical Issue design/plan を pre-start に書かないことを hard rule として明示する。
- Epic Execution skill は `handoff-ready` と `execution-ready` を分け、placeholder design/plan を「実行不能」ではなく「Issue Planning に route すべき状態」と扱う。
- Issue Planning skill は draft artifact adoption と canonical compose の順序を明示する。
- Smoke test / validation は、未開始 Issue の canonical `design.md` / `plan.md` に draft body がある状態を検出できるとよい。

## current epic-00270 migration proposal

現 `epic-00270` については、次の移行が妥当である。

1. `iss-00271` から `iss-00276` の Issue shell と dependency chain は維持する。
2. 各 Issue の canonical `requirement.md` は、現時点では安定している前提で維持する。ただし後続レビューで不安定と判断された場合は artifact へ戻す。
3. 各 Issue の現 canonical `design.md` / `plan.md` 本文は misplaced draft evidence として扱う。
4. `spec-dock new artifact draft-design --issue <issue-id>` と `spec-dock new artifact draft-plan --issue <issue-id>` で Issue-local artifact を作成し、現本文を退避または要約する。
5. 各 Issue の canonical `design.md` / `plan.md` を compose placeholder に戻す。
6. 各 Issue `report.md` へ、requirement は canonical として保持し、design/plan は draft artifact へ移動し、canonical design/plan promotion は `issue start` / assurance compose / fresh review 後に行うと記録する。
7. Epic `plan.md` / `report.md` から「canonical Issue design/plan が作成済み」と誤読される表現を削り、batch review は handoff package consistency review として再分類する。
8. migration 後に fresh spec-reviewer を通し、`iss-00271` から通常の `issue start` / Issue Planning / Issue Execution に進む。

## validation checks / 検証観点

- 未開始 Issue の canonical `design.md` / `plan.md` が `awaiting-assurance-compose` placeholder であること。
- 未開始 Issue の design/plan draft が Issue-local `artifacts/` 配下の `draft-design` / `draft-plan` artifact として存在すること。
- Epic report が draft artifact review と canonical Issue phase promotion を混同していないこと。
- Issue report が canonical requirement の維持、draft design/plan artifact の存在、canonical design/plan pending 状態を明示していること。
- `issue start` 後、`.assurance.json` / `authorized_profile` が存在し、canonical design/plan が profile に従って compose されていること。
- draft artifact adoption が Evidence Adoption Ledger で採用・部分採用・棄却・supersede のいずれかとして記録されていること。
- stale / blocked の EAL entry が残ったまま phase promotion されていないこと。

## リスク/制約

- draft artifact を増やしすぎると参照性が落ちるため、Epic handoff package は artifact path index を持つ必要がある。
- 一方で、draft を canonical path に混ぜると authority leak が起きるため、参照性のために canonical boundary を崩してはいけない。
- canonical Issue requirement を Epic Planning で固定する場合も、requirement stability criteria と reviewer gate を明示しないと stale risk が残る。
- `draft-plan` は Issue-local artifact type として扱う必要がある。Epic-scope artifact にまとめるだけでは、Issue Start 後の EAL adoption path が弱くなる。

## 反映先

候補:

- ADR: Epic Planning における downstream Issue canonical/design/plan boundary
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_issue.md`
- `.agents/skills/spec-dock-epic-planning/SKILL.md`
- `.agents/skills/spec-dock-epic-execution/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `epic-00270/plan.md`
- `epic-00270/report.md`
- `iss-00271` から `iss-00276` の artifact / report

## 参考

- Deep consultant final recommendation: `019f214d-3d10-7833-a4dc-3bb85bc15e8f`
- ChatGPT-5.5 Pro output: Oracle session `specdock-issue-planning-policy`
- ChatGPT prompt/output scratch:
  - `/private/tmp/codex-agent-work/501/session-20260702t053321z-specdock-epic-issue-planning-analysis-544cc470/chatgpt-prompt.md`
  - `/private/tmp/codex-agent-work/501/session-20260702t053321z-specdock-epic-issue-planning-analysis-544cc470/chatgpt-output.md`
