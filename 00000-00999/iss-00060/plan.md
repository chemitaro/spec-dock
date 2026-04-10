---
種別: 実装計画書（Issue）
ID: "iss-00060"
タイトル: "Meta json dependency schema and reader alignment"
関連GitHub: ["#60"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00060 Meta json dependency schema and reader alignment — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
- 制約:
  - `DepsTopologyLoadResult` の downstream surface は変えない
  - `deps.json` dual-read / fallback migration は導入しない
  - mutation command / downstream parity / dogfooding checked-in data manual fix / dogfooding `validate`・`sync` evidence は `iss-00062` owner に残し、T1 completion gate に含めない

## マイルストーン一覧
- M1:
  - 対象:
    - `.meta.json` dependency schema と hard cutover boundary note の固定
  - exit:
    - field 名、default、raw value grammar、T1/T3 owner split が docs 上で確定している
- M2:
  - 対象:
    - `deps_reader.py` の read source 切り替えと low-level reader unit
  - exit:
    - `.meta.json` source で `DepsTopologyLoadResult` を current contract どおり返せる
- M3:
  - 対象:
    - downstream smoke と docs refresh を含む close-ready packet
  - exit:
    - schema / reader / boundary note / unit tests の組が reviewer に追え、provider-side `reference_deps.md` 更新が正本として確認できる

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - schema と owner boundary が未固定だと reader 実装の acceptance が定まらないため、S01 を先に置く
  - downstream consumer は `DepsTopologyLoadResult` に依存しているため、S02 では return shape を変えずに source file だけを置換する
  - docs refresh と final packet は code/test の観測点が揃ってから S90 / S99 で閉じる
- step ordering notes:
  - S01 が S02 の acceptance basis
  - S02 が S90 の smoke / docs refresh basis
  - S90 は code/test 観測点の確定後にのみ実施する

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `.meta.json` dependency schema と T1/T3 boundary note が reviewer にとって曖昧でない
  - closes:
    - AC-001
    - AC-003
    - EC-004
  - review gate:
    - schema と owner split が spec review で pass
- S02:
  - 観測可能な振る舞い:
    - `deps_reader.py` が `.meta.json` を唯一の read source として `DepsTopologyLoadResult` を current contract どおり返す
  - closes:
    - AC-002
    - EC-001
    - EC-002
    - EC-003
  - review gate:
    - reader-focused unit tests と minimal downstream smoke が pass
- S90:
  - 観測可能な振る舞い:
    - docs / examples / runbook wording が T1 boundary に整列している
  - closes:
    - AC-001
    - AC-003
  - review gate:
    - docs diff が schema/read boundary だけに留まっている
- S99:
  - 観測可能な振る舞い:
    - final diff review で T1 scope leak が無い
  - closes:
    - final exit contract
  - review gate:
    - final diff review approval

## 要件 ↔ ステップ対応
- AC-001 -> S01, S90
- AC-002 -> S02
- AC-003 -> S01, S90
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S02
- EC-004 -> S01

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前
    - S01 完了後
  - scope:
    - `.meta.json` schema
    - `DepsTopologyLoadResult` 互換
    - T1/T3 owner split
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- RG1 implementation review:
  - timing:
    - S02 完了後
    - S99 前の final review
  - scope:
    - `deps_reader.py` source change
    - no dual-read / no fallback
    - unit test coverage の妥当性
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S02 完了後
    - S90 完了後
    - S99 前の final review
  - scope:
    - reader-focused unit tests
    - minimal downstream smoke
    - provider-side `reference_deps.md` 更新確認
    - dogfooding `spec-dock/docs/reference_deps.md` の secondary verification
  - commit gate:
    - pass まで test/review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- T1 scope を越える defect / parity gap / cutover作業が見つかった場合は、この issue で暗黙拡張せず `report.md` に記録して stop / escalate する。

## 実装ステップ

### S01 — schema and boundary lock
- target:
  - issue docs
  - provider-side dependency reference docs
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
- step boundary:
  - `.meta.json` `depends_on` schema、default、raw value grammar、hard cutover boundary note を固定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — schema wording
- purpose:
  - storage boundary と reader acceptance を先に固定する
- files:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_deps.md`（secondary verification）

##### I1 — define top-level depends_on contract
- slice goal:
  - `.meta.json` top-level `depends_on` と field absence=`[]` を明文化する

###### Red
- failing test:
  - なし
- expected failure:
  - schema が曖昧だと reader 実装の acceptance と T3 owner split が決まらない

###### Green
- minimum implementation:
  - spec と provider-side docs に schema と boundary note を反映し、dogfooding docs は secondary verification として整合を確認する
- pass condition:
  - reviewer が `.meta.json` SoT、provider-side docs 正本、T1/T3 owner split を一読で追える

###### Refactor
- 目的:
  - Green を維持したまま、spec と reference docs の言い回しを揃える
- guardrail:
  - 振る舞いを変えない
  - T1 scope を越えて mutation / parity の話を膨らませない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - SG1 spec review pass
- expected tests:
  - なし
- report update:
  - reviewer verdict / owner split / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — reader source alignment and unit hardening
- target:
  - `infra/deps_reader.py`
  - reader-focused tests
- design refs:
  - `spec-dock/active/issue/design.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`
- step boundary:
  - `.meta.json` source へ reader を切り替え、`DepsTopologyLoadResult` 互換を保ったまま unit tests を通す

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — low-level meta loader
- purpose:
  - `.meta.json` payload から `depends_on` を安全に取り出す helper を導入する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - 必要なら focused test file

##### I1 — missing field defaults to empty
- slice goal:
  - `depends_on` 未設定時の default を `[]` に固定する

###### Red
- failing test:
  - `.meta.json` に `depends_on` が無いときに empty dependency として扱う test 1 本
- expected failure:
  - 既存 reader は `deps.json` を見に行くため `.meta.json` default contract を満たせない

###### Green
- minimum implementation:
  - `.meta.json` loader を追加し、missing field を `[]` へ正規化する
- pass condition:
  - missing-field default test が pass する

###### Refactor
- 目的:
  - Green を維持したまま、meta loader と existing ref resolver の責務を分離する
- guardrail:
  - return shape を変えない
  - `fs_repo.py` へ不要な責務移譲をしない
  - 必要がなければスキップしてよい

##### I2 — invalid schema fails closed
- slice goal:
  - unsupported `depends_on` type / element を明示 error にする

###### Red
- failing test:
  - bool / object / invalid string を含む `.meta.json` に対する fail-closed test 1 本
- expected failure:
  - current implementation は `.meta.json` schema validation をまだ持たない

###### Green
- minimum implementation:
  - type validation と error wording を追加する
- pass condition:
  - invalid schema test が pass し、曖昧な normalize を行わない

###### Refactor
- 目的:
  - エラー文言と helper 名を整える
- guardrail:
  - failure mode を増やさない
  - T1 scope を越えて cycle validation を reader に足さない
  - 必要がなければスキップしてよい

#### B2 — compile contract preservation
- purpose:
  - shorthand 解決、issue-level compile、warning、dedupe/sort を current contract どおり保つ
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `tests/cli_runtime/test_deps.py`
  - 必要最小限で `tests/cli_runtime/test_sync.py`
  - 必要最小限で `tests/cli_runtime/test_active.py`

##### I1 — preserve compile and warning semantics
- slice goal:
  - `.meta.json` source でも `deps_ref_expanded_to_empty` と canonical issue map が崩れない

###### Red
- failing test:
  - issue/epic/initiative shorthand compile または empty expansion warning の focused test 1 本
- expected failure:
  - source file 切り替え後に current compile semantics を失うと downstream contract が壊れる

###### Green
- minimum implementation:
  - `load_issue_depends_on_map()` を `.meta.json` source に切り替え、existing helper を再利用する
- pass condition:
  - focused compile/warning tests が pass し、`DepsTopologyLoadResult` shape が維持される

###### Refactor
- 目的:
  - helper の重複を減らしつつ compile semantics を読みやすくする
- guardrail:
  - downstream consumer の呼び出し方を変えない
  - warning code を変えない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - RG1 implementation review pass
  - QG1 QA review pass
- expected tests:
  - `python -m unittest tests.cli_runtime.test_deps -v`
  - 必要最小限の related dependency tests
- report update:
  - reviewer verdict / test結果 / 追加した helper / scope spill の有無を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md` の schema 例、storage source、hard cutover boundary note を T1 契約へ更新する
  - `spec-dock/docs/reference_deps.md` は secondary verification として provider-side wording との差分を確認する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — dependency reference refresh
- purpose:
  - operator / reviewer 向け docs で `deps.json` SoT を残さない
- files:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_deps.md`（secondary verification）

##### I1 — align examples and boundary note
- slice goal:
  - example JSON と note が `.meta.json` schema / T1 boundary に一致する

###### Red
- failing test:
  - なし
- expected failure:
  - docs が古いままだと reviewer が read source を誤認する

###### Green
- minimum implementation:
  - provider-side docs example / note を更新し、dogfooding docs が secondary verification として整合することを確認する
- pass condition:
  - docs review で schema/read boundary と provider/dogfooding の責務差分に誤読余地がない

###### Refactor
- 目的:
  - docs 内の表現揺れを最小限で減らす
- guardrail:
  - new behavior を追加しない
  - T3 cutover evidence の本文まで抱え込まない
  - 必要がなければスキップしてよい

#### step gate
- review:
  - QG1 QA review pass
- expected tests:
  - なし
- report update:
  - docs diff summary / provider-side update確認 / dogfooding secondary verification 結果 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00060` の schema / reader / docs / unit tests 差分
- required validation:
  - `python -m unittest tests.cli_runtime.test_deps -v`
  - 必要最小限の related dependency tests
  - provider-side `reference_deps.md` 更新確認
  - dogfooding `spec-dock/docs/reference_deps.md` の secondary verification
- reviewer approvals:
  - SG1 spec review pass
  - RG1 implementation review pass
  - QG1 QA review pass
- report update:
  - final diff review verdict / closing evidence / scope spill の有無 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし:
  - 実装前提の step、gate、owner split はこの plan で固定する

## final exit contract
- AC/EC 達成:
  - `.meta.json` dependency schema、reader source alignment、hard cutover boundary note、reader-focused unit tests が揃っている
  - `DepsTopologyLoadResult` の downstream surface は維持されている
- docs impact resolved:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md` が正本として T1 boundary に更新されている
  - `spec-dock/docs/reference_deps.md` は secondary verification として provider-side wording と整合している
- final diff approved:
  - T1 scope leak がなく、T2/T3/T4 owner を侵食していないと reviewer が判断できる
