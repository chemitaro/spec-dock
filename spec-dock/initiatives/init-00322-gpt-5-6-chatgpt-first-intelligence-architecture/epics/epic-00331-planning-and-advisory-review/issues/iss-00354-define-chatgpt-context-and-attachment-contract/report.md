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
| D-002 | resolved | scope | ChatGPT-Use S05 brief | S05 execution cardの許可パスが、old `--context-manifest` help契約とprompt synthesis変更を検証するテストを含んでいない | S05 cardにcommands/application/prompt、CLI help、prompt unit、transport/lifecycle testの最小パスを追加する | S05は既存hard cutoverのテスト同期を必要とし、allowlist不足のまま実装すると既知のhelp test失敗を残すため、production architectureを変更せず計画境界だけを補正する | S05 briefのexact branch確認と現行テストのsource inspectionで不足を確認し、計画補正後にfresh plan reviewを要求する | applied | `plan.md`, `artifacts/implementation-briefs/s05-orchestration-cli-cutover.md`, `tests/cli_runtime/test_chatgpt_cli.py` | fresh plan review PASS後にS05実装を開始する |

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
| EAL-011 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-20260804/brief-full.md` | chatgpt-use-plan-clarification | S03/S04 を一つの deployable change-set とし、S03 は application path-only contract/caller、S04 は direct repeated `--file` transport を担当する計画補正案を採用した。両 closure は同一 resulting HEAD でのみ closeする | `plan.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md`, `report.md` | S03/S04 execution boundary、union allowlist、closure coupling | 現行コードの bytes producer と generated-pack consumer を既承認の path-only/direct transport 設計へ整合させるための最小補正。v1/v2 reviewのP1を修正し、v3 fresh review PASSで実装開始前ゲートを通過した。v8 code review PASSによりS03/S04 closureも完了し、S05以降の責務は変更しない | advisory_plan | `/private/tmp/codex-agent-work/501/s03-s04-plan-20260804/brief-full.md` (SHA-256 `3286db64b54a82c67237a637a9fad4bd4a9443b9f8e29590de97edccbd4ae2ea`), base HEAD `a2bc5e00cf7aefe049c234bfe0207f992077af8f`, v3 plan review PASS, v8 code review PASS | issue orchestrator | ChatGPT-Use | no | EAL-011は採用済みのatomic execution boundaryとして保持し、S05以降は各stepの実装ブリーフとreview gateを経て進める |
| EAL-012 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-20260805/review.md` | chatgpt-use-red-team | exact branch HEAD `dada1f403241f615340ae1f0f8fb28b047edae75` に対する fresh defect-only plan review は FAIL（P0=0/P1=3）であり、RT-354-S03S04-001〜003を修正入力として採用した | `plan.md`, `report.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` | S03/S04 atomic allowlist、resource/e2e contract、EAL gate | Red Teamはread-onlyで、Candidate、canonical docs、repositoryを変更していない。P1三件だけを修正対象とし、アーキテクチャ再設計や提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-20260805/review.md` (SHA-256 `7be36264dae97ec8718dc93e12400b9c8736f1a8015547f3d26d92387fff5c06`), review identity SHA-256 `d660016800b378b9fbd689a18ed3d41af0a1c4aa5e380ada6bbdd064df3e2a05` | issue orchestrator | ChatGPT-Use Red Team | no | v2 repairを反映した新しいHEADをfresh Red Teamで再レビューする |
| EAL-013 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-v2-20260805/review-short.md` | chatgpt-use-red-team | exact branch HEAD `18db33044221204b3cc1d856f78570ee6523ac48` に対する fresh defect-only plan review v2 は FAIL（P0=0/P1=2）であり、RT-354-S03S04-V2-001〜002を修正入力として採用した | `plan.md`, `report.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` | S03/S04 execution-card allowlist、focused verification、same-HEAD closure | Red Teamはread-onlyで、Candidate、canonical docs、repositoryを変更していない。指摘はresource identity契約の許可範囲とfull-chain e2e検証の明示不足に限定され、アーキテクチャ再設計や改善提案はない | fresh_fail | `reviews/red-team-review-s03-s04-plan-v2.md` (SHA-256 `a7b866a54c753d6e8619404e113afba08615037e22fd0dd98114601261bc7c75`), review identity SHA-256 `2d2e1b4e35b4dd2d2e44ad34289af2408cc3263bc3537f5fa8a97b98d0792c71` | issue orchestrator | ChatGPT-Use Red Team | no | v3修正を反映した新しいHEADのfresh Red Team PASSにより履歴として確定し、S03/S04実装へ進む |
| EAL-014 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-plan-review-v3-20260805/review.md` | chatgpt-use-red-team | exact branch HEAD `961a8b8370ed7e3e4cd162ebe15a55ef61101fe1` に対する fresh defect-only plan review v3 は PASS（P0=0/P1=0/P2=0/P3=0）であり、S03/S04 atomic planを実装準備済み入力として扱える | `plan.md`, `report.md`, `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` | S03/S04 execution-card allowlist、focused verification、same-HEAD closure | Red Teamはnamed branchとGitHub exact HEAD/blobを確認し、Candidate、canonical docs、repositoryを変更していない。v2 P1二件は解消済みで、アーキテクチャ再設計や改善提案はない | fresh_pass | `reviews/red-team-review-s03-s04-plan-v3.md` (SHA-256 `6df048185086aeabd946eeb5c22d5b13fea5624942982a786426744802d78455`), review identity SHA-256 `ff189b9807e43b1a6391c811484a448eba3c46b93c10d42c4798710a11c09fed` | issue orchestrator | ChatGPT-Use Red Team | no | S03/S04専用実装ブリーフを作成し、atomic implementationを同一 resulting HEADで開始する。Luna/Maxは未確認のまま主張しない |
| EAL-015 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-implementation-brief-20260805/brief-final.md` | chatgpt-use-implementation-brief | exact branch HEAD `8b44eb6da5d8be4f2178ce3be09d25e968f14747` を対象に、S03/S04を同一 atomic change-set として実装するための path-only producer、direct repeated `--file` consumer、Review identity body、allowlist、focused verification、停止条件を具体化した | `artifacts/implementation-briefs/s03-s04-atomic-implementation-brief-20260805.md`, `artifacts/implementation-briefs/s03-input-path-model-v2.md`, `artifacts/implementation-briefs/s04-direct-attachment-transport.md`, `report.md` | S03/S04 implementation preparation and step evidence | ChatGPT-Use の出力を変更せず三つの role-specific artifactへ byte-identical にコピーし、SHA-256一致を確認した。これは advisory brief であり、レビューPASS、実装完了、assurance昇格を意味しない | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-implementation-brief-20260805/brief-final.md` (SHA-256 `631b24e9d852e15d9a61ca429cb8da12293b571e362eb33afa3c1232b288971e`), session `iss354-s03-s04-implementa-brief-7` | issue orchestrator | ChatGPT-Use | no | S03/S04 dev-coderへ同一ブリーフを引き継ぎ、同一 resulting HEADで実装・検証する。GPT-5.6 Luna / Reasoning Effort Maxの実測証跡は未確認のため主張しない |
| EAL-016 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-implementation-20260805/rebind.md` | chatgpt-use-implementation-brief-identity-rebind | S03/S04実装ブリーフを、コミット後の named branch exact HEAD `f2238d12313b36a002185d3e101154c20f19993c` へ再結合した。`8b44eb6` から `f2238d1` は report と implementation-brief artifact の docs-only lineage で、provider runtime、対象テスト、canonical requirement/design/plan、Review resourceには差分がないことを確認した | `artifacts/implementation-briefs/s03-s04-implementation-identity-rebind-20260805.md`, `report.md` | implementation baseline identity and docs-only lineage | addendumは元ブリーフのscope、不変条件、allowlist、検証、停止条件を変更せず、source identityとworker preconditionのみを補足する。GPT-5.6 Luna / Reasoning Effort Maxは未確認のため主張しない | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-implementation-20260805/rebind.md` (SHA-256 `42435793d23e4032bf2d902da8f7a93fa5bf66c3a68a5f9d539618d70c8ced2d`), session `iss354-s03-s04-identity-rebind` | issue orchestrator | ChatGPT-Use | no | `f2238d1` をruntime/test baselineとしてworkerへ引き継ぎ、S03/S04を同一 resulting HEADで実装・検証する |
| EAL-017 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v1-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `458fa4a130be05c3a6ed0ad675639148b604f91a` に対するfresh defect-only Red Team code reviewはFAIL（P0=0/P1=4/P2=0/P3=0）であり、RT-354-S03S04-CODE-001〜004をBlue修正入力として採用した | `reviews/red-team-review-s03-s04-code-v1.md`, `report.md` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、provider/projection、runtime、resource、指定5テストをread-onlyで確認し、repositoryとCandidateを変更していない。指摘はrepository-relative path表現、application projection parity、必須no-inspection/no-materialization test evidence、implementation report closureの欠落に限定され、アーキテクチャ再設計はない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v1-20260805/review.md` (SHA-256 `9de26415ebca05c5a902710703bd9ff45430d9cf48544a877aeec851337a8ce3`), session `iss354-s03-s04-code-review` | issue orchestrator | ChatGPT-Use Red Team | no | P0/P1を修正した新しいBlue resulting HEADをpushし、別Fresh Red Team threadで再レビューする。S03/S04 closureとS05開始は保留 |
| EAL-018 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-implementation-20260805/rebind.md`, `reviews/red-team-review-s03-s04-code-v1.md` | implementation-and-repair | exact implementation HEAD `836a9c7372879747a24b7785e9484a9e9dfc2f3b` に、CODE-001〜004の修正（lexical repository-relative paths、application projection parity、no-inspection/no-materialization spies、report evidence update）を反映し、provider/projection/test parityと検証結果を確認した | provider runtime、projection、resource、unit/integration tests、report | S03/S04 implementation closure and next fresh code-review target | v1 FAILは修正入力として保持し、Blue修正は同一resulting HEAD `836a9c73` に集約した。P0/P1の再判定は新規Fresh Red Team v2でのみ行い、現時点ではS03/S04 closureを未完了として扱う | repair_applied | fix commit `836a9c7372879747a24b7785e9484a9e9dfc2f3b`; local/remote exact HEAD parity; tests and static checks recorded in current implementation section | issue orchestrator | Blue implementation | no | 新規fresh v2 code reviewでexact HEAD `836a9c73` を確認するまで、closure、S05、PRを開始しない |
| EAL-019 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v2-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `5813ad0d97510110c498102cbe18c7b4556d104c` に対するv1とは別のfresh defect-only code reviewはFAIL（P0=0/P1=2/P2=0/P3=0）。V2-001（direct transportのinput-side read/copy/ZIP/hash spy不足）とV2-002（report current-state/closure ID/exact review identity/必須証跡の不整合）をBlue修正入力として採用した | `reviews/red-team-review-s03-s04-code-v2.md`, `report.md`, `tests/unit/infra/test_issue_planning_chatgpt.py` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、provider/projection、runtime、resource、指定testをread-onlyで確認し、repositoryを変更していない。P1二件だけを修正対象とし、アーキテクチャ再設計や改善提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v2-20260805/review.md` (SHA-256 `0757413f2002b3782f52402903a8b71eafa5f8e1ad57d3c6d091575afa6f37f8`), session `iss354-s03-s04-code-review-2`; implementation test repair commit `0586f151407ff95aeb4ef8b72d18a019b5d7a1a8` | issue orchestrator | ChatGPT-Use Red Team | no | 新しいcurrent report identityを含むBlue修正HEADをpushし、v3 fresh code reviewで再判定する。S03/S04 closure、S05、PRは保留 |
| EAL-020 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `91781cf507f979b02ba3ceb0a0610f2815114ec8` に対するv1/v2とは別のfresh defect-only code reviewはFAIL（P0=0/P1=1/P2=0/P3=0）。`RT-354-S03S04-V3-001` はmixed repository-relative/absolute operandとOracle subprocess `cwd=repo_root`を同時に固定する回帰テスト証跡不足を指摘した | `reviews/red-team-review-s03-s04-code-v3.md`, `report.md`, `tests/unit/infra/test_issue_planning_chatgpt.py`, `tests/integration/test_issue_planning_e2e.py` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub named branchのexact HEADを確認し、repository、canonical docs、tests、review artifactsを変更していない。P1一件だけを最小修正入力として採用し、production runtime・設計・S05以降は変更しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/review.md` (SHA-256 `17a35426d2bd3149b783e55c962ac34a27755f864936abe021a6827a22f3d69c`), session `iss354-s03-s04-review-v3b`; model requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | EAL-021の最小test repairを新しいpushed exact HEADへ束ね、v1〜v3とは別のFresh Red Team v4でP0/P1=0を確認する。S03/S04 closure、S05、PRは保留 |
| EAL-021 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/blue-repair-brief2.md` | chatgpt-use-implementation-brief | exact branch HEAD `91781cf507f979b02ba3ceb0a0610f2815114ec8` に対するP1最小修正として、mixed absolute/relative operand、input no-inspection guard、argv lexical identity、explicit `cwd=repo_root` assertionをtest-onlyで具体化した。実装ブリーフはChatGPT-Use本文-onlyで取得し、添付送信障害を回避した | `artifacts/implementation-briefs/s03-s04-v3-repair-brief-20260805.md`, `tests/unit/infra/test_issue_planning_chatgpt.py`, `tests/integration/test_issue_planning_e2e.py`, `report.md` | Blue repair scope and step evidence | ブリーフは出力をbyte-identicalに保存し、SHA-256一致を確認した。GPT-5.6 Luna / Reasoning Effort Maxの実測は未確認で、requested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`のみ記録する。production runtime、provider projection、要件・設計・計画、S05以降は変更しない | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/blue-repair-brief2.md` (SHA-256 `553fa26fd28875eda9e80a7c1b6f75e8fc459ccbc7bfa8aee5523275c93be344`), session `iss354-s03-s04-brief-v3b`; follow-up sessionはChat/Work判定不能、添付送信は600秒で投入前停止 | issue orchestrator | ChatGPT-Use | no | test-only repairをcommit/pushし、検証証跡とともに別Fresh Red Team v4へ渡す |
| EAL-022 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `150d81a3e1a98e1f3e9776743e8376c28a7c7184` に対するv1〜v3とは別のfresh defect-only code reviewはFAIL（P0=0/P1=2/P2=0/P3=0）。`RT-354-S03S04-V4-001` はrepository外absolute Candidateを同一infra invocationへ渡す実テスト不足、`RT-354-S03S04-V4-002` はcommit済みHEADとreportのcurrent-state/必須検証証跡不整合を指摘した | `reviews/red-team-review-s03-s04-code-v4.md`, `report.md`, `tests/unit/infra/test_issue_planning_chatgpt.py` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、runtime、tests、既存reviewをread-onlyで確認し、repository、Candidate、canonical artifactsを変更していない。P1二件だけを修正対象とし、アーキテクチャ再設計、production runtime変更、S05以降の提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/review.md` (SHA-256 `0efea79260633b5fab656a7ce7f5bfb79f148c46376a68171bc7f3656722398d`), session `iss354-s03-s04-code-review-5`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | EAL-023のtest/report最小修正を新しいpushed exact HEADへ束ね、v5 Fresh Red Teamで再判定する |
| EAL-023 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/blue-repair-brief.md` | chatgpt-use-implementation-brief | exact branch HEAD `150d81a3e1a98e1f3e9776743e8376c28a7c7184` のv4 P1二件を、direct transport unit testのrepo外Candidate fixture追加とcanonical reportの履歴・検証証跡整合に限定して修正するブリーフを取得した | `artifacts/implementation-briefs/s03-s04-v4-repair-brief-20260805.md`, `tests/unit/infra/test_issue_planning_chatgpt.py`, `report.md` | Blue repair scope and step evidence | ブリーフは本文-only送信で取得し、byte-identicalに保存した。添付なしでもGitHub named branch/HEADを明示し、model evidenceはwrapperの実測値だけを記録する。production runtime、projection、要件・設計・計画、S05以降は変更しない | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/blue-repair-brief.md` (SHA-256 `d5fdf4c91e679cc7dc324ace5c5b5f786d99e575e3fea9f27f6ff7e979665c47`), session `iss354-s03-s04-brief-v4b`; `--reasoning-effort max`指定はAPI経路へ切替り送信前に失敗、browser current経路で再実行 | issue orchestrator | ChatGPT-Use | no | test/report修正、必須verification、commit/push後のv5 Fresh Red Teamへ渡す |
| EAL-024 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `827e439d20557ef99e05f8ac844310915acce704` に対するv1〜v4とは別のfresh defect-only code reviewはFAIL（P0=0/P1=1/P2=0/P3=0）。`RT-354-S03S04-V5-001` は、push済みcurrent HEADをreportのidentity/verification ledgerへ束縛せず、current欄にpush前を示す同義表現を残している不整合を指摘した。V4-001は解消済みと確認された | `reviews/red-team-review-s03-s04-code-v5.md`, `report.md` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、runtime、tests、v1〜v4 reviewをread-onlyで確認し、repositoryやartifactsを変更していない。P1一件だけを修正対象とし、コード変更、アーキテクチャ再設計、S05以降の提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/review.md` (SHA-256 `82c0b6bcea5852a3b199c84cc9b1178a16e5f02627bf26955bd2d5ad155043d8`), session `iss354-s03-s04-code-review-6`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | EAL-025のreport-only修正を新しいpushed exact HEADへ束ね、v6 Fresh Red Teamで再判定する |
| EAL-025 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/blue-repair-brief.md` | chatgpt-use-implementation-brief | exact branch HEAD `827e439d20557ef99e05f8ac844310915acce704` のV5-001を、canonical reportのcurrent identity、commit ledger、final gates、次ゲート表現の記録整合だけで修正するブリーフを取得した | `artifacts/implementation-briefs/s03-s04-v5-repair-brief-20260805.md`, `report.md` | Blue repair scope and step evidence | ブリーフは本文-only送信で取得し、byte-identicalに保存した。既存v1〜v5履歴を保持し、production/test/spec変更を禁止する。モデル証跡はwrapperの実測値だけを記録する | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/blue-repair-brief.md` (SHA-256 `1f5577bed5163bab8c2397be5c9ba2f78046723bff4cf3e780ac25986ef11d9b`), session `iss354-s03-s04-brief-v5`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, verified `no` | issue orchestrator | ChatGPT-Use | no | report-only修正、commit/push後のv6 Fresh Red Teamへ渡す |
| EAL-026 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `3b0d255d38272b431c364cdf65daeac2786b7ead` に対するv1〜v5とは別のfresh defect-only code reviewはFAIL（P0=0/P1=1/P2=0/P3=0）。`RT-354-S03S04-V6-001` は、v5 reviewed source `827e439d` のfull SHAがcommit ledgerから欠落し、Delegated Worker Evidenceにpush前の時制が残る不整合を指摘した。`3b0d`自身のreport内自己参照はfindingではない | `reviews/red-team-review-s03-s04-code-v6.md`, `report.md` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、runtime、tests、v1〜v5 reviewをread-onlyで確認し、repositoryやartifactsを変更していない。P1一件だけをreport-only修正対象とし、コード変更、アーキテクチャ再設計、S05以降の提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/review.md` (SHA-256 `ecb2c8c6634af7d70d4d4bb39eb930f3c5da9fa61864e59e17624bf7f521a29a`), session `iss354-s03-s04-code-review-7`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | EAL-027のreport-only修正を新しいpushed exact HEADへ束ね、v7 Fresh Red Teamで再判定する |
| EAL-027 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/blue-repair-brief.md` | chatgpt-use-implementation-brief | exact branch HEAD `3b0d255d38272b431c364cdf65daeac2786b7ead` のV6-001を、canonical reportのcommit ledgerとDelegated Worker Evidenceの2箇所だけで修正し、v1〜v6履歴とidentityを保持するブリーフを取得した | `artifacts/implementation-briefs/s03-s04-v6-repair-brief-20260805.md`, `report.md` | Blue repair scope and step evidence | ブリーフはGitHub exact identityとread-only reviewを確認した上でbyte-identicalに保存した。production/test/spec変更、review artifactの変更、self-reference要件の追加を禁止する。モデル証跡はwrapperの実測値だけを記録する | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/blue-repair-brief.md` (SHA-256 `18387e7a4b3f043a71152f83f1215479b724014b0b48990181d1906435bea258`), session `iss354-s03-s04-blue-repair-v6`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use | no | report-only修正、commit/push後のv7 Fresh Red Teamへ渡す |
| EAL-028 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `48b0c86ee7e58ae8b971c15b14a3249db577e6d5` に対するv1〜v6とは別のfresh defect-only code reviewはFAIL（P0=0/P1=1/P2=0/P3=0）。`RT-354-S03S04-V6-001` のうちcommit ledgerは解消されたが、S03-S04 workerの親統合判断にv6 report-only pushを将来条件とする時制が残っていた | `reviews/red-team-review-s03-s04-code-v7.md`, `report.md` | S03/S04 implementation gate and repair boundary | Red TeamはGitHub exact HEAD、canonical docs、runtime、tests、v1〜v6 reviewをread-onlyで確認し、repositoryやartifactsを変更していない。P1一件だけをreport-only修正対象とし、コード変更、アーキテクチャ再設計、S05以降の提案は採用しない | fresh_fail | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/review.md` (SHA-256 `ae1fe0a99d9c174689057cb2eb5bd996861b5c0277d407c9c11b5120c8e771a0`), session `iss354-s03-s04-code-review-8`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | EAL-029のreport-only修正を新しいpushed exact HEADへ束ね、v8 Fresh Red Teamで再判定する |
| EAL-029 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/blue-repair-brief.md` | chatgpt-use-implementation-brief | exact branch HEAD `48b0c86ee7e58ae8b971c15b14a3249db577e6d5` のV6-001残存時制を、S03-S04 worker親統合判断の1行置換だけで修正し、v1〜v7履歴とidentityを保持するブリーフを取得した | `artifacts/implementation-briefs/s03-s04-v7-repair-brief-20260805.md`, `report.md` | Blue repair scope and step evidence | ブリーフはGitHub exact identityとread-only reviewを確認した上で取得した。reportの1文字列置換以外の変更、self-reference、runtime/test/spec変更を禁止する。モデル証跡はwrapperの実測値だけを記録する | advisory_adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/blue-repair-brief.md` (SHA-256 `328820cb0acbca1ca9d9b1902ed5bd08af5ba5eed364d8892d24dd596da8dbd`), session `iss354-s03-s04-blue-repair-2`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use | no | report-only修正、commit/push後のv8 Fresh Red Teamへ渡す |
| EAL-030 | adopted | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v8-20260805/review.md` | chatgpt-use-red-team-code | exact branch HEAD `366ea40c2a2783098cbce0750809e20567ab5445` に対するv1〜v7とは別のfresh defect-only code reviewはPASS（P0=0/P1=0/P2=0/P3=0）。`RT-354-S03S04-V6-001` のcommit ledger・worker時制とも解消済みで、runtime/test/specへの追加変更はない | `reviews/red-team-review-s03-s04-code-v8.md`, `report.md` | S03/S04 implementation gate and closure | Red TeamはGitHub exact HEAD、canonical docs、runtime、tests、v1〜v7 reviewをread-onlyで確認し、repositoryやartifactsを変更していない。アーキテクチャ再設計や改善提案はなく、P0/P1なしのためPASSを採用する | fresh_pass | `/private/tmp/codex-agent-work/501/s03-s04-code-review-v8-20260805/review.md` (SHA-256 `a126d359ee57389edc6d4f6a9793204158e8e10b029e1c68ac68e0d456c9a1b8`), session `iss354-s03-s04-code-review-9`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use Red Team | no | v8 PASSをS03/S04 same-HEAD closureへ採用し、S05実装前ブリーフへ進む |
| EAL-031 | adopted | `/private/tmp/iss-00354-s05-implementation-brief-20260805/brief.md` | chatgpt-use-implementation-brief | S05実装前ブリーフは、旧CLI help契約を同期するテスト許可境界の不足を検出し、実装開始を停止した。S05 execution cardへ prompt synthesis、CLI help、prompt test、transport/lifecycle testの最小許可パスを追加する補正を採用した | `plan.md`, `artifacts/implementation-briefs/s05-orchestration-cli-cutover.md`, `report.md` | S05 execution-card allowlist and pre-implementation gate | named branch exact HEADとGitHub parityを確認したうえで、S05のproduction scopeを拡張せず、既存 hard cutover のテスト同期だけを計画へ反映した。ブリーフ出力はBLOCKEDであり、計画補正とfresh plan reviewが完了するまで実装開始・コード変更は行わない | advisory_blocked | `/private/tmp/iss-00354-s05-implementation-brief-20260805/brief.md` (SHA-256 `1cc61ef724dbe958129632cae3f6c63578b7e3fee833eccad634d9dc32ff6699`), session `iss354-s05-brief-20260805`; requested `gpt-5.6`, target `GPT-5.6 Sol`, resolved `Pro`, strategy `current`, verified `no` | issue orchestrator | ChatGPT-Use | no | fresh exact-HEAD plan reviewでallowlist補正とS05 hard-cutover契約を確認し、PASS後に新しいS05実装ブリーフへ再結合する |

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
- S01 の実装ブリーフは `artifacts/implementation-briefs/s01-capability-characterization.md`、S02 の実装ブリーフは `artifacts/implementation-briefs/s02-operation-resources.md`、S03/S04 の atomic 実装ブリーフは `artifacts/implementation-briefs/s03-s04-atomic-implementation-brief-20260805.md`、`s03-input-path-model-v2.md`、`s04-direct-attachment-transport.md` に配置した。S03/S04 v3〜v7修正ブリーフは `artifacts/implementation-briefs/s03-s04-v3-repair-brief-20260805.md`、`s03-s04-v4-repair-brief-20260805.md`、`s03-s04-v5-repair-brief-20260805.md`、`s03-s04-v6-repair-brief-20260805.md`、`s03-s04-v7-repair-brief-20260805.md` に保存した。S03/S04 runtimeは`836a9c7372879747a24b7785e9484a9e9dfc2f3b`、v2 P1修正テストは`0586f151407ff95aeb4ef8b72d18a019b5d7a1a8`、v3/v4 test/report修正は`150d81a3e1a98e1f3e9776743e8376c28a7c7184`、v4修正とv5レビュー証跡は`827e439d20557ef99e05f8ac844310915acce704`、v5 report-only更新後のv6レビュー対象は`3b0d255d38272b431c364cdf65daeac2786b7ead`、v8レビュー対象は`366ea40c2a2783098cbce0750809e20567ab5445`としてGitHub branchにpush済みである。v8 Fresh Red TeamはP0/P1=0のPASSとなり、S03/S04 same-HEAD closureを完了した。S05〜S13、PR、merge、Issue closeは未実施である。

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
| S03-S04 | implementation | S03 path-only producer/caller と S04 direct repeated `--file` transportをatomic change-setとして実装し、same-HEAD closureに結び付ける | runtime `836a9c...`、input-side spy修正 `0586f151...`、v3/v4 repair `150d81a3...`、v5 report-only修正 `827e439d...`、v6 review source `3b0d255d...`、v7 report-only修正 `366ea40c...` | exact branch HEAD / GitHub parity、実装ブリーフ、Fresh Red Team code review v1〜v8 | green; v8 fresh review PASS | v1〜v7のP1修正入力を保持し、v8 PASS（P0=0/P1=0）を同一 reviewed HEAD `366ea40c...`で確認。S03/S04 closureを完了し、S05へ進む |
| S05〜S13 | implementation preparation | inspect-only until each step's brief and execution gate | no execution evidence yet; executable step contracts remain in plan.md | docs inspection and runtime gate commands | pending | implementation evidence is collected per step |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | strict version parsing, preflight failure, argv and recovery boundary cases | ChatGPT-Use implementation review v2 and native Oracle probe | strict parser, timeout/nonzero/argv tests, and sanitized directory/multiple/continuation receipt recorded; no plan amendment | `cl-s01-capability` | no | remote post-upload attachment-failure stage is deferred to S10 |
| S02 | issue planning resources/application contract の回帰検証（prompt read/text binding / caller binding / invalid input） | Red Team review-v2 + 実行テスト | planning resources operations 3種、issue_planning_prompt caller identity binding、runtime caller context整合チェックを追加 | `cl-s02-profile` / `tc-s02-001` | no | P0/P1/P2/P3=0 でpass；identity SHA `10453a1669f2d64b462ad332177a69a70099cb91ac97ff9c312910f77e3ca760` |
| S03-S04 | path-only/no-materialization transport regression、provider/projection parity、same-HEAD closure | S03/S04 implementation brief + Red Team v1〜v8 findings | lexical path operands、direct `--file` order、opaque attachment-directory spies、external Path identity、repo外absolute Candidate、provider/projection parity、input-side read/open/tree/copy/ZIP/hash spies、current report identityを実装・検証し、v1〜v7のP1を修正入力として保持した上でv8 PASSを確認 | `cl-s03-path-input` / `tc-s03-001` / `cl-s04-direct-transport` / `tc-s04-001` | no | runtime `836a9c...`、test repair `0586f151...`、v3/v4 repair `150d81a3...`、v5 current identity review `827e439d...`、v6 report identity review `3b0d255d...`、v7 report-only修正 `366ea40c...`、focused/full tests、domain、validate、provider update、parity、legacy zero-match、diff-check、v8 fresh review PASS |
| S05〜S13 | no execution tests yet; closure risks are enumerated in plan.md | plan | no implementation response yet | `cl-s05-profile`〜`cl-s13-closure` | no | each step requires its own brief and evidence |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `cl-s01-capability` | strict preflight receipt, fail-closed unsupported capability, 0.16.1 regression tests, and direct capability receipt | implementation, focused test, exact HEAD, and sanitized live receipt recorded; remote post-upload failure stage explicitly deferred to S10 | closed | directory/multiple/continuation supported; S02 may start |
| S02 | `cl-s02-profile`, `tc-s02-001` | issue planning prompt/application contract の実装と、full identity binding・prompt-minimal化の検証 | focused/unit tests, lint/type validation, `spec-dock validate .`、parity確認、diff-check | closed | resources operations 3種とissue_planning caller bindingが反映 |
| S03-S04 | `cl-s03-path-input`, `tc-s03-001`, `cl-s04-direct-transport`, `tc-s04-001` | path-only producer/caller、direct repeated `--file` transport、no-inspection/no-materialization tests、provider/projection parity、同一 resulting HEAD | runtimeは`836a9c7372879747a24b7785e9484a9e9dfc2f3b`、入力側spy修正は`0586f151407ff95aeb4ef8b72d18a019b5d7a1a8`、v3/v4 repairとreportは`150d81a3...`、v5 reviewとcurrent identity修正起点は`827e439d...`、v6 review sourceは`3b0d255d...`、v7修正とv8 PASSは`366ea40c...`へ反映済み。v8 fresh reviewはP0/P1=0で、同一 reviewed HEAD上のS03/S04 closureを完了 | closed | v8 PASS（P0=0/P1=0）を根拠にS03/S04を同一 reviewed HEAD `366ea40c...`でclose |
| S05〜S13 | `cl-s05-profile`〜`cl-s13-closure` | per-step behavior slice and gate in plan.md | no implementation observation yet; closure is pending execution | pending | implementation must populate each row per step |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `cl-s01-capability` | S01 | yes | implementation | focused pytest, infra subset, full infra, ruff, mypy, diff check, and sanitized direct capability receipt | executed; all code/static checks pass and receipt recorded | pass | remote post-upload failure stage is a later S10 obligation |
| `cl-s02-profile` | S02 | yes | implementation | focused pytest, unit pytest, ruff、mypy、validate、diff-check | close by this commit; P0/P1/P2/P3=0, review-v2 pass | pass | test evidence links to review `s02-review-v2-20260804` |
| `tc-s02-001` | S02 | yes | implementation | focused pytest, unit pytest, ruff、mypy、validate、diff-check | close by this commit; P0/P1/P2/P3=0, review-v2 pass | pass | test evidence links to review `s02-review-v2-20260804` |
| `cl-s03-path-input` | S03 | yes | implementation | S03/S04 atomic plan、v3 fresh plan review PASS、S03/S04 implementation brief、identity rebind、Blue repair `0586f151...`、v4/v5/v6/v7 repair brief、v8 review PASS | focused/unit/integration suites、provider/projection parity、lexical path/no-inspection spies、repo外absolute Candidate fixture、current report identity | pass | v8 Fresh Red TeamでP0/P1=0を確認し、同一 reviewed HEAD `366ea40c...`でclose |
| `tc-s03-001` | S03 | yes | implementation | v3 plan review PASS、S03/S04 implementation brief、Blue repair `0586f151...`、v4/v5/v6/v7 repair brief、v8 review PASS | nested/hidden/symlink/FIFO、dynamic path no-inspection spies、lexical path assertions、repo外Candidate、current identity ledger | pass | same reviewed HEAD `366ea40c...`でclose |
| `cl-s04-direct-transport` | S04 | yes | implementation | S03/S04 implementation brief、identity rebind、Blue repair commit `0586f151...`、v4/v5/v6/v7 repair brief、v8 review PASS | direct transport input-side no-materialization spies（read/open/tree/copy/ZIP/hash）、repeated `--file` argv and order、external Path identity、repo外absolute Candidate | pass | same reviewed HEAD `366ea40c...`でclose |
| `tc-s04-001` | S04 | yes | implementation | S03/S04 implementation brief、Blue repair `0586f151...`、v4/v5/v6/v7 repair brief、v8 review PASS | full-regression integration subset plus transport-focused tests、input-side read/open/tree/copy/ZIP/hash spies、repo外Candidate | pass | same reviewed HEAD `366ea40c...`でclose |
| `cl-s05-profile`〜`cl-s13-closure` | S05〜S13 | yes | inspect-only before implementation | runtime gate and per-step test command to be added at execution | not executed | pending | closure evidence is required during execution |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-s01-capability` | S01 | exact-HEAD test/static command output and live Oracle capability probe | code/static checks pass; directory/multiple/continuation supported; missing-path preflight fail-closed; remote post-upload failure stage unknown | pass | S02 may start; S10 must characterize remaining stage |
| `cl-s02-profile` / `tc-s02-001` | S02 | execution-specific command output | exact-HEAD S02 evidence and red-team v2 の結果を report に反映 | closed | implementation will proceed to S03 |
| `cl-s03-path-input` / `tc-s03-001` | S03 | S03/S04 implementation brief、Blue repair commit `0586f151...`、v3/v4 repair `150d81a3...`、v5 identity ledger `827e439d...`、v6 review source `3b0d255d...`、v7 repair `366ea40c...`、focused/full tests、lexical/no-inspection spies、provider/projection parity | implementation evidence is recorded; v8 review at `366ea40c...` is PASS（P0=0/P1=0） | closed | same reviewed HEAD `366ea40c...`でclose |
| `cl-s04-direct-transport` / `tc-s04-001` | S04 | direct repeated `--file` argv/order、input-side read/open/tree/copy/ZIP/hash spies、external Path identity、repo外Candidate、full-chain integration | input-side/path-location spies are implemented; v8 review at `366ea40c...` is PASS（P0=0/P1=0） | closed | close only with S03 on the same resulting HEAD |
| `cl-s05-profile`〜`cl-s13-closure` | S05〜S13 | execution-specific command output | not observed before implementation | pending | implementation will populate each row |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `cl-s01-capability` / `cl-s02-profile` / `tc-s02-001` | no alias | `cl-s02-profile` / `tc-s02-001` はclosedとして解決 | no plan amendment before implementation | no | no |
| repair | `cl-s03-path-input` / `tc-s03-001` / `cl-s04-direct-transport` / `tc-s04-001` | no alias | runtimeは`836a9c73...`、v2 P1×2の入力側spy修正は`0586f151...`、v3/v4 test/report修正は`150d81a3...`、v5 review/current identity修正起点は`827e439d...`、v6/v7 report ledger・時制修正は`3b0d255d...` / `366ea40c...`へ反映し、v8 PASSで同一 reviewed HEADのclosureを解決した | no | yes |
| none | `cl-s05-profile`〜`cl-s13-closure` | no alias | same closure ids are retained from plan.md | no plan amendment before implementation | no | no |

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
| S03-S04 | completed-and-closed | implementation with per-step ChatGPT-Use briefs | dev-coder | S03/S04 union allowlist in plan.md、v2 atomic addendum、v3 plan review、implementation brief、v4/v5/v6/v7 repair brief | plan.md and current Issue scope | runtime、Review resource identity contract、e2e fixture、unit/transport tests、provider-sync projection as generated output、report evidence | no bridge、generated pack、CLI/profile/recovery change、merge or close; both closures require same resulting HEAD | S03/S04 briefs、focused suite、legacy search zero-match、provider sync/parity、validate、scope audit、v1-v8 fresh code review、report closure | any out-of-allowlist production change or S03/S04 same-HEAD failure | v8 Fresh Red Team PASS at `366ea40c...`; S03/S04 same-HEAD closure is complete; begin S05 after evidence commit |
| S05-S13 | pending-next-step | implementation with per-step ChatGPT-Use brief | dev-coder | step-local allowed paths in plan.md | plan.md and current Issue scope | only the active step's allowed files | no execution before active step brief/review, no merge or close | per-step brief, tests, report closure | active step gate or capability ambiguity | begin S05 after S03/S04 same-HEAD closure |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Implemented strict preflight receipt and 0.16.1 regression-boundary tests within the approved provider infra scope | `issue_planning_chatgpt.py`, `test_issue_planning_chatgpt.py` | 92 focused tests; 60 infra subset; 507 infra tests passed/573 skipped; ruff/mypy/diff check passed | ChatGPT-Use Fresh Red Team v2 PASS (P0=0/P1=0, P2=1) | remote post-upload attachment-failure stage remains unknown for S10 | parent integration records exact HEAD and sanitized capability receipt |
| S02 | dev-coder | issue planning resources のoperations化とapplication contract/caller bindingの修正を実施 | `artifacts/implementation-briefs/s02-operation-resources.md`, `issue_planning_prompt.py`, `issue_planning.py`, `test_issue_planning_prompt.py` | focused 144 passed; unit 1471 passed, 573 skipped; ruff/mypy/validate/diff-check | ChatGPT-Use Fresh Red Team review-v2 PASS (P0/P1/P2/P3=0) | no unresolved S01 blocker; remote attachment-failure stage remains S10 scope | parent integration records exact HEAD, identity SHA, and scope expansion note |
| S03-S04 | dev-coder | S03 path-only contract/caller とS04 direct transportをatomic change-setとして実装し、v1/v2のP1を修正後、v3 P1×1のmixed-path/cwd回帰テスト、v4 P1×2のrepo外Candidate/report整合、v5 P1×1のcurrent identity整合を追加した | provider runtime/application/prompt/infra、Review resource、projection、unit/integration tests、v3〜v7 repair brief/review artifact | 既存証跡: `uv run pytest -q` -> 1472 passed / 2252 skipped、infra unit -> 93 passed、domain -> 88 passed、full-regression integration -> 11 passed、validate/update/parity/legacy search/diff-check pass。v3修正: focused unit -> 1 passed、infra unit -> 93 passed、e2e -> 4 passed、ruff/diff-check pass。v8 reviewでP0/P1=0を確認し、runtime/test/specを追加変更せず同一 reviewed HEADのclosureを完了 | Fresh Red Team v1 FAIL (P1×4); repair `836a9c73...`; v2 at `5813ad0...` FAIL (P1×2); repair `0586f151...`; v3 at `91781cf...` FAIL (P1×1); v4 at `150d81a3...` FAIL (P1×2); v5 at `827e439d...` FAIL (P1×1); v6 at `3b0d255d...` FAIL (P1×1); v7 at `48b0c86...` FAIL (P1×1); v8 at `366ea40c...` PASS (P0/P1=0) | v8 PASSを同一 reviewed HEADで採用し、S03/S04両closureをcloseしてS05へ進む |
| S05-S13 | dev-coder | not started; S03/S04 atomic closure待ち | none | not executed | pending | S03/S04 same resulting HEAD closureが前提 | begin after S03/S04 implementation review PASS |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | no delegation exception; code implementation was delegated within the approved provider infra scope | user request to implement and review; risk accepted: no | provider infra source/test and report evidence | S01 implementation, verification, and report update | no rollback needed; immutable Candidate v2 retained | focused/full infra tests, diff check, fresh ChatGPT review, and sanitized capability receipt | S01 review PASS; remote post-upload failure stage deferred to S10 | continue to S02; no merge or close |
| S02 | no delegation exception; application contract / caller-binding修正でS02 stepを実施 | user request to implement and review; risk accepted: no | S02 scope files in plan.md（application prompt and issue_planning） | per-step implementation and report evidence | no rollback needed; immutable Candidate v2 retained | focused/unit tests, ruff/mypy/validate/diff-check, and red-team review-v2 | active step gate or capability ambiguity | parent integration records scope expansion and exact-HEAD closure, then stop on plan gate |
| S03-S04 | no delegation exception; atomic code implementation and report repair were performed in the active Issue scope | user request to implement and review; risk accepted: no | S03/S04 union allowlist in plan.md and implementation briefs | provider/projection/runtime/resource/test changes plus report evidence | no rollback needed; immutable Candidate v2 retained | per-step briefs, focused/full tests, parity, diff-check, fresh code review | v5 review failure or out-of-scope change | stop before S05, PR, merge, or close |
| S05-S13 | no delegation exception; documentation work was performed in the active Issue scope | user request to implement and review; risk accepted: no | step-local allowed paths in plan.md | per-step implementation and report evidence | no rollback needed; immutable Candidate v2 retained | per-step ChatGPT brief, tests, review, and diff check | active step gate or capability ambiguity | stop on plan-defined gate; no merge or close |

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
| S03-S04 | implementation code review | ChatGPT-Use Red Team | fresh v1〜v8 | pass | no | promote | v1 exact-HEAD `458fa4a1...` FAIL (P1=4); v2 exact-HEAD `5813ad0...` FAIL (P1=2); v3 exact-HEAD `91781cf...` FAIL (P1=1); v4 exact-HEAD `150d81a3...` FAIL (P1=2); v5 exact-HEAD `827e439d...` FAIL (P1=1); v6 exact-HEAD `3b0d255d...` FAIL (P1=1); v7 exact-HEAD `48b0c86...` FAIL (P1=1); v8 exact-HEAD `366ea40c...` PASS (P0=0/P1=0) |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | `e599d19e2027cfd599f00aa730f90bf52dc06742` | `e599d19e2027cfd599f00aa730f90bf52dc06742` plus report evidence commits | local/GitHub parity; clean before next step | provider infra + existing infra unit test only | source/test, S01 brief, and sanitized capability receipt | `git diff --check` | directory/multiple/continuation evidence recorded; remote failure stage deferred to S10 |
| S02 | committed | `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` | `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` plus report evidence commit | local/GitHub parity; clean after commit | issue planning application contract / caller binding and S02 evidence | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `tests/unit/application/test_issue_planning_prompt.py` | `uv run pytest` / `uv run ruff check` / `uv run mypy` / `uv run spec-dock validate .` / `git diff --check` | remote parity verified; cl-s02-profile / tc-s02-001 closed |
| S03-S04 | committed-and-closed | `836a9c7372879747a24b7785e9484a9e9dfc2f3b` + `0586f151407ff95aeb4ef8b72d18a019b5d7a1a8` + `150d81a3e1a98e1f3e9776743e8376c28a7c7184` + `827e439d20557ef99e05f8ac844310915acce704` + `3b0d255d...` + `48b0c86...` + `366ea40c...` | Blue runtime/test/report repair履歴、v1〜v8 review artifact、v3〜v7 repair briefを保持し、v8 PASSをrecord | v8 exact reviewed HEAD `366ea40c...`とGitHub parity; evidence-only report updateはreviewed runtimeを変更しない | provider/application/prompt/infra/resource/test change-set plus v1-v8 review evidence and v3-v7 repair briefs | v1-v8 fresh review、focused/full tests、provider/projection parity、validate、diff-check | v8 P0/P1=0でS03/S04同一 reviewed HEAD closureを完了; S05 briefへ進む |
| S05-S13 | pending | not started | none | not applicable | no product-code change | step-local paths in plan.md; S05 allowlist correction recorded in D-002 | not run | S05 awaits fresh plan review after allowlist correction; later steps await their own brief and review |

