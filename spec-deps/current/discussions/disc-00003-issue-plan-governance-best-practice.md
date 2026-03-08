---
種別: disc
ID: "disc-00003"
タイトル: "issue 実装計画 governance 強化のベストプラクティス案"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-08"
親: ["iss-00016"]
関連: ["#16", "research-00002"]
---

# disc-00003 issue 実装計画 governance 強化のベストプラクティス案

## 提案の要点
- issue plan template に、**各 step 共通の review ループ** を昇格する。
- docs の陳腐化を防ぐため、**docs impact resolution step** を final gate の前に固定する。
- branch 全体の品質を担保するため、**final diff review quality gate** を最後の必須 step にする。
- 規範は docs を正本とし、template で実行形にし、skill には短い reminder だけを置く。

## 推奨する最終構成

### 1. 全ステップ共通ルール
- 各 step は `1 observable behavior` 単位で設計する
- 各 step は次を必須にする
  - 対象 AC/EC
  - 観測点 / 追加・更新テスト
  - この step で追加しないこと
  - step 末尾の review / report / commit 条件

### 2. 各 step の共通末尾
- review 依頼
- blocking 指摘の修正
- 再レビュー
- reviewer verdict 記録
- step-local テスト / quality gate
- report 更新
- step-scoped commit または no-op 記録

### 3. 終盤固定 step
- `S90 docs impact resolution`
  - docs / workflow / shipped assets / skill guidance の更新要否を確定
  - 必要なら更新、不要なら no-op を記録
- `S99 final diff review quality gate`
  - `git diff <base>...HEAD` を reviewer が確認
  - full test suite
  - packaging / shipped asset check
  - 必要な修正と再レビュー
  - approved まで反復

## 推奨 wording

### issue plan template に入れるべき実行ルール
```md
## 実行ルール（全ステップ共通） (必須)
- plan 全体は着手前に承認する。
- 各ステップは 1 つの観測可能な振る舞いを単位とする。
- 各ステップは Red → Green → Refactor → step-local quality gate → review → fix → re-review → report → commit の順で完了する。
- reviewer の blocking 指摘が残っている間は、そのステップを完了扱いにしない。
- 実差分があるステップは、承認済み状態を step-scoped commit として記録する。
- 実差分がないステップは、commit の代わりに no-op を report.md に記録する。
- docs impact を issue ごとに判定し、必要なら docs refresh step を final quality gate 前に置く。
- 最後に `git diff <base>...HEAD` を対象に final diff review quality gate を実施し、reviewer が承認するまで終了しない。
```

### 各 step の共通末尾
```md
#### ステップ末尾（省略しない） (必須)
- [ ] step diff を reviewer にレビュー依頼した
- [ ] blocking 指摘を解消した、または却下理由を report.md に記録して承認された
- [ ] reviewer verdict を report.md に記録した
- [ ] このステップの期待テスト/確認を実行し、成功した
- [ ] docs impact を更新した
- [ ] report.md にコマンド/結果/変更ファイル/レビュー結果を記録した
- [ ] 実差分がある場合は step-scoped commit を作成した
- [ ] `update_plan` を更新した
```

### docs refresh step
```md
### S90 — docs / workflow / distributed assets を現行挙動へ整合させる (条件付き必須)
- 条件: docs impact が `required`
- Given: この issue で変更した CLI / API / workflow / template / shipped asset
- When: 対象 docs と distributed docs assets を更新する
- Then: 利用者向け説明と配布物の文面が現行挙動と一致する
```

### final quality gate
```md
### S99 — final diff review quality gate を通す (必須)
- Given: このブランチの差分全体
- When: full test suite と packaging check を実行し、`git diff <base>...HEAD` を reviewer が確認する
- Then: test / packaging / docs / diff 全体で blocking finding が残っていない
```

## skill に書くべきこと
- `spec-dock-issue-execution/SKILL.md`
  - docs が SSOT であること
  - docs-impact step を飛ばさないこと
  - final quality gate を飛ばさないこと
- hub skill
  - issue work は issue-execution skill を使う、という routing だけ

## docs に書くべきこと
- `workflow_issue.md`
  - governance の正本
  - plan 承認と step 承認の違い
  - docs impact step の意味
  - final diff quality gate の意味
- `templates/issue/plan.md`
  - 実行可能な checklist
  - 予約 step の雛形

## 明確に避けるべきこと
- review を最後に 1 回だけにする
- docs refresh を毎回必須にして儀式化する
- final diff gate を feature step の一部に埋め込む
- skill に詳細な規範文書を複製する
- `1 step = exactly 1 commit` を必須化する

## ベストプラクティス提案（結論）
- **採用すべき構成**
  - `workflow_issue.md` に rules
  - `templates/issue/plan.md` に execution form
  - `spec-dock-issue-execution/SKILL.md` に short reminder
- **採用すべき運用**
  - step review approval を全 step 共通化
  - docs impact resolution を明示 step 化
  - final diff review quality gate を branch 全体で実施
- **採用すべき記録**
  - reviewer verdict を report に残す
  - no-op step も report に残す
  - base branch を plan に明示する

## 次の実装候補
- `templates/issue/plan.md` の共通ルール節追加
- `workflow_issue.md` の governance 節拡張
- `spec-dock-issue-execution/SKILL.md` の reminder 追記
