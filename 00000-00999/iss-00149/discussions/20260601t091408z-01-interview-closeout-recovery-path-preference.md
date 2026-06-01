---
種別: interview
ID: "20260601t091408z-01-interview"
タイトル: "Closeout recovery path preference"
状態: "archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-01"
親: ["iss-00149"]
関連: ["#149"]
scope: "issue"
scope_id: "iss-00149"
created_at: "2026-06-01T09:14:08Z"
created_by: "iwasawayuuta"
status: "superseded"
authority: "synthesized"
adoption_status: "rejected"
derived_from:
  - "spec-dock/active/issue/discussions/20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md"
reflected_to:
  - "discussions/20260601t092641z-disc-deep-consultant-lifecycle-transition-decision.md"
---

# 20260601t091408z-01-interview Closeout recovery path preference

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`:
    - Official CLI path の成功条件と non-scope を左右する。
  - `design.md`:
    - `issue finish` の内部自動昇格にするか、別 command / explicit operation にするかで責務境界が変わる。
  - `plan.md`:
    - red test、migration / recovery test、docs update step の切り方が変わる。
  - `ADR`:
    - 既存 authority model を変更する場合は ADR candidate になり得る。
- chat 上の軽微な一問では足りない理由:
  - 回答は lifecycle authority boundary と user-facing recovery command に影響し、複数 artifact へ反映する必要がある。
  - ただし、この artifact 作成後に、ユーザーから「人間に option 選択を求めるべきではなく、deep consultant analysis によって技術的に判断するべき」という方針が示された。
  - そのため、この artifact は unanswered user interview ではなく、後続の consultant-backed synthesis に supersede された記録として扱う。

## 質問の目的
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - `issue start` 由来の synthetic active state を、どの official path で `issue finish` 可能な lifecycle-approved state に変換するべきか。
- 回答が後続判断へ与える影響:
  - requirement の acceptance wording、design の責務境界、plan のテスト義務、docs guidance を決める。

## 質問
- 質問:
  - `issue finish` が synthetic active state で止まる問題は、どの official recovery / transition path として解くのが望ましいですか？
- 回答してほしいこと:
  - Option A / B / C のどれを preferred path にするか。
  - preferred でない option を明示的に禁止または対象外にしたいか。

## source-grounded context
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `workflow_issue.md` は primary start を `issue start`、primary finish を `issue finish` としている。
  - `issue_finish()` は close / active clear の前に `issue_finish` authority gate を通す。
  - `issue start` / `active set` は `promotion_decision=runtime_active_selection` を持つ active entry を作る。
  - authority gate は lifecycle grants に対して `runtime_active_selection` を fail-closed する。
  - test helper は `promotion_decision=main_orchestrator_promotion` へ手動変更すると finish success path が成立することを示している。
- local context で解決できたこと:
  - root cause は GitHub state ではなく local active authority state の transition gap である。
  - 手動 `active.json` 編集は動くが standard path ではない。
- まだ人間判断が必要な理由:
  - security / workflow ergonomics の tradeoff があり、code だけでは product preference を決められない。

## 回答案
- Option A: `issue finish` が内部で lifecycle-grade approval へ昇格する
  - `issue finish` が close 前に必要条件を検査し、成立する場合だけ active issue entry の finish 用 approval を内部生成 / 更新する。
  - operator は `issue start` -> work -> `issue finish` の primary path だけを覚えればよい。
- Option B: 明示 command を追加する
  - 例: `spec-dock issue approve-finish` / `active promote` / `issue ready` などを追加し、`issue finish` は lifecycle-grade approval が存在する場合だけ進む。
  - authority transition は明示的になるが、通常 workflow の step が増える。
- Option C: `issue start` / active set の grants 表示を狭め、エラー guidance に recovery command だけを追加する
  - synthetic active selection は lifecycle grants を持たない状態として表現し、`issue finish` 失敗時の guidance を改善する。
  - ただし、公式 transition path を別途用意しない限り、primary lifecycle は完結しない。

## Codex の分析
- 判断軸:
  - primary workflow の短さ。
  - synthetic approval と lifecycle approval の区別の明確さ。
  - fail-closed authority model の維持。
  - existing docs/tests への影響範囲。
- tradeoff:
  - Option A は UX が最も自然だが、finish command が approval mutation を兼ねるため、事前条件を厳密に定義する必要がある。
  - Option B は authority model が最も明示的だが、operator が追加 command を覚える必要がある。
  - Option C は表現を正すだけなので、この bug report の expected behavior を単独では満たしにくい。
- リスク:
  - Option A で条件が緩いと、review / delivery evidence がない issue を finish できる regression になる。
  - Option B で追加 command が重いと、従来の `issue start` / `issue finish` primary path と docs がまた乖離する。
- 具体シナリオ / edge case:
  - GitHub issue already closed でも local active clear が必要。
  - PR merge 済みでも local report / reviewer evidence が不足している場合に approval してよいかは design で条件化が必要。

## Codex の推奨案
- 推奨:
  - Option A を preferred path にし、`issue finish` が fail-closed の事前条件を満たした時だけ finish 用 lifecycle approval を内部生成する。
- 理由:
  - `workflow_issue.md` が primary path としている `issue start` -> `issue finish` を回復できる。
  - 手動 `active.json` 編集を standard workaround から排除できる。
  - synthetic approval と lifecycle approval の区別は維持しつつ、transition を command 内で明示的に検査できる。
- supersede 前の影響:
  - 当初は preferred transition path 未確定として扱っていたが、後続の deep-consultant synthesis により technical decision として解決した。

## ユーザー回答
- 回答:
  - ユーザーは Option A / B / C の選択ではなく、deep consultant による根本原因分析と技術判断を求めた。
- 回答日時:
  - 2026-06-01

## 追加確認の要否
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断
- adoption_status:
  - rejected
- 採用 / 棄却 / deferred の理由:
  - 人間への preference question としては棄却。内容は `20260601t092641z-disc-deep-consultant-lifecycle-transition-decision.md` で consultant-backed technical decision として再整理した。

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - 未確定事項ではなく、consultant-backed decision として Option A 採用を反映する。
- `design.md`:
  - finish-scoped lifecycle transition の責務境界を設計方針として固定する。
- `plan.md`:
  - Red / Green / negative test obligations と docs update step を固定する。
- `ADR`:
  - authority model の durable decision が必要なら design phase で ADR candidate 化する。
- reflected_to 更新方針:
  - `disc`、`requirement.md`、`report.md` に反映済み。
