# Interview: 決定的 `@codex review` trigger 対応の issue scope 確認

- 作成日: 2026-06-09
- 対象: `iss-00176 GitHub PR observation should trigger and wait for Codex review completion`
- 種別: answered interview
- 状態: answered

## 背景

現時点で active issue として `iss-00176` / GitHub `#176` が存在している。

この issue の canonical docs はまだ scaffold に近い一方、`discussions/` には次の分析 artifact があり、実装対象はかなり具体化されている。

- `20260608t085332z-research-chatgpt55-pro-analysis-request-package.md`
- `20260608t092803z-research-chatgpt55-pro-codex-review-trigger-completion-analysis.md`
- `20260608t111111z-research-deterministic-codex-review-trigger-design.md`

主な合意済み方向:

- `wait_pr_observation.sh` の通常 path は `@codex review` を実行開始時に決定的に1回投稿する。
- 投稿処理は `trigger_codex_review.sh` に固定 write boundary として分離する。
- `wait_pr_observation.sh` が通常 path で `trigger_codex_review.sh` を必ず内部呼び出しする。
- 既存 trigger の自動 reuse はしない。
- `stdout` final JSON / `stderr` progress の境界を維持する。

## 確認したいこと

この作業は、既存の `iss-00176` を実装 issue としてこのまま育てるべきですか。それとも、`iss-00176` は分析・準備 issue として扱い、今回の決定的 trigger 投稿実装を別の新規 issue として作成すべきですか。

## 推奨

推奨は **既存 `iss-00176` をこのまま実装 issue として育てる** こと。

理由:

- GitHub issue `#176` のタイトルがすでに今回の実装対象と一致している。
- active issue 直下に分析 artifact が揃っており、要件定義書へ採用しやすい。
- まだ canonical `requirement.md` / `design.md` / `plan.md` は scaffold に近く、issue分割による履歴移動コストを避けられる。

## 選択肢

### A. 既存 `iss-00176` を実装 issue として育てる（推奨）

- `iss-00176` の canonical docs を作成・更新する。
- 既存 discussion artifact を evidence として採用する。
- 新規 issue は作成しない。

### B. 新規 issue を作成する

- `iss-00176` は分析・準備 issue として扱う。
- 今回の実装対象を新規 issue として作成する。
- 必要に応じて既存 discussion artifact を新規 issue の `discussions/` へ移す、または参照として残す。

## 回答欄

- ユーザー回答:
  - はい。現在アクティブにしている `iss-00176` を実装 issue として扱う。
  - この issue は計画準備だけで閉じず、要件定義書・設計書・実装計画書を具体化した上で、この issue の中で実装まで進める。
  - 次の別 issue を作って実装するわけではない。
- 採用判断:
  - 採用: A. 既存 `iss-00176` を実装 issue として育てる。
- 反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` の Evidence Adoption Ledger / Spec Authoring Gate
