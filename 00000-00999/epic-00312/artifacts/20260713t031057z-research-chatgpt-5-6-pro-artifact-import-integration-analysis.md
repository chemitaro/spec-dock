# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a544f47-97a4-83ee-9648-259a4a5fca40

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: main
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached brief. Inspect @GitHub chemitaro/spec-dock main at e3db1325c93d2f0b95ffd2253821b5c2b6db260e and produce the requested Japanese repository-grounded analysis. Treat output as evidence-only.

### File: ../../../../../private/tmp/codex-agent-work/501/session-20260712t154229z-specdock-chatgpt-first-storage-analysis-ac120a25/epic-00312-artifact-import-analysis-prompt.md
Lines: 1-48
```md
 1 | # Epic 00312 Artifact import analysis brief
 2 | 
 3 | ## Context
 4 | - Repository: `chemitaro/spec-dock`, branch `main`, commit `e3db1325c93d2f0b95ffd2253821b5c2b6db260e`.
 5 | - Epic 00312 requirement/design/plan were reviewed before a new user-proposed decision was added.
 6 | - New evidence: `20260713t023439z-decision-candidate-chatgpt-output-artifact-import-contract.md`.
 7 | - Output is evidence-only. Do not claim canonical adoption or Issue creation.
 8 | 
 9 | ## Task
10 | Use the GitHub connector to inspect the specified commit and analyze whether the proposed byte-preserving `artifact import chatgpt-output` capability should be integrated into Epic 00312 or split into a separate Epic/Issue.
11 | 
12 | Inspect at minimum:
13 | - Epic 00312 canonical requirement/design/plan/report and all relevant artifacts.
14 | - Epic 00259 and its Artifact filename/type/template/collision/authority decisions, especially the accepted Artifact ADR/contract.
15 | - Current `new artifact` implementation, filename collision handling, templates, validators, CLI parser/registry, filesystem/persistence adapters, and tests.
16 | - `workflow_spec_authoring.md`, `workflow_chatgpt_authoring_pack.md`, authoring pack docs, and ChatGPT-first planning skills.
17 | - Existing ZIP quarantine/staging and raw evidence boundaries.
18 | 
19 | ## Proposed contract to evaluate
20 | - Separate `artifact import` from template-based `new artifact`.
21 | - MVP type `chatgpt-output`; single Markdown file only.
22 | - Copy, never move; preserve source.
23 | - Do not alter bytes, frontmatter, formatting, encoding, or newline style.
24 | - Generate only the Artifact-compliant destination filename.
25 | - Never overwrite; reuse existing collision suffix rule.
26 | - Copy to temporary destination, compare SHA-256 before/after, then publish to formal Artifact path.
27 | - Evidence-only; adoption remains in EAL.
28 | - ChatGPT-first principle: preserve a useful completed ChatGPT report as `chatgpt-output` before Codex rewrites canonical docs; never persist only the Codex summary.
29 | - Defer PDF/image/ZIP/bundles/directories/RawCaptureBundle until observed need.
30 | 
31 | ## Questions
32 | 1. Is this inside Epic 00312's objective, or should it be a separate Epic? Give a firm recommendation grounded in current scope contracts.
33 | 2. Does `chatgpt-output` fit the Artifact type/filename/template contracts from Epic 00259? Identify exact required refinements and contradictions.
34 | 3. Define the smallest correct CLI, application, domain, infra, and presentation design. Preserve bytes and avoid unnecessary framework design.
35 | 4. Specify atomicity, temp-file placement, SHA-256 verification, fsync/rename expectations, collision handling, source/destination identity, symlink input, encoding/Markdown validation, and cleanup behavior. Distinguish MVP requirements from overengineering.
36 | 5. Explain how an Artifact with no frontmatter remains discoverable/valid under current runtime and how authority/provenance is recorded without altering bytes.
37 | 6. Define workflow/skill changes for import-before-canonical-rewrite without creating an impossible hard gate when ChatGPT produces inline text instead of a downloaded file.
38 | 7. Propose revised Epic requirement/design/plan deltas and Issue decomposition. Preserve a mandatory final quality/PR Issue for multi-Issue implementation.
39 | 8. Provide a decision disposition table: adopt/refine/reject/defer, evidence paths, risks, tests, and unresolved human decisions.
40 | 
41 | ## Constraints
42 | - Japanese Markdown.
43 | - Cite repository paths for material claims.
44 | - Do not produce code or patches.
45 | - Do not invent current behavior.
46 | - Keep `new artifact` semantics unchanged.
47 | - Do not expand MVP beyond one Markdown file and `chatgpt-output` unless a repository contract makes it unavoidable.
48 | - Preserve the user's core objective: keep valuable ChatGPT reports verbatim, without Codex summarization loss.
```

## Answer

# 結論

**証跡限定の推奨は、`artifact import chatgpt-output` を Epic 00312 に統合し、独立した実装 Issue とワークフロー統合 Issue に分けることです。別 Epic にはしません。**

ただし、現在の W2「scoped Workbench copy」へ混ぜるべきでもありません。改訂後の分割は次が妥当です。

