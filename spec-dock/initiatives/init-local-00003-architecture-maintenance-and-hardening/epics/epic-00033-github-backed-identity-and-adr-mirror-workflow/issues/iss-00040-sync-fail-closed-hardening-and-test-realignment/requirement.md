---
種別: 要件定義書（Issue）
ID: "iss-00040"
タイトル: "Sync Fail Closed Hardening And Test Realignment"
関連GitHub: ["#40"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
親: ["epic-00033", "init-local-00003"]
---

# iss-00040 Sync Fail Closed Hardening And Test Realignment — 要件定義（WHAT / WHY）

## 目的
- epic-00033 で導入済みの GitHub mandatory / canonical repo scope / fail-closed contract を正本として、未追随の stale tests と checked-in dogfooding parity drift を修正する。
- production runtime contract を巻き戻さずに、回帰テスト群が現行仕様を正しく検証できる状態へ戻す。

## 背景・現状
- 現状の挙動:
  - `python -m unittest discover -v` は 524 tests 中 107 failures で終了する。
  - `tests.cli_runtime.test_active` / `tests.cli_runtime.test_deps` / `tests.cli_runtime.test_sync` の多くは、旧 `new ... --no-github` fixture または `origin` 未初期化 fixture のため、現行 create contract の前段で失敗する。
  - `tests.cli_runtime.test_wrappers` は現行 docs に存在しない旧 command example を期待して失敗する。
  - `tests.domain_runtime.test_runtime_domain_s01` は fail-closed 順序変更後も旧 validation error を期待して失敗する。
  - `tests.test_init_update` は provider asset と checked-in dogfooding runtime mirror の不一致を検知して失敗する。
- 現状の課題:
  - current-contract tests と legacy-compat tests の fixture 戦略が分離されておらず、旧 local-only create path への依存が normal path tests に混入している。
  - `without_github` を「live fetch を使わない」の意味ではなく、「local-only node を作る」の意味で扱う stale tests が残っている。
  - stale-contract cluster が full suite の signal を汚しており、実際の product regression と区別しづらい。
- 再現手順:
  1. `/srv/mount/spec-dock` で `python -m unittest discover -v` を実行する。
  2. 代表失敗として次を確認する。
    - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_accepts_explicit_id_flag -v`
    - `python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_github_ready_when_deps_closed -v`
    - `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs -v`
    - `python -m unittest tests.domain_runtime.test_runtime_domain_s01.TestRuntimeDomainS01.test_validate_graph_and_deps_detects_structural_error -v`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v`
- 観測点:
  - CLI:
    - `error: '--no-github' is not supported for initiative; GitHub linkage is mandatory.`
    - `error: git failed: git remote get-url origin`
  - Filesystem:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` と `spec-dock/scripts/spec_dock_runtime/application/sync_state.py` の不一致
  - Docs/tests:
    - `spec-dock/docs/workflow_issue.md` は current contract 前提だが、wrapper tests は旧 `--no-github` command example を期待する
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/docs/phase_design.md`
  - `spec-dock/docs/phase_plan.md`
  - `spec-dock/active/issue/discussions/20260329t053816z-01-research-active-and-deps-test-failure-clustering.md`
  - `spec-dock/active/issue/discussions/20260329t053816z-disc-test-realignment-scope-and-acceptance.md`
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/domain_runtime/test_runtime_domain_s01.py`
  - `tests/test_init_update.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` の runtime regression を保守する maintainer / coding agent
- 代表シナリオ:
  - maintainer が full suite または targeted suites を実行したとき、recent contract change に未追随の stale tests による false negative が大量発生しない。
  - provider asset 更新後に checked-in dogfooding mirror parity が維持され、parity check が安定して通る。

## スコープ
- MUST:
  - `tests/cli_runtime/test_active.py`、`tests/cli_runtime/test_deps.py`、`tests/cli_runtime/test_sync.py` の fixture と assertion を、GitHub mandatory / `origin` basis の repo scope / fail-closed contract に合わせて更新する。
  - `tests/cli_runtime/test_wrappers.py` の docs expectation を current workflow/docs contract に合わせて更新する。
  - `tests/domain_runtime/test_runtime_domain_s01.py` の validation expectation を current fail-closed ordering に合わせて更新する。
  - provider asset と checked-in dogfooding runtime mirror の parity drift を解消し、parity check を回復する。
  - issue 完了時に、current stale-contract cluster が解消されたことを regression evidence で示す。
- MUST NOT:
  - GitHub mandatory / canonical repo scope / fail-closed contract を弱める方向で runtime 実装を変更しない。
  - failing tests を skip や assertion の過度な緩和で隠蔽しない。
  - unrelated feature 追加や architecture change を持ち込まない。
- OUT OF SCOPE:
  - epic-00033 の要件再定義
  - current runtime contract と無関係な別系統の failing tests の一括解消
  - source-of-truth docs の大規模刷新

## 境界
- Always:
   - current runtime/docs contract を source of truth とする。
   - normal path tests と legacy-compat tests の fixture 戦略を分離する。
   - checked-in dogfooding mirror は provider asset に一致させる。
- Stop / Escalate:
  - implementation 中に test realignment / parity recovery では閉じない true product defect が見つかった場合、この issue の implementation を停止し、`report.md` に所見を記録した上で、人間の判断により別 issue 化または明示的な scope update が承認されるまで runtime behavior に触れない。
  - full-suite rerun 後に残る failure が current stale-contract cluster と無関係なら、本 issue の close 判定では scope 外として `report.md` に記録し、人間判断で別 issue または既存 issue 参照先へエスカレーションする。
- Never:
   - `new --no-github` の normal path success を戻して tests を通すこと。
   - `origin` 必須の repo scope resolver を無効化して tests を通すこと。
   - true product defect を見つけたことを理由に、この issue 内で runtime rollback や無承認の scope expansion を行うこと。

## 非交渉制約
- epic-00033 の GitHub-backed identity / repo-scope / fail-closed postureに反しないこと。
- `src/spec_dock/assets/spec_dock/...` を provider-side source of truth として扱うこと。
- 既存テストの検証意図を保ったまま realign すること。
- uppercase path を新たに増やさないこと。

## 前提
- `tests/cli_runtime/test_new.py` には current-contract fixture の参照実装がある。
- `tests/cli_runtime/harness.py` には repo 初期化と same-repo linked hierarchy を構築する helper がある。
- sync read path は legacy checked-in data を完全には捨てていないため、legacy-compat coverage 自体は still meaningful である。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `active set` / `deps check` / `sync` の normal path regression tests
  - When:
    - `iss-00040` の修正を適用する
  - Then:
    - normal path tests は GitHub-backed fixture と `origin` 初期化済み repo を使う
    - 旧 `new --no-github` setup に依存しない
    - current id/path/status contract を検証する assertion に更新されて pass する
  - 観測点:
    - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_deps tests.cli_runtime.test_sync -v`
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - wrapper docs contract tests と domain validation tests
  - When:
    - current docs / current fail-closed ordering に expectation を realign する
  - Then:
    - 旧 `--no-github` docs expectation や旧 validation error expectation ではなく、current source of truth を検証して pass する
  - 観測点:
    - `python -m unittest tests.cli_runtime.test_wrappers tests.domain_runtime.test_runtime_domain_s01 -v`
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - provider asset と checked-in dogfooding runtime mirror がずれている
  - When:
    - parity drift を解消する
  - Then:
    - checked-in mirror が provider asset と一致し、parity check が pass する
  - 観測点:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v`
    - relevant file diff の解消
- AC-004:
  - Actor:
    - maintainer
  - Given:
    - issue scope の修正完了後
  - When:
    - regression evidence を取得する
  - Then:
    - current stale-contract cluster に起因する failures が解消されている
    - remaining failures がある場合は、各 failure について「本 issue の対象ファイル / 契約変更に起因しない」ことを report に明記し、別 issue 化または既存 issue 参照先を紐づけて close 判定できる
  - 観測点:
    - `python -m unittest discover -v`
    - `report.md` の記録

## 例外・エッジケース
- EC-001:
  - 条件:
    - fixture 更新後に、前段 failure に隠れていた secondary assertion mismatch が顕在化する
  - 期待:
    - current contract に属する mismatch なら同 issue で修正し、無関係なら scope 外として仕分ける
  - 観測点:
    - incremental rerun と report
- EC-002:
  - 条件:
    - local-only / legacy read path を検証したい test が残る
  - 期待:
    - unsupported CLI path ではなく、explicit legacy fixture で coverage を保持する
  - 観測点:
    - legacy fixture を使う targeted tests
- EC-003:
  - 条件:
    - parity drift の原因が checked-in mirror refresh だけでは解消しない
  - 期待:
    - provider asset を正本として parity を回復するが、新しい product behavior change は追加しない
  - 観測点:
    - provider vs mirror comparison
    - parity test

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_accepts_explicit_id_flag -v`
  - Output:
    - 修正前は `--no-github` contract error で fail
    - 修正後は current-contract fixture で `active set --id ...` の intended assertion まで到達して pass

## 用語（ドメイン語彙）
- TERM-001:
  - stale-contract cluster:
    - recent contract change に未追随の fixture / assertion / checked-in artifact 群
- TERM-002:
  - current-contract test:
    - GitHub mandatory / canonical repo scope / fail-closed contract を正本として検証する test
- TERM-003:
  - legacy-compat test:
    - local-only / unscoped checked-in data の read path や互換境界を explicit fixture で検証する test
- TERM-004:
  - dogfooding mirror parity:
    - provider asset と checked-in consumer mirror が一致している状態

## 未確定事項
- なし:
  - close 判定は AC-004 と report contract で固定した
