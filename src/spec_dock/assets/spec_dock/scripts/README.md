# .spec-dock/scripts

このディレクトリは、`spec-dock` が作成する補助スクリプト置き場です。

v2 では、日常運用（initiative/epic/issue/adr の作成、active 切り替え、sync/validate）は
このディレクトリ内の **ローカルスクリプト**で実行します。

- `new {initiative,epic,issue}` は **デフォルトで GitHub Issue を作成**します（`gh` が必要）。
- GitHub を使わない場合は、`--no-github` を付けて **ローカルのみ**で作成します。

## 使い方（例）

```bash
# 新規作成（デフォルト: GitHub Issue を作成して番号を ID に使う）
./.spec-dock/scripts/spec-dock new initiative --title "Auth platform"            # creates GH issue, id=init-0123
./.spec-dock/scripts/spec-dock new epic --initiative 123 --title "JWT auth"      # creates GH issue, id=epic-0124
./.spec-dock/scripts/spec-dock new issue --epic 124 --title "Add refresh token"  # creates GH issue, id=iss-0125

# ローカルのみ（GitHub を使わない）
./.spec-dock/scripts/spec-dock new initiative --no-github --title "Auth platform"            # id=init-local-0001
./.spec-dock/scripts/spec-dock new epic --no-github --initiative 1 --title "JWT auth"        # id=epic-local-0001
./.spec-dock/scripts/spec-dock new issue --no-github --epic 1 --title "Add refresh token"    # id=iss-local-0001

# 既存の GitHub Issue 番号に紐づける（新規作成しない）
./.spec-dock/scripts/spec-dock new issue --epic 124 --title "Add refresh token" --github-issue 123  # id=iss-0123
./.spec-dock/scripts/spec-dock new adr --issue iss-0123 --title "Token rotation"

# active（現在作業中）を設定
./.spec-dock/scripts/spec-dock active set --issue 0123  # also accepts iss-0123

# 状態集計を生成
./.spec-dock/scripts/spec-dock sync
./.spec-dock/scripts/spec-dock sync --github  # 追加で GitHub の状態を enrich（gh が必要）

# 構造チェック
./.spec-dock/scripts/spec-dock validate
```

## 採番ルール（ID）

- デフォルト（GitHub 使用）
  - `new {initiative,epic,issue}` は `gh issue create` を実行し、作成された Issue 番号をそのまま ID に使います（例: `iss-0123`）。
  - このモードでは `--id` は使えません（GitHub Issue 番号と一致させるため）。
- `--no-github`（ローカルのみ）
  - `*-local-*` 名前空間で自動連番します（例: `iss-local-0001`）。
  - 連番は `.spec-dock/initiatives/**/meta.json` を走査し、同じ prefix の `*-local-*` の最大値 + 1 を採番します（GitHub 番号とは衝突しません）。
- 親 ID の指定（`--initiative` / `--epic` / `--issue`）
  - 数字だけ（例: `--initiative 123`）も受け付けます。
  - 既存ノードに `init-0123` と `init-local-0123` の両方がある場合は曖昧になるため、完全な ID を指定してください。

注:
- `.spec-dock/.work/` と `.spec-dock/active/` は生成物です（git 管理しません）。
- 導入/更新（`.spec-dock/{docs,templates,scripts}` の配置）は `uvx spec-dock init/update` を使います。
