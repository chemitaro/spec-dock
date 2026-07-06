---
種別: 実装計画書（Issue）
ID: "iss-00284"
タイトル: "仕様作成パックの事前確認とプロンプトパックを作る"
関連GitHub: ["#284"]
状態: "review-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00284 仕様作成パックの事前確認とプロンプトパックを作る — 実装計画

## 位置づけ

この `plan.md` は、この Issue の canonical implementation plan です。ChatGPT ZIP 仕様作成パック由来の draft artifact は evidence-only handoff として保持し、main orchestrator が採否判断した内容だけをこの文書に再記述しています。execution-ready と扱うには、この計画への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## Assurance / reviewer obligation

この Issue の local `authorized_profile` は `.assurance.json` / `assurance classify` を権威とし、ChatGPT 推奨や Epic 側の推奨グレードでは上書きしません。ただし、この Issue は branch / ref / source / stale_if を固定する制御プレーン入口であるため、strict 相当の追加 obligation を持ちます。execution-ready と扱うには、manual fallback evidence、failure-mode record、fresh `spec-reviewer` result を `report.md` に残します。

## 実装ステップ

1. S01: 親 Epic trace、Issue scope、local assurance、allowed / forbidden paths、no-per-Issue-PR relay policy を確認する。
2. S02: `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py` に preflight model、status taxonomy、diagnostics、exit code policy を実装する。
3. S03: source hashing、repo / ref observation、`.assurance.json` read-only snapshot、`stale_if` comparison を実装する。
4. S04: preflight status が `pass` の場合だけ prompt-pack files を生成する renderer、denylist、safe output constraints を実装する。
5. S05: valid / invalid fixtures、deterministic examples、`tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` を追加する。
6. S90: Issue `report.md` に EAL / SID / Closure Evidence Ledger / Relay Policy を更新する。
7. S99: targeted pytest、`spec-dock validate`、`git diff --check`、fresh reviewer readiness を閉じる。

S03 が `source-manifest.json` と `assurance_snapshot` を出力しない限り、S04 の prompt-pack renderer は `pass` にできない。S04 が prompt-pack を生成しない限り、S05 の end-to-end test は Green にできない。S90 / S99 は observed evidence を `report.md` に残す gate であり、新 behavior を追加しない。

## 検証計画

- Valid fixture から `preflight.json`、`source-manifest.json`、`stale-if.json`、`validation-taxonomy.json`、`safe-output-constraints.md`、`chatgpt-use-prompt.md` が作られることを確認する。
- Negative fixture で missing source は `fail`、missing assurance は `blocked`、unsafe claim は `rejected`、stale source hash は `stale` になることを確認する。
- `.assurance.json` が preflight script によって変更されていないことを確認する。
- `chatgpt-use-prompt.md` に authority boundary、forbidden claims、expected ZIP root、no-per-Issue-PR relay policy が含まれることを確認する。
- `git status` または差分確認で正本直接上書き、runtime provider 変更、Pull Request 作成がないことを確認する。


## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| closure id | step | purpose | maps to | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | 親 Epic trace と依存 Issue output を確認する | 親 E-RQ / E-AC、依存関係 | 親 docs / 依存 Issue report の確認メモ | 対応する親 trace と依存 output を説明できる | Issue `report.md` の Closure Evidence Ledger |
| tc-002 | S02/S03/S05 | Valid preflight output を生成する | Issue AC-002 | generated `preflight.json` / `source-manifest.json` | repo / ref / source manifest / stale_if / assurance snapshot が出力される | Issue `report.md` の実行証跡 / EAL |
| tc-003 | S02/S03/S05 | Missing source / missing assurance / stale hash を fail-closed にする | Issue AC-003〜AC-005 / AC-008 | pytest output、diagnostics JSON、`.assurance.json` 差分確認 | `fail` / `blocked` / `stale` を区別できる | Issue `report.md` の Closure Evidence Ledger |
| tc-004 | S04/S05 | Prompt-pack が authority boundary を含む | Issue AC-006 | generated `chatgpt-use-prompt.md` | evidence-only、forbidden claims、expected ZIP root、no-per-Issue-PR relay が明示される | Issue `report.md` の Closure Evidence Ledger |
| tc-005 | S04/S05 | Unsafe path / unsafe claim を rejected にする | Issue AC-007 | pytest output、diagnostics JSON | unsafe claim が `rejected` になり、prompt-pack が adoption-ready にならない | Issue `report.md` の Closure Evidence Ledger |
| tc-006 | S03/S05 | Stale source hash を stale にする | Issue AC-008 | pytest output、diagnostics JSON | source hash mismatch が `stale` になり、再生成 / reconciliation が要求される | Issue `report.md` の Closure Evidence Ledger |
| tc-007 | S02/S04/S05/S90 | Status taxonomy を report へ転記可能にする | Issue AC-009 | `validation-taxonomy.json`、report mapping | `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` と `unreviewed` が分離される | Issue `report.md` の Closure Evidence Ledger |
| tc-008 | S90/S99 | 正本上書き / `.assurance.json` mutation / PR 作成がない | Issue AC-010 | `git status --short`、`git diff --check`、no-mutation evidence | allowed paths 以外の変更がない | Issue `report.md` の Final Gate |
| tc-009 | S99 | required commands を実行可能にする | Issue AC-011 | targeted pytest、`spec-dock validate`、`git diff --check` | P0/P1 blocker がない、または blocker と next action が明確 | Issue `report.md` の Final Gate |
| tc-010 | S99 | fresh reviewer gate を閉じる | all AC / EC | fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result | P0/P1 blocker がなく、残リスクと次アクションが明確 | Issue `report.md` の Reviewer Gate Status |

## ステップ別実行契約

- S01:
  - 担当: main orchestrator または委任 worker。
  - close 条件: 親 Epic trace、依存 Issue、local `authorized_profile` を確認し、ChatGPT 推奨で `.assurance.json` を変更していないことを記録する。
  - closure id: `tc-001`。
- S02:
  - 担当: 実装 worker。
  - close 条件: preflight model、status taxonomy、diagnostics、exit code policy を実装し、required field missing が `fail` になる。
  - closure id: `tc-002` / `tc-003`。
- S03:
  - 担当: 実装 worker。
  - close 条件: source hashing、repo / ref observation、assurance read-only snapshot、stale_if comparison を実装し、missing source / missing assurance / stale hash が fail-closed になる。
  - closure id: `tc-002` / `tc-003`。
- S04:
  - 担当: 実装 worker / doc-writer。
  - close 条件: prompt-pack renderer、denylist、safe output constraints を実装し、unsafe claim が `rejected` になり、prompt に authority boundary と no-per-Issue-PR relay policy が入る。
  - closure id: `tc-004` / `tc-005`。
- S05:
  - 担当: QA / 実装 worker。
  - close 条件: valid / invalid fixtures、deterministic examples、targeted pytest を追加し、normal / negative flow が Green になる。
  - closure id: `tc-002` / `tc-003`。
- S90:
  - 担当: main orchestrator。
  - close 条件: docs impact、EAL、Spec Authoring Gate、Closure Delta を更新または no-op として記録する。
  - closure id: `tc-007` / `tc-008`。
- S99:
  - 担当: main orchestrator と fresh reviewers。
  - close 条件: `spec-dock validate`、必要な関連テスト、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result を揃え、P0/P1 blocker を残さない。
  - closure id: `tc-009` / `tc-010`。

## Step-local Executable Contracts

