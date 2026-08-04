---
種別: 実装報告書（Issue）
ID: "iss-00354"
タイトル: "Define ChatGPT Context and Attachment Contract"
関連GitHub: ["#354"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-08-04"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00331", "init-00322"]
---

# iss-00354 Define ChatGPT Context and Attachment Contract — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | ChatGPT-Use reviewer | Candidate v2、last reviewed branch tip、current canonical working copy の権威境界および実装準備ゲート | Candidate v2 の immutable identity を historical evidence として保持し、last reviewed exact HEAD と次回 review target を別レコードで扱う | Candidate v2 archive は `deferred`。v4 Red Team が確認した branch tip は `bb75f6d5...` であり、その後の repair commit は新しい fresh review target として GitHub preflight で確定する。fresh exact-HEAD review が PASS するまで execution-ready にしない | v2 PASS と v4 FAIL はそれぞれ異なる source HEAD に束ね、current canonical docs の採用と review target の先取りを行わない | applied | `candidate-note.md`, `report.md`, v4 external identity, GitHub preflight | fresh review PASS 後に S01〜S13 ブリーフを作成し、各ステップの検証を report に記録する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | `reviews/red-team-review-v2.md` | red-team-review | Candidate v2 の requirement/design/plan/ADR は P0/P1 なしで PASS した | `requirement.md`, `design.md`, `plan.md` | historical design inputs only | v2 PASS は Candidate source HEAD に対する結果であり、ZIP archive 自体の canonical adoption を意味しない | formal_pass | `reviews/red-team-review-v2.md`, `candidate-note.md` | issue orchestrator | spec-reviewer | no | immutable evidence として保持し、current HEAD の fresh review と分離する |
| EAL-002 | adopted | `/private/tmp/iss-00354-chatgpt-review-20260804/implementation-readiness-review.md` | chatgpt-use-advisory | 前回 current-working-copy advisory review のP1三件を repair input として取り込んだ | `report.md`, `plan.md`, `candidate-note.md` | adoption/gate/step-contract sections | advisory finding は canonical docs の修正根拠として採用したが、review PASS や implementation approval には昇格していない | blocked_advisory | `/private/tmp/iss-00354-chatgpt-review-20260804/implementation-readiness-review.md`, commits `704fe487`, `dba243168` | issue orchestrator | ChatGPT-Use reviewer | no | 修正履歴として保持し、fresh exact-HEAD review の対象外にしない |
| EAL-003 | adopted | `/private/tmp/iss-00354-chatgpt-review-v3-20260804/review-compact.md` | chatgpt-use-red-team | current HEAD `dba243168647902c8883c0a44ed58a89c754070b` に対する fresh review は P0=0/P1=3 の FAIL であり、F01–F03 を repair input として採用する | `report.md`, `plan.md`, `candidate-note.md` | current binding, EAL, reviewer gates, executable step contract | FAIL の指摘だけを修正入力として採用し、reviewer の canonical modification や implementation start は行わない | fresh_fail | `/private/tmp/iss-00354-chatgpt-review-v3-20260804/review-compact.md` (SHA-256 `0e57f60f1a86a1be3299d360e55509b5905edd7e3bfaaa98c0809eb69fa4f26f`) | issue orchestrator | ChatGPT-Use Red Team | no | EAL-005 PASS により修正済みとして履歴保持する |
| EAL-004 | adopted | `/private/tmp/iss-00354-chatgpt-review-v4-20260804/review.md` | chatgpt-use-red-team | branch tip `bb75f6d5fcd142d8f2d0dd3ff4a06a057b4ee709` に対する fresh review は P0=0/P1=3 の FAIL であり、R3-01〜R3-03 を repair input として採用する | `report.md`, `plan.md`, `candidate-note.md` | current binding, execution evidence, S10–S12 cards | FAIL の指摘だけを修正入力として採用し、reviewer の canonical modification や implementation start は行わない | fresh_fail | `/private/tmp/iss-00354-chatgpt-review-v4-20260804/review.md` (SHA-256 `a936c4671b8bfb8ab0a87f7b137a332209856d44c55e050ec91cd1cde3639401`) | issue orchestrator | ChatGPT-Use Red Team | no | EAL-005 PASS により修正済みとして履歴保持する |
| EAL-005 | adopted | `/private/tmp/iss-00354-chatgpt-review-v5-20260804/review.md` | chatgpt-use-red-team | exact branch HEAD `079685b2a38baf9300c5bec7d5589ce9712bc7d3` に対する fresh review は PASS（P0=0/P1=0）であり、R3-01〜R3-03 の修正後文書を実装準備のレビュー済み入力として扱える | `requirement.md`, `design.md`, `plan.md`, `report.md`, `candidate-note.md` | review/adoption gates and implementation-preparation boundary | v5 review scope is defect-only and confirms identity, executable plan, report gate semantics, and code baseline without architecture redesign; implementation and Human adoption remain separate | fresh_pass | `/private/tmp/iss-00354-chatgpt-review-v5-20260804/review.md` (SHA-256 `d0a2e1bef291bab88797e166c5e96a368357452f7c2b4ddeaca402dc8bf5ea1a`) | issue orchestrator | ChatGPT-Use Red Team | no | record PASS, retain evidence-only Candidate boundary, and begin S01 brief only after normal execution preflight |
| EAL-006 | adopted | `/private/tmp/iss-00354-s01-brief-20260804/brief.md` | chatgpt-use-implementation-brief | S01の実装前ブリーフは、厳格なOracle preflight、content-free receipt、0.16.1境界テスト、未知の0.17 capabilityを停止ゲートとして扱う方針を具体化した | `artifacts/implementation-briefs/s01-capability-characterization.md`, `report.md` | S01 implementation scope and step evidence | byte-identical artifact copy and SHA match were verified; model evidence is recorded separately and does not claim Luna/Max | advisory_adopted | `/private/tmp/iss-00354-s01-brief-20260804/brief.md` (SHA-256 `391c7a2a8f65a9c5caff2a3a8b8239f9603f00858cc924c971574afec39a33c4`) | issue orchestrator | ChatGPT-Use | no | retain artifact and use it only for S01 implementation context |
| EAL-007 | adopted | `/private/tmp/iss-00354-s01-review-v2-20260804/review.md` | chatgpt-use-red-team | exact branch HEAD `e599d19e2027cfd599f00aa730f90bf52dc06742` に対する fresh review は PASS（P0=0/P1=0、P2=1）であり、前回S01-R01/R02は解消された。P2はexact-HEADのコマンド証跡をreportへ追記する非コード課題である | `report.md`, `issue_planning_chatgpt.py`, `test_issue_planning_chatgpt.py` | S01 review gate and execution evidence | GitHub branch tipとsource/test blobが一致し、scope逸脱・privacy leak・argv driftは確認されなかった。P2の最小修正としてこのreportへ実行結果を記録する | fresh_pass | `/private/tmp/iss-00354-s01-review-v2-20260804/review.md` (SHA-256 `3636c3c4b421be893293cbcfced6a0680ef9eaa9c813a8c76fee64a96bf21518`) | issue orchestrator | ChatGPT-Use Red Team | no | append exact-HEAD test/static command evidence; keep S01 stop gate for live 0.17 capabilities |
| EAL-008 | adopted | Oracle native capability probe | oracle-native-capability-probe | PATH Oracle 0.17.0のhelp surfaceと、directory、multiple path、native follow-upのpositive evidenceを確認した。missing pathは送信前にfail-closedした | `report.md` | S01 capability receipt and stop gate | sanitized receiptは管理一時領域に保存し、raw prompt/path/session handleは保存しない。remote post-upload attachment-failure stageだけはunknownとしてS10へ引き継ぐ | observed_supported_with_gap | `/private/tmp/codex-agent-work/501/session-20260804t115555z-iss-00354-s01-capability-probes-67ecbf19/receipt.md` (SHA-256 `a91c02140d5f649ae164c2817a5977f8536dd3b5b17e947357f6279cd6ee422d`)、Oracle native probe sessions | issue orchestrator | implementation execution | no | S01 closure; carry remote attachment-failure stage as S10 characterization input |
| EAL-009 | adopted | `/private/tmp/codex-agent-work/501/s02-review-v2-20260804/review-retry.md` | chatgpt-use-red-team | issue planningのapplication contract/caller binding更新が、full context identityとresources-operations化により正しい修正として完了した | `artifacts/implementation-briefs/s02-operation-resources.md`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/test_issue_planning_prompt.py`, `report.md` | S02 scope expansion（application caller filesがP1修正のため含まれる）を記録し、cl-s02-profile/tc-s02-001をcloseする | fresh_pass | `/private/tmp/codex-agent-work/501/s02-review-v2-20260804/review-retry.md` (SHA-256 `71848ca189d87d82b1b2cadf0c81e5533d47b0732deac830c2dde6142b1c26ec`), `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` | issue orchestrator | ChatGPT-Use Red Team | no | S03以降の実装に先立ちS02の実装完了を反映 |
| EAL-010 | deferred | `/private/tmp/codex-agent-work/501/s03-brief-20260804/brief.md` | chatgpt-use-implementation-brief | S03 実装ブリーフを `artifacts/implementation-briefs/s03-input-path-model.md` に採用した。旧 allowlist では `app/issue_planning.py` のbytes producer と `infra generated-pack consumer` を同時に移行できなかったため、当初のS03単独実装は保留した | `artifacts/implementation-briefs/s03-input-path-model.md`, `report.md` | 仕様実装の履歴とscope補正 | 当初のscope-blockはEAL-011のS03/S04 atomic cutoverで解消方針へ置換された。履歴は保持するが、現在の実装開始を止める未解決blockではない | advisory_deferred | `/private/tmp/codex-agent-work/501/s03-brief-20260804/brief.md` (SHA-256 `700b9c44cba1b66993cc30fd7fa1c52cefa6a79de59fd3b562ba2927cae682a8`) | issue orchestrator | ChatGPT-Use | no | EAL-011のatomic scopeとfresh plan reviewの結果を正本とし、旧単独scopeは再利用しない |
| EAL-011 | partially_adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-20260804/brief-full.md` | chatgpt-use-plan-clarification | S03/S04 を一つの deployable change-set とし、S03 は application path-only contract/caller、S04 は direct repeated `--file` transport を担当する計画補正案を採用候補とした。両 closure は同一 resulting HEAD でのみ close する | `plan.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md`, `report.md` | S03/S04 execution boundary、union allowlist、closure coupling | 現行コードの bytes producer と generated-pack consumer を既承認の path-only/direct transport 設計へ整合させるための最小補正。fresh v1 review はP1三件を指摘したため、v2 addendumでresource、e2e test、EAL語彙を補正して再レビューする。要件・設計、S05以降の責務は変更しない | advisory_plan | `/private/tmp/codex-agent-work/501/s03-s04-plan-20260804/brief-full.md` (SHA-256 `3286db64b54a82c67237a637a9fad4bd4a9443b9f8e29590de97edccbd4ae2ea`), base HEAD `a2bc5e00cf7aefe049c234bfe0207f992077af8f` | issue orchestrator | ChatGPT-Use | yes | v2 addendumを含む修正をpushし、新規fresh Red Team threadでPASSを得る |
| EAL-012 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-20260805/review.md` | chatgpt-use-red-team | exact branch HEAD `dada1f403241f615340ae1f0f8fb28b047edae75` に対する fresh defect-only plan review は FAIL（P0=0/P1=3）であり、RT-354-S03S04-001〜003を修正入力として採用した | `plan.md`, `report.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` | S03/S04 atomic allowlist、resource/e2e contract、EAL gate | Red Teamはread-onlyで、Candidate、canonical docs、repositoryを変更していない。P1三件だけを修正対象とし、アーキテクチャ再設計や提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-20260805/review.md` (SHA-256 `7be36264dae97ec8718dc93e12400b9c8736f1a8015547f3d26d92387fff5c06`), review identity SHA-256 `d660016800b378b9fbd689a18ed3d41af0a1c4aa5e380ada6bbdd064df3e2a05` | issue orchestrator | ChatGPT-Use Red Team | no | v2 repairを反映した新しいHEADをfresh Red Teamで再レビューする |
| EAL-013 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-v2-20260805/review-short.md` | chatgpt-use-red-team | exact branch HEAD `18db33044221204b3cc1d856f78570ee6523ac48` に対する fresh defect-only plan review v2 は FAIL（P0=0/P1=2）であり、RT-354-S03S04-V2-001〜002を修正入力として採用した | `plan.md`, `report.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` | S03/S04 execution-card allowlist、focused verification、same-HEAD closure | Red Teamはread-onlyで、Candidate、canonical docs、repositoryを変更していない。指摘はresource identity契約の許可範囲とfull-chain e2e検証の明示不足に限定され、アーキテクチャ再設計や改善提案はない | fresh_fail | `reviews/red-team-review-s03-s04-plan-v2.md` (SHA-256 `a7b866a54c753d6e8619404e113afba08615037e22fd0dd98114601261bc7c75`), review identity SHA-256 `2d2e1b4e35b4dd2d2e44ad34289af2408cc3263bc3537f5fa8a97b98d0792c71` | issue orchestrator | ChatGPT-Use Red Team | no | RT-354-S03S04-V2-001〜002をplan/cards/v2 briefへ反映してpushし、新規fresh Red Team threadで再レビューする |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ChatGPT context and attachment contract is the primary objective; execution briefs are supporting evidence | Candidate v2 docs, user-approved S01-S13 brief operation, and current plan closure index | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | current requirement.md, Candidate v2 MANIFEST/CHECKSUMS, and v5 exact-head review record | v5 fresh review returned PASS; Candidate remains historical evidence-only | adopted_for_review | pass | no | promote |
| design | current design.md, runtime classifier, and v5 exact-head review record | v5 fresh review returned PASS; no design redesign was requested | adopted_for_review | pass | no | promote |
| plan | current plan.md S01-S13 closure index and step-local contracts | v5 fresh review returned PASS; S10–S12 scope repairs are included | adopted_for_review | pass | no | promote |

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
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
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
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | v5 fresh review PASS; implementation still not started | pass | execute approved plan after per-step brief |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
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
- S01（Oracle preflight capability characterization and 0.16.1 regression boundary）を実装した。変更は provider-side infra adapter と既存 unit test に限定し、strict semver 判定、content-free receipt、fail-closed preflight、既存 browser/recovery argv の境界テストを追加した。
- S01 の実装ブリーフは `artifacts/implementation-briefs/s01-capability-characterization.md`、S02 の実装ブリーフは `artifacts/implementation-briefs/s02-operation-resources.md`、S03 の実装ブリーフは `artifacts/implementation-briefs/s03-input-path-model.md` に配置し、コードコミットは `e599d19e2027cfd599f00aa730f90bf52dc06742`（S01）と `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95`（S02）として GitHub branch に push 済みである。S03〜S13 の実装、PR、merge、Issue close は未実施であり、S03はscope-blockのため実装未着手。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-08-04 / implementation preparation — historical pre-S01）

#### 対象
- Step: S01〜S13（pre-S01 historical snapshot; implementation not started at that checkpoint）
- AC/EC: `plan.md` section 17.6 の closure contract を参照
- 計画上の出典（Planned source）:
  - `plan.md` section 17.6
  - `cl-s01-capability`〜`cl-s13-closure`

#### 実施内容（pre-S01 historical snapshot）
- Candidate v2 identity、current canonical docs、report evidence gate の整合を確認し、実装準備の承認境界を記録した。
- S01〜S13 の実行カード、delegation contract、具体テストケース、closure id を `plan.md` に追加した。

#### 実行コマンド / 結果
```bash
PYTHONPATH=spec-dock/scripts python - <<'PY'
from pathlib import Path
from spec_dock_runtime.application.workflow import _classify_plan_text, _classify_design_text
from spec_dock_runtime.domain.workflow_state import evaluate_report_evidence_gate
base = Path("spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract")
print(_classify_design_text((base / "design.md").read_text()))
print(_classify_plan_text((base / "plan.md").read_text()))
print(evaluate_report_evidence_gate((base / "report.md").read_text(), "standard"))
PY
./spec-dock/scripts/spec-dock assurance verify
./spec-dock/scripts/spec-dock guidance issue-execution

