---
種別: 要件定義書（Issue）
ID: "iss-00257"
タイトル: "Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening"
関連GitHub: ["#257"]
状態: "review-needed"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00257 Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening — Issue 要件定義

## 0. 位置づけ

この Issue は、Codex PR review observation / merge preparation workflow における「報告すべき指摘」と「自律修復・merge blocking の対象」を分離する。

親 `epic-00224` は継承する。ただし、`P2 + protected_domain + machine_evidence` を `promoted_blocker` に昇格する旧方針は、この Issue 内では採用しない。親 Epic 文書は別 worktree で作業中のため、この Issue では編集しない。

## 1. 目的

- Codex review の severity policy を、`P0/P1` は merge blocking、`P2/P3` は reportable but non-blocking として明確化する。
- `protected_domain` や deterministic / machine evidence は attention metadata として保持するが、それだけを理由に `P2/P3` を `P1` 相当へ自動昇格しない。
- P2/P3-only の terminal observation で、repo-persistent repair batch 更新、branch push、re-review request、追加の自律修復ループが発生しないことを保証する。

## 2. 背景と現状

### 2.1 現状

- 現行の review instruction は Codex を `merge-blocking reviewer` として扱い、non-blocking `P2/P3` findings を報告しないよう指示している。
- 現行 runtime は `P2` かつ `protected_domain` かつ `machine_evidence` の finding を `promoted_blocker` として扱う経路を持つ。
- 現行 tests には P2-only が non-blocking になる経路の保証がある一方で、protected-domain + machine-evidence P2 の旧昇格を期待する test も残っている。
- `github-pr-merge-preparer` と `pr-repair-batch` template は review-clean と merge-prepared の分離を一部持つが、terminal P2/P3-only の no-mutation 境界と severity-aware repair policy は十分に明文化されていない。

### 2.2 根拠

