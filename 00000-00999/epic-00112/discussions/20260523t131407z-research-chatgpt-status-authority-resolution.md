---
type: research
source: chatgpt-5.5-pro
created_at: 2026-05-23T13:14:07+09:00
epic: epic-00112
topic: status-authority-grants resolution
chatgpt_thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a11a65d-2d44-83ab-afb3-d3f0abb04352
status: current
---

# ChatGPT 5.5 Pro 追加分析: status / authority / grants の分離

## 追加論点

draft canonical artifact model は便利だが、`status: draft` だけでは canonical path の権威シグナルを抑えきれない。そこで、status 以外に authority と grants を導入するべきかを追加確認した。

## 回答の要点

`status: draft` だけでは不十分。3 軸以上で扱う必要がある。

- canonical path: location
- status: lifecycle
- authority / grants: downstream が何をしてよいか

## 推奨 frontmatter

```yaml
schema: spec-dock.artifact.v1
artifact: design
spec_id: example-spec
status: draft
authority: proposed
canonical_role: latest_proposal
owner_role: main-orchestrator
draft_author_role: system-architect
promotion_required_by: main-orchestrator
grants:
  review_input: true
  planning_input: true
  design_baseline: false
  implementation_start: false
  issue_ready: false
  phase_completion: false
source_discussions: []
evidence_ledger: evidence-ledger.yaml
approval:
  approved_by: null
  approved_at: null
  approved_revision: null
  promotion_record: null
```

## 実装可能条件

implementation allowed は、少なくとも次を満たす必要がある。

- artifact が plan
- `status: approved`
- `authority: approved`
- `grants.implementation_start: true`
- `approval.approved_by` が main orchestrator
- `approval.approved_revision` が current hash と一致
- 参照される design revision も approved

## 推奨実装順

1. frontmatter schema
2. `status` / `authority` / `grants` / `approval` required
3. forbidden state combination validator
4. purpose-aware context-pack
5. evidence ledger
6. child output path gate
7. review_requested gate
8. promotion gate
9. issue lifecycle の approved revision 参照
10. approved snapshot / promotion record

## 判断

draft canonical artifact model を採るなら、この status-authority-grants separation は必須。これがない状態では、専門 author に canonical draft write を解禁しない方が安全。
