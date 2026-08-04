---
種別: 実装計画書（Issue）
ID: "iss-00354"
タイトル: "ChatGPT Context and Attachment Contract"
状態: "draft"
作成者: "ChatGPT Blue Team authoring planner"
最終更新: "2026-08-04"
依存: ["requirement.md", "design.md"]
親: ["epic-00331", "init-00322"]
---

# iss-00354 ChatGPT Context and Attachment Contract 実装計画書

> **Candidate / evidence-only**  
> 本計画は `CAND-ISS-00354-20260803T172642Z` の未採用案である。repository 変更、Red Team review、commit、PR、merge を
> 実施していない。

## 1. 実装方針

Issue #334 で完成済みの Issue Planning lifecycle を土台に、input boundary だけを増分変更する。

- provider source を正本とする。
- old behavior を characterization test で固定してから、Option A / C の failing test を追加する。
- minimal body、direct path transport、thread policy を別 step に分ける。
- output ZIP / Review JSON / Candidate / Human / apply の regression を各 step で通す。
- dogfood projection、skills、docs、親 Epic consistency を一つの closure に含める。
- Oracle capability が不足する場合は停止し、personal wrapper / API へ逃げない。

## 2. Source HEAD 時点の baseline

| 項目 | Baseline |
|---|---|
| Branch / HEAD | `codex/iss-00354-chatgpt-context-contract` / `88a9fdb567f17f50bee421862d3b7859a5eb6384` |
| Issue docs | approved front matter を持つが本文は Standard template の placeholder |
| Planning input | canonical / relevant source individual read + scanner + generated prompt pack |
| CLI | optional `--context-manifest` |
| Oracle input | one generated directory via `--file` |
| Session | role invocation ごとに new random session。同 invocation recovery のみ |
| Planning output | exact authoring ZIP |
| Review output | strict closed JSON |
| Authority | Candidate / Review evidence-only、Human-approved applyのみmanaged write |
| Projection | provider / installed / dogfood copiesあり |
| Assurance | `standard` provisional |

## 3. 変更対象

