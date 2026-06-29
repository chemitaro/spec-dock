---
種別: 要件定義書（Issue）
ID: "iss-00238"
タイトル: "Use Stdout Runbook Handoff Instead Of Generated Workflow Files"
関連GitHub: ["#238"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["epic-00224", "init-local-00003"]
---

# iss-00238 Use Stdout Runbook Handoff Instead Of Generated Workflow Files — 要件定義（何を、なぜ行うか）

## 目的

- SpecDock の agent-facing な動的 workflow handoff を、生成ファイル参照ではなく、毎回実行される runtime command の stdout に一本化する。
- `workflow next` という「次」を前提にした名前を廃止し、`guidance <target>` によって「今この状態で何をすべきか」を返す command surface へ置き換える。
- 人間向け runbook projection は便利な ignored artifact として残しつつ、agent が projection の作成・参照・管理を意識しない設計へ切り替える。

## 背景・現状

- Epic `epic-00224` では、Issue の状態、Assurance、実装 step、context policy に応じて runtime が current Runbook を生成し、Skill は固定 kernel としてそれを取得する方針を導入した。
- 現行の Issue Planning / Execution Skill は `./spec-dock/scripts/spec-dock workflow next issue-planning` / `issue-execution` を first-read handoff として実行する。
- 現行 runtime は Runbook を stdout に出すだけでなく、通常実行で `spec-dock/.agent/runbooks/current-runbook.*` と `spec-dock/active/current-runbook.*` を生成する。
- 調査時点で active issue は `iss-00238` だったが、`spec-dock/.agent/runbooks/current-runbook.json` は `iss-00237` を指していた。生成 projection は実際に stale になり得る。
- `tests/cli_runtime/test_workflow.py` は `workflow next` が projection を書くことを通常 contract として固定している。

## 現状の課題

- `workflow next` という名前は、実際には「次」ではなく現在状態に対する guidance を返しているため、利用者と agent の mental model を誤らせる。
- `workflow` は全体手順を返す印象が強く、実際の出力である action guidance、stop condition、runbook fragment、context routing とズレる。
- Skill から generated runbook projection の存在が見えると、agent が command stdout ではなく古い file を読む余地が残る。
- Projection write failure が guidance stdout 取得を block すると、agent-facing handoff と human-facing snapshot の責務が混ざる。
- 動的 guidance を読んだ後、agent が `state`、`next_action`、commands、stop conditions、selected step、verification / reviewer gate を自身の task checklist へ登録する要求が弱い。

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock Skill を使う Codex / agent。
  - SpecDock の workflow state を確認する人間の開発者。
- 代表シナリオ:
  - Agent が issue planning を開始し、`guidance issue-planning` の stdout から requirement capture / design / plan readiness を判断する。
  - Agent が issue execution を開始し、`guidance issue-execution` の stdout から実行可能 step、stop condition、verification / reviewer obligation を task checklist に登録する。
  - 人間が ignored projection を確認して現在の runbook snapshot を読むが、agent の handoff authority としては扱わない。

## スコープ

- 必須:
  - `workflow next <target>` を agent-facing primary command から外し、`guidance <target>` を導入する。
  - Target は `issue-planning` と `issue-execution` を分ける。
  - `guidance <target>` は stdout を agent-facing な正本とし、引数なしで Markdown を返す。
  - Human-facing projection は自動生成されてもよいが、Git 管理されない ignored artifact とし、agent-facing docs / skills から参照導線を消す。
  - Projection write failure は `guidance` stdout の成功を block しない。
  - Issue Planning / Execution Skill は `guidance <target>` 実行と task checklist 登録を first-read handoff として要求する。
  - Runtime / CLI / presentation / tests / shipped Skill asset を provider-side source of truth で更新する。
- 禁止:
  - `guidance current`、`workflow next`、`runbook current` など、現在 / 次 / file projection を primary concept にする command 名を採用しない。
  - `workflow next` の互換 alias を追加しない。この変更は main branch 未マージの issue 内で切り替える。
  - Agent に projection file を作成・更新・参照・管理させない。
  - Context packet の責務を今回の issue で再設計しない。
- 対象外:
  - Epic 全体の Assurance Profile / Step Assurance / Context Policy の再設計。
  - GitHub PR review policy / blocker closure。
  - Existing issue 全量 migration。
  - Human-facing projection の高度な閲覧 UI。

## 非交渉制約

- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` と `src/spec_dock/assets/install_root/...` であり、dogfooding mirror を実装 source として扱わない。
- `spec-dock/` 配下の active dogfooding workspace は確認対象であり、必要な場合だけ反映・検証する。
- Generated projection は canonical authority ではない。
- Agent-facing の状態依存 guidance は、毎回 command stdout から取得する。
- User-facing / artifact 文書は日本語で書く。

## 前提

- Active Issue は `iss-00238`。
- 既存 runtime には `workflow status / next`、`WorkflowNextRequest`、`workflow_next`、Runbook compiler / store、presentation が存在する。
- 既存 Skill asset には `workflow next issue-planning` / `workflow next issue-execution` の first-read handoff が存在する。
- 親 Epic の一部記述は `workflow next` 前提を含むが、この issue で `guidance <target>` へ補正する。

## 受け入れ条件

- AC-001: `guidance issue-planning` が planning guidance を stdout に返す
  - アクター: agent / developer
  - 前提: SpecDock initialized repo で active issue が存在する。
  - 操作: `./spec-dock/scripts/spec-dock guidance issue-planning` を実行する。
  - 期待結果: Markdown stdout に state、next action、commands、stop conditions、target が読める形で返る。
  - 観測点: CLI runtime tests、Markdown stdout。

- AC-002: `guidance issue-execution` が execution guidance を stdout に返す
  - アクター: agent / developer
  - 前提: SpecDock initialized repo で active issue が存在する。
  - 操作: `./spec-dock/scripts/spec-dock guidance issue-execution` を実行する。
  - 期待結果: stdout に execution 向け guidance が返る。実行可能な場合は step assurance / context packet refs を含み、実行不可の場合は planning required / blocked guidance を返す。
  - 観測点: CLI runtime tests、context routing tests。

- AC-003: `current` / `next` を primary command surface に残さない
  - アクター: developer
  - 前提: provider-side Skill asset と runtime tests が更新済み。
  - 操作: Skill asset、runtime parser、CLI tests を検索する。
  - 期待結果: agent-facing first-read handoff は `guidance issue-planning` / `guidance issue-execution` を指す。`workflow next` は primary command / compatibility alias として残らない。
  - 観測点: `rg` inspection、installer / wrapper tests。

- AC-004: Projection は agent guidance を block しない
  - アクター: agent / developer
  - 前提: projection path への書き込みが失敗する fixture。
  - 操作: `guidance issue-planning` を実行する。
  - 期待結果: command は guidance stdout を成功として返す。projection write failure は agent-facing state を `runbook-write-failure` にしない。
  - 観測点: unit / CLI runtime tests。

- AC-005: Projection は ignored human artifact として扱われる
  - アクター: developer
  - 前提: Git initialized target repo。
  - 操作: `guidance issue-planning` または `guidance issue-execution` を実行し、`git status --short` を確認する。
  - 期待結果: projection が生成されても tracked diff が出ない。Projection header / payload は agent handoff ではないことと refresh command を示す。
  - 観測点: CLI runtime tests、generated file inspection。

- AC-006: Skill が stdout guidance の task checklist 登録を促す
  - アクター: agent
  - 前提: shipped Issue Planning / Execution Skill を読む。
  - 操作: First-Read Handoff section を確認する。
  - 期待結果: Skill は `guidance <target>` stdout を読むこと、`state` / `next_action` / selected step / commands / stop conditions / verification / reviewer gate を task checklist へ登録すること、projection を agent handoff として読まないことを明記する。
  - 観測点: provider asset tests、installed asset tests。

- AC-007: Stale projection が guidance 結果に影響しない
  - アクター: agent / developer
  - 前提: `current-runbook.*` が別 issue を指す stale 状態で存在する。
  - 操作: `guidance issue-planning` を実行する。
  - 期待結果: stdout は現在の active issue / state から生成され、stale projection の内容に依存しない。
  - 観測点: CLI runtime regression tests。

## 例外・エッジケース

- EC-001: active issue が存在しない
  - 条件: no-active state。
  - 期待: `guidance issue-planning` / `guidance issue-execution` は `issue-start-required` guidance を stdout に返し、authoring / execution を開始しない。
  - 観測点: CLI runtime tests。

- EC-002: unknown target
  - 条件: `guidance unknown-target` を指定する。
  - 期待: parser が明確に reject し、projection を生成しない。
  - 観測点: CLI runtime tests。

- EC-003: malformed assurance / stale source binding
  - 条件: `assurance.json` が壊れている、または source binding が stale。
  - 期待: guidance は classification required / blocked state を stdout に返す。
  - 観測点: 既存 workflow tests の guidance 版。

- EC-004: context packet write failure
  - 条件: issue-execution で context packet write が失敗する。
  - 期待: context packet は execution handoff payload なので、既存の fail-closed 挙動を維持する。Runbook projection write failure と混同しない。
  - 観測点: context routing tests。

## 入力→出力例

- EX-001: planning Markdown guidance
  - 入力: `./spec-dock/scripts/spec-dock guidance issue-planning`
  - 出力: state、next action、reason code、active issue、commands、stop conditions、projection warning を人間と agent が読める Markdown。

- EX-002: execution Markdown guidance
  - 入力: `./spec-dock/scripts/spec-dock guidance issue-execution`
  - 出力: 現在状態、commands、stop conditions、必要に応じて step assurance / context packet refs を含む Markdown。

## 用語

- Guidance:
  - SpecDock runtime が現在の repository / active context / artifact / assurance / worktree 状態から stdout に生成する agent-facing な行動指示。
- Target:
  - Guidance の意図を示す引数。今回の対象は `issue-planning` と `issue-execution`。
- Projection:
  - 人間確認 / debug / evidence 用に自動生成される ignored artifact。Agent-facing authority ではない。
- Static workflow docs:
  - `workflow_*.md` などの durable policy / fallback。状態依存の current guidance ではない。

## 未確定事項

- なし。
  - `guidance <target>`、target 分離、互換 alias 不要、projection は人間向け自動生成 ignored artifact、context packet は対象外という判断は、リサーチ artifact とユーザー確認で採用済み。
