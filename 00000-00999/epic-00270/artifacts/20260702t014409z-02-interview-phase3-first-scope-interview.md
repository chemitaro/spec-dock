---
種別: interview
ID: "20260702t014409z-02-interview"
タイトル: "Phase 3 First Scope Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-01"
  - "20260702t014409z-research"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T01:44:09Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t014409z-02-interview Phase 3 First Scope Interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Epic scope、acceptance criteria、non-goals、Phase 3 の採用境界に影響する。
  - `design.md`:
    - V3 reference 群をどの程度そのまま design envelope として採用するかに影響する。
  - `plan.md`:
    - 6 Issue セットを baseline として固定するか、Issue slicing を再設計可能な状態にするかに影響する。
  - `ADR`:
    - 現時点では ADR までは不要。長期的に scope-layering model を cross-Epic rule に昇格する場合のみ ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 回答が downstream Issue 作成、Epic plan、report adoption evidence、reviewer gate の判断根拠になるため、artifact として保存する。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - V3 ZIP の6 Issue構成を Epic plan の固定 baseline として採用するか、canonical Epic docs 作成中に Issue分割を再設計する余地を残すか。
- 回答が後続判断へ与える影響:
  - Issue作成のタイミング、Plan の dependency/order、reviewer gate の評価基準、最終PR delivery model が変わる。

## 質問

- pressure-test question:
  - V3 は「6つの具体 Issue」と「scope-layering は Epic design/plan が持つ」という方針をかなり明確にしています。この6 Issue構成を、以後の Epic plan の baseline として固定してよいですか。
- 質問:
  - `epic-00270` の具体化では、V3 ZIP の6 Issueセットを原則そのまま採用し、repo調査や reviewer findings で必要な補正だけを行う進め方でよいですか。それとも、まず canonical requirement/design/plan を作る中で Issue分割そのものを再設計する余地を残しますか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。必要なら条件付きでも構いません。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 ZIP 24 Markdown files。
  - `init-local-00003` requirement/design/plan。
  - `epic-00270` scaffold。
  - provider-side Initiative/Epic templates。
  - provider-side planning/execution skills and workflow docs。
  - recent git history around artifacts migration and issue-profile hardening。
- local context で解決できたこと:
  - 親 initiative は `init-local-00003`。
  - V2 は採用せず、V3 を raw intake evidence として保存する。
  - 新規 working evidence は `artifacts/` に置く。
  - 現在のギャップは主に Initiative/Epic planning surface であり、Issue grade/TDD surface や artifacts surface は直近履歴で既に強化済み。
- まだ人間判断が必要な理由:
  - V3 は6 Issueを提示しているが、これを「固定 baseline」とするか「強い提案」とするかは maintainer の delivery 方針に関わる。

## 回答案

- Option A:
  - V3 の6 Issueセットを baseline として固定する。Canonical Epic docs はこの構成を前提に具体化し、補正は repo facts / reviewer findings /明確な矛盾に限定する。
- Option B:
  - V3 は採用候補として扱うが、canonical Epic requirement/design/plan の作成中に Issue分割を再設計してよい。
- Option C:
  - V3 の6 Issueセットは固定するが、final delivery は1 PR前提ではなく、IssueごとのPR分割も plan に明記してよい。

## Codex の分析

- 判断軸:
  - Epic-level design ownership を保てるか。
  - downstream Issue が execution-ready handoff を受け取れるか。
  - PR delivery / manual test / reviewer repair loop をどこまで一体化するか。
- tradeoff:
  - Option A は最も速く、V3 の設計意図を保ちやすい。一方、あとで Issue粒度の微調整が必要なら report/deferred evidence が必要。
  - Option B は柔軟だが、V3 が解消した「scope-layering を別Issueにする」問題へ戻るリスクがある。
  - Option C は大きいEpicの運用リスクを下げるが、V3 の final quality/one coherent PR という delivery model を弱める。
- リスク:
  - baseline を固定しないまま Issue作成に進むと、decision-only Issue や insufficient handoff が混入しやすい。
  - baseline を固定しすぎると、repo現物のテスト/skill構造に合わない slice を無理に残す可能性がある。
- 具体シナリオ / edge case:
  - Issue 03 と Issue 04 の境界が実装中に重なる場合、Option A でも reviewer findings に基づく補正として plan へ反映できる。

## Codex の推奨案

- 推奨:
  - Option A。V3 の6 Issueセットを baseline として固定し、repo facts / reviewer findings で必要な補正のみ許す。
- 理由:
  - V3 は不足していた upstream planning analysis を補完するために作成されており、現在の repo 調査結果とも大きく矛盾しない。
  - 6 Issue は Initiative templates、Epic templates、skills/docs、Epic execution、tests、final delivery と関心事が分かれていて、実装順も自然。
  - この方針なら、まず Epic canonical docs を reviewer-gated に具体化し、その後 Issue scaffold / planning へ進める。
- 未回答時の影響:
  - Canonical `plan.md` で Issue list を固定しきれず、Issue作成前に追加質問が必要になる。

## ユーザー回答

- answer capture:
  - Option B を採用する。ただし V3 の6 Issueを完全に捨てるのではなく、暫定 baseline として扱う。
  - これから一緒に議論しながら Epic を具体化するため、当初想定していなかった課題や作業区分が見つかった場合は、6 Issue の slice にこだわらず追加 Issue や再分割を許す。
  - 無闇な追加は推奨しない。原則は既存6 Issueで進め、必要に応じて柔軟に変更する。
- 回答:
  - `epic-00270` の Issue slicing は、V3 の6 Issueを暫定 baseline としつつ、調査・議論・reviewer findings により必要と判断できる場合は追加 Issue / 再分割を許容する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 次は、追加 Issue / 再分割を許可する判断基準を Epic design/plan にどの強さで固定するかを確認する。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md` / `design.md` / `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Epic 具体化の進め方として、V3 の6 Issueを暫定 baseline としながら、必要な場合の追加 Issue / 再分割を許容する判断が明示されたため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Scope/non-goal/acceptance criteria に、V3 の6 Issueを暫定 baseline とするが、必要時の追加 Issue / 再分割を許容する方針を反映する。
- `design.md`:
  - Scope-layering model と upstream abstraction model を採用しつつ、Issue slicing は Epic design/plan の判断対象として柔軟性を残す。
- `plan.md`:
  - 6 Issue baseline、追加 Issue 判断基準、dependency/order/final gate、再分割時の report evidence を反映する。
- `ADR`:
  - 今回は不要見込み。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - canonical docs へ反映するまでは、この interview artifact が user-approved evidence。`report.md` Evidence Adoption Ledger へ採用記録を残す必要がある。