result: design substantive; plan executable; report evidence blocked (`report-spec-authoring-gate-invalid`); assurance valid; guidance blocked (`issue-planning-required`)
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | implementation | strict preflight receipt and 0.16.1 regression boundary implemented; S01 brief is recorded | `uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q` -> 92 passed; infra subset -> 60 passed; ruff/mypy/diff check passed | exact HEAD `e599d19e2027cfd599f00aa730f90bf52dc06742` and GitHub parity | green | ChatGPT-Use fresh review v2 is PASS for P0/P1; P2 is non-blocking evidence bookkeeping |
| S02 | implementation | issue planning リソースを operations 3種へ再構成し、application側 contract/caller-binding と evidence body binding を追加した | focused pytest 144 passed; unit pytest 1471 passed, 573 skipped; ruff/mypy/validate/diff-check pass; review replay PASS | exact HEAD `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` and GitHub parity | green | `cl-s02-profile`、`tc-s02-001` は closed |
| S03 | implementation preparation | S03 input-path model のブリーフを report へ反映し、scope-block を明示した。現行 allowlist は `prompt/domain/tests` であり、`app/issue_planning.py` の bytes producer と `infra generated-pack consumer` を含む migration には plan amendment / cutover再承認が必要 | no implementation evidence yet; brief generated only | docs inspection and runtime gate commands | blocked | scope-block due allowlist mismatch |
| S04〜S13 | implementation preparation | inspect-only until each step's brief and execution gate | no implementation evidence yet; executable step contracts remain in plan.md | docs inspection and runtime gate commands | pending | implementation evidence is collected per step |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | strict version parsing, preflight failure, argv and recovery boundary cases | ChatGPT-Use implementation review v2 and native Oracle probe | strict parser, timeout/nonzero/argv tests, and sanitized directory/multiple/continuation receipt recorded; no plan amendment | `cl-s01-capability` | no | remote post-upload attachment-failure stage is deferred to S10 |
| S02 | issue planning resources/application contract の回帰検証（prompt read/text binding / caller binding / invalid input） | Red Team review-v2 + 実行テスト | planning resources operations 3種、issue_planning_prompt caller identity binding、runtime caller context整合チェックを追加 | `cl-s02-profile` / `tc-s02-001` | no | P0/P1/P2/P3=0 でpass；identity SHA `10453a1669f2d64b462ad332177a69a70099cb91ac97ff9c312910f77e3ca760` |
| S03 | issue planning input path-model migration scope / allowlist check | `artifacts/implementation-briefs/s03-input-path-model.md`, `scope-block review` | brief生成とscope-block検証のみ。実装テストは未実施 | `cl-s03-path-input` / `tc-s03-001`（pending） | no | plan amendment または S03-S04 atomic cutover 再承認が必要 |
| S04〜S13 | no execution tests yet; closure risks are enumerated in plan.md | plan | no implementation response yet | `cl-s04-profile`〜`cl-s13-closure` | no | each step requires its own brief and evidence |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `cl-s01-capability` | strict preflight receipt, fail-closed unsupported capability, 0.16.1 regression tests, and direct capability receipt | implementation, focused test, exact HEAD, and sanitized live receipt recorded; remote post-upload failure stage explicitly deferred to S10 | closed | directory/multiple/continuation supported; S02 may start |
| S02 | `cl-s02-profile`, `tc-s02-001` | issue planning prompt/application contract の実装と、full identity binding・prompt-minimal化の検証 | focused/unit tests, lint/type validation, `spec-dock validate .`、parity確認、diff-check | closed | resources operations 3種とissue_planning caller bindingが反映 |
| S03 | `cl-s03-path-input` | S03 input path-model scope のブリーフ反映と scope-block の検証 | no implementation observation; brief-only evidence and scope-block recorded | pending | implementation will proceed only after re-approval |
| S04〜S13 | `cl-s04-profile`〜`cl-s13-closure` | per-step behavior slice and gate in plan.md | no implementation observation yet; closure is pending execution | pending | implementation must populate each row per step |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `cl-s01-capability` | S01 | yes | implementation | focused pytest, infra subset, full infra, ruff, mypy, diff check, and sanitized direct capability receipt | executed; all code/static checks pass and receipt recorded | pass | remote post-upload failure stage is a later S10 obligation |
| `cl-s02-profile` | S02 | yes | implementation | focused pytest, unit pytest, ruff、mypy、validate、diff-check | close by this commit; P0/P1/P2/P3=0, review-v2 pass | pass | test evidence links to review `s02-review-v2-20260804` |
| `tc-s02-001` | S02 | yes | implementation | focused pytest, unit pytest, ruff、mypy、validate、diff-check | close by this commit; P0/P1/P2/P3=0, review-v2 pass | pass | test evidence links to review `s02-review-v2-20260804` |
| `cl-s03-path-input` | S03 | no | no-op | S03ブリーフ採用のみ; scope-block record | pending | pending | `advisory` brief evidence only |
| `tc-s03-001` | S03 | no | no-op | S03ブリーフ採用のみ; scope-block record | pending | pending | `advisory` brief evidence only |
| `cl-s04-profile`〜`cl-s13-closure` | S04〜S13 | yes | inspect-only before implementation | runtime gate and per-step test command to be added at execution | not executed | pending | closure evidence is required during execution |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-s01-capability` | S01 | exact-HEAD test/static command output and live Oracle capability probe | code/static checks pass; directory/multiple/continuation supported; missing-path preflight fail-closed; remote post-upload failure stage unknown | pass | S02 may start; S10 must characterize remaining stage |
| `cl-s02-profile` / `tc-s02-001` | S02 | execution-specific command output | exact-HEAD S02 evidence and red-team v2 の結果を report に反映 | closed | implementation will proceed to S03 |
| `cl-s03-path-input` / `tc-s03-001` | S03 | scope-block evidence and brief evidence | no implementation evidence; ブリーフ採用とブロッキング判断を report へ記録 | blocked | scope re-approval required |
| `cl-s04-profile`〜`cl-s13-closure` | S04〜S13 | execution-specific command output | not observed before implementation | pending | implementation will populate each row |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `cl-s01-capability` / `cl-s02-profile` / `tc-s02-001` | no alias | `cl-s02-profile` / `tc-s02-001` はclosedとして解決 | no plan amendment before implementation | no | no |
| none | `cl-s03-path-input` / `tc-s03-001` | no alias | S03 pending（scope-block）。plan amendment / cutover 再承認が必要 | no plan amendment before approval | yes | yes |
| none | `cl-s04-profile`〜`cl-s13-closure` | no alias | same closure ids are retained from plan.md | no plan amendment before implementation | no | no |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to use SpecDock workflow | `chemitaro/spec-dock` / active worktree | iss-00354 | current session | spec-reviewer / doc-writer / ChatGPT-Use | active Issue scope, current branch, current session, and documented role responsibility; no merge, close, or external mutation | session end, scope change, host conflict, or user revocation | none | continue after fresh ChatGPT review; block on identity drift |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | implemented-ready-for-s02 | provider infra implementation with per-step ChatGPT-Use brief | dev-coder | provider infra adapter and existing infra unit test only | plan.md and current Issue scope | S01 code/test changes and report evidence | no 0.17 profile, stage decoder, inline fallback, artifact reader, application/domain/CLI, merge or close | focused tests/static checks, fresh ChatGPT review, and live capability gate | remote post-upload attachment-failure stage remains unknown for S10 | changed files, verification result, and adoption decision | code review PASS; directory/multiple/continuation receipt recorded; S01 closed |
| S02 | completed-and-closed | implementation with per-step ChatGPT-Use brief | dev-coder | `artifacts/implementation-briefs/s02-operation-resources.md` と provider application resources / tests | plan.md, S02 brief, and current Issue scope | only S02 allowed files + evidence fields in report | no execution before active step brief/review, no merge or close | per-step brief, tests, report closure | active step gate or capability ambiguity | change log and adoption decision | code review PASS; cl-s02-profile/tc-s02-001 close |
| S03 | implementation preparation-blocked | implementation with per-step ChatGPT-Use brief | dev-coder | `artifacts/implementation-briefs/s03-input-path-model.md` のみ（report update） | plan.md and current Issue scope | S03 brief + scope-block evidence の追加のみ | S03実装前に plan amendment / S03-S04 atomic cutover 再承認が必要 | brief generation record only | scope block / allowlist mismatch | begin S03 once re-approval is complete |
| S04-S13 | pending-active-step | implementation with per-step ChatGPT-Use brief | dev-coder | step-local allowed paths in plan.md | plan.md and current Issue scope | only the active step's allowed files | no execution before active step brief/review, no merge or close | per-step brief, tests, report closure | active step gate or capability ambiguity | begin S04 after this report commit |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Implemented strict preflight receipt and 0.16.1 regression-boundary tests within the approved provider infra scope | `issue_planning_chatgpt.py`, `test_issue_planning_chatgpt.py` | 92 focused tests; 60 infra subset; 507 infra tests passed/573 skipped; ruff/mypy/diff check passed | ChatGPT-Use Fresh Red Team v2 PASS (P0=0/P1=0, P2=1) | remote post-upload attachment-failure stage remains unknown for S10 | parent integration records exact HEAD and sanitized capability receipt |
| S02 | dev-coder | issue planning resources のoperations化とapplication contract/caller bindingの修正を実施 | `artifacts/implementation-briefs/s02-operation-resources.md`, `issue_planning_prompt.py`, `issue_planning.py`, `test_issue_planning_prompt.py` | focused 144 passed; unit 1471 passed, 573 skipped; ruff/mypy/validate/diff-check | ChatGPT-Use Fresh Red Team review-v2 PASS (P0/P1/P2/P3=0) | no unresolved S01 blocker; remote attachment-failure stage remains S10 scope | parent integration records exact HEAD, identity SHA, and scope expansion note |
| S03 | dev-coder | issue planning input path-model のブリーフをreport化し、scope-blockを記録（実装は未実施） | `artifacts/implementation-briefs/s03-input-path-model.md` | not executed | blocked | no unresolved S02 blocker; no  unresolved S03 blocker | begin with scope reapproval |
| S04-S13 | dev-coder | not started; S03でブロック中 | none | not executed | pending | no unresolved S03 blocker | begin with S04 brief |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | no delegation exception; code implementation was delegated within the approved provider infra scope | user request to implement and review; risk accepted: no | provider infra source/test and report evidence | S01 implementation, verification, and report update | no rollback needed; immutable Candidate v2 retained | focused/full infra tests, diff check, fresh ChatGPT review, and sanitized capability receipt | S01 review PASS; remote post-upload failure stage deferred to S10 | continue to S02; no merge or close |
| S02 | no delegation exception; application contract / caller-binding修正でS02 stepを実施 | user request to implement and review; risk accepted: no | S02 scope files in plan.md（application prompt and issue_planning） | per-step implementation and report evidence | no rollback needed; immutable Candidate v2 retained | focused/unit tests, ruff/mypy/validate/diff-check, and red-team review-v2 | active step gate or capability ambiguity | parent integration records scope expansion and exact-HEAD closure, then stop on plan gate |
| S03-S13 | no delegation exception; documentation work was performed in the active Issue scope | user request to implement and review; risk accepted: no | step-local allowed paths in plan.md（S03は brief と report 更新のみ） | per-step implementation and report evidence | no rollback needed; immutable Candidate v2 retained | per-step ChatGPT brief, tests, review, and diff check | active step gate or capability ambiguity | stop on plan-defined gate; no merge or close |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `lite` | `not applicable` | `not applicable` | Lite specialist evidence is not used; v5 exact-head review PASS is recorded | `pass` | `ready` |
| `standard` | `manual fallback` | `used` | Manual authoring fallback is retained and v5 exact-head Red Team review PASS is recorded | `pass` | `ready` |
| `strict` | `manual fallback` | `used` | Strict execution is not selected; v5 exact-head review PASS is recorded | `pass` | `ready` |
| `critical` | `manual fallback` | `used` | Critical execution is not selected; v5 exact-head review PASS is recorded | `pass` | `ready` |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | implementation review | spec-reviewer | fresh | pass | no | promote | ChatGPT-Use Red Team v2 at exact HEAD `e599d19e...` is PASS (P0=0/P1=0, P2=1); code scope is valid and sanitized S01 capability receipt now closes the S01 gate; remote post-upload failure stage is deferred to S10 |
| S02 | implementation-readiness review | ChatGPT-Use Red Team | fresh | pass | no | closed | `/private/tmp/codex-agent-work/501/s02-review-v2-20260804/review-retry.md` (SHA-256 `71848ca189d87d82b1b2cadf0c81e5533d47b0732deac830c2dde6142b1c26ec`), model requested `gpt-5.6`, target/resolved `GPT-5.6 Sol`, strategy `select`, verified `yes` |
| S03-S04 | implementation-readiness review | ChatGPT-Use Red Team | pending | blocked | no | wait for active step brief and re-approval of scope/block status | each step requires a fresh brief/review as prescribed by plan.md |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | `e599d19e2027cfd599f00aa730f90bf52dc06742` | `e599d19e2027cfd599f00aa730f90bf52dc06742` plus report evidence commits | local/GitHub parity; clean before next step | provider infra + existing infra unit test only | source/test, S01 brief, and sanitized capability receipt | `git diff --check` | directory/multiple/continuation evidence recorded; remote failure stage deferred to S10 |
| S02 | committed | `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` | `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` plus report evidence commit | local/GitHub parity; clean after commit | issue planning application contract / caller binding and S02 evidence | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `tests/unit/application/test_issue_planning_prompt.py` | `uv run pytest` / `uv run ruff check` / `uv run mypy` / `uv run spec-dock validate .` / `git diff --check` | remote parity verified; cl-s02-profile / tc-s02-001 closed |
| S03-S13 | pending | not started | none | not applicable | no product-code change | step-local paths in plan.md | not run | each step awaits its own brief and review |

#### 変更したファイル
- S01 implementation: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, `tests/unit/infra/test_issue_planning_chatgpt.py`
- S01 artifact: `artifacts/implementation-briefs/s01-capability-characterization.md`
- S02 implementation: `artifacts/implementation-briefs/s02-operation-resources.md`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `tests/unit/application/test_issue_planning_prompt.py`
- S03 artifact: `artifacts/implementation-briefs/s03-input-path-model.md`
- This report: implementation, verification, review, and remaining capability gate evidence

#### コミット
- `e599d19e2027cfd599f00aa730f90bf52dc06742` (`fix(iss-00354): S01のpreflight検証とテストを堅牢化`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` (`fix(iss-00354): Issue planning証跡生成のidentity検証を厳密化`), pushed to `codex/iss-00354-chatgpt-context-contract`

