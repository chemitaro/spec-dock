---
種別: 要件定義書（Issue）
ID: "iss-00052"
タイトル: "Reject Non Canonical Git Issue Targets"
関連GitHub: ["#52"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-04-07"
親: ["epic-00048", "init-local-00002"]
---

# iss-00052 Reject Non Canonical Git Issue Targets — 要件定義（WHAT / WHY）

## 目的
- `active set` が non-canonical な GitHub issue target を fail-closed で拒否し、`import issue` と同じ入力契約にそろう状態を作る。
- malformed target を shorthand 解釈で通してしまう経路をなくし、active selection の入力検証を docs 契約どおりに戻す。

## 背景・現状
- 現状の挙動:
  - `import issue` は `git@github.com:owner/repo/issues/<n>` のような non-canonical URL-like target を reject する。
  - `active set` は canonical GitHub issue URL、`#<n>`、`<n>`、node id を受け付ける契約になっている。
  - しかし実際には `active set git@github.com:owner/repo/issues/<n>` が `github#<n>` として受理される。
- 現状の課題:
  - `workflow_issue.md` と `reference_github.md` が期待する fail-closed 契約と、`active set` 実装の挙動が不一致になっている。
  - malformed target が成功扱いになることで、repo scope 検証や command parity のバグを覆い隠す。
- 再現手順:
  1. current repo 上で linked issue を持つ workspace を用意する。
  2. `./spec-dock/scripts/spec-dock active set git@github.com:chemitaro/spec-dock-completion-guard-current-20260407/issues/1` を実行する。
  3. 現状は invalid target で失敗せず、`target=github#1` 相当として成功する。
- 観測点:
  - UI:
    - CLI が `spec-dock: ok (active set)` を返してしまう。
  - HTTP:
    - なし。target parsing 段階のローカル判定。
  - DB:
    - なし。
  - Log:
    - bug report discussion と manual test execution log に再現結果が記録されている。
- 情報源:
  - `spec-dock/active/issue/discussions/20260407t131500z-disc-active-set-non-canonical-git-target-bug-report.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_import.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `active set` を手動実行する operator
  - `active set` を呼び出す agent / host adapter / delegated workflow
- 代表シナリオ:
  - agent が active issue をセットする前に GitHub issue target を解決する
  - operator が URL をコピペして `active set` を実行する
  - negative-path manual test で malformed target handling を検証する

## スコープ
- MUST:
  - `active set` の positional `<target>` が URL-like 文字列を受け取った場合、canonical GitHub issue URL の full match のみを GitHub issue target として扱うこと。
  - `git@github.com:owner/repo/issues/<n>`、`owner/repo/issues/<n>`、`example.com/.../issues/<n>` など canonical でない URL-like target を invalid target として reject すること。
  - canonical `https://github.com/<owner>/<repo>/issues/<n>`、`#<n>`、`<n>`、node id は既存契約どおり扱うこと。
  - shared parser を通る `deps check <target>` も同じ canonical-only / fail-closed 契約に従うこと。
  - `active set` と `import issue` の malformed target handling が矛盾しないことを自動テストで保証すること。
- MUST NOT:
  - malformed target を `/issues/<n>` の部分一致だけで `github#<n>` にフォールバックしてはならない。
  - canonical URL の repo-scope 解決、deps guard、checkout 既定動作を本 issue で変更してはならない。
- OUT OF SCOPE:
  - `import issue` の repo identity policy 自体の変更
  - foreign canonical URL を `active set` で許可する/しない既存仕様の見直し
  - GitHub CLI 呼び出しや active manifest 書き込みの仕様変更
  - manual test harness 全体の blocker 解消

## 境界
- Always:
  - fail-closed を優先し、曖昧な URL-like input は拒否する。
  - user-facing contract は `workflow_issue.md` / `reference_github.md` と一致させる。
- Ask:
  - なし。現時点では discussion と docs から契約を確定できる。
- Never:
  - non-canonical URL-like target を shorthand とみなして成功扱いにしない。
  - node id / 数値 shorthand の既存成功経路を壊さない。

## 非交渉制約
- provider-side source of truth である `src/spec_dock/assets/spec_dock/...` を基準に修正方針を立てること。
- `active set` は documented contract に従い canonical GitHub issue URL のみを URL target として受理すること。
- docs と test の観測可能な契約を同時にそろえること。

## 前提
- `active set` の target parsing は `commands/targets.py` で行われ、`application/set_active.py` は解決済み `TargetRef` を前提にしている。
- `import issue` は同じ `commands/targets.py` 内の別 parser を使い、URL-like string をより厳格に reject している。
- current docs はすでに canonical-only の方針を明示している。

## 受け入れ条件
- AC-001:
  - Actor:
    - operator / agent
  - Given:
    - linked issue を持つ workspace がある
  - When:
    - `./spec-dock/scripts/spec-dock active set git@github.com:owner/repo/issues/123`
  - Then:
    - command は非 0 exit で失敗し、invalid target を示す
    - active state は更新されない
  - 観測点:
    - CLI stderr
    - `tests/cli_runtime/test_active.py` の回帰テスト
- AC-002:
  - Actor:
    - operator / agent
  - Given:
    - current repo と一致する linked issue がある
  - When:
    - `./spec-dock/scripts/spec-dock active set https://github.com/<owner>/<repo>/issues/123`
  - Then:
    - repo-scoped GitHub issue target として従来どおり解決される
  - 観測点:
    - 既存 success test
    - active manifest の issue id
- AC-003:
  - Actor:
    - operator / agent
  - Given:
    - linked issue がある
  - When:
    - `./spec-dock/scripts/spec-dock active set 123` または `#123` または `iss-00123`
  - Then:
    - 既存契約どおり解決される
  - 観測点:
    - 既存 `test_active.py` 回帰群
- AC-004:
  - Actor:
    - operator / agent
  - Given:
    - `deps check` が positional `<target>` を shared parser で解釈する
  - When:
    - `./spec-dock/scripts/spec-dock deps check git@github.com:owner/repo/issues/123`
  - Then:
    - `active set` と同様に invalid target として fail-closed する
  - 観測点:
    - CLI stderr
    - `deps check` の回帰テスト

## 例外・エッジケース
- EC-001:
  - 条件:
    - `https://example.com/not-github/issues/123` を `active set` に渡す
  - 期待:
    - canonical GitHub issue URL ではないため reject する
  - 観測点:
    - CLI stderr
- EC-002:
  - 条件:
    - current repo URL が SSH remote (`git@github.com:owner/repo.git`) である
  - 期待:
    - canonical HTTPS issue URL は current repo scope として継続受理される
  - 観測点:
    - existing repo-scoped active set/import tests
- EC-003:
  - 条件:
    - `foo/issues/123` や `owner/repo/issues/123` のような slash を含む URL-like 文字列を渡す
  - 期待:
    - 部分一致で `github#123` に落とさず reject する
  - 観測点:
    - 新規または拡張した parser test / CLI test

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `active set git@github.com:owner/repo/issues/123`
  - Output:
    - `Invalid target ...`
- EX-002:
  - Input:
    - `active set https://github.com/owner/repo/issues/123`
  - Output:
    - `spec-dock: ok (active set) target=github:owner/repo#123 ...`
- EX-003:
  - Input:
    - `import issue git@github.com:owner/repo/issues/123 --title ...`
  - Output:
    - `Invalid target ...`

## 用語（ドメイン語彙）
- TERM-001:
  - canonical GitHub issue URL:
    - `https://github.com/<owner>/<repo>/issues/<n>` の full string を指す。
- TERM-002:
  - non-canonical URL-like target:
    - `issues/` や `/` や `:` を含むが canonical GitHub issue URL full match ではない文字列を指す。
- TERM-003:
  - command parity:
    - 同じ種類の malformed GitHub issue target に対して `active set` と `import issue` が矛盾しないこと。

## 未確定事項
- なし
