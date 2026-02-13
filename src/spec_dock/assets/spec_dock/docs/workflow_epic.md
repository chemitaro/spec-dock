# workflow: epic

Epic は「設計の背骨」です。  
このワークフローは、Epic を **単独で完結**させ、Issue を安全に分割できる状態を作ります。

関連:
- 総合: [guide.md](guide.md)
- Initiative: [workflow_initiative.md](workflow_initiative.md)
- Issue: [workflow_issue.md](workflow_issue.md)
- GitHub 連携: [reference_github.md](reference_github.md)

## 1. 作成（new / import）

Epic は必ず Initiative 配下に作成します。

### 1.1 new（デフォルト: GitHub）

```bash
./spec new epic --initiative <initiative-id> --title "..."
```

GitHub を使わない場合:

```bash
./spec new epic --no-github --initiative <initiative-id> --title "..."
```

### 1.2 import（既存 GitHub Issue を取り込む）

```bash
./spec import epic <num|#num|url> --title "..." --initiative <initiative-id>
```

注意:
- `import` は GitHub を更新しません（`gh issue view` のみ）
- URL は **番号抽出のみ**です（owner/repo は無視されます）

## 2. 記述（requirement/design/plan）

- `requirement.md`: 期待する価値 / 受け入れ条件（AC）/ 非機能（NFR）/ スコープ
- `design.md`: 変更方針 / インタフェース契約 / 移行 / 観測性 / リスク
- `plan.md`: Issue 分割（粒度）/ 依存順序 / 品質ゲート

## 3. 品質ゲート（Epic）

### requirement
- [ ] 「何を満たせば Done か」が観測可能になっている（AC/NFR）
- [ ] スコープ（やる/やらない）が明確

### design
- [ ] 契約（API/Schema/IF）が明記されている
- [ ] 移行（段階移行/互換/ロールバック）が書かれている
- [ ] 観測性（ログ/メトリクス/アラート）の方針がある

### plan
- [ ] Issue へ分割できている（各 Issue が単独で完了する粒度）
- [ ] 依存順が現実的（先に壊れるところから潰す）

## 4. 観測可能にする（validate / sync）

```bash
./spec validate
./spec sync
```

## 5. よくある失敗

- Issue へ降ろす前に “契約/移行/観測性” を書かない（後で手戻り）
- 1 Epic に詰め込みすぎて “設計” が破綻する

