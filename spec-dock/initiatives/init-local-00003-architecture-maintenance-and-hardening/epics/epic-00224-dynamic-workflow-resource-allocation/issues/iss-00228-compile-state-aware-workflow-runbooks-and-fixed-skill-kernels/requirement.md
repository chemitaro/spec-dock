---
種別: 要件定義書（Issue）
ID: "iss-00228"
タイトル: "Compile State Aware Workflow Runbooks And Fixed Skill Kernels"
関連GitHub: ["#228"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00228 Compile State Aware Workflow Runbooks And Fixed Skill Kernels — 要件定義（何を、なぜ行うか）

## 目的
- Agent が現在の SpecDock workflow state を推測せず、runtime の `workflow status` / `workflow next` から state-aware current Runbook を取得できるようにする。
- Planning / Execution Skill を fixed kernel 化し、Issue 切替・分類・Runbook 更新によって tracked `.agents/skills/**` 差分が発生しないようにする。
- `lite_candidate` と `authorized_profile` を分離し、候補情報だけで workflow obligation が削減されないことを runtime 出力で保証する。

## 背景・現状
- 現状の挙動:
  - Planning / Execution Skill は workflow docs と active state を agent が読み解く前提が強く、軽量 Issue でも広い手順を毎回読み込みやすい。
  - Issue start / active switch は canonical docs を切り替えるが、state-specific な current instruction projection は runtime command として提供されていない。
  - `iss-00227` により `assurance.json` と `authorized_profile` / `lite_candidate` の分類基盤は導入済みである。
- 現状の課題:
  - active issue がない状態、要件未作成状態、分類未実施状態を agent が推測すると、誤った workflow phase に進むリスクがある。
  - Skill 本文に全 profile / 全 phase の手順を持たせると、軽量 task でも context と review burden が大きい。
  - Skill を state ごとに生成・編集すると tracked diff と workflow state が結合し、review / rollback が難しくなる。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
  - `spec-dock/active/epic/discussions/20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`
  - `spec-dock/active/issue/discussions/20260623t033549z-draft-requirement-draft-requirement.md`
  - `spec-dock/active/issue/discussions/20260623t033557z-draft-design-draft-design.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock を操作する Codex / agent。
  - SpecDock workflow を dogfooding する開発者。
- 代表シナリオ:
  - active Issue がない状態で agent が `workflow next issue-execution` を実行し、実装ではなく `issue start <target>` guidance だけを受け取る。
  - active Issue の要件が未作成または scaffold の状態で agent が `workflow next issue-planning` を実行し、requirement capture へ戻る指示を受け取る。
  - active Issue に `assurance.json` がない状態で agent が `workflow next issue-execution` を実行し、classification-required として `assurance classify` へ誘導される。
  - active Issue に `lite_candidate=true` があっても `authorized_profile` が Lite でない場合、Runbook は obligation を削減しない。

## スコープ
- 必須:
  - Workflow State Resolver を導入し、no-active / requirement-capture / classification-required / ready の state を判定する。
  - Runbook schema / compiler を導入し、state と command context から Markdown / JSON Runbook を生成する。
  - `workflow status` と `workflow next` の runtime CLI を提供する。
  - Runbook projection を ignored generated path へ atomic write できる store を導入する。
  - `spec-dock/active/current-runbook.{md,json}` 相当の projection を生成し、tracked authority ではないことを出力上も明示する。
  - Planning / Execution Skill を fixed kernel 化し、runtime `workflow next` を first-class handoff point にする。
  - generated state や Issue switch / classification で tracked Skill diff が出ないことを検証する。
- 禁止:
  - Profile-aware artifact composition を実装しない。
  - Step worker routing / context packet routing を実装しない。
  - PR review policy / repair loop を実装しない。
  - `lite_candidate` のみで workflow obligation を減らさない。
  - Generated Runbook を canonical source of truth として扱わない。
- 対象外:
  - 自動 Lite default 有効化。
  - legacy Issue の全量 backfill。
  - GitHub Actions / PR review 連携。

## 境界
- 常に行う:
  - current state に対して一つの next action を返す。
  - Runbook JSON は machine-readable な state、reason、commands、authority fields を持つ。
  - Markdown Runbook は agent が次に読む最小手順を提示し、未選択 profile の完全手順を含めない。
- 判断が必要:
  - `requirement.md` が scaffold / placeholder のままなら requirement-capture と判定する。
  - active Issue があり、requirement が実質入力済みで `assurance.json` がない場合は classification-required と判定する。
  - valid `assurance.json` があり `authorized_profile` が存在する場合は ready と判定し、固定 Skill kernel から既存 workflow docs へ狭く橋渡しする。
- 行わない:
  - Runbook compiler 内で downstream Issue の profile-specific plan section を合成しない。
  - state resolver が GitHub PR / CI / review status を判定しない。

## 非交渉制約
- Fixed Skill kernel / compiled Runbook authority ADR に従い、Skill 本文は state-specific に生成・編集しない。
- Adaptive Assurance ADR に従い、`authorized_profile` だけを execution authority とし、`lite_candidate` は telemetry / recommendation として扱う。
- Unknown / malformed / missing authority は fail-closed とし、obligation を減らさない。
- Provider source of truth は `src/spec_dock/assets/...` に置き、dogfooding mirror は provider から同期する。
- MyPy / Ruff baseline を壊さず、typed data contract を使って stringly-typed ad hoc branching を避ける。

## 前提
- `iss-00227` の Assurance Contract / classification runtime が完了している。
- `spec-dock/.gitignore` または同等の shipped scaffold により `.agent/` と `active/` projection は tracked diff に入らない。
- 現時点の Lite 自動削減は無効であり、Lite は explicit authorization がある場合だけ future Issue で扱う。

## 受け入れ条件
- AC-001 no-active guidance:
  - アクター: agent。
  - 前提: active Issue がない。
  - 操作: `spec-dock workflow next issue-planning` または `spec-dock workflow next issue-execution` を実行する。
  - 期待結果: Runbook は `issue start <target>` または target 入力要求だけを次 action として返し、要件作成・実装・review 手順へ進ませない。
  - 観測点: CLI text / JSON / Markdown output。
- AC-002 requirement-capture state:
  - アクター: agent。
  - 前提: active Issue はあるが `requirement.md` が scaffold / placeholder のまま。
  - 操作: `spec-dock workflow status --format json` と `spec-dock workflow next issue-planning --format json` を実行する。
  - 期待結果: state は `requirement-capture` となり、次 action は requirement authoring / review gate に限定される。
  - 観測点: JSON fields と Markdown Runbook。
- AC-003 classification-required state:
  - アクター: agent。
  - 前提: active Issue はあり、要件は実質入力済みだが `assurance.json` がない。
  - 操作: `spec-dock workflow next issue-execution --format markdown` を実行する。
  - 期待結果: Runbook は `assurance classify` / `assurance verify` 相当の分類手順へ誘導し、実装開始を許可しない。
  - 観測点: Markdown Runbook と JSON reason code。
- AC-004 authorized profile authority:
  - アクター: agent。
  - 前提: `assurance.json` に `lite_candidate=true` があるが `authorized_profile` は Lite ではない。
  - 操作: `spec-dock workflow next issue-execution --format json` を実行する。
  - 期待結果: Runbook obligation は Lite 向けに削減されず、`authorized_profile` を authority として明示する。
  - 観測点: JSON authority fields、Markdown authority note。
- AC-005 fixed Skill / clean Git:
  - アクター: 開発者 / agent。
  - 前提: Issue start / classification / workflow next を実行する。
  - 操作: tracked status を確認する。
  - 期待結果: generated Runbook は ignored path に作成され、tracked `.agents/skills/**` diff は発生しない。
  - 観測点: `git status --short`、runtime tests。
- AC-006 Runbook minimality:
  - アクター: agent。
  - 前提: Standard / Strict / Lite candidate のいずれかの state。
  - 操作: `workflow next` の Markdown / JSON を確認する。
  - 期待結果: Runbook は現在 state に必要な手順だけを含み、未選択 profile の完全手順を含まない。
  - 観測点: golden output / structural assertions。

## 例外・エッジケース
- EC-001 malformed assurance:
  - 条件: `assurance.json` が壊れている、schema 不整合、または `authorized_profile` が解決できない。
  - 期待: state は fail-closed の classification-required / authority-invalid として扱い、obligation を減らさない。
  - 観測点: CLI JSON reason code、Markdown warning。
- EC-002 generated store write failure:
  - 条件: Runbook projection path へ書き込めない。
  - 期待: state は blocked として扱い、temp cleanup / doctor 相当の次 action を返す。canonical docs / tracked skill は変更しない。
  - 観測点: CLI exit behavior、JSON `state=blocked` / `reason_code=runbook-write-failure`、Markdown blocked guidance。
- EC-003 unknown command target:
  - 条件: `workflow next` に未知の workflow target が渡される。
  - 期待: validation error を返し、Runbook projection を更新しない。
  - 観測点: CLI exit code / stderr。

## 入力→出力例
- EX-001 no-active JSON:
  - 入力: `spec-dock workflow next issue-execution --format json`
  - 出力: `state=no-active`, `next_action=issue-start-required`, `commands=["./spec-dock/scripts/spec-dock issue start <issue-id>"]`
- EX-002 classification-required Markdown:
  - 入力: active Issue with filled requirement and no assurance contract。
  - 出力: `assurance classify --issue <active>` を先に実行し、execution を開始しない Runbook。

## 用語（ドメイン語彙）
- TERM-001 Workflow State:
  - active context、artifact readiness、Assurance authority から解決される workflow の現在状態。
- TERM-002 Runbook:
  - current state に対する agent 向け next action projection。canonical authority ではなく generated output。
- TERM-003 Fixed Skill Kernel:
  - state-specific 手順を持たず、canonical docs の読み込みと `workflow next` 問い合わせへ誘導する安定した Skill 本文。
- TERM-004 Authorized Profile:
  - workflow obligation を選択できる authority。`lite_candidate` とは別物。

## 未確定事項
- なし。Markdown projection の細部、ignored generated path naming、snapshot layout はこの Issue の設計で固定する。
