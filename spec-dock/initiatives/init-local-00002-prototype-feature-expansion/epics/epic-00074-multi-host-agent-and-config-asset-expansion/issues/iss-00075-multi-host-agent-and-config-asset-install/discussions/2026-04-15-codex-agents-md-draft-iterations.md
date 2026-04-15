---
種別: 議論メモ（Issue）
ID: "disc-2026-04-15-codex-agents-md-draft-iterations"
タイトル: "Codex AGENTS.md draft iterations"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["iss-00075", "epic-00074", "init-local-00002"]
---

# `.codex/AGENTS.md` ドラフト反復ログ

## 目的
- `src/spec_dock/assets/install_root/.codex/AGENTS.md` を、session rule の再掲ではなく「SpecDock bootstrap guide」として再設計する。
- 複数の consultant / spec reviewer の評価を受けながら、v1 → v4 の反復でベストプラクティス案を固める。

## 固定前提
- `<repo>/.codex/AGENTS.md` は標準 auto-read の主役ではない。
- このファイルは `project_doc_fallback_filenames = [".codex/AGENTS.md"]` を使う前提で、root `AGENTS.md` が未作成の repo に bootstrap guidance を与える bridge として扱う。
- root `AGENTS.md` が作られた後は、そちらが authoritative な product/domain guidance になる。
- `.codex/config.toml` が session behavior と orchestrator responsibility を担い、`.codex/AGENTS.md` は operational charter に限定する。

---

## V1

### ねらい
- 最小限で誤操作を防げる bootstrap guide を作る。
- 長文 manual にせず、SpecDock の正本、読む順序、CLI による安全操作だけを載せる。

### ドラフト

```md
# SpecDock Bootstrap Guide

This file is a bootstrap guide for repos that use SpecDock.
If the repository root has an `AGENTS.md`, treat that file as the authoritative guide for product/domain-specific rules.

## Read This First
- Start with `spec-dock/active/issue/{requirement,design,plan}.md` if an active issue exists.
- Then read `spec-dock/active/epic/{requirement,design,plan}.md`.
- Then read `spec-dock/active/initiative/{requirement,design,plan}.md`.
- If there is no active context, inspect `spec-dock/system/active-none/` and the nearest root `AGENTS.md`.

## Working Model
- Treat repo docs as the source of truth, not chat history.
- Use SpecDock docs to fix scope, design, and execution order before implementation.
- Record decisions, validation, and unresolved items in issue `report.md`.

## Safe Defaults
- Use the SpecDock CLI for active pointers; do not hand-edit active symlinks or `.path` files.
- Use `sync` to regenerate derived artifacts; do not hand-edit generated state when a command exists.
- Run `validate` after structural changes, sync operations, or before closing work.
- Check dependency readiness before implementation when the task depends on other work.

## Command Cheat Sheet
- `./spec-dock/scripts/spec-dock active show`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`
- `./spec-dock/scripts/spec-dock sync --github`
- `./spec-dock/scripts/spec-dock deps check <target>`

## Do Not
- Do not treat chat logs as the source of truth.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit derived state artifacts when the CLI owns them.
- Do not assume this file contains product-specific domain knowledge.

## Use The Right Document
- Root `AGENTS.md`: product/domain rules and repo-specific guidance.
- `.codex/config.toml`: session behavior and orchestrator rules.
- `spec-dock/active/*`: current task contract.
- `discussion` / `ADR`: reasoning history and long-lived decisions.

