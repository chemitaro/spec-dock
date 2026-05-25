---
doc_type: discussion
title: Static All Discussions Write Permission Analysis
created_at: "2026-05-25T01:02:11Z"
created_by_role: main-orchestrator
scope_id: iss-00127
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - src/spec_dock/assets/install_root/.codex/agents/system-architect.toml
  - src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/install_root/.codex/agents/system-architect.toml
  - src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md
adoption_status: unreviewed
reflected_to: []
---

# Static All Discussions Write Permission Analysis

## 背景

`iss-00127` では、system-architect / implementation-planner を canonical docs の author ではなく、scope-local `discussions/` に draft / analysis / report を残す delegated authoring agent として扱う方針を採用した。

この方針自体は維持する。一方で、直近の S04 実装では、静的 agent adapter を read-mostly fallback とし、実際の書き込み可能 path は `spec-dock delegated-authoring scoped-context --role ... --scope ... --discussion-file ...` によって、run ごとに 1 つの discussion file だけへ絞る設計になっている。

これは既存設定ファイルを直接毎回書き換える実装ではないが、実行のたびに runtime permission context を生成・注入する必要があり、運用上は「動的に agent の write boundary を組み立てる」仕組みになっている。

## 現状の問題点

### 1. 運用が過剰に複雑である

現在の `scoped-context --discussion-file` 方式では、sub-agent が discussion draft を 1 ファイル作るたびに、main orchestrator が対象 scope と対象 file name を解決し、外部 context TOML を生成し、その context を sub-agent 実行へ渡す必要がある。

これは、単一 issue の単一 draft だけを扱う場合には安全に見える。しかし、実際の harness engineering / context engineering では、次のようなケースが自然に発生する。

- 1 回の分析で initiative / epic / issue それぞれの `discussions/` に draft を残す。
- 1 つの epic の配下にある複数 issue について、設計 draft や実装計画 draft を連続して作成する。
- system-architect が複数 scope の設計論点を比較し、それぞれの scope に分割した discussion evidence を残す。
- implementation-planner が epic 全体計画と issue 別追加作業を同じ実行単位で整理する。

このたびに `--scope` / `--discussion-file` 単位の permission context を作る運用は、ユーザーの意図する file-based context persistence と相性が悪い。

### 2. サブエージェントの役割分類と実装がずれている

system-architect / implementation-planner は read-only specialist ではない。researcher / consultant / repo-analyst のような SSA 的 agent とは異なり、設計・計画の draft をファイルとして残す delegated authoring agent である。

一方で、現在の静的 adapter は read/write 表現だけを見ると read-only specialist に近く見える。これは「canonical docs は編集できない」と「discussion drafts は作成できる」を同時に表現できていない。

あるべき分類は次の通りである。

| 分類 | agent | write boundary |
|---|---|---|
| read-only specialist | researcher, consultant, deep-consultant, repo-analyst, spec-reviewer, code-reviewer, qa-reviewer など | no file write |
| scoped delegated author | system-architect, implementation-planner | all scope-local `discussions/` write |
| broad workspace worker | dev-coder, doc-writer, utility-worker など | task-scoped broad write |
| canonical authority | main orchestrator / spec-manager-like flow | canonical requirement / design / plan / report integration |

### 3. 1 ファイル exact write root は安全性に寄せすぎている

直近の D-013 では、post-run diff guard は write boundary の代替ではないとして、runtime scoped context で direct child Markdown 1 ファイルだけを write root にした。

この判断は reviewer findings に対する局所的な安全対策としては成立する。しかし、ユーザーが重視しているのは、sub-agent の context を会話内に揮発させず、repo docs の `discussions/` に直接残すことである。

したがって、write boundary を「1 ファイル exact root」まで狭めるよりも、次の二段構えにする方が今回の product direction に合う。

1. 実行前 permission は、system-architect / implementation-planner に全 scope の `discussions/` 書き込みを静的に与える。
2. 実行後 diff guard / front matter / review gate で、canonical docs や forbidden paths への変更を採用不可にする。

### 4. 動的 context 注入は設計の説明コストが高い

runtime scoped context は、Permission Profile / generated context / default_permissions / output path など、説明すべき概念が多い。

今回の delegated authoring v2 では、JSON/TOML authority graph や複雑な manifest 依存を削り、シンプルな file-based operation に寄せる方針である。にもかかわらず、`scoped-context --discussion-file` は別の形で複雑さを再導入している。

## あるべき状態

### 基本方針

system-architect / implementation-planner は、静的 permission として、すべての scope-local `discussions/` への書き込み権限を持つ。

ただし、この権限は canonical docs や implementation files への編集権限ではない。権限境界は次のように定義する。

Allowed:

```text
spec-dock/initiatives/*/discussions/
spec-dock/initiatives/*/epics/*/discussions/
spec-dock/initiatives/*/epics/*/issues/*/discussions/
```

