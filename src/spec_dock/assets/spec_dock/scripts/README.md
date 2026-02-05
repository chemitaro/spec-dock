# .spec-dock/scripts

このディレクトリは、`spec-dock` が作成する補助スクリプト置き場です。

v2 では、日常運用（initiative/epic/issue/adr の作成、active 切り替え、sync/validate）は
このディレクトリ内の **ローカルスクリプト**で実行します（ネットワーク不要）。

## 使い方（例）

```bash
# 新規作成
./.spec-dock/scripts/spec-dock new initiative --title "Auth platform"
./.spec-dock/scripts/spec-dock new epic --initiative init-0001 --title "JWT auth"
./.spec-dock/scripts/spec-dock new issue --epic epic-0001 --title "Add refresh token" --github-issue 123
./.spec-dock/scripts/spec-dock new adr --issue iss-0123 --title "Token rotation"

# active（現在作業中）を設定
./.spec-dock/scripts/spec-dock active set --issue iss-0123

# 状態集計を生成
./.spec-dock/scripts/spec-dock sync
./.spec-dock/scripts/spec-dock sync --github  # 追加で GitHub の状態を enrich（gh が必要）

# 構造チェック
./.spec-dock/scripts/spec-dock validate
```

注:
- `.spec-dock/.work/` と `.spec-dock/active/` は生成物です（git 管理しません）。
- 導入/更新（`.spec-dock/{docs,templates,scripts}` の配置）は `uvx spec-dock init/update` を使います。
