---
種別: レポート（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
最終更新: "2026-08-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- recognized target の `update` と `init --force` を `execute_recognized_distribution()` の単一路線へ切り替えた。
- read-only `WorkspaceAssessment` と blocker-free `ExecutableMutationPlan` を分離し、root / intent / contract / canonical plan digest に束縛した `.distribution-journal.json` を導入した。
- managed regular file / symlink / obsolete prune / generated version / active fallback を既存 descriptor-bound kernel で適用し、action checkpoint、staging lease、exact pre/postcondition から partial failure を forward recovery できるようにした。
- legacy `.distribution-retry.json` は、同一 root/operation の `preflight-complete` で、実行 package が同一または compatible newer の場合だけ one-way conversion する。staging lease がある場合も action/name family/parent chain/device/inode/ctime/type/link count のexact一致を証明できれば schema-2 journal へ引き継ぎ、それ以外と dual recovery state は mutation 前に拒否する。
- recognized flow から旧 scaffold callback、CLI-owned marker transition、plan 外の version write を除去し、fresh-only compatibility route は `iss-00369` の対象として到達不能のまま残した。
- README と shipped/dogfooding docs の recovery guidance を new journal contract に更新した。
- Strict bounded review で検出した journal action 改変、generated path traversal、parent rebind、plan 外 active mutation、no-op journal 作成を根因単位で修正し、回帰テストを追加した。
- Strict remediation で active fallback の generated refresh authority を事前観測した exact pointer identity に束縛し、外部・workbench symlink と asset capture 後の pointer rebind を operation 全体の write 前 blocker にした。
- Strict successor remediation で assessment と canonical plan の authority 一致を発行前に検証し、legacy marker 変換失敗時の prepared journal rollback、terminal journal の digest/action contract 再検証、recognized flow 全体の descriptor-bound root と visible identity 検証を追加した。
- retained-skill SHA failure は fixed point と Strict candidate の expected/actual 値がそれぞれ同一であることを `artifacts/retained-skill-baseline-comparison.json` に記録し、Issue 368 による回帰ではないことを再現可能にした。
- marker / journal の cleanup は、root operation lock 内で推測不能な nonce を持つ private quarantine 名へ no-replace rename し、移動後の held-fd identity が一致した場合だけ削除する。並行置換を検出した場合は置換 entry を元の予約パスへ復元して fail-closed にする。
- quarantine rename は削除前に directory fsync し、削除または事前 fsync が失敗した場合は held identity を canonical journal / marker path へ no-replace restore する。失敗を返した後も次回 retry が同じ recovery authority を再読できる。
- Strict g6 remediation で missing parent も journal precondition に保持し、resume 前に出現した parent collision を write 前に拒否するようにした。journal package compatibility は exact protocol / contract / plan を維持した forward-only version とし、downgrade は拒否する。
- staging lease は operation ID に束縛した digest と action/known-stage contract の両方を検証し、journal へ追加された未証明 lease から cleanup authority を得ない。active fallback の refresh authority は有効な `.meta.json` entry または layer 固有の exact `active-none` target に限定した。
- Strict g6 の再審査で検出した `active/context-pack.md` の symlink collision は、事前観測した単一リンク regular identity だけを generated refresh の対象にすることで write 前 blocker にした。regular file の安定性判定から read に伴う atime 変化を除外し、正当な stale context pack の更新は維持した。
- Strict g8 bounded review を受け、fresh retry は D2 所有の `_install_fresh_compatibility_distribution_unlocked()` へ直接接続し、recognized handler から legacy/fresh compatibility call edge を物理的に除去した。fresh fault-injection contract は専用入口を通して維持する。
- Strict g9 semantic review の4件を受け、journal publish の stage 名を nonce 化し、swap 後の旧 journal cleanup を held-fd quarantine 経路へ統一した。missing parent の作成権限は journal に未作成 binding として mkdir より前に永続化し、作成後の exact inode binding へ昇格するため、mkdir 直後と journal rename 直前の crash から同一 plan を再開できる。
- journal 前置 guard は schema 2 / `recognized-journal-forward-only` とし、schema 1 のみを認識する旧 installer が new journal workspace を mutation 前に拒否する一方、現行 installer は journal 作成前 crash と journal 併存状態を forward recovery できる。
- Strict g10 remediation では、prune と regular/symlink upgrade の最終 pathname mutation を held identity の再検証と nonce quarantine／atomic rollback へ統一し、競合差し替えを削除せず canonical path へ復元して fail closed にした。`uninstall --apply --keep-specs` は managed scaffold root 内の未知ファイル・ディレクトリを preflight blocker として列挙し、最初の mutation 前にツリー全体を保持する。
- Strict g10 bounded remediation では、durable な親作成意図と exact inode binding を分離した。mkdir 直後に exact binding を journal へ記録し、再開時に出現済み親を受理するのは `exists=true` の binding と inode が一致する場合だけとした。inventory にない旧 scaffold entry も未知ユーザー entry と同じく preflight で保持する。
- Strict g10 candidate 2 remediation では、pending journal action の precondition が assessment の完全な親チェーンを順序どおり保持することを要求した。親要素を削除して digest を再計算した journal も plan mismatch として mutation 前に拒否する。
- Strict g11 remediation では、full-regression の既知27件について固定点と実装 anchor の JUnit failure message を採取し、checkout / temporary path と pytest diagnostic suffix を正規化した assertion/error signature を node ID ごとに比較した。27件すべての SHA-256 が一致し、比較契約・run metadata・per-node signature を failure ledger 内へ保存した。
- Strict g11 bounded remediation では、installer の既存 regular file 更新を pathname `os.replace` から held target/staging descriptor に束縛した atomic swap へ変更した。identity 確認後に destination が差し替えられても swap 後検証または事前照合で拒否し、ユーザー置換 entry を保持する。
- Strict g11 candidate 2 remediation では、completed prune が再 assessment から消えた場合も descriptor-bound 再観測で exact postcondition を検証して terminal journal を完結できるようにした。全 journal action の pre/postcondition は完全な親チェーンを保持し、digest を再計算した親省略も拒否する。
- Strict g13 remediation では、uninstall の managed scaffold root 一括再帰削除を廃止し、各 shipped file を current content digest と no-follow identity に束縛した個別 action へ変更した。unknown または modified file は全 mutation 前の blocker とし、E365-R03 の preserve-and-block 契約を S70 と installer 回帰テストで固定した。
- Strict g13 final remediation では、legacy marker の admission 時 no-follow identity と bytes digest を journal publish 直前に再検証し、同一 root lock 内で schema-2 forward-only guard へ原子的に置換してから journal authority を発行する。compatible newer conversion の journal publish failure は guard から再開でき、admission 後の同内容 marker 差し替えは mutation 前に拒否する。
- terminal journal の regular/symlink postcondition に file type と link count 1 を保持し、`completed` retry でも current assessment が blocker-free かつ adopt/preserve のみであることを再確認してから journal を削除する。completed publish 後に managed target が hardlink 化された場合は journal を保持して recovery-required にする。
- Strict g14 bounded remediation では、journal action の target precondition を `device` / `inode` / `ctime_ns` を含む canonical 10-field schema として検証する。field を単独で欠落させた journal、および3項目を除いて同内容・同modeの別inodeへ差し替えた journal は、digestを再計算されても mutation 前に拒否する。
- Strict g14 candidate 2 remediation では、legacy marker の pathname `stat` 後に開いた held descriptor を事前観測した device / inode / ctime / mode / link count と再照合する。`stat` と `open` の間に同内容markerへ差し替えられても、guard swapとjournal発行前に拒否する。
- Strict g15 remediation では、journal の読取時 identity と bytes digest を非直列化 evidence として保持し、全 journal transition の publish 直前に predecessor の exact identity / bytes を再検証する。stage file も held descriptor に束縛し、stage・canonical journal・forward guard が同内容へ差し替えられても atomic rollback 後に fail closed とする。
- journal 再開時は schema-2 forward-only guard の exact identity / digest を admission と全 publish 境界で再検証し、guard 欠落、schema-1 downgrade、同内容差し替え、journal publish 直前の置換を `dual-recovery-state` または recovery-required として mutation 前に拒否する。
- `uninstall --apply --keep-specs` は Epic 365 の固定点契約どおり、管理対象ルート `spec-dock/{docs,templates,scripts,system}` をルート単位で再帰削除する。管理ルート内の legacy / modified / unknown entry はルートとともに削除し、Strict g13 で導入された個別ファイル preserve-and-block 退行を解消した。
- full-regression の pre-slow 診断は、実装 anchor 上の JUnit failure node ID と正規化 signature 27件を ledger と実行時照合してから exit 0 を返す verifier で実施した。controller の authoritative slow profile が実行する `pytest --run-full-regression -q` 自体にも同一 ledger guard を組み込み、全既知 node を収集した suite で node ID、signature、setup/teardown error が不一致なら非許可の exit 3 とする。検証中に発見した本文長 `37` と時刻文字列の部分一致による既存 privacy test の誤検知も、曖昧な短数値 sentinel を除去して安定化した。
- `chatgpt-final-quality-gate-strict-new` の exact-SHA review で検出した recovery entry の authority 再取得を修正した。journal transition は forward guard の held descriptor、identity、bytes digest を publish 前後で検証し、journal / guard の successor evidence は公開に用いた stage descriptor から構築して canonical name が同じ inode を指すことを返却直前に確認する。
- journal / guard finalization は caller が保持する source snapshot と digest を deletion authority とし、quarantine rename 前に held descriptor の identity と bytes を照合する。同内容・異内容の並行置換はいずれも削除せず fail closed とし、journal publish 後に guard が置換された場合は current operation が公開した exact journal inode だけを rollback する。
- authoritative full-regression ledger guard は `--run-full-regression` 指定時に常時有効化し、ledger の欠落・不正、および削除・rename・focused selection による expected node 欠落を mismatch として exit 3 にする。expected node が collection に揃わないことを guard 無効化の条件にはしない。
- Strict successor review で検出した symlink exchange race は、交換前の exact snapshot とlink target、交換後の安定した両pathname、rollback前後の両identityとlink targetを照合するCASへ変更した。最初の交換内で置換されたentryはexact pairを再交換してcanonicalへ復元し、二重raceでidentityが曖昧なstageを再取得してcleanup authorityへ昇格しない。
- schema-2 forward guard はjournal作成前に `operation_id`、`contract_identity`、canonical `plan_digest` を永続化する。再開時はguardとjournalの独立アンカーを照合するため、action順序やimmutable metadataを変更してjournal内部のdigestを再計算してもmutation前に拒否する。
- managed stage名とprune quarantine名は作成・rename前にzero-identityの予約leaseとしてjournalへ記録し、作成後のexact inode leaseへ昇格する。swap直後に停止してdesired inodeがcanonicalへ移り旧precondition inodeがstageへ移った状態、およびprune rename直後の予約quarantineは、journalへ遷移後identityをwrite-ahead記録してからcleanupする。元はmissingの親directoryは、全descendant actionがpendingかつ出現したreal directoryが空の場合だけexact inode bindingへ昇格し、非空・symlink・計画外出現は拒否する。
- 強制終了時に残るfilesystem状態を直接構築する回帰として、予約stage作成直後、regular swap直後、prune quarantine直後、self-rehashed action reorderを追加し、同一plan retryの収束とplan改変のmutation前拒否を固定した。
- Strict successor の5件 remediationで、exact legacy stage leaseのschema-2引き継ぎ、mutable regular write中のreserved-name lease維持、publish前のexact successor昇格、canonical successorのdisplaced predecessor cleanupより先のdurable化、same-bytes/different-inode create successor拒否を追加した。regular/symlink exchangeはpre-exchange canonical raceのみexact successor/unknown stage pairをCAS rollbackし、post-exchange unknown canonicalはrollback/cleanupせず保持する。legacy guard predecessorはschema-2 successor受理後まで削除しない。
- Strict successor の guard-only remediationで、journal不在のschema-2 forward guardはlegacy markerとして再発行せず、既存operation/contract/planと再構成planのexact一致時だけ同じguardからjournalを発行する。terminal cleanupはguard削除の成功後までcompleted journalを保持し、guard削除後のcompleted journal-only状態は対象を再適用せずcleanupのみ完了する。
- `1d62f3221a5a55add1c592076de2688c2f0b4a89` は旧 campaign の実装 anchor であり、その後の Strict remediation で実装とテストを変更したため最終 candidate anchor ではない。最終 exact candidate の SHA と同一 SHA 上の review/test 合否は Strict check attestation を正本とする。

