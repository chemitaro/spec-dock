---
種別: research
ID: "20260728t054338z-research"
タイトル: "Workbenchと任意ファイルArtifact importのあるべき状態・現状差分再整理"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00312"]
関連: ["20260728t053452z"]
authority: "synthesized"
derived_from:
  - "2026-07-28 user clarification"
  - "20260728t053452z-chatgpt-output-workbench-artifact-import-intent-gap-analysis.md"
reflected_to: []
---

# Workbenchと任意ファイルArtifact importのあるべき状態・現状差分再整理

> 確定整理。Workbench tracked shell の適用範囲は
> `20260728t054625z-interview-workbench-tracked-shell-coverage.md`
> で回答済み。任意file importのfilename規則も
> `20260728t060417z-interview-generic-file-import-filename-contract.md`
> でOption Aとして回答済み。repository外sourceの許可方式は
> `20260728t060706z-interview-external-file-import-policy.md`
> でOption Aとして回答済み。`workbench copy`の今後の扱いは
> `20260728t060909z-interview-workbench-copy-disposition.md`
> でOption Cとして回答済み。blockingなユーザー意図の未確定事項はない。

## 1. この再整理の結論

前回調査は、現在の狭い canonical Epic 契約に実装が適合しているかを重視しすぎていた。そのため、利用者が必要としている単純な二つの機能が中心から外れていた。

必要な機能は次の二つである。

1. Initiative / Epic / Issue を新規作成した時点で、その node 直下に `.workbench/` が自動生成される。
2. Workbench 内外を問わず、任意の regular file を指定した Initiative / Epic / Issue の `artifacts/` へ import できる。保存先 filename には runtime が Artifact 規約に合う prefix を自動付与する。

Workbench は独立した managed workspace product ではない。Git が管理するのは `.workbench/` の存在を表す tracked shell だけであり、配下の作業ファイルは Git 管理しない。したがって、複雑な retention、promotion、handoff、同期 lifecycle は主目的ではない。

```text
tracked node tree
└── <initiative|epic|issue>/
    ├── requirement.md
    ├── design.md
    ├── plan.md
    ├── report.md
    ├── artifacts/                 tracked
    └── .workbench/                directory shell is tracked
        ├── .gitkeep               tracked markerの一例
        └── arbitrary files...     ignored / worktree-local
```

Workbench 内の作業ファイルは worktree-local である。worktree を閉じて削除すれば、作業ファイルもその worktree と一緒に破棄される。それでよく、別 Workbench へ copy して延命することを標準 workflow にしてはならない。

ただしlinked worktree作成時、Git管理外のWorkbench contentsは新しいworktreeへ移らない。元のworktreeにあるcontentsがtarget worktreeでも必要な場合に限り、利用者が`workbench copy`を手動実行できる。この補助機能は自動実行、標準handoff、同期lifecycleではない。

## 2. ユーザーが確定したあるべき状態

### 2.1 Workbench の存在

- `new initiative`
- `new epic`
- `new issue`

これらの node 作成操作は、canonical files、`artifacts/`、metadata と同時に `.workbench/` の tracked shell を作る。

利用者が手作業で `mkdir` する必要はない。Workbench は追加機能ではなく、作成される node の標準構造の一部である。

fresh `spec-dock init` は、root/pre-scope `spec-dock/.workbench/` の tracked shellも作る。

ただしWorkbenchの存在はrepository validityの必須条件ではない。

- existing repositoryのrootは`update`でbackfill・変更しない。
- existing Initiative / Epic / Issueもmigrationしない。
- Workbenchがないscopeでも`validate`をpassできる。
- 利用者は必要に応じてmissing Workbenchを手動作成できる。
- 自動生成契約はfresh rootとfuture-created nodeにだけ適用する。

### 2.2 Git 管理境界

自動生成されるWorkbenchでGit管理するもの:

- `.workbench/` が存在することを保証する marker file
- Workbench の ignore contract

Git管理対象外:

- `.workbench/` 内に置かれた調査資料
- model output
- log
- image
- archive
- database
- source fragment
- その他の一時作業ファイル