```text
W1  Workbench ignore / opaque traversal foundation
 ├─> W2  Scoped cross-worktree Workbench copy
 └─> W3  Byte-preserving Artifact import runtime
          └─> W4  ChatGPT-first preservation workflow / skills
W1 + W2 + W3 + W4
 └─> W5  Installed parity / final quality / mergeable Epic PR
```

この判断には、以下の重要な但し書きがあります。

* 現在の decision-candidate は `status: proposed`、`adoption_status: unreviewed` であり、まだ canonical requirement/design/plan や accepted ADR ではありません。
* 現行 Epic 00312 は 3 Issue 案の human approval 待ちで、Issue node はまだ作成されていません。そのため、いまが Issue 分割を変更する最も低コストな時点です。
* `chatgpt-output` を正式な typed Artifact とするには、Epic 00259 の accepted Artifact ADR を**黙って拡張せず、更新または supersede する Epic-level decision**が、子 Issue 実行前に必要です。
* 以下は採用・Issue 作成・実装完了の主張ではありません。

---

## 1. Epic 00312 に含めるべきか

### 推奨判定

**Epic 00312 の objective 内です。別 Epic へ分ける必要はありません。**

Epic 00312 は現在、Workbench を disposable scratch とし、durable evidence は `artifacts/` に残す境界をすでに定義しています。また、必要な証跡は利用者またはモデルが `artifacts/` へ移す、と明記しています。

現行契約に欠けているのは、その「移す」を次の条件で安全かつ再現可能に実行する標準経路です。

* 完成済み Markdown 一件だけ。
* Workbench から formal Artifact への明示操作。
* 内容は変更しない。
* 自動採用や canonical promotion はしない。
* 既存 Artifact を上書きしない。
* 原文と保存後の内容が一致したことを検証する。

したがって、これは新しい storage model ではなく、Epic 00312 がすでに持つ次の境界を閉じる機能です。

```text
disposable Workbench
    ↓ explicit evidence capture
scope-local artifacts/
    ↓ EAL disposition / canonical rewrite
canonical docs
```

候補契約自身も、MVP を単一 Markdown・一種類・三 scope に限定し、PDF、画像、ZIP、bundle、directory、RawCaptureBundle を延期しています。

### W2 に混ぜない理由

W2 の契約は「一つの scoped Workbench tree を別 worktree の scoped Workbench へ通常の filesystem copy で重ねる」ものです。内容分類、hash、transaction、Artifact authority は扱いません。

一方、Artifact import は次を扱います。

* formal `artifacts/` namespace への新規作成。
* Artifact ID と filename grammar。
* same-second collision allocation。
* no-overwrite publication。
* byte-level integrity。
* Evidence Adoption Ledger への provenance handoff。
* Epic 00259 accepted ADR との整合。

責務と失敗モデルが異なるため、W2 へ分岐を足すと両方の契約が不明瞭になります。

### 別 Epic に切り出す条件

次のいずれかへ広げる場合は、別 Epic の再検討が妥当です。

* Workbench 外の任意 host path を汎用 import source にする。
* PDF、画像、ZIP、directory、bundle を扱う。
* import type registry や provider registry を作る。
* persistent hash manifest、capture catalog、retention、quarantine を持つ。
* raw conversation transcript や credential-bearing capture の durable storage policyを扱う。
* Artifact 以外の evidence store を導入する。

MVP はそこまで広げないため、現時点では Epic 00312 内が最小かつ一貫した配置です。

---

## 2. `chatgpt-output` と Epic 00259 契約の適合性

### 総合判定

**Artifact の意味、typed filename、collision、evidence-only authority には適合します。
閉じた type catalog、template routing、blank filename grammar にはそのままでは適合しません。**

Epic 00259 の accepted ADR は、Artifact を scope-local working evidence と定義し、type catalog、filename、template routing を Epic-level contract としています。

| 契約面                 | 判定  | 必要な修正                                                               |
| ------------------- | --- | ------------------------------------------------------------------- |
| Artifact の意味        | 適合  | 完成済み ChatGPT report は working evidence であり、canonical docs ではないと明記する |
| typed filename      | 適合  | `<ts>-chatgpt-output-<slug>.md` と collision 形を type grammar に追加する   |
| collision           | 適合  | 現行 `01..99` allocation と no-overwrite をそのまま再利用する                    |
| closed type catalog | 矛盾  | accepted ADR を更新または supersede し、`chatgpt-output` を追加する              |
| template routing    | 矛盾  | 「認識可能 type」と「`new artifact` で template 作成可能な type」を分離する             |
| frontmatter         | 要修正 | imported type は frontmatter を要求しない明示的例外とする                          |
| authority           | 適合  | evidence-only、採否は EAL、canonical rewrite は main orchestrator         |
| provenance          | 要修正 | source/hash/capture boundary を本文外の command result と EAL に記録する       |

### type catalog は三つに分ける

現行実装では、`SUPPORTED_ARTIFACT_TYPES` が次を同時に担っています。

* filename parser が認識する type。
* validator が許す type。
* `new artifact` が作成できる type。
* blank slug の予約語。

`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py` では、同じ type tuple から typed filename regex と blank ambiguity 判定を作っています。

最小の正しい分離は次です。

