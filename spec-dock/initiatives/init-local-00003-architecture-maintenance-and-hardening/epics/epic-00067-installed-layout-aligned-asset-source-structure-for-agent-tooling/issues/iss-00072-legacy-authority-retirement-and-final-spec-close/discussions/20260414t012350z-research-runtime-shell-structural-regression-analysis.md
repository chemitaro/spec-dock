---
種別: research
ID: "20260414t012350z-research"
タイトル: "runtime shell structural regression analysis"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-04-14"
親: ["iss-00072"]
関連: []
---

# 20260414t012350z-research runtime shell structural regression analysis

## 調査目的 (必須)
- `python -m unittest discover -v` の full suite green を阻害している failing test を特定し、issue-72 の closeout scope を崩さずに修正可能な最小原因と対処方針を明らかにする。
- 特に `RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression` の failure が、test の過剰制約なのか、実装の layering regression なのかを切り分ける。
- この調査結果を、issue-72 の設計書と実装計画書で参照する独立正本にする。

## 調査方法 (必須)
- 実行コマンド:
  - `python -m unittest discover -v`
  - `python -m unittest -v tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
- 参照した source / tests:
  - `tests/cli_runtime/test_runtime_shell_s11.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py`
- 調査観点:
  - commands 層の import boundary
  - `MutateDepsRequest` へ渡す ID の正規化責務
  - closeout tranche で許容される変更範囲の局所性
- 比較した修正案:
  - Option A: test 側の structural contract を緩和する
  - Option B: commands-safe helper へ局所移設する
  - Option C: application request contract 側へ責務移動する

## 調査結果 (必須)
- full suite 実行中に再現した明示 failure は次の 1 件である。
  - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
- 単体再現結果:
  - failure location: `tests/cli_runtime/test_runtime_shell_s11.py:568`
  - assertion message: `forbidden import in /srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py: domain.ids`
- 事実:
  - `commands/deps.py` は `from ..domain.ids import format_id, parse_id` を持ち、commands 層から domain への直 import が存在する。
  - 同 test は commands 層を thin shell layer とみなし、`domain` / `infra` / `app` への直 import を structural regression として検知している。
  - `commands/targets.py` には commands 層内で閉じた正規表現ベースの parsing / validation helper がすでに存在し、commands-safe helper を置く先として自然である。
  - `application/contracts.py` の request contract は canonicalized な ID 文字列を前提にしており、application 層へ責務を広げると closeout tranche には不要なインターフェース変更が生じやすい。
- 切り分け:
  - test が新たに過剰化したのではなく、現実に commands 層の直 import が contract 違反を起こしている。
  - よって root cause は test ではなく実装側の layering regression である。
- 選択肢評価:
  - Option A:
    - 失敗を消せるが、S11 structural regression guard を弱めるため不採用。
  - Option B:
    - 振る舞い維持のまま boundary violation を除去でき、変更範囲が最小。
  - Option C:
    - request contract / downstream error surface / validation ownershipを広げるため、issue-72 の closeout fix としては過大。

## 結論 (必須)
- 推奨修正は Option B である。
- 具体方針:
  - `commands/deps.py` から `domain.ids` 直 import を除去する。
  - ID normalization は commands 層内の helper へ寄せる。候補は `commands/targets.py` への共通 helper 追加、または commands 専用 helper module の新設。
  - S11 test の structural contract 自体は維持する。
- 検証順序:
  - 1. failing test 単体
  - 2. deps command 周辺の targeted tests
  - 3. `python -m unittest discover -v`
- この調査は requirement の変更根拠ではなく、design/plan を具体化するための独立分析正本として扱う。

## リスク/制約 (任意)
- full suite の最終結果は修正後に再実行して再確認が必要である。
- closeout issue であるため、application/domain contract の広域変更は避ける。
- current worktree には issue-72 closeout 関連の既存変更が残っているため、差分統合時に unrelated rollback を行わない。

## 参考（References） (任意)
- `tests/cli_runtime/test_runtime_shell_s11.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py`