Expected output files:

```text
<timestamp>-<kind>-<slug>.md
<timestamp>-<nn>-<kind>-<slug>.md
```

Forbidden:

```text
spec-dock/initiatives/**/requirement.md
spec-dock/initiatives/**/design.md
spec-dock/initiatives/**/plan.md
spec-dock/initiatives/**/report.md
src/
tests/
.agents/
.codex/
.github/
.env
.env.*
```

### 運用ルール

- system-architect / implementation-planner は `discussions/` に draft / analysis / discussion-local report を直接作成できる。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator が統合する。
- sub-agent が作成した discussion draft は `adoption_status: unreviewed` または `status: proposed` を持つ。
- main orchestrator は evidence adoption ledger / report / canonical docs へ採用判断を記録する。
- post-run diff guard は delegated output の採用資格を判定する。write permission を細かく生成するための前提にはしない。

### Permission 表現上の注意

理想は、Codex permission profile で上記の `**/discussions/` 相当を静的に表現することである。

ただし、現在の repo 内実装・TOML 例では、`:workspace_roots` は明示 path を `read` / `write` / `deny` で列挙する形が中心であり、glob write rule が host 側で確実に機能するかは未検証である。

したがって、実装前に小さな feasibility check を行う。

- `:workspace_roots` に glob path を置けるか。
- allow / deny の優先順位が期待通りか。
- `spec-dock/initiatives/**/discussions` を write にしつつ、canonical docs / src / tests / config を deny できるか。
- glob が使えない場合、静的に広すぎる `spec-dock/initiatives` write へ逃げるべきか、それとも permission model 側の制約として別案にするか。

現時点の推奨は、glob が使えるなら静的 all discussions write を採用する。glob が使えない場合でも、run ごとの 1 ファイル context 生成へ戻すのではなく、より単純な代替を検討する。

## 具体的な修正作業

### 1. issue docs の方針修正

対象:

- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`
- `spec-dock/active/issue/report.md`

修正内容:

- `scoped-context --discussion-file` を標準成功経路から外す。
- system-architect / implementation-planner の分類を `read-mostly fallback` ではなく `scoped delegated author` と明記する。
- write boundary を「target scope の exact discussion file」から「all scope-local discussions」へ変更する。
- D-013 は superseded / revised decision として report に追記する。
- plan の追加作業として、静的 permission 方式への修正 step を末尾に追加する。

### 2. static agent adapter の修正

対象:

- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- `.codex/agents/system-architect.toml`
- `.codex/agents/implementation-planner.toml`

修正内容:

- developer instructions から「static adapter is read-mostly fallback」「runtime scoped context required」「one direct child Markdown file only」という表現を削除または降格する。
- `default_permissions` の permission profile を、discussion authoring 用の静的 profile として表現する。
- 可能であれば `spec-dock/initiatives/**/discussions` 相当を write とする。
- canonical docs / implementation / tests / config / secrets は deny または禁止事項として明記する。
- host permission が glob を解釈しない場合は、その事実を tests / report に記録し、別案を採用する。

### 3. role skill の修正

対象:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
- `.agents/skills/spec-dock-system-architect/SKILL.md`
- `.agents/skills/spec-dock-implementation-planner/SKILL.md`

修正内容:

- 出力先を「main orchestrator が指定した exact file」ではなく「scope-local flat `discussions/`」へ戻す。
- 複数 scope の `discussions/` へ draft を残せることを明記する。
- canonical docs への直接反映は禁止する。
- `discussions/delegated-authoring/`、per-agent directory、run/task directory は引き続き禁止する。
- draft front matter の必須項目と adoption status を明記する。

### 4. runtime delegated-authoring command の整理

対象:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- dogfooding mirror under `spec-dock/scripts/spec_dock_runtime/...`

修正内容:

- `delegated-authoring scoped-context --discussion-file` は削除する。
- deprecated / blocked / diagnostic fallback として残さない。
- parser binding、command args / runner / renderer、application request / result / helper functions、exact-file context TOML rendering を削除する。
- `diff-guard` は単一 target scope だけでなく、複数 scope または all discussions を検査できる形へ拡張することを検討する。
- `baseline-status` は引き続き repo-external output を使い、pre-existing dirtiness と delegated run diff を切り分ける。

### 5. tests の修正

対象:

- `tests/test_init_update.py`
- `tests/cli_runtime/test_delegated_authoring.py`
- `tests/domain_runtime/test_delegated_authoring.py`

修正内容:

- taxonomy test を更新し、system-architect / implementation-planner が static discussion write capability を持つことを固定する。
- canonical docs / src / tests / `.agents` / `.codex` / `.github` / `.env*` が許可されないことを固定する。
- glob permission を採用する場合は、TOML 上の static write pattern を検査する。
- `scoped-context` exact file write root 前提の tests は削除する。strict fallback 用へ降格しない。
- diff-guard では、複数 scope discussions の正当な draft create と forbidden path mutation を確認する。

### 6. shipped docs / workflow guidance の修正

対象候補:

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`

