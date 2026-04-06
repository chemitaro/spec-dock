# iss-00051 手動テストにおける runtime blocker レポート

## 要約
- host-native shim 配備の install / static contract は通過した
- runtime の委譲実行検証は一部までしか完了できなかった
- end-to-end の完了を妨げた blocker は 2 件とも環境側の制約だった

## 参照
- 計画書: `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/plan.md`
- チェックリスト: `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/checklist.md`
- 実行ログ: `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/execution-log.md`
- サマリ: `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/summary.md`

## 通過した項目
- `.codex/agents/spec-dock.toml` が正しく配置され、`developer_instructions` を持っている
- `.github/agents/spec-dock.agent.md` が正しく配置され、委譲先 skill を参照している
- `.agents/host-adapters/meta.json` と delegated skill 群が正しく配置されている
- Codex native shim の discovery prompt は成功し、active target / 次に読む doc の案内を返した
- `chemitaro/spec-dock-native-shim-current-20260406` に対する GitHub seed issue の作成は成功した
- Copilot 側の static contract 確認は成功した

## blocker

### blocker 1: この環境では nested Codex runtime が shell 実行できない
- local real-work flow と GitHub-backed flow の両方で、goal-level prompt による `codex exec` 実行時に発生した
- 問題が出たコマンド系統:
  - manual-test workspace 内からの nested `codex exec ...`
- 観測したエラー:
  - `bwrap: No permissions to create a new namespace, likely because the kernel does not allow non-privileged user namespaces`
- 影響:
  - delegated agent が shell を使う spec-dock 実作業（create / active set / sync / validate）を完了できなかった
  - 一方で、MCP による調査や discovery 応答までは可能だった
- 判定:
  - 環境 blocker
  - installer / shim 契約そのものの不具合を示す証拠ではない

### blocker 2: この環境では Copilot runtime command が利用できない
- 観測したコマンド:
  - `gh copilot --help`
- 観測したエラー:
  - `unknown command "copilot" for "gh"`
- 影響:
  - Copilot runtime の委譲実行は検証できなかった
  - Copilot 側は static install / contract 確認までに留まった
- 判定:
  - 環境 blocker
  - `.github/agents/spec-dock.agent.md` の契約不備を示すものではない

## テスト結果の解釈
- 現時点の証拠から、インストール側は正しく動いていると判断できる
  - provider-side の native shim ファイルが存在している
  - installer がそれらを target path へ正しく配置している
  - static contract check が通っている
- 一方で、delegated real-work execution の runtime 受け入れを完了したとはまだ言えない
- したがって、現時点の正しい整理は次のとおり
  - install / static contract: `pass`
  - runtime end-to-end delegated execution: `blocked (environment)`

## 再現情報
- current trial workspace:
  - `manual-tests/workspaces/2026-04-06-iss-00051-native-shim-real-manual/trial-gh-current/repo`
- GitHub current repo:
  - `https://github.com/chemitaro/spec-dock-native-shim-current-20260406`
- seed issue:
  - `https://github.com/chemitaro/spec-dock-native-shim-current-20260406/issues/1`

## 推奨する次アクション
1. non-privileged user namespace が有効な環境、または nested Codex shell 実行が許可された環境で Codex runtime 手動テストを再実施する
2. `gh copilot` が利用可能な環境を用意し、`.github/agents/spec-dock.agent.md` の runtime 委譲実行を検証する
3. 現在の static / install check は baseline acceptance gate として維持し、runtime delegated execution は環境 blocker 解消後の follow-up acceptance gate として扱う

## 判断
- 今回の結果を、asset-copy installer correction そのものの不具合とは解釈しない
- 環境能力に起因する manual-test runtime blocker として記録・追跡する
