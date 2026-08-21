---
種別: 要件定義書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-21"
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

fresh target に対する `spec-dock init [path]`、`spec-dock init --force [path]`、`spec-dock update [path]` を、Issue 368 後の実装境界である `WorkspaceAssessment`、`ExecutableMutationPlan`、`OperationJournalStore`、`apply_distribution_plan()`、`DistributionProcessResult` へ統合する。

Issue 369 完了後は、新規 fresh operation が CLI 所有の schema-1 `.distribution-retry.json`、`scaffold_applier` callback、recursive scaffold copier、plan 外の `spec-dock.version` write を使用してはならない。fresh target の作成対象は package の Current catalog、fresh scaffold、generated active fallback、version、required directories、fresh-only Workbench seed から一意に導出し、collision-free な target だけを descriptor-bound kernel で provision する。

## 確認済みの実装基線

本 Issue は、次の現行事実を前提とする。

- `DistributionOperation` は既に `fresh`、`update`、`init-force`、`uninstall` を表現し、`build_distribution_plan(..., operation="fresh")` は fresh の `create` / `adopt` / preserve-and-block classification を生成できる。
- Current contract は `src/spec_dock/assets/managed_distribution.json` に列挙されていない。Current files は `_current_assets()` と `_scaffold_assets()` が physical package assets から構築し、root shortcut `spec` は `_CURRENT_SHORTCUTS`、generated active state は CLI の `_active_fallback_distribution_assets()`、version は generated regular asset として構築される。
- `_scaffold_assets(..., operation="fresh")` は `templates/root/.workbench/README.md` を `spec-dock/.workbench/README.md` として fresh contract にだけ追加する。recognized `update` / `init-force` はこの seed を contract に含めない。
- Issue 368 により recognized target の `update` / `init --force` は `execute_recognized_distribution()` の単一路線を使用する。`WorkspaceAssessment` と `ExecutableMutationPlan` は read-only assessment と mutation authority を分離し、schema-2 forward guard、`.distribution-journal.json`、action checkpoint、staging lease、created-parent binding を使用する。
- 現行 journal intent、journal parser、`DistributionProcessResult` は `update` / `init-force` に限定される。fresh はまだこの service を使用しない。
- 現行 fresh path は `_install_fresh_distribution_unlocked()` または `_install_fresh_compatibility_distribution_unlocked()` から `apply_distribution_plan(..., scaffold_applier=...)` を呼び、`_install_spec_dock_bound()` と recursive copy helpers で scaffold を action list 外から変更し、最後に `_write_spec_dock_version()` を plan 外で呼ぶ。
- 現行 CLI admission は、`spec-dock` が存在しない target に対する `update` を `workspace-missing` で拒否する。fresh target の `update` provisioning は Issue 369 が追加する意図的な compatibility change であり、既存動作の記述ではない。
- 現行 fresh flow に interactive prompt または backup 作成はない。Issue 369 はそれらを新設しない。

## 用語

### fresh target

root operation lock で束縛した target root が real directory であり、次のいずれかに該当する target を fresh target とする。

1. `spec-dock` が存在しない。
2. `spec-dock` が exact empty real directory である。
3. successful `uninstall --apply --keep-specs` が残した、`spec-dock/initiatives` だけを持つ exact preserved-specs workspace である。
4. fresh intent に属する有効な schema-1 marker、`purpose="fresh-journal-forward-only"` の schema-2 forward guard、または operation journal があり、同じ root と authority で recovery 可能である。

`spec-dock` が symlink、non-directory、説明不能な non-empty workspace、または別 intent の recovery state である場合は fresh target とみなさず、write 前に拒否する。

### requested entrypoint と effective intent

