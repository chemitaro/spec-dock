---
種別: 実装報告書（Issue）
ID: "iss-00344"
タイトル: "Workbench Shell Scaffolding"
関連GitHub: ["#344"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00343", "init-local-00002"]
---

# iss-00344 Workbench Shell Scaffolding — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | user / Epic 343 | `.gitkeep` では Workbench の用途と境界を伝えられない | `.gitkeep`; tracked README; directory only | fresh root と future node に tracked `.workbench/README.md` を生成し、既存 scope は変更しない | 親 Epic の採用済み要件とユーザー承認に一致する | applied | `../../requirement.md`; `requirement.md` | design と plan で実装・検証境界を具体化する |
| D-002 | resolved | compatibility | ChatGPT authoring / local source inspection | tracked README と ignored payload の worktree 間移動を混同するリスク | automatic copy; README 専用 copy; Git checkout + manual opaque copy | README は通常 checkout、ignored payload だけを必要時に `workbench copy` で移す | Git tracking と既存 one-shot copy の責務が分離される | applied | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; `requirement.md#I344-RQ-007` | requirement PASS 後に合成する `design.md` へ反映する |
| D-003 | resolved | interpretation | ChatGPT requirement review F-001 | `spec-dock artifact import file` が global installer CLI と repo-local runtime のどちらか曖昧 | installer dispatch; shorthand; repo-local exact command | repository root から `./spec-dock/scripts/spec-dock artifact import file ...` を実行する契約へ限定 | current console script と Issue 345 ownership を誤解させない | applied | `artifacts/20260728t155212z-chatgpt-output-chatgpt-issue-00344-requirement-review.md`; `requirement.md#I344-RQ-003` | fresh re-review |
| D-004 | resolved | compatibility | ChatGPT requirement review F-002/F-003 | no-backfill と source-wins copy の受け入れ条件が過大・競合 | root 全体不変; Workbench 状態限定; README filter; conditional source-wins | no-backfill の不変対象を README / Workbench state に限定し、copy は identical / divergent の2ケースへ分割 | parent Epic と現行 runtime contract に一致する | applied | `requirement.md#AC-344-005`; `requirement.md#AC-344-007A`; `requirement.md#AC-344-007B` | fresh re-review |
| D-005 | resolved | scope | ChatGPT requirement third review F-007 | root と node の共通 README が `workbench copy` の root support を示唆する | root route 追加; guidance 分離; helper scope 明示 | tracked README は root/node とも checkout、helper は Initiative/Epic/Issue の node-scoped ignored payload のみ、root ignored payload は対象外と固定 | existing CLI と親 Epic の compatibility ownership に一致する | applied | `artifacts/20260728t162105z-chatgpt-output-chatgpt-issue-00344-requirement-third-review.md`; `requirement.md#I344-RQ-007`; `requirement.md#AC-344-007C` | fresh re-review |
| D-006 | resolved | deviation | user | 通常のSub-agent reviewerではなく、各stepの前後でChatGPT-Useを全面活用する実行方法が指定された | 通常Sub-agent reviewer; ChatGPT advisoryだけ追加; reviewer責務をChatGPT-Useで実行 | reviewer名を責務契約として維持し、push済みexact commitをChatGPT-UseがJSON reviewするoverlayをplanへ追加する | 実装scopeとclosure contractを変えず、ユーザー指定の高深度reviewと過剰実装抑制を両立できる | promoted_to_plan | `plan.md#11-chatgpt-first-execution-overlay`; user instruction on 2026-07-29 | F-001〜F-004を限定修正し、新exact commitへfresh reviewする |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | ChatGPT authoring (`gpt-5.5-pro`, GitHub Connector, evidence-only) | `requirement.md` | 親 Epic と local source に整合する要件、受け入れ条件、境界を採用。実装順序と具体設計は design / plan phase まで未採用 | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; SHA-256 `3eec9fd0865d452aa59e6faa883fb8c07c074e606790af76b94aab255f560835`; 85,422 bytes | ChatGPT requirement review と fresh `spec-reviewer` review |
| EAL-002 | adopted | `artifact import chatgpt-output` command | Issue Artifact | Workbench に保存した ChatGPT 完全回答を opaque bytes のまま Issue Artifact へ保存した | import receipt: `status=ok`, `import_kind=chatgpt-output`, `storage_identity=blank`, `committed=true`, `cleanup_state=removed` | なし |
| EAL-003 | adopted | ChatGPT requirement review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-001〜F-004 をすべて blocking finding として採用し、command boundary、no-backfill、copy compatibility、report state を修正した | `artifacts/20260728t155212z-chatgpt-output-chatgpt-issue-00344-requirement-review.md`; SHA-256 `037acab9142ae0128ef01b79ef51334edaf7c9285af6b09dec2b7f4283910be1`; 9,229 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-004 | adopted | ChatGPT requirement re-review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-005 の残存 root-wide immutability を managed provider update 可能な境界へ修正し、F-006 の premature design promotion claim を撤回した | `artifacts/20260728t160531z-chatgpt-output-chatgpt-issue-00344-requirement-rereview.md`; SHA-256 `c0a35277c3f3322b16269bbf3d60d88043fbe8aa31da1ee9701ddf4b9c7f5ffb`; 7,890 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-005 | adopted | ChatGPT requirement third review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-007 を採用し、root/node checkout、node-scoped copy helper、root helper exclusion を明示した | `artifacts/20260728t162105z-chatgpt-output-chatgpt-issue-00344-requirement-third-review.md`; SHA-256 `48a0cd7dae46233be5e8283d7698a6460c2c20798c55553a6d6667ea1d9cf281`; 6,133 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-006 | adopted | ChatGPT requirement final review (`PASS`, advisory) | `requirement.md`, `report.md` | commit `1087ea15` を connected GitHub app で確認した fresh review。blocking finding なし、F-007 と親 Epic / current copy contract の整合を確認した | `artifacts/20260728t164218z-chatgpt-output-chatgpt-issue-00344-requirement-final-review.md`; SHA-256 `756b70eb67743c7d4fa87ce98ee1e3acad9c97fefd00fd9ea192aab6beddca49`; 6,115 bytes | fresh `spec-reviewer` requirement review |
| EAL-007 | adopted | fresh `spec-reviewer` requirement review (`PASS`) | `requirement.md`, `report.md` | P0/P1なし。P2のChatGPT external evidence / delegated draft lane誤分類を修正し、requirement phaseをapprovedとした | reviewer output on commit `2e0bb6ae`; `requirement.md`; Delegated Draft Evidence row | assurance classify / design compose |
| EAL-008 | partially_adopted | ChatGPT planning candidate design section (`advisory`) | `design.md` | reviewed requirement、parent Epic、local sourceと照合し、freshness、template recursion、ignore、opacity、copy compatibility、distribution exact allowlist、docs責任をStandard designへ統合 | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; `.assurance.json` authorized profile `standard` | commit / push 後に ChatGPT design review と fresh `spec-reviewer` review |
| EAL-009 | adopted | ChatGPT design review (`FAIL`, advisory) | `design.md`, `report.md` | B-001〜B-003とNB-001を採用。Git trackingをpathname contractへ限定し、canonical README完全本文、generic byte-stable materialization、package inventory探索rootを設計へ固定した | `artifacts/20260728t170651z-chatgpt-output-chatgpt-issue-00344-design-review.md`; SHA-256 `53d496a9f09008f1a5623611035daf982e4f8a62a0901c80f450c55f3b49355f`; 10,259 bytes | commit / push 後に fresh ChatGPT design re-review と fresh `spec-reviewer` review |
| EAL-010 | adopted | ChatGPT design re-review (`FAIL`, advisory) | `design.md`, `report.md` | B-004/B-005とNB-002を採用。canonical本文へscope `artifacts/` destinationを追加し、wording変更をdesign amendment + fresh reviewへ統一し、template subtree相対5pathを固定した | `artifacts/20260728t172049z-chatgpt-output-chatgpt-issue-00344-design-rereview.md`; SHA-256 `99f4a67dc3917b9a10d20d8ab559d65c769e7b80c872311e079e8f2a3054fa81`; 12,450 bytes | commit / push 後に fresh ChatGPT design re-review と fresh `spec-reviewer` review |
| EAL-011 | adopted | ChatGPT design final review (`FAIL`, advisory) | `design.md`, `report.md` | B-006を採用。`setup.py` のcustom `build_py` post-build pruneをsource map、DES-344-008、責任表、TC-344-008、rollbackへ追加し、exact allowlist保存とstale nested README除去を両立させた | `artifacts/20260728t174335z-chatgpt-output-chatgpt-issue-00344-design-final-review.md`; SHA-256 `8777a0d837309d71e7326f659407afa1b6cc27c069ec7ed42e02e9d643f11b76`; 9,571 bytes | commit / push 後に fresh ChatGPT design re-review、その後 fresh `spec-reviewer` review |
| EAL-012 | adopted | ChatGPT design post-B-006 review (`PASS`, advisory) | `design.md`, `report.md` | connected GitHub appでcommit `dae3c3485cd29e63e72a3258178f186160e9ceb3`を確認したfresh review。blocking/non-blocking findingなし。active `setup.py` build boundary、exact five-path allowlist、stale nested README除去、actual post-build prune検証、rollback、Issue 344/346 ownershipを確認した | `artifacts/20260728t175913z-chatgpt-output-chatgpt-issue-00344-design-post-b006-review.md`; SHA-256 `d7d6dc3554be93d4b7f68a31e9df3791a632eda6136aac21031d28cdba15a2a5`; 8,488 bytes | fresh `spec-reviewer` design review |
| EAL-013 | adopted | fresh `spec-reviewer` design review (`PASS`) | `design.md`, `report.md` | commit `46794734b3b2067c9c3bf64508feaf1f36fdb325`を独立レビュー。findingなし。要件・親Epic・provider/build境界・exact five-path allowlist・検証・rollback・advisory laneの整合を確認し、design phaseをapprovedとした | reviewer output; `design.md`; `report.md`; commit `46794734b3b2067c9c3bf64508feaf1f36fdb325` | assurance再分類 / plan compose |
| EAL-014 | partially_adopted | ChatGPT planning candidate plan section (`advisory`) | `plan.md`, `report.md` | 3つのvertical micro-batch、Spec-Locked Closure、TDD、focused evidence、Issue 346 handoffを採用し、approved requirement/design、3-rule ignore、B-006 `setup.py` post-build prune、current Standard templateへ正規化した | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; SHA-256 `3eec9fd0865d452aa59e6faa883fb8c07c074e606790af76b94aab255f560835`; 85,422 bytes | commit / push 後にChatGPT plan review、その後fresh `spec-reviewer` plan review |
| EAL-015 | adopted | ChatGPT plan review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001/B-002を採用。generic exact-copy実装をallowed surface/Closure/TDDへ追加し、path-agnostic unchanged-byte copyとplaceholder renderを固定した。custom build prune、temporary build、wheel/sdist/installed inventory、scoped static checksをexact test node/commandとEVDへ結び付けた | `artifacts/20260728t182343z-chatgpt-output-chatgpt-issue-00344-plan-review.md`; SHA-256 `1eeebfc9532b00c1304ce5a7c048c6ead855c2da7b3793d27b72f992a168696b`; 12,617 bytes | commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` plan review |
| EAL-016 | adopted | ChatGPT plan re-review (`PASS`, advisory) | `plan.md`, `report.md` | connected GitHub appでcommit `1c98baabbde0cf9a7535cd91d6760012439e5e24`を確認したfresh review。B-001/B-002解消、blocking/material/non-blocking findingなし。generic exact-copyとdistribution/static実行契約、EVD、sibling/human boundaryを確認した | `artifacts/20260728t183939z-chatgpt-output-chatgpt-issue-00344-plan-rereview.md`; SHA-256 `dcb0e93513f7be284c5fed9ad87fbd6e829659b5f18f27c9582fb5fe5aa7191e`; 9,260 bytes | fresh `spec-reviewer` plan review |
| EAL-017 | adopted | fresh `spec-reviewer` plan review (`FAIL`) | `plan.md`, `report.md` | P1 4件/P2 1件を採用。各S01/S02/S03/S90/S99へstep-local delegation contract、具体テストケースcard、step closure/gate、depends/unblocks/targets/commit候補を追加し、Closure Indexをrequired/observable/locked/bug/evidenceへ拡張した。Active TDDはfresh initからGit observationまでのvertical tracerへ変更し、新規scaffolder test pathをallowed surfaceへ追加した | reviewer output on commit `f5e7f77daad6de89bd2f34a62a4abcefe40e678b`; `plan.md`; `docs/authoring/issue-plan.md`; `docs/phase_plan_issue.md` | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-018 | adopted | ChatGPT plan schema re-review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-003を採用。S90/S99へstep-local behavior/planned contractを追加し、S99のreport→三者review→result approval→mandatory final commit→clean checkを固定した。docs ownershipをS90へ統一し、4 canonical READMEはS01-owned/S90 read-onlyとした | `artifacts/20260728t190320z-chatgpt-output-chatgpt-issue-00344-plan-schema-rereview.md`; SHA-256 `ce0a3e4d8ebb2ada6e58cb2d6c98b37187e0d2fcdb5bcf4cae8babb992ac3a62`; 13,718 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-019 | adopted | ChatGPT final plan schema review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004を採用。S99のfinal commit SHAを同じcommit内のreportへ追記する循環契約を解消し、final commit前のreport ledgerとcommit後の外部引き渡し証跡を分離した。EVD-009/010はreviews/handoffのまま維持する | `artifacts/20260728t192021z-chatgpt-output-chatgpt-issue-00344-plan-final-schema-review.md`; SHA-256 `9f0d193c9e271904c8b8f302aee00b1ea6f2af02839aaa9da43328f0961d3a98`; 10,377 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-020 | adopted | ChatGPT plan B-004 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004解消PASSを確認し、追加blocking B-005/B-006を採用。S90のPython testとdocs変更をdev-coder/code-reviewer、doc-writer/spec-reviewerへ順序分離し、TC-344-005を全no-backfill triggerのexact before/after snapshotへ拡張した | `artifacts/20260728t193842z-chatgpt-output-chatgpt-issue-00344-plan-b004-final-review.md`; SHA-256 `f41eeb8198206c5f5fcbbf5d944e39dab715a235d3ba7a09424c941ba119bed0`; 15,087 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-021 | adopted | ChatGPT plan B-005/B-006 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004/B-005/B-006の主要修正PASSを確認し、B-005-R1/B-007を採用。delegated workerのcanonical report write permissionを除去してmain orchestrator統合へ戻し、Ruff check/format exact path listへ`tests/cli_runtime/test_new.py`を追加した | `artifacts/20260728t195703z-chatgpt-output-chatgpt-issue-00344-plan-b005-b006-final-review.md`; SHA-256 `14ce2594144499d708a792b9d11ec390975795380c66518b9e0eaa42da7b0194`; 14,735 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-022 | adopted | ChatGPT final plan pass review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-007のclosureを確認し、B-008を採用。S01/S02/S03/S90をreview→actual commit/approved-no-op→clean→close state→Result Approval→next-step admissionの順へ統一し、S99のpre-commit判断をfinal evidence commit authorizationへ限定した | `artifacts/20260728t201813z-chatgpt-output-chatgpt-issue-00344-plan-final-pass-review.md`; SHA-256 `1fced0dc948df5ee1e836f49b5de1d3ddd259d08a1af676dc1b335ac673cbd6f`; 15,114 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-023 | adopted | ChatGPT plan B-008 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-007/B-005-R1とB-008 step内部順序のclosureを確認し、B-008-R1を採用。依存グラフをS01→S02→S03→S90→S99へ一本化し、S99 predecessorをResult Approval済みかつ`committed|approved-no-op`へ固定した | `artifacts/20260728t203308z-chatgpt-output-chatgpt-issue-00344-plan-b008-final-review.md`; SHA-256 `77763002eaa0f85196948ca9afad3b9d543bc5bdff93cfc2be687842caf28f9a`; 13,529 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-024 | adopted | ChatGPT terminal plan review (`PASS`, advisory) | `plan.md`, `report.md` | connected GitHub appでcommit `00ee3da37a6f75d60969989c8370cba0231adf2c`を確認したfresh terminal review。B-001〜B-008-R1/B-005-R1は全てCLOSED、blocking/non-blocking findingなし。一本道のResult Approval admission、S99 predecessor close state、external-only final evidenceを確認した | `artifacts/20260728t204554z-chatgpt-output-chatgpt-issue-00344-terminal-plan-pass.md`; SHA-256 `fa09700bc8b5bb15b130b89d1b2ef48621879dc08db2f29115c0aac612a806b9`; 14,525 bytes | fresh `spec-reviewer` plan review |
| EAL-025 | adopted | fresh `spec-reviewer` plan review (`PASS`) | `plan.md`, `report.md` | commit `85de9b37a6bacc1ddf56664ac50d3fa42ac8b8ef`を独立レビュー。blocking/material findingなし、`review_status: pass`。P3のS01 Red seed名表記差をexact nodeへ正規化し、plan phaseをapprovedとした | reviewer output; `plan.md`; terminal ChatGPT PASS artifact; parent Epic/workflow/authoring docs | assurance再分類 / planning completion。実装は本依頼のscope外 |
| EAL-026 | adopted | user-specified ChatGPT-First execution method | `plan.md`, `report.md` | step scopeとclosure contractを維持し、pre-step具体化Artifact、担当共有、push済みexact commitのJSON review、finding採否、非循環なevidence-only closure commitを追加した。fresh review PASS後にplanをapprovedへ戻した | `plan.md#11-chatgpt-first-execution-overlay`; D-006; merge commit `3829600aa304ee76c6e8dcfbe31d2b6b2511927b`; EAL-027/EAL-028 | assurance再分類後にS01 pre-step具体化を開始する |
| EAL-027 | adopted | ChatGPT-Use fresh plan amendment review (`FAIL`, advisory) | `plan.md`, `report.md` | commit `41073c582575d6af70a60a95a56203a63b07064d`をGitHub同期後にreview。F-001〜F-003をblocking/majorとして採用し、candidate review commit→fresh review→evidence-only closure commitの非循環順序、S90のrole分離、blocking/major 0のPASS条件へ限定修正した。F-004も採用し、旧PASSをstaleとしてcurrent readinessをblockedへ同期した | `artifacts/20260729t032949z-chatgpt-output-chatgpt-first-plan-review-41073c58.md`; SHA-256 `8715545fe690431dc5d9e1dc43023283a8d07e75a7e9979cff39ae8455f4f4c0`; reviewed commit `41073c582575d6af70a60a95a56203a63b07064d` | 修正をcommit/pushし、新exact SHAへfresh ChatGPT-Use `spec-reviewer`責務review |
| EAL-028 | adopted | ChatGPT-Use fresh plan amendment re-review (`PASS`, advisory) | `plan.md`, `report.md` | GitHub同期後のexact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`をreviewし、finding 0件。F-001〜F-004の解消、非循環SHA境界、S90 role分離、blocking/major 0のPASS条件、prior PASS stale/current blocked同期、機能scopeとIssue 345/346境界不変を確認した | `artifacts/20260729t034457z-chatgpt-output-chatgpt-first-plan-rereview-a0b99765.md`; SHA-256 `9abadebc2beed093c34e399527ba3f57711154123cba1c4dbfbdc729721283f3`; reviewed commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9` | planをapprovedへ戻し、assurance再分類、S01 admission |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | fresh root と future Initiative / Epic / Issue に tracked `.workbench/README.md` を含む optional shell を生成し、existing scope を backfill しない (`I344-RQ-001`〜`I344-RQ-005`) | semantic opacity、node-scoped `workbench copy` compatibility、package parity、generic import / PR delivery の sibling Issue 境界 (`I344-RQ-006`〜`I344-RQ-010`) | low: copy/import/package の副次境界は primary shell を成立させる guardrail に限定し、root copy や generic import 実装を本 Issue へ取り込んでいない | pass: exact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`のfresh ChatGPT-Use `spec-reviewer`責務reviewでfinding 0、scope creepなし |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic requirement/design/plan、provider source、package config、relevant tests、ChatGPT authoring/review Artifacts | F-001〜F-007 を canonical docs に反映。final ChatGPT review は blocking finding なし | adopted | passed | no | promote |
| design | approved requirement、parent Epic、provider source、current copy / package contracts、ChatGPT planning candidate / design reviews | B-001〜B-006、NB-001/NB-002をcanonical designへ修正し、post-B-006 fresh ChatGPT reviewとfresh `spec-reviewer` reviewで新規findingなし | adopted | passed | no | promote |
| plan | approved requirement/design、ChatGPT planning candidate、Standard assurance obligations、current provider/build/test seams、Issue plan authoring規約 | prior findings B-001〜B-008-R1/B-005-R1とChatGPT-First amendment F-001〜F-004をcanonical planへ修正済み | adopted | passed | no | execute approved plan |

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
| 該当なし | iss-00344 | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring path: main orchestratorがcanonical docsへ統合。ChatGPT-first external evidenceをEALで採用し、重複authoringを避けるためdelegated draft laneは使用していない | 該当なし | なし | passed | execute approved plan |

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
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-29 HH:MM - HH:MM）

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- 計画上の出典（Planned source）:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required / covered-existing / inspect-only / manual-required | ... | `command` / 文書点検（docs inspection） / 手動記録（manual record） | pass / approved-no-op / fail / blocked | ... |
| S01 | 緑フェーズ（Green） | ... | ... | `command` / 点検（inspection） / 手動記録（manual record） | pass / fail / blocked | ... |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | ... | 差分点検（diff inspection） / command | pass / approved-no-op / fail / blocked | ... |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none / ... | implementation / review / QA / user report | recorded / added test / deferred / amended plan | tc-001 / new | yes / no | ... |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required / covered-existing / inspect-only / manual-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to execute Issue 344 with ChatGPT-First authoring/review | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/692d/spec-dock` | iss-00344 | current session | dev-coder; doc-writer (S90 only); ChatGPT-Use executing code-reviewer / spec-reviewer / qa-reviewer responsibility contracts | active repo/worktree、active Issue、current session、approved step scope。merge、Issue 345/346、scope expansionは含めない | Issue 344 execution終了 / session end / scope change / user revocation | none | F-001〜F-004修正版をpushし、ChatGPT-Use fresh spec review後にS01を開始 |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `implementation-planner / manual fallback` | `skipped` | skip reason: approved requirement/design/planとChatGPT planning/review Artifactsが既にあり、追加delegated draftは重複authoringになる。今回の実行overlayはmain orchestratorが限定修正した | `passed` | `ready` |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| plan amendment / S01 admission | ChatGPT-First plan amendment review | spec-reviewer | fresh | passed | no | execute approved plan | ChatGPT-Use reviewed exact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`; finding 0。backendはChatGPT-Use、role名は責務契約 |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### セッションログ（2026-07-29 HH:MM - HH:MM）

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
