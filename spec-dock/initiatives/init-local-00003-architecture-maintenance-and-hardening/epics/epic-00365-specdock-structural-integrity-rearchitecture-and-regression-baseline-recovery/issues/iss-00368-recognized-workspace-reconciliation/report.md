---
種別: レポート（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
最終更新: "2026-08-19"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- recognized target の `update` と `init --force` を `execute_recognized_distribution()` の単一路線へ切り替えた。
- read-only `WorkspaceAssessment` と blocker-free `ExecutableMutationPlan` を分離し、root / intent / contract / canonical plan digest に束縛した `.distribution-journal.json` を導入した。
- managed regular file / symlink / obsolete prune / generated version / active fallback を既存 descriptor-bound kernel で適用し、action checkpoint、staging lease、exact pre/postcondition から partial failure を forward recovery できるようにした。
- legacy `.distribution-retry.json` は、同一 root/package/operation の `preflight-complete` かつ staging lease なしの場合だけ one-way conversion し、それ以外と dual recovery state は mutation 前に拒否する。
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
- 実装 anchor は `2715c0bfbbe4b7ac5583cb2af37117810bb05ae3`。この後の差分は campaign plan と semantic review plan で一致する5件の `evidence_only_paths` に限定する。full regression ledger は実測候補 `2715c0bfbbe4b7ac5583cb2af37117810bb05ae3` の既存失敗集合へ再束縛し、後続の exact candidate 再実行結果は Strict check attestation で検証する。slow profile の完全な command/ledger 定義は `artifacts/final-quality-gate-check-profile.json` に保存した。

## Verification

exact candidate の SHA と合否の正本は、当該 report 自身を含む `review_head_sha` に対して生成される Strict controller の candidate manifest / check attestation / certificate とする。report 内へ自己参照的な候補 SHA を固定せず、以下の手動確認は controller 実行前の診断証拠として区別する。

- [x] `make lint` — successor 候補 commit 前の診断で ruff check / format check / mypy が成功
- [x] `uv run pytest -q tests/unit/infra/test_managed_distribution.py` — 144 passed
- [x] `uv run pytest --run-full-regression -q tests/unit/infra/test_init_update.py -k 'unknown_file_inside_managed_scaffold_root or scaffold_managed_roots_remove_recursively or preserves_unknown_files_under_managed_roots'` — 3 passed、129 deselected
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py` — 131 passed
- [x] `uv run pytest --run-full-regression -q tests/cli_runtime/test_distribution_cutover.py` — 144 passed、1 failed。残る failure は fixed point と remediation SHA で expected/actual SHA が不変な Issue 359 retained-skill golden の既存不一致
- [x] `uv run pytest --run-full-regression -q` at `72c1e4c724c115f0d6d6831eb6c2cff8bc239700` — 27 failed、2053 passed、48 skipped、17m10s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `f07c6440d827b2cea5ccdae7fe268e76706d1c39` — 27 failed、2057 passed、48 skipped、17m02s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `4d6304c7c983a45f495e3efc439e5c3b17ce5cad` — 27 failed、2058 passed、48 skipped、16m59s。27件は fixed point ledger の node ID 集合と一致
- [x] `uv run pytest --run-full-regression -q` at `2715c0bfbbe4b7ac5583cb2af37117810bb05ae3` — 27 failed、2059 passed、48 skipped、17m18s。27件は fixed point ledger の node ID 集合と一致
- [x] failure ledger に列挙した9ファイルを `--run-full-regression --junitxml=<run.xml>` で固定点と実装 anchor の双方で再実行 — 各27 failed、正規化した27件の failure signature と aggregate SHA-256 `6ee128836773e80ca6c07e17f0b45bf75cb9901976205cf37ab23844bb6c1dc8` が一致
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q` — 275 passed、1 failed。残る failure は既知の Issue 359 retained-skill golden
- [x] `uv run pytest -q` — 1079 passed、1053 policy-skipped
- [x] `./spec-dock/scripts/spec-dock validate` — `nodes=227`
- [x] `git diff --check` — 成功
- Strict の最終合否は repository 外の append-only campaign ledger と certificate にのみ記録し、合否記録のために認証後の candidate を変更しない。

## Residual Risks / Follow-ups

- fresh target の同名 entrypoint は現行 compatibility route を維持しており、`iss-00369` で同じ Contract / Assessment / Kernel / Journal / Result seam へ移行する。
- deprovision、history purge、all-surface/Linux/package parity は親 Epic の順序どおり `iss-00370`〜`iss-00372` で扱う。
- full regression の既存 runtime/golden failures は本 Issue で修復しない。Issue 368 に関係する distribution cutover surface は、既存 retained-skill SHA golden 1 件を除いて通過している。