| catalog                                 | 内容                                                      |
| --------------------------------------- | ------------------------------------------------------- |
| recognized / valid typed Artifact types | 現行 typed types + `chatgpt-output`                       |
| template-creatable `new artifact` types | 現行 catalogを変更しない                                        |
| importable types                        | MVP は `chatgpt-output` だけ                               |
| routing-only types                      | `draft-requirement` / `draft-design` / `draft-plan` のまま |

これにより、

* `new artifact chatgpt-output` は提供しない。
* `chatgpt-output` template は作らない。
* 既存 `new artifact` の template rendering は変更しない。
* `artifact import chatgpt-output` だけがその type を作成できる。

という境界になります。

### 避けられない blank filename 互換問題

ここには、明示的な矛盾があります。

現在の blank filename は次です。

```text
<ts>-<slug>.md
```

そのため、現在はたとえば次の名前を blank Artifact として解釈できます。

```text
20260713t130000z-chatgpt-output-analysis.md
```

一方、`chatgpt-output` を typed token として追加すると、同じ名前は typed Artifact として解釈されます。現行 parser は typed grammar を先に評価し、blank slug が既知 type で始まる場合を曖昧として拒否します。

したがって、次の二条件を完全に同時には満たせません。

1. `chatgpt-output` を content-independent な typed Artifact とする。
2. 従来 valid だった全ての `new artifact blank` slug を一件も変更しない。

**推奨は、`chatgpt-output-*` を新たな予約 prefix とし、その prefix を使う blank slug だけを新規に拒否することです。** `new artifact` の template catalog、通常の出力、他 type の意味は変更しません。

この一点さえ許容できない場合の代替は、`chatgpt-output` を Artifact type にせず、import provenance kind として扱い、destination を blank Artifact にすることです。ただし、その場合は filename parser 上の type discoverability を失うため、第一推奨にはしません。

### accepted ADR の扱い

既存 ADR は、identity、filename、supported catalog、template routing の変更時には ADR を更新または supersede してから子 Issue を実行するよう要求しています。

履歴を保つ観点では、既存 accepted ADR を直接書き換えるより、次を明記した**superseding ADR**が適切です。

* `chatgpt-output` の追加理由。
* recognized / creatable / importable catalog の分離。
* template-less import exception。
* frontmatter 非必須。
* blank prefix reservation。
* EAL による外部 provenance。
* `new artifact` の template semantics は維持。
* bundle、ZIP、directory import は対象外。

この決定は W3 の実装中に行うのではなく、Epic-level planning / review で先に固定すべきです。

---

## 3. 最小の CLI・application・domain・infra・presentation 設計

### CLI

候補 CLI はそのまま採用できます。

```text
spec-dock artifact import chatgpt-output
  --file <workbench-markdown-path>
  --title <title>
  [--slug <slug>]
  (--initiative <id> | --epic <id> | --issue <id>)
```

最小契約は次です。

* `chatgpt-output` だけを受け付ける。
* scope は正確に一件。
* `--file` は現在の worktree の `spec-dock/.workbench/` 配下に限定する。
* root Workbench、scoped Workbench のどちらからでも一件選択できる。
* Workbench 外の任意 host path は MVP 対象外。
* `--move`、`--overwrite`、`--body-file`、`--template-file`、`--id`、`--seq` は提供しない。
* destination basename は caller に指定させない。
* node 用の既存 top-level `import` command は変更しない。

既存 parser は `new artifact` と node import を別 surface として持ち、registry も module 単位で明示登録しています。したがって、`artifact` command group を独立 module として登録するのが衝突の少ない構成です。

### Application

独立 use case とします。

```text
ImportArtifactRequest
ImportArtifactResult
import_artifact(request)
```

`CreateArtifactDocRequest` に `source_file` や mode flag を足してはいけません。現行 `create_artifact_doc` は template 解決、UTF-8 text rendering、frontmatter replacement、`write_text` を前提としているためです。

Application の責務は次です。

1. type、scope、title、slug、source path を検証する。
2. scope directory と `artifacts/` を既存方式で解決する。
3. source が現在の `.workbench/` 配下であることを確認する。
4. 既存 create lock を取得する。
5. Artifact filename state を scan し、timestamp / suffix を allocation する。
6. binary publisher port を呼ぶ。
7. result を返す。
8. `report.md` や EAL は自動編集しない。

Result は最低限、次を持てば足ります。

* `artifact_type`
* `artifact_id`
* `scope_id`
* repo-relative destination path
* repo-relative source path
* SHA-256
* byte count
* durability / cleanup warning

### Domain

Domain は内容を扱いません。

* recognized / creatable / importable type の分類。
* `chatgpt-output` filename parse / format。
* slug validation。
* timestamp / `01..99` collision allocation。
* duplicate Artifact ID detection。
* import type eligibility。

現行 allocator は同じ秒の空き suffix を `01..99` から選び、枯渇時に失敗します。これはそのまま再利用できます。

SHA-256、filesystem path containment、binary copy、fsync は domain に置きません。

### Infrastructure

`TemplateScaffolder` や既存 text writer を流用せず、狭い binary publication port を追加します。

概念的な責務は次です。

```text
ArtifactBinaryPublisher
  - inspect source
  - copy to same-directory temporary file
  - calculate and compare hashes
  - fsync staged file
  - publish atomically without replacement
  - clean owned temporary file
```

現行 `TemplateScaffolder` は `read_text` / `write_text` と replacement を行うため、byte-preserving import には不適切です。

