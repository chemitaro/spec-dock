---
種別: "要件定義書（Issue）"
ID: "iss-00346"
タイトル: "Integration, Distribution, and Final Quality"
関連GitHub: ["#346"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-31"
親: ["epic-00343", "init-local-00002"]
依存: ["iss-00344", "iss-00345"]
---

# iss-00346 Integration, Distribution, and Final Quality — 要件定義

## 0. この文書の位置づけ

本書は、ChatGPT planning に共有した GitHub 上の計画時 baseline revision `2217889c31e1a8a83732c446264dec00dde77be6`、親Epic、Issue 344/345、accepted ADR、現行コードとテスト、Issue-local clarification researchを根拠に、Issue 346が満たす観測可能な要件を定義する。実装方法と実行順序は`design.md`と`plan.md`が所有し、本書だけでは実装開始、レビュー完了、PR送達、マージ準備、Issue/Epic完了を意味しない。

本 Issue は親 Epic `epic-00343-workbench-shell-and-explicit-file-artifact-import` の Candidate 3 である。Issue 344 が Workbench shell scaffolding を、Issue 345 が generic single-file Artifact import を担当した。本 Issue は両者を再実装せず、**配布パッケージを通した統合、既存 consumer 更新、dogfood projection、互換性、platform 境界、全回帰、最終レビューと delivery gate** を閉じる。

## 1. 背景

Workbench は、SpecDock の root、Initiative、Epic、Issue ごとに置ける、一時的・worktree-local・破棄可能・non-canonical な作業領域である。追跡対象にできるのは direct child の `.workbench/README.md` だけで、それ以外の Workbench 内容は ignore される。残す価値がある単一ファイルは、明示的な generic Artifact import により、対象 scope の `artifacts/` へ evidence-only の複製として保存できる。

Issue 344 と Issue 345 の局所実装が正しくても、配布物として次が証明されなければ利用者価値は成立しない。

- candidate wheel に必要な shell、runtime、docs が入り、不要な stale output が混入していないこと。
- source checkout ではなく、その wheel から入れた CLI で fresh consumer が動くこと。
- feature 導入前を模した valid existing consumer を update しても、既存 scope に tracked README を backfill しないこと。
- update 後に作る future node には tracked README が入ること。
- provider repository 自身の dogfood consumer でも、既存 `epic-00343` を backfill せず、Workbench と generic import が一緒に機能すること。
- opaque bytes、external source privacy、Linux/macOS の accepted publication boundary、legacy command compatibility が配布後も維持されること。
- ordinary fast lane だけでなく、最終統合 Issue に要求された explicit opt-in full regression と fresh reviewer gates を通す計画と証跡経路があること。

## 2. 目的

| ID | 目的 |
|---|---|
| `I346-OBJ-001` | 各検証 cycle の開始時に記録した candidate revision から作った candidate wheel を唯一の配布入力として、fresh、existing-update、dogfood の三経路で Workbench shell と generic single-file import の統合動作を観測可能にする。 |
| `I346-OBJ-002` | no-backfill、external-source privacy、opaque lifecycle、Linux/macOS publication boundary、既存 command compatibility を回帰から保護する。 |
| `I346-OBJ-003` | Issue/Epic report、docs parity、fast/full test、fresh QA/code/spec review、commit/push、pull-request handoff Gate、Merge Preparation Gate へつながる最終品質証跡を、human-only merge の直前まで整える。 |

## 3. 利用者価値

1. **新規利用者**は、公開候補 wheel をインストールした直後から、各 scope の Workbench guidance と generic import を同じ配布物で利用できる。
2. **既存利用者**は、update により既存の root/Initiative/Epic/Issue が意図せず書き換えられず、将来作る node だけが新しい shell を受け取る。
3. **セキュリティ・運用担当者**は、external source の絶対 path、本文、digest、byte count などが public output や tracked provenance に漏れないことを確認できる。
4. **開発者・レビュアー**は、source checkout 依存ではない wheel-installed E2E、platform-specific host evidence、compatibility、full regression を一つの closure map で追跡できる。
5. **保守担当者**は、失敗時に正式 destination の作成有無、cleanup state、retry disposition、残存変更を区別し、bounded repair または rollback を判断できる。

## 4. ステークホルダー

| ステークホルダー | 関心 |
|---|---|
| SpecDock consumer | fresh install、update safety、CLI/output compatibility |
| Provider maintainer | package inventory、provider-first source、dogfood parity、回帰 |
| Linux/macOS platform maintainer | accepted filesystem capability boundary と host evidence |
| Security/privacy reviewer | external source disclosure、opaque byte handling、fail-closed semantics |
| `dev-coder` | runtime/CLI/infra/tests/scaffold の bounded implementation |
| `doc-writer` | shipped docs/templates/workflow text の parity |
| `qa-reviewer` / `code-reviewer` / `spec-reviewer` | 独立した最終品質、実装、仕様整合の判定 |
| Codex orchestrator | candidate evidence の採否、正本統合、report ledger、delivery coordination |
| Human maintainer | 最終 merge 判断と実行 |

## 5. スコープ

### 5.1 In scope

- exact branch/head の再確認と candidate-wheel provenance。
- `uv build` による wheel build、template README inventory、stale/cached output 非混入検査。
- wheel を isolated environment に install した fresh consumer の init/node creation/import E2E。
- valid synthetic existing consumer の update/no-backfill/future-node E2E。
- exact revision の disposable dogfood checkout に candidate wheel を適用する integrated projection。
- root/Initiative/Epic/Issue generic import、external source、可能な host での actual cross-filesystem source。
- binary、ZIP、invalid UTF-8、NUL-bearing file の opaque lifecycle。
- Linux supported filesystem と capability-insufficient failure lane。
- macOS clone-capable success と accepted cleanup trust boundary。
- `artifact import chatgpt-output`、`new artifact`、`workbench copy` の compatibility regression。
- provider/docs/dogfood parity、Issue/Epic report traceability、EAL disposition 候補。
- ordinary fast lane、explicit opt-in full regression、fresh reviewer gates、commit/push、pull-request handoff/merge-preparation、人間 merge 前停止。
- 発見された cross-feature integration/distribution defect に限る最小修理。

### 5.2 Out of scope

- Workbench shell または generic import の新しい major feature。
- Issue 344/345 の欠落 scope を本 Issue に吸収すること。
- automatic Workbench sync、watch、hook、copy-back。
- root Workbench payload を `workbench copy` 対象へ拡張すること。
- generic file の semantic parse、frontmatter 解釈、MIME/encoding policy、canonical promotion。
- external source の absolute path、本文、digest、byte count を public contract に追加すること。
- Linux に named-temp、visible probe、pathname cleanup fallback を導入すること。
- macOS trust boundary を accepted ADR より強く見せること。
- parent Epic、accepted ADR、cross-Issue ownership、workflow completion policy の再定義。
- human merge の実行。

## 6. 前提

| ID | 前提 |
|---|---|
| `I346-ASM-001` | Issue 344 と Issue 345 の canonical docs/report は本 Issue の upstream dependency evidence であり、本 Issue 開始前に fresh に再確認される。 |
| `I346-ASM-002` | `.workbench/README.md` がない workspace/node も valid であるため、pre-feature existing consumer は historical revision を必須とせず synthetic fixture で表現できる。 |
| `I346-ASM-003` | historical revision を任意採用する場合は、feature absence の根拠、exact SHA、取得方法を `report.md` に記録する。 |
| `I346-ASM-004` | provider source of truth は `src/spec_dock/`、`spec-dock/` は dogfood consumer projection である。 |
| `I346-ASM-005` | platform success は OS 名だけでなく、destination filesystem と必要 primitive の capability に依存する。 |
| `I346-ASM-006` | full-regression body は `--run-full-regression` がある場合だけ実行され、`-m full_regression` 単独は実行許可にならない。 |
| `I346-ASM-007` | revision `2217889c31e1a8a83732c446264dec00dde77be6` は ChatGPT planning に共有した計画時 baseline であり、実装・検証対象となる candidate revision を固定する値ではない。 |

## 7. 制約

| ID | 制約 |
|---|---|
| `I346-CON-001` | repository `chemitaro/spec-dock`、branch `iss-00346-integration-distribution-and-final-quality` に対し、各検証 cycle の開始時 HEAD を candidate revision として記録する。wheel、consumer、platform、dogfood、regression、review の関連証跡は同じ candidate revision に結び付ける。実装・文書・test の変更で HEAD が変わった場合は新しい candidate revision として扱い、変更の影響を受ける証跡を fresh に再取得する。 |
| `I346-CON-002` | parent Epic と accepted ADR の意味を Issue-local 文書で再定義しない。矛盾が判明した場合は実装を止め、Epic planning repair へ戻す。 |
| `I346-CON-003` | 許容修理は、S01〜S04 の証拠で発見された cross-feature integration または distribution defect を閉じる最小変更だけとする。新 feature、広い refactor、Candidate 1/2 scope 回収は禁止する。 |
| `I346-CON-004` | shipped behavior/docs/templates/runtime は provider-first で変更し、dogfood projection を source of truth にしない。 |
| `I346-CON-005` | 外部planning evidence、test output、Artifact import resultはevidence-onlyであり、明示的な採否判断なしに正本やlifecycle authorityを変更しない。 |
| `I346-CON-006` | pre-feature fixture は update 前に valid で、既存 root/Initiative/Epic/Issue の `.workbench/README.md` がすべて欠落していることを観測する。条件を満たさない fixture は使用しない。 |
| `I346-CON-007` | Linux explicit import は linkable anonymous `O_TMPFILE`、held FD、`/proc/self/fd/<fd>`、FD-bound no-replace commit を使う。capability 不足時は formal destination 作成前に fail closed し、named-temp、visible probe、pathname cleanup fallback を使わない。 |
| `I346-CON-008` | macOS は clone-capable `fclonefileat` success と accepted cleanup policy を検証するが、same-UID actor が final identity check と unlink の間に置換する事象を除外した trust boundary を超える保護を主張しない。 |
| `I346-CON-009` | ordinary `uv run pytest` と explicit `uv run pytest --run-full-regression` は別々の required evidence として記録する。skip を full-regression success と扱わない。 |
| `I346-CON-010` | pull-request handoff Gate と Merge Preparation Gate の後も merge は human-only とし、自動 merge または merge 実行を本 Issue の agent scope に入れない。 |
| `I346-CON-011` | external source の user-visible text/JSON と tracked provenance に、absolute path、parent path、本文、SHA-256、byte count、その他 content-derived value を含めない。 |
| `I346-CON-012` | `plan.md` は planned contract、`report.md` は observed evidence ledger とし、実行結果を plan に書き戻して二重正本にしない。 |

## 8. 用語

| 用語 | 平易な定義 |
|---|---|
| Workbench | root または node に置く、一時的で worktree-local、破棄可能、non-canonical な作業領域。 |
| tracked README guidance shell | `.workbench/README.md`。Workbench の用途、安全境界、import/copy の手順を説明する唯一の追跡対象 entry。 |
| ignored Workbench contents | README 以外の `.workbench/` 内容。Git ignore 対象だが、secret を置いてよいという意味ではない。 |
| generic Artifact import | `artifact import file` により、明示した regular file の opaque bytes を target scope の `artifacts/` に evidence-only で複製する機能。 |
| candidate wheel | 各検証 cycle の開始時に記録した candidate revision から build し、最終配布候補としてテストする Python wheel。planning baseline revision から固定的に build するものではない。 |
| fresh consumer | candidate wheel の CLI で新規 init した repository。 |
| existing consumer | update 前から有効な SpecDock workspace を持つ repository。本 Issue では README 欠落状態を synthetic に構成する。 |
| dogfood | SpecDock provider repository 自身を、その shipped scaffold/runtime の consumer として検証すること。 |
| no-backfill | update が既存 root/node に新しい tracked README を遡及追加しないこと。 |
| opaque file | byte 列として保存し、内容を text/frontmatter/ADR/metadata として解釈しない file。 |
| evidence-only | 採否判断の材料であり、正本や権限状態を自動変更しないこと。 |
| canonical document | review と採用 workflow を経て source of truth になった requirement/design/plan/report 等。 |
| reviewer gate | 指定 role が fresh source/diff/evidence を独立確認し、次工程へ進めるか判断する gate。 |
| formal destination | import が利用者に返す最終 Artifact filename。staging/probe path ではない。 |
| capability-insufficient | OS 名は一致しても、filesystem/primitive/procfs 等が accepted publication contract を満たさない状態。 |

## 9. 機能要件

| ID | 要件 |
|---|---|
| `I346-RQ-001` | 実行時に repository/branch/HEAD/working-tree state を取得し、candidate wheel と全 integration evidence を exact source revision に結び付ける。 |
| `I346-RQ-002` | clean build から candidate wheel を生成し、template subtree の許可 README 5件、必要 runtime/docs、禁止 stale wrapper/template/cache entry の inventory を機械検査する。 |
| `I346-RQ-003` | source checkout を import path に入れない isolated environment へ candidate wheel を install し、fresh consumer の root/Initiative/Epic/Issue shell と generic import を end-to-end で検証する。 |
| `I346-RQ-004` | valid synthetic existing consumer を update し、既存 root/Initiative/Epic/Issue の README 欠落、既存 spec/metadata/ignored payload の不変、managed asset update を同時に検証する。 |
| `I346-RQ-005` | update 後に新規作成した Initiative/Epic/Issue が tracked README shell を受け取り、その README が provider template と byte-identical であることを検証する。 |
| `I346-RQ-006` | exact revision の disposable dogfood checkout を candidate wheel で update し、既存 `epic-00343` を backfill せず、future node の Workbench file を generic import できることを検証する。 |
| `I346-RQ-007` | candidate-wheel-installed runtime から root/Initiative/Epic/Issue の全 target へ generic import を行い、source/destination bytes、identity grammar、`canonical=false`、no-overwrite を検証する。 |
| `I346-RQ-008` | repository-relative、absolute external、nested-CWD relative external、および host capability があれば actual cross-filesystem source を検証する。 |
| `I346-RQ-009` | external source の text/JSON output と tracked provenance を allowlist 検査し、absolute/parent path、body sentinel、digest、byte count、content-derived value がないことを証明する。 |
| `I346-RQ-010` | binary、ZIP、invalid UTF-8、NUL-bearing generic Artifact が validate、sync、discovery、dependency compilation、context generation により body-open/parse されず、既存 output を汚染しないことを検証する。 |
| `I346-RQ-011` | Linux supported-filesystem lane で anonymous `O_TMPFILE` staging と FD-bound no-replace commit を実証し、capability-insufficient lane で formal destination 前 fail-closed、visible staging/probe 不在、pathname cleanup 不在を実証する。 |
| `I346-RQ-012` | macOS clone-capable lane で destination-side staging と `fclonefileat` no-replace success を実証し、cleanup uncertainty は retained/no-unlink semantics と accepted same-UID exclusion の範囲で評価する。 |
| `I346-RQ-013` | `artifact import chatgpt-output`、typed/blank `new artifact`、node-scoped `workbench copy` の現行 public contract と既存 data を回帰させない。 |
| `I346-RQ-014` | ordinary fast tests、explicit full regression、lint、validate、`sync --no-github`、docs/provider-dogfood parity を別々の evidence として記録し、Issue report と Epic report に trace する。 |
| `I346-RQ-015` | fresh QA/code/spec review、Issue/Epic-wide review、final commit/push、pull-request handoff Gate、Merge Preparation Gate を順に計画し、human merge の直前で停止する。blocking defect 修理は `I346-CON-003` に従う。 |

## 10. 非機能要件

| ID | 要件 |
|---|---|
| `I346-NFR-001` | **再現可能性**: wheel filename、wheel digest、inventory、Python/OS/filesystem capability、source revision、実行 command、test node を report から再構成できる。 |
| `I346-NFR-002` | **隔離性**: fresh/update fixture と dogfood exercise は disposable directory/checkout で行い、失敗しても developer の canonical workspace や external source を破壊しない。 |
| `I346-NFR-003` | **fail-closed**: source eligibility、target binding、publication capability、identity、privacy allowlist の不確実性を success に丸めない。 |
| `I346-NFR-004` | **platform honesty**: hermetic simulation、actual host evidence、skipped/unavailable capability を区別し、別 platform の成功を推測しない。 |
| `I346-NFR-005` | **保守性**: 既存 installer/runtime/helpers/test harness を優先し、Issue-local distribution test のためだけの production abstraction を導入しない。 |
| `I346-NFR-006` | **診断可能性**: precommit failure、postcommit warning、cleanup state、retry disposition、fixture phase、platform capability、changed-path manifest を content-free に記録する。 |
| `I346-NFR-007` | **実行時間政策**: ordinary fast lane の policy を維持し、heavy E2E/platform/full suite は明示 opt-in のまま最終 Issue で実行する。 |

## 11. 互換性要件

- `artifact import chatgpt-output` は Workbench-only source policy、既存 filename grammar、source/hash/count を含む固有 result contract を維持する。generic import の privacy contract を legacy command に誤適用しない。
- `new artifact` は typed/blank Artifact の既存 creation、collision slot、rules link、filename grammar を維持する。既存 file の migration/rename を行わない。
- `workbench copy` は node-scoped、manual one-shot、source-wins/既存 contract を維持し、root Workbench を対象へ追加しない。
- `spec-dock update` は managed scaffold を更新するが、`spec-dock/initiatives/**` の canonical data を削除・置換せず、既存 node の Workbench README を backfill しない。
- generic imported file は既存 typed/blank/ADR/discussion discovery と slot accounting を壊さず、default semantic lifecycle の入力にならない。

## 12. Platform 境界

### 12.1 Linux

Supported lane の成立条件は少なくとも次を含む。

- destination filesystem が linkable anonymous `O_TMPFILE` を提供する。
- opened object が regular file である。
- `/proc/self/fd/<fd>` が held descriptor と同一 object を指す。
- destination directory の durability preflight が成功する。
- held source FD から held anonymous temp FD へ copy/verify できる。
- `/proc/self/fd/<temp-fd>` から held destination-directory FD への no-replace link commit が成功する。

成立しない場合、結果は content-free の `publication_unsupported` 相当で `committed=false`、formal destination 不在とする。Linux explicit flow に named stage、visible capability probe、stage pathname cleanup、unsafe fallback を追加しない。

### 12.2 macOS

Supported lane は clone-capable destination filesystem と `fclonefileat` を用いる。staging は destination directory 内の high-entropy、`O_EXCL`、`O_NOFOLLOW` の named file と held FD で行う。commit 前に destination parent identity と source/stage stability を検証し、no-replace clone を formal destination に行う。

cleanup は final lstat/open/fstat/identity/type check で owned stage を確認できる場合だけ unlink し、不確実、missing、replacement、unexpected type、stat/open failure の場合は retain/no-unlink とする。ただし同一 UID の敵対 actor が final check と unlink の間に置換する事象は accepted trust boundary で除外されており、それ以上の protection は本 Issue の acceptance に含めない。

### 12.3 その他 platform

Accepted commit primitive がない platform を推測で success にしない。unsupported は fail closed とし、support 拡張は別 planning/ADR 対象とする。

## 13. Privacy / Security 要件

1. 明示した一 file だけが read authorization の対象であり、parent directory の列挙や sibling read を行わない。
2. external source の public `source` 表示は basename-only とする。
3. text/JSON output、warning/error、tracked report/provenance に次を含めない。
   - source の absolute path または parent path sentinel
   - body sentinel または body excerpt
   - source/stage/destination SHA-256
   - byte count
   - body から導出した MIME、encoding、content ID 等
4. byte equality/hash/count は test process 内部の assertion に利用できるが、public result と tracked evidence には値そのものを残さず、`matched=true` 等の content-free 判定だけを記録する。
5. generic imported Artifact body は evidence そのものであるため target `artifacts/` に保存されるが、report/provenance へ複製しない。
6. secret/authentication secret/private data を fixture に使わず、漏えい検査には無害な sentinel を使う。
7. Git ignore は security boundary ではないため、Workbench に機密を置くことを推奨しない。

## 14. Failure semantics

| 区分 | 必須意味 |
|---|---|
| build/inventory failure | candidate wheel を consumer test に進めない。dist/build の stale 状態を消した fresh build で再現し、package repair は最小範囲に限定する。 |
| precondition/fixture failure | fixture を無効として停止する。invalid fixture で product failure を主張しない。 |
| source/target eligibility failure | source/target を変更せず、formal destination を作らず、content-free failure を返す。 |
| Linux capability insufficient | formal destination 前 `not_committed`。named/visible fallback へ降格しない。 |
| macOS precommit cleanup uncertainty | formal destination 不在。owned stage の identity を確定できなければ retain/no-unlink として報告する。 |
| postcommit durability/cleanup warning | committed result を取り消さず、`committed_with_warning` と retry `not_needed` を区別する。 |
| no-backfill violation | managed update が既存 node を変えた distribution defect として blocker。最小修理で閉じられなければ Epic planning repair。 |
| privacy leak | release blocker。漏えい値を report に転載せず、漏えい class と affected surface だけを記録する。 |
| ordinary/full regression failure | success claim をせず、failing nodes、head、platform、scope を記録して bounded triage へ進む。 |
| requirement/design/ADR conflict | implementation を止め、Issue-local repair で吸収せず Epic planning repair または clarification へ戻す。 |
| PR/check/review blocker | latest head に再束縛して PR preparation workflow で扱い、human gate または bounded repair とする。 |

## 15. Observability と evidence obligation

| ID | 必須証跡 |
|---|---|
| `I346-EVD-001` | repository、branch、計画時 baseline revision、検証 cycle の candidate revision、working-tree state、確認時刻。candidate revision 変更時は無効化した証跡と再取得結果も記録する。 |
| `I346-EVD-002` | build command、wheel path/name、wheel digest、package version、inventory allow/deny result、build source revision。 |
| `I346-EVD-003` | fresh consumer の isolated install method、source-checkout 非依存、root/node shell、generic import result、cleanup。 |
| `I346-EVD-004` | synthetic existing fixture recipe、update 前 valid state、README absent matrix、before/after immutable snapshot、future-node shell。historical revision 利用時は exact SHA と absence proof。 |
| `I346-EVD-005` | disposable dogfood checkout、pre/post `epic-00343` README absence、provider-to-projection manifest、future node + import integrated result。 |
| `I346-EVD-006` | target/source/platform matrix、actual cross-filesystem availability、Linux capability details、macOS clone capability、unavailable/skip reason。 |
| `I346-EVD-007` | privacy sentinel allowlist result、opaque body-open count、validate/sync/discovery/deps/context before/after equivalence。値そのものは保存しない。 |
| `I346-EVD-008` | legacy compatibility test nodes と結果、changed existing expectations の有無。 |
| `I346-EVD-009` | lint、ordinary tests、explicit full regression、validate、`sync --no-github`、diff/clean status の個別結果。 |
| `I346-EVD-010` | docs impact、Issue/Epic report trace、EAL dispositions、fresh reviewer verdicts、commit/push、pull-request handoff Gate、Merge Preparation Gate、human-only merge stop。 |

`report.md` には command の完全な verbatim interaction log ではなく、command、exit status、test summary、artifact/evidence path、head/platform binding、判断に必要な短い要約を残す。

## 16. Acceptance criteria

| ID | 観測可能な acceptance criterion |
|---|---|
| `I346-AC-001` | 計画時 baseline revision `2217889c31e1a8a83732c446264dec00dde77be6` と、build/test 開始時の candidate revision を別々に記録し、wheel provenance には candidate revision と同じ revision が記録される。検証途中で HEAD が変わった場合、旧 candidate revision に結び付く影響対象の証跡を stale として停止し、新 revision で再取得する。 |
| `I346-AC-002` | clean `uv build` で wheel が生成され、wheel 内 template subtree の README は許可された5件だけで、legacy wrapper-era file、`current/`、`completed/`、non-allowlisted nested README、`__pycache__`、`.pyc/.pyo` が存在しない。 |
| `I346-AC-003` | isolated environment に wheel を install し、source checkout を Python/import/runtime path に使わずに fresh init、Initiative/Epic/Issue creation、4 scope の tracked README、少なくとも1件の generic import が成功する。 |
| `I346-AC-004` | update 前に valid かつ root/Initiative/Epic/Issue README がすべて absent の synthetic consumer を candidate wheel で update しても、4 scope の README は absent のまま、既存 spec/metadata/ignored payload は byte/identity snapshot 上不変である。 |
| `I346-AC-005` | `I346-AC-004` の update 後に作る future Initiative/Epic/Issue はそれぞれ tracked README を持ち、provider template と byte-identical である。 |
| `I346-AC-006` | exact-revision の disposable dogfood checkout で update 前後とも既存 `epic-00343/.workbench/README.md` が absent であり、同じ projected runtime で future node shell から generic import を実行できる。 |
| `I346-AC-007` | candidate-wheel-installed runtime で root/Initiative/Epic/Issue の4 target に opaque file を import でき、source/destination bytes は一致し、source は不変、result は `canonical=false`、既存 destination を上書きしない。 |
| `I346-AC-008` | repository-relative、absolute external、nested-CWD relative external、および利用可能な actual cross-filesystem source が動作し、external output/provenance は basename-only かつ absolute/parent path、body、digest、count、derived value を含まない。 |
| `I346-AC-009` | binary、ZIP、invalid UTF-8、NUL-bearing generic files の存在前後で validate、`sync --no-github`、discovery、deps、context が decode/body-open error を起こさず、generic body-open count は0、typed/ADR/projection output は正規化比較で同等である。 |
| `I346-AC-010` | actual Linux supported-filesystem host で anonymous `O_TMPFILE` が linkable であり、visible `.spec-dock-import-*` entry を一度も作らず、held FD から no-replace formal commit して byte-preserving success になる。 |
| `I346-AC-011` | Linux capability 不足を注入または実ホストで観測した場合、`publication_unsupported` 相当、`committed=false`、formal destination 不在、visible stage/probe 不在、pathname cleanup call 不在となる。 |
| `I346-AC-012` | clone-capable macOS host で external/cross-filesystem source を destination-side stage から `fclonefileat` で no-replace commit でき、cleanup ambiguity/replacement/missing/type/stat/open failure は accepted retain/no-unlink semantics に従う。evidence は same-UID exclusion を超える保護を主張しない。 |
| `I346-AC-013` | existing focused suites により `artifact import chatgpt-output`、typed/blank `new artifact`、`workbench copy` の public contract と既存 data が不変である。 |
| `I346-AC-014` | `make lint` と ordinary `uv run pytest` が実行され、full-regression tests が policy skip された数と通常 lane の結果が記録される。ordinary lane を full result と表現しない。 |
| `I346-AC-015` | `uv run pytest --run-full-regression` が最終 candidate revision で実行され、skip ではない full suite result、duration、failure/skip summary が記録される。以後 HEAD が変わった場合は変更影響を判定し、wheel、consumer/platform/dogfood、regression、review を含む影響対象の証跡を新しい candidate revision で再取得する。 |
| `I346-AC-016` | shipped docs/help/rules、provider assets、dogfood projection が実装 contract と一致し、Issue report と Epic report が Candidate 1/2 dependency、Candidate 3 evidence、platform/compat/full-regression status を相互参照する。 |
| `I346-AC-017` | final candidate revision の実装/test/docsと、reviewer evidence欄を空に正規化したfinal reportを対象に `review_content_hash` を固定し、fresh `qa-reviewer`、Issue/Epic-wide `code-reviewer`、`spec-reviewer` を独立実施して未解決 blocker が0である。review後に許可するreport変更は、外部review出力からrole、task/session ID、status、findings count、scope、observed_at、機械的gate stateを転記する場合だけとし、転記後に同じ正規化で`review_content_hash`が一致することを確認する。unavailable/denied/skipped は成功扱いしない。 |
| `I346-AC-018` | `review_content_hash`が一致するfinal reviewed contentと許可されたreview evidence転記をcommit/pushし、final commit SHAとpost-commit clean checkは自己参照しないexternal delivery evidenceへ記録する。PR URL/base/head/latest SHA/issue linkageをpull-request handoff Gateに、checks/reviews/conflicts/threads/blockers/final decisionをMerge Preparation Gateに記録し、agentはhuman merge前に停止する。 |
| `I346-AC-019` | 実装中の変更が strict repair boundary 内であることを changed-path/decision ledger から確認できる。requirement/design/ADR/cross-Issue ownership の変更が必要な場合、実装を進めず Epic planning repair へ戻した証跡を残す。 |

## 17. Edge cases

| ID | ケース | 必須挙動 |
|---|---|---|
| `I346-EC-001` | build 中または test 中に branch HEAD が移動する | evidence を stale とし、新 head で build からやり直す。異なる head の結果を混在させない。 |
| `I346-EC-002` | `dist/`/`build/` に前回 build の stale file がある | clean build と wheel inventory を再実行し、stale contamination を release candidate に含めない。 |
| `I346-EC-003` | wheel install 後も source checkout が `PYTHONPATH`/cwd から import される | fixture failure。installed module origin を wheel environment 内で検査し、source fallback を許可しない。 |
| `I346-EC-004` | synthetic existing fixture のいずれかの README が update 前から存在する、または validate 不可能 | fixture を破棄して再作成し、no-backfill evidence に使わない。 |
| `I346-EC-005` | update 前の ignored Workbench payload がある | payload bytes/path を保持し、README だけでなく payload の accidental deletion/track を検出する。 |
| `I346-EC-006` | existing consumer の managed asset は古いが canonical node data は新しい | managed asset だけ更新し、node data を migrate/backfill/rename しない。 |
| `I346-EC-007` | external basename と body に path/hash/count らしい sentinel が含まれる | basename 以外を public output/provenance に出さず、sentinel body/derived value を leak しない。 |
| `I346-EC-008` | cross-filesystem source を作れる mount が host にない | hermetic device-independence evidence と unavailable reason を記録し、actual cross-FS requirement がある gate を未完了のままにする。 |
| `I346-EC-009` | Linux filesystem に `O_TMPFILE` がない、linkable でない、`/proc` identity を確認できない、directory fsync が失敗する | formal destination 前に fail closed。named/visible fallback を使用しない。 |
| `I346-EC-010` | Linux no-replace commit 時に destination が競合する | existing file を保持し、shared allocation policy に従って次 slot を試す。上書きしない。 |
| `I346-EC-011` | macOS destination が clone-capable でない | `publication_unsupported` 相当で precommit failure。copy/rename fallback を追加しない。 |
| `I346-EC-012` | macOS stage cleanup 中に stage が missing/replaced/special type、または stat/open が不確実 | unlink せず retain/uncertain として報告する。accepted same-UID exclusion は残る。 |
| `I346-EC-013` | ZIP/invalid UTF-8/NUL file の basename が `.md` または ADR 風である | filename family だけで generic と認識し、body を text/frontmatter として読まない。 |
| `I346-EC-014` | legacy command と generic import が同秒に filename slot を競合する | shared slot ledger と no-overwrite を維持し、既存 typed/blank/generic file を変更しない。 |
| `I346-EC-015` | ordinary lane は成功するが explicit full regression が失敗する | final quality gate は未完了。failure を bounded triage し、full result を省略しない。 |
| `I346-EC-016` | docs、report、PR observation が final pushed head より古い | 原則としてstale evidenceとし、latest headへ再束縛してrefresh/re-review/re-observeする。唯一の例外は`I346-AC-017`で許可されたreview evidence転記だけでfinal SHAが変わり、正規化後`review_content_hash`がreview時と一致する場合であり、このときreviewer receiptとfinal SHAの両方をexternal delivery evidenceで結ぶ。 |

## 18. Rollback / recovery

### 18.1 Test fixture

- fresh/update/dogfood は disposable directory または disposable checkout で実行し、終了時に削除する。
- failure 時は fixture を保持する必要がある場合でも、host-local path や payload を tracked report に貼らず、content-free artifact reference だけ残す。
- source file は copy/import の成功・失敗にかかわらず不変であることを検査する。

### 18.2 Production change

- cross-feature/distribution repair は step-local commit candidate に分離する。
- repair が acceptance を満たさない場合はその commit を revert 可能な粒度に保つ。
- provider asset を直した場合は corresponding dogfood projection を repository-approved update flow で再生成し、consumer-first 手修正を残さない。
- canonical Issue/Epic data の accidental mutation は、provider repair と分離して元 snapshot へ戻し、原因を blocker として扱う。
- committed Artifact は rollback のために自動削除しない。test fixture 内では fixture ごと破棄する。

### 18.3 Workflow recovery

- reviewer finding、CI failure、merge conflict は latest head に対する integrated blocking batch として扱う。
- P0/P1 または required CI failure の repair は strict repair boundary 内でのみ delegated worker に渡す。
- requirement/design/ADR/ownership の修正が必要なら Issue execution を止め、Epic planning repair と fresh review へ戻す。
- PR preparation は merge を行わず、human gate で終了する。

## 19. Handoff contract

1. current branch/head、依存Issue、accepted ADR、source manifestのfreshnessを再確認する。
2. `design.md`で各要件を既存provider/build/update/runtime/test surfaceへ割り当てる。
3. `plan.md`で全required closure IDをvertical behavior slice、検証、report evidenceへ追跡可能にする。
4. requirement/design/planの各phaseでfresh `spec-reviewer` passを得る。
5. runtime guidanceとreport evidence gateが実装開始を許可することを別途確認する。
6. approved planned contractに従い、`dev-coder` / `doc-writer`とreviewer gatesをstep単位で実行する。
7. 実測結果はIssue `report.md`、最終traceは親Epic `report.md`へ残す。
8. final deliveryはPR Delivery GateとMerge Preparation Gateまで進め、人間のmerge判断前で停止する。
