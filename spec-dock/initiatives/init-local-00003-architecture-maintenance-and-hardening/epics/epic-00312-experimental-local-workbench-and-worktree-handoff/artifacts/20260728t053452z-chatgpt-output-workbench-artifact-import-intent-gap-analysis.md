# epic-00312 Workbench / Artifact import 意図差分調査

## 文書メタデータ

* **文書名**: `epic-00312-workbench-artifact-import-intent-gap-analysis.md`
* **対象 repository**: `chemitaro/spec-dock`
* **調査 ref**: `epic-00312-experimental-local-workbench-and-worktree-handoff`
* **調査 HEAD**: `3ee6d9047506a40b938407ecfffbb341a3ca76af`
* **default branch**: `main`
* **ref 関係**: 調査時点で current branch と `main` は同一 commit
* **調査日**: 2026-07-28
* **権限**: evidence-only research
* **変更**: repository 変更、patch 作成、canonical 文書更新、Issue / PR 操作は行っていない
* **禁止する自己主張**: canonical adoption、reviewer pass、execution-ready、PR-ready、merge-ready、Issue finish、Epic completion を本書は主張しない

本書の「確認済み」は、GitHub connector で当該 ref のファイルまたは GitHub object を読み取ったことを意味する。テストコードは確認したが、この調査セッションではテストを実行していない。PR 本文や report に記載された過去の test pass は historical evidence であり、本調査による独立再実行結果ではない。

---

## 1. 調査結論

### 1.1 結論

現在の Workbench と `artifact import chatgpt-output` は、**現在の狭い canonical Epic 契約には概ね適合しており、中核実装の明白な defect は確認できなかった**。一方、現在の仕組みは、利用者が今後必要としている次の end-to-end 体験を満たさない。

```text
任意の作業ファイル
  ├─ Workbench 内
  ├─ repository 内だが Workbench 外
  └─ repository 外の明示指定 file
          ↓
安全な explicit import
          ↓
scope-local artifacts/
          ↓
EAL で provenance / 採否
          ↓
必要な規範だけ canonical docs へ再記述
```

現在提供される永続化経路は、次に限定される。

```text
current worktree の approved .workbench/
  └─ lowercase ".md" suffix の single regular non-symlink file
          ↓
artifact import chatgpt-output
          ↓
blank Artifact identity の .md
```

したがって主要な差分は、実装が current contract から外れていることではなく、**current contract 自体が「完成済み ChatGPT Markdown 原文保存」に狭く固定され、汎用的な scope-local file capture へ進んでいないこと**である。

### 1.2 「当初意図」の正確な整理

「当初の product intent は任意 file の Artifact import だった」と断定するのは証拠に反する。強い証拠からは、次の二段階を区別すべきである。

1. **Workbench の当初意図は広い**
   Workbench は image、binary、archive、設定 file、program、巨大 log、未整理資料を形式不問で置く低摩擦 scratch であり、scope-local Workbench の worktree handoff も内容分類なしで行う意図だった。

2. **Artifact import の起点は狭い**
   後から追加された import decision の直接目的は、Codex が要約・再構成する前に「完成済み ChatGPT Markdown report」の原文を保存することだった。MVP は最初から single Markdown に限定され、PDF、image、ZIP、directory、multi-file bundle は future-only とされた。

よって現在の「Workbench 内外の一般 file を実用的に Artifact 化したい」という要求は、既存 Epic の未実装 requirement というより、**Workbench の広い利用実態から自然に生じた未充足 capability、または過去に deferred された export/import 方向の再評価**と位置づけるのが正確である。

### 1.3 defect と limitation の総括

| 判定                                             | 結論                                                                                                                           |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| implementation defect                          | 調査対象の中核動作について確認済み defect は 0 件                                                                                               |
| contract/documentation inconsistency           | full/non-local scope ID 制約の Epic requirement 上の明示不足、root date bucket 表記の揺れ、stale な Epic report がある                           |
| intentional limitation now judged insufficient | manual Workbench creation、root no-handoff、single lowercase `.md`、approved Workbench-only source、no directory/bundle/bulk が該当 |
| missing product capability                     | generic single-file import、outside-Workbench source、formal non-Markdown Artifact identity、optional bundle import が該当         |
| lifecycle/closeout residue                     | PR #323 と Issue #319 の実状態に対して `report.md` が古い。Epic #312 だけが open                                                             |

### 1.4 推奨 target state

最も単純で安全な target state は、既存実装を破棄せず次へ拡張することである。

1. `artifact import chatgpt-output` は compatibility-preserving preset として残す。
2. 独立した generic single-file use case、候補名 `artifact import file` を追加する。
3. source を `workbench`、`repo-local`、明示 opt-in の `external` に分類し、各 source zone の path / provenance policy を固定する。
4. Markdown は既存 blank `.md` grammar を再利用できる。
5. non-Markdown は「unrelated file」を Artifact と偽装せず、既存 `artifacts/` 内の import-only opaque-file identity と naming / validator contract を新 ADR で定義する。
6. copy-not-move、source stability、same-directory staging、SHA-256、byte count、atomic no-replace、content-free output、EAL authority boundary は現行実装を再利用する。
7. directory / bundle は後段の別 slice とし、manifest、payload tree、atomic publish、entry/byte limits を明示する。
8. ZIP/tree authoring pack は generic import に流さず、既存 quarantine / review / stage lane を維持する。
9. automatic promotion、glob-based bulk import、canonical/EAL 自動編集、in-place update/overwrite は導入しない。
10. PR #323 merged 後の broader capability は current Epic 00312 を黙って再定義せず、follow-up Epic / accepted ADR で扱う。

---

## 2. 調査対象と証拠の優先順位

### 2.1 GitHub ref の確認

GitHub connector で次を確認した。

* repository `chemitaro/spec-dock` はアクセス可能。
* current branch `epic-00312-experimental-local-workbench-and-worktree-handoff` の file を直接取得できた。
* current branch と `main` の compare は `identical`。
* 両 ref の HEAD は `3ee6d9047506a40b938407ecfffbb341a3ca76af`。
* PR #323 は merged。
* child Issues #315、#316、#317、#318、#319 は closed。
* Epic #312 は open。

### 2.2 証拠の優先順位

本書では、衝突時に次の順で強い証拠として扱った。

1. **current GitHub ref の accepted canonical contract**

   * `requirement.md`
   * `design.md`
   * `plan.md`
   * accepted ADR
2. **current GitHub ref の implementation**

   * provider authority `src/spec_dock/assets/spec_dock/**`
3. **current GitHub ref の tests**

   * unit / CLI runtime / infra / opacity tests
4. **current public docs**

   * guide / reference / workflow / authoring pack
5. **adopted historical evidence**

   * product-owner interviews
   * clarification synthesis
   * EAL disposition
6. **proposal / research evidence**

   * early ChatGPT analyses、decision candidate
7. **lifecycle report の observed-state 記述**

   * GitHub object の actual state と衝突する場合は GitHub actual state を優先
8. **添付 preflight receipt**

   * supplementary。GitHub connector の current observation を代替しない

