# iss-00514 の報告（2026-11-13、統括）

## 一覧と利用者の判断
0.9.0 の配布（2026-11-06）から1週間、問題なし。2026-11-13 に一覧（パス、大きさ、作った日、失うもの）を利用者に示し、推奨（控えと一時の置き場は消す、版3の worktree は残す）が採用された。

## 消したもの（2026-11-13）
- `worktrees/i12-prep/backups`（592K）、`worktrees/i12-prep/migrate-to-canonical-state`（1.2M）
- `worktrees/spec-dock-{042,050,051,060,070,080,090}/backups`（240K〜1.3M）と、空になった親のディレクトリ
- `/private/tmp/spec-dock-v0.4.0-src`〜`v0.9.0-dist`（空〜4K）

## 残したもの
- `worktrees/orca/spec-dock/local-macos-vm-ci`（#463、main にないコミット 7、未保存なし）
- `worktrees/spec-dock/schema1-preserving-migration-20261004`（Codex の作業、main にないコミット 2、未保存なし）
- #463 を再検討するときに、main を取り込むか消すかを決める。
