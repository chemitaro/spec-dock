# workflow: issue（TDD）

Issue は「実装の最小単位」です。  
このワークフローは、active issue を入口に **Red→Green→Refactor** を回し、Issue を単独完結させます。

対応 leaf skill:
- `.agents/skills/spec-dock-issue-execution/SKILL.md`

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

注意:
- `--title` / `--slug` には入力制約があります（ASCII / kebab-case）。詳細は [reference_naming.md](reference_naming.md) を参照してください。

### 1.2 import（既存 GitHub Issue を取り込む）

```bash
./spec import issue <num|#num|url> --title "..." [--epic <epic-id>]
```

注意:
- `import` の共通仕様/注意（読み取りのみ、`--title` 必須、URL は番号抽出のみ、など）は [reference_github.md](reference_github.md) を参照してください。
- `--epic` を省略すると、current active から親 epic を解決します。
  - active epic があればそれを使います。
  - active issue のみでも、そこから親 epic を解決できれば使います。

## 2. active set（作業対象を固定する）

```bash
./spec active set <issue-id|github-issue-number|url>
./spec active set <issue-id|github-issue-number|url> --checkout
./spec active show
```

すると `spec-dock/active/context-pack.md` が生成され、エージェント/人間の作業入口になります。

注意:
- `active set` のデフォルトは no-checkout（active 更新のみ）です。
- 実装作業でブランチ移動が必要な場合のみ `--checkout` を付けます（安全装置あり）。詳細は [reference_github.md](reference_github.md)。
- `active set` は依存ガードがあります。依存未解決（blocked）の場合はデフォルトで失敗します。
  - ブロッカー確認: `./spec deps check <target> --github`
  - 例外化（非推奨）: `./spec active set <target> --github --force`（または `-f`）

## 3. 計画（requirement → design → plan）

active issue 配下の仕様を埋めます:

- `spec-dock/active/issue/requirement.md`
  - 共通の進め方: [phase_requirement.md](phase_requirement.md)
- `spec-dock/active/issue/design.md`
  - 共通の進め方: [phase_design.md](phase_design.md)
- `spec-dock/active/issue/plan.md`
  - 共通の進め方: [phase_plan.md](phase_plan.md)
- `spec-dock/active/issue/discussions/`（ADR / 議論 / 調査 / メモ）
  - ADR: `./spec-dock/scripts/spec-dock new adr --issue <issue-id> --title "..."`
  - 非ADR: `spec-dock/templates/discussions/{note,disc,research}.md` をコピーして利用

方針:
- requirement は AC/EC（観測可能な振る舞い）に落とす
- design は「何を変えるか/壊れるか/どう守るか」を先に書く
- plan は “テストで観測できる粒度” のステップに分ける
- Issue 固有の観点（active issue 起点 / TDD 実行 / docs impact / final quality gate）はこの workflow に残し、ヒアリング・discussion sheet・ADR・review loop などの共通作法は各 phase playbook を正本として参照します。
- phase progression rule:
  - requirement が reviewer 承認される前に design へ進みません。
  - design が reviewer 承認される前に plan へ進みません。

## 4. 実装（TDD + review loop）

`plan.md` のステップを 1 つずつ、次の順で進めます:

1. Red: 失敗するテストを書く
2. Green: 最小の実装で通す
3. Refactor: 可読性/重複/命名を整える（テストは維持）
4. review: reviewer に step result approval を依頼する
5. fix: 指摘があれば最小差分で修正する
6. re-review: 承認レベルまで再レビューする
7. report: 実行コマンド/結果/変更ファイルを `report.md` に残す
8. commit / no-op: step-scoped commit を行う。実差分がない場合のみ no-op 理由を記録する

### 4.1 plan 承認と step result approval

- plan upfront approval:
  - 実装着手前に、`requirement.md` / `design.md` / `plan.md` の整合を確認し、作業方針として承認を得る
  - 目的は「どの順序で何を実装するか」を固定することです
- step result approval:
  - 各 step の実装結果に対して reviewer が確認する承認です
  - 目的は、次の step に欠陥やズレを持ち越さないことです

### 4.2 docs impact と docs refresh

- docs impact は、今回の差分が README / workflow / distributed docs / skill reminder の更新要否を持つかを判定するための分類です
- docs impact が `none` でない場合は、最終品質ゲートの前に docs refresh / docs impact resolution step を置きます
- docs は規範の正本です。skill は reminder なので、詳細ルールは docs 側で更新します

### 4.3 final diff review quality gate

- 最後に、`git diff <base>...HEAD` を対象に branch 全体の差分を確認します
- ここでは tests / packaging / docs / diff 全体をまとめて確認し、reviewer approval まで終える必要があります
- この最終品質ゲートは最後の feature step に埋め込まず、独立 step として置きます

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
- [ ] 各ステップに review -> fix -> re-review -> report -> commit/no-op がある
- [ ] docs impact / docs refresh step が final quality gate 前に置かれている
- [ ] final diff review quality gate が独立 step になっている

### report
- [ ] 実行したコマンドと結果が残っている
- [ ] 想定外と対処が残っている（該当する場合）

## 7. 最後に（validate / sync）

```bash
./spec validate
./spec sync --github
```