### 2.3 証拠衝突

主な衝突は lifecycle である。

* GitHub actual state:

  * PR #323 merged
  * #319 closed
  * #312 open
* current `report.md`:

  * PR #323 ready/open/unmerged
  * #319 open
  * external observation pending

この衝突では GitHub actual state が強い。`report.md` は stale closeout residue と判定する。

### 2.4 仮定

* 「practical import」は、file の内容を canonical 化することではなく、scope-local `artifacts/` へ durable evidence として保存することを指す。
* non-Markdown file も filename だけでなく runtime が formal Artifact と認識できる必要がある。
* existing ZIP/tree authoring-pack safety lane は変更対象ではない。
* source file は成功後も残す copy-not-move を既定とする。
* imported Artifact は immutable append-only に近い運用とし、再 import は新規 Artifact を作る。

### 2.5 不確実性と未検証主張

* 本調査では test suite を実行していない。
* Windows、macOS、Linux 各 platform の実 filesystem behavior は再実証していない。
* Artifact import の local-ID destination は code path 上は `resolve_id_input` を通るため対応していると推定できるが、確認した import tests には local-ID 専用 case が見当たらなかった。
* current branch と `main` が identical であることは調査時点の observation であり、後続変更を保証しない。
* broader generic import の需要頻度、対象 file サイズ、extension 分布、directory/bundle の実 corpus は提示されていない。

---

## 3. 当初目指していた利用体験

### 3.1 root scope の問題

scope が未確定の調査段階では、資料を Initiative / Epic / Issue のどこへ置くか決められない。OS temporary directory だけでは repository と作業文脈の対応が弱く、worktree 分岐後にも見失いやすい。

そのため root/pre-scope Workbench は次の役割を持つ。

```text
spec-dock/.workbench/YYYY-MM-DD/
```

* scope 作成前の横断調査
* download file
* screenshot
* temporary database
* model output
* diff
* config
* archive
* rough note
* 比較用 material
* 後で捨ててよい未整理物

ここでは構造、manifest、session、TTL、retention、promotion state を持たず、人間または model が必要な file だけを選ぶ。

### 3.2 Initiative / Epic / Issue scope の問題

scope が確定した後は、対象 node の direct child `.workbench/` に一時資料を置く。

```text
<initiative>/.workbench/
<epic>/.workbench/
<issue>/.workbench/
```

目的は、canonical documents と同じ tree の近くに作業文脈を置きながら、default scanner が意味解釈しないことにある。

* fake `.meta.json` を node と誤認しない
* `meta.json` を legacy node と誤認しない
* ADR-like Markdown を accepted ADR と誤認しない
* dependency-like data を dependency と誤認しない
* authoring source manifest に混入しない
* scratch size に比例して default discovery が遅くならない

### 3.3 worktree handoff の問題

Git-ignored file は linked worktree 作成では移らない。scope-local Workbench の意図は、利用者が明示したときだけ current worktree から同一 repository の別 linked worktree へ、一回の snapshot として引き継ぐことだった。

```text
source scope .workbench/
          ↓ explicit one-shot copy
target scope .workbench/
```

重要な意味は次である。

* source は current worktree
* target は same-repository linked worktree
* source / target scope は同じ ID を独立解決
* destination-only entry は残す
* same-relative-path は source wins
* sync / watcher / copy-back はない
* file language、extension、MIME、content を分類しない

### 3.4 Workbench、Artifact、canonical docs の関係

狙われた responsibility boundary は次である。

| Surface                                    | 性質                                          |               Git | authority                | lifecycle                       |
| ------------------------------------------ | ------------------------------------------- | ----------------: | ------------------------ | ------------------------------- |
| `.workbench/`                              | scratch、雑、未整理                               |           ignored | none                     | scope/worktree と共に消えてよい         |
| `artifacts/`                               | durable evidence、draft、research、raw capture |           tracked | evidence-only by default | commit / review可能               |
| `requirement.md` / `design.md` / `plan.md` | normative specification                     |           tracked | canonical                | main orchestrator single-writer |
| accepted ADR                               | long-lived decision                         |           tracked | accepted authority       | review / adoption gate          |
| `report.md` EAL                            | evidence 採否と lifecycle observation          |           tracked | adoption record          | actual observation を更新          |
| external quarantine                        | raw ZIP/tree の安全確認                          | repository 外または隔離 | none until staged        | review / quarantine / stage     |

この関係では、「Workbench から Artifact へ保存」と「Artifact の claim を canonical に採用」は別操作である。

### 3.5 Artifact import が解こうとした原問題

Artifact import の decision candidate が直接扱った問題は、完成済み ChatGPT report を Codex が要約すると、原文の構造、詳細、説明力、洞察が失われることだった。

そのため追加された checkpoint は次である。

```text
complete ChatGPT Markdown
          ↓ byte-preserving import
scope-local Artifact
          ↓ EAL disposition
canonical rewrite
          ↓ fresh reviewer
```

ここでは single Markdown が意図的に採用され、PDF、image、ZIP、directory、bundle は future-only とされた。

### 3.6 broader aspiration と採用済み requirement の境界

次は historical aspiration または自然な利用期待として読み取れる。

* Workbench に任意 file を置ける。
* Workbench から必要な file を durable evidence にしたい。
* root / scope / outside source から一貫した capture がほしい。
* file を別場所へ一度 copy してからでないと import できない friction を減らしたい。

ただし次は accepted original requirement ではない。

* arbitrary host path import
* non-Markdown formal Artifact
* directory import
* bulk import
* bundle manifest
* automatic promotion

この差を明示しないと、「実装 defect」と「新しい product capability」を混同する。

---

## 4. canonical Epicで確定した狭い契約

### 4.1 Workbench contract

canonical Epic は Workbench を次に固定した。

* exact path component `.workbench`
* Git-ignored
* non-canonical
* disposable
* no schema / manifest / catalog / session / TTL
* default semantic discovery から prune
* manual filesystem placement
* root Workbench は runtime management 対象外
* scope Workbench だけ explicit one-shot handoff
* no automatic sync / copy-back
* no content classifier
* no second store

### 4.2 Artifact import contract

accepted ADR と canonical Epic は import を次へ限定した。

| 項目                       | current contract                                      |
| ------------------------ | ----------------------------------------------------- |
| command                  | `artifact import chatgpt-output`                      |
| trigger                  | explicit only                                         |
| import kind              | `chatgpt-output`                                      |
| storage identity         | existing blank Artifact                               |
| source worktree          | current worktree                                      |
| source roots             | root または resolved Initiative/Epic/Issue `.workbench/` |
| source count             | exactly one                                           |
| source kind              | regular non-symlink file                              |
| suffix                   | exact lowercase `.md`                                 |
| source ancestor          | symlink 不可                                            |
| content                  | opaque bytes。UTF-8 / Markdown parse なし                |
| destination              | selected Initiative/Epic/Issue `artifacts/`           |
| mutation                 | copy-not-move。source を残す                              |
| publish                  | temp、hash、source stability、fsync、no-replace           |
| collision                | existing blank timestamp / suffix allocation          |
| provenance               | command result + EAL                                  |
| authority                | evidence-only                                         |
| automatic canonical edit | なし                                                    |
| outside Workbench        | reject                                                |
| PDF / image / ZIP        | non-goal                                              |
| directory / multi-file   | non-goal                                              |
| bulk                     | non-goal                                              |
| auto promotion           | non-goal                                              |