Git は空 directory を追跡できないため、実装上は tracked marker が必要になる。候補は次のいずれかである。

- `.workbench/.gitkeep`
- `.workbench/.gitignore`

推奨する最小形は、fresh rootと各 node template に `.workbench/.gitkeep` を含め、managed ignore rule を次の意味へ変更することである。

```gitignore
# .workbench shell markerだけを追跡し、それ以外は無視する
**/.workbench/*
!**/.workbench/.gitkeep
```

実際の pattern は Git の platform matrix で検証する必要があるが、重要なのは「directory 全体を ignore」から「tracked shell を残して contents を ignore」へ契約を変えることである。

### 2.3 Workbench lifecycle

Workbench の lifecycle は次で十分である。

1. fresh initまたはfuture node作成時にshellを生成する。
2. worktree 内で自由に使う。
3. 必要な file だけを明示的に Artifact import する。
4. worktree を閉じると、import しなかった作業ファイルは worktree と一緒に破棄される。

必要ないもの:

- Workbench 間の自動または標準 copy / handoff
- branch 間の自動同期
- copy-back
- retention database
- TTL manager
- promotion state
- manifest
- catalog
- session管理
- Workbench 内容の Git commit

`workbench copy`はoptional manual helperとして残す。

- linked worktree作成時に自動実行しない。
- Workbench contentsが必要な場合だけ利用者が明示実行する。
- current worktreeのscope Workbenchをtarget linked worktreeの同scopeへone-shot copyする。
- sync、watch、copy-backは行わない。
- 通常はcopyせず、worktree-local contentsとして破棄する。

### 2.4 任意ファイルの Artifact import

必要な command surface の概念形:

```bash
./spec-dock/scripts/spec-dock artifact import file \
  --file <任意のregular-file-path> \
  --initiative <id>

./spec-dock/scripts/spec-dock artifact import file \
  --file <任意のregular-file-path> \
  --epic <id>

./spec-dock/scripts/spec-dock artifact import file \
  --file <任意のregular-file-path> \
  --issue <id>
```

source file は次のどこにあってもよい。

- target scope 自身の `.workbench/`
- 別 scope の `.workbench/`
- root Workbench
- repository 内の Workbench 外
- repository 外の利用者が明示指定した path

Workbench は便利な作業場所であり、import eligibility を制限する security boundary ではない。

repository外sourceにも追加flagを要求しない。利用者が`artifact import file --file <path>`を明示実行したこと自体をauthorization boundaryとする。external absolute pathは通常出力やtracked provenanceへ保存しない。

初期対象は「任意の regular file 一件」でよい。directory、glob、bulk、archive 展開は別 capability とする。

### 2.5 import 時の filename

caller に Artifact filename を手組みさせない。runtime が prefix を付ける。

採用する基本形:

```text
<ts>-<normalized-original-basename>
<ts>-<nn>-<normalized-original-basename>   # collision時
```

例:

```text
source: report.pdf
dest:   20260728t060000z-report.pdf

source: system-log.txt
dest:   20260728t060001z-system-log.txt

source: analysis.md
dest:   20260728t060002z-analysis.md
```

確定した要点:

- timestamp / collision prefix は runtime が自動生成する。
- original basenameとextensionは可能な限り維持する。
- basename はfilesystem/path safety上必要な箇所だけnormalizeする。
- source bytes は変更しない。
- source file は残す。copy-not-move とする。
- destination が存在する場合は overwrite せず、新しい prefix/suffix を割り当てる。
- `--title` や `--slug` を必須にしない。

既存 Artifact grammar は Markdown document family を前提としているため、non-Markdown regular file を正式な Artifact と認識する validator / naming contract は追加が必要である。ただし利用者から見た機能は「prefix が自動付与され、指定 scope の `artifacts/` に保存される」で一貫させる。

## 3. 現状

### 3.1 Workbench は自動生成されない

現行 node creation:

- `application/create_node.py::plan_node_creation`
- `application/create_node.py::execute_create_plan`
- `infra/template_scaffolder.py::copy_scaffolded_tree`

これらは `templates/{initiative,epic,issue}` の file と rules symlink、`.meta.json` を生成する。

