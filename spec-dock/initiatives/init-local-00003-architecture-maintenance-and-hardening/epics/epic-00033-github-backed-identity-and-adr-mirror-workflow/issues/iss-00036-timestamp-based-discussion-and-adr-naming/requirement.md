---
種別: 要件定義書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
親: ["epic-00033", "init-local-00003"]
---

# iss-00036 Timestamp Based Discussion and ADR Naming — 要件定義（WHAT / WHY）

## 目的
- discussion / ADR filename を timestamp-prefix naming へ切り替え、連番衝突を避けられる naming contract を固定する。
- `new doc` と validation / sync scan 前提のあいだで、同一 grammar を共有できる状態にする。

## 背景・現状
- 現状の挙動:
  - discussion / ADR は sequential naming 前提の運用が残っている。
- 現状の課題:
  - sequential naming は worktree / branch / merge を跨ぐと duplicate sequence を防げない。
  - naming grammar が未固定だと `new doc`、validate、sync scan の契約がずれる。
- 再現手順:
  1. 複数環境で discussion / ADR を連番採番すると番号が衝突しうる。
  2. grammar 未固定のまま mirror 走査を実装すると対象判定がぶれる。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock new doc adr`
    - `./spec-dock/scripts/spec-dock new doc disc`
  - Filesystem:
    - generated filename
  - Validation:
    - naming / scan contract
- 情報源:
  - `epic-00033` requirement / design / plan
  - `epic-00033/discussions/001-adr-adr-symlink-mirror-without-index.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - discussion / ADR を追加する maintainer
- 代表シナリオ:
  - `new doc adr` / `new doc disc` で conflict-resistant な filename を自動生成する。
  - same-second collision でも deterministic に suffix が付く。

## スコープ
- MUST:
  - basename grammar を `<ts>-<kind>-<slug>.md` に固定する。
  - `ts = yyyymmddthhmmssz`、`kind in {adr, disc}`、同秒衝突時 `-<nn>-` suffix を acceptance に入れる。
  - legacy grandfathered docs を自動 rename しない境界を明記する。
- MUST NOT:
  - sequential naming を新規生成しない。
  - legacy docs の一括 rename / migration をこの issue の責務にしない。
- OUT OF SCOPE:
  - `sync` の mirror 再生成そのもの
  - GitHub mandatory node create contract
  - docs parity の全面クローズ

## 境界
- Always:
  - naming grammar は lowercase path 制約に適合する。
  - same-second collision は 2 桁 suffix でのみ吸収する。
  - `001-adr...` / `002-adr...` は grandfathered planning artifacts として保持する。
- Ask:
  - timestamp 精度を秒より細かくする判断は行わない。
- Never:
  - pre-contract legacy docs を自動 rename する。
  - grammar 未固定のまま validate / sync 前提を増やす。

## 非交渉制約
- UTC ベースの grammar を崩さない。
- `t` / `z` は lowercase 固定とする。
- naming contract は validate / sync scan と整合していなければならない。

## 前提
- issue-00034 の create contract が先行している。
- `new doc` の対象は issue / epic / initiative scope の `discussions/` である。
- epic spec で grandfathered legacy docs の扱いが確定している。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `new doc adr` または `new doc disc` を実行する
  - When:
    - 新しい discussion / ADR を作成する
  - Then:
    - basename は `<ts>-<kind>-<slug>.md` grammar で生成される
  - 観測点:
    - naming tests
    - generated file assertions
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - same-second collision が発生する
  - When:
    - 同じ秒に複数 doc を作成する
  - Then:
    - `yyyymmddthhmmssz-<nn>-<kind>-<slug>.md` の 2 桁 suffix が付与される
  - 観測点:
    - collision tests
    - suffix evidence
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - pre-contract legacy docs（`001-adr...` / `002-adr...`）が存在する
  - When:
    - new naming contract と validate 前提を確認する
  - Then:
    - legacy docs は grandfathered として残り、自動 rename / migrate 対象にならない
  - 観測点:
    - docs diff
    - validate contract tests

## 例外・エッジケース
- EC-001:
  - 条件:
    - slug が長い、または複雑である
  - 期待:
    - grammar を壊さず lowercase path 制約に従う
  - 観測点:
    - filename normalization tests
- EC-002:
  - 条件:
    - timestamp grammar に合わない legacy file が存在する
  - 期待:
    - legacy grandfathering と新規生成 contract を混同しない
  - 観測点:
    - validate behavior tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock new doc adr --issue iss-00036 --title "Example Decision"`
  - Output:
    - `yyyymmddthhmmssz-adr-example-decision.md` または同秒時 `yyyymmddthhmmssz-01-adr-example-decision.md`

## 用語（ドメイン語彙）
- TERM-001:
  - timestamp-prefix naming:
    - UTC timestamp を basename 先頭に持つ discussion / ADR filename contract
- TERM-002:
  - grandfathered planning artifact:
    - 新 contract 移行前に作られた legacy doc で、自動 rename 対象にしないもの

## 未確定事項
- なし:
  - naming grammar は epic spec で固定済み
