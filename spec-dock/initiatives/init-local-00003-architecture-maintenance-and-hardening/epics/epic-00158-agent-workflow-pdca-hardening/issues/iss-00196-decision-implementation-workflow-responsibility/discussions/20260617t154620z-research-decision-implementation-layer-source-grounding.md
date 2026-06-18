---
種別: research
ID: "20260617t154620z-research"
タイトル: "Decision Implementation Layer Source Grounding"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260617t154620z-research Decision Implementation Layer Source Grounding

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00196` の要件具体化に向けて、SpecDock の既存 workflow / skill / parent epic に、decision layer と implementation layer の責務境界がどこまで既に表現されているかを確認する。
- ユーザーへ質問すべき論点を、local source で解ける事実と、人間の意図確認が必要な判断に分ける。

## sources / 調査方法 (必須)
- 参照先:
  - `gh issue view 196 --json number,title,body,state,url`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_initiative.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/install_root/.agents/skills/**`
- 検証手順:
  - `issue start iss-00196` で active scope を固定した。
  - active issue / parent epic / workflow docs / related skills を読み、既存の責務境界表現と不足している gate を分類した。
  - provider-side source と dogfooding mirror の両方を検索し、decision / implementation / readiness / clarification 関連の既存表現を確認した。
- 実験条件:
  - この調査は authoring / clarification phase の source-grounding であり、canonical docs はまだ変更していない。

## facts / 観測できた事実 (必須)
- `iss-00196` の canonical `requirement.md` は import 直後の template 状態で、実質的な要件は GitHub issue body にある。
- GitHub issue body は、Issue が「何かを決める場所」になり、実装可能な単位へ落ちない failure mode を問題としている。
- GitHub issue body は、「決定は上位レイヤーで行い、実装は下位レイヤーで行う」「Issue は具体的な実装・検証・移行・反映の単位」という方針を提案している。
- Parent epic `epic-00158` は、skills / docs / templates の context surface ownership、reviewer gate、evidence adoption、provider source / dogfooding mirror boundary を主対象にしている。
- Parent epic design は、skills が workflow spine、docs が detail semantics、templates が scaffold / examples を所有する boundary を既に採用している。
- Parent epic plan は、first wave では runtime gate / automated harness を blocker にしない方針を採用している。
- `workflow_issue.md` は「Issue は実装の最小単位」と明記しているが、decision-only issue を検出して Epic / Initiative へ戻す entry gate はまだ十分に明文化されていない。
- `workflow_epic.md` は「Epic は設計の背骨」と明記しているが、Issue へ渡す前に Epic が決めるべき decision set / carry-over allowed uncertainty は薄い。
- `workflow_initiative.md` は「Initiative は投資単位」と明記しているが、複数 Epic / 横断プロダクト方針を Initiative に戻す具体的な routing criteria は薄い。
- `workflow_spec_authoring.md` は requirement / design / plan phase gate と clarification return を定義しているが、scope-level decision ownership の見分け方は主題ではない。
- `spec-dock-issue-planning` skill は unresolved gaps を clarification / prior authoring phase へ戻すと明記しているが、decision-only issue や上位 scope への戻し条件を first-read gate として持っていない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `iss-00196` は runtime enforcement ではなく、workflow docs / planning skills / templates の first-read gate と checklists を追加・整合させる docs/skill/template issue として扱うのが parent epic と整合する。
  - 具体化すべき中心は「どの scope がどの種類の decision を所有するか」と「Issue planning 中に上位 scope へ戻す条件」である。
  - 受け入れ条件は、文言追加だけでなく、agent が dogfooding で使える short checklist と、issue requirement / design / plan template への反映を含めると実効性が上がる。
- 推測の根拠:
  - Parent epic は context surface cleanup を主対象にし、runtime gate / harness を deferred にしている。
  - GitHub issue body の変更候補は workflow docs と planning / clarification skills であり、runtime CLI は含まれていない。
  - 既存 docs は scope の役割を説明しているが、decision routing の gate としては未整備である。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - ユーザーがこの issue で必ず template まで更新したいか、それとも workflow docs / skills の明文化を先に閉じたいか。
  - `management_core` / shared kernel boundary の具体例を、SpecDock 汎用 docs に例として載せるべきか、project-local dogfooding evidence に留めるべきか。
  - この issue の完了条件に ADR candidate triage を含めるべきか。
