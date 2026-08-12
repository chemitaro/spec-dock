---
種別: 実装報告書（Issue）
ID: "iss-00359"
タイトル: "Replace Managed Workflow Skills with SpecDock Skills"
関連GitHub: ["#359"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-13"
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
- Codex configを`project_doc_fallback_filenames = [".codex/AGENTS.md"]`だけに限定し、その他の設定を利用者のCodex設定へ委譲
- 四routeのpositive test、主要negative test、additive materializationのstatic contract test
- recognized explicit-only policy metadata
- 二skill tree限定のcollision-safe init / update adoption
- no-follow / device / inode / `ctime_ns`再検証を行うskill-local Artifact finalizer

Artifact Runtime、public CLI argument、managed / legacy inventory、obsolete inventory、旧skill、consumer migrationには変更を加えていない。installer変更は二skill treeの非同一existing fileを全copy前に拒否するpreflightだけである。

## 2. 仕様採用と実装権限

- Active context: Initiative `init-local-00003` / Epic `epic-00356` / Issue `iss-00359`。
- Dependency: `deps check iss-00359`は`ready=true`、`blockers=0`。
- Review evidence: `artifacts/20260812t090019z-review-issue-359-strict-pass.md`。P0=0、P1=0、P2=0、P3=0。
- Current reviewed bundle: `artifacts/20260812t090016z-bundle-issue-359-reviewed-specifications.zip`、SHA-256 `ffd9876e4537dee3a8a835689ab2567e6e705397024c8ad969329875642dcec6`。required CI blockerの`ctime_ns`修正をR/D/P、companion、final gate evidenceへ反映して差し替えた。
- Human approval: ユーザーは2026-08-12に、review済み仕様を基準とする実装開始と完了を明示承認した。
- Model boundary: 実装、修正、最終品質ゲートではChatGPT / Oracleを使用しない。
- Adoption route: normal `planning apply`用closed JSONは再構成成果物に含まれず、ユーザーがChatGPT経路を使用しないよう明示したため、既存PASS evidenceとhuman approvalを根拠にmanual adoptionした。
- Promotion: R/D/PのFront Matterを`approved`へ変更した。仕様本文の追加変更はD-359-001、ユーザーの最終品質ゲート指示を同期したD-359-002、Codex configを最小化したD-359-009、final gateのP1を閉じたD-359-010である。

Reviewed bundle内のpre-promotion hash:

| 文書 | SHA-256 |
|---|---|
| `requirement.md` | `532f0da2fad3f6756f2b0e06349781d70ffab217148b883ff1d82a1cc6a9a361` |
| `design.md` | `9f17d861d9d83d9a035c5e56030ee49fe86dc272142ed7467d14132ff48303af` |
| `plan.md` | `30858e6bcc92030195fa9539690692e45710d4c42d1118e4cea36e9658eb61c0` |

現在のcanonical hash:

| 文書 | SHA-256 | 差分理由 |
|---|---|---|
| `requirement.md` | `e11e3f5b074681351c4d79163fdbe34a7629557ba72bf5bd16747672f766d608` | promotion、D-359-009、D-359-010 |
| `design.md` | `684efefcded0a0910a7a3e1afd48d3cac4691537a64e09667c4624ea18f4dcd9` | promotion、D-359-001、D-359-009、D-359-010 |
| `plan.md` | `9361670122d7286efa248bb7620e76c6d56412be02cb89a21385f636ef9c89ca` | promotion、D-359-002、D-359-009、D-359-010 |

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
| D-359-008 | resolved | safety | finalizer identityへ`ctime_ns`を追加する | Provider CI blocker。Linuxでunlink後にinodeが即時再利用され、device / inodeだけでは置換を識別できなかった。public Artifact CLIとpartial recoveryを変えず、truncate前のidentity比較だけを強化した |
| D-359-009 | resolved | scope | repo-local Codex configは`project_doc_fallback_filenames`だけを保持する | ユーザーの明示決定。SpecDock固有workflowだけでなく`developer_instructions`、`personality`、`[agents]`、`[mcp_servers.*]`を削除し、Codex動作は利用者設定へ委ねる。既存consumer migrationは#360 |
| D-359-010 | resolved | safety | CLI生成scaffoldを保持してroute sectionだけを確定し、open済みpathの移動を再確認する | Final Code / QA P1。helperはID / title / parent / template / authority / title headingを保持し、write直前にparent chainをrepo rootから再bindする。installerは最初のdata writeを行う関数内でparentを再bindし、移動検出後はpathname cleanupを行わずreplacementを保持する |

未解決entryはない。新しいfeature、運用flow、証跡、品質gateは追加していない。

## 4. Parent Implementation Exception

- Approval source: ユーザーによる「ChatGPTを使用せず、自分自身の高度な推論能力で実装を完了」の明示指示。
- Allowed changes: `plan.md` §2の対象file、Issue-local R/D/P/report、同scopeのPR修正artifactに加え、PR #363のP1修正に必要な二skillの`agents/openai.yaml`、skill-local安全確定helper、`src/spec_dock/cli.py`の二skill限定collision preflight、その公開境界test、およびユーザーが明示したCodex configの一項目化。
- Forbidden changes: managed / legacy inventory、obsolete inventory、旧skill prune、consumer migration、publication、Issue 360のTarget inventory / uninstall / migration責務、既存Artifact CLIのpublic argument contract。
- Rollback: 新規skill fileは独立して除去可能。既存config / docs / testsは対象diffを逆適用できる。無関係な既存変更は巻き戻さない。
- Verification: invocation metadata static contract、collision preflightのinit / update public behavior、safe finalizerのno-follow / inode reuse / `ctime_ns` test、Codex configのexact-key contract、focused test、provider / dogfood byte parity、TOML parse、lint、ordinary pytest、sync、validate、S99 final review、PR latest-head再観測。
- Reviewer cadence: per-step reviewはユーザー指示により実施せず、S99 final gateだけをfreshかつissue-wideに実施する。
- User approval: 2026-08-12の再設定ゴール「このissueの実装を完了させ、マージ可能なプルリクエストを作成」「ChatGPT-Useは今後不要」「最終品質ゲートで包括的なレビュー」と、2026-08-13のCodex config一項目化の決定を、`approved-local-execution`およびscope authorityとして記録する。

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
| Issue 359 focused contract（static、collision、race、hard-link adoption、finalizer、four-route、主要negative） | 27 passed |
| `tests/unit/infra/test_artifact_templates.py` | 54 passed |
| `tests/cli_runtime/test_storage_core_cli.py` | 4 passed（targeted explicit permission） |
| `tests/unit/infra/test_authoring_kit_assets.py` | 304 passed |
| `make lint` | ruff check / format / mypy pass |
| ordinary `uv run pytest -q` | 1651 passed、2203 policy-skipped |
| D-359-009 config exact contract | focused 1 passed、関連helper/callsite 5 passed |
| D-359-009 CLI route explicit run | 7 passed、43 deselected |
| D-359-009 storage core explicit run | 4 passed |
| `test_init_update.py` full-regression diagnosis | 556 passed、29 failed。失敗は旧workflow文書、退役済みruntime/API、旧planning / authoring asset等の既存契約で、Issue 359 focused nodeの失敗なし |
| `./spec-dock/scripts/spec-dock sync` | pass。active unchanged、current projections regenerated |
| `./spec-dock/scripts/spec-dock validate` | pass、nodes=221 |

通常laneでは`test_init_update.py`とCLI runtimeのfull-regression bodyがpolicy skipされるため、Issue 359のfocused nodeを`--run-full-regression -k issue_359`付きで明示実行した。さらに、影響面の診断として`test_init_update.py`と新規helper testをfull-regression permission付きで完走した。28 failureはいずれもIssue 359のfocused契約外であり、本Issueに取り込むと旧planning / authoring / runtimeの復元になるため修正しない。repository全体のfull-regression、consumer matrix、publication testは実施していない。

### 検出・修正した回帰

初回fast laneでprovider docsのskill相対linkが2件failした。providerとdogfoodで異なるrootを跨ぐ相対linkをbyte-identicalにできないため、Current `.agents/skills/.../SKILL.md`をcode path pointerとして記載した。修正後、authoring asset 304件とordinary suiteがpassした。

最終品質ゲートの初回判定では、旧config責務を要求する既存full-regression test二件、安全契約のsection固定不足、既存Artifact内容を含まないexactly-one snapshot不足をP1として検出した。config contract helperを新しい削除 / 保持境界へ統一し、CLI分類、selector、preflight、one-write、zero-write、partial recoveryをsection単位で固定した。成功時は返却path一件だけを許可して既存Artifactの内容 / symlinkとprotected scopeを比較し、失敗時はcanonical / metadata / active / dependencyも不変であることを確認するよう修正した。影響testはすべてpassした。

最終gate後のrequired Provider CIでは、Linux filesystemがunlink直後の同名fileへinodeを再利用し、device / inodeだけのpinが置換を見逃すP1相当の安全blockerを検出した。finalizer identityへ`ctime_ns`を追加し、lstat / open / fstatの三値が一致する場合だけtruncateするよう修正した。deterministicなctime mismatch testを追加し、helper 6件、Issue 359 focused 21件、lint、ordinary 1648件がlocalでpassした。これは新しいreview工程ではなく、S99とrequired CIで検出したblockerのclosureである。

Spec reviewの初回指摘二件は、explicit user authorityとRequirement §5を再照合し、full planning closure indexとdelegated-draft ledgerをIssue #359へ追加するscope expansionであるため撤回された。R/D/P、Report、companion、実装、testへ統合していない。

## 7. Parityとadditive materialization

| Pair / contract | 結果 |
|---|---|
| provider / dogfood `spec-dock/SKILL.md` | byte-identical |
| provider / dogfood `spec-dock-grill-with-docs/SKILL.md` | byte-identical |
| provider / dogfood `spec-dock-grill-with-docs/agents/openai.yaml` | byte-identical、implicit invocation禁止 |
| provider / dogfood `spec-dock-grill-with-docs/scripts/finalize-artifact.py` | byte-identical、no-follow / device / inode / `ctime_ns`-pinned |
| provider / dogfood `docs/README.md` | byte-identical |
| provider / dogfood `.codex/config.toml` | byte-identical、valid TOML、設定項目は`project_doc_fallback_filenames`だけ |
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
| I359-AC-009 | pass | exactly-one / protected scope不変、safe finalizerのsymlink / inode reuse / `ctime_ns` test |
| I359-AC-010 | pass | input、route、scope、path、slug、lock negative test |
| I359-AC-011 | pass | partial Artifact stop / no retry static contract |
| I359-AC-012 | pass | forbidden reference static contract |
| I359-AC-013 | pass | docs pointerとprovider / dogfood parity |
| I359-AC-014 | pass | config parity、TOML parse、exact equalityによりfallback一項目だけを固定 |
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

最終再判定はStandards / safety軸、Specification軸とも`P0=0 / P1=0 / pass`。その後required Provider CIが検出したinode reuse blockerも、同じfinal gateのclosureとして`ctime_ns` pinと回帰testで修正し、local再検証を通過した。証跡は`artifacts/20260812t150257z-review-issue-359-final-quality-gate.md`。PR latest-headのpush後再観測まではmerge-preparedを主張しない。

D-359-009は上記の過去判定後に行ったユーザー承認済み変更であるため、過去のpassを流用しなかった。今回のworking treeを含むIssue-wide Final QA / Code / Spec reviewでは、config一項目化に加え、親component race、Artifact / parent移動、CLI生成metadata保持をP1として再現・修正した。最終candidateはCode / Spec / QAの三軸すべて`pass`、`P0=0 / P1=0`である。focused 27件、lint、ordinary suite、provider / dogfood parity、config exact、diff check、validateがpassした。P2 / P3は非blockerとして実装・R/D/P/companionへ統合していない。

## 11. PR #363 Repair Batch（進行中）

### 11.1 Batch identity

- `batch_path`: `N/A`
- Inline理由: Current Storage Coreの`new artifact` catalogは`pr-repair-batch`を受理しないため、merge-preparerの同一body schemaをscope-local `report.md`へ記録する。runtime catalogを本修正のために拡張しない。
- PR: `https://github.com/chemitaro/spec-dock/pull/363`
- Base / head: `main` / `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
- First observed head: `93e2d44bfe9f5fa1bfca3ac533e5bf073a223108`
- Latest observed head: `0159985c266930519bfce00709f07f0a9477db04`
- Latest observation: Provider CI run `31610744167`がhelperのinode replacement testでfailure。Codex reviewはcurrent completion signal前、merge conflictなし。
- Iteration: `iteration_index=2`、`iteration_count=telemetry only`

### 11.2 Raw Intake Inventory

| ID | reported_priority | decided_priority | validity | merge_blocking | need_to_fix | disposition | root_cause_family | status |
|---|---|---|---|---|---|---|---|---|
| PR363-P1-001 | P1 | P1 | valid | yes | yes | fix-now | `skill-invocation-policy` | implemented |
| PR363-P1-002 | P1 | P1 | valid | yes | yes | fix-now | `additive-skill-ownership` | implemented |
| PR363-P1-003 | P1 | P1 | valid | yes | yes | fix-now | `artifact-finalization-toctou` | implemented |
| PR363-CI-001 | CI | required-ci | valid | yes | yes | fix-now | `artifact-finalization-inode-reuse` | implemented-local |

P2 / P3、merge conflict、observation limitationはない。全inventoryをtriage済みとし、P2 / P3由来の変更は行わない。

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

#### CI repair fallback binding

- `consultation_status`: `consultation_denied`
- Reason: ユーザーの明示指示「ChatGPTを使用せずに、自分自身の高度な推論能力を用いて、この実装を完了」に従う。
- `fallback_state`: `approved_for_invocation`
- `fallback_invocation_id`: `pr-363-issue359-ci-inode-reuse-20260813`
- `fallback_approved_by`: human user
- `fallback_approved_at`: `2026-08-12T15:12:41Z`
- `bound_strategy_context`: PR #363 head `0159985c266930519bfce00709f07f0a9477db04`のrequired Provider CI failure `PR363-CI-001`だけ。Artifact CLI、planning、P2 / P3、#360責務を含まない。
- `fallback_manual_analysis_ref`: 本節11.2、11.4および`artifacts/20260812t151202z-disc-pr-repair-unit-pr363-u004-ci-inode-reuse.md`
- `fallback_consumed_at`: `2026-08-12T15:12:41Z`
- Expiry: `PR363-CI-001`の修正commitをpushした時点、またはinventory / strategy / scopeがmaterialに変わった時点の早い方。再利用しない。

### 11.4 Orchestrator disposition and integrated strategy

| Family | Disposition | 最小修正 |
|---|---|---|
| `skill-invocation-policy` | use | `spec-dock-grill-with-docs/agents/openai.yaml`をprovider / dogfoodへ追加し、`policy.allow_implicit_invocation: false`を正本とする |
| `additive-skill-ownership` | use | 二skill配下のnew asset targetだけをcollision-aware adoption対象とし、missingまたはbyte-identicalだけを許可し、非同一existing fileは全copy前preflightでfail-closedにする |
| `artifact-finalization-toctou` | use | skill-local helperでparent directoryとArtifact inodeをpinし、no-follow open後にidentityを再検証してから本文を確定する |
| `artifact-finalization-inode-reuse` | use | helper identityへ`ctime_ns`を追加し、inodeが再利用されてもtruncate前にreplacementを拒否する |

- Coupling / order: metadataとhelperをprovider authorityへ追加し、collision preflightはそれらを含む二skill tree全体を保護する。public seamのRED test、最小実装、provider / dogfood projection、R/D/P整合の順で進める。
- `strategy_delta`: 初回PRはfront matterだけでexplicit invocationを表し、generic copyとpathname直接writeを信頼していた。修正ではrecognized host metadata、pre-copy content collision、dirfd / inode / no-follow finalizationへ境界を移す。
- Validation: 三seamのfocused test、affected regression、full ordinary suite、lint、parity、sync、validate、一度だけのissue-wide final QA / Code / Spec review、commit / push / latest-head re-observation。
- Residual boundary: Durable ownership inventory、uninstall migration、旧skill pruneは#360。Artifact CLIのpublic argumentは変更しない。
- `orchestrator_disposition`: 初回三findingとrequired CI blockerを`use`。修正scopeはP1解消に必要な範囲へ限定する。
- CI `strategy_delta`: `device + inode`だけのpinから`device + inode + ctime_ns`へ変更し、Linux inode reuseというCI実測条件を識別する。public Artifact CLIとpartial recoveryは変更しない。

### 11.5 Repair units

| Unit | Family | Source | State |
|---|---|---|---|
| PR363-U001 | `skill-invocation-policy` | PR363-P1-001 | `artifacts/20260812t134617z-disc-pr-repair-unit-pr363-u001-skill-invocation-policy.md` / implemented, validated, commit `7d303a11` |
| PR363-U002 | `additive-skill-ownership` | PR363-P1-002 | `artifacts/20260812t134618z-disc-pr-repair-unit-pr363-u002-additive-skill-ownership.md` / implemented, validated, commit `7d303a11` |
| PR363-U003 | `artifact-finalization-toctou` | PR363-P1-003 | `artifacts/20260812t134618z-01-disc-pr-repair-unit-pr363-u003-artifact-finalization-toctou.md` / implemented, validated, commit `7d303a11` |
| PR363-U004 | `artifact-finalization-inode-reuse` | PR363-CI-001 | `artifacts/20260812t151202z-disc-pr-repair-unit-pr363-u004-ci-inode-reuse.md` / implemented, validated locally, commit `9bfcecae` |

### 11.6 Re-observation result

head `0159985c266930519bfce00709f07f0a9477db04`ではProvider CI failureを観測し、current Codex review completion前に停止した。trigger boundaryはcomment `5268667887` / `2026-08-12T15:09:32Z`。PR363-U004修正後のnew latest headを新しいfixed trigger境界で再観測する。

## 12. D-359-009 Codex config最小化

- Provider authorityとdogfood projectionは、ともに`project_doc_fallback_filenames = [".codex/AGENTS.md"]`の一行だけであり、byte-identicalである。
- `tomllib.loads()`後のmappingをexact equalityで検証するため、未知の追加keyやtableも回帰として検出する。
- historical Issue 170 migration testは当時のstale configをtest fixture内で自己完結させ、Current provider configへ旧`developer_instructions`を再導入しない。
- fresh provider / dogfoodだけを本Issueで変更する。既存consumerのconfig migrationはIssue #360へ渡す。
- `make lint`とordinary suiteはpassした。Issue 359のpolicy-selected testは`--run-full-regression`で明示実行してpassした。
- 最終品質ゲート: Code / Spec / QAともpass、P0=0 / P1=0。P2 / P3は非blockerとして未統合。