#### メモ
- Candidate v2 archive remains immutable; current working-copy amendments are a separate history entry.
- S01 implementation is not an assurance promotion, PR, merge, or Issue close.

---

### セッションログ（追加実装 — historical pre-S01）

#### 対象
- Step: none
- AC/EC: none

#### 実施内容
- この時点では追加実装は未実施であり、次回をS01のChatGPT-Use実装ブリーフ生成としていた。現在のS01実装結果は後段の「S01実装・Fresh Red Team Review」に記録する。

---

## 候補 v2 配置記録（2026-08-04）

- 対象候補: `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z`
- 対象 ZIP: `iss-00354-oracle-017-compatibility-candidate-v2-20260804t043533z.zip`
- ZIP SHA-256: `a870bb35971d86a5a0c5311f404ab717669d6bbaf6798a03a0ad3061537202f8`
- source HEAD: `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1`
- source branch: `codex/iss-00354-chatgpt-context-contract`
- 配置先: `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/`
- 配置内容: Candidate の `requirement.md`、`design.md`、`plan.md`、ADR、全アーティファクト、`MANIFEST.json`、`CHECKSUMS.sha256`、Candidate 注記、および v1/v2 の正式レビュー記録を、解凍したファイルとして配置した。既存の履歴アーティファクトは削除していない。
- 検証: 配置先で `shasum -a 256 -c CHECKSUMS.sha256` を実行し、Candidate v2 に含まれる全エントリが一致した。v2 Red Team は fresh thread で PASS（P0/P1 なし）となった。
- 配置状態: `copied_to_issue_scope`
- 正式採用状態: `deferred`。今回の依頼は解凍した仕様書等の配置であり、`planning apply`、assurance 更新、implementation start は実行していない。Candidate 文書に記載された `evidence-only` / `unadopted` の境界を維持する。

