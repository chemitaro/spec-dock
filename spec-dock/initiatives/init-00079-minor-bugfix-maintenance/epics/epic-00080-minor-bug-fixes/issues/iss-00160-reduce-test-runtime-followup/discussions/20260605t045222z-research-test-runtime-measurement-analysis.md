---
種別: research
ID: "20260605t045222z-research"
タイトル: "Test Runtime Measurement Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00160"]
関連: []
authority: "synthesized"
derived_from:
  - "python -m unittest discover"
  - "file-level unittest timing script"
  - "micro measurement script for init, hierarchy fixture, and gh stub"
reflected_to: []
---

# 20260605t045222z-research Test Runtime Measurement Analysis

## 調査目的

- `spec-dock` のテスト実行が 10 分以上かかる現象を、現時点の worktree で再現し、客観的な実行時間・失敗状態・遅いテスト群を記録する。
- 要件定義や設計に入る前の evidence として、全体実行、ファイル単位実行、代表 fixture のマイクロ測定、コード構造の照合を分けて残す。
- 実装方針はまだ確定せず、どの仮説が測定事実に支えられているかを明確にする。

## sources / 調査方法

### 参照先

- `README.md`
  - full baseline command として `python -m unittest discover -v` が記載されている。
- `pyproject.toml`
  - project metadata と Python package 構成を確認した。
- `tests/cli_runtime/harness.py`
  - runtime subprocess helper、default `gh` stub、linked hierarchy fixture を確認した。
- `tests/cli_runtime/test_deps.py`
- `tests/cli_runtime/test_validate.py`
- `tests/cli_runtime/test_delegated_authoring.py`
- `tests/test_init_update.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`

### 検証手順

1. Active issue が `iss-00160` であることを `./spec-dock/scripts/spec-dock active show` で確認した。
2. 全体実行として `time python -m unittest discover` を実行した。
3. `tests` 配下の `test*.py` 33 ファイルを 1 ファイルずつ `python -m unittest <module>` で実行し、壁時計時間と return code を記録した。
4. `main(["init", target])`、`init + _create_same_repo_linked_hierarchy()`、default 10,000 件 `gh issue list` stub、小型 `gh issue list` stub をマイクロ測定した。
5. default 10,000 件 GitHub stub と 3 件 GitHub stub で、`init + new initiative + new epic + new issue + sync` の A/B 測定を行った。
6. `rg` で helper 使用箇所と runtime post-mutation sync の呼び出し箇所を確認した。

### 実験条件

- worktree:
  - `/Users/iwasawayuuta/.codex/worktrees/af4e/spec-dock`
- branch:
  - `iss-00160-reduce-test-runtime-followup`
- date:
  - `2026-06-05`
- runner:
  - local `python -m unittest`
- parallelism:
  - なし。逐次実行。
- note:
  - full run は `-v` なしで実行したため、README の full baseline より出力量は少ない。
  - file-level run はファイルごとに独立 process で実行したため、合計時間は full run と完全一致しない。

## facts / 観測できた事実

### 全体実行

- command:
  - `time python -m unittest discover`
- result:
  - `Ran 1035 tests in 599.706s`
  - `FAILED (failures=1)`
  - shell time: `python -m unittest discover  332.86s user 157.92s system 81% cpu 10:00.07 total`
- 10 分超の再現:
  - 実行開始から 10 分を超えた時点でもプロセスは完走していなかった。
  - 最終的な wall clock は `10:00.07 total` だった。