また、既存 `FileArtifactWriter` も単純な UTF-8 `write_text` であり、import に必要な hash/no-replace publication を提供していません。

### Presentation

Presentation は次を返します。

```text
spec-dock: ok (artifact import)
type=chatgpt-output
id=<artifact-id>
scope=<scope-id>
path=<repo-relative-path>
sha256=<digest>
bytes=<count>
```

必要なら既存 CLI convention に合わせて structured result へ投影しますが、import 専用の汎用 formatter framework は作りません。

失敗時に source 内容、file listing、secret-like value を出力してはいけません。

---

## 4. Atomicity、hash、fsync、collision、symlink、encoding、cleanup

### 推奨する処理順序

#### 4.1 Source preflight

MVP では次を要求します。

* source が存在する。
* current worktree の `spec-dock/.workbench/` 配下である。
* `.md` extension である。
* regular file である。
* source 自体が symlink ではない。
* Workbench root から source までの ancestor に symlink がない。
* directory、FIFO、socket、device 等ではない。
* zero-byte file は拒否する。
* UTF-8 として decode 可能である。
* NUL byte を含まない。
* Markdown parser、frontmatter parser、heading validator は実行しない。

**推奨は UTF-8-only です。** 現行 Artifact templates、staging、docs toolchain は UTF-8 text を前提としているためです。UTF-8 validation は read-only で行い、BOM、LF、CRLF、final newline の有無は変更しません。

Shift-JIS 等の非 UTF-8 input まで受け付けることは、「内容を変更しない」とは両立しますが、現在の repository text ecosystem との互換が未定義です。観測需要が出るまで延期するのが安全です。

#### 4.2 Source snapshot

source は binary mode で開き、最初に次を記録します。

* device / inode
* size
* modification time の高精度値
* SHA-256
* byte count

copy 後に再度 `fstat` と source path の `lstat` を行い、同じ regular file が残っていることを確認します。

外部 process による concurrent mutation が検出された場合は、publish 前に失敗します。

#### 4.3 Destination lock と allocation

現行 artifact creation が利用する repository create lock を共有します。別 lock を新設すると、`new artifact` と import の間で collision race が残るためです。

lock 内で次を行います。

* target scope 解決。
* `artifacts/` の symlink / non-directory guard。
* malformed filename / duplicate ID scan。
* timestamp と suffix allocation。
* final path が存在しないことの確認。

既存 create lock は O_EXCL ベースの ownership token を使い、release 時にも token を確認しています。

#### 4.4 Temporary copy と verification

temporary file は final `artifacts/` directory と同じ directory に置きます。

例:

```text
.specdock-artifact-import-<random>.tmp
```

`.md` suffix を付けないため、通常の Artifact validation が一時ファイルを候補として扱いません。現行 validation は `artifacts/*.md` のみを scan します。

手順は次です。

1. temporary file を exclusive-create する。
2. source descriptor から binary stream copy する。
3. copy 中の hash と byte count を計算する。
4. temporary file を flush する。
5. temporary file を `fsync` する。
6. temporary file を独立に再読込して SHA-256 を計算する。
7. source pre-hash、copy hash、temporary hash、byte count が全て一致することを確認する。
8. source stat が変わっていないことを確認する。

repository 内には同一 directory の temporary file と file `fsync` を行う先例がありますが、その実装は最終的に `replace` するため、そのまま no-overwrite import には使えません。

#### 4.5 Atomic no-replace publish

通常の `Path.replace()` / `os.replace()` は destination を上書きし得るため使用不可です。

必要な infra contract は、特定 API 名ではなく次です。

> final path が存在しない場合だけ、検証済み temporary inode を一操作で公開し、既存 path は絶対に置換しない。

POSIX での小さい実装候補は、同一 filesystem 上での atomic hard-link publication です。

```text
link(temp, final)  # final が存在すれば失敗
unlink(temp)
```

または、platform が提供する rename-no-replace primitive を使用します。

no-replace atomic primitive を提供できない platform で、次の check-then-replace fallback をしてはいけません。

```text
if not final.exists():
    replace(temp, final)
```

これは競合時に上書き race を残します。

publication が `EEXIST` で失敗した場合は、既存 file を触らず、destination state を再scanして次の suffix を allocationします。`01..99` を使い切れば no-write failure とします。

#### 4.6 fsync の期待値

MVP の推奨は次です。

| 項目                             | MVP                                |
| ------------------------------ | ---------------------------------- |
| temporary file `fsync`         | 必須                                 |
| atomic no-replace visibility   | 必須                                 |
| parent directory `fsync`       | platform が対応する場合は実行                |
| power-loss durability の絶対保証    | 主張しない                              |
| unsupported directory fsync    | `durability_not_confirmed` warning |
| persistent transaction journal | 対象外                                |

directory fsync が publish 後に失敗した場合、final file を自動削除してはいけません。file はすでに公開済みであるため、result は「committed、ただし durability warning」として path を明示し、利用者の無条件 retry を防ぐ必要があります。

#### 4.7 Cleanup