## 修正コミットとGitHub同期（2026-08-04 / history）

- 修正コミット: `9ffef840c50c4796da784aab699c1b7d74d7637e` (`docs(iss-00354): v2レビュー修正を現行HEAD方針へ統合`)
- repository: `chemitaro/spec-dock`
- branch: `codex/iss-00354-chatgpt-context-contract`
- local HEAD と GitHub branch HEAD: `identical`
- この行の同期記録は履歴であり、v4の実レビュー対象は `bb75f6d5fcd142d8f2d0dd3ff4a06a057b4ee709` として別節に記録する。新しい repair commit は毎回 GitHub preflight で exact HEAD を確定してからレビューする。default branch fallback は使用しない。

## 実装ブリーフ運用追加（2026-08-04）

- `plan.md` の S01〜S13 各マイルストーンに、実装開始前の ChatGPT-Use ブリーフ作成手順を一行ずつ追加した。
- ブリーフの対象モデルは `GPT-5.6 Luna`、推論レベルは `Max` とし、`artifacts/implementation-briefs/sXX-*.md` に保存する。
- Codex は各ブリーフを参照して当該マイルストーンを実装し、採用判断・実測結果・未解決リスクは `report.md` に記録する。
- この追加は実装手順の運用補足であり、ユーザー指示により既存の仕様レビューを再実行しない。実装開始・ChatGPTレビュー・正式採用は別ゲートで確認する。
- この時点ではブリーフ本文の生成、実装、テスト、assurance の正式採用更新は行っていない。

