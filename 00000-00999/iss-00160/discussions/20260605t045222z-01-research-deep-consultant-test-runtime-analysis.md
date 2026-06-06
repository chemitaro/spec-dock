---
種別: research
ID: "20260605t045222z-01-research"
タイトル: "Deep Consultant Test Runtime Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00160"]
関連:
  - "20260605t045222z-research"
authority: "synthesized"
derived_from:
  - "deep-consultant agent 019e960b-92d2-79c3-beae-55846614e835"
reflected_to: []
---

# 20260605t045222z-01-research Deep Consultant Test Runtime Analysis

## 調査目的

- `iss-00160` のテスト実行時間問題について、main orchestrator の実測とは独立した deep-consultant 分析を記録する。
- 分析は read-only で行い、実装や canonical spec authoring は行わない。
- deep-consultant の結論をそのまま採用済み仕様にせず、後続の requirement/design/plan authoring で採否判断できる evidence として残す。

## sources / 調査方法

### 参照先

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/cli.py`
- `tests/cli_runtime/harness.py`
- `tests/cli_runtime/test_deps.py`
- `tests/cli_runtime/test_validate.py`
- `tests/cli_runtime/test_delegated_authoring.py`
- `tests/cli_runtime/test_worktree.py`
- `tests/test_init_update.py`

### 検証手順

- deep-consultant agent に次を依頼した。
  - root-cause hypotheses ordered by likely contribution
  - concrete evidence from code/tests with file references
  - measurements that would prove/disprove each hypothesis
  - optimization directions
  - risks/unknowns
- main orchestrator は deep-consultant の結果を、別 research の実測値と照合する。

### 実験条件

- deep-consultant は read-only。
- deep-consultant 自身は実測コマンドを実行していない。
- deep-consultant の寄与率判断はコード構造と既知/今回の測定計画に基づく仮説である。

## facts / 観測できた事実

### deep-consultant の推奨結論

- 最初に疑うべき主因:
  - `new` / `deps add/remove` のたびに post-mutation sync が走る。
  - その sync が既定で GitHub 10,000 件 index を読む。
- 次点:
  - 各 test/subTest が `main(["init", ...])` と subprocess runtime fixture を作り直す。
- 実装変更より先に、test fixture の E2E 範囲を絞るのが低リスク。

### 仮説 1: post-mutation sync + 10,000 件 `gh issue list` が最大寄与

- `create_node_core()` は成功後に `post_mutation_sync(ports)` を返す。
  - file:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `sync_after_mutation()` は `github_enabled=True` / `issue_limit=10000` 固定で sync を実行する。
  - file:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
- test harness の default `gh` stub は `range(1, 10001)` を JSON 出力する。
  - file:
    - `tests/cli_runtime/harness.py`
- `deps add/remove` の updated path も `post_mutation_sync(ports)` を呼ぶ。
  - file:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`

### 仮説 2: 同じ重い hierarchy fixture を多数の test が subprocess で再作成している

- `_create_same_repo_linked_hierarchy()` は `new initiative` / `new epic` / `new issue` を 3 回 runtime subprocess で実行する。
  - file:
    - `tests/cli_runtime/harness.py`
- `test_deps.py` は helper 系を多数使う。
  - 代表例では 1 test 内で複数 `new` を実行後に `sync` する。
- `test_validate.py` は subTest ループ内で `init` + hierarchy + `validate` を作り直す箇所がある。

### 仮説 3: CLI runtime harness が毎回新しい Python interpreter を起動している

- `_run_runtime*` は `[sys.executable, spec-dock/scripts/spec-dock, *args]` を `subprocess.run()` する。
  - file:
    - `tests/cli_runtime/harness.py`
- その subprocess 内で sync は node records load、validation、GitHub index、artifact write を繰り返す。

### 仮説 4: `main(["init", ...])` は scaffold と agent assets を毎回コピー・検査している

- `init` は `docs/templates/scripts/system` を管理対象としてコピーする。
- skill install plan も走る。
- `_install_spec_dock()` 内で `shutil.copytree()` が使われる。
  - file:
    - `src/spec_dock/cli.py`

### 仮説 5: packaging / worktree / delegated authoring 系は別個に重い

- `test_init_update.py` の一部 helper は `venv`、`pip install --target`、`python -m build` を複数回実行する。
- `test_delegated_authoring.py` は約 50 件が `_make_target_repo_with_scope()` を呼び、各回 `init` + 3 `new` 後に git commit/diff 系を実行する。
- `test_worktree.py` は各 case で `git init/add/commit` と実 `git worktree` 操作を使う。

