---
種別: research
ID: "20260613t083027z-research"
タイトル: "Deep Consultant Skill Policy Findings"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-13"
親: ["iss-00186"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260613t083027z-research Deep Consultant Skill Policy Findings

## 調査目的 (必須)
- `iss-00186` のために起動した deep-consultant 2 名の追加分析を、canonical docs へ採用可能な research finding として整理する。
- 既存の skill/docs/templates responsibility policy と、`spec-dock-issue-execution` update scope の妥当な境界を確認する。
- Raw transcript ではなく、source-grounded findings、推論、未検証事項、後続 authoring への含意を残す。

## sources / 調査方法 (必須)
- 参照先:
  - deep-consultant `019ec014-ded8-7072-84d5-9c6b74ec73f8` output.
  - deep-consultant `019ec014-be73-7be3-a0db-4a3a67a7940a` output.
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00162-align-skill-docs-template-context-surfaces/discussions/20260606t040013z-disc-context-surface-inventory.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00166-align-templates-as-scaffolds-and-examples/requirement.md`
- 検証手順:
  - Consultant A に、既存方針を踏まえた `spec-dock-issue-execution` の最小 coherent change set を分析させた。
  - Consultant B に、skill 作成 / docs / templates の responsibility policy と既存 records を探索させた。
  - 両者の findings を、local analysis artifact `20260613t082454z-research-issue-execution-step-gate-analysis.md` と `20260613t082641z-research-skill-workflow-spine-policy-analysis.md` と突き合わせた。
- 実験条件:
  - Consultants は read-only analysis のみ。ファイル編集は main orchestrator が research artifact 作成として実施した。
  - Canonical requirement / design / plan / report への採用はまだ行っていない。

## facts / 観測できた事実 (必須)
- Consultant A は、provider 側 docs/templates が `iss-00186` の中核である sequential step、per-step review、per-step commit、親 agent direct mutation 禁止、`dev-coder` / `doc-writer` 委任をすでにかなり表現していると評価した。
- Consultant A は、skill は `workflow_issue.md` を source of truth とし full workflow をコピーしない方針を維持すべきだと評価した。
- Consultant A は、最小変更として `spec-dock-issue-execution` skill に 1 bullet だけ追加し、per-step cadence、delegation gate、review、commit/clean before next step を目立たせる案を提示した。
- Consultant A は、`workflow_issue.md` は大きな変更不要で、必要なら next step 前に commit/clean 完了を軽く補強する程度がよいとした。
- Consultant A は、`authoring/issue-plan.md` / `phase_plan_issue.md` の ownership 分離は正しいため、`workflow_issue.md` policy を再定義せず、plan へどう埋めるかだけを書く方針を維持すべきとした。
- Consultant A は、templates は必要 slot をすでに持つため、skill-only wording update なら template 更新不要、workflow wording を変えた場合のみ矛盾確認が必要とした。
- Consultant A は、skill fragment assertion が `tests/unit/infra/test_init_update.py` にあるため、skill 文言変更時は最小更新が必要とした。
- Consultant B は、accepted ADR が Skills / Docs / Templates の責務分担を固定していると確認した。Skills は operational workflow spine、Docs は concepts / field meanings / policy details / hard-case criteria、Templates は scaffolds / evidence slots / examples である。
- Consultant B は、先行 synthesis が問題を runtime enforcement 不足ではなく、skill が薄く mandatory workflow が docs に分散して見落とされる問題として整理していると確認した。
- Consultant B は、hub skill も同じ方針で、skills are first-read workflow spine、docs are detailed semantics、templates are not compliance authorities と明記していると確認した。
- Consultant B は、`spec-dock-issue-execution` skill は現時点でも readiness gate、executable `plan.md`、unresolved gap return、report ledger、delegation routing、unavailable tooling incomplete を持つが、`current step only -> review pass -> commit -> clean -> next step unlock` loop が入口で十分に目立たないと評価した。
- Consultant B は、`workflow_issue.md` は detail authority として parent orchestration owner、step order、pass-until-review gates、full completion evidence を持つと確認した。
- Consultant B は、`authoring/issue-plan.md` が field semantics / executable step schema detail authority として `delegation contract`、`具体テストケース一覧`、reviewer fail conditions を定義すると確認した。
- Consultant B は、templates は evidence slots と examples を提供するが compliance authority ではなく、`N/A delegated role` や multi-step bundled log が通常成功に見える表現は避けるべきとした。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `iss-00186` は `workflow_issue.md` の policy を skill へ全文移植する issue ではない。
  - 中心 deliverable は、`spec-dock-issue-execution` を first-read で踏み外しにくい execution gate spine にすることである。
  - 詳細 semantics は `workflow_issue.md` / `authoring/issue-plan.md` / templates に残し、skill は first action / stop condition / route / exit gate に集中させるべきである。
  - Consultant A は最小差分を強く推しており、Consultant B は既存方針への alignment を強く推している。両者は「skill を厚くしすぎない」「入口 gate は目立たせる」という点で一致している。
  - Local analysis で挙げた template / prompt alignment は有効だが、`iss-00186` の scope として採用する場合は requirement / design で明示的に範囲管理が必要である。
- 推測の根拠:
  - Consultant A と B は、異なるレンズでも `workflow_issue.md` authority 維持と skill top-loaded reminder 強化に収束した。
  - 既存 ADR / synthesis / inventory / hub skill が、skill/docs/templates の責務分担を一貫して示している。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Consultant B が参照した accepted ADR の正確な採用状態と、現在の canonical docs への反映状況。
  - `tests/unit/infra/test_init_update.py` の該当 assertion の現在内容。
  - Provider / dogfooding mirror の `spec-dock-issue-execution` skill と docs/templates の byte-level parity。
  - skill-only wording update で empirical behavior が改善するか。
- 確認できない理由:
  - この artifact は consultant findings の整理であり、まだ design / implementation / verification phase へ進んでいない。
  - empirical behavior は別途 fixture / prompt harness が必要である。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `iss-00186` の実装 scope を skill + workflow wording の最小差分に絞るか、templates / prompt / tests まで含めるか。
  - Empirical harness をこの issue の必須検証に含めるか、follow-up とするか。
- pressure-test question として切り出すべき候補:
  - 既存方針に沿って「skill へ追加するのは 1 bullet 相当の per-step cadence reminder に留め、詳細は docs/templates の整合確認へ回す」方針で十分か。
- 質問せずに解決できた候補:
  - Skill / docs / templates の責務分担は existing records から確認できた。
  - `spec-dock-issue-execution` の問題は policy 不在ではなく entry spine visibility 不足だと確認できた。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `source of truth`
  - `operational workflow spine`
  - `detail authority`
  - `template scaffold`
  - `approved-local-execution`
  - `degraded mode`
- 既存 docs / code / tests / discussions での使われ方:
  - `source of truth` は `workflow_issue.md` に詳細 policy を置くという意味で使われているが、skill が first-read operational action を持つことと矛盾しない。
  - `operational workflow spine` は agent が次に何を読む / 何を止める / どこへ handoff するかを示す薄い実行 spine である。
  - `detail authority` は docs が lifecycle policy / field semantics / hard cases を持つことを指す。
  - `template scaffold` は evidence slots / examples を提供するが compliance authority ではない。
  - `approved-local-execution` と `degraded mode` は通常成功値に見えるリスクがあり、例外 / availability evidence として扱いを明確化する必要がある。
- 判断が必要な理由:
  - 用語境界を明確にしないと、skill を厚くしすぎるか、逆に docs-only に寄せすぎて entry gate が見えなくなる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Skill に per-step cadence reminder を 1 bullet だけ追加しても、templates / prompt が multi-step bundle を誘うままで効果が弱い。
  - Template 更新まで含めると scope が膨らみ、`iss-00186` が skill hardening issue から scaffold governance issue へ膨張する。
  - Empirical harness を必須にすると、first change の delivery が遅れる。
  - Skill 文言変更に test assertion があり、最小 wording change でも tests update が必要になる。
- その edge case が requirement / design / plan に与える影響:
  - Requirement では scope / non-scope を明確にし、skill-only / workflow-doc / template / prompt / tests のどこまでを含むかを決める必要がある。
  - Design では provider source と mirror validation、test assertion update、template alignment check を分けて扱う必要がある。
  - Plan では research adoption、skill wording, workflow wording, test assertion, mirror sync / validate を step 分割する必要がある。

## implications / 判断への含意 (必須)
- Requirement 候補:
  - `spec-dock-issue-execution` を first-read execution spine として、sequential step / delegation / review / commit / clean / next-step unlock を踏み外しにくくする。
  - Detailed lifecycle / field semantics は docs に残し、skill へ全文移植しない。
  - Parent direct implementation、degraded mode、final commit の境界を通常成功と誤読されないようにする。
- Design 候補:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` に top-loaded per-step cadence reminder を追加する。
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` は必要最小限の exact semantics 補強に留める。
  - `authoring/issue-plan.md` / templates / prompts は alignment check の対象にし、変更要否は design で判断する。
  - Provider source を変更し、dogfooding mirror は sync / parity / validate で確認する。
- Plan 候補:
  - S01 research adoption and scope lock.
  - S02 skill reminder wording.
  - S03 workflow exact semantics if needed.
  - S04 tests / assertion update if wording changes.
  - S90 docs/templates/prompt alignment check.
  - S99 final reviews and validation.

## 追加確認（2026-06-13）
- Accepted ADR `20260605t080509z-adr-skill-docs-template-context-surface-ownership.md` は、Skills / Docs / Templates の ownership model を accepted decision として固定している。
  - Skills: operational workflow spine that the model must follow during the task.
  - Docs: concepts, field meanings, policy details, references, hard-case decision criteria.
  - Templates: scaffolds, evidence slots, good examples; templates are not compliance authorities.
- 同 ADR は、mandatory workflow を docs に置くだけの薄すぎる skill も、full docs を skill にコピーする厚すぎる skill も rejected とし、compact workflow spine in skills + details in docs/templates を accepted としている。
- `iss-00162` inventory は `spec-dock-issue-execution` を mixed skill-owned spine and docs-detail routing と分類し、`workflow_issue.md` を docs-owned detail with hidden execution-policy density と分類している。この分類は `iss-00186` の直接前提になる。
- `tests/unit/infra/test_init_update.py` は `workflow_issue.md` と provider-side `spec-dock-issue-execution` skill の具体 fragment を assert している。skill 文言や workflow wording を変更する場合、該当 assertion の最小更新が必要になる。
- 特に現在の test は `spec-dock-issue-execution` skill に次の fragment が残ることを期待している:
  - `spec-dock/docs/workflow_issue.md as the source of truth`
  - `concise reminder for issue execution`
  - `parent agent responsible for orchestration`
  - `Route runtime, tests, and scaffold behavior to `dev-coder``
  - `Route shipped docs, templates, skills, and workflow text to `doc-writer``
  - `bounded delegated follow-up`
  - `Parent direct fixes require a documented Parent Implementation Exception`
- したがって、`iss-00186` の実装計画では、skill の phrase を置換するより既存 fragment を保持して additive に per-step cadence reminder を足す方がテスト影響が小さい。
- もし `approved-local-execution` / `degraded mode` の語を変更または削除する場合、`workflow_issue.md` fragment assertion も影響するため、scope が大きくなる。

## リスク/制約 (任意)
- Consultant A の最小方針と local analysis の template / prompt alignment 方針には scope size の差がある。requirement / design で採用範囲を明確化する必要がある。
- Skill wording の効果は empirical harness なしでは推定に留まる。
- Accepted ADR / synthesis / inventory を canonical authority として採用するには、report evidence ledger で adoption decision が必要である。

## 反映先 (任意)
- reflected_to:
  - candidate: `requirement.md`
  - candidate: `design.md`
  - candidate: `plan.md`
  - candidate: `report.md` Evidence Adoption Ledger
  - candidate: follow-up issue if empirical harness or template broadening is out of scope

## 参考（References） (任意)
- `.agents/skills/spec-dock-hub/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00162-align-skill-docs-template-context-surfaces/discussions/20260606t040013z-disc-context-surface-inventory.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00166-align-templates-as-scaffolds-and-examples/requirement.md`
