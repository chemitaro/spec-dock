---
種別: 実装報告書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-12"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00359 実装報告

## 1. 現在の結果

Issue 359のreview済みscopeに従い、次を実装した。

- `spec-dock`と`spec-dock-grill-with-docs`のprovider assetとdogfood projection
- Current CLI操作のread-only / present-only / forbidden分類
- grill skillのexplicit selector、route、title、bootstrap preflight、zero-write、exactly-one、partial recovery契約
- operator-owned `grilling` / `domain-modeling`のread-only利用境界
- provider / dogfood byte parity
- Current docs pointer
- Codex `developer_instructions`から旧SpecDock workflow固有責務だけを削除
- 四routeのpositive test、主要negative test、additive materializationのstatic contract test
- recognized explicit-only policy metadata
- 二skill tree限定のcollision-safe init / update adoption
- no-follow / device / inode再検証を行うskill-local Artifact finalizer

Artifact Runtime、public CLI argument、managed / legacy inventory、obsolete inventory、旧skill、consumer migrationには変更を加えていない。installer変更は二skill treeの非同一existing fileを全copy前に拒否するpreflightだけである。

## 2. 仕様採用と実装権限

- Active context: Initiative `init-local-00003` / Epic `epic-00356` / Issue `iss-00359`。
- Dependency: `deps check iss-00359`は`ready=true`、`blockers=0`。
- Review evidence: `artifacts/20260812t090019z-review-issue-359-strict-pass.md`。P0=0、P1=0、P2=0、P3=0。
- Reviewed bundle: `artifacts/20260812t090016z-bundle-issue-359-reviewed-specifications.zip`、SHA-256 `0d6e0748a79858f63268d4dd46a0bf9718c722188464bb594f3be155516fc79b`。
- Human approval: ユーザーは2026-08-12に、review済み仕様を基準とする実装開始と完了を明示承認した。
- Model boundary: 実装、修正、最終品質ゲートではChatGPT / Oracleを使用しない。
- Adoption route: normal `planning apply`用closed JSONは再構成成果物に含まれず、ユーザーがChatGPT経路を使用しないよう明示したため、既存PASS evidenceとhuman approvalを根拠にmanual adoptionした。
- Promotion: R/D/PのFront Matterを`approved`へ変更した。仕様本文の追加変更はD-359-001と、ユーザーの最終品質ゲート指示を同期したD-359-002である。

Reviewed bundle内のpre-promotion hash:

| 文書 | SHA-256 |
|---|---|
| `requirement.md` | `532f0da2fad3f6756f2b0e06349781d70ffab217148b883ff1d82a1cc6a9a361` |
| `design.md` | `9f17d861d9d83d9a035c5e56030ee49fe86dc272142ed7467d14132ff48303af` |
| `plan.md` | `30858e6bcc92030195fa9539690692e45710d4c42d1118e4cea36e9658eb61c0` |

実装開始後のcurrent hash:

| 文書 | SHA-256 | 差分理由 |
|---|---|---|
| `requirement.md` | `151cf34de26e1ab829ea748d88d79e8760a03cbaa33b265a23409e2fbf2de144` | `状態: approved`へのpromotionのみ |
| `design.md` | `d9dccddfea23fb0a7fba1ce74db0371ba5b6ea268735901ea1c64efec8a996fc` | promotionとD-359-001 |
| `plan.md` | `e44ffcb23b03f1ed6013e18ee0dbeaa4bb21d148c4abe91f18251d1c5492ca52` | promotionとD-359-002（S90 / S99） |

## 3. 仕様解釈・判断台帳

