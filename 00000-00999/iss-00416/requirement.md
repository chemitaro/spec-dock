---
種別: 要件定義書（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
状態: "draft"
最終更新: "2026-10-13"
親: ["epic-00080", "init-00079"]
---

# iss-00416 Restore Active Scope Links For Human Navigation — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

## 目的

人間が `spec-dock/initiatives/**` の深いツリーをたどらずに、その worktree で実施中の Initiative・Epic・Issue の `requirement.md` / `design.md` / `plan.md` をエディタやファイラーから直接開けるようにする。

そのために、worktree の直接選択（`spec-dock/.agent/work-target/`）と、そこから導出した祖先を指す閲覧用シンボリックリンク `spec-dock/active/{initiative,epic,issue}` を、選択を変える操作の結果として作り直す。リンクは閲覧用の派生物であり、選択の正本にはしない。

## 背景

- 旧 writer は `work start` / `active set` のたびに `spec-dock/active/{initiative,epic,issue}` のリンク、`*.path`、`context-pack.md` を書いていた。未選択の役割は `spec-dock/system/active-none/<role>` を指していた。
- PR #414（Issue #413、2026-10-04 マージ）のコミット `1510e37b` で `infra/active_store.py` が削除され、生成が止まった。根拠は Issue 413 設計 D-01 の技術判断「第二の閲覧状態も増やさない」と CLI 表の「資料閲覧は scope show TARGET を使う」である。利用者の確定決定（Q1〜Q8・合意1〜9）と要件（RQ/AC）には、リンク廃止の明記がない。
- 結果として、人間の閲覧手段が利用者確認なしに失われた。本 Issue はこの機能後退を修正する。
- 親 Epic #80 は、repo 内で密結合した runtime / scaffold / dogfood 契約の小さな不具合修正を扱う。本 Issue は provider 側（`src/spec_dock/`）を正本として修正し、dogfood consumer で確認する。

## 関係者と期待成果

| 関係者 | 期待成果 |
|---|---|
| 人間の利用者 | 選択中の Scope と祖先の資料を `spec-dock/active/<role>/` から開ける。 |
| agent | 選択の判定は従来どおり `active show --json` と直接記録で行い、リンクに依存しない。リンク操作の結果は JSON の effects / warnings で正直に観測できる。 |
| 既存 consumer の保守者 | 旧 `spec-dock/active/` に残るユーザー成果物や未知のファイルが壊されない。 |

## 観測可能な要件

<a id="rq-416-01"></a>
### RQ-416-01 選択に追従するリンク

- `work start` が直接選択を publish したあと、`spec-dock/active/` 配下の `initiative`、`epic`、`issue` の3つのリンクが、直接対象とその祖先の Scope ディレクトリを指す。
- 直接対象より下位の役割（例: 直接対象が Epic のときの `issue`）は、`spec-dock/system/active-none/<role>` を指す。
- リンクは相対パスで作る。worktree ディレクトリを移動しても、同じ worktree 内の対象を指す。

<a id="rq-416-02"></a>
### RQ-416-02 選択解除で fallback に戻る

- `active clear` または `work finish` が直接記録を削除したとき、3つのリンクは `spec-dock/system/active-none/<role>` を指す。
- 直接記録を削除しなかった場合、選択が残っていればリンクを変更しない。選択が元から空なら、リンクを fallback へ揃える（未選択時の修復手段）。
- `work start` が `unchanged`（同じ対象が選択済み）で終わった場合は、リンクを扱わない。修復は `active set @current` で行う。

<a id="rq-416-03"></a>
### RQ-416-03 リンクは正本ではない

- 選択の判定、祖先の導出、`--expect-current` などの guard は、リンクを読まない。
- リンクが欠けている、古い、壊れている場合でも、`active show` などの読み取りコマンドの結果は変わらない。読み取りコマンドはリンクを書かない。

<a id="rq-416-04"></a>
### RQ-416-04 結果の正直な報告

- リンク更新の計画・結果は、JSON 出力から観測できる。`--dry-run` では書かずに計画だけを示す。
- リンク更新に失敗しても、すでに成功した選択の変更は取り消さない。失敗は warning として出力に残り、exit は選択の結果で決まる（Q1）。

<a id="rq-416-05"></a>
### RQ-416-05 既存ファイルの保全

- SpecDock がリンクとして書くのは `spec-dock/active/` 直下の `initiative`、`epic`、`issue` の3つの名前だけとする。
- その名前に既存のシンボリックリンクがあれば置き換える。実体のファイルやディレクトリがあれば変更せず、その役割を更新しなかったことを報告する。
- 旧 writer が生成した既知の名前（`context-pack.md`、`current-runbook.json`、`current-runbook.md`、`initiative.path`、`epic.path`、`issue.path`）は、リンクを同期するときに削除する。現行は更新しないため、残すと古い内容を誤読させる。ただし通常ファイルまたはシンボリックリンクの場合だけ削除し、ディレクトリの場合は変更せずに報告する。中身は読まない。
- 上記9つ以外の名前（利用者のファイルなど）は読まず、変更も削除もしない。
- `spec-dock/active` 自体がシンボリックリンクまたはディレクトリ以外の場合は、何も書かず、何も削除せずに報告する。
- `spec-dock/active/` 配下が Git に無視されない場合（`.gitignore` の改変など）や、配下に Git で追跡されたファイルがある場合は、worktree を dirty にしないため、何も書かず、何も削除せずに報告する。
- 検査の後で `spec-dock/active` が別の場所への symlink に差し替えられても、書込・削除は検査したディレクトリの中だけで行い、外部に及ばない。
- 同じ clone で `work start` が実行中（Start lock 保持中）の場合、リンクの書込・削除は行わず報告する。選択コマンドは Start lock を待たない。変更が不要なときは Start lock に触れない。
- 役割名の確認後に別の writer が実体を置いた場合も、その実体を置換・削除しない。

