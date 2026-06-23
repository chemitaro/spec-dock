---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Draft Requirement

## 目的
- PR base SHA 上の project-owned review policy から deterministic multiline `@codex review` comment を生成する。
- PR head 上の policy 変更や caller-provided arbitrary body を trusted input として扱わない。

## スコープ
- 必須:
  - `.github/codex/review-policy.md` bootstrap-only asset。
  - base SHA fixed-path fetch。
  - policy UTF-8 / NUL / size / schema validation。
  - trigger compiler and evidence。
  - reviewed head SHA / policy base SHA / policy hash / body hash。
  - stale head detection。
- 禁止:
  - caller-provided arbitrary body / endpoint / raw `gh` args。
  - finding blocker policy。
  - Codex Action migration。

## Trace
- closes: E-RQ-009, E-AC-009, E-AC-010。

## 受け入れ条件
- AC-001: valid base policy から multiline `@codex review` comment を生成し、hash evidence を返す。
- AC-002: PR head 側で policy を弱めても当該 review には使われない。
- AC-003: missing / invalid policy は required external review で human gate になる。
- AC-004: expected head SHA と current PR head が違う場合 stale として trigger しない。

## 依存
- Upstream: iss-00227。
- Parallel possible: iss-00228 after I01。
- Downstream: iss-00232, iss-00233。

## 静的解析前提
- GitHub boundary は typed command result / error model を持ち、network/permission failure を explicit に扱う。
