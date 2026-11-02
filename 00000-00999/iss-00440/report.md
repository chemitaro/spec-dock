---
種別: レポート（Issue）
ID: "iss-00440"
タイトル: "Remove Legacy Mode"
関連GitHub: ["#440"]
最終更新: "2026-11-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

従来モード（宣言の版3、`.meta.json`、入れ子の置き場、slug）のコード、テスト、文書を撤去し、canonical モードだけを持つ SpecDock 0.5.0 にした。版3の宣言を読むと、`canonical check` のほかのどのコマンドも、何も読み書きせずに `CANONICAL_NOT_MIGRATED`（終了コード3）で止まり、「SpecDock 0.4.2 を入れ直し、版のタグ v0.4.2 の scripts/migrate-to-canonical/README.md に従って移す」を示す。

### 実装したこと

- **宣言の受け付けと振り分け（C2）**：`project_context.read_workspace_declaration` は版4だけを受け付け、版3は `WorkspaceNotMigrated`（`ValueError` の子）を投げる。`dispatch()` はそれを `CANONICAL_NOT_MIGRATED` に変える。モードの型と関数（`LEGACY_WORKSPACE_SCHEMA`、`WorkspaceMode`、`workspace_mode`、`probe_workspace_mode`、`ProjectContext.mode`）を消し、「その checkout は版4か」は `declares_schema_4` の1つで判定する（`canonical_status`、`canonical_link` の2か所、`canonical_dashboard`）。`installation` と `workspace doctor --raw` は `require_migrated` で版3だけを止め、宣言が読めない・曖昧なとき（重複キーなど）は 0.4.2 と同じく観測を返す。`dispatch()` の従来の分岐（30余りの `elif`）を消し、宣言を受け付けた後は `CANONICAL_HANDLERS` の表だけを引く。
- **ほかの worktree の観測（統括の判断、2026-11-02）**：`resolve_observed_context` を足し、`work start` の重複選択の確かめと `workspace sync` の worktree の一覧だけは、版3の linked worktree も Git の識別と直接の選択の記録だけで観測する（`.meta.json` や仕様は読まない）。spec-dock のクローンに、利用者が残すと決めた版3の worktree が2つあるため。その worktree の中のコマンドは `CANONICAL_NOT_MIGRATED` で止まる。
- **コマンドと引数**：`workspace migrate` と `workbench copy`、`workspace validate --ci`、`workspace sync --source local`、`dependency check --source local`、`scope create`・`scope import github` の `--slug` を消した（引数の誤り、終了コード2）。公開のコマンドは 55 から 53 になった（Epic の文書の「51」は 0.4.0 の `scope check` と `scope render` を数える前の数で、Epic の文書も 53 に直した）。`CANONICAL_NOT_APPLICABLE` と `CANONICAL_WORKBENCH_SHARED` の定数と分岐、`canonical_refusals.py` を消した。`--help` の説明から `Schema 4:` の区別、`.meta.json`、ローカルの metadata、`--ci`、`--slug` の拒否の文を消し、canonical の今の動きを書いた。
- **到達できないコードの削除**：下の「到達の判定の結果」。`runtime/` の Python は 173 ファイル・約 44,000 行から 126 ファイル・約 28,300 行になった。
- **雛形と名前の規則**：`.md` の Scope の雛形 `templates/{initiative,epic,issue}/`（各5ファイル）と、`docs/rules/initiative/epics.md`・`docs/rules/epic/issues.md` を外した。CUE の雛形の `report.md` の前付けから `タイトル:` と `親:` を外し、写すときの除去（`strip_structure_front_matter`）と「詳細:」の書き換え（`rebase_spec_dock_links`）をやめた（作られる `report.md` は 0.4.2 と同じバイト）。canonical の作成は `artifacts.md` と `discussions.md` だけを確かめる。`domain/ids.py` から Scope の slug と英数字の題名の規則を消した（Artifact の `--slug` を確かめる `INPUT_SLUG_KEBAB_RE` と `validate_input_slug_kebab` は残す）。
- **配布資産の一覧**：`static-inventory.json` で、変えた24の資産に 0.4.2 のバイトを既知の古い版として足し、外した17の資産を `retired` にした。退役してよい場所の許可（`infra/static_assets.py`）に、この17のパスを名前で足した（接頭辞では許さない）。
- **文書**：README、`AGENTS.md`、配布する `spec-dock/docs/`（`canonical.md`、`migration.md`、`guide.md`、`reference_cli.md`（C01〜C53 に詰めた）、`reference_naming.md`、`reference_sync.md`、`reference_worktree.md`、`README.md`、`authoring/cue.md`、`overview.md`、`issue-plan.md`、`cli-redesign-guide.html`（表を `reference_cli.md` から作り直した））、`scripts/README.md`、`templates/README.md`、雛形の `.workbench/README.md`（`workbench copy` の案内をカタログの共有の説明に変えた）、配布するスキル（規則の節を Epic の10章の撤去の指示のとおりにした。grill のスキルの対象の解決を `scope show --json` にした）、リポジトリの `docs/github-issue-integration.md` と `docs/sync-aggregation.md`（統括の許可）。`migration.md` に「## 0.5.0 への更新」を足し（撤去の内容、#496、#497、上げる手順、戻し方）、「## canonical モードへの移行」を 0.4.2 と `v0.4.2` の手順書の案内（手順書の 0.3.0 は 0.4.2 と読み替える）に直し、「## schema3の旧writerから移行」を消した。
- **移行のスクリプトと従来の CI**：`scripts/migrate-to-canonical/`、`.github/scripts/specdock-ci-validate.sh` とそのテストを消し、`run.sh` の `TARGETS` から外した。I-7 の `ls-tree` の解析の重複は、`infra/committed_validation.py` が到達できなくなって消えたので、`infra/commit_tree.py` の1つになった。
- **版と dogfood**：`pyproject.toml`、`uv.lock`、版のファイルとその写しを 0.5.0 にした。作った wheel を一時の venv に入れ、その `installation update --target <この worktree> --backup-dir <一時> --yes` で spec-dock の配布資産を上げた（`succeeded`、変えた24、退役17、警告なし）。`installation update` は空のディレクトリを消さないので、空になった `spec-dock/templates/{initiative,epic,issue}/` だけを手で消した。
- **戻し方（R-440-09）**：撤去の後の戻し先を 0.4.2 にした（0.3.0 は CUE の Scope を扱えず、`v0.4.2` の手順書は I-12 の注意点を含む）。Epic の `requirement.md`、`design.md`、`plan.md`、`migration.md`、次の1手をそろえた。

## Verification

（書き直しの結果と最終品質ゲートの後に書く）

## Residual Risks / Follow-ups

（同上）
