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

注意:
- `--title` / `--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。

### 1.2 import（既存 GitHub Issue を取り込む）

```bash
./spec import epic <num|#num|url> --title "..." --initiative <initiative-id>
```

注意:
- `import` の共通仕様/注意（読み取りのみ、`--title` 必須、URL は番号抽出のみ、など）は [reference_github.md](reference_github.md) を参照してください。

### 1.3 Epic 配下で Issue を追加（wrapper）

Epic 作成後は、対象ノード配下の wrapper で Issue を追加できます。

```bash
<epic-dir>/issues/new-issue "..."
```

補足:
- 引数はタイトル1つのみです。
- 親が local (`epic-local-*`) の場合、子も自動で local として作成されます。

## 2. 記述（requirement/design/plan）

- `requirement.md`: 期待する価値 / 受け入れ条件（AC）/ 非機能（NFR）/ スコープ
- `design.md`: 変更方針 / インタフェース契約 / 移行 / 観測性 / リスク
- `plan.md`: Issue 分割（粒度）/ 依存順序 / 品質ゲート
- `artifacts/`: 補足資料（調査メモ/図/ログ断片）。`_template.md` をコピーして利用する

補足:
- ノード直下や配下ディレクトリにテンプレ由来の `README.md` は生成されません。

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
