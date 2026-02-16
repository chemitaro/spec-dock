# workflow: initiative

Initiative は「投資単位」です。  
このワークフローは、Initiative を **単独で完結**させ、後続（Epic/Issue）へ安全に分解できる状態を作ります。

関連:
- 総合: [guide.md](guide.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- GitHub 連携: [reference_github.md](reference_github.md)
- sync: [reference_sync.md](reference_sync.md)

## 1. 作成（new / import）

### 1.1 new（デフォルト: GitHub）

```bash
./spec new initiative --title "..."
```

GitHub を使わない場合:

```bash
./spec new initiative --no-github --title "..."
```

注意:
- `--title` / `--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。

### 1.2 import（既存 GitHub Issue を取り込む）

```bash
./spec import initiative <num|#num|url> --title "..."
```

注意:
- `import` の共通仕様/注意（読み取りのみ、`--title` 必須、URL は番号抽出のみ、など）は [reference_github.md](reference_github.md) を参照してください。

### 1.3 Initiative 配下で Epic を追加（wrapper）

Initiative 作成後は、対象ノード配下の wrapper で Epic を追加できます。

```bash
<initiative-dir>/epics/new-epic "..."
```

補足:
- 引数はタイトル1つのみです。
- 親が local (`init-local-*`) の場合、子も自動で local として作成されます。

## 2. 記述（requirement/design/plan）

作成後、以下のファイルを埋めます（配置は `spec-dock/initiatives/**`）。

- `requirement.md`: なぜやるか / 成功条件 / スコープ
- `design.md`: 方針 / 境界 / 依存 / リスク
- `plan.md`: 実行計画（Epic への分解を含む）
- `artifacts/`: 補足資料（調査メモ/図/ログ断片）。`_template.md` をコピーして利用する

補足:
- ノード直下や配下ディレクトリにテンプレ由来の `README.md` は生成されません。

## 3. 品質ゲート（Initiative）

最低限、以下を満たしてから次（Epic）へ進みます。

### requirement
- [ ] 背景/目的が 1〜3 行で言える
- [ ] 成功条件（観測可能な指標）がある
- [ ] スコープ（やる/やらない）が明記されている

### design
- [ ] 依存関係（組織/システム/権限/データ）が列挙されている
- [ ] リスクと打ち手が書かれている

### plan
- [ ] Epic への分解方針がある（どこで切るか）
- [ ] 大まかな順序（先にやること/後にやること）がある

## 4. 観測可能にする（validate / sync）

```bash
./spec validate
./spec sync
```

## 5. よくある失敗

- 「成功」が定義されていない（進捗が議論だけになる）
- スコープが無限に広がる（Epic/Issue が爆発する）