#### 変更したファイル
- S01 implementation: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, `tests/unit/infra/test_issue_planning_chatgpt.py`
- S01 artifact: `artifacts/implementation-briefs/s01-capability-characterization.md`
- S02 implementation: `artifacts/implementation-briefs/s02-operation-resources.md`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `tests/unit/application/test_issue_planning_prompt.py`
- S03/S04 implementation: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`, Review resource `instructions.md`, provider projection, and unit/integration tests
- S03/S04 artifacts: `artifacts/implementation-briefs/s03-s04-atomic-implementation-brief-20260805.md`, `s03-input-path-model-v2.md`, `s04-direct-attachment-transport.md`, `s03-s04-implementation-identity-rebind-20260805.md`, `s03-s04-v3-repair-brief-20260805.md`, `s03-s04-v4-repair-brief-20260805.md`, `s03-s04-v5-repair-brief-20260805.md`, `s03-s04-v6-repair-brief-20260805.md`, `s03-s04-v7-repair-brief-20260805.md`; Fresh Red Team reviews `reviews/red-team-review-s03-s04-code-v1.md`〜`reviews/red-team-review-s03-s04-code-v8.md`
- S05 implementation brief (blocked pending plan-boundary correction): `artifacts/implementation-briefs/s05-orchestration-cli-cutover.md` (SHA-256 `1cc61ef724dbe958129632cae3f6c63578b7e3fee833eccad634d9dc32ff6699`)
- v3 repair: mixed absolute/relative direct-transport input spy, lexical argv preservation assertion, and integration fake Oracle explicit cwd assertion; v4 repair adds a repository-external absolute Candidate fixture and report evidence reconciliation; production runtime/provider projection unchanged
- This report: implementation, verification, review, and remaining capability gate evidence

#### コミット
- `e599d19e2027cfd599f00aa730f90bf52dc06742` (`fix(iss-00354): S01のpreflight検証とテストを堅牢化`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `fccdc561a9abd2b9c4bef565cfcd5f0a28d21f95` (`fix(iss-00354): Issue planning証跡生成のidentity検証を厳密化`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `458fa4a130be05c3a6ed0ad675639148b604f91a` (`feat(iss-00354): S03/S04実装のtransport契約を実装反映`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `836a9c7372879747a24b7785e9484a9e9dfc2f3b` (`fix(iss-00354): S03/S04実装のpath transportを契約通り修正`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `0586f151407ff95aeb4ef8b72d18a019b5d7a1a8` (`fix(iss-00354): direct transportの入力非再構成テストを強化`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `150d81a3e1a98e1f3e9776743e8376c28a7c7184` (`test(iss-00354): S03/S04のmixed pathとcwd証跡を補強`), pushed to `codex/iss-00354-chatgpt-context-contract`
- `827e439d20557ef99e05f8ac844310915acce704` (`fix(s03-s04): v4修正でdirect transport testとreportを反映`), pushed to `codex/iss-00354-chatgpt-context-contract`

#### メモ
- Candidate v2 archive remains immutable; each current canonical amendment is a separate history entry.
- S01/S02 implementation is not an assurance promotion, PR, merge, or Issue close. S03/S04 runtime、v2 input-spy repair、v3/v4 test/report repair、v5 report-only repairはpush済みであり、v6 Fresh Red Teamのsource HEADは`3b0d255d...`である。v6 Fresh Red TeamはP1×1（commit ledgerと現行worker時制）を検出し、v7 Fresh Red TeamまでPR、merge、Issue closeは保留する。今回の修正commit SHAはreport自身へ自己参照しない。

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

### S03/S04 atomic cutover 計画レビュー v3（2026-08-05 / read-only Red Team）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@961a8b8370ed7e3e4cd162ebe15a55ef61101fe1`
- identity SHA-256: `ff189b9807e43b1a6391c811484a448eba3c46b93c10d42c4798710a11c09fed`
- review artifact: `reviews/red-team-review-s03-s04-plan-v3.md`、外部出力 `/private/tmp/codex-agent-work/501/s03-s04-plan-review-v3-20260805/review.md`、SHA-256 `6df048185086aeabd946eeb5c22d5b13fea5624942982a786426744802d78455`
- verdict: `PASS`（P0=0 / P1=0 / P2=0 / P3=0）。S03/S04 execution cardのresource identity-contract許可範囲、provider-sync projection、full-chain e2e必須検証、generated-pack search gate、same-HEAD closureが§8.1・v2 addendumと整合していることを確認した。
- scope: Red Teamはnamed branchのexact HEADと添付7ファイルのGit blobを確認し、Candidate、canonical docs、repositoryを変更していない。レビューはv2 P1修正の確認に限定され、アーキテクチャ再設計や改善提案はない。
- model evidence: wrapperはrequested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、`strategy=select`、`verified=yes`を返した。GitHub connector経路ではReasoning Effort証跡がなく、GPT-5.6 Luna / Reasoning Effort Maxの実測成功は主張しない。
- next gate: S03/S04各専用実装ブリーフを最新HEADへ結び付け、atomic implementationを開始する。両closureは同一 resulting HEAD、同一push、fresh code review PASSまでpendingのままとする。