### 4.3 狭められた論点と理由

#### manual Workbench creation

`E-RQ-002` は root date bucket の作成、列挙、検証、期限管理、削除を runtime が担わないと固定する。CLI parser に `workbench create` / `ensure` はない。

**理由**: Workbench を managed workspace product にしないため。

**現在の評価**: 安全な非管理境界として合理的だが、初回利用 friction は残る。

#### root Workbench without bulk handoff

root は雑多で不要物を含む前提とされ、root copy route は明示的に棄却された。必要 file は model / human が通常 filesystem 操作で選ぶ。

**理由**: root 全体の accidental copy、root path grammar、session-like management の肥大化を避ける。

**現在の評価**: intentional limitation。generic file import があれば root handoff command を追加せずに friction を軽減できる。

#### scope copy requiring a published/non-local full ID

`application/workbench.py::_validate_scope_id` は `init|epic|iss` の full ID を要求し、`is_local` を拒否する。CLI tests は `init-local-00003` と numeric shorthand を明示的に reject する。

**理由として推定できること**: 親 Initiative は local-only node identity を廃止対象としており、新 command を published/non-local node に限定した。

**contract gap**: Epic `E-RQ-006` 本文は「Initiative / Epic / Issue ID」と書くが、non-local/full-only を同じ明瞭さでは述べていない。public docs、implementation、tests の方が強い。

#### a single lowercase `.md` regular file

source guard は `Path.suffix == ".md"` を exact check する。`.MD` は reject test で固定される。

**理由**: ChatGPT completed report の narrow MVP だったため。

**現在の評価**: content は opaque で invalid UTF-8 や NUL も受け付けるため、実質的には「Markdown content」ではなく「`.md` と名づけられた opaque regular file」である。これは security classifier ではなく interface gate である。

#### approved Workbench sources only

approved roots は current repository の root `.workbench/` と graph から解決した Initiative/Epic/Issue direct child `.workbench/` である。

**理由**: source containment、provenance、symlink ancestry、current worktree boundary を単純に固定するため。

**現在の評価**: source safety は強いが、download path や repository 内の既存 file を一度 Workbench へ copy する余分な操作が必要。

#### `chatgpt-output` import kind with blank storage identity

accepted ADR は typed token / prefix reservationを棄却し、`chatgpt-output` を operation kind、stored file を blank identity とした。

**理由**:

* existing blank grammar を壊さない
* `new artifact blank --slug chatgpt-output-*` と共存
* body を変更しない
* sidecar / catalog を作らない

**現在の評価**: compatibility は高いが、filename だけでは creation route / provenance を識別できない。generic import へ広げる場合は storage identity の再検討が必要。

#### no outside-Workbench source

Workbench 外 path は pre-publish reject。

**理由**: arbitrary host path access、absolute path leakage、source boundary の複雑化を避ける。

**現在の評価**: product friction の主要因。明示 external source policy が欠落している。

#### no arbitrary binary / directory / bundle import

binary bytes 自体は `.md` file 内なら許容されるが、non-`.md` regular file、directory、bundle は非対応。

**理由**: Artifact naming / validator / template contract を変更せず、single-file atomic publish に限定するため。

**現在の評価**: Workbench は arbitrary file を持てるのに、durable evidence lane は suffix で閉じるため、workflow discontinuity がある。

#### no bulk import

glob、recursive import、multi-file transaction はない。

**理由**: no-overwrite、source stability、failure atomicity、provenance を一件に限定するため。

**現在の評価**: initial safety boundary として妥当。directory/bundle requirement が実証されるまでは、generic bulk より manifest-driven bundle を優先すべき。

#### no automatic promotion

import は EAL、canonical docs、ADR、assurance state を編集しない。

**理由**: evidence 保存と canonical adoption を分離するため。

**現在の評価**: この制限は維持すべきであり、product inadequacy ではない。

---

## 5. 現在の実装とテスト

### 5.1 Workbench copy implementation

主要 flow は `application/workbench.py::workbench_copy` にある。

1. ports / current repository context を確認
2. scope ID を normalize / validate
3. Git worktree inventory から current source と target を解決
4. target current / bare / missing を reject
5. source / target `spec-dock/` ancestry を guard
6. metadata inventory を `.workbench` prune 前提で guard
7. source / target scope ID を独立解決
8. direct child `.workbench/` を解決
9. source missing、malformed root、symlink ancestry を reject
10. filesystem gateway で descriptor-relative merge
11. failure は `mutation_started` を含む content-free error
12. success は target Workbench path を返す

`infra/fs_cli.py` は regular file、directory、symlink object を扱い、symlink target を dereference しない。directory/non-directory collision と unsupported special entry は copy failure とする。これは canonical の「semantic filtering をしないが、standard filesystem operation が処理できない場合は failure」に適合する。

### 5.2 Artifact import implementation

主要 flow は `application/import_artifact.py::import_artifact` にある。

1. runtime ports を確認
2. import kind が `chatgpt-output` だけであることを確認
3. destination scope を既存 graph / resolver で解決
4. title / slug を normalize
5. source guard request を作成
6. approved Workbench source を preflight
7. destination `artifacts/` と timestamp を決定
8. existing artifact create lock を取得
9. blank Artifact destination を allocate
10. publisher で stage / verify / no-replace publish
11. `EEXIST` は bounded reallocation
12. repo-relative source / destination、SHA-256、byte count、commit / warning を返す
13. source、EAL、canonical docs は変更しない

### 5.3 Source guard と publication safety

`FilesystemBinaryArtifactPublisher` は次を実装する。

* exact `.md` suffix
* approved root containment
* source / ancestor symlink rejection
* regular file check
* descriptor identity check
* chunked binary copy
* source / stream / staged hash
* byte count
* source mutation / replacement / unlink detection
* destination same-directory temp
* file fsync
* atomic no-replace publication
* directory fsync warning
* post-publish destination confirmation
* owned temp cleanup
* source survival
* content-free error

### 5.4 CLI surface

current parser にある Workbench / Artifact import command は次だけである。

```text
workbench copy --scope <full-id> --to <target> [--json]

artifact import chatgpt-output
  (--initiative|--epic|--issue <id>)
  --file <approved-workbench-file.md>
  --title <title>
  [--slug <slug>]
  [--json]
```

存在しないもの:

```text
workbench create
workbench ensure
workbench list
workbench copy-root
artifact import file
artifact import directory
artifact import bundle
artifact import --from-external
artifact import --glob
artifact promote
```

### 5.5 tests が固定している behavior

#### Workbench