## ChatGPT-Use Advisory Review（2026-08-04 / historical pre-repair）

- 実行経路: ChatGPT-Use / Oracle `0.17.0` / browser foreground。repository `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、HEAD `57ba2cd56d9bf3722c9ea097ba861f06f966b9c1` を GitHub で確認し、default branch fallback は使用していない。
- 要求モデル: `GPT-5.6 Luna` / `Reasoning Effort Max`。現行 wrapper の選択肢に Luna はなく、browser で Max を指定すると API 経路へ切り替わり個人ビルドで無効となるため、要求どおりの実行はできなかった。
- 実測モデル: Oracle の model selection evidence は requested `gpt-5.6`、resolved `GPT-5.6 Sol`、`verified=yes`。ChatGPT 回答本文の `GPT-5.6 Pro` という自己申告とは一致しないため、自己申告は採用せず、wrapper の実測証跡を正とする。
- 外部レビュー出力: `/private/tmp/iss-00354-chatgpt-review-20260804/implementation-readiness-review.md`、SHA-256 `8e1be273dcfabbae7f34797bab5f392e1e59f462a9f42c2d82a98c579bcd385a`。
- advisory 判定: `blocked`。P0 は `None`。P1 は (1) Candidate PASS と current HEAD / canonical authority の未閉鎖、(2) `design-not-substantive` に続く executable plan gate 未閉鎖、(3) `report.md` の EAL・phase gate・reviewer gate が scaffold のまま、の3件。
- 採否: ChatGPT-Use 出力は advisory evidence として扱い、修正・ZIP生成・canonical adoption・assurance promotion・implementation start はこのレビューでは実施していない。

## ChatGPT-Use Fresh Red Team Review（2026-08-04 / historical HEAD `dba243168...`）

- 実行経路: ChatGPT-Use / Oracle `0.17.0` / browser foreground。repository `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、HEAD `dba243168647902c8883c0a44ed58a89c754070b` を GitHub で確認し、default branch fallback は使用していない。
- 添付対象: `requirement.md`、`design.md`、`plan.md`、`report.md`、`candidate-note.md`、`.assurance.json`、ADR、v2 Red Team review、およびレビュー指示 `prompt.md`。レビュアーは対象 branch のファイルと添付内容を照合した。
- モデル選択証跡: wrapper は requested `gpt-5.6` / target `GPT-5.6 Sol`、resolved UI label `Pro`、`strategy=current`、`verified=no` を記録した。`GPT-5.6 Luna / Max` の実測成功とは主張しない。
- 外部レビュー出力: `/private/tmp/iss-00354-chatgpt-review-v3-20260804/review-compact.md`、SHA-256 `0e57f60f1a86a1be3299d360e55509b5905edd7e3bfaaa98c0809eb69fa4f26f`。
- fresh Red Team verdict: `FAIL`、P0 `0`、P1 `3`。`RT-354-F01` は Candidate/current canonical authority、`RT-354-F02` は S01〜S13 step contract、`RT-354-F03` は report の EAL/reviewer gate の意味整合を指摘した。
- disposition: 三件の P1 は `EAL-003` として repair input に採用した。Red Team は read-only のままで、Candidate ZIP、canonical docs、repository をレビュー中に変更していない。implementation start、assurance promotion、PR、merge、Issue close は未実施であり、fresh PASS まで blocked とする。

