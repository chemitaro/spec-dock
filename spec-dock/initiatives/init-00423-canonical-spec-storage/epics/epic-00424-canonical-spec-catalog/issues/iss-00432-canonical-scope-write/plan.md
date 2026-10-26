---
種別: 実装計画書（Issue）
ID: "iss-00432"
タイトル: "Write Scopes To GitHub In Canonical Mode"
関連GitHub: ["#432"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00432 Write Scopes To GitHub In Canonical Mode — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- **strict**（Epic の計画の選択のまま）。
- 理由：利用者の仕様のファイル（カタログ）と GitHub の構造に書く。誤ると、Issue の重複、親子や依存の取り違え、仕様の消失、保存されていない変更での Issue の完了が起きる。GitHub の書き込みは自動で巻き戻せない。
- risk factor：書き込みの結果が分からないときの扱い、書く前の確かめの抜け、`work finish` の保存の確かめ、従来の部品の写し（`work start`、Artifact）、従来モードを変えない制約（AC-15）、並行の I-11 との共有ファイルの衝突。
- 再評価の条件：C1〜C11 と I-4 の部品の公開の形を、Epic が I-5 に任せた追加のほかに変える必要が出たとき、従来のモジュールを変える必要が出たとき、Epic の文書で決まっていない判断が出たときは、統括に聞く。

## 目標

requirement.md の AC-432-01〜17 を満たす。canonical モードで、Scope を書くコマンドがすべて動き、`CANONICAL_NOT_IMPLEMENTED` で止まるコマンドがなくなる。

## 順序・依存

- 前提：I-1〜I-4、I-7、I-8 が `main` にある（`cee4c896b`）。
- 並行：I-11（`iss-00438`）が別のworktreeで進む。`cli/catalog.py`、`commands/canonical_dispatch.py`、コマンドの一覧のテストで衝突しうる。先に `main` に入った方を、`origin/main` のマージで取り込む（rebase しない）。
- この Issue の中の順：S1（C1 と C10 の追加）→ S2（書く側の共通の部品）→ S3〜S8（コマンド。S3 の後は互いに独立）→ S9（I-4 から引き継ぐ直し）→ S10（全体）。

## 実装step

テストを先に書き（`tdd`）、各 step の終わりにコミットする。

- **S0 文書**：requirement、design、plan を書き、この会話を知らないサブエージェントにレビューさせ、指摘を分析して直す（下の「文書のレビューの指摘の対応」）。
- **S1 C1 と C10 の追加**（AC-432-06、07 の単体）：`update_issue(body=…)` と読み直しの比べ方、`apply_changes_lenient`、`SnapshotStore.reflect` の飛ばしと古い扱い、`reflect_writes`。
- **S2 書く側の共通の部品**（AC-432-02、03 の土台）：`application/canonical_writes.py`、`assemble_canonical_scopes`、`require_writable_format`、`domain/canonical_scaffold.py`、`infra/canonical_scaffold.py`、新しいコード。CLI のテストの部品（書き込みの時計、束の読み取り）を `tests/support/canonical_writes.py` に置く。
- **S3 作成と取り込み**（AC-432-01、03、04、05）：`scope create`（3つの種類）、`scope import github`。
- **S4 題名、移動、完了、再開**（AC-432-01、07、09）：`scope edit`、`scope move`（`cli/catalog.py` の葉、配布資産の `reference_cli.md` と `static-inventory.json`、版3の振り分けを含む）、`scope close`、`scope reopen`。
- **S5 削除**（AC-432-10）：`scope delete`。
- **S6 依存と Artifact**（AC-432-08、11）：`dependency add`、`dependency remove`、`artifact create`、`artifact import file`。
- **S7 作業の開始**（AC-432-12）：`work start`。
- **S8 作業の終了**（AC-432-13）：`work finish`。
- **S9 I-4 から引き継ぐ直し**（AC-432-14）：ブランチの再観察、`--expect-current`、`worktree remove` とリンク。
- **S10 全体**（AC-432-15〜17）：`CANONICAL_NOT_IMPLEMENTED` が残らないことのテスト、`make lint`、`uv run pytest`。`git diff origin/main -- tests/` で変えた既存のテストを一覧にし、許された区分のほかにないことを確かめる。従来のモジュールに差分がないことを確かめる。
- **S11 実装のレビュー**：`code-review` の観点で、規約と仕様を、独立した2つのサブエージェントにレビューさせ、指摘を `analyze-review-findings` で分析して直す。
- **S12 最終品質ゲート**：`origin/main` をマージし、すべてをコミットして通常の push をし、その SHA で `make lint` と `uv run pytest`、新しい2つのサブエージェントのレビュー（規約と仕様）。指摘を直したら、新しい SHA でやり直す（2回目以降のレビューは、前のゲートの SHA からの差分と、前の指摘の確かめに絞る）。
- **S13 実機の確かめ、報告、PR**：`design.md` の testability の実機の確かめ、`report.md`、`github-pr-creator` で PR、`github-pr-checks` で CI。マージはしない。`work finish` は実行しない。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-432-01〜05、07〜12、14、15 | `tests/cli_runtime/test_issue432_*.py`。一時の bare とクローン、`canonical link`、偽の `gh`（書き込みの順、本文、id、条件付きの要求、読み直しを記録で）、一時の状態の置き場、変更の束の JSON |
| AC-432-06 | `tests/unit/domain/test_canonical_structure.py` と `tests/unit/infra/test_github_snapshot.py` に足すテストと、CLI のテスト（相手がスナップショットにない依存の追加） |
| AC-432-07 の読み直し | `tests/unit/infra/test_github_structure.py` に足すテスト（応答を失わせた `PATCH` と、違う `state_reason`） |
| AC-432-13 | `tests/cli_runtime/test_issue432_work_finish.py`。bare のリモート、偽のスケジューラーの `on_kick` での1周期、注入した時計 |
| AC-432-16 | 版3の振る舞いのテストが変更なしで通る。版3の `scope move` のテスト。`git diff --name-only origin/main -- src/` が、`design.md` の「置き場」の表のファイルだけである |
| AC-432-17 | `make lint`、`uv run pytest` |

- 主な negative test：GitHub につながらない（書き込みとカタログの変化がない）、`--offline`、スナップショットにない古い状態が読み直しで見つかる、リンクなし、形式の版、作成の後の sub-issue の失敗、作成の応答の消失、カタログの排他が取れない、循環、違う親の取り込み、基点に仕様、`BLOCKED`、`UNKNOWN`、`DOING`、印の失敗、保留、時間切れ、一時停止、`--expect-current` の後の選択の変化、無視されたファイル。
- 外部依存：本物の GitHub は使わない（偽の `gh`）。実機の確かめは、wheel を入れた一時の venv と、一時の bare とクローンと偽の `gh` で行う（`design.md` の testability）。
- security / privacy / operability：新しい秘密情報の扱いはない。`gh` の資格情報は、今と同じく `gh` に任せる。`work finish` は最大180秒待つ（端末に、待っていることを示す必要はない。JSON の結果で示す）。

## rollback

- PR を `git revert` する。版4のリポジトリは I-10 まで利用者の環境にないので、利用者の運用への影響はない。データの移行はない（N/A）。

## exit / handoff

- **完了**：AC-432-01〜17 を満たし、最終品質ゲートに通り、PR がマージできる状態。マージの後に統括の指示で `work finish`。
- **I-6 への引き渡し**：題名と slug の規則を入れる場所（`canonical_scope_create` の `resolve_input_title_and_slug` の呼び出しと、`canonical_scope_change.edit_scope` の題名の確かめ）。
- **I-9 への申し送り**：`scope move` の文書（`help`、参照の文書、使い方）、新しいコード（`SCOPE_IN_PROGRESS`、`CANONICAL_PROGRESS_MARK_FAILED`、`SCOPE_MOVE_INCOMPLETE`、`DESCENDANT_STATUS_UNKNOWN`）の Epic の12章と文書への追記、選択を持つworktreeの `worktree remove` には今と同じく `--discard-ignored` が要ること、`SCOPE_IN_PROGRESS` でエージェントが利用者に確かめる規則（統括の判断 Q1）、`work finish` が最大180秒待つこと、`worktree remove` がリンクだけなら `--discard-ignored` なしで消すこと。
- **統括へ**：Epic の5章の `--save-timeout` の記述の直し（統括の判断 Q2）、Epic の12章への新しいコードの追記と、`CANONICAL_SAVE_UNCONFIRMED`（束を書いていないときの3）と `CANONICAL_SAVE_HELD`（待つ間に現れたときの6）の終了コードの違い、`scope delete` の順（バックアップ → 選択 → ディレクトリ → GitHub。やり直せるようにするため）、`--expect-current` の残る窓（Q3）。
- 残るリスクは `report.md` に書く。

## 統括の判断（2026-10-26、Orca の `ask` の答え）

統括は、この答えを Epic の文書より優先する正本とする。この Issue は Epic の文書を変えない。

- **Q1 `work start` と作業中の印（DOING）**：止めずに警告 `SCOPE_IN_PROGRESS` を返して進める。同じクローンの二重の選択は従来どおり `SCOPE_ALREADY_SELECTED` で止まる。`BLOCKED`、`UNKNOWN`、`DONE` は `READINESS_NOT_SATISFIED` で止まる。警告の `details` に、作業中の印を付けた担当者（`assignees`）と、分かれば印を付けた時刻を入れ、次の1手は「別のPCで作業中でないか利用者に確かめる。古い印なら `spec-dock work finish` か GitHub でラベルを外す」とする。エージェントがこの警告で利用者に確かめることは、I-9 の規則の節に書く。
- **Q2 `work finish` の `--save-timeout`**：足さず、180秒の固定にする。テストでは待ち時間を注入する。理由：`work finish` の引数の解析は版3と共有で、足すと版3の `--help` に使えない引数が出る。従来モードの表面を変えないほうを選ぶ。Epic の5章の `--save-timeout` の記述は、統括が直す。
- **Q3 `--expect-current` の競合（I-4 の ST-3）**：`worktree remove` と `worktree bootstrap` は、従来の内側の関数（`_remove_captured_worktree`、`_bootstrap_captured_target`）を、canonical で取り込んで確かめた同じ記録で呼ぶ。`worktree create` と `installation` の `--expect-current` は、従来の処理を呼ぶ直前に記録を読み直して一致を確かめ、docstring を実際の保証に直し、残る狭い窓を `report.md` に書く。従来のコードは変えない。
- **Q4 `worktree remove` とリンク**：無視されたものが正しいリンクだけなら、`--discard-ignored` なしで消す。ほかが1つでもあれば従来どおり求める。確かめから `git worktree remove` までの短い窓は、従来の `--discard-ignored` と同じ種類として `report.md` に書く。
- **参考の2つ**：`scope delete` は、バックアップを GitHub への書き込みより先に行う。`scope import github` の `--title` は、印も `--slug` もないときの slug の材料にだけ使い、GitHub の題名は変えない。

## 文書のレビューの指摘の対応（S0、2026-10-26）

この会話を知らないサブエージェント1つ。blocker 0、major 7、minor 14。すべて根拠を確かめて妥当と判断し、Epic の契約と統括の判断の範囲で直した（新しく統括の判断が要るものはなかった。`scope delete` の順は、統括の判断の「バックアップが先」を、やり直せる順にさらに進めたもので、報告で伝える）。

| 指摘 | 対応 |
|---|---|
| D-1 作業中の印があると前提の未完了を見落とす | `ready` が真のときだけ進む（R-432-11、design、AC-432-12） |
| D-2 読み直しが親子と依存を新しくしない | `scope move` は `get_parent`、依存は `list_blocked_by` を読み直し、`scope delete` は全体を取り直す（R-432-01、design の表、AC-432-02） |
| D-3 ディレクトリがないと保存の確かめを飛ばす | 飛ばさない。消えた場所は束の `deletions` に入れて待つ（R-432-12、design、AC-432-13） |
| D-4 待った後に古い値で閉じる | 閉じる前に `decision` と読み直しで確かめ直す（R-432-12、design、AC-432-13） |
| D-5 ラベルを外した後の失敗でやり直せない | 順をバックアップ → 選択 → ディレクトリ → GitHub にし、同じコマンドで続きから整う（R-432-08、design、AC-432-10） |
| D-6 取り込みの次の1手が実行できない | 次の1手を直した（R-432-04、design） |
| D-7 別のリポジトリの子を完了の判定で見落とす | `DESCENDANT_STATUS_UNKNOWN` で止まる（R-432-07、design、AC-432-07） |
| D-8 移動の後の `spec-dock/active/` | このチェックアウトは直し、ほかは警告（R-432-06、design、AC-432-09） |
| D-9 `CANONICAL_SAVE_UNCONFIRMED` は新しくない | 「新」を外し、Epic との終了コードの違いと理由を書いた（design、exit / handoff） |
| D-10 待つ条件が弱い | 毎回の読むだけの `status` と HEAD の一致、`finished_at` は待ち始めの秒より後（R-432-12、design） |
| D-11 パスの渡し方 | `pathspecs=` を使う（design） |
| D-12 古いことの印が上書きされうる | risk に書いた（まれで、30分ごとの取り直しで直る） |
| D-13 Scope でない子で毎回古くなる | Scope の子だけを反映し、古いと扱わない（design、AC-432-05） |
| D-14 印の失敗の書き込みが見えない | 警告の `details.writes` に入れる（R-432-11、design） |
| D-15 `incomplete` の終了コード | 原因に従う（design） |
| D-16 `worktree remove` の包みと `discard_ignored` | 包みを写す、`replace_namespace` で渡す、選択を持つworktreeは今と同じ（R-432-13、design） |
| D-17 従来のモジュールの差分の確かめ方 | `git diff --name-only` を置き場の表と比べる（plan、AC-432-16） |
| D-18 `@root` と `work start` のリンク | `@root` はリンクを求めない。`work start` はリンクを条件にせず、作れなければ `active` を飛ばして警告（R-432-02、R-432-11、design） |
| D-19 入れ子のずれた子孫 | 書く前に止まり `scope move` を示す（R-432-08、design、AC-432-10） |
| D-20 AC の前提と `HELP_EFFECTS` の文 | AC-432-03 に時刻の前提、AC-432-15 に Epic の文（requirement） |
| D-21 この節がない | この節を足した |