* source / target scope の independent resolution
* source と target の slug/path 差
* local/full/numeric ID rejection
* missing / ambiguous / malformed scope
* same/current / bare / missing target
* source Workbench missing は no target mutation
* empty Workbench success
* root symlink / malformed root rejection
* source-wins
* destination-only preservation
* fake metadata / ADR / dependency opacity
* content-free output
* no `--from` / `--root` / `--date` / `--path`

#### Artifact import

* LF / CRLF / BOM / no-final-newline
* Japanese
* NUL
* invalid UTF-8
* empty file
* secret-like bytes
* root Workbench source
* blank identity
* SHA-256 / byte count
* source survival
* outside source rejection
* uppercase `.MD` rejection
* directory / symlink / ancestor symlink / FIFO rejection
* new blank Artifact との collision coexistence
* import vs import / import vs new concurrency
* EEXIST rescan
* suffix exhaustion
* source mutation / replace / unlink
* hash mismatch
* temp / write / fsync / publication failure
* committed-with-warning
* no ADR mirror / projection impact

### 5.6 current canonical contract への適合

| Contract                                | 実装 / test evidence                                                  | 判定 |
| --------------------------------------- | ------------------------------------------------------------------- | -- |
| exact `.workbench` opacity              | walker prune、source manifest rejection、near-name preservation tests | 適合 |
| Git ignore                              | managed `.gitignore` に `.workbench/`                                | 適合 |
| manual root convention                  | create/list command なし                                              | 適合 |
| root handoff exclusion                  | parser optionsなし、tests reject                                       | 適合 |
| current source + one scope + one target | `workbench_copy` request                                            | 適合 |
| independent scope resolution            | source / target node recordsを別に load                                | 適合 |
| unfiltered Workbench copy               | file/dir/symlink、content classifierなし                               | 適合 |
| source-wins / destination-only preserve | descriptor merge + tests                                            | 適合 |
| no sync / copy-back                     | command / docs / output                                             | 適合 |
| single `.md` Workbench import           | source guard exact check                                            | 適合 |
| byte preservation                       | binary copy / multi-hash tests                                      | 適合 |
| source survival                         | copy-not-move tests                                                 | 適合 |
| no-overwrite                            | allocator + no-replace + collision tests                            | 適合 |
| blank coexistence                       | accepted ADR + tests                                                | 適合 |
| no automatic authority                  | command resultのみ、docs / EAL boundary                                | 適合 |
| ZIP/tree separate lane                  | authoring pack docs                                                 | 適合 |

### 5.7 確認できた actual defect

**中核 behavior の actual implementation defect は確認できなかった。**

ただし、次は defect と断定しないが follow-up review に値する。

* `commands/artifact_import.py` は unexpected `Exception` を `runtime_failed` に変換するため、operator-visible diagnostics が限定される。content-free security には寄与するが、internal observability は別途確認が必要。
* external source、non-Markdown、bundle を追加する場合、現在の guard / publisher をそのまま generalize すると source-zone policy と naming identity が曖昧になる。既存関数への option flag の追加だけで済ませるべきではない。

---

## 6. scope別機能マトリクス

### 6.1 current behavior matrix

| 観点                             | Root / pre-scope                                          | Initiative                                          | Epic                        | Issue                       |
| ------------------------------ | --------------------------------------------------------- | --------------------------------------------------- | --------------------------- | --------------------------- |
| Workbench placement            | `spec-dock/.workbench/YYYY-MM-DD/` convention             | direct child `.workbench/`                          | direct child `.workbench/`  | direct child `.workbench/`  |
| Workbench creation             | manual filesystem operation                               | manual filesystem operation                         | manual filesystem operation | manual filesystem operation |
| runtime-managed date / catalog | なし                                                        | なし                                                  | なし                          | なし                          |
| Git ignore                     | exact `.workbench/` rule                                  | 同左                                                  | 同左                          | 同左                          |
| traversal opacity              | exact component を prune                                   | 同左                                                  | 同左                          | 同左                          |
| worktree handoff               | command 非対応。必要 file を手動選択                                 | `workbench copy`                                    | `workbench copy`            | `workbench copy`            |
| handoff source                 | current worktree                                          | current worktree                                    | current worktree            | current worktree            |
| handoff target                 | n/a                                                       | same-repo linked worktree                           | same-repo linked worktree   | same-repo linked worktree   |
| scope resolution               | n/a                                                       | source / target で ID 独立解決                           | 同左                          | 同左                          |
| local-ID handoff               | n/a                                                       | rejected                                            | rejected                    | rejected                    |
| numeric shorthand handoff      | n/a                                                       | rejected                                            | rejected                    | rejected                    |
| import source eligibility      | approved source。single lowercase `.md` regular file       | approved source。single lowercase `.md` regular file | 同左                          | 同左                          |
| source と destination scope の一致 | 必須ではない                                                    | 必須ではない                                              | 必須ではない                      | 必須ではない                      |
| Artifact destination           | root Artifact destination はない。別 scope を指定                 | `<initiative>/artifacts/`                           | `<epic>/artifacts/`         | `<issue>/artifacts/`        |
| destination local-ID           | n/a                                                       | code path 上は resolver 対応と推定                         | 同左                          | 同左                          |
| Workbench 内 file forms         | arbitrary names / bytes。copy時は regular/dir/symlink object | 同左                                                  | 同左                          | 同左                          |
| Artifact import file forms     | one regular non-symlink `.md`                             | 同左                                                  | 同左                          | 同左                          |
| invalid UTF-8 / NUL            | `.md` suffixなら保存可能                                        | 同左                                                  | 同左                          | 同左                          |
| non-`.md` regular file import  | 不可                                                        | 不可                                                  | 不可                          | 不可                          |
| directory / bundle import      | 不可                                                        | 不可                                                  | 不可                          | 不可                          |
| source preservation            | import成功/失敗で source を削除しない                                | 同左                                                  | 同左                          | 同左                          |
| destination preservation       | importはno-overwrite。copyはsame-path source-wins            | 同左                                                  | 同左                          | 同左                          |
| update behavior                | `spec-dock update` は Workbench content を保持                | 同左                                                  | 同左                          | 同左                          |
| deletion behavior              | worktree削除で消失可                                            | scope/worktree削除で消失可                                | 同左                          | 同左                          |
| automatic promotion            | なし                                                        | なし                                                  | なし                          | なし                          |

### 6.2 matrix の注記

1. **Artifact import source は destination scope に束縛されない**
   application は graph 上のすべての Initiative/Epic/Issue Workbench を approved root 候補にする。root Workbench から Issue destination、別 scope Workbench から Epic destination といった組合せも source eligibility 上は可能である。

2. **local-ID behavior は command 間で異なる**
   Workbench copy は `_validate_scope_id` で local を明示 reject する。Artifact import destination は existing `_resolve_scope_node` / `resolve_id_input` を使うため local ID を排除していない。この差は current public docs で十分説明されていない。

3. **`.md` は content type ではなく interface gate**
   invalid UTF-8、NUL、empty file も bytes opaque として保存される。よって「Markdown only」という表現は semantic validation を意味しない。

4. **Workbench copy の preservation と Artifact import の preservation は異なる**

   * Workbench copy: tree merge、source-wins、tree-wide atomicityなし
   * Artifact import: single-file byte identity、no-overwrite、prepublish fail-closed