現行 templates には `.workbench/` marker がない。

```text
templates/initiative/
  requirement.md
  design.md
  plan.md
  report.md

templates/epic/
  requirement.md
  design.md
  plan.md
  report.md

templates/issue/
  requirement.md
  design.md
  plan.md
  report.md
```

したがって `new initiative` / `new epic` / `new issue` の完了後にも `.workbench/` は存在しない。利用者が必要になった時点で手動作成する前提になっている。

これは今回確定した理想状態に対する主要な欠落である。

### 3.2 現行 ignore contract は directory shell まで無視する

現行 contract は `.workbench/` subtree 全体を Git-ignored reserved boundary として扱う。

この形では、Workbench 内の作業ファイルだけでなく、directory の存在を保証する marker も通常の Git 操作では追跡されない。

つまり現行設計は次の状態である。

```text
.workbench/ があれば中身を無視する
```

必要な状態は次である。

```text
.workbench/ の存在はGitで配布する
.workbench/ の作業内容だけを無視する
```

この違いが、自動生成されない問題と branch/worktree で存在が保証されない問題の根にある。

### 3.3 `workbench copy` に重点が置かれている

現行 Epic は、scope-local Workbench を linked worktree 間で one-shot copy する `workbench copy` を主要機能として設計した。

現行挙動:

- source Workbench が必要
- target Workbench は必要に応じて作る
- source-wins merge
- destination-only file は残す
- copy-back / sync はしない

これは「既に作った ignored contents を別 worktree でも必要な場合に限り手動で受け渡す」問題を解く。この限定用途には引き続き必要である。

必要なのは:

- 各 node に Workbench shell が最初から存在する
- contents はその worktree だけで使う
- 残したい file だけ Artifact import する
- worktree 終了時に残りを破棄する

したがって問題はcommandの存在ではなく、これをWorkbenchの主要lifecycleとして扱ったことにある。

### 3.4 Artifact import は限定されすぎている

現行 `artifact import chatgpt-output`:

- import kind は `chatgpt-output` 一種類だけ
- source は approved Workbench 配下だけ
- single file
- exact lowercase `.md` だけ
- regular non-symlink file
- title 必須
- slug は title または `--slug` から生成
- destination は blank Markdown Artifact
- filename slug に `chatgpt-output-` を付与

拒否されるもの:

- Workbench 外の file
- repository 外の file
- `.txt`
- `.json`
- `.pdf`
- `.png`
- extensionなし file
- その他の non-Markdown regular file

この command は「ChatGPT Markdown 原文を保存する」狭い用途には動作する。しかし「任意の file を特定 scope の Artifact として取り込む」という必要機能ではない。

### 3.5 prefix 自動付与は部分的に存在するが汎用でない

現行 import も timestamp と `chatgpt-output-<slug>` を自動生成する。この点だけを見れば prefix allocator は存在する。

不足しているのは次である。

- generic file import から同じ allocator を使えない
- original basename / extension を保持する汎用規則がない
- non-Markdown destination を Artifact として認識できない
- Workbench 外 source を guard が拒否する
- `--title` が必須で、単純な file capture になっていない

したがって「prefix 機能が全くない」のではなく、「ChatGPT Markdown 専用経路に閉じ込められ、必要な汎用 import から利用できない」が正確である。

## 4. 理想状態と現状のギャップ

