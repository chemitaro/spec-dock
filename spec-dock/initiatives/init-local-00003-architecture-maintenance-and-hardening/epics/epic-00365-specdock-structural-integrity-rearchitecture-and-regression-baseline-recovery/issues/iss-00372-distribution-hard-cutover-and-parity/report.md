---
種別: レポート（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
最終更新: "2026-08-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

これは実装計画 Step 11 の candidate freeze 前レポートである。実装・テスト・CI・ドキュメントの D5 変更は中間 candidate `ef48b913ab6aeb364db363a0248f33b030705849`（親 `5d5916aeb7ee25b59139d6da162ecd61a0759732`）で確認できる。report 編集前の `git status --short` は空だったが、この report 編集自体が次の candidate を作るため、上記 SHA は最終 candidate `C` ではない。

M1〜M5 の変更は次のとおりである。

| マイルストーン | 実装内容 | 結果 |
|---|---|---|
| M1 | `src/spec_dock/cli.py` の dead distribution writer/private-kernel seam を除去し、CLI を typed managed-distribution service の adapter に限定。AST 境界 assertion を追加し、現役の `managed_distribution.py` kernel は保持。 | managed-distribution unit 575 passed、distribution cutover focused suite 158 passed。 |
| M2 | production code は変更せず、schema 2 current guard、schema 1 migration input、journal、legacy uninstall reader-only 境界を recovery selector で固定。 | recovery selector 220 passed。 |
| M3 | wheel/sdist の isolated installed runtime から deprovision (`--keep-specs`) と explicit purge (`--remove-specs`) の public dispatch・preservation 境界を検証する package test を追加。 | package heavy suite 16 passed（648.43s）。 |
| M4 | `.github/workflows/provider-ci.yml` に Linux/macOS の provider distribution parity matrix を追加。`github.event.pull_request.head.sha` を明示 checkout し、runner の `git rev-parse HEAD` と照合。 | workflow contract 1 passed、provider lane 24 passed、YAML parse pass。 |
| M5 | root README、dogfood/provider README・migration の recovery wording を schema/purpose 基準へ更新し、provider/dogfood projection parity を固定。 | wording 1 passed、mirror 1 passed、provider/dogfood comparison pass。 |

## Implementation

production authority は引き続き `src/spec_dock/managed_distribution.py` である。M1 は CLI 側の到達不能な旧 writer と direct private-kernel import/test seam の除去に限定し、M2 では production recovery logic を変更していない。package configuration、Full Regression ledger、`verify-full-regression.py`、Issue metadata はこの candidate では変更していない。

変更された tracked path は次の11件である。

