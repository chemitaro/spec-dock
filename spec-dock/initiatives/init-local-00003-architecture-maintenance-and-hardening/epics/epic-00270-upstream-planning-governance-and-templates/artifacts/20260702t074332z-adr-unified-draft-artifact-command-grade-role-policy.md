---
種別: ADR（Architecture Decision Record）
ID: "20260702t074332z-adr"
タイトル: "Unified Draft Artifact Command And Grade Role Policy"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-02"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from:
  - "artifacts/20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md"
  - "artifacts/20260702t071230z-decision-candidate-epic-planning-issue-draft-composition-workflow.md"
  - "artifacts/20260702t054322z-research-issue-planning-draft-strategy-analysis.md"
  - "artifacts/20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md"
  - "artifacts/20260702t062053z-disc-pre-start-issue-concretization-management-model.md"
  - "Deep Consultant analysis, 2026-07-02"
  - "ChatGPT 5.5 Pro consultation, 2026-07-02"
reflected_to:
  - "report.md"
  - "artifacts/20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md"
---

# 20260702t074332z-adr Unified Draft Artifact Command And Grade Role Policy

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `decision-candidate` / `design.md` / `plan.md` / `report.md`
- ADR として残す理由:
  - Issue Start 前に downstream Issue の `draft-design` / `draft-plan` を作る方法は、今後の Epic Planning workflow と Issue Planning workflow の境界に影響する。
  - command に actor semantics を持たせるか、workflow / skill / EAL で actor responsibility を管理するかは、CLI surface、権威境界、後続エージェントの動線に関わる。
  - 一度 command を増やすと後から縮退しにくく、canonical docs と evidence artifacts の境界を曖昧にするリスクがある。

## 結論（Decision）

SpecDock は、Issue-local `draft-design` / `draft-plan` 作成について、actor 別、specialist 別、深さ別の command を作らない。

採用する責務分離は次の通り。

1. Runtime command は、verified `.assurance.json` の `authorized_profile` に基づき、profile template から Issue-local draft artifact を生成する機械的 surface に限定する。
2. その統一 primitive は、既存の `new artifact draft-design --issue <issue-id>` と `new artifact draft-plan --issue <issue-id>` を中心にする。
3. `assurance compose` は canonical `design.md` / `plan.md` / `report.md` を compose する command として維持し、pre-start draft artifact 作成には使わない。
4. `composed draft` と `authored draft` の違いは command ではなく、同じ artifact の lifecycle / provenance / `report.md` Evidence Adoption Ledger state として扱う。
5. system-architect / implementation-planner を使うかどうかは、Issue grade に応じた workflow / skill / reviewer gate が管理する。
6. `assurance compose-draft`、`issue prepare`、`epic prepare-issues` などの高レベル command は初期実装の必須 surface にしない。将来導入する場合も、既存 `new artifact draft-*` を呼ぶ thin wrapper / batch orchestration に留め、actor assignment、reviewer pass、canonical adoption を主張しない。

Grade 別の actor obligation は次の通り。

- Lite:
  - `draft-design` / `draft-plan` は作ってよいが、thin alignment scaffold とする。
  - system-architect / implementation-planner は不要。
  - `report.md` に Lite 根拠、specialist not applicable、残リスク、reviewer evidence を残す。
- Standard:
  - specialist は推奨だが任意。
  - 使わない場合は、確認した source、skip reason、manual authoring evidence、残リスクを `report.md` に残す。
- Strict:
  - design draft は system-architect、plan draft は implementation-planner の enrichment / authorship を原則必須にする。
  - unavailable / denied / host constraint の場合は manual fallback evidence を要求する。
  - skip reason だけでは readiness gate を満たさない。
- Critical:
  - specialist output がない場合は原則 blocked。
  - manual fallback は、明示的な risk acceptance、追加 reviewer / manual gate、rollback / safety evidence がある場合だけ例外的に許容する。

## 背景（Context）

Epic Planning で複数 Issue をまとめて具体化する場合、Issue Start 前でも downstream Issue の設計境界、依存順、検証観点を揃えるために `draft-design` / `draft-plan` が欲しい。

一方で、Issue Start 前に canonical `design.md` / `plan.md` を具体化すると、それが正本として誤読されやすい。SpecDock の既存方針では、canonical docs は main orchestrator single-writer authority であり、sub-agent / external / discussion outputs は採用されるまで evidence に留まる。

ユーザーは、system-architect / implementation-planner が作る draft も、正式版の前に作る draft も、実体としては grade/profile に対応した template を出発点にするため、command を分ける意味が薄いのではないかと指摘した。また、command は実際にどの actor が中身を濃くしたかを制御できない。

Deep Consultant と ChatGPT 5.5 Pro の分析はいずれも、actor 別 command を作らず、command は統一し、actor responsibility は workflow / skill / report evidence gate で管理する方針を支持した。差分は command surface 名であり、ローカル実装との整合性から、初期実装では既存 `new artifact draft-design` / `draft-plan` を統一 primitive として強化する。

## 選択肢（Options considered）

- 選択肢 A:
  - 概要:
    - actor / depth 別 command を作る。
    - 例: `draft-design-specialist`、`compose-authored-draft`、`--by system-architect`。
  - 良い点:
    - 名前だけを見ると、誰が関与すべきかが分かりやすい。
  - 悪い点 / 制約:
    - command が actor を実際に呼ぶわけではなく、編集者も保証できない。
    - fake authorship と authority leak を生む。
    - CLI surface が増え、coding agent がどの command を使うべきか迷いやすい。
  - 棄却理由:
    - command で保証できない社会的/ワークフロー的責務を command 名へ押し込むべきではない。
