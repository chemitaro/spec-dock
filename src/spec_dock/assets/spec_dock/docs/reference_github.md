# reference: GitHub（`gh` 連携）

このドキュメントは、spec-dock が GitHub CLI（`gh`）を使う箇所と、その前提/副作用/注意点をまとめた参照です。

関連:
- 入口: [README.md](README.md)
- 総合: [guide.md](guide.md)

## 1. 前提（どのリポジトリが対象になるか）

spec-dock は `gh` 実行時に `--repo owner/repo` を指定しません。  
そのため、対象リポジトリは **`gh` の解釈**で決まります。

代表的な解決材料（`gh` 側）:
- カレントディレクトリが Git リポジトリであること
- `git remote` の URL
- 必要に応じて `GH_REPO` 等の環境変数
- `gh auth`（認証）状態

## 2. 何が GitHub を更新し、何が読み取りだけか

### 更新する（デフォルト動作）

- `new {initiative,epic,issue}`（デフォルト）は GitHub Issue を作ります
  - GitHub を使わない場合は `--no-github` を付けてください（`gh` を呼びません）

### 読み取りだけ（非交渉）

- `import {initiative,epic,issue}` は **読み取りのみ**です
  - `gh issue view` で存在確認するだけで、GitHub の Issue 本体（title/body/labels 等）を更新しません
  - ローカルにはノードを生成し、`sync --no-update-active` 相当まで実行します（active は変更しません）

## 3. `import` の URL 入力に関する注意（事故防止）

`import` は `123` / `#123` / URL を受け付けますが、URL は **番号抽出のためだけ**に使います。

重要:
- URL 内の `owner/repo` は **無視**されます
- そのため、別リポジトリの URL を貼っても「現在の `gh` が見ているリポジトリの同番号 Issue」として解釈され得ます

クロスリポジトリ対応はスキーマ拡張や安全装置が必要になるため、別案件（別ADR）です。

## 4. `active set` と checkout（安全装置）

`active set` は target を active として固定します。

- target が GitHub Issue と紐づくノード（`github.issue_number` があるノード）の場合、checkout を伴います
- 作業ツリーが dirty の場合は安全のため checkout を中断します

## 5. よくある失敗

- `gh` が未導入/未認証で `new` が失敗する → `--no-github` を付けるか、`gh auth login` 等を先に行う
- URL を貼ったのに別リポジトリの Issue が import されない → 仕様上、URL は番号抽出のみ（`owner/repo` は無視）

