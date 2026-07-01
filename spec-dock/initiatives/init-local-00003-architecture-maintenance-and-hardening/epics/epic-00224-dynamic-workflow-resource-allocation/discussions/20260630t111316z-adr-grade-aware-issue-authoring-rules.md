---
種別: ADR（Architecture Decision Record）
ID: "20260630t111316z-adr"
タイトル: "Grade-Aware Issue Authoring Rules"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224"]
authority: "accepted"
amends:
  - "20260623t074443z-adr"
  - "20260629t003131z-adr"
derived_from:
  - "20260630t084325z-disc-grade-aware-authoring-rules-definition.md"
  - "20260630t082805z-disc-epic-224-amendment-and-followup-issue-draft.md"
  - "20260630t055323z-disc-issue-247-manual-test-followup-analysis.md"
  - "20260630t080402z-disc-manual-test-readiness-failure-root-cause-analysis.md"
  - "/Users/iwasawayuuta/.codex/attachments/7d1d7ff9-799a-40ae-a732-da5eb7b06d0f/pasted-text.txt"
  - "src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260630t111316z-adr Grade-Aware Issue Authoring Rules

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Grade 別 Issue authoring rules は Epic #224 配下の複数 follow-up Issue が共有する workflow authority であり、Issue ごとに再設計すると方針が分岐する。
  - `authorized_profile`、manual escalation、delegated specialist、fresh reviewer gate、execution readiness の境界は、template、guidance、skill、review evidence、manual test にまたがる。
  - 前回 draft では `W1` として Issue 化しかけたが、これは実装単位ではなく上流設計判断であるため、ADR として固定する。

## 結論（Decision）

- Grade 別 Issue authoring rules は follow-up Issue として作成せず、Epic #224 の上流設計判断として扱う。
- `W1. Define Grade-Aware Issue Authoring Workflow Matrix` は Issue 化しない。補正後の実装 Issue は `R0 + G1〜G4` とする。
- `authorized_profile` は runtime template / guidance / obligation selection の authority とする。
- Issue authoring grade / manual escalation は、planning、delegated specialist、review、report evidence、manual gate を強める判断であり、`authorized_profile` を silent override しない。
- `lite` は automatic default にしない。unknown / ambiguous な Issue は `standard` 以上として扱い、Lite は明示根拠がある場合だけ使う。
- Requirement / design / plan / review / report evidence の各 phase に、`lite / standard / strict / critical` ごとの作業ルールを適用する。
- `system-architect` と `implementation-planner` は shipped skill file の存在を前提にせず、delegated specialist role として扱う。
- `standard` では delegated specialist を推奨とし、設計差分、runtime behavior、TDD behavior、責務境界、milestone decomposition がある場合に使う。使わない場合は理由を `report.md` に残す。
- `strict` 以上では delegated specialist を原則必須とする。利用不可の場合は unavailable と manual fallback 理由を `report.md` に残す。
- `critical` では strict の規約に加え、manual approval、safety、security/privacy、migration dry-run、rollback/recovery gate を扱う。
- Fresh `spec-reviewer` gate は grade によって弱めない。変えるのは review focus、追加 reviewer、manual gate、evidence density である。
- `assurance compose` の成功は execution readiness ではない。`workflow status` / `guidance issue-execution` は fail-closed readiness preflight として、未解決 placeholder、template-only artifact、heading-only plan、stale reviewer evidence、missing adoption evidence を ready にしない。

## 背景（Context）

- Issue #247 / PR #248 により、Issue design / plan の grade 別 Markdown template pack が provider-side source of truth として導入された。
- その後の手動テストで、template pack の導入自体とは別に、`workflow status` / `guidance issue-execution` が未完成 artifact を ready と判定し得ることが分かった。
- GPT-5.5 Pro の追加分析では、問題は単なる template 配置ではなく、Issue grade に応じて「誰が、どの推論強度で、どの artifact を作り、どの review gate を通すか」が workflow に戻っていないことだと整理された。
- 現行 `spec-dock-issue-planning` skill は `system-architect` / `implementation-planner` を delegated agent role として扱い、その draft は scope-local evidence であり canonical docs の代替ではないと定義している。
- 既存 `workflow_spec_authoring.md` は、canonical docs は main orchestrator-owned、delegated evidence は採否判断後に canonical docs と `report.md` へ反映し、各 phase promotion には fresh `spec-reviewer` pass が必要だと定義している。
- Epic #224 にはすでに `authorized_profile`、Lite automatic default 禁止、monotonic escalation、plan-centric execution preflight の ADR がある。今回の判断は、それらを Issue authoring phase へ適用する。