- 選択肢 B:
  - 概要:
    - `assurance compose-draft --issue <issue-id> --artifact all` を主導線にする。
  - 良い点:
    - design / plan をまとめて作る batch primitive としては分かりやすい。
    - Deep Consultant はこの案を推奨した。
  - 悪い点 / 制約:
    - `assurance compose` は既に canonical docs を更新する command 語彙であり、draft artifact へ広げると canonical/evidence 境界が曖昧になる。
    - 初期実装では command 増になり、既存 `new artifact draft-*` の責務と重複する。
  - 棄却理由:
    - 初期実装では不要。将来必要な場合も thin wrapper に留める。
- 選択肢 C:
  - 概要:
    - 既存 `new artifact draft-design` / `draft-plan` を統一 primitive として強化する。
  - 良い点:
    - 既存 artifact catalog と実装に合う。
    - command は Issue-local evidence artifact 作成だけを担うため、canonical docs との境界が明確。
    - actor responsibility を workflow / skill / EAL に残せる。
    - command proliferation を避けられる。
  - 悪い点 / 制約:
    - design / plan の両方を作るには primitive を2回呼ぶ必要がある。
    - Epic Planning の大量 Issue では将来 batch wrapper が欲しくなる可能性がある。
  - 採用理由:
    - 最小の command surface で、現行実装、artifact rules、canonical ownership 方針と整合するため。

## 判断理由（Rationale）

SpecDock の command は、機械的に検証できる操作を担うべきである。`draft-design` / `draft-plan` について機械的に検証できるのは、次の範囲である。

- explicit `--issue` で non-active Issue を解決できること。
- Issue scope 以外では fail すること。
- valid かつ non-stale `.assurance.json` を要求すること。
- `authorized_profile` に対応する `templates/issue-profiles/<profile>/design.md` または `plan.md` を render すること。
- target Issue の `artifacts/` 配下に timestamped artifact を作ること。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を変更しないこと。
- missing / invalid / stale assurance では no-write fail-closed すること。

一方で、次は command だけでは保証できない。

- system-architect / implementation-planner が実際に中身を濃くしたこと。
- specialist を使わない判断が妥当であること。
- Strict / Critical の fallback evidence が十分であること。
- draft artifact が canonical docs へ採用されたこと。
- fresh `spec-reviewer` が phase promotion を承認したこと。

そのため、actor responsibility は command option ではなく、Issue grade matrix、planning skills、`report.md` Evidence Adoption Ledger、fresh reviewer gate で扱う。

この分離により、CLI は単純で検証可能になり、workflow は grade に応じた人間/agent responsibility を表現できる。

## 影響（Consequences）

- 良い影響:
  - CLI surface が増えすぎず、coding agent が使うべき primitive が明確になる。
  - canonical docs と evidence artifacts の境界が保たれる。
  - Lite / Standard / Strict / Critical の違いを command ではなく workflow evidence として表現できる。
  - fake authorship を避けられる。
  - 既存 `new artifact draft-design` / `draft-plan` 実装を活かせる。
- 悪い影響 / 将来負債:
  - Epic Planning で多数 Issue の draft design / draft plan を作る場合、初期実装では command 呼び出しが冗長になる。
  - `new artifact draft-*` の metadata / output / validation が不足している場合は、後続実装で補強が必要。
  - `.assurance.json` の source binding が canonical placeholder 変更で stale になりやすい問題は別途設計が必要。
- 影響範囲:
  - `new artifact draft-design` / `draft-plan`
  - `assurance classify`
  - `assurance compose`
  - Issue artifact front matter / metadata
  - `workflow_epic.md`
  - `workflow_issue.md`
  - `workflow_spec_authoring.md`
  - planning skills
  - Issue grade / reviewer gate
  - validation / smoke tests
- 移行 / ロールバック:
  - 既に作成された pre-start draft 的な canonical `design.md` / `plan.md` 本文は、可能な限り Issue-local artifacts へ移し、canonical docs は Issue Start 後の正規化対象とする。
  - `assurance compose-draft` がどうしても必要になった場合は、独立した actor semantics を持たない thin wrapper として導入する。
  - Strict / Critical の fallback が過重または不足する場合は、command ではなく grade matrix / workflow / reviewer gate を調整する。
- 追加対応:
  - `new artifact draft-design` / `draft-plan` の metadata と no-write fail-closed test を補強する。
  - Epic handoff package に downstream Issue ごとの `draft-requirement` / `draft-design` / `draft-plan` path index を含める。
  - `assurance compose` を canonical compose 専用として docs に明示する。
  - `workflow_epic.md` / `workflow_issue.md` / planning skills に grade-aware actor obligation を反映する。
  - validation / smoke tests で canonical docs が変更されないこと、stale assurance で fail すること、Strict / Critical が draft artifact だけでは readiness にならないことを確認する。

## 参考（References）

- 関連仕様:
  - `epic-00270/requirement.md`
  - `epic-00270/design.md`
  - `epic-00270/plan.md`
  - `epic-00270/report.md`
- 元になった artifacts:
  - `artifacts/20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md`
  - `artifacts/20260702t071230z-decision-candidate-epic-planning-issue-draft-composition-workflow.md`
  - `artifacts/20260702t054322z-research-issue-planning-draft-strategy-analysis.md`
  - `artifacts/20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md`
  - `artifacts/20260702t062053z-disc-pre-start-issue-concretization-management-model.md`
- 反映先:
  - `report.md`
  - `artifacts/20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md`
- 外部/委任分析:
  - Deep Consultant analysis, 2026-07-02
  - ChatGPT 5.5 Pro consultation, 2026-07-02