| step | behavior goal | planned contract | red-or-alternative evidence | green verification | refactor guardrail | step closure contract | report evidence destination | amendment trigger |
|---|---|---|---|---|---|---|---|---|
| S01 | 親 Epic trace、Issue scope、local assurance、no-per-Issue-PR relay を確認する | inspect-only。必要な場合だけ Issue `report.md` に evidence を追記する | `inspect-only` | 親 trace、非スコープ、allowed paths、`.assurance.json` read-only、relay policy を説明できる | 実装変更を行わない | Scope / non-scope / local assurance / relay の確認が report に残り blocker がない | Closure Evidence Ledger / SID | ZIP intake、runtime command、profile mutation、PR 作成が必要に見えた場合 |
| S02 | preflight 入力、status taxonomy、diagnostics、exit code policy を実装する | stdlib-only script と focused pytest。required field missing を `fail` にする | `red-required`: required field missing が fail になるテストを先に置く | required field missing が exit code `1` / status `fail` で、taxonomy が JSON で出る | runtime package へ昇格しない。external dependency を追加しない | taxonomy / diagnostics の基本構造があり、targeted pytest が pass | Closure Evidence Ledger / EAL | public runtime command、external dependency、ZIP validation が必要になった場合 |
| S03 | source hash、repo/ref observation、assurance snapshot、stale_if を固定する | source path normalization、hash、assurance read-only snapshot、stale comparison を実装する | `red-required`: missing source と stale hash が fail-closed になるテストを置く | valid preflight が `preflight.json` / `source-manifest.json` を生成し、missing source / missing assurance / stale hash が expected status になる | `.assurance.json` を書かない。local Git metadata を推測で補完しない | Valid output と fail-closed negative が report に記録可能 | Closure Evidence Ledger | repo boundary を保証できない、profile mutation が必要、GitHub API/network 依存が必要になった場合 |
| S04 | prompt-pack renderer、denylist、safe constraints を実装する | status `pass` の場合だけ prompt-pack files を生成し、authority boundary と forbidden claims を含める | `red-required`: unsafe authority claim が `rejected` になるテストを置く | generated prompt が evidence-only、expected ZIP root、no-per-Issue-PR relay を含む | prompt template を shipped docs / runtime docs へ昇格しない | Prompt-pack sample と unsafe claim rejected evidence が report に記録可能 | Closure Evidence Ledger | prompt-pack output root / required files / ZIP validation contract が変わる場合 |
| S05 | fixtures、examples、targeted pytest を追加する | valid / missing-source / missing-assurance / unsafe-claim / stale-hash fixture を追加する | `red-required`: missing-source と unsafe-claim が fail する状態を確認する | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` が normal / negative を coverage する | fixtures に secrets、host-local absolute path、raw transcript を入れない | Fixture list、test output、generated example path が report に記録可能 | Closure Evidence Ledger | fixture が external network / live GitHub API / host-specific path を必要とする場合 |
| S90 | docs impact、EAL、report consistency、relay policy を解消する | Issue `report.md` を更新し、Epic report は直接矛盾がある場合だけ更新する | `inspect-only` | EAL、Spec Authoring Gate、Closure Evidence Ledger、Reviewer Gate Status、Relay Policy が矛盾しない | historical ledger を削除しない。broad docs cleanup をしない | Report update と no-op rationale が残り direct contradiction がない | EAL / SID / Closure Evidence Ledger / Deferred PR Delivery Gate | workflow docs や Epic docs の正本判断が必要になった場合 |
| S99 | final quality gate を閉じる | targeted pytest、`spec-dock validate`、`git diff --check`、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` を確認する | `manual-required`: reviewer gate evidence が必要 | P0/P1 blocker がなく、各 reviewer gate の pass / blocker / next action が明確 | S99 で新 behavior を追加しない。必要なら bounded fix 後に S02〜S05 evidence を更新する | Commands と fresh review が report に記録され、issue finish 可能か判断できる | Final Gate / Reviewer Gate Status | reviewer が requirement / design / plan / code / QA 不足を指摘した場合 |


## 委任契約（Delegation Contract）

