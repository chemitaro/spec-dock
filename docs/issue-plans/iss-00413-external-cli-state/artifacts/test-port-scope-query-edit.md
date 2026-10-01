# Scope照会・タイトル編集試験の公開CLI移行

D-03/D-09/D-11に従い、既存metadataの読取・編集の保証を公開CLIへ移す。旧test_scope_query_vnext.pyの三test関数と、旧application/edit_scope.pyの全79行を確認した。新規local Scope作成、control/epoch/WriterLockをfixtureの必須条件として残さない。既存local metadataの互換読取・編集と新規作成禁止は別の契約である。

| 旧test関数 | 公開CLIで残す保証 |
|---|---|
| `test_scope_query_filters_local_and_cached_github_without_network_or_write` | `test_scope_query_filters_existing_local_data_without_network_or_write`へ置換。既存local metadataをfixtureとして用意し、kind/state filter、空Issue一覧、ID指定と直接recordによる@currentの同一対象、local authorityを検査する。native Git/public mainを使い、gh request 0、全tree bytes/mode不変、effects空、旧Git controlなしを確認。 |
| `test_scope_query_ignores_retired_github_status_cache` | 同名の公開testへ置換。GH紐付けの既存Scopeと旧cacheを用意し、showはunknown/source unknown/observed_at null、completed filterは空でunknown_filtered_count=1を返す。cacheを含むtree不変・gh request 0・effects空を確認。古いcacheのstateや時刻を現行観測として採用しない。 |
| `test_scope_title_edit_preserves_slug_backend_and_read_only_mode` | `test_scope_title_edit_preserves_existing_fields_documents_and_mode`へ置換。未知field/custom_note、ID/backend/parent/slug/lifecycle等はそのまま、title/revisionだけを変更し、三つの仕様Markdownと既存modeを保持する。同じtitleの再要求はunchanged/changed=false/effects空・metadata bytes/tree不変。gh request 0、旧Git controlなしを確認。 |

fixtureで既存metadataをmode 0444にしているのは既存の権限を保存する回帰検査である。製品が新たな編集権限制度や共通lockを導入するものではない。WorkTargetStore/project_contextは実態に合う一時fixtureを構築するだけに使い、製品挙動のassertionは公開mainの結果とfilesystem/gh境界へ置く。owned内部moduleをmockしない。新規local Scopeを発行せず、独自番号予約も行わない。

三件を一件ずつ実行し、それぞれ1 passed（0.34/0.24/0.34秒）だった。現行公開実装のcharacterizationであり、製品Redと呼ばない。

## 旧編集writerの退役

| 旧symbol | 判断・現行authority |
|---|---|
| `ScopeEditResult` | control付き旧title writerの内部返却型。公開v2 OperationResult/Scope payloadが現行authorityなので退役。 |
| `edit_scope_title` | 旧control/epoch/admission/WriterLockによる編集を退役。現在のdirect_scope_edit.edit_scopeがmetadata source capture/CAS・unknown field保存・局所staging・実mode保存・partial診断を提供する。 |

試験置換後、source/testsの全Python ASTでTYPE_CHECKINGとfrom-import子moduleを含め、このmoduleへのimport 0を確認した。source/tests/setup/pyproject/scripts/CIの名前・symbol参照も旧module本体だけである。metadataや仕様Markdownの生成物を削除する操作とは区別し、通常配布から旧Python一fileを除いた。旧asset inventoryのpath/digestはownership証拠として保持する。新alias/fallback/build除外を作らない。

通常wheelの明示収録禁止を先に追加し、正常buildしたartifactに旧edit_scope.pyがあるRed 1 failed（0.77秒）を確認した。source削除後の同testは1 passed（13.37秒）。fresh wheel/sdist inventory・外部非editable venv・実console・context不要utilities・局所static操作と入力保全を検査した。

関連Scope query/edit/create/契約の40 tests（6.23秒）、全source/tests Ruff check/format（373 files）、変更二test限定mypy --follow-imports=silent、diff checkも成功した。元logは既存Epic Workbenchのiss-00413-implementation/pytest-scope-query-port.log、pytest-scope-query-source-{red,green}.log、pytest-scope-query-port-related.logへ保持する。全体lintは直近407 errorsで未合格のままであり、この限定成功をfull gateに読み替えない。旧private writersの参照整理、full type/pytest、native Windows/別Python、fresh Strict、最終手動確認を継続する。実consumer・既存WT・旧Git領域・live GitHubは未変更。
