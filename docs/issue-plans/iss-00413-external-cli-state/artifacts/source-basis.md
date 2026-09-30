# 出典・基準・確認範囲

本書は「何を確認したか」と「今回の設計判断」を分けます。基準実装が旧要求を実装していることは、新しい利用者回答を取り消す理由にはなりません。個人や過去agentの意図、control欠落の直接原因を推測して断定しません。

<a id="strict"></a>
## Strict GitHub connector検証

| 項目 | 今回の確認事実 |
|---|---|
| repository | `chemitaro/spec-dock` |
| 指定branch | `main` |
| expected_sha | `6fec3099d8759b4e5b3b393b2987534b46dfa383` |
| 直接操作 | 接続GitHubの `fetch` で `/repos/chemitaro/spec-dock/git/ref/heads/main` をGET |
| 返却ref / type | `refs/heads/main` / `commit` |
| 取得full tip | `6fec3099d8759b4e5b3b393b2987534b46dfa383` |
| 比較 | full 40桁のASCII bytesが完全一致。検証成功 |
| 他branch/default branch | 解決・fallbackなし |

最初にGitHub connectorの利用可能操作を確認し、添付を実装の代用にする前に指定refを直接取得しました。検証日は2026-09-30（日本時間）。上記はその照会時点の先端であり、以後もbranchが動かない保証ではありません。以後のコード/設計fileは全てこのfull SHAに固定した `fetch_file`、およびこのtreeから得たobjectを使いました。live Issue本文と歴史上の明示commitは別の情報として下で扱います。