---

## 7. 差分・不足・不整合の分類

### 7.1 gap inventory

| ID      | 差分 / 不足                                                  | 分類                                                    | 影響                                                    | 判定  |
| ------- | -------------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- | --- |
| GAP-001 | generic single regular-file import がない                   | missing product capability                            | ChatGPT以外の evidence を標準保存できない                         | 高   |
| GAP-002 | Workbench 外 source を直接 import できない                       | missing product capability                            | download/repo fileを一度 Workbenchへ移す必要                  | 高   |
| GAP-003 | non-`.md` formal Artifact identity がない                   | intentional limitation now judged insufficient        | image、PDF、binary、data fileがdurable evidence laneへ入らない | 高   |
| GAP-004 | directory / bundle import がない                            | intentional limitation / missing capability           | multi-file evidenceのtree関係を保存できない                     | 中   |
| GAP-005 | bulk / manifest-driven import がない                        | intentional limitation                                | 多数fileの反復操作                                           | 低〜中 |
| GAP-006 | Workbench creation helper がない                            | intentional limitation now judged insufficient        | 初回配置・正しいscope path discoveryにfriction                 | 中   |
| GAP-007 | root Workbench handoff command がない                       | intentional limitation                                | root資料のmanual selectionが必要                            | 低〜中 |
| GAP-008 | `workbench copy` が local ID を拒否                          | intentional limitation / contract under-specification | grandfathered local scopeをhandoffできない                 | 中   |
| GAP-009 | `chatgpt-output` provenanceをfilename単独で識別できない            | accepted tradeoff                                     | EALを失うとcreation route不明                               | 低〜中 |
| GAP-010 | persistent provenance lookup / catalogがない                | intentional non-goal                                  | 大量import後の横断検索が弱い                                     | 低   |
| GAP-011 | Epic requirementがfull/non-local IDを明瞭に固定していない            | contract/documentation inconsistency                  | parent contractとpublic behaviorの読み違い                  | 低   |
| GAP-012 | guide の root date bucket 表記が canonical `YYYY-MM-DD` より緩い | contract/documentation inconsistency                  | convention の揺れ                                        | 低   |
| GAP-013 | `report.md` が merged PR / closed #319 を反映していない           | lifecycle/closeout residue                            | governance / finish判断を誤らせる                            | 高   |
| GAP-014 | broader import の archive/quarantine policyが未定義           | missing product decision                              | generic importがZIP safetyを迂回し得る                       | 高   |
| GAP-015 | external sourceのprivacy/provenance policyが未定義            | missing product decision                              | absolute path漏洩、unexpected host read                  | 高   |
| GAP-016 | non-Markdown naming/validator contractが未定義               | missing product decision                              | unrelated fileをArtifactと誤称する危険                        | 高   |

### 7.2 implementation defect

確認済み implementation defect はない。

次は defect ではない。

* special filesystem entry を error にすること
  canonical は silent skip を禁止するが、全 platform の FIFO/socket/device copy を保証していない。
* `.MD` を reject すること
  tests と source guard が明示的に固定する current contract である。
* outside Workbench を reject すること
  accepted non-goal である。
* import success が EAL / canonical を変更しないこと
  authority boundary の必須要件である。
* reimport が新しい Artifact を作ること
  no-overwrite contract の帰結である。

### 7.3 product-inadequate limitation

次は一貫した current behavior だが、broader user goal には不足する。

1. source relocation を強制する Workbench-only boundary
2. `.md` suffix gate
3. single-file only
4. no direct external file
5. no formal non-Markdown identity
6. no idempotent Workbench setup helper
7. local scope handoff rejection
8. provenance が EAL にのみ依存

### 7.4 lifecycle residue

GitHub actual state と canonical report の差分は、core runtime の defect ではない。ただし Epic governance 上は無視できない。

推奨される separate closeout action:

* #319 closed を report へ反映
* PR #323 merged / merge commit を反映
* EAL-022 の disposition を actual observation に更新
* #312 を close するか、broader capability の follow-up を別 Epic に分離するか human decision
* broader generic import を理由に current Epic の既存 accepted contract を retroactive に書き換えない

---

## 8. あるべきtarget state

### 8.1 不変に保つ境界

次は変更しない。

* `.workbench/` は Git-ignored、opaque、disposable
* `artifacts/` は durable evidence
* canonical docs は main orchestrator single-writer
* imported body は evidence-only
* import は explicit
* source は copy-not-move
* existing destination は overwrite しない
* EAL / canonical docs / ADR を command が自動編集しない
* content / secret / absolute host path を output しない
* ZIP/tree authoring pack は quarantine / review / stage lane
* no background sync / watcher / copy-back
* no automatic promotion

### 8.2 generic single-file import

候補 CLI:

```text
spec-dock artifact import file
  (--initiative|--epic|--issue <id>)
  --file <path>
  --title <title>
  [--slug <slug>]
  [--external]
  [--source-label <safe-label>]
  [--json]
```

これは candidate surface であり、exact spelling は follow-up design で決める。

#### source zone

| source zone                  |         default | eligibility                                                    | persisted provenance                                    |
| ---------------------------- | --------------: | -------------------------------------------------------------- | ------------------------------------------------------- |
| Workbench                    |           allow | existing approved roots、regular non-symlink                    | repo-relative path                                      |
| repo-local outside Workbench |           allow | repo containment、regular non-symlink、safe ancestry             | repo-relative path                                      |
| external host path           | explicit opt-in | exact user-selected file、regular non-symlink、stable descriptor | safe label、basename、hash、byte count。absolute pathは保存しない |

`--external` を付けずに repo 外 path を受け付けない。external source は parent directory を scan せず、指定 file だけを descriptor-relative / no-follow で読む。

### 8.3 compatibility with `chatgpt-output`

`artifact import chatgpt-output` は削除・rename しない。generic use case の preset として、現行 behavior を完全に保持する。

```text
chatgpt-output preset
  source zone: Workbench only
  source suffix: exact .md
  destination storage identity: blank
  slug prefix: chatgpt-output-
  preservation semantics: imported_byte_exact / captured_received_text workflow
```

これにより existing scripts、docs、EAL、filenames、tests を壊さない。

### 8.4 Markdown regular file

generic `artifact import file` で `.md` を import する場合、次のいずれかを採る。

**推奨**: current blank `.md` grammar を再利用する。

* body bytes unchanged
* frontmatterなし
* source extension `.md`
* creation routeは command result / EAL
* existing validator compatibility

ただし generic import と ChatGPT preset の slug prefix は分ける。generic importに自動 `chatgpt-output-` prefixを付けない。

### 8.5 non-Markdown regular file

non-Markdown fileを `artifacts/` に単に copyし、validatorが「unrelated file」として無視する案は棄却する。それでは formal Artifact にならない。

推奨は、既存 `artifacts/` 内に**import-only opaque-file family**を定義することである。

要件候補:

