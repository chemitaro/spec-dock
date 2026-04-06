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
- Issue plan playbook: [phase_plan_issue.md](phase_plan_issue.md)

## 作成と active set

```bash
./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title "..."
./spec-dock/scripts/spec-dock new issue --create-github-issue --epic <epic-id> --title "..."

./spec-dock/scripts/spec-dock import issue <num|#num|canonical-url> --title "..." [--epic <epic-id>]

./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url>
./spec-dock/scripts/spec-dock active set --id <issue-id>
./spec-dock/scripts/spec-dock active set --github-issue <n>
./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url> --checkout
./spec-dock/scripts/spec-dock active show
```

- `import issue` で `--epic` を省略した場合は current active から親 epic を解決する
- `import issue` の canonical URL は current repo と照合され、current repo を検証できない場合も含めて foreign GitHub issue URL は fail-closed で reject される
- `--allow-foreign-url` は compatibility flag として残るが、cross-repo node identity import の成功経路にはならない
- canonical でない URL-like target は受け付けない
- `active set` のデフォルトは no-checkout。ブランチ移動が必要な場合だけ `--checkout`
- `active set` は `<target>` の後方互換を維持しつつ、`--id` / `--github-issue` の explicit form も使える
- 依存未解決なら `active set` は通常失敗する。確認は `./spec-dock/scripts/spec-dock deps check <target> --github`
- 例外で進める場合だけ `./spec-dock/scripts/spec-dock active set <target> --github --force`

## spec authoring

- active issue 配下の `requirement.md` / `design.md` / `plan.md` を埋める
- `discussions/`: `new doc {adr|disc|research|note} --issue <issue-id> --title "..."` で、この issue の `discussions/` 配下に timestamp-prefixed original を作成する。標準形は `<ts>-<kind>-<slug>.md`、same-second collision は `<ts>-<nn>-<kind>-<slug>.md`。詳細 contract は [reference_naming.md](reference_naming.md) を参照する
- shared な書き方は `phase_*.md`、Issue plan の構造化は `phase_plan_issue.md`、Issue 固有の実行 policy はこの workflow を正本とする

## 実行 contract

- 実装前に `requirement.md` / `design.md` / `plan.md` の整合を確認し、特に `design.md` の依存関係分析と `plan.md` の step 順が一致していることを確認して、plan upfront approval を得る
- 各 step は `Red → Green → Refactor → review → fix → re-review → report → コミット/no-op` の順で進める
- `Refactor` は Green 後の bounded decision point とし、plan では詳細 task を事前確定しない
- step 順は `design.md` の依存関係分析を根拠に、upstream / prerequisite から downstream へ組む
- cleanup が既知で大きい場合は `Green` / design / 別 step へ切り出す
- review / QA / spec の各 stage gate は `pass` まで回す
- 各 stage gate の `pass` 後は、`spec-dock/active/issue/report.md` を更新し、差分確認後に report とまとめてコミットするか no-op とするかを判断する
- `1 step = 1 つの観測可能な振る舞い` を原則にし、各 step に観測用の 1 本のコマンドを置く
- `plan.md` では TDD cycle を step / block / iteration に埋め込み、配置ルールは `phase_plan_issue.md` に従う
- 各 step は step result approval を得てから次へ進む
- docs impact が `none` でない場合は、final quality gate の前に docs refresh / docs impact resolution step を置く
- `git diff <base>...HEAD` を見る final diff review quality gate は独立 step にし、reviewer approval まで終える
- Issue work の完了条件は、active issue が確定しており、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままではなく、必要な `sync` / `validate` / review の結果または未実施理由が `report.md` に記録されていることである。
- 4 点の issue docs のいずれかがテンプレートのまま、または実質未記入の状態で残る場合は、完了扱いにしない。
- `sync` / `validate` / review を実施できない場合は、その理由、影響、次のアクションを `report.md` に残す。
- 完了条件を満たせない状態は `blocked` または `未完了` として扱い、成功報告をしてはならない。

## report

- `spec-dock/active/issue/report.md` に、実行コマンド、結果、判断、想定外と対処を残す
- stage gate ごとの reviewer verdict / test結果 / 修正内容 / no-op 理由もここに残す
- 実際に行った refactor は事前計画ではなくここに残す
- 依存関係の想定と違った実装順や refactor が必要になった場合もここに残す
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
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --github
```