- 添付 bundle `specdock-pr-review-policy-update.zip`
- `spec-dock/active/issue/discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md`
- `spec-dock/active/issue/discussions/20260701t023648z-research-pr-review-policy-clarification-research.md`
- `spec-dock/active/issue/discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md`
- Current implementation and tests:
  - `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `spec-dock/templates/discussions/pr-repair-batch.md`
  - provider mirrors under `src/spec_dock/assets/...`
  - `tests/unit/infra/test_init_update.py`

## 3. スコープ

### 3.1 対象範囲

- Codex review instruction を severity-aware policy へ更新する。
- `github-pr-merge-preparer` skill を、P0/P1 repair と P2/P3 terminal report の分離が明確になるよう更新する。
- `pr-repair-batch` template を、repo-persistent repair batch が blocking repair / blocking triage 用であることが分かるよう更新する。
- Observation runtime の blocker policy を、P0/P1 だけが blocker になり、P2/P3 は protected-domain / machine-evidence metadata を持っていても non-blocking follow-up になるよう更新する。
- Provider-side shipped assets と local dogfooding assets の mirror parity を維持する。
- Existing tests を、新しい severity-aware policy に合わせて更新する。
- Issue Planning dogfooding 中の違和感や不具合は Issue discussion artifact と `report.md` に記録する。
- SpecDock workflow invocation が、SpecDock-defined named sub-agents / reviewers の workflow-scoped 利用許可であることを、provider / dogfooding の instruction、workflow docs、skill docs に明示する。

### 3.2 対象外

- 親 `epic-00224` / initiative 文書の更新。
- GitHub PR の merge、issue finish、branch deletion、review dismissal、conversation resolution の自動化。
- `root_cause_family` を runtime JSON output、`blocker_fingerprint`、automation stalled 判定の first-class contract にする変更。
- 複雑な runtime consent schema、新しい permission persistence、または新しい許可判定ロジックの追加。
- GitHub platform の `CHANGES_REQUESTED`、unresolved thread、branch protection を semantic code repair blocker と同一視する変更。
- 全 SpecDock workflow の一般方針変更。今回の変更は `iss-00257` の対象 surface に閉じる。

### 3.3 変更してはいけないもの

- `P0/P1` findings が merge-blocking repair target であること。
- GitHub platform / human gate が残っている場合に、それを自律的に解消済みと誤認しないこと。
- Priority-less または confidence が足りない review comment を silent pass にしないこと。
- Existing `blocker_fingerprint` contract を `root_cause_family` へ置き換えないこと。
- Canonical docs の single-writer authority は main orchestrator が保持し、sub-agent authoring outputs は evidence として扱うこと。
- Scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途ユーザー確認を必要とすること。

## 4. Actors / Triggers

| Actor | 役割 | この Issue との関係 |
|---|---|---|
| Codex PR reviewer | PR 上の指摘を severity 付きで報告する | P0/P1 と P2/P3 の意味を instruction から受け取る |
| github-pr-observation workflow | review / CI / PR 状態を観測する | blocker policy と terminal signal を出す |
| github-pr-merge-preparer workflow | blocking repair と merge handoff を進める | P2/P3-only terminal state で追加 repair を起こさない |
| SpecDock maintainer | shipped asset と dogfooding asset を管理する | provider / dogfooding mirror parity を確認する |
| Main orchestrator | SpecDock workflow を進行し canonical docs を統合する | workflow-defined named role を適切な gate で起動し、canonical 採用判断を行う |
| SpecDock-defined named sub-agent / reviewer | spec-reviewer / code-reviewer / qa-reviewer / planning roles など | active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲で workflow gate を担う |

Triggers:

- Codex review observation script execution
- Merge-preparer skill execution
- Installed asset scaffold / update verification
- Issue Planning workflow execution

## 5. 要求される振る舞い

### BH-001: P0/P1 は blocking repair target である

- Given: Codex review finding が `P0` または `P1` として判定される。
- When: observation が blocker policy を集計する。
- Then: finding は blocker として扱われ、repair loop / human attention の対象になる。

### BH-002: P2/P3 は reportable but non-blocking である

- Given: Codex review finding が `P2` または `P3` として判定される。
- When: observation が blocker policy を集計する。
- Then: finding は non-blocking follow-up として保持されるが、semantic blocker にはならない。
- And: `protected_domain` や `machine_evidence` が真でも、severity は自動昇格しない。

### BH-003: P2/P3-only terminal observation は branch mutation を起こさない

- Given: 最新 head、required CI、review decision、unresolved thread、collection failure など他の blocking gate が clean である。
- And: Codex findings が P2/P3-only である。
- When: observation / merge-preparer が terminal state を判断する。
- Then: merge-prepared として報告できる。
- And: repo-persistent repair batch update、commit、push、re-review request、自律修復 loop は行わない。

### BH-004: GitHub platform / human gates は別扱いで残る

- Given: P2/P3-only review comment とは別に `CHANGES_REQUESTED`、unresolved thread、branch protection、collection limitation が残っている。
- When: observation / merge-preparer が terminal state を判断する。
- Then: semantic blocker policy は P2/P3 を blocker にしない。
- And: platform / human gate は別の gate として報告され、自律修復で解消済みとは扱わない。

### BH-005: root_cause_family は docs / LLM judgement の運用語彙である

- Given: review instruction、merge-preparer skill、repair-batch template が finding grouping を説明する。
- When: LLM / operator が repair unit を整理する。
- Then: `root_cause_family` は判断語彙として使える。
- And: runtime JSON / fingerprint / stalled 判定の必須 field にはしない。

### BH-006: SpecDock workflow invocation は workflow-scoped named role authorization である

- Given: ユーザーが SpecDock workflow、SpecDock skill、Issue Planning、Issue Execution、Epic Planning、Initiative Planning などの利用を依頼する。
- When: workflow が SpecDock-defined named sub-agent / reviewer を必要とする。
- Then: その依頼自体を、active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲で該当 named role を利用する明示的な許可として扱う。
- And: role ごと・phase ごとの追加承認を求めず、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` pass など必要な gate を省略しない。
- And: scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途ユーザー確認を求める。

## 6. 受け入れ条件

### AC-001: Review instruction が severity-aware policy を明示する

- `P0/P1` は blocking。
- `P2/P3` は reportable but non-blocking。
- `P2/P3` は protected domain または machine evidence だけで P1 に自動昇格しない。
- Non-blocking findings を黙殺せず、terminal report / follow-up として扱う。

### AC-002: Observation runtime が P2 protected-domain + machine-evidence を non-blocking にする

- `P2` finding が `protected_domain: true` かつ `machine_evidence: true` でも `promoted_blocker` にならない。
- blocker count / blocker fingerprints は P0/P1 のみから作られる。
- metadata は follow-up / terminal report 用に保持される。

