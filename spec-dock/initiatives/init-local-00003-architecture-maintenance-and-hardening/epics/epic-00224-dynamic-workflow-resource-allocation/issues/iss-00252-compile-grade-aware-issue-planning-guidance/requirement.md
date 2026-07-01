---
種別: 要件定義書（Issue）
ID: "iss-00252"
タイトル: "Compile Grade Aware Issue Planning Guidance"
関連GitHub: ["#252"]
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00252 Compile Grade Aware Issue Planning Guidance — Issue 要件定義

## 1. 目的

Issue planning guidance に `lite / standard / strict / critical` ごとの authoring rule を組み込み、agent が旧来の step-centric または一律 Strict 相当の planning に戻らないようにする。

## 2. 背景

Epic #224 は grade 別 template pack を導入したが、template が存在するだけでは、agent がどの grade で誰を呼び、どの evidence gate を満たすべきかを判断できない。`20260630t111316z-adr` は、この作業ルールを follow-up Issue で再設計せず Epic-level authority として固定した。

## 3. 観測可能な成果

- `guidance issue-planning` または関連 workflow docs から、grade 別 authoring matrix を確認できる。
- Lite は automatic default ではなく、明示根拠がある場合だけ使えると分かる。
- unknown / ambiguous な Issue は Standard 以上へ倒れる。
- `authorized_profile` と manual escalation の役割が分離される。
- Standard では specialist 使用 / 未使用理由、Strict / Critical では specialist unavailable / manual fallback evidence が guidance で要求される。

## 4. スコープ

対象:

- issue planning guidance / workflow docs / skill kernel handoff text
- grade-aware authoring matrix
- provider docs と dogfooding docs parity
- guidance regression tests

対象外:

- readiness classifier の runtime 修正（R0）
- `new doc draft-design` / `draft-plan` routing（G2）
- report evidence gate の enforcement（G3）
- end-to-end smoke matrix（G4）

## 5. 親 Epic との対応

- `E-RQ-022`: Grade-aware Issue authoring, draft, review, and evidence workflow
- `E-AC-022`: Grade-aware Issue authoring workflow
- Epic design: `Grade-Aware Authoring Router`
- Epic plan: `G1`

## 6. 受け入れ条件

- AC-001: guidance は Lite / Standard / Strict / Critical の requirement / design / plan / review / report evidence rules を示す。
- AC-002: Lite automatic default は禁止され、Lite 使用には明示根拠が必要である。
- AC-003: unknown / ambiguous な Issue は Standard 以上として扱う。
- AC-004: `authorized_profile` は runtime template / guidance / obligation authority、manual escalation は gate 強化であると明示される。
- AC-005: Standard は specialist 推奨条件と未使用理由の記録先を示す。
- AC-006: Strict / Critical は specialist 原則必須、利用不可時の manual fallback evidence を示す。
- AC-007: G1 は downstream G2 / G3 / G4 が参照できる stable wording を提供する。

## 7. 制約

- G1 は grade-aware authoring rules を実装 guidance に落とす Issue であり、ADR の決定を変更しない。
- G1 は draft artifact generation の routing を変更しない。
- guidance の本文は日本語を基本とし、必要な英語名称は括弧で補う。
