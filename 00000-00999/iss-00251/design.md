---
種別: 設計書（Issue）
ID: "iss-00251"
タイトル: "Enforce Fail Closed Issue Artifact Readiness Preflight"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00251 Enforce Fail Closed Issue Artifact Readiness Preflight — Issue 設計書（Strict）

## 1. Strict とする理由

workflow readiness は Issue execution の開始可否を決める shared runtime contract である。誤って ready にすると未完成 artifact から実装が始まるため、通常の documentation fix ではなく strict grade とする。

## 2. 設計要約

- `[N]` Artifact readiness 判定を fail-closed に統一する。
- `[N]` placeholder detection は requirement / artifact cell / artifact text の文脈を分ける。
- `[N]` plan readiness は executable work marker と quality marker を分離する。
- `[N]` design readiness は explicit scaffold marker に限定し、ordinary word `template` / `placeholder` だけで block しない。
- `[N]` 既存 contract が必須化している reviewer / adoption evidence の欠落を、generic fail-closed block reason として扱えるようにする。Grade-aware evidence policy の定義は G3 に残す。

## 3. コンポーネント

| Component | 責務 | 配置候補 |
|---|---|---|
| Shared Placeholder Detector | `REQ-XXX`、`CON-...`、composite placeholder cell、scaffold sentence を文脈付きで検出する | `domain/workflow_state.py` または `domain/artifact_readiness.py` |
| Plan Executable Predicate | milestone / behavior / verification / actionable step を executable marker として判定する | `domain/workflow_state.py` |
| Quality Marker Filter | `Validation Gate`、`M99`、static analysis / lint / tests / report / commit を supporting marker として扱う | `domain/workflow_state.py` |
| Design Scaffold Predicate | `artifact_state: awaiting-assurance-compose` と明示 scaffold marker だけを block に使う | `domain/workflow_state.py` |
| Evidence Readiness Predicate | 既存 contract が必須化している fresh reviewer / adoption ledger / report evidence の欠落を generic block reason に変換する。必須条件そのものは定義しない | `domain/workflow_state.py` |

## 4. 判定ルール

| Artifact | block するもの | block しないもの |
|---|---|---|
| requirement | `REQ-XXX`、`CON-...`、未置換 placeholder row、旧 scaffold sentence | 正当な説明文中の省略表現 |
| design | `artifact_state: awaiting-assurance-compose`、draft-only state、明示 scaffold marker | title や本文中の ordinary word `template` / `placeholder` |
| plan | 実行可能 milestone / behavior なし、quality marker だけ、placeholder cell | executable step と supporting quality gate の共存 |
| report evidence | 既存 contract 上の stale reviewer、missing adoption ledger、required command result missing | 実行不能理由が明記された no-op evidence、新規 grade-aware evidence policy 定義 |

## 5. 失敗設計

- 判定不能な artifact は ready にせず、repair guidance を返す。
- placeholder detector が過剰検出した場合も、execution start を止める側に倒す。
- 既存 substantive issue が新 detector で block された場合は、block reason を具体化し、artifact 修正で解除できるようにする。

## 6. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 / AC-003 | Shared Placeholder Detector |
| AC-002 | Plan Executable Predicate + Quality Marker Filter |
| AC-004 / AC-005 | Design Scaffold Predicate |
| AC-006 | Evidence Readiness Predicate |
| AC-007 | regression tests for strict-legacy / stale binding |

## 7. 非対象

- `guidance issue-planning` の grade-aware authoring matrix は G1。
- delegated specialist draft routing は G2。
- report evidence gate の guidance / template 整備は G3。
- integrated smoke coverage は G4。