## Escalate When
- Active docs conflict with each other.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- A structural change would rewrite managed docs or generated state broadly.
```

### 自己評価
- 長所:
  - 短い
  - bootstrap bridge の役割が明確
  - root `AGENTS.md` との責務分離が見える
- 懸念:
  - bridge であることの期限や handoff 条件がやや弱い
  - CLI command の優先順位がまだ曖昧
  - “generated state” の表現が product repo では抽象的すぎる可能性がある

### review log
- consultant:
  - bridge の役割分離は妥当
  - 有効条件 / 退場条件 / day-0 command 優先順位を本文で明示すべき
- spec review:
  - fail
  - bootstrap bridge の発火条件と handoff 条件が本文で契約化されていない
  - fallback 時の参照先表現、misuse prevention、command 優先順位が曖昧

---

## V2

### ねらい
- bridge の発火条件、適用範囲、handoff 条件を本文で固定する。
- day-0 repo 向けの最短導線を 2〜3 ステップで明示する。
- 抽象語を減らし、SpecDock が管理する対象を path/command ベースで具体化する。

### ドラフト

```md
# SpecDock Bootstrap Bridge

This file is a bootstrap-only guide for repositories that use SpecDock.
It is intended to be loaded only when `.codex/config.toml` enables `.codex/AGENTS.md` as a fallback project document and the repository root does not yet provide the product/domain guidance you need.

If the repository root has an `AGENTS.md`, treat that file as the authoritative source for repo-specific and domain-specific rules.
Do not expand this file into a second root guide. Keep it limited to SpecDock bootstrap rules.

## When This Applies
- Use this file to learn how to work with SpecDock before the repository root `AGENTS.md` is available or complete.
- Once the repository root `AGENTS.md` exists, keep product/domain guidance there and keep this file minimal.

## Read Order
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if present

If there is no active context, inspect `spec-dock/system/active-none/` and then the repository root `AGENTS.md`, if present.

## Working Model
- Treat repo docs as the source of truth, not chat history.
- Align `requirement.md`, `design.md`, and `plan.md` before implementation.
- Record decisions, validation, and unresolved items in issue `report.md`.

## Day-0 Safe Flow
1. Run `./spec-dock/scripts/spec-dock active show` to confirm the current context.
2. Read the active issue / epic / initiative docs in the order above.
3. Run `./spec-dock/scripts/spec-dock validate` before closing work or after structural changes.

Use `./spec-dock/scripts/spec-dock sync` when SpecDock-managed derived views or generated state need to be refreshed.

## Do Not
- Do not treat chat logs as the source of truth.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit SpecDock active pointers, including `spec-dock/active/*` links and `.path` files.
- Do not hand-edit SpecDock-managed derived state when the CLI owns regeneration through `sync`.
- Do not put product/domain guidance in this file.
- Do not copy session behavior from `.codex/config.toml` into this file.

## Use The Right Source
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo/product/domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating guide
- `discussion` / `ADR`: reasoning history and long-lived decisions