* publish 前の失敗: owned temporary file を削除する。final path は存在しない。
* publish 後の temporary unlink 失敗: final は成功扱いとし、cleanup warning を返す。final を rollback しない。
* source は全てのケースで削除・rename・chmod しない。
* process kill / machine crash による orphan temp の自動 garbage collector は MVP に入れない。
* orphan temp は `.md` ではないため Artifact validator には影響しないが、manual cleanup 手順を docs に残す。
* background cleanup、TTL、journal、recovery daemon は延期する。

### MVP と overengineering の境界

| MVP 必須                            | 延期                                  |
| --------------------------------- | ----------------------------------- |
| single regular `.md`              | PDF / image / ZIP / directory       |
| Workbench source containment      | arbitrary host path import          |
| read-only UTF-8 validation        | arbitrary encoding registry         |
| binary byte preservation          | Markdown AST validation             |
| same-directory temp               | generic staging framework           |
| SHA-256 / byte-count verification | persistent hash database            |
| shared create lock                | distributed lock                    |
| atomic no-replace publish         | multi-file transaction              |
| source mutation detection         | filesystem snapshot abstraction     |
| normal failure cleanup            | background orphan GC                |
| EAL provenance                    | sidecar receipt store               |
| explicit security warning         | heuristic secret/content classifier |

---

## 5. Frontmatter なし Artifact の validity、discoverability、authority

### Runtime validity

現行 validator は generic Artifact の本文や frontmatter を読みません。

`scan_artifact_duplicate_state` が検査するのは主に次です。

* filename grammar。
* malformed artifact-intent filename。
* symlink。
* duplicate artifact ID。
* timestamp / suffix collision。

したがって、type catalog と filename parser に `chatgpt-output` を追加すれば、次の file は frontmatter なしでも runtime-valid にできます。

```text
20260713t130000z-chatgpt-output-workbench-architecture-analysis.md
```

現在の generic validation には本文 metadata 要件がありません。

ただし、Artifact rules docs は現状、Artifact workflow を `new artifact` が作成する template surface として説明しています。imported Artifact という第二の正規作成経路を明記する docs 修正が必要です。

### Discoverability の正確な意味

MVP で保証できる discoverability は次です。

* scope-local `artifacts/` の filesystem enumeration。
* typed filename parser。
* `validate` による filename recognition。
* report/EAL から evidence path への参照。

**現在、全 generic Artifact を検索可能にする永続 Artifact catalog や global index はありません。** それを新設することは Epic 00312 の「second store / catalog を作らない」契約に反します。

したがって「discoverable」は、専用 query database を意味せず、scope、type token、filename、EAL path から見つけられることを意味します。

### Authority

imported file の中に次のような文字列が含まれていても、

```text
authority: accepted
reviewer pass
canonical
```

それだけで authority は生じません。

* type は `chatgpt-output` であり、`adr` ではない。
* accepted ADR mirror 対象にならない。
* import command は EAL を自動で adopted にしない。
* canonical docs は main orchestrator だけが編集する。
* fresh reviewer gate は別工程。

Artifact rules も、Artifact の採用は canonical docs、accepted ADR、または report EAL への反映によって成立すると定義しています。

### Provenance

本文を変更せず provenance を残す場所は、次の二つです。

1. import command result
2. `report.md` Evidence Adoption Ledger

推奨 EAL evidence fields は次です。

| field                     | 値                                                         |
| ------------------------- | --------------------------------------------------------- |
| source                    | `artifact import chatgpt-output`                          |
| source_role               | ChatGPT evidence producer / operator                      |
| capture_boundary          | downloaded-file / received-inline-text                    |
| source_path               | repo-relative Workbench path                              |
| evidence_path             | imported Artifact path                                    |
| sha256                    | import result digest                                      |
| size_bytes                | byte count                                                |
| adoption_status           | initially unreviewed、後に adopted/refined/rejected/deferred |
| claim                     | 採用対象となる具体的な claim                                         |
| target_artifact / section | canonical 反映先                                             |
| rationale                 | 採否理由                                                      |
| reviewer                  | fresh reviewer reference                                  |
| next_action               | rewrite / reject / revisit                                |

absolute host path、browser profile path、private download path は report に保存せず、repo-relative Workbench path または安全な origin label を使います。

sidecar JSON や import receipt Artifact を自動生成すると、MVP が一件から複数 file に広がり、persistent import metadata model が生じるため採用しません。

---

## 6. ChatGPT-first workflow の変更

### mandatory にする範囲

「原文を保存せず、Codex summary だけを残してはならない」は、次の条件付き hard gate にします。

> **完全な source file、または完全な受信 inline text が利用可能な場合、canonical rewrite より先に保存工程を実施する。完全な出力を取得できない場合は、理由を記録した exception で進行できる。**

これにより、価値ある原文を不用意に捨てず、inline-only UI で file export が存在しない場合の不可能な gate も避けられます。

### 入力形態別の処理

| ChatGPT output              | 処理                                                          | 保証                                                      |
| --------------------------- | ----------------------------------------------------------- | ------------------------------------------------------- |
| standalone Markdown file    | Workbench に置き、`artifact import chatgpt-output`              | source file と Artifact の byte equality                  |
| 完全な inline text             | 受信した text を編集せず Workbench の UTF-8 `.md` に capture して import | 「受信 text」からの byte equality。provider original bytes は未確認 |
| inline text が途中で切れている、コピー不能 | canonical work を block しない。report に exception を記録           | verbatim preserved を主張しない                               |
| ZIP / tree authoring pack   | 既存 review / safe extraction / stage lane                    | ZIP contract。single-file import へ流用しない                  |
| raw conversation transcript | MVP の `chatgpt-output` 対象外                                  | 将来の RawCaptureBundle / privacy contract                 |