## Grade 別 authoring rules

| Phase | `lite` | `standard` | `strict` | `critical` |
|---|---|---|---|---|
| Requirement | main orchestrator。specialist 原則なし。Lite 前提と非影響を確認する。 | main orchestrator。調査補助は必要時のみ。AC / behavior / constraint / grade signal を確認する。 | main orchestrator。必要時に consultant / repo evidence を使い、contract / compatibility / migration signal を確認する。 | main orchestrator。必要時に security / deep consultant を使い、no-go / protected / manual / recovery signal を確認する。 |
| Design | lite template。`system-architect` 原則なし。必要になった時点で `standard` 以上へ上げる。 | standard template。`system-architect` 推奨。設計差分や責務境界がある場合に使う。 | strict template。`system-architect` 原則必須。contract / compatibility / migration / readiness を確認する。 | critical template。`system-architect` 必須。必要時に clean-room / security / recovery consultant を追加する。 |
| Plan | lite template。`implementation-planner` 原則なし。軽量 checklist と focused verification を確認する。 | standard template。`implementation-planner` 推奨。TDD behavior / milestone / validation ladder がある場合に使う。 | strict template。`implementation-planner` 原則必須。contract / compatibility / migration / review gate を確認する。 | critical template。`implementation-planner` 必須。safety / manual / dry-run / rollback / recovery を確認する。 |
| Review | fresh `spec-reviewer`。Lite 前提を破っていないことを確認する。 | fresh `spec-reviewer`。traceability と TDD 実行可能性を確認する。 | fresh `spec-reviewer` + 必要時追加 reviewer。contract / compatibility を確認する。 | fresh `spec-reviewer` + manual / safety / security / recovery reviewer。no-go / protected gate を確認する。 |
| Report evidence | grade source、Lite 非影響、reviewer pass を記録する。 | grade source、delegated specialist の使用 / 未使用理由、reviewer pass を記録する。 | delegated evidence adoption、unavailable / fallback、reviewer pass、compatibility evidence を記録する。 | manual approval、safety/security/recovery、dry-run / rollback evidence を記録する。 |

## 選択肢（Options considered）

- Option A: Grade 別 authoring matrix を follow-up Issue `W1` として実装する。
  - Pros:
    - Issue として進捗を追いやすい。
    - 後続 Issue の前に明示的な作業枠を置ける。
  - Cons:
    - 実装対象ではなく設計判断を Issue 化するため、Issue planning の中で上流方針を再決定する矛盾が生じる。
    - 後続 Issue が `W1` 完了まで blocked になり、Epic amendment の正本化が遅れる。
  - 判断: 棄却する。
- Option B: Grade 別 authoring rules を ADR として固定し、Epic canonical docs へ反映したうえで実装 Issue を切る。
  - Pros:
    - 上流設計判断と実装 Issue を分離できる。
    - `authorized_profile` / manual escalation / delegated role / review gate の境界を後続 Issue が共有できる。
    - 既存 ADR の monotonic escalation / plan-centric preflight と整合する。
  - Cons:
    - ADR と Epic docs の反映作業が先に必要になる。
  - 判断: 採用する。
- Option C: ADR 化せず `workflow_spec_authoring.md` や template に直接ルールを埋め込む。
  - Pros:
    - 実装差分は短くなる。
  - Cons:
    - なぜ standard は推奨で strict 以上は原則必須なのか、なぜ W1 を Issue 化しないのかが失われる。
    - 後続 agent が古い draft の W1 を再採用するリスクが残る。
  - 判断: 棄却する。

## 判断理由（Rationale）

- Grade 別 authoring rules は、個別 Issue の実装判断ではなく、Epic #224 全体の workflow authority を定める判断である。
- `authorized_profile` は runtime authority、manual escalation は gate 強化の authoring decision として分離すると、template selection と human safety judgment が衝突しにくい。
- `standard` で specialist を必須にすると、通常 Issue の token / wall-clock 削減という Epic #224 の目的に反する。一方で推奨に留め、使用 / 未使用理由を report evidence に残せば、必要な場面では高推論設計を使える。
- `strict` 以上は contract、compatibility、migration、template/scaffold/runtime/workflow、security/recovery などの影響が大きく、specialist draft と adoption evidence を原則必須にする価値が token cost を上回る。
- Fresh `spec-reviewer` gate は phase promotion の安全境界であり、Lite であっても弱めると template 導入後の false positive を再発させる。
- `assurance compose` と execution readiness を分離することで、template materialization 成功を実行準備完了と誤認する事故を避けられる。