## S03/S04 実装ブリーフ生成（2026-08-05 / exact HEAD `8b44eb6d...`）

- ChatGPT-Use は、GitHub同期済みの `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、exact source HEAD `8b44eb6da5d8be4f2178ce3be09d25e968f14747` を対象に実行した。github-sync preflight は `status=pass`、local/remote HEAD は一致し、default branch fallback は使用していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-implementation-brief-20260805/brief-final.md`、SHA-256 `631b24e9d852e15d9a61ca429cb8da12293b571e362eb33afa3c1232b288971e`。ChatGPT出力は編集せず、`s03-s04-atomic-implementation-brief-20260805.md`、`s03-input-path-model-v2.md`、`s04-direct-attachment-transport.md` へ byte-identical にコピーし、三つのSHA一致を確認した。
- ブリーフの実装境界: S03 application path-only synthesized contract、S04 direct repeated `--file` transport、Review resourceのminimal-body identity/digest、provider runtime/resourceと指定testのunion allowlist、provider sync projection、focused verification、legacy symbol search、same resulting HEAD closure。
- ChatGPT-Useのモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved label `Pro`、strategy `current`、`verified=no`。`GPT-5.6 Luna / Reasoning Effort Max` の実測成功は確認できないため、本台帳でも主張しない。
- 実行上の問題と復旧: 最初の大容量添付は prompt reconstruction mismatch、続く試行は rate-limit dialog、model pickerの `Got it`、添付送信準備の300秒 timeout（`attachment-send-not-ready`）で送信前に停止した。会話ID・promptSubmittedは生成されず、別の短い smoke と `--browser-attachment-timeout 10m` を指定した最終試行で同じセッションが応答生成まで完了した。Oracle/API fallback、personal wrapper、repository変更は行っていない。
- 採用境界: このブリーフは advisory implementation context として採用し、コード変更、レビュー判定、assurance promotion、PR、merge、Issue closeは行っていない。S03/S04 の `cl-s03-path-input`、`tc-s03-001`、`cl-s04-direct-transport`、`tc-s04-001` は同一 resulting HEAD の実装・検証完了まで pending とする。

