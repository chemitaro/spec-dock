---
種別: interview
ID: "20260702t015012z-interview"
タイトル: "Phase 3 Issue Slicing Flexibility Criteria"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-02-interview"
  - "20260702t014409z-research"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T01:50:12Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t014409z-02-interview-phase3-first-scope-interview.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t015012z-interview Phase 3 Issue Slicing Flexibility Criteria

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Scope / non-goal と Epic acceptance criteria に、Issue追加・再分割をどの程度許すかが影響する。
  - `design.md`:
    - Epic が所有する design slice catalog と downstream Issue handoff の安定性に影響する。
  - `plan.md`:
    - Issue list、dependency/order、Issue readiness criteria、追加 Issue の evidence 条件に直接影響する。
  - `ADR`:
    - 現時点では不要。将来この判断基準を全 Epic 共通ルールへ昇格する場合だけ ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 前回回答で「6 Issue は暫定 baseline、必要なら追加/再分割可」と決まったため、むやみな増殖を防ぐ判断基準を artifact として残す必要がある。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - 追加 Issue / 再分割を許す条件を、Plan 上の軽いガードレールにするか、強い gate にするか。
- 回答が後続判断へ与える影響:
  - Canonical `plan.md` の Issue slicing policy、Issue readiness criteria、追加 Issue 作成前の report evidence、reviewer gate の強さが変わる。

## 質問

- pressure-test question:
  - 6 Issue baseline を柔軟に変えられるようにする一方で、「なんとなく増やす」を防ぐには、追加/再分割の条件をどの強さで固定するべきですか。
- 質問:
  - 追加 Issue / 再分割を行う条件は、どれに近い形で Epic plan に入れるのがよいですか。
- 回答してほしいこと:
  - A / B / C のどれに近いか、または組み合わせたい条件を教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 ZIP full intake artifact。
  - Repo context and implementation survey。
  - First scope interview answer: 6 Issue は暫定 baseline。必要なら追加 Issue / 再分割を許すが、むやみに追加しない。
  - `workflow_epic.md`: Epic は Issue 分割、責務境界、依存方向、rollout 順に影響する durable decision を所有する。
  - `phase_plan_epic.md`: Epic plan は issue slicing strategy / order / integration checkpoint / readiness contract / final exit contract を固定する。
- local context で解決できたこと:
  - 追加/再分割を完全禁止する必要はない。
  - 追加/再分割を無制限に許すと V3 の scope-drift anti-pattern に反する。
  - 判断基準は canonical `plan.md` と `report.md` evidence に反映するのが自然。
- まだ人間判断が必要な理由:
  - どの程度 gate を強くするかは、開発速度と governance のバランス判断であり、repo facts だけでは決まらない。

## 回答案

- Option A:
  - 軽いガードレールにする。追加/再分割は main orchestrator 判断で可能。ただし理由、影響、V3 baseline との差分を `report.md` または artifact に記録する。
- Option B:
  - 中程度の gate にする。追加/再分割は、既存6 Issueでは独立レビュー性・責務境界・検証可能性・PR delivery のいずれかが明確に悪化する場合に限り、`plan.md` 更新と fresh `spec-reviewer` gate を必要にする。
- Option C:
  - 強い gate にする。追加/再分割は原則禁止に近く、ユーザー確認または reviewer 指摘がある場合のみ許す。

## Codex の分析

- 判断軸:
  - 6 Issue baseline の安定性。
  - 想定外の課題を吸収する柔軟性。
  - Issue 増殖の防止。
  - downstream Issue が execution-ready handoff を受け取れるか。
- tradeoff:
  - Option A は速いが、後から scope drift と見分けにくくなる。
  - Option B は柔軟性と統制のバランスがよい。Plan 更新と reviewer gate を挟むため、追加/再分割が canonical に追跡される。
  - Option C は統制が強いが、今回の「議論しながら具体化する」進め方には少し硬い。
- リスク:
  - gate が弱すぎると、final quality Issue が膨らむか、skills/docs/tests の境界が曖昧になる。
  - gate が強すぎると、調査で見つかった自然な作業区分を無理に6 Issueへ押し込む。
- 具体シナリオ / edge case:
  - Skills と workflow docs の更新が大きく分かれる場合、Issue 03 を2つに分ける可能性がある。
  - Smoke tests と final manual quality gate が重複する場合、Issue 05/06 の境界を調整する可能性がある。
  - 新しい scope-layering reference doc を provider docs に追加する必要が出た場合、既存 Issue の中に入れるか追加 Issue にするか判断が必要。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - ユーザー回答の「暫定は6だが柔軟に変更」を最も忠実に operationalize できる。
  - 追加/再分割を許しつつ、`plan.md` 更新と fresh `spec-reviewer` gate によって decision-only drift を防げる。
  - V3 の upstream planning governance という Epic 目的にも合う。
- 未回答時の影響:
  - Canonical `plan.md` に追加/再分割条件を書けず、Issue作成前に再確認が必要になる。

## ユーザー回答

- answer capture:
  - Option B を採用する。
  - ただし、これは追加 Issue / 再分割を推奨するものではない。
  - 今後 Epic plan を具体化する中で、既存6 Issueでは独立レビュー性・責務境界・検証可能性・PR delivery のいずれかが悪化する場合に限り、必要に応じて Issue を増やす。
  - Issue 追加は柔軟に対応する必要があるが、むやみに増やすものではない。
- 回答:
  - 追加 Issue / 再分割は中程度の gate とする。既存6 Issueを暫定 baseline とし、必要性が説明できる場合に限って `plan.md` 更新と fresh `spec-reviewer` gate を通して変更する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - PR delivery を1本に寄せるか、IssueごとのPRも許すか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Issue追加を推奨しない前提を保ちながら、計画具体化中に必要な再分割を許す operational gate が明示されたため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - 追加/再分割は推奨ではなく、必要時の柔軟性として Scope / non-goal に反映する。
- `design.md`:
  - Design slice catalog と Issue handoff package の変更条件として、独立レビュー性・責務境界・検証可能性・PR delivery の悪化を判断軸にする。
- `plan.md`:
  - Issue slicing policy、Issue readiness criteria、Plan update、fresh `spec-reviewer` gate 条件として反映する。
- `ADR`:
  - 今回は不要見込み。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - canonical docs へ反映するまでは、この interview artifact が user-approved evidence。`report.md` Evidence Adoption Ledger へ採用記録を残す必要がある。
