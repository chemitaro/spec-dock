---
種別: 実装報告書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28"]
状態: "in_progress"
作成者: "Codex CLI"
最終更新: "2026-03-18"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# issue-28-runtime-regression-bugs manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する — 実装報告

## 実施サマリー
- `S01 create transaction で duplicate id を予防する` を完了
- `S02 discussion seq を同じ transaction に統合し validator でも守る` を完了
- `S03 status/readiness contract を統一し stale projection を明示する` を完了
- `S04 sync artifact / doctor / validator 契約を揃える` を完了
- implementation review と QA review を通過
- 次は `S05 GitHub targeting と CLI intent surface を安全化する` に着手

## 記録
- `S01` 実装:
  - `new initiative|epic|issue` の create に repo-level lock を導入
  - bounded wait / stale lock safe failure / no-write failure / `spec doctor` 誘導メッセージを追加
  - post-write duplicate guard を追加
- `S01` implementation review:
  - 初回 `fail`
  - 指摘:
    - lock metadata write 失敗時の orphan lock cleanup 漏れ
    - release unlink 失敗の黙殺
  - 対応:
    - metadata write failure 時の cleanup を追加
    - release unlink failure を明示的 failure として扱うよう修正
  - 再レビュー:
    - `pass`
- `S01` QA review:
  - `pass`
  - 実行:
    - `python -m unittest -v tests.cli_runtime.test_runtime_new_s08`
    - `python -m unittest -v tests.cli_runtime.test_new tests.cli_runtime.test_import tests.cli_runtime.test_runtime_import_s10`
    - `python -m unittest discover -v tests/cli_runtime`
    - 競合/lock 系 7 テストの 20 回反復実行
- `S02` 実装:
  - `new doc` の create を S01 と同じ create lock 契約に統合
  - post-write duplicate guard を追加し、discussion seq の重複を作成直後に検知
  - validator に duplicate discussion sequence 検知を追加
- `S02` implementation review:
  - `pass`
  - 実行:
    - `python -m unittest -v tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate`
- `S02` QA review:
  - `pass`
  - 実行:
    - `python -m unittest -v tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate`
- `S03` 実装:
  - local-only issue を deterministic に `open` / `ready` と解釈するよう status/readiness 契約を統一
  - `IssueStatusSnapshot` と sync/deps JSON・text 出力に `authority` / `effective_status` / `source` / `stale` / `last_sync_at` を追加
  - `deps check` / `active set` / `sync` が同じ status context を使うよう統一
  - cache の `last_sync_at` は top-level `generated_at` ではなく issue node ごとの保存値を読むよう修正
- `S03` implementation review:
  - 初回 `fail`
  - 指摘:
    - cache の `last_sync_at` が local-only sync 後の `generated_at` で前進して見え、authoritative freshness を過大表示する
  - 対応:
    - cached `last_sync_at` を issue node の persisted field から読むよう修正
    - GitHub authoritative / cache re-sync の freshness 回帰テストを追加
  - 再レビュー:
    - `pass`
- `S03` QA review:
  - 初回 `fail`
  - 指摘:
    - linked issue sync の freshness 契約が cache/live 両経路で未固定
    - `deps check` text 出力の freshness 表示が未固定
  - 対応:
    - `tests/cli_runtime/test_sync.py` に authoritative / cache 両経路の `source` / `stale` / `last_sync_at` 検証を追加
    - `tests/cli_runtime/test_runtime_deps_s04.py` に blocked / ready 両経路の text freshness 表示検証を追加
  - 再レビュー:
    - `pass`
  - 実行:
    - `python -m unittest -v tests.domain_runtime.test_runtime_domain_s03 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_deps tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.presentation_runtime.test_runtime_sync_s07`
- `S04` 実装:
  - `initiative` / `epic` / `issue` の required artifact presence を validate 契約へ追加し、`.meta.json` / `requirement.md` / `design.md` / `plan.md` / `report.md` 欠損を failure 化
  - `doctor` command/use case/presentation を追加し、`duplicate_id` / `duplicate_seq` / `missing_artifact` / `broken_meta` / `stale_active_pointer` の supported guidance を返すようにした
  - `active show` の not-set 出力に fallback path と next action を追加
  - installer `init/update` で `spec-dock/active/{initiative,epic,issue}` と `context-pack.md` の fallback entrypoint を自動生成し、empty active dir / symlink failure / dangling symlink / missing context-pack を復旧できるようにした
- `S04` implementation review:
  - 初回 `fail`
  - 指摘:
    - `doctor` が `Invalid JSON: .../.meta.json` や required field 欠損を `broken_meta` に分類できない
    - invalid active manifest や stale pointer の一部で `doctor` guidance が漏れる
  - 対応:
    - `.meta.json` 系エラーの分類条件を拡張
    - invalid active manifest、absolute path outside repo、file path target、graph unavailable、dangling symlink / missing context-pack の各 edge case を修正
    - stale pointer false positive を避けるため `graph is None` 時の id-side stale check を抑止
  - 再レビュー:
    - `pass`
- `S04` QA review:
  - 初回 `fail`
  - 指摘:
    - required artifact matrix の一部と `doctor` guidance / installer fallback edge case の回帰保護が薄い
  - 対応:
    - `initiative|epic|issue × requirement.md|design.md|plan.md|report.md` の欠損を全組合せで検証
    - `doctor` の exact duplicate id / duplicate seq / broken meta / stale active pointer guidance をテスト固定
    - installer の symlink failure / dangling symlink / persisted active からの context-pack 再生成をテスト固定
  - 再レビュー:
    - `pass`
  - 実行:
    - `python -m unittest -v tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_validate_s02 tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_active tests.cli_runtime.test_runtime_doctor_s04 tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_update_bootstraps_active_fallback_entrypoints_when_active_dir_is_empty tests.test_init_update.TestInitUpdate.test_update_bootstraps_active_path_files_when_active_symlink_creation_fails tests.test_init_update.TestInitUpdate.test_update_repairs_dangling_active_symlink_entrypoint tests.test_init_update.TestInitUpdate.test_update_regenerates_context_pack_from_persisted_active_manifest`

## 発見事項
- create lock は local filesystem 前提で、NFS 等の特殊 filesystem は未検証
- `issue` の GitHub create が遅延するケースでは lock 保持時間が伸び、競合失敗が増える運用リスクがある
- 全 repository の test suite は未実行で、現時点の QA は runtime CLI スコープに限定
- duplicate discussion sequence 検知は filename 規約（`NNN-type-slug.md`）に一致する discussion file を前提とする
- cache `last_sync_at` は issue node の persisted freshness field がない旧 index では `None` になる
- discussion は first-class node / manifest を持たないため、S04 の required artifact presence validation は `initiative` / `epic` / `issue` に限定した。discussion は既存どおり recognized markdown の integrity contract（少なくとも seq uniqueness）を validate 対象とする

## 次アクション
- `S04` の変更をコミットする
- `S05` の dev implementation を開始する
- `S05` 完了後に implementation review / QA review / report 更新 / commit を同じ単位で進める