- failure:
  - `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
  - failure reason:
    - `checked-in dogfooding .meta.json path set diverged from cutover snapshot`
  - speed issue との切り分け:
    - この失敗は snapshot divergence であり、実行時間の主因ではなく、別の reliability/snapshot 問題として扱う。

### ファイル単位実行結果

| rank | file | seconds | rc |
| ---: | --- | ---: | ---: |
| 1 | `tests/cli_runtime/test_deps.py` | 113.02 | 0 |
| 2 | `tests/cli_runtime/test_validate.py` | 101.91 | 0 |
| 3 | `tests/cli_runtime/test_delegated_authoring.py` | 85.50 | 0 |
| 4 | `tests/test_init_update.py` | 60.03 | 1 |
| 5 | `tests/cli_runtime/test_active.py` | 56.76 | 0 |
| 6 | `tests/cli_runtime/test_import.py` | 36.84 | 0 |
| 7 | `tests/cli_runtime/test_sync.py` | 34.58 | 0 |
| 8 | `tests/cli_runtime/test_new.py` | 33.61 | 0 |
| 9 | `tests/cli_runtime/test_issue_lifecycle.py` | 28.60 | 0 |
| 10 | `tests/cli_runtime/test_worktree.py` | 21.25 | 0 |
| 11 | `tests/cli_runtime/test_delete.py` | 18.27 | 0 |
| 12 | `tests/cli_runtime/test_close.py` | 10.58 | 0 |
| 13 | `tests/cli_runtime/test_wrappers.py` | 3.87 | 0 |
| 14 | `tests/cli_runtime/test_uninstall.py` | 3.56 | 0 |
| 15 | `tests/cli_runtime/test_update.py` | 2.76 | 0 |
| 16 | `tests/cli_runtime/test_runtime_new_doc_s09.py` | 0.92 | 0 |
| 17 | `tests/cli_runtime/test_runtime_new_s08.py` | 0.72 | 0 |
| 18 | `tests/presentation_runtime/test_runtime_sync_s07.py` | 0.29 | 0 |
| 19 | `tests/test_cli.py` | 0.26 | 0 |
| 20 | `tests/cli_runtime/test_runtime_shell_s11.py` | 0.24 | 0 |
| 21 | `tests/cli_runtime/test_runtime_import_s10.py` | 0.22 | 0 |
| 22 | `tests/cli_runtime/test_runtime_delete_s13.py` | 0.17 | 0 |
| 23 | `tests/cli_runtime/test_runtime_doctor_s04.py` | 0.14 | 0 |
| 24 | `tests/cli_runtime/test_runtime_deps_s04.py` | 0.13 | 0 |
| 25 | `tests/cli_runtime/test_runtime_active_s05.py` | 0.09 | 0 |
| 26 | `tests/cli_runtime/test_runtime_close_s12.py` | 0.09 | 0 |
| 27 | `tests/cli_runtime/test_runtime_validate_s02.py` | 0.09 | 0 |
| 28 | `tests/domain_runtime/test_delegated_authoring.py` | 0.09 | 0 |
| 29 | `tests/domain_runtime/test_runtime_domain_s01.py` | 0.09 | 0 |
| 30 | `tests/cli_runtime/test_post_mutation_sync_s01.py` | 0.06 | 0 |
| 31 | `tests/cli_runtime/test_runtime_active_s06.py` | 0.06 | 0 |
| 32 | `tests/domain_runtime/test_authority.py` | 0.04 | 0 |
| 33 | `tests/domain_runtime/test_runtime_domain_s03.py` | 0.04 | 0 |

- file-level total:
  - `TOTAL,614.85,files=33`
- 観測:
  - `test_runtime_*`、`domain_runtime`、`presentation_runtime` はほぼ sub-second。
  - 遅いファイルは古い CLI black-box 系に集中している。
  - top 10 だけで約 `572.10s` になり、file-level total `614.85s` の約 `93.0%` を占める。
  - top 5 だけで約 `417.22s` になり、file-level total の約 `67.9%` を占める。

### マイクロ測定

| measurement | reps | values seconds | avg seconds |
| --- | ---: | --- | ---: |
| `main_init_empty_target` | 5 | `0.045,0.041,0.041,0.040,0.039` | 0.041 |
| `init_plus_create_same_repo_linked_hierarchy` | 3 | `0.862,0.851,0.838` | 0.850 |
| `default_gh_issue_list_stub_10000` | 5 | `0.180,0.128,0.144,0.136,0.134` | 0.144 |
| `small_gh_issue_list_stub_empty` | 5 | `0.315,0.114,0.121,0.114,0.120` | 0.157 |
| `default_10000_hierarchy_plus_sync` | 5 | `1.019,1.013,1.040,1.013,1.006` | 1.018 |
| `small_3_hierarchy_plus_sync` | 5 | `0.997,0.784,0.806,0.795,0.799` | 0.836 |

- `main(["init"])` 単体は平均 `0.041s` で、単体では主因ではない。
- `init + linked hierarchy` は平均 `0.850s` で、3 runtime `new` を含む fixture 作成としては non-trivial。
- `default_10000_hierarchy_plus_sync` と `small_3_hierarchy_plus_sync` の差は平均 `0.182s`。
  - 1 回あたりの差は小さいが、大量反復されると累積する。
- default `gh issue list` stub の単独実行は 10,000 件で平均 `0.144s`、小型 stub は平均 `0.157s` だった。
  - 単独実行では bash/Python startup が支配的で、10,000 件 JSON 生成だけを主因とは断定できない。
  - runtime sync 内では JSON parse、status map、artifact generation と組み合わさるため、A/B では差が出た。

### コード構造の観測

- `tests/cli_runtime/harness.py`
  - `_run_runtime*` は `[sys.executable, spec-dock/scripts/spec-dock, *args]` を `subprocess.run()` する。
  - `_create_same_repo_linked_hierarchy()` は `new initiative`、`new epic`、`new issue` の 3 subprocess runtime command を実行する。
  - `_runtime_env()` は env 未指定時に target ごとの `.test-gh-default/gh` を作り、PATH に prepend する。
  - default `gh issue list` stub は `range(1, 10001)` の JSON を返す。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `create_node_core()` は成功後に `post_mutation_sync(ports)` を返す。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
  - changed path では `post_mutation_sync(ports)` を返す。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `sync_after_mutation()` は `github_enabled=True`、`issue_limit=10000` で `sync_tree()` を呼ぶ。
- helper usage count:
  - `_create_same_repo_linked_hierarchy()`:
    - `test_validate.py`: 38
    - `test_deps.py`: 29
    - `test_active.py`: 22
    - `test_new.py`: 19
    - `test_sync.py`: 9
    - `test_issue_lifecycle.py`: 5
    - `test_import.py`: 1
    - `test_delegated_authoring.py`: 1
  - `test_delegated_authoring.py`:
    - `_make_target_repo_with_scope()` call sites: 49

## inference / 推測

### I-001: 主因は古い CLI black-box integration tests の大量反復である

- 根拠:
  - sub-second の `test_runtime_*` / `domain_runtime` / `presentation_runtime` と、数十〜百秒級の `test_deps.py` / `test_validate.py` / `test_delegated_authoring.py` の差が大きい。
  - 重いファイルほど temp repo、runtime subprocess、linked hierarchy、sync、GitHub stub を繰り返す。
- 含意:
  - runtime domain/application 層へ落とせる branch coverage を CLI black-box から分離できれば、速度改善余地が大きい。

### I-002: `post_mutation_sync` と GitHub 10,000 件 default stub は累積コストとして効いている

- 根拠:
  - `new` / `deps add/remove` の mutation path が `post_mutation_sync` を呼ぶ。
  - `sync_after_mutation()` が `issue_limit=10000` を固定している。
  - A/B で `default_10000_hierarchy_plus_sync` 平均 `1.018s`、`small_3_hierarchy_plus_sync` 平均 `0.836s` の差が出た。
- 注意:
  - 単独 `gh issue list` stub 実行では 10,000 件と空配列の差が明確ではなかったため、GitHub stub だけが主因とは言えない。
  - subprocess startup、sync graph read、artifact generation と合成されたときに効いている可能性が高い。

### I-003: `main(["init"])` 単体は主因ではないが、fixture の粒度では無視できない

- 根拠:
  - `main_init_empty_target` は平均 `0.041s`。
  - しかし `init_plus_create_same_repo_linked_hierarchy` は平均 `0.850s`。
  - full run stdout では `spec-dock: ok (init)` が大量に観測された。
- 含意:
  - `init` 自体を最適化するより、test fixture reuse / direct materialization / boundary selection を先に検討する方が効果が大きい可能性がある。

### I-004: `test_init_update.py` は速度問題と failure 問題が混在している

- 根拠:
  - file-level で `60.03s`、return code `1`。
  - failure は dogfooding `.meta.json` path set snapshot divergence。
- 含意:
  - runtime 短縮 issue では、`test_init_update.py` の slow path と snapshot failure を分けて扱う必要がある。

## unverified / 未検証事項

- per-test-method timing:
  - 今回は file-level timing まで。method/subTest 単位の累積時間は未測定。
- call-count instrumentation:
  - `_run_runtime*`、`main(["init"])`、`post_mutation_sync`、`gh issue list` の実際の full run call count は未測定。
- CPU / disk I/O profiling:
  - `cProfile`、`dtruss`、`fs_usage`、`py-spy` などは未実行。
- parallel execution:
  - unittest 並列化や per-file parallel execution の安全性は未検証。
- fixture reuse:
  - prepared fixture copy が test isolation を壊さないかは未検証。
- product behavior impact:
  - `sync_after_mutation(issue_limit=10000)` を変えることの product contract 影響は未検証。

## terminology conflicts / 用語衝突

- `unit`
  - 現在の速い `tests/domain_runtime` / `tests/presentation_runtime` / `test_runtime_*` は実質的に single-process または lower-layer の unit/contract tests として扱える。
  - ただし `tests/cli_runtime/test_runtime_*` は path 上は `cli_runtime` にあるため、単純な directory name だけでは分類できない。
- `integration`
  - 遅い `tests/cli_runtime/test_*.py` は temp repo、subprocess runtime、git/gh stub、filesystem artifact を跨ぐ integration tests。
  - すべてを routine full-run に入れると feedback loop が 10 分になる。
- `e2e`
  - 現時点では browser や external live service を使う e2e ではない。
  - ただし CLI black-box + temp repo は e2e 的コストを持つ。

## edge cases / 具体シナリオ

- edge case:
  - GitHub 10,000 件 index regression を検出するために default stub を大きくしている可能性がある。
  - 影響:
    - 全テストで小型 stub を default にすると、大量 index regression を見逃す恐れがある。
- edge case:
  - shared prepared fixture を導入すると、ある test の mutation が別 test へ漏れる可能性がある。
  - 影響:
    - fixture reuse は copy-on-test または direct materialization で isolation を保つ必要がある。
- edge case:
  - post-mutation sync を test-only no-op にすると、mutation command が derived artifacts を更新する contract を検証できなくなる。
  - 影響:
    - no-op 化は representative smoke を残すか、application-layer contract tests と分ける必要がある。

## implications / 判断への含意

- 次の設計では、テストの分類軸を明示する必要がある。
  - fast routine suite:
    - domain/application/presentation/single-process contract tests。
  - integration representative suite:
    - CLI subprocess、temp repo、git/gh stub、post-mutation sync を跨ぐ代表 smoke。
  - full regression suite:
    - 現行 `python -m unittest discover` 相当。
- 速度改善の第一候補は production runtime の変更ではなく、test fixture と test boundary の見直し。
- `gh issue list --limit 10000` 相当の regression は専用テストに閉じ込め、全 test の default fixture にしない選択肢を検討する価値がある。
- `test_validate.py` / `test_deps.py` は branch coverage を application/domain-level tests に移せるかが最大の検討点。
- `test_delegated_authoring.py` は `_make_target_repo_with_scope()` の 49 回反復を、direct materialization または copy-on-test fixture へ移せるかが検討点。

## リスク/制約

- 現時点で実装は行っていない。
- 測定はローカル Mac / 現在 worktree の 1 回測定であり、CI では異なる可能性がある。
- file-level timing は独立 process 実行なので、full discover の順序・cache・stdout 量とは一致しない。
- `tests/test_init_update.py` の failure は速度改善とは別に解消が必要。

## 反映先

- 後続の requirement/design/plan authoring で、acceptance criteria と execution plan の evidence として採用候補。
- canonical docs へ反映する場合は、測定条件と未検証事項を report の Evidence Adoption Ledger に明記する。