* template creation 不可
* body / bytes opaque
* original extension または suffix chain を保持
* identity / filename parser / validator が formal recognition
* no frontmatter
* provenanceは result / EAL
* accepted ADRで namingを固定
* `.md` blank familyとの ambiguity を避ける
* new fileだけに適用し、既存 fileをrenameしない

naming は hard-to-reverse なので本書では確定しない。候補例:

```text
<ts>-opaque-file-<slug><source-suffix>
<ts>-<nn>-opaque-file-<slug><source-suffix>
```

`artifact_id`、suffixなし source、multiple suffix、case sensitivity、reserved names は ADR で決める。

### 8.6 provenance

single-file result と EAL は最低限次を持つ。

```text
import_kind
storage_identity
source_zone
source_path            # repo-relative only
source_label           # externalはsafe label
original_basename
original_suffix
destination_path       # repo-relative
scope_id
sha256
byte_count
capture_boundary
committed
cleanup_state
warning_codes
adoption_status        # commandは設定しない。orchestratorがEALで設定
```

禁止:

* evidence body
* secret-like value
* absolute host path
* browser download directory
* canonical / reviewer / readiness self-claim

### 8.7 Workbench UX

optional convenience として、idempotent mkdir だけを行う helper は有効である。

候補:

```text
workbench ensure --root [--date YYYY-MM-DD]
workbench ensure --scope <full-id>
```

制約:

* manifest / session / catalog を作らない
* existing contentを変更しない
* pathをstdoutで返すだけ
* delete / TTL / listingを管理しない
* root bulk handoffを追加しない

generic file import が実現すれば、root Workbench の必要 file を直接 scope Artifact に保存できるため、root copy command は引き続き不要である可能性が高い。

### 8.8 local-ID policy

候補は二つある。

1. current rejectionを維持し明文化
2. existing grandfathered local nodeに限り、full local IDをsource/target双方でexact resolveしてcopy可能にする

推奨は product owner が local node lifecycle を確認するまで保留すること。generic Artifact import は existing resolver と整合させ、full local IDを受ける場合でも numeric shorthand ambiguityをfail-closedにする。

### 8.9 directory / bundle

directory は初期 single-file import に混ぜない。別 use case とする。

候補 model:

```text
artifacts/
└── <bundle-id>-<slug>/
    ├── manifest.json
    └── payload/
        └── <source-relative-tree>
```

bundle requirement:

* source directoryをsymlink followなしでwalk
* regular filesをbyte-preserving copy
* manifestにrelative path、entry kind、SHA-256、byte count
* path traversal不可
* duplicate / case-fold collision検出
* entry count / total bytes / depthのbound
* special entry reject
* source tree mutation検出
* staging directoryへ完全copy
* atomic no-replace directory publish
* manifest-last または committed marker
* no automatic extraction
* no canonical/EAL auto-edit
* sourceを残す
* partial formal bundleを残さない

### 8.10 ZIP / archive boundary

ZIPを二種類に曖昧に扱わない。

1. **ChatGPT authoring pack / code tree transport**
   existing quarantine、path traversal、symlink、manifest、review、stage laneを必須とする。generic file importで迂回させない。

2. **opaque archive evidence**
   本当にbytesとして保存したい場合は、quarantine receiptまたはexplicit reviewed-opaque-archive policyを要求する。初期phaseではreject / deferが安全。

ZIP suffixだけで安全性や用途を自動判定しない。利用者が lane を明示し、receipt を検証する。

### 8.11 update / delete / overwrite

* import は immutable create
* overwrite option は追加しない
* in-place update は追加しない
* reimport は新 timestamp / suffix
* source delete / move option は初期非対応
* Artifact delete command は別 concern
* update は existing Workbench / imported Artifactを保持
* committed warning後は自動retryしない

---

## 9. 段階的な実装候補

### Phase 0 — lifecycle correction と product decision

**目的**: current Epic を閉じる証跡と、broader capability の authority を分離する。

作業候補:

* GitHub actual stateを `report.md` に反映
* EAL-022をactual merge observationへ更新
* #312 close / follow-up Epic creationをhuman decision
* generic importのaccepted requirement / ADRを作成
* non-Markdown naming
* external source policy
* archive quarantine boundary
* local-ID policy
* size / entry bounds
* fresh spec review

**実装なし**。

### Phase 1 — generic Markdown single-file import

**目的**: existing publisherを壊さず、Workbench と repo-local outside-Workbench の single `.md` を generic importできるようにする。

候補 scope:

* independent `ImportFileRequest` / `ImportFileResult`
* source-zone resolver
* repo-local safe source guard
* current Workbench source guard再利用
* blank `.md` destination
* existing create lock / allocator
* existing publisher primitives
* `chatgpt-output` compatibility preset
* docs / CLI / tests

non-scope:

* external host path
* non-Markdown
* directory / bundle
* bulk
* archive

### Phase 2 — external source と non-Markdown opaque-file Artifact

**目的**: explicit external file と arbitrary regular non-Markdown fileをformal Artifactとして保存する。

entry gate:

* accepted naming / validator ADR
* external privacy policy
* platform support decision

scope:

* explicit external opt-in
* source label
* absolute path non-disclosure
* import-only opaque-file family
* suffix / no-suffix / multi-suffix rules
* parser / validator / allocator
* no-overwrite / source-stability publisher
* content-free output
* provider/dogfood parity

### Phase 3 — Workbench UX と local-ID alignment

**目的**: practical workflow frictionを減らす。

候補:

* `workbench ensure`
* returned path contract
* full local ID policyの実装または明文化
* root date conventionのdocs修正
* no catalog / no TTL / no root bulk copy

このphaseは generic import と独立可能であり、需要が低ければ延期できる。

### Phase 4 — directory / bundle import

**目的**: multi-file treeを一つの durable evidence unitとして保存する。

entry gate:

* bundle naming / identity ADR
* manifest schema
* source stability algorithm
* limits
* archive/quarantine integration
* platform case sensitivity policy

scope:

* directory source
* staged bundle
* atomic no-replace publish
* manifest
* payload hashes
* special-entry policy
* fault injection
* quarantine receipt integration

non-scope:

* arbitrary raw ZIP extraction
* automatic canonical promotion
* background indexing
* shared global catalog

### Phase 5 — manifest-driven batch import（observed needがある場合のみ）

globを直接受け付けず、explicit manifestを入力とする。

* each itemのsource zone / destination / title / expected hash
* per-item committed result
* fail-fast または continue-on-error を明示
* silent partial success禁止
* batch-level canonical adoptionなし

### final quality slice

multi-Issueで進める場合は、最後に別 final quality Issueを置く。

* provider / dogfood / installed consumer parity
* fresh init / update
* full focused regressions
* static analysis
* manual Workbench / repo-local / external / non-Markdown / bundle scenario
* docs alignment
* security review
* lifecycle report / EAL
* PR delivery

---

## 10. 必要なテスト

### 10.1 existing compatibility

* current `artifact import chatgpt-output` の全 existing testsがpass
* existing filenamesをrenameしない
* blank `chatgpt-output-*` coexistence
* current warning / cleanup tokens
* current JSON fields
* Workbench opacity
* workbench copy source-wins
* provider/dogfood parity

