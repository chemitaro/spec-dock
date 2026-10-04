# Scope publicationの旧writer import分離

Issue #413 / P-12 / D-11。現行のpublic create/importが旧`create_node`と`create_github_scope`からhelpersをimportすることで、実行しない旧control・WriterLock・operation journalまで読み込んでいた。この結合を解消するため、必要な処理だけをapplication層の共有moduleへ移す。

## 保持する十一処理

| Helper | 現在のauthority（`src/spec_dock/runtime/application/`） | 保持する保証 |
| --- | --- | --- |
| `_scaffold_file_paths` | `scope_scaffold.py` | 既存templateの列挙・missing directory拒否。 |
| `_rules_source_paths` | `scope_scaffold.py` | 三階層に対応するshared rule source path。 |
| `_rules_scaffold_specs` | `scope_scaffold.py` | 各Scope内のrules link配置。 |
| `_open_relative_directory_at` | `scope_scaffold.py` | dirfdとno-followでlink親を開く。 |
| `_create_relative_symlink_at` | `scope_scaffold.py` | 観測したdirectory内のrelative link公開。 |
| `_validate_parent_dir_preflight` | `scope_scaffold.py` | 既存のredirected/non-directory親を拒否。 |
| `_validate_rules_symlink_preflight` | `scope_scaffold.py` | source/link destinationのpreflight。 |
| `_precheck_pre_github_create_rules_sources` | `scope_scaffold.py` | GH publication前に必須rulesを確認。 |
| `_replacements` | `scope_scaffold.py` | 既存template tokensの置換。GH番号・既存Scope IDを保持。 |
| `_parent_records` | `scope_ancestors.py` | initiative/epic/issueの必要親を検証。 |
| `_require_open_ancestors` | `scope_ancestors.py` | 既存local lifecycleまたはGH Issueのopen状態とrepositoryを検証。 |

旧helpersの定義は元moduleから削除し、現行`direct_scope_publish.py`と`github_scope_scaffold.py`が新moduleを直接importする。旧`create_node.py`/`create_github_scope.py`にもまだ実際のprivate callersがあるため、今回残したcodeは同じauthorityを使う。重複実装やfallbackは追加しない。旧writers自体の退役はtestの個別対応と参照監査を済ませてから行う。

`AncestorGateway`は既存のget境界だけを表すProtocolとし、新しいremote効果を作らない。親helperのgateway注釈以外は十一処理のAST本体が移動前と同一であることを検査した。旧moduleに残る64/5 definitionsと現行publisher四functions/scaffold builder一functionもASTが不変だった。

## 公開seamのRedとGreen

fresh Python processでpublic Scope create previewを実行し、v2/plannedの結果と入力保全を確認する。同processが七つの退役writer/control modulesを読み込まないことを検査する。先行したRedは実際に七moduleすべての読込を検出した（1 failed、0.44秒）。helpers分離後は同じtestがGreen（1 passed、0.32秒）。その後、既存GH Issue importのpreviewへ広げた二casesも成功した（0.92秒）。createはremote接触0、importは指定IssueのGET一回のみで、両方のlocal treeは不変。

current/old ScopeとArtifactの関連97 tests（23.72秒）、fresh通常wheel/sdist/isolated consoleの一test（15.66秒）、全Ruff、新authorityとpublisher/testの限定mypy五filesが成功した。通常make lintはRuff成功・mypy 443 errors/49 filesで未完了。限定成功や旧testの退役を全体型gateの合格に読み替えない。元ログと以後の退役作業はimplementation-reportを参照する。
