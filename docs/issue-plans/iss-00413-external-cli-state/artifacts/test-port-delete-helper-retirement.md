# 旧Delete use caseの退役と非canonical領域の保全

## 判断と読取範囲

RQ-413-02、D-03/D-11/D-12、C-05、P-12に従い、通常CLIが参照しない `application/delete_node.py` を退役する。全1437行・42 top-level symbolsと、旧resolver opacity testの全44行・一test関数を読み、ASTの絶対/相対/子module/TYPE_CHECKING/literal importと文字列検索で照合した。外部production参照は0、旧testからのimportだけが一件あった。退役後はsrc/testsのAST参照0。旧consumer静的inventoryのpath/hashは過去資産の識別用に保持する。

| 削除するsymbols | 判断・維持する境界 |
|---|---|
| `_CanonicalRemoteIssue`, `_to_spec_node_seed`, `_normalize_issue_number`, `_validate_node_metadata` | 旧metadata/remote型のcompositionを撤去。現行Scope linkage/ID/三階層の検査は維持 |
| `_resolve_specdock_dir`, `_iter_managed_nodes`, `_is_canonical_managed_node_dir`, `_node_kind_from_prefix`, `_matching_target_directories`, `_target_node_dir_from_error_message`, `_target_local_metadata_failure_result`, `_resolve_node_id_matches`, `_resolve_github_issue_matches`, `_resolve_target_id` | 旧Ports/fallback walkと例外文からのpath推定を撤去。現在treeからのexact selector、canonical container、guarded metadataへ統一 |
| `_empty_remote_close`, `_result`, `_metadata_failure_result`, `_dependency_topology_load_failure_result`, `_remote_close_failed_result`, `_local_delete_partial_failure_result`, `_build_partial_failure_recovery_guidance` | 旧private結果型/復旧案内を撤去。公開v2のdiagnostic、path別effects、exit6と実backupを維持 |
| `_subtree_ids`, `_subtree_issue_ids`, `_issue_ids_for_scope_node`, `_subtree_delete_order` | 旧graph orchestrationを撤去。現行の明示subtree/recursive判定と実体保全を維持 |
| `_collect_boundary_dependency_edges`, `_collect_surviving_raw_node_dependency_refs`, `_load_meta_payload`, `_write_meta_payload`, `_ref_matches_deleted_node`, `_build_deleted_ref_match_context`, `_build_survivor_ref_match_context`, `_scrub_surviving_dependency_refs` | 旧fallback metadata書込と別ID/ref形式のscrubを撤去。現行ID依存、明示detach、捕捉bytes再検査・実backupを維持 |
| `_active_ids`, `_drop_deleted_nodes_from_manifest`, `_manifest_has_entries`, `_repair_active_after_clear_failure` | 三段snapshot/親を残すrepair/restoreを撤去。現行captured tokenだけの明示clearと他WT記録保全を維持 |
| `_subtree_remote_close_targets`, `_close_remote_issues_barrier` | DeleteによるGitHub自動Closeを撤去。C-05に従いGitHub/branch不変。完了Closeは別Finish/lifecycle経路 |
| `_delete_local_node_directory`, `_delete_subtree_locally`, `delete_node` | 旧Ports/rmtree/自動post_syncを撤去。現行guarded削除・途中効果・backup保全、必要時readonly Syncを維持 |

現行 `direct_scope_delete.py`（459行）と `scope_tree.py`（128行）も全文確認した。DeleteでGitHubをCloseしないこと、branchを消さないことはC-05の決定である。旧三段Activeのrestore/repair、例外文からのtarget path推定、rmtree後の自動Syncを新しい保証として残さない。現行の明示backup、path別effects/partial、捕捉したdirect tokenだけのclear、依存detachと他WT不変の試験は保持する。このunitは現行productionの挙動を変更せず、旧42 symbolsを削除する。

## 旧testと後継の対応

`test_delete_fallback_scan_prunes_workbench_and_preserves_near_name` はprivateなos.walkの列挙順を検査していた。WorkbenchをScopeとして誤認しない境界を公開CLIの `test_scope_delete_ignores_private_and_noncanonical_containers_without_reading_them` へ移した。三階層のcontainer × .workbench/.workbench-copy × 現存/不存在targetの十二casesで、不正なprivate metadata・重複ID・ghost IDを置き、private directory列挙とmetadata inodeのopenを検出する。正常なScopeだけを削除・実backupし、ghost targetはSCOPE_NOT_FOUND/exit4・effects=[]で拒否する。両方でprivate bytes、親metadata、GitHub、Git control領域を保全する。

旧near-nameを一般walkで辿るという実装上の期待は廃止し、現在のcanonical containerだけの読取へ統一する。全private領域の保全を「旧一般walkと同じ動作」とは説明しない。他のtest削除、skip/型ignore/収集除外追加、既存assertionの緩和は0。

## 実測と残り

- source削除前の後継十二cases: **12 passed、37 deselected、2.22秒、exit0**。既存Greenのcharacterizationである。
- 通常wheelの旧module収録禁止: **Red 1 failed、0.77秒、exit1 → Green 1 passed、16.35秒、exit0**。
- 公開Delete、旧公開command契約、fs_repo opacityの三suite: **56 passed、9.56秒、exit0**。最初の実行は誤ったtest pathでexit4/no tests ranとなった。実在fileへ直して上の実測を得た。このharness errorを製品Redに数えない。
- 実Python 3.10.15のprefix/source importを照合した後継十二cases: **12 passed、37 deselected、1.91秒、exit0**。
- 全Ruff check/format（304 files）、MYPYPATH=srcの変更二test限定mypy、diff checkが成功。
- 通常make lint: **Ruff成功、mypy 30 errors/10旧files（223 source files）、make exit2**。限定成功をfull gate合格にしない。

元logsは既存Epic Workbenchの `iss-00413-implementation/pytest-delete-opacity-public.log`、`pytest-delete-helper-retirement-{red,green,related,related-2}.log`、`pytest-delete-helper-python310.log`、`lint-delete-helper-retirement.log` へ保持する。別候補c4c26bdbのLinux全件は一件失敗が残り、このunitを含まない。残る旧source、Windows native、通常full gates、fresh Strict、最終手動確認を続ける。実consumer/live GitHubは未変更。