| ID | Status | Type | 判断 | 根拠 / Disposition |
|---|---|---|---|---|
| D-359-001 | resolved | implementation | `spec-dock-grill-with-docs`へ`disable-model-invocation: true`を設定する | descriptionだけではI359-RQ-003のexplicit invocationを強制できない。`design.md` §2.1へpromoted_to_design。最終spec review対象 |
| D-359-002 | resolved | deviation | stepごとのreviewを省略し、S99のFinal QA / Code / Spec reviewへ一本化する | ユーザーの明示指示。TDD Red / Greenとfocused verificationは各stepで維持し、`plan.md` S90 / S99へ反映。final review失敗時は修正と再reviewを実施 |
| D-359-003 | resolved | implementation | docsのskill pointerを相対Markdown linkではなくcode pathにする | provider docsとdogfood docsはroot構造が異なり、同一relative linkはproviderでbrokenになる。byte parityを保つCurrent path pointerとしてapplied |
| D-359-004 | resolved | safety | grillのexplicit-only authorityを`agents/openai.yaml`へ移す | PR #363 P1。Current Codexが認識する`policy.allow_implicit_invocation: false`を採用し、未認識front matter keyを削除。R/D/Pへpromoted |
| D-359-005 | resolved | safety | 二skill treeだけをcollision-aware adoptionにする | PR #363 P1。missing / byte-identicalはmaterialize / adopt、非同一existing fileは全copy前に保持してfail。Target inventory / migrationは#360へ維持 |
| D-359-006 | resolved | safety | Artifact本文をskill-local helperで安全確定する | PR #363 P1。public Artifact CLIを変えず、identity / finalize間のdevice / inode pin、component no-follow traversal、direct pathname write禁止をR/D/Pへpromoted |
| D-359-007 | resolved | safety | additive materializationをdescriptor-relative no-follow / no-replaceにする | S99 P1。final preflight後のtarget差し替えでもgeneric `copy2`を使わず、外部pathへ書かない。R/D/Pへpromoted |

未解決entryはない。新しいfeature、運用flow、証跡、品質gateは追加していない。

## 4. Parent Implementation Exception

- Approval source: ユーザーによる「ChatGPTを使用せず、自分自身の高度な推論能力で実装を完了」の明示指示。
- Allowed changes: `plan.md` §2の対象file、Issue-local R/D/P/report、同scopeのPR修正artifactに加え、PR #363のP1修正に必要な二skillの`agents/openai.yaml`、skill-local安全確定helper、`src/spec_dock/cli.py`の二skill限定collision preflight、その公開境界test。
- Forbidden changes: managed / legacy inventory、obsolete inventory、旧skill prune、consumer migration、publication、Issue 360のTarget inventory / uninstall / migration責務、既存Artifact CLIのpublic argument contract。
- Rollback: 新規skill fileは独立して除去可能。既存config / docs / testsは対象diffを逆適用できる。無関係な既存変更は巻き戻さない。
- Verification: invocation metadata static contract、collision preflightのinit / update public behavior、safe finalizerのno-follow / inode test、focused test、provider / dogfood byte parity、TOML parse、lint、ordinary pytest、sync、validate、S99 final review、PR latest-head再観測。
- Reviewer cadence: per-step reviewはユーザー指示により実施せず、S99 final gateだけをfreshかつissue-wideに実施する。
- User approval: 2026-08-12の再設定ゴール「このissueの実装を完了させ、マージ可能なプルリクエストを作成」「ChatGPT-Useは今後不要」「最終品質ゲートで包括的なレビュー」を、上記P1限定の`approved-local-execution`およびrisk acceptanceとして記録する。

## 5. 変更ファイル

### 新規

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py`
- `.agents/skills/spec-dock/SKILL.md`
- `.agents/skills/spec-dock-grill-with-docs/SKILL.md`
- `.agents/skills/spec-dock-grill-with-docs/agents/openai.yaml`
- `.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py`
- `tests/unit/infra/test_issue_359_skill_helpers.py`

### 変更

- `src/spec_dock/assets/install_root/.codex/config.toml`
- `.codex/config.toml`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `spec-dock/docs/README.md`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_new.py`
- `src/spec_dock/cli.py`（二skill tree限定collision preflight）
- Issue 359 `requirement.md`、`design.md`、`plan.md`、`report.md`

### 変更していない境界

- `_MANAGED_SKILL_NAMES`
- `_LEGACY_MANAGED_SKILL_NAMES`
- obsolete exact path inventory
- Runtime / parser / registry / application / domain / infra
- 旧managed skill asset

## 6. TDDと検証証跡

### Red / characterization

| 対象 | コマンド / 観測 | 結果 |
|---|---|---|
| static contract RED | `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py::test_issue_359_repo_local_skill_contracts_and_additive_materialization -q` | provider `spec-dock/SKILL.md` missingで1 failed。実装後は1 passed |
| four-route characterization | Issue 359 route test | 実装前からCurrent CLI境界が4 passed。Runtime変更不要を確認 |

