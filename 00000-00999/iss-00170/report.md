---
種別: 実装報告書（Issue）
ID: "iss-00170"
タイトル: "Harden Pr Monitor Stable Observation"
関連GitHub: ["#170"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00170 Harden Pr Monitor Stable Observation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | GPT-5.5 Pro 議事録は prompt-only 更新ではなく fixed read-only wrapper と stable snapshot 契約まで推奨していた。 | A: pr-monitor instructions だけを強化する; B: stable snapshot と wrapper output contract まで issue scope に含める; C: GraphQL/thread state は follow-up に分離する | 本 issue は B として、head-SHA-bound stable observation、all/Codex review signal separation、thread state limitation handling、fixed read-only wrapper を requirement scope に含める。 | 既存 `iss-00105` では review thread state は follow-up candidate だったが、今回のユーザー依頼はその改善案の実施であり、`github-pr-merge-preparer` も latest head SHA と unresolved-thread limitation を merge-prepared predicate に含めている。 | applied | `discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`; `requirement.md` | design で wrapper 分割、GraphQL query、status mapping を具体化する |
| D-002 | superseded | implementation | system-architect draft / orchestrator | 既存 Codex review wrapper を拡張するか、新規 stable observation wrapper を追加するか。 | A: `fetch_codex_pr_review_comments.sh` を拡張する; B: 既存 wrapper を維持し `fetch_pr_stable_observation.sh` を追加する; C: agent prompt のみで安定観測を指示する | 当時は B を採用したが、後続の user decision により旧 wrapper は `github-pr-observation` review collector へ統合して削除する方針へ置換された。 | 互換 wrapper を残すと full PR observation と Codex-only path が二重化し、正規入口が曖昧になるため。 | superseded_by_D-004 | `discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md`; `discussions/20260607t110532z-research-pr-observation-skill-retirement-and-naming.md`; `design.md` | use D-004 for implementation planning |
| D-003 | superseded | implementation | user decision / deep-consultant research | 旧設計は `pr-monitor` agent が polling loop を持つ前提だったが、ユーザーは loop を deterministic script に移す案を全面採用した。 | A: agent-driven polling を維持する; B: wait wrapper が polling loop を持ち、agent は final JSON を要約する; C: PR workflow skills も agent に統合する | 当時は B を採用したが、後続の user decision により `pr-monitor` sub-agent は完全廃止し、`github-pr-observation` skill/script を正規入口にする方針へ置換された。 | script が final JSON / artifacts を authority として返すなら、`pr-monitor` は script executor になり責務が薄い。 | superseded_by_D-004 | `discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md`; `discussions/20260607t083017z-research-v2-progress-delta-for-script-driven-polling.md`; `discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md`; `discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`; `design.md` | use D-004 for implementation planning |
| D-004 | resolved | implementation | user decision / deep-consultant research / clarification interview | `pr-monitor` sub-agent と旧 Codex-only wrapper を残すか、完全廃止して `github-pr-observation` skill/script に一本化するか。 | A: `pr-monitor` を summarizer として残す; B: deprecated shim を残す; C: `pr-monitor` と旧 wrapper を削除し `github-pr-observation` に一本化する | C を採用する。互換 shim は残さず、`github-pr-observation` の `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh` を正規入口にする。`summary.md` も生成せず、human-facing summary は final JSON fields として caller が受け取る。 | 単純性、決定性、testability、final JSON authority、重複 asset 回収の観点で C が最も一貫する。 | promoted_to_adr_and_design | `discussions/20260607t110532z-research-pr-observation-skill-retirement-and-naming.md`; `discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md`; `discussions/20260607t132357z-interview-summary-artifact-contract.md`; `discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`; `design.md` | requirement and plan must be regenerated / updated from this revised design before implementation |
| D-005 | resolved | implementation | user decision / deep-consultant progress analysis | long foreground wait の progress をどう表示し、CI / review status をどこまで断定するか。 | A: progress default off; B: event-diff log を出す; C: stderr に current-state summary を default 表示し、stdout final JSON を唯一の primary result にする | C を採用する。progress は poll ごと最大1行の stderr key/value とし、CI は `unknown|none|failed|running|pending|passed`、review は `unknown|unresolved|changes_requested|requested|commented|approved|none` に限定する。`mixed`、`inconclusive`、`review=blocked`、P1/P2 text interpretation は採用しない。 | agent / human の liveness には default progress が必要だが、途中ログは流れ去るため event log ではなく自己完結した current-state summary がよい。final decision authority は stdout JSON に固定する必要がある。 | promoted_to_adr_and_design | `discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`; `requirement.md`; `design.md` | plan must be regenerated from the revised stdout/stderr and status taxonomy contract |
| D-006 | resolved | implementation | user decision / consultant analysis | stdout final JSON に review 本文と CI failure detail を含めるか。全件コメント取得では古い review がノイズになる。 | A: final JSON は counts / hashes のみ; B: 全 PR comment body を毎回含める; C: `@codex review` trigger window 後の body を body mode / cap 付きで含め、CI failure detail も含める | C を採用する。`--trigger-comment-id` / `--trigger-created-at` を first-class input にし、default `--body-mode trigger-window-truncated` で trigger 後の body を final JSON に含める。CI 失敗時は workflow / run / job / failed step detail を出す。 | caller が安全境界を迂回して direct GitHub API を叩く必要を減らしつつ、古いコメント混入、stdout 肥大化、secret 混入リスクを trigger window と cap で抑えられる。 | promoted_to_requirement_and_design | `discussions/20260608t000000z-research-trigger-window-review-body-and-ci-detail.md`; `requirement.md`; `design.md` | plan must include trigger-window/body-mode/failure-detail tests |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | user-provided GPT-5.5 Pro discussion captured as research | `requirement.md` | 議事録の主張を raw transcript ではなく facts / inference / edge cases に分けて保存し、requirement には WHAT / WHY / scope / AC として採用した。 | `discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`; `requirement.md` | fresh `spec-reviewer` で requirement gate を確認する |
| EAL-002 | adopted | delegated system-architect design draft | `design.md` | system-architect draft は required frontmatter / source paths / intended targets / non-authoritative posture を満たし、requirement AC-001〜AC-010 に対して wrapper split、SHA-bound observation、status taxonomy、thread limitation、provider/mirror parity を具体化していたため正式設計へ採用した。 | `discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md`; `design.md`; `git diff --check` -> pass | fresh `spec-reviewer` で design gate を確認する |
| EAL-003 | superseded | delegated implementation-planner plan draft | historical `plan.md` only | implementation-planner draft was adopted against the pre-ADR passed design and did pass review at that time, but `20260607t085456z-adr` replaced the design premise with script-driven polling. This evidence is retained as historical authoring evidence and is no longer implementation authority. | `discussions/20260607t072057z-disc-implementation-plan-pr-monitor-stable-observation.md`; historical `plan.md`; `20260607t085456z-adr`; revised `requirement.md`; revised `design.md` | regenerate plan from the revised design before implementation execution |
| EAL-004 | adopted | user-approved research v1/v2 and PR workflow role-boundary analysis promoted to ADR | `requirement.md`; `design.md` | ユーザーが script-driven polling / progress delta / PR workflow skill boundary の案を全面採用し、ADR への格上げと requirement/design 反映を指示した。 | `discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md`; `discussions/20260607t083017z-research-v2-progress-delta-for-script-driven-polling.md`; `discussions/20260607t085217z-research-pr-monitor-and-pr-workflow-role-boundary.md`; `discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`; `requirement.md`; `design.md` | run fresh `spec-reviewer` for revised requirement/design; regenerate plan afterwards |
| EAL-005 | adopted | user clarification interview on summary artifact contract | `design.md` | ユーザーは `summary.md` file generation より、script 実行結果を JSON として caller agent が受け取る方がよいと判断した。設計は `summary.md` artifact を生成せず、final JSON / `result.json` の `summary`, `recommended_next_action`, `limitations`, `artifacts` fields を human-facing handoff source とする。 | `discussions/20260607t132357z-interview-summary-artifact-contract.md`; `design.md` | reflect same decision in requirement and regenerated plan |
| EAL-006 | adopted | user-approved progress/status refinement and deep-consultant analysis | `requirement.md`; `design.md`; ADR | 長時間 wait 中の default progress、stdout/stderr 分離、技術的に取得可能な CI / review status taxonomy、`skipped` / `neutral` の passed 扱い、path-filter required Pending の pending 扱いを正本へ反映した。 | `discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`; `requirement.md`; `design.md` | regenerate plan and run fresh spec-reviewer before implementation |
| EAL-007 | adopted | consultant analysis on trigger-window review body and CI failure detail | `requirement.md`; `design.md`; `report.md` | GitHub official API docs と既存 fixed REST GET wrapper 境界を踏まえ、trigger-window body payload、body mode / cap、fixed GraphQL query boundary、CI failure detail schema を採用した。 | `discussions/20260608t000000z-research-trigger-window-review-body-and-ci-detail.md`; `requirement.md`; `design.md` | regenerate plan and include body payload / CI failure detail tests |
| EAL-008 | adopted | fresh spec-reviewer re-review for regenerated plan | `plan.md`; `report.md` | Initial plan review found EC-003〜EC-006 traceability drift and stale report wording. The plan/report were corrected and fresh re-review returned findingsなし / `review_status=pass`. | `discussions/20260607t154933z-disc-spec-review-regenerated-plan-pass.md`; `plan.md`; `report.md` | implementation execution may proceed from regenerated plan |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ... | ... | なし / 低 / 中 / 高（none / low / medium / high） | 合格 / 不合格 / blocked（pass / fail / blocked） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `spec-dock active show`; `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`; `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`; `.agents/skills/github-pr-merge-preparer/SKILL.md`; `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`; `iss-00105` requirement / review-thread discussion; `discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`; `discussions/20260608t000000z-research-trigger-window-review-body-and-ci-detail.md`; `20260607t085456z-adr` | Blocking question: none. Review request comment requester is out of scope. Defaults are fixed in requirement: `timeout=1800s`, `poll_interval=30s`, `quiet=90s`, `same_fingerprint_count=2`. | revised requirement adopts full `pr-monitor` retirement, old skill deletion, new `github-pr-observation` skill/scripts, stdout final JSON authority, stderr default progress, trigger-window body payload, CI failure details, fixed REST/GraphQL read-only boundary, and technically feasible CI/review status taxonomy. Fresh reviewer found no issues. | passed (`/private/tmp/iss-00170-requirement-spec-review-1.md`, `review_status=pass`, findings=[]） | no | requirement phase is promoted to design |
| design | `requirement.md`; `report.md`; `discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`; delegated system-architect draft `discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md`; provider and mirror `pr-monitor` assets; existing Codex review wrapper; `github-pr-merge-preparer` skill; `github-pr-creator` skill; `tests/unit/infra/test_init_update.py`; `discussions/20260608t000000z-research-trigger-window-review-body-and-ci-detail.md`; `20260607t085456z-adr` | Blocking question: none. No user-confirmation-needed unknowns remain in design. | revised design traces AC-001〜AC-014 / EC-001〜EC-006 and defines asset retirement, new skill/script paths, stdout/stderr contract, trigger-window body modes/caps, CI failure detail schema, fixed REST GET / fixed GraphQL boundary, progress taxonomy, zero-check grace, thread-state unknown handling, and PR workflow skill boundary. Fresh reviewer found no issues. | passed (`/private/tmp/iss-00170-design-spec-review-1.md`, `review_status=pass`, findings=[]） | no | design phase is promoted to implementation planning |
| plan (pre-ADR historical) | `requirement.md`; pre-ADR passed `design.md`; delegated implementation-planner draft `discussions/20260607t072057z-disc-implementation-plan-pr-monitor-stable-observation.md`; system-architect draft; provider/mirror assets; existing wrapper skill/script; `tests/unit/infra/test_init_update.py` | Superseded by `20260607t085456z-adr` and revised requirement/design. | Historical only: the pre-ADR plan was adopted and reviewed before the script-driven polling decision. It is retained as evidence but is not implementation authority. | superseded | no; superseded by regenerated plan row | use regenerated plan row as current implementation planning authority |
| requirement/design revision after ADR | `20260607t085456z-adr`; v1/v2 script-driven polling research; PR workflow role-boundary research; trigger-window body / CI detail research; current provider `pr-monitor` / `github-pr-merge-preparer` / `github-pr-creator` assets | Blocking question: none. Review request comment posting remains out of scope and may become a follow-up. | replaced requirement/design to make wait wrapper the loop owner, default stderr progress required, stdout final JSON primary, trigger-window review body included by body mode, CI failure detail included, `pr-monitor` fully retired, old Codex-only review skill retired, and PR workflow skills unchanged except for direct `github-pr-observation` invocation. Fresh requirement and design reviews passed. | passed for requirement/design | no | promoted to regenerated implementation planning |
| plan (regenerated after ADR) | current `requirement.md`; current `design.md`; `20260607t085456z-adr`; trigger-window body / CI detail research; fresh requirement review `/private/tmp/iss-00170-requirement-spec-review-1.md`; fresh design review `/private/tmp/iss-00170-design-spec-review-1.md`; `discussions/20260607t154933z-disc-spec-review-regenerated-plan-pass.md` | Blocking question: none. Initial plan review found EC-003〜EC-006 traceability drift and stale report wording; both were corrected. | plan was recreated from template-level structure and current design, then corrected so EC traceability and report state align with requirement/design. Fresh plan re-review returned findingsなし / `review_status=pass`. | passed | no | implementation execution may proceed from regenerated plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| spec-dock-system-architect | iss-00170 | `discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md` | `requirement.md`; `report.md`; research discussion; parent epic docs; provider/mirror `pr-monitor` assets; Codex review wrapper; `github-pr-merge-preparer`; `tests/unit/infra/test_init_update.py` | `design.md`; `plan.md`; `report.md` | adopted by orchestrator after inspection | `design.md`; `report.md` | passed (`git diff --check`) | Wrapper split、SHA-bound stable observation、status taxonomy、thread-state limitation、provider/mirror parity、test strategy を正式設計へ統合 | none | none | fresh `spec-reviewer` re-review passed | design promoted to implementation planning |
| spec-dock-implementation-planner | iss-00170 | `discussions/20260607t072057z-disc-implementation-plan-pr-monitor-stable-observation.md` | pre-ADR `requirement.md`; pre-ADR passed `design.md`; `report.md`; research discussion; system-architect draft; parent epic docs; provider/mirror `pr-monitor` assets; Codex review wrapper; `github-pr-merge-preparer`; `tests/unit/infra/test_init_update.py` | historical `plan.md`; `report.md` | superseded after ADR | historical `plan.md`; `report.md` | passed (`git diff --check`) at time of adoption | Pre-ADR dependency order and closure index are retained as historical evidence but no longer current implementation authority | entire pre-ADR plan is superseded by `20260607t085456z-adr` and revised design | none for current planning after regenerated plan row was added | fresh pre-ADR `spec-reviewer` had passed; post-ADR requirement/design reviewer passed with plan-stale note | current implementation authority is regenerated `plan.md` |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- S01 では provider-side source of truth と dogfooding mirror から `pr-monitor` agent assets と `github-codex-pr-review-comments` skill を退役し、`github-pr-observation` skill scaffold を追加した。
- 初回 code-reviewer は command rules の prefix pattern 破損と obsolete skill の空 directory 残りを検出した。修正後の fresh code-reviewer は findings なし / `review_status=pass`。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-08 S01）

#### 対象
- Step: S01 Asset retirement and observation skill scaffold
- AC/EC: AC-011
- 計画上の出典（Planned source）:
  - `plan.md` section: `### S01 Asset retirement and observation skill scaffold`
  - closure ids: CL-AC-011

#### 実施内容
- dev-coder が provider-side `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` を追加し、dogfooding mirror `.agents/skills/github-pr-observation/` と byte parity を取った。
- provider/dogfooding から旧 `pr-monitor` agent assets と旧 `github-codex-pr-review-comments` skill files を削除した。
- managed skill inventory、CLI harness、command rules、obsolete cleanup manifest、focused tests を更新した。
- 初回 code-reviewer fail 後、command rules を wrapper ごとの `prefix_rule` に分離し、obsolete exact file unlink 後に managed obsolete prefix 内の空 parent directory だけを prune する処理と regression test を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_native_shim_assets_satisfy_static_delegation_only_contract -q
# 1 passed

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_update_prunes_empty_obsolete_pr_review_skill_dirs_only tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_placeholder_fails_without_gh_api tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_review_wrapper_rejects_unsafe_inputs_before_gh_api -q
# 4 passed

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets -q
# 1 passed

git diff --check
# pass

codex exec --ephemeral --sandbox read-only -C . "Reply only: ok"
# rules load errorなしで pass

```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required / parity + stale cleanup | 初回 code-reviewer が broken command rule と empty obsolete skill directory 残りを検出 | reviewer review + focused command | pass | fail finding を red evidence として採用 |
| S01 | 緑フェーズ（Green） | new skill scaffold / old assets retired / cleanup fixed | focused pytest 1+4+1 tests pass、rules load smoke pass | `uv run pytest ...`; `codex exec --ephemeral ...` | pass | CL-AC-011 の実装証跡 |
| S01 | リファクタリング（Refactor） | guardrail satisfied | `git diff --check` pass、fresh code-reviewer pass | command + reviewer | pass | S02-S06 の実装は先取りしていない |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | command rules の `pattern` が wrapper 2本を同一 prefix sequence として扱い、allow rule が壊れる | code-reviewer | wrapper ごとの `prefix_rule` に分離し、static contract test を再実行 | CL-AC-011 | no | `test_bundled_native_shim_assets_satisfy_static_delegation_only_contract` -> pass |
| S01 | obsolete exact file cleanup 後に旧 skill の空 directory が残る | code-reviewer | managed obsolete prefix 内の空 parent dirs pruning を追加し、custom content preservation test を追加 | CL-AC-011 | no | `test_issue_75_update_prunes_empty_obsolete_pr_review_skill_dirs_only` -> pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | CL-AC-011 | new skill added、old agent/skill removed、shim なし、stale cleanup あり | provider/dogfooding scaffold parity、old assets deleted、obsolete cleanup test、fresh code-reviewer pass | pass | S06 の guidance 文言置換は計画どおり残 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CL-AC-011 | S01 | yes | red-required + parity | code-reviewer fail findings | focused pytest + fresh code-reviewer | pass | compatibility shim は追加していない |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CL-AC-011 | S01 | `test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present`; `test_issue_75_update_prunes_empty_obsolete_pr_review_skill_dirs_only`; parity test; code-reviewer pass | pass | provider source and dogfooding mirror aligned |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | CL-AC-011 | S01 focused tests | CL-AC-011 | 計画内の retirement / scaffold / cleanup を補強しただけで closure semantics は変更なし | no | completed |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/3b01/spec-dock` | iss-00170 | current session | dev-coder, code-reviewer | same repo, active issue, S01 bounded implementation/review; no commit/publish by worker | issue complete / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped scaffold / installer cleanup / tests | dev-coder | S01 asset retirement and scaffold only | `plan.md`; provider install_root; dogfooding mirror | listed provider/mirror assets, CLI inventory, command rules, focused tests | S02-S06 behavior, compatibility shim, broad docs guidance | focused pytest, parity, `git diff --check`, code-reviewer | scope expansion / reviewer fail | worker summary / changed files / verification / risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | New `github-pr-observation` scaffold added; old `pr-monitor` / `github-codex-pr-review-comments` retired; broken command rules and empty obsolete directory cleanup fixed after review. | `.agents/`; `.codex/rules/spec-dock-commands.rules`; `.github/agents/`; `src/spec_dock/assets/install_root/`; `src/spec_dock/cli.py`; `tests/cli_runtime/harness.py`; `tests/unit/infra/test_init_update.py` | focused pytest 1+4+1 pass; `git diff --check` pass; rules load smoke pass | pass | S02 input validation/read-only API boundary; S06 guidance migration | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | `codex exec` が S01 中の broken command rules 読み込みで起動不能になり、一度だけ orchestrator が rules pattern を最小自己回復した | implied by execution continuity; final diff re-owned by dev-coder and reviewed | `.codex/rules/spec-dock-commands.rules`; `src/spec_dock/assets/install_root/.codex/rules/spec-dock-commands.rules` | broken pattern の一時最小修正 | `git diff` で確認し、dev-coder 修正に統合 | focused pytest / code-reviewer pass | code-reviewer fresh pass | resolved; no waiver |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | initial fail fixed; re-review findingsなし |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 source/test/report diff | current HEAD after S01 amend | `feat(pr-observation)!: PR観測スキルの足場を追加` | `git status --short` clean immediately after commit | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` - new observation skill scaffold.
- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/` - retired.
- `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml` - retired.
- `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md` - retired.
- `.agents/`, `.codex/`, `.github/` mirror files - dogfooding parity updates.
- `src/spec_dock/cli.py` - managed skill inventory and empty obsolete parent directory pruning.
- `tests/cli_runtime/harness.py`; `tests/unit/infra/test_init_update.py` - inventory, rules, stale cleanup, scaffold tests.

#### コミット
- pending

#### メモ
- `github-pr-creator` / `github-pr-merge-preparer` / orchestrator guidance に残る `pr-monitor` 文言は S06 の計画対象。

---

### セッションログ（2026-06-07 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
