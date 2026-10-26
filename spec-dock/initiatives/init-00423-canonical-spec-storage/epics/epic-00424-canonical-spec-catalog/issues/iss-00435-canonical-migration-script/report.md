---
種別: レポート（Issue）
ID: "iss-00435"
タイトル: "Add Throwaway Canonical Migration Script"
関連GitHub: ["#435"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- `scripts/migrate-to-canonical/migrate.py`（パッケージを読み込まない1つのファイル）と `README.md`、`.gitignore`（`.state/`）を足した。サブコマンドは `plan`、`register`、`verify`、`undo`、`build-canonical`、`cut`、`move-local`、`adopt-worktree`、`export-legacy`。既定では予定の表示だけで、`--apply` でだけ書く。
- 写した値（C1、C2、C3、C5、C6、C7）を、パッケージの定数と資産と比べるテストを置いた（`tests/unit/infra/test_migration_contract_copies.py`）。
- I-7 から引き継いだ `canonical check` の調べること4を直した。版4の宣言の `writer_protocol` が `specdock.worktree-writer/v1` でなければ（古い `specdock.writer/v1` を含む）、`WORKSPACE_DECLARATION_INVALID` の失敗の1件になる。
- `make lint` の対象に `scripts/migrate-to-canonical` を足した（統括の判断 Q6）。
- 偽の `gh`（`tests/support/fake_github.py`）に、番号で Issue を読む GraphQL、本文の PATCH、ラベルの定義の削除を足した（今の振る舞いは変えていない）。

### 変えたテスト（AC-15 の確認）

- 版3の振る舞いを確かめるテストは変えていない。
- 変えたのは I-7 の `canonical check` のテストだけである：`tests/unit/application/test_canonical_check.py` の「古い既知の値を通す」テストを、「失敗の1件になる」テストに置き換えた（統括の判断による振る舞いの変更）。`tests/cli_runtime/test_issue434_canonical_check.py` に、同じ場合の CLI のテストを1件足した。

## Verification

### 本物の5つのリポジトリでの `plan`（AC-435-05。2026-10-26、読むだけ）

- 実行：各リポジトリの mainのチェックアウトで `python3 scripts/migrate-to-canonical/migrate.py plan --project <main> --json`。GitHub は読むだけ（GraphQL と GET）。
- 書かないことの確かめ：実行の前後で、`git for-each-ref`、`git --no-optional-locks status --porcelain`、`.git/index` の更新の時刻を比べ、6つのクローンのすべてで同じだった。
- 結果（数は `origin/<既定のブランチ>` の手元の値。下の「古い参照」を参照）：

| リポジトリ | 既定 | Scope（I/E/Is）・依存 | 止める異常 | ほかの異常 | 登録の予定（書き込み、見込み） | 作業用のworktree | mainの追跡外・無視 |
|---|---|---|---|---|---|---|---|
| spec-dock | main | 261（4/27/230）・159 | なし | `LOCAL_SCOPE` 2、`TITLE_MISMATCH` 35、`CLOSED_PARENT_OPEN_CHILD` 1（iss-00250 が閉じた epic-00224 の下で開いている） | 940回、約113分 | 12。仕様の変更があるのは、この Epic の実装ブランチ（iss-00430、iss-00431、iss-00435。各3ファイルのコミット済み） | 114 |
| taikyohiyou_project | develop | 246（4/44/198）・284 | なし | `TITLE_MISMATCH` 62 | 1021回、約123分 | 0 | 19 |
| housing-lifecycle | main | 233（16/36/181）・56 | なし | なし | 742回、約89分 | 15。どれも仕様の変更なし | 0 |
| input-devices | main | 17（1/3/13）・13 | なし | なし | 66回、約8分 | 1（`/private/tmp` の下、prunable） | 0 |
| company-os | main | 0 | なし | なし | 3回（種類のラベルだけ） | 2。どれも仕様の変更なし | 0 |

- ローカルの Scope（spec-dock）：`init-local-00002` は #39 と題名が同じなので `init-00039` に置き換える。`init-local-00003` は #31 の題名が違う（'Replace Wrapper S…'）ので、`register` が題名 'Architecture Maintenance and Hardening' の新しい Initiative の Issue を作る。
- `TITLE_MISMATCH` の多くは、GitHub の題名が日本語や大文字小文字の違いで、`.meta.json` が英語の slug 風の題名のもの。GitHub の題名を正とする（登録で題名は変えない）。
- 古い参照：taikyohiyou_project の2つのクローンで、手元の `origin/develop` が GitHub の先頭（`71954a8b…`）より古いと警告した。mainのチェックアウトの HEAD も `origin/develop` と違う。本番の前に `git fetch origin` が要る（スクリプトは書くサブコマンドで止まる）。
- SpecDock を呼ぶCIの行：`.github/` の下で `spec-dock` か `specdock` を含む行を、文字の一致で示すので、CIの手順ではない行も出る。統括が切り替えのPRで外すべき手順は次のとおり（ほかの行は外さない）。
  - taikyohiyou_project：`ci.yml` 16〜20行（`pip install 'git+…/spec-dock.git@0e7dc868…'` と `workspace validate --ci --json`）。`resolve_staging_route.py`（67、68、297〜316行）と `check_commit_identities.py` は、`spec-dock/` のパスやボットの名前を扱う行で、手順ではない。`resolve_staging_route.py` の `spec-dock/` の扱いが切り替えの後も正しいかは、I-12 の予行演習で確かめる（Epic の Current の注記）。
  - housing-lifecycle：`ci.yml` 16〜21行（`pip install … spec-dock@4d25a8b4…`、`spec-dock --version`、`workspace validate --ci --json`）。
  - input-devices：`ci.yml` 17〜20行（`uvx --from git+…/spec-dock@4d25a8b4… spec-dock workspace validate --ci --json`）。
  - company-os：`ci.yml` 16〜21行（`uv tool install …`、`workspace validate --json`、`workspace doctor --json`）。
  - spec-dock：`ci.yml` 18行（`specdock-ci-validate.sh`）。`specdock-ci-check.sh` と `release-tag-decision.py` は残す（I-7 の部品）。
- 別のクローン `/Volumes/990p2t/workspace/company-os/businesses/housing-lifecycle/products/taikyohiyou_project`：`origin` は同じ `chemitaro/taikyohiyou_project`（既定 `develop`）で、taikyohiyou の2つ目のクローンである。手元の `origin/develop` が `/Volumes/990p2t/workspace/product/taikyohiyou_project` のものと違い（`212bb229…` と `0fd1e1d4…`。どちらも GitHub より古い）、Scope は253と数えた。作業用のworktreeが2つある（`/Volumes/990p2t/workspace/worktrees/orca/taikyohiyou_project/bonefish`、ブランチ `chemitaro/gha-hosted-runner-cost`、仕様のコミット済みの変更9件。もう1つは変更なし）。I-12 では、この2つ目のクローンでも `move-local`、`adopt-worktree`、`canonical link` が要るかを、統括が決める必要がある（書き込みはしていない）。

### 自動のテスト

- 受け入れのテスト：`tests/integration/migration/`（`test_migrate_plan.py`、`test_migrate_register.py`、`test_migrate_canonical.py`、`test_migrate_checkouts.py`）と `tests/unit/infra/test_migration_contract_copies.py`。外のネットワークは使わない（偽の `gh`、一時ディレクトリの bare の `origin`、`XDG_STATE_HOME` と作業の記録は一時ディレクトリ）。
- AC との対応：AC-435-01（全サブコマンドの `--apply` なし）、02（`develop` の `cut`）、03（Scope なし）、04（bare にだけ push）、06（止めて再開、`undo`）、07（注入した時計で1秒、80回/分、500回/時、`retry-after`）、08（ローカルの Scope、番号の不一致、題名）、09（canonical のツリーの一致と2回目）、10（`move-local` とその後の `canonical link`）、11（`adopt-worktree`、両方で変えたときの別名ファイルと停止、取り込み済みの再実行）、12（`export-legacy` と従来モードの `workspace validate`、`scope show`、日本語の題名）、13（写した値）、14（`canonical check`）、16（`plan` の観測）、17（足すだけ）、18（止まる条件）、19（`cut` の宣言のバイト列と、切った後の `canonical check`）、20（README）。

## Residual Risks / Follow-ups

- 予行演習と本番の実行は I-10、I-12 で行う。この Issue では、本物の GitHub とリポジトリに書いていない。`build-canonical` の `git subtree split` の時間（spec-dock は約2000コミット）は未確認（予行演習で測る）。
- `adopt-worktree` は、canonical とブランチの両方で変えたファイルや、git が中身を統合したファイルがあると、push の後に何も消さずに止まる（統括の判断 Q2 の条件）。README に手で外す手順を書いた。ブランチで変えていないファイル（分岐点と同じ中身）は「一致」として扱う解釈にした（`plan.md` の統括の判断 Q2 の注）。統括の確認を求める。
- CIの行の一覧は文字の一致なので、手順でない行も出る（上）。外す手順は統括が選ぶ。
- I-13 への申し送り：`scripts/migrate-to-canonical/` と、`scripts/static_analysis/run.sh` の対象の行を消す。
