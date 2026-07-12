---
種別: research
ID: "20260707t143719z-research"
タイトル: "Workflow first ChatGPT authoring redesign provisional analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295"]
関連: []
scope: "epic"
scope_id: "epic-00295"
created_at: "2026-07-07T14:37:19Z"
created_by: "codex"
status: "provisional"
authority: "evidence_only"
adoption_status: "unreviewed"
derived_from:
  - "ChatGPT Use session: specdock-workflow-first-chatgpt-authoring-2"
  - "artifacts/20260707t140041z-01-research-chatgpt-workflow-integration-analysis.md"
  - "artifacts/20260707t140041z-research-authoring-pack-install-architecture-analysis.md"
reflected_to: []
---

# Workflow first ChatGPT authoring redesign provisional analysis

## 位置づけ

この research は、ChatGPT-Use / GPT-5.5 Pro Extended に依頼した workflow-first redesign analysis の要約です。

重要: この ChatGPT 依頼は、ユーザー interview 回答前に開始されたため、`pre-interview provisional` として扱います。ユーザー回答により、最優先体験は **Option A: 大きな仕事を一括で計画する体験**、かつ **A の先に B がある / A と B はセット** と確定しました。この research は、後続 requirement / design / plan でその回答に照らして再採用判断します。

## ChatGPT 実行メモ

- session: `specdock-workflow-first-chatgpt-authoring-2`
- model: `gpt-5.5-pro`
- mode: Pro Extended
- files: 12
- prompt estimate: 約 45,961 tokens
- caveat:
  - GitHub connector では current branch `codex/authoring-pack-installed-runtime` が開けず、default branch `main` と添付 files を基準に分析した。
  - code patch、tests、`spec-reviewer`、runtime command 実行、installer packaging verification は未実施。

## 主要結論

ChatGPT の結論は、`epic-00295` は scripts / runtime command から再設計せず、まず SpecDock の実利用を workflow mode に分け、その mode を運用できる skill / skill mode を定義し、最後に runtime command を導出するべき、というものだった。

中核提案:

1. ChatGPT GPT-5.5 Pro Extended は `ChatGPT Batch Evidence Lane` として扱う。
2. Codex は local orchestrator / canonical adopter として残す。
3. `spec-dock-issue-planning` は分割せず、`zero-base` と `draft-adoption` の 2 mode を明示する。

## Use-case taxonomy

ChatGPT は、SpecDock の実利用を以下の mode に分ける案を出した。

| Mode | 入口 | 主な成果物 | ChatGPT 利用 | Codex-local authority |
|---|---|---|---|---|
| `initiative-planning` | 大きな Initiative | Initiative docs / Epic portfolio | Initiative -> Epic slicing | 既存 fit / canonical adoption / Epic 作成 |
| `epic-planning` | Epic | Epic docs / Issue handoff package | Epic -> Issue slicing / Issue draft pack | Issue 作成 / dependency mutation / Epic canonical docs |
| `issue-planning: zero-base` | 単一 Issue / vague request | Issue canonical requirement/design/plan | optional design/plan brainstorm | clarification / profile authority / canonical docs / reviewer gate |
| `issue-planning: draft-adoption` | Epic handoff / pre-start drafts | adopted canonical Issue docs | draft refinement / consistency check | EAL / draft disposition / assurance compose / fresh reviewer |
| `epic-execution` | reviewed Epic plan | one Issue at a time coordination | 原則使わない。planning repair に戻す | dependency readiness / issue start / routing / PR policy |
| `issue-execution` | execution-ready Issue | implementation / report / PR delivery evidence | 原則使わない。spec gap は planning に戻す | tests / local edits / reviewer gates / issue finish |

## Proposed workflow model

提案されたモデルは、`Scope workflow x Evidence lane x Authority gate` の 3 層。

```text
Scope Router
  spec-dock-hub
    -> initiative-planning
    -> epic-planning
    -> issue-planning(mode=zero-base | draft-adoption)
    -> epic-execution
    -> issue-execution

Optional Evidence Lane
  local source grounding
    -> ChatGPT batch pack prepare
    -> backend invocation
    -> ZIP/tree review
    -> mode-specific validation
    -> staged evidence / EAL candidate

Authority Gate
  Codex adoption
    -> canonical requirement/design/plan/report rewrite
    -> fresh spec-reviewer
    -> handoff-ready or execution-ready
```

重要な状態名:

- `handoff-ready`
- `execution-ready`

この 2 つは混ぜない。Epic Planning から渡る draft pack は handoff-ready の材料であり、Issue implementation を始める execution-ready ではない。

## Skill set / skill modes

維持する skill:

- `spec-dock-hub`
- `spec-dock-initiative-planning`
- `spec-dock-epic-planning`
- `spec-dock-epic-execution`
- `spec-dock-issue-planning`
- `spec-dock-issue-execution`
- `spec-dock-clarification`
- `spec-dock-adr-facilitation`

