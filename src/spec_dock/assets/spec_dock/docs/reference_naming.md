# reference: naming（`--title` / `--slug` / branch）

このドキュメントは、spec-dock が扱う **命名**（title/slug と、checkout 後のブランチ名）をまとめた参照です。

関連:
- 入口: [README.md](README.md)
- GitHub 連携: [reference_github.md](reference_github.md)

---

## 1. 対象（どのコマンドに効くか）

### 1.1 `--title` / `--slug` の入力制約があるコマンド

- `new {initiative,epic,issue}`
- `import {initiative,epic,issue}`

補足:
- `new adr` はこの制約対象ではありません（ADR は title/slug ルールが別です）。

### 1.2 ブランチ命名（checkout 後の正規化）が効くコマンド

- `active set <target> --checkout`
  - デフォルト（`active set <target>`）は no-checkout のため、ブランチ操作は行いません

---

## 2. `--title`（ASCII 制約）

`new/import {initiative,epic,issue}` の `--title` は、**trim 後**に次を満たす必要があります。

- 正規表現: `^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$`
- 意味: 「英数字トークンを **半角スペース 1 個**で区切った列」

許可:
- 英字（`A-Z` / `a-z`）
- 数字（`0-9`）
- 区切り（半角スペース 1 個）

不許可（例）:
- 日本語などの非 ASCII（例: `トークン追加`）
- 記号（例: `Add-Token`, `Fix: token`, `foo/bar`）
- 連続スペース / 全角スペース（例: `Add  Token`, `Add　Token`）

保存:
- 保存される title は **trim 後の文字列**です（先頭/末尾の空白は保存しません）。

目的:
- title から slug を決定的に生成できるようにし、パス/ブランチ名を安全に保つためです。

---

## 3. `--slug`（kebab-case 制約）

`new/import {initiative,epic,issue}` の `--slug` は、**trim 後**に次を満たす必要があります。

- 正規表現: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
- 意味: 「小文字英数字トークンを `-` で区切った列（kebab-case）」

許可（例）:
- `add-refresh-token`
- `jwt-auth`
- `oauth2`

不許可（例）:
- 大文字（例: `Add-token`）
- アンダースコア/スペース（例: `add_refresh_token`, `add refresh token`）
- 連続/前後のハイフン（例: `add--token`, `-add-token`, `add-token-`）

### 3.1 `--slug` を省略した場合（title → slug 合成）

`--slug` を省略した場合、slug は title から自動生成されます。

- ルール: `slug = lower(title).replace(" ", "-")`

（title 側が ASCII + 半角スペース 1 個区切りに制約されているため、決定的に kebab-case 化できます）

---

## 4. `active set --checkout` のブランチ命名（日本語ブランチを避ける）

### 4.1 目的

`active set --checkout` では、ブランチ名を **ASCII かつ git 的に妥当**な形式へ寄せます。  
これにより、非ASCII名や不正ref名による運用トラブルを避けます。

### 4.2 対象

- `active set <target> --checkout` を明示した場合のみ
- target の node 種別（initiative / epic / issue）や GitHub 紐づき有無は問いません
- `--checkout` を付けない場合は **ブランチ操作しません**

### 4.3 望ましいブランチ名（desired）

基本:
- desired = `<id>-<slug>`
  - 例: `iss-00123-add-refresh-token`

フォールバック:
- `<id>-<slug>` が次のいずれかに該当する場合、desired は `<id>` にフォールバックします
  - **非 ASCII**（`isascii()` 相当で判定）
  - `git check-ref-format --branch` を満たさない

### 4.4 既存ブランチがある場合（衝突）

desired ブランチが既に存在する場合:
- 既存ブランチを checkout して **再利用**します（上書き/削除/強制更新はしません）
- stderr に warning を出します（例: `spec-dock: (warn) branch already exists; reusing existing branch; content is not verified`）

desired ブランチが存在しない場合:
- `git checkout -b <desired>` で新規作成して checkout します

補足:
- `active` の解決は checkout 前に確定しており、checkout 後に node を再解決しません
- spec-dock は `git branch -D` / `git reset --hard` / `git checkout -B` / `git branch -M` 等の破壊的/強制操作は行いません

### 4.5 警告（stderr）の安定トークン

warning は stderr に `spec-dock: (warn)` プレフィクスで出力されます。  
運用/テストでは全文一致ではなく、このプレフィクスやキーフレーズ（例: `fallback to id`, `reusing existing branch`）の **包含**で検証するのが安全です。