### 10.2 source-zone matrix

| case                                  | expected                                        |
| ------------------------------------- | ----------------------------------------------- |
| root Workbench relative path          | allow                                           |
| scope Workbench absolute path         | allow                                           |
| repo-local outside Workbench relative | allow under generic command                     |
| repo-local outside Workbench absolute | allow、resultはrepo-relative                      |
| repo外 path without explicit opt-in    | reject before read                              |
| repo外 path with explicit opt-in       | allow exact regular file                        |
| missing external file                 | no destination                                  |
| external directory                    | reject single-file route                        |
| source symlink                        | reject                                          |
| ancestor symlink                      | reject or exact documented platform-safe policy |
| FIFO / socket / device                | reject                                          |
| source equals destination             | reject                                          |
| hardlink alias to destination         | reject                                          |
| source replaced after preflight       | reject before publish                           |
| source mutated same-size              | reject before publish                           |
| source unlinked during copy           | reject before publish                           |

### 10.3 extension / naming matrix

* `.md`
* `.MD`
* no suffix
* `.txt`
* `.json`
* `.pdf`
* `.png`
* `.tar.gz`
* Unicode basename
* leading dot
* reserved device name
* very long basename
* case-fold collision
* same-second standard slot
* suffix `01..99`
* suffix exhaustion
* malformed opaque-file name
* duplicate Artifact ID
* unrelated file remains unrelated
* current blank / typed grammar unaffected

### 10.4 byte preservation

* LF / CRLF
* BOM
* no final newline
* invalid UTF-8
* NUL
* empty
* random binary
* sparse file policy
* large streamed file
* hash mismatch injection
* partial read / write
* file fsync failure
* directory fsync failure
* destination read warning
* temp cleanup warning
* source permissions unchanged
* source path unchanged

### 10.5 publication / concurrency

* import vs import
* import vs `new artifact`
* generic Markdown vs chatgpt preset
* generic non-Markdown vs generic non-Markdown
* external writer creates final path before publish
* no-replace unavailable
* cross-device behavior
* create-lock acquire/release failure
* committed warning does not trigger retry
* existing destination bytes unchanged

### 10.6 authority / provenance

* command does not edit `report.md`
* command does not edit canonical docs
* command does not edit ADR mirror
* command does not edit assurance state
* output does not contain source body
* output does not contain absolute external path
* EAL example has source zone / safe label / hash / byte count
* imported body containing `authority: accepted` has no runtime authority
* preservation status and adoption status remain separate

### 10.7 Workbench UX

* root `ensure` idempotent
* scope `ensure` independent resolution
* existing content preserved
* malformed / symlink root reject
* no manifest / catalog generated
* no Git tracking
* update preserves
* local-ID policy exact tests
* near-name `.workbench-notes` unaffected

### 10.8 bundle

* empty directory
* nested directory
* zero-byte file
* binary matrix
* relative path order determinism
* symlink
* hardlink
* FIFO
* source tree mutation
* file/dir type collision
* case-insensitive collision
* depth limit
* entry count limit
* total byte limit
* manifest hash completeness
* staging failure
* atomic publish failure
* no partial formal bundle
* existing bundle no overwrite
* source tree survives
* result content-free

### 10.9 archive / quarantine

* authoring pack ZIP cannot enter generic single-file route without required lane
* traversal ZIP rejected
* absolute member rejected
* symlink member rejected
* manifest mismatch rejected
* reviewed tree receipt required for bundle route
* quarantine result does not imply adoption
* generic opaque archive policy, if adopted, requires explicit mode and does not extract

### 10.10 manual end-to-end

1. root WorkbenchにMarkdown
2. generic import to Initiative
3. scope WorkbenchにPNG
4. generic opaque-file import to Epic
5. repo-local outside WorkbenchにJSON
6. generic import to Issue
7. external fileをexplicit opt-in import
8. EALにcontent-free provenance
9. canonical rewrite
10. original sources unchanged
11. imported bytes/hash一致
12. reimport creates new path
13. ZIP/treeはquarantine laneへ
14. update後もすべて保持

---

## 11. セキュリティ・互換性・移行リスク

### 11.1 security failure modes

| Risk                             | 影響                            | 必須対策                                                 |
| -------------------------------- | ----------------------------- | ---------------------------------------------------- |
| path traversal                   | repo外 read/write              | lexical containment、descriptor-relative operation    |
| source symlink                   | 意図外 file read                 | `lstat`、`O_NOFOLLOW`、ancestor guard                  |
| destination symlink              | scope外 write                  | secure parent fd、identity recheck                    |
| TOCTOU source replacement        | 別bytes publish                | inode/device/mode/stat/hash再確認                       |
| hardlink alias                   | source/destination identity混同 | inode identity / alias guard                         |
| external absolute path leakage   | user privacy                  | output/EALにabsolute pathを出さない                        |
| secret-bearing file commit       | credential exposure           | explicit warning、content-free output、operator review |
| large file / resource exhaustion | disk / time exhaustion        | streaming、size policy、preflight free-space guidance  |
| bundle bomb                      | file count / depth exhaustion | entry/byte/depth limits                              |
| archive traversal                | arbitrary write               | existing quarantine lane                             |
| unsafe file execution            | imported evidenceの実行          | importはsafety certificationではないと明記                   |
| MIME spoofing                    | policy bypass                 | MIME / suffixをtrust boundaryにしない                     |
| partial bundle publish           | corrupt formal Artifact       | staging + atomic directory no-replace                |
| committed-warning retry          | duplicate Artifact            | committed pathを返しauto retry禁止                        |

### 11.2 secret scanning

current Workbench philosophy は content classifier / secret scan を command責務にしない。generic importでも heuristic secret scanを必須にすると、false positive、content disclosure、second policy systemを生む。

推奨:

* defaultはscanしない
* public docsでtracked Artifactへのcommit riskを明記
* optional organization policy hookを将来別 concernとして検討
* error/outputにcontentを含めない
* external source opt-inでoperator responsibilityを明示

### 11.3 compatibility

#### existing chatgpt Artifact

* renameしない
* typed tokenへ変更しない
* blank identityを維持
* EAL provenanceを維持
* existing validatorを維持

#### current `new artifact`

* template catalogを変更しない
* blank slug compatibilityを維持
* create lockを共有
* generic import-only identityをtemplate-creatable catalogへ自動追加しない

#### Workbench

* ignore patternを変更しない
* opacityを弱めない
* existing contentをmigrationしない
* helper導入時もmetadataを追加しない

#### source path

* existing approved Workbench pathを引き続き許可
* outside sourceは新 commandでのみ許可
* chatgpt presetにoutside sourceを追加しない

### 11.4 migration

推奨 migration は additive である。

1. current filesはそのまま
2. current commandsはそのまま
3. new generic commandを追加
4. new opaque-file grammarはfuture filesだけ
5. `validate`はnew familyをrecognize
6. existing unrelated non-Markdown filesを自動Artifact化しない
7. no database/schema migration
8. no automatic EAL backfill
9. no provenance inference from filename
10. report lifecycle correctionはbehavior migrationと分離

