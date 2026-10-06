---
種別: 実装計画書（Issue）
ID: "iss-00415"
タイトル: "共通CLI刷新後の操作案内・補完契約の整合"
関連GitHub: ["#415"]
状態: "実装承認済み"
最終更新: "2026-10-06"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00415 共通CLI刷新後の操作案内・補完契約の整合 — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)。WHAT／WHYとACは[Requirement](requirement.md)、構造・Interface・失敗時の設計判断は[Design](design.md)を正本にします。

> 2026-10-06、ユーザーが本計画に沿った実装・完了とGPT 5.6 ProによるStrict Final Quality Gateを依頼しました。下表を実施状態として更新し、実結果はreport.mdへ記録します。記載するコマンド・期待値そのものは実行証拠ではありません。ZIP採用、source commit、candidate install、利用者環境の更新、About更新、human mergeは相互に代替する完了証拠ではありません。

## Planning Level

**選択: strict。** [strict Completion Guide](../../../../../../docs/authoring/issue-plan-levels/strict.md)を適用します。

理由は、現在の公開診断と三shellの補完という利用者向け契約、既存consumerのhash識別・backupを伴う配布資産更新、Gitとは独立したAboutの適用・回復を一つの成果として確認する必要があるためです。危険な手作業への誘導、複数更新面の取り違え、部分更新の復旧を扱います。P2というラベル、件数、文書量、作業時間だけで選んだlevelではありません。

risk factorは、legacy同居時の誤った復旧、候補生成とparserの乖離、unknown資産の誤採用、source試験とinstalled packageの取り違え、Aboutの同時変更と未確認の成功表示です。不可逆なデータ変更、秘密漏洩、広いblast radius、incident recoveryが必要な事象が新たに判明した場合は、該当stepを停止し同じplan本文でcriticalへの再評価を行います。今回の範囲を自動拡張しません。

Planning Levelを`.meta.json`、`.assurance.json`、active、runtimeの実行可否へ複製しません。level別plan、regression ledger、policy skip制度は作りません。

## 目標

SD-OPS-001〜007を現行受付契約に合わせ、利用者が診断・例・参照・補完・公開紹介から矛盾した操作へ誘導されない状態を確認します。配布文書のprovider／wheel／installed resource／fresh consumerの一致と、認可された実環境の適用・About read-backまでを別の証拠で扱います。

本計画の基準は`chemitaro/spec-dock`／`codex/iss-00415-cli-refresh-specs`／`95ec39b751054bf48098215fc077fe7b8f533f62`です。基準SHAは本依頼で新しくGitHub connector照会して一致確認したものです。以後の実装でSHAが進んだ場合は、実施候補を改めて識別し、基準との差分を確認します。古い期待SHAを現在tipであると偽らず、他branchへfallbackしません。

### 読む入力と継承境界

最初に[ローカル照合結果](artifacts/20261006t035502z--verified-report.md)、[外部分析原文](artifacts/20261006t035503z--chatgpt-report.md)、本IssueのR/D/P、親Initiativeの[R](../../../../requirement.md)・[D](../../../../design.md)・[P](../../../../plan.md)、親Epicの[R](../../requirement.md)・[D](../../design.md)・[P](../../plan.md)を確認します。

作成規約は`repo-root: spec-dock/templates/issue/{requirement,design,plan}.md`と[Authoring概要](../../../../../../docs/authoring/overview.md)・[Scope layering](../../../../../../docs/authoring/scope-layering.md)を使います。[Issue413 pack](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/README.md)と[R](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/requirement.md)・[D](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/design.md)・[P](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/plan.md)・[実装記録](../../../../../../../docs/issue-plans/iss-00413-external-cli-state/implementation-report.md)は当時の契約・実施記録として参照します。

親の旧active set取得・index projectionを現在の操作へ戻しません。Issue413の歴史的試験数、モデル指定、rollout状態、レビュー工程を、現在の製品合格や本Issue独自の新制度へ転用しません。調査Artifactの「3 passed in 2.71s」も過去の限定結果です。

<a id="traceability"></a>
### RQ／AC・設計・step・検証の対応

