---
種別: 実装計画書（Issue）
ID: "iss-00049"
タイトル: "Protocol Contract And Runtime Alignment"
関連GitHub: ["#49"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
依存: ["requirement.md", "design.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00049 Protocol Contract And Runtime Alignment — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - host adapter 実装は本 issue に含めない
  - full-history artifact を削除しない
  - provider-side source of truth から修正する

## マイルストーン一覧
- M1:
  - 対象:
    - protocol contract の fixed point 化
  - exit:
    - requirement/design/plan と provider docs の変更対象が一致している
- M2:
  - 対象:
    - runtime payload / context pack alignment
  - exit:
    - generated state と context pack が新 contract を表現できる
- M3:
  - 対象:
    - docs/tests parity
  - exit:
    - provider/dogfooding docs と relevant tests が一致して green になる

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - protocol read order と payload responsibility が docs/design で固定される
  - closes:
    - なし（baseline / spec gate）
  - review gate:
    - spec review で issue contract が pass している
- S02:
  - 観測可能な振る舞い:
    - generated JSON payload が `current-future` / `full-history` / `open-issues-dependency-view` を表現できる
  - closes:
    - AC-002
    - EC-002
  - review gate:
    - payload verification tests が green
- S03:
  - 観測可能な振る舞い:
    - context pack と docs が `active -> index/deps -> index-all(if needed)` を一貫して示す
  - closes:
    - AC-001
    - AC-003
    - EC-001
    - EC-003
  - review gate:
    - docs parity と runtime verification が green

## 要件 ↔ ステップ対応
- AC-001 -> S03
- AC-002 -> S02
- AC-003 -> S03
- EC-001 -> S03
- EC-002 -> S02
- EC-003 -> S03

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前に pass を取得する
  - scope:
    - read-order contract、scope boundary、verification mapping
- RG1 implementation review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - payload metadata、context-pack wording、docs parity
- QG1 QA review:
  - timing:
    - S03 完了後
  - scope:
    - `sync` / `validate` と snapshot evidence
- step approval loop:
  - SG1 pass 後に S02 へ進む
  - S02 後は RG1 pass を取ってから S03 へ進む
  - S03 後は RG1/QG1 pass を取ってから close 候補にする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。

## 実装ステップ

### S01 — spec fixed point for protocol contract
- target:
  - issue docs
  - epic alignment
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/design.md`
- step boundary:
  - 実装前に read-order と projection boundary を reviewer-pass 状態にする

#### step gate
- review:
  - SG1/spec review pass
- expected tests:
  - なし（docs review only）
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — payload metadata and dependency-view alignment
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - relevant runtime/presentation tests
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - generated JSON payload の projection/role が検証可能になるまで

#### B1 — index payloads
- purpose:
  - `index.json` / `index-all.json` の projection を固定する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - relevant tests

##### I1 — add projection metadata
- slice goal:
  - `current-future` と `full-history` を payload で判別可能にする

###### Red
- failing test:
  - payload snapshot / shape verification
- expected failure:
  - projection metadata が存在しない

###### Green
- minimum implementation:
  - payload metadata を追加し tests を通す
- pass condition:
  - `index.json` / `index-all.json` の shape が期待どおり

###### Refactor
- cleanup target:
  - metadata naming の重複整理
- invariants to keep green:
  - 既存 consumer が壊れない

#### B2 — deps view
- purpose:
  - `deps-issues.json` の default dependency view を固定する
- files:
  - same as above

##### I1 — keep source/projection explicit
- slice goal:
  - issue-only dependency view の由来を payload と tests で固定する

###### Red
- failing test:
  - deps-issues artifact verification
- expected failure:
  - projection/meaning が不明確

###### Green
- minimum implementation:
  - projection/source metadata を整える
- pass condition:
  - `deps-issues.json` verification が green

###### Refactor
- cleanup target:
  - duplicated constants / wording
- invariants to keep green:
  - fail-closed placeholder behavior を維持する

#### step gate
- review:
  - RG1/implementation review
- expected tests:
  - relevant runtime/presentation tests
- report update:
  - `./spec-dock/active/issue/report.md`

### S03 — context pack and docs parity alignment
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - dogfooding generated docs / context pack
  - relevant tests
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - docs / context pack / generated state が同じ read order を示すまで

#### B1 — context pack guidance
- purpose:
  - generated `context-pack.md` の read order を直す
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - maybe `presentation/json_state.py`
  - tests

##### I1 — refresh read order and generated state section
- slice goal:
  - `deps-issues.json` と `index-all.json` の位置づけを明示する

###### Red
- failing test:
  - context pack snapshot verification
- expected failure:
  - read order が old contract のまま

###### Green
- minimum implementation:
  - generated context pack wording を更新
- pass condition:
  - snapshot verification が green

###### Refactor
- cleanup target:
  - duplicated context rendering logic
- invariants to keep green:
  - active-none fallback を壊さない

#### B2 — provider/dogfooding docs parity
- purpose:
  - docs explanation を runtime contract に揃える
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_sync.md`

##### I1 — align wording and examples
- slice goal:
  - normal path / escalation path の説明を統一する

###### Red
- failing test:
  - docs parity check or manual diff evidence
- expected failure:
  - wording drift が残る

###### Green
- minimum implementation:
  - provider/dogfooding docs を同期
- pass condition:
  - parity evidence が揃う

###### Refactor
- cleanup target:
  - repetitive wording の整理
- invariants to keep green:
  - `sync --force` / placeholder 説明を落とさない

#### step gate
- review:
  - RG1 implementation review
  - QG1 QA review
- expected tests:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - relevant automated tests
- report update:
  - `./spec-dock/active/issue/report.md`

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - provider docs と dogfooding docs の parity を確認し、issue-00050 へ handoff できる fixed point を残す

### S99 — final diff review quality gate
- branch diff scope:
  - issue-00049 で更新した provider docs / runtime / tests / dogfooding outputs
- required validation:
  - relevant automated tests
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer approvals:
  - spec review pass
  - implementation review pass
  - QA review pass

## 未確定事項
- なし:
  - `projection` key naming は固定し、`source` metadata も追加する前提で S02 を進める。

## final exit contract
- AC/EC 達成:
  - AC-001..003 と EC-001..003 の evidence が揃う
- docs impact resolved:
  - provider/dogfooding docs parity が確認できる
- final diff approved:
  - S99 reviewer approvals が pass している