- `.github/workflows/provider-ci.yml`
- `README.md`
- `spec-dock/docs/README.md`
- `spec-dock/docs/migration.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`
- `src/spec_dock/cli.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- `tests/integration/test_epic_00343_distribution.py`
- `tests/unit/infra/test_init_update.py`
- `tests/unit/infra/test_managed_distribution.py`

TDD の証跡は、既存挙動の characterization と red の structural boundary を先に置き、最小変更後に M1〜M5 の focused green を確認する流れで整理されている。CLI の private writer seam を再導入すると AST test が失敗し、`managed_distribution.py` の descriptor-bound kernel primitive は引き続き検証対象となる。

## Verification

### Step 9 — ordinary / focused gates

| コマンドまたは確認 | 結果 |
|---|---|
| `make lint` | pass |
| `uv run pytest` | 1526 passed、1134 skipped（ordinary fast lane）。skipped heavy node を Full Regression の代替とは扱わない。 |
| `uv run pytest tests/unit/infra/test_managed_distribution.py` | 575 passed |
| `uv run pytest tests/unit/infra/test_managed_distribution.py -k 'guard or journal or recovery or legacy'` | 220 passed |
| `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py` | 158 passed（1483.90s） |
| `uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py` | 16 passed（648.43s） |
| provider CI workflow contract / YAML parse / provider-dogfood comparison | contract 1 passed、provider lane 24 passed、YAML parse pass、comparison pass |
| `./spec-dock/scripts/spec-dock validate` | pass（nodes=227） |
| `git diff --check` | pass |

### Step 10 — current Full Regression verifier

次の verifier を candidate `ef48b913ab6aeb364db363a0248f33b030705849` で実行した。

```bash
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --shards 4
```

結果は exit 1、`status: ledger-mismatch` であり、Step 10 は未達である。結果ファイルは `spec-dock/.workbench/full-regression/20260829T194406.715724Z/result.json` にある。`candidate_sha` は上記中間 candidate と一致し、`missing_failures` は次の historical retained-skill node の1件だけだった。

```text
tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source
```

`unexpected_errors`、`unexpected_failures`、`signature_mismatches` はすべて空である。ledger を削除・改変してこの failure を隠しておらず、Full Regression verifier の current result contract は未成立として扱う。

### Evidence and gate status

artifact SHA-256、PR head、GitHub Linux/macOS run/check、runner checkout HEAD、post-freeze receipt、Strict review result はまだ candidate `C` に束縛されていない。したがってこの report は pre-freeze 実装要約と verification contract の記録であり、final evidence receipt ではない。

## Residual Risks / Follow-ups

### Decision Required

ChatGPT Use Extra High による red-team 分析では、最初に不整合となった normative layer は Step 10 の evidence contract と判定された。推奨される仕様変更は、historical ledger row を保持したまま、明示的な `resolved-baseline` metadata と successor test の collected・passed・not-skipped を要求する `resolved-baseline + successor-pass` 契約を requirement/design/plan と verifier に定義することである。

これは ledger/verifier の意味を変更する人間の設計判断であり、この report の範囲では承認済みとみなさない。承認なしに requirement/design/plan、ledger、verifier を変更してはならない。

### Remaining work and process gates

- 人間の承認後に、必要なら仕様 amendment と verifier/ledger/negative-test の変更を別の実装単位として行い、Full Regression を新 candidate で再実行する。
- report を含む candidate を commit/push し、同一 PR head SHA について package artifact digest、Linux/macOS provider CI、focused tests、ordinary gates、Full Regression の再現可能な receipt を PR/check/CI artifact に記録する。post-freeze receipt を tracked report に追記しない。
- Strict Final Quality Gate は未実施である。指摘があれば新 candidate として影響範囲の evidence を取り直し、exact final SHA を再レビューする。
- Human PR merge と `issue finish` は未実施であり、implementation completion や Strict review の代替ではない。

現時点の process gate は次の状態である。

| gate | 状態 |
|---|---|
| M1〜M5 implementation change | 実装済み・中間 candidate で確認済み |
| Step 9 ordinary/focused local verification | pass |
| Step 10 current Full Regression verifier | **未達（ledger-mismatch）** |
| Step 11 same-candidate final evidence | 未成立（report 編集後に新 candidate が必要） |
| Implementation Completion | 未達 |
| Strict Review Pass / Final Quality Gate | 未実施 |
| Human PR Merge Gate | 未実施 |
| `issue finish` | 未実施 |

従って Issue 372 の実装完了、最終 candidate `C`、merge可能状態はまだ宣言しない。

### Step 10B — accepted canonical verifier による pre-freeze acceptance（2026-08-31）

Issue 382 の人間による merge と lifecycle closure を確認したうえで、Issue 372 branch の
merge commit `bc1560096593c645ec0309a37a080c53a7e7f35d` を pre-freeze candidate として
受入確認した。

- PR [#383](https://github.com/chemitaro/spec-dock/pull/383) は `bc1560096593c645ec0309a37a080c53a7e7f35d` として Issue 372 branch に merge 済みである。
- GitHub Issue #382 は `CLOSED`、`./spec-dock/scripts/spec-dock deps check --id iss-00372 --github --json` は `ready=true`、`blockers=[]` である。
- 実行したのは repository-level canonical root route `uv run python -m scripts.quality.verify_full_regression --shards 4` である。root の `scripts/quality/` evaluator と root `full-regression-ledger.json` / `full-regression-timing-weights.json` を使用し、Issue 368 配下の historical `verify-full-regression.py`／artifact verifier は流用していない。
- focused GREEN: `uv run pytest tests/unit/test_full_regression_baseline.py tests/unit/test_provider_test_lanes.py` — `70 passed in 3.98s`。resolved successorを含む evaluator/adapter contract selectorもこの結果に含まれる。
- Full Regression: 上記 canonical command は exit 0、`2708 tests collected`、`status=verified`、`evaluation.verified=true`、`active_verified=26`、`resolved_verified=1`、`retired_verified=0`、`violations=[]`、`total_elapsed_seconds=1630.669` だった。各 shard の pytest process は active baseline failureを観測して exit 1 だが、shared evaluator が26件の承認済みactive failureとして正確に検証し、runner全体を verified とした。
- result artifact: `spec-dock/.workbench/full-regression/20260830T231104.876692Z/result.json`。`candidate_sha` は `bc1560096593c645ec0309a37a080c53a7e7f35d` と一致する。resolved successor `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` は shard-2 で exactly once collected・executed、outcome `passed` であり、skipされていない。観測ファイルは同ディレクトリの `shard-1.json`〜`shard-4.json` にある。
- この節は report 追記前の `bc156009…` に対する Step 10B pre-freeze acceptance 証拠であり、report追記後に生成される新しい candidate の final same-SHA receiptではない。primary はこの追記を含む commit/push後の新SHAについて、ordinary/focused/package/Linux/macOS/Full Regression/Strict evidenceを再取得する。
- 本Stepでは production semantics、ledger/timing policy、historical row/history、workflow、tests、その他の tracked fileを変更していない。既実施履歴も書き換えていない。
