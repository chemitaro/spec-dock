---
種別: interview
ID: "20260529t012153z-interview"
タイトル: "Issue planning skill authority boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00138"]
関連: []
scope: "issue"
scope_id: "iss-00138"
created_at: "2026-05-29T01:21:53Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260529t012153z-01-research"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260529t012153z-interview Issue planning skill authority boundary

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Issue planning skill の責務、非スコープ、AC、EC が変わる。
  - `design.md`:
    - 新規 skill の authority boundary、provider/dogfooding parity、hub routing 設計が変わる。
  - `plan.md`:
    - 実装 step と test obligation の範囲が変わる。
  - `ADR`:
    - 現時点では不要見込み。direct authoring authority を採用する場合は authority model との長期整合判断が ADR candidate になり得る。
- chat 上の軽微な一問では足りない理由:
  - 回答が skill 追加の scope、execution skill の縮小範囲、hub の sequencing、provider asset tests に波及するため、回答前に artifact として未回答状態を残す必要がある。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `spec-dock-issue-planning` の authority boundary を、main orchestrator 向け workflow reminder とするか、canonical docs を直接編集する delegated authoring skill とするかを決める。
- 回答が後続判断へ与える影響:
  - requirement の必須範囲、禁止範囲、acceptance criteria、design の変更対象、plan の step 分割が確定する。

## 質問 (必須)
- 質問:
  - 今回新設したい `spec-dock-issue-planning` は、まずは Initiative / Epic planning skill と同じく「main orchestrator が Issue の `requirement.md` / `design.md` / `plan.md` を作成・改善するための concise workflow reminder」として設計しますか。それとも、`system-architect` / `implementation-planner` のように、skill 自体を delegated author として canonical docs または discussion draft を直接作る role に近づけたいですか。
- 回答してほしいこと:
  - Option A / B / C のどれに近いか。
  - 追加で「今回の issue ではここまでやる / やらない」という境界があれば明示してほしい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_wrappers.py`
- local context で解決できたこと:
  - Issue planning skill は現状存在しない。
  - Initiative / Epic planning skill は canonical docs を直接編集する delegated role ではなく、workflow docs への concise reminder である。
  - `workflow_spec_authoring.md` が Issue の requirement / design / plan authoring の正本である。
  - `spec-dock-issue-execution` は implementation / verification / report / PR delivery / finish に寄った skill であり、gap 発見時は clarification / authoring へ戻す。
  - 新規 skill を shipped asset に足す場合、provider-side install_root、dogfooding `.agents/skills`、hub skill、docs README、init/update tests が影響候補になる。
- まだ人間判断が必要だった理由:
  - skill の authority boundary は product workflow UX の判断であり、local source だけでは「軽量分離」か「delegated authoring の拡張」かを確定できなかった。

## 回答案 (必須)
- Option A:
  - 軽量分離。`spec-dock-issue-planning` は Initiative / Epic planning と同じ抽象度の concise workflow reminder とし、canonical docs は main orchestrator が workflow_spec_authoring / clarification に従って作成する。
- Option B:
  - delegated draft author 寄り。`spec-dock-issue-planning` は issue-local `discussions/` に draft-requirement / draft-design / draft-plan などの proposal を作る role とし、canonical docs は main orchestrator が採用する。
- Option C:
  - canonical direct authoring 寄り。`spec-dock-issue-planning` が `requirement.md` / `design.md` / `plan.md` の direct authoring を担う前提で、authority / promotion / permission / report gate まで含めて設計する。

## Codex の分析 (必須)
- 判断軸:
  - 既存 skill の抽象度と整合するか。
  - 今回の issue を小さく閉じられるか。
  - Epic の authority-aware delegated authoring model と衝突しないか。
  - planning + execution 同時指定時に reviewer gate を飛ばす誤解を避けられるか。
- tradeoff:
  - Option A は最小で既存 Initiative / Epic planning skill と揃うが、sub-agent が draft file を作る能力は増えない。
  - Option B は deep discussion / draft evidence と相性がよいが、direct-write delegated output の consent / diff guard / adoption ledger を requirement に含める必要が出る。
  - Option C は強力だが、Epic が扱っている authority / promotion / permission model と重なり、この issue の scope を大きく広げる。
- リスク:
  - Option B/C を採ると、`iss-00138` が skill split ではなく delegated authoring architecture の追加実装 issue になり、目的が広がる。
  - Option A でも hub/docs の文言が曖昧だと、planning + execution 同時指定で implementation gate を飛ばしてよいと誤読される。
- 具体シナリオ / edge case:
  - Active issue docs が template の状態で `$spec-dock-issue-execution` だけが指定された場合、execution は start せず planning / clarification へ戻す必要がある。
  - `$spec-dock-issue-planning` と `$spec-dock-issue-execution` が同時指定された場合、planning artifact が spec-reviewer pass / handoff readiness を満たしてから execution に進む必要がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - 今回のメモにある「Initiative / Epic と抽象度を揃える」に最も合い、既存 `workflow_spec_authoring.md` と `workflow_clarification.md` を正本にした小さい変更で閉じられるため。
  - direct draft authoring はすでに `system-architect` / `implementation-planner` と Epic authority model が扱っているため、Issue planning skill 自体にその権限を持たせると責務が重なるため。
  - planning + execution 同時指定は「gate を通ったら handoff」として表現すれば、半自動の余地を残しつつ安全境界を守れるため。

## ユーザー回答 (回答後に必須)
- 回答:
  - 既存 workflow をそのまま保つ。独自に大きく変えない。
  - 設計書 draft は `system-architect` に依頼し、それをもとに main orchestrator が正式な `design.md` を作成する。
  - 実装計画書 draft は `implementation-planner` に依頼し、それをもとに main orchestrator が正式な `plan.md` を作成する。
  - 要件 / 設計 / 計画側と実装側は分けるが、既存 rule を大きく変えるのではなく、既存 rule を保ったまま分割する。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、`spec-dock-issue-planning` は新しい delegated authoring authority ではなく、既存 `workflow_spec_authoring.md` / `workflow_clarification.md` / delegated draft rules への Issue planning entrypoint として分離する方針が確定した。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Issue planning skill の新設は必須とする。
  - Issue execution skill は実装開始以降の execution / verification / report / delivery に集中させる。
  - Existing `system-architect` / `implementation-planner` delegated draft flow は維持し、Issue planning skill 自体に direct canonical authoring authority を持たせない。
- `design.md`:
  - provider-side skill asset、hub routing、docs README / workflow references、tests、dogfooding parity を設計対象にする。
- `plan.md`:
  - skill asset addition、routing/docs update、tests/dogfooding parity verification を behavior slice として分ける。
- `ADR`:
  - 新しい durable architecture decision は不要。既存 workflow を保つ corrective split として扱う。
- reflected_to 更新方針:
  - `requirement.md` に正式反映する。
  - `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に採用証跡を残す。