- requested entrypoint は `init`、`init --force`、`update` のいずれかであり、public success label、retry command、diagnostic mapping のために CLI adapter が保持する。
- effective intent は journal authority に用いる `fresh`、`update`、`init-force` のいずれかである。
- fresh target に対する三つの requested entrypoint はすべて effective intent `fresh` へ正規化する。
- recognized target に対する `update` と `init --force` は従来どおり、それぞれ effective intent `update` と `init-force` を使用する。
- `init` without `--force` は recognized target を fresh として再解釈しない。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I369-R01 | existing real target directory に対する `spec-dock init [path]`、`spec-dock init --force [path]`、`spec-dock update [path]` の command name、flag grammar、target resolution、success output format、exit code contract を維持する。invalid target directory は exit 2、operation blocker または recovery failure は exit 1、成功は exit 0 とする。 |
| I369-R02 | fresh target に対する三つの requested entrypoint を effective intent `fresh` として admission し、同じ fresh Contract / Assessment / Plan / Kernel / Journal / Result を使用する。現行で `workspace-missing` となる fresh `update` は、本 Issue の完了後は fresh provisioning へ進む。 |
| I369-R03 | recognized target の `update` / `init --force` は `execute_recognized_distribution()` compatibility route を維持し、Issue 368 の intent、authority、journal、generated refresh、output mapping を変更しない。recognized target の second `init` without `--force` は mutation せず、`'spec-dock' already exists. Use 'spec-dock update' or re-run with '--force'.` guidance を維持する。 |
| I369-R04 | fresh Desired Distribution Contract は、`_current_assets()` の Current install-root files、`_scaffold_assets(..., operation="fresh")` の scaffold files、synthetic root `spec` symlink、package version asset、`_active_fallback_distribution_assets()` 相当の `spec-dock/active/{initiative,epic,issue}` symlink または `.path` fallback と `spec-dock/active/context-pack.md`、required directories、fresh-only `spec-dock/.workbench/README.md` seed から構築する。 |
| I369-R05 | `managed_distribution.json` は historical recognition / obsolete provenance の正本として維持し、Current fresh inventory の重複台帳にしない。Current bytes、mode、symlink target は physical package sources と generated-asset builder から一度だけ導出する。 |
| I369-R06 | fresh contract は少なくとも current installer が作成する `spec-dock/initiatives`、`spec-dock/active`、`spec-dock/.agent`、`spec-dock/.workbench` と、shipped/generated assets に必要な parent directories を明示する。asset child を持たない required directory も plan 内 action として表現し、callback または plan 外 `mkdir` にしない。ただし journal storage 自体を格納する top-level `spec-dock` bootstrap は I369-R12 の限定例外とする。 |
| I369-R07 | fresh assessment は target root、全 parent chain、exact target、file type、device/inode/ctime、link count、regular bytes/mode、symlink target を no-follow で観測する。unknown current collision、historical-but-not-current identity、wrong mode、unsafe type、symlink container/final、hard-link mutation risk、root/parent rebind、provider source mutation、unsupported no-follow/no-replace capabilityがあれば、managed target mutation 前に typed blocker または recovery-required result を返す。 |
| I369-R08 | root 内の unrelated content、`spec-dock/initiatives/**` の preserved history、fresh contract に含まれない root Workbench content、unknown external siblings を action authority に含めず byte-identical に保持する。unknown entry を探して recursive clean、replace、prune してはならない。 |
| I369-R09 | fresh-only Workbench seed は target `spec-dock/.workbench/README.md` が absent の場合だけ `create` する。provider bytes と mode が exact に一致する既存 regular fileは `adopt` し、現行で許容される identical hard link も書き換えない。modified content、wrong mode、symlink/unsafe parent は preserve-and-block とする。recognized `update` / `init-force` は seed を backfill しない。 |
| I369-R10 | fresh mutation grammar は `ensure-directory`、`create`、`adopt`、`preserve`、`block` に限定する。fresh intent は existing entry を `upgrade` または `prune` しない。`upgrade` と `prune` は recognized/deprovision owner のままとする。 |
| I369-R11 | regular file create は staged write、captured mode、fsync、exact digest verification、no-replace publish を使用する。symlink create は normalized in-root target、unique stage、no-replace publish を使用する。destination が assessment 後に出現した場合は上書きへ fallback せず、外部 entry を保持して recovery-required とする。 |
| I369-R12 | `spec-dock` が absent の場合だけ、root lock と root descriptor に束縛した fresh bootstrap が top-level real directory を一度作成できる。bootstrap 後は fresh 専用 schema-2 forward guard と journal を最初の managed asset mutation より前に発行する。guard/journal 発行が同期的に失敗した場合、作成した exact inode が空であり replacement がないと証明できるときだけ rmdir する。crash で exact empty boundary が残った場合は次回 fresh admission が再開する。 |
| I369-R13 | 新規 fresh operation は schema version 2 の既存 field shape と root/operation/contract/plan bindingを再利用するが、guard `purpose` は fresh 専用の `fresh-journal-forward-only` とする。Issue 368 parserがこのpurposeをunsupportedとしてmanaged target mutation前に拒否し、`recognized-journal-forward-only` はrecognized `update` / `init-force`専用のまま維持する。新parserはpurposeとoperation/intent/authorityの組合せを検証し、fresh guardをlegacy schema-1 writerへ渡さない。journal `intent` は `fresh`、`authority` は `fresh-distribution-provisioning` とし、recognized journal authorityと混同しない。 |
| I369-R14 | no-op または blocker-only path は、bootstrap が不要な場合、prompt、backup、schema-1 marker、schema-2 guard、journal、staging entry を作成しない。現行実装に存在しない prompt/backup を追加しない。 |
| I369-R15 | partial failure は root identity、effective intent `fresh`、authority、package/contract identity、canonical plan digest、action order、exact pre/postcondition、stage/GC lease、created-directory binding に束縛した forward recovery state を残す。同じ contract と exact stateだけが resume でき、unknown divergence は mutation 前に拒否する。whole-operation rollback は要求しない。 |
| I369-R16 | fresh recovery state は `init`、`init --force`、`update` のいずれから到達しても effective intent `fresh` のまま再開する。requested entrypoint を recognized `update` / `init-force` authority に読み替えてはならない。`uninstall`、Issue 371 purge、別 root、downgrade package、contract mismatch は拒否する。 |
| I369-R17 | existing schema-1 `purpose=distribution-rerun` / `operation=fresh` marker は新規作成しない。exact root、exact marker identity/bytes、supported phase、same package contract、valid stage ownership、blocker-free fresh reassessmentを証明できる場合だけ、current tree を再分類して schema-2 guard/journalへ one-way conversionする。legacy phase名だけから completed action や cleanup authorityを推測しない。証明不能な marker は保持して recovery-required とする。 |
| I369-R18 | successful completion は全 fresh contract path が `adopt` または authorized `preserve`、required directories が safe real directory、generated/version content が current contract、regular filesのbytes/mode、symlink targetがexpectedと一致することを再assessmentしてから guard/journalを exact-identity cleanupする。 |
| I369-R19 | CLI result adapter は `DistributionProcessResult(status="completed"|"blocked"|"recovery_required")` を current public surfaceへ写像し、absolute provider paths、source bytes、credentialsを出力しない。existing fresh `init` retry は `spec-dock init` guidanceを維持し、新たに有効化する fresh `init --force` / `update` の retry commandは requested entrypointを保持する。legacy markerにrequested entrypoint evidenceがない場合は canonical `spec-dock init`を使用する。 |
| I369-R20 | fresh call graphから `_install_fresh_distribution_unlocked()`、`_install_fresh_compatibility_distribution_unlocked()`、fresh use of `_install_spec_dock_bound()`、`scaffold_applier`、fresh schema-1 marker phase writer、plan外 `_write_spec_dock_version()`を除去する。shared helperまたはuninstallで実際に使用されるコードはcall graph確認なしに削除しない。 |
| I369-R21 | focused verification と final verification は provider test-lane policy に従う。ordinary focused run で `full_regression` tests が policy-skip された結果をbehavior passとして扱わず、focused selectionへ `--run-full-regression`を付けてledger missing-node exit 3となるcommandを成功条件にしない。 |