| 項目 | あるべき状態 | 現状 | ギャップ |
|---|---|---|---|
| Initiative 作成 | `.workbench/` shellを自動生成 | 生成しない | template/scaffold欠落 |
| Epic 作成 | `.workbench/` shellを自動生成 | 生成しない | template/scaffold欠落 |
| Issue 作成 | `.workbench/` shellを自動生成 | 生成しない | template/scaffold欠落 |
| Git 管理 | shell/markerのみtracked | directory全体ignored | ignore contractが逆 |
| Workbench contents | ignored、worktree-local | ignored | この点は一致 |
| worktree close | 未import contentsを破棄 | remove時に消せるが、handoff機能を強調 | lifecycleモデルが過剰 |
| branch/worktree間 | shellはGitで存在、contentsは通常移さない。必要時だけmanual copy | `workbench copy`で明示one-shot copy可能 | 機能は再利用し、位置づけだけ補助へ変更 |
| import source | 任意のregular file | approved Workbench内の`.md`のみ | source guardが狭すぎる |
| import destination | 任意のInitiative/Epic/Issue | Initiative/Epic/Issue | 一致 |
| file form | Markdown/non-Markdown | lowercase `.md`のみ | generic binary/file contract欠落 |
| filename prefix | runtimeが自動付与 | ChatGPT Markdownだけ自動付与 | allocatorの汎用化欠落 |
| original extension | 維持 | `.md`固定 | non-Markdown naming欠落 |
| title/slug | 原則不要、optional override | title必須 | unnecessary friction |
| source preservation | copy-not-move | copy-not-move | 一致 |
| overwrite | 禁止、collision allocation | 禁止、collision allocation | 再利用可能 |
| byte preservation | 必須 | 実装済み | 再利用可能 |
| canonical authority | importだけでは付与しない | evidence-only | 一致 |

## 5. あるべき最小実装

### 5.1 Workbench shell

1. fresh rootとInitiative/Epic/Issue templatesへtracked markerを追加する。
2. node creation planのplanned pathsにmarkerを含める。
3. managed ignore ruleを「directory全体ignore」から「contents ignore、marker allow」へ変更する。
4. fresh init / new nodeのprovider-consumer parityを確認する。
5. `update`がexisting root/nodeをbackfill・変更しないことを確認する。

候補構造:

```text
templates/initiative/.workbench/.gitkeep
templates/epic/.workbench/.gitkeep
templates/issue/.workbench/.gitkeep
```

### 5.2 Generic file import

1. `artifact import file` commandを追加する。
2. exactly one Initiative/Epic/Issueをtargetとする。
3. sourceは任意のreadable regular fileとする。
4. symlink、directory、FIFO、socket、deviceは初期版でrejectする。
5. source pathがWorkbench内かどうかを要件にしない。
6. existing binary publisherのbyte preservation、source stability、no-replace、hash、byte countを再利用する。
7. destination filenameはruntimeが生成する。
8. original basenameをnormalizeし、extensionを維持する。
9. sourceは削除しない。
10. import結果はsource/destination、SHA-256、byte count、committed stateをcontent-freeで返す。

### 5.3 既存commandの位置づけ

`artifact import chatgpt-output`:

- compatibility presetとして残せる
- 内部的にはgeneric file importへ委譲できる
- `.md`、`chatgpt-output-` naming、title/slug semanticsを既存互換として維持する

`workbench copy`:

- optional manual helperとして残す
- headline workflowから外す
- worktree create時に自動実行しない
- 必要時だけcurrent worktreeからtarget linked worktreeへone-shot copyする
- 「Workbenchの標準lifecycle」にはしない
- sync / watch / copy-backは追加しない

## 6. 受け入れ条件

### 6.1 Workbench

- fresh `init`の成功後、rootにtracked `.workbench/` shellが存在する。
- `new initiative` の成功後、node直下に tracked `.workbench/` shellが存在する。
- `new epic` の成功後、node直下に tracked `.workbench/` shellが存在する。
- `new issue` の成功後、node直下に tracked `.workbench/` shellが存在する。
- 自動生成済みshellはfresh clone / checkout / linked worktreeでも存在する。
- `.workbench/` 内に作成した任意fileは`git status`に出ない。
- markerはGit trackedである。
- existing root/nodeは`update`でbackfill・変更しない。
- `.workbench/`がないexisting scopeもvalidである。
- 利用者がmissing `.workbench/`を作成できる。
- `validate` / sync / discoveryはWorkbench contentsを読まない。
- worktree remove時、Workbench contentsは別worktreeへcopyされず、対象worktreeとともに消える。
- linked worktree作成時、Workbench contentsは自動copyされない。
- 利用者が明示実行した場合だけ`workbench copy`でscope contentsをtargetへcopyできる。

### 6.2 Artifact import

