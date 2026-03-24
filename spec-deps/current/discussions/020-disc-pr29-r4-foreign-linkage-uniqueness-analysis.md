---
種別: discussion
ID: "020"
タイトル: "pr-29 review r4 foreign github linkage uniqueness analysis"
状態: "closed"
作成者: "Codex CLI"
作成日: "2026-03-19"
関連: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# pr-29 review r4 foreign github linkage uniqueness analysis

## 対象指摘

- review id:
  - `2957830288`
- path:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py:119`
- 要旨:
  - foreign repo import 向けに `github_repo_owner` / `github_repo_name` を永続化したが、duplicate check が依然 `github_issue_number` 単独で動いている
  - そのため `current/repo#123` が既存の repo では `other/repo#123` を import できず、cross-repo overlapping issue number を扱えない

## 事実確認

- `import_node.import_node_core()` は import 前に `guard_github_issue_uniqueness(graph, issue_number)` を呼ぶ
- `guard_github_issue_uniqueness` は現状 `github_issue_number` だけで linked node を集める
- `domain.validation.validate_github_issue_numbers_unique()` も `github_issue_number` 単独で duplicate 判定する
- 一方で node/model/meta には `github_repo_owner` / `github_repo_name` が保存されるようになっている
- 後続の `sync --github` / `deps check --github` / `active set --github` は repo-aware refresh へ拡張済みで、repo identity を使える前提が既に入っている

## 妥当性評価

- verdict:
  - `valid`
- 理由:
  - GitHub issue number は repo 内でしか一意ではない
  - foreign import を正式に許容する contract を入れた以上、uniqueness も `repo + issue_number` で評価しないと contract が途中で破綻する
  - 現状実装のままだと「保存はできる前提に見えるが、番号衝突で import 自体が不必要に reject される」ため、feature が半端に閉じている

## 修正要否

- 判定:
  - `修正が必要`
- 理由:
  - `AC-004 GitHub URL safety` の「foreign import を explicit opt-in で扱える」契約が、repo 重複番号ケースで満たせていないため

## 修正案

### 案 A
- 内容:
  - duplicate check と validator を `github_issue_number` 単独から `normalized_repo_slug + issue_number` へ変更する
  - repo slug が無い node は current/local repo 相当の `None + issue_number` として扱う
- 利点:
  - 今回追加した repo identity と自然に整合する
  - import preflight と validate contract を同じ key で統一できる
- 懸念:
  - same-repo linked node の duplicate error message を repo-aware に更新する必要がある

### 案 B
- 内容:
  - import 時だけ特例で foreign repo 同番号を許可し、validator は従来どおり `github_issue_number` 単独とする
- 利点:
  - 変更量が小さい
- 懸念:
  - import は通るが validate で落ちるため contract が自己矛盾する
  - 採用不可

### 案 C
- 内容:
  - foreign import では番号重複を禁止し続け、docs で「cross-repo でも issue number は全体一意」と制約を明文化する
- 利点:
  - 既存実装を大きく変えずに済む
- 懸念:
  - GitHub の実世界モデルと一致しない
  - `--allow-foreign-url` を追加した意味が薄く、UX/仕様ともに不自然

## 推奨案

- 推奨:
  - `案 A`
- 理由:
  - contract、保存モデル、refresh モデルの 3 点を最も素直に一致させられる
  - import preflight / validate / ambiguity detection を同じ identity tuple で揃えやすい
  - same-repo duplicate は引き続き防ぎつつ、foreign overlap だけを正しく許容できる

## 実装時の注意

- `guard_github_issue_uniqueness` と `validate_github_issue_numbers_unique` を同じ helper に寄せる
- key は少なくとも `(repo_owner, repo_name, issue_number)`、repo 未設定は `(None, None, issue_number)` で正規化する
- error message は `github.issue_number=123` だけでなく必要に応じて `repo=owner/name` も含める
- regression として次を固定する:
  - same repo `#123` + same repo `#123` は fail
  - same repo `#123` + foreign repo `#123` は allow success
  - validator でも同じ判定になる

## 結論

- review は `valid`
- 修正は `必要`
- 最良の修正方針は `repo-aware uniqueness key への統一`
