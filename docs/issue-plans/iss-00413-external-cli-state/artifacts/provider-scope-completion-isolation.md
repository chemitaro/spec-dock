# Scope完了判定の旧writerからの分離

D-11/D-09の現行Scope close/reopenは、scope_completion.pyから二つの純粋なplan関数を借りていた。同moduleには旧control/WriterLock/journalによるwriter/resumeも混在し、現行previewだけで旧六modulesがimportされていた。判定七symbolsのauthorityをapplication/scope_completion_plan.pyへ移し、direct_scope_lifecycle.pyは直接importする。旧private lifecycle callersは同じauthorityを使い、重複実装/新lock/復旧aliasを追加しない。

ScopeViewはapplicationの既存観測型なので、判定も同applicationの小moduleへ分離する。metadata codecや三階層を変えず、純粋な判定と効果実行を分ける。old writer sourceの退役そのものは、残るprivate testsの個別移行を伴う後続stepである。

| 移動symbol | 維持する責務 |
|---|---|
| `CompletionReason` | completed/not-plannedの既存値を維持。旧journalの操作reasonとは分離。 |
| `CompletionDecision` | 観測済みbefore/after/descendantsだけの不変な判定値を維持。operation ID/control/epochを含めない。 |
| `_state` | 未観測Scope状態のfail-closedを維持。 |
| `_ancestors` | 祖先の不存在/循環検証を維持。 |
| `_descendants` | 子孫の不存在/循環検証と列挙を維持。 |
| `plan_close` | completedなら全子孫completedを要求し、unknownとterminal reason競合を拒否。not-plannedは子孫をCloseしない。 |
| `plan_reopen` | 既にopenでも祖先全件openを要求し、unknownを拒否。 |

移動七nodesのAST本体は元HEADと完全同一。旧moduleに残る七nodes、direct_scope_lifecycleの四functionsもAST本体不変だった。変更はimport authorityと不要なMapping importの整理であり、GitHub/metadata/選択/checkoutの効果は追加しない。

## 公開境界のRed → Green

fresh Python processで公開Scope close @current --dry-run --jsonを実行した。旧scope_completion/operation_executor/cli.admission/control_store/operation_journal/writer_lockの読込を検出して1 failed（0.61秒）。分離後、同じtestは1 passed（0.58秒）。その後reopenを含む二casesへ広げて2 passed（0.94秒）。いずれもv2/planned、所定のGH GET一回だけ、効果planned、consumer全tree不変を確認した。

関連old lifecycle/current lifecycle/Finishの76 tests（22.00秒）と、通常wheel/sdist/isolated consoleの一test（13.60秒）も成功した。元ログは既存Epic Workbenchのiss-00413-implementation/pytest-completion-isolation-{red,green,related,wheel}.logへ保持する。Ruffの初回指摘は移動後の余分な空行二箇所で、formatterで正規化後に全check/format（396 files）が成功した。現行判定/adapter/test限定mypy --follow-imports=silentの三filesも成功。full type gate、旧writersの退役、native Windows/別Python、fresh Strictと最終手動確認は残る。実consumer/live GitHubは未変更。
