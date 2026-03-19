---
種別: discussion
ID: "019"
タイトル: "pr-29 codex review 指摘の妥当性分析と corrective patch 方針"
状態: "closed"
作成者: "Codex CLI"
作成日: "2026-03-18"
関連: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# pr-29 codex review 指摘の妥当性分析と corrective patch 方針

## 対象指摘

### R1 foreign repo identity persistence
- 内容:
  - `--allow-foreign-url` で import した foreign repo issue は import 時点では `gh issue view --repo owner/repo` で読める
  - しかし node に永続化されるのは `github_issue_number` だけで、後続の `sync --github` / `deps check --github` は current repo の同じ番号を参照しうる

### R2 stale create lock doctor guidance
- 内容:
  - create lock が stale になった時に create 系は `spec doctor` を案内する
  - しかし doctor 側は `.runtime/create.lock` を診断しないため、repo が wedged のままになる

### R3 dogfooding runtime parity
- 内容:
  - create lock failure から `spec doctor` を案内していても、この repo に checked-in されている dogfooding consumer workspace `spec-dock/scripts/` が古いと、その場で `doctor` を実行できない
  - 同じ stale mirror で `active set --id` など issue-28 追加 surface も欠け、provider-side fix が dogfooding repo で検証不能になる

## 妥当性評価

### R1
- verdict:
  - `valid`
- 根拠:
  - import use case は foreign repo context を read-time にだけ使い、永続化された node/meta には repo slug が残らない
  - `sync_state.py` / `check_deps.py` の GitHub fetch は linked issue を issue number のみで current repo に問い合わせる
  - そのため cross-repo import は次回 refresh で status/url/source を誤 hydrate しうる

### R2
- verdict:
  - `valid`
- 根拠:
  - create lock failure message は stale/timeout の両方で `spec doctor` を案内する
  - 一方 `doctor.py` は duplicate/missing/broken/stale active pointer しか見ておらず、`.runtime/create.lock` を診断しない
  - stale create lock が実際に残ると operator に supported recovery path がない

### R3
- verdict:
  - `valid`
- 根拠:
  - `HEAD` 時点の checked-in `spec-dock/scripts/spec_dock_runtime/cli/parser.py` / `registry.py` は provider-side shipped assets に追随しておらず、`doctor` subcommand と explicit target help が欠けている
  - そのため review 時点では `python spec-dock/scripts/spec-dock doctor --help` が dogfooding repo で失敗し、repair guidance を follow できない

## corrective patch 方針

### P1 foreign repo identity persistence
- linked/imported issue の persisted meta/model に `github.repo_owner` / `github.repo_name` 相当の repo identity を追加する
- graph/model/application status context が issue number だけでなく repo identity 付きで GitHub snapshot を引けるようにする
- `sync --github` / `deps check --github` / import 後 sync が persisted repo identity を優先して current repo と誤混線しないことを固定する

### P2 stale create lock doctor guidance
- doctor に create lock inspection を追加し、stale lock / unreadable lock metadata / ownership mismatch 後の残骸を finding として返す
- guidance に lock path、読めた metadata、supported recovery（不要 lock の削除または再実行前確認）を含める
- stale lock failure message と doctor finding の契約を揃える

### P3 dogfooding runtime parity
- checked-in consumer workspace `spec-dock/scripts/` を provider-side shipped runtime に refresh する
- parity は file sync だけでなく `python spec-dock/scripts/spec-dock doctor --help` と explicit target help の smoke で固定する
- 再発防止として checked-in dogfooding runtime surface を確認する test を追加する

## requirement/design/plan への反映方針
- requirement:
  - `AC-004` に「explicit opt-in が許可された foreign import でも、後続 refresh/deps は同じ foreign repo identity を維持する」を追加
  - `AC-008` に `stale create lock` を追加
  - `AC-010` として checked-in dogfooding runtime parity を追加
- design:
  - GitHub targeting 節に persisted repo identity と repo-aware refresh を追加
  - create transaction / doctor 節に stale create lock diagnosis を追加
  - dogfooding runtime parity 節を追加
- plan:
  - `S05` に foreign repo identity persistence と repo-aware sync/deps regression を追記
  - `S04` に stale create lock doctor guidance と regression test を追記
  - `S90` に checked-in dogfooding runtime smoke を追記

## merge/PR への影響
- 3 件とも `valid`
- PR #29 はこのまま merge-ready ではなく、corrective patch を入れて再push・再review が必要
