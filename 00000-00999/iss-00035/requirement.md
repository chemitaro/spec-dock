---
種別: 要件定義書（Issue）
ID: "iss-00035"
タイトル: "Sync ADR Symlink Mirror"
関連GitHub: ["#35"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
親: ["epic-00033", "init-local-00003"]
---

# iss-00035 Sync ADR Symlink Mirror — 要件定義（WHAT / WHY）

## 目的
- `sync` が top-level `spec-dock/adrs/` を generated symlink mirror として毎回安全に再構築できるようにする。
- stale symlink を残さないことを最優先に、non-symlink 環境でも終状態を一意にする。

## 背景・現状
- 現状の挙動:
  - top-level ADR browse view の contract はまだ未実装で、原本からの generated mirror も存在しない。
- 現状の課題:
  - ADR を集約して見たい要件に対し、source-of-truth を増やさずに一覧性を提供できていない。
  - non-symlink 環境や rename / delete 後の stale cleanup の終状態が未実装だと、mirror が壊れやすい。
- 再現手順:
  1. ADR 原本を追加・変更・削除しても、top-level browse view は自動追従しない。
  2. mirror 再生成 contract がないため、stale symlink 不残存を保証できない。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock sync`
  - Filesystem:
    - `spec-dock/adrs/`
  - Artifact:
    - sync 出力と warning
- 情報源:
  - `epic-00033` requirement / design / plan
  - `epic-00033/discussions/001-adr-adr-symlink-mirror-without-index.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - ADR を横断参照したい maintainer
- 代表シナリオ:
  - `sync` 実行後に `spec-dock/adrs/` から current ADR 一覧を確認する。
  - symlink 非対応環境でも stale link を残さず運用を継続する。

## スコープ
- MUST:
  - `sync` が `spec-dock/adrs/` を clear-then-rebuild する contract を固定する。
  - timestamp grammar 前提の ADR 走査と mirror 再生成を扱う。
  - stale symlink 不残存と non-symlink empty-dir warning success を acceptance に入れる。
- MUST NOT:
  - index / manifest を追加しない。
  - `adrs/` を source-of-truth とみなさない。
- OUT OF SCOPE:
  - ADR filename grammar 自体の策定
  - provider / dogfooding docs parity の全面更新
  - local-only identity contract の変更

## 境界
- Always:
  - ADR 原本の source-of-truth は各 scope の `discussions/` に残る。
  - `adrs/` は generated view で、`sync` が毎回再生成する。
  - non-symlink 環境では empty generated directory + warning success を採用する。
- Ask:
  - warning message の wording や補足 guidance は実装時に最小限でよい。
- Never:
  - stale symlink を残す。
  - `adrs/` を手編集前提の管理面にする。

## 非交渉制約
- clear-then-rebuild を崩さない。
- rename / delete 後も stale link を残さないことを成功条件の中心に置く。
- legacy grandfathered ADR を自動 rename しない。

## 前提
- `iss-00036` の naming contract が前段で固定される。
- ADR 原本は issue / epic / initiative 配下の `discussions/` に存在する。
- symlink を作れない環境があり得る。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - ADR 原本が存在する
  - When:
    - `./spec-dock/scripts/spec-dock sync` を実行する
  - Then:
    - `spec-dock/adrs/` は毎回クリア後に再生成され、current ADR 原本を指す symlink mirror になる
  - 観測点:
    - sync tests
    - filesystem assertions
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - ADR 原本の rename / delete が発生した
  - When:
    - `sync` を再実行する
  - Then:
    - 旧原本を指す stale symlink は残らない
  - 観測点:
    - clear-then-rebuild evidence
    - stale link 不残存 assertions
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - symlink 非対応環境である
  - When:
    - `sync` を実行する
  - Then:
    - `spec-dock/adrs/` は空の generated directory として残るか再作成され、warning を出しつつ成功扱いになる
  - 観測点:
    - non-symlink warning evidence
    - sync exit=0

## 例外・エッジケース
- EC-001:
  - 条件:
    - legacy grandfathered ADR と timestamp-based ADR が混在する
  - 期待:
    - mirror 走査は許可された対象だけを扱い、legacy を自動 rename しない
  - 観測点:
    - sync scan tests
- EC-002:
  - 条件:
    - `adrs/` に古い symlink や手動作成物が残っている
  - 期待:
    - clear-then-rebuild により generated state が毎回初期化される
  - 観測点:
    - filesystem cleanup tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock sync`
  - Output:
    - `spec-dock/adrs/` が current original ADRs に整合した generated mirror になる

## 用語（ドメイン語彙）
- TERM-001:
  - ADR mirror:
    - `spec-dock/adrs/` に再生成される symlink ベースの一覧 view
- TERM-002:
  - stale symlink:
    - rename / delete 済み ADR 原本を指し続ける不要 link
- TERM-003:
  - non-symlink empty-dir success:
    - symlink 非対応環境で `adrs/` を空の generated directory として残しつつ warning success にする終状態

## 未確定事項
- なし:
  - mirror contract の方針は epic spec で固定済み
