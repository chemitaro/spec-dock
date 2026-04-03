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
  - 本 issue は protocol contract surface の runtime/provider-doc/dogfooding-doc/test parity までを担当し、adapter scaffold 残件と final epic parity/review は issue-00050 に残す
  - full-history artifact を削除しない
  - provider-side source of truth から修正する

## マイルストーン一覧
- M1:
  - 対象:
    - protocol contract の fixed point 化
  - exit:
    - requirement/design/plan と epic plan の scope boundary、および provider docs の変更対象が一致している
- M2:
  - 対象:
    - runtime payload / context pack alignment
  - exit:
    - generated state と context pack が新 contract を表現できる
- M3:
  - 対象:
    - docs/tests parity
  - exit:
    - 本 issue が変更する protocol contract surface について provider/dogfooding docs と relevant tests が一致して green になる
    - adapter scaffold 起因の残件 parity / final epic review は issue-00050 に明示的に handoff されている

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - protocol read order・artifact metadata responsibility・issue-00049/00050 scope boundary が docs/design/epic plan で固定される
  - closes:
    - なし（baseline / spec gate）
  - review gate:
    - spec review で issue contract、artifact ごとの metadata contract、issue-00049/00050 scope split が pass している
- S02:
  - 観測可能な振る舞い:
    - generated JSON payload が次を表現できる:
      - `index.json`: top-level `projection=current-future`、new top-level `source` なし
      - `index-all.json`: top-level `projection=full-history`、new top-level `source` なし
      - `deps-issues.json`: top-level `projection=open-issues-dependency-view`、top-level `source` は artifact provenance のまま
      - existing per-node issue status `source` semantics unchanged
  - closes:
    - AC-002
    - EC-002
  - review gate:
    - payload verification tests が green
    - fail-closed deps placeholder verification が green で、`deps-issues.json` の projection/provenance contract 維持が確認できる
- S03:
  - 観測可能な振る舞い:
    - context pack と docs が `active -> index/deps -> index-all(if needed)` を一貫して示し、active-none placeholder path でも入口 contract を崩さない
  - closes:
    - AC-001
    - AC-003
    - EC-001
    - EC-003
  - review gate:
    - provider/dogfooding docs parity（本 issue の contract surface）が green
    - active-none placeholder / context-pack read-order verification が green
    - runtime read-order verification が green

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
  - commit gate:
    - SG1 pass 後に `report.md` を更新し、その更新を含めて docs-only commit を原則作成する。no-op の場合だけ理由を `report.md` に残す
- RG1 implementation review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - payload metadata、context-pack wording、docs parity
  - commit gate:
    - 各 RG1 pass 後に `report.md` を更新し、その stage で確定した差分と report を 1 commit にまとめる
- QG1 QA review:
  - timing:
    - S03 完了後
  - scope:
    - `sync` / `validate` と snapshot evidence
  - commit gate:
    - QG1 pass 後に `report.md` を更新し、QA 反映済みの最終差分と report を commit して S99 へ渡す
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
- 各 review/test cycle は reviewer status が `pass` になるまで fix -> re-review / re-test を繰り返す。
- 各 stage gate（SG/RG/QG）通過後は、先に `report.md` を更新し、その gate で確定した差分と report を原則まとめて commit する。no-op の場合のみ `report.md` に理由を残す。

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
  - spec review verdict / fixed point / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - docs fixed point と report 更新をまとめて commit し、以後の実装差分と分離する

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
  - `index.json` / `index-all.json` の projection と top-level `source` 非追加 contract を固定する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - relevant tests

##### I1 — add projection metadata
- slice goal:
  - `current-future` と `full-history` を payload で判別可能にし、index artifacts に new top-level `source` を増やさないことを固定する

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
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — deps view
- purpose:
  - `deps-issues.json` の default dependency view と provenance `source` contract を固定する
- files:
  - same as above

##### I1 — keep source/projection explicit
- slice goal:
  - issue-only dependency view の projection と artifact provenance `source` を payload と tests で固定し、per-node issue status `source` semantics は維持する

###### Red
- failing test:
  - deps-issues artifact verification
- expected failure:
  - projection/meaning が不明確

###### Green
- minimum implementation:
  - projection/source metadata contract を artifact ごとに整える
- pass condition:
  - `deps-issues.json` verification が green
  - fail-closed placeholder verification でも projection/provenance contract が崩れない

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - RG1/implementation review
- expected tests:
  - relevant runtime/presentation tests
  - deps invalid placeholder / fail-closed verification
- report update:
  - review verdict / test結果 / 修正内容を `./spec-dock/active/issue/report.md` に残す
- commit:
  - payload metadata / deps view alignment と report 更新を 1 commit として確定する

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
  - `deps-issues.json` と `index-all.json` の位置づけ、および active-none placeholder 時の入口 contract を明示する

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
  - active-none placeholder read-order verification が green

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — provider/dogfooding docs parity
- purpose:
  - 本 issue が変更する protocol contract surface の docs explanation を runtime contract に揃える
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_sync.md`

##### I1 — align wording and examples
- slice goal:
  - normal path / escalation path / issue-00049 と issue-00050 の責務境界の説明を統一する

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
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - RG1 implementation review
  - QG1 QA review
- expected tests:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - relevant automated tests
  - active-none placeholder / context-pack verification
- report update:
  - review verdict / QA verdict / validation evidence / 追加修正内容を `./spec-dock/active/issue/report.md` に残す
- commit:
  - context pack / docs parity / QA反映込みの差分と report 更新を 1 commit として確定する

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - 本 issue が変更した protocol contract surface について provider docs と dogfooding docs の parity を確認し、adapter scaffold 起因の残件だけを issue-00050 へ handoff できる fixed point を残す

### S99 — final diff review quality gate
- branch diff scope:
  - issue-00049 で更新した protocol contract surface の provider docs / runtime / tests / dogfooding outputs
- required validation:
  - relevant automated tests
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
- reviewer approvals:
  - spec review pass
  - implementation review pass
  - QA review pass
- commit expectation:
  - 追加修正があれば final diff review -> report update の後に最終 commit を作成し、追加修正が無ければ直前 gate の commit を最終成果として扱う

## 未確定事項
- なし:
  - `projection` key naming は固定し、top-level `source` contract は artifact ごとに固定した前提で S02 を進める。

## final exit contract
- AC/EC 達成:
  - AC-001..003 と EC-001..003 の evidence が揃う
- docs impact resolved:
  - provider/dogfooding docs parity が確認できる
- final diff approved:
  - S99 reviewer approvals が pass している