## スコープ

### 対象

- fresh target admission for `init` / `init --force` / `update`
- requested entrypoint と effective intent の分離
- `WorkspaceAssessment` / `ExecutableMutationPlan` / `DistributionProcessResult` の fresh 対応
- fresh physical/generated contract と required-directory contract
- `ensure-directory` action と created-directory binding
- top-level `spec-dock` の限定 bootstrap
- schema-2 guard / journal による fresh forward recovery
- schema-1 fresh marker の bounded one-way conversion
- fresh-only Workbench seed
- fresh CLI result mapping と retry guidance
- legacy fresh callback / copier / marker / version route の撤去
- unit、CLI runtime、package parity、provider test-lane tests

### 対象外

- recognized `update` / `init-force` reconciliation semantics の再設計
- `uninstall` deprovision（Issue 370）
- history purge / remove-specs authority（Issue 371）
- all-surface、Linux/macOS/package final parity campaign（Issue 372）
- new public command または flag
- arbitrary project scaffolding
- Windows support
- prompt、confirmation、backup UX の追加
- unknown user content のcleanup
- whole-operation rollback

## 失敗・境界条件

- target root は caller が用意した existing real directory でなければならない。CLI は repository root 自体を作成しない。
- provider source tree、manifest、required runtime executable、fresh Workbench seed source の不正は bootstrap 前に拒否する。
- root-level Current path または `spec` shortcut collision は `spec-dock` bootstrap 前に検出し、target write 0 とする。
- top-level `spec-dock` bootstrap 後に race または full assessment blocker を検出した場合、exact empty bootstrap directoryだけを戻せる。non-empty、replaced、symlinked directoryをcleanupしない。
- journal/guard作成後の failure は recovery metadataを保持する。journal作成自体はmanaged asset mutationではないが、no-write pathの証拠として区別する。
- missing parent作成直後、binding checkpoint直前に停止しても、次回はempty/explained closed set と exact inode が一致する場合だけ binding を昇格する。
- regular/symlink stageの作成、write、publish、cleanup、checkpointの各境界で停止しても、leased exact identityだけをcleanupする。
- destination appearance、root/parent rebind、same-bytes different-inode replacement、hard-link topology changeは上書きまたは再取得せず fail closed とする。
- fresh postconditionはunknown extra entryを削除して成立させない。
- fresh journal完了後のguard/journal cleanup failureはterminal recovery stateを保持し、target actionsを再適用せずcleanupだけを完了する。
- platformにrequired `flock`、`O_NOFOLLOW`、directory descriptor、no-replace rename、必要なsymlink fallbackがない場合は最初のmanaged asset mutation前に拒否する。
- destination parentのwritabilityがassessmentだけで証明できない場合、write-zeroを断定しない。failureがjournal作成後ならrecovery-requiredとし、既存user entryを変更しない。

