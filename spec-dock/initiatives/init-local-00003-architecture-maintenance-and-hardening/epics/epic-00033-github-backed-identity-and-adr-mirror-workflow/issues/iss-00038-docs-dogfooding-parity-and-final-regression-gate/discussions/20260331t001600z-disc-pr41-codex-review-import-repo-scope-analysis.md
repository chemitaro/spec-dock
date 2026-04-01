# PR #41 Codex Review Analysis — Numeric Import Repo Scope Enforcement

## 対象レビュー
- reviewer:
  - Codex
- comment:
  - `_require_numeric_issue_import_repo_scope` が `kind == "issue"` のときしか効かないため、`import initiative 123` / `import epic 123` が origin 未解決でも通り、repo scope のない GitHub linkage を持つ invalid metadata を作る可能性がある
- source:
  - `https://github.com/chemitaro/spec-dock/pull/41#discussion_r3009931318`

## 事実確認
- 対象実装:
  - [import_node.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py#L178)
  - [import_node.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py#L304)
  - [import_node.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py#L116)
- 現状では `_require_numeric_issue_import_repo_scope(...)` が `kind != "issue"` なら即 return する。
- 一方で `build_linked_create_request(...)` は `current_repo_slug` が解決できない場合、`github_issue_number` を保持したまま `github_repo_owner` / `github_repo_name` を `None` にする。
- `import_node_core(...)` は preflight の後に `build_linked_create_request(...)` を使って local write に進むため、initiative/epic numeric import は unresolved origin 下でも unscoped GitHub linkage を持つ node を作りうる。
- その後の validation は `legacy unscoped github linkage` を reject する既存 contract を持つ:
  - [validation.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py#L144)
  - [test_validate.py](/srv/mount/spec-dock/tests/cli_runtime/test_validate.py#L109)
- 既存テストは issue import の fail-fast だけをカバーしている:
  - [test_import.py](/srv/mount/spec-dock/tests/cli_runtime/test_import.py#L1078)
  - [test_runtime_import_s10.py](/srv/mount/spec-dock/tests/cli_runtime/test_runtime_import_s10.py#L995)
- さらに、既存の issue 分析 docs でも「`initiative / epic / issue` の import は current repo scope を解決できなければ fail-fast する」が expected state として明文化されている:
  - [005-disc-numeric-import-no-origin-fail-closed-fix-analysis.md](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/discussions/005-disc-numeric-import-no-origin-fail-closed-fix-analysis.md#L76)

## 妥当性判定
- 判定:
  - 妥当
- 理由:
  - 指摘は spec と既存 validation contract の両方に整合している。
  - しかも問題が起きる場所は preflight ではなく local write 後なので、fail-closed 設計の趣旨に反する。

## 影響度
- severity:
  - high
- user impact:
  - import コマンドが成功したように見える
  - しかし作られた metadata は invalid で、直後の `validate` / `sync` / workflow 継続で壊れる
  - 「成功後に壊れる」ため、user trust と recovery cost の両方が悪い

## 修正要否
- before merge:
  - 必須
- rationale:
  - これは docs wording ではなく runtime contract の破綻可能性。
  - mandatory GitHub linkage と fail-closed import を main に入れる PR で、この穴を残すのは一貫しない。

## 修正案
- Option A:
  - `_require_numeric_issue_import_repo_scope` を kind 共通の guard に拡張する
  - 併せて関数名も `_require_numeric_import_repo_scope` のように一般化する
  - initiative / epic / issue の 3 種別すべてで、numeric target かつ repo scope 未指定、かつ current repo slug 未解決なら preflight fail-fast にする
  - pros:
    - 修正点が import preflight に集中する
    - 既存 contract と issue analysis の expected state に最も自然に一致する
    - no-write / fail-fast テストを追加しやすい
  - cons:
    - 関数名変更を含むため call site と mirror/test 更新が必要
- Option B:
  - `build_linked_create_request(...)` 側で、initiative/epic も repo scope が欠けたら例外を投げる
  - pros:
    - write 前には止められる
    - call site の変更は少ない
  - cons:
    - import-specific preflight ruleが data-construction 側へ分散する
    - numeric import guard の責務が見えにくくなる
- Option C:
  - validation を緩め、initiative/epic の unscoped GitHub linkage を許可する
  - pros:
    - import 成功後に validate failure しなくなる
  - cons:
    - GitHub mandatory linkage contract と衝突する
    - PR 全体の方向性を崩す
    - 不採用

## 推奨案
- recommended:
  - Option A
- reason:
  - 問題の本質は「numeric import preflight の適用範囲が issue にだけ狭すぎる」ことなので、guard を spec どおり `initiative / epic / issue` へ広げるのが最も筋がよい。
  - これなら local write より前に止まり、invalid metadata を生成しない。
  - 既存の `issue` 用テストパターンを initiative/epic に横展開できるため、回帰防止も明快。

## 具体化方針
- provider runtime:
  - [import_node.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py)
  - `_require_numeric_issue_import_repo_scope` を全 kind 対象へ拡張し、名称も責務に合わせて見直す
- dogfooding mirror:
  - `spec-dock/scripts/spec_dock_runtime/application/import_node.py`
- tests:
  - CLI layer に initiative/epic numeric import の no-origin fail-fast test を追加
  - application layer に initiative/epic import use case の no-origin fail-fast test を追加
  - no-write guarantee も確認する

## consultant view
- このレビューは「strict すぎる」ではなく「strictness の適用範囲が半端」という指摘で、技術的に筋が通っている。
- 失敗するなら最初に失敗させるべきで、成功後に invalid metadata を残す設計は優先的に潰すべき。
