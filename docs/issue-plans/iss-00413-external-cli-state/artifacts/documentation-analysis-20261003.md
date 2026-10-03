# Issue 413 文書乖離分析

## 1. GitHub connector検証

### 検証済み事実

- repository: `chemitaro/spec-dock`
- target branch: `codex/iss-00413-external-cli-state`
- expected SHA: `8606e132327066d56567556e336e4bc1ae6a0b17`
- GitHub connectorのrepository取得は成功しました。
- branch検索でtarget branchをexactに取得しました。
- 同一target branchをbase/headにしたcommit比較で、base・head・merge-baseのfull SHAがすべて `8606e132327066d56567556e336e4bc1ae6a0b17` となり、expected SHAとbyte-for-byte一致しました。
- exact SHAをrefにしてroot `README.md`、`AGENTS.md`、CLI catalog、work-target store、Start lockを取得し、添付内の対応Git blobと照合しました。Issue 413のRequirement/Design/Plan/HTMLも添付内Git blob IDがexact SHAのtreeと一致しました。

### 実際に試みた操作と観測

1. repository metadata取得 — 成功。
2. branch API URLの直接fetch — connectorの許可URL形式に合わず拒否。repository/branch不存在や権限不足の証拠には使用していません。
3. connectorのbranch検索 — exact branchを取得。
4. connectorのcommit比較 — branch tipのfull SHAを取得し一致確認。
5. exact SHAのtree/file取得 — 正本文書と実装根拠を確認。

### 仮説・未確認

- branch API URLの拒否理由はconnectorのURL形式制約と推定します。branch検索とcommit比較で同じtarget refを直接確認できたため、repository/branch/SHA検証には影響しません。
- 添付ZIPは依頼文では142 selected filesとされていますが、安全展開後のregular file実数は147でした。path traversalとsymlinkはありませんでした。追加5件の由来はbundle生成側の選択内訳を持たないため原因未特定です。

## 2. 根拠の区分

### 製品実装・合意済み仕様の正本

GitHubで検証したexact SHA `8606e132327066d56567556e336e4bc1ae6a0b17` のsourceと正本文書だけを、現行実装契約の根拠にしました。主な根拠は次のとおりです。

- `src/spec_dock/runtime/cli/catalog.py`: 公開44 leaf。`workspace doctor`、`artifact import file`、`installation`を含むCurrent catalog。
- `src/spec_dock/runtime/cli/options.py`: `--backend local`を退役入力として拒否し、新規ScopeにGitHub-issued numberを要求。
- `src/spec_dock/runtime/application/direct_scope_publish.py`: GitHubが返したissue numberから`init-` / `epic-` / `iss-` IDを生成。
- `src/spec_dock/runtime/infra/work_target_store.py`: `spec-dock/.agent/work-target/target-<32hex>.json`、0/1件、opaque file token。
- `src/spec_dock/runtime/infra/start_lock.py`: 既存Git common directory descriptorへの`fcntl.flock`。custom lock fileを残さない。
- `src/spec_dock/runtime/commands/runtime_dispatch.py`: business commandはLinux/macOS以外で`UNSUPPORTED_PLATFORM`。
- `src/spec_dock/runtime/application/direct_artifact.py`: `artifact import file PATH --scope @root`を含むCurrent Artifact publicationとv2 result。
- `src/spec_dock/runtime/application/direct_installation.py`、`direct_static_update.py`、`direct_migration.py`、`infra/static_assets.py`: package runtimeとworktree単位static資産、workspace writer migrationの分離。
- `pyproject.toml`: external console entrypointとPython 3.10+。

### GitHub未収録の補助資料

`input-context.md`、`status-evidence.json`、原Gate JSONは、現在のrollout観測、利用者指示、既存証拠の所在を更新するために使用しました。これらをGitHub収録済みの実装sourceとは表現していません。

- 0805 worktreeのpackage/shim/writer/static適用、240 Scope validate、empty active、Sync exit 7。
- mainとほか3 linked worktreeの未移行、main dry-runの`LEGACY_IMPACT_UNVERIFIED`。
- #413/#356 open、#31 closed/completed、formal #413 Start未実施。
- PR/merge/package publication未実施。
- exact SHAの既存Final Quality Gate v2、OS別test件数、14-op manual flowの制限。

## 3. 確認範囲

全文を確認した正本範囲:

- root `README.md`、`AGENTS.md`
- `src/spec_dock/assets/spec_dock/docs/` のauthoring、rules、guide、migration、CLI/GitHub/naming/deps/sync/worktree reference、HTML guide
- `src/spec_dock/assets/spec_dock/system/` と`active-none/`
- `src/spec_dock/assets/spec_dock/templates/`
- provider側二つの`SKILL.md`
- `docs/issue-plans/iss-00413-external-cli-state/` のRequirement、Design、Plan、explanation HTML
- CLI catalog/help契約、Scope publish、Start/Finish/active/Sync、work-target store、Start lock、Artifact、installation/static update/migration、platform guard

consumer側 `spec-dock/` とroot `.agents/` は投影/現物観測の参照に留め、置換対象にしていません。

## 4. 主な乖離と修正