推奨 preservation status は次です。

```text
imported_byte_exact
captured_received_text
skipped_inline_unavailable
rejected_unsafe_or_incomplete
```

`captured_received_text` は「ChatGPT provider が生成した remote file bytes」と同一とは主張しません。ブラウザ、Markdown renderer、clipboard を通過した時点で remote byte identity は不明だからです。

### 更新対象

#### `workflow_spec_authoring.md`

現在は delegated Artifact output を runtime-owned `new artifact <type>` で作成するとしています。

次の二経路を分離します。

```text
new artifact <type>
  = SpecDock template から作る draft / research / decision artifact

artifact import chatgpt-output
  = 完成済み外部 evidence を内容不変で取り込む
```

imported raw evidence に、delegated draft 用 frontmatter schema を挿入してはいけません。provenance は EAL へ置きます。

#### `workflow_chatgpt_authoring_pack.md` / `authoring/chatgpt-pack.md`

既存 ZIP/tree lane は、review、stage、candidate validation、EAL、canonical rewrite を行う構造です。

ここへ「standalone completed Markdown report lane」を並列追加します。ZIP review/stage の安全 scanner や raw transcript rejection は変更しません。

#### `spec-dock-chatgpt-authoring`

この skill はすでに「raw output を adopted canonical text とは別に保存する」と定義しています。

必要なのは抽象的な指示を、次の実行可能な checkpoint にすることです。

1. output form を file / inline / ZIP-tree に分類。
2. preservation status を決定。
3. file または complete inline の場合は import。
4. import path / hash / capture boundary を report に記録。
5. その後に canonical adoption review。
6. fresh reviewer gate。

#### Initiative / Epic / Issue planning skills

各 skill は現在も raw ChatGPT output を artifacts に残し、Codex が canonical docs を再記述するとしています。

変更点は、「残す」の具体的手段と exception record を共通化することです。

---

## 7. Epic requirement / design / plan の改訂差分

## Requirement 候補

既存 E-RQ-001–018 は維持し、次を追加するのが妥当です。

### E-RQ-019 Explicit Artifact import

* `artifact import chatgpt-output` は明示実行時だけ作動する。
* automatic promotion、background process、copy-on-rewrite は行わない。

### E-RQ-020 Source boundary

* input は current worktree の `.workbench/` 配下にある regular `.md` 一件。
* symlink、directory、special file、Workbench 外 path は拒否。
* source は削除・rename・変更しない。

### E-RQ-021 Byte integrity

* template、frontmatter、formatting、newline normalization、encoding conversion を行わない。
* valid UTF-8 bytes を binary copy する。
* source / staged destination の SHA-256 と byte count を比較する。
* source concurrent mutation を publish 前に検出する。

### E-RQ-022 Naming and no-overwrite

* destination filename だけを Artifact naming contract に従って生成する。
* collision は `01..99` rule。
* existing file を上書きしない。
* atomic no-replace primitive なしの check-then-replace fallback を禁止する。

### E-RQ-023 Authority and provenance

* imported Artifact は evidence-only。
* command は canonical docs、accepted ADR、report EAL を自動更新しない。
* path/hash/capture boundary を EAL disposition に渡す。

### E-RQ-024 ChatGPT-first preservation checkpoint

* complete file または complete inline text が利用可能なら canonical rewrite 前に保存する。
* exact capture が不可能な場合は exception record で進行できる。
* exception 時に verbatim preservation を主張しない。

### Acceptance 候補

* LF、CRLF、BOM、final newline なし、多言語 Markdown の byte equality。
* source が成功・失敗の双方で残る。
* hash mismatch / source mutation 時に final file がない。
* collision / concurrency で既存 file が変わらない。
* frontmatter なし `chatgpt-output` が validate を通る。
* `new artifact` help/catalog/template output が既存どおり。
* imported file が ADR authority / mirror にならない。
* standalone / inline / ZIP-tree の workflow 分岐が docs/skills と一致する。
* installed consumer / dogfood / provider parity と full quality。

既存の「hash manifest/database を導入しない」は維持できます。SHA-256 は一回の operation result と EAL evidence であり、persistent manifest ではありません。

## Design 候補

現在の design responsibility を次へ拡張します。

```text
DS-001 Workbench ignore / opaque foundation
DS-002 Scoped Workbench copy
DS-003 Byte-preserving Artifact import
DS-004 ChatGPT-first preservation workflow
DS-005 Distribution / final quality / PR
```

DS-003 の data flow は次です。

```text
Workbench regular Markdown
  -> source validation and pre-hash
  -> existing create lock
  -> Artifact filename allocation
  -> same-directory binary temporary file
  -> SHA-256 / size / source-stability verification
  -> atomic no-replace publication
  -> import result
  -> EAL disposition by orchestrator
```

## Plan / Issue decomposition 候補

### W1 — Experimental Workbench Ignore And Opaque Traversal Foundation

現行内容を維持します。