v3修正後に次回対象として記録した `d556295a93a51b9c2f1e697a7d18e21876727f77` は、v4前の履歴上の修正コミットである。v4の実レビュー対象は、次節に記録する `bb75f6d5...` である。

## ChatGPT-Use Fresh Red Team Review（2026-08-04 / v5 exact HEAD `079685b2...`）

- 実行経路: ChatGPT-Use / Oracle `0.17.0` / browser foreground。repository `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、HEAD `079685b2a38baf9300c5bec7d5589ce9712bc7d3` を GitHub で確認し、default branch fallback は使用していない。
- 添付対象: `prompt.md` と Issue の requirement/design/plan/report/candidate-note/.assurance/ADR/v2 review。添付内容と GitHub branch の対応ファイルは blob 単位で一致した。
- モデル選択証跡: wrapper は requested `gpt-5.6` / target `GPT-5.6 Sol`、resolved label `Pro`、`strategy=current`、`verified=no` を記録した。`GPT-5.6 Luna / Max` の実測成功とは主張しない。
- 外部レビュー出力: `/private/tmp/iss-00354-chatgpt-review-v5-20260804/review.md`、SHA-256 `d0a2e1bef291bab88797e166c5e96a368357452f7c2b4ddeaca402dc8bf5ea1a`。
- verdict: `PASS`、P0 `0`、P1 `0`、P2/P3なし。Candidate/current authority、S01〜S13 executable plan、report gate semantics、code baselineに重大な矛盾はないと確認された。
- disposition: v5 read-only PASSを `EAL-005` として採用した。実装、assurance promotion、PR、merge、Issue closeは未実施であり、PASSは実装完了またはHuman adoptionを意味しない。次は通常のexecution preflight後、S01実装ブリーフを作成する。

## ChatGPT-Use Fresh Red Team Review（2026-08-04 / v4 exact HEAD `bb75f6d5...`）

- 実行経路: ChatGPT-Use / Oracle `0.17.0` / browser foreground。repository `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、HEAD `bb75f6d5fcd142d8f2d0dd3ff4a06a057b4ee709` を GitHub で確認し、default branch fallback は使用していない。
- 添付対象: `prompt.md` と Issue の requirement/design/plan/report/candidate-note/.assurance/ADR/v2 review。添付内容と GitHub branch の対応ファイルは blob 単位で一致した。
- モデル選択証跡: wrapper は requested `gpt-5.6` / target `GPT-5.6 Sol`、resolved label unavailable、`strategy=current`、`verified=no` を記録した。`GPT-5.6 Luna / Max` の実測成功とは主張しない。
- 外部レビュー出力: `/private/tmp/iss-00354-chatgpt-review-v4-20260804/review.md`、SHA-256 `a936c4671b8bfb8ab0a87f7b137a332209856d44c55e050ec91cd1cde3639401`。
- verdict: `FAIL`、P0 `0`、P1 `3`。`RT-354-R3-01` は current HEAD binding、`RT-354-R3-02` は report gate の stale `pass/ready` 記録、`RT-354-R3-03` は S10〜S12 execution scope の不整合を指摘した。
- disposition: 三件の P1 は `EAL-004` として repair input に採用した。Red Team は read-only のままで、Candidate ZIP、canonical docs、repository をレビュー中に変更していない。implementation start、assurance promotion、PR、merge、Issue close は未実施であり、fresh PASS まで blocked とする。

