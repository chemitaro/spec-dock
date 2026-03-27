---
種別: 要件定義書（Issue）
ID: "iss-00038"
タイトル: "Docs Dogfooding Parity and Final Regression Gate"
関連GitHub: ["#38"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
親: ["epic-00033", "init-local-00003"]
---

# iss-00038 Docs Dogfooding Parity and Final Regression Gate — 要件定義（WHAT / WHY）

## 目的
- provider docs / dogfooding docs / tests / generated state の期待値を新 contract に揃え、epic の close-out gate を客観的に閉じる。
- final regression と final spec review record を束ね、`epic-00033` の exit evidence を整える。

## 背景・現状
- 現状の挙動:
  - epic の個別 contract は issue ごとに分離されるが、最終的には provider / dogfooding / generated state の整合をまとめて確認する必要がある。
- 現状の課題:
  - docs parity を個別 issue に散らしたままだと、old local-only / sequential / index assumption の残存が見落とされる。
  - regression gate と final review record が曖昧だと、epic close の客観性が弱くなる。
- 再現手順:
  1. issue-1〜4 の実装が完了しても、provider / dogfooding docs と generated state が揃っているとは限らない。
  2. final review record がないと close evidence の参照先が散逸する。
- 観測点:
  - Docs:
    - provider docs
    - dogfooding docs
  - CLI:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
  - Tests:
    - targeted unittest output
- 情報源:
  - `epic-00033` requirement / design / plan
  - issue-1〜4 の close evidence

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - epic close を行う maintainer / reviewer
- 代表シナリオ:
  - final close 前に docs / validate / sync / regression / review record を一括確認する。
  - old contract assumption が repo docs に残っていないことを確認する。

## スコープ
- MUST:
  - targeted docs list を provider + dogfooding で更新対象として固定する。
  - validate / sync / targeted regression / final spec review record を close evidence に入れる。
  - issue-1〜5 の close evidence を epic exit に結び付ける。
- MUST NOT:
  - close-out の判断を narrative だけに依存させない。
  - old local-only / sequential / index assumption を残したまま epic を閉じない。
- OUT OF SCOPE:
  - create / naming / sync / migration の中核実装そのもの
  - 新しい docs contract の追加拡張

## 境界
- Always:
  - provider docs と dogfooding docs の両方を対象にする。
  - close evidence は named docs diff + command exit=0 + final review record で残す。
- Ask:
  - regression suite の最終選定は実装影響を見て plan で具体化する。
- Never:
  - docs parity を provider side だけで閉じない。
  - `validate` / `sync` / tests / review record のどれかを欠いたまま close しない。

## 非交渉制約
- 更新対象 docs を明示する。
- final spec review verdict は `pass` を要求する。
- epic exit contract と 1:1 に対応する evidence を残す。

## 前提
- issue-1〜4 が完了し、各 close evidence が参照可能である。
- provider docs と dogfooding docs の両方が repo 内に存在する。
- `validate` と `sync` が current contract を観測できる。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - docs parity を確認する
  - When:
    - targeted docs list を比較する
  - Then:
    - provider / dogfooding の `reference_github.md` / `reference_naming.md` / `reference_sync.md` で old local-only / sequential / index assumption が除去されている
  - 観測点:
    - targeted docs diff
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - current repo state を検証する
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する
  - Then:
    - 両コマンドが exit=0 で成功し、generated state が current contract と整合する
  - 観測点:
    - command outputs
- AC-003:
  - Actor:
    - maintainer / reviewer
  - Given:
    - epic 対象の tests と issue close evidence がある
  - When:
    - final regression と final spec review を確認する
  - Then:
    - targeted unittest output が exit=0 であり、final spec review record の verdict が `pass` である
  - 観測点:
    - unittest output
    - final review record

## 例外・エッジケース
- EC-001:
  - 条件:
    - docs は更新済みだが generated state が古い
  - 期待:
    - close-out にはならず、`sync` / `validate` の実行 evidence を要求する
  - 観測点:
    - command evidence check
- EC-002:
  - 条件:
    - tests は通るが docs に old contract assumption が残っている
  - 期待:
    - docs parity 未達として close を reject する
  - 観測点:
    - docs diff review

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - issue-1〜4 close evidence + targeted docs diff + `validate`/`sync`/unittest outputs
  - Output:
    - epic final close に必要な final review record を作成できる

## 用語（ドメイン語彙）
- TERM-001:
  - targeted docs list:
    - provider と dogfooding の `reference_github.md` / `reference_naming.md` / `reference_sync.md`
- TERM-002:
  - final review record:
    - final spec review verdict と issue close evidence の参照を束ねた close-out 記録

## 未確定事項
- なし:
  - close-out gate の対象は epic spec で固定済み
