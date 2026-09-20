---
種別: レポート（Issue）
ID: "iss-00405"
タイトル: "Directory Replacement Final Cleanup"
関連GitHub: ["#405"]
最終更新: "2026-09-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00384", "init-local-00003"]
---

# Result Summary

## Current outcome — S7 delivery checks and integrated review complete

GitHub Issue #405 はEpic #384配下に作成され、`issue start --id iss-00405`で正式開始されています。実装branchは`iss-00405-directory-replacement-final-cleanup`、active Issueは`iss-00405`です。

承認済みRequirement / Design / Planとtest dispositionに従い、S0〜S6の実装・ローカル統合検証を完了し、PR #406を作成しました。PR candidate `11825a335b628b195cb61ddd47abe8aaab9cfd88`ではPR checksとfresh integrated reviewが合格しています。その後のcommit `2849bf596efc5d98c061299035fcdf05e049727e`はIssue/Epic Reportだけを更新し、現在のブランチtipはこのReport snapshotを含みます。したがって、`11825...`のchecks/reviewは前candidateの証拠として記録し、Report snapshotを含む現在tipのPR checksは別途確認します。final-SHA必須テストとFinal Quality Gate Strict v2も未実施で、人間によるmergeは行っていません。

### Unit status

| Unit | 状態 | 証拠・境界 |
|---|---|---|
| S0 | 完了 | accepted仕様、strict仕様レビュー、baseline、test disposition、HTML、SpecDock validateを確認。実装baselineは`a865277de85740acee536613bde6c7de50092e71`。 |
| S1–S3 | 完了 | provider generation/shared-lease gateの撤去と必要なcheckout/worktree/data safetyの維持。candidate `f77f6f7163430d6e5f1142eec7b8f07440e259f6`のfresh GPT-5.6 Sol Extra High reviewは`pass`、findings 0、confidence 0.94。 |
| S4–S5 | 完了 | test/harness cleanup、installer failure successorの現行挙動照合、provider-first docs/dogfood sync。candidate `0ab3ab341cf734a032042c9beebb0fb2dba94125`のfresh GPT-5.6 Sol Extra High reviewは`pass`、findings 0、confidence 0.97。 |
| S6 | 完了（local） | restart candidate `0d9114b038ddb78dab32bc6039b51c4d02943846`でfocused/full suite、lint、package、distribution integration、parity、SpecDock validateが完了。raw logsは後掲のS6 run directoryに保存。 |
| S7 | 進行中 | PR #406、全PR checks、fresh integrated reviewはprior candidate `11825a3`で合格。Report-only successor `2849bf5`のcurrent-tip checks、Final Quality Gate Strict v2と同じfinal SHAの必須テストを実施中／未完了。human merge未実施。 |

### S6 candidate restartの履歴

最初のS6試行はcandidate `0ab3ab341cf734a032042c9beebb0fb2dba94125`から開始しました。focused suiteとfull pytestは通りましたが、後続の`make lint`でS4–S5時に触れたtest/fixture 5ファイルのRuff check/format違反が見つかり、S6をそこで停止しました。mypyはその試行でも成功しています。このcandidateの途中結果を新candidateの合格証拠として流用していません。

違反5ファイルに`uv run ruff format`だけを適用し、実装動作や期待値は変更せず`0d9114b038ddb78dab32bc6039b51c4d02943846`として記録しました。その新candidateでS6の正規シーケンス全体を先頭から再実行し、以下の結果を得ました。

### S6 local qualification — exact candidate `0d9114b038ddb78dab32bc6039b51c4d02943846`

| 検証 | 実測結果 |
|---|---|
| focused seven-file suite | `141 passed in 92.22s` |
| canonical `uv run pytest` | `1551 passed, 25 skipped in 688.52s` |
| `make lint` | Ruff check成功、248 filesのformat check成功、174 source filesのmypy成功 |
| `uv build` | sdistとwheelのbuild成功。`dist/spec_dock-0.2.4.tar.gz`、`dist/spec_dock-0.2.4-py3-none-any.whl`を生成 |
| distribution integration | `11 passed in 13.05s` |
| `./spec-dock/scripts/spec-dock validate` | `spec-dock: ok (validate) nodes=237` |
| provider/dogfood parity | `10 passed in 0.28s` |
| end identity | branch/candidate一致、worktree/index差分なし、`git diff --check`成功 |