### S03/S04 実装ブリーフ identity rebind addendum（2026-08-05 / exact HEAD `f2238d12...`）

- ChatGPT-Use は named branch `codex/iss-00354-chatgpt-context-contract` の exact source HEAD `f2238d12313b36a002185d3e101154c20f19993c` を GitHub connector で確認し、default branch fallbackを使用せず、元ブリーフのidentityだけを再結合する短い addendumを生成した。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-implementation-20260805/rebind.md`、SHA-256 `42435793d23e4032bf2d902da8f7a93fa5bf66c3a68a5f9d539618d70c8ced2d`。出力は編集せず `artifacts/implementation-briefs/s03-s04-implementation-identity-rebind-20260805.md` にbyte-identicalで保存した。
- `8b44eb6...` から `f2238d1...` へのGitHub比較は docs-only lineage（reportと三つのimplementation-brief artifactのみ）であり、canonical requirement/design/plan、provider runtime、対象tests、provider projection、Review resourceには差分がないことを確認した。元ブリーフのscope、不変条件、allowlist、検証、停止条件は変更しない。
- addendumはworker preconditionとしてnamed branch exact HEAD、scope外変更なし、provider/test baseline差分なし、同一 resulting HEAD closureを再確認する。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり、wrapperのrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / `strategy=current` / `verified=no`だけを記録する。
- 採用境界: addendumはidentity evidenceとして採用し、コード変更、レビュー判定、assurance promotion、PR、merge、Issue closeは行っていない。S03/S04の実装中にprovider/test baselineが先行変更されていた場合は、このaddendumを流用せず停止する。

### S03/S04 Fresh Red Team code review v1（2026-08-05 / exact HEAD `458fa4a1...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@458fa4a130be05c3a6ed0ad675639148b604f91a`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v1-20260805/review.md`、SHA-256 `9de26415ebca05c5a902710703bd9ff45430d9cf48544a877aeec851337a8ce3`。read-only結果を `reviews/red-team-review-s03-s04-code-v1.md` へbyte-identicalに保存した。
- 判定: **FAIL**（P0=0 / P1=4 / P2=0 / P3=0）。findingは `RT-354-S03S04-CODE-001`（repository-relative source pathをroot-prefixed absolute operandへ変換）、`CODE-002`（application provider/projection byte parity不一致）、`CODE-003`（no-inspection/no-materialization failure-spy matrix不足）、`CODE-004`（implementation resulting HEADとreport closure/evidenceの不整合）である。
- 実装事実: provider prompt/infra/resource、unit/integration tests、dogfood projectionの実装差分は `458fa4a1` に含まれる。通常pytest `1472 passed / 2252 skipped`、S03/S04 focused default `237 passed / 11 skipped`、domain contract `88 passed`、S03/S04 full-regression integration subset `11 passed`、ruff、diff-checkはローカルで確認済みだが、application projection parityはコミット後に再確認が必要である。
- 採用境界: Red Teamはrepository、canonical docs、report、artifact、testsを変更していない。FAILを修正入力としてのみ採用し、P0/P1解消、projection parity、failure-spy追加、reportのexact resulting HEAD更新が完了するまでS03/S04 closure、assurance昇格、S05開始、PR作成を保留する。GPT-5.6 Luna / Reasoning Effort Maxは実測未確認で、wrapperのrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / strategy `current` / verified `no`のみ記録する。

