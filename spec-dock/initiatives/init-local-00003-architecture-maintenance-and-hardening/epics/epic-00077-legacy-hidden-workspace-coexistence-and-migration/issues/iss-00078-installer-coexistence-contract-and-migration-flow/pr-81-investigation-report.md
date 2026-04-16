---
種別: 調査報告書
ID: "pr-81-investigation"
タイトル: "PR #81 review and ci investigation"
関連GitHub: ["#78", "#79", "#80", "PR #81"]
状態: "draft"
作成者: "codex"
最終更新: "2026-04-16"
依存: ["report.md"]
親: ["iss-00078", "epic-00077", "init-local-00003"]
---

# PR #81 調査レポート

## 概要
- 対象 PR は [PR #81](https://github.com/chemitaro/spec-dock/pull/81) `feat(spec-dock): legacy hidden workspaceの共存移行を実装`。
- 2026-04-16 時点で PR 状態は `OPEN`、`mergeStateStatus` は `UNSTABLE`。
- status checks は `CI / validate` が成功、`Provider CI / provider-tests` が失敗。
- review は `copilot-pull-request-reviewer` から inline comment 10 件で、主な指摘は doc front matter 正規化不足。

## 調査対象
- review comment の内容と件数
- GitHub Actions の失敗 workflow と失敗テスト
- CI failure が実装本体の不整合か、dogfooding snapshot の不整合か

## 調査方法
以下の GitHub CLI コマンドで PR と Actions の状態を取得した。

```bash
gh pr view 81 --repo chemitaro/spec-dock \
  --json number,title,state,mergeStateStatus,headRefOid,reviews,statusCheckRollup
gh pr view 81 --repo chemitaro/spec-dock --comments
gh api repos/chemitaro/spec-dock/pulls/81/comments
gh run list --repo chemitaro/spec-dock --limit 10 \
  --json databaseId,workflowName,event,status,conclusion,headSha,displayTitle
gh run view 24484241847 --repo chemitaro/spec-dock --log-failed
```

## PR の現状
- PR 番号: `81`
- タイトル: `feat(spec-dock): legacy hidden workspaceの共存移行を実装`
- state: `OPEN`
- mergeStateStatus: `UNSTABLE`
- head SHA: `5eb330a5eee6199277d8f102c4afeac5b9cf26c3`

## Review の調査結果

### 件数と傾向
- reviewer: `copilot-pull-request-reviewer`
- review state: `COMMENTED`
- inline comments: `10`
- 傾向:
  - ほとんどが docs front matter の placeholder を単一値に正規化してほしいという指摘
  - 実装ロジックへの重大な欠陥指摘は確認されていない

### 主な指摘内容

#### 1. front matter の `状態` が placeholder のまま
以下のファイルで `状態: "draft | approved"` のような union placeholder が残っている点が繰り返し指摘されている。

- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/requirement.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/design.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/plan.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/report.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/requirement.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/design.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/plan.md`
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/report.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/report.md`

#### 2. CLI message の軽微な文言指摘
- `src/spec_dock/cli.py`
- manual migration guidance の文中で sentence の開始が小文字 `legacy` になっており、`Legacy` に揃えた方が読みやすいという軽微指摘が 1 件あった。

### Review に関する評価
- blocking に見える実質論点は front matter hygiene が中心。
- ロジック破綻や仕様不整合の重大指摘は現時点では見つかっていない。

## CI/CD の調査結果

### Status checks
- `CI / validate`: `SUCCESS`
- `Provider CI / provider-tests`: `FAILURE`

### 失敗 workflow
- workflow: `Provider CI`
- event: `pull_request`
- run id: `24484241847`

### 失敗サマリー
- suite result: `Ran 741 tests in 345.414s`
- summary: `FAILED (failures=1)`

### failing test
- `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`

### failure の意味
この failure は、checked-in dogfooding の `.meta.json` 一覧と、`tests/test_init_update.py` 側の snapshot expectation が一致していないことを示している。

実質的には次のどちらか、または両方が起きている。

- 新規追加した `init-00079` / `epic-00080` 系の `.meta.json` path が expectation に不足している
- expectation の並びまたは集合が、現在の checked-in initiatives 構成と同期していない

### 重要な切り分け
- GitHub Actions 上では full suite 全体が崩れているのではなく、実際の failing は 1 件のみ
- 以前ローカル環境で観測した `22 failures / 1 error` とは状況が異なる
- したがって PR #81 の CI blocker は「issue-78 実装そのもの」ではなく、「dogfooding snapshot expectation の不整合」である可能性が高い

## 総合評価
PR #81 の blocking items は現時点で次の 2 点に集約できる。

1. docs front matter の `状態` を placeholder から単一値へ正規化すること
2. `tests/test_init_update.py` の checked-in dogfooding snapshot expectation を、現行 repo の checked-in nodes と再同期すること

この 2 点が解消されれば、PR は review と CI の両面でかなり前進する見込みが高い。

## 推奨アクション

### 優先度高
1. `init-00079` / `epic-00080` と関連 report の front matter `状態` を単一値へ修正する
2. `tests/test_init_update.py` の `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` を current repo state に合わせて更新する
3. `Provider CI` を再実行して、snapshot test が green に戻るか確認する

### 優先度中
1. `src/spec_dock/cli.py` の小文字始まり文言を `Legacy` へ揃える
2. review comments が解消済みかを再取得して、残件を確認する

## 補足
- このレポートは PR #81 の review / CI 状況を把握するための調査メモであり、修正実施そのものはまだ含まない。
- 実装修正に着手する場合は、本レポートの blocking items をそのまま修正計画に落とし込める。
