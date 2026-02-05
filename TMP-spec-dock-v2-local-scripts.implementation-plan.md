# 実装計画書: v2 ローカルスクリプト運用への再設計（追加対応）

## 進め方（高レベル）
1. uvx CLI（パッケージ）の責務を `init/update` に限定する
2. 運用 CLI を `.spec-dock/scripts/spec-dock` として assets に追加する
3. README / guide / skill をローカルスクリプト導線に変更する
4. テストを更新し、`init/update` + ローカルスクリプトの E2E を通す

## タスク分解（詳細）
### A. パッケージ CLI の整理
- [ ] `src/spec_dock/cli.py` のサブコマンドを `init/update` 중심に再編
  - [ ] `new/active/sync/validate` は削除、または hidden（ヘルプに出さない）にする
  - [ ] 互換方針は “捨てる” なので、README からも削除

### B. ローカルスクリプトの実装（assets）
- [ ] `src/spec_dock/assets/spec_dock/scripts/spec-dock` を追加（Python）
  - [ ] コマンド: `new`, `active`, `sync`, `validate`
  - [ ] `.spec-dock/templates/` を参照してファイル生成
  - [ ] repo root 探索（cwd から `.spec-dock` を探す）
  - [ ] symlink 生成（失敗時 fallback）
- [ ] `src/spec_dock/assets/spec_dock/scripts/README.md` を “実行方法” に更新

### C. ドキュメント更新
- [ ] `README.md` を修正（運用は `./.spec-dock/scripts/spec-dock`）
- [ ] `src/spec_dock/assets/spec_dock/docs/spec-dock-guide.md` を修正
- [ ] `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` を修正

### D. テスト更新
- [ ] `tests/test_cli.py` を更新
  - [ ] `init/update` のみを `spec_dock.cli.main` で検証
  - [ ] ローカルスクリプトを `subprocess`（python 実行）で検証
  - [ ] `active` が `current.json` と `active/context-pack.md` を生成すること
  - [ ] `sync` が `state.json` を生成すること
  - [ ] `validate` が通ること

### E. 検証
- [ ] `python -m unittest discover -v`
- [ ] `python -m compileall -q src`

## 完了条件
- 受け入れ条件（requirements）を満たし、全テストが green
- README / guide / skill がローカルスクリプト導線に整合