正規S6 raw log directory:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00405-directory-replacement-final-cleanup/.workbench/s6-local-qualification/0d9114b038ddb78dab32bc6039b51c4d02943846/20260920T102326Z/
```

`uv run pytest -rs`による同一candidateの補助的skip理由採取も成功し、`1551 passed, 25 skipped in 707.12s`でした。この補助実行はskip分類の記録専用であり、正規S6の実測時間・結果を置き換えません。25件の内訳は次のとおりです。

- 16件はS04で記載されたapplication/domain/runtime successor coverageにより重複する旧CLIケース。
- 7件はS06で記載された`test_runtime_new_s08`および`test_runtime_sync_s07`のsuccessor coverage。
- 1件はDarwin arm64上でraw non-UTF-8 filename bytesを扱うfilesystem操作が`EPERM`となるplatform limitation。
- 1件はDarwin arm64上でLinux `O_TMPFILE` capabilityがないため実行できないplatform limitation。

skip全項目とraw summaryは`20260920T102326Z/08-full-pytest-skip-reasons.log`および隣接する`skip-reason-breakdown.md`にあります。正規S6のfull-suite raw resultは`02-full-pytest.log`です。

### Current delivery gates

| Gate | 状態 | 結果の扱い |
|---|---|---|
| S6 local qualification | pass | 上記の公開済みcandidate `0d9114...`で実測済み |
| PR #406 / Ubuntu・macOS CI / latest exact-tip checks | pending | Prior candidate `11825...` passed; the Report-only successor is a new PR head and needs its own current-tip checks |
| fresh integrated code/spec/QA review | pass for prior candidate | GPT-5.6 Sol Extra High、range `a865277de85740acee536613bde6c7de50092e71..11825a335b628b195cb61ddd47abe8aaab9cfd88`、`review_status=pass`、findings 0、confidence 0.97。current Report-only successor is additionally covered by final FQG |
| Final Quality Gate Strict v2 | pending | Report更新後に確定するfinal pushed SHAの全必須テストと最新PR checksを確認後、GPT-5.6 Sol Proで実施する |
| human merge | 未実施 | agentはmergeせず、merge-ready handoffで停止する |

### S7 delivery evidence — exact PR candidate `11825a335b628b195cb61ddd47abe8aaab9cfd88`

PR #406: [refactor: provider generation gateと旧テスト残滓を撤去 (#405)](https://github.com/chemitaro/spec-dock/pull/406)。評価済み候補`11825...`は下記check/reviewにpassしました。その後のcommit `2849...`はReportだけを更新してPR headを進めたため、新headのPR checksとmergeabilityは別途再確認します。これはmerge実施の記録ではありません。

| Check | 実測結果 |
|---|---|
| Provider CI / `provider-tests` | success、`1546 passed, 30 skipped in 1018.01s`。job内`make lint`も成功。 [run/job](https://github.com/chemitaro/spec-dock/actions/runs/35507399426/job/106069427747) |
| Provider distribution parity (`ubuntu-latest`) | success、`12 passed in 2.77s`。 [job](https://github.com/chemitaro/spec-dock/actions/runs/35507399426/job/106069427826) |
| Provider distribution parity (`macos-latest`) | success、`12 passed in 3.71s`。 [job](https://github.com/chemitaro/spec-dock/actions/runs/35507399426/job/106069427917) |
| CI `validate` | success。 [job](https://github.com/chemitaro/spec-dock/actions/runs/35507399439/job/106069427736) |
| Commit identity `check` | success。 [job](https://github.com/chemitaro/spec-dock/actions/runs/35507399443/job/106069427820) |
| PR/push-triggered check inventory | `gh pr checks 406` readbackでは、上記PR jobsおよび同candidateのpush-triggered `validate` / `check`を含め、返された全checksがsuccess。 |

Provider CIはpull-request merge commit `cae669050cb5209cfcf3c958e70fdf7b307da1a2`上で実行されました。そのtree SHA `bb2fd5c1c2a39d05c584f82bc55d2ada435d0a2d`はPR head `11825...`のtree SHAと一致しています。Provider CIの30 skipsはCIログに個別理由が出ていないため、このレポートでは理由を推定しません。Darwin arm64上のローカルS6 `1551 passed, 25 skipped`と、Linux runner上のCI `1546 passed, 30 skipped`は環境・候補の異なる結果として分けて扱います。

fresh integrated Strict reviewはsession `required-strict-github-connector-verificati-1050`、GPT-5.6 Sol / Extra Highでrange `a865277de85740acee536613bde6c7de50092e71..11825a335b628b195cb61ddd47abe8aaab9cfd88`を対象に実施し、`review_status=pass`、findings 0、confidence 0.97でした。raw structured resultはGit管理外Workbenchの`reviews/s7-integrated-review.json`に保存し、SHA-256は`2cef8ca7501d9b0a8d006bde4a03dca09fb4435e84ddfdb389651b1a43f05f6d`です。このreviewはFinal Quality Gate Strict v2の代替ではなく、現行PR head checksも別途必要です。

## Deliverables

- [要件](requirement.md) / [設計](design.md) / [計画](plan.md)
- [人間向けHTML](artifacts/cleanup-guide.html)
- [Luna Max handoff](artifacts/20260920t055027z-luna-max-handoff.md)
- [Source symbol map](artifacts/20260920t055027z-01-source-symbol-map.md)
- [Test disposition](artifacts/test-disposition.csv)
- [採用記録](artifacts/20260920t055027z-02-specification-adoption-receipt.md)
- [仕様レビュー指摘の分析](artifacts/20260920t064301z-specification-review-findings-analysis.md)

## Checkpoints

- `3c5ffff237e38f767b0600de39e7ce2d6ef04e12`: Issue #405雛形作成。
- `457faf31df8840d1f2fc87417d297dc318903fbe`: 監査ZIP保存。Strict authoringの公開基点。
- `a865277de85740acee536613bde6c7de50092e71`: accepted仕様と実装baseline。
- `f77f6f7163430d6e5f1142eec7b8f07440e259f6`: S1–S3実装・ローカル検証・Strict review pass。
- `0ab3ab341cf734a032042c9beebb0fb2dba94125`: S4–S5 cleanup/sync・Strict review pass。
- `0d9114b038ddb78dab32bc6039b51c4d02943846`: S6 restart candidate。Ruff formatのみの修正後、S6全sequenceを再実行。
- `11825a335b628b195cb61ddd47abe8aaab9cfd88`: S7 Report証拠更新、PR #406、PR checks、fresh integrated review pass。final-SHA tests/FQG v2は次のゲート。

## Residual risks / non-goals

- installerは仕様どおりnontransactionalであり、自動rollbackしない。途中失敗時は外部installerを再実行して置換を完了する。
- native Git hook/config failureは起こり得る。
- same-EUID非協調actorへの追加保証、cross-filesystem worktree対応、atomic installer/journal/rollbackは追加していない。
- S7のPR CIとintegrated reviewはpass。final evidence SHAの全必須テストとFinal Quality Gate Strict v2が未完了のため、merge-readyではない。

## Historical appendix — specification authoring and adoption

以下は実装開始前の仕様作成・採用時点の記録です。実装状態のsource of truthではなく、上記current outcomeを上書きしません。

同じChatGPT会話をStrict/GPT-5.6 Sol・Proで継続し、Luna Max実装用のrequirement/design/planを作成しました。F001〜F009の処置、target-bound helperを保持する具体設計、test successor、checkpoint、通常品質経路を仕様化しました。

- Strict著者側exact SHA: `457faf31df8840d1f2fc87417d297dc318903fbe`。原ZIP CRC/internal hashes、SpecDock validate (`nodes=237`)、Markdown links、既存test 100 caseのpath/symbol/line照合を確認。
- HTMLの2図描画、拡大操作、keyboard/focusを検証し、承認されたlive symlinkでTailscale配信した。仕様作成時URL: `http://100.85.74.8:8765/iss-00405-cleanup-guide.html`。
- 独立仕様reviewの初回はfail（P1 4件、P2 2件）。指摘を分析・修正し、再review pass後に仕様を採用した。
- [仕様レビュー分析記録](artifacts/20260920t064301z-specification-review-findings-analysis.md)。初回ZIPはその採用時点の履歴であり、後続修正済み仕様の代替ではない。
