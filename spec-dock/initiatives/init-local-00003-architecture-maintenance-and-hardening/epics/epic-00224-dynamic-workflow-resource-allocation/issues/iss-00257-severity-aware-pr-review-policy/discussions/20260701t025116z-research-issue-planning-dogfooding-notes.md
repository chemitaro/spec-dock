---
種別: research
ID: "20260701t025116z-research"
タイトル: "Issue Planning Dogfooding Notes"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["iss-00257"]
関連: []
authority: "synthesized"
derived_from:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/phase_requirement.md"
  - "spec-dock/docs/phase_design.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - ".agents/skills/spec-dock-issue-planning/SKILL.md"
reflected_to:
  - "spec-dock/active/issue/report.md"
---

# 20260701t025116z-research Issue Planning Dogfooding Notes

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- 新しい Issue Planning workflow を `iss-00257` で dogfooding し、具体化作業中の良い点、不具合、違和感、follow-up 候補を記録する。
- この artifact は product requirement ではなく、workflow 運用観察の evidence として残す。

## sources / 調査方法 (必須)
- 参照先:
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `./spec-dock/scripts/spec-dock guidance issue-planning`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_requirement.md`
  - `spec-dock/active/issue/{requirement.md,design.md,plan.md}`
  - `spec-dock/active/issue/discussions/`
- 検証手順:
  - main merge 後に `git status --short`、`active show`、`guidance issue-planning` を実行した。
  - active issue が `iss-00257` のまま維持されていることを確認した。
  - `guidance issue-planning` が `requirement-capture` / `requirement-scaffold` を返すことを確認した。
  - skill の指示に従い、Issue grade matrix と requirement phase playbook を読んだ。
- 実験条件:
  - 実装変更はまだ行っていない。
  - Requirement / design / plan はまだ具体化前。
  - この issue は Issue Planning workflow 導入後の初回実運用として扱う。

## facts / 観測できた事実 (必須)
- `guidance issue-planning` は現在状態を短く返し、`state: requirement-capture`、`next_action: requirement-capture-required`、`reason_code: requirement-scaffold`、`authority: authorized_profile=strict` を確認できた。
- Guidance は generated runbook projection path を出すが、skill 側の指示によりそれらを agent handoff authority として読まない判断ができた。
- Active symlink path (`spec-dock/active/issue/...`) から canonical issue docs と discussions を読める。
- main merge 後も、以前作成した issue-local discussion artifacts は active issue 配下に残っていた。
- `git status --short` は clean から開始できたため、Issue Planning dogfooding の観察と canonical authoring を分けやすい。
- `assurance classify --stage requirement` は requirement 具体化後に成功し、`authorized_profile: standard`、`complexity_tier: normal`、`lite_candidate: false` を返した。
- `assurance compose --artifact all` は成功し、`design.md`、`plan.md`、`report.md` を profile-aware template で合成した。
- 合成後の `design.md` / `plan.md` は front matter `状態: "approved"` になったが、fresh `spec-reviewer` pass はまだ未実行だった。`draft` は workflow preflight が scaffold と判定するため、main orchestrator は具体化時に `review-needed` へ変更し、report に reviewer not_run として記録する判断をした。
- `guidance issue-planning` は design/plan/report の具体化後、`reason_code: report-spec-authoring-gate-invalid` で停止した。Details は `Spec Authoring Gate must record non-blocking pass evidence for requirement/design/plan.` であり、fresh spec-reviewer pass 未実行を execution readiness blocker として検出している。
- 要件、設計、計画を各 phase ごとに spec-reviewer review した後、`report.md` の `Spec Authoring Gate`、`Delegated Draft Evidence`、`Reviewer Gate Status`、`Grade Specialist Evidence Gate` は runtime が期待する表の列順と契約値に合わせる必要があった。
- 最終的に `guidance issue-planning` は `state: ready`、`reason_code: assurance-valid` を返した。
- 初回 authoring 時、main orchestrator が multi-agent tool の一般制約を優先して、SpecDock workflow が必要とする `spec-reviewer` の起動を追加人間許可待ちにしてしまった。ユーザー補足指示により、SpecDock workflow invocation 自体を workflow-defined named role 利用の明示許可として扱う方針を、この Issue scope に追加した。

## inference / 推測 (必須)
- 事実から推測したこと:
  - runtime guidance は「現在どの phase にいるか」の入口として十分に有用。
  - 詳細な grade / phase obligation は docs に分かれており、skill と docs の責務分担は概ね機能している。
  - 一方、初回利用時は「いつ assurance classify / compose を実行するか」「reviewer gate をどの実コマンド/agentで実行するか」は guidance だけでは完結しないため、phase docs と workflow docs を併読する必要がある。
- 推測の根拠:
  - Guidance は `Edit requirement.md` だけを next action として返す。
  - `design.md` / `plan.md` は `artifact_state: awaiting-assurance-compose` で、requirement 具体化後の classify / compose が必要と明記されている。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Fresh `spec-reviewer` gate の実行経路と、fresh pass evidence を `report.md` に残す手順。
  - Strict profile で specialist を使う場合の実際の delegated draft workflow。
- 確認できない理由:
  - このホストの multi-agent tool は明示的な sub-agent / delegation 依頼がある場合のみ spawn 可能であり、今回の authoring では spec-reviewer を未実行のまま not_run として記録したため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - none at this point.
- pressure-test question として切り出すべき候補:
  - none at this point.
- 質問せずに解決できた候補:
  - `root_cause_family` の runtime scope はユーザー回答により Option B として解決済み。
  - 親 Epic docs を編集しない制約もユーザー回答により解決済み。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - 初回 guidance の `authorized_profile=strict` と requirement 具体化後 classify の `authorized_profile: standard`。
  - `guidance` と canonical workflow docs。
- 既存 docs / code / tests / discussions での使われ方:
  - Guidance は current next action projection であり canonical authority ではない。
  - `assurance classify` は具体化済み requirement から profile を判定し、compose はその profile に応じた artifact template を生成する。
- 判断が必要な理由:
  - Guidance と classify の表示が変わること自体は不具合とは断定しないが、初回利用者には「scaffold 時点の暫定 profile」と「requirement 具体化後の classified profile」の違いが少し分かりづらい。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Requirement 具体化前に design / plan を本文編集しようとすると、placeholder が「この状態のまま設計本文を書き始めないでください」と明示している。
  - Guidance projection files を agent handoff authority と誤読すると、skill の first-read instruction に反する。
- その edge case が requirement / design / plan に与える影響:
  - Requirement を先に substantive にし、必要な gate を通してから design / plan へ進む必要がある。
  - Planning workflow の使い勝手に関する違和感は product requirement に混ぜず、この dogfooding note に分離する。

## implications / 判断への含意 (必須)
- Superseded: 初回 guidance の `authorized_profile=strict` を前提にした implication は、requirement 具体化後の `assurance classify --stage requirement` が `authorized_profile: standard` を返したため採用しない。
- Current adopted implication: `iss-00257` authoring は `authorized_profile: standard` として扱い、requirement / design / plan 各 phase で fresh spec-reviewer gate と report evidence を残す必要がある。
- Specialist を使わず main orchestrator の manual authoring で進める場合、Standard profile の manual authoring fallback evidence と fresh reviewer pass を `report.md` に残す。
- Issue Planning workflow 自体の改善候補が出た場合は、この issue の本筋と分けて discussion / follow-up 候補として残す。

## リスク/制約 (任意)
- 現時点の不具合:
  - none observed. `classify` と `compose` は期待どおり実行できた。
- 現時点の違和感:
  - 初回 guidance の `authorized_profile=strict` が、requirement 具体化後の `authorized_profile: standard` へ変わる流れは合理的だが、stdout だけでは暫定/確定の違いが読み取りづらい。
  - 合成直後の `design.md` / `plan.md` が `状態: "approved"` になる一方で fresh reviewer gate は未実行なので、agent がそのまま承認済みと誤読する余地がある。逆に `draft` は scaffold 扱いになるため、未レビューだが具体化済みの状態名が必要だった。
  - planning docs を具体化しただけでも guidance は execution readiness gate まで評価するため、spec-reviewer 未実行が blocker として出る。これは安全側の挙動だが、「planning authoring 完了」と「execution ready」の違いを利用者に明示する UX があると分かりやすい。
  - `report.md` evidence gate は human-readable な自然文よりも、表の列順と契約値 (`passed`, `no`, `promote`, `ready` など) に強く依存する。初回利用時は gate の期待 schema が docs か guidance から直接分かると運用しやすい。
  - SpecDock workflow の利用依頼が named sub-agent / reviewer 起動の許可を含むことが、skill / workflow docs / orchestrator instruction に明示されていないと、required reviewer gate を不必要に人間許可待ちしてしまう。
  - `guidance issue-planning` は next action と stop condition を簡潔に返すが、reviewer / specialist 実行コマンドまでは返さないため、phase docs 併読が必須。

## 反映先 (任意)
- reflected_to:
  - `spec-dock/active/issue/report.md`

## 参考（References） (任意)
- `./spec-dock/scripts/spec-dock guidance issue-planning`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_requirement.md`
