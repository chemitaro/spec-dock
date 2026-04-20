---
種別: 要件定義書（Issue）
ID: "iss-00082"
タイトル: "Fail fast on malformed node metadata"
関連GitHub: ["#82"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-20"
親: ["epic-00080", "init-00079"]
---

# iss-00082 Fail fast on malformed node metadata — 要件定義（WHAT / WHY）

## 目的
- `load_node_records()` が malformed `.meta.json` を silent skip して graph を部分的に読み込む挙動を廃止し、node metadata integrity violation として fail-fast させる。
- maintainer が壊れた metadata の path を即座に特定できる error contract を導入する。

## 背景・現状
- 現状の挙動:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` と dogfooding mirror の `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py` では、`load_node_records()` が `.meta.json` を読み込んだあと、`type` または `id` を `str(...).strip()` で正規化し、結果が空なら `continue` している。
- 現状の課題:
  - malformed node が fail せず読み飛ばされるため、maintainer は metadata corruption に気づけないまま partial graph を扱ってしまう。
  - PR review では、この silent skip が node integrity contract を壊す P1 として指摘されている。
- 再現手順:
  1. node directory の `.meta.json` の `type` または `id` を欠落、空文字、または空白のみの文字列にする。
  2. graph load / repo read path から `load_node_records()` を通す。
  3. 現状は RuntimeError にならず、その node だけ読み飛ばされる。
- 観測点:
  - Code:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
    - `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - Review:
    - Codex review on PR `#1821`
  - Runtime behavior:
    - graph load / repo read path
- 情報源:
  - 2026-04-17 `pr review and staging failure analysis`
  - `load_node_records()` 実装
  - `deps check` / `sync --github` による repo state 確認

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - corrupted metadata を修復したい maintainer
  - runtime contract を保守する implementer / reviewer
- 代表シナリオ:
  - node metadata を誤編集した直後に graph load が fail-fast し、どの path が壊れているか即時に把握したい

## スコープ
- MUST:
  - `.meta.json` の `type` が正規化後に非空文字列でない場合を integrity violation として fail-fast する
  - `.meta.json` の `id` が正規化後に非空文字列でない場合を integrity violation として fail-fast する
  - error message に壊れた `meta_path` を含める
  - provider-side source of truth と dogfooding mirror の挙動を揃える
- MUST NOT:
  - malformed node を silent skip しない
  - valid metadata の node 読み込み挙動を壊さない
  - external staging failure をこの issue の修正対象に含めない
- OUT OF SCOPE:
  - external consumer repo の test / workflow 修正
  - metadata schema の大規模再設計
  - `type` / `id` 以外の validation 範囲拡張

## 境界
- Always:
  - failure surface は graph load / repo read path に統一する
  - malformed metadata は fail-closed で扱う
- Ask:
  - 追加 validation を広げる必要が本当にあるか
- Never:
  - node metadata corruption を warning や ignore で済ませない
  - background evidence の staging flaky failure をこの issue の acceptance に入れない

## 非交渉制約
- provider-side source of truth は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
- dogfooding mirror `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py` も parity を保つ
- spec は malformed metadata fail-fast に閉じる

## 前提
- `type` と `id` は node identity の最小必須フィールドであり、`.strip()` 後に非空文字列である必要がある
- 現状の skip は intentional contract ではなく bug とみなす

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - node directory の `.meta.json` の `type` が欠落している、空文字である、空白のみである、または非文字列値である
  - When:
    - `load_node_records()` を通る path を実行する
  - Then:
    - RuntimeError で fail し、error message に `meta_path` が含まれる
  - 観測点:
    - targeted unit / runtime tests
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - node directory の `.meta.json` の `id` が欠落している、空文字である、空白のみである、または非文字列値である
  - When:
    - `load_node_records()` を通る path を実行する
  - Then:
    - RuntimeError で fail し、error message に `meta_path` が含まれる
  - 観測点:
    - targeted unit / runtime tests
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - valid `.meta.json` を持つ node 群
  - When:
    - graph load / repo read path を実行する
  - Then:
    - 既存どおり node records が読み込まれる
  - 観測点:
    - regression tests
- AC-004:
  - Actor:
    - reviewer
  - Given:
    - issue spec と research を確認する
  - When:
    - fix scope を判断する
  - Then:
    - external staging failure は background evidence としてのみ残り、この issue の修正対象に含まれていない
  - 観測点:
    - requirement / design / research

## 例外・エッジケース
- EC-001:
  - 条件:
    - `.meta.json` 自体が object ではない
  - 期待:
    - 既存の `Invalid .meta.json (expected object)` error contract を維持する
  - 観測点:
    - regression tests
- EC-002:
  - 条件:
    - provider-side source を修正したが dogfooding mirror が古い
  - 期待:
    - parity 差分として扱い、mirror も揃える
  - 観測点:
    - changed files review
- EC-003:
  - 条件:
    - staging failure analysis を issue に添付する
  - 期待:
    - research / non-goal としてのみ記録し、acceptance criteria へ混ぜない
  - 観測点:
    - requirement / research

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `.meta.json` with missing / blank / non-string `type`
  - Output:
    - `RuntimeError: Invalid .meta.json ... missing type ... <meta_path>`
- EX-002:
  - Input:
    - `.meta.json` with missing / blank / non-string `id`
  - Output:
    - `RuntimeError: Invalid .meta.json ... missing id ... <meta_path>`

## 用語（ドメイン語彙）
- TERM-001:
  - malformed node metadata:
    - `type` / `id` など node identity に必要な必須項目が欠落、非文字列、または `.strip()` 後に空になる `.meta.json`

## 未確定事項
- なし:
  - current scope is fixed to malformed metadata fail-fast