### S03/S04 Blue修正（2026-08-05 / resulting HEAD `836a9c73...`）

- 対象: `chemitaro/spec-dock` / `codex/iss-00354-chatgpt-context-contract`。修正コミット `836a9c7372879747a24b7785e9484a9e9dfc2f3b` をGitHubへpushし、local HEADとupstream HEADの一致を確認した。default branch fallbackは使用していない。
- CODE-001修正: repository-relative source pathは`repo_root / relative`へ変換せず、`Path(relative)`としてlexical operandを維持し、worker cwd=repo_rootで解決する。Git-bound dynamic pathも同じ契約に統一した。
- CODE-002修正: provider-side `application/issue_planning.py`を正本としてprojectionを再生成し、provider/projectionのbyte parityを確認した。prompt/infra/resourceのparityも再確認した。
- CODE-003修正: attachment directoryのnested/hidden/symlink/FIFOに対するinspection禁止、dynamic pathの`read_bytes/resolve/stat/rglob/iterdir`ゼロ、direct transport入力側のmkdir/write/copy/ZIP/hash/tree traversalゼロ、external `Path` identity、direct repeated `--file`順序をfailure spiesとassertionで追加した。
- CODE-004修正: このreportにresulting HEAD、変更範囲、検証結果、v1 FAILと修正境界、次回Fresh Red Team対象を記録した。report更新自体はコード変更と分離した証跡コミットとして扱う。
- 検証（resulting HEAD）:
  - `uv run pytest` -> `1472 passed, 2252 skipped`
  - focused unit/integration -> `237 passed, 11 skipped`
  - `uv run pytest --run-full-regression tests/integration/test_issue_planning_e2e.py tests/integration/test_issue_planning_chatgpt_transport.py -q` -> `11 passed`
  - `uv run ruff check` -> pass、`git diff --check` -> pass
  - provider/projection `cmp`（prompt、application、infra、Review resource）-> pass
