---
種別: 実装計画書（Issue）
ID: "iss-00071"
タイトル: "Verification dogfooding and update parity"
関連GitHub: ["#71"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00071 Verification dogfooding and update parity — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
  - `AC-004`
  - `AC-005`
- EC:
  - `EC-001`
  - `EC-002`
- 制約:
  - issue-71 は verification / dogfooding / update parity evidence を閉じる tranche であり、新しい source-of-truth や migration layer は作らない。
  - closure 判定の primary evidence は automated tests / fixture-driven assertions とする。
  - manual `validate` / `sync` / `sync --github` は補助証跡として report に残す。
  - `commands/deps.py` shell layering structural regression は、`validate` / `sync` / `sync --github`、checked-in dogfooding parity、installed package smoke に影響しない限り scope-out とし、full-suite residual risk として扱う。
  - 各実装 step は code review `pass` 後に report を更新し、step 単位でコミットする。
  - `S99` で final code review / final spec review / validate / sync / sync --github / full-suite informational sweep を実施する。

## マイルストーン一覧
- M1:
  - 対象:
    - upstream handoff consumption と checked-in dogfooding parity の closure tests
  - exit:
    - issue-69 / issue-70 の evidence を issue-71 で消費し、checked-in agent-tooling と runtime fixture surface の parity が automated tests で追跡できる
- M2:
  - 対象:
    - runtime command surface と fail-fast / degraded semantics の verification bundle
  - exit:
    - `validate` / `sync` / `sync --github` / `sync --force` が install-shaped layout と矛盾しない evidence を report に集約できる
- M3:
  - 対象:
    - isolated installed package smoke と final report / quality gate
  - exit:
    - checkout / runtime / installed package / dogfooding parity の 4 面が issue-71 report に集約され、E-AC-002 / E-AC-003 を閉じる

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `closure matrix`
- sequencing rule:
  - upstream handoff と checked-in parity を先に固定する
  - runtime command verification は checked-in runtime fixture surface が整合してから束ねる
  - installed package smoke は issue-69 / issue-70 の harness を最後に再消費する
  - report evidence は各 step 後に追記し、S99 で最終レビューする
- step ordering notes:
  - `S01` が issue-69/70 handoff consumption と checked-in parity evidence の入口になる
  - `S02` は runtime command surface の primary evidence を束ねる
  - `S03` は installed package final smoke を closure matrix に接続する
  - `S90` / `S99` は evidence report と final gate に閉じる

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - checked-in dogfooding agent-tooling と runtime fixture surface が `install_root` cutover 後の contract に収束していることを tests で確認できる
  - closes:
    - `AC-001`
    - `AC-002`
    - `EC-001`
  - review gate:
    - targeted tests `pass`
    - code review `pass`
    - report update
    - stage commit
- S02:
  - 観測可能な振る舞い:
    - `validate` / `sync` / `sync --github` / `sync --force` / missing artifact fail-fast の runtime command evidence が install-shaped layout 前提で束ねられる
  - closes:
    - `AC-003`
    - `AC-004`
    - `EC-002`
  - review gate:
    - targeted runtime tests `pass`
    - code review `pass`
    - report update
    - stage commit
- S03:
  - 観測可能な振る舞い:
    - non-editable isolated installed package smoke が checkout fallback なしで issue-71 closure matrix に接続される
  - closes:
    - `AC-005`
  - review gate:
    - installed package targeted smoke `pass`
    - code review `pass`
    - report update
    - stage commit
- S90:
  - 観測可能な振る舞い:
    - issue-71 report の `checkout-verification` / `runtime-command-verification` / `installed-package-verification` / `dogfooding-parity` / `upstream-handoff-consumed` が実測値で埋まる
  - closes:
    - report evidence contract
  - review gate:
    - report completeness review
    - docs-only commit または直前 step commit に含める
- S99:
  - 観測可能な振る舞い:
    - branch 全体が final reviews と quality gates を通り、scope-out residual risk も report に記録される
  - closes:
    - final exit contract
  - review gate:
    - final code review `pass`
    - final spec review `pass`
    - `validate` / `sync` / `sync --github` 成功
    - full-suite informational sweep result 記録
    - final commit

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`, `S90`
- `AC-002` -> `S01`
- `AC-003` -> `S02`
- `AC-004` -> `S02`
- `AC-005` -> `S03`
- `EC-001` -> `S01`
- `EC-002` -> `S02`

## レビュー / QA ゲート方針
- RG1 step code review:
  - timing:
    - `S01` / `S02` / `S03` の各実装後
  - scope:
    - 当該 step の tests / helper / report 差分
  - commit gate:
    - code review `pass` まで review loop を回し、pass 後に `report.md` を更新して差分確認後に commit する
- QG1 targeted validation:
  - timing:
    - 各 step 完了時
  - scope:
    - step 対応の targeted tests と manual supplemental command
  - commit gate:
    - 成功結果を `report.md` に残す
- SG1 spec review:
  - timing:
    - 実装着手前の requirement/design/plan fix
    - `S99` final gate
  - scope:
    - docs の scope 境界、closure matrix、report evidence completeness
  - commit gate:
    - spec review `pass` まで review loop を回す
- Full-suite sweep:
  - timing:
    - `S99`
  - scope:
    - `python -m unittest discover -v`
  - rule:
    - `commands/deps.py` shell layering structural regression が残る場合は residual risk として report に記録する
    - `validate` / `sync` / `sync --github`、checked-in dogfooding parity、installed package smoke に影響する新規 failure は blocker とする

## 実行ルール（全ステップ共通）
- plan は実装着手前に spec review を通して approved にする。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 各 step は `Red → Green → Refactor → code review → fix → re-review → report → commit/no-op` で閉じる。
- failing test は iteration ごとに 1 本ずつ追加する。
- `Refactor` は green 維持前提の bounded cleanup に限る。
- production code 変更が不要な場合は verification tests / report evidence の変更だけで step を閉じてよい。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。
- report には command evidence、review verdict、修正内容、commit hash、scope-out residual risk を残す。

## 実装ステップ

### S01 — checked-in dogfooding parity と upstream handoff consumption を固定する
- target:
  - `tests/test_init_update.py`
  - `report.md`
- design refs:
  - `closure matrix`
  - `upstream handoff evidence`
  - `dogfooding parity evidence`
- step boundary:
  - checked-in agent-tooling parity、runtime fixture surface、issue-69/70 handoff consumption に閉じる
  - runtime command fail-fast / degraded semantics は `S02` へ回す

#### B1 — dogfooding parity regression
- purpose:
  - checked-in `.agents` / `.codex` / `.github` / `.github/workflows` が install-root cutover 後の provider asset と一致することを証明する
- files:
  - `tests/test_init_update.py`

##### I1 — agent-tooling parity map
- slice goal:
  - checked-in agent-tooling files と provider-side `install_root` source の parity を explicit test で固定する
- Red:
  - failing test:
    - issue-71 名前空間の checked-in agent-tooling parity test
  - expected failure:
    - test 未実装
- Green:
  - minimum implementation:
    - `.agents/host-adapters/meta.json`、`.codex/agents/spec-dock.toml`、`.github/agents/spec-dock.agent.md`、`.github/workflows/ci.yml` を `install_root` source と比較する test を追加
  - pass condition:
    - parity test が通る
- Refactor:
  - 目的:
    - 既存 mirror helper を再利用できる範囲だけ整理する
  - guardrail:
    - issue-70 installer contract は変更しない

##### I2 — handoff consumption evidence
- slice goal:
  - issue-69 / issue-70 の required evidence sections が placeholder ではなく、issue-71 の verification input として読めることを固定する
- Red:
  - failing test:
    - issue-69 package parity evidence と issue-70 handoff evidence の presence / non-placeholder test
  - expected failure:
    - issue-71 名前空間の consumption test 未実装
- Green:
  - minimum implementation:
    - evidence-bearing heading / required field / pending placeholder absence を確認する test を追加
  - pass condition:
    - upstream handoff consumption test が通る
- Refactor:
  - 目的:
    - markdown evidence assertion helper を test-local に閉じる
  - guardrail:
    - docs を自動生成しない

#### step gate
- review:
  - code_reviewer に checked-in parity / handoff consumption tests の妥当性をレビューさせる
- expected tests:
  - issue-71 S01 targeted tests
- report update:
  - `checkout-verification`
  - `dogfooding-parity`
  - `upstream-handoff-consumed`
- commit:
  - S01 stage commit

### S02 — runtime command verification bundle を固定する
- target:
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
  - 必要なら `tests/test_init_update.py`
  - `report.md`
- design refs:
  - `runtime command evidence`
  - `closure matrix`
- step boundary:
  - `validate` / `sync` / `sync --github` / `sync --force` と fail-fast / degraded semantics に閉じる
  - deps command shell layering cleanup は scope-out のまま

#### B1 — runtime command evidence mapping
- purpose:
  - existing runtime command tests を issue-71 closure evidence として束ねる
- files:
  - runtime test files
  - `report.md`

##### I1 — validate/sync/sync-github targeted bundle
- slice goal:
  - issue-71 report に記録できる targeted command test set を確定する
- Red:
  - failing test:
    - 必要に応じて issue-71 名前空間の evidence bundle smoke
  - expected failure:
    - issue-71 bundle test 未実装
- Green:
  - minimum implementation:
    - 既存 tests の targeted command set を実行し、足りない assertion があれば最小 test を追加
  - pass condition:
    - `validate` / `sync` / `sync --github` targeted tests が通る
- Refactor:
  - 目的:
    - runtime fixture duplication があれば test-local helper に寄せる
  - guardrail:
    - production behavior は変更しない

##### I2 — fail-fast and degraded semantics
- slice goal:
  - missing artifact fail-fast と `sync --force` degraded warning surface を install-shaped layout 前提で再確認する
- Red:
  - failing test:
    - 必要に応じて issue-71 名前空間の degraded/fail-fast evidence smoke
  - expected failure:
    - issue-71 bundle test 未実装
- Green:
  - minimum implementation:
    - 既存 fail-fast / degraded tests を closure set として実行し、不足があれば最小 assertion を追加
  - pass condition:
    - fail-fast / degraded targeted tests が通る
- Refactor:
  - 目的:
    - output assertion を既存 helper に合わせる
  - guardrail:
    - `sync --force` の degraded contract を変えない

#### step gate
- review:
  - code_reviewer に runtime command evidence と scope-out boundary をレビューさせる
- expected tests:
  - targeted runtime validate/sync/sync-github/fail-fast/degraded tests
- report update:
  - `runtime-command-verification`
- commit:
  - S02 stage commit

### S03 — installed package final smoke を closure matrix に接続する
- target:
  - `tests/test_init_update.py`
  - `report.md`
- design refs:
  - `installed package surface`
  - `closure matrix`
- step boundary:
  - non-editable isolated installed package smoke と no fallback confirmation に閉じる

#### B1 — installed-package verification
- purpose:
  - issue-69 / issue-70 の isolated installed package helper を issue-71 closure evidence として再消費する
- files:
  - `tests/test_init_update.py`

##### I1 — issue-71 installed final smoke
- slice goal:
  - checkout fallback なしの installed package `init/update` と issue-70 cutover reflection を issue-71 名前空間で証明する
- Red:
  - failing test:
    - issue-71 installed package final smoke test
  - expected failure:
    - test 未実装
- Green:
  - minimum implementation:
    - issue-69 / issue-70 helpers を再利用し、non-editable env、no `PYTHONPATH`、no cwd fallback、install-root reflection を確認する
  - pass condition:
    - installed package final smoke が通る
- Refactor:
  - 目的:
    - 重い build/install helper の重複を増やさない
  - guardrail:
    - package inclusion contract 自体は変更しない

#### step gate
- review:
  - code_reviewer に installed package final smoke の十分性をレビューさせる
- expected tests:
  - issue-71 installed package targeted smoke
- report update:
  - `installed-package-verification`
- commit:
  - S03 stage commit

### S90 — evidence report を完成させる
- 対象:
  - `report.md`
- 対応:
  - `checkout-verification`
  - `runtime-command-verification`
  - `installed-package-verification`
  - `dogfooding-parity`
  - `upstream-handoff-consumed`
  - full-suite residual risk
- commit:
  - S01/S02/S03 の各 stage commit に含めるか、追加 evidence-only commit とする

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00071` branch の issue-71 差分全体
- required validation:
  - issue-71 targeted tests
  - checked-in dogfooding parity tests
  - runtime validate/sync/sync-github/fail-fast/degraded targeted tests
  - installed package final smoke
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock sync --github`
  - `python -m unittest discover -v` informational sweep
- reviewer approvals:
  - final code review `pass`
  - final spec review `pass`
- report update:
  - final diff review verdict
  - validation evidence
  - full-suite residual risk / scope-out judgment
  - close-ready judgment
  - final commit または no-op rationale
- commit expectation:
  - 追加修正があれば final commit を作成する。なければ直前 stage commit を最終成果として扱い、no-op rationale を report に残す。

## 未確定事項
- なし:
  - verification surfaces、closure owner、scope-out structural failure、report evidence 集約方針は requirement/design で固定済み。

## final exit contract
- AC/EC 達成:
  - `AC-001` から `AC-005`、`EC-001` から `EC-002` が targeted validation と review で閉じている
- docs impact resolved:
  - `report.md` の 5 required evidence sections が実測値で埋まっている
- final diff approved:
  - final code review / final spec review がともに `pass`
  - `validate` / `sync` / `sync --github` が成功
  - full-suite informational sweep の結果と residual risk 判定が `report.md` に残っている
