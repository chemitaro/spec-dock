---
種別: 要件定義書（Issue）
ID: "iss-00035"
タイトル: "Sync ADR Symlink Mirror"
関連GitHub: ["#35"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
親: ["epic-00033", "init-local-00003"]
---

# iss-00035 Sync ADR Symlink Mirror — 要件定義（WHAT / WHY）

## 目的
- `sync` が top-level `spec-dock/adrs/` を generated symlink mirror として毎回安全に再構築できるようにする。
- mirror layout は flat とし、各 mirror entry は採用された ADR 原本の basename をそのまま `spec-dock/adrs/<basename>` に写す。
- stale symlink を残さないことを最優先に、non-symlink 環境でも終状態を一意にする。

## 背景・現状
- 現状の挙動:
  - top-level ADR browse view の contract はまだ未実装で、原本からの generated mirror も存在しない。
  - 現在の `sync` 実装は `.agent/index*.json` / `tree*.json` / `deps-issues.*` / `dashboard.md` までを出力するが、`spec-dock/adrs/` は artifact writer 契約にも含まれていない。
  - `iss-00036` により `new doc adr` の新規生成 basename は timestamp-prefix contract へ切り替わっており、本 issue はその新 contract を前提に mirror 側を追加する段階である。
  - 親 epic requirement / design は、legacy ADR を naming 上の grandfathered artifact として保持しつつ、mirror 入力は新 contract に一致する ADR 原本だけを対象とする方針へ整合済みである。
- 現状の課題:
  - ADR を集約して見たい要件に対し、source-of-truth を増やさずに一覧性を提供できていない。
  - non-symlink 環境や rename / delete 後の stale cleanup の終状態が未実装だと、mirror が壊れやすい。
  - backward compatibility を持ち込んで legacy ADR まで mirror 対象にすると、scan / filter / validation / test matrix が不必要に複雑になる。
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
  - mirror 対象は、`spec-dock/initiatives/**/discussions/*.md` を initiative / epic / issue の全 scope 横断で走査したうえで、`iss-00036` の timestamp ADR basename contract に適合し、かつ `new doc adr` template が出力する ADR front matter contract（少なくとも `種別: ADR` と `ID: "<doc_id>"` と `親: ["<scope_id>"]`）が観測でき、さらに `親` の `<scope_id>` がその原本を含む scope path と一致する原本に限定する。
  - mirror path は flat な `spec-dock/adrs/<basename>` とし、basename は原本 ADR の basename をそのまま使う。
  - stale symlink 不残存と non-symlink empty-dir warning success を acceptance に入れる。
  - basename collision は clear 前の preflight で検出し、collision 発生時は `sync` 全体を failure として終了し、`spec-dock/adrs/` を変更しない。
  - warning success へ劣化してよいのは、「環境として symlink がサポートされていない」と preflight で分類できた場合だけとし、その他の symlink / write failure は hard failure にする。
- MUST NOT:
  - index / manifest を追加しない。
  - `adrs/` を source-of-truth とみなさない。
  - legacy ADR 互換のための fallback scan / dual-mode を持ち込まない。
  - mirror basename collision を silent overwrite や last-write-wins で解決しない。
- OUT OF SCOPE:
  - ADR filename grammar 自体の策定
  - legacy ADR の救済、移行、mirror 掲載
  - provider / dogfooding docs parity の全面更新
  - local-only identity contract の変更

## 境界
- Always:
  - ADR 原本の source-of-truth は各 scope の `discussions/` に残る。
  - `adrs/` は generated view で、`sync` が毎回再生成する。
  - mirror 対象は `new doc adr` contract で生成されたと観測できる ADR 原本のみとし、判定は path + basename + ADR front matter contract で行う。
  - mirror entry は原本 basename を保った flat layout の `spec-dock/adrs/<basename>` とする。
  - 同一 basename に複数の有効 ADR 原本が衝突する場合、`sync` は clear 前の preflight で fail-fast し、overwrite せず、`spec-dock/adrs/` の事前状態を維持する。
  - non-symlink 環境では empty generated directory + warning success を採用する。
- Ask:
  - warning message の wording や補足 guidance は実装時に最小限でよい。
- Never:
  - stale symlink を残す。
  - `adrs/` を手編集前提の管理面にする。
  - legacy ADR を拾うための互換分岐を足す。

## 非交渉制約
- clear-then-rebuild を崩さない。
- rename / delete 後も stale link を残さないことを成功条件の中心に置く。
- legacy ADR は mirror 対象外とし、互換のために scan / rename / rescue を行わない。
- basename collision は silent overwrite ではなく sync failure として露出させる。
- basename collision failure は clear-then-rebuild 開始前に検出し、`spec-dock/adrs/` に partial rebuild や empty-dir 破壊を残さない。

## 前提
- `iss-00036` の naming contract が前段で固定される。
- ADR 原本は issue / epic / initiative 配下の `discussions/` に存在する。
- symlink を作れない環境があり得る。
- backward compatibility は不要であり、legacy ADR が残っていても本 issue の contract では無視してよい。
- `new doc adr` template の front matter contract は mirror source 判定に利用できる。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - ADR 原本が存在する
  - When:
    - `./spec-dock/scripts/spec-dock sync` を実行する
  - Then:
    - `spec-dock/adrs/` は毎回クリア後に再生成され、`spec-dock/initiatives/**/discussions/*.md` を全 scope 横断で走査して見つかる原本のうち、basename が timestamp ADR grammar に一致し、front matter が `new doc adr` contract に一致し、`親` と containing scope path が一致する、workspace 上に存在する全 ADR 原本だけを、flat な `spec-dock/adrs/<basename>` symlink mirror として持つ
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
    - legacy ADR が workspace 内に残っている
  - 期待:
    - mirror 走査は整合済み epic / issue contract に従って legacy ADR を対象外とし、basename や body を legacy 向けに救済せず無視する
  - 観測点:
    - sync scan tests
- EC-002:
  - 条件:
    - `discussions/` 配下に timestamp ADR basename を持つが、ADR front matter contract が壊れている手動作成ファイルが存在する
  - 期待:
    - mirror 走査は basename だけで採用せず、path + basename + front matter contract を満たす原本だけを mirror 対象にする
  - 観測点:
    - sync scan tests
- EC-003:
  - 条件:
    - `adrs/` に古い symlink や手動作成物が残っている
  - 期待:
    - clear-then-rebuild により generated state が毎回初期化される
  - 観測点:
    - filesystem cleanup tests
- EC-004:
  - 条件:
    - 異なる scope にある有効 ADR 原本どうしが、同じ basename を `spec-dock/adrs/<basename>` へ要求する
  - 期待:
    - `sync` は basename collision を clear 前に明示的 failure として扱い、silent overwrite や last-write-wins を行わず、`spec-dock/adrs/` の事前状態を保持したまま非0終了または同等の failure evidence を返す
  - 観測点:
    - sync collision tests
    - sync exit failure evidence
- EC-005:
  - 条件:
    - basename と front matter は一見有効だが、`親` の `<scope_id>` と原本が置かれている scope path が一致しない
  - 期待:
    - mirror source として採用せず、scope mismatch を除外できる
  - 観測点:
    - sync scan tests
- EC-006:
  - 条件:
    - symlink create が失敗する
  - 期待:
    - 環境として symlink unsupported と preflight で分類できた場合だけ warning success に劣化し、それ以外の symlink / write failure は hard failure にする
  - 観測点:
    - sync fallback classification tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock sync`
  - Output:
    - `spec-dock/adrs/` が、workspace 上に存在し source contract を満たす全 ADR 原本に整合した generated mirror になる

## 用語（ドメイン語彙）
- TERM-001:
  - ADR mirror:
    - `spec-dock/adrs/<basename>` に再生成される flat な symlink ベースの一覧 view
- TERM-002:
  - stale symlink:
    - rename / delete 済み ADR 原本を指し続ける不要 link
- TERM-003:
  - non-symlink empty-dir success:
    - symlink 非対応環境で `adrs/` を空の generated directory として残しつつ warning success にする終状態

## 未確定事項
- なし:
  - mirror contract の方針は epic spec で固定済み
