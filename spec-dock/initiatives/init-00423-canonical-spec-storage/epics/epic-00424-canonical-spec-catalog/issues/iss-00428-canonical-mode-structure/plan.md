---
種別: 実装計画書（Issue）
ID: "iss-00428"
タイトル: "Add Canonical Mode And GitHub Structure Snapshot"
関連GitHub: ["#428"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00428 Add Canonical Mode And GitHub Structure Snapshot — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- 選択：`strict`（Epic の `plan.md` の指定）。
- 理由：すべてのコマンドが通る `dispatch()` と宣言の読み取りを変える。ほかのすべての Issue と次の Epic が使う契約（C1、C2、C10）と、`snapshot.json` の版1の形式を決める。誤ると、版3のリポジトリの回帰（AC-15）か、後の Issue の作り直しになる。
- risk factor：従来モードの経路の変化、配布資産の宣言の版4、GitHub の呼び出しの扱い（304、レート制限、結果が不明な書き込み）、スナップショットの重ね合わせ。
- 再評価条件：本物の GitHub への書き込み、利用者の状態の置き場への書き込み、従来の処理の変更が要るとわかったら、止まって統括に聞き、`critical` を検討する。`design.md` の testability の4件と、Epic の testability の3つの区分のほかに、版3の振る舞いを確かめるテストの変更が要るとわかったら、変えずに止まって統括に聞く。

## 目標

- `requirement.md` の AC-428-01〜12 を、テスト先行の単体テストと CLI のテスト、全体のテスト、`make lint` で満たす。
- `design.md` の公開の形（C1、C2、C10）を、後の Issue がそのまま使える状態にする。

## 順序・依存

1. 文書（この3つ）を書き、独立のレビューを受けて直す（S0）。
2. 偽の GitHub（S1）を先に作る。S3〜S5 のテストが使う。
3. 純粋な規則（S2）→ 呼び出しの部品（S3）→ スナップショット（S4）の順。S2 は S1 と並べて進めてよい。
4. モードの判定と振り分け（S5）と、`installation`（S6）は、S2〜S4 と独立している。
5. 全体の確かめ（S7）、実装のレビュー（S8）、最終の品質の関門（S9）、報告書と PR（S10）。

並行の注意：`cli/catalog.py`、`commands/runtime_dispatch.py` は、ほかの Issue も変える共有のファイルである。衝突したら `origin/main` をこのブランチにマージして解く（rebase しない）。

## 実装step

各 step は、`tdd` の Red → Green → Refactor で進め、区切りでコミットする。

- **S0 文書**：`requirement.md`、`design.md`、`plan.md` を書き、この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す。設計書で決まっていなかった判断は `ask` で統括に聞き、答え（下の「統括の判断」）を文書に入れた。
- **S1 偽の GitHub**（`tests/support/fake_github.py`）：モデル（Issue、ラベル、親子、依存、担当者、id と番号の別）、REST の各操作、GraphQL（ラベルの OR、ページ送り、`totalCount` の超過）、条件付きの要求と 304、要求の記録、`inject`（403/429 とヘッダー、500番台、時間切れ）、時計、`PATH` に置く `gh`。偽物そのものの単体テストも書く。
- **S2 構造の規則**（`domain/canonical_structure.py`）：印の読み書き（`\r\n`、途中の印、0個、2個、規則外、行頭の空白）、種類、ID、`build_snapshot`（異常の各コード、`external`、`blocking`、循環の帰属）、`to_json`/`from_json`、`apply_changes`、`merge_refresh`。
- **S3 呼び出しの部品**（`infra/github_structure.py`）：応答の解析（状態行、304 と終了コード1）、`ok` の状態コード、分類、レート制限（読み取りの待ちと3回、60秒を超える待ち、書き込みの即時の停止）、500番台の再試行、書き込みの間の1秒、GraphQL の `errors`、`fetch_structure`（ページ送り、関係の超過、ラベルの超過、別のリポジトリ）、`probe`、REST の各操作、id の送り方、404 の扱い、結果の確かめ。
- **S4 スナップショット**（`infra/state_root.py`、`infra/github_snapshot.py`）：置き場、排他、原子的な書き込み、壊れたファイルと違う版、メモリー、`ensure_fresh` の表、304 の要求の数、`ETag` を進めないこと、`merge_refresh` による取り直しの途中の反映の保護、`reread`、`refresh`。
- **S5 モードと振り分け**（`project_context.py`、`canonical_dispatch.py`、`canonical_errors.py`、`canonical_refusals.py`、`runtime_dispatch.py`）：版3/4/5/真偽値/文字列、`probe_workspace_mode`、`--ci` と `--raw` の振り分け、全コマンドの `CANONICAL_NOT_IMPLEMENTED`、`workspace migrate` の拒否、`CANONICAL_NOT_MIGRATED` の経路、リポジトリによらない入口、例外の対応。
- **S6 `installation`**：配布資産の版4と `static-inventory.json`（`sha256`、`known_old_sha256`）、`init` の警告、版4の `show`、`update`、`uninstall`、版4の `--expect-current` の止め方、ヘルプの文言。統括の判断の1に従い、`design.md` の testability の4件のテストを変える。
- **S6b 版3の出力の比較**（AC-428-16）：変更の前のコミット（`be4810244`）を一時の worktree に取り出し、版3の作り物に対する `workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update --dry-run` と適用の出力を、パスを置き換えて `tests/fixtures/issue428/legacy-outputs.json` に記録する。今のコードの出力をそれと比べるテストを足す。一時の worktree は消す。
- **S7 全体の確かめ**：`make lint`、`uv run pytest`（S6 の後に全体を動かし直す）。本物の GitHub に対して、読むだけで、全体の問い合わせと条件付きの要求が動くことを確かめる（書き込みはしない。状態の置き場は一時ディレクトリ）。
- **S8 実装のレビュー**：`code-review` の観点で、規約と仕様を、独立した2つのサブエージェントにレビューさせ、指摘を分析して直す。
- **S9 最終の品質の関門**：PR #441 のマージを確かめて `origin/main` をマージし、push した SHA で `make lint` と `uv run pytest`、新しい2つのサブエージェントのレビュー。指摘を直したら、新しい SHA でやり直す。
- **S10 報告と PR**：`report.md` を書き、`github-pr-creator` で PR を作り、`github-pr-checks` で CI を確かめる。マージはしない。`work finish` は実行しない。

## 統括の判断（2026-10-26、Orca の `ask` の答え）

統括は、この答えを Epic の文書より優先する正本とし、同じ内容を Epic の `design.md` に反映する（PR #441 の追加のコミット）。この Issue は Epic の文書を変えない。

1. **案A**：`installation init` の版4は、この Issue で入れる。`init` で作った作り物に従来のコマンドを当てるテスト（実験で4件）は、`init` の直後に宣言を版3に戻す準備の行だけを足す。確かめる中身（`assert`）は変えない。`test_issue413_assets.py` の宣言の値と init の直後の `workspace validate`（`CANONICAL_NOT_IMPLEMENTED` の確かめにする）、`test_issue413_wheel.py` の資産の値は、「配布資産の値」の許された変更として扱う。変えたテストと行と理由を `report.md` に一覧で書き、最終のレビューで確かめる中身が変わっていないことを見てもらう。
2. 版4の `installation show`、`update`、`uninstall` に `--expect-current` を付けた組み合わせだけ、この Issue では `CANONICAL_NOT_IMPLEMENTED` にする。canonical の処理は I-4 の担当。
3. 全体の問い合わせの3つの変更（`blockedBy` の要素のラベルを外す、`repository { nameWithOwner }` を足す、ラベルの `totalCount`）を了承。別のリポジトリのものは、`parent`、`sub_issues`、`blocked_by`、`blocking`、`external` のどれにも入れず、異常として記録し、テストで確かめる。実測の費用（設計どおり104点、変更の後4点）を `report.md` に書く。

実験の記録：配布資産を版4にし、版4を `CANONICAL_NOT_IMPLEMENTED` に送る一時の変更で全体を動かすと、2067件のうち4件が落ちた（ほかは通った）。一時の変更は元に戻した。この実験には `known_old_sha256`、`init` の警告、`--expect-current` の止め方、ヘルプの文言を含まないので、S6 の後に全体を動かし直し、4件のほかに落ちるテストがあれば、上の再評価条件で止まる。

### 2回目（2026-10-26、文書の独立レビューの後）

文書の独立レビューで、Epic の記述と Issue の解釈が違う点が出たので、統括に確かめた。統括は了承し、Epic の `design.md` と `plan.md` に反映する。

- **A1**：`read_workspace_declaration` は辞書のまま返し、モードは `workspace_mode` と `ProjectContext.mode` で返す。
- **A2**：要る待ちが60秒を超えるレート制限は、待たずに `GITHUB_RATE_LIMITED`（`retry_at` 付き）。`display` でスナップショットがあれば、古いもので続けて `GITHUB_SNAPSHOT_STALE`。
- **A3**：印の数え方（`design.md` 5章）。I-8 はこの規則を写す。
- **A4**：`id` のない依存先は循環の確かめに入れず、そのような依存を持つ Scope は着手できるにしない（I-4、I-11）。
- **A5**：`CANONICAL_NOT_LINKED` のコードと次の1手は、I-1 が `application/canonical_errors.py` の定数として1か所に置き、I-2 はそれを使う。
- **A6**：`resolve_state_root` は明示の上書きを受け取る。根の求め方の持ち主は I-1、登録簿、`state.json`、`--state-root` は I-3。
- **A7**：GitHub の失敗のコードは、今と同じ分類のコード（`GITHUB_ACCESS_DENIED` など）を使い、Epic の12章の表に足す。`decision` などは元のコードのまま止める。
- **B**：`resolve_context` より前に呼ぶ表（`REPOSITORY_INDEPENDENT_HANDLERS`）を C2 の公開の形にし、I-7 が `canonical check` を登録する。`canonical check` は、版3の宣言を `CANONICAL_CHECK_FAILED`（終了コード7）の1件として返す（`CANONICAL_NOT_MIGRATED` の例外）。
- **C**：版3の `installation show` が宣言を `known-old` と示すことは、配布資産の値の変化として受け入れる。条件として、版3の `workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update`（宣言を書き換えない）の結果が、変更の前と後で同じことをテストで確かめ、最終の品質の関門の SHA で `.github/scripts/specdock-ci-validate.sh` を通す（AC-428-16）。

## 検証

| 対象 | 方法 |
|---|---|
| AC-428-01（AC-15） | 変更の前の全体のテスト（2067件成功、8件スキップ。2026-10-26）と同じテストが、許された変更のほかは変更なしで通る。`git diff origin/main -- tests/` で、変えたテストを一覧にし、報告書に理由を書く |
| AC-428-02〜05 | `tests/cli_runtime/test_issue428_canonical_mode.py`、`tests/unit/commands/test_canonical_dispatch.py` |
| AC-428-06 | `tests/unit/domain/test_canonical_structure.py`、`tests/unit/infra/test_github_structure.py` |
| AC-428-07〜09 | `tests/unit/infra/test_github_snapshot.py` |
| AC-428-10〜11、13〜14 | `tests/unit/infra/test_github_structure.py` |
| AC-428-12 | `make lint`、`uv run pytest` |
| AC-428-15 | `tests/unit/infra/test_github_structure.py`、`tests/unit/infra/test_github_snapshot.py` |
| AC-428-16 | `tests/cli_runtime/test_issue428_legacy_outputs.py` と、最終の品質の関門での `.github/scripts/specdock-ci-validate.sh` |
| rollback | N/A（自動のテストはない）。理由：戻すのは PR の `git revert` で、データの移行がなく、版3のリポジトリは状態の置き場に何も作らないため。S7 の全体のテストが通れば、元のコードの振る舞いは、変更の前のテストの全体（2067件）が保っている |
| negative test | 壊れた応答、状態行のない応答、GraphQL の `errors`、PR の混入、別のリポジトリ、壊れた `snapshot.json`、違う版、権限のない置き場、排他が取れない、時間切れの書き込み |

- テストは外のネットワークを使わない。状態の置き場はいつも一時ディレクトリにする。
- security / privacy：Issue の本文は保存しない（印だけを取り出す）。トークンは扱わない（`gh` に任せる）。ログに本文を書かない。状態の置き場は利用者だけが読める `0o700` で作る。
- operability：`probe.json` の `last_error` と `FreshSnapshot.payload()` で、古いことと失敗の理由を示せる。
- migration：配布資産の宣言の版だけ。版3のリポジトリの宣言は変えない（`init_only`）。データの移行はない（N/A。スナップショットは新しい置き場に作るだけ）。

## rollback

- マージの前：ブランチを捨てるか、コミットを revert する。
- マージの後で、後の Issue（I-2 以降）がまだ C1、C2、C10 を使っていない間：PRを `git revert` する。版3のリポジトリでは canonical の処理が動かず、状態の置き場にも何も作らないので、利用者の運用に影響はない。`installation init` で版4のリポジトリを作っていた場合は、宣言を手で版3に戻す（この間に作る予定はない）。
- 後の Issue がマージされた後：I-1 だけを `git revert` で戻すことはできない（後の Issue が部品を使っているため）。forward recovery で、この部品を直す PR を作る。
- forward recovery：後の Issue が契約の不足を見つけたら、Epic の `design.md` とこの `design.md` を先に直し、この部品を直す PR を別に作る。

## exit / handoff

- 完了の条件：AC-428-01〜12 をテストで確かめ、最終の品質の関門に合格し、`report.md` に証拠を書き、PR がマージできる状態（CI が通っている）で止まる。マージは人が行い、`work finish` は統括の指示で行う。
- 後の Issue への引き渡し：`design.md` の公開の形と、偽の GitHub の使い方。I-2 は `CANONICAL_NOT_LINKED` の定数、I-3 は `ensure_fresh("cycle")`、`probe.json` の `last_error`、`FreshSnapshot.graphql_cost`、`resolve_state_root(override=…)`、`REPOSITORY_INDEPENDENT_HANDLERS`、I-4 は `display`、`refresh`、`repository_for_checkout`、I-5 は `decision`、`reread`、`reflect`、`dependency_violations` と書き込みの関数、I-7 は `REPOSITORY_INDEPENDENT_HANDLERS` を使う。
- 残るリスク：本物の GitHub での書き込みの確かめ（I-10 まで行わない）、親子と依存の変更で `updated_at` が変わるか（Epic の未確認の事項）。
