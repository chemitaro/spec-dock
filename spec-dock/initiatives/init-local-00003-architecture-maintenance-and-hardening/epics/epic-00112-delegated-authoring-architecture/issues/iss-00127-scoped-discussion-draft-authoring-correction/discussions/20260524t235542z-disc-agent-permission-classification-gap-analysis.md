---
種別: disc
ID: "20260524t235542z-disc"
タイトル: "agent permission classification gap analysis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-24"
親: ["iss-00127"]
関連:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "src/spec_dock/assets/install_root/.codex/agents/system-architect.toml"
  - "src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml"
  - ".agents/skills/spec-dock-system-architect/SKILL.md"
  - ".agents/skills/spec-dock-implementation-planner/SKILL.md"
authority: "proposed"
derived_from:
  - "user discussion: system-architect and implementation-planner lack discussions write permission"
  - "inspection: current Codex static agent adapters grant read/deny only"
reflected_to: []
---

# Agent Permission Classification Gap Analysis

## 議題

`system-architect` と `implementation-planner` の権限分類が、現在の実装で read-only static fallback に寄りすぎている。
本来は read-only specialist ではなく、canonical docs を編集しない一方で、対象 scope の `discussions/` 直下に draft / analysis / discussion-local report を直接作成できる scoped-write delegated authoring agent として分類するべきだった。

この資料は、現在の誤り、あるべき分類、ギャップ、解決すべき課題を整理する。

## 現在の状態

### 実装上の観測

- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml` は `default_permissions = "spec_dock_system_architect_draft_authoring"` を持つが、filesystem permission は `read` と `deny` のみで、`write` がない。
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml` も同様に `read` と `deny` のみで、`write` がない。
- どちらの adapter も developer instructions では「scope-local flat Markdown draft/analysis/report under the target `discussions/` direct child」と述べるが、実際の権限では対象 `discussions/` に書けない。
- active issue の requirement / design は、sub-agent direct write を採用しつつ、static adapter では broad write を許可しない判断を記録している。

### 現在の矛盾

現在の成果物は次の 3 つが食い違っている。

| 観点 | 現在の記述 / 実装 | 問題 |
| --- | --- | --- |
| 要件思想 | sub-agent が `discussions/` に draft を直接保存する | direct write を採用している |
| skill contract | `system-architect` / `implementation-planner` は target `discussions/` direct child に Markdown を書く | 書き込み可能であることを前提にしている |
| adapter permission | `.codex/agents/*.toml` は read-only fallback で write 権限なし | 実行時に draft を作成できない |

つまり、文書上は scoped direct-write model を採用しているが、実体は read-only static agent として実装されている。

## 誤りの本質

### 分類ミス

現在の完了判断では、既存 agent と新規 authoring agent を十分に分類せず、`system-architect` / `implementation-planner` を read-only static fallback として扱ってしまった。

本来は、次のように分ける必要があった。