### AC-003: P0/P1 blocking behavior は維持される

- P0/P1 finding は blocker として集計される。
- P0/P1 blocker が存在する場合、recommended next action は repair / review-feedback handling に進む。

### AC-004: P2/P3-only clean terminal state は merge-prepared になれる

- 他 gate が clean で、P2/P3-only findings だけが残る場合、`blocker_policy_no_action` 相当の terminal signal に到達できる。
- この状態だけを理由に repo-persistent batch update、commit、push、re-review request を行わない。

### AC-005: Platform / human gate は誤って消さない

- `CHANGES_REQUESTED`、unresolved review thread、branch protection、collection limitation が残る場合、それらは P2/P3 policy とは別 gate として報告される。
- P2/P3 non-blocking policy は GitHub platform mergeability を保証するものではない。

### AC-006: Merge-preparer と repair-batch template が blocking repair 境界を示す

- `github-pr-merge-preparer` は P0/P1 repair と P2/P3 terminal report の違いを明示する。
- `pr-repair-batch` は repo-persistent batch を blocking repair / blocking triage 用として扱う。
- `root_cause_family` は docs / LLM judgement の grouping vocabulary として記述され、runtime contract 化は要求しない。

### AC-007: Provider / dogfooding mirror parity が維持される

- `.agents/...` と `src/spec_dock/assets/install_root/.agents/...` の対応 asset は一致する。
- `spec-dock/templates/...` と `src/spec_dock/assets/spec_dock/templates/...` の対応 template は一致する。
- Existing parity tests は更新後の contract を確認する。

### AC-008: Issue-local override と非スコープが守られる

- 親 `epic-00224` docs はこの Issue で編集しない。
- Issue docs / report は、旧 P2 promotion policy の issue-local override と、親 docs 非編集の制約を明示する。

### AC-009: Issue Planning dogfooding notes が残る

