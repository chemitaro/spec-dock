---
種別: interview
ID: "20260701t023858z-interview"
タイトル: "Root Cause Family Runtime Scope Clarification"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["iss-00257"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00257"
created_at: "2026-07-01T02:38:58Z"
created_by: "iwasawayuuta"
status: "unanswered"
authority: "proposed"
adoption_status: "unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked"
derived_from:
  - "specdock-pr-review-policy-update.zip/docs/codex-initial-prompt.md"
  - "specdock-pr-review-policy-update.zip/repo-files/.agents/skills/github-pr-observation/scripts/codex-review-instructions.md"
  - "specdock-pr-review-policy-update.zip/repo-files/.agents/skills/github-pr-merge-preparer/SKILL.md"
  - "specdock-pr-review-policy-update.zip/repo-files/spec-dock/templates/discussions/pr-repair-batch.md"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - "spec-dock/active/issue/discussions/20260701t023648z-research-pr-review-policy-clarification-research.md"
reflected_to: []
---

# 20260701t023858z-interview Root Cause Family Runtime Scope Clarification

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
    - `root_cause_family` を observable runtime contract として要求するか、merge-preparer / repair-batch の triage vocabulary として要求するかで、観測可能な成果と受け入れ条件が変わる。
  - `design.md`:
    - `pr_review_snapshot.py` が review body から `root_cause_family` を parse して `blocker_policy.findings[]` へ出力するか、現行の `blocker_fingerprint` を維持して docs / batch 側で grouping するかで設計が変わる。
  - `plan.md`:
    - parser / JSON output / automation stalled tests を追加するか、Markdown / template / existing blocker fingerprint tests に留めるかで実装 step と検証コマンドが変わる。
  - `ADR`:
    - 現時点では ADR 必須とは判断していない。ただし runtime JSON contract を拡張するなら、将来の互換性として ADR candidate になり得る。
- chat 上の軽微な一問では足りない理由:
  - 添付 bundle は `root_cause_family` による group-by を強く求めているが、現行 runtime は blocker fingerprint ベースで、`root_cause_family` の構造化 field を持たない。ここをどこまで今回の Issue に含めるかは scope と実装量に影響する。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `root_cause_family` を runtime output / automation stalled の code-level contract に含めるか、今回の Issue では review instruction / merge-preparer / repair-batch の triage surface に留めるか。
- 回答が後続判断へ与える影響:
  - 含める場合は `pr_review_snapshot.py` parser、blocker policy payload、fingerprint / stalled tests の設計が必要。含めない場合は docs/template/skill と P2/P3 blocker policy の修正に集中し、runtime は現行 fingerprint contract を維持する。

## 質問 (必須)
- pressure-test question:
  - 今回の目的は P2/P3 による repair loop を止めることだが、同時に review repair loop の単位を `root_cause_family` へ code-level に移行しないと不十分か。
- 質問:
  - `root_cause_family` は今回の `iss-00257` の implementation scope に含め、Codex review body の `root_cause_family:` を `pr_review_snapshot.py` で抽出して JSON / blocker fingerprint / automation stalled 判定へ反映するべきですか？
- 回答してほしいこと:
  - `yes`: runtime output / tests まで含め、`root_cause_family` を first-class contract として扱う。
  - `no`: 今回は review instruction、merge-preparer skill、repair-batch template の triage vocabulary として扱い、runtime は既存 `blocker_fingerprint` contract を維持する。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - 添付 `codex-initial-prompt.md` は「Review findings are processed by observation batch and `root_cause_family`, not by individual comment」とし、「same-root-cause-family loop stop for repeated P0/P1 blockers」のテストを期待している。
  - 添付 `codex-review-instructions.md` は Finding format に `root_cause_family: stable kebab-case or dotted key` を要求している。
  - 添付 `github-pr-merge-preparer/SKILL.md` と `pr-repair-batch.md` は batch triage / repair units を `root_cause_family` 単位にする。
  - 現行 `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` は `blocker_fingerprint(item.kind, priority, raw_body)` を出すが、`root_cause_family` field はない。
  - 現行 `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py` は `blocker_fingerprints(payload)` と `mark_automation_stalled(...)` で repeated blocker を判定する。
- local context で解決できたこと:
  - P2/P3 non-blocking 化自体は `root_cause_family` の code-level 導入がなくても実装できる。
  - Bundle の Markdown replacement は `root_cause_family` を reviewer / merge-preparer / repair-batch の運用語彙として既に含んでいる。
  - 現行 code-level loop stop は blocker fingerprint であり、root-cause-family semantic grouping とは同一ではない。
- まだ人間判断が必要な理由:
  - `root_cause_family` を parser / JSON contract にすると scope が広がり、free-form review body parsing と互換性を新たに持つことになる。逆に docs-only にすると bundle の「same-root-cause-family」期待を完全には runtime で満たさない。

## 回答案 (必須)
- Option A:
  - `root_cause_family` を runtime first-class field にする。Codex review body の `root_cause_family:` 行を抽出し、`blocker_policy.findings[]` に含め、P0/P1 blocker fingerprints / stalled判定に使う。
- Option B:
  - 今回は runtime first-class field にせず、review instruction、merge-preparer skill、repair-batch template の triage vocabulary として扱う。Runtime は P0/P1 blocker fingerprint と P2/P3 non-blocking policy の修正に集中する。
- Option C:
  - `root_cause_family` を finding metadata として optional に抽出するが、automation stalled / blocker fingerprint には使わない。

## Codex の分析 (必須)
- 判断軸:
  - 今回の primary objective、実装リスク、free-form parsing の堅牢性、将来の automation stalled 精度、test coverage。
- tradeoff:
  - Option A は bundle の言葉に最も忠実だが scope が広く、review body format への依存が増える。Option B は今回の P2/P3 repair-loop problem を最小差分で解けるが、same-root-cause-family は運用/ドキュメント上の contract に留まる。Option C は中間だが、field があるのに loop 判定に使わないため期待が曖昧になりやすい。
- リスク:
  - Option A の risk は、Codex review body が format を外したときの fallback や互換性。Option B の risk は、同じ root cause が表現違いで再投稿されたとき、fingerprint では同一 family と見なせない可能性。Option C の risk は contract ambiguity。
- 具体シナリオ / edge case:
  - 同じ P1 root cause が本文修正や別行番号で再投稿されると、body hash 由来の fingerprint は変わる可能性がある。`root_cause_family` を使えば同一 family と見なしやすいが、reviewer が正しく field を書く必要がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - この Issue の primary objective は P2/P3 の自動 blocking 化と terminal P2/P3-only branch mutation を止めること。`root_cause_family` の code-level contract は有用だが、free-form parsing と automation stalled semantics を広げる別リスクがあるため、まずは docs / skill / template の batch triage vocabulary として採用し、runtime は既存 fingerprint contract のまま P0/P1-only blocker policy へ絞るのが小さく正しい。
- 未回答時の影響:
  - Requirement / design / plan で `root_cause_family` を implementation acceptance criteria に入れるべきか判断できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ...
- 回答:
  - ...
- 回答日時:
  - ...

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes | no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - ...

## 採用判断 (回答後に必須)
- adoption_status:
  - unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked
- adoption target:
  - `requirement.md` | `design.md` | `plan.md` | `ADR` | `report.md` Evidence Adoption Ledger | none
- 採用 / 棄却 / deferred の理由:
  - ...
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes | no

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- reflected_to 更新方針:
  - ...
- adoption reflection:
  - ...

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