## inference / 推測

### I-001: deep-consultant の主因仮説は今回の実測と概ね整合する

- main orchestrator の file-level timing でも、最遅は `test_deps.py`、`test_validate.py`、`test_delegated_authoring.py` だった。
- `test_runtime_*` / `domain_runtime` / `presentation_runtime` が sub-second であることから、問題は runtime logic 全体ではなく、CLI black-box integration fixture の反復に偏っている。

### I-002: GitHub 10,000 件 index は単独主因ではなく、subprocess + sync + artifact generation と合成されて効く

- main orchestrator のマイクロ測定では、default `gh issue list` stub 単独実行は小型 stub と大差がなかった。
- ただし hierarchy + sync の A/B では 10,000 件 stub の方が平均 `0.182s` 遅かった。
- そのため、10,000 件 stub は単独の最大要因というより、fixture 反復時の累積コストと見るのが妥当。

### I-003: production behavior を直接変える前に test boundary を分離するべき

- `sync_after_mutation(issue_limit=10000)` は実運用上の contract の可能性がある。
- まずはテスト側で、large GitHub index を検証する代表ケースと、GitHub index が本質でないケースを分ける方が低リスク。

## unverified / 未検証事項

- deep-consultant は実測を実行していない。
- `gh issue list` call count、bytes、elapsed の full-run 集計は未測定。
- `_run_runtime*`、`main(["init"])`、`_create_same_repo_linked_hierarchy()` の full-run 実回数は未測定。
- `post_mutation_sync` を test-only no-op にした A/B は未実施。
- default GitHub issue limit を 10,000 から小さくする product impact は未検証。
- packaging tests の venv / build / install 段階別 timing は未測定。

## terminology conflicts / 用語衝突

- `fast`
  - deep-consultant の提案では、fast は subprocess / temp repo / git / gh を避けた lower-layer tests を指す。
  - 現在の directory 名だけでは fast/slow を判断できない。
- `integration`
  - CLI subprocess + temp repo + git/gh stub + derived artifact write を含むものは integration として扱うべき。
  - ただし `tests/cli_runtime/test_runtime_*` は path 上は `cli_runtime` だが、実測上は fast。
- `large-index regression`
  - GitHub 10,000 件 stub を使う regression は必要かもしれないが、すべての CLI test の default にする必要があるかは別問題。

## edge cases / 具体シナリオ

- edge case:
  - 10,000 件 GitHub issue index は、過去に current repo overlap / ambiguity / status resolution を守るために必要だった可能性がある。
  - implication:
    - 小型 stub を default にする場合、large-index 専用 regression を別に残す必要がある。
- edge case:
  - shared fixture reuse は mutation leak を起こす可能性がある。
  - implication:
    - prepared fixture は immutable seed から test ごとに copy する必要がある。
- edge case:
  - CLI smoke を削りすぎると parser/renderer/subprocess/import path の regression を見逃す。
  - implication:
    - representative CLI smoke は残し、branch explosion だけを lower-layer に移す必要がある。

## implications / 判断への含意

- 低リスクの改善方向:
  - `new` 自体を検証しないテストは direct materialization fixture へ寄せる。
  - GitHub 状態が本質でないテストは `--no-github` または小型 issue list stub を使う。
  - default 10,000 件 stub と large-index 専用 stub を分ける。
  - subTest ごとの `init` + hierarchy 再作成を copy-on-test fixture へ置き換える。
  - packaging tests は build artifact reuse が可能か測る。
- 大きめの改善方向:
  - CLI E2E と application/domain 検証を分離し、subprocess runtime は代表 smoke に限定する。
  - post-mutation sync に testable policy injection または fast fixture path を作る。
  - sync の graph/load/artifact write を incremental 化する。
  - unittest 実行の並列化を検討する。ただし temp/HOME/env/git worktree 干渉検証が必要。

## リスク/制約

- deep-consultant の分析は root-cause hypothesis であり、採用済み仕様ではない。
- product runtime の `post_mutation_sync` を変えると、derived artifacts freshness contract を壊す可能性がある。
- stub 縮小は large-index regression を隠すリスクがある。
- fixture reuse は test isolation を壊すリスクがある。

## 反映先

- 後続の `iss-00160` requirement/design/plan authoring で、root cause hypothesis と optimization option の evidence として採用候補。
- 採用時は `report.md` に、main orchestrator 実測との整合と未検証事項を明記する。