<a id="rq-416-06"></a>
### RQ-416-06 案内文書の整合

- `system/README.md` と `system/active-none/README.md` の provider 資産は、リンクを「現在の選択の閲覧用派生物」と説明し、正本は `active show --json` と直接記録であることを維持する。
- `active set` の catalog 説明と installed skill `spec-dock` は、同じ直接対象でリンクを修復することと、リンクが正本ではないことを含める。
- 使われていない旧テキスト renderer（`presentation/cli_text.py` の `render_active_show_text` と、それに付随する `active set <target>` の旧案内）を除去するか、現行契約に揃える。

## スコープ

対象:

- `work start`、`work finish`、`active clear` の後段と、`active set @current` でのリンク生成・更新と旧生成物の削除。
- リンク書込を担う infra adapter と、その呼び出し。
- 上記の tests、provider 資産の文書、dogfood consumer での確認。

対象外:

- 旧 `*.path`、`context-pack.md`、`current-runbook.*` の生成の復活（削除のみ行う）。
- 選択モデル（1 worktree に直接対象1件、Start だけの排他、台帳・cache・journal・自動 rollback なし）の変更。
- `branch switch` に追従したリンク更新（`branch switch` は直接記録を変えないため）。
- Windows 対応（Issue 413 で Linux/macOS に限定済み）。
- 旧 writer（`writer_protocol` が旧版の worktree）の挙動。

## 失敗・境界条件

- 直接記録の publish / 削除自体が失敗・unknown の場合: リンクは更新しない（`not_attempted`）。
- `spec-dock/system/active-none/<role>` が存在しない場合: その役割のリンクは作らず報告する。
- 対象の Scope ディレクトリが後から削除・移動された、または branch 切替で存在しなくなった場合: リンクは dangling になり得る。次に選択を変える操作、または `active set @current` で作り直される（Q3）。
- 同じ worktree で `active clear` と `work start` が同時に走った場合: リンクが最終的な直接記録とずれることがある。リンクは正本ではないため、修復は次の選択操作で行う。
- `spec-dock/active/` は `spec-dock/.gitignore` の `active/` で無視されている。worktree の clean 判定に影響しない。
- 旧 writer がまだ動く worktree（`writer_protocol` が旧版）では、新 writer は動かない（`require_writer`）。旧 writer が再び旧生成物を書くことは本 Issue の対象外。

## 受け入れ条件

- **AC-416-01** — Issue を `work start` すると、`active/initiative`、`active/epic`、`active/issue` がそれぞれ祖先 Initiative、祖先 Epic、対象 Issue のディレクトリを相対リンクで指し、`active/issue/requirement.md` を開ける。
- **AC-416-02** — Epic または Initiative を直接対象にすると、下位の役割は `system/active-none/<role>` を指す。
- **AC-416-03** — `active clear` と、直接記録を削除した `work finish` のあと、3つのリンクが `system/active-none/<role>` を指す。選択が残る `unchanged` ではリンクが変わらない。選択が空の状態の `active clear` は、古いリンクを fallback へ直す。
- **AC-416-04** — `work start`、`work finish`、`active clear`、`active set` の `--dry-run` は、リンクを書かず旧生成物も削除せず、計画を出力に含める。
- **AC-416-05** — 旧 consumer の `active/` で、リンクを同期する操作のあと、既知の旧生成物（通常ファイル・シンボリックリンク）は削除され、その旨が effects に出る。未知の名前のファイルとディレクトリ、旧生成物と同名のディレクトリ、役割名の実体はバイト列が変わらず、変更しなかった旨が出力に出る。`active` 自体がシンボリックリンクなら何も書かず、何も削除しない。
- **AC-416-06** — リンク更新の失敗は、成功した選択の変更を取り消さず、出力に残る。
- **AC-416-07** — `active show` などの読み取りコマンドはリンクを書かず、リンクの有無・内容で結果が変わらない。
- **AC-416-08** — `make lint`、`uv run pytest`、fresh wheel の外部 console で上記を確認できる。

## 制約・前提

- Issue 413 の確定事項（直接記録が唯一の正本、Start だけの短い排他、台帳・cache・永続 journal・自動 rollback・daemon を追加しない）を守る。
- 祖先は直接記録と Scope metadata から必要時に導出する（`worktree_observation.ancestors_for`）。
- 旧実装（`git show 1510e37b^:src/spec_dock/runtime/infra/active_store.py`）の multifile transaction や snapshot/restore は戻さない。
- CLI の 44 leaf 契約は変えない。
- AC-413-36（旧 `active/` の保全）は、本 Issue で「既知の旧生成物6件は削除、それ以外は保全」に変更する（利用者決定 Q4、2026-10-13）。

## 利用者決定（2026-10-13）

| ID | 論点 | 決定 |
|---|---|---|
| Q1 | リンク更新に失敗したときの結果 | 選択の結果で status / exit を決め、リンクの失敗は warning として報告する（exit 0）。 |
| Q2 | 未選択時の placeholder | `system/active-none/<role>` を指すリンクを復活する（旧挙動と同じ）。 |
| Q3 | 古い・欠けたリンクの修復手段 | 新しい leaf は追加せず、`active set @current`（同じ直接対象）でリンクだけを修復する。 |
| Q4 | 旧 consumer に残る旧 writer の生成物 | 既知の旧生成物（6件）は削除する。それ以外は触れない。 |