## Escalate When
- Active docs conflict with each other.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- A structural change would rewrite SpecDock-managed docs or generated state broadly.
```

### v1 からの改善
- fallback 前提を本文へ昇格
- root `AGENTS.md` 出現後の handoff 条件を明文化
- “repository root `AGENTS.md`” と一意に表現
- day-0 command 順序を固定
- `active/*` links と `.path` files を具体化

### 自己評価
- 長所:
  - 発火条件と適用範囲が明確になった
  - bridge の退場条件が見えた
  - command priority が改善された
- 懸念:
  - “repository root `AGENTS.md` is available or complete” は少し人間判断に寄る
  - `sync` の使いどころはまだやや広い
  - 文体をさらに圧縮できる余地がある

### review log
- consultant:
  - 実務投入に近づいた
  - 停止条件を `repository root AGENTS.md exists` に寄せるべき
  - `sync` 説明と section 重複をさらに圧縮できる
- spec review:
  - fail
  - bridge の発火条件に主観表現が残る
  - root `AGENTS.md` 作成後の停止条件をより強く固定すべき

## V3

### ねらい
- bridge の発火条件と handoff 条件を人間判断ではなく停止条件として書き切る。
- `Read Order` と `Use The Right Source` の役割を整理して文量を圧縮する。

### ドラフト

```md
# SpecDock Bootstrap Bridge

Use this file only when `.codex/config.toml` enables `.codex/AGENTS.md` as a fallback project document.
This file is a bootstrap-only guide for SpecDock and is not the primary source for repo-specific or domain-specific rules.

If the repository root `AGENTS.md` exists, use that file for repo, product, and domain guidance.
After the repository root `AGENTS.md` exists, use this file only for bootstrap-level SpecDock operating rules.

## Read Order
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

If there is no active context, read `spec-dock/system/active-none/` and then the repository root `AGENTS.md`, if it exists.

## Working Model
- Treat repo docs as the source of truth, not chat history.
- Align `requirement.md`, `design.md`, and `plan.md` before implementation.
- Record decisions, validation, and unresolved items in issue `report.md`.

## Day-0 Safe Flow
1. Run `./spec-dock/scripts/spec-dock active show`.
2. Read the active docs in the order above.
3. Run `./spec-dock/scripts/spec-dock validate` after structural changes and before closing work.

Use `./spec-dock/scripts/spec-dock sync` only to refresh SpecDock-managed generated views, pointers, or exported state owned by the CLI.

## Do Not
- Do not treat chat logs as the source of truth.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not put repo/product/domain guidance or session behavior in this file.

## Use The Right Source
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo/product/domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `discussion` / `ADR`: reasoning history and long-lived decisions

## Escalate When
- Active docs conflict with each other.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- A structural change would rewrite SpecDock-managed docs or generated state broadly.
```

### v2 からの改善
- `available or complete` のような主観表現を除去
- root `AGENTS.md` 存在後の読み方を停止条件として固定
- `sync` の用途を CLI-managed generated views / pointers / exported state に絞った
- `Do Not` を圧縮し、重複を削った

### 自己評価
- 長所:
  - contract がかなり硬くなった
  - handoff 条件が機械的に読める
  - 文量も少し締まった
- 懸念:
  - `discussion / ADR` まで bootstrap guide に入れる必要が本当にあるかは再評価余地あり
  - `repository root AGENTS.md exists` のときにこの file が runtime 上どこまで参照されるかは実装依存なので、文章をさらに保守的にもできる

### review log
- consultant:
  - `temporary bootstrap bridge` としての lifecycle をさらに固定すべき
  - root `AGENTS.md` 成立後は `.codex/AGENTS.md` を durable guidance の置き場として育てない契約が必要
  - `sync` を一般修復コマンドとして誤用しない文言を入れるべき
  - `CLI-managed か手編集可能か判定不能` を escalation 条件に加えると事故耐性が上がる
- spec review:
  - fail
  - precedence rule が暗黙で、root `AGENTS.md` / active docs / `.codex/config.toml` と衝突した場合の解決順序が明示されていない
  - `bootstrap-only SpecDock operating rules` の scope boundary を opening contract でより具体化すべき
  - `discussion` と `ADR` を同列 source に見せず、accepted durable decision と supporting rationale を分けて記述すべき

## V4

### ねらい
- bootstrap bridge の一時性、優先順位、scope boundary を opening contract で明示する。
- root `AGENTS.md` 成立後の dormant 化を強めつつ、`sync` / managed path 誤用もさらに防ぐ。

### ドラフト

```md
# SpecDock Bootstrap Bridge

This file exists only as a temporary SpecDock bootstrap bridge.

Use it only when `.codex/config.toml` enables `project_doc_fallback_filenames = [".codex/AGENTS.md"]` and the repository root does not already provide authoritative `AGENTS.md` guidance for the same scope.

If this file conflicts with `spec-dock/active/*`, the repository root `AGENTS.md`, or `.codex/config.toml`, follow the higher-authority source and treat this file as subordinate bootstrap guidance.

This file may define only SpecDock bootstrap workflow rules such as active-doc discovery, `validate` / `sync` usage, and handling of SpecDock-managed files.
Do not use it for repo architecture, product/domain guidance, coding conventions, testing policy, or session/orchestrator behavior.

If the repository root `AGENTS.md` exists, that file is authoritative for repo, product, and domain guidance.
Do not extend this file with repo-specific guidance after the repository root `AGENTS.md` is established.

## Read First
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

If there is no active context, read `spec-dock/system/active-none/` first and then the repository root `AGENTS.md`, if it exists.

## Operating Rules
- Treat repo docs as the source of truth, not chat history.
- Do not implement until issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Record decisions, validation, and unresolved items in issue `report.md`.
- Run `./spec-dock/scripts/spec-dock active show` at session start.
- Run `./spec-dock/scripts/spec-dock validate` after structural changes and before handoff.
- Use `./spec-dock/scripts/spec-dock sync` only to regenerate CLI-managed views, pointers, or exported state. Do not use it as a general repair step.

## Source Boundaries
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo, product, and domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `ADR`: accepted durable decisions
- `discussion`: supporting rationale and context, including superseded options

## Do Not
- Do not treat chat logs as canonical instructions.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not store repo, product, domain, or session rules in this file.
- Do not keep adding durable repo guidance here once the repository root `AGENTS.md` exists.

## Escalate When
- Active docs conflict with each other or with the repository root `AGENTS.md`.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- It is unclear whether a file is CLI-managed or safe to edit manually.
- A structural change would broadly rewrite SpecDock-managed docs or generated state.
```

### v3 からの改善
- precedence rule を opening contract に追加
- bootstrap workflow rule の範囲を具体化し、非スコープも列挙
- `temporary` と `do not extend` により dormant 化を強化
- `ADR` と `discussion` の役割を分離
- `sync` の一般修復コマンド誤用を禁止
- `CLI-managed か判定不能` を escalation 条件へ追加

### 自己評価
- 長所:
  - どの source が優先されるかを明示できた
  - bootstrap bridge の一時性と scope boundary が十分に硬くなった
  - durable guidance の置き場を root `AGENTS.md` へ明確に押し戻せた
- 懸念:
  - `Read First` に root `AGENTS.md` を 4 番目で残すか、authority track として section 分離するかはまだ美観の改善余地がある
  - `product_doc_fallback_filenames` の exact syntax を本文に出すことで実装依存度が少し上がる

### review log
- consultant:
  - structural problem は解消済み
  - ただし exact fallback syntax を本文に埋め込むと drift risk がある
  - precedence は `higher-authority` より scope-based rule の方が durable
  - post-root `AGENTS.md` の重複記述は少し削れる
- spec review:
  - pass
  - authority model, scope boundary, source taxonomy は十分に enforceable
  - `Read First` の authority/task 混在は optional polish であり blocker ではない

## 最終採用案
## V5

### ねらい
- fallback config の exact syntax 依存を避け、behavioral contract に寄せる。
- precedence を `higher-authority` ではなく scope-based resolution として書き切る。
- 重複を少し削り、最終候補としての durability を上げる。

### ドラフト

```md
# SpecDock Bootstrap Bridge

This file exists only as a temporary SpecDock bootstrap bridge.

Use it only when `.codex/config.toml` explicitly configures `.codex/AGENTS.md` as a fallback project document and the repository root does not already provide authoritative `AGENTS.md` guidance for the same scope.

Resolve overlap by scope: `spec-dock/active/*` defines the current task contract, the repository root `AGENTS.md` defines repo, product, and domain rules, `.codex/config.toml` defines session and orchestrator behavior, and this file remains subordinate bootstrap guidance.

This file may define only SpecDock bootstrap workflow rules such as active-doc discovery, `validate` / `sync` usage, and handling of SpecDock-managed files.
Do not use it for repo architecture, product/domain guidance, coding conventions, testing policy, or session/orchestrator behavior.

If the repository root `AGENTS.md` exists, that file is authoritative for repo, product, and domain guidance. After it is established, keep this file limited to bootstrap workflow rules only.

## Read First
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

If there is no active context, read `spec-dock/system/active-none/` first and then the repository root `AGENTS.md`, if it exists.

## Operating Rules
- Treat repo docs as the source of truth, not chat history.
- Do not implement until issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Record decisions, validation, and unresolved items in issue `report.md`.
- Run `./spec-dock/scripts/spec-dock active show` at session start.
- Run `./spec-dock/scripts/spec-dock validate` after structural changes and before handoff.
- Use `./spec-dock/scripts/spec-dock sync` only to regenerate CLI-managed views, pointers, or exported state. Do not use it as a general repair step.

## Source Boundaries
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo, product, and domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `ADR`: accepted durable decisions
- `discussion`: supporting rationale and context; may include superseded options

## Do Not
- Do not treat chat logs as canonical instructions.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not store repo, product, domain, or session rules in this file.

## Escalate When
- Active docs conflict with each other or with the repository root `AGENTS.md`.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- It is unclear whether a file is CLI-managed or safe to edit manually.
- A structural change would broadly rewrite SpecDock-managed docs or generated state.
```

### v4 からの改善
- exact TOML snippet を behavioral contract に置換
- precedence を scope-based resolution rule に変更
- post-root `AGENTS.md` の重複を削減
- `discussion` の文言を少し締めて superseded risk を明示

### 自己評価
- 長所:
  - 実装 detail への結合を少し減らせた
  - source precedence が運用概念として理解しやすくなった
  - これ以上の改善は美観差分が中心になりそう
- 懸念:
  - `Read First` を authority track と task track に分ける編集はなおあり得るが、短さとのトレードオフ

### review log
- consultant:
  - V5 で十分
  - meaningful improvement はほぼ尽きており、これ以上は editorial polish 領域
  - `spec-dock/system/active-none/` の directory 参照は少し抽象的だが blocker ではない
- spec review:
  - pass
  - authority model、scope boundary、fallback bridge としての位置づけ、source taxonomy は final candidate として十分
  - 残りは clarity polish のみで specification blocker はなし

## 最終採用案
## V6

### ねらい
- bootstrap guide の範囲を保ったまま、`spec-manager` を SpecDock 操作の default specialist として明示する。
- 新規 repo の初回利用者が迷わないよう、SpecDock の capability を短く示す。

### ドラフト

```md
# SpecDock Bootstrap Bridge

This file exists only as a temporary SpecDock bootstrap bridge.

Use it only when `.codex/config.toml` explicitly configures `.codex/AGENTS.md` as a fallback project document and the repository root does not already provide authoritative `AGENTS.md` guidance for the same scope.

Resolve overlap by scope: `spec-dock/active/*` defines the current task contract, the repository root `AGENTS.md` defines repo, product, and domain rules, `.codex/config.toml` defines session and orchestrator behavior, and this file remains subordinate bootstrap guidance.

This file may define only SpecDock bootstrap workflow rules such as active-doc discovery, `validate` / `sync` usage, handling of SpecDock-managed files, default delegation for SpecDock operations, and a short capability summary for first use.
Do not use it for repo architecture, product/domain guidance, coding conventions, testing policy, or session/orchestrator behavior.

If the repository root `AGENTS.md` exists, that file is authoritative for repo, product, and domain guidance. After it is established, keep this file limited to bootstrap workflow rules only.

## Default Operator

Treat `spec-manager` as the default specialist for SpecDock operations.

Use `spec-manager` by default for SpecDock workflows instead of operating the tool ad hoc. If `spec-manager` delegates to other specialists, the authoritative task contract still comes from `spec-dock/active/*` and the current issue docs.

## What SpecDock Can Do

SpecDock provides a CLI workflow for spec-driven execution. It can:
- create and import spec nodes such as initiatives, epics, issues, and discussion docs
- maintain the active working context for the current task
- validate the tree and diagnose broken or incomplete state
- regenerate CLI-managed derived state
- check dependency readiness before implementation starts

## Read First
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

If there is no active context, read `spec-dock/system/active-none/` first and then the repository root `AGENTS.md`, if it exists.

## Operating Rules
- Treat repo docs as the source of truth, not chat history.
- Do not implement until issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Record decisions, validation, and unresolved items in issue `report.md`.
- Run `./spec-dock/scripts/spec-dock active show` at session start.
- Run `./spec-dock/scripts/spec-dock validate` after structural changes and before handoff.
- Use `./spec-dock/scripts/spec-dock sync` only to regenerate CLI-managed views, pointers, or exported state. Do not use it as a general repair step.

## Source Boundaries
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo, product, and domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `ADR`: accepted durable decisions
- `discussion`: supporting rationale and context; may include superseded options

## Do Not
- Do not treat chat logs as canonical instructions.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not store repo, product, domain, or session rules in this file.

## Escalate When
- Active docs conflict with each other or with the repository root `AGENTS.md`.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- It is unclear whether a file is CLI-managed or safe to edit manually.
- A structural change would broadly rewrite SpecDock-managed docs or generated state.
```

### v5 からの改善
- `spec-manager` を SpecDock 操作の default specialist として明示
- 初回利用向けに SpecDock capability の短い summary を追加
- 追加内容も bootstrap workflow 補助情報に限定し、root `AGENTS.md` や `.codex/config.toml` と競合しないように維持

### 自己評価
- 長所:
  - 「誰に依頼するか」と「何ができるか」が入り、初回導線としてさらに実用的になった
  - `spec-manager` を唯一の operator ではなく default specialist として表現できている
  - capability summary も CLI surface の大枠に留めており README 化していない
- 懸念:
  - `What SpecDock Can Do` を長くしすぎると bridge ではなく onboarding manual に寄りすぎるため、要約は今の密度が上限に近い

### review log
- consultant:
  - `spec-manager` の default delegation と short capability summary は bootstrap workflow 補助情報として適切
  - 追加位置は intro 直後がよく、長い manual 化は避けるべき
- spec review:
  - pass
  - `Default Operator` は bootstrap bridge の範囲内であり、global orchestrator policy を再定義していない
  - `What SpecDock Can Do` も現状の長さと抽象度なら bootstrap guide の範囲に収まる
  - 新規追加は既存 authority model と競合しない
  - 残りは `Read First` の並び順など editorial polish のみ

## V7

### ねらい
- `active-none` への明示誘導をやめ、入口を常に `spec-dock/active/*` に統一する。
- SpecDock 自体の使い方へ進める docs path を追加し、bootstrap guide と product docs の接続を強める。

### ドラフト

```md
# SpecDock Bootstrap Bridge

This file exists only as a temporary SpecDock bootstrap bridge.

Use it only when `.codex/config.toml` explicitly configures `.codex/AGENTS.md` as a fallback project document and the repository root does not already provide authoritative `AGENTS.md` guidance for the same scope.

Resolve overlap by scope: `spec-dock/active/*` defines the current task contract, the repository root `AGENTS.md` defines repo, product, and domain rules, `.codex/config.toml` defines session and orchestrator behavior, and this file remains subordinate bootstrap guidance.

This file may define only SpecDock bootstrap workflow rules such as active-doc discovery, `validate` / `sync` usage, handling of SpecDock-managed files, default delegation for SpecDock operations, and a short capability summary for first use.
Do not use it for repo architecture, product/domain guidance, coding conventions, testing policy, or session/orchestrator behavior.

If the repository root `AGENTS.md` exists, that file is authoritative for repo, product, and domain guidance. After it is established, keep this file limited to bootstrap workflow rules only.

## Default Operator

Treat `spec-manager` as the default specialist for SpecDock operations.

Use `spec-manager` by default for SpecDock workflows instead of operating the tool ad hoc. If `spec-manager` delegates to other specialists, the authoritative task contract still comes from `spec-dock/active/*` and the current issue docs.

## What SpecDock Can Do

SpecDock provides a CLI workflow for spec-driven execution. It can:
- create and import spec nodes such as initiatives, epics, issues, and discussion docs
- maintain the active working context for the current task
- validate the tree and diagnose broken or incomplete state
- regenerate CLI-managed derived state
- check dependency readiness before implementation starts

## Read First
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

Always start from `spec-dock/active/*`. When no active context exists, those paths already resolve to the built-in placeholder provided by SpecDock.

## Learn SpecDock

For SpecDock usage and workflow details, start here:
- `spec-dock/docs/guide.md`: overall entry point
- `spec-dock/docs/workflow-tree.md`: tree structure, active context, and sync outputs
- `spec-dock/docs/workflow_issue.md`: issue execution workflow
- `spec-dock/docs/reference_sync.md`: sync behavior and generated artifacts

## Operating Rules
- Treat repo docs as the source of truth, not chat history.
- Do not implement until issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Record decisions, validation, and unresolved items in issue `report.md`.
- Run `./spec-dock/scripts/spec-dock active show` at session start.
- Run `./spec-dock/scripts/spec-dock validate` after structural changes and before handoff.
- Use `./spec-dock/scripts/spec-dock sync` only to regenerate CLI-managed views, pointers, or exported state. Do not use it as a general repair step.

## Source Boundaries
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo, product, and domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `ADR`: accepted durable decisions
- `discussion`: supporting rationale and context; may include superseded options

## Do Not
- Do not treat chat logs as canonical instructions.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not store repo, product, domain, or session rules in this file.

## Escalate When
- Active docs conflict with each other or with the repository root `AGENTS.md`.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- It is unclear whether a file is CLI-managed or safe to edit manually.
- A structural change would broadly rewrite SpecDock-managed docs or generated state.
```

### v6 からの改善
- `spec-dock/system/active-none/` を直接読ませる導線を削除
- `spec-dock/active/*` を常に入口とするルールに統一
- SpecDock docs への参照導線を追加し、guide / workflow / reference の入口を明示

### 自己評価
- 長所:
  - active symlink の実際の挙動と一致するため説明が素直になった
  - bootstrap guide から SpecDock docs への遷移が自然になった
  - `spec-manager` に依頼しつつ、必要なら人が deeper docs を読める導線も確保できた
- 懸念:
  - docs path を増やしすぎると bootstrap guide の密度が上がるため、参照先は 4 つ程度が上限

### review log
- spec review:
  - pass
  - `active-none` への明示誘導を外し、`spec-dock/active/*` に一本化したことで operational model が改善
  - `Learn SpecDock` は navigational guidance に留まっており bootstrap bridge の範囲内
  - authority / scope boundary も維持されている
  - 残りは docs pointer の量に関する editorial guardrail のみ

## V8

### ねらい
- auto-ingested prompt として自然に読めるよう、冒頭の contract を file-centric wording から instruction-centric wording へ置き換える。
- V7 の operational model を維持したまま、prompt perspective の不自然さを減らす。

### ドラフト
```md
# SpecDock Bootstrap Bridge

Treat these instructions as a temporary SpecDock bootstrap bridge.

Apply them only when `.codex/config.toml` configures `.codex/AGENTS.md` as a fallback project document and the repository root does not already provide authoritative `AGENTS.md` guidance for the same scope.

Resolve overlap by scope: `spec-dock/active/*` defines the current task contract, the repository root `AGENTS.md` defines repo, product, and domain rules, `.codex/config.toml` defines session and orchestrator behavior, and these instructions remain subordinate bootstrap guidance.

Limit these instructions to SpecDock bootstrap workflow rules such as active-doc discovery, `validate` / `sync` usage, handling of SpecDock-managed files, default delegation for SpecDock operations, and a short capability summary for first use.
Do not apply them to repo architecture, product/domain guidance, coding conventions, testing policy, or session/orchestrator behavior.

If the repository root `AGENTS.md` exists, treat it as authoritative for repo, product, and domain guidance. Keep these instructions limited to bootstrap workflow rules only.

## Default Operator

Treat `spec-manager` as the default specialist for SpecDock operations.

Use `spec-manager` by default for SpecDock workflows instead of operating the tool ad hoc. If `spec-manager` delegates to other specialists, the authoritative task contract still comes from `spec-dock/active/*` and the current issue docs.

## What SpecDock Can Do

SpecDock provides a CLI workflow for spec-driven execution. It can:
- create and import spec nodes such as initiatives, epics, issues, and discussion docs
- maintain the active working context for the current task
- validate the tree and diagnose broken or incomplete state
- regenerate CLI-managed derived state
- check dependency readiness before implementation starts

## Read First
1. `spec-dock/active/issue/{requirement,design,plan}.md`
2. `spec-dock/active/epic/{requirement,design,plan}.md`
3. `spec-dock/active/initiative/{requirement,design,plan}.md`
4. Repository root `AGENTS.md`, if it exists

Always start from `spec-dock/active/*`. When no active context exists, those paths already resolve to the built-in placeholder provided by SpecDock.

## Learn SpecDock

For SpecDock usage and workflow details, start here:
- `spec-dock/docs/guide.md`: overall entry point
- `spec-dock/docs/workflow-tree.md`: tree structure, active context, and sync outputs
- `spec-dock/docs/workflow_issue.md`: issue execution workflow
- `spec-dock/docs/reference_sync.md`: sync behavior and generated artifacts

## Operating Rules
- Treat repo docs as the source of truth, not chat history.
- Do not implement until issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Record decisions, validation, and unresolved items in issue `report.md`.
- Run `./spec-dock/scripts/spec-dock active show` at session start.
- Run `./spec-dock/scripts/spec-dock validate` after structural changes and before handoff.
- Use `./spec-dock/scripts/spec-dock sync` only to regenerate CLI-managed views, pointers, or exported state. Do not use it as a general repair step.

## Source Boundaries
- `spec-dock/active/*`: current task contract
- Repository root `AGENTS.md`: repo, product, and domain rules
- `.codex/config.toml`: session behavior and orchestrator rules
- `.codex/AGENTS.md`: bootstrap-only SpecDock operating rules
- `ADR`: accepted durable decisions
- `discussion`: supporting rationale and context; may include superseded options

## Do Not
- Do not treat chat logs as canonical instructions.
- Do not start implementation before issue `requirement.md`, `design.md`, and `plan.md` are aligned.
- Do not hand-edit `spec-dock/active/*` links or `.path` files.
- Do not hand-edit CLI-managed generated views or exported state when `sync` owns regeneration.
- Do not use these instructions for repo, product, domain, or session rules.

## Escalate When
- Active docs conflict with each other or with the repository root `AGENTS.md`.
- `validate` fails and the cause is unclear.
- Dependency readiness blocks implementation.
- It is unclear whether a file is CLI-managed or safe to edit manually.
- A structural change would broadly rewrite SpecDock-managed docs or generated state.
```

### v7 からの改善
- `This file ...` / `Use it ...` を `Treat these instructions ...` / `Apply them ...` に置換
- file metadata の語りよりも、auto-ingested instruction の適用契約を前面に出した
- `Do Not` も `use these instructions` ベースに揃え、視点の一貫性を上げた

### 自己評価
- 長所:
  - startup prompt として読まれたときの perspective mismatch が減る
  - authority / scope / fallback 条件はそのまま維持できる
  - V7 の operational model を壊さずに delivery semantics を改善できた
- 懸念:
  - `.codex/AGENTS.md` への path reference 自体は authority 説明に必要なので、self-reference と path reference の線引きは意識し続ける必要がある

### review log
- consultant:
  - ユーザーのフィードバックは妥当
  - best practice は document-centric narration ではなく prompt-native instruction phrasing
  - `Default Operator` / `Source Boundaries` / `Learn SpecDock` は現状維持でよい
- spec review:
  - pass
  - opening は auto-ingested prompt に対して正しく instruction-centric になった
  - authority model / scope boundary / default operator section はいずれも適切
  - 残りは `Read First` や capability summary の editorial polish のみ

## 最終採用案
- 採用バージョン: V8
- 理由:
  - `AGENTS.md` が startup prompt に自動取り込みされる前提に合わせ、導入部を prompt-native な instruction phrasing に修正できた
  - V7 の operational model、authority resolution、scope boundary、docs 導線を維持したまま、不自然な自己言及を減らせた
  - spec reviewer も final best-practice candidate として `PASS` 判定
- 提出ステータス:
  - final best-practice candidate