- 判定境界（v1修正時点の履歴）: v1のP1×4は修正済みだが、Red Teamの判定をBlue側で先取りしない。後続のreport-only updateを含むexact HEAD `5813ad0...`を対象にFresh Red Team v2を実施し、P1×2が検出された。v2の修正とv3 reviewが完了するまでS03/S04 closure、S05開始、PR作成を保留する。GPT-5.6 Luna / Reasoning Effort Maxは実測未確認で、wrapperのrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / strategy `current` / verified `no`のみ記録する。

### S03/S04 Fresh Red Team code review v2（2026-08-05 / exact HEAD `5813ad0d...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@5813ad0d97510110c498102cbe18c7b4556d104c`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1とは別の新規Fresh Red Team threadで、Red Teamはread-onlyのまま repository、canonical docs、tests、report、review artifactsを変更していない。
- Blue implementation identity: runtime path/transport change `836a9c7372879747a24b7785e9484a9e9dfc2f3b`、その後のreport-only update `5813ad0...`。v2 reviewはcurrent branch tip `5813ad0...`を判定対象とした。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v2-20260805/review.md`、SHA-256 `0757413f2002b3782f52402903a8b71eafa5f8e1ad57d3c6d091575afa6f37f8`。`reviews/red-team-review-s03-s04-code-v2.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=2 / P2=0 / P3=0）。`RT-354-S03S04-V2-001`はdirect transport入力側のread/open、copy、archive/ZIP、hash no-materialization spy不足、`RT-354-S03S04-V2-002`はreportのcurrent-state/closure ID/exact review identity/必須証跡不整合を指摘した。production code自体のinput pack再生成は確認されず、アーキテクチャ再設計の提案はなかった。
- Blue修正境界: V2-001に対し、`tests/unit/infra/test_issue_planning_chatgpt.py`へ`Path.read_bytes`、`Path.open`、builtin `open`、`os.scandir/listdir`、copy系、ZIP、hashの入力側failure spiesを追加し、output-only artifact verificationのhashとは分離した。V2-002に対し、本reportのClosure Coverage、canonical `cl-s04-direct-transport`、implementation/review HEAD distinction、必須検証証跡を整合させる。
- resulting repair commit: test/review artifact修正は`0586f151407ff95aeb4ef8b72d18a019b5d7a1a8`としてpush済み。report更新後の次のbranch tipをv3 Fresh Red Teamの唯一のreview identityとする。
- 検証証跡（Blue repair baseline）:
  - `uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q` -> `93 passed`（exit 0）
  - `uv run pytest -q` -> `1472 passed, 2252 skipped`（exit 0）
  - `uv run pytest tests/unit/domain/test_issue_planning_contracts.py -q` -> `88 passed`（exit 0）
  - `uv run pytest --run-full-regression tests/integration/test_issue_planning_e2e.py tests/integration/test_issue_planning_chatgpt_transport.py -q` -> `11 passed`（exit 0）
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=228`（exit 0）
  - `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update)`（exit 0）。生成対象はprovider-managed projectionで、repo-root shortcut warning以外の失敗はない。
  - Legacy production search（実行コマンド）:
    ```bash
    rg -n "_write_transport_pack|reviewed-identity\\.(json|sha256)|exact_attachments|SynthesizedPlanningPrompt\\.attachments" \\
      src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \\
      src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \\
      src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \\
      .agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md \\
      spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \\
      spec-dock/scripts/spec_dock_runtime/application/issue_planning.py \\
      spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
    ```
    -> zero-match、exit 1（rgのnon-matchを成功証跡として記録）。historical artifacts/reviewsと、非実装テストのabsence assertionsはこのproduction searchから除外した。
  - provider/projection parity: prompt `eca57d97...`、application `0498c2a9...`、infra `303ae989...`、Review resource `db2a0cc0...` が各対で一致（`cmp` exit 0）。
  - scope audit: `git diff --name-only 5813ad0d97510110c498102cbe18c7b4556d104c 0586f151407ff95aeb4ef8b72d18a019b5d7a1a8` は `reviews/red-team-review-s03-s04-code-v2.md` と `tests/unit/infra/test_issue_planning_chatgpt.py` の2ファイルのみ。`git status --short --branch` は修正コミット後にcleanで、local/upstream HEADは`0586f151...`で一致した。
  - `git diff --check` -> pass（exit 0）。
- 判定境界: V2 P1×2を修正するまではS03/S04 closure、assurance昇格、S05開始、PR作成を保留する。修正後はreportを含む新しいexact branch tipを、v1/v2とは別のFresh Red Team v3へ渡す。GPT-5.6 Luna / Reasoning Effort Maxは実測未確認で、wrapperのrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / strategy `current` / verified `no`のみ記録する。

### S03/S04 Fresh Red Team code review v3（2026-08-05 / exact HEAD `91781cf5...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@91781cf507f979b02ba3ceb0a0610f2815114ec8`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1/v2とは別の新規Fresh Red Team threadで、Red Teamはread-onlyのまま repository、canonical docs、tests、report、review artifactsを変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/review.md`、SHA-256 `17a35426d2bd3149b783e55c962ac34a27755f864936abe021a6827a22f3d69c`。`reviews/red-team-review-s03-s04-code-v3.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=1 / P2=0 / P3=0）。`RT-354-S03S04-V3-001`は、direct transportの実際のinfra invocationにmixed absolute/external/lexical-relative pathを渡すspyと、Oracle subprocessの明示`cwd=repo_root`を同時に固定する回帰テストが不足していると指摘した。production runtimeはpath-only、repeated `--file`、明示cwdに整合し、P1はテスト証跡の欠落に限定された。
- v1/v2 finding解消確認: repository-relative operand、provider/projection parity、input-side API guard、report current-state/closure ID/HEAD distinctionは解消済み。残るのはrelative path shapeとexplicit cwdのmixed-chain assertionだけである。アーキテクチャ再設計、productionコード変更、S05提案はなかった。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxは未確認であり主張しない。

### S03/S04 Blue修正（v3 P1最小修正 / historical repair before v4）

- ChatGPT-Use実装ブリーフ: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v3-retry-20260805/blue-repair-brief2.md`、SHA-256 `553fa26fd28875eda9e80a7c1b6f75e8fc459ccbc7bfa8aee5523275c93be344`。`artifacts/implementation-briefs/s03-s04-v3-repair-brief-20260805.md`へbyte-identical保存した。本文-only送信で取得し、モデルはrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`である。
- 修正範囲: `tests/unit/infra/test_issue_planning_chatgpt.py`でabsolute static directory・absolute external Candidate・lexical repository-relative source pathを同一のinfra invocationへ渡し、relative operandと`repo_root/relative`の双方を入力側read/open/tree/copy/ZIP/hash guard対象にし、argvのrelative文字列保持と`cwd==repo_root`をassertした。`tests/integration/test_issue_planning_e2e.py`ではfake Oracleの明示cwdを記録・検証し、呼出元をrepository外に置いて継承cwdでは通らない証跡にした。production runtime/provider projection/Review resourceは変更していない。
- 検証: focused unit `1 passed`、infra unit `93 passed`、e2e `4 passed`、Ruff pass、`git diff --check` pass。新しいcommit/push後にfull quality gate（全体pytest、full-regression integration、validate、provider update/parity、legacy search、scope audit）を再実行し、v4 Fresh Red Teamへ渡す。
- wrapper障害: v3 review前の複数行promptは`prompt-reconstruction-mismatch`、Blue follow-upはChat/Work mode判定不能、添付付きBlue新規送信は`promptSubmitted=false`のまま600秒で投入前停止した。いずれも会話ID・回答・repository変更はなく、回答を採用していない。添付なし本文-onlyでBlueブリーフを取得し、障害をEAL-021に記録した。
- 判定境界: v3 P1を修正したcommit/pushのexact branch tipを、v1〜v3とは別のFresh Red Team v4へ渡す。v4がP0/P1=0を示すまでS03/S04 closure、assurance昇格、S05開始、PR作成、Issue closeは行わない。

### S03/S04 Fresh Red Team code review v4（2026-08-05 / exact HEAD `150d81a3...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@150d81a3e1a98e1f3e9776743e8376c28a7c7184`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1〜v3とは別の新規Fresh Red Team threadで、Red Teamはrepository、canonical docs、tests、report、review artifactsをread-onlyで確認し、変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/review.md`、SHA-256 `0efea79260633b5fab656a7ce7f5bfb79f148c46376a68171bc7f3656722398d`。`reviews/red-team-review-s03-s04-code-v4.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=2 / P2=0 / P3=0）。`RT-354-S03S04-V4-001`はrepository外absolute Candidateを同一infra invocationへ渡す実テスト不足、`RT-354-S03S04-V4-002`はcommit済みHEADとreportのcurrent-state・post-repair必須検証証跡の不整合を指摘した。production runtime、provider/projection、要件・設計・計画にはfindingがない。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり主張しない。
- disposition: P1二件だけをEAL-022の修正入力として採用し、S03/S04 closure、assurance昇格、S05開始、PR、merge、Issue closeは保留する。

### S03/S04 Blue修正（v4 P1最小修正 / repair source `150d81a3...` / historical before v5）

- ChatGPT-Use実装ブリーフ: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v4-20260805/blue-repair-brief.md`、SHA-256 `d5fdf4c91e679cc7dc324ace5c5b5f786d99e575e3fea9f27f6ff7e979665c47`。`artifacts/implementation-briefs/s03-s04-v4-repair-brief-20260805.md`へbyte-identical保存した。`--reasoning-effort max`指定は個人OracleのAPI経路へ切り替わり送信前に失敗したため、browser current経路で再取得した。モデル証跡はrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`である。
- 修正範囲: `tests/unit/infra/test_issue_planning_chatgpt.py`のdirect transport testを`repo_root=tmp_path/repo`へ分離し、repo内absolute attachments、repo外absolute Candidate、lexical repository-relative sourceを同一の実infra invocationへ渡すfixtureへ変更した。Candidateをprotected input setへ追加し、repeated `--file`の順序・relative文字列・`cwd=repo_root`・input-side read/open/tree/copy/ZIP/hash zero-callをassertした。production runtime/provider projection/Review resourceは変更していない。
- report整合（v5以前の履歴）: `150d81a3...`をv3 test-repair commitとして固定し、v4 FAIL（P0=0/P1=2）、修正対象、検証コマンド、v5 review identityを本reportへ記録した。その後の修正コミットは`827e439d...`としてpush済みであり、v5 reviewのsourceとなった。
- v4修正後の実測検証（すべてexit 0、legacy searchのみzero-matchのexit 1）:
  - `uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q` -> **93 passed**
  - `uv run pytest tests/unit/domain/test_issue_planning_contracts.py -q` -> **88 passed**
  - `uv run pytest -q` -> **1472 passed, 2252 skipped**
  - `uv run pytest --run-full-regression tests/integration/test_issue_planning_e2e.py tests/integration/test_issue_planning_chatgpt_transport.py -q` -> **11 passed**
  - `uv run pytest --run-full-regression tests/integration/test_issue_planning_e2e.py -q` -> **4 passed**
  - `uv run ruff check tests/unit/infra/test_issue_planning_chatgpt.py tests/integration/test_issue_planning_e2e.py` -> pass
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=228`
  - `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update)`（repo-root shortcut warningは既知の非失敗）
  - provider/projection parity `cmp`（prompt/application/infra/Review resource）-> 各組 exit 0
  - legacy production search -> zero-match、exit 1
  - `git diff --check` -> pass
