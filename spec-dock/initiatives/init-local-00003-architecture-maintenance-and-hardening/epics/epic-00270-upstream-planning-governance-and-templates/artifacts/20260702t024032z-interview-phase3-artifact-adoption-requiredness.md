---
種別: interview
ID: "20260702t024032z-interview"
タイトル: "Phase 3 Artifact Adoption Requiredness"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t020503z-01-disc"
  - "20260702t020436z-01-disc"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T02:40:32Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved evidence"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t020503z-01-disc-phase3-scope-authority-model.md"
  - "artifacts/20260702t020436z-01-disc-phase3-reference-adoption-map.md"
reflected_to:
  - "artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md"
  - "report.md"
---

# 20260702t024032z-interview Phase 3 Artifact Adoption Requiredness

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Discovery artifacts を requirement input として扱う条件に影響する。
  - `design.md`:
    - Research / interview / decision-candidate を design decision へ採用する手順に影響する。
  - `plan.md`:
    - Report Evidence Adoption Ledger / Spec Authoring Gate の必須度に影響する。
  - `report.md`:
    - EAL の必須記録対象が変わる。
- chat 上の軽微な一問では足りない理由:
  - artifacts は Phase 2 で強化された重要surfaceだが、raw evidence のまま実装根拠にすると canonical authority model が壊れる。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - Initiative/Epic authoring で artifacts を参照・採用するとき、どの程度 `report.md` Evidence Adoption Ledger を必須にするか。
- 回答が後続判断へ与える影響:
  - Templates、planning skills、workflow docs、reviewer gates、smoke tests の必須項目が変わる。

## 質問

- pressure-test question:
  - artifacts を使いやすくしつつ、raw artifact が勝手に canonical authority になる事故をどう防ぎますか。
- 質問:
  - Initiative/Epic authoring で artifact adoption evidence はどの程度必須にしますか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 `discovery-to-canonical-specs.md` は artifacts are working evidence only とし、artifact note -> requirement/design/plan update -> report adoption evidence を示している。
  - Current templates already include Evidence Adoption Ledger in report templates.
  - `workflow_clarification.md` and `phase_design.md` already distinguish artifacts from canonical docs.
  - Deep consultant recommendation included no artifact authority leak as a smoke check.
- local context で解決できたこと:
  - Artifacts are not canonical authority.
  - Canonical docs or accepted ADR must reflect adopted facts.
  - Report EAL is the natural place to record adoption.
- まだ人間判断が必要な理由:
  - すべての軽微なartifact参照までEAL必須にすると運用が重くなる一方、重要判断だけに絞ると境界が必要。

## 回答案

- Option A:
  - 軽め。EAL は delegated drafts / major decisions / reviewer findings のみ必須。通常のresearch参照は canonical docs に反映されていればよい。
- Option B:
  - 中程度。Canonical requirement/design/plan の判断・制約・Issue slicing・handoffに影響する artifact adoption は EAL 必須。軽微な背景参照やリンクはEAL不要。Raw artifactを実装根拠にする記述は fail。
- Option C:
  - 強め。Canonical docs が artifacts を参照する場合はほぼすべて EAL 必須。EALなしのartifact参照は reviewer fail。

## Codex の分析

- 判断軸:
  - Authority leak 防止。
  - 運用負荷。
  - Reviewer が採用判断を追えるか。
  - Lightweight CLI toolとしてのSpecDockに過剰儀式を持ち込まないか。
- tradeoff:
  - Option A は軽いが、重要なresearch/interview adoptionがEALに残らない可能性がある。
  - Option B は重要判断だけEAL必須にでき、運用負荷と追跡性のバランスがよい。
  - Option C は追跡性が高いが、artifact参照が多いEpicで重すぎる。
- リスク:
  - EAL必須条件が曖昧だと、後続エージェントが記録を省く。
  - 必須範囲が広すぎると、reportが儀式化する。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - V3のauthority flowを守りつつ、軽微な参照までEAL化しない。
  - 重要な採用判断、Issue slicing、handoff、constraints は追跡可能になる。
  - Existing report template のEALを活用できる。
- 未回答時の影響:
  - Initiative/Epic templates と planning skills の artifact adoption guidance が固定できない。

## ユーザー回答

- answer capture:
  - 完全な要件定義書、設計書、計画書を作成するには、完全な理解が必須であり、曖昧な情報で決定してはならない。
  - ただし、すべてをユーザーへ質問するのではなく、コードベース、既存設計方針、過去の調査・分析から分かることはエージェントが自分で調査する。
  - 完全な理解を達成する上でユーザーに確認しなければ分からないことだけを、的確にインタビューする。
  - 理解や判断はコンテキストに保持するだけではなく、artifacts / canonical docs / ADR / report ledger へ外部化する。
  - 今後のインタビューもこの方針に従う。
- 回答:
  - A/B/C の強弱選択ではなく、「完全理解は必須」「自力調査可能なことは自力で行う」「ユーザー判断が必要な点だけ質問する」「知識は外部化する」を採用する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Epic execution skill が handoff package を検査する強さ。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `design.md` / `plan.md` / report template guidance / planning skills / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが明示的に、完全理解・自力調査・必要最小限のユーザー質問・知識の外部化を今後の interview / authoring 方針として採用した。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Discovery artifact references and adopted constraints.
- `design.md`:
  - Artifact-to-canonical authority flow.
- `plan.md`:
  - Evidence Adoption Ledger requiredness and reviewer gates.
- `ADR`:
  - この判断は今後の interview / authoring 全体へ効くため、`20260702t025127z-adr-complete-understanding-before-canonical-authoring.md` へ格上げする。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - `artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md` と `report.md` EAL-010 へ反映する。
