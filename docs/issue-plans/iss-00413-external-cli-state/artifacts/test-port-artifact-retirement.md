# 旧Artifact writer・試験の退役

## 根拠と対象

採用済み [D-11](../design.md#d-11) / [CLI契約](cli-contract.md) と、[第11回レビューの分析](code-review-p06-11-analysis.md) に従う。読取基準はローカル `82240b58019678c015b3ddf0ada5e44cdf8f6ff2`。旧 application/artifact_vnext.py（152行・六関数/classと一type alias）、test_artifact_vnext.py（111行・五test関数）を全文確認した。

既存資料のidentity・filename・bytes、六種類のtemplate、Scope/root ownership、読取privacy・重複slot拒否を維持する。共通WriterLock/control/epoch/三段旧activeに依存するadapterは退役する。既存local metadataの保全互換性を残し、製品の新規local Scope発行は追加しない。

候補外source/test AST importはTYPE_CHECKING/from-import子moduleを含め0。退役後の文字列参照は通常wheelの不在assertと、既知旧資産のpath/hashを保持するstatic-inventoryだけ。alias・fallback・build除外・pytest skip・収集除外は増やさない。

## 五つの旧試験への対応

公開seamは `spec_dock.cli.main`、一時native Git repository、実metadata/Artifact、OS file open境界、gh stubである。旧control付きlocal create fixtureは使わない。

| 旧test関数 | 維持／採用仕様による変更 | 後継test関数 |
|---|---|---|
| test_artifact_catalog_accepts_current_historical_unknown_and_generic_without_reading_body | 現在typed・旧連番・未知type・generic fileのidentity/typeを維持。本文を開かず、authorityを本文やfilenameから推測しない | test_scope_artifact_catalog_preserves_typed_historical_unknown_and_generic_evidence_without_opening_bodies、test_root_artifact_catalog_reads_only_identity_without_control_or_body |
| test_root_scope_can_list_generic_but_rejects_duplicate_slots | root generic一覧と同timestamp slot衝突拒否を維持し、Scope catalogにも同じ保全を検査 | test_root_artifact_catalog_reads_only_identity_without_control_or_body、test_duplicate_artifact_timestamp_slots_refuse_catalog_reads_without_changes |
| test_scope_artifact_creation_accepts_local_initiative_and_rejects_root | 真正の既存local Initiativeへの作成/show・元metadata/仕様保全を維持。root create拒否だけはC-05とr11の修正方針に従い撤去し、既存公開root createを維持 | test_existing_local_initiative_accepts_all_artifact_types_and_preserves_metadata_and_documents、test_root_create_supports_all_templates_and_preview_without_unrelated_scope_metadata |
| test_six_creation_types_remain_distinct_from_observed_authority | 六種類とblankのuntyped表示を維持。v2の四fieldはidentity/typeだけで、ADRの採択を認定しない。core catalogのunverifiedも保持 | test_existing_local_initiative_accepts_all_artifact_types_and_preserves_metadata_and_documents、test_all_creation_templates_and_owner_local_timestamp_slots_are_preserved |
| test_root_file_import_keeps_source_and_returns_private_catalog_entry | root importのbytes・basename・元source保全、本文/外部source pathの非開示を維持 | test_import_one_opaque_file_to_root_preserves_bytes_name_source_and_privacy、test_root_artifact_import_and_catalog_do_not_require_unrelated_scope_metadata |

root createは十二既存casesでapply/previewと六templateを検査する。旧拒否期待の削除を、新しい禁止や今回独自のscope拡張として説明しない。

## 七symbolsへの対応

| 旧symbol | 後継／退役理由 |
|---|---|
| ArtifactCreationType | CLIの六type whitelistと現行template/publicationを維持。旧moduleのtype aliasは残さない |
| ArtifactMutationPreview | v2 FamilyDataとplanned Effectに統合 |
| _selected_scope | direct_artifactとworktree_observationの捕捉直接record/動的selectorへ統合。旧selection storeを使わない |
| preview_scope_artifact | 現行artifact create --dry-run。rootも許可し、無関係なScopeを読まない |
| preview_import_scope_file | 現行artifact import file --dry-run。単一regular source、privacy、無書込を維持 |
| create_scope_artifact | direct_artifact.mutate_artifactと局所file_publicationに統合。共通WriterLock/control/epochを撤去 |
| import_scope_file | 同公開familyのopaque importと正確なpartial/effectsへ統合 |

`application/artifact_query.py` は現行list/showが使用し、本文非読取・slot検証・held descriptorを担うため削除しない。旧create_artifact_doc/import_file_artifact/ports等は他callerを個別に確認する別unitで扱う。

## 実測

- mixed catalogを本文open拒否のOS境界で照会：1 passed、0.23秒。
- root/Scopeの重複slotをlist/showで拒否し全tree保全：2 passed、0.37秒。
- 既存local Initiativeの六type create/show、metadata/仕様/mode/ref保全、GH request 0：6 passed、1.45秒。
- 最初のmixed catalog試験はCLI完了後の試験側tree_digestまでbody open拒否を延長し、1 failed（0.31秒）。障害注入をCLIのcontextへ限定して訂正した。製品Redではなく、失敗logも保持。
- 通常wheel収録禁止は旧writerの実収録で1 failed（0.77秒）。source/test退役後の同testは1 passed（14.08秒）。通常wheel/sdist、外部非editable venv、実consoleまで完走。
- Artifact公開CLI / Grill finalizer / filename domain / 配布templateの関連四suite：141 passed、8.89秒。
- 全source/tests Ruff check/format：353 filesで成功。
- 変更二test限定mypy `--follow-imports=silent` とdiff check：成功。

追加公開試験は既存Greenのcharacterizationである。元logは既存Epic Workbenchの `iss-00413-implementation/pytest-artifact-retirement-port.log`、`pytest-artifact-retirement-source-{red,green}.log`、`pytest-artifact-retirement-related.log` に保存した。

## 未完了

このunit前のclean 82240b58の通常make lintはRuff成功・mypy 95 errors/26 files（274 source files）、source 47/test 48 errors、make exit2で未合格。元logは `iss-00413-implementation/lint-p12-82240b58.log`。189 errorsは旧snapshotである。残る旧source/tests、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer・既存WT・旧Git領域・live GitHubは未変更。