- Workbench内のMarkdownを任意scopeへimportできる。
- Workbench内のnon-Markdownを任意scopeへimportできる。
- Workbench外かつrepository内のfileを任意scopeへimportできる。
- repository外の明示fileを任意scopeへimportできる。
- source extensionがdestinationで維持される。
- destinationにArtifact規約準拠prefixが自動付与される。
- source bytesとdestination bytesが一致する。
- source fileが残る。
- existing destinationをoverwriteしない。
- same-second collision時に自動suffixを割り当てる。
- source symlink、directory、special fileをwrite前にrejectする。
- importでcanonical docsや`report.md`を自動変更しない。

## 7. 現在の再評価

この問題の中心は、Workbench の高度な lifecycle が不足していることではない。

中心問題は次の三点である。

1. Workbench shell が node scaffold の標準構造になっていない。
2. Git ignore contract が「shellを追跡しcontentsだけを無視する」形になっていない。
3. Artifact import が任意file captureではなく、approved Workbench内のChatGPT Markdown専用機能になっている。

現在実装済みの次の部品は再利用価値がある。

- `.workbench` traversal opacity
- byte-preserving copy
- source stability checks
- symlink rejection
- no-overwrite publication
- timestamp/collision allocation
- scope-local `artifacts/` resolution
- content-free result

したがって全面作り直しではなく、誤って狭めた入口とnode scaffoldを修正すればよい。

## 8. 未確定事項

blocking なユーザー意図の不明点はない。

実装設計で確定が必要な細部:

1. tracked markerを `.gitkeep` とするか `.gitignore` とするか。
2. non-Markdownをvalidator上で認識するgeneric imported-file familyの表現。
3. minimum safety normalizationのplatform別文字規則。
4. external sourceのabsolute pathをresultに表示せず、どのsafe labelをprovenanceに残すか。

いずれも target state を変える論点ではなく、requirement/designで決める実装詳細である。

## 9. 調査根拠

### ユーザー意図

- 2026-07-28 clarification:
  - fresh rootと新規 Initiative/Epic/IssueにWorkbenchを自動配置する。
  - existing root/nodeは変更しない。
  - Workbenchの存在は必須ではなく、なければ手動作成できる。
  - Workbenchをbranch/worktree間で移動・受け渡しすることを中心にしない。
  - linked worktreeで元のWorkbench contentsが必要な場合だけ、`workbench copy`を手動実行できる補助機能として残す。
  - worktree作成時に`workbench copy`を自動実行しない。
  - Workbench directoryはGit管理し、contentsはGit管理しない。
  - worktreeを閉じればcontentsは破棄される。
  - Workbench内外の任意fileを任意scopeのArtifactとしてimportする。
  - repository外の明示fileも追加flagなしで許可する。
  - external absolute pathは通常出力やtracked provenanceへ保存しない。
  - filename prefixはruntimeが規約に合わせて自動付与する。
  - prefix後はoriginal basename/extensionを可能な限り保持し、safety上必要な箇所だけnormalizeする。
  - importにtitle/slugを必須としない。

### canonical Epic

- `requirement.md`
  - root/scoped `.workbench/` placement
  - manual creation
  - scope Workbench copy
  - approved Workbench内single `.md` import
- `design.md`
  - `workbench copy` architecture
  - `artifact import chatgpt-output`
- `plan.md`
  - Workbench copyをW2、ChatGPT Markdown importをW4として実装

### current implementation

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py`
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workbench.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`

### tests

- `tests/unit/application/test_workbench.py`
- `tests/cli_runtime/test_workbench.py`
- `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
- `tests/unit/infra/test_binary_artifact_publisher.py`
- `tests/cli_runtime/test_worktree.py`

## 10. 反映先

mode: `analysis-only`

この Artifact は target state の再整理であり、まだ canonical adoption ではない。

後続 authoring では少なくとも次を更新する必要がある。

- Epic requirement: Workbench tracked shell、automatic scaffold、generic file import
- Epic design: ignore layout、node creation integration、generic publisher/naming
- Epic plan: copy-centered decompositionからscaffold/import-centered decompositionへの変更
- Epic report: 前回evidenceの部分採用/棄却、本Artifactのadoption decision
- ADR: non-Markdown Artifact naming familyが長期互換性を持つ場合のみ作成