## 受け入れ条件

1. fresh target の `init`、`init --force`、`update` が effective intent `fresh` として同じ assessment、executable plan、journal store、kernel、resultを使用する。
2. absent `spec-dock`、exact empty workspace、preserved-specs workspaceのentrypoint matrixがgolden testsで固定され、fresh `update`が成功する。
3. recognized targetの`update` / `init --force` と second `init` guidanceにIssue 368以後のregressionがない。
4. collision-free fresh targetでCurrent install-root files、scaffold files、root `spec`、fresh Workbench seed、required directories、active fallback、versionが作成される。
5. installed regular filesのrelative path、bytes、modeとsynthetic/generated symlink targetがfresh contractと一致し、runtime wrapper以外へ不要なexecute bitを付与しない。
6. unrelated root content、preserved initiatives、unknown siblings、existing root Workbench contentが変更されない。
7. Current collision、wrong mode、symlink/directory/special collision、unsafe parent、provider mutation、root rebindが外部entryを変更せずblockまたはrecovery-requiredになる。
8. fresh-only Workbench seedのabsent/create、exact/adopt、hard-link/adopt、modified/block、symlink-parent/blockと、recognized no-backfillがtestsで固定される。
9. top-level bootstrap、guard-only、journal-prepared、created-directory、stage reservation/write/publish、checkpoint、terminal cleanupのfault injectionからsame-plan retryが収束するかtyped blockerになる。fresh guard-only fixtureをIssue 368 parserへ入力した場合はmarker bytesを再書込せずmanaged target mutation 0で拒否し、Issue 369 parserでは同じguardからfresh journal recoveryへだけ進む。
10. schema-1 fresh markerは証明可能なstateだけがschema-2へone-way conversionされ、unsupported/mismatched/forged stateはmarkerを保持してwrite前に拒否される。
11. source inspectionとcall-graph testにより、fresh routeから`scaffold_applier`、recursive scaffold mutation、CLI schema-1 marker writer、plan外version writeが到達不能または削除済みである。
12. ordinary focused tests、ordinary fast-lane suite、repository-wide ledger-aware full-regression verifier、lint、SpecDock validation、`git diff --check`の有効なcommand setが定義される。実行結果は実装reportまたはquality-gate evidenceで別途記録し、本要件書だけをpass evidenceにしない。

## 制約・前提・未確定事項

- verified commit 時点の journal wire field shapeは再利用できる。`fresh` intentと`ensure-directory`は既存field内のenum拡張で表現し、不要なschema migrationを行わない。wire field追加が必要になった場合は、protocol versionを上げ、既存recognized journal protocolのresumeを同時に維持しなければならない。
- schema-2 guardのfield shapeとschema version 2は再利用するが、wire literalはrecognized用`purpose="recognized-journal-forward-only"`とfresh用`purpose="fresh-journal-forward-only"`に分離する。Issue 368 parserはfresh purposeをsupported guard/legacy markerのどちらにも分類できず、extra binding fieldsを含むfixtureを`marker-invalid`としてmutation前に拒否する。このwire discriminatorをpackage-version比較だけへ置き換えてはならない。
- exact required-directory inventoryは `_install_spec_dock_bound()`、package asset parents、generated assets、current testsから導出する。pathnameを推測して新しいempty directoryを追加しない。
- fresh `update` successは現行動作に存在しないため、成功outputは既存`update` success formatを再利用するという本Issueの新規contractである。
- fresh `init --force` / `update` failure時のrequested-entrypoint retry mappingは、現行fresh `init` retry contractを壊さず追加する。legacy markerにはrequested entrypointが保存されていないためcanonical `init`へfallbackする。
- 本文は実装と検証の要求を定義するものであり、記載したtestsまたはcommandsの実行済みを意味しない。