| step | delegated role | input docs | allowed paths | forbidden changes | acceptance criteria | required tests or docs-only verification | reviewer focus | stop conditions | output required | report destination | amendment trigger | step gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | main orchestrator / implementation-planner | Epic docs, this Issue `requirement.md` / `design.md` / `plan.md`, `.assurance.json` | inspect-only; this Issue `report.md` for evidence | `.assurance.json` mutation, source/runtime edits, PR creation | parent trace and dependency outputs are understood | docs-only inspection; no command required beyond optional `spec-dock validate` | scope, dependency, local assurance consistency | missing dependency evidence, stale profile, unclear parent trace | S01 evidence row and blocker/no-blocker note | Issue `report.md` Closure Evidence Ledger | parent trace or allowed paths differ from plan | S01 closed before S02 |
| S02 | dev-coder | this Issue `requirement.md`, `design.md`, S01 evidence | `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`, `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | `src/spec_dock/**`, unrelated Issue docs, `.assurance.json`, direct canonical overwrite by generated ZIP, PR/CI operations, tracked files under `manual-tests/**` | preflight model / taxonomy / diagnostics が動作する | focused pytest; `git diff --check` | fail-closed default, no runtime command expansion | outside allowed paths, public command追加, unsafe ZIP/adoption claim | changed files, test output, diagnostics shape | Issue `report.md` execution evidence / EAL | status taxonomy or exit code contract changes | S02 closed before S03/S04 |
| S03 | dev-coder | S02 output, Issue `.assurance.json` | `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`, `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`, `tests/fixtures/authoring_pack/**` | `.assurance.json` mutation, `src/spec_dock/**`, network/GitHub API dependency, unrelated docs, tracked files under `manual-tests/**` | source manifest / assurance snapshot / stale_if が動作する | focused pytest, `.assurance.json` no-mutation check, `git diff --check` | source hash correctness, path normalization, assurance read-only | repo boundary不明、profile mutation必要、Git ref補完が必要 | generated preflight sample, source manifest, no-mutation evidence | Issue `report.md` Closure Evidence Ledger | source manifest data modelがpublic runtime contract化する場合 | S03 closed before S04 |
| S04 | dev-coder or doc-writer | S03 output, Epic relay policy | `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`, `scripts/authoring-pack/README.md`, `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | runtime command additions, canonical docs auto-overwrite, `.assurance.json`, PR creation, tracked files under `manual-tests/**` | prompt-pack が authority boundary / forbidden claims / expected ZIP root / no-per-Issue-PR relay を含む | focused pytest content assertions | forbidden claims, profile authority, no-per-Issue-PR relay | prompt asks ChatGPT to decide profile or claim reviewer pass | generated prompt-pack sample, rejected unsafe claim evidence | Issue `report.md` Closure Evidence Ledger | prompt-pack output root or required files change | S04 closed before S05 |
| S05 | dev-coder / qa-reviewer | S02〜S04 output | `tests/fixtures/authoring_pack/**`, `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | unrelated tests, hidden secrets, host-local absolute paths, `.assurance.json`, PR creation, tracked files under `manual-tests/**` | normal / negative fixtures are covered | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`, `git diff --check` | deterministic fixtures, no secrets, status taxonomy coverage | fixtures require network/GitHub API/host-specific paths | fixture list, test output, generated example path | Issue `report.md` Closure Evidence Ledger | tests reveal missing AC or new failure mode | S05 closed before S90 |
| S90 | main orchestrator / doc-writer | S01〜S03 evidence, Epic docs, workflow docs if touched | this Issue docs/report, Epic report; `spec-dock/docs/**` only for direct contradiction | broad docs cleanup, template changes unrelated to this Issue, historical ledger deletion | docs impact and adoption ledger are resolved | docs-only inspection; `rg` for direct contradictions; `spec-dock validate` | report consistency, EAL/SID/closure integrity | unresolved contradiction or required docs update | docs impact decision, EAL/SID updates or no-op rationale | Issue `report.md`, Epic `report.md` when needed | docs impact changes canonical workflow | S90 closed before S99 |
| S99 | main orchestrator + fresh reviewers | all closure evidence, final diff, reviewer results | this Issue `report.md`, Epic report for summary; bounded fixes only in previously allowed paths | new behavior implementation, PR creation, unrelated cleanup | all required closure ids pass or approved no-op | `spec-dock validate`, `git diff --check`, focused tests from S02/S03, fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result | final readiness, P0/P1 blocker absence, residual risk clarity | any P0/P1 finding, stale reviewer, missing closure evidence | final gate result, reviewer status, remaining risks | Issue `report.md` Final Gate / Closure Evidence Ledger / Reviewer Gate Status | reviewer requires plan/design/code/QA change | Issue completion-ready only after S99 |

## 具体テストケース一覧

- `tc-s01-00284-001` inspect: 親 Epic trace と profile authority を確認する
  - 前提: この Issue の `requirement.md`、`design.md`、`.assurance.json`、Epic report の採用台帳が読める。
  - 操作: E-RQ-001〜E-RQ-003 / E-AC-001 への trace、`authorized_profile`、ChatGPT output の evidence-only 境界を確認する。
  - 期待結果: parent trace、profile authority、ZIP 生成が正本昇格ではないことが Issue `report.md` に記録される。
  - 失敗検出: ChatGPT 推奨で `.assurance.json` や `authorized_profile` を決める回帰、または親 Epic への trace 欠落を検出する。
  - 検証方法: docs-only inspection と Issue `report.md` Closure Evidence Ledger。
  - 関連 closure id: `tc-001`

- `tc-s02-00284-001` acceptance: 事前確認 JSON スキーマ案を生成する
  - 前提: repo、ref、source_paths、source hashes、stale_if、denylist、profile snapshot の入力候補がある。
  - 操作: 事前確認 JSON スキーマ案とソース一覧 fixture を作成し、必須 field の有無を検査する。
  - 期待結果: 必須 field がすべて含まれ、欠落時は prompt pack 生成へ進めない条件が明示される。
  - 失敗検出: source provenance が曖昧なまま ChatGPT ZIP 生成へ進む回帰を検出する。
  - 検証方法: staged artifact inspection、validation report、または Issue `report.md` execution evidence。
  - 関連 closure id: `tc-002`

- `tc-s02-00284-002` acceptance: プロンプトパックが権威境界を含む
  - 前提: 事前確認 JSON スキーマ案と source manifest が作成済みである。
  - 操作: プロンプトパック案に `authority: evidence_only`、禁止 claim、出力 root、stale_if、source manifest を含める。
  - 期待結果: ChatGPT に渡す入力だけで、正本直接上書き禁止、reviewer gate 非代替、`.assurance.json` 非変更が読み取れる。
  - 失敗検出: reviewer pass claim、canonical overwrite claim、profile 決定 claim がプロンプトに混入する回帰を検出する。
  - 検証方法: prompt pack artifact inspection と `rg` による禁止 claim 確認。
  - 関連 closure id: `tc-004`

- `tc-s03-00284-001` negative: `stale_if` と source hash 不一致を prompt pack 生成前に止める
  - 前提: stale_if 期限切れ fixture または source hash mismatch fixture がある。
  - 操作: 事前確認 JSON を検査し、期限切れまたは hash 不一致の扱いを確認する。
  - 期待結果: validation status は stale / blocked になり、ChatGPT ZIP 生成や downstream adoption へ進めない。
  - 失敗検出: 古い source_paths から prompt pack が生成される回帰を検出する。
  - 検証方法: stale_if fixture inspection、validation report、Issue `report.md` Closure Evidence Ledger。
  - 関連 closure id: `tc-006`

- `tc-s03-00284-002` negative: assurance missing は blocked になる
  - 前提: `missing-assurance-snapshot.json` が存在しない `.assurance.json` path を指す。
  - 操作: preflight script を invalid fixture で実行する。
  - 期待結果: exit code は `2`、status は `blocked`、`authorized_profile` を ChatGPT 推定にしない。
  - 失敗検出: missing assurance を `standard` などへ自動補完する profile authority regression を検出する。
  - 検証方法: pytest の blocked fixture case。
  - 関連 closure id: `tc-003`

- `tc-s04-00284-001` acceptance: prompt-pack contains authority boundary
  - 前提: valid preflight output がある。
  - 操作: preflight script を valid fixture で実行し、`chatgpt-use-prompt.md` を読む。
  - 期待結果: prompt に `authority: evidence_only`、`bundle_generation_not_promotion: true`、`authorized_profile` observation-only、expected ZIP root `specdock-authoring-pack/`、no-per-Issue-PR relay policy が含まれる。
  - 失敗検出: ChatGPT output を正本、reviewer pass、implementation complete、PR created と誤認させる prompt regression を検出する。
  - 検証方法: pytest の generated prompt content assertion。
  - 関連 closure id: `tc-004`

- `tc-s04-00284-002` negative: unsafe claim は rejected になる
  - 前提: `unsafe-output-claim.json` が forbidden claim を含む。
  - 操作: preflight script を invalid fixture で実行する。
  - 期待結果: exit code は `4`、status は `rejected`、prompt-pack は adoption-ready と扱われない。
  - 失敗検出: `spec-reviewer passed`、`adoption_status: adopted`、`.assurance.json updated` などを通す回帰を検出する。
  - 検証方法: pytest の unsafe claim fixture case。
  - 関連 closure id: `tc-005`

- `tc-s05-00284-001` regression: examples contain no host-local absolute paths
  - 前提: generated examples が存在する。
  - 操作: examples 内の `/Users/`、`/home/`、`.env`、`token`、`private key`、raw transcript らしい文字列を検査する。
  - 期待結果: prompt-pack examples に secret / host-local path / raw transcript が含まれない。
  - 失敗検出: repo 外情報を ChatGPT prompt に漏らす回帰を検出する。
  - 検証方法: pytest の content scan。
  - 関連 closure id: `tc-008`

- `tc-s90-00284-001` inspect: docs / report / EAL の直接矛盾を解消する
  - 前提: S01〜S03 の evidence と、この Issue / Epic の report が更新候補を持つ。
  - 操作: EAL、Closure Evidence Ledger、SID に prompt pack の採否と no-op rationale が残っているか確認する。
  - 期待結果: update または approved no-op rationale が記録され、ChatGPT output を正本扱いする記述が残らない。
  - 失敗検出: evidence-only artifact が downstream authority として扱われる記述を検出する。
  - 検証方法: docs-only inspection と `rg` による authority claim 確認。
  - 関連 closure id: `tc-007` / `tc-008`

- `tc-s99-00284-001` final-gate: 構造検証と fresh reviewer を通す
  - 前提: S01〜S03 と S90 が closed または approved no-op である。
  - 操作: `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`、`./spec-dock/scripts/spec-dock validate`、`git diff --check`、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result を確認する。
  - 期待結果: P0/P1 blocker がなく、残リスクまたは次アクションが Issue `report.md` Final Gate に記録される。
  - 失敗検出: stale reviewer result や未検証の acceptance を完了扱いする回帰を検出する。
  - 検証方法: command output と reviewer result の report 記録。
  - 関連 closure id: `tc-009` / `tc-010`

### S90 ドキュメント影響解消

- この Issue の実装が workflow docs、template、README、Epic docs、Issue docs に影響する場合だけ更新する。
- 更新しない場合も、直接矛盾がないことを `report.md` に no-op rationale として残す。
- ChatGPT output、ZIP、staged artifact、reviewer-focus は正本昇格や reviewer pass の代替として記述しない。

### S99 最終品質ゲート

- 前提: S01〜S03 と S90 が closed または approved no-op である。
- 必須確認: `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`、`./spec-dock/scripts/spec-dock validate`、`git diff --check`、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result。
- reviewer 指摘が出た場合は、bounded fix を行い、Closure Delta と再検証結果を report に残す。

## 検証コマンド

```bash
python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py \
  --config tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00284-prompt-pack

uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py
./spec-dock/scripts/spec-dock validate
git diff --check
```

## Final Exit Contract

- Spec-Locked Closure Index の required closure id が `pass` または valid approved-no-op として `report.md` に記録されている。
- `.assurance.json` / `authorized_profile` は ChatGPT 推奨では変更されていない。
- ChatGPT output / ZIP / staged artifact は evidence-only であり、正本直接上書きや self-review pass claim がない。
- S90 docs impact が解消されている。
- S99 final `spec-reviewer` / `code-reviewer` / `qa-reviewer` が fresh pass である、または blocker と次アクションが明確である。

## リスク

- branch / ref / source provenance が曖昧なまま ZIP 生成へ進むリスクを遮断する。
- ChatGPT 出力を正本完了や reviewer pass と誤認するリスク。
- ドッグフード専用の提案が配布ランタイム契約のように読まれるリスク。

## 完了条件

- `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py` が valid fixture から prompt-pack を生成できる。
- `preflight.json` が repo / ref / source hashes / stale_if / assurance snapshot を含む。
- prompt-pack が authority boundary、safe output constraints、forbidden claims、no-per-Issue-PR relay policy を含む。
- missing source / missing assurance / stale hash / unsafe claim が fail-closed になる。
- 親 trace E-RQ-001, E-RQ-002, E-RQ-003 / E-AC-001 を説明できる。
- validation report が `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` を区別する。
- 正本上書き、runtime provider 変更、`.assurance.json` mutation、Pull Request 作成がない。
- `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`、`./spec-dock/scripts/spec-dock validate`、`git diff --check` の結果が report に残る。
- fresh reviewer gate result と closure evidence が report に残る。

## レビュアー引き渡しメモ

- この Issue は `strict` 推奨だが、最終グレードは local assurance が決める。
- ChatGPT 出力は採用候補であり、正本ではない。
- 実装前に、Issue-local draft artifacts は採用済み証跡として確認し、追加変更が必要な場合は Closure Delta と fresh reviewer evidence を残す。
