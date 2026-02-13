# workflow: issue（TDD）

Issue は「実装の最小単位」です。  
このワークフローは、active issue を入口に **Red→Green→Refactor** を回し、Issue を単独完結させます。

関連:
- 総合: [guide.md](guide.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- ADR: [workflow_adr.md](workflow_adr.md)
- GitHub 連携: [reference_github.md](reference_github.md)

## 1. 作成（new / import）

Issue は必ず Epic 配下に作成します。

### 1.1 new（デフォルト: GitHub）

```bash
./spec new issue --epic <epic-id> --title "..."
```

GitHub を使わない場合:

```bash
./spec new issue --no-github --epic <epic-id> --title "..."
```

### 1.2 import（既存 GitHub Issue を取り込む）

```bash
./spec import issue <num|#num|url> --title "..." --epic <epic-id>
```

注意:
- `import` は GitHub を更新しません（`gh issue view` のみ）
- `--title` は必須です（GitHub title は取り込みません）
- URL は **番号抽出のみ**です（owner/repo は無視されます）

## 2. active set（作業対象を固定する）

```bash
./spec active set <issue-id|github-issue-number|url>
./spec active show
```

すると `spec-dock/active/context-pack.md` が生成され、エージェント/人間の作業入口になります。

注意:
- 対象が GitHub 紐づき（`github.issue_number` がある）場合、`active set` は checkout を伴います（安全装置あり）。詳細は [reference_github.md](reference_github.md)。

## 3. 計画（requirement → design → plan）

active issue 配下の仕様を埋めます:

- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`

方針:
- requirement は AC/EC（観測可能な振る舞い）に落とす
- design は「何を変えるか/壊れるか/どう守るか」を先に書く
- plan は “テストで観測できる粒度” のステップに分ける

## 4. 実装（TDD: Red → Green → Refactor）

`plan.md` のステップを 1 つずつ、次の順で進めます:

1. Red: 失敗するテストを書く
2. Green: 最小の実装で通す
3. Refactor: 可読性/重複/命名を整える（テストは維持）

## 5. 記録（report.md）

作業ログ（実行したコマンド・結果・判断・差分）を `spec-dock/active/issue/report.md` に残します。  
1 セッション 1 追記で構いません（未来の自分/レビュアが追えることが目的です）。

## 6. 品質ゲート（Issue）

### requirement
- [ ] AC が箇条書きで列挙されている（観測可能）
- [ ] EC（異常系/境界）が書かれている
- [ ] 対象外（やらないこと）が明記されている

### design
- [ ] 変更点が列挙されている（ファイル/IF/データ）
- [ ] テスト戦略が書かれている（どこをどう観測するか）
- [ ] 互換/移行/ロールバックが必要なら書かれている

### plan
- [ ] ステップが Red/Green/Refactor の単位に分割されている
- [ ] 各ステップで回す “1本のコマンド” がある（例: `python -m unittest ...`）

### report
- [ ] 実行したコマンドと結果が残っている
- [ ] 想定外と対処が残っている（該当する場合）

## 7. 最後に（validate / sync）

```bash
./spec validate
./spec sync
```

