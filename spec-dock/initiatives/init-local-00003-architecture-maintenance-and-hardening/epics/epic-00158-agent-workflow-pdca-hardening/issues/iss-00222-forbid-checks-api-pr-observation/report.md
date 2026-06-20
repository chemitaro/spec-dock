---
種別: 実装報告書（Issue）
ID: "iss-00222"
タイトル: "Forbid Checks API In PR Observation"
関連GitHub: ["#222"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00222 Forbid Checks API In PR Observation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | 未解決 / 解決済み / 置換済み（open / resolved / superseded） | 解釈 / 範囲 / 実装 / 互換性 / テスト戦略 / 運用 / 逸脱 / フォローアップ（interpretation / scope / implementation / compatibility / test-strategy / operation / deviation / follow-up） | 起票元（orchestrator / reviewer / worker source） | 計画の曖昧さ / 実装制約 / レビュー指摘 / 発見リスク（plan ambiguity / implementation constraint / reviewer finding / discovered risk） | 選択肢 A; 選択肢 B; 対応なし（option A; option B; no action） | ... | ... | 採用 / 却下 / design 昇格 / ADR 昇格 / plan 昇格 / follow-up 化 / 延期 / 対応なし / 置換済み（applied / rejected / promoted_to_design / promoted_to_adr / promoted_to_plan / converted_to_followup / deferred / no_action / superseded） | `path` / コマンド / reviewer 指摘 / discussion（path / command / reviewer finding / discussion） | 対象 artifact / issue / discussion / 置換先 entry / 理由付き対応なし（target artifact / issue / discussion / replacement entry / none with reason） |
| D-S02-001 | resolved | compatibility | dev-coder / orchestrator | S02 で `zero_actions_runs_non_success` を導入すると、S03 の wait/snapshot consumer がまだ legacy `zero_checks_s03_non_success` を見ているため挙動が変わる | A: legacy marker を即削除; B: legacy marker のみ維持; C: new marker と legacy compatibility marker を併記 | C を採用し、S02 では Actions-only semantics を `zero_actions_runs_non_success` で示しつつ、S03 migration まで `zero_checks_s03_non_success` を互換 marker として残す | S02 は snapshot/wait consumer 変更禁止。code-reviewer が temporary marker を S02 契約上許容と判定した | applied | `pr_observation_checks.py`; S02 worker ledger note; code-reviewer `019ee5e8-a0e4-75b2-8793-0f5404296571` pass | S03 で wait/snapshot consumption を Actions summary / new marker へ移行し、可能なら legacy marker 削除を再評価する |
| D-S03-001 | resolved | compatibility | dev-coder / orchestrator / code-reviewer | S03 で wait/snapshot consumer が Actions-only source policy を理解するため、旧 `zero_checks_s03_non_success` をどのように扱うかを確定する必要があった | A: legacy marker を blocking limitation として扱い続ける; B: source_policy が `github_actions_only` の場合は `zero_actions_runs_non_success` を authoritative とし legacy marker を互換ノイズとして無視する | B を採用。Actions-only payload では new marker と Actions summary/source_policy を decision/fingerprint/progress の source of truth とし、legacy marker は互換 duplicate として blocking decision へ使わない | user clarification は語彙禁止ではなく API surface 禁止。S02 marker 併記は downstream migration のためで、S03 で新 marker へ移行するのが計画通り。code-reviewer も compatibility bridge として acceptable と判定した | applied | `pr_observation_wait.py`; `pr_observation_snapshot.py`; `test_issue_222_s03_*`; code-reviewer `019ee5f7-0c53-7660-8111-a402a8c5b9b1` finding/assessment | legacy marker の collector emission 削除は S03 scope では必須にせず、S90 docs/compatibility wording と final review で再評価する |
| D-S05-001 | resolved | implementation | dev-coder / orchestrator | Doctor capability probe は `--github-extended` で Actions/comments を扱っていたが、S05 では PR observation repair に必要な read surfaces を Checks/status 系なしで診断対象にする必要があった | A: Actions/comments を extended のまま残す; B: PR observation に必要な Actions/review/comment read surfaces を core probe に移す; C: global doctor schema を再設計する | B を採用。PR observation repair の core probe は repo metadata、pull request、Actions、issue comments、PR reviews、PR review comments の read surfaces とする | AC-006 は Checks/statuses/status rollup permissions を repair requirement にしないことを要求している。PR observation の実動作は Actions と review/comment read に依存するため、extended 扱いのままだと通常 doctor で必要診断が欠落する | applied | `github_capability_cli.py`; `doctor.py`; `contracts.py`; `tests/cli_runtime/test_runtime_doctor_s04.py`; `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> `43 passed` | `--github-extended` は互換引数として残るが S05 path では追加 probe を持たない。非 PR-observation extended group が必要なら別 issue/design で扱う |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） / 部分採用（`partially_adopted`） / 棄却（`rejected`） / 延期（`deferred`） / stale（`stale`） / blocked（`blocked`） | サブエージェント（`sub-agent`） / レビュアー（`reviewer`） / 議論（`discussion`） / コマンド（`command`） / 調査（`research`） | 成果物（`artifact`） / Issue（`issue`） / フォローアップ（`follow-up`） | ... | `path` / コマンド / レビュアー指摘 | なし / フォローアップ（`follow-up`） / 再レビュー（`re-review`） / 再訪条件（`revisit condition`） |
| EAL-CLAR-001 | `adopted` | 調査（`research`） / 正式質問（`interview`） / ユーザー回答（`user answer`） | `requirement.md` / `design.md` / `plan.md` | Checks API / status rollup 禁止に加え、legacy commit statuses も Actions-only 制約に含める方針がユーザー回答で確定した | `discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md`; `discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md` | Deep Consultant 分析を統合し、canonical docs へ反映する |
| EAL-DEEP-001 | `adopted` | Deep Consultant（`sub-agent`） / 調査（`research`） / 議論（`discussion`） | `requirement.md` / `design.md` | Checks API / status rollup / commit statuses を完全排除しても PR observation は Actions-centered monitoring として維持可能。ただし GitHub UI の all checks / external checks 再現は失う | `discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md`; `discussions/20260620t141319z-disc-feasibility-without-checks-api.md` | requirement/design へ Actions-only scope と intentional loss を反映する |
| EAL-DEEP-002 | `adopted` | Deep Consultant（`sub-agent`） / 議論（`discussion`） | `design.md` / `plan.md` | CI collector は Actions workflow runs/jobs のみに縮小し、run-level conclusion を primary、jobs を diagnostic detail とする。public entrypoint は維持可能 | `discussions/20260620t141320z-disc-actions-only-collector-design.md` | design/plan へ collector structure、forbidden call guard、JSON compatibility 判断を反映する |
| EAL-DEEP-003 | `adopted` | Deep Consultant（`sub-agent`） / 議論（`discussion`） | `requirement.md` / `design.md` / `plan.md` | zero Actions runs、Actions API unavailable、external/non-Actions checks は pass に倒さず unknown / human gate / out-of-scope として扱う | `discussions/20260620t141317z-disc-observation-semantics-and-losses.md` | edge cases と wording constraints を canonical docs へ反映する |
| EAL-DEEP-004 | `adopted` | Deep Consultant（`sub-agent`） / 議論（`discussion`） | `design.md` / `plan.md` | doctor capability、tests、skill/docs migration も Actions-only contract に同期する必要がある | `discussions/20260620t141318z-disc-doctor-tests-docs-migration.md` | doctor/test/doc migration を implementation steps と closure index へ反映する |
| EAL-ADR-001 | `adopted` | ADR（`adr`） / ユーザー依頼（`user request`） | `requirement.md` / `design.md` / `plan.md` | Checks API / statusCheckRollup / gh pr checks / legacy commit statuses を PR observation CI 判定から除外する意思決定を長期参照用 ADR として固定した | `discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md` | requirement/design/plan authoring 時に source decision として反映する |
| EAL-CLAR-002 | `adopted` | 正式質問（`interview`） / ユーザー回答（`user answer`） | `requirement.md` / `design.md` / `plan.md` | `checks` という語や互換名の禁止ではなく、GitHub Checks API / status rollup surface の利用禁止であることが確定した | `discussions/20260620t144016z-interview-checks-named-compatibility-boundary.md` | compatibility naming を許容しつつ forbidden API guard を canonical docs へ反映する |
| EAL-DESIGN-DRAFT-001 | `adopted` | system-architect（`sub-agent`） / delegated draft | `design.md` / `report.md` | Actions-only PR observation の architecture、payload compatibility、review boundary、doctor migration、test strategy が requirement/ADR と整合していたため canonical design に統合した | `discussions/20260620t145235z-draft-design-actions-only-pr-observation-design-draft.md` | fresh spec-reviewer で canonical `design.md` を review する |
| EAL-PLAN-DRAFT-001 | `adopted` | implementation-planner（`sub-agent`） / delegated draft | `plan.md` / `report.md` | Actions-only collector、downstream wait/snapshot、review/comment regression、doctor migration、docs wording、final gates を dependency order と closure evidence に分解しており、approved requirement/design/ADR と整合していたため canonical plan に統合した | `discussions/20260620t151203z-draft-plan-actions-only-pr-observation-plan-draft.md` | fresh spec-reviewer で canonical `plan.md` を review する |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ... | ... | なし / 低 / 中 / 高（none / low / medium / high） | 合格 / 不合格 / blocked（pass / fail / blocked） |
| OAL-CLAR-001 | Issue #222 とユーザー回答は forbidden API surface の完全排除を主要目的にしている | PR observation の監視価値維持は Actions-centered monitoring として実現する | 低: external/non-Actions checks 再現を目的化すると forbidden surface 排除が崩れるため、loss model を明示した | provisional: requirement/design authoring 前の調査として整合 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| 要件 / 設計 / 計画（requirement / design / plan） | 文書 / コード / discussions / 外部証跡（docs / code / discussions / external evidence） | なし / `discussions/...`（none / `discussions/...`） | 採用 / 部分採用 / 棄却 / 延期 / なし（adopted / partially_adopted / rejected / deferred / none） | 合格 / 不合格 / 利用不可 / 拒否 / waiver / provisional（passed / failed / unavailable / denied / waived / provisional） | はい / いいえ（yes / no） | 昇格 / clarification へ戻す / 再レビュー / フォローアップ（promote / return to clarification / re-review / follow-up） |
| requirement | GitHub issue `#222`; active issue scaffold; parent Initiative/Epic docs; clarification workflow docs; provider-side and dogfooding PR observation skill/scripts; doctor capability probe; focused tests; GitHub REST API docs; Deep Consultant 3視点; accepted ADR | `discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md` answered: commit statuses も廃止し Actions workflow runs/jobs のみ許可。`discussions/20260620t144016z-interview-checks-named-compatibility-boundary.md` answered: `checks` 語の禁止ではなく GitHub Checks API 利用禁止 | adopted | passed: spec-reviewer `019ee582-049a-7402-866f-1eac8d3ee2c7` returned `review_status: pass` | no | design phase へ promotion。system-architect delegated draft を作成して canonical `design.md` へ統合する |
| design | `requirement.md` reviewer pass; accepted ADR; system-architect delegated draft; provider-side PR observation scripts; runtime doctor capability code; merge-preparer skill/template; focused tests | なし。Requirement gap / user-intent blocker は残っていない。review findings により merge-preparer wording surface、Delegated Draft Evidence row、draft frontmatter authority boundary を整合した | adopted | passed: spec-reviewer `019ee593-2508-71f3-9096-799956f2b4b9` returned `review_status: pass` after fixes | no | plan phase へ promotion。implementation-planner delegated draft を作成して canonical `plan.md` へ統合する |
| plan | `design.md` reviewer pass; accepted ADR; implementation-planner delegated draft; issue plan authoring docs; closure index; delegation contracts; concrete test cases | なし。Design gap / user-intent blocker は残っていない。`checks` 語は禁止しないが forbidden GitHub Checks API / status rollup / commit statuses surfaces は step contracts と tests で閉じる | adopted | passed: spec-reviewer `019ee5a0-eb91-7e73-b65e-9b727aeaaaa2` returned `review_status: pass`; P2 S03/S04 test path concreteness finding was addressed and re-reviewed as pass | no | implementation handoff ready |

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
| system-architect | iss-00222 | `discussions/20260620t145235z-draft-design-actions-only-pr-observation-design-draft.md` | `requirement.md`; accepted ADR; compatibility interview; Actions-only research/discussions; provider-side PR observation scripts; runtime doctor capability code; focused tests | `design.md`; `report.md` | adopted | `design.md`; `report.md` | passed | canonical `design.md` に統合済み | なし | なし（none） | design reviewer passed after provenance rows were reconciled | design phase promotion evidence として採用 |
| implementation-planner | iss-00222 | `discussions/20260620t151203z-draft-plan-actions-only-pr-observation-plan-draft.md` | `requirement.md`; `design.md`; accepted ADR; compatibility interview; `phase_plan_issue.md`; `authoring/issue-plan.md`; `workflow_issue.md` | `plan.md`; `report.md` | adopted | `plan.md`; `report.md` | passed | canonical `plan.md` に統合済み | なし | なし（none） | plan reviewer passed after S03/S04 path concreteness fix | plan phase promotion evidence として採用 |

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
- 実装は未着手。Issue 222 の要件定義・設計に向けて、Checks API / `statusCheckRollup` / commit statuses / Actions workflow runs/jobs の現行利用箇所を調査し、research と interview を作成した。
- ユーザー回答により legacy commit statuses も廃止対象として採用した。
- Deep Consultant 3視点を使い、Actions-only PR observation の可否、collector design、observability loss、doctor/tests/docs migration を 5つの Markdown artifact に統合した。
- ユーザー依頼により、Checks API を利用しない意思決定を accepted ADR として作成した。
- ユーザー回答により、`checks` という語や互換名の削除は要求せず、GitHub Checks API / status rollup surface の利用禁止として要件化した。
- `requirement.md` を作成し、fresh `spec-reviewer` で pass を得た。
- system-architect delegated design draft を採用し、canonical `design.md` を作成した。
- implementation-planner delegated plan draft を採用し、canonical `plan.md` を作成した。
- `plan.md` は fresh `spec-reviewer` で pass を得た。P2 の S03/S04 test path 具体化指摘は反映し、再レビューで pass を得た。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-20 14:00 - 14:10）

#### 対象
- Step: clarification / source-grounded research
- AC/EC: 未作成。Requirement / design authoring 前の調査。
- 計画上の出典（Planned source）:
  - GitHub issue `#222`
  - `spec-dock-clarification` source-grounded grill loop
  - closure ids: N/A

#### 実施内容
- Active issue を `iss-00222` に設定した。
- GitHub issue `#222` の本文、active issue scaffold、parent Initiative/Epic docs、clarification workflow docs、PR observation 実装、doctor capability probe、関連テストを調査した。
- Checks API / `statusCheckRollup` の禁止は source-grounded に確定した。
- Legacy commit statuses を Actions-only 制約に含めるかが要件・設計・テストを分岐させるため、正式質問を作成した。
- ユーザー回答により、legacy commit statuses も廃止し Actions workflow runs/jobs だけを許可する方針を採用した。
- Deep Consultant を 3視点で並列利用し、機能維持可否、技術方式、リスク/テスト/doctor migration を分析した。
- 分析結果を `research-actions-only-pr-observation-viability-research` と 4つの観点別 discussion に統合した。
- ユーザー依頼により、Checks API を利用しない意思決定を accepted ADR として作成した。
- 追加のユーザー回答を `checks` named compatibility boundary として採用し、語彙禁止ではなく API 利用禁止であることを確定した。
- `requirement.md` を作成し、spec-reviewer `019ee582-049a-7402-866f-1eac8d3ee2c7` が `review_status: pass` を返した。
- system-architect `019ee583-64b5-7ec1-b1a5-0a50942e7fff` が `discussions/20260620t145235z-draft-design-actions-only-pr-observation-design-draft.md` を作成し、内容を canonical `design.md` へ統合した。
- design spec-reviewer `019ee589-712f-7933-88d6-11bb82e54ad7` が merge-preparer wording scope 欠落を P1 finding として返したため、`design.md` に `github-pr-merge-preparer` skill/template の変更対象を追加した。
- design spec-reviewer `019ee58c-60a3-7bd0-a332-9585da1012a8` が delegated draft provenance mismatch を P1 finding として返したため、draft frontmatter を `adoption_status: adopted` / `diff_guard_result: passed` / `reflected_to` 更新済みに整合した。
- design spec-reviewer `019ee58f-28dc-7ab2-be2d-e0684e85e0f3` が Delegated Draft Evidence row mismatch を P1 finding として返したため、report の Delegated Draft Evidence table を実際の system-architect draft 採用状態に整合した。
- design spec-reviewer `019ee591-375a-7462-8c5e-7eca9f7226dd` が draft self-adoption claim を P1 finding として返したため、draft frontmatter は `adoption_status: unreviewed` / `reflected_to: []` に戻し、report の EAL / Delegated Draft Evidence が採用判断を持つ形に修正した。
- design spec-reviewer `019ee593-2508-71f3-9096-799956f2b4b9` が `review_status: pass` を返した。
- implementation-planner `019ee596-0400-75a2-913d-7a966cbac688` が `discussions/20260620t151203z-draft-plan-actions-only-pr-observation-plan-draft.md` を作成し、内容を canonical `plan.md` へ統合した。
- plan spec-reviewer `019ee5a0-eb91-7e73-b65e-9b727aeaaaa2` が P2 finding とともに `review_status: pass` を返した。S03/S04 の test allowed paths を `tests/unit/infra/test_init_update.py` と bounded `tests/unit/infra/` discovery に具体化し、同 reviewer の再確認で `review_status: pass` を得た。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock active set --id iss-00222 --no-checkout --github
# spec-dock: ok (active set) target=iss-00222 initiative=init-local-00003 epic=epic-00158 issue=iss-00222

gh issue view 222 --json number,title,body,state,url,labels,comments
# Issue 222 body confirmed Checks API / statusCheckRollup forbidden and Actions workflow runs/jobs as CI source of truth.

rg -n "statusCheckRollup|check-runs|gh pr checks|ci_coverage_limited_to_github_actions|mergeStateStatus" ...
# Found provider-side and dogfooding PR observation scripts, doctor capability probe, and focused tests that still rely on supplemental Checks/status rollup behavior.

./spec-dock/scripts/spec-dock new doc --type research --title "Actions Only PR Observation Viability Research" --parent iss-00222
./spec-dock/scripts/spec-dock new doc --type disc --title "Feasibility Without Checks API" --parent iss-00222
./spec-dock/scripts/spec-dock new doc --type disc --title "Actions Only Collector Design" --parent iss-00222
./spec-dock/scripts/spec-dock new doc --type disc --title "Observation Semantics And Losses" --parent iss-00222
./spec-dock/scripts/spec-dock new doc --type disc --title "Doctor Tests Docs Migration" --parent iss-00222
# Created issue-local research/discussion artifacts for Deep Consultant synthesis.

./spec-dock/scripts/spec-dock new doc adr --issue iss-00222 --title "Forbid Checks Api In Pr Observation" --slug forbid-checks-api-in-pr-observation
# Created discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | 既存 collector に `gh pr view --json mergeStateStatus,statusCheckRollup`、`/check-runs`、`/status` 呼び出しがあり、広め verification lane は旧 rollup/status 前提で `25 failed, 58 passed, 394 deselected` だった | source inspection; `uv run pytest tests/unit/infra/test_init_update.py -k "observation or checks or github_pr"` before stale-test cleanup | pass | forbidden surface と stale expectations を再現 |
| S01 | 緑フェーズ（Green） | cl-001 / cl-011 | collector は forbidden supplemental API を呼ばず、S01 guard と広め lane が pass | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s01"` -> `2 passed, 475 deselected`; `uv run pytest tests/unit/infra/test_init_update.py -k "observation or checks or github_pr"` -> `83 passed, 394 deselected` | pass | static guard は `checks` token ではなく forbidden API surface を対象にする |
| S01 | リファクタリング（Refactor） | guardrail satisfied | unused import / stale supplemental limitation expectations を整理。実装 source は provider-side collector と focused tests のみ | `git diff --check -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py tests/unit/infra/test_init_update.py` -> pass | pass | full file test は `473 passed, 4 failed`; failure は generated `__pycache__` inventory と dogfooding snapshot/parity。`__pycache__` は削除済み、dogfooding parity は後続 mirror/snapshot synchronization で扱う |
| S02 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | S02 edge fixtures were missing before implementation; source inspection showed dead legacy check/status decision branches and no explicit source policy marker | source inspection; worker precheck `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222 or actions or observation or checks"` -> existing lane pass but without S02-specific coverage | pass | missing coverage was closed by new S02 tests |
| S02 | 緑フェーズ（Green） | cl-002 through cl-006 | Actions-only source policy marker and status classification were implemented; zero/unavailable/job-unavailable cases covered | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s02"` -> `5 passed, 477 deselected`; `uv run pytest tests/unit/infra/test_init_update.py -k "actions or observation or checks"` -> `123 passed, 359 deselected` | pass | static forbidden pattern scan returned no matches |
| S02 | リファクタリング（Refactor） | guardrail satisfied | dead check/status/status-rollup classification helpers and fallback branches removed; compatibility fields retained empty | `git diff --check -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py tests/unit/infra/test_init_update.py` -> pass | pass | no broad rename of compatibility fields |
| S03 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | S03-specific wait/snapshot consumer coverage was absent before implementation; initial code-reviewer found a missed edge where `jobs_summary.total == 0` could hide nonzero workflow run counts in progress output | source inspection; code-reviewer `019ee5f7-0c53-7660-8111-a402a8c5b9b1` fail finding; pre-fix S03 lane had only `3 passed` and did not cover jobs-empty/workflow-nonzero progress | pass | missing coverage was closed by follow-up dev-coder fix |
| S03 | 緑フェーズ（Green） | cl-007 | snapshot/wait fingerprint, progress, and zero-Actions decision consume Actions summary/source_policy and ignore contradictory legacy check/status fields under Actions-only policy | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s03"` -> `4 passed, 482 deselected`; `uv run pytest tests/unit/infra/test_init_update.py -k "observation_wait or observation_snapshot"` -> `38 passed, 448 deselected` | pass | includes jobs-summary-empty/workflow-runs-nonzero regression; legacy marker treated as compatibility duplicate |
| S03 | リファクタリング（Refactor） | guardrail satisfied | wait progress prefers job counts only when useful, otherwise Actions workflow counts; snapshot fingerprint includes source_policy and Actions summaries | `git diff --check -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py tests/unit/infra/test_init_update.py` -> pass | pass | no legacy Checks/status fallback reintroduced |
| S04 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | S04/cl-008 dedicated regression was absent before implementation | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s04"` before test addition -> `486 deselected / 0 selected`, exit 5 | pass | test-only regression was added; no implementation change required |
| S04 | 緑フェーズ（Green） | cl-008 | review snapshot preserves issue comments, PR reviews, review comments, requested reviewers/teams, reviewThreads, and reviewDecision while forbidden CI surfaces are blocked | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s04"` -> `1 passed, 486 deselected`; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_review_snapshot"` -> `5 passed, 482 deselected` | pass | allowed GraphQL reviewThreads/reviewDecision is retained; `statusCheckRollup`, `/check-runs`, `/status`, and `pr checks` fail-fast in fixture |
| S04 | リファクタリング（Refactor） | guardrail satisfied | S04 was test-only; no runtime refactor needed | `git diff --check -- tests/unit/infra/test_init_update.py` -> pass | pass | code-reviewer accepted S04 as test-only closure |
| S05 | 赤フェーズ（Red） | red-required | S05 expectation failed against old doctor fallback/probe model because it still used `check_runs_read`, `commit_statuses_read`, and `status_check_rollup_read` as PR observation capabilities | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py -k "issue_222_s05 or without_github_target"` after S05 tests/pre-change expectation -> `2 failed, 1 passed` | pass | failure reproduced old Checks/status repair requirement |
| S05 | 緑フェーズ（Green） | cl-009 | doctor PR observation probe uses Actions and review/comment read capabilities, not Checks/status/status rollup | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py -k "issue_222_s05 or without_github_target"` -> `3 passed, 40 deselected`; `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> `43 passed` | pass | missing Actions read remains diagnostic; review/comment read remains diagnostic |
| S05 | リファクタリング（Refactor） | guardrail satisfied | target/gateway unavailable fallback capability changed from `check_runs_read` to `actions_read`; legacy capability literals retained only for classification compatibility | `git diff --check -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py tests/cli_runtime/test_runtime_doctor_s04.py` -> pass | pass | no GitHub write capability added |
| S90 | docs inspection | cl-010 / cl-011 | shipped skill/docs/template wording now states Actions workflow runs/jobs are the only CI source, forbidden API surfaces are not used, compatibility `checks` names are not a word ban, and external/non-Actions checks are intentionally unobserved | static scan; docs diff inspection; spec-reviewer `019ee61a-44c2-70d2-ac39-33be5053a45d` pass | pass | remaining forbidden-surface terms appear only in “does not use / intentionally not used” explanations |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | stale rollup/status/check-runs tests still expected forbidden supplemental API evidence | code-reviewer / verification | updated tests to assert Actions-only forbidden collection policy, non-call behavior, or Actions evidence; no plan amendment | cl-001 / cl-011 | no | code-reviewer fail then pass; `83 passed, 394 deselected` |
| S01 | full `tests/unit/infra/test_init_update.py` still reports dogfooding snapshot / provider mirror parity failures after provider asset change and issue import | verification | recorded for later sync/mirror step; not S01 blocker per code-reviewer because outside S01 allowed-path contract | follow-up parity risk | no | full file `473 passed, 4 failed`; code-reviewer pass allowed deferral |
| S02 | S03 consumer still depends on `zero_checks_s03_non_success` | dev-coder / verification | kept compatibility marker alongside new `zero_actions_runs_non_success`; recorded D-S02-001 | cl-004 | no | code-reviewer pass accepted temporary compatibility marker |
| S03 | wait progress could select empty `jobs_summary` counts even when workflow run counts exist | code-reviewer | updated `ci_progress_counts()` to use jobs summary only when useful and otherwise use workflow run counts without legacy fallback for Actions-only payloads | cl-007 | no | `issue_222_s03` -> `4 passed`; `observation_wait or observation_snapshot` -> `38 passed` |
| S04 | review/comment/thread preservation lacked issue-specific regression under forbidden CI guard | dev-coder / verification | added S04 fake-gh test that blocks CI surfaces but allows review GraphQL and asserts review payload preservation | cl-008 | no | `issue_222_s04` -> `1 passed`; `pr_review_snapshot` -> `5 passed`; code-reviewer pass |
| S05 | doctor core probe still treated Checks/status/status rollup permissions as PR observation repair requirements | dev-coder / verification | migrated PR observation capability probe to Actions and review/comment read surfaces; updated fallback representative capability to `actions_read` | cl-009 | no | focused S05 lane -> `3 passed`; full doctor S04 lane -> `43 passed` |
| S90 | shipped guidance still described supplemental Checks/status/rollup coverage and merge-preparer required-check coverage too broadly | doc-writer / inspection | updated observation and merge-preparer guidance to Actions-only CI, compatibility naming, intentional external/non-Actions loss, and human confirmation wording | cl-010, cl-011 | no | static scan and spec-reviewer pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | cl-001, cl-011 | cl-001: forbidden API calls are not executed and fake-gh detects them; cl-011: compatibility names may remain without word-ban behavior | provider collector has no forbidden decision call pattern; `test_issue_222_s01_pr_observation_ci_collector_forbids_checks_api_surfaces`; `test_issue_222_s01_static_guard_targets_forbidden_ci_surfaces_not_checks_name`; broad lane pass | pass | S02-S05/S90/S99 remain unlocked only after this committed step |
| S02 | cl-002, cl-003, cl-004, cl-005, cl-006 | Actions workflow runs/jobs alone determine CI state; zero/unavailable Actions evidence never becomes pass through legacy fallback | S02 focused tests and broad lane pass; code-reviewer pass | pass | S03 migration remains separate |
| S03 | cl-007 | snapshot/wait progress and fingerprint use Actions summary, not legacy check fields | S03 focused tests cover empty legacy fields, contradictory legacy fields, snapshot fingerprint stability, and jobs-summary-empty/workflow-runs-nonzero progress; broad wait/snapshot lane pass | pass | code-reviewer initial P2 was fixed before closure |
| S04 | cl-008 | issue comments, PR reviews, review comments, reviewThreads, reviewDecision, and review requests remain present while CI forbidden surfaces are blocked | `test_issue_222_s04_pr_review_snapshot_preserves_review_payload_without_ci_surfaces`; existing `pr_review_snapshot` lane; code-reviewer pass | pass | no runtime change required |
| S05 | cl-009 | doctor does not require Checks/statuses/status rollup permissions for PR observation repair | S05 focused tests, full `tests/cli_runtime/test_runtime_doctor_s04.py`, and code inspection show no Checks/status/status rollup probe in PR observation capability gateway | pass | code-reviewer first pass failed only for missing report evidence; evidence now recorded |
| S90 | cl-010, cl-011 | shipped guidance says API/surface is forbidden, not the word `checks`; external/non-Actions checks are intentionally unobserved; merge-preparer avoids full GitHub UI check coverage claims | `github-pr-observation/SKILL.md`; `fetch_pr_checks_snapshot.sh`; `github-pr-merge-preparer/SKILL.md`; `pr-repair-batch.md`; spec-reviewer pass | pass | compatibility names retained with explicit Actions-only meaning |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-001 | S01 | yes | red-required | source inspection showed `statusCheckRollup`, `/check-runs`, commit status calls in collector | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s01"`; `uv run pytest tests/unit/infra/test_init_update.py -k "observation or checks or github_pr"` | pass | fake-gh fails on forbidden surface and collector uses Actions API only |
| cl-011 | S01 | yes | inspect-only | compatibility names such as `fetch_pr_checks_snapshot.sh` remain intentionally | static test `test_issue_222_s01_static_guard_targets_forbidden_ci_surfaces_not_checks_name`; provider collector `rg` forbidden patterns -> no matches | pass | no word-ban on `checks` token |
| cl-002 | S02 | yes | red-required | explicit success source-policy coverage absent before S02 | `test_issue_222_s02_actions_success_passes_with_source_policy_marker` | pass | source policy marker is present top-level and under `ci` |
| cl-003 | S02 | yes | red-required | non-success Actions state coverage incomplete before S02 | `test_issue_222_s02_actions_non_success_states_classify_from_actions_only` | pass | failure/cancelled/timed_out/queued/in_progress/pending/unknown classified from Actions |
| cl-004 | S02 | yes | red-required | zero Actions needed non-pass/no-fallback evidence | `test_issue_222_s02_zero_actions_runs_never_pass_and_do_not_fallback` | pass | emits `zero_actions_runs_non_success` and temporary S03 compatibility marker |
| cl-005 | S02 | yes | red-required | Actions unavailable needed no-fallback evidence | `test_issue_222_s02_actions_unavailable_is_unknown_without_fallback` | pass | limitation is `actions_read`; no forbidden fallback |
| cl-006 | S02 | yes | red-required | failed run with jobs unavailable needed run-level preservation | `test_issue_222_s02_failed_run_stays_failed_when_jobs_api_unavailable` | pass | failed run stays failed and jobs limitation is recorded |
| cl-007 | S03 | yes | red-required | downstream wait/snapshot consumer did not have Actions-only source_policy/fingerprint/progress coverage before S03 | `test_issue_222_s03_wait_uses_actions_summary_with_empty_legacy_fields`; `test_issue_222_s03_wait_fingerprint_ignores_contradictory_legacy_ci_fields`; `test_issue_222_s03_snapshot_fingerprint_uses_actions_summary_not_legacy_fields`; `test_issue_222_s03_wait_uses_workflow_counts_when_jobs_summary_empty` | pass | Actions-only payload ignores legacy check/status fields and uses workflow counts when jobs summary is empty |
| cl-008 | S04 | yes | red-required | S04-specific preservation fixture was missing before implementation | `test_issue_222_s04_pr_review_snapshot_preserves_review_payload_without_ci_surfaces`; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_review_snapshot"` | pass | review GraphQL is allowed and preserved; forbidden CI rollup/status surfaces are blocked |
| cl-009 | S05 | yes | red-required | old fallback/core probe used Checks/status/status rollup representative capabilities | `test_issue_222_s05_doctor_reports_actions_and_review_capabilities_without_checks_requirements`; `test_issue_222_s05_github_capability_cli_probes_actions_and_review_surfaces_without_checks_api`; `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` | pass | missing Actions read and review/comment read remain diagnostic without Checks/status repair requirements |
| cl-010 | S90 | yes | inspect-only | guidance previously mentioned supplemental Checks/status/rollup and complete required-check style wording | docs diff inspection; static scan; spec-reviewer pass | pass | Actions-only guidance and external/non-Actions unobserved residual risk are explicit |
| cl-011 | S90 | yes | inspect-only | compatibility `checks` names remained and required clarification to avoid word-ban/API-ban confusion | docs diff inspection; `fetch_pr_checks_snapshot.sh` usage wording; spec-reviewer pass | pass | compatibility names remain but do not imply GitHub Checks API usage |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-001 | S01 | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s01"` -> `2 passed`; broad lane -> `83 passed` | pass | forbidden API calls removed from runtime path |
| cl-011 | S01 | static guard plus code-reviewer pass | pass | compatibility names preserved; `checks` word itself not banned |
| cl-002 | S02 | S02 focused test | pass | Actions success passes |
| cl-003 | S02 | S02 focused test | pass | Actions non-success states do not pass incorrectly |
| cl-004 | S02 | S02 focused test | pass | zero Actions runs non-pass |
| cl-005 | S02 | S02 focused test | pass | Actions unavailable unknown/no fallback |
| cl-006 | S02 | S02 focused test | pass | failed run stays failed when jobs unavailable |
| cl-007 | S03 | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s03"` -> `4 passed`; `uv run pytest tests/unit/infra/test_init_update.py -k "observation_wait or observation_snapshot"` -> `38 passed` | pass | snapshot/wait consumption migrated to Actions summary/source policy |
| cl-008 | S04 | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s04"` -> `1 passed`; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_review_snapshot"` -> `5 passed` | pass | review payload preserved under forbidden CI guard |
| cl-009 | S05 | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py -k "issue_222_s05 or without_github_target"` -> `3 passed`; `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> `43 passed` | pass | doctor capability probe migrated to Actions/review/comment read |
| cl-010 | S90 | static scan and spec-reviewer pass | pass | no mergeability overclaim; external/non-Actions checks remain human-confirmed residual risk when relevant |
| cl-011 | S90 | static scan and spec-reviewer pass | pass | `checks` compatibility names are documented as historical names, not API usage |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| changed | cl-001 | legacy rollup/status tests | cl-001 | forbidden supplemental API is no longer observable; stale tests now assert non-call / forbidden policy / Actions evidence | no | yes; code-reviewer re-review passed |
| added | cl-002..cl-006 | `test_issue_222_s02_*` | cl-002..cl-006 | S02 needed explicit Actions-only classification fixtures | no | yes; code-reviewer passed |
| added | cl-007 | `test_issue_222_s03_*` | cl-007 | S03 needed downstream wait/snapshot fixtures for Actions-only payloads, contradictory legacy fields, and jobs-summary-empty progress | no | yes; code-reviewer re-review required |
| added | cl-008 | `test_issue_222_s04_pr_review_snapshot_preserves_review_payload_without_ci_surfaces` | cl-008 | review preservation needed issue-specific regression under forbidden CI surface guard | no | yes; code-reviewer passed |
| changed | cl-009 | doctor capability core probe | cl-009 | PR observation repair no longer depends on Checks/status/status rollup permissions; Actions and review/comment read surfaces are core diagnostics | no | yes; code-reviewer re-review required |
| changed | cl-010, cl-011 | shipped skill/docs wording | cl-010, cl-011 | docs needed to align with Actions-only implementation and user clarification that this is not a `checks` word ban | no | yes; spec-reviewer passed |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/1fd6/spec-dock` | iss-00222 | current session | dev-coder, doc-writer, code-reviewer, qa-reviewer, spec-reviewer | same repo, active issue, named role; no destructive action beyond approved cleanup; no scope expansion without report evidence | issue complete / session end / scope change / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped scaffold runtime and tests | dev-coder | forbidden CI surface guard and stale test cleanup | requirement/design/plan/ADR/interview | provider `pr_observation_checks.py`; `tests/unit/infra/test_init_update.py` | canonical docs/report by worker; dogfooding mirror as implementation source; review/comment collector; broad rename of `checks` compatibility names | focused and broad pytest; static forbidden pattern inspection; diff check | forbidden API must remain; fake-gh cannot detect forbidden calls; allowed paths insufficient | changed files, tests, closure evidence, ledger note, risks | pass |
| S02 | delegated | shipped scaffold runtime and tests | dev-coder | Actions-only CI classification | requirement/design/plan/ADR/interview; S01 commit evidence | provider `pr_observation_checks.py`; `tests/unit/infra/test_init_update.py` | docs/report by worker; dogfooding mirror; S03 snapshot/wait; S04 review collector; doctor/docs; forbidden API reintroduction | S02 focused and broad pytest; static forbidden pattern inspection; diff check | payload shape cannot support downstream consumers without broader design | changed files, tests, payload notes, ledger note, risks | pass |
| S03 | delegated | shipped scaffold runtime and tests | dev-coder | snapshot/wait compatibility and decision consumption | requirement/design/plan/ADR/interview; S02 commit evidence | provider `pr_observation_wait.py`; provider `pr_observation_snapshot.py`; `tests/unit/infra/test_init_update.py` | docs/report by worker; dogfooding mirror; review collector; doctor/docs; forbidden API reintroduction | S03 focused pytest; broad wait/snapshot pytest; diff check | downstream decision still depends on legacy Checks/status fields; progress/fingerprint cannot be stable from Actions-only payload | changed files, tests, compatibility note, risks | pass after follow-up |
| S04 | delegated | shipped scaffold regression tests | dev-coder | review/comment/thread preservation regression | requirement/design/plan; S01/S03 evidence | `tests/unit/infra/test_init_update.py`; `pr_review_snapshot.py` only if narrow bug found | runtime CI collector changes; docs/report by worker; removing reviewThreads/reviewDecision; treating all GraphQL as forbidden | S04 focused pytest; existing review snapshot lane; diff check | fixture cannot distinguish allowed review GraphQL from forbidden CI rollup | changed files or approved no-op evidence, tests, review payload note | pass |
| S05 | delegated | shipped runtime doctor and tests | dev-coder | doctor/capability migration | requirement/design/plan; S02/S04 evidence | `github_capability_cli.py`; `doctor.py`; `contracts.py` if typing requires; `tests/cli_runtime/test_runtime_doctor_s04.py` | observation scripts; docs wording outside runtime doctor output; GitHub write capabilities; broad doctor architecture rewrite | focused S05 pytest; full runtime doctor S04 pytest; diff check | doctor architecture cannot represent Actions/read and review/comment/read separately | changed files, tests, diagnostic wording note, risks | pass |
| S90 | delegated | shipped skill/docs/templates | doc-writer | docs impact resolution and skill wording | requirement/design/plan/ADR; S02/S03/S05 evidence | shipped skill docs/templates listed in plan S90 | runtime Python/tests; canonical docs/report by worker; dogfooding mirror as source; public compatibility renames | docs diff inspection; static scan; diff check; spec-reviewer alignment | wording cannot be aligned without changing canonical requirement/design | changed docs files, scan result, residual docs risk | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | removed forbidden supplemental collector calls; added S01 fake-gh/static guard; updated stale rollup/status/check-runs tests to Actions-only forbidden policy | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s01"` -> pass; broad lane -> pass; diff check -> pass | pass: code-reviewer `019ee5aa-8402-7a13-8aca-1ce183fbe83a` after two follow-ups | dogfooding mirror/snapshot parity remains for later step | accepted |
| S02 | dev-coder | added `source_policy: github_actions_only`; removed dead legacy check/status/rollup decision branches; added S02 focused fixtures | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s02"` -> pass; `uv run pytest tests/unit/infra/test_init_update.py -k "actions or observation or checks"` -> pass; diff check -> pass | pass: code-reviewer `019ee5e8-a0e4-75b2-8793-0f5404296571` | temporary `zero_checks_s03_non_success` compatibility marker until S03 | accepted |
| S03 | dev-coder | migrated wait/snapshot fingerprint/progress/decision consumption to Actions summary/source_policy; fixed reviewer-found empty jobs summary progress regression | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s03"` -> pass; `uv run pytest tests/unit/infra/test_init_update.py -k "observation_wait or observation_snapshot"` -> pass; diff check -> pass | pending re-review | legacy marker still emitted by collector as compatibility duplicate | accepted pending reviewer |
| S04 | dev-coder | added test-only regression proving review snapshot keeps review/comment/thread evidence while CI surfaces are fail-fast forbidden | `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_222_s04"` -> pass; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_review_snapshot"` -> pass; diff check -> pass | pass: code-reviewer `019ee607-0af6-70e2-a0cc-59441644154e` | live GitHub schema drift is outside this fake-gh regression | accepted |
| S05 | dev-coder | migrated doctor capability probe from Checks/status/status rollup to Actions and review/comment read surfaces | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`; `tests/cli_runtime/test_runtime_doctor_s04.py` | `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py -k "issue_222_s05 or without_github_target"` -> pass; `uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py` -> pass; diff check -> pass | pending re-review | live GitHub API behavior not exercised by unit tests | accepted pending reviewer |
| S90 | doc-writer | updated shipped observation and merge-preparer guidance for Actions-only CI, compatibility naming, intentional external/non-Actions loss, and doctor capability wording | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` | static scan -> only intentional forbidden-surface mentions; diff check -> pass | pass: spec-reviewer `019ee61a-44c2-70d2-ac39-33be5053a45d` | external/non-Actions checks remain outside script responsibility | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | no | proceed to S01 commit | initial reviews found stale tests; final review returned `review_status: pass` |
| S02 | step reviewer | code-reviewer | fresh | passed | no | proceed to S02 commit | temporary zero-checks compatibility marker accepted for S02 |
| S03 | step reviewer | code-reviewer | fresh | failed -> pending re-review | no | fix findings before S03 commit | first review found missing report evidence and empty jobs-summary progress issue; report and code updated |
| S04 | step reviewer | code-reviewer | fresh | passed | no | proceed to S04 commit | S04 accepted as test-only regression |
| S05 | step reviewer | code-reviewer | fresh | passed | no | proceed to S05 commit | first review found missing S05 report evidence only; re-review `019ee614-1c88-7c01-a16a-1c2665ad1043` passed |
| S90 | docs/spec reviewer | spec-reviewer | fresh | passed | no | proceed to S90 commit | docs wording closes cl-010/cl-011 after report evidence update |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider collector, focused tests, S01 report evidence | `a49eee58` | `git status --short --branch` clean before S02 | N/A | N/A | N/A | N/A |
| S02 | committed | provider collector, focused tests, S02 report evidence | `9bb40938` | `git status --short --branch` clean before S03 | N/A | N/A | N/A | N/A |
| S03 | committed | provider wait/snapshot consumers, focused tests, S03 report evidence | `5afdfec6` | `git status --short --branch` clean before S04 | N/A | N/A | N/A | N/A |
| S04 | committed | focused review snapshot regression, S04 report evidence | `b05b55cc` | `git status --short --branch` clean before S05 | N/A | N/A | N/A | N/A |
| S05 | committed | runtime doctor/capability migration, focused tests, S05 report evidence | `c70bdbbf` | `git status --short --branch` clean before S90 | N/A | N/A | N/A | N/A |
| S90 | pending commit | shipped skill/docs/templates, S90 report evidence | pending S90 commit | post-commit clean check to be recorded before S99 | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### セッションログ（2026-06-20 HH:MM - HH:MM）

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
| shipped PR observation / merge-preparer skills and repair template | yes | doc-writer | Actions-only CI source, forbidden API surface, compatibility naming, external/non-Actions unobserved, and merge-prepared wording updated in shipped skill docs/templates | pass: spec-reviewer `019ee61a-44c2-70d2-ac39-33be5053a45d` |

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
