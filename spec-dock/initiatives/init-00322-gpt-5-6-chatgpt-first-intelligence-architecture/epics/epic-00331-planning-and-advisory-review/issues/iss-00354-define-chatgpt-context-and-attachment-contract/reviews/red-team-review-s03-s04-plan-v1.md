reviewed_identity: chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@dada1f403241f615340ae1f0f8fb28b047edae75
reviewed_identity_sha256: d660016800b378b9fbd689a18ed3d41af0a1c4aa5e380ada6bbdd064df3e2a05
verdict: FAIL
P0: 0
P1: 3
P2: 0
P3: 0

## Findings

### RT-354-S03S04-001

severity: P1

exact file/section:
`plan.md` §8.1 S03/S04 Atomic Cutover Amendment、S03/S04 execution cards;
`artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification.md` “Candidate, Review, revision request, and identity” / “Read/run-only files”;
`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md` 冒頭、および対応する dogfood projection。

violated requirement or contradiction:
Atomic plan は `reviewed-identity.json` と `reviewed-identity-sha256.txt` を生成せず、既存 `ReviewedPlanningIdentity.to_dict()` と `identity.sha256` を minimal body に描画すると定める一方、Review operation の現行 instructions は `reviewed-identity-sha256.txt` と `reviewed-identity.json` を入力契約として明示している。さらに plan は operation resource files を read/run-only として、この cutover での変更を禁止している。したがって、generated identity files の廃止と Review resource contract の保持は同時に成立しない。

concrete impact:
Formal Review は、存在しない digest attachment を参照する instructions を受ける。`reviewed_identity_sha256` の欠落または誤生成により、現行の strict `PlanningReviewResult` identity validation が Review JSON を reject し得る。必要な production resource change が union allowlist 外なので、現行計画のままでは S03/S04 を同一 HEAD で Green／close できない。

### RT-354-S03S04-002

severity: P1

exact file/section:
`plan.md` §8.1 test write allowlist、および S04 execution card;
`artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification.md` “Required focused commands” / “Legacy-removal search gate”;
`tests/integration/test_issue_planning_e2e.py` `_FAKE_ORACLE` の Review output branch。

violated requirement or contradiction:
Atomic plan の test write allowlist は三つの unit test と `tests/integration/test_issue_planning_chatgpt_transport.py` に限定されている。しかし既存 full-chain integration fixture は Oracle argv から単一 `pack` path を取得し、その配下の `reviewed-identity.json` と `reviewed-identity-sha256.txt` を実際に読み込む旧 generated-pack consumer のままである。clarification は全 `tests` を対象とする legacy-removal search で、旧 pack symbols の実装参照を残さないことを closure condition としている。

concrete impact:
計画どおり production contract を hard cutover すると、この integration fixture は旧 pack を要求して破綻する。また legacy-removal search gate も失敗する。一方、この test は write allowlist 外であるため、計画に従う限り修正できない。関連テストを過不足なく含むという atomic union allowlist の成立条件を満たしていない。

### RT-354-S03S04-003

severity: P1

exact file/section:
`report.md` “Evidence Adoption Ledger” の許可 `adoption_status` 語彙、EAL-010、EAL-011;
`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py` `evaluate_report_evidence_gate()` / `_is_unresolved_eal_status()`。

violated requirement or contradiction:
Report 自身が許可する `adoption_status` は `adopted`、`partially_adopted`、`rejected`、`deferred`、`stale`、`blocked` だが、EAL-010 は非契約値 `blocked_advisory` を使用している。現行 report gate は status に `blocked` を含む全 EAL row を unresolved と判定するため、EAL-010 の `blocking=no` や「履歴として保持」という意図にかかわらず gate を停止させる。EAL-011 は fresh exact-HEAD review PASS 後の実装開始を next action としているため、両記録の意味が一致していない。

concrete impact:
本レビューが仮に P0/P1 なしで PASS しても、EAL-010 により automated report evidence gate は `report-eal-unresolved` のままになる。したがって atomic implementation start の前提を正規 gate で満たせず、ゲート迂回または未記録の追加補正なしには S03/S04 を開始できない。

## Scope confirmation

architecture_redesign_proposed: no
candidate_or_repository_modified: no
review_basis: GitHub connector で named branch `codex/iss-00354-chatgpt-context-contract` の tip と reviewed HEAD `dada1f403241f615340ae1f0f8fb28b047edae75` が `identical`、ahead `0`、behind `0` であることを確認し、default branch fallback は使用していない。exact HEAD の canonical requirement/design/plan/report、両 implementation brief、provider application/infra code、domain typed identity contract、関連 unit/integration tests、operation resources を照合した。添付 bundle の対象12ファイルは GitHub exact-HEAD blob と byte-identical であることを確認した。 別添の設計判断資料は iss-00354 S03/S04 計画補正と無関係な内容であり、判定根拠には採用していない。 wrapper/browser が返した model picker、resolved model、Reasoning Effort の証跡は本レビュー経路では確認できないため、GPT-5.6 Luna / Max の成功は主張しない。
