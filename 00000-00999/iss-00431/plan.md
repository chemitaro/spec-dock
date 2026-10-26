---
種別: 実装計画書（Issue）
ID: "iss-00431"
タイトル: "Read Scopes From GitHub In Canonical Mode"
関連GitHub: ["#431"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00431 Read Scopes From GitHub In Canonical Mode — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **standard**（Epic の計画の選択のまま）。
- 理由：読むコマンドだけで、GitHub、カタログ、リポジトリに書かない（`active` のリンクと選択の記録、`branch` の参照は今と同じ書き方）。版4のリポジトリは I-10 まで利用者の環境にないので、失敗しても PR の revert で戻る。
- risk factor：着手の判定の部品は I-5 と I-11 の公開の形になる。従来の部品の再利用で、従来モードを変えない制約（AC-15）を守る必要がある。
- 再評価の条件：C1、C2、C3、C10 の公開の形を変える必要が出たとき、従来のモジュールを変える必要が出たとき、書くコマンドの範囲に踏み込むときは、統括に聞き、strict に上げるかを決める。

## 目標

requirement.md の AC-431-01〜17 を満たす。canonical モードで、Scope とその周りを読むコマンドが動き、I-5 と I-11 が着手の判定の部品を使える。

## 順序・依存

- 前提：I-1（`iss-00428`）と I-2（`iss-00429`）が `main` にある（`d5c8cc943`）。I-7（`iss-00434`）も `main` にある。
- 並行：I-3（`iss-00430`）と I-8（`iss-00435`）が別のworktreeで進む。`cli/catalog.py`、`commands/canonical_dispatch.py`、`application/canonical_status.py`、コマンドの一覧のテストで衝突しうる。先に `main` に入った方を、`origin/main` のマージで取り込む（rebase しない）。
- この Issue の中の順：S1（直しと部品）→ S2（共通の部品）→ S3〜S7（コマンド。互いに独立）→ S8（全体）。

## 実装step

テストを先に書き（`tdd`）、各 step の終わりにコミットする。

- **S0 文書**：requirement、design、plan を書き、この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す（下の「文書のレビューの指摘の対応」）。
- **S1 I-1 から引き継ぐ直し**（AC-431-16）：`_rate_limit_wait(...) or 60.0` を `is None` に直すテスト、`github_error_result` と dispatch のテスト、`probe.json` の書き込みの失敗のテストの直し。
- **S2 着手の判定の部品**（AC-431-06）：`domain/canonical_readiness.py` を、`StructureSnapshot` を直接作る単体のテストで作る。
- **S3 共通の部品と表示**（AC-431-01〜04、14）：`application/canonical_scopes.py`（スナップショット、`ScopeView`、ディレクトリ、`payload`、`--expect-current`）、`scope show`、`scope list`。CLI のテストの部品（カタログ、Scope のディレクトリ、偽の `gh`、`origin` の付け替え）を `tests/support/canonical_scopes.py` に置く。
- **S4 依存と選択と Artifact**（AC-431-05、07、08）：`dependency list`、`dependency check`（`--source` の既定の変更と、従来モードの回帰のテストを含む）、`active show`、`active set`、`active clear`、`artifact list`、`artifact show`。
- **S5 ブランチ**（AC-431-09）：`branch show`、`branch create`、`branch switch`、`CANONICAL_BASE_HAS_SPECS`。
- **S6 worktree と workbench と installation**（AC-431-10）：`worktree list`、`show`、`remove`、`bootstrap`、`create --expect-current`、`workbench copy`、版4の `installation … --expect-current`。
- **S7 workspace と status**（AC-431-11〜13）：`workspace validate`（各検査を1つずつ作った異常で）、`workspace sync`、`workspace doctor`、`canonical status --structure`。
- **S8 全体**（AC-431-14、15、17）：読むだけの確かめ、`make lint`、`uv run pytest`。`git diff origin/main -- tests/` で変えた既存のテストを一覧にし、許された区分のほかにないことを確かめる。`CANONICAL_NOT_IMPLEMENTED` が I-5 の書くコマンドだけに残ることを、コマンドの一覧のテストで確かめる。
- **S9 実装のレビュー**：`code-review` の観点で、規約と仕様を、独立した2つのサブエージェントにレビューさせ、指摘を `analyze-review-findings` で分析して直す。
- **S10 最終品質ゲート**：`origin/main` をマージし、すべてをコミットして通常の push をし、その SHA で `make lint` と `uv run pytest`、新しい2つのサブエージェントのレビュー（規約と仕様）。指摘を直したら、新しい SHA でやり直す。
- **S11 報告と PR**：`report.md` を書き、`github-pr-creator` で PR を作り、`github-pr-checks` で CI を確かめる。マージはしない。`work finish` は実行しない。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-431-01〜05、07〜13 | `tests/cli_runtime/test_issue431_*.py`。一時の bare とクローン、`canonical link`、偽の `gh`、一時の状態の置き場 |
| AC-431-06 | `tests/unit/domain/test_canonical_readiness.py` |
| AC-431-14 | 各読むコマンドの前後の `tree_digest`（カタログ、`.git`）、`git status`、偽の `gh` の書き込みの要求が0件 |
| AC-431-15 | 版3の振る舞いのテストが変更なしで通る。`--source` の既定の回帰のテスト（版3の作り物で、値、`--help`、JSON） |
| AC-431-16 | S1 のテスト |
| AC-431-17 | `make lint`、`uv run pytest` |

- 主な negative test：リンクなし、GitHub につながらない（スナップショットのあり／なし）、明示の `--source local`、`--ci`、カタログの `worktree remove`、`workbench copy`、仕様のある基点のブランチ、選択の不一致の `--expect-current`、ディレクトリのない Scope。
- 外部依存：本物の GitHub は使わない（偽の `gh`）。実機の確かめは、wheel を入れた一時の venv と偽の `gh` で、主なコマンドを一時ディレクトリで動かす（`design.md` の testability）。
- security / privacy / operability：新しい秘密情報の扱いはない。`gh` の資格情報は、今と同じく `gh` に任せる。読むだけのコマンドは状態の置き場のスナップショットだけを書く（運用で消してよいキャッシュ）。

## rollback

- PR を `git revert` する。版4のリポジトリは I-10 まで利用者の環境にないので、利用者の運用への影響はない。データの移行はない（N/A）。

## exit / handoff

- **完了**：AC-431-01〜17 を満たし、最終品質ゲートに通り、PR がマージできる状態。マージの後に統括の指示で `work finish`。
- **I-5 への引き渡し**：着手の判定の部品（`evaluate_readiness`）、読む側の共通の部品（`load_canonical_scopes`、`check_canonical_expectation`）、`CANONICAL_BASE_HAS_SPECS` の定数と次の1手。`work start` が `DOING` を拒むかは I-5 が決める。
- **I-11 への引き渡し**：`evaluate_all` と、理由の一覧。配下からの集計は epic-00427。
- **I-9 への申し送り**：`dependency check` と `workspace sync` の `--source` の既定の意味（canonical ではスナップショット）、`--offline` の意味（スナップショットだけで示す）、`canonical status --structure`、Epic の12章にない新しいコード（`DEPENDENCY_NOT_IN_SNAPSHOT`、`READINESS_UNKNOWN`、`SCOPE_DIRECTORY_SLUG_MISMATCH`、`SCOPE_DIRECTORY_DUPLICATE`、`SCOPE_DIRECTORY_MISSING`、`SCOPE_DIRECTORY_MISPLACED`、`SCOPE_ISSUE_MISSING`、`SCOPE_DOCUMENT_MISSING`、`SCOPE_METADATA_PRESENT`、`CANONICAL_CONFLICT_COPY`、`DEPENDENCY_NOT_SCOPE`）を、`help` と参照の文書と Epic の12章の表に書く。
- **I-1 の report の P3 の指摘**：Epic の計画は「触れるコードにあるものは直してよい」とする。この Issue は `infra/github_structure.py` の GraphQL のレート制限の1か所（必須の直し）だけを触るので、ほかの P3 は直さず、I-1 の report の一覧に残す。
- 残るリスクは `report.md` に書く。

## 統括の判断（2026-10-26、Orca の `ask` の答え）

統括は、この答えを Epic の文書より優先する正本とする。この Issue は Epic の文書を変えない。

- **Q1 `--source` の既定**：canonical で引数なしはスナップショット（`display`）、明示の `--source local` だけ `CANONICAL_NOT_APPLICABLE`、`--source github` は全体の取り直し。パーサーの既定を None にする変更で、従来モードの値、`--help` の文、JSON の出力が変わらないことをテストで確かめる（版3の振る舞いのテストは変えない）。
- **Q2 着手の判定の部品**：状態の優先は `DONE` > `UNKNOWN` > `DOING` > `BLOCKED` > `READY`、`ready` は `DOING` を見ない。部品の結果に、止めている理由（ブロッカーの Scope と、Scope でない Issue の番号）と `UNKNOWN` の理由（異常のコード）を一覧で持たせる。epic-00427 のダッシュボードが「なぜ止まっているか」を示し、Epic と Initiative の状態を配下から集めるのに使うため。配下からの集計そのものは作らない（epic-00427 の範囲）。公開の形は Issue の `design.md` に書く。
- **Q3 `branch create` / `switch`**：従来の `.meta.json` の照合をやめ、対象のコミットのツリーに `spec-dock/initiatives` があれば `CANONICAL_BASE_HAS_SPECS`（Epic の12章の既存のコードと次の1手）で止める。定数は I-4 が `canonical_errors` に置き、I-5 が使う。

## 文書のレビューの指摘の対応（S0、2026-10-26）

この会話を知らないサブエージェント1つ。blocker 1、major 6、minor 7。すべて根拠を確かめて妥当と判断し、Epic の契約の範囲で直した（統括の判断が要るものはなかった）。

| 指摘 | 対応 |
|---|---|
| 1 `list_artifacts` はリンクを通るパスを開けない（`O_NOFOLLOW`） | Artifact は実際のカタログのパスを同じ検査と domain の解析で読み、場所を `spec-dock/initiatives/…` で示す（design、R-431-06、AC-431-08） |
| 2 `--source` を戻す場所 | `parse_vnext` の中で戻し、canonical は `getattr(..., "source_explicit", False)` で読む（design） |
| 3 `--offline` | スナップショットだけで示し、なければ `PRECONDITION_FAILED`。`--source github --offline` は今と同じく拒否（R-431-01、AC-431-03、05） |
| 4 ディレクトリの重複で関係のない読み取りが止まる | `ambiguous` に分け、ディレクトリそのものが要るときだけ止める（design、R-431-01、AC-431-03） |
| 5 doctor がリンクを求める | 求めない。問題は `findings` と項目に示す（R-431-09、AC-431-12） |
| 6 祖先のディレクトリがないとリンクがぶら下がる | `active set` は鎖のすべてのディレクトリを先に確かめる（R-431-05、AC-431-07） |
| 7 選択の記録の作り方 | テストの部品が `WorkTargetStore` で直接書く（AC-431-07） |
| 8 変わる canonical のテスト | 区分を分けて `report.md` に一覧で書く（AC-431-15） |
| 9 状態の `unknown` | 状態の一覧と `observed_state` に足した（R-431-02、design） |
| 10 名前の衝突と `details` | `CanonicalBlocker` に改名、`READINESS_BLOCKED` と `READINESS_UNKNOWN` の `details` を決めた（design） |
| 11 `--view`、`--allow-invalid`、カタログの bootstrap | `--view` は文字の出力だけ、`--allow-invalid` は今と同じく結果を変えない、bootstrap はカタログを `CANONICAL_CATALOG_PROTECTED` で拒む（R-431-08、09、design） |
| 12 `structure` の項目の形 | `not_checked`、`ok`/`problem`、`unavailable` の形を決めた（R-431-10、design） |
| 13 P3 の扱いと新しいコードの申し送り | exit / handoff に書いた |
| 14 版3のworktreeの `workspace sync` | 同じく観察し、読めなければ `unavailable` の行（R-431-09、design） |

## 実装のレビューの指摘の対応（S9、2026-10-26）

対象は `d5c8cc943..f3a0568a4`。規約（ST）と仕様（SP）の、独立した2つのサブエージェントが見た。根拠をソースと再現で確かめ、判断が要るもの（ST-7、ST-8）のほかを直した。統括の指示（2026-10-26）で、ST-1〜ST-6、ST-9、SP-1〜SP-6 を直した。

| 指摘 | 判定 | 対応 |
|---|---|---|
| ST-1 / SP-1 親のある Initiative で `KeyError`（`SCOPE_NOT_FOUND` に化ける） | 妥当（high） | 入れ子の表を `SCOPE_NESTING` の1か所にし、表にない種類は飛ばす。異常は `PARENT_INVALID` で示される。テストを足した |
| ST-2 ブランチの作成と切り替えで、書いた後の確かめの失敗が効果なしになる | 妥当 | 書いた後の確かめを囲み、効果 `succeeded` の `partial`（終了コード6、`BRANCH_VERIFICATION_FAILED` / `CHECKOUT_VERIFICATION_FAILED`。従来と同じ）。作成の後の選択の確かめも戻した。テストを足した |
| ST-3 / SP-3 doctor が GitHub 以外の失敗で止まる | 妥当 | `ValueError`、`GitProcessError`、`OSError` も `findings` と `unverified` にする。テストを足した |
| ST-4 `active clear` が構造なしで観察し、正しい選択を `stale` と示す | 妥当 | 観察のときに構造を読む（読めなければ従来どおり空）。テストを足した |
| ST-5 status の docstring、`--structure` の I/O の失敗 | 妥当 | docstring を直し、`OSError`、`RuntimeError` も項目の `unavailable` にする |
| SP-4 `--structure` に `--offline` が渡らない | 妥当 | `status_of` から `structure_item` まで渡す |
| ST-6 / SP-5 カタログの判定の重複、`show` の2回の解決、`remove` の選択の取り込み | 妥当 | `catalog_at` の1つにし、`show` は表示した行から判定する。`remove` と `bootstrap` は取り込んだ選択で `--expect-current` を確かめる（従来の処理は、その後に自分で取り込んだ記録の変化を見る） |
| ST-9 型と `assert` | 妥当 | 取り込んだ選択の型を `StoredSelection` にし、`assert` を明示の分岐と例外に替えた。時刻の注入は従来の sync と同じく行わない |
| SP-2 `report.md` に変えた既存のテストの一覧がない | 妥当 | S11 で書く |
| SP-6 テストの不足 | 妥当 | 読むだけの一覧に `worktree show`、版3のworktreeと読めないworktreeの観察、`installation update` / `uninstall` の `--expect-current`、異常ごとの検出（`KIND_LABEL_MULTIPLE`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`、`DEPENDENCY_FOREIGN_REPOSITORY`）を足した |
| ST-7 Artifact の走査が従来の写し | 判断（直さない） | 従来のモジュールを変えない制約（AC-15）のため。I-13 の撤去で canonical 側に寄せる。`report.md` の残るリスクに書く |
| ST-8 従来の非公開の関数への依存 | 判断（直さない） | 同じ理由。canonical の経路のテストが、シグネチャの変化を検出する |

全体のテスト（`f3a0568a4`）で、この Issue のコマンドが動くようになったために古くなった canonical のテストが3件失敗した（`test_issue429_canonical_status` の `structure`、`test_issue413_assets` の init の直後の `workspace validate`、`test_canonical_dispatch` の未実装の例）。期待を今の振る舞いに直した（`report.md` の一覧）。
