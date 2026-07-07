---
種別: 実装計画書（Issue）
ID: "iss-00285"
タイトル: "安全な仕様作成パック検査とスキーマ検証を実装する"
関連GitHub: ["#285"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00285 安全な仕様作成パック検査とスキーマ検証を実装する — 実装計画

## 位置づけ

この `plan.md` は、この Issue の canonical implementation plan です。ChatGPT Use の計画具体化は evidence-only draft として扱い、main orchestrator が採用した範囲だけを正本へ反映します。execution-ready と扱うには、この計画への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## この計画で満たす要件ID

- AC-001: 親 Epic trace と `iss-00284` preflight dependency。
- AC-002: actual ZIP central directory の展開前安全検査。
- AC-003: expected root と mandatory metadata。
- AC-004: unsafe path / unsafe file type の fail-closed rejection。
- AC-005: preflight / source hash / stale_if の検査。
- AC-006: unsafe authority claim の検出。
- AC-007: safe diagnostics / redaction。
- AC-008: canonical docs / `.assurance.json` no-mutation。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。ただし、この Issue は ZIP 安全検査、スキーマ検証、unsafe authority claim の拒否を担うため、strict 相当の追加 obligation を持ちます。

execution-ready と扱うには、ChatGPT Use planning evidence、manual fallback evidence、failure-mode record、fresh `spec-reviewer` result を `report.md` に残します。実装後は `code-reviewer`、`qa-reviewer`、final `spec-reviewer` の gate を通します。

## 変更対象

作成:

- `scripts/authoring-pack/authoring_pack_review.py`
- `scripts/authoring-pack/review_chatgpt_authoring_pack.py`
- `tests/manual_tests/test_review_chatgpt_authoring_pack.py`

変更:

- `scripts/authoring-pack/README.md`
- この Issue の `report.md`

変更しない:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- unrelated Issue docs
- PR / CI workflow files

例外:

- `.assurance.json` は planning 中の `assurance classify` による command-generated source binding metadata としてのみ更新し、Planning Verification Log に記録する。
- validator library / CLI / tests / README の実装 step は `.assurance.json` を変更しない。

## 実装順序

1. S01: dependency / preflight contract inspection。
2. S02: validator library / CLI の最小 Green。
3. S03: negative fixture と status taxonomy の拡張。
4. S90: README / report impact resolution。
5. S99: final QA / code / spec gate。

## 要件 ↔ ステップ対応

| AC | primary step | secondary step | planned evidence |
|---|---|---|---|
| AC-001 | S01 | S99 | `report.md` Closure Evidence Ledger、validation report trace |
| AC-002 | S02 | S03 | unsafe ZIP tests、extract-dir absence evidence |
| AC-003 | S02 | S03 | missing metadata tests、valid report sample |
| AC-004 | S02 | S03 | path / file type negative tests |
| AC-005 | S02 | S03 | preflight status / source hash / stale_if tests |
| AC-006 | S02 | S03 | unsafe authority claim tests |
| AC-007 | S03 | S99 | redaction tests、leak check |
| AC-008 | S03 | S99 | bytes equality / `git status --short` evidence |

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | purpose | maps to | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | `iss-00284` preflight と親 Epic trace を確認する | AC-001 | current branch inspection note、preflight contract note、assurance verify | source hash / stale / forbidden claim input が trace できる | Issue `report.md` Closure Evidence Ledger |
| tc-002 | S02 | ZIP central directory / safe extraction / schema validator を実装する | AC-002〜AC-004 | changed files、valid validation report sample、unsafe ZIP report sample | dangerous ZIP が展開前に reject される | Issue `report.md` EAL / execution evidence |
| tc-003 | S03 | negative fixture と status taxonomy を検証する | AC-005〜AC-007 | pytest output、fixture list、redaction check | fail / blocked / stale / rejected / deferred を区別できる | Issue `report.md` Closure Evidence Ledger |
| tc-004 | S90 | docs impact と adoption ledger を解消する | report integrity | README diff、EAL / SID rows、no-op rationale | runtime command 誤認や canonical overwrite 誤認がない | Issue `report.md` Docs Impact / EAL |
| tc-005 | S99 | final QA / reviewer gate を閉じる | all AC | validate、assurance verify、diff check、focused tests、fresh reviewer record | P0/P1 blocker がない、または blocker / next action が明確 | Issue `report.md` Final Gate |

## 実装ステップ

### S01: dependency / preflight contract inspection

- depends on: reviewed planning docs。
- unblocks: S02。
- target files: this Issue `report.md` only。

Planned contract:

- behavior goal: `iss-00284` preflight output を validator の信頼ベースラインとして使える条件を確認する。
- scope: source inspection と report row 追加のみ。
- test obligation: inspect-only。source contract と assurance observation を確認する。
- red or alternative evidence requirement: inspect-only。
- green verification: `./spec-dock/scripts/spec-dock assurance verify` と docs inspection。
- refactor guardrail: source code、tests は変更しない。`.assurance.json` は planning metadata として既に `assurance classify` が更新済みであり、S01 の validator 実装では変更しない。
- amendment trigger: preflight actual output が design の `preflight / stale validation` と矛盾する場合。

Delegation contract:

- delegated role: main orchestrator direct execution。
- input docs: `requirement.md`、`design.md`、`plan.md`、`scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`、`tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json`。
- allowed paths: this Issue `report.md`。
- forbidden changes: source code、tests、unrelated Issue docs。validator 実装による `.assurance.json` mutation。
- acceptance criteria: `iss-00284` preflight fixture の `sources` / `stale_if` / `safe_output_constraints.forbidden_claims` を `iss-00285` validator input として trace できる。
- required tests or docs-only verification: docs inspection と `./spec-dock/scripts/spec-dock assurance verify`。
- reviewer focus: parent trace、preflight status propagation、no `.assurance.json` mutation。
- stop conditions: `iss-00284` preflight contract が読めない、source hash baseline が説明できない、assurance verify が失敗する。
- output required: report row、verification result、No material implementation decisions beyond the approved plan。

#### 具体テストケース一覧

- `tc-s01-00285-001` inspect: preflight input contract を trace できる
  - 前提: `tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json` が存在する。
  - 操作: `sources`、`stale_if`、`safe_output_constraints.forbidden_claims`、`assurance_path` を読む。
  - 期待結果: `iss-00285` の validator が preflight baseline、source hash、unsafe claim denylist を得られることを説明できる。
  - 失敗検出: preflight fixture に source hash または forbidden claim baseline がなく、validator が信頼ベースラインなしで pass 可能になる回帰を検出する。
  - 検証方法: docs-only inspection と Issue `report.md` Closure Evidence Ledger。
  - 関連 closure id: `tc-001`

- `tc-s01-00285-002` inspect: local assurance authority を確認する
  - 前提: active Issue が `iss-00285` である。
  - 操作: `./spec-dock/scripts/spec-dock assurance verify` を実行する。
  - 期待結果: issue `iss-00285`、`authorized_profile=standard`、`reason=ok` が確認できる。
  - 失敗検出: stale `.assurance.json` または wrong active issue により planning / execution authority を誤認する回帰を検出する。
  - 検証方法: command output を Issue `report.md` に記録する。
  - 関連 closure id: `tc-001`

Step gate:

- commit candidate: S02/S03/S90/S99 とまとめる。S01 単独 commit は不要。
- report evidence destination: `Closure Evidence Ledger`、`Execution Evidence`。

### S02: validator library / CLI の最小 Green

- depends on: S01。
- unblocks: S03。
- target files: `scripts/authoring-pack/authoring_pack_review.py`、`scripts/authoring-pack/review_chatgpt_authoring_pack.py`、`tests/manual_tests/test_review_chatgpt_authoring_pack.py`。

Planned contract:

- behavior goal: actual ZIP を展開前に検査し、valid ZIP / valid tree / minimal metadata / report writing を通す。
- scope: library、CLI wrapper、最小 focused tests。
- test obligation: public CLI と JSON report の observable behavior を first Green にする。
- red or alternative evidence requirement: red-required。valid ZIP report test を先に追加し、未実装で fail することを確認する。
- green verification: `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py`。
- refactor guardrail: `prepare_chatgpt_authoring_pack.py` の public behavior を変更しない。共通化は S02 の tests が通ってから最小限にする。
- amendment trigger: valid pack schema、mandatory metadata、exit code mapping が design と矛盾する場合。

Delegation contract:

- delegated role: dev-coder。
- input docs: `requirement.md`、`design.md`、`plan.md`、`scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`、`tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`。
- allowed paths: `scripts/authoring-pack/authoring_pack_review.py`、`scripts/authoring-pack/review_chatgpt_authoring_pack.py`、`tests/manual_tests/test_review_chatgpt_authoring_pack.py`。
- forbidden changes: `src/spec_dock/**`、unrelated Issue docs、PR / CI workflow files、canonical docs auto-overwrite、validator 実行または実装による `.assurance.json` mutation。
- acceptance criteria: valid ZIP / tree が report を作り、missing metadata と source hash mismatch が expected status / exit code になる。
- required tests or docs-only verification: focused pytest、sample `validation-report.json` inspection、`git diff --check`。
- reviewer focus: central directory before extraction、root / path / file-type validation、output dir ownership、report redaction。
- stop conditions: safe extraction が central directory 検査前に走る、valid ZIP が report を作れない、unowned output dir を削除しそうになる。
- output required: changed files、focused pytest result、sample report path、residual risk、No material implementation decisions beyond the approved plan。

#### 具体テストケース一覧

- `tc-s02-00285-001` acceptance: valid ZIP が pass report を作る
  - 前提: tmp path に `specdock-authoring-pack/` root、mandatory metadata、safe Markdown / JSON、preflight と一致する source-manifest を含む ZIP がある。
  - 操作: `review_chatgpt_authoring_pack.py --input <zip> --preflight <preflight> --output-dir <tmp>` を実行する。
  - 期待結果: exit code `0`、`validation-report.json.status=pass`、authority boundary、trace、source list、`validation-summary.md` が作られる。
  - 失敗検出: valid pack が report を作れない、または adoption-ready / canonical claim を出す回帰を検出する。
  - 検証方法: `tests/manual_tests/test_review_chatgpt_authoring_pack.py` の CLI test。
  - 関連 closure id: `tc-002`

- `tc-s02-00285-002` acceptance: tree input は schema を検査し ZIP safety note を残す
  - 前提: tmp path に隔離済み `specdock-authoring-pack/` directory tree がある。
  - 操作: `--input-kind tree` で validator を実行する。
  - 期待結果: schema / claim / source hash は検査され、ZIP central directory safety は `deferred` note として report に残る。tree mode は AC-002 の代替証跡にならない。
  - 失敗検出: tree input を ZIP safety pass と誤認する回帰を検出する。
  - 検証方法: focused pytest と `validation-report.json.deferred` inspection。
  - 関連 closure id: `tc-002`

- `tc-s02-00285-003` negative: manifest 欠落は fail になる
  - 前提: mandatory `manifest.json` を欠く ZIP がある。
  - 操作: validator を実行する。
  - 期待結果: exit code `1`、status `fail`、`errors` に missing manifest reason が出る。
  - 失敗検出: mandatory metadata 欠落 ZIP が pass または deferred になる回帰を検出する。
  - 検証方法: focused pytest。
  - 関連 closure id: `tc-002`

- `tc-s02-00285-004` negative: source hash mismatch は stale になる
  - 前提: preflight source sha と ZIP `source-manifest.json` sha が異なる ZIP がある。
  - 操作: validator を実行する。
  - 期待結果: exit code `3`、status `stale`、canonical docs への mutation はない。
  - 失敗検出: stale source を valid output として採用候補に流す回帰を検出する。
  - 検証方法: focused pytest と post-run bytes check。
  - 関連 closure id: `tc-003`

Step gate:

- commit candidate: S02+S03+S90+S99 を同一 Issue commit にまとめる。
- report evidence destination: `Execution Evidence`、`Closure Evidence Ledger` `tc-002`。

### S03: negative fixture / fail-closed expansion

- depends on: S02。
- unblocks: S90。
- target files: `scripts/authoring-pack/authoring_pack_review.py`、`tests/manual_tests/test_review_chatgpt_authoring_pack.py`、必要な小型 fixture under `tests/fixtures/authoring_pack/review/**`。

Planned contract:

- behavior goal: unsafe ZIP、unsafe tree、unsafe claim、preflight non-pass、redaction、no-mutation を fail-closed にする。
- scope: validator library と focused tests。
- test obligation: risk-calibrated negative coverage。unsafe path / file type / preflight / claim / diagnostic / mutation を含める。
- red or alternative evidence requirement: red-required for each bug class where feasible。ZIP metadata edge は pytest 内生成で characterization first にしてよい。
- green verification: focused pytest、`git diff --check`、`git status --short`。
- refactor guardrail: failure taxonomy を broad exception catch で潰さず、status と reason を report へ残す。
- amendment trigger: unsafe claim false positive / false negative、diagnostic leak、status taxonomy mismatch が出た場合。

Delegation contract:

- delegated role: dev-coder。
- input docs: `requirement.md` AC-004〜AC-008、`design.md` safety validation / preflight validation / unsafe claim detection、S02 output。
- allowed paths: `scripts/authoring-pack/authoring_pack_review.py`、`tests/manual_tests/test_review_chatgpt_authoring_pack.py`、small fixtures under `tests/fixtures/authoring_pack/review/**` if tracked fixtures are needed。
- forbidden changes: provider runtime、unrelated Issue docs、PR / CI files、broad test fixture rewrite outside authoring pack scope、validator 実行または実装による `.assurance.json` mutation。
- acceptance criteria: unsafe ZIP は extraction before validation を起こさず `rejected`、preflight non-pass は pass にならず、diagnostics は redacted、canonical docs / assurance は mutated しない。
- required tests or docs-only verification: focused pytest、redaction assertion、bytes equality assertion、post-run `git status --short` inspection。
- reviewer focus: fail-closed behavior、status taxonomy、redaction、no-mutation。
- stop conditions: dangerous ZIP が extraction dir に file を残す、host path / private key / token が stdout/report に出る、`.assurance.json` bytes が変わる。
- output required: changed files、negative fixture list、pytest output、remaining uncovered edge cases、No material implementation decisions beyond the approved plan。

#### 具体テストケース一覧

- `tc-s03-00285-001` negative: path traversal は展開前に rejected になる
  - 前提: `../evil.md` entry を含む ZIP がある。
  - 操作: validator を `--extract-dir <tmp>` 付きで実行する。
  - 期待結果: exit code `4`、status `rejected`、extract dir に file が作られない。
  - 失敗検出: central directory 検査前に展開する回帰を検出する。
  - 検証方法: focused pytest と extract dir inspection。
  - 関連 closure id: `tc-002`

- `tc-s03-00285-002` negative: absolute / Windows path は raw path を出さず rejected になる
  - 前提: `/Users/example/token.md` または `C:\Users\example\token.md` entry を含む ZIP がある。
  - 操作: validator を実行する。
  - 期待結果: exit code `4`、status `rejected`、stdout / stderr / report に host-local path が出ない。
  - 失敗検出: unsafe path を report に echo する redaction 回帰を検出する。
  - 検証方法: focused pytest の combined output leak assertion。
  - 関連 closure id: `tc-003`

- `tc-s03-00285-003` negative: symlink / nested archive / binary は rejected になる
  - 前提: symlink mode entry、nested `.zip` entry、binary-looking `.md` entry の各 ZIP がある。
  - 操作: validator をそれぞれ実行する。
  - 期待結果: 各 case が exit code `4` / status `rejected` になる。
  - 失敗検出: unsafe file type が staged candidate として残る回帰を検出する。
  - 検証方法: focused pytest。
  - 関連 closure id: `tc-002`

- `tc-s03-00285-004` negative: non-pass preflight は validator pass にならない
  - 前提: `preflight.status` が `fail`、`blocked`、`stale`、`rejected` の preflight JSON がある。
  - 操作: otherwise valid ZIP と組み合わせて validator を実行する。
  - 期待結果: validator は preflight status を安全側に伝播し、status `pass` を返さない。
  - 失敗検出: failed preflight を trusted baseline として受け入れる回帰を検出する。
  - 検証方法: focused pytest の parameterized test。
  - 関連 closure id: `tc-003`

- `tc-s03-00285-005` negative: stale_if current source hash mismatch は stale になる
  - 前提: preflight `stale_if.source_paths` が current repo file を指し、current sha256 が preflight snapshot と異なる。
  - 操作: validator を実行する。
  - 期待結果: exit code `3`、status `stale`、report に stale reason が出る。
  - 失敗検出: local source drift を無視して pass にする回帰を検出する。
  - 検証方法: temp repo fixture または monkeypatch 可能な source root fixture の focused pytest。
  - 関連 closure id: `tc-003`

- `tc-s03-00285-006` negative: unsafe authority claim は rejected になる
  - 前提: Markdown または JSON に `spec-reviewer-passed`、`adoption_status: adopted`、`.assurance.json updated`、`canonical overwrite` のいずれかを含む ZIP がある。
  - 操作: validator を実行する。
  - 期待結果: exit code `4`、status `rejected`、fresh reviewer gate と混同しない reason が report に出る。
  - 失敗検出: ChatGPT output が self-review pass や canonical adoption を claim したまま downstream に流れる回帰を検出する。
  - 検証方法: focused pytest。
  - 関連 closure id: `tc-003`

- `tc-s03-00285-007` negative: diagnostics は private key と token を漏らさない
  - 前提: private key header または token-like string を含む unsafe file がある。
  - 操作: validator を実行する。
  - 期待結果: output / report には redacted reason だけが残り、raw secret-like value は出ない。
  - 失敗検出: diagnostics leak の回帰を検出する。
  - 検証方法: focused pytest の stdout / stderr / JSON / Markdown leak assertion。
  - 関連 closure id: `tc-003`

- `tc-s03-00285-008` invariant: canonical docs と assurance は mutation されない
  - 前提: active Issue の canonical docs と `.assurance.json` bytes を記録する。
  - 操作: valid / invalid fixture を validator で実行する。
  - 期待結果: validator 実行後も recorded bytes が一致する。
  - 失敗検出: ChatGPT pack review helper が canonical docs や assurance を直接上書きする回帰を検出する。
  - 検証方法: focused pytest の bytes equality assertion。
  - 関連 closure id: `tc-003`

Step gate:

- commit candidate: S02 と同一 commit。
- report evidence destination: `Closure Evidence Ledger` `tc-003`、`AC 達成状況`。

### S90: docs impact / report refresh

- depends on: S03。
- unblocks: S99。
- target files: `scripts/authoring-pack/README.md`、this Issue `report.md`。

Planned contract:

- behavior goal: helper の用途を dogfood-only / evidence-only として説明し、runtime command 誤認を防ぐ。
- scope: README と report のみ。
- test obligation: docs-only inspection。
- red or alternative evidence requirement: inspect-only。
- green verification: `rg` inspection、`./spec-dock/scripts/spec-dock validate`。
- refactor guardrail: Epic docs は直接矛盾がない限り変更しない。
- amendment trigger: README が provider runtime command の存在を示唆する場合、または Epic docs と矛盾する場合。

Delegation contract:

- delegated role: doc-writer。
- input docs: `requirement.md`、`design.md`、`plan.md`、S02/S03 verification output、`scripts/authoring-pack/README.md`。
- allowed paths: `scripts/authoring-pack/README.md`、this Issue `report.md`。
- forbidden changes: source code、tests、provider runtime、unrelated docs、Epic docs unless direct contradiction is found and recorded first。
- acceptance criteria: README が preflight helper と review helper の責務差を説明し、runtime command / PR / reviewer pass / canonical overwrite を claim しない。
- required tests or docs-only verification: `rg` inspection と `spec-dock validate`。
- reviewer focus: docs/spec alignment、dogfood-only boundary、no canonical overwrite claim。
- stop conditions: docs が `spec-dock authoring-pack` runtime command の存在を claim する、PR 作成済みと読める記述が入る。
- output required: README diff summary、report EAL/SID updates、docs impact no-op rationale、No material implementation decisions beyond the approved plan。

#### 具体テストケース一覧

- `tc-s90-00285-001` inspect: README が runtime command を claim しない
  - 前提: README 更新後の `scripts/authoring-pack/README.md` がある。
  - 操作: `rg -n "spec-dock authoring-pack|Pull Request created|reviewer pass" scripts/authoring-pack/README.md` を実行する。
  - 期待結果: runtime command、PR 作成済み、reviewer pass claim と読める表現がない。
  - 失敗検出: dogfood-only helper を配布 runtime と誤認させる docs regression を検出する。
  - 検証方法: `rg` inspection と docs diff。
  - 関連 closure id: `tc-004`

- `tc-s90-00285-002` inspect: report ledger が implementation evidence と deferred PR policy を持つ
  - 前提: S02/S03 verification output がある。
  - 操作: Issue `report.md` の EAL / SID / Closure Evidence / Deferred PR Delivery Gate を読む。
  - 期待結果: implementation evidence、docs impact、no per-Issue PR rationale、next Issue relay が記録されている。
  - 失敗検出: Issue 単独 PR 作成や canonical adoption claim を report が示唆する回帰を検出する。
  - 検証方法: docs-only inspection と `spec-dock validate`。
  - 関連 closure id: `tc-004`

Step gate:

- commit candidate: S02/S03 と同一 commit。
- report evidence destination: `Docs Impact`、`EAL`、`SID`、`Closure Evidence Ledger` `tc-004`。

### S99: final QA / code / spec gate

- depends on: S90。
- unblocks: `issue finish` and next Issue `iss-00286` start。
- target files: no new source changes unless reviewers find bounded in-scope defects。

Planned contract:

- behavior goal: all closure ids を pass または approved-no-op とし、fresh reviewer gates を記録する。
- scope: verification、reviewer gates、bounded in-scope fixes。
- test obligation: final focused tests、existing preflight regression、SpecDock validation、reviewer pass。
- red or alternative evidence requirement: covered-existing for final regression; reviewer findings trigger bounded fix and re-review。
- green verification: verification command list and reviewer pass。
- refactor guardrail: final gate では新機能追加をしない。P0/P1 fix は bounded in-scope に限定する。
- amendment trigger: reviewer P0/P1、focused pytest failure、`assurance verify` failure、`git diff --check` failure。

Delegation contract:

- delegated role: main orchestrator for gates; dev-coder or doc-writer only for bounded reviewer-fail fixes。
- input docs: all canonical Issue docs、report evidence、final diff、README、focused tests。
- allowed paths: previously allowed implementation paths only。
- forbidden changes: new behavior outside plan、runtime command publication、PR creation、unrelated cleanup。
- acceptance criteria: all required commands pass, `code-reviewer` / `qa-reviewer` / final `spec-reviewer` return pass, deferred PR delivery evidence is recorded.
- required tests or docs-only verification: focused pytest, existing preflight pytest, `spec-dock validate`, `assurance verify`, `git diff --check`, `git status --short`。
- reviewer focus: requirement/design/plan/report/implementation/test/docs alignment。
- stop conditions: any P0/P1 finding、unresolved report ledger blocker、unexpected dirty files after commit、PR delivery requested before `iss-00293`。
- output required: command outputs、reviewer IDs、final report ledger、commit evidence、post-commit clean check、No material implementation decisions beyond the approved plan。

#### 具体テストケース一覧

- `tc-s99-00285-001` final-gate: focused tests and SpecDock validation pass
  - 前提: S01〜S90 の implementation evidence が report に記録済みである。
  - 操作: focused pytest、existing preflight pytest、`spec-dock validate`、`assurance verify`、`git diff --check` を実行する。
  - 期待結果: すべて pass し、失敗時は blocker と next action が report に記録される。
  - 失敗検出: validator 実装は動くが SpecDock workflow evidence や既存 preflight regression を壊す回帰を検出する。
  - 検証方法: command output と `report.md` Final Gate。
  - 関連 closure id: `tc-005`

- `tc-s99-00285-002` final-gate: fresh reviewers pass
  - 前提: verification commands が pass している。
  - 操作: `code-reviewer`、`qa-reviewer`、final `spec-reviewer` に review を依頼する。
  - 期待結果: P0/P1 blocker がなく、reviewer result が `report.md` の Reviewer Gate Status に記録される。
  - 失敗検出: worker output や ChatGPT output を reviewer pass の代替にする回帰を検出する。
  - 検証方法: reviewer result IDs と final report ledger。
  - 関連 closure id: `tc-005`

- `tc-s99-00285-003` final-gate: deferred PR delivery を守る
  - 前提: Issue implementation が完了している。
  - 操作: final report と `git status --short` を確認する。
  - 期待結果: この Issue では PR を作成せず、`issue finish` 後に `iss-00286` を開始する方針が残る。
  - 失敗検出: intermediate Issue で PR 作成済みと claim する workflow regression を検出する。
  - 検証方法: Issue `report.md` Deferred PR Delivery Gate と GitHub PR command 未実行の作業ログ。
  - 関連 closure id: `tc-005`

Step gate:

- commit candidate: final Issue commit after all gates pass。
- report evidence destination: `Reviewer Gate Status`、`Closure Evidence Ledger` `tc-005`、`Final Gate`。

## レビュー / QA ゲート方針

- planning 前: `spec-reviewer` が requirement / design / plan / report の実装可能性を確認する。
- implementation 後: `code-reviewer` が safe extraction、path normalization、ZIP metadata interpretation、output dir ownership、diagnostic sanitization を確認する。
- implementation 後: `qa-reviewer` が fixture coverage、redaction、status taxonomy、no-mutation を確認する。
- final: `spec-reviewer` が requirement / design / plan / report / implementation / tests / docs の整合を確認する。
- どの reviewer gate も ChatGPT output や worker output では代替しない。

## 検証コマンド

```bash
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
git status --short
```

## Final Exit Contract

- `review_chatgpt_authoring_pack.py` と `authoring_pack_review.py` が存在する。
- actual ZIP input の central directory 検査が展開前に実行される。
- expected root / mandatory metadata / preflight status / source hash / stale_if / unsafe claim が検査される。
- dangerous fixtures が `rejected`、missing metadata が `fail`、hash mismatch が `stale`、local observation missing が `blocked`、later-stage responsibility が `deferred` として区別される。
- `unreviewed` は execution status ではなく adoption state としてだけ report に残る。
- report は host path、secret、private key、raw transcript を漏らさない。
- canonical docs / `.assurance.json` が validator で変更されない。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` を変更していない。
- `report.md` に EAL / SID / closure evidence / reviewer results が残る。
- この Issue 単独の PR を作らず、finish 後に次 Issue へ進む。

## リスク

- 危険な ZIP を展開してしまうリスク。
- tree input を ZIP central directory safety evidence と誤認するリスク。
- non-pass preflight を信頼ベースラインとして扱うリスク。
- `deferred` や `unreviewed` を `pass` と誤認するリスク。
- ChatGPT output を正本完了や reviewer pass と誤認するリスク。
- dogfood-only helper が配布 runtime command のように読まれるリスク。