- この節はv5以前の履歴である。修正対象はreport、unit test、v4 review artifact、v4 repair briefのみで、production runtimeやcanonical requirement/design/planは変更しなかった。その後のpush済みHEAD `827e439d...`をv5 Fresh Red Teamが確認し、closureは引き続きpendingである。

### S03/S04 Fresh Red Team code review v5（2026-08-05 / exact HEAD `827e439d...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@827e439d20557ef99e05f8ac844310915acce704`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1〜v4とは別の新規Fresh Red Team threadで、Red Teamはread-onlyのまま repository、canonical docs、tests、report、review artifactsを変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/review.md`、SHA-256 `82c0b6bcea5852a3b199c84cc9b1178a16e5f02627bf26955bd2d5ad155043d8`。`reviews/red-team-review-s03-s04-code-v5.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=1 / P2=0 / P3=0）。`RT-354-S03S04-V5-001`は、v4修正内容と検証結果は記録されている一方、reportのcurrent identity/verification ledgerがpush済みHEAD `827e439d...`へ閉じておらず、「must be pushed」「after next commit」「ready to commit/push」「awaits its pushed exact tip」等の同義表現がcurrent欄に残り、commit一覧も`150d81a3...`で止まっていることを指摘した。V4-001のrepo外absolute Candidateテストは解消済みと確認された。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり主張しない。
- disposition: P1一件だけをEAL-024の修正入力として採用し、S03/S04 closure、assurance昇格、S05開始、PR、merge、Issue closeは保留する。

### S03/S04 Blue修正（v5 P1最小修正 / report-only）