## 影響（Consequences）

- Positive:
  - Follow-up Issue が上流方針を再決定せず、同じ grade-aware authoring rules に従って具体化できる。
  - `W1` を Issue から外すことで、Epic amendment と実装 Issue の責務が分離される。
  - `system-architect` / `implementation-planner` の扱いが shipped skill file 前提ではなく delegated role routing として安定する。
  - `standard` の過剰委任を避けつつ、`strict` / `critical` の安全 gate を強められる。
- Negative / Debt:
  - Epic `requirement.md` / `design.md` / `plan.md` / `report.md` への反映が必要である。
  - `guidance issue-planning`、`workflow_spec_authoring.md`、template readiness tests はこの ADR に合わせて更新が必要である。
  - Delegated specialist が unavailable な場合の manual fallback 証跡を、後続 Issue で具体化する必要がある。
- 影響範囲:
  - Epic #224 canonical docs
  - `workflow_spec_authoring.md`
  - `spec-dock-issue-planning` skill guidance
  - `guidance issue-planning`
  - `guidance issue-execution`
  - Issue profile templates and readiness validation
  - `report.md` Spec Authoring Gate / Evidence Adoption Ledger
- 移行/ロールバック:
  - 既存の Issue #247 template pack は破棄せず、`authorized_profile` に基づく template materialization source として継続する。
  - この ADR を取り消す場合は、`W1` を Issue 化する設計へ戻す新 ADR が必要である。
  - Lite automatic default は引き続き無効であり、変更する場合は既存 ADR と同様に別 ADR / policy version bump / rollout Issue を必要とする。
- Follow-ups:
  - R0: Enforce Fail-Closed Issue Artifact Readiness Preflight
  - G1: Compile Grade-Aware Issue Planning Guidance
  - G2: Connect Delegated Specialist Role Routing To Guidance And Evidence
  - G3: Add Grade-Aware Spec Review And Evidence Gates
  - G4: Add Grade-Aware Issue Authoring Smoke Tests

## 旧決定との関係（Supersession / Amendment）

- `20260623t074443z-adr Adaptive Assurance Contract Lite Authorization And Monotonic Escalation`:
  - 維持: `authorized_profile` だけが workflow obligation を減らせる authority であり、Lite automatic default は有効化しない。
  - 追加: Issue authoring grade / manual escalation は `authorized_profile` を silent override せず、authoring / review / evidence gate を強める判断として扱う。
- `20260629t003131z-adr Plan Centric Issue Execution Preflight`:
  - 維持: Issue execution authority は approved `plan.md` であり、`guidance issue-execution` は preflight validator である。
  - 追加: Issue authoring phase で grade 別 plan quality gate と specialist evidence を明示し、execution 時 runtime が worker / reviewer / verification を自由補完しない。
- `workflow_spec_authoring.md`:
  - 維持: canonical docs は main orchestrator-owned、delegated output は scope-local evidence、fresh `spec-reviewer` pass が phase promotion 条件である。
  - 追加: delegated specialist の使用要否、review focus、report evidence density は grade 別に決める。

## 非目標（Non-goals）

- `system-architect` / `implementation-planner` を必ず shipped skill file として追加することは、この ADR の scope ではない。
- `standard` のすべての Issue に specialist draft を必須化しない。
- `lite` の reviewer gate を省略しない。
- `authorized_profile` を manual escalation で暗黙に書き換えない。
- `assurance compose` を execution readiness authority にしない。
- `R0 + G1〜G4` の詳細 requirement / design / plan をこの ADR 内で確定しない。

## 未確定事項（Open Questions）

- `standard` で specialist を推奨から必須へ上げる条件の細部は、G2 / G3 の実装 Issue で guidance と report evidence contract として具体化する。ただし `standard=推奨、strict以上=原則必須` の原則はこの ADR で固定する。
- `critical` の manual approval / safety / recovery reviewer の具体 role 名と実行方法は、G3 の実装 Issue で定義する。

## 参考（References）

- `20260630t084325z-disc-grade-aware-authoring-rules-definition.md`
- `20260630t082805z-disc-epic-224-amendment-and-followup-issue-draft.md`
- `20260630t055323z-disc-issue-247-manual-test-followup-analysis.md`
- `20260630t080402z-disc-manual-test-readiness-failure-root-cause-analysis.md`
- `../requirement.md`
- `../design.md`
- `../plan.md`
- `../report.md`
- `20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`
- `20260629t003131z-adr-plan-centric-issue-execution-preflight.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