追加候補:

- `spec-dock-authoring-batch`

ただしこれは planning leaf skill ではなく、各 planning skill から呼ばれる cross-scope evidence producer とする。

`spec-dock-issue-planning` は別 skill に分けず、同一 skill 内で以下を明示する提案だった。

- `zero-base`
- `draft-adoption`

## Planning redesign

### Initiative Planning

ChatGPT は Initiative -> Epic slicing、risk / dependency portfolio、Epic candidate portfolio を担当。

Codex は既存 Initiative / Epic fit、canonical adoption、Epic 作成を担当。

### Epic Planning

ChatGPT Batch Evidence Lane の primary use case。

ChatGPT は以下を生成:

- Epic design / plan candidate
- Issue list
- responsibility boundary
- dependency order
- per-Issue draft requirement/design/plan

Codex は以下を担当:

- Issue 作成
- Issue-local draft artifact placement
- dependency command
- Epic canonical docs
- fresh `spec-reviewer`

### Issue Planning: zero-base

ユーザーとの quick clarification と Codex の対話性が主。

ChatGPT は requirement が固まった後の design / plan brainstorm に限定。

### Issue Planning: draft-adoption

Epic handoff package と draft artifacts を読み、claim ごとに採否判断する。

結果:

- EAL disposition
- canonical requirement/design/plan
- fresh `spec-reviewer`
- execution handoff readiness

## Execution redesign

Epic Execution は one-Issue-at-a-time coordinator。

Issue start 後の routing:

```text
if canonical Issue docs missing/template/draft-only:
  route -> spec-dock-issue-planning(mode=draft-adoption)
elif requirement/design/plan gaps discovered:
  route -> spec-dock-issue-planning(mode=zero-base or repair)
elif canonical docs reviewer-passed and plan executable:
  route -> spec-dock-issue-execution
else:
  record structural blocker
```

Issue Execution は ChatGPT lane から切り離す。実装中に spec gap が出た場合は ChatGPT で即興補完せず、Issue Planning / clarification に戻す。

## Runtime / script architecture

ChatGPT は、primary UX を以下にする案を提示した。

```text
./spec-dock/scripts/spec-dock authoring ...
```

提案 command group:

```text
./spec-dock/scripts/spec-dock authoring chatgpt prepare
./spec-dock/scripts/spec-dock authoring chatgpt invoke
./spec-dock/scripts/spec-dock authoring chatgpt review
./spec-dock/scripts/spec-dock authoring chatgpt stage

./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates
./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill
```

`adopt` command は作らない方がよい、という提案だった。canonical adoption は Codex が docs を rewrite し、`report.md` に EAL / Spec Authoring Gate を記録し、fresh reviewer を通す workflow action であり、ZIP stage の副作用にしてはいけない。

## Migration plan

ChatGPT 提案:

1. workflow decision artifact を作成する。
2. Epic canonical docs を workflow-first に更新する。
3. shipped workflow docs を追加・更新する。
4. skills を更新する。
5. runtime command design / implementation を行う。
6. safety / validation を追加する。
7. real Epic planning と Issue draft-adoption で dogfood する。

## ユーザー回答による補正

この ChatGPT 暫定分析では Issue Planning の `draft-adoption` が強めに扱われている。しかしユーザー回答により、最優先は次のように補正された。

- 第一優先: Option A、大きな仕事を一括で計画する体験。
- A と B はセット。
- A の先に B がある。
- 主要 workflow は、大きな仕事をスライスし、Epic / Issue に分解し、各 Issue の実装直前に正式仕様へ整えて実装する流れ。

したがって後続 design / plan では、`initiative-planning` / `epic-planning` の batch slicing を主軸にし、その下流に `issue-planning:draft-adoption` を置く構造として再解釈する。

## 採用候補

採用候補:

- workflow-first の順序。
- `ChatGPT Batch Evidence Lane` の概念。
- A と B をつなぐ `handoff-ready -> draft-adoption -> execution-ready` の状態分離。
- `spec-dock-authoring-batch` のような cross-scope evidence producer skill。
- `spec-dock-issue-planning` の `zero-base` / `draft-adoption` mode。
- `adopt` command を作らず、canonical adoption は Codex / reviewer gate に残す方針。

補正または再検討:

- ChatGPT の「Issue Planning は分割せず mode 化」提案は、ユーザー回答を踏まえて再評価する。
- 新 skill 名は `spec-dock-authoring-batch` がよいか、`spec-dock-chatgpt-authoring` がよいか未確定。
- Initiative-scale execution skill は今回作らず future hook に留める提案だが、大規模 work を重視するユーザー意図に照らして再検討余地がある。
