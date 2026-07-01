---
種別: interview
ID: "20260701t022257z-interview"
タイトル: "Parent Epic P2 Promotion Policy Clarification"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["iss-00257"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00257"
created_at: "2026-07-01T02:22:57Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "specdock-pr-review-policy-update.zip/docs/issue-draft.md"
  - "specdock-pr-review-policy-update.zip/docs/implementation-notes.md"
  - "specdock-pr-review-policy-update.zip/docs/codex-initial-prompt.md"
  - "specdock-pr-review-policy-update.zip/docs/self-review.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/design.md"
reflected_to: []
---

# 20260701t022257z-interview Parent Epic P2 Promotion Policy Clarification

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `iss-00257` が親 Epic の既存 P2 promotion rule を置換する Issue なのか、Issue-local な例外として扱うのかで、目的、範囲、非目標、受け入れ条件が変わる。
  - `design.md`:
    - PR blocker policy の不変条件を `P0/P1 only` に固定するか、親 Epic の `P2 protected-domain + machine evidence` 昇格を残すかで、`pr_review_snapshot.py` と merge-preparer skill の設計境界が変わる。
  - `plan.md`:
    - 親 Epic docs の amendment を実装 step に含めるか、Issue-local docs と code/tests のみで閉じるかで作業単位と verification が変わる。
  - `ADR`:
    - 現時点では ADR 必須とは判断していない。ただし親 Epic の長期方針を恒久的に反転するなら ADR または Epic amendment が必要になる可能性がある。
- chat 上の軽微な一問では足りない理由:
  - 親 Epic は現在、P2 protected-domain + machine evidence を validated blocker へ昇格する方針を保持している。一方、添付 bundle はその自動昇格を明示的に禁止しており、どちらを canonical 方針として採用するかが後続 artifact 全体に影響する。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `iss-00257` で、親 Epic の旧 P2 promotion 方針を明示的に上書きするかどうか。
- 回答が後続判断へ与える影響:
  - 上書きする場合は、Issue 要件に supersession / amendment を明記し、必要なら親 Epic の関連記述更新も plan に含める。上書きしない場合は、Issue-local な運用例外として範囲を限定し、親 Epic 方針との共存条件を設計に残す。

## 質問 (必須)
- pressure-test question:
  - P2/P3-only terminal observation を本当に「コード修正・branch mutation・再レビュー不要」とするには、親 Epic に残る P2 protected-domain promotion rule をどの scope で無効化する必要があるか。
- 質問:
  - `iss-00257` は、親 `epic-00224` に残っている「P2 が protected domain かつ machine evidence ありなら validated blocker へ昇格する」方針を、今回の Issue で明示的に廃止・上書きする扱いで進めてよいですか？
- 回答してほしいこと:
  - `yes`: 親 Epic 方針の amendment として扱い、Issue 要件・設計・計画で旧ルール廃止を明記する。
  - `no`: 親 Epic 方針は残し、今回の bundle が対象とする PR review / merge-preparer loop に限定した例外または暫定運用として設計する。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `specdock-pr-review-policy-update.zip/docs/issue-draft.md`: P0/P1 のみ semantic merge blockers、P2/P3 は non-blocking、protected domain や deterministic evidence だけで P2/P3 を P1 へ上げない、と定義している。
  - `specdock-pr-review-policy-update.zip/docs/implementation-notes.md`: `P2/P3 => non_blocking_followup`、protected domain / machine evidence は metadata のまま保持し、automatic P2 promotion はしない、としている。
  - `specdock-pr-review-policy-update.zip/docs/codex-initial-prompt.md`: `pr_review_snapshot.py` の `P2 + protected_domain + machine_evidence => promoted_blocker` を変更対象として明示している。
  - `specdock-pr-review-policy-update.zip/docs/self-review.md`: terminal P2/P3-only は no branch mutation / no batch update / no push / no re-review としている。
  - `spec-dock/initiatives/.../epic-00224.../requirement.md`: E-RQ-010 と例外シナリオに、P2 protected-domain + machine evidence を blocker へ昇格する旧方針が残っている。
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`: 現行コードに `elif priority == "P2" and protected_domain and machine_evidence: disposition = "promoted_blocker"` がある。
  - `tests/unit/infra/test_init_update.py`: `test_issue_232_review_collector_promotes_protected_p2_with_machine_evidence` が旧方針を期待している。
- local context で解決できたこと:
  - 添付 bundle の実装意図は、P2/P3 の報告は許可するが自動修正・再レビュー・branch mutation の trigger にはしないこと。
  - 現行コードと一部テストは親 Epic の旧方針に沿っており、bundle 方針とは衝突していること。
  - Issue の主な変更面は Markdown asset mirror、`pr_review_snapshot.py` blocker policy、関連 tests、merge-preparer / repair-batch persistence policy であること。
- まだ人間判断が必要な理由:
  - 親 Epic の canonical 方針を更新するか、Issue-local 例外として閉じるかは、今後の PR observation workflow 全体の durable contract に関わる。

## 回答案 (必須)
- Option A:
  - 親 Epic の P2 promotion rule を `iss-00257` で明示的に廃止・上書きする。Issue docs には supersession を置き、必要なら親 Epic docs の amendment も実装 plan に含める。
- Option B:
  - 親 Epic の既存 rule は残し、今回の変更は Codex PR review instruction / merge-preparer loop の局所的な運用例外として扱う。
- Option C:
  - P2/P3 は原則 non-blocking にするが、別の明示的 human gate または future ADR で protected-domain escalation を再設計する。

## Codex の分析 (必須)
- 判断軸:
  - reviewer severity の正直さ、branch mutation / CI rerun 抑制、parent Epic との整合、future agent が読む canonical source の一貫性。
- tradeoff:
  - Option A は方針が最も一貫するが、親 Epic の記述更新を伴う可能性がある。Option B は差分が狭いが、future agent が親 Epic の旧 rule を読んで旧挙動へ戻すリスクが残る。Option C は安全弁を残せるが、今回の issue の完了条件が曖昧になりやすい。
- リスク:
  - 旧 rule を残すと、P2/P3-only terminal observation が再び repair loop や record-only push の入口になる。逆に旧 rule を完全に廃止すると、protected domain の重大 follow-up を P2 として報告したまま human が見落とす可能性があるため、final report で non-blocking findings を明示する必要がある。
- 具体シナリオ / edge case:
  - Codex が `P2: auth permission regression. Test: failing test proves access is widened.` と報告した場合、旧 rule は blocker として修正ループへ入れる。bundle 方針では `non_blocking_followup` として metadata と terminal report に残すが、branch mutation や re-review は発生させない。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。`iss-00257` は親 Epic の PR review blocker policy を更新する amendment issue として扱う。
- 理由:
  - 添付 bundle の中心目的は P2/P3 の自動 blocking 化を止めることなので、親 Epic の旧昇格 rule を残すと要件・コード・テストが矛盾する。P2/P3 を final terminal report に残すことで、見落としリスクは merge-prepared evidence / human merge decision 側へ移せる。
- 未回答時の影響:
  - 要件定義書に旧 rule の扱いを断定できず、設計書で blocker policy の不変条件を固定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - `yes`。ただし、`epic-00224` は別 worktree で作業中のため、この worktree では親 Epic docs を修正しない。
- 回答:
  - `iss-00257` では、親 `epic-00224` に残っている「P2 が protected domain かつ machine evidence ありなら validated blocker へ昇格する」旧方針を、Issue-local な上書き方針として扱う。
  - 親 Epic の `requirement.md` / `design.md` / `plan.md` / `report.md` などはこの Issue の作業では変更しない。
  - 上書き方針は `iss-00257` の canonical artifacts と実装・テストに閉じ込める。
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - 採用する。添付 bundle の P2/P3 non-blocking 方針を `iss-00257` の正本 artifact に反映し、旧 P2 promotion rule はこの Issue の範囲では廃止されたものとして扱う。ただし親 Epic docs は別 worktree の作業境界を守るため変更しない。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `iss-00257` の範囲内で、P2/P3 は protected domain / machine evidence の有無にかかわらず semantic merge blocker へ自動昇格しないことを明記する。
  - 親 Epic docs は変更対象外であることを scope boundary として明記する。
- `design.md`:
  - `pr_review_snapshot.py` の blocker policy を `P0/P1 => blocker`, `P2/P3 => non_blocking_followup`, `protected_domain` / `machine_evidence` は metadata として保持、に固定する。
  - merge-preparer / repair-batch では terminal P2/P3-only observation による branch mutation、repo batch update、push、re-review を禁止する。
- `plan.md`:
  - 親 Epic docs を編集しない確認を実装 step の guardrail に含める。
  - Markdown mirror、provider asset mirror、runtime script、tests の更新と、P2 protected-domain machine-evidence case が non-blocking になる regression test を含める。
- `ADR`:
  - 現時点では不要。Issue-local adoption と report evidence で足りる。
- reflected_to 更新方針:
  - Requirement / design / plan 作成時に、この artifact を採用 evidence として `report.md` Evidence Adoption Ledger に記録し、その後 `reflected_to` を更新する。
- adoption reflection:
  - 未反映。次の canonical authoring phase で反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