## S01実装・Fresh Red Team Review（2026-08-04 / exact HEAD `e599d19e...`）

- 実装対象: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py` と `tests/unit/infra/test_issue_planning_chatgpt.py` の2ファイルのみ。S01ブリーフは `artifacts/implementation-briefs/s01-capability-characterization.md` に配置した。
- repository / branch: `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract`。local HEAD と GitHub branch tip は `e599d19e2027cfd599f00aa730f90bf52dc06742` で一致し、default branch fallbackは使用していない。
- 実装内容: Oracle version stdoutのstrict単一semver判定、raw path/URL/複数行値をreceiptへ保持しないcontent-free preflight receipt、unsupported/timeout/nonzero時のfail-closed、0.16.1のpreflight順序・subprocess安全引数・submit/recovery argv境界テストを追加した。0.17 profile、stage decoder、inline fallback、artifact reader、application/domain/CLI、projection、未文書化flagは追加していない。
- exact HEAD検証:
  - `uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q` -> **92 passed**
  - `uv run pytest tests/unit/infra -k 'issue_planning and (oracle or session or capability)' -q` -> **60 passed, 1020 deselected**
  - `uv run pytest tests/unit/infra -q` -> **507 passed, 573 skipped**
  - `uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py tests/unit/infra/test_issue_planning_chatgpt.py` -> **pass**
  - `uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py` -> **Success: no issues found**
  - `git diff --check` -> **pass**
- commit / push: `e599d19e2027cfd599f00aa730f90bf52dc06742` (`fix(iss-00354): S01のpreflight検証とテストを堅牢化`) をpush済み。検証後のreport更新前はcleanで、remote parityを確認した。
- ChatGPT-Use fresh Red Team: `/private/tmp/iss-00354-s01-review-v2-20260804/review.md`（SHA-256 `3636c3c4b421be893293cbcfced6a0680ef9eaa9c813a8c76fee64a96bf21518`）。GitHub exact HEAD、source/test blob、scope境界を照合し、P0=0、P1=0、P2=1、P3=0の **PASS**。P2は、レビュー入力時点でreportへexact-HEADコマンド証跡が未記録だったという非コードの記録課題であり、このセクションとEAL-007で解消記録を追加した。
- モデル証跡: wrapperは requested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、`strategy=select`、`verified=yes`。要求されたGPT-5.6 Luna / Reasoning Effort Maxの実測成功とは主張しない（`--reasoning-effort max`は個人OracleビルドでAPI実行無効となるため使用していない）。
- live capability probe: PATH Oracle `0.17.0` の `--version`、root `--help`、`session --help` は exit 0 で確認した。helpには `--file <paths...>`、`--followup` が明示され、directory単独（`files=1`・marker一致）、directory＋standalone file（`files=2`・両marker一致）、Oracle-native `--followup`（A→B）が成功した。存在しないpathはブラウザー起動前に拒否され、prompt/recovery/harvestは0だった。個人設定・認証情報・private prompt/pathはreportへ保存していない。
- S01停止ゲート: directory、multiple paths、continuationは `supported` と確定し、`cl-s01-capability`を閉じる。remote post-upload attachment-failure stageは `unknown` のままS10入力へ引き継ぐが、S02〜S08を妨げるS01停止条件ではない。
- 実装、assurance promotion、PR作成、merge、Issue closeはこの時点では実施していない。

## S02実装・Fresh Red Team Review（2026-08-04 / exact HEAD `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95`）

- 実装対象: `artifacts/implementation-briefs/s02-operation-resources.md`、`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`、`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`、`tests/unit/application/test_issue_planning_prompt.py` の4ファイル。
- repository / branch: `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract`。local HEAD と GitHub branch tip は `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` で一致し、default branch fallback は使用していない。
- 実装内容: issue planning の resource 構成を `operations/planning|review|revision` の3種へ再構成し、prompt.md先頭空白を保持。application の caller から evidence/signer context を厳密化して `remote_head`/`upstream`/`issue`/`parent`情報を identity に束ね、sensitive scan を operation context 全体へ適用。symlink/invalid UTF-8/子要素 add-delete に対する不変性テストと `cl-s02-profile` / `tc-s02-001` 回路を追加。
- exact HEAD 検証:
  - focused pytest: **144 passed**
  - unit pytest: **1471 passed**, **573 skipped**
  - `uv run ruff check`
  - `uv run mypy`
  - `./spec-dock/scripts/spec_dock validate .`
  - `git diff --check`
- commit / push: `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` (`fix(iss-00354): Issue planning証跡生成のidentity検証を厳密化`) をpush済み。検証後のreport更新前は clean で、remote parityを確認した。
- review: `/private/tmp/codex-agent-work/501/s02-review-v2-20260804/review-retry.md`（SHA-256 `71848ca189d87d82b1b2cadf0c81e5533d47b0732deac830c2dde6142b1c26ec`）はexact branch / exact HEAD / source blob一致、P0=0/P1=0/P2=0/P3=0 の PASS。identity SHAは `10453a1669f2d64b462ad332177a69a70099cb91ac97ff9c312910f77e3ca760`。モデルは requested `gpt-5.6`、target `GPT-5.6 Sol`、`strategy=select`、`verified=yes`。`Luna/Max` の実測成功は確認できないため、主張しない。
- S02のクローズ: `cl-s02-profile` と `tc-s02-001` を **closed** として記録。`S03〜S13` は引き続き pending。

## S03実装準備ブリーフ（2026-08-04 / ブリーフ追加のみ）

- 実装対象: `artifacts/implementation-briefs/s03-input-path-model.md`（canonical artifact）
- repository / branch: `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract`。local HEAD は `9a3ce89e...`、external brief は `/private/tmp/codex-agent-work/501/s03-brief-20260804/brief.md`。SHA-256 は `700b9c44cba1b66993cc30fd7fa1c52cefa6a79de59fd3b562ba2927cae682a8`。
- 実装内容: S03 input path-model ブリーフを canonical artifact として採用し、`report.md` にs03セクションを追加した。ブリーフでは、現行 allowlist（prompt/domain/tests）での実装では、bytes producer application (`app/issue_planning.py`) と infra generated-pack consumer の移行を満たせないため、S03 execution は blocked。
- scope-block: 現行allowlistではS03の実装開始不可。`plan amendment` または `S03-S04 atomic cutover` の再承認が必要。
- closure: `cl-s03-path-input` と `tc-s03-001` は **pending** のまま。
- reviewer gate: implementation-readiness は **blocked**。本ステップは「fresh red-team / 実行」には進まず、ブロッキング条件をreportへ記録した。
- wrapper evidence: requested `gpt-5.6` / target `GPT-5.6 Sol` / `strategy=select` / `verified=yes`。`GPT-5.6 Luna / Max` の実測成功は確認できないため、主張しない。

## S03/S04 atomic cutover 計画補正（2026-08-04 / 実装前ゲート）

- 計画補正ブリーフ: `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md`（元v1 briefは履歴証跡として保持）
- 対象 base HEAD: `a2bc5e00cf7aefe049c234bfe0207f992077af8f`。GitHub branch tip と一致し、default branch fallback は使用していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-plan-20260804/brief-full.md`、SHA-256 `3286db64b54a82c67237a637a9fad4bd4a9443b9f8e29590de97edccbd4ae2ea`。
- 計画判断: `cl-s03-path-input`（application path-only contract/caller）と `cl-s04-direct-transport`（infra repeated `--file` / no generated pack）を責務別に保持しつつ、一つの deployable change-set、rollback unit、fresh review target として実施する。片方だけの Green / close は許可しない。
- Union allowlist: provider application `issue_planning_prompt.py`、`issue_planning.py`、infra `issue_planning_chatgpt.py`、Review operation resource instructions、対応する application/infra unit tests、transport integration test、full-chain e2e test。Review instructions は generated identity attachments ではなく minimal body の identity/digest を参照する契約へ更新し、installed/dogfood projection は provider sync で再生成する。domain、CLI、Oracle profile/recovery、artifact reader、上記以外の resource wording/inventory は read/run-only とする。
- 禁止事項: compatibility property、dual-write、path-to-bytes 再構成、generated pack、copy/ZIP/hash/tree inspection、inline fallback、alternate backend は追加しない。
- reviewer gate: `repair_required`。fresh exact-HEAD の defect-only plan review は P0=0/P1=3 の FAIL だったため、RT-354-S03S04-001〜003を反映して新しいHEADで再レビューするまで実装開始ゲートは blocked のままとする。
- モデル証跡: 要求は GPT-5.6 Luna / Reasoning Effort Max。follow-up wrapper は target/resolved model unavailable、verified=no を返したため、Luna/Max の実測成功は主張しない。
- S03/S04 closure: `cl-s03-path-input` / `tc-s03-001`、`cl-s04-direct-transport` / `tc-s04-001` は pending。両者は同じ resulting implementation HEAD に結び付ける。

