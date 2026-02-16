# workflow: ADR

ADR（Architecture Decision Record）は、意思決定を仕様（requirement/design/plan）から **切り離して**記録するための仕組みです。

関連:
- 総合: [guide.md](guide.md)
- Initiative: [workflow_initiative.md](workflow_initiative.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- Issue: [workflow_issue.md](workflow_issue.md)

## 1. いつ ADR を起こすか

次のどれかに当てはまるなら、先に ADR を作ります:

- 方針が複数ありトレードオフがある
- “やり直しコストが高い” 変更（データ/契約/公開API）
- チーム合意が必要（合意無く進めると事故る）

## 2. 作る（叩き台を先に作る）

Issue/Epic/Initiative のいずれかに紐づけて作成します。

推奨（スコープ配下の wrapper を使う）:

```bash
# issue スコープ
<issue-dir>/adrs/new-adr "..."

# epic スコープ
<epic-dir>/adrs/new-adr "..."

# initiative スコープ
<initiative-dir>/adrs/new-adr "..."
```

代替（runtime script へ直接指定）:

```bash
./spec new adr --issue <issue-id> --title "..."
# or
./spec new adr --epic <epic-id> --title "..."
# or
./spec new adr --initiative <initiative-id> --title "..."
```

生成先:
- scope ノード配下の `adrs/`（例: `.../init-.../adrs/` / `.../epic-.../adrs/` / `.../iss-.../adrs/`）

方針:
- Decision は最初は **TBD** で良い（議論の叩き台として先に置く）
- Options を列挙し、Pros/Cons を書く

## 3. 決める（Decision → accepted）

レビュー/合意後に:
- Decision を確定し、必要ならステータスを `accepted` にする
- 影響がある仕様（design/plan）へリンクして反映する

## 4. 品質ゲート（ADR）

- [ ] 問題（Context）が 1〜3 行で説明できる
- [ ] 選択肢（Options）が複数あり、それぞれ Pros/Cons がある
- [ ] Decision が明確（何を採り、何を捨てたか）
- [ ] 影響範囲（仕様/実装/移行/運用）が書かれている（必要なら）
