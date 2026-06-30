---
種別: 要件定義書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
関連GitHub: ["#254"]
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — Issue 要件定義

## 1. 目的

Grade-aware Issue authoring workflow に、fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist adoption、report evidence gate を接続する。canonical phase promotion / issue readiness を、draft や stale review だけで主張できないようにする。

## 2. 背景

Epic #224 は canonical docs を main orchestrator authority とし、delegated draft は evidence に限定する。G1 は作業ルールを guidance に入れ、G2 は draft source を profile template に接続する。G3 は、その evidence が canonical promotion と readiness 判定に使われる条件を明確にする。

## 3. 観測可能な成果

- guidance / docs / report template から、grade 別の review / evidence gate が確認できる。
- Standard では specialist 使用または未使用理由を report に記録できる。
- Strict / Critical では delegated specialist unavailable / manual fallback evidence がない限り gate を通過しない。
- stale draft、stale reviewer、missing Evidence Adoption Ledger は readiness / phase promotion を block する。
- Fresh `spec-reviewer` gate は Lite でも省略されない。

## 4. スコープ

対象:

- spec authoring / issue planning docs
- report evidence ledger guidance
- delegated draft adoption rule
- readiness evidence hook with R0
- tests for missing / stale review evidence where available

対象外:

- raw readiness placeholder classifier の実装（R0）
- draft profile routing（G2）
- grade matrix initial wording（G1）
- live GitHub review / PR observation policy

## 5. 親 Epic との対応

- `E-RQ-022`
- `E-AC-022`
- Epic design: `Spec Authoring Evidence Gate`
- Epic plan: `G3`

## 6. 受け入れ条件

- AC-001: phase promotion には fresh `spec-reviewer` pass が必要であると guidance / docs が示す。
- AC-002: delegated draft adoption は Evidence Adoption Ledger へ記録される。
- AC-003: stale draft / stale reviewer evidence は promotion evidence として使えない。
- AC-004: Standard の specialist skip reason と Strict / Critical の unavailable / fallback evidence が report evidence contract に入る。
- AC-005: missing adoption evidence / reviewer evidence は readiness block reason として R0 の validator と整合する。
- AC-006: Draft artifact は authority / adoption / reviewer pass / phase completion / issue readiness を自己主張できない。

## 7. 制約

- G3 は spec-reviewer gate を弱めない。
- G3 は user approval や manual fallback を成功扱いにせず、証跡がある場合だけ non-blocking とする。
- G3 は code review / PR review policy を再設計しない。