### Green / regression

| 検証 | 結果 |
|---|---|
| Issue 359 focused contract（static、collision、race、hard-link adoption、finalizer、four-route、主要negative） | 20 passed |
| `tests/unit/infra/test_artifact_templates.py` | 54 passed |
| `tests/cli_runtime/test_storage_core_cli.py` | 4 passed（targeted explicit permission） |
| `tests/unit/infra/test_authoring_kit_assets.py` | 304 passed |
| `make lint` | ruff check / format / mypy pass |
| ordinary `uv run pytest -q` | 1647 passed、2200 policy-skipped |
| affected full-regression diagnosis | 558 passed、28 failed。28件は旧workflow文書、退役済みruntime/API、旧planning asset等の既存契約 |
| `./spec-dock/scripts/spec-dock sync` | pass。active unchanged、current projections regenerated |
| `./spec-dock/scripts/spec-dock validate` | pass、nodes=221 |

通常laneでは`test_init_update.py`とCLI runtimeのfull-regression bodyがpolicy skipされるため、Issue 359のfocused nodeを`--run-full-regression -k issue_359`付きで明示実行した。さらに、影響面の診断として`test_init_update.py`と新規helper testをfull-regression permission付きで完走した。28 failureはいずれもIssue 359のfocused契約外であり、本Issueに取り込むと旧planning / authoring / runtimeの復元になるため修正しない。repository全体のfull-regression、consumer matrix、publication testは実施していない。

### 検出・修正した回帰

初回fast laneでprovider docsのskill相対linkが2件failした。providerとdogfoodで異なるrootを跨ぐ相対linkをbyte-identicalにできないため、Current `.agents/skills/.../SKILL.md`をcode path pointerとして記載した。修正後、authoring asset 304件とordinary suiteがpassした。

最終品質ゲートの初回判定では、旧config責務を要求する既存full-regression test二件、安全契約のsection固定不足、既存Artifact内容を含まないexactly-one snapshot不足をP1として検出した。config contract helperを新しい削除 / 保持境界へ統一し、CLI分類、selector、preflight、one-write、zero-write、partial recoveryをsection単位で固定した。成功時は返却path一件だけを許可して既存Artifactの内容 / symlinkとprotected scopeを比較し、失敗時はcanonical / metadata / active / dependencyも不変であることを確認するよう修正した。影響testはすべてpassした。

Spec reviewの初回指摘二件は、explicit user authorityとRequirement §5を再照合し、full planning closure indexとdelegated-draft ledgerをIssue #359へ追加するscope expansionであるため撤回された。R/D/P、Report、companion、実装、testへ統合していない。

## 7. Parityとadditive materialization

| Pair / contract | 結果 |
|---|---|
| provider / dogfood `spec-dock/SKILL.md` | byte-identical |
| provider / dogfood `spec-dock-grill-with-docs/SKILL.md` | byte-identical |
| provider / dogfood `spec-dock-grill-with-docs/agents/openai.yaml` | byte-identical、implicit invocation禁止 |
| provider / dogfood `spec-dock-grill-with-docs/scripts/finalize-artifact.py` | byte-identical、no-follow / inode-pinned |
| provider / dogfood `docs/README.md` | byte-identical |
| provider / dogfood `.codex/config.toml` | byte-identical、valid TOML |
| `_build_current_managed_file_mappings()` | 二つの新provider skill treeを対応するrepo-local targetへmapping |
| init / update collision boundary | non-identical existing fileを保持し、preflight後のsymlink差し替えでも外部へ書かずfail |
| managed / legacy inventory | baseline exact tupleから変更なし |
| old skill prune / Target inventory cutover | 未実施 |

## 8. 受け入れ条件クロージャ