[指定refの照会先](https://api.github.com/repos/chemitaro/spec-dock/git/ref/heads/main) は可変refの来歴を示すリンクです。コード引用は可変refではなく以下のcommit固定リンクを使います。GitHub responseのobject SHAと文書payloadのSHA-256は用途が異なります。本作業でsourceの署名認証や再ビルド認証を実施したとは記録しません。

実行した操作はGETによるref/tree/contents/file/Issue/git-commitの読取だけです。GitHub write、commit/push、branch作成、Issue作成/Close、認証設定変更はしていません。任意の補助archive取得をcontainerで一度試みましたがDNS解決に失敗し、archiveは取得せず根拠にも使用しませんでした。これはconnectorのアクセス拒否ではなく、Strict検証失敗でもありません。製品をこの環境にclone・install・実行していません。

<a id="authority"></a>
## Authorityの適用順と資料の役割

| 資料 | 正とする範囲 | 正としない範囲 |
|---|---|---|
| [確定回答](user-decisions.md)と今回の利用者指示 | 新しい要求。Q1〜Q8と合意事項、文書納品/表示契約 | 技術的な細部を利用者が承認したという未記録の主張 |
| 検証済みSHAのprovider source・tests・#409設計 | 現在の実装/既存契約と変更前の挙動 | 今回の新要求を逆転する根拠 |
| 添付current-pack-context.md | 差替え対象、以前の論点、Codexの既存観測の記録 | 旧stateless全面廃止、全writer lock等の再採用 |
| 添付explanatory-document.htmlと二つのガイド | JavaScript/modal、PlantUML、平易な日本語の表示要件 | 製品挙動の実装根拠 |
| 本packの設計 | 要求を満たす最小のmodule/API/schema/操作順の確定案 | 実装・製品試験・実環境への適用実績 |

保存先/token、active setの取得制限、親の自動昇格撤回、Syncの非永続出力、Start mutexのOS具体化、workspace宣言の値は、本版の設計判断です。Q&Aへ利用者の回答として追記しません。旧reportとローカルinterviewは採用先の [report.md](../report.md) / [interview-worktree-start.md](interview-worktree-start.md) に原文を残す前提です。本packはこの二つを生成/上書きしません。

<a id="implementation"></a>
## 基準実装として読んだsource

RTは `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` です。`src/spec_dock/` がprovider、`spec-dock/` がdogfoodingデータ/配布投影です。実際のsrc treeを照会し、work/active/syncやcontextの実pathを確認しました。以下はGitHubが返した本文の読取範囲です。「一部読取」を全repo監査や全文確認に拡張しません。

| 根拠 | commit固定path | 読取範囲 | 設計に使った事実 |
|---|---|---|---|
| <a id="s-01"></a>S-01 | [src/spec_dock/cli.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/cli.py) | 全文 | console entrypointはexternal_cliへ委譲する。通常wheel化でこの公開名を維持する。 |
| <a id="s-02"></a>S-02 | [src/spec_dock/external_cli.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/external_cli.py) | 全文 | utilityの先行解析、asset runtimeのimport、業務のfixed bin/lib配置検査。外部helpとshimのhelpを区別。 |
| <a id="s-03"></a>S-03 | [src/spec_dock/shim_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/shim_vnext.py) | 全文 | helpの委譲前にengine/controlを検証し、不備でexit3になる経路。 |
| <a id="s-04"></a>S-04 | [src/spec_dock/runtime_loader.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/runtime_loader.py) | 全文 | engineの実体はcheckout外。engine.jsonは絶対path/digestのlocator、control.jsonと照合する。 |
| <a id="s-05"></a>S-05 | [src/spec_dock/fixed_bundle.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/fixed_bundle.py) | 全文 | installed packageから別の固定bin/lib配布物を作る。単なる通常console installとは異なる。 |
| <a id="s-06"></a>S-06 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/catalog.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/catalog.py) | LEAF_PATHS、LEAF_ARGUMENTSを含む表示範囲。応答の後半に省略あり | 44 leaf、旧各入力、recovery対象。全help文章の逐語照合とはしない。 |
| <a id="s-07"></a>S-07 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/options.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/options.py) | 1–205 | 共通option、strict parser、static help/completion、旧recovery案内。 |
| <a id="s-08"></a>S-08 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/vnext_runtime.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/vnext_runtime.py) | 1–215 | 実際の_contextがcontrol/登録worktree/digestを要求。仮のcli/context.pyを根拠にしない。 |
| <a id="s-09"></a>S-09 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/admission.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/admission.py) | 全文 | epoch/protocol/schema/digest、全登録worktree、pending journalによるwriter admission。 |
| <a id="s-10"></a>S-10 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/work_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/work_vnext.py) | 全文 | Start/Finishのadapter、dry-run、effects、Finishの--yes、旧operation_id。 |
| <a id="s-11"></a>S-11 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active_vnext.py) | 全文 | show空選択成功、set/from-branch、clearの既存公開入口。 |
| <a id="s-12"></a>S-12 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workspace_sync_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workspace_sync_vnext.py) | 全文 | generation公開・不完全結果・invalidの旧出力。 |
| <a id="s-13"></a>S-13 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/work_lifecycle.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/work_lifecycle.py) | 1–550、780–1110 | 開始のbranch→binding→checkout→selection、journal、Git失敗の汎用化、Finishのlive完了と解除。未読区間を全文確認とはしない。 |
| <a id="s-14"></a>S-14 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/active_selection.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/active_selection.py) | 全文 | 任意対象の選択、chain、部分clear後の親focus、WriterLock/registry依存。 |
| <a id="s-15"></a>S-15 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workspace_sync_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workspace_sync_vnext.py) | 全文 | 自WTの選択を含むgeneration、GitHub cache、共通lock、partial観測。 |
| <a id="s-16"></a>S-16 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/branch_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/branch_vnext.py) | 1–220 | 完全なregistry bindingを読む。既定ID-slug、base、clean/他WT使用/切替先祖先検査。 |
| <a id="s-17"></a>S-17 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/installation_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/installation_vnext.py) | 1–185（表示された本文） | controlと登録worktree群を単位にしたinstallation観測。新しい単一WT static仕様は変更対象。 |
| <a id="s-18"></a>S-18 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py) | 1–160 | numeric/旧local綴り、最小桁数、create/importのASCII titleとkebab slug。 |
| <a id="s-19"></a>S-19 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/selectors.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/selectors.py) | 1–170（本文全体を含む） | 完全ID/GH ref/active roles、importの裸番号+repo、Artifact @root、旧WT ID/alias。 |
| <a id="s-20"></a>S-20 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/lifecycle.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/lifecycle.py) | 全文 | schema3、IDとbackendの独立検査、unknown field保持、GH state_reason、SelectionState chain。 |
| <a id="s-21"></a>S-21 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py) | 1–225、570–800 | 旧.agent/active.jsonとschema3選択、revision/identityによる保存。 |
| <a id="s-22"></a>S-22 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/control_store.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/control_store.py) | 1–180 | common-dir/spec-dock/control、control mode/epoch、worktree registration。 |
| <a id="s-23"></a>S-23 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/registry_store.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/registry_store.py) | 1–220 | local高水位/予約、deleted IDs、任意branch binding、全登録WT/履歴走査。 |
| <a id="s-24"></a>S-24 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/writer_lock.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/writer_lock.py) | 全文 | common-dirのlock fileとworktree lease。Unix flock/Windows locking分岐。新方式の実試験証拠ではない。 |
| <a id="s-25"></a>S-25 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/operation_journal.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/operation_journal.py) | 1–165 | 固定対象・phase・intent/effects・前像参照の永続journal。業務cacheではない。 |
| <a id="s-26"></a>S-26 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py) | 1–230、255–420 | Git環境隔離、origin照合、旧行単位worktree parser、helperのasset/PYTHONPATH依存。 |
| <a id="s-27"></a>S-27 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py) | 1–180 | 旧raw helperのGH入出力。これだけを現在typed lifecycleのdispatch根拠にはしない。 |
| <a id="s-28"></a>S-28 | [src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_lifecycle.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_lifecycle.py) | 1–240 | repository-bound REST、PR拒否、state reason、timeout unknown、単発変更+確認GET、旧marker探索。 |
| <a id="s-29"></a>S-29 | [src/spec_dock/assets/spec_dock/.gitignore](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/spec_dock/.gitignore) | 全文 | .agent/等がignore対象。全実checkoutのignoreを保証したものではない。 |
| <a id="s-30"></a>S-30 | [pyproject.toml](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/pyproject.toml) | 全文 | Python>=3.10、spec_dock.cli:main、package/asset収録、dev依存。 |
| <a id="s-31"></a>S-31 | [setup.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/setup.py) | 全文 | build先の清掃とsdistのbytecode除外。 |
| <a id="s-32"></a>S-32 | [.github/workflows/provider-ci.yml](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/.github/workflows/provider-ci.yml) | 全文 | Ubuntu/Python3.11のmake lint・uv run pytest、Ubuntu/macOS配布parity。Windows laneはこのfileでは未定義。 |
| <a id="s-33"></a>S-33 | [src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md) | 全文 | 旧入口/固定engine、active/workの説明、破壊的境界、実行証拠とhuman mergeの区別。 |
| <a id="s-34"></a>S-34 | [src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md) | 1–130 | 明示起動、限定source、active fallback禁止、read-only外部能力、one-Artifactと既存finalize手順。 |
| <a id="s-35"></a>S-35 | [tests/cli_runtime/test_active_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/cli_runtime/test_active_vnext.py) | 全文 | 各階層chain、同じ対象no-op、部分解除の親昇格、metadata不変、旧CAS。 |
| <a id="s-36"></a>S-36 | [tests/cli_runtime/test_work_start_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/cli_runtime/test_work_start_vnext.py) | 1–255 | 兄弟切替flag、祖先移動、branch create/checkout、旧journal resume、3kind。 |
| <a id="s-37"></a>S-37 | [tests/cli_runtime/test_work_finish_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/cli_runtime/test_work_finish_vnext.py) | 1–260 | 親昇格、子孫completed guard、chain外対象、既完了、lifecycle後のresume。 |
| <a id="s-38"></a>S-38 | [tests/cli_runtime/test_workspace_sync_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/cli_runtime/test_workspace_sync_vnext.py) | 全文 | selection不変、generation/cache、GH unknown、invalid parent、projection failure。 |
| <a id="s-39"></a>S-39 | [tests/cli_runtime/test_scope_local_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/cli_runtime/test_scope_local_vnext.py) | 1–150 | 旧local採番/gap/親kind/祖先/stale cache。採番保証を新要件にはしない。 |
| <a id="s-40"></a>S-40 | [tests/integration/test_cli_entrypoint_vnext.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/integration/test_cli_entrypoint_vnext.py) | 1–200 | fixed bundle、controlなしCI validate、通常wheel業務拒否、console help、固定pin。 |
| <a id="s-41"></a>S-41 | [tests/unit/infra/test_provider_distribution.py](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/tests/unit/infra/test_provider_distribution.py) | 全文 | provider/dogfood scripts/docs/skills byte parityとfixed shim一致。 |
| <a id="s-42"></a>S-42 | [spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00409-scope-active-work-cli-redesign/design.md](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00409-scope-active-work-cli-redesign/design.md) | 1–280、240–280、280–520、358–389、390–470。大きい応答の省略を短い範囲で補足 | D-02/D-08/D-09/D-13/D-16と公開CLI/三階層/依存/Finishの設計背景。全文逐語確認ではない。 |
| <a id="s-43"></a>S-43 | [spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00409-scope-active-work-cli-redesign/report.md](https://github.com/chemitaro/spec-dock/blob/6fec3099d8759b4e5b3b393b2987534b46dfa383/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00409-scope-active-work-cli-redesign/report.md) | 1–145を要求、表示された冒頭Outcome/Verification。応答途中省略あり | provider実装、検証候補、独立clone適用と他consumer未展開の区別。全報告/実測logの再検証はしていない。 |

<a id="tests"></a>
### treeで存在を確認したが本文を全ては読んでいない関連領域

基準root tree、src再帰tree、tests/cli_runtimeのtreeを読取りました。application/infra/commandsのScope create/import/completion/delete、依存・Artifact・Workbench、worktree、installation/migrationの関連moduleと対応test名はここから実pathを確認しています。一方、これら全ての関数・test bodyをこの生成中に通読したわけではありません。catalogの公開syntax、上の主要実装、#409の既存契約から必要変更を定義し、[Plan](../plan.md#regression) で変更前の全文確認と回帰を要求します。

特に新設する `src/spec_dock/runtime/`、work_target、StartLock、legacy_reader、issue413用testは**予定path**です。現在sourceに存在するものと記載しません。`cli/context.py` ではなく実在の `cli/vnext_runtime.py::_context` を改修します。root treeにMANIFEST.inはなく、今回の収録変更はpyproject/setupを対象にします。存在確認を製品テストの成功へ読み替えません。

<a id="history"></a>
## engine/controlを追加した背景

基準SHAの#409設計D-02は、checkout/self-updateの途中で後続importが別版になり得ることを防ぐため、checkout外の固定engineを選んでいます。実体は処理をするPython配布物です。engine.jsonはその場所とdigestを記録するlocator、control.jsonはmode/epoch/互換性/worktree群を記録する別の状態です。

D-08は任意branch対応をtracked metadataへ書くとdirtyになりcheckoutを妨げるため、共通registryに保存する理由を説明しています。D-09は共通controlと各worktreeのactiveを分け、D-13は互換性と共通writer lockを定めています。D-16のjournalはcacheではなく、限定された複数段階操作の中断復旧用です。これらの役割はS-13、S-21〜S-25の現実装でも確認できます。

一方、基準shimではutility委譲より先にengine/controlを読みます。通常consoleのhelpが先行解析できることと、`./spec -h` がその経路まで到達することは同じではありません。本件は外部にコードを置く理由まで否定せず、通常package installでコード混在を避け、独自pin/control/運用台帳の起動依存をなくします。

#409 reportの表示範囲では、製品source・fixtureの検証と独立cloneへの実導入、他の稼働consumerの未更新が区別されています。その報告から全consumerの展開完了や、今回の障害原因を断定しません。今回の製品実装/導入は全て未着手です。

### 指定された6 commitの追加確認

添付source-basisの履歴を起点に、接続GitHubで明示したfull commit objectをGETし、SHA、日時、messageを確認しました。次表は**commit metadataで裏付けた経緯**であり、各commitの全diffや基準tipへの祖先到達性を今回再検査したという意味ではありません。過去branchは解決していません。

| full commit | 日時（JST） | 確認できたmessageの要旨 |
|---|---|---|
| [7a10e783ecdbb52d3247efc946b69c20e52ba019](https://github.com/chemitaro/spec-dock/commit/7a10e783ecdbb52d3247efc946b69c20e52ba019) | 2026-09-24 19:03:03 | 要件・設計・計画、44 leaf、状態分離/復旧/移行を拡充 |
| [f44cc4f8f059a3355cfd4155c3bf64b2ba9f5f6f](https://github.com/chemitaro/spec-dock/commit/f44cc4f8f059a3355cfd4155c3bf64b2ba9f5f6f) | 2026-09-24 21:35:46 | Git共通directoryのwriter制御、worktree lease、互換性検証 |
| [d96065a2270d1b05b760cee47818a104c4797f4d](https://github.com/chemitaro/spec-dock/commit/d96065a2270d1b05b760cee47818a104c4797f4d) | 2026-09-24 22:00:24 | 外部fixed distributionのpath/実行可能性/digest検証 |
| [1226d700fd8cad8f92bbecb320cc5f463ad9a0aa](https://github.com/chemitaro/spec-dock/commit/1226d700fd8cad8f92bbecb320cc5f463ad9a0aa) | 2026-09-25 08:40:47 | 外部CLIとrepository shim、安全な委譲 |
| [9c879c8ac942249d3a3e6415e510b544211e129a](https://github.com/chemitaro/spec-dock/commit/9c879c8ac942249d3a3e6415e510b544211e129a) | 2026-09-25 09:46:07 | installed packageからの固定engine構築、公開入口/更新整合性 |
| [7964b6c133803a17dec6c848ed8a9612dcb3f28c](https://github.com/chemitaro/spec-dock/commit/7964b6c133803a17dec6c848ed8a9612dcb3f28c) | 2026-09-25 14:20:10 | 固定engine世代のactivate/resume/rollback、locator/control/worktree整合 |

「7a10e783時点のD-02に理由が既にある」という細かな過去file照合は添付のCodex履歴調査の報告です。本生成ではその古いfile本文までは取得していません。基準SHAのD-02と、7a10e783のdocs拡充messageを直接確認した範囲に限定します。

<a id="observations"></a>
## Issue・利用者端末の観測・未確認を分ける

接続GitHubで [Issue #413](https://github.com/chemitaro/spec-dock/issues/413) と [#409](https://github.com/chemitaro/spec-dock/issues/409) を読み、存在を確認しました。本文はliveな運用資料で、実装SHAの一部ではありません。#413本文に残る旧案・未完了項目は、確定回答を優先して差替える対象です。本作業で本文更新、formal scope import、work startを実行していません。

control不在と `./spec -h` の失敗、240 Scope/schema3/github、local綴り2件と#39/#31、例外配置の許可、正式登録とwork start未成功は、利用者指示/添付Codex証拠に基づきます。現在のlifecycle codecがlocal綴りとgithub backendの組合せを受理することはS-20から確認しましたが、全240metadataのbytesを取得して独立検査していません。後続の全件照合条件はAC-413-28、AC-413-35〜37とPlanの対応を参照してください。対象数を資料に合わせて書き換える手順ではありません。

この環境は利用者端末へ接続していません。古いreport中のテスト数・HTML描画合格・配信成功は前の版の実績です。今回の文書に引き継いで合格を捏造しません。新しいartifact自己点検は [self-check.md](self-check.md) に別記します。

<a id="external"></a>
## 外部の一次資料（検証後に参照）

次の資料はOS/Git/packageの公開契約を確認する補助根拠です。repo固有の実装の代替ではありません。APIの存在や文章上の仕様だけで実OS/FS試験に合格したとはしません。参照日は2026-09-30。

| 一次資料 | 使う範囲・限界 |
|---|---|
| [Git worktree](https://git-scm.com/docs/git-worktree) | main/linked一覧、porcelain -z、locked/prunable、通常repair/prune。独自名簿を必要としない観測の根拠 |
| [Python 3.10 fcntl](https://docs.python.org/3.10/library/fcntl.html) | Unixのdescriptorに対するflockと非blocking要求。APFS等の実動作・directoryの利用可否は別process試験が必要 |
| [CreateMutexW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw) | named mutex、Global/Local名前空間、既存objectの権限。ACL自動変更や万能なsecurity保証は採用しない |
| [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject) | timeout、WAIT_ABANDONED。所有取得と保存データの妥当性を分ける |
| [FILE_ID_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info) | VolumeSerialNumberとFileId128。世界的に永続一意なScope IDではない |
| [PyPA entry points](https://packaging.python.org/en/latest/specifications/entry-points/) | console scriptを通常install環境が生成する契約。独自fixed bundleが必要という意味ではない |

Windowsの動作保証、network FSの排他、異なるOSユーザー間の共有運用を勝手に拡張しません。実装者はD-05とP-13で、対象環境に必要な試験と未実施を明示します。最新版ライブラリや指定実装モデルの公開能力を評価・推測する依頼には拡大していません。

<a id="attachments"></a>
## 添付の抽出と表示契約

添付bundleは行番号付きテキストです。行番号の連続性を確認して、内容をUTF-8/LFへ復元しました。下表のhashは**復元した内容**のSHA-256です。利用者端末にある元fileの改行/末尾LFまで同一という証明ではありません。

| 添付内容 | 復元bytes | SHA-256 |
|---|---:|---|
| user-decisions.md | 5646 | `32fc35c2116d3d6f4a2e4e99f8ecf7e2a8761217e63f8858510790d782202e12` |
| current-pack-context.md | 183385 | `d310a43f8ea42d863eca42d1790edf8e27cf43f393374b2696dbe86270475fc2` |
| explanatory-document.html | 20671 | `10a8ab06f250c45f9ecad014e98f65245514d4aad2e949000be7dfafaa5ae104` |
| japanese-writing-guidelines.md | 3312 | `f3ee1debbb24c3fd43c657341c054e3899c22c17f04463c58483fa546c54ca12` |
| plantuml-browser-rendering.md | 7242 | `a9c7d35f69a9984f20e280e0a9f2bade5bd31373824c6c734bccc5215dfedf4c` |

HTMLは本文・補助CSS・text/plain図だけを変更し、実行scriptと共有modalは復元templateから保持します。図ソースを外部rendererに送らず、固定CDN libraryをブラウザ内で使います。実行JSのbyte一致、DOM構造の静的確認、実際のSVG/modal操作検証は別の検査です。実施範囲はself-checkに示します。