| 分類 | 権限 | 代表 agent | 目的 |
| --- | --- | --- | --- |
| read-only static specialist | read-only | `researcher`, `consultant`, `deep-consultant`, `repo-analyst`, `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `pr-monitor` | 調査、分析、レビュー、監視 |
| full workspace-write worker | workspace write | `dev-coder`, `doc-writer`, `worker`, `utility-worker`, `default`, `explorer` | 実装、テスト、文書編集などの広い作業 |
| scoped-write delegated authoring agent | target scope `discussions/` direct child write only | `system-architect`, `implementation-planner` | canonical docs ではなく discussion draft を作成 |
| canonical authority / orchestrator | canonical docs write / adoption authority | main orchestrator, spec-manager-like orchestration support | 採否判断、canonical docs 統合、phase / lifecycle authority |

`system-architect` / `implementation-planner` は read-only specialist ではない。full workspace-write worker でもない。第三の分類である scoped-write delegated authoring agent として扱うべきである。

### static fallback と本命実行経路の混同

static `.codex/agents/*.toml` が exact target `discussions/` write を表現できない場合、read-mostly fallback にする判断自体は安全側の判断として理解できる。
しかし、その判断を採用するなら、別途 runtime / session-scoped / task-scoped の本命実行経路で、対象 `discussions/` 直下だけ write できる仕組みが必要だった。

現在はその本命経路がない、または完了条件として固定されていない。
そのため、read-mostly fallback が実質的な唯一の実行経路になり、direct-write delegated authoring が成立していない。

## あるべき状態

### 権限分類のあるべき姿

#### 1. Read-only static specialist

対象:

- `researcher`
- `consultant`
- `deep-consultant`
- `repo-analyst`
- `spec-reviewer`
- `code-reviewer`
- `qa-reviewer`
- `pr-monitor`
- `spark-worker`

許可:

- repo / spec / PR / CI / diff の読み取り
- read-only な調査コマンド
- 結果の返答

禁止:

- ファイル作成、編集、削除
- canonical docs の更新
- GitHub mutation
- phase / lifecycle authority claim

#### 2. Full workspace-write worker

対象:

- `dev-coder`
- `doc-writer`
- `worker`
- `utility-worker`
- `default`
- `explorer`

許可:

- 委任範囲内の実装ファイル、テスト、ドキュメント編集
- 必要なローカル検証

制御:

- main orchestrator のタスク境界
- reviewer gate
- git diff / tests / spec-dock validation

#### 3. Scoped-write delegated authoring agent

対象:

- `system-architect`
- `implementation-planner`

許可:

- repo / active scope / source docs / relevant implementation の読み取り
- 対象 initiative / epic / issue の `discussions/` 直下に、命名規則準拠の flat Markdown を新規作成
- main orchestrator が明示指定した既存 proposed discussion draft の更新

禁止:

- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の編集
- `src` / `tests` / `.agents` / `.codex` / `.github` / `.env*` の編集
- `discussions/delegated-authoring/` への出力
- per-agent directory / run directory / task directory / nested directory の作成
- `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` の自己主張
- reviewer pass、phase promotion、issue ready、issue finish、implementation readiness の自己主張

必須:

- frontmatter に `authority: proposed` または equivalent editable state を持つ
- `created_by_role`
- `scope_id`
- `source_paths`
- `intended_targets`
- `adoption_status: unreviewed`
- `reflected_to: []`
- post-run diff guard
- main orchestrator による Evidence Adoption Ledger 記録

#### 4. Canonical authority / orchestrator

対象:

- main orchestrator
- spec-manager-like orchestration support

責務:

- discussion draft の採否判断
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への統合
- Evidence Adoption Ledger 記録
- spec-reviewer gate の実行
- phase / lifecycle authority

## ギャップ

### G-001: Skill contract と adapter permission が一致していない

- Skill は `discussions/` への direct write を期待している。
- Adapter は write 権限を持っていない。
- 結果として、agent は指示上は作成すべき artifact を実際には作成できない。

### G-002: Static fallback と scoped-write 実行経路が分離されていない

- Static adapter を read-mostly fallback にするなら、target scope を注入した scoped-write session / task adapter が必要。
- 現在は read-mostly fallback が唯一の実行経路のように見えている。

### G-003: Completion criteria が実際の file creation 能力を検証していない

- Tests / inspection は broad write を許可していないことを確認した。
- しかし、`system-architect` / `implementation-planner` が対象 `discussions/` に draft を作成できることを確認していない。

### G-004: Agent classification が docs / adapters / tests で固定されていない

- read-only specialist、full workspace-write worker、scoped-write delegated authoring agent、canonical authority の分類が single source of truth として明文化されていない。
- そのため、`system-architect` / `implementation-planner` が read-only specialist と同列に扱われる回帰が起きた。

## 解決すべき課題

### R-001: Agent permission taxonomy を canonical docs に追加する

`requirement.md` / `design.md` / workflow docs のどこかに、agent 権限分類を明記する。

最低限、次を区別する。

- read-only static specialist
- full workspace-write worker
- scoped-write delegated authoring agent
- canonical authority / orchestrator

### R-002: `system-architect` / `implementation-planner` を scoped-write delegated authoring agent として再定義する

この 2 つは read-only specialist ではない。
canonical docs write は禁止したまま、対象 `discussions/` 直下の flat Markdown 作成・限定更新を許可する。

### R-003: Static fallback と scoped-write execution path を設計上分離する

`system-architect.toml` / `implementation-planner.toml` を read-mostly fallback として残す場合でも、実運用の本命経路を別に定義する。

候補:

- main orchestrator が target scope を解決し、session-scoped permission config を生成する。
- generated invocation では target `discussions/` direct child のみ write を許可する。
- static fallback は、host が scoped write を表現できない場合の degraded mode として扱う。

### R-004: Acceptance criteria を更新する

修正後の acceptance criteria は、次を含むべきである。

- `researcher` / `consultant` / `repo-analyst` / reviewers は read-only のまま。
- `dev-coder` / `doc-writer` は full workspace-write worker として扱う。
- `system-architect` / `implementation-planner` は対象 `discussions/` 直下のみ write 可能。
- canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.env*` はこの 2 agent から write 不可。
- 実際に `discussions/<ts>-<kind>-<slug>.md` を作成できることを test / fixture / generated config inspection で固定する。
- forbidden path の write が diff guard で rejected / adoption-ineligible になることを確認する。

### R-005: Current PR / issue completion state を見直す

現在の実装は CI / review 上は mergeable でも、要件上は未完成である。
少なくともこの gap を追跡する follow-up issue、または既存 PR の修正 commit が必要である。

## 推奨案

推奨は、`system-architect` / `implementation-planner` を read-only static agents から外し、scoped-write delegated authoring agents として明示的に分類することである。

ただし、静的 `.codex/agents/*.toml` に `spec-dock/initiatives` 全体の broad write を与えるべきではない。
本命は、main orchestrator が対象 scope を解決したうえで、target `discussions/` direct child だけ write できる session-scoped / task-scoped adapter を生成する方式である。

これにより、次の両方を満たせる。

- sub-agent の file-based context persistence と direct draft authoring を実現する。
- canonical docs と実装ファイルの single-writer / review-gated authority を維持する。

## 未決事項

- 現在の host / Codex agent config が、実行ごとに target `discussions/` だけ write 可能な session-scoped permission を表現できるか。
- それができない場合、static adapter にどの程度の最小 write root を与えるか。
- scoped-write execution path を runtime command として生成するか、orchestrator workflow の責務にするか。
- 既存 PR #119 / #128 を修正するか、follow-up issue / PR に分けるか。

## 次アクション

- `requirement.md` / `design.md` に agent permission taxonomy と scoped-write delegated authoring agent の分類を反映する。
- `system-architect` / `implementation-planner` の adapter / skill / tests を、read-only fallback と scoped-write execution path の二層として再設計する。
- acceptance tests または inspection tests に、`system-architect` / `implementation-planner` が target `discussions/` に書けること、かつ canonical / implementation / config には書けないことを追加する。
- 現在の PR / issue 完了状態を見直し、未解決 gap として report / follow-up に記録する。
