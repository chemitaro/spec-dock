---
種別: 実装計画書（Issue）
ID: "iss-00050"
タイトル: "Host Adapter Scaffold And Final Parity"
関連GitHub: ["#50"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
依存: ["requirement.md", "design.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00050 Host Adapter Scaffold And Final Parity — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - issue-00049 protocol contract を変更しない
  - unknown custom skills を pruning しない
  - adapter を thin entrypoint に保つ

## 実装順序の根拠
- `design.md` の依存関係分析を正本にする。
- issue-00049 protocol / installer ownership / bundled asset pattern が upstream なので、これを前提に step を並べる。
- 依存の少ない adapter asset / metadata contract を先に固定し、その contract を installer sync へ接続してから parity / final review へ進む。
- したがって順序は S01（spec fixed point）→ S02（installer sync）→ S03（parity / docs / validate）→ S04（final review）とする。
- TDD の各 iteration でも、asset shape → ownership/sync → parity/validation の順に閉じ、未解決依存を抱えたまま downstream step へ進まない。

## マイルストーン一覧
- M1:
  - 対象:
    - adapter asset / metadata layout の fixed point 化
  - exit:
    - installer, assets, tests の変更面が確定している
- M2:
  - 対象:
    - installer managed asset sync への adapter 導入
  - exit:
    - init/update で adapter が同期される
- M3:
  - 対象:
    - dogfooding parity / docs parity / final spec review
  - exit:
    - validate, relevant tests, parity evidence, spec review pass が揃う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - host adapter の thin contract と metadata 方針が docs/design で固定される
  - closes:
    - なし（spec gate）
  - review gate:
    - spec review pass
- S02:
  - 観測可能な振る舞い:
    - `init/update` で host adapter assets が managed sync される
  - closes:
    - AC-001
    - EC-001
    - EC-002
  - review gate:
    - installer tests が green
- S03:
  - 観測可能な振る舞い:
    - adapter assets が thin host adapter contract を満たし、parity / validate / docs が揃う
  - closes:
    - AC-002
    - AC-003
    - EC-003
  - review gate:
    - content review, parity evidence, validate pass
- S04:
  - 観測可能な振る舞い:
    - epic-00048 final spec review が pass し、2 issue split に矛盾がない
  - closes:
    - AC-004
  - review gate:
    - final spec review record が pass

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S03
- AC-004 -> S04
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S03

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前
    - S04 final close 前
  - scope:
    - thin adapter contract、issue boundary、final epic consistency
  - commit gate:
    - 初回 SG1 pass 後は `report.md` を更新し、その更新を含めて docs-only commit を原則作成する。final SG1 でも追加差分があれば同様に commit する
- RG1 implementation review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - installer changes、asset layout、adapter thinness
  - commit gate:
    - 各 RG1 pass 後に `report.md` を更新し、その stage で確定した差分と report を 1 commit にまとめる
- QG1 QA review:
  - timing:
    - S03 完了後
  - scope:
    - init/update behavior、parity evidence、validate
  - commit gate:
    - QG1 pass 後に `report.md` を更新し、QA 反映済みの最終差分と report を commit して S04 へ渡す
- step approval loop:
  - SG1 pass 後に S02 へ進む
  - S02 後は RG1 pass を取ってから S03 へ進む
  - S03 後は RG1/QG1 pass を取ってから S04 へ進む
  - S04 は final SG1 pass を取って close 候補にする

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

### S01 — spec fixed point for host adapter deployment
- target:
  - issue docs
  - epic handoff from issue-00049
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/design.md`
- step boundary:
  - thin adapter contract と metadata 方針が reviewer-pass になるまで

#### step gate
- review:
  - SG1/spec review pass
- expected tests:
  - なし（docs review only）
- report update:
  - spec review verdict / fixed point / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - thin adapter contract と metadata fixed point、および report 更新をまとめて commit し、後続の実装差分と分離する

### S02 — installer managed asset sync for host adapters
- target:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/`
  - installer tests
- design refs:
  - `spec-dock/active/issue/design.md`
- step boundary:
  - init/update が adapter assets を managed sync できるまで

#### B1 — asset layout
- purpose:
  - adapter skill directories と metadata asset を定義する
- files:
  - `src/spec_dock/assets/codex_skills/`
  - required metadata asset path

##### I1 — add adapter assets
- slice goal:
  - Codex/Copilot adapter scaffold を provider assets に追加する

###### Red
- failing test:
  - installer asset expectation test
- expected failure:
  - adapter asset が存在しない

###### Green
- minimum implementation:
  - adapter asset を追加し installer sync 対象へ含める
- pass condition:
  - asset existence / sync verification が green

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — installer ownership and pruning
- purpose:
  - managed ownership を安全に広げる
  - unknown custom skills を保持したまま managed prune する
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`

##### I1 — extend managed skill lists
- slice goal:
  - adapter を managed sync / obsolete prune の対象へ入れる

###### Red
- failing test:
  - init/update managed skill tests
  - unknown custom skill preservation test
- expected failure:
  - adapter が配布されない、または pruning safety が崩れる

###### Green
- minimum implementation:
  - managed skill names / ownership names / copy loop を更新
- pass condition:
  - init/update tests が green
  - unknown custom skills が preserve される

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
- expected tests:
  - relevant installer tests
  - unknown custom skill preservation test
- report update:
  - review verdict / test結果 / 修正内容を `./spec-dock/active/issue/report.md` に残す
- commit:
  - installer managed asset sync 差分と report 更新を 1 commit として確定する

### S03 — adapter thinness, dogfooding parity, docs parity
- target:
  - adapter `SKILL.md`
  - dogfooding `.agents/skills/`
  - related docs and parity evidence
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/design.md`
- step boundary:
  - adapter content が thin contract を満たし、provider/dogfooding parity と validate が揃うまで

#### B1 — adapter content reviewability
- purpose:
  - host-specific wording だけを持つ scaffold にする
- files:
  - adapter skill files
  - metadata file if present

##### I1 — keep protocol references thin
- slice goal:
  - issue-00049 protocol を参照するだけの adapter にする

###### Red
- failing test:
  - content review / snapshot check
- expected failure:
  - adapter が厚すぎる、または contract が曖昧

###### Green
- minimum implementation:
  - thin wording に整える
- pass condition:
  - review で thin adapter contract を確認できる

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

#### B2 — parity and validation
- purpose:
  - provider/dogfooding/docs parity を閉じる
- files:
  - dogfooding `.agents/skills/`
  - related docs/tests

##### I1 — refresh generated workspace and verify
- slice goal:
  - dogfooding workspace を provider asset に揃える

###### Red
- failing test:
  - parity / validate evidence
- expected failure:
  - drift が残る

###### Green
- minimum implementation:
  - update / sync / validate で parity を回復する
- pass condition:
  - validate pass と parity evidence が揃う

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
  - relevant installer tests
  - `./spec-dock/scripts/spec-dock validate`
- report update:
  - review verdict / QA verdict / parity evidence / validation結果を `./spec-dock/active/issue/report.md` に残す
- commit:
  - adapter thinness / parity / QA反映込みの差分と report 更新を 1 commit として確定する

### S04 — final spec review and close readiness
- target:
  - issue-00049/00050 docs
  - epic-00048 docs
  - report evidence
- design refs:
  - both issue docs and epic docs
- step boundary:
  - reviewer が 2 issue split に矛盾なしと判断できるまで

#### step gate
- review:
  - SG1/spec review pass
- expected tests:
  - evidence review only
- report update:
  - final spec review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - final spec review で追加入力があれば closing commit を作成し、無ければ直前 gate の commit を最終成果として扱う

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / skills / dogfooding workspace
- 対応:
  - provider/dogfooding parity と final wording を揃え、close evidence を report に残す

### S99 — final diff review quality gate
- branch diff scope:
  - issue-00050 で更新した installer / assets / dogfooding outputs / docs
- required validation:
  - relevant installer tests
  - `./spec-dock/scripts/spec-dock validate`
  - parity evidence
- reviewer approvals:
  - spec review pass
  - implementation review pass
  - QA review pass
- commit expectation:
  - final diff review -> report update 後に追加修正があれば最終 commit を作成し、追加修正が無ければ直前 gate の commit を最終成果として扱う

## 未確定事項
- なし:
  - metadata file を実装する前提で S02/S03 を進める。

## final exit contract
- AC/EC 達成:
  - AC-001..004 と EC-001..003 の evidence が揃う
- docs impact resolved:
  - provider/dogfooding/docs parity が確認できる
- final diff approved:
  - S99 reviewer approvals が pass している
