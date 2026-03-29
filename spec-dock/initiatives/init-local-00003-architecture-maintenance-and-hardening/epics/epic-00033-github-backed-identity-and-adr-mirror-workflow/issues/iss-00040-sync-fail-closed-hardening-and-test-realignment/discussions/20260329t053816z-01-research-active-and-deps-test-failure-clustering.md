---
種別: research
ID: "20260329t053816z-01-research"
タイトル: "active-and-deps-test-failure-clustering"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-03-29"
親: ["iss-00040"]
関連: []
---

# 20260329t053816z-01-research active-and-deps-test-failure-clustering

## 調査目的 (必須)
- `python -m unittest discover -v` で再現する失敗が、runtime defect なのか、epic-00033 で先行導入済み contract に対する test fixture / expectation / checked-in parity の未更新なのかを切り分ける。
- `iss-00040` の requirement / design / plan に必要な事実、境界、fixture 戦略、parity 回復方針を確定する。

## 調査方法 (必須)
- active context の initiative / epic / issue docs、`workflow_issue.md`、`phase_requirement.md`、`phase_design.md`、`phase_plan.md` を確認した。
- 全体回帰として `python -m unittest discover -v` を実行し、失敗クラスタを確認した。
- 代表的な failing tests と関連実装を読み、以下を確認した。
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/domain_runtime/test_runtime_domain_s01.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/harness.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
- representative reruns:
  - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_accepts_explicit_id_flag -v`
  - `python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_github_ready_when_deps_closed -v`
  - `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs -v`
  - `python -m unittest tests.domain_runtime.test_runtime_domain_s01.TestRuntimeDomainS01.test_validate_graph_and_deps_detects_structural_error -v`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v`

## 調査結果 (必須)
- `python -m unittest discover -v` は 524 tests 中 107 failures で終了した。
- `active` / `deps` / `sync` の主クラスタは次の 2 種類だった。
  - クラスタA:
    - test setup が `new initiative|epic|issue --no-github` を使っており、現行の GitHub mandatory contract で即時 reject される。
  - クラスタB:
    - `--github-issue` を使う fixture が `origin` remote を初期化しておらず、repo scope 解決で fail-fast する。
- `tests/cli_runtime/test_new.py` は current contract に追随済みで、current-contract fixture の参照実装になっている。
- `tests/cli_runtime/harness.py` には `_init_origin_repo()` と `_create_same_repo_linked_hierarchy()` があり、current-contract fixture helper はすでに存在する。
- `tests/cli_runtime/test_wrappers.py` は current docs ではなく旧 `--no-github` command example を期待している。
- `tests/domain_runtime/test_runtime_domain_s01.py` は current fail-closed ordering より後段の legacy expectation を持っている。
- `tests/test_init_update.py` は provider asset と checked-in dogfooding runtime mirror の parity drift を検知している。
- sync read path は legacy checked-in data を完全には捨てていないため、legacy/local-only coverage 自体は still meaningful である。
- ユーザー確認により、本 issue は `active/deps` に限定せず、`sync` / `wrappers` / `domain` / parity まで含めて閉じる方針が採択された。

## 結論 (必須)
- `iss-00040` の主眼は production runtime contract の巻き戻しではなく、epic-00033 で先行導入済み contract に合わせた test realignment と checked-in parity recovery である。
- 修正は 2 系統に分ける必要がある。
  - current-contract tests:
    - `origin` を持つ Git repo を初期化し、GitHub-backed node を作る helper に寄せる。
    - 旧 `--no-github` setup と `*-local-*` 前提の expectation を normal path から除去する。
  - legacy-compat tests:
    - local-only / unscoped checked-in data を本当に検証したいケースだけ explicit legacy fixture にする。
- wrappers / domain / parity も同じ contract shift に対する未追随として、同 issue でまとめて閉じるのが妥当である。

## リスク/制約 (任意)
- すべての failing tests を GitHub-backed fixture に機械変換すると、legacy/local-only compatibility read path の coverage を落とす。
- テストを通すために runtime の `--no-github` rejection や `origin` 必須 contract を緩めると、epic-00033 と矛盾する。
- fixture 更新後に、前段 failure に隠れていた secondary assertion mismatch が顕在化する可能性がある。

## 参考（References） (任意)
- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/docs/workflow_issue.md`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/harness.py`
- `tests/test_init_update.py`
