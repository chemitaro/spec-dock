---
種別: research
ID: "20260624t062341z-research"
タイトル: "MT015 Symlink Abuse Retest Plan"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-015", "symlink-safety"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_packet_store.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py"
reflected_to: []
---

# 20260624t062341z-research MT015 Symlink Abuse Retest Plan

## 調査目的
- MT-015 の skipped を、product bug と断定せず、次に必要な fresh trial retest の範囲として整理する。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_packet_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
- 検証手順:
  - manual log の skipped 理由を確認した。
  - symlink guard が存在する主要 store を read-only で確認した。
  - deep-consultant の second opinion を統合した。

## facts / 観測できた事実
- MT-015 は未実施。
- skipped 理由:
  - MT-009 の routing defect 発見後、同じ trial repo に破壊的 security-boundary test のノイズを増やさないため。
- deep-consultant の指摘:
  - planning artifact write/read、context packet、runbook projection、assurance contract write には symlink guard が確認できる。
  - ただし実地確認は fresh trial repo で分離して行うべき。

## inference / 推測
- 現時点では product bug とは断定しない。
- ただし symlink abuse は security boundary に関わるため、未実施のまま release confidence に含めるのは危険。
- routing defect 修正後、fresh trial repo で再実施する manual regression または automated regression が必要。

## retest scope
- planning artifact symlink:
  - `requirement.md` / `plan.md` / `report.md` のいずれかを外部 target への symlink にする。
  - 期待: unsafe write/read が fail closed し、外部 target が不変。
- runbook projection symlink:
  - `spec-dock/.agent/runbooks` または `spec-dock/active/current-runbook.*` 周辺に symlink を置く。
  - 期待: CLI が fail closed し、partial/stale projection を成功扱いしない。
- context packet projection symlink:
  - `spec-dock/.agent/context-packets` を外部 directory symlink にする。
  - 期待: `context-packet-write-failure` などの blocked state になり、外部 target が不変。
- assurance contract symlink:
  - issue `assurance.json` を外部 target symlink にする。
  - 期待: unsafe write が拒否される。

## recommendation
- iss-00237 の routing修正本体には混ぜない。
- follow-up issue として「fresh trial repo symlink abuse manual/regression test」を分離する。
- 完了条件は次の3点。
  - external symlink target が不変。
  - CLI が fail closed。
  - stale / partial generated artifact を success として扱わない。

## implications / 判断への含意
- MT-015 は release blocker というより confidence gap。
- routing defect 修正後の manual retest checklist に必ず含める。