### W2 — Experimental Scoped Workbench Copy And Source-Wins Merge

現行内容を維持します。

### W3 — Byte-Preserving ChatGPT Output Artifact Import

担当:

* Artifact type catalog 分離。
* filename parser / allocator / validator。
* application request/result/use case。
* binary publisher port / adapter。
* CLI/parser/registry/bootstrap/presentation。
* collision、hash、atomic no-replace、cleanup tests。
* `new artifact` regression。
* Issue report。

依存: W1。

### W4 — ChatGPT-First Preservation Workflow And Skill Integration

担当:

* `workflow_spec_authoring.md`
* `workflow_chatgpt_authoring_pack.md`
* `authoring/chatgpt-pack.md`
* `spec-dock-chatgpt-authoring`
* Initiative/Epic/Issue planning skills
* file/inline/ZIP-tree decision matrix
* EAL provenance guidance
* provider/dogfood docs and skill mirror tests
* dogfood import scenario

依存: W3。

### W5 — Installed Runtime, Final Quality And Mergeable Epic PR

担当:

* W1–W4 の provider / installed / dogfood parity。
* fresh init / update preservation。
* focused/full tests。
* static analysis。
* manual Workbench-to-Artifact scenario。
* review/repair loop。
* Epic EAL/OAL/AC closure。
* push / mergeable Epic PR。

依存: W1、W2、W3、W4。

現行 plan は multi-Issue Epic に mandatory final quality Issue を要求しています。これを削除せず、現行 W3 の責務を W5 へ後退させます。

### 実行前 gate

Issue 作成前に次が必要です。

1. decision-candidate の EAL disposition。
2. Artifact contract を更新する superseding ADR。
3. revised requirement/design/plan。
4. 各 canonical artifact の fresh `spec-reviewer` pass。
5. revised 5-Issue slice への human approval。
6. その後に Issue node / dependency edge 作成。

---

## 8. Decision disposition table

| 項目                            | disposition               | 根拠 path                                | 主リスク                            | 必須テスト                             | 人間判断                        |
| ----------------------------- | ------------------------- | -------------------------------------- | ------------------------------- | --------------------------------- | --------------------------- |
| Epic 00312 内への統合              | **adopt**                 | `epic-00312/requirement.md`, candidate | scope 膨張                        | revised scope review              | 5-Issue案の承認                 |
| 別 Epic 化                      | **reject for MVP**        | candidate future boundary              | generic import framework化       | non-scope scan                    | 将来形式拡張時に再評価                 |
| `new artifact` と分離            | **adopt**                 | `application/create_artifact_doc.py`   | mode flag 混入                    | current `new artifact` regression | なし                          |
| typed `chatgpt-output`        | **refine**                | Epic 00259 accepted ADR                | blank prefix互換                  | parser/blank ambiguity tests      | prefix reservation の承認      |
| template を作らない                | **adopt**                 | candidate content contract             | type/template catalog混同         | help/template inventory           | なし                          |
| Workbench 内 source に限定        | **refine**                | Epic 00312 boundary                    | downloaded file が外部にある          | outside-path rejection            | 任意 host path を許すか           |
| single regular Markdown       | **adopt**                 | candidate MVP                          | special file / symlink          | file-kind matrix                  | なし                          |
| UTF-8-only read validation    | **refine**                | current text ecosystem                 | 非UTF-8 report拒否                 | BOM/CRLF/invalid UTF-8            | 非UTF-8需要を延期するか              |
| byte-preserving binary copy   | **adopt**                 | candidate                              | text APIによる改行変換                 | byte fixture matrix               | なし                          |
| frontmatter 非挿入               | **adopt**                 | candidate                              | provenance不足                    | no-frontmatter validate           | provenanceはEALでよいか          |
| collision suffix再利用           | **adopt**                 | Artifact ADR/domain allocator          | concurrent external writer      | suffix/concurrency tests          | なし                          |
| temporary + SHA verification  | **adopt with refinement** | candidate, existing temp precedent     | source mutation / partial write | hash fault injection              | なし                          |
| atomic no-replace publication | **refine**                | no-overwrite contract                  | `replace` による上書き                | EEXIST race test                  | unsupported platform policy |
| file fsync                    | **adopt**                 | integrity contract                     | I/O failure                     | fsync failure injection           | なし                          |
| directory fsync               | **refine**                | durability semantics                   | success後の曖昧 failure             | committed-warning test            | power-loss保証範囲              |
| source copy-not-move          | **adopt**                 | candidate                              | cleanupでsource誤削除               | all-failure source-survival       | なし                          |
| EAL authority/provenance      | **adopt**                 | workflow/report contract               | commandによるauthority越権           | no-report-mutation test           | なし                          |
| import-before-rewrite         | **refine**                | ChatGPT-first skills                   | inline-onlyで不可能なgate            | 4 output-mode scenarios           | exception条件の承認              |
| ZIP staging の流用               | **reject**                | Epic 00283 ZIP design                  | raw output rejection / text再書込  | existing ZIP regressions          | なし                          |
| secret/content classifier     | **reject for MVP**        | Epic 00312 no-classifier               | sensitive content commit        | warning/help review               | operator responsibility受容   |
| sidecar/import receipt store  | **reject**                | no second catalog/model                | metadata proliferation          | no-extra-file assertion           | なし                          |
| PDF/image/ZIP/bundle/dir      | **defer**                 | candidate future boundary              | scope explosion                 | none in MVP                       | observed need 後             |
| final quality Issue           | **adopt mandatory**       | current Epic plan                      | incomplete parity/PR            | full W1–W4 matrix                 | W5 ownership承認              |

