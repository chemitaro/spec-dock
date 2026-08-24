---
種別: レポート（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
最終更新: "2026-08-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Issue 369 の fresh provisioning を、`init`、`init --force`、`update` の三つの entrypoint から同一の effective `fresh` intent として実行する構成へ切り替えた。`spec-dock` が absent、exact empty、preserved-specs の各状態で、top-level bootstrap 以外の変更を forward guard と operation journal に束縛した shared service が担当する。

fresh contract には current/scaffold/generated assets、active fallback、version、root Workbench seed、`spec-dock/initiatives`・`spec-dock/active`・`spec-dock/.agent`・`spec-dock/.workbench` と asset parent の required-directory action を含めた。recognized `update` / `init --force` の互換経路では Workbench seed の backfill を行わず、旧 fresh callback・recursive writer・plan 外 version write を fresh call graph から除去した。

P1 再レビューで検出された fresh Workbench seed の非所有 retry における構造 identity 欠落も解消した。外部に先行配置された provider-identical seed を採用する場合は、`device`・`inode`・`ctime_ns`・`link_count` を write-ahead journal へ保存し、親 directory の出現と plan digest の実行時 identity を同一契約で扱う。これにより、同一内容の別 inode 置換、link topology 変更、unknown child を非破壊のまま fail closed とし、許可された seed だけを同一 plan retry で採用できる。

Final Quality Gate Strict v2 で検出された fresh action grammar の防御不足も解消した。fresh の許可 action を `create`・`adopt`・`preserve`・`block`・`ensure-directory` に固定し、実行権限発行、journal 再開検証、apply kernel 入口の三境界で同じ規則を強制する。自己整合した assessment / plan / journal に `upgrade` または `prune` を偽装しても、filesystem の観測・変更前に拒否し、利用者所有 entry を保持する。

全回帰が4時間を超えていた根本原因は、fresh distribution の各action後に残り全actionを再観測する二乗走査と、同じfresh initを多数のテストsetupで反復していたことだった。freshに限って検証をphase boundaryと未束縛directory guardへ局所化し、operationで観測済みの親snapshotを後続actionへ伝播した。recognized update、upgrade、prune、GCの破壊的経路は従来の全再観測を維持している。freshの非破壊phaseはjournal checkpointをphase単位へ集約し、作業領域のtop-level entry集合はjournal開始後のimmutable indexへ固定した。

テスト側では、plain fresh initをsession単位で1回だけ実行してAPFS CoWまたはLinux reflinkで複製する。runtime clockなどテスト固有の事前状態を変えるhierarchy全体はキャッシュ対象外とし、fresh init自体を検査するケースも実経路のまま残した。distribution cutoverでも、update・uninstall・recognized動作の前提となるplain initだけを再利用し、fresh・reinit・option付きinit・非空targetは実経路を維持する。全回帰検証器はcollectionを含む600秒の総deadline、4シャード、JUnitとtiming evidenceを持ち、pytest assertionの既知署名を維持するため台帳作成時と同じ`-q`で実行する。並列テストの一時targetはGit管理外Workbenchへ隔離した。

4シャードの単純round-robinは、実行環境の変動下で重いnodeが偏り、正しい最終deadline判定により600秒でfailする余地が残っていた。成功したancestor candidateのJUnitから2秒以上のnode実測値を抽出し、未登録nodeを2秒として扱う決定的LPTへ置き換えた。timing evidenceのschema、有限正数、ancestor SHAをfail closedで検証し、各shard内のcollection order、全nodeの一意性・coverage、approved failure signature照合は維持する。

## Verification

- `make lint`: pass（ruff、format check、mypy）
- `uv run pytest -q`: pass（implementation candidate `fd36911438bed5dfd44ac06a8c86f67d4130c5b7`、1295 passed / 1119 skipped、60.40秒）
- `uv run pytest -q tests/unit/infra/test_managed_distribution.py -k "fresh_action_grammar or forged_assessment_cannot_prune"`: pass（3 passed / 346 deselected、5.20秒）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- `uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00369-fresh-distribution-provisioning/artifacts/benchmark-fresh-distribution.py --warmup 1 --runs 5`: pass（median 4.146666秒、max 4.210318秒。各runの`observe_target=1934`、`journal_publications=395`）
- `uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --timeout-seconds 600 --max-total-seconds 600 --shards 4`: pass（candidate `4b41339e3314431f7983f9d6fe05265f8588fd6e`、2417 tests、raw pytest `27 failed / 2342 passed / 48 skipped`、collection 0.425秒、shards 584.333秒、total 584.808秒、SLO 600秒）。27件の失敗はすべてfull-regression ledgerのapproved failure signaturesと完全一致し、unexpected failure/error、欠落、重複は0件だった。

## Residual Risks / Follow-ups

- full-regression は4シャードで2417 tests（27 failed / 2342 passed / 48 skipped）を584.808秒で実行した。27件のapproved failure ledgerはIssue 368から継承した本Issueの変更範囲外であり、candidate `4b41339e3314431f7983f9d6fe05265f8588fd6e`上で署名完全一致を確認済み。
- fresh benchmarkはwall-time契約（median 5秒以下、max 8秒以下）を満たす一方、観測回数とjournal publicationには追加削減余地がある。安全性を損なうlease batchingは本修正へ含めず、600秒SLOと安全回帰を優先した。
- Issue 369 の fresh provisioning 変更に起因する unexpected failure/error は検出されていない。
- fresh Workbench seed の親 directory が assessment 後に出現するケースでは、pending `ensure-directory` と子 action の閉集合・exact identity を満たす場合だけ採用する。未知の子、symlink/file parent、内容変更、別 inode 置換は guard/journal を保持して拒否する。
- marker/journal の terminal cleanup failure では、journal と forward guard を残して同一 plan の再試行へ進む。異なる root、contract、plan、または未知の child は fail closed とする。
- Strict v2 の advisory P2 として、protocol-1 の pending write が最初の current publication 前に protocol-2へ昇格されない境界が残る。P0/P1ではなく、将来のprotocol migration hardeningとしてIssue 370以降で扱う。