- 確認できない理由:
  - これらは local source だけではユーザーの意図と許容スコープを確定できないため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - この issue の主成果物を「workflow docs / skills の decision routing gate」に絞るか、「templates の checklist / scaffold 更新」まで含めるか。
  - management_core / shared kernel boundary のような具体例を generic docs に載せるか。
  - ADR candidate triage を完了条件に含めるか。
- pressure-test question として切り出すべき候補:
  - Scope boundary: `iss-00196` では、workflow docs / skills への gate 明文化に加えて templates まで更新するべきか。
- 質問せずに解決できた候補:
  - Runtime enforcement は first fix の主対象外。parent epic が runtime gate / harness を deferred としているため。
  - Canonical issue docs はまだ template のため、GitHub issue body と parent epic を source として requirement 具体化を始める必要がある。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `decision layer`
  - `implementation layer`
  - `Issue readiness gate`
  - `Epic planning gate`
- 既存 docs / code / tests / discussions での使われ方:
  - 既存 docs は `Issue は実装の最小単位`, `Epic は設計の背骨`, `Initiative は投資単位` と表現している。
  - `workflow_spec_authoring.md` は `WHAT / WHY` を requirement、`HOW` を design、executable work を plan へ分けるが、scope-level decision ownership は明示していない。
- 判断が必要な理由:
  - 新しい用語を増やすと docs/skills が重くなる一方、既存語彙だけでは user-reported failure mode を検出しにくい。

## edge cases / 具体シナリオ (必須)
- edge case:
  - 軽微な実装中判断: small naming / local fallback / simple file placement など、Issue 内で即断してよいもの。
  - decision-only issue: 受け入れ条件が「決定する」「調査して方針を出す」だけで、観測可能な変更がないもの。
  - cross-issue architecture decision: dependency direction、ownership、shared kernel boundary など、複数 Issue の実装単位を変えるもの。
  - cross-epic product direction: 複数 Epic や product policy に影響する decision。
- その edge case が requirement / design / plan に与える影響:
  - 軽微な判断は Issue 内許容として例外規則に入れる。
  - decision-only issue は Epic / Initiative clarification / discussion / ADR candidate へ戻す gate にする。
  - cross-issue decision は Epic design / discussion / ADR candidate へ戻す。
  - cross-epic decision は Initiative requirement / design / plan へ戻す。

## implications / 判断への含意 (必須)
- `requirement.md` には、scope-level decision ownership と Issue readiness gate / Epic planning gate / clarification routing を必須スコープとして書く必要がある。
- `design.md` では、どの docs / skills / templates にどの粒度で gate を置くかを、provider-side source と dogfooding mirror boundary に沿って設計する必要がある。
- `plan.md` では、docs/skills と templates を混ぜる場合は step を分け、docs-only / skill-text-only / template scaffold の review scope を明確にする必要がある。
- ADR は必須ではないが、「decision layer / implementation layer」という新しい durable policy を既存 scope workflow の上位原則として固定するなら ADR candidate になり得る。

## リスク/制約 (任意)
- Gate を強くしすぎると、軽微な Issue 内判断まで Epic / Initiative に戻す過剰運用になり、作業速度を落とす。
- Gate が抽象的すぎると、agent が実際の issue planning で使えず、現在の failure mode が残る。
- Scope を広げすぎると、workflow docs / skills / templates / ADR / runtime gate が混ざり、parent epic の first-wave boundary を破る。

## 反映先 (任意)
- reflected_to:
  - pending: `spec-dock/active/issue/requirement.md`
  - pending: `spec-dock/active/issue/report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- GitHub issue `#196`
- Parent epic `epic-00158`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_initiative.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/workflow_clarification.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-hub/SKILL.md`