- Issue Planning workflow の利用中に観測した不具合・違和感・manual test 結果を `discussions/` artifact に残す。
- 採用した内容は `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に反映する。

### AC-010: SpecDock workflow-scoped named role authorization が明文化される

- Provider 側と dogfooding 側の orchestrator instruction / skill docs / workflow docs に、次の趣旨が明示される。
  - “A user request to use a SpecDock workflow is explicit workflow-scoped authorization to use the SpecDock-defined named sub-agents and reviewers required by that workflow.”
  - “Do not ask for additional per-role or per-phase permission before invoking SpecDock-defined named roles within the active repo/worktree, active SpecDock scope, current session, and documented role responsibility.”
  - “Ask the user only for scope expansion, destructive actions, external publishing, credentialed external mutation, private external systems, or roles outside the SpecDock workflow.”
- 日本語でも同趣旨を記載する。
  - 「ユーザーが SpecDock workflow の利用を依頼した場合、その依頼自体を、SpecDock が定義する named sub-agent / reviewer を workflow に従って利用する明示的な許可として扱う。」
  - 「active repo/worktree、active SpecDock scope、current session、documented role responsibility の範囲内では、role ごと・phase ごとの追加承認を求めない。」
  - 「scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途確認する。」
- Canonical docs の single-writer authority は main orchestrator に残し、sub-agent outputs は canonical ではなく evidence として扱う。
- 複雑な runtime consent schema や新しい許可ロジックは追加しない。

## 7. 例外・エッジケース

### EC-001: Priority-less Codex comment

- 条件: review comment から P0/P1/P2/P3 が信頼できる形で判定できない。
- 期待: silent pass ではなく fallback / manual review required として扱う。

### EC-002: P2-only だが GitHub review decision が CHANGES_REQUESTED

- 条件: semantic finding は P2-only だが GitHub review decision が blocking。
- 期待: semantic blocker policy は non-blocking、GitHub human gate は blocking として分離する。

### EC-003: P2/P3-only だが unresolved thread が platform gate

- 条件: branch protection または unresolved conversation policy が残る。
- 期待: 自律修復対象ではなく platform / human gate として報告する。

### EC-004: Multiple priorities in one body

- 条件: review body に複数 priority または incidental priority mention が含まれる。
- 期待: declared finding priority を根拠に分類し、 incidental mention だけで blocker 化しない。

### EC-005: Bundle replacement と現行 repo の差分

- 条件: 添付 bundle の replacement Markdown と現行 repo asset に差分がある。
- 期待: そのまま無批判に上書きせず、今回の Issue scope と user-approved decisions に照らして採用する。

### EC-006: SpecDock workflow 外の role または範囲拡大

- 条件: workflow が定義していない role、active repo/worktree 外、active SpecDock scope 外、current session 外、または documented role responsibility 外の作業が必要になる。
- 期待: workflow-scoped authorization の範囲外として扱い、ユーザー確認を求める。

## 8. 契約上の注意

- Public API: 影響なし。
- CLI contract: observation output の blocker policy semantics に影響あり。ただし new first-class JSON field は追加しない。
- Template contract: `pr-repair-batch.md` の運用契約に影響あり。
- Installed asset contract: `.agents` shipped assets に影響あり。
- Metadata / generated index: 影響なし。

## 9. 非機能要求

### 9.1 互換性

- Existing `blocker_fingerprint` は維持する。
- Existing P0/P1 blocker behavior は維持する。
- P2/P3 non-blocking 化により、旧 `promoted_blocker` 期待は新 policy に置き換える。

### 9.2 可観測性

- Tests で P2 protected-domain + machine-evidence が non-blocking になることを確認できること。
- Tests または inspection で provider / dogfooding mirror parity を確認できること。
- `report.md` に Issue Planning dogfooding と spec authoring gate の証跡を残すこと。

### 9.3 セキュリティ・プライバシー

- secrets、tokens、credentials、private GitHub data を docs / report に追加しない。
- Review finding body を必要以上に永続化する新 contract は追加しない。

## 10. 制約

### CON-001: Parent Epic docs non-edit constraint

- 種別: operation / scope
- 内容: 親 `epic-00224` docs はこの worktree / Issue で編集しない。
- 根拠: ユーザー指示。
- 変更可能性: fixed for this Issue.

### CON-002: Severity blocking boundary

- 種別: workflow / compatibility
- 内容: P0/P1 だけが semantic merge blocker。P2/P3 は reportable but non-blocking。
- 根拠: 添付 bundle、user-approved clarification。
- 変更可能性: fixed.

### CON-003: root_cause_family docs-only boundary

- 種別: implementation scope
- 内容: `root_cause_family` は review / repair planning の運用語彙に留め、runtime JSON / stalled logic へ組み込まない。
- 根拠: ユーザー回答 Option B。
- 変更可能性: fixed for this Issue.

### CON-004: Mirror parity

- 種別: shipped asset compatibility
- 内容: Provider-side shipped assets と dogfooding assets の対応ファイルを同期する。
- 根拠: Dogfooding repo policy and existing parity tests。
- 変更可能性: fixed.

### CON-005: Workflow-scoped named role authorization boundary

- 種別: workflow / operation
- 内容: SpecDock workflow 利用依頼は、SpecDock-defined named sub-agent / reviewer を workflow に従って使う明示許可として扱う。ただし active repo/worktree、active SpecDock scope、current session、documented role responsibility に限定する。
- 根拠: ユーザー補足指示。
- 変更可能性: fixed for this Issue.

### CON-006: Escalation remains required outside workflow-scoped authorization

- 種別: safety / operation
- 内容: Scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用は別途ユーザー確認を必要とする。
- 根拠: ユーザー補足指示。
- 変更可能性: fixed.

## 11. Trace

| Requirement item | Source |
|---|---|
| P0/P1 blocking, P2/P3 non-blocking | attached bundle, research artifact |
| P2 protected-domain + machine-evidence promotion 廃止 | `20260701t022257z-interview-parent-epic-p2-promotion-policy.md` |
| root_cause_family docs / LLM judgement scope | `20260701t023858z-interview-root-cause-family-runtime-scope.md` |
| parent Epic docs non-edit | user instruction, `CON-001` |
| Issue Planning dogfooding record | user instruction, `20260701t025116z-research-issue-planning-dogfooding-notes.md` |
| SpecDock workflow-scoped named role authorization | user supplemental instruction, `AC-010`, `CON-005`, `CON-006` |

## 12. 未解決事項

なし。次工程へ進む前に、この要件定義書の fresh `spec-reviewer` pass を取得する。
