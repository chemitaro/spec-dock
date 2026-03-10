# workflow: issue（TDD）

Issue は実装の最小単位です。
この workflow は、active issue を入口にした TDD、step review loop、docs impact、final quality gate を正本として扱います。
この workflow の品質ゲートは scope 固有の additive gate であり、`phase_*.md` の shared minimum gate 通過を前提とします。

対応 leaf skill:
- `.agents/skills/spec-dock-issue-execution/SKILL.md`

関連:
- 総合: [guide.md](guide.md)
- Epic: [workflow_epic.md](workflow_epic.md)
- ADR: [workflow_adr.md](workflow_adr.md)
- GitHub 連携: [reference_github.md](reference_github.md)
- 共通 phase playbook: [phase_requirement.md](phase_requirement.md), [phase_design.md](phase_design.md), [phase_plan.md](phase_plan.md)

## 作成と active set

```bash
./spec new issue --epic <epic-id> --title "..."
./spec new issue --no-github --epic <epic-id> --title "..."

./spec import issue <num|#num|url> --title "..." [--epic <epic-id>]

./spec active set <issue-id|github-issue-number|url>
./spec active set <issue-id|github-issue-number|url> --checkout
./spec active show
```

- `import issue` で `--epic` を省略した場合は current active から親 epic を解決する
- `active set` のデフォルトは no-checkout。ブランチ移動が必要な場合だけ `--checkout`
- 依存未解決なら `active set` は通常失敗する。確認は `./spec deps check <target> --github`
- 例外で進める場合だけ `./spec active set <target> --github --force`

## spec authoring

- active issue 配下の `requirement.md` / `design.md` / `plan.md` を埋める
- `discussions/`: `new doc {adr|disc|research|note} --issue <issue-id> --title "..."`
- shared な書き方は `phase_*.md`、Issue 固有の実行ルールはこの workflow を正本とする

## 実行 contract

- 実装前に `requirement.md` / `design.md` / `plan.md` の整合を確認し、plan upfront approval を得る
- 各 step は `Red → Green → Refactor → review → fix → re-review → report → commit/no-op` の順で進める
- `1 step = 1 つの観測可能な振る舞い` を原則にし、各 step に観測用の 1 本のコマンドを置く
- 各 step は step result approval を得てから次へ進む
- docs impact が `none` でない場合は、final quality gate の前に docs refresh / docs impact resolution step を置く
- `git diff <base>...HEAD` を見る final diff review quality gate は独立 step にし、reviewer approval まで終える

## report

- `spec-dock/active/issue/report.md` に、実行コマンド、結果、判断、想定外と対処を残す
- 1 セッション 1 追記でよいが、未来の自分と reviewer が追える粒度を保つ

## 品質ゲート

- requirement:
  - AC が観測可能
  - EC が書かれている
  - 対象外が明記されている
- design:
  - 変更点が列挙されている
  - テスト戦略がある
  - 互換 / 移行 / ロールバックが必要なら整理されている
- plan:
  - step が TDD と review loop を回せる粒度
  - docs impact / docs refresh step が必要なら入っている
  - final diff review quality gate が独立している
- report:
  - 実行コマンドと結果が残っている
  - 想定外と対処が追える

## 仕上げ

```bash
./spec validate
./spec sync --github
```