---

## 最低限のテストマトリクス

### Domain / filename

* `chatgpt-output` standard filename parse。
* `01..99` collision parse / allocation。
* suffix exhaustion。
* duplicate Artifact ID。
* malformed type spelling。
* recognized / creatable / importable catalog separation。
* `new artifact chatgpt-output` rejection。
* blank slug `chatgpt-output-*` の決定済み挙動。

現行 tests は全 direct template catalog の filename、frontmatter、help surface、unsupported type、malformed Artifact を固定しています。これらを回帰 baseline にできます。

### Byte integrity

fixture:

* LF
* CRLF
* UTF-8 BOM
* final newline あり / なし
* multibyte Japanese
* Markdown frontmatter-like text
* `authority: accepted` を含む本文
* large streamed file
* invalid UTF-8
* NUL byte
* zero-byte file

assertion:

* source bytes == staged bytes == final bytes
* SHA-256 が一致
* byte count 一致
* source inode/path が残る
* chmod、mtime、filename は source 側で変わらない

### Source safety

* missing source
* outside Workbench
* source symlink
* symlinked ancestor
* directory
* FIFO / socket / device
* source mutation during pre-hash/copy
* source unlink/replace during operation
* target `artifacts/` symlink
* target ancestor symlink

### Collision / publication

* existing standard slot
* existing suffix slots
* exact final basename race
* concurrent two imports
* concurrent `new artifact` と import
* no-replace primitive `EEXIST`
* temporary write failure
* hash mismatch
* file fsync failure
* directory fsync failure after commit
* temporary cleanup failure
* normal failure後に final fileがない
* commit後 warning が final path を返す

### Authority / validation

* no-frontmatter `chatgpt-output` が validate pass。
* imported file が ADR mirrorにならない。
* content内の authority claim が runtime authorityにならない。
* command が `report.md`、canonical docs、`.assurance.json` を変更しない。
* only one new `.md` file。
* no sidecar。
* temporary `.tmp` が Artifact validation対象外。

### Workflow

* standalone file → `imported_byte_exact`
* complete inline → `captured_received_text`
* incomplete inline → `skipped_inline_unavailable`
* ZIP/tree → existing authoring pack lane
* canonical rewrite が保存 checkpoint 後に進む
* exception 時に「verbatim preserved」を主張しない
* EAL に path/hash/capture boundary が残る

### Final quality

* provider asset tests
* installed runtime tests
* fresh `init`
* existing `update`
* dogfood mirror inventory
* full pytest
* static analysis
* CLI help/text output
* manual Workbench → Artifact → EAL → canonical rewrite scenario
* fresh spec/code/QA review
* mergeable Epic PR evidence

---

## 人間による未解決判断

リポジトリだけでは確定できない点と、推奨 default は次です。

| 判断                                                    | 推奨 default                                         |
| ----------------------------------------------------- | -------------------------------------------------- |
| typed type 追加で `chatgpt-output-*` blank slug を予約してよいか | **許容する**。typed discoverability を優先                 |
| 非 UTF-8 Markdown を受け付けるか                              | **MVP では拒否**。valid UTF-8 bytes のみ                  |
| source を任意 path に広げるか                                 | **広げない**。current worktree Workbench 内のみ            |
| parent directory fsync 非対応時の扱い                        | **成功 + durability warning**。power-loss完全保証は主張しない   |
| completed report に secret scanner をかけるか               | **かけない**。明示 warning と operator responsibility      |
| full conversation transcript を扱うか                     | **扱わない**。別の privacy / RawCaptureBundle decisionへ延期 |
| superseding ADR と既存 ADR 更新のどちらか                       | **superseding ADR**。accepted history を保持           |

---

## 仮定・不確実性・未検証主張

### 仮定

* `artifact import` の source は current worktree の `.workbench/` 内とする。
* `chatgpt-output` は完成した report であり、会話全体の raw transcript ではない。
* EAL は command が直接編集せず、main orchestrator が更新する。
* existing create lock を `new artifact` と import で共有する。
* `new artifact` の template catalog と出力本文は変更しない。

### 不確実性

* typed type の追加に伴う blank prefix reservation は、repository grammar 上避けられません。人間による compatibility acceptance が必要です。
* directory fsync と atomic no-replace primitive の cross-platform availability は、対象 platform 上での probe が必要です。
* non-UTF-8 Markdown を将来サポートする必要性は観測されていません。
* imported report に sensitive content が含まれる運用リスクは、heuristic scanner なしでは command が保証できません。

### 未検証主張

* コード、tests、filesystem probe は実行していません。
* canonical docs、ADR、report は変更していません。
* candidate を採用済みとは扱っていません。
* Issue node、dependency edge、PR は作成していません。
* 外部 Web 参照は使用していません。

添付の `設計判断と提案.txt` は exception / failure taxonomy に関する別論点であり、本件の repository evidence には使用していません。
