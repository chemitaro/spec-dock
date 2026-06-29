---
種別: 実装報告書（Issue）
ID: "iss-00244"
タイトル: "Simplify Issue Execution Guidance Into Plan Centric Preflight Validation"
関連GitHub: ["#244"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00244 Simplify Issue Execution Guidance Into Plan Centric Preflight Validation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | user / orchestrator | `guidance issue-execution` を step-by-step dynamic selector として維持するか、plan-centric preflight validator へ縮退するか。 | dynamic selector 維持; plan-centric preflight; hybrid fallback | plan-centric preflight を採用し、実行順序・レビュー・品質ゲートは `plan.md` に集約する。 | ユーザーは複雑な動的状態管理より、実装計画書一本に作業契約を集約する方向を支持した。 | applied | `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`; `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md`; `requirement.md`; `design.md`; `plan.md` | なし |
| D-002 | resolved | compatibility | user | 既存の `workflow next` / dynamic guidance field 互換を残すか。 | compatibility shim; hard cutover | hard cutover を採用し、不要な interface / field は削除対象にする。 | ユーザーが「hard cutoverを採用します。不要なインターフェースやフィールドは削除」と明示した。 | applied | `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`; `requirement.md` AC-001/AC-002; `design.md` S01/S03 | なし |
| D-003 | resolved | test-strategy | orchestrator | Issue Planning の実運用テストで、substantive draft requirement が `reason_code=requirement-scaffold` と表示され、`assurance classify` の `standard` と guidance の `strict` も不一致だった。 | この issue の外へ延期; この issue の planning/validation 要件へ織り込む | 本 issue の AC-009/AC-010 と S05 に取り込み、guidance semantics、authorized profile source consistency、provider/dogfood parity を検証対象にする。 | `assurance classify` は requirement を valid/standard と判定する一方、guidance は scaffold/strict を表示したため、agent-facing guidance の状態表現と profile source を検証する必要がある。 | applied | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md`; `plan.md` S05/tc-009/tc-010 | なし |
| D-004 | resolved | test-strategy | ChatGPT Pro advisory review / orchestrator | GPT-5.5 Pro review が、`may_execute_approved_plan`、旧 structured step selector 不要テスト、invalid assurance fail-closed、projection refresh negative test の明示を推奨した。 | 既存 plan のまま; すべて採用; source-grounded な不足分だけ採用 | source-grounded な不足分だけ採用し、`tc-011` - `tc-014` と output / preflight contract へ反映した。 | 外部 review には active issue 本体が確認できないという誤認があったため、助言をそのまま権威化せず、ローカル文書と照合できた指摘だけ採用する。 | applied | `discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md`; `requirement.md`; `design.md`; `plan.md` | なし |
| D-005 | resolved | operation | dogfooding manual test | `uvx --from . spec-dock update .` 後も dogfooding runtime が古い `guidance issue-execution` 判定を返した。 | update root cause をこの issue で深掘り; dogfooding parity のため provider 正本から同期して本 issue を進める; issue を停止する | 本 issue では provider 正本と dogfooding runtime の parity を確保して検証を続行し、update root cause の深掘りは scope expansion として扱う。 | 主目的は guidance hard cutover であり、provider 正本の実装と dogfooding command の実挙動確認が closure に必要。update behavior の根本原因は別関心事。 | applied | `discussions/20260627t154455z-research-dogfooding-runtime-update-drift-finding.md`; dogfooding `guidance issue-execution` / `guidance issue-planning`; `spec-dock validate` | 必要なら update path 調査を follow-up |
| D-006 | resolved | compatibility | dev-coder / orchestrator | `.assurance.json` がなく旧 `assurance.json` だけがある場合の public status / reason をどう扱うか。 | `missing / missing_assurance_contract`; `invalid / legacy_assurance_contract_path` | `invalid / legacy_assurance_contract_path` を採用する。 | 旧 visible path は「存在しない契約」ではなく、current authority ではない stale artifact である。missing strict-legacy と区別し、show / verify を fail-closed にする必要がある。 | applied | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`; `tests/unit/infra/test_assurance_store.py`; `tests/cli_runtime/test_assurance.py`; focused pytest `53 passed` | なし |
| D-007 | resolved | implementation | dev-coder / orchestrator | Script-local Codex review instruction body の metadata labels と instruction size limit をどう固定するか。 | max size を変更する; 既存 32768 bytes を維持する | 既存上限 32768 bytes を維持し、body metadata は `source`, `instruction_sha256`, `instruction_status`, `reviewed_head_sha` とする。 | ADR / plan は script-local path/hash/status/head metadata を要求しており、既存 size limit の変更理由はない。GitHub base/head policy fetch を廃止しつつ、最小差分で deterministic body を保てる。 | applied | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`; `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`; `tests/unit/infra/test_init_update.py` | なし |
| D-008 | resolved | operation | user / ChatGPT Pro advisory / orchestrator | PR #245 で `wait_pr_observation.sh` が `review_completion_unknown` で終了した約 14 分後に Codex submitted PR review と 5 件の P1 finding が投稿され、time / quiet / same fingerprint / selected comments 0 を completion proof とする設計欠陥が露出した。 | active `review_completion_unknown` 維持; timeout だけ延長; explicit artifact model へ切替; full state-machine rewrite | Option C hybrid を採用し、active `review_completion_unknown` terminal path を廃止する。Review completion は current trigger boundary と expected head SHA に bind された Codex-authored submitted PR review または strict no-findings comment に限定し、completion artifact がない場合は retryable `timeout` / `wait_or_resume` とする。 | GPT-5.5 Pro advisory と追加分析は、時間経過・静穏・fingerprint 安定は非同期 review worker の完了証拠ではないと結論づけた。full rewrite は scope 過大であり、現 defect は wait layer の terminalization と hydration/head binding を絞って直せる。 | promoted_to_adr / promoted_to_design / promoted_to_plan | `../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md`; `discussions/20260628t143306z-research-pr-observation-review-completion-signals.md`; `discussions/20260628t150332z-disc-pr-observation-completion-wait-repair-draft.md`; `requirement.md` AC-020..AC-023; `design.md` 方針 F; `plan.md` S300..S399 | なし |
| D-009 | resolved | operation | PR #245 Codex review / orchestrator | Codex submitted pull request review body に P1 が含まれる場合、inline review comment / review thread が 0 件でも blocker として扱うか。 | inline comments/threads のみ scan; selected pull request review body も scan; review body は human-only gate | selected pull request review body も blocker policy input に含め、body P0 / P1 は `human_gate` / `address_review_feedback` として扱う。 | submitted review は completion artifact であり、その body を blocker input から外すと completion は認識するが finding は捨てる矛盾が起きる。Epic の目的は P2/P3 noise 削減であり、P0/P1 blocker の見逃しではない。 | promoted_to_adr / promoted_to_design / promoted_to_plan | `../../discussions/20260628t185812z-adr-pr-review-body-blocker-ingestion.md`; `requirement.md` AC-024; `design.md` wait output contract; `plan.md` tc-036; `tests/unit/infra/test_init_update.py` | なし |
| D-010 | resolved | implementation | dogfooding guidance manual test / orchestrator | `guidance issue-execution` が active `design.md` を `design-not-substantive` と誤判定した。実際には設計本文は substantive だが、本文中の過去事例 `状態: "draft"`、`templates/`、`non-placeholder` が scaffold marker に誤爆していた。 | 文書から該当語を消す; scaffold marker を全文検索のまま維持; frontmatter / 明示的 scaffold 文言だけを判定する | status / scaffold marker は frontmatter または明示的 managed scaffold 文言に限定し、本文の調査メモや否定表現では実行可能 artifact を block しない。 | preflight は実行可否 safety gate だが、設計本文が過去の失敗や template asset を説明できないと dogfooding と原因分析を阻害する。 | promoted_to_design / promoted_to_plan / applied | `design.md` 方針 B; `plan.md` tc-037; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`; `spec-dock/scripts/spec_dock_runtime/application/workflow.py`; `tests/cli_runtime/test_workflow.py`; `./spec-dock/scripts/spec-dock guidance issue-execution` | なし |
| D-011 | resolved | implementation | PR #245 Codex review / orchestrator | PR #245 latest head `9df7a4b0` の Codex review が P1 を5件返した。4件は protected gate の有効な欠陥、1件は current ADR と逆行する旧 trusted base policy 指摘だった。 | 全件修正; 誤指摘を含めて全件コード変更; 有効4件を修正し、trusted-base 指摘は current ADR に基づき誤指摘として記録 | 有効4件（non-file `.assurance.json`、TODO/TBD body marker、strict-legacy symlink planning artifact、compose partial write）を修正し、trusted-base 指摘は script-local ADR へ変更済みのため採用しない。 | User decision / iss-00244 ADR は script-local instruction source を明示しており、base policy 復活は本 issue の目的に反する。一方、他4件は public validation / execution-ready / generated-file write safety に関わるため修正対象。 | applied / rejected | PR observation result `/private/tmp/spec-dock-pr245-observation-9df7a4b0/result.json/result.json`; `design.md`; `plan.md` tc-038..tc-041; focused tests | なし |
| D-012 | resolved | operation | PR #245 dogfooding observation / orchestrator | latest head `a1ee5ac3` の PR observation で、current no-findings completion artifact が投稿されたが、旧 carryover unresolved review threads が17件残っていたため最初は `human_gate` になった。 | carryover を無視して pass; old threads をすべて対応済みとして resolve して同一 trigger boundary で resume; 新規 trigger を投稿し直す | old carryover threads は GitHub 上で解決済みとして resolve し、同一 trigger boundary の resume で `codex_no_findings_issue_comment` / `passed` / `merge_prepared` を確認する。 | no-findings comment は単体では merge proof ではなく、carryover blocker zero まで統合して初めて merge-prepared proof になる。旧未解決threadを無視すると blocker-centric closure に反するが、対応済み/誤指摘の thread は GitHub 上で resolve すれば current gate は通過できる。 | promoted_to_adr / applied | `/private/tmp/spec-dock-pr245-observation-a1ee5ac3/result.json`; `/private/tmp/spec-dock-pr245-observation-a1ee5ac3-resume-after-resolve/result.json`; `20260628t154553z-adr-pr-observation-explicit-review-completion.md`; `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md` | docs-only commit 後に latest head で最終 PR observation を再実行する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | requirement / design / plan | Plan-centric guidance への縮退、report-control-plane の廃止、Step Obligation Pattern の plan authoring 移管を本 issue の主対象として採用した。 | `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md` | なし |
| EAL-002 | adopted | discussion | requirement / design / plan | dynamic selector を削り、preflight validator と plan lint に責務を分ける構成を採用した。 | `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md` | なし |
| EAL-003 | adopted | user decision | requirement / design / plan | hard cutover と不要 field 削除を互換性方針として採用した。 | `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md` | なし |
| EAL-004 | adopted | command / research | design / plan / report | Issue Planning guidance の manual test 結果を採用し、guidance semantics drift と profile source inconsistency を検証対象へ加えた。 | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md`; `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json` | 実装時に S05 で再検証 |
| EAL-005 | partially_adopted | external advisory review | requirement / design / plan / report | GPT-5.5 Pro review のうち、ローカル文書と照合できた不足分を採用した。active issue 本体未確認という指摘は Oracle 側の可視性制約として参考止まりにした。 | `discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md`; Oracle session `iss-00244-plan-centric-guidance` | なし |
| EAL-006 | adopted | command / research | report | Dogfooding runtime update drift finding を採用し、provider/dogfood parity と実コマンド出力の両方を最終検証対象にした。 | `discussions/20260627t154455z-research-dogfooding-runtime-update-drift-finding.md`; `./spec-dock/scripts/spec-dock guidance issue-execution`; `./spec-dock/scripts/spec-dock validate` | PR 前に provider/dogfood diff と guidance output を再確認 |
| EAL-007 | adopted | delegated worker / command | report / implementation | S200/S210 実装結果と legacy visible path status semantics を採用した。 | `dev-coder` result; focused pytest `51 passed`; hidden file inspection; `assurance verify`; `guidance issue-execution`; `validate` | final review gates and commit |
| EAL-008 | adopted | delegated worker / command | report / implementation | S100/S110 review trigger repair と QA P2 test tightening を採用した。 | `dev-coder` result; `test_init_update.py` 515 passed; focused assurance lane 53 passed; grep/file-list inspections | final review gates and commit |
| EAL-009 | adopted | research / discussion / advisory analysis / ADR | requirement / design / plan / report | PR observation completion wait repair の Option C hybrid を採用し、AC-020..AC-023、方針 F、S300..S399、tc-028..tc-035 へ反映したうえで、`20260628t154553z-adr` へ昇格した。 | `../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md`; `discussions/20260628t143306z-research-pr-observation-review-completion-signals.md`; `discussions/20260628t150332z-disc-pr-observation-completion-wait-repair-draft.md`; `requirement.md`; `design.md`; `plan.md`; `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock assurance verify`; fresh spec-reviewer pass | implementation ready |
| EAL-010 | adopted | PR #245 Codex review finding / ADR | requirement / design / plan / report / implementation | Pull request review body blocker ingestion を採用し、AC-024、tc-036、ADR `20260628t185812z-adr`、snapshot blocker regression へ反映した。 | `../../discussions/20260628t185812z-adr-pr-review-body-blocker-ingestion.md`; `requirement.md`; `design.md`; `plan.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`; `tests/unit/infra/test_init_update.py` | focused tests and PR re-observation |
| EAL-011 | adopted | dogfooding command finding | design / plan / report / implementation | active issue の `guidance issue-execution` が `design-not-substantive` に誤停止したため、frontmatter-only scaffold marker 判定を採用した。 | `./spec-dock/scripts/spec-dock guidance issue-execution`; `design.md`; `plan.md` tc-037; `tests/cli_runtime/test_workflow.py` | full verification and commit |
| EAL-012 | adopted | PR #245 Codex review | design / plan / report / implementation | P1 5件のうち4件を有効な merge-blocking risk として採用し、1件を current ADR と矛盾する誤指摘として却下した。 | PR observation `trigger=4827376238`; selected comments `3488547379`, `3488547380`, `3488547383`, `3488547384`, `3488547386`; `design.md`; `plan.md`; focused tests | fix, re-run gates, push, re-observe PR |
| EAL-013 | adopted | PR #245 live observation | report / ADR | `a1ee5ac3` の live observation で、旧 quiet/time-based early-stop が再発せず、Codex no-findings issue comment を explicit completion artifact として待機できることを採用した。旧 carryover threads は blocker-centric gate として扱い、resolve 後の resume で `passed / merge_prepared` を確認した。 | `/private/tmp/spec-dock-pr245-observation-a1ee5ac3/result.json`; `/private/tmp/spec-dock-pr245-observation-a1ee5ac3-resume-after-resolve/result.json`; `../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md` | docs-only commit後に latest head final observation |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `guidance issue-execution` を plan-centric preflight validator に単純化する要件・設計・計画が作成済み。 | Issue Planning guidance の manual test 結果を `discussions/` と plan の検証対象へ反映済み。 | low | pass: fresh spec-reviewer |
| OAL-002 | PR observation wait の早期終了を防ぐ AC-020..AC-024 / S300..S399 を追加し、レビュー完了判定を explicit artifact model へ寄せ、review body blocker ingestion を追加した。 | 既存 S01-S299 は残し、PR trigger repair / hidden assurance rename と分離した追加 repair scope として扱う。 | medium | pass: fresh spec-reviewer; AC-024 re-review pending |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active epic/issue docs, runtime code, discussions, user hard-cutover decision, PR #245 wait failure analysis | Q-001 resolved; Q-002/Q-003 design-routed; PR observation completion wait scope resolved by Option C hybrid | adopted | pass: fresh spec-reviewer | no | implementation-ready |
| design | `application/workflow.py`, `context_packets.py`, `context_routing.py`, `runbook.py`, `presentation/workflow.py`, PR observation wait/snapshot scripts, shipped skills, docs/scaffold assets, tests | no blocking open question; deletion depth captured as S03; completion wait repair captured as 方針 F | adopted | pass: fresh spec-reviewer | no | implementation-ready |
| plan | requirement/design AC and module dependency analysis, PR observation wait repair dependency analysis | no blocking open question; AC-020..AC-024 mapped to S300..S399 and tc-028..tc-036 | adopted | pass: fresh spec-reviewer; AC-024 re-review pending | no | implementation-ready |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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
- `guidance issue-execution` を plan-centric preflight validator へ hard cutover し、旧 dynamic fields（`selected_step` / `step_assurance` / `context_packets` など）を default output / projection / skill handoff から除去した。
- 実行順序・worker/reviewer/verification obligation は `plan.md` 正本へ集約し、runtime guidance は `state` / `next_action` / `reason_code` / `authority` / `may_execute_approved_plan` / `contract_source` / `evidence_ledger` を返す軽量な実行可否確認に縮退した。
- provider source と dogfooding workspace の実コマンドで `guidance issue-execution` / `guidance issue-planning` / `validate` を確認し、dogfooding runtime update drift は discussion artifact として記録した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-27 14:05 - 14:45）

#### 対象
- Step: planning authoring
- AC/EC: AC-001..AC-010, EC-001..EC-006
- 計画上の出典（Planned source）:
  - `plan.md` sections: Issue Execution Plan / Step Contract
  - closure ids: tc-001..tc-010

#### 実施内容
- `guidance issue-planning` を実行し、初期状態が requirement capture であることを確認した。
- `requirement.md` を具体化した後、`assurance classify` と `assurance compose` を実行した。
- `design.md` と `plan.md` を具体化し、plan-centric preflight validation への hard cutover 方針を反映した。
- Issue Planning guidance の manual test として、substantive draft requirement が `reason_code=requirement-scaffold` に残る挙動を確認し、discussion artifact に記録した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# result: state=requirement-capture, reason_code=requirement-scaffold

./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json
# result: ok=true, status=valid, authorized_profile=standard

./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json
# result: ok=true, status=valid, authorized_profile=standard, assurance.json written

./spec-dock/scripts/spec-dock assurance compose --artifact all --format json
# result: ok=true; design.md, plan.md, report.md changed

./spec-dock/scripts/spec-dock assurance verify --format json
# result: ok=true, status=valid, authorized_profile=standard

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=153

./spec-dock/scripts/spec-dock guidance issue-planning
# result: state=requirement-capture, reason_code=requirement-scaffold, authority=authorized_profile=strict

npx -y @steipete/oracle --engine browser --model gpt-5.5-pro --browser-thinking-time extended ...
# result: GPT-5.5 Pro advisory review completed; accepted additions recorded in discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| planning | 代替証跡（authoring） | manual-required | guidance / assurance command behavior observed | command / docs inspection | pass-with-finding | finding recorded in `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| planning | Draft frontmatter が残る substantive requirement を guidance が `requirement-scaffold` と表現し、`assurance verify` の `standard` と guidance の `strict` が不一致になる。 | manual test | recorded and added to plan verification | tc-009 / tc-010 | yes | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| planning | tc-001..tc-010 | requirement/design/plan authoring complete before implementation | documents updated; assurance compose run | provisional | final spec-review pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-009 | S05 | yes | manual-required | Issue Planning guidance manual test | `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json` | pass-with-finding | finding incorporated into plan |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001..tc-010 | planning | requirement/design/plan inspection | provisional | implementation and final gates pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | tc-009 / tc-010 | guidance-semantics-manual-test | tc-009 / tc-010 | Issue Planning guidance manual test exposed provider/dogfood semantics drift. | yes | yes |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00244 | current session | spec-reviewer if needed | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue planning complete / session end / scope change / host policy conflict / user revocation | none | proceed to final spec-review |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planning | approved-local-execution | docs-only authoring with current orchestrator context | N/A | requirement/design/plan/report/discussions | active issue docs | docs update only | implementation code changes | guidance and assurance commands | reviewer failure / unresolved blocking gap | updated artifacts / verification / risks | pass-with-finding |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| planning | N/A | no delegated draft used in this phase | requirement/design/plan/report/discussions | guidance and assurance commands | provisional | final spec-review pending | accepted for review |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| planning | direct issue-planning authoring requested by user | user request; risk accepted: no unresolved blocking risk | active issue docs and discussions | docs authoring | git diff can revert docs-only edits | guidance / assurance commands -> pass-with-finding | spec-reviewer pending | proceed to review |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | final spec authoring review | spec-reviewer | fresh pending | provisional | no | proceed to request review | requirement/design/plan/report authored |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| planning | not committed | docs-only planning artifacts | pending | pending | implementation not started | N/A | N/A | N/A |

#### 変更したファイル
- `requirement.md` - plan-centric preflight validator の要件を具体化。
- `design.md` - dynamic context routing removal と plan lint / skill / template 更新方針を具体化。
- `plan.md` - Step-level Obligation Pattern を含む実装計画を具体化。
- `report.md` - 計画作成中の採用判断と manual test findings を記録。
- `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` - Issue Planning guidance manual test findings を記録。

#### コミット
- 未実施。

#### メモ
- 実装開始前に fresh spec-reviewer の pass が必要。

### セッションログ（2026-06-28 実装・検証）

#### 対象
- Step: S01 / S02 / S03 / S04 / S05 / S90
- AC/EC: AC-001..AC-010, EC-001..EC-006
- closure ids: tc-001..tc-014

#### 実施内容
- `Runbook` domain model、workflow application、Markdown/JSON renderer、projection store から旧 dynamic execution handoff fields を削除した。
- ready issue の runtime guidance は `execute-approved-plan` と `may_execute_approved_plan=true` を返し、実行契約 source と evidence ledger を明示する形へ変更した。
- invalid/stale assurance は `unavailable` authority として fail-closed し、`strict` fallback を current authority として表示しないようにした。
- shipped issue planning / execution skills を更新し、runtime guidance から current step / worker / reviewer / verification / context packet を導出しないようにした。
- assurance compose の plan fragment を `Step Obligation Contract` へ更新し、worker/reviewer obligations は `plan.md` に書く契約へ寄せた。
- `uvx --from . spec-dock update .` 後に dogfooding runtime drift を検出したため、provider 正本と dogfooding runtime の parity を確保してから manual test を再実行した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/cli_runtime/test_assurance_compose.py
# result: 28 passed

uv run pytest tests/cli_runtime
# result: 671 passed, 76 skipped

uv run pytest tests/unit
# result: 832 passed

uv run ruff check .
# result: All checks passed

uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py
# result: Success: no issues found in 6 source files

./spec-dock/scripts/spec-dock guidance issue-execution
# result: state=ready, next_action=execute-approved-plan, reason_code=assurance-valid, may_execute_approved_plan=true, authorized_profile=standard

./spec-dock/scripts/spec-dock guidance issue-planning
# result: state=ready, next_action=planning-ready, may_execute_approved_plan=false, authorized_profile=standard

rg -n "selected step|selected_step|Step Assurance|Context Packets|context_packets|workflow-plan-unselectable|Context Packet" \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  spec-dock/scripts/spec_dock_runtime \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  .agents/skills/spec-dock-issue-execution/SKILL.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md \
  spec-dock/active/current-runbook.md \
  spec-dock/active/current-runbook.json
# result: no matches

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=153
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | Green | ready guidance output contract | `execute-approved-plan`, `may_execute_approved_plan=true`, `contract_source`, `evidence_ledger` observed | pytest / manual command | pass | tc-001, tc-002, tc-011 |
| S02 | Green | non-executable / invalid assurance blocks execution | invalid/stale assurance fixtures use unavailable authority and `may_execute_approved_plan=false` | pytest | pass | tc-004, tc-013 |
| S03 | Green | old dynamic fields no longer control execution | old dynamic fields absent in CLI/runtime/projection/skills; report rows no longer select steps | pytest / rg | pass | tc-002, tc-003, tc-012, tc-014 |
| S04 | Green | skill/template handoff points to plan-centric obligation | provider/generated skill assertions and template assertions pass | pytest / inspection | pass | tc-005, tc-006, tc-007 |
| S05 | Green | regression and dogfooding parity | CLI runtime/unit suites pass; dogfooding guidance returns ready/standard | pytest / command | pass-with-finding | update drift recorded separately |
| S90 | Green | docs impact and projection refresh | `current-runbook.*` refreshed without dynamic sections; guidance commands align with active issue | command / rg | pass | tc-010, tc-014 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S05 | `spec-dock update .` 成功後も dogfooding runtime が古い判定を返す場合がある。 | dogfooding manual test | provider 正本から dogfooding runtime parity を確保し、finding を discussion artifact に記録。 | tc-010 / tc-014 | no | `discussions/20260627t154455z-research-dogfooding-runtime-update-drift-finding.md` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-011 | Runbook output contract hard cutover | focused tests and manual guidance output | pass | ready guidance uses approved plan contract |
| S02 | tc-004, tc-006, tc-013 | plan readiness preflight validation | workflow tests and invalid/stale assurance fixtures | pass | fail-closed unavailable authority |
| S03 | tc-002, tc-003, tc-008, tc-012 | dynamic context routing removal | replaced CLI tests, removed obsolete context routing / packet modules, and no old dynamic field grep matches | pass | old context packet control plane removed |
| S04 | tc-005, tc-007 | planning docs, skill kernels, compose scaffold | provider/generated skill assertions and template assertion | pass | runtime-selected step registration removed |
| S05 | tc-008, tc-009, tc-010, tc-014 | regression tests and dogfooding parity | `tests/cli_runtime`, `tests/unit`, dogfooding commands, `validate` | pass-with-finding | update drift finding recorded |
| S90 | tc-010, tc-014 | docs impact resolution | projection refresh and structural grep | pass | no dynamic projection sections |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | command | old guidance lacked plan-centric execution permission | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | plan/report sources asserted |
| tc-002 | S01/S03 | yes | command | old dynamic fields existed in contract/tests | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py`; `rg ...` | pass | no old field matches in target surfaces |
| tc-003 | S03 | yes | command | report rows could influence guidance step selection | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | report no longer control plane |
| tc-004 | S02 | yes | command | scaffold/non-executable plan needed block | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | `may_execute_approved_plan=false` |
| tc-005 | S04 | yes | structural assertion | plan scaffold needed obligation fields | `uv run pytest tests/cli_runtime/test_assurance_compose.py tests/unit/infra/test_init_update.py` | pass | `Step Obligation Contract` asserted |
| tc-006 | S02/S04 | yes | structural assertion | planning taxonomy needed review obligations | `uv run pytest tests/unit/infra/test_init_update.py` | pass | skill/template contracts assert no runtime-derived reviewer |
| tc-007 | S04 | yes | structural assertion | skill text still registered selected step | `uv run pytest tests/unit/infra/test_init_update.py`; `rg ...` | pass | selected step phrase absent |
| tc-008 | S05 | yes | command | old tests locked dynamic behavior | `uv run pytest tests/cli_runtime` | pass | replacement suite passed |
| tc-009 | S05 | yes | inspect-only | planning manual test finding needed record | discussion/report inspection | pass | finding recorded |
| tc-010 | S05/S90 | yes | command | provider/dogfood parity could drift | dogfooding guidance commands; `./spec-dock/scripts/spec-dock validate` | pass-with-finding | update drift finding recorded |
| tc-011 | S01/S02 | yes | command | execution permission implicit | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | `may_execute_approved_plan` asserted |
| tc-012 | S03/S05 | yes | command | hidden structured step selector could remain | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | no `workflow-plan-unselectable` |
| tc-013 | S02/S05 | yes | command | invalid assurance could show false strict authority | `uv run pytest tests/cli_runtime/test_workflow.py` | pass | unavailable authority asserted |
| tc-014 | S05/S90 | yes | manual + structural | projection could reintroduce old model | `guidance issue-execution`; `rg ... current-runbook.*` | pass | projection has no old dynamic sections |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001..tc-014 | S01/S02/S03/S04/S05/S90 | focused tests, full CLI runtime, unit suite, ruff, mypy, dogfooding guidance, validate | pass-with-finding | dogfooding update drift is non-blocking finding recorded in D-005/EAL-006 |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| discovered | tc-010 / tc-014 | dogfooding-runtime-update-drift | tc-010 / tc-014 | update success alone is not sufficient dogfooding evidence. | no | final PR reviewで確認 |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S90 | approved-local-execution | current host policy did not allow write-capable subagent mutation without explicit subagent request in this turn | N/A | provider runtime/assets/tests and dogfooding validation surfaces | active issue docs / provider source | planned implementation paths | unrelated PR delivery / GitHub review policy / destructive actions | pytest / ruff / mypy / dogfooding commands | failing gates / scope expansion | changed files, tests, risks, report evidence | pass-with-finding |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S90 | parent direct implementation under current tool policy; subagents not used for mutation | user requested implementation completion and PR creation in this worktree | planned provider/runtime/assets/tests/dogfood files | implementation, tests, dogfood validation, report update | git diff and tests before commit/PR | focused tests, CLI runtime, unit, ruff, mypy, validate | PR Codex review / final observation pending | recorded as parent implementation exception |

### セッションログ（2026-06-28 追加実装: Hidden assurance contract path）

#### 対象
- Step: S200 / S210
- AC/EC: AC-016..AC-019, EC-009
- closure ids: tc-022..tc-027

#### 実施内容
- Issue-local Assurance Contract の canonical path を `assurance.json` から `.assurance.json` に hard cutover した。
- provider runtime と dogfooding runtime の `AssuranceStore` が `.assurance.json` を read/write/verify authority として扱うようにした。
- `assurance classify` は `.assurance.json` を作成し、`assurance.json` を新規作成しないようにした。
- `.assurance.json` がなく旧 `assurance.json` だけがある場合は、`invalid / legacy_assurance_contract_path` として fail-closed し、`legacy_path` と `canonical_path` を diagnostics に含めるようにした。
- `.assurance.json` が symlink の場合は `invalid / contract_path_symlink` として fail-closed することを確認した。
- current dogfooding Issue-local `assurance.json` 7 件を `.assurance.json` に rename した。
- CLI help と focused tests を `.assurance.json` contract に更新した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py
# result: 51 passed in 49.20s

rg --files --hidden spec-dock/initiatives | rg '(^|/)assurance\.json$|(^|/)\.assurance\.json$'
# result: 7 hidden .assurance.json paths; 0 current Issue-local assurance.json paths

./spec-dock/scripts/spec-dock assurance verify --format json
# result: ok=true, status=valid, issue_id=iss-00244, reason=ok

./spec-dock/scripts/spec-dock guidance issue-execution
# result: state=ready, reason_code=assurance-valid, may_execute_approved_plan=true

./spec-dock/scripts/spec-dock assurance classify --help
# result: --dry-run help says "Return classification without writing .assurance.json"

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=153

git diff --check
# result: pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S200 | Red / 代替証跡 | existing tests expecting `assurance.json` fail before update | grep で runtime/tests が old path を read/write/help/fixture として参照していることを確認 | `rg -n "assurance\\.json|\\.assurance\\.json" ...` | observed | provider/dogfood `AssuranceStore` が旧 path を直接参照していた |
| S200 | Green | classify writes hidden path; show/verify read hidden path; legacy path requires migration; hidden symlink guard fail-closes | focused pytest `51 passed`; help/guidance/verify commands pass | pytest / CLI commands | pass | tc-022, tc-023, tc-024, tc-026, tc-027 |
| S210 | Green | current dogfooding artifacts are renamed and tests use `.assurance.json` | hidden file inspection shows 7 `.assurance.json` and 0 current `assurance.json` artifacts | `rg --files --hidden spec-dock/initiatives ...` | pass | tc-025 |
| S210 | Refactor | no broad historical rewrite and no dual authority | historical text references left where they are diagnostics/tests or history; runtime uses single canonical filename constant plus legacy diagnostic filename | diff inspection | pass | no compatibility dual-write |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S200 | legacy visible path の public status / reason が計画上は diagnostics とだけ定義されていた。 | dev-coder Ledger Note | `invalid / legacy_assurance_contract_path` を D-006 として採用し、missing strict-legacy と区別した。 | tc-024 | no | `tests/unit/infra/test_assurance_store.py`; `tests/cli_runtime/test_assurance.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S200 | tc-022, tc-023, tc-024, tc-026, tc-027 | focused evidence pass; code-reviewer + spec-reviewer pass; Step Commit Gate committed | focused tests and CLI commands pass; reviewer/commit pending | implementation-pass-review-pending | legacy visible path is fail-closed |
| S210 | tc-022..tc-027 | focused tests and dogfooding rename inspection pass; code-reviewer + qa-reviewer pass; Step Commit Gate committed | focused tests and hidden inspection pass; reviewer/commit pending | implementation-pass-review-pending | old current Issue-local `assurance.json` paths are absent |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-022 | S200/S210 | yes | command | runtime wrote old visible path | focused pytest; `test_assurance_classify_writes_contract` | pass | classify writes `.assurance.json` and does not create `assurance.json` |
| tc-023 | S200/S210 | yes | command | show/verify read old path | focused pytest; `./spec-dock/scripts/spec-dock assurance verify --format json` | pass | active issue valid through hidden contract |
| tc-024 | S200/S210 | yes | command | old path could be silently authoritative | focused pytest; legacy-only fixtures | pass | returns `invalid / legacy_assurance_contract_path` |
| tc-025 | S210 | yes | structural assertion | 7 current dogfooding `assurance.json` artifacts existed | `rg --files --hidden spec-dock/initiatives ...` | pass | 7 hidden paths, 0 old current artifact matches |
| tc-026 | S200/S299 | yes | structural assertion | help text mentioned `assurance.json` | `./spec-dock/scripts/spec-dock assurance classify --help`; grep inspection | pass | help text mentions `.assurance.json` |
| tc-027 | S200/S210 | yes | command | hidden path safety not covered | focused pytest symlink fixtures | pass | `.assurance.json` symlink returns `contract_path_symlink` |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-022..tc-027 | S200/S210 | focused pytest, hidden file inspection, active verify/guidance, help inspection, validate, diff check | pass-review-pending | S299 final reviewer gates pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| clarified | tc-024 | legacy-visible-path-migration-diagnostics | tc-024 | legacy-only path status/reason was implemented as `invalid / legacy_assurance_contract_path` rather than generic missing. | no | yes, S299 review |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S200/S210 | approved-delegated-execution | normal file mutation is delegated by issue-execution skill | dev-coder | hidden assurance contract path hard cutover and dogfooding rename | active issue docs / plan S200/S210 | provider runtime, dogfood mirror, focused tests, current dogfooding contract files | unrelated lifecycle behavior, historical discussion rewrites, dual authority | focused pytest, hidden inspection, active verify/guidance, validate | runtime writes old path / old path silently accepted / stale old artifacts remain | changed files, tests, status semantics, Ledger Note | pass; parent accepted D-006 |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S200/S210 | dev-coder | `.assurance.json` hard cutover、legacy visible path migration diagnostics、dogfooding artifact rename を実装。 | provider/dogfood assurance runtime, parser/help, focused tests, 7 dogfooding contract renames | worker: focused pytest 51 passed, hidden inspection, verify/guidance/help/validate; parent rerun: same focused pytest 51 passed, hidden inspection, verify/guidance/help/validate, diff-check pass | S299 pending | exact legacy status semantics was material decision | accepted; D-006 recorded |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S200/S210 | pending-review | hidden assurance runtime/tests/dogfood rename/report evidence | pending | pending | N/A | N/A | N/A | N/A |

### セッションログ（2026-06-28 S100/S110 + QA P2 follow-up）

#### 対象
- Step: S100 / S110, QA P2 follow-up for S200/S210
- AC/EC: AC-011..AC-019
- closure ids: tc-015..tc-019, tc-021, tc-023, tc-027

#### 実施内容
- `trigger_codex_review.sh` の instruction source を GitHub base/head の `.github/codex/review-policy.md` fetch から script-local `codex-review-instructions.md` へ切り替えた。
- provider asset と dogfooding mirror の `github-pr-observation` skill / trigger helper を同期し、script-local instruction asset を追加した。
- provider / dogfooding の `.github/codex/review-policy.md` asset を削除した。
- missing instruction は deterministic plain `@codex review` fallback を投稿し、invalid / non-UTF-8 / oversized / unreadable は human gate で fail-closed するようにした。
- QA P2 follow-up として、hidden `.assurance.json` を `assurance show` / `assurance verify` が `status=valid`, `has_contract=true`, `contract`, `classification` 付きで読める CLI assertion を追加した。
- `.assurance.json` contract の source binding が別 Issue を指す場合に `source_binding_path_not_issue_local` で invalid になる unit coverage を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py
# result: 515 passed in 312.02s

uv run pytest tests/unit/infra/test_assurance_store.py tests/unit/application/test_assurance.py tests/cli_runtime/test_assurance.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py
# result: 53 passed in 50.62s

rg -n "trusted base|base-SHA|review-policy.md|\\.github/codex/review-policy|review_policy|Trusted review policy|base policy" .agents/skills/github-pr-observation src/spec_dock/assets/install_root/.agents/skills/github-pr-observation tests/unit/infra/test_init_update.py
# result: no matches

rg --files --hidden .agents src/spec_dock/assets/install_root .github | rg '(^|/)review-policy\\.md$|(^|/)codex-review-instructions\\.md$'
# result: only provider and dogfooding codex-review-instructions.md

rg --files --hidden spec-dock | rg '(^|/)assurance\\.json$|(^|/)\\.assurance\\.json$'
# result: 7 hidden .assurance.json paths, 0 current assurance.json paths
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S100 | Red / 代替証跡 | existing base-SHA policy tests fail before update; fake gh log would show contents API call | pre-implementation grep showed trigger helpers using `baseRefOid` and `.github/codex/review-policy.md` contents API | `rg -n "trigger_codex_review|review-policy|baseRefOid|review_policy" ...` | observed | old trusted-base behavior present before patch |
| S100/S110 | Green | valid instruction included; missing instruction posts fallback; invalid / unreadable / oversized blocks; no GitHub policy fetch | focused pytest `515 passed`; grep no obsolete trusted-base/review-policy matches | pytest / grep | pass | tc-015..tc-019, tc-021 |
| S100/S110 | Refactor | provider and dogfooding assets stay synchronized | file-list shows two `codex-review-instructions.md` assets and no `review-policy.md` asset | `rg --files --hidden ...` | pass | script and skill copied from provider to dogfood mirror |
| S200/S210 | QA P2 Green | hidden `show` / `verify` expose valid status, contract, classification; dual-path and outside-issue guards are explicit | focused assurance lane `53 passed` | pytest | pass | tc-023, tc-027 strengthened |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S100/S110 | tc-015, tc-016, tc-017, tc-018, tc-019, tc-021 | focused tests and grep inspection pass | `test_init_update.py` 515 passed; obsolete grep no matches; asset list has only script-local instruction assets | implementation-pass-review-pending | PR #245 live dogfooding S120 remains orchestrator-owned |
| QA P2 for S200/S210 | tc-023, tc-027 | focused hidden assurance read and guard tests pass | assurance/workflow lane 53 passed | implementation-pass-review-pending | show/verify assertion now checks status/contract/classification; dual-path state fails closed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-015 | S100/S110 | yes | red-required | old script fetched remote policy | `test_issue_244_trigger_helper_uses_script_local_review_instruction` | pass | body includes source, instruction hash, status, reviewed head SHA, instruction text |
| tc-016 | S100/S110 | yes | red-required | old fake gh fixture included contents API | fake gh log assertion and final grep | pass | no `/contents/` GitHub API read in trigger tests |
| tc-017 | S100/S110 | yes | red-required | missing base policy blocked | `test_issue_244_trigger_helper_posts_plain_review_when_instruction_missing` | pass | posts fallback with `missing_plain_fallback` |
| tc-018 | S100/S110 | yes | red-required | invalid policy gate was remote-policy based | empty, non-UTF-8, oversized instruction tests | pass | human gate with no comment |
| tc-019 | S100/S110 | yes | structural assertion | provider/dogfood `review-policy.md` existed | file-list inspection | pass | only script-local instruction assets remain |
| tc-023 | S200/S210 | yes | command | QA P2 found weak assertion | `tests/cli_runtime/test_assurance.py` | pass | show/verify assert `status=valid`, `has_contract=true`, `contract`, `classification` |
| tc-027 | S200/S210 | yes | command | outside-issue guard needed explicit coverage | `test_hidden_contract_rejects_source_binding_from_another_issue` | pass | `.assurance.json` source binding outside target issue is invalid |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S100/S110 + QA P2 | dev-coder | script-local review instruction behavior、asset removal/parity、hidden assurance QA assertions を実装。 | provider/dogfood github-pr-observation assets, focused tests, report evidence | `test_init_update.py` 515 passed; assurance/workflow lane 53 passed; grep/file-list inspections pass | S199/S299 pending | exact trigger body metadata semantics and retained 32768-byte max are implementation-time choices from ADR bounds | pending orchestrator review |

#### レビュー指摘フォローアップ（S199/S299）
| レビュー元（reviewer） | 優先度 | 指摘 | 対応 | 証跡 | 状態 |
|---|---|---|---|---|---|
| code-reviewer | P1 | hidden `.assurance.json` と旧 `assurance.json` が coexist すると valid hidden contract が受理され、no-dual-authority を破る。 | `read_contract` と `_contract_write_path` で旧 visible path が存在する限り `legacy_assurance_contract_path` として fail-closed にし、dual-path unit test を追加。 | `tests/unit/infra/test_assurance_store.py`; code-reviewer re-review pass | fixed |
| qa-reviewer / code-reviewer | P2 | script-local instruction unreadable branch が未テスト。 | `codex-review-instructions.md` の位置に directory を置く regression test を追加し、`review_instruction_unreadable` / no POST を検証。 | `tests/unit/infra/test_init_update.py`; qa-reviewer/code-reviewer re-review pass | fixed |
| spec-reviewer | P2 | Final Code Review Gate が stale に `implementation not started` と記録していた。 | gate row を実装済み diff に対する code review pending 表現へ更新。 | `report.md`; spec-reviewer re-review pass | fixed |

#### PR #245 dogfooding 観測（S120 / S199 follow-up）
| 項目 | 証跡 | 結果 | メモ |
|---|---|---|---|
| branch push | `git push origin iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation` | pass | PR head updated to `4d7cf1a4751d0a89562c99af6b7b6f63497f9227` |
| review trigger | `wait_pr_observation.sh --repo chemitaro/spec-dock --pr 245 --head-sha 4d7cf1a4751d0a89562c99af6b7b6f63497f9227 --trigger-mode post-once ...` | pass | trigger comment `4825350981`; `body_matches_expected=true`; `instruction_status=loaded`; source `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md` |
| PR observation | same command | failed | `Provider CI` failed in `Run provider static analysis`; recommended action `fix_ci` |
| CI failure fix | `gh run view 28316189965 --log-failed` | diagnosed | unused `base64` import and ruff format drift in `tests/unit/infra/test_init_update.py` |
| local static analysis | `make lint` | pass | ruff check pass; ruff format check pass; mypy pass |
| focused trigger tests | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_244_trigger_helper or issue_176_s05b_codex_review_trigger_helper_is_installed_by_init_and_update'` | pass | `7 passed, 508 deselected in 3.93s` |

#### Review instruction 文面調整（S120 user feedback follow-up）
| 項目 | 観測 / 決定 | 証跡 | 状態 |
|---|---|---|---|
| Epic-level intent | Codex review instruction の目的は、P0/P1 と machine-validated blocker に review / repair loop を集中させ、P2/P3 や style/format/lint 相当の低価値指摘による review-push-review 反復を抑制すること。 | `epic/requirement.md` E-RQ-010/E-RQ-011, E-AC-011; `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md` | confirmed |
| gap | 既存 `codex-review-instructions.md` は correctness/security/user-visible regressions を優先するだけで、P2/P3 non-blocking、lint/formatter 責務、comment zero ではなく blocker zero という意図を十分に明文化していなかった。 | PR #245 posted comment `4825350981` body inspection | fixed |
| instruction update | provider authority と dogfooding copy の script-local instruction を、merge-blocking risk / P0-P1 / protected-domain P2 with machine evidence / no low-value comments へ最適化した。 | `.agents/.../codex-review-instructions.md`; `src/spec_dock/assets/install_root/.../codex-review-instructions.md` | implemented |
| regression guard | install/update 後の instruction asset に P0/P1 blocker、P2/P3 non-blocking、lint/formatter-enforceable issue suppression の文言が含まれる assertion を追加した。 | `tests/unit/infra/test_init_update.py` | implemented |

### セッションログ（2026-06-29 S300/S310/S320 PR observation completion wait repair）

#### 対象
- Step: S300 / S310 / S320
- AC/EC: AC-020..AC-023
- closure ids: tc-028, tc-029, tc-030, tc-031, tc-032, tc-033, tc-034

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 判断（decision） | 例外理由（reason） | 直接変更した範囲（direct mutation scope） | 代替策（alternatives） | リスク低減（risk mitigation） | 状態（status） |
|---|---|---|---|---|---|---|
| S300/S310/S320 | parent-direct-implementation | 今回の修正対象は `github-pr-observation` skill 自体とその wait script であり、PR作成後の手動dogfooding監視まで同一文脈で連続検証する必要がある。 | provider/dogfooding `github-pr-observation/SKILL.md`; provider/dogfooding `pr_observation_wait.py`; focused tests | delegated dev-coder | 変更範囲を wait completion contract と focused tests に限定し、focused PR observation lane 107件、ruff、assurance、validate を実行した。 | approved |
| S02/S399 dogfooding follow-up | parent-direct-implementation | dev-coder subagent spawn failed because the thread had reached the agent limit. The finding blocked the active issue execution guidance itself and had to be repaired before PR observation could continue. | provider/dogfooding `workflow.py`; `tests/cli_runtime/test_workflow.py`; research artifact | delegated dev-coder | 変更範囲を plan readiness marker ordering and focused regression test に限定し、provider/dogfood parity diff、focused workflow pytest、active `guidance issue-execution` を確認した。 | approved |

#### 実施内容
- `pr_observation_wait.py` から active `review_completion_unknown` terminal path を削除した。
- `missing_current_completion_signal` は stable / quiet / latency で完了扱いにせず、明示的な Codex completion artifact、blocker、CI/permission terminal、または timeout まで wait/resume する契約にした。
- deadline 到達、under-budget final poll skip、snapshot poll timeout は `timeout / wait_or_resume / observation_complete=false` として扱い、`post_unknown_fresh_audit_required` を新規出力しないようにした。
- provider と dogfooding の `github-pr-observation/SKILL.md` から terminal-like `review_completion_unknown` contract を削除し、legacy vocabulary と retryable timeout/resume contract を明記した。
- 旧unknown期待の unit tests を timeout/resume期待へ反転し、遅延submitted reviewを見逃さない回帰テスト名・期待を明確化した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k "s101_wait_times_out_stable_no_completion or s204_wait or s01_wait_carryover or s420_wait_pending_review_beats_unknown or s430_ci_passed_age_below_300 or s430_post_unknown or s430_short_timeout_does_not_force_no_completion_confirmation_poll"
# result: 13 passed, 508 deselected in 33.12s

uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or s04_wait or s101 or s204 or s420_wait or s430 or s01_wait_carryover or s03_wait_fallback"
# result: 107 passed, 414 deselected in 153.91s; after formatting rerun 107 passed, 414 deselected in 142.60s

uv run pytest tests/unit/infra/test_init_update.py
# result: 521 passed in 320.06s

uv run ruff check src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py tests/unit/infra/test_init_update.py
# result: All checks passed

make lint
# result: ruff check pass; ruff format check pass; mypy pass

./spec-dock/scripts/spec-dock assurance verify
# result: ok, issue=iss-00244, authorized_profile=standard, reason=ok

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=153

rg -n "review_completion_unknown is a non-pass|terminal-like review state|post_unknown_fresh_audit_required|mark_decision_review_completion_unknown|is_review_completion_unknown_candidate|REVIEW_COMPLETION_UNKNOWN|review_completion_unknown_latency_satisfied" src/spec_dock/assets/install_root/.agents/skills/github-pr-observation .agents/skills/github-pr-observation tests/unit/infra/test_init_update.py
# result: only negative assertions in tests remain
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S300 | Red / 代替証跡 | existing tests expected active `review_completion_unknown` | focused pytest initially failed 9 tests where stable no-completion promoted to human_gate unknown or emitted latency metadata | initial focused pytest failure output | observed | old behavior was still encoded in tests before expectation update |
| S300 | Green | no-completion does not complete by stability/time/quiet; timeout remains retryable | focused wait tests now return `timeout / wait_or_resume / observation_complete=false`; old unknown functions removed | focused pytest; grep inspection | pass | tc-028, tc-029, tc-034 |
| S310 | Green | delayed submitted review is not missed | `test_issue_187_s204_wait_delayed_submitted_review_is_not_missed` waits through no-completion and selects submitted review blocker | focused pytest 107 passed | pass | tc-030 |
| S320 | Green | quiet/same fingerprint only stabilizes explicit completion; no-completion stability cannot pass | no-completion classify returns `can_complete_when_stable=false`; under-budget / deadline path becomes timeout; strict no-findings and blocker paths remain covered in PR observation lane | diff inspection; focused pytest 107 passed | pass | tc-031..tc-033 |
| S300/S320 | Refactor | remove obsolete unknown metadata and keep provider/dogfood parity | provider/dogfood wait script and skill are byte-identical; grep finds no active unknown contract in skill/scripts | `diff -u ...`; `rg ...` | pass | only legacy vocabulary note and negative tests remain |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S300 | tc-028, tc-029, tc-031, tc-034 | active unknown terminal path removed from wait behavior and skill contract; focused tests pass | provider/dogfood `pr_observation_wait.py` removes unknown promotion helpers and latency guards; skill contract updated; focused pytest/grep pass | implementation-pass-review-pending | reviewer gates pending |
| S310 | tc-028, tc-029, tc-030 | delayed review and timeout/resume regression tests pass | focused pytest 107 passed; delayed submitted review test selects `current_selected_unresolved_thread` with `submitted_pull_request_review` | implementation-pass-review-pending | PR #245 live/manual S330 pending |
| S320 | tc-031, tc-032, tc-033 | hydration/head-binding tests pass; no broad state-machine rewrite | no-completion cannot complete via stability; existing no-findings/blocker tests included in PR observation lane | implementation-pass-review-pending | no GitHub Checks/status-rollup surface added |

#### ADR 昇格 / 旧決定変更済み注記（ADR Promotion and Supersession Evidence）
| 対象 | 処理 | 証跡 | 結果 |
|---|---|---|---|
| PR observation completion wait decision | `20260628t154553z-adr PR Observation Explicit Review Completion` を accepted ADR authority として更新 | PR #245 delayed review failure、explicit completion artifact、hydration stability gate、under-budget broad pass preservation 不採用の境界を Decision / Context / Rationale / Consequences に追記 | pass |
| Script-local review instruction ADR | 古い trusted base-SHA / missing policy 方針との境界を明確化 | `20260623t074444z-adr` に、review completion / no-review-work / merge-prepared 判断は同 ADR の authority ではなく `20260628t154553z-adr` が authority であると追記 | pass |
| Blocker-centric PR closure ADR | blocker disposition と review completion 判定の責務を分離 | `20260623t074447z-adr` に、completion artifact 未観測時は blocker-centric closure 評価へ入らず、timeout / wait_or_resume は review 不要の human gate ではないと追記 | pass |
| PR review body blocker ingestion ADR | selected pull request review body も blocker input とする意思決定をADRへ昇格 | `20260628t185812z-adr-pr-review-body-blocker-ingestion.md` を追加し、`20260623t074447z-adr` / `20260628t154553z-adr` に変更済み注記を追記 | pass |
| PR #245 no-findings completion dogfooding decision | latest live observation を ADR へ反映 | `a1ee5ac3` の wait は quiet/time guard で早期終了せず、Codex no-findings issue comment を待機した。旧 carryover threads 解決後の resume で `passed / merge_prepared` を確認したことを `20260628t154553z-adr` / `20260623t074447z-adr` へ追記 | pass |
| Historical draft package artifacts | 古い draft / seed の矛盾を変更済みとして注記 | draft requirement / draft design / issue slice seeds / provided draft package synthesis に historical status update を追加 | pass |

#### ADR 整合検証（ADR Alignment Verification）
| コマンド / 確認 | 結果 | メモ |
|---|---|---|
| `uv run pytest tests/unit/infra/test_init_update.py -k "issue_75_pr_observation_wait_applies_zero_check_grace_before_human_gate or issue_75_pr_observation_wait_late_review_change_resets_stability" -vv` | pass: 2 passed, 519 deselected | reviewer が指摘した zero-check grace / late review stability regression は現行手元で再現せず通過 |
| `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or s04_wait or s101 or s204 or s420_wait or s430 or s01_wait_carryover or s03_wait_fallback or issue_75_pr_observation_wait or issue_232_review_collector"` | pass: 119 passed, 405 deselected | PR observation lane で completion / timeout / hydration / review body blocker 周辺を再確認 |
| `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` | pass: 19 passed | design / plan readiness と hard cutover guidance fixture を確認 |
| `uv run pytest tests/unit/infra/test_init_update.py` | pass: 524 passed in 315.43s | shipped asset / PR observation / installer regression 全体を確認 |
| `make lint` | pass: ruff check, ruff format check, mypy | static analysis 全体を確認 |
| `./spec-dock/scripts/spec-dock validate` | pass: `spec-dock: ok (validate) nodes=153` | ADR / historical note 追加後の SpecDock tree validation |
| `./spec-dock/scripts/spec-dock assurance verify` | pass: issue=iss-00244, authorized_profile=standard | requirement/design/plan source binding 更新後の assurance contract を確認 |
| `git diff --check` | pass | Markdown 差分の whitespace error なし |

#### PR #245 Review Finding Follow-up（2026-06-29）
| Review / finding | 対応 | 検証 | 結果 |
|---|---|---|---|
| Codex P1: `Preserve terminal PR observation result on final timeout` | final snapshot poll が timeout した場合でも、直前 payload が zero-check grace terminal または stable review completion として既に成立していれば、その terminal / completion state を保持するよう `pr_observation_wait.py` を修正 | added `test_issue_187_s430_final_snapshot_timeout_preserves_zero_check_terminal_state` and `test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state` | fixed |
| PR observation lane | provider / dogfooding mirror の wait script を同期し、既存 issue_75 regression と新規 final snapshot timeout regression を含めて確認 | focused: 4 passed; broad: 109 passed, 414 deselected; full `test_init_update.py`: 523 passed in 304.49s | pass |
| Static analysis / SpecDock validation | wait script parity、lint、assurance、validate を確認 | `make lint` pass; provider/dogfood `diff -u` no diff; `assurance verify` ok; `validate` ok nodes=153 | pass |
| Codex P1: `Block scaffold plans in strict-legacy guidance` | `.assurance.json` がない strict legacy path でも `plan.md` scaffold / missing を execution-ready にしないよう `workflow.py` を修正 | added `test_guidance_blocks_strict_legacy_placeholder_plan`; focused pytest 7 passed; CLI runtime lane 19 passed | fixed |
| Codex P1: `Require non-placeholder design before ready guidance` | valid assurance path / strict legacy path の両方で `design.md` が missing / scaffold の場合は execution-ready にしないよう `workflow.py` を修正 | added `test_guidance_blocks_placeholder_design_even_with_valid_assurance_and_executable_plan`; focused pytest 7 passed; CLI runtime lane 19 passed | fixed |
| Codex P1: `Include pull review bodies in blocker policy` | selected pull request review body を blocker policy input に含め、body P1 を comments/threads 0 でも blocker として扱うよう `pr_review_snapshot.py` を修正し、ADRへ昇格 | added `test_issue_232_review_collector_treats_p1_pull_review_body_as_blocker`; focused pytest 7 passed; PR observation lane 119 passed; ADR `20260628t185812z-adr` | fixed |
| Dogfooding finding: `design-not-substantive` false positive | `design.md` / `plan.md` readiness helper の status / scaffold marker 判定を frontmatter / 明示的 scaffold 文言へ限定し、本文の `状態: "draft"`、`docs/templates`、`non-placeholder` では block しないよう修正 | added `test_guidance_allows_substantive_design_that_mentions_draft_status_in_body`; `uv run pytest tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` => 20 passed; `guidance issue-execution` => `state=ready`, `may_execute_approved_plan=true` | fixed |
| Codex P1: `Return invalid JSON for unreadable assurance paths` | `.assurance.json` が directory など non-file の場合に `contract_path_not_file` の structured invalid result を返し、OSError も `contract_unreadable` として fail-closed にした | added `test_read_contract_rejects_non_file_hidden_assurance_contract` | fixed |
| Codex P1: `Restrict TODO scaffold markers to placeholders` | `TODO` / `TBD` を本文全体の scaffold marker から外し、frontmatter / 明示的 scaffold 判定へ限定した | added `test_guidance_allows_executable_plan_that_mentions_todo_in_body` | fixed |
| Codex P1: `Reject symlinked planning artifacts before ready` | strict-legacy path の `_read_optional_text` で symlinked `design.md` / `plan.md` を読まず、execution-ready にしないよう修正した | added `test_guidance_blocks_strict_legacy_symlinked_planning_artifact` | fixed |
| Codex P1: `Roll back compose artifact writes on failure` | `assurance compose` が変更 artifact を書く前に全 changed artifact の writable preflight を行うようにし、後段 artifact failure による部分書き込みを防いだ | added `test_compose_preflights_all_changed_artifacts_before_writing` | fixed |
| Codex P1: `Read review policy from the trusted base` | 採用しない。current issue / Epic ADR は trusted base policy を script-local instruction source へ変更済みであり、GitHub base/head `.github/codex/review-policy.md` を読まないことが AC-012 / AC-015 の期待結果である。 | `requirement.md` AC-012/AC-015; `design.md` 方針 D; `plan.md` tc-016/tc-019/tc-021; trigger script comment added for current contract clarity | rejected |
| Post-review local verification | P1 4件の修正と trusted-base 誤指摘の明文化後、assurance / workflow / trigger / full init-update / lint / validate を再実行した。 | `40 passed` assurance/application/compose lane; `23 passed` workflow lane; `17 passed` trigger focused lane; `524 passed` full `test_init_update.py`; `make lint`; `validate`; `assurance verify`; `git diff --check` | pass |

#### PR #245 Review Finding Follow-up（2026-06-29 round 2）
| Review / finding | 対応 | 検証 | 結果 |
|---|---|---|---|
| Codex P1: `Reject symlinked requirements before marking execution ready` | strict-legacy path の `requirement.md` reader が symlink を辿らないようにし、symlinked requirement は missing として requirement-capture に戻す。 | `test_guidance_blocks_strict_legacy_symlinked_requirement`; workflow lane 25 passed | fixed |
| Codex P1: `Refuse directories when clearing stale runbook projections` | `active/current-runbook.json` / `current-runbook.md` / `context-pack.md` が directory の場合、active pointer refresh は削除せず RuntimeError で停止する。 | `test_apply_active_pointers_refuses_generated_projection_directories`; active/assurance unit lane 23 passed | fixed |
| Codex P1: `Reject negated plan text before enabling execution` | `implementation step(s)` / `planned contract` のような汎用語を positive marker から外し、`no implementation steps` / `no executable steps` を scaffold marker として扱う。 | `test_guidance_blocks_negated_plan_text_without_executable_steps`; workflow lane 25 passed | fixed |
| Codex P1: `Keep draft discussion frontmatter delimited` | draft discussion normalization が frontmatter closing delimiter と body を改行で分離するよう修正した。 | `test_new_doc_creates_draft_artifacts_from_scope_specific_templates`; compose/new lane 53 passed, 5 skipped | fixed |
| Codex P1: `Return stale compose as JSON before reading missing artifacts` | `assurance compose` は stale source binding を検出した時点で structured invalid result を返し、missing artifact read へ進まないようにした。 | `test_assurance_compose_returns_stale_binding_before_reading_missing_artifact`; compose/new lane 53 passed, 5 skipped | fixed |
| Codex P1: `Preserve or reject non-empty obligation notes` | 現行 domain model が preserve しない `obligations.notes` non-empty は `unsupported_obligations_notes` として invalid schema にする。 | `test_invalid_json_and_invalid_schema_have_distinct_machine_reasons`; active/assurance unit lane 23 passed | fixed |
| Current spec alignment | 上記 6 件を `requirement.md` / `design.md` / `plan.md` に明文化し、`tc-042`〜`tc-047` を追加した。ADR は既存 accepted ADR（explicit review completion / review body blocker ingestion）と旧 ADR の変更済み注記で整合している。 | docs inspection; focused tests pass | pass |
| Codex P1: `Allow late stable review completion before timing out` | 採用しない。現行の `20260628t154553z-adr` は explicit completion artifact に加えて hydration stability（quiet window / same fingerprint）を completion 後 gate として要求する。under-budget final poll で incomplete hydration を broad に `passed / merge_prepared` へ保存する試行は、既存の quiet / same fingerprint contract tests を壊したため rejected / false positive として扱う。 | `PYTHONPATH=src uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_wait_late_review_change_resets_stability -q` pass; broad preservation trial failed existing stability tests and was reverted | rejected |
| Dogfooding finding: active `plan-not-executable` false positive | `Spec-Locked Closure Index` の失敗検出説明に含まれる `no implementation steps` を scaffold marker として先勝ち評価しないよう修正した。Frontmatter scaffold は引き続き fail-closed とし、本文中の negated marker は executable marker がない場合だけ block する。 | research `20260628t225731z-research-plan-readiness-negated-example-false-block.md`; added `test_guidance_allows_executable_plan_that_mentions_negated_marker_as_test_fixture`; focused pytest 3 passed; active `guidance issue-execution` returns `ready / may_execute_approved_plan=true` | fixed |

#### PR #245 Observation Dogfooding（2026-06-29 latest head `a1ee5ac3`）
| 観測項目 | 証跡 | 結果 | メモ |
|---|---|---|---|
| post-once wait | `/private/tmp/spec-dock-pr245-observation-a1ee5ac3/result.json` | completed with `human_gate / address_review_feedback` | completion signal は `fallback_issue_comment` / strict no-findings candidate。旧 carryover unresolved threads 17件が残っていたため merge-prepared にはしなかった |
| early-stop regression | poll log / result wait metadata | pass | `quiet_seconds > 90`、`trigger_age > 300`、`completion_signal=none` の状態では終了せず、Codex no-findings issue comment 出現まで待機した |
| trigger evidence | trigger comment `4827674309` | pass | `body_matches_expected=true`; `instruction_status=loaded`; `reviewed_head_sha=a1ee5ac3cfe9e7a603de396b0d686d2fdb350e25` |
| carryover resolution | GitHub GraphQL `resolveReviewThread` for 17 old threads | pass | 旧 review threads は対応済み/誤指摘として GitHub 上で resolved にした |
| resume after resolve | `/private/tmp/spec-dock-pr245-observation-a1ee5ac3-resume-after-resolve/result.json` | pass: `passed / merge_prepared` | `decision.status_reason=codex_no_findings_issue_comment`; `completion_signal=codex_no_findings_issue_comment`; `carryover_unresolved_count=0`; `current_selected_unresolved_count=0`; CI/head matched |

#### PR #245 Review Finding Follow-up（2026-06-29 round 3）
| Review / finding | 対応 | 検証 | 結果 |
|---|---|---|---|
| Codex P1: `Promote composed artifacts out of draft` | `assurance compose` が awaiting-assurance-compose placeholder を materialize する際、frontmatter の `artifact_state` を削除し、`状態: "draft"` / `状態: draft` を `状態: "approved"` へ昇格するよう修正した。 | `test_assurance_compose_materializes_placeholder_design_and_plan`; compose/workflow lane 39 passed | fixed |
| Codex P1: `Emit a plan marker accepted by workflow readiness` | standard profile の composed plan section heading を `## 実装ステップ` に変更し、初期 step closure contract として扱う説明を追加した。 | `test_assurance_compose_materializes_placeholder_design_and_plan` で compose 後の `guidance issue-execution` が `ready / may_execute_approved_plan=true` になることを確認 | fixed |
| Codex P1 body: `Allow the last stabilizing review poll` | 現行 ADR は completion artifact 後の hydration stability を必須とし、under-budget final timeout で incomplete hydration を broad に pass へ保存しない。ローカルでは reviewer が示した exact regression test が pass したため、現時点では no-code / stale finding として扱う。 | `PYTHONPATH=src uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_observation_wait_late_review_change_resets_stability -q` => pass | rejected-no-code |
| Codex P1 body: `Ignore the waitable Actions-context limitation` | `required_actions_context_pending` は waitable limitation であるため、`ci.status=unknown` のとき blocking limitation として human_gate に昇格しないよう classifier の ignored codes に追加した。 | `test_issue_244_pr_observation_snapshot_required_actions_context_pending_is_waitable`; focused PR observation lane 81 passed | fixed |
| ADR promotion: plan-centric execution hard cutover | Issue execution authority を `plan.md` に一本化し、runtime-selected `selected_step` / `step_assurance` / `context_packets` を廃止する意思決定を Epic ADR `20260629t003131z-adr Plan Centric Issue Execution Preflight` へ昇格した。 | ADR inspection; old ADR `20260623t074441z` / `20260623t074442z` に変更済み注記を追加 | pass |
| ADR promotion: hidden assurance contract path | Issue-local Assurance Contract を `assurance.json` から `.assurance.json` へ hard cutover する意思決定を Epic ADR `20260629t003132z-adr Hidden Assurance Contract Path` へ昇格した。 | ADR inspection; old ADR `20260623t074443z` に変更済み注記を追加 | pass |
| Current focused verification | round 3 の実装差分と ADR/report 更新後に focused / broader regression を実行した。 | compose readiness test 1 passed; required-actions context test 1 passed; late review stability test 1 passed; compose/workflow/context lane 39 passed; PR observation focused lane 81 passed; full `test_init_update.py` 525 passed; `make lint`; `validate`; `assurance verify`; `git diff --check` | pass-current-head-pr-reobservation-pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-028 | S300/S310 | yes | command | stable no-completion promoted to human_gate unknown | focused pytest 13 passed / 107 passed | pass | stable no-completion returns timeout/resume, not unknown |
| tc-029 | S300/S310 | yes | command | timeout/latency metadata mixed with unknown promotion | focused pytest 13 passed / 107 passed | pass | resume action remains `wait_or_resume`; `observation_complete=false` |
| tc-030 | S310 | yes | command | PR #245 style delayed review could be missed after no-completion stability | `test_issue_187_s204_wait_delayed_submitted_review_is_not_missed` | pass | final result is `human_gate / address_review_feedback` |
| tc-031 | S320 | yes | command / inspection | quiet/same fingerprint could complete no-completion candidate | classify/diff inspection plus focused pytest | pass | no-completion `can_complete_when_stable=false` |
| tc-032 | S320 | yes | command | wrong/no explicit completion must not pass | focused PR observation lane | pass | existing strict no-findings/blocker tests remain green |
| tc-033 | S320 | yes | command | partial/no completion visibility could be over-promoted | focused PR observation lane | pass | no completion becomes timeout/resume, not pass |
| tc-036 | S320/S399 | yes | command | PR review body P1 could be ignored if only issue comments / inline comments / threads are scanned | `test_issue_232_review_collector_treats_p1_pull_review_body_as_blocker`; focused pytest 7 passed; PR observation lane 119 passed | pass | selected pull request review body is blocker input |
| tc-037 | S02/S399 | yes | command | substantive active design was blocked by body prose containing draft/template/placeholder words | `test_guidance_allows_substantive_design_that_mentions_draft_status_in_body`; `guidance issue-execution` | pass | active issue guidance now returns `ready / may_execute_approved_plan=true` |
| tc-038 | S02/S399 | yes | command | executable plan body containing TODO/TBD was blocked as scaffold | `test_guidance_allows_executable_plan_that_mentions_todo_in_body` | pass | TODO/TBD body prose no longer controls readiness |
| tc-039 | S02/S399 | yes | command | strict-legacy path followed symlinked planning artifacts | `test_guidance_blocks_strict_legacy_symlinked_planning_artifact` | pass | symlinked design/plan blocks ready guidance |
| tc-040 | S200/S399 | yes | command | non-file `.assurance.json` raised unstructured OSError path | `test_read_contract_rejects_non_file_hidden_assurance_contract` | pass | returns structured invalid result |
| tc-041 | S210/S399 | yes | command | compose could partially write earlier artifacts before later artifact failure | `test_compose_preflights_all_changed_artifacts_before_writing` | pass | all changed artifact writes are preflighted before mutation |
| tc-034 | S300 | yes | structural assertion | skill text described terminal-like unknown human gate | grep inspection | pass | active terminal unknown wording removed from provider/dogfood skills |
| tc-042 | S02/S399 | yes | command | strict-legacy path followed symlinked requirement.md | `test_guidance_blocks_strict_legacy_symlinked_requirement` | pass | symlinked requirement returns `requirement-capture / requirement-missing` |
| tc-043 | S05/S399 | yes | command | active projection cleanup could recursively delete directory content | `test_apply_active_pointers_refuses_generated_projection_directories` | pass | generated file paths refuse directories |
| tc-044 | S02/S399 | yes | command | negated plan prose could match positive implementation-step marker | `test_guidance_blocks_negated_plan_text_without_executable_steps`; `test_guidance_allows_executable_plan_that_mentions_negated_marker_as_test_fixture` | pass | genuine no implementation steps remains blocked; executable plan fixture prose is allowed |
| tc-045 | S05/S399 | yes | command | draft discussion frontmatter closing delimiter could concatenate with body heading | `test_new_doc_creates_draft_artifacts_from_scope_specific_templates` | pass | delimiter/body separation is asserted |
| tc-046 | S210/S399 | yes | command | compose could read missing source-bound artifact before returning stale JSON | `test_assurance_compose_returns_stale_binding_before_reading_missing_artifact` | pass | stale source binding returns structured invalid JSON |
| tc-047 | S200/S399 | yes | command | non-empty obligation notes were accepted and lost on round trip | `test_invalid_json_and_invalid_schema_have_distinct_machine_reasons` | pass | `unsupported_obligations_notes` rejects non-empty notes |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-028..tc-047 | S300/S310/S320/S399 | focused pytest 13 passed, PR observation lane 119 passed, CLI runtime lane 25 passed, active/assurance unit lane 23 passed, assurance/application/compose/new lanes 32 passed + 53 passed / 5 skipped, full `test_init_update.py` 525 passed, `make lint`, `assurance verify`, `validate`, `git diff --check`, provider/dogfood parity diffs, PR #245 `a1ee5ac3` observation/resume | pass-current-head-docs-update-pending | docs-only ADR/report update will require final PR re-observation after commit/push |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S300/S310/S320 + round 2 PR review follow-up | local-pass-pr-review-pending | PR observation wait script/skill/tests/report evidence plus round 2 safety fixes | pending commit | pending post-commit clean check | N/A | N/A | N/A | N/A |

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer | `plan.md` S90 に docs impact resolution を明記 | pending |
| runtime guidance / shipped issue skills / assurance compose fragment / dogfooding projection | yes | orchestrator | `guidance issue-execution`; focused workflow/compose/new/assurance tests; full `uv run pytest tests/unit/infra/test_init_update.py`; provider/dogfood parity diffs | local pass; PR review pending |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | S100/S110/S200/S210/S299 obligation coverage | added | QA re-review pass; `test_init_update.py` 515 passed; assurance/workflow lane 53 passed; hidden/file-list inspections | pass |
| local verification | whole issue obligation coverage | executed | `uv run pytest tests/unit/infra/test_init_update.py` 525 passed; `uv run pytest tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py tests/cli_runtime/test_workflow_context_routing.py` 39 passed; focused PR observation lane 81 passed; `./spec-dock/scripts/spec-dock validate`; `assurance verify`; `git diff --check`; `make lint` | pass |
| PR observation | PR #245 current head `a1ee5ac3` | executed / passed for current head before this docs update | `wait_pr_observation.sh --trigger-mode post-once` waited for completion artifact; old carryover threads produced human_gate; after resolving 17 carryover threads, `--trigger-mode resume` returned `passed / merge_prepared` with `codex_no_findings_issue_comment` | pass-current-head-docs-update-pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | S100/S110/S200/S210 integrated diff | P1 dual-path fix and P2 unreadable instruction test verified | 2 | pass |
| PR Codex review | issue-wide integrated diff | latest current-head observation reached `passed / merge_prepared` after carryover thread resolution | multiple | pass-current-head-docs-update-pending |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report alignment including AC-020..AC-024 / S300..S399 | fresh spec-reviewer pass; P2 traceability gap fixed by adding new ADR to S320/S399 inputs and `tc-036` to S320 closure criteria | 4 | pass |
| spec-reviewer round 2 | requirement / design / plan / report alignment including tc-042..tc-047 and ADR supersession | fresh spec-reviewer pass with P2 findings; AC-024 top-level plan index and stale final-gate rows updated | 1 | pass |
| local spec traceability | requirement / design / plan / report alignment | closure ids tc-001..tc-047 have local implementation evidence; PR #245 `a1ee5ac3` observation reached `passed / merge_prepared`; this ADR/report docs-only update requires final re-observation after commit/push | 0 | local pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| report.md planning ledger | requirement/design/plan/report/discussions | final response | implementation commit `4d7cf1a4`; follow-up lint/report commit pending |
| report.md implementation ledger | provider runtime/assets/tests plus dogfooding workspace parity | PR body / final response | S300-S320 local implementation verified; PR #245 re-push / re-observation pending |

## 遭遇した問題と解決 (任意)
- 問題: Issue Planning guidance が、substantive draft requirement を `reason_code=requirement-scaffold` と表示した。
  - 解決: `assurance classify` と provider/runtime inspection で原因を切り分け、manual test finding として discussion artifact に記録し、S05/tc-009/tc-010 に検証対象として組み込んだ。
- 問題: `uvx --from . spec-dock update .` 成功後も dogfooding runtime が古い guidance 判定を返した。
  - 解決: provider 正本と dogfooding runtime の差分を確認し、dogfooding parity を確保してから guidance / validate を再実行した。根本原因は scope expansion として discussion artifact に残した。

## 学んだこと (任意)
- guidance のユーザー向け reason code は safety gate としては機能していても、agent が次の作業を判断する signal としては draft/scaffold/review-needed を分ける必要がある。

## 今後の推奨事項 (任意)
- provider source と dogfooding runtime の両方で guidance output を比較し、`assurance classify` と矛盾しない状態表現に揃える。
- `spec-dock update .` が dogfooding runtime を更新しないケースは、別途 update path の follow-up として調査候補にする。

## 省略/例外メモ (必須)
- ローカル実装・自動テスト・dogfooding manual test は一部実施済み。PR #245 の Codex review trigger は実施済みで、script-local instruction metadata 付きコメント投稿は成功した。初回 PR 観測は Provider CI の静的解析 failure で止まり、その後 S300-S320 wait repair を追加実装したため、再 push / 修正版 wait script による再観測を実施する。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