修正内容:

- delegated authoring の標準運用を「static all discussions write + post-run diff guard + orchestrator adoption」へ更新する。
- exact runtime permission context を必須とする文言を削除する。
- sub-agent が canonical docs を編集できないことと、discussion draft を直接作成できることを同時に説明する。

## 受け入れ条件案

- system-architect / implementation-planner の静的 adapter に、discussion authoring 用 write capability が表現されている。
- read-only specialist agent 群には write capability がない。
- broad workspace worker 群の既存分類は壊れていない。
- canonical docs / implementation / tests / config / secrets への delegated author write は docs / tests / guard で禁止されている。
- `scoped-context --discussion-file` が標準成功経路として要求されなくなる。
- S04 exact-file runtime scoped-context code と tests が削除され、役割を終えた code path が残っていない。
- sub-agent が複数 scope の `discussions/` に draft を残す運用が、設計上自然に説明できる。
- provider assets と dogfooding mirror が同期している。
- `python -m unittest discover -v`、`spec-dock validate`、`spec-dock doctor`、`git diff --check` が通る。

## 推奨判断

現在の `exact file runtime scoped-context` 方式は supersede するべきである。

採用すべき方向は、system-architect / implementation-planner に静的な all discussions write capability を与え、canonical docs の single-writer authority は main orchestrator に残し、実行後の diff guard / front matter / reviewer gate で採用資格を閉じる方式である。

この方が、設定・生成物・実行手順の複雑さを抑えつつ、sub-agent の知見を file-based context として確実に repo に残せる。

## 追加コード全体分析: 削除対象 inventory

2026-05-25 の再確認により、S04 exact-file runtime scoped-context 方針に由来する削除対象は次の通りである。

### Provider runtime

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `delegated-authoring scoped-context` subparser binding。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `DelegatedAuthoringScopedContextRequest` / `generate_delegated_authoring_scoped_context` imports。
  - `DelegatedAuthoringScopedContextArgs`。
  - `delegated_authoring_scoped_context` command spec。
  - `_add_scoped_context_arguments`。
  - `_scoped_context_args`。
  - `_run_scoped_context`。
  - `_expect_scoped_context_args`。
  - `_render_scoped_context_result`。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `DelegatedAuthoringScopedContextRequest`。
  - `DelegatedAuthoringScopedContextResult`。
  - `_SCOPED_CONTEXT_PERMISSION_PROFILES`。
  - `generate_delegated_authoring_scoped_context`。
  - `_blocked_scoped_context_result`。
  - `_render_scoped_context_toml`。
  - `_resolve_scoped_discussion_file`。
  - `_scoped_discussion_file_error`。
  - `_toml_string` if no longer used after scoped-context removal。

### Dogfooding runtime mirror

- `spec-dock/scripts/spec_dock_runtime/cli/parser.py`
- `spec-dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
- `spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py`

Provider runtime と同じ scoped-context code path を削除し、provider / mirror parity を維持する。

### Tests

- `tests/cli_runtime/test_delegated_authoring.py`
  - `test_scoped_context_writes_external_permission_context_for_exact_discussion_file`
  - `test_scoped_context_rejects_non_exact_discussion_file_targets`
  - `test_scoped_context_rejects_repo_local_output`
- `tests/test_init_update.py`
  - runtime scoped context / `delegated-authoring scoped-context` / `--discussion-file` を期待する asset wording assertions。

これらは削除または static all discussions write 方針の regression tests へ置換する。exact-file context generation を守る tests は残さない。

### Agent / workflow guidance

- `src/spec_dock/assets/install_root/.codex/AGENTS.md`
- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
- Dogfooding mirror under `.codex/` and `.agents/`

削除する文言:

- static adapter is read-mostly fallback。
- runtime scoped context required。
- `spec-dock delegated-authoring scoped-context --role ... --scope ... --discussion-file ...`。
- one exact direct child Markdown file write root。
- no scoped context の場合は draft を返すだけ、という read-only fallback guidance。

### 残してよいもの

- Historical evidence under older issues / discussions / reports。
- S05 docs 内の「この code path は削除対象である」という説明。
- `delegated-authoring manifest` の deprecated / blocked stub。
- `delegated-authoring diff-guard` と `baseline-status`。

### 残してはいけないもの

- `delegated-authoring scoped-context` runtime command。
- exact-file context TOML generation helper。
- exact-file write root regression tests。
- adapter / skill / workflow docs における runtime scoped context guidance。
- deprecated / diagnostic fallback としての scoped-context command。