| 乖離 | 現行根拠 | 文書修正 |
|---|---|---|
| provider source、installed package、consumer static asset、ignored direct recordが混同される | package entrypoint、asset tree、installation/static update、work-target store | README、AGENTS、authoring overview、templates README、provider skill、Issue R/D/P/HTMLで四層と更新単位を明記 |
| `system/README.md` と`active-none`がlegacy `active/...` linkとbest-effort read-onlyをCurrent selectionとして説明 | Current writerは`.agent/work-target/target-<token>.json`、AGENTSもlegacy linkを非Currentと明記 | system/active-none全READMEをfallback説明へ更新。permission gateを作らず、取得を`work start`へ統一 |
| active-none leafが`active set`で新規取得する例 | `active set`は同一Current targetのunchangedだけ。空/別対象はStartへ | Initiative/Epic/Issueの例を`work start`へ変更 |
| `.runtime/README.md`が`create.lock`とrepository shared leaseを説明 | Startだけが既存common-dir descriptorへ`flock`し、custom lock fileを残さない | `.runtime/README.md`をStart-only exclusionへ差し替え |
| root Artifact rulesが退役文法`artifact import file --root --file`と旧publication fieldを説明 | catalog/reference/direct_artifactは`artifact import file PATH --scope @root`とv2 envelope/effects | root Artifact rulesをCurrent CLI・opaque evidence・authority flowへ差し替え |
| rulesが`main orchestrator single-writer authority`を現行概念のように説明 | Current productはcanonical docsとevidence adoptionを分離し、通常編集のpermission/orchestratorを追加しない | 6 rules fileをdurable canonical authorityと明示的adoptionの表現へ更新 |
| authoring overviewがconsumer `.agents`だけをrepo-local authorityのように説明 | provider authorityは`src/spec_dock/assets/install_root/.agents/skills/`、consumerはworktree projection | provider正本とconsumer投影を明記 |
| Issue R/D/P/HTMLがpre-Gate SHA、FQ pending、P-16未着手、実導入未実施を表示 | exact SHAの既存Gate証拠、0805限定適用、peer/Formal Start/merge/publication保留 | current aggregateを更新し、旧測定をraw historyとして保持 |
| explanation HTMLが旧`./spec`/candidate進捗、旧base branch/SHAを現在説明に使用 | external installed console、thin shim、exact target branch/SHA | standaloneな現在説明へ全面更新。四層、既存P2、rollout制限を追加 |

## 5. 現在の完了と保留

### 完了として保持するもの

- exact SHA `8606e132327066d56567556e336e4bc1ae6a0b17` の製品実装・合意済み仕様。
- 同SHAに結び付く既存Final Quality Gate v2証拠。coverage complete、13 perspective、P0/P1=0、P2=3。
- 既存OS/Python/console test証拠。実行者、環境、stub/live境界は分離。
- caller-provided観測として、0805 worktreeへの外部package、thin shim、writer declaration、static assetの限定適用。

### 完了扱いにしないもの

- mainとほか3 linked worktreeの移行。
- clone全体のcompleteなSync。
- formal Issue #413 import/Start。
- GitHub #31のreopen/付替え。
- PR、human merge、package publication。
- この文書差し替え候補に対する新しいreviewまたはFinal Quality Gate。

## 6. HTML契約の保持

置換後HTMLについて、元HTMLと次を機械比較しました。

- `data-plantuml-contract="2"` を保持。
- editable PlantUML source 4件をID・本文ともbyte一致で保持。
- `@plantuml/core@1.2026.6` の固定参照を保持。
- render/zoomの実行script本文をbyte一致で保持。
- style boilerplateをbyte一致で保持。
- PNG、pre-rendered SVG、remote renderer、新しい外部JS/dependencyを追加していません。

これは静的な文書契約確認であり、更新HTMLのbrowser実描画や新しい品質認定を主張しません。

## 7. 未確認事項

- 選択bundleだけではruntime packageの全moduleが揃わないため、添付sourceからCLIを直接起動してhelpを再生成していません。exact SHAのcatalog/options/sourceと既存観測を照合しました。
- live GitHub Closeは実行していません。14-op flowはstateful gh stubという既存証拠です。
- mainと3 peer worktreeのfilesystemを本作業から直接変更・再観測していません。直近状態はcaller-provided補助資料によります。
- 更新HTMLのbrowser描画、zoom、mobile表示は本ZIP生成では再実行していません。
- 文書差し替え後のrepository commit SHA、PR、merge、package publicationはまだ存在しません。

## 8. 差し替え後にCodexが行う派生資産処理

このZIPの全文置換fileを採用した後、現物hashを使って次を行ってください。本ZIPではinventoryを推測生成していません。

1. 配布`static-inventory.json`の対象entryを新しいsha256へ更新する。
2. 置換前sha256を各entryの`known_old_sha256`へ重複なく追記し、既知旧版からのguarded updateを可能にする。
3. candidate packageを更新した後、installed Current CLIで明示した現在consumer worktreeへstatic assetを反映する。consumer側fileを手編集で正本化しない。
4. pack manifestと配布ZIPを、新しいprovider fileとinventoryから再生成する。
5. package更新は利用者tool環境、static updateはworktree単位であることを検証し、ほかのreal worktreeを暗黙更新しない。

## 9. 変更境界

このZIPは文書全文だけを含みます。製品コード、公開command、runtime、test、CI、dependency、Git内部の独自管理領域、通常編集のpermission control、Scope metadata、direct record、Git/GitHub stateは追加・変更していません。ZIP内pathはrepository-relativeで、`..`、symlink、実行可能fileを含みません。