### 3.1 Primary provider code

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`
- 必要なら `application/ports.py` / bootstrap wiring。ただし既存 port ownership を確認して限定する。

### 3.2 Provider resources / skills

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- clarification resource convention / skill guidance（runtime public command は追加しない）。

### 3.3 Tests

- `tests/unit/application/test_issue_planning_prompt.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/infra/test_issue_planning_chatgpt.py`
- `tests/unit/commands/test_issue_planning.py`
- `tests/cli_runtime/test_chatgpt_cli.py`
- `tests/integration/test_issue_planning_e2e.py`
- installed projection / wrapper tests のうち resource path を固定する箇所。

### 3.4 Docs

provider と dogfood の双方:

- `docs/workflow_issue.md`
- `docs/workflow_chatgpt_authoring_pack.md`
- `docs/authoring/chatgpt-pack.md`
- Issue Planning / Clarification skill。
- `epic-00331` Requirement / Design の矛盾箇所。
- Issue #354 canonical three documents / report は Human-approved adoption 時だけ更新する。

## 4. Milestone S01 — Capability characterization と regression boundary

### 4.1 目的

production code を変える前に、direct Oracle だけで次を満たせるか確認する。

1. directory path を recursive attachment として受け取る exact contract。
2. static directory と dynamic file を同 invocation へ渡す contract。
3. same Blue conversation を継続する direct Oracle contract。
4. attachment failure の exit / session status / artifact behavior。

### 4.2 Red

focused infra tests に、fake executable の help / argv / session behavior を使った characterization test を追加する。

- directory path を一つの `--file` operand として保持する。
- multiple direct attachment operand の exact order。
- continuation start / resume の exact command。
- unsupported capability で prompt submission 0。
- personal wrapper / API fallback invocation 0。
- output snapshot behavior 不変。

real Oracle を必要とする capability smoke は opt-in / local integration とし、unit test が undocumented flag を
発明しない。

### 4.3 Green

- `_ROOT_CAPABILITIES` / `_SESSION_CAPABILITIES` を実測 interface に合わせて更新する。
- application へまだ新 architecture を入れず、supported / unsupported 判定だけを明示する。
- capability receipt は report に command surface と version だけを content-free に記録する。

### 4.4 Stop gate

次のいずれかなら S02 へ進まない。

- directory attachment unsupported。
- multiple path unsupported かつ conversion なしの表現がない。
- continuation unsupported。
- supported interface が personal wrapper にしかない。

### 4.5 Verification

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_chatgpt.py
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

## 5. Milestone S02 — Operation resource layout と minimal body

### 5.1 Red

`test_issue_planning_prompt.py` を新契約へ書き換える。

- planning / review / revision の body に exact identity、authority、output がある。
- detailed instruction text、13 heading contract、4 diagram contract、attachment SHA index が body にない。
- `prompt.md` と `attachments/` path が operation ごとに分離される。
- attachments へ file を追加しても registry / code を変更しない。
- reviewer は fresh / read-only / defect-only。
- revision は selected P0 / P1 identity を扱う。
- provider / installed resource resolver が new root を解決する。

### 5.2 Green

- `resources/operations/{planning,review,revision}/` を作る。
- old `planner-prompt.md`、`reviewer-prompt.md`、`revision-prompt.md`、
  `transport-output-contract.md` の内容を minimal `prompt.md` と detailed `attachments/*.md` に分割する。
- `issue_planning_prompt.py` に operation registry と minimal body renderer を追加する。
- onboarding の固定 13 H2 / 4 PlantUML text を削除し、subordinate status と必要な diagram guidance へ縮小する。

### 5.3 Refactor

- shared authority wording を code concatenation で重複排除しない。各 operation directory を self-contained にする。
- generic unknown operation fallback を作らない。
- body field ordering を deterministic にする。

### 5.4 Verification

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py -q
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  tests/unit/application/test_issue_planning_prompt.py
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

## 6. Milestone S03 — Input model を bytes から path へ変更

### 6.1 Red

- `SynthesizedPlanningPrompt` が attachment bytes / classification / SHA を保持しない。
- directory fixture 内に nested、hidden、symlink、FIFO を作っても prompt synthesis が tree を触らない。
- `Path.rglob`、`iterdir`、`resolve`、`read_bytes`、`stat` を monkeypatch で failure にしても synthesis が成功する。
- optional operator attachment directory の path text が変更されない。
- source / operator content scanner が invocation path で呼ばれない。

### 6.2 Green

- `SynthesizedChatGptOperation` または既存 type の互換を切り、`attachment_paths` を導入する。
- `PlanningPromptAttachment`、input SHA index、file-safe-read helpers、hard size / count constants を削除する。
- `PlanningContext` から `relevant_source_paths` / `operator_context` を formal prompt materialization 用 field として
  除去する。source staleness に必要な typed state は別 contract へ残す。
- `_attachments_match_source_manifest` と `_exact_attachments_have_sensitive_content` を transport path から削除する。
- body dynamic identity に old content scanner を適用しない。typed identity validation は維持する。

### 6.3 Refactor

- source preflight state と ChatGPT attachment state を別 object にする。
- output expectation type は変更を最小化する。
- static / dynamic / operator paths の top-level order を operation assembler が明示する。

### 6.4 Verification

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py -q
```

## 7. Milestone S04 — Direct Oracle attachment transport

### 7.1 Red

`test_issue_planning_chatgpt.py` に次を追加する。

- adapter argv が static directory path を direct `--file` operand にする。
- dynamic Candidate / Review path を original path のまま渡す。
- input `TemporaryDirectory/prompt-pack` を作らない。
- `.specdock-authoring-pack`、`context-*.md`、`manifest.json`、`source-manifest.json`、
  `provenance.json`、`stale-if.json` を作らない。
- directory tree API を一度も呼ばない。
- Oracle attachment error で entry exclusion / retry / conversion 0。
- existing managed Chrome / env / executable / output tests が pass。

### 7.2 Green

- `_write_transport_pack` と input pack generation を削除する。
- `invoke_issue_planning_chatgpt` が synthesized `attachment_paths` を direct argv へ追加する。
- output snapshot 用 private staging だけを残す。
- supported Oracle capability に従う exact repeated file syntax を実装する。
- attachment submission failure を existing content-free public reason へ正規化する。

### 7.3 Refactor

- argv assembly を pure function に分離し、no-prewalk test を容易にする。
- prompt submission は一回だけ。
- same invocation recovery path も initial invocation と同じ attachment semantics を保持する。

### 7.4 Verification

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run pytest tests/integration/test_issue_planning_e2e.py -q
```

## 8. Milestone S05 — Planning / Review / Revision orchestration と CLI cutover

### 8.1 Planning create

#### Red

- `--context-manifest` が help / parser から消える。
- optional repeatable `--attachment-dir` 相当が exact path を request へ渡す。
- missing / unusual path を CLI が content inspect しない。
- provider static planning directory は常に追加される。
- exact GitHub preflight / postflight と Candidate publication は不変。

#### Green

- `PlanningCreateRequest.context_manifest_path` を directory path collection へ置換する。
- `_load_planning_context_manifest` と merge helpers を削除する。
- canonical docs は GitHub exact HEAD から ChatGPT が読む。formal route で local file text attachment を再生成しない。
- help / skill / docs を hard cutover へ更新する。

### 8.2 Review

#### Red

- fresh Red request が必ず new thread を要求する。
- Candidate ZIP path が copy / rename されない。
- reviewed identity digest は formal identity として body / output validator に bind される。
- Blue binding は read / mutate されない。

#### Green

- `review_prompt_synthesizer` の `PlanningPromptAttachment` 生成を direct evidence path / compact body identity へ置換する。
- `reviewed-identity.json` / `reviewed-identity-sha256.txt` の temporary input file が不要なら body identity へ移す。
- Oracle output closed JSON parser と identity comparison は維持する。

### 8.3 Semantic revision

#### Red

- prior Candidate、exact Review、revision request が original path。
- selected P0 / P1 と preserved assumptions が minimal body identity。
- prior canonical docs の duplicate attachment copy を作らない。
- revised ZIP validation / publication 不変。
- mechanical lane 不変。

#### Green

- `revision_prompt_synthesizer` を operation assembler へ置換する。
- exact Candidate / Review validator を invocation 前に維持する。
- static revision directory と dynamic evidence paths を direct Oracle へ渡す。

### 8.4 Verification

```bash
uv run pytest tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/application/test_issue_planning.py -q
```

## 9. Milestone S06 — Blue continuity / fresh Red

### 9.1 Red

- first planning starts Blue。
- same identity / lineage semantic revision continues verified Blue。
- review always starts fresh Red。
- source HEAD change invalidates Blue。
- unavailable handle + exact lineage starts new Blue with complete current inputs。
- ambiguous lineage blocks before submission。
- public result / Candidate / Review does not contain provider handle。
- no raw transcript persistence。
- same invocation timeout recovery remains distinct from cross-operation continuity。

### 9.2 Green

- `ChatGptThreadPort` と `BlueThreadBinding` を domain / application boundary に追加する。
- provider-owned private store を existing Oracle home / state convention に合わせて実装する。
- binding key は repository / branch / Issue / lane とし、source HEAD / Candidate lineage を record に保持する。
- planning / semantic revision は reuse policy を application で判定する。
- review は `fresh_red` request を強制し、binding store に reusable Red state を残さない。
- new Blue は current minimal body と current static / dynamic attachment paths を完全に送る。
- Human confirmation が必要な case を content-free blocked result へ正規化する。

### 9.3 Refactor

- provider handle を serialization、repr、equality、CLI output から除外する。
- internal supersession は raw handle ではなく digest / generation で追跡する。
- retention / cleanup は existing Oracle lifecycle を尊重し、独自 transcript archive を作らない。

### 9.4 Stop gate

S01 で direct continuation interface が確認できなかった場合、本 milestone は実装しない。wrapper fallback を使わず、
capability gap と後続設計を report する。

### 9.5 Verification

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/application/test_issue_planning.py \
  tests/integration/test_issue_planning_e2e.py -q
```

## 10. Milestone S07 — Provider projection、docs、parent consistency

### 10.1 Provider / dogfood

- provider runtime / resource / skill / docs を更新する。
- project の既存 projection / installer workflow を実行する。
- dogfood copy を手編集しない。
- recursive tree byte parity test を追加または更新する。
- resource file 増減を fixed allowlist が拒否しないことを確認する。

### 10.2 Skill / docs

更新内容:

- minimal body と detailed attachments。
- `--attachment-dir` hard cutover。
- Option C の operator responsibility。
- input manifest / scanner を持たない。
- output ZIP / JSON safety は維持。
- Blue continuity / fresh Red。
- personal wrapper は runtime dependency ではない。
- normal transport failure に委ねる。
- clarification は reusable convention、public wiring は follow-up。

### 10.3 Parent Epic

`epic-00331` Requirement / Design の次の矛盾だけを修正する。

- detailed instruction の本文集中。
- attachments reference-only。
- attachment SHA / manifest を input authority とする記述。
- phase ごとの session policy。

Issue ordering、scope allocation、Candidate / Human lifecycle は変更しない。

### 10.4 Issue docs / report

この Candidate をそのまま canonical overwrite しない。Human が採用する場合:

1. Candidate preservation。
2. Evidence Adoption Ledger。
3. canonical three docs へ main orchestrator が反映。
4. fresh spec review。
5. assurance rebind。
6. implementation readiness gate。

## 11. Milestone S08 — Regression、quality gate、closure evidence

### 11.1 Focused suite

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py -q
```

### 11.2 Static quality

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py

uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

repository の canonical `make lint` / ordinary pytest lane が Issue #334 report で利用されている場合、focused suite 後に
同じ entrypoint を実行する。

### 11.3 Explicit contract checks

- grep / test で runtime path に `context-NNN.md`、input manifest generation、attachment scanner が残っていない。
- output `manifest` / Candidate provenance を誤って削除していない。
- provider / dogfood parity。
- personal wrapper path / API fallback / default branch fallback 0。
- attachment directory prewalk 0。
- Reviewer fresh thread reuse 0。
- provider handle public serialization 0。
- old `--context-manifest` docs 0。
- parent Epic contradiction 0。

### 11.4 Review gates

- fresh code review は exact pushed HEAD を対象にする。
- P0 / P1 だけを blocking repair loop へ戻す。
- P2 / P3 は non-blocking follow-up として記録する。
- Review PASS は Human adoption / execution-ready ではない。
- PR / merge / Issue close は別 workflow。

## 12. テスト観点マトリクス

| Behavior | Unit | Integration / E2E | Regression |
|---|---|---|---|
| minimal body | prompt test | fake Oracle captures prompt | exact GitHub / output wording |
| direct directory path | infra argv test | fake Oracle sees directory operand | no tree walk |
| dynamic path passthrough | application + infra | review / revision chain | Candidate bytes unchanged |
| no input manifest | infra filesystem assertion | E2E pack inventory | output manifest remains |
| normal transport failure | infra result mapping | fake Oracle failure | no fallback |
| Blue reuse | thread store / adapter | planning → revision | no handle leak |
| fresh Red | application | Candidate N review | no PASS reuse |
| continuity recovery | application / store | invalid binding scenario | Human block ambiguity |
| output ZIP | existing parser tests | create / revise | exact root / inventory |
| Review JSON | existing strict parser | review | duplicate / unknown key reject |
| provider projection | resource parity | installer smoke | file add/remove no code change |
| CLI cutover | command tests | CLI runtime | old flag rejected |

## 13. 移行順と互換性

1. S01 capability gate。
2. new resources と new model を provider に追加。
3. application を direct path へ切替。
4. adapter の generated pack を削除。
5. CLI / docs を同 commit boundary で hard cutover。
6. thread continuity を追加。
7. projection / parent docs。
8. full regression。

partial dual-mode は作らない。old `--context-manifest` と new directory mode を同時維持すると、同一 operation に
inspection path と no-inspection path が混在し、契約が不明確になるためである。

rollback は commit-level revert とする。runtime 内に legacy fallback switch を残さない。

## 14. 実装中の停止条件

次を検出した時点で mutation を止める。

- current branch / remote HEAD が source baseline から変化した。
- worktree に task scope 外の変更がある。
- Oracle capability characterization が不十分。
- direct attachment のために temporary copy / ZIP が必要。
- continuation のために personal wrapper が必要。
- output validator を緩める必要がある。
- provider / dogfood parity の生成経路を特定できない。
- clarification public command が必要になったが owning Issue がない。
- existing Candidate / Review / apply regression が失敗し、原因が本 Issue の intended input change ではない。
- P0 / P1 review finding が未解決。

## 15. Evidence と report 記録

Issue report には最低限次を記録する。

- implementation source HEAD / resulting HEAD。
- Oracle version と確認した attachment / continuation capability。
- provider paths と projection paths。
- removed old input contract。
- retained output / authority contract。
- focused / ordinary test commands と結果。
- provider / dogfood parity。
- Blue continuity / fresh Red behavior。
- normal transport failure scenario。
- remaining follow-up。
- Candidate / Review / Human authority boundary。
- PR / merge / Issue close 未実施ならその状態。

attachment contents、secret-like value、private absolute path、raw transcript、provider thread handle は記録しない。

## 16. Follow-up 候補

本 Issue の completion を阻害しない follow-up:

1. clarification の provider-owned direct Oracle public operation wiring。
2. other product-owned ChatGPT operations への operation directory convention 展開。
3. thread binding retention / cleanup の cross-operation policy が複数 scope に広がる場合の ADR triage。
4. Oracle capability version update policy。
5. optional operator tooling for preparing trusted attachment directories。ただし runtime scanner / classifier にはしない。

## 17. Definition of Done

- canonical requirement / design / plan が adopted and freshly reviewed。
- S01 stop gate を通過。
- Option A / C の tests が pass。
- old input pack / scanners / context manifest が production path から除去。
- direct Oracle、exact GitHub、output validators、Human gate が回帰なし。
- Blue continuity / fresh Red が direct Oracle の supported interface で実装済み、または unsupported capability として
  明示停止・再計画済み。
- provider / installed / dogfood parity。
- docs / skills / parent Epic consistency。
- focused + static + validation gates pass。
- report evidence 完了。