### 11.5 platform risk

current publisherはPOSIX-oriented no-replace / fd behaviorを多く持つ。broader external / bundle supportでは次を明示する必要がある。

* Windows no-follow / rename-no-replace
* directory fsync availability
* case-insensitive names
* reserved filenames
* symlink privilege
* hardlink behavior
* cross-filesystem staging
* extended attributes / ACL / owner非保証
* sparse file behavior

unsupported platformでunsafe fallbackを行わず、`publication_unsupported` equivalentでfail-closedにする。

---

## 12. 未確定事項と判断が必要な論点

### 12.1 product decisions

| ID    | 判断                                          | 推奨                                           |
| ----- | ------------------------------------------- | -------------------------------------------- |
| D-001 | broader importをcurrent Epic 00312へ追記するか     | follow-up Epicに分離                            |
| D-002 | non-Markdownをformal Artifactとしてrecognizeするか | yes                                          |
| D-003 | non-Markdown naming / artifact ID           | accepted ADRで固定                              |
| D-004 | external host sourceを許可するか                  | explicit opt-inで許可                           |
| D-005 | external sourceのprovenance                  | safe label + basename + hash。absolute pathなし |
| D-006 | `.MD` generic import                        | generic file routeでは許容候補。chatgpt presetは現行維持 |
| D-007 | local-ID Workbench handoff                  | grandfathered node policy確認後に決定              |
| D-008 | root Workbench helper                       | idempotent `ensure` は採用候補                    |
| D-009 | root bulk handoff                           | 引き続きreject                                   |
| D-010 | directory symlink                           | 初期bundleではreject推奨                           |
| D-011 | raw ZIP opaque import                       | quarantine receiptなしはreject                  |
| D-012 | max file size                               | deployment policyとして明示値を決定                   |
| D-013 | max bundle entries / bytes / depth          | 必須                                           |
| D-014 | persistent provenance catalog               | 初期はEALのみ。需要観測後                               |
| D-015 | source delete / move                        | 初期reject                                     |
| D-016 | in-place Artifact update                    | reject。append-only create                    |
| D-017 | bulk import                                 | manifest-drivenのみ、後段                         |
| D-018 | content / secret scan                       | core command非対応を維持                           |

### 12.2 strongest recommended decisions

1. broader generic importは新 follow-up Epic。
2. current chatgpt presetをcompatibility wrapperとして維持。
3. repo-local outside Workbenchを最初に追加。
4. external sourceは明示 opt-in。
5. non-Markdownはformal opaque-file familyを新 ADRで定義。
6. directory/bundleは別 phase。
7. ZIP/tree authoring packは既存 quarantine lane。
8. no automatic promotion / overwrite / move。
9. provenanceはcontent-free result + EAL。
10. current lifecycle residueを先に訂正。

### 12.3 未検証 claim

次は本調査で未検証であり、実装前に確認が必要である。

* actual user corpusにおける non-Markdown extension分布
* directory/bundleの平均・最大 file数
* external sourceの主要 location
* PDF/image/SQLite/ZIPの需要比率
* local-ID nodeの現存数とlifecycle
* Windows support obligation
* current no-replace primitiveの全supported platform behavior
* `artifacts/` directory familyを導入した場合の全 scanner / validator / sync callsite
* package / installer parityへの新 file family影響
* existing unrelated non-Markdown filesとの naming collision
* external file privacy requirements

---

## 13. 参照した主要ファイル

### 13.1 canonical Epic

* `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/requirement.md`

  * 目的 / capability envelope: lines 14–50
  * E-RQ-001–024: lines 64–135
  * scope / non-scope: lines 229–246
* `.../design.md`

  * overall / cross-Issue boundary: lines 15–49
  * opacity / CLI / copy / import: lines 98–198
  * failure / workflow / tests: lines 223–310
* `.../plan.md`

  * W1–W5 decomposition、dependencies、final quality
* `.../report.md`

  * progress / EAL / lifecycle state
  * stale PR / Issue observation

### 13.2 historical intent / decisions

* `.../artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md`
* `.../artifacts/20260713t003208z-disc-workbench-clarification-synthesis-and-authoring-handoff.md`
* `.../artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md`
* `.../artifacts/20260713t013008z-interview-local-only-node-prohibition-and-disposable-workbench-boundary.md`
* `.../artifacts/20260713t015912z-interview-unfiltered-filesystem-copy-without-content-classification.md`
* `.../artifacts/20260713t023439z-decision-candidate-chatgpt-output-artifact-import-contract.md`
* `.../artifacts/20260713t031057z-research-chatgpt-5-6-pro-artifact-import-integration-analysis.md`
* `.../artifacts/20260713t031808z-adr-template-free-artifact-import-and-blank-filename-coexistence.md`

### 13.3 implementation

* `src/spec_dock/assets/spec_dock/.gitignore`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workbench.py`

  * `workbench_copy`
  * `_validate_scope_id`
  * `_load_scope`
  * `_guard_ancestry`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py`

  * `import_artifact`
  * `_normalize_import_slug`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`

  * `_allocate_artifact_destination_under_create_lock`
  * `_resolve_scope_node`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py`

  * `resolve_id_input`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workbench.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`

  * `guard_workbench_ancestry`
  * `guard_workbench_inventory`
  * `copy_workbench`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`

  * `FilesystemBinaryArtifactPublisher.guard_source`
  * `FilesystemBinaryArtifactPublisher.publish`

### 13.4 public docs

* `src/spec_dock/assets/spec_dock/docs/guide.md`
* `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
* `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
* `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
* `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`

### 13.5 tests

* `tests/unit/application/test_workbench.py`
* `tests/cli_runtime/test_workbench.py`
* `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
* `tests/cli_runtime/test_artifact_import_s04.py`
* `tests/unit/infra/test_binary_artifact_publisher.py`
* `tests/unit/domain/test_authoring_source_manifest_workbench.py`
* `tests/unit/infra/test_installer_workbench_resolver_opacity.py`
* `tests/unit/infra/test_runtime_resolver_workbench_opacity.py`
* `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`

### 13.6 GitHub lifecycle objects

* Epic Issue #312: open
* child Issues #315–#319: closed
* PR #323: merged
* merge commit / current HEAD: `3ee6d9047506a40b938407ecfffbb341a3ca76af`

---

## 最終的な推奨

current implementationを「汎用importの不完全実装」として修理するのではなく、**完成した narrow capability として保持し、その上へ generic single-file importを独立追加する**のが最も安全である。

実装順は次が最小である。

```text
lifecycle correction / new ADR
  -> repo-local generic Markdown import
  -> external + non-Markdown opaque-file import
  -> optional Workbench ensure / local-ID decision
  -> optional directory bundle
  -> final parity / security / docs gate
```

この構成なら、現行のpath traversal、symlink、TOCTOU、source-stability、no-overwrite、content-free output、canonical-authority、ZIP/tree quarantineを弱めず、Workbench内外のfileを実用的にscope-local Artifactへ保存できる。