## Verification

exact candidate の SHA と合否の正本は、当該 report 自身を含む `review_head_sha` に対して生成される Strict controller の candidate manifest / check attestation / certificate とする。report 内へ自己参照的な候補 SHA を固定せず、以下の手動確認は controller 実行前の診断証拠として区別する。

- [x] `make lint` — successor 候補 commit 前の診断で ruff check / format check / mypy が成功
- [x] `uv run pytest -q tests/unit/infra/test_managed_distribution.py` — 156 passed
- [x] `uv run pytest --run-full-regression -q tests/unit/infra/test_init_update.py -k 'unknown_file_inside_managed_scaffold_root or scaffold_managed_roots_remove_recursively or preserves_unknown_files_under_managed_roots'` — 3 passed、129 deselected
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py` — 131 passed
- [x] `uv run pytest --run-full-regression -q tests/cli_runtime/test_distribution_cutover.py` — 144 passed、1 failed。残る failure は fixed point と remediation SHA で expected/actual SHA が不変な Issue 359 retained-skill golden の既存不一致
- [x] `uv run pytest --run-full-regression -q` at `72c1e4c724c115f0d6d6831eb6c2cff8bc239700` — 27 failed、2053 passed、48 skipped、17m10s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `f07c6440d827b2cea5ccdae7fe268e76706d1c39` — 27 failed、2057 passed、48 skipped、17m02s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `4d6304c7c983a45f495e3efc439e5c3b17ce5cad` — 27 failed、2058 passed、48 skipped、16m59s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `2715c0bfbbe4b7ac5583cb2af37117810bb05ae3` — 27 failed、2059 passed、48 skipped、17m18s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run python .../artifacts/verify-full-regression.py` at `700a39fa71ee8aab283648c79e5101930d8db3fa` — underlying pytest は 27 failed、2061 passed、48 skipped、17m19s。verifier は既知27件の node ID と正規化 failure signature の完全一致を確認して exit 0
- [x] `uv run python .../artifacts/verify-full-regression.py` at `a28b57f25c82cde96411965ace491f44540cab48` — underlying pytest は 27 failed、2063 passed、48 skipped、17m10s。verifier は既知27件の node ID と正規化 failure signature の完全一致を確認して exit 0
- [x] `uv run python .../artifacts/verify-full-regression.py` at `bd2141708ed3a332bfb98ccbd2eabcf008e8ca66` — underlying pytest は 27 failed、2063 passed、48 skipped、17m14s。authoritative pytest guard と外側 verifier の双方が既知27件の node ID と正規化 failure signature の完全一致を確認
- [x] `uv run python .../artifacts/verify-full-regression.py` at `967b7253ac78ee925bead668951fc1065191ec7c` — underlying pytest は 27 failed、2064 passed、48 skipped、17m21s。authoritative pytest guard と外側 verifier の双方が既知27件の node ID と正規化 failure signature の完全一致を確認
- [x] `uv run python .../artifacts/verify-full-regression.py` at `b8c5a64260cd640d5bda720c60e0e067739dc3de` — underlying pytest は 27 failed、2067 passed、48 skipped、17m21s。authoritative pytest guard と外側 verifier の双方が既知27件の node ID と正規化 failure signature の完全一致を確認
- [x] `uv run python .../artifacts/verify-full-regression.py` at `001350ff90d8725cf69ddea54930bfa0524657bb` — underlying pytest は 27 failed、2071 passed、48 skipped、17m19s。authoritative pytest guard と外側 verifier の双方が既知27件の node ID と正規化 failure signature の完全一致を確認
- [x] `uv run python .../artifacts/verify-full-regression.py` at `9170f2d5e78ee3b6ebf8593f2d9f9add86fa8efb` — underlying pytest は 27 failed、2072 passed、48 skipped、17m13s。authoritative pytest guard と外側 verifier の双方が既知27件の node ID と正規化 failure signature の完全一致を確認
- [x] `uv run pytest --run-full-regression -q` at `1d62f3221a5a55add1c592076de2688c2f0b4a89` — 27 failed、2077 passed、48 skipped、17m54s。authoritative pytest guard が既知27件の node ID と正規化 failure signature の完全一致を確認し、新規 failure 0件
- [x] `uv run pytest --run-full-regression -q tests/unit/infra/test_init_update.py` — uninstall の exact-content file action と preserve-and-block を含む 133 passed
- [x] fixed point と candidate で `test_tc_346_s03_003_actual_cross_filesystem_source` の時刻 `08:37` 誤検知を再現し、privacy oracle 修正後の focused full-regression は 1 passed
- [x] failure ledger に列挙した9ファイルを `--run-full-regression --junitxml=<run.xml>` で固定点と実装 anchor の双方で再実行 — 各27 failed、正規化した27件の failure signature と aggregate SHA-256 `6ee128836773e80ca6c07e17f0b45bf75cb9901976205cf37ab23844bb6c1dc8` が一致
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q` — 275 passed、1 failed。残る failure は既知の Issue 359 retained-skill golden
- [x] `uv run pytest -q` — 1099 passed、1053 policy-skipped
- [x] `uv run pytest tests/unit/infra/test_managed_distribution.py -q` — write-ahead reservation、abrupt swap/prune recovery、plan anchor、symlink CAS race を含む 176 passed
- [x] `uv run pytest tests/unit/infra/test_managed_distribution.py -q` — legacy exact-stage conversion、mutable stage lifecycle、same-bytes inode replacement拒否、post-exchange third-party preservation、guard predecessor保持、schema-2 guard-only drift拒否、terminal journal-only cleanupを含む 185 passed
- [x] `uv run pytest tests/unit/test_provider_test_lanes.py -q` — missing ledger / missing node / incomplete selection を含む 12 passed
- [x] `make lint` — ruff check / format check / mypy が成功
- [x] `uv run pytest -q` — 1115 passed、1053 policy-skipped
- [x] `./spec-dock/scripts/spec-dock validate` — `nodes=227`
- [x] `git diff --check` — 成功
- Strict の最終合否は repository 外の append-only campaign ledger と certificate にのみ記録し、合否記録のために認証後の candidate を変更しない。

## Residual Risks / Follow-ups

- fresh target の同名 entrypoint は現行 compatibility route を維持しており、`iss-00369` で同じ Contract / Assessment / Kernel / Journal / Result seam へ移行する。
- deprovision、history purge、all-surface/Linux/package parity は親 Epic の順序どおり `iss-00370`〜`iss-00372` で扱う。
- full regression の既存 runtime/golden failures は本 Issue で修復しない。Issue 368 に関係する distribution cutover surface は、既存 retained-skill SHA golden 1 件を除いて通過している。