| AC | 結果 | 主証跡 |
|---|---|---|
| I359-AC-001 | pass | skill tree 2 pairの存在、policy / helperを含むbyte parity |
| I359-AC-002 | pass | current mapping、init / update collision / race test、inventory定数未変更 |
| I359-AC-003 | pass | `spec-dock` read order / output / no-go static contract |
| I359-AC-004 | pass | 三つのCLI side-effect class |
| I359-AC-005 | pass | bare `doctor`と実在GitHub optionのstatic contract |
| I359-AC-006 | pass | recognized explicit-only policy、一selector必須、active fallback禁止 |
| I359-AC-007 | pass | route / title / external dependency contract |
| I359-AC-008 | pass | 四route parameterized test 4 passed |
| I359-AC-009 | pass | exactly-one / protected scope不変、safe finalizerのsymlink / inode test |
| I359-AC-010 | pass | input、route、scope、path、slug、lock negative test |
| I359-AC-011 | pass | partial Artifact stop / no retry static contract |
| I359-AC-012 | pass | forbidden reference static contract |
| I359-AC-013 | pass | docs pointerとprovider / dogfood parity |
| I359-AC-014 | pass | config parity、TOML parse、限定marker削除 / 一般責務保持 |
| I359-AC-015 | pass | exact inventory assertion、CLI差分は二skill限定collision preflightのみ |
| I359-AC-016 | pass | consumer matrix / cutover / prune / publication未実施 |
| I359-AC-017 | pass | IC-2最小入力を下記へ整理。IC-2 passは未宣言 |

## 9. Issue 360 / IC-2 handoff

### Skill entries

- `spec-dock`: provider / dogfoodの二entry path
- `spec-dock-grill-with-docs`: provider / dogfoodの二entry path

### External boundary

- 必須: operator-owned `grilling`と`domain-modeling`
- missing / incompatible: Artifact CLIを呼ばずzero-write
- repository mutationを要求するexternal output: untrusted dataとして拒否

### Legacy inventory for Issue 360

Managed 18件:

`spec-dock-hub`, `spec-dock-initiative-planning`, `spec-dock-epic-planning`, `spec-dock-epic-execution`, `spec-dock-issue-planning`, `spec-dock-issue-execution`, `spec-dock-chatgpt-authoring`, `spec-dock-initiative-planning-manual`, `spec-dock-epic-planning-manual`, `spec-dock-issue-planning-manual`, `spec-dock-clarification`, `spec-dock-adr-facilitation`, `spec-dock-codex-adapter`, `spec-dock-copilot-adapter`, `git-commit-conventional-ja`, `github-pr-observation`, `github-pr-creator`, `github-pr-merge-preparer`。

Legacy managed 3件:

`spec-driven-tdd-workflow`, `spec-dock-system-architect`, `spec-dock-implementation-planner`。

Issue 360はexact implementation commitでTarget inventory、prune / preserve、fresh / update / uninstall migrationを決定する。Issue 359はIC-2 passを自己宣言しない。

## 10. 最終品質ゲート

初回PR前のFinal QA / Code / Spec reviewはpassしたが、PR #363のlatest-head reviewでP1三件が検出されたためsupersededした。修正後の包括的S99では、最初の判定でadditive materializationのpreflight-to-copy raceをP1一件として検出し、二skill targetをdescriptor-relative no-follow / no-replaceへ変更した。再判定では、書き込みを行わないbyte-identical hard-linked regular fileまで拒否する仕様不一致をP1一件として検出し、existing adoptionからlink-count拒否だけを除去した。symlink差し替えとhard-link adoptionの回帰testを追加した。P2二件は非blockerとしてR/D/P/companionへ統合していない。

最終再判定はStandards / safety軸、Specification軸とも`P0=0 / P1=0 / pass`。証跡は`artifacts/20260812t150257z-review-issue-359-final-quality-gate.md`。local final gateは通過した。PR latest-headのpush後再観測まではmerge-preparedを主張しない。

## 11. PR #363 Repair Batch（進行中）

### 11.1 Batch identity

