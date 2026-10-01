# 旧domain台帳・復旧契約の退役

## 対象

採用済み[旧source置換表](../design.md#d-11)に従う。読取基準は `08ff6af49775371d3dc0196c2ae7a53530014b59`。旧四source files、435行、14 top-level symbolsを全文確認した。registry/branch_bindingは相互の型importだけ、operationのcallerは旧operation_executorだけであり、候補外のsource/test importは絶対／相対／TYPE_CHECKING／from-import子moduleを含め0。文字列参照は既知旧path/hashと非load検査だけ。

local ID採番予約、高水位・tombstone・永久branch binding、UUID付き操作計画・revision/engine/epoch固定・intent再送・resumeの型とexecutorを削除する。互換aliasを残さない。既存metadataのID/selector codecは保持し、新規Scopeの番号はGitHubに従う。現在のoperation結果のeffects/partial/unknownと、legacy_readerのreadonly診断は別の現行契約である。

## 十四symbolsへの対応

| 旧module | symbols | 後継／退役理由 |
|---|---|---|
| domain/registry | LocalIdRegistry、reserve_local_id、include_observed_local_ids | 新規local採番・永続予約・Git履歴全走査を廃止。既存local綴りを含むID codecはdomain/idsとselectorsで保持 |
| domain/branch_binding | BranchBinding、bind_branch | Scopeとbranchの永久binding台帳を廃止。current branch操作はGit refs/HEADと明示branch名を都度検査し、既存branchをresetしない |
| domain/operation | OperationEffect、OperationRecord | UUID、writer epoch、engine digest、fixed effect plan、revision、retry_ofを持つ復旧用型とblocking/rollback allowlistを廃止。現行CLIは今回操作の効果とpartial/unknownを返す |
| application/operation_executor | _logical_id、prepare_operation、assert_resume_request、record_effect_intent、record_effect_result、record_effect_observation、can_send_effect | 過去操作のintent/結果/観測を続行し再送許可を出すexecutorを廃止。fresh processは現物の確認から新しい明示操作として開始する |

既存test関数の削除0。`domain/ids.py`、`selectors.py`、current branch/Scope writer、readonly legacy readerは変更しない。旧情報の保全・未確定remoteの調査を省略したことにはしない。

## 実測

通常wheelの旧四module収録禁止はRed 1 failed（0.73秒、exit1）。退役後の同testはGreen 1 passed（15.02秒、exit0）。通常wheel/sdist、外部非editable venv、実consoleまで完走した。

公開Scope create/import/lifecycle、branch、旧recovery argument拒否の五suiteは156 passed（47.47秒）、exit0。全source/tests Ruff check/formatは329 filesで成功。変更wheel test限定mypy `--follow-imports=silent` とdiff checkが成功。skip／収集除外を追加しない。

元logは既存Epic Workbenchの `iss-00413-implementation/pytest-domain-retirement-source-{red,green}.log` と `pytest-domain-retirement-related.log` に保持。

残る旧installation/その他のhelpers、通常full gates、native OS／別Python、fresh Strictと最終手動確認は未完了。実consumer、旧Git領域、他WT、live GitHubは変更していない。