- ChatGPT-Use実装ブリーフ: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v5-20260805/blue-repair-brief.md`、SHA-256 `1f5577bed5163bab8c2397be5c9ba2f78046723bff4cf3e780ac25986ef11d9b`。`artifacts/implementation-briefs/s03-s04-v5-repair-brief-20260805.md`へbyte-identical保存した。本文-only送信で取得し、モデルはrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`である。
- 修正範囲: canonical `report.md`のみ。current state、commit ledger、Final Code Review Gate、Final Commit Gate、S03/S04 execution/review rowsを、push済みHEAD `827e439d20557ef99e05f8ac844310915acce704`、v5 verdict `FAIL (P0=0/P1=1)`、v5 review artifact、v6 next gateへ整合させる。v1〜v4履歴、v4 review、production runtime、provider/projection、unit/e2e test、requirement/design/planは変更しない。
- current identity: repository `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、local HEAD / upstream HEAD `827e439d...`、作業ツリーclean、commit `fix(s03-s04): v4修正でdirect transport testとreportを反映`。このcommitはv4 repair brief、v4 review artifact、v4 report、direct transport unit testを含み、GitHubへpush済みである。
- current欄から未pushを示す表現を除去し、future actionを`v6 fresh reviewへ渡す`だけに限定する。v5 P1が解消されるまでclosure、S05、PR、merge、Issue closeは保留する。

### S03/S04 Fresh Red Team code review v6（2026-08-05 / exact HEAD `3b0d255d...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@3b0d255d38272b431c364cdf65daeac2786b7ead`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1〜v5とは別の新規Fresh Red Team threadで、Red Teamはrepository、canonical docs、tests、report、review artifactsをread-onlyで確認し、変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/review.md`、SHA-256 `ecb2c8c6634af7d70d4d4bb39eb930f3c5da9fa61864e59e17624bf7f521a29a`。`reviews/red-team-review-s03-s04-code-v6.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=1 / P2=0 / P3=0）。`RT-354-S03S04-V6-001`は、commit ledgerにv5 reviewed source `827e439d20557ef99e05f8ac844310915acce704`のfull SHAがなく、Delegated Worker Evidenceにpush前の時制が残ることを指摘した。`3b0d...`自身のreport内自己参照はfindingではない。production runtime、provider/projection、要件・設計・計画にはfindingがない。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり主張しない。
- disposition: P1一件だけをEAL-026の修正入力として採用し、S03/S04 closure、assurance昇格、S05開始、PR、merge、Issue closeは保留する。

### S03/S04 Blue修正（v6 P1最小修正 / report-only）

- ChatGPT-Use実装ブリーフ: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v6-20260805/blue-repair-brief.md`、SHA-256 `18387e7a4b3f043a71152f83f1215479b724014b0b48990181d1906435bea258`。`artifacts/implementation-briefs/s03-s04-v6-repair-brief-20260805.md`へbyte-identical保存した。モデルはrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`である。
- 修正範囲: canonical `report.md`の`#### コミット`と`#### 委任 worker 証跡（Delegated Worker Evidence）`の2箇所を中心に、v6 review artifact、v6 brief、current review/closure gateの観測証跡を追加する。v5 reviewed source `827e439d...`のfull SHAとcommit messageを履歴台帳へ追加し、v5 report-only pushを未来条件として表現していたworker行を、v6 FAILとv7 next gateを示す現行記録へ訂正する。production runtime、tests、requirement/design/plan、provider/projection、v1〜v6 review artifactは変更しない。
- 必須検証: report identity inspection、v6 stale wording zero-match、`git diff --check`、report-only scope audit、commit後のlocal/GitHub exact parityとclean worktree。v7 Fresh Red Teamは今回の修正後の新しいexact branch tipをread-onlyで確認する。
- disposition: v6 P1が解消されたことをv7 Fresh Red Teamで確認するまで、S03/S04 closure、S05開始、PR、merge、Issue closeは保留する。今回のrepair commit SHAはreport本文へ自己参照しない。

### S03/S04 Fresh Red Team code review v7（2026-08-05 / exact HEAD `48b0c86...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@48b0c86ee7e58ae8b971c15b14a3249db577e6d5`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1〜v6とは別の新規Fresh Red Team threadで、Red Teamはrepository、canonical docs、tests、report、review artifactsをread-onlyで確認し、変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/review.md`、SHA-256 `ae1fe0a99d9c174689057cb2eb5bd996861b5c0277d407c9c11b5120c8e771a0`。`reviews/red-team-review-s03-s04-code-v7.md`へbyte-identical保存済み。
- 判定: **FAIL**（P0=0 / P1=1 / P2=0 / P3=0）。`RT-354-S03S04-V6-001`のcommit ledger部分は解消されたが、S03-S04 worker親統合判断にv6 report-only修正を未来条件とする時制が残っていた。production runtime、provider/projection、要件・設計・計画にはfindingがない。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり主張しない。
- disposition: P1一件だけをEAL-028の修正入力として採用し、S03/S04 closure、S05開始、PR、merge、Issue closeは保留する。

### S03/S04 Blue修正（v7 P1最小修正 / report-only）

- ChatGPT-Use実装ブリーフ: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v7-20260805/blue-repair-brief.md`、SHA-256 `328820cb0acbca1ca9d9b1902ed5bd08af5ba5eed364d8892d24dd596da8dbd6`。`artifacts/implementation-briefs/s03-s04-v7-repair-brief-20260805.md`へbyte-identical保存した。モデルはrequested `gpt-5.6` / target `GPT-5.6 Sol` / resolved `Pro` / verified `no`である。
- 修正範囲: canonical `report.md`のS03-S04 `Delegated Worker Evidence` 親統合判断セルの1文字列置換だけ。`v6 report-only修正をpushし、同一 resulting HEADでv7 PASSを確認してから両closureをcloseし、S05へ進む`を、既にpush済みの状態を示す`v6 report-only修正はpush済み。Fresh Red Team v8でP0/P1=0を確認してから両closureをcloseし、S05へ進む`へ変更した。self-reference、runtime/test/spec変更は行っていない。
- 検証: exact one-string replacement、`git diff --check`、report-only scope audit（1 file、1 addition/1 deletion）、commit/push後のlocal/GitHub parityを確認した。commit `366ea40c...`をpushし、v8 Fresh Red Teamへ渡した。

### S03/S04 Fresh Red Team code review v8（2026-08-05 / exact HEAD `366ea40c...`）

- reviewed identity: `chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@366ea40c2a2783098cbce0750809e20567ab5445`。GitHub connectorでnamed branch tipとexact SHAの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。v1〜v7とは別の新規Fresh Red Team threadで、Red Teamはrepository、canonical docs、tests、review artifactsをread-onlyで確認し、変更していない。
- 外部出力: `/private/tmp/codex-agent-work/501/s03-s04-code-review-v8-20260805/review.md`、SHA-256 `a126d359ee57389edc6d4f6a9793204158e8e10b029e1c68ac68e0d456c9a1b8`。`reviews/red-team-review-s03-s04-code-v8.md`へbyte-identical保存済み。
- 判定: **PASS**（P0=0 / P1=0 / P2=0 / P3=0）。`RT-354-S03S04-V6-001`のcommit ledger・worker時制とも解消された。差分はS03-S04 workerの1行のみで、runtime、tests、requirement/design/plan、provider/projection、Final Gate、S05以降に変更はない。
- Red Teamモデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり主張しない。
- disposition: v8 PASSをS03/S04 same-HEAD closureへ採用し、`cl-s03-path-input`、`tc-s03-001`、`cl-s04-direct-transport`、`tc-s04-001`をcloseする。S05実装前ブリーフへ進み、PR、merge、Issue closeは引き続き保留する。

## S05 実装前ブリーフ（2026-08-05 / exact HEAD `ee012140...`）

- ChatGPT-Use実行: `/private/tmp/iss-00354-s05-implementation-brief-20260805/brief.md`。出力は編集せず `artifacts/implementation-briefs/s05-orchestration-cli-cutover.md` へ byte-identical に保存し、SHA-256 `1cc61ef724dbe958129632cae3f6c63578b7e3fee833eccad634d9dc32ff6699` の一致を確認した。
- 入力 identity: `chemitaro/spec-dock`、branch `codex/iss-00354-chatgpt-context-contract`、source HEAD `ee012140410f3a3d73b147d8e57515feb017803c`。GitHub named branch tipとの一致（ahead 0 / behind 0）を確認し、default branch fallbackは使用していない。
- 判定: **BLOCKED（実装開始前の計画境界不足）**。現行 `tests/cli_runtime/test_chatgpt_cli.py` は `planning create --help` に旧 `--context-manifest` を要求しており、S05 hard cutoverと同期させる必要がある。一方、S05 delegation contractのallowlistに同テスト、`application/issue_planning_prompt.py`、prompt unit test、transport/lifecycle testが含まれていなかった。
- 補正: production architectureやS03/S04契約は変更せず、S05 execution cardのallowed paths、required verification、stop conditionだけを補正した（D-002 / EAL-031）。補正後に fresh exact-HEAD plan reviewを行い、PASSするまで実装・commit候補・code reviewを開始しない。
- モデル証跡: requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、strategy `current`、verified `no`。GPT-5.6 Luna / Reasoning Effort Maxの実測成功は未確認であり、主張しない。
- scope: このブリーフはS05の実装入力候補と不足境界を示す advisory evidenceであり、canonical docsのレビューPASS、実装完了、assurance promotion、PR、merge、Issue closeを意味しない。

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
| ChatGPT-Use Red Team | S03/S04 atomic implementation, path/transport tests, provider/projection/report evidence | v1 exact HEAD `458fa4a1...` FAIL (P1=4); v2 exact HEAD `5813ad0...` FAIL (P1=2); v3 exact HEAD `91781cf...` FAIL (P1=1); v4 exact HEAD `150d81a3...` FAIL (P1=2); v5 exact HEAD `827e439d...` FAIL (P1=1); v6 exact HEAD `3b0d255d...` FAIL (P1=1); v7 exact HEAD `48b0c86...` FAIL (P1=1); v8 exact HEAD `366ea40c...` PASS (P0=0/P1=0) | 8 fresh reviews; v8 is the accepted PASS gate for S03/S04 | PASS |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer / ChatGPT-Use Red Team | requirement / design / plan / report / candidate identity alignment plus S03/S04 atomic plan amendment | v5 exact-head review at `079685b2...` is historical baseline PASS; S03/S04 plan amendment was separately reviewed at exact HEAD `961a8b8370ed7e3e4cd162ebe15a55ef61101fe1` and v3 is PASS with P0=0/P1=0 | v5 baseline plus S03/S04 plan v1/v2 FAIL repair cycle and v3 PASS; implementation code review is separate: code v1〜v7 are historical FAIL and v8 is PASS | spec-docs pass; S03/S04 implementation gate passed; S05以降は各step gateで継続 |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| current branch HEAD | S03/S04 v8 PASS evidence and S05 next-step handoff | v8 reviewed exact HEAD is `366ea40c...`; v8 output and SHA are recorded above; P0/P1=0でS03/S04 closureを完了した。v7/v8 review artifactとbriefのcanonical保存はreport-only evidence updateとして行い、production runtimeは変更していない | pass; S05 pending |

## 遭遇した問題と解決 (任意)
- 問題: 前回のChatGPT advisory reviewは、Candidate v2とcurrent HEADの結び付け、executable plan、report gateをP1として指摘した。
  - 解決: 正規三文書の承認境界、S01〜S13のclosure契約、reportの採用・レビュー・専門家ゲートを補完した。fresh reviewはpush後に実施する。

## 学んだこと (任意)
- Candidate archiveのimmutable identityと、現在のcanonical working copyのHEADを別々に記録し、レビュー入力で明示する必要がある。

## 今後の推奨事項 (任意)
- S03/S04開始前にChatGPT-Useで各専用実装ブリーフを作成し、atomic change-setの証跡をこのreportへ追記する。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
