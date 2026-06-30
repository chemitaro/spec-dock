---
種別: 要件定義書（Issue）
ID: "iss-00251"
タイトル: "Enforce Fail Closed Issue Artifact Readiness Preflight"
関連GitHub: ["#251"]
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00251 Enforce Fail Closed Issue Artifact Readiness Preflight — Issue 要件定義

## 1. 目的

`workflow status` と `guidance issue-execution` が、未完成の Issue artifact を execution-ready と誤判定しないようにする。`assurance compose` の成功、ファイル存在、品質ゲート見出しだけでは ready とせず、requirement / design / plan / report evidence を fail-closed に判定する。

## 2. 背景

`iss-00247 / #247` 後の手動テストで、profile template pack 導入後の placeholder vocabulary と plan structure に readiness classifier が追従していないことが分かった。これは template 本文の問題ではなく、runtime readiness contract の drift である。

## 3. 観測可能な成果

- `REQ-XXX`、`CON-...`、複合 placeholder cell を含む artifact は ready にならない。
- `Validation Gate`、`M99`、static analysis / lint / tests / report / commit などの品質ゲート見出しだけを持つ plan は ready にならない。
- `artifact_state: awaiting-assurance-compose` や明示 scaffold marker を持つ design / plan は ready にならない。
- title に普通語として `template` または `placeholder` を含む substantive design は、それだけでは block されない。
- 既存 contract が reviewer / Evidence Adoption Ledger 証跡を必須としている状態では、証跡欠落を issue readiness の block reason として扱える。

## 4. スコープ

対象:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
- 必要に応じた小さな domain helper
- `workflow status` / `guidance issue-execution` の readiness 判定
- `tests/unit/domain/test_workflow_state.py`
- `tests/cli_runtime/test_workflow.py`
- provider / dogfooding docs の readiness contract 記述

対象外:

- grade-aware issue planning guidance の本文整理
- `new doc draft-design` / `draft-plan` の profile routing 実装
- delegated specialist routing
- profile template 本文の全面改訂
- automatic Lite default の有効化

## 5. 親 Epic との対応

- `E-RQ-006`: Grade template materialization and artifact readiness contract
- `E-AC-006`: Grade template materialization and fail-closed readiness
- Epic design: `Artifact Readiness Validator`
- Epic plan: `R0`

## 6. 受け入れ条件

- AC-001: requirement に `REQ-XXX`、`CON-...`、旧 scaffold sentence、placeholder table/list entry が残る場合、workflow readiness は block される。
- AC-002: plan が品質ゲート見出しだけで実行可能 milestone / behavior / verification を持たない場合、workflow readiness は block される。
- AC-003: plan の table/list/code span に複合 placeholder が含まれる場合、workflow readiness は block される。
- AC-004: design の title に `template` / `placeholder` が含まれていても、本文が substantive なら ready 判定を妨げない。
- AC-005: `artifact_state: awaiting-assurance-compose`、draft-only state、明示 scaffold marker は ready 判定を block する。
- AC-006: 既存 contract が delegated adoption / fresh reviewer / report evidence を必須としている状態で証跡が欠落している場合、R0 は新しい grade-aware evidence policy を定義せず、generic fail-closed readiness predicate / block reason として扱える。
- AC-007: 既存 strict-legacy path と stale source binding block は退行しない。

## 7. 制約

- false positive より false negative を優先する。判定不能な artifact は ready にしない。
- 裸の `...` のような一般的な省略記号だけで全体を block しない。ID sentinel、table/list placeholder、明示 scaffold marker を文脈付きで判定する。
- design の ordinary word `template` / `placeholder` は scaffold marker として扱わない。
- R0 は readiness contract の修正に集中し、grade-aware authoring rules、delegated specialist evidence policy、fresh reviewer gate、Evidence Adoption Ledger policy の再設計を行わない。それらの grade-aware policy 定義と guidance/template 接続は G1 / G3 の責務である。