- `batch_path`: `N/A`
- Inline理由: Current Storage Coreの`new artifact` catalogは`pr-repair-batch`を受理しないため、merge-preparerの同一body schemaをscope-local `report.md`へ記録する。runtime catalogを本修正のために拡張しない。
- PR: `https://github.com/chemitaro/spec-dock/pull/363`
- Base / head: `main` / `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
- Observed head: `93e2d44bfe9f5fa1bfca3ac533e5bf073a223108`
- Observation: submitted Codex review、required CI 3件success、未解決P1 3件、merge conflictなし。
- Iteration: `iteration_index=1`、`iteration_count=telemetry only`

### 11.2 Raw Intake Inventory

| ID | reported_priority | decided_priority | validity | merge_blocking | need_to_fix | disposition | root_cause_family | status |
|---|---|---|---|---|---|---|---|---|
| PR363-P1-001 | P1 | P1 | valid | yes | yes | fix-now | `skill-invocation-policy` | implemented |
| PR363-P1-002 | P1 | P1 | valid | yes | yes | fix-now | `additive-skill-ownership` | implemented |
| PR363-P1-003 | P1 | P1 | valid | yes | yes | fix-now | `artifact-finalization-toctou` | implemented |

P2 / P3、CI failure、merge conflict、observation limitationはない。全inventoryをtriage済みとし、P2 / P3由来の変更は行わない。

### 11.3 Consultation fallback binding

- `consultation_status`: `consultation_denied`
- Reason: ユーザーが本実装と今後の修正でChatGPT / Oracleを使用しないよう明示した。
- `fallback_state`: `approved_for_invocation`
- `fallback_invocation_id`: `pr-363-issue359-p1-repair-20260812`
- `fallback_approved_by`: human user
- `fallback_approved_at`: `2026-08-12T13:45:36Z`
- `bound_strategy_context`: PR #363 head `93e2d44bfe9f5fa1bfca3ac533e5bf073a223108`の上記P1三familyだけ。新しいfeature、P2 / P3、Target inventory、uninstall、consumer migration、#360責務を含まない。
- `fallback_manual_analysis_ref`: 本節11.2および11.4
- `fallback_consumed_at`: `2026-08-12T13:45:36Z`
- Expiry: この三familyの修正commitをpushし、PR #363のlatest head再観測が完了した時点、またはinventory / strategy / scopeがmaterialに変わった時点の早い方。再利用しない。

### 11.4 Orchestrator disposition and integrated strategy

| Family | Disposition | 最小修正 |
|---|---|---|
| `skill-invocation-policy` | use | `spec-dock-grill-with-docs/agents/openai.yaml`をprovider / dogfoodへ追加し、`policy.allow_implicit_invocation: false`を正本とする |
| `additive-skill-ownership` | use | 二skill配下のnew asset targetだけをcollision-aware adoption対象とし、missingまたはbyte-identicalだけを許可し、非同一existing fileは全copy前preflightでfail-closedにする |
| `artifact-finalization-toctou` | use | skill-local helperでparent directoryとArtifact inodeをpinし、no-follow open後にidentityを再検証してから本文を確定する |

- Coupling / order: metadataとhelperをprovider authorityへ追加し、collision preflightはそれらを含む二skill tree全体を保護する。public seamのRED test、最小実装、provider / dogfood projection、R/D/P整合の順で進める。
- `strategy_delta`: 初回PRはfront matterだけでexplicit invocationを表し、generic copyとpathname直接writeを信頼していた。修正ではrecognized host metadata、pre-copy content collision、dirfd / inode / no-follow finalizationへ境界を移す。
- Validation: 三seamのfocused test、affected regression、full ordinary suite、lint、parity、sync、validate、一度だけのissue-wide final QA / Code / Spec review、commit / push / latest-head re-observation。
- Residual boundary: Durable ownership inventory、uninstall migration、旧skill pruneは#360。Artifact CLIのpublic argumentは変更しない。
- `orchestrator_disposition`: 三findingとも`use`。修正scopeはP1解消に必要な範囲へ限定する。

### 11.5 Repair units

| Unit | Family | Source | State |
|---|---|---|---|
| PR363-U001 | `skill-invocation-policy` | PR363-P1-001 | `artifacts/20260812t134617z-disc-pr-repair-unit-pr363-u001-skill-invocation-policy.md` / implemented, validated |
| PR363-U002 | `additive-skill-ownership` | PR363-P1-002 | `artifacts/20260812t134618z-disc-pr-repair-unit-pr363-u002-additive-skill-ownership.md` / implemented, validated |
| PR363-U003 | `artifact-finalization-toctou` | PR363-P1-003 | `artifacts/20260812t134618z-01-disc-pr-repair-unit-pr363-u003-artifact-finalization-toctou.md` / implemented, validated |

### 11.6 Re-observation result

未実施。修正、最終品質ゲート、commit、push後にlatest headへ`resume`境界で一度だけ再観測する。
