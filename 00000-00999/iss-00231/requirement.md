---
種別: 要件定義書（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Inject Trusted Base Branch Codex Review Policy — 要件定義

## 目的
- GitHub Codex review trigger が、PR head 側の未信頼な policy ではなく、PR base SHA 上の project-owned review policy を使って deterministic multiline `@codex review` comment を投稿できるようにする。
- Review trigger の evidence に policy source、policy hash、reviewed head SHA を残し、後続の blocker-centric PR closure が「どの policy でどの head を review したか」を検証できるようにする。

## 背景・現状
- 既存の `trigger_codex_review.sh` は PR head SHA を検証して固定本文 `@codex review` を 1 回投稿する。
- 固定本文は安全だが、repository 固有の review policy や priority guidance を Codex review へ渡せない。
- PR head 内の policy をその PR review に使うと、review 対象自身が review instruction を変更できるため trust boundary が崩れる。

## スコープ
- 必須:
  - `.github/codex/review-policy.md` を provider-side bootstrap asset として追加する。
  - `trigger_codex_review.sh` が PR metadata の base SHA を取得できる場合、`<base-sha>:.github/codex/review-policy.md` を読み、policy hash と reviewed head SHA を含む deterministic multiline body を投稿する。
  - Base policy は fixed path、base SHA、non-empty UTF-8、32 KiB 以下という runtime validation を満たす場合だけ review body へ注入する。
  - caller-provided arbitrary body / endpoint / method / raw gh args は引き続き禁止する。
  - base policy が取得できない、decode できない、または size 上限を超える場合は、従来の固定 `@codex review` 互換を維持し、machine-readable limitation を返す。
  - provider asset と dogfooding mirror を同期する。
- 禁止:
  - PR head 上の `.github/codex/review-policy.md` を当該 PR review に使うこと。
  - trigger caller から任意本文を受け取ること。
  - review finding blocker policy、repair loop、merge predicate をこの Issue で実装すること。
- 対象外:
  - Codex Action migration。
  - GitHub 以外の review provider。
  - P0/P1/P2 finding triage。
  - `spec-dock doctor` への dedicated review-policy diagnosis。現 Issue では trigger payload の limitation を machine-readable evidence とし、doctor integration は rollout / operationalization issue へ送る。

## 非交渉制約
- Review policy source は PR base SHA に bind する。
- Review comment は reviewed head SHA、policy base SHA、policy hash を machine-readable payload と comment body の両方から確認できる。
- GitHub write surface は fixed issue-comment endpoint だけに限定する。
- Token、secret、private reasoning、raw credential は出力しない。

## 受け入れ条件
- AC-001: Trusted base policy trigger
  - 前提: Open PR、expected head SHA、base SHA、base SHA 上の valid `.github/codex/review-policy.md` がある。
  - 操作: `trigger_codex_review.sh --repo owner/repo --pr 13 --head-sha <head>` を実行する。
  - 期待結果: 投稿本文は multiline `@codex review` になり、base policy source、policy SHA-256、reviewed head SHA、policy text を含む。
  - 観測点: fake `gh` trigger helper test、JSON payload。
- AC-002: Head-side policy is not trusted
  - 前提: PR head で policy が変更されていても、base SHA の policy が取得できる。
  - 操作: review trigger を実行する。
  - 期待結果: body と JSON payload は base SHA policy を参照し、head 側 policy 由来の本文を使わない。
  - 観測点: base SHA contents API endpoint assertion。
- AC-003: Compatibility fallback
  - 前提: base SHA metadata または base policy contents が取得できない。
  - 操作: review trigger を実行する。
  - 期待結果: arbitrary body を受け付けず、従来の fixed `@codex review` trigger 互換を維持し、policy limitation を JSON に記録する。
  - 観測点: existing trigger helper tests。

## 例外・エッジケース
- EC-001: stale head
  - 条件: PR current head が expected head SHA と一致しない。
  - 期待: comment を投稿せず `stale_head` を返す。
- EC-002: policy decode failure
  - 条件: base policy contents が non-empty UTF-8 として decode できない、または 32 KiB を超える。
  - 期待: limitation を返し、unsafe arbitrary body へ fallback しない。
- EC-003: permission denied
  - 条件: comment write 権限がない。
  - 期待: token を出力せず `github_token_permission_denied` limitation を返す。

## 用語
- Trusted base policy: PR base SHA の fixed path `.github/codex/review-policy.md` から取得する review instruction。
- Reviewed head SHA: Codex review 対象として trigger 時に固定した PR head SHA。
