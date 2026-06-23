---
種別: 要件定義書ドラフト（Issue）
ID: "iss-00229"
タイトル: "Compose Profile Aware Planning Artifacts"
関連GitHub: ["#229"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00229 Draft Requirement

## 目的
- Provisional / approved Assurance に応じて design / plan / report section を安全に合成し、planning handoff を支援する。
- Approved source binding が stale になった場合に execution を block できるようにする。

## スコープ
- 必須:
  - Fragment source / preset manifest。
  - design / plan / report composer。
  - stable section markers。
  - pristine/full materialization と additive mode。
  - substantive content no-overwrite。
  - requirement-stage provisional、design-stage approved source binding。
  - source hash mismatch / stale invalidation。
- 禁止:
  - Step worker routing。
  - GitHub review。
  - automatic downgrade による section deletion。

## Trace
- closes: E-RQ-006, E-AC-006, E-AC-008。

## 受け入れ条件
- AC-001: Profile fixture ごとに必要 section だけを materialize する。
- AC-002: 同じ input で二度 compile しても diff が出ない。
- AC-003: substantive body を自動上書きしない。
- AC-004: approved `assurance.json` 後に requirement / design / plan が substantive change した場合、stale source binding として block する。

## 依存
- Upstream: iss-00227, iss-00228。
- Downstream: iss-00230, iss-00233。

## 静的解析前提
- Markdown composition は typed fragment manifest と explicit parser / writer を使い、unchecked dict / string manipulation を局所化する。