### S03/S04 atomic cutover 計画レビュー v1（2026-08-05 / read-only Red Team）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@dada1f403241f615340ae1f0f8fb28b047edae75`
- identity SHA-256: `d660016800b378b9fbd689a18ed3d41af0a1c4aa5e380ada6bbdd064df3e2a05`
- review artifact: `reviews/red-team-review-s03-s04-plan-v1.md`、外部出力 `/private/tmp/codex-agent-work/501/s03-s04-plan-review-20260805/review.md`、SHA-256 `7be36264dae97ec8718dc93e12400b9c8736f1a8015547f3d26d92387fff5c06`
- verdict: `FAIL`（P0=0 / P1=3 / P2=0 / P3=0）。指摘は generated identity attachments と Review resource contract の不整合、e2e fixture の旧 generated-pack consumer の allowlist 漏れ、EAL-010の非契約status語彙の三件である。
- scope: Red Teamはnamed branchのexact HEADをGitHubで確認し、Candidate、canonical docs、repositoryを変更していない。アーキテクチャ再設計や改善提案はなく、P1の整合性修正だけを採用する。
- model evidence: wrapperはrequested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、`strategy=select`、`verified=yes`を返した。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は確認できないため主張しない。
- next gate: RT-354-S03S04-001〜003をplan/reportへ反映し、commit/pushした新規HEADを別のfresh Red Team threadで再レビューする。PASS（P0/P1=0）までS03/S04実装は開始しない。

### S03/S04 atomic cutover 計画レビュー v2（2026-08-05 / read-only Red Team）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@18db33044221204b3cc1d856f78570ee6523ac48`
- identity SHA-256: `2d2e1b4e35b4dd2d2e44ad34289af2408cc3263bc3537f5fa8a97b98d0792c71`
- review artifact: `reviews/red-team-review-s03-s04-plan-v2.md`、外部出力 `/private/tmp/codex-agent-work/501/s03-s04-plan-review-v2-20260805/review-short.md`、SHA-256 `a7b866a54c753d6e8619404e113afba08615037e22fd0dd98114601261bc7c75`
- verdict: `FAIL`（P0=0 / P1=2 / P2=0 / P3=0）。指摘はS03/S04 execution cardのresource allowlist/forbidden記述が§8.1・v2 addendumと不一致であること、v2 addendumとexecution cardの必須focused verificationにfull-chain e2eが明記されていないことの二件である。
- scope: Red Teamはnamed branchのexact HEADをGitHubで確認し、Candidate、canonical docs、repositoryを変更していない。指摘は計画の実行可能性の欠陥に限定され、アーキテクチャ再設計や改善提案はない。
- model evidence: wrapperはrequested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、`strategy=select`、`verified=yes`を返した。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は確認できないため主張しない。
- next gate: RT-354-S03S04-V2-001〜002をplan/cards/v2 briefへ反映し、commit/pushした新しいexact HEADを別のfresh Red Team threadで再レビューする。PASS（P0/P1=0）までS03/S04実装は開始しない。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer | Candidate v2 scope and current Issue docs were reconciled; provider projection is checked at implementation S07 | pending implementation S07 |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | pending implementation and test execution | S01-S13 closure evidence not yet available | pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | S01 provider infra implementation and unit tests | strict preflight/recovery boundary; no scope expansion | 1 ChatGPT-Use Fresh Red Team review plus sanitized native capability receipt | PASS for P0/P1; S01 gate closed, remote post-upload failure stage deferred to S10 |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer / ChatGPT-Use Red Team | requirement / design / plan / report / candidate identity alignment | v2 Red Team PASS is historical Candidate evidence; v5 exact-head review at `079685b2...` is PASS with P0=0/P1=0 and EAL-005 records the external output | 4 prior review records including v5 PASS; no further spec re-review required for this evidence-only update | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| current branch HEAD | documentation repair commit and pushed branch | v5 PASS output and SHA are recorded above for exact HEAD `079685b2...`; this post-review ledger update contains no design or implementation change | pass | recorded |

## 遭遇した問題と解決 (任意)
- 問題: 前回のChatGPT advisory reviewは、Candidate v2とcurrent HEADの結び付け、executable plan、report gateをP1として指摘した。
  - 解決: 正規三文書の承認境界、S01〜S13のclosure契約、reportの採用・レビュー・専門家ゲートを補完した。fresh reviewはpush後に実施する。

## 学んだこと (任意)
- Candidate archiveのimmutable identityと、現在のcanonical working copyのHEADを別々に記録し、レビュー入力で明示する必要がある。

## 今後の推奨事項 (任意)
- S01開始前にChatGPT-Useで専用実装ブリーフを作成し、各stepの証跡をこのreportへ追記する。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
