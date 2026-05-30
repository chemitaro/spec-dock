---
種別: 要件定義書（Issue）
ID: "iss-00143"
タイトル: "Manage External Git Worktrees"
関連GitHub: ["#143"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["epic-00107", "init-local-00002"]
---

# iss-00143 Manage External Git Worktrees — 要件定義（何を、なぜ行うか）

## 目的

`spec-dock worktree list` / `show` / `remove` を、SpecDock が作成した managed worktree だけでなく、同一 Git repository に属する linked worktree 全体を扱える command surface にする。

Codex Desktop など外部ツールが作成した worktree も、Git が同じ repository の linked worktree として認識しているなら、SpecDock から一覧確認、詳細確認、削除できるようにする。

## 背景・現状

- 現状の挙動:
  - `worktree list` / `show` は Git worktree records を読み、central root namespace 配下を `managed=true`、それ以外を `managed=false` と分類して表示できる。
  - `worktree remove` は `unmanaged` を non-bypassable blocker として扱い、`--force` でも external worktree を削除しない。
  - `worktree list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` を必須とし、未設定または invalid root では fail-fast する。
- 現状の課題:
  - Codex Desktop など spec-dock 外で作成された linked worktree は、同一 repository に属していても `worktree remove` で cleanup できない。
  - external worktree を片付けるには Git command や filesystem cleanup を別途手作業で行う必要があり、worktree 管理面が分断される。
  - `list` / `show` / `remove` が central root 設定に依存するため、Git worktree records だけで判断できる inspection / cleanup まで root 設定にブロックされる。
- 情報源:
  - `discussions/20260530t000000z-scratch-external-worktree-management.md`
  - `discussions/20260530t100431z-research-external-worktree-requirement-analysis.md`
  - `discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md`
  - `discussions/20260530t111421z-interview-worktree-root-requirement-for-external-management.md`
  - `discussions/20260530t112038z-interview-external-worktree-post-remove-cleanup.md`
  - `discussions/20260530t112440z-interview-managed-classification-when-root-absent.md`
  - `discussions/20260530t112713z-interview-codex-desktop-specific-scope.md`
  - 親 epic `epic-00107` の requirement / design / plan
  - 現行実装 `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - 現行 tests `tests/cli_runtime/test_worktree.py`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock repo-local runtime command を使って、複数の linked worktree を inspect / cleanup する maintainer / agent。
- 代表シナリオ:
  - Codex Desktop が同一 repository の linked worktree を作成したあと、operator が `spec-dock worktree list --json` で全 worktree を把握する。
  - agent が `worktree show <target> --json` で external worktree の詳細と削除可否を確認する。
  - operator / agent が `worktree remove <target>` で external worktree を Git-first に削除し、残った target directory も cleanup する。

## スコープ

## 親 Epic への変更関係

この issue は、先行 `iss-00137` で実装された `worktree list` / `show` / `remove` contract の amendment として扱う。

親 `epic-00107` の従来 contract では、`list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` を必須とし、`remove` は managed worktree のみに限定していた。今回の user-approved clarification により、`worktree create` の central root contract は維持したまま、`list` / `show` / `remove` は Git worktree records を正本にする all-linked-worktree management へ拡張する。

この amendment は E-RQ-011 / E-RQ-012 / E-AC-012 / E-AC-013 の inventory / cleanup contract を更新する。E-RQ-008 の Codex app internals / Handoff 非再実装、E-RQ-010 の provider-side source of truth、branch deletion / prune / repair の対象外は維持する。

- 必須:
  - `worktree list` / `show` / `remove` は、Git が認識する同一 repository の linked worktree 全体を対象にする。
  - `worktree remove` は external / unmanaged worktree を削除対象に含める。
  - `managed` / `unmanaged` は削除可否 blocker ではなく、SpecDock-created managed worktree と external worktree を区別する diagnostic として残す。
  - `worktree list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` 未設定でも動作する。
  - `worktree create` は引き続き `SPEC_DOCK_WORKTREE_ROOT` を必須にする。
  - `worktree remove` は Git `worktree remove` 成功後、resolved target path が残る場合に filesystem cleanup する。
  - `worktree remove` は related local branch を削除しない。
  - provider-side source of truth は `src/spec_dock/assets/spec_dock/...` とし、dogfooding workspace は検証・反映対象として扱う。
- 禁止:
  - main checkout / current checkout / bare worktree / stale record を削除すること。
  - `--force` によって main / current / bare / stale record の guard を bypass すること。
  - branch deletion を remove の副作用にすること。
  - `git worktree prune` / repair を remove の副作用にすること。
  - Codex Desktop の Handoff、environment setup、metadata cleanup、`$CODEX_HOME/worktrees` detection を実装 scope に含めること。
  - provider-side source of truth を飛ばして dogfooding workspace だけを編集すること。
- 対象外:
  - `worktree create` の placement / naming / bootstrap contract の変更。
  - worktree status dashboard。
  - stale record repair / prune。
  - orphan directory cleanup。
  - branch deletion option。
  - Codex Desktop 固有 lifecycle の再実装。

## 境界

- 常に行う:
  - `list` / `show` / `remove` の source of truth は Git worktree records とする。
  - `remove` は削除直前に target を再解決し、安全 guard を再評価する。
  - `remove` は Git-first に実行し、Git remove が失敗した場合は filesystem cleanup を行わない。
  - Git remove 成功後の filesystem cleanup は resolved target path のみを対象にし、parent directory、central root、namespace directory は削除しない。
  - JSON output は agent が target、origin / classification、削除可否、削除結果を判断できる情報を返す。
- 判断が必要:
  - `managed_classification_available` / `classification_reason` / origin diagnostic などの具体 field 名。
  - symlink / path containment の具体設計。
- 行わない:
  - Git worktree record に存在しない path を remove target として cleanup しない。
  - branch name target を受け付けない。
  - Codex Desktop 固有 path を特別扱いしない。

## 非交渉制約

- `worktree create` は引き続き `SPEC_DOCK_WORKTREE_ROOT` を必須にする。
- `worktree list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` なしで動作する。
- `managed` は JSON 互換性のため boolean として維持する。
- root がないため managed classification できない場合は、`managed=false` とし、classification unavailable を別 diagnostic で表す。
- `branch_deleted` は常に `false` とする。
- destructive cleanup は Git worktree record から解決した target path だけに限定する。

## 前提

- 実行環境に Git CLI があり、対象 repository で `git worktree list --porcelain` が成功する。
- `worktree remove` の dirty / locked / untracked に対する基本挙動は Git `worktree remove` / `worktree remove --force` に従う。
- Codex Desktop generated worktree は、特別な Codex metadata ではなく Git linked worktree として扱う。

## 受け入れ条件

- AC-001: 全 linked worktree の一覧表示
  - アクター: agent / operator
  - 前提: Git repo に main checkout、SpecDock-created managed worktree、external linked worktree がある。
  - 操作: `spec-dock worktree list --json` を実行する。
  - 期待結果: JSON に同一 repo の linked worktree 全体が含まれ、各 record が stable `id`、path、basename、branch、main/current 判定、managed diagnostic、remove 可否 diagnostic を持つ。
  - 観測点: CLI runtime test / JSON assertion。
- AC-002: root なしでの list/show/remove
  - アクター: agent / operator
  - 前提: `SPEC_DOCK_WORKTREE_ROOT` が未設定で、Git repo に external linked worktree がある。
  - 操作: `worktree list --json`、`worktree show <target> --json`、`worktree remove <target> --json` を実行する。
  - 期待結果: `list` / `show` / `remove` は root missing を理由に fail-fast せず、Git worktree records に基づいて動作する。classification unavailable は diagnostic として表される。
  - 観測点: CLI runtime test / JSON assertion。
- AC-003: create は root 必須を維持
  - アクター: operator
  - 前提: `SPEC_DOCK_WORKTREE_ROOT` が未設定。
  - 操作: `worktree create <label>` を実行する。
  - 期待結果: command は fail-fast し、worktree / branch / bootstrap side effect を作らない。
  - 観測点: existing regression test / CLI runtime test。
- AC-004: external worktree remove
  - アクター: agent / operator
  - 前提: target は同一 repo の external linked worktree であり、main/current/bare/stale ではない。
  - 操作: `worktree remove <target> --json` を実行する。
  - 期待結果: Git worktree record が削除され、target path が残る場合はその directory が cleanup され、related local branch は削除されない。
  - 観測点: CLI runtime test、`git worktree list --porcelain` assertion、filesystem assertion、branch existence assertion。
- AC-005: main/current/bare/stale は拒否
  - アクター: agent / operator
  - 前提: target が main checkout、current checkout、bare worktree、または path missing / record missing の stale target である。
  - 操作: `worktree remove <target> --force --json` を実行する。
  - 期待結果: command は削除を拒否し、Git remove と filesystem cleanup を実行しない。JSON error は blocker reason を含む。
  - 観測点: CLI runtime test / JSON assertion / filesystem assertion。
- AC-006: managed diagnostic の互換性
  - アクター: agent
  - 前提: valid `SPEC_DOCK_WORKTREE_ROOT` があり、managed worktree と external worktree が存在する。
  - 操作: `worktree list --json` / `worktree show <target> --json` を実行する。
  - 期待結果: `managed` は boolean として返り、SpecDock-created managed worktree と external worktree を区別できる diagnostic が含まれる。
  - 観測点: JSON schema / payload assertion。
- AC-007: docs / dogfooding parity
  - アクター: maintainer
  - 前提: provider-side docs / runtime / tests が更新されている。
  - 操作: shipped docs と dogfooding workspace を確認する。
  - 期待結果: docs は root requirement、all-linked-worktree scope、external remove cleanup、Codex-specific non-scope を正しく説明している。
  - 観測点: docs inspection、`validate`、targeted tests。

## 例外・エッジケース

- EC-001: ambiguous target
  - 条件: stable id / basename / absolute path target が複数の worktree に一致する。
  - 期待: command は候補付き fatal error を返し、remove では削除しない。
  - 観測点: CLI runtime test / JSON error payload。
- EC-002: branch target
  - 条件: target が branch name にだけ一致する。
  - 期待: branch name target は対象外として拒否する。
  - 観測点: CLI runtime test。
- EC-003: Git remove failure
  - 条件: Git が dirty / locked / untracked などを理由に `git worktree remove` を拒否する。
  - 期待: command は Git error を surfaced error として返し、filesystem cleanup は行わない。`--force` 指定時は Git force semantics に従う。
  - 観測点: CLI runtime test / filesystem assertion。
- EC-004: invalid root with list/show/remove
  - 条件: `SPEC_DOCK_WORKTREE_ROOT` が invalid path を指す。
  - 期待: `list` / `show` / `remove` は root invalid を availability blocker にせず、classification diagnostic で表す。
  - 観測点: CLI runtime test / JSON assertion。
- EC-005: symlink or containment risk
  - 条件: resolved target path または parent が symlink / unexpected path を含み、cleanup 範囲が曖昧になる。
  - 期待: design で定義した containment guard に従い、危険な cleanup は拒否する。
  - 観測点: unit / runtime test。

## 入力→出力例

- EX-001: root なし list
  - 入力: `SPEC_DOCK_WORKTREE_ROOT` 未設定で `spec-dock worktree list --json`
  - 出力: `status=ok`、`worktrees[]`、`managed=false`、classification unavailable diagnostic。
- EX-002: external remove
  - 入力: `spec-dock worktree remove /abs/path/to/external-worktree --json`
  - 出力: `status=ok`、`removed_record=true`、`removed_directory=true|false`、`branch_deleted=false`。

## 用語

- TERM-001: Git linked worktree
  - `git worktree list --porcelain` に record として現れる、同一 repository に紐づく worktree。
- TERM-002: SpecDock-created managed worktree
  - `spec-dock worktree create` の placement contract に従い、valid `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` namespace 配下に存在する linked worktree。
- TERM-003: external / unmanaged worktree
  - SpecDock-created managed worktree ではないが、同一 repository の Git linked worktree として認識される worktree。
- TERM-004: classification unavailable
  - `SPEC_DOCK_WORKTREE_ROOT` が未設定または invalid で、SpecDock-created managed worktree かどうかを判定できない状態。

## 未確定事項

- Q-001:
  - 質問: JSON diagnostic の具体 field 名をどうするか。
  - 推奨案: design phase で既存 JSON payload との互換性を見て決める。
  - 影響範囲: `application.contracts`、presentation、tests、docs。
- Q-002:
  - 質問: symlink / containment guard の詳細をどう実装するか。
  - 推奨案: design phase で `resolved target path only` を守る最小 guard として固定する。
  - 影響範囲: remove use case、filesystem cleanup tests。