| 指摘／横断要求 | RQ | AC | 設計 | 実装step | 検証IDと主な既存再利用先 |
|---|---|---|---|---|---|
| SD-OPS-001 | RQ-415-001 | AC-415-001 | [D-415-001](design.md#d-415-001) | S-01、S-02、S-05、S-06 | V-001：`tests/cli_runtime/test_issue413_scope_publish.py`、`tests/cli_runtime/test_issue413_scope_import.py` |
| SD-OPS-002 | RQ-415-002 | AC-415-002 | [D-415-002](design.md#d-415-002) | S-01、S-03、S-06 | V-002：`tests/integration/test_cli_docs_vnext.py`と公開Scope fixture |
| SD-OPS-003 | RQ-415-003 | AC-415-003 | [D-415-003](design.md#d-415-003) | S-03、S-05、S-07 | V-003：`tests/cli_runtime/test_issue413_scope_import.py`、`tests/integration/test_cli_docs_vnext.py` |
| SD-OPS-004 | RQ-415-004 | AC-415-004 | [D-415-004](design.md#d-415-004) | S-03、S-06 | V-004：`tests/cli_runtime/test_workspace_sync_vnext.py`、root文書検査 |
| SD-OPS-005 | RQ-415-005 | AC-415-005 | [D-415-005](design.md#d-415-005) | S-01、S-03、S-09 | V-005：AGENTSの現行段落と履歴原本の不変確認 |
| SD-OPS-006 | RQ-415-006 | AC-415-006 | [D-415-006](design.md#d-415-006) | S-01、S-04、S-05、S-06 | V-006：`tests/cli_runtime/test_help_completion_vnext.py`、`tests/cli_runtime/test_cli_vnext_contract.py`、`tests/cli_runtime/test_issue413_lock_options.py` |
| SD-OPS-007 | RQ-415-007 | AC-415-007 | [D-415-007](design.md#d-415-007) | S-08、S-09 | V-007：live GET／descriptionだけの許可済み変更／独立read-back |
| 配布・局所適用 | RQ-415-008 | AC-415-008 | [D-415-008](design.md#d-415-008) | S-05、S-06、S-07 | V-008：`tests/integration/test_issue413_assets.py`、`tests/integration/test_issue413_wheel.py`、`tests/unit/infra/test_provider_distribution.py` |
| 品質・履歴・状態 | RQ-415-009 | AC-415-009 | [D-415-009](design.md#d-415-009) | S-01、S-06、S-09 | V-009：通常lint／全pytest／差分、全V証拠の現在候補への対応 |

表のtest pathはすべてrepository rootからのpathです。以下の実行コマンドにも省略しないpathを記載します。追加するtest functionは計画上の新規検査であり、既存node IDとして実行済みとは扱いません。

## 順序・依存

主経路はS-01 → S-02／S-03／S-04 → S-05 → S-06 → S-07 → S-09です。S-08は採用description・実施許可と前提が揃えばS-06以後に独立して実行できます。S-09はS-07とS-08の両方の状態を集約します。

S-02の診断、S-03の文書、S-04の補完は責務上分離できます。ただし、共有する文書テスト・fixtureへの変更は一人の統合担当が調整し、同じtestを互いに上書きしません。配布hashは文書bytes確定後に更新します。実環境適用はcandidateの合格後です。

### 実施状態

| step | 成果 | 現在 |
|---|---|---|
| S-01 | 基準・許可範囲・新しいbaselineの取得 | 完了 |
| S-02 | legacy診断と公開negative test | 完了 |
| S-03 | README／TARGET／Sync／AGENTS整合 | 完了 |
| S-04 | 三shellの候補整合とnative検査 | 完了 |
| S-05 | inventory／fresh wheel／fresh consumer | 完了 |
| S-06 | 現在候補の通常全体検証と配布確認 | 完了（環境差はReport参照） |
| S-07 | 外部packageと明示consumerの別々の適用 | 完了 |
| S-08 | GitHub About descriptionの独立適用・確認 | 完了（副次変更の復元確認済み） |
| S-09 | 全ACの照合とhandoff | Strict Final Quality Gate待ち |

仕様作成時に行った資料読取り・ZIP自己点検は、この表の製品実装stepの完了に数えません。実測は後続で[report.md](report.md)へ記録し、本計画を日誌化しません。

## 実装step

<a id="s-01"></a>
### S-01 基準、対象、保全、既存baselineを固定する — 完了

**前提:** 本R/D/Pの採否と後続実装の許可が明確であることです。親OPENは今回のユーザー提示観測として保持し、将来必要なlive条件はその時点で確認します。正式Issue413 Startや他worktreeの更新を開始条件に追加しません。

**手順:** 指定repository／branch／実施候補full SHAを再確認し、root AGENTS、本Issueの文書・metadata・二Artifact・親R/D/Pを読みます。採用後の文書commitを含む候補SHAと、本仕様の基準SHAを分けて記録します。local root、branch、HEAD、tracked／untracked差分、変更を許されたpathを確認します。既存作業をclean/reset/stashで消しません。

repository rootからの`src/spec_dock/runtime/infra/fs_repo.py`、`src/spec_dock/runtime/application/direct_scope_publish.py`、`src/spec_dock/runtime/commands/runtime_dispatch.py`、`src/spec_dock/runtime/cli/options.py`、`src/spec_dock/runtime/cli/catalog.py`、`src/spec_dock/runtime/domain/selectors.py`、変更するroot／provider文書、関連テストを再読します。参照先が基準から変わっていれば、該当D/Vだけを照合してから進めます。

本件で保持するIssue413 pack、実装記録、二Artifact、skill・shim・template・systemの変更前識別を記録します。通常のbaselineを取得します。

```sh
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check
make lint
uv run pytest
```

**完了条件:** 実施対象とbaselineの実exit、OS／Python、使用tool、既存失敗・skipが記録され、本件の追加検査と区別できることです。新しいRedがどのACを検査するか決まっていることです。

**失敗時:** branch／SHA／対象が不明なら停止します。既存テストが失敗した場合は原因・本件との関係を記録し、削除・policy skipで隠しません。fixtureのcollection/import故障は本件のRed成功ではありません。

<a id="s-02"></a>
### S-02 legacy診断を公開経路のRed→Greenで修正する — 完了

**依存:** S-01。[D-415-001](design.md#d-415-001)、V-001です。

**手順:** `tests/cli_runtime/test_issue413_scope_publish.py`の`publication_fixture`と必要な親Scope作成fixtureを使い、妥当な`.meta.json`と異なる内容の`meta.json`の同居を用意します。text／JSON、create／import、apply／dry-runを通す新しい検査を同じ既存test fileへ追加します。必要なimport固有の対照は`repo-root: tests/cli_runtime/test_issue413_scope_import.py`へ置きます。

現行実装で副作用なしに停止することを確認し、その診断が保全・確認・比較・手動判断を欠くために新しいassertionが失敗するRedを記録します。fixture不備や確認flag不足による別の停止をRedにしません。その後、`fs_repo.py`の診断文言だけをD-415-001へ変更して同じ試験をGreenにします。

```sh
uv run pytest tests/cli_runtime/test_issue413_scope_publish.py tests/cli_runtime/test_issue413_scope_import.py -q
```

**完了条件:** V-001の正しい到達と無副作用が確認され、旧rename案内が消えることです。`RuntimeError`／`LOCAL_IO_FAILED`／exit 5、検出範囲、GitHub変更前停止、既存negative testを維持します。

**失敗時:** 先行するschema・repo・stage・OS原語の不備で止まった場合はfixtureを正し、製品guardを迂回しません。期待と異なるwriteが観測された場合は、その事実を保全して範囲・Designを再評価します。一律削除や別writer導入へ進みません。

<a id="s-03"></a>
### S-03 四つの現行文書とprovider参照を整合させる — 完了

**依存:** S-01。[D-415-002](design.md#d-415-002)〜[D-415-005](design.md#d-415-005)、V-002〜005です。

**手順:** READMEの三つのJSON作成例、通常TARGET／import ref、root GitHub文書、root Sync文書、AGENTSの現在段落を、各Dで定めた範囲だけ変更します。配布CLI参照はprovider側を先に編集します。consumerの同名文書を先に書き換えません。

`tests/integration/test_cli_docs_vnext.py`へ限定したroot文書の検査と実掲載例の検証を追加します。既存の禁止語検索は「現在実行すべき例」の検査として維持し、履歴全体の一括禁止へ拡張しません。文法の既存正例・負例と公開実行を併用します。

```sh
uv run pytest tests/integration/test_cli_docs_vnext.py tests/cli_runtime/test_issue413_scope_import.py tests/cli_runtime/test_workspace_sync_vnext.py -q
git diff --check
```

**完了条件:** V-002〜005が成立し、履歴原本・親文書・runtimeの受付条件は不変です。配布文書のcurrent hashが一時的に不一致である場合は未統合と記録し、S-05までに必ず整合させます。その途中候補を配布可能としません。

**失敗時:** 文法を通すためのparser拡張、旧cache復活、過去記録の改ざんでは解決しません。作成例でGitHubへの実送信が必要なfixtureになった場合は試験を止め、隔離stubへ直します。

<a id="s-04"></a>
### S-04 leaf別の補完候補を三shellで揃える — 完了

**依存:** S-01。[D-415-006](design.md#d-415-006)、V-006です。

**手順:** `tests/cli_runtime/test_help_completion_vnext.py`へ、現在catalogの全44 leafについてyes／lockの候補表を検査するassertionと、実shellの代表的な正負例を追加します。最初に既存生成scriptの無効候補が検査を失敗させることを記録します。

`repo-root: src/spec_dock/runtime/cli/options.py::completion_script()`の共通候補選別と必要なshell出力に限定して修正します。lexical値処理とparser受付を変更しません。Bash/Zshの既存native harnessを再利用し、Fishは公開CLIのscriptを実Fishで読み込んで評価する検査を追加します。生成script自体が正しくてもshellが期待する候補を出さない場合は合格にしません。

```sh
uv run pytest tests/cli_runtime/test_help_completion_vnext.py tests/cli_runtime/test_cli_vnext_contract.py tests/cli_runtime/test_issue413_lock_options.py -q
```

**完了条件:** 全leafの候補集合と三shellの実補完がV-006を満たすことです。read leafの`-y`も除外し、`active set`等の既存MUTATING分類は保持します。44 leaf、共通option位置、helpのcontext-free性を保ちます。

**失敗時:** 実shell不在はそのnative検証の未実施として扱います。既存の環境依存skipを全て廃止する必要はありませんが、三shellの受入を文字列検査だけで閉じず、必要なshellを備えた認可済み検証環境で確認します。新しいpolicy skip／ledgerで未確認を隠しません。

<a id="s-05"></a>
### S-05 inventory、fresh wheel、fresh consumerを結合して確認する — 完了

**依存:** S-02〜04。[D-415-008](design.md#d-415-008)、V-008です。

**手順:** 変更したprovider文書の基準bytesと旧current SHA-256を照合します。`static-inventory.json`の該当current hashを改稿後bytesで更新し、基準current hashを既知旧hashへ追加します。既存旧hash二つとpath／mode／init_only／他entry／retired集合は保持します。仕様Markdown自身のhashを製品inventoryに使いません。

既存の`repo-root: tests/integration/test_issue413_assets.py`に、改稿前のCLI参照bytesを旧版consumerへ配置する更新検査を追加します。旧bytesは基準Git blobから取得した実内容を使い、テストfixtureへの取り込みを記録します。改稿済みbytesに適当な文字列を足して「既知旧版」と呼びません。unknown対照は正確に区別します。

```sh
uv run pytest tests/unit/infra/test_provider_distribution.py tests/integration/test_issue413_assets.py tests/integration/test_issue413_wheel.py tests/integration/test_cli_entrypoint_vnext.py -q
```

さらに、固定した候補SHAからfresh wheelを作り、外部非editable環境・fresh consumerで内容と挙動を確認します。下記はBash用の実施骨格です。`SOURCE_ROOT`は検証済みrepositoryの絶対root、`CANDIDATE_SHA`はその対象branchの検証済みcommit、`LAB`はすべての実worktree・Git領域・installed packageから離れた未使用の絶対pathです。実施前に親directoryが普通の実directoryであること、既存データと重ならないことを確認します。

```sh
set -euo pipefail
: "${SOURCE_ROOT:?検証したrepository rootを指定してください}"
: "${CANDIDATE_SHA:?検証したfull SHAを指定してください}"
: "${LAB:?未使用の外部作業pathを指定してください}"
test ! -e "$LAB"
mkdir "$LAB"
mkdir "$LAB/build-source" "$LAB/dist" "$LAB/run"
git -C "$SOURCE_ROOT" archive "$CANDIDATE_SHA" | tar -xf - -C "$LAB/build-source"
(cd "$LAB/build-source" && uv build --wheel --out-dir "$LAB/dist")
uv venv "$LAB/venv"
set -- "$LAB"/dist/*.whl
test "$#" -eq 1
test -f "$1"
WHEEL="$1"
uv pip install --python "$LAB/venv/bin/python" "$WHEEL"
CONSOLE="$LAB/venv/bin/spec-dock"
(cd "$LAB/run" && env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE \
  "$CONSOLE" help)
```

candidateのversionだけでは同じversionで異なるbuildを区別できません。source SHA、wheelのSHA-256、installed metadata、実consoleの絶対pathとmoduleのimport元を照合します。`-e`／editable install、consumerへのPythonコピー、`PYTHONPATH=src`による代用はしません。最低Python 3.10で必要となる依存も含めて正規に導入し、依存wheel未準備のまま`--no-index`を強制して検証不能にしません。

`LAB/run`等のsource外から実consoleを起動します。utility検査ではGit／ghを利用できないPATHでもhelp/version/completionが成功することを確認します。実行済みpackageがsourceを参照しないことはimport元の確認と、隔離copy内のsourceを参照不能にした条件で検査します。元repositoryは移動・削除しません。

fresh consumerは一時Git repositoryです。新しい外部consoleでinitし、全inventoryの配置内容を照合した後、stateful gh stubをPATHに置いて、修正した診断・例・補完を検査します。実repositoryのIssue作成、認証情報、直接対象をfixtureに使いません。

**完了条件:** V-008が成立し、source／wheel／installed resource／fresh consumerの内容と対象挙動が一致することです。既存consumer更新、ユーザー共通tool更新はまだ完了ではありません。

**失敗時:** wheelとログ・実hashを保全し、利用者環境へ進みません。unknownをknown-oldに追加したり、既知旧資産の保全検査を削ったりして解決しません。

<a id="s-06"></a>
### S-06 現在候補の通常検証・OS境界・配布を受け入れる — 完了

**依存:** S-05。V-001〜006、V-008、V-009です。

**手順:** 統合された現在候補で通常lint／全pytest／差分を実行し、限定suiteの結果とは別に保存します。LinuxとmacOSの既存配布laneを維持し、実console／static update／保全の結果をOSごとに記録します。最低Python 3.10の変更箇所と、既存CIのPython条件を満たすことを確認します。新たなWindows対応義務は追加しません。

```sh
make lint
uv run pytest
git diff --check
```

実行結果には候補SHA、OS／Python／shell、実コマンド、exit、passed／failed／skipped、wheel hashを対応付けます。異なる候補・OSの件数を合算して一つの全件合格としません。ソースが検査後に変わった場合は、変更範囲に必要な検査を再実行し、最終候補の通常gateを満たします。

**完了条件:** 通常gateと必要な実shell・配布検査が同じ候補を支えることです。未検証OSやnative shellは残余として明示し、必要受入が残る状態を全合格としません。source上の実装準備完了と、S-07／08の運用完了は別です。

**失敗時:** 関連stepへ戻り、元ログを残します。CIの権限・環境不足を製品修正で隠さず、正規の環境確認へ分離します。新しいしきい値緩和、policy skip、ledger、全件検査の削除は行いません。

<a id="s-07"></a>
### S-07 利用者packageと指定worktreeへ別々に適用する — 完了

**依存:** S-06。実施時の対象・更新結果が明示された許可が必要です。本仕様作成依頼そのものは実適用許可ではありません。承認済みの実施計画がその対象・操作を明示している場合は、その範囲で実行します。

**S-07a 外部package:** 現在PATHで選ばれるconsole、その実体、tool manager、package版、復元可能な更新前wheel／導入元、利用者共通の影響を確認します。S-06で認定したwheelとhashを使い、既存tool環境の正規の更新操作を行います。uv管理の通常導入なら`uv tool install "$WHEEL"`が入口の例です。使用中のuvのhelpで置換／再導入の条件を確認し、同versionで実体が更新されていない場合を検出します。無関係なconsoleをforceで上書きしません。

更新後は`command -v spec-dock`、`spec-dock --version`、実package resource・import元・対象診断／補完を確認します。candidate venvのconsoleが動くだけでユーザー共通toolを更新済みにしません。PATH設定の無断改変、旧engine fallback、global skill導入はしません。

**S-07b 一つのconsumer:** 明示された対象rootでinstallation showとdry-runを行い、対象がGit worktree rootか、writer protocolが現在のものか、資産がcurrent／known-old／unknownのどれかを確認します。対象が既存consumerならinitを再実行しません。新writerへのmigrationが必要な環境は、このIssueへ黙って取り込まず保留します。

```sh
spec-dock installation show --target "$PROJECT" --json
spec-dock installation update --target "$PROJECT" --dry-run --json
```

`PROJECT`は許可された絶対rootです。結果の`data.result.planned_paths`、`planned_retired_paths`、effectsを確認し、今回の承認差分以外の退役・欠落資産追加・変更があれば本適用を停止します。current CLIは全inventoryを扱うため、存在しない`--paths`等の絞り込みを前提にしません。

許可された差分だけであり、unknownがなく、新しい外部backup先がすべてのworktree／Git／packageから分離されている場合にだけ、次を実行します。

```sh
spec-dock installation update --target "$PROJECT" \
  --backup-dir "$BACKUP" --yes --json
spec-dock installation show --target "$PROJECT" --json
```

更新後は返却effectsと実fileのbytes/mode、backupと復元照合の結果、対象文書の内容を確認します。Scope metadata・直接記録・成果物・workspace宣言、非対象のskill／shim／template／system、他worktreeを変更していないことを確認します。`workspace.json`のinit-only整形差を通常static同期の不具合としません。

**完了条件:** package更新とconsumer適用が別の実結果で確認されることです。既に同じ内容なら、変更なしの観測結果として記録します。source変更から適用済みと推測しません。

**失敗時:** unknownや範囲外の計画は適用前停止です。partialならsucceeded／unknown／not_attemptedとbackupを残し、後述R-03の復元・forward recoveryへ進みます。他worktree更新や旧資産一括削除で辻褄を合わせません。

<a id="s-08"></a>
### S-08 About descriptionを独立して適用・read-backする — 完了

**依存:** S-06、[D-415-007](design.md#d-415-007)の候補の採否、descriptionだけの実施許可、正規の操作手段です。READMEのcommitやZIP採用は実施結果でも追加の設定変更許可でもありません。

**手順:** connectorで正確なrepositoryと現在descriptionを読み、許可された更新actionが利用できる場合はその正規actionを使います。利用する手段がGET専用なら書込みできると仮定しません。承認済みのローカルGitHub CLIが操作手段である場合、以下が将来の手順です。

最初に`full_name`、description、homepage、topicsと確認時刻を記録します。候補文字列と同じならPATCHを省略し、独立GETと「変更なし」で現在整合を記録できます。違う場合は変更直前に再読して競合を確認します。

```sh
gh api --hostname github.com --method GET repos/chemitaro/spec-dock \
  --jq '{full_name,description,homepage,topics}'
```

採用した候補と許可が一致する場合にだけ、descriptionを一回設定します。以下は未実行の操作例です。

```sh
DESCRIPTION='GitHub Issueに紐づく仕様・依存・成果物とworktreeごとの作業対象を管理する外部インストール型Python CLI。Linux/macOS・Python 3.10+に対応し、指定projectへ文書・template・project-local skill・薄いshimを静的配置します。'
gh api --hostname github.com --method PATCH repos/chemitaro/spec-dock \
  --raw-field "description=$DESCRIPTION" \
  --jq '{full_name,description,homepage,topics}'
```

PATCHと別のlive GETで確認します。`--cache`を使わず、送信値やPATCH応答をread-backの代わりに再表示しません。

```sh
gh api --hostname github.com --method GET repos/chemitaro/spec-dock \
  --jq '{full_name,description,homepage,topics}'
```

機械的な比較は、JSONから取り出したdescription文字列と採用候補の文字列を比較します。JSONのエスケープや表示上の折返しを文字列変更と混同しません。結果に`full_name=chemitaro/spec-dock`を要求します。

**証拠:** 操作主体、許可の根拠、時刻、repository、変更前description、送信したdescription、使用したmethod、実exit、PATCHの結果、別GETのactual、expectedとの一致、homepage/topicsの比較を[report.md](report.md)へ要約します。証拠は秘密を含まない必要部分に絞り、認証ヘッダ・token・環境変数全体を保存しません。

**完了条件:** V-007が成立することです。未実施、送信後確認不能、read-back不一致は保留です。About保留でもコードの限定的な検証結果は記録できますが、七件すべてを完了扱いにはしません。

**失敗時:** 権限不足ならその事実を記録して停止し、認証設定を自動変更しません。応答不明ならGETを先行し、送信していないと断定せず、自動再送しません。他設定や第三者の変更を戻さず、R-04へ進みます。

<a id="s-09"></a>
### S-09 全ACを実証拠へ結び付けてhandoffする — 未実施

**依存:** S-01〜08の実結果です。human mergeはこのstepに含めません。

**手順:** traceability表の全ACを現在候補・対応V・実ログ／read-backへ結び付け、未達・未実施・条件付きの項目を明示します。七件の修正だけであること、非対象の廃止やglobal化・履歴改変・他worktree適用がないことを確認します。source／package／consumer／Aboutの状態を別々に引き渡します。

**完了条件:** AC-415-001〜009を満たす実証拠があり、残余リスク・復元情報・別責務が明確なことです。仕様の完成だけ、過去3 passed、About候補文字列の記載だけでは完了にしません。人間のmergeやpackage公開は別の許可・責務として残します。

**失敗時:** 未達ACを正確に列挙して担当stepへ戻します。未実施の実適用をN/Aやpassに書き換えて全体を閉じません。対象scopeを将来変更する必要があれば、先にRequirementの明示的な採否判断へ戻します。

<a id="verification"></a>
## 検証

### V-001 legacy同居の公開negative test

既存再利用先は`repo-root: tests/cli_runtime/test_issue413_scope_publish.py`の`publication_fixture`、親を増やす`tests/cli_runtime/test_issue413_contract.py::add_scope`、既存の`tree_digest`です。新しい検査は公開`spec_dock.cli.main()`を通します。製品のlegacy検出関数をmockして「期待する例外を出した」だけでは検証になりません。

fixtureはcurrent writer、妥当なschema3 Scope、正しいGit remote、必要な親・template・rules・ignored staging条件を備えます。対象とは別の未登録GitHub番号をimportに使い、duplicateや親不正で先に止まることを避けます。createのapplyには`--yes`を付け、確認不足で止めません。metadataと同じdirectoryの`meta.json`は内容を区別できるsentinelとし、秘密や本物の利用者データは使いません。

基本matrixはcreate/import × initiative/epic/issue × apply/dry-run × text/JSONです。さらに代表的な同居ケースで既存の妥当な直接記録を持つfixtureも用意し、空の場合だけでなく既存選択の不変を確認します。Gitと必要原語の正しい環境で実行し、次を同時に確認します。

| 観測 | 期待 |
|---|---|
| 到達 | legacy検出に由来する文言を返します。先行schemaエラーや確認不足ではありません |
| 終了とJSON | 現在の`LOCAL_IO_FAILED`／exit 5、`status=failed`、`effects=[]`です |
| 診断 | 保全、既存`.meta.json`確認、比較、手動判断を促し、一律rename案内がありません |
| filesystem | 両metadataのbytes/mode、他metadata、直接記録、成果物、entry typeが不変です。新stage／scopeを残しません |
| Git／remote | `.git`のsnapshotとHEAD・branchが不変で、gh stubへの作成・変更がありません。このfixtureの経路ではlegacy拒否前のgh呼出しもないことを確認します |
| 対照 | legacyなしの公開作成／取込は既存の正例で成立します。`.meta.json`欠落は先行構造検査の失敗として別に扱います |

状態比較はatime等の読取に伴う値ではなく、既存tree digestのentry type／mode／bytesと意味のあるGit状態を用います。stub logは比較対象のconsumer外に置きます。失敗を新しい安全不具合と誤認しないため、例外classと発生段階を確認します。

### V-002 READMEの実掲載例と確認guard

既存`repo-root: tests/integration/test_cli_docs_vnext.py`を拡充し、READMEの対象code blockから三階層の作成argvを抽出します。固定例の親番号だけをfixtureの返却IDへ置換し、flagsや業務コマンドをテスト側で補いません。

stateful gh stubは未使用の異なる番号を返し、作成した親をOPENとしてGETできる状態を持ちます。三つの公開実行が成功し、返却ID／parent／linkageが一致することを確認します。各例から`--yes`を外した対照は`CONFIRMATION_REQUIRED`／exit 3・effectsなしとなり、stub変更とscaffold公開がないことを確認します。stdinは非対話に固定し、TTY環境で偶然成功する検査にしません。

### V-003 通常TARGETとimport ref

既存`repo-root: tests/cli_runtime/test_issue413_scope_import.py`の`test_import_accepts_existing_exact_reference_forms`と、現在のselector codecを基礎に、次の表を文書・実関数・公開入口で照合します。

| 入力 | 用途 | 期待 |
|---|---|---|
| `iss-00003`、`gh:example/repo#3` | 通常Scope TARGET | 妥当なfixture内で同じ対象へ解決します |
| `@current`等 | 通常Scope TARGET | 有効な選択・role条件がある場合だけ解決します |
| `3`、完全Issue URL | 通常Scope TARGET | 拒否し、変更しません |
| 完全gh ref、完全Issue URL | import REF | 同じrepositoryの妥当なIssueなら受理します |
| `413 --github-repo example/repo` | import REF | 既存のhint付き番号として受理します |
| `413`だけ、refとhintの不一致、別repository | import REF | 既存の拒否を維持し、remote変更・local公開がありません |

構文に見える誤りでも、通常selectorはproject解決後のValueErrorでexit 3になる経路があります。parserのexit 2へ揃える変更はしません。root文書の例とprovider文書の表が上記と一致すること、旧固定engineを現在方式として案内しないこと、リンク先が実在することを確認します。

### V-004 root Sync文書と読取不変

再利用先は`repo-root: tests/cli_runtime/test_workspace_sync_vnext.py`です。既存の`test_sync_preserves_direct_selection_and_opaque_old_projection`、`test_live_sync_failure_returns_unknown_and_keeps_the_captured_selection`等を維持します。

root文書の現行例をparser／公開CLIで確認し、local既定・github明示・cache退役を分けます。`--source cache`は退役診断／exit 2であり、存在しないcacheを初期化する手順を追加しません。opaqueな旧projection・direct recordのbytes不変、GitHub失敗時のunknown／partial／exit 7を確認します。新しいindex/treeを生成したことを完了条件にしません。

### V-005 AGENTSと履歴原本の境界

現行段落が「現在もmerge pending／0805以外は必ず未移行」という命令・現在認定になっていないことをレビューします。日時付きの過去引用を禁止語検索で除去しません。PR414の`merged`・merge commit・日時を根拠にし、他環境の移行証拠は別物とします。

基準との差分で、`repo-root: docs/issue-plans/iss-00413-external-cli-state/`全体と本Issueの二つの調査Artifactが不変であることを確認します。既存原本のbroken relative linkや旧ローカル絶対pathを直す作業には広げません。新しい文書からは実在するtimestamp付きArtifactへ直接参照し、その内部の古い参照名に依存しません。

### V-006 全leaf候補表、実shell、受付維持

公開CLIの`completion bash`／`completion zsh`／`completion fish`で得たscriptを使います。内部mapのみの検査にせず、全44 leafの生成候補がD-415-006の表を満たすことを確認します。正候補が一つもない実装でnegativeだけがGreenになることを避けます。

代表native入力は次です。

| 補完中の入力 | 必須観測 |
|---|---|
| `spec-dock scope list --` | `--json`等はあり、`--yes`／`--lock-timeout`はありません |
| `spec-dock scope list -` | 同義の`-y`もありません |
| `spec-dock active show --` | `--lock-timeout`はありません |
| `spec-dock work start iss-00003 --` | `--yes`／`--lock-timeout`／`--base`があります |
| `spec-dock scope create initiative --` | `--yes`があり、`--lock-timeout`はありません |
| `spec-dock --project "/not a repository" scope list --` | common valueをcommandと誤認せず、read leafの候補を返します |
| operand後、inline値、必要な値の入力中、既存`--`境界 | 既存の回帰テストが期待する挙動を維持します |

Bash/Zshは既存`_native_completion`を使えます。Fishは一時HOME／設定・completion探索先を隔離し、公開scriptを読み込んだ同じ実process内で`complete -C 'spec-dock scope list --'`等を評価します。返却行に説明が付く場合は候補とタブ区切りの説明を分けて比較します。利用者のshell設定は変更しません。

parser側でもread leafの`--yes`／`-y`、Start以外の`--lock-timeout`が従来どおり拒否され、受理leafの正例が通ることを確認します。root／44 leaf help、version、三補完は壊れたproject指定・Git/ghなしで成功し、Git/認証/業務contextへのアクセスとconsumer書込みがないことを確認します。

### V-007 Aboutのlive受入

S-08の前後GETと一回の許可されたPATCH、または既に同値の場合のlive unchanged観測を証拠にします。repository名とdescriptionの完全一致を確認します。homepage/topicsその他は更新payloadに含めません。実際のscopeを越えた変更がなかったか、保存する前後の必要項目と送信payloadで確認します。

送信後のtimeout、read-back不能、不一致、権限不足のいずれも「反映した」と表示しません。未実施を未実施と記録することは必須の報告ですが、それだけでAC-415-007の整合完了を満たしたことにはしません。pytestで本物のrepository descriptionを変更してこの検証を自動化しません。

### V-008 配布・旧版更新・保全のmatrix

| 検証面 | 具体的な確認 | 既存再利用先／追加部分 |
|---|---|---|
| inventory | 新currentがprovider bytesに一致し、旧二hash＋変更前currentが個別に保持されます。他entry・retired集合は不変です | `static_assets.package_static_assets()`とassets suite。今回変更entryの旧hash根拠を追加します |
| fresh wheel | runtimeが通常packageに一組、hidden assetsあり、inventory全resourceのbytes/hash一致です | `tests/integration/test_issue413_wheel.py`を維持します |
| 非editable環境 | worktree外の実console、import元が外部site-packages、sourceを参照不能にしても動きます | 同wheel suiteと`tests/integration/test_cli_entrypoint_vnext.py`です |
| fresh consumer | 実init後に全inventoryのpath/type/mode/bytes、改稿したCLI参照、維持skill/shimを照合します | `tests/integration/test_issue413_assets.py`、`tests/unit/infra/test_provider_distribution.py`です |
| 実挙動 | candidate consoleからV-001の診断、V-002/003の例・解決、V-006の補完を確認します | 既存fixtureと外部console呼出しを結び付ける追加境界です |
| 既知旧更新 | 基準CLI参照の実bytesから更新し、backup内旧bytes/mode、新内容、workspace／metadata不変を確認します | `test_update_replaces_only_verified_old_static_bytes_after_an_external_backup`の既存目的を再利用し、今回のentryを追加します |
| unknown対照 | 現行または旧資産を未知bytesへ変更したfixtureで、保全・更新前に停止します | `test_static_changes_refuse_unknown_current_or_retired_files_before_preservation`を維持します |
| backup／競合／partial | 不正backup先、同byte別実体、途中失敗で現物・backup・未実行効果が残ります | `test_update_checks_backup_location_and_confirmation_before_any_effect`と既存static update故障検査を維持します |
| 本件外の効果 | 実consumerのdry-runに別資産退役等があれば停止します | S-07bの運用確認です。汎用installerを本件専用の選択APIへ改造しません |

表中の関数名だけの行はすべて`repo-root: tests/integration/test_issue413_assets.py`に存在する既存関数です。fresh consumerの成功は実dogfood更新の成功ではありません。実環境のstatic受入はS-07bの別証拠を要求します。

### V-009 全体品質と完了表示

通常`make lint`／`uv run pytest`／`git diff --check`の現在候補の実結果、必要な三shell・Linux/macOS・Python 3.10境界、全Vの結果を集約します。既存全体試験を限定suiteに置き換えません。合格／失敗／skip／未実施を分け、未実施を隠すpolicyやledgerを作りません。

source差分、provider資産、inventory、実consumer、Aboutを別々にレビューします。履歴pack・親の旧操作・非対象skill廃止等が混入していないことを確認します。依存する証拠pathは実在するものだけを使用します。

## rollback

実装者・運用者が行う回復は次の四面に分けます。失敗の回復操作も正確な対象と許可に基づき、記載だけで自動実行しません。

| ID | 条件 | 手順 | 復旧確認／停止条件 |
|---|---|---|---|
| R-01 source／文書 | 本Issueの変更に不具合があり、まだ実適用していない、またはsourceを先に戻す必要があります | 現在差分と後続編集を保全し、本Issueの差分だけをレビュー可能な逆変更で戻します | 通常gateを再実行します。実consumer／Aboutまで戻ったとは表示しません |
| R-02 外部package | 更新後のCLIが誤動作し、旧compatible packageが識別・保全されています | 新しい操作を止め、正規toolで保全済みの新writer互換版へ戻します。PATHと実console/resourceを確認します | 旧fixed engineやwriter逆migrationへ戻りません。元wheel不明・互換不明ならforward recoveryを選びます |
| R-03 静的資産 | update partial、または改稿資産の限定復元が必要です | effects・現在file・backupを再観測し、backupを別の安全な一時場所へ復元してbytes/modeを比較します。現在fileの後続編集がない対象だけを明示復元します | metadata／成果物／direct record／他worktreeは不変です。後続編集・不明実体があれば停止しmanual mergeします |
| R-04 About | 設定後に説明を戻す必要があり、旧descriptionが保全されています | live GETで現在値を確認し、自分が設定した候補のままで復元許可がある場合だけ旧descriptionを一回設定し、別GETします | 第三者の新しい値・不明な送信結果なら停止します。他設定の巻戻しはしません |

`git reset --hard`、`git clean`、旧stateの一括削除、`installation uninstall`による回避、旧journal resume／rollbackを本Issueの回復手順にはしません。static backupはファイル復元の根拠であり、旧writer実行を許す証拠ではありません。

旧packageは改稿後のstatic bytesをknown-oldと認識しない可能性があります。downgradeしたCLIのupdateを無理に通さず、R-03の実体比較に基づく限定復元か、新しい修正版の適用を選びます。失敗ログ・backup・不明candidateは、復元確認前に掃除しません。

## exit / handoff

### 状態を分けた終了条件

| 状態 | 判定に必要なもの |
|---|---|
| 仕様候補作成 | 三文書の役割分離、RQ/AC対応、実在参照、ZIPの整合です。現在の納品はここだけです |
| 実装候補検証済み | S-02〜06の現在候補への実証拠です。Aboutや実環境の更新は含意しません |
| 運用適用確認済み | S-07のpackage／consumerの別証拠と、S-08のlive read-backです |
| Issueの七件整合完了 | AC-415-001〜009の全実証拠と、未達なしのhandoffです。human mergeは別責務です |

handoffには候補SHA／wheel hash、変更したpath、Vごとの実結果、適用した一つのtarget、packageの実体、backupと復元条件、Aboutのexpected／actual、保留と担当を含めます。長期判断はR/D/P、実測要約は[Report Guide](../../../../../../docs/authoring/report.md)に沿う既存[report.md](report.md)、生の根拠は認可された実在証拠へ分離します。

### 未決・別Issueと実施条件

| 区分 | 残す事項 | 扱い |
|---|---|---|
| 本Issueの実施入力 | 候補SHA、実wheel、tool環境、対象絶対root、外部backup、shell/OS環境、操作許可 | 該当step前に確定します。未確定ならそのstepを保留します |
| 本IssueのAbout採否 | D-415-007のdescription、実施主体・手段・権限、実施時点 | S-08前に確認します。未実施のまま成功にはしません |
| 将来の独立判断 | root `./spec`廃止、配布薄いshim廃止、global共通skill＋local project情報、同名優先順位、無関係なdead code整理 | 七件に不可欠ではありません。実施も決定も本Issueに含めません |
| 別の運用責務 | 他worktree更新、正式Issue413 Start、human merge、package公開 | 現在の成功を推測しません。別の明示依頼・責務へ残します |

現在のproject-local skillと現役rules symlinkは維持します。既存の旧資産・履歴を一括置換しません。本計画を採用しただけで、新しい配置方式・廃止方針が決まったことにはなりません。

### 実施手段の公式参照

外部手段は2026-10-06時点で確認した次の一次情報を基にしています。実施環境のtool版は別に記録します。

- GitHub repository更新: `https://docs.github.com/en/rest/repos/repos#update-a-repository`。descriptionのPATCHはfine-grained tokenではAdministration(write)等の該当する権限が必要です。token／接続方式に応じて確認し、変更許可を新設しません。
- GitHub CLI: `https://cli.github.com/manual/gh_api`。`--raw-field`は文字列を送信します。field追加時の既定methodに依存せず`--method PATCH`を明示します。
- Fish補完: `https://fishshell.com/docs/current/cmds/complete.html`。`complete -C`は補完候補の評価に使います。
- uv tool導入: `https://docs.astral.sh/uv/reference/cli/#uv-tool-install`。通常tool環境への導入と、candidateの外部venv検証を分けます。
