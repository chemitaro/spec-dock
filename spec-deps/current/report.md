---
種別: 実装報告書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28"]
状態: "in_progress"
作成者: "Codex CLI"
最終更新: "2026-03-17"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# issue-28-runtime-regression-bugs manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する — 実装報告

## 実施サマリー
- `S01 create transaction で duplicate id を予防する` を完了
- `S02 discussion seq を同じ transaction に統合し validator でも守る` を完了
- implementation review と QA review を通過
- 次は `S03 status/readiness contract を統一し stale projection を明示する` に着手

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

## 発見事項
- create lock は local filesystem 前提で、NFS 等の特殊 filesystem は未検証
- `issue` の GitHub create が遅延するケースでは lock 保持時間が伸び、競合失敗が増える運用リスクがある
- 全 repository の test suite は未実行で、現時点の QA は runtime CLI スコープに限定
- duplicate discussion sequence 検知は filename 規約（`NNN-type-slug.md`）に一致する discussion file を前提とする

## 次アクション
- `S02` の変更をコミットする
- `S03` の dev implementation を開始する
- `S03` 完了後に implementation review / QA review / report 更新 / commit を同じ単位で進める
