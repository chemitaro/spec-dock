---
種別: 要件定義書（Issue）
ID: "iss-00345"
タイトル: "Generic Single-File Artifact Import"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["epic-00343", "init-local-00002"]
関連GitHub: ["#345"]
関連: ["iss-00344", "iss-00346", "20260728t100038z-adr"]
authorized_profile_observed: "strict"
parent_recommended_grade: "critical"
classification_status: "pending_runtime_owned_decision"
---

# iss-00345 Generic Single-File Artifact Import — Issue 要件定義

## 0. 文書の位置づけ

本書は Issue `iss-00345` の canonical requirement draft である。親 Epic、accepted ADR、現行 provider 実装、既存テスト、clarification evidence、ChatGPT Pro authoring evidenceをリポジトリ事実と照合して統合している。

本書が canonical path に存在することだけでは reviewer pass、assurance mutation、execution-ready、PR-ready、merge-ready、Issue finish、Epic completion、PR delivery を意味しない。assurance classification、fresh review、実装開始判断は runtime と main orchestrator の後続 workflow に残る。

現行 runtime guidance が示す `authorized_profile=strict` と、親 Epic の Candidate 2 推奨 `critical` は一致していない。本書は authority を選択または変更せず、この差を **pending classification input** として保持する。ただし、不可逆な filename identity、外部 path privacy、no-overwrite publication、retry disposition を扱うため、内容は `critical` 推奨に耐える安全性、failure mode、rollback、observability、test detail を持たせる。

## 1. 目的

### I345-OBJ-001 利用者価値

利用者が明示した任意の readable regular file 一件を、内容形式に依存せず、SpecDock root、Initiative、Epic、Issue のいずれかの Artifact 領域へ保存できるようにする。

### I345-OBJ-002 安全性

import は source を変更せず、opaque bytes を保持し、既存 Artifact を上書きせず、公開前 failure と公開後 warning を機械判定可能にする。

### I345-OBJ-003 意味論と privacy の分離

generic imported file を typed Artifact、ADR、canonical specification として自動解釈せず、repository 外 source の位置と内容由来情報を通常出力および tracked provenance へ漏らさない。

## 2. 背景と現状

SpecDock には既に `artifact import chatgpt-output` がある。この command は approved Workbench 内の lowercase `.md` を、`--title` / `--slug` に基づく blank Artifact identity へ byte-preserving import する専用経路である。現行実装は `commands/artifact_import.py`、`application/import_artifact.py`、`FilesystemBinaryArtifactPublisher`、`presentation/cli_text.py` にまたがり、destination-side staging、source revalidation、FD-bound no-replace publication を備える。

しかし、既存 command は次の理由で arbitrary single-file import の代替にならない。

- Workbench 内かつ lowercase `.md` に限定される。
- title / slug と blank Markdown naming grammar を要求する。
- 現行 result contract は source path、SHA-256、byte count を公開する。
- ancestor symlink を拒否する。
- root を Artifact target として扱わない。
- binary、archive、画像、PDF、invalid UTF-8、extensionless file を generic identity で扱う契約を持たない。

そのため、本 Issue は既存 command を一般化せず、独立した additive command `artifact import file` を追加する。

## 3. 用語

| 用語 | 本書での意味 |
|---|---|
| SpecDock root | repository 内の `spec-dock/` directory。graph node ではないが、本機能では明示 Artifact target になる。 |
| node | Initiative、Epic、Issue のいずれか。`.meta.json` により graph へ参加する。 |
| Artifact | root または node の `artifacts/` 直下に保存される evidence file。保存されたこと自体は canonical adoption を意味しない。 |
| typed Artifact | filename grammar に artifact type token を持つ既存 Markdown Artifact。 |
| blank Artifact | type token を持たない既存 Markdown Artifact。`chatgpt-output` はこの family を使う。 |
| generic Artifact | 本 Issue の `--` delimiter を持ち、original basename を中心に識別される opaque file。拡張子や body の意味分類をしない。 |
| slot | 同一 timestamp 内の標準 slot または `01..99` suffix slot。typed、blank、generic が共有する。 |
| Workbench | `.workbench/` の一時的・non-canonical・原則 Git 管理外の作業領域。Issue `iss-00344` の shell premise を前提とする。 |
| opaque bytes | text decode、MIME 判定、format 変換を行わず、そのまま保存する byte sequence。 |
| commit point | destination-side staged file を FD-bound no-replace primitive で正式 basename に公開した瞬間。 |
| external source | repository root の外側に解決される明示 source file。 |

## 4. Actors と triggers

### 4.1 Actors

| Actor | 役割 | 必要な観測 |
|---|---|---|
| SpecDock 利用者 | source file と target を明示する | 保存先 identity、commit state、retry 要否を privacy-safe に確認できる |
| 自動化 agent | text または JSON result を機械処理する | stable token と publication state を利用し、warning 後の重複 retry を避ける |
| reviewer | requirement、implementation、tests を照合する | parent trace、privacy、no-overwrite、opaque lifecycle、互換性を確認できる |
| maintainer | platform capability と fault を診断する | public output を汚染せず、test/internal evidence で原因を切り分けられる |

### 4.2 Triggers

- 利用者が repository 内または外の明示 file 一件を durable evidence として残したい。
- source が Markdown に限らず、PDF、画像、ZIP、binary、invalid UTF-8、extensionless file である。
- Workbench の temporary state とは分離して Artifact として残したい。
- typed Artifact / ADR semantics を付与せず original basename を維持したい。

## 5. 継承する上位契約

### 5.1 親 Initiative / repository 契約

- provider 実装 authority は `src/spec_dock/`、特に shipped runtime は `src/spec_dock/assets/spec_dock/` にある。
- `spec-dock/` は generated consumer workspace、dogfooding、active specification の面であり、一次実装 authority ではない。
- provider を先に変更し、必要な generated dogfood projection を後続確認する。
- Artifact 保存と canonical adoption、review、assurance を混同しない。

### 5.2 親 Epic requirement / design / plan

本 Issue は `E-RQ-008`〜`E-RQ-025` の Candidate 2 ownership、`E-AC-008`〜`E-AC-018` の focused closure、`D-003`〜`D-009`、Candidate 2 の vertical slice を継承する。

`E-AC-019` distribution と `E-AC-020` Epic final closure は Issue `iss-00346` が所有する。本 Issue は candidate-wheel consumer E2E、integrated dogfood、opt-in full regression、Epic-wide final review、残余 Epic integration PR を先取りしない。

### 5.3 accepted ADR

accepted ADR `20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md` が、generic family、full destination basename identity、shared slot、minimal normalization、external basename-only visibility、opaque lifecycle、FD-bound commit point、post-commit retry 不要を固定する。本 Issue 内でこれらを再判断しない。

## 6. Scope

### 6.1 In scope

- additive command `artifact import file`。
- required `--file <path>` と、exactly one の `--root` / `--initiative <id>` / `--epic <id>` / `--issue <id>`。
- repository-root-relative path、absolute path、`..` を含む明示 external relative path。
- readable regular leaf file 一件。
- leaf symlink reject、ancestor symlink allow with identity verification。
- opaque byte preservation と source non-mutation。
- root / Initiative / Epic / Issue の Artifact destination resolution。
- generic filename parser、minimal basename normalizer、shared slot ledger。
- destination-side staging、source stability verification、FD-bound no-replace publication、capability fail-closed。
- privacy-safe text / JSON / diagnostic contract。
- generic body を読まない validate / sync / dependency / context-pack / ADR mirror / authoring discovery。
- 既存 `chatgpt-output` / typed / blank Artifact behavior の regression protection。
- focused/default test lane、fault injection、provider-first docs/runtime change、必要な checked-in dogfood projection。

### 6.2 Out of scope

- directory、glob、bulk、recursive、watch、automatic sync、copy-back。
- source move、delete、rename、write-back。
- title、slug、typed `file` token。
- MIME、encoding、content type、archive、Markdown semantics の classifier。
- archive extraction、format conversion、preview、catalog、persistent source provenance。
- source body、hash、byte count、MIME、encoding、absolute path、parent path の public 出力。
- root を graph node として追加すること。
- canonical docs、report、ADR、assurance の自動更新。
- Issue `iss-00344` の Workbench shell 再実装。
- candidate wheel、fresh/updated consumer E2E、integrated dogfood、opt-in full regression、Epic-wide final review、残余 Epic PR。これらは `iss-00346`。
- merge、Issue close、`issue finish`、PR delivery。

### 6.3 Unchanged behavior

- `artifact import chatgpt-output` は Workbench-only、lowercase `.md`、`--title` required、optional `--slug`、blank identity、既存 source/hash/count result contract を維持する。
- `new artifact` の typed / blank grammar と result contract を維持する。
- existing Artifact を rename、migrate、reclassify しない。
- `workbench copy`、Workbench opacity、no-backfill premise を変更しない。
- root 以外の graph topology、node ID resolution、dependency model を変更しない。

## 7. Issue-level requirements

### I345-RQ-001 Additive command と target selection

`./spec-dock/scripts/spec-dock artifact import file --file <path>` を追加し、`--root`、`--initiative <id>`、`--epic <id>`、`--issue <id>` の exactly one を要求する。zero または multiple selector は source open、Artifact setup、formal destination creation より前に拒否する。

- Parent trace: `E-RQ-008`, `E-RQ-009`; `D-003`, `D-004`。
- ADR trace: root は ADR の対象 family を受けるが graph node にはしない。

### I345-RQ-002 Source path resolution と explicit authorization

relative source path は process current directory ではなく repository root を基準に lexical normalization する。`..` により repository 外 file を明示する path と absolute path を受け付け、追加 allow flag や parent directory enumeration を要求しない。explicit path はその leaf file 一件だけを読む authorization とする。

- Parent trace: `E-RQ-010`, `E-RQ-012`; `D-005`。
- ADR trace: Decision 5。

### I345-RQ-003 Eligible source と identity guard

source は readable regular leaf file 一件でなければならない。missing、directory、leaf symlink、FIFO、socket、device、unreadable file は content-free error で拒否する。ancestor symlink は許容するが、open descriptor、leaf path、device/inode/mode、および stage 後の source stability が一致する場合だけ成功させる。

- Parent trace: `E-RQ-011`, `E-RQ-013`; `D-005`。

### I345-RQ-004 Opaque byte / source preservation

source を text decode、newline normalization、MIME 判定、format conversion せず bounded-memory stream で destination-side temp へ copy する。empty、NUL、invalid UTF-8、binary、PDF、image、ZIP、large file を同じ契約で扱う。成功・失敗・warning の全経路で source file を write、move、rename、delete しない。

- Parent trace: `E-RQ-013`, `E-RQ-020`; `D-005`, `D-009`。
- ADR trace: Consequences の opaque byte contract。

### I345-RQ-005 Generic public filename identity

標準 basename は `<timestamp>--<safe-original-basename>`、同 timestamp slot が使用済みなら `<timestamp>-<nn>--<safe-original-basename>` とする。`nn` は `01..99`。`--` は generic family delimiter であり typed `file` token ではない。generic `artifact_id` は full destination basename とする。

- Parent trace: `E-RQ-014`; `D-006`。
- ADR trace: Decision 1〜3。

### I345-RQ-006 Minimal `NAME_MAX`-safe normalization

normalizer は path safety と destination component length に必要な変更だけを行う。original basename の extension chain、case、spaces、Unicode を可能な限り保持し、title、slug、MIME、content から filename を生成しない。UTF-8 byte budget を超える場合は code point boundary で deterministic に短縮し、最大 suffix prefix を含めても filesystem `NAME_MAX` を超えない。

- Parent trace: `E-RQ-015`; `D-007`。
- ADR trace: Decision 4。

### I345-RQ-007 Shared slot ledger と no-overwrite concurrency

typed、blank、generic family は `(timestamp, optional suffix)` slot ledger を共有する。allocator は destination `artifacts/` の direct child names だけを読み、body を読まない。cooperative process は existing create lock を共有し、non-cooperative race は FD-bound no-replace commit で上書きを防ぐ。`01..99` が全て使用済みなら mutation-free exhaustion error とする。

- Parent trace: `E-RQ-014`, `E-RQ-016`; `D-006`。
- ADR trace: Decision 3, 8。

### I345-RQ-008 Destination-side publication と platform capability

source filesystem に依存せず、destination directory 内に owned temp を作る。copy、file fsync、staged hash/count verification、source revalidation、destination parent identity verification の後、opened temp FD に結び付いた no-replace primitive で formal basename を公開する。Linux / macOS の supported primitive が利用できない場合、fallback overwrite や mutable-path rename を使わず fail closed とする。source と destination が別 filesystem でも成功可能でなければならない。

- Parent trace: `E-RQ-013`, `E-RQ-016`, `E-RQ-017`; `D-005`。
- ADR trace: Decision 8。

### I345-RQ-009 Publication state と retry disposition

public state は次の三つを区別する。

1. `not_committed`: commit point 前に失敗。`committed=false`。formal destination は作られない。修復後の retry は許容される。
2. `committed`: commit point と必要な durability / cleanup が完了。`committed=true`。retry 不要。
3. `committed_with_warning`: commit point 後に directory durability または owned-temp / create-lock cleanup warning。`committed=true`。retry は `not_needed`。

post-commit warning を command failure に変換して重複 import を誘発してはならない。

- Parent trace: `E-RQ-017`; `D-005`, `D-008`。
- ADR trace: Decision 8。

### I345-RQ-010 Privacy-safe public contract

repository 外 source について、text、JSON、error、warning、diagnostic、tracked provenance へ出してよい source identity は original basename だけとする。absolute path、parent component、body、hash、byte count、MIME、encoding、content-derived count/value、raw exception を出さない。repository 内 source は repository-relative path のみ許可する。pre-commit error は source field と destination fieldを持たず、unexpected exception も stable `runtime_failed` へ正規化する。

- Parent trace: `E-RQ-018`; `D-008`。
- ADR trace: Decision 6。

### I345-RQ-011 Opaque semantic lifecycle

generic filename は専用 parser で認識する。generic `.md` を含め、body を typed Artifact、ADR、requirement、design、plan、report、delegated draft として解釈しない。default `validate`、`sync`、dependency collection、context-pack、ADR mirror、authoring discovery は generic body を open / read / decode しない。

- Parent trace: `E-RQ-019`, `E-RQ-020`; `D-009`。
- ADR trace: Decision 7。

### I345-RQ-012 Root Artifact setup

`--root` は `spec-dock/` を target path、`root` を public target id として解決し、`spec-dock/artifacts/` を使用する。root を `SpecGraph` または `.meta.json` node として追加しない。必要な root rules source `spec-dock/docs/rules/root/artifacts.md` と `spec-dock/artifacts/rules.md` setup は node setup と同じ安全条件を満たし、invalid target/source の前処理で不用意に作成しない。

- Parent trace: `E-RQ-009`, `E-RQ-025`; `D-004`。

### I345-RQ-013 Compatibility isolation

新 command は既存 `artifact import chatgpt-output`、`new artifact`、typed / blank parser、Workbench shell / copy の public contract を変更しない。generic の result DTO、renderer、source guard、parser を既存 command と分離し、既存 tests を characterization / regression gate として維持する。

- Parent trace: `E-RQ-021`, `E-RQ-022`, `E-RQ-023`; `D-003`, `D-009`。
- ADR trace: Migration consequence。

### I345-RQ-014 Provider-first projection と documentation

runtime、docs、rules は `src/spec_dock/assets/spec_dock/` を先に更新し、必要な managed projection を `spec-dock/` へ反映して provider / dogfood parity を確認する。public docs は command、target、source policy、naming、privacy、publication state、authority boundary、Issue `iss-00346` handoff を説明する。

- Parent trace: `E-RQ-024`, `E-RQ-025`; Candidate 2 plan。

### I345-RQ-015 Authority / grade boundary

import は evidence storage だけを行い、canonical adoption、review、assurance、readiness を変更しない。本 requirement は `authorized_profile=strict` と parent `critical` recommendation の差を解決したと主張せず、runtime-owned classification と後続 authoring gate へ戻す。

- Parent trace: `E-RQ-019`; workflow authoring grade matrix。
- ADR trace: Decision 7。

## 8. Observable behaviors

### I345-BH-001 Targeted success

利用者が valid file と exactly one target を指定すると、target の `artifacts/` に一つの generic Artifact が作成され、source は残る。

### I345-BH-002 Root success

`--root` は `spec-dock/artifacts/` を使用し、graph node count、node metadata、dependency topology を変えない。

### I345-BH-003 Content-agnostic success

同じ command contract で text、binary、invalid UTF-8、empty、archive、image、PDF を保存できる。

### I345-BH-004 Collision-safe identity

同じ second の typed / blank / generic import が重なっても異なる shared slot を得て、既存 file は変わらない。

### I345-BH-005 Privacy-safe external result

external source の success result は basename だけを示し、failure result は source location を示さない。

### I345-BH-006 Honest warning

commit 後の durability / cleanup fault は exit success と `committed_with_warning` を返し、retry が不要であることを明示する。

### I345-BH-007 Semantic opacity

generic `.md` の body が ADR-like frontmatter や malformed UTF-8 を含んでも、default lifecycle は読まず、typed mirror / projectionsを増減させない。

### I345-BH-008 Existing command compatibility

同じ revision で `artifact import chatgpt-output` の help、source eligibility、filename、result fields、warning behavior が既存 characterization test と一致する。

## 9. Inputs and outputs

### 9.1 CLI input

```text
./spec-dock/scripts/spec-dock artifact import file \
  --file <path> \
  (--root | --initiative <id> | --epic <id> | --issue <id>) \
  [--json]
```

許可しない option: `--title`、`--slug`、`--type`、`--mime`、`--encoding`、`--directory`、`--glob`、`--recursive`、`--move`、`--delete-source`、`--overwrite`、external allow flag。

### 9.2 Success / warning output contract

| Field | 値 / 制約 |
|---|---|
| `status` | `ok` |
| `import_kind` | `file` |
| `storage_identity` | `generic` |
| `target_kind` | `root` / `initiative` / `epic` / `issue` |
| `target_id` | root は `root`、node は canonical node id |
| `artifact_id` | full destination basename |
| `source_visibility` | `repo_relative` / `basename_only` |
| `source` | repository 内は repo-relative path、外部は basename のみ |
| `destination` | repository-relative destination path |
| `committed` | `true` |
| `publication_state` | `committed` / `committed_with_warning` |
| `cleanup_state` | stable cleanup token |
| `warning_codes` | content-free stable tokens |
| `retry_disposition` | `not_needed` |
| `canonical` | `false` |

禁止 fields: hash、byte count、MIME、encoding、absolute path、parent path、content preview、raw exception。

### 9.3 Pre-commit error output contract

| Field | 値 / 制約 |
|---|---|
| `status` | `error` |
| `import_kind` | `file` |
| `storage_identity` | `generic` |
| `code` | stable content-free error token |
| `committed` | `false` |
| `publication_state` | `not_committed` |
| `cleanup_state` | stable cleanup token |
| `retry_disposition` | `safe_after_remediation` |
| `canonical` | `false` |

error output は source、destination、basename、hash、byte count、MIME、encoding、raw exception を含めない。

## 10. Privacy and security requirements

### I345-CON-001 Least authorization

explicit source path はその leaf file 一件だけの read authorization であり、parent directory listing、sibling traversal、recursive discovery をしない。

### I345-CON-002 No path disclosure

external source の directory identity を public/tracked surface に残さない。test sentinel を text / JSON / warning / stderr / exception string へ出さない。

### I345-CON-003 No content disclosure

body と content-derived metadata は public/tracked surface に出さない。hash / byte count は infra 内 verification と test evidence だけに限定する。

### I345-CON-004 No overwrite

formal destination の既存 entry を置換しない。symlink、directory、special entry が candidate generic name を占有する場合も fail closed とする。

### I345-CON-005 Bounded memory

copy と verification は configurable fixed-size chunk で行い、file 全体を memory へ読み込まない。

### I345-CON-006 TOCTOU resistance

source FD identity、path identity、metadata、hash/count を stage 前後で照合し、destination parent と temp FD を descriptor-bound に扱う。

### I345-CON-007 Platform fail-closed

安全な no-replace capability が確認できない platform/filesystem では代替 rename/copy overwrite を使わない。

### I345-CON-008 Semantic opacity

name parser 以外の理由で generic body を開かない。generic body に authority-bearing text があっても効力を与えない。

### I345-CON-009 Provider-first

implementation と shipped docs は provider path が authority。dogfood projection の直接手修正を一次実装にしない。

### I345-CON-010 Scope boundary

Issue `iss-00346` の distribution / integrated final-quality obligationsを本 Issue の closure として要求しない。

### I345-CON-011 Evidence-only authority

本 requirement、import receipt、Artifact presence は review、readiness、delivery の証明ではない。

## 11. Edge cases

### I345-EC-001 Zero / multiple target

zero または multiple selector は argument/application boundary で拒否し、source open と destination mutation を行わない。

### I345-EC-002 Repository-root-relative nested invocation

command を nested current directory から実行しても、relative source は repository root 基準で解決する。

### I345-EC-003 Explicit external relative path

`../evidence/report.PDF` のような path は explicit external file として扱い、basename `report.PDF` 以外の location を公開しない。

### I345-EC-004 Leaf / ancestor symlink

leaf symlink は拒否する。ancestor symlink は descriptor/path identity が安定しているときだけ許容し、retarget race は `source_changed` 相当で失敗する。

### I345-EC-005 Special / unreadable source

missing、directory、FIFO、socket、device、permission-denied regular file は formal destination なしで失敗する。

### I345-EC-006 Empty / binary / invalid UTF-8

empty、NUL、invalid UTF-8、PDF、image、ZIP、large payload は decode error なく byte-identical に保存される。

### I345-EC-007 Basename variants

no extension、multi-suffix、dotfile、uppercase extension、spaces、combining characters、CJK、emoji、case-sensitive variantsを content classification せず扱う。

### I345-EC-008 Unsafe / reserved basename

separator、control、NUL 相当、platform-reserved component、trailing unsafe component を deterministic に最小正規化し、空または `.` / `..` にはしない。

### I345-EC-009 `NAME_MAX`

標準 prefix と最大 `-99` prefix のどちらでも component byte limit を超えず、Unicode code point を途中で切らない。

### I345-EC-010 Cross-family collision

同一 timestamp の typed、blank、generic existing entry が標準または suffix slot を占める場合、次の空き suffix を使う。

### I345-EC-011 Exhaustion

`01..99` 全 slot 使用済みなら、既存 entry/source を変えず `not_committed` で失敗する。

### I345-EC-012 Cooperative / non-cooperative race

create lock を使う同時処理と、lock を使わず destination を作る race の両方で overwrite せず、一つの formal identityだけが各 commit に対応する。

### I345-EC-013 Source mutation

stage 中の same-size rewrite、replace、unlink、ancestor symlink retarget を検知し、formal destination を作らない。

### I345-EC-014 Cross-filesystem source

source device と destination device が異なっても、source を move/link せず destination-side stage により成功する。

### I345-EC-015 Unsupported publication capability

Linux `/proc/self/fd` link または macOS descriptor clone の必要 capability がない場合、formal destinationを作らず `not_committed` で失敗する。

### I345-EC-016 Post-commit warning

directory fsync、owned-temp cleanup、create-lock release が commit 後に失敗しても、formal destination は committed として報告し、retry 不要とする。

### I345-EC-017 Generic ADR-looking Markdown

basename/body が ADR に見えても generic family のままで、ADR mirror、canonical docs、authoring discovery に入らない。

### I345-EC-018 Root setup

fresh root に `artifacts/` / `rules.md` がない場合、valid import の locked setup で作成する。broken/wrong rules entry は上書きせず fail closed。

### I345-EC-019 Existing `chatgpt-output`

lowercase `.md` / Workbench / title / slug / blank identity / existing hash-count result を維持し、generic external policy を混入させない。

## 12. Acceptance criteria

### I345-AC-001 Command and selector

`artifact import file` help に `--file`, `--root`, `--initiative`, `--epic`, `--issue`, `--json` だけが該当 public option として現れ、exactly one target が必須である。`--title` / `--slug` 等は受け付けない。`I345-RQ-001`, `I345-EC-001` を閉じる。

### I345-AC-002 Target resolution

root、Initiative、Epic、Issue の四 target で destination が正しく解決され、kind mismatch / missing node は mutation-free で拒否される。root は graph node count/metadataを増やさない。`I345-RQ-001`, `I345-RQ-012`, `I345-EC-018` を閉じる。

### I345-AC-003 Path resolution

nested invocation、repo-relative、absolute、`..` external relative が repository-root-based contractで解決され、external location は basename 以外公開されない。`I345-RQ-002`, `I345-EC-002`, `I345-EC-003` を閉じる。

### I345-AC-004 Source eligibility

regular leaf と stable ancestor symlink path は受け付け、missing、directory、leaf symlink、FIFO、socket、device、unreadable は source/destination mutation 前に content-free error となる。`I345-RQ-003`, `I345-EC-004`, `I345-EC-005` を閉じる。

### I345-AC-005 Byte/source preservation

empty、NUL、invalid UTF-8、binary、PDF、image、ZIP、large stream の source/destination bytes が一致し、command は source を write、move、rename、delete、chmod、chown、または明示的に timestamp 更新しない。source path と content は保持される。読み取りに伴う access time の扱いは filesystem / mount policy に従い、本 command の mutation contract には含めない。`I345-RQ-004`, `I345-EC-006` を閉じる。

### I345-AC-006 Generic naming

標準 / collision filename が fixed grammar に一致し、artifact identity は full destination basename である。generic parser は typed/blank parser と意味的に分離される。`I345-RQ-005` を閉じる。

### I345-AC-007 Minimal normalization

case、spaces、Unicode、extension chain を可能な限り保持し、unsafe basename と `NAME_MAX` 超過だけを deterministic に正規化する。最大 suffixでも component limit を超えず code point を分断しない。`I345-RQ-006`, `I345-EC-007`〜`I345-EC-009` を閉じる。

### I345-AC-008 Shared ledger / exhaustion

typed、blank、generic の standard/suffix slot が一つの ledger で衝突回避され、`01..99` exhaustion は source/既存 entry を変えず `not_committed` になる。`I345-RQ-007`, `I345-EC-010`, `I345-EC-011` を閉じる。

### I345-AC-009 Concurrency / no overwrite

cooperative concurrent imports と non-cooperative destination race の両方で既存 file を上書きせず、success result ごとに一意な committed basename が存在する。`I345-RQ-007`, `I345-CON-004`, `I345-CON-006`, `I345-EC-012` を閉じる。

### I345-AC-010 Source race detection

same-size mutation、replace、unlink、ancestor symlink retarget が commit 前に検知され、formal destination が存在しない。`I345-RQ-003`, `I345-RQ-008`, `I345-EC-013` を閉じる。

### I345-AC-011 Cross-filesystem / capability

original source が destination と別 filesystem でも destination-side staging で成功する。安全 primitive が unavailable/unsupported の場合は formal destination なしで fail closed となる。`I345-RQ-008`, `I345-CON-007`, `I345-EC-014`, `I345-EC-015` を閉じる。

### I345-AC-012 Publication state

fault injection が pre-commit failure を `not_committed` / exit failure、post-commit durability/cleanup fault を `committed_with_warning` / exit success / retry `not_needed` として区別する。`I345-RQ-009`, `I345-EC-016` を閉じる。

### I345-AC-013 External privacy

external source の success text/JSON は basename のみを含み、failure/warning/unexpected error は absolute path、parent sentinel、body sentinel、hash、byte count、MIME、encoding、raw exceptionを含まない。tracked provenance にも同じ制約が成立する。`I345-RQ-010`, `I345-CON-001`〜`I345-CON-003` を閉じる。

### I345-AC-014 Opaque lifecycle

generic Markdown/binary を配置して `validate`, `sync --no-github`, dependency checks, context-pack, ADR mirror, authoring discovery を実行しても generic body open/decode がなく、typed projections/mirrorsが変わらない。`I345-RQ-011`, `I345-CON-008`, `I345-EC-017` を閉じる。

### I345-AC-015 Root setup safety

root rules source と `spec-dock/artifacts/rules.md` が provider-firstに用意され、valid root importでのみ安全に setup される。wrong/broken/symlinked destination setup を上書きしない。`I345-RQ-012`, `I345-EC-018` を閉じる。

### I345-AC-016 Existing command compatibility

既存 `artifact import chatgpt-output` の current focused testsが変更なしまたは意図を維持した更新で通り、lowercase `.md`、Workbench guard、title/slug、blank identity、既存 fieldsを保持する。`I345-RQ-013`, `I345-EC-019` を閉じる。

### I345-AC-017 Typed / blank compatibility

`new artifact` と existing typed/blank parsing、duplicate detection、ADR mirror behaviorが維持され、generic entry導入前の既存 Artifact を rename/migrateしない。`I345-RQ-013` を閉じる。

### I345-AC-018 Provider/docs/local quality

provider files、必要な managed dogfood projection、public docs、CLI help が一致し、Issue 345 focused/default lane と static checksが計画どおり検証される。candidate-wheel / integrated dogfood / opt-in full regression / Epic-wide review / residual PR は `iss-00346` handoffとして残る。`I345-RQ-014`, `I345-CON-009`, `I345-CON-010` を閉じる。

### I345-AC-019 Authority boundary

result/docs は `canonical=false` と evidence-only boundary を保持し、本 requirementと import receiptが assurance、review、readiness、delivery を変更しない。`I345-RQ-015`, `I345-CON-011` を閉じる。

## 13. Requirement traceability

| Issue requirement | Parent Epic requirement | Parent design | Accepted ADR / workflow evidence |
|---|---|---|---|
| `I345-RQ-001` | `E-RQ-008`, `E-RQ-009` | `D-003`, `D-004` | additive generic boundary |
| `I345-RQ-002` | `E-RQ-010`, `E-RQ-012` | `D-005` | ADR Decision 5 |
| `I345-RQ-003` | `E-RQ-011`, `E-RQ-013` | `D-005` | explicit leaf authorization |
| `I345-RQ-004` | `E-RQ-013`, `E-RQ-020` | `D-005`, `D-009` | ADR opaque-byte consequence |
| `I345-RQ-005` | `E-RQ-014` | `D-006` | ADR Decision 1〜3 |
| `I345-RQ-006` | `E-RQ-015` | `D-007` | ADR Decision 4 |
| `I345-RQ-007` | `E-RQ-014`, `E-RQ-016` | `D-006` | ADR Decision 3, 8 |
| `I345-RQ-008` | `E-RQ-013`, `E-RQ-016`, `E-RQ-017` | `D-005` | ADR Decision 8 |
| `I345-RQ-009` | `E-RQ-017` | `D-005`, `D-008` | ADR Decision 8 |
| `I345-RQ-010` | `E-RQ-018` | `D-008` | ADR Decision 6 |
| `I345-RQ-011` | `E-RQ-019`, `E-RQ-020` | `D-009` | ADR Decision 7 |
| `I345-RQ-012` | `E-RQ-009`, `E-RQ-025` | `D-004` | root is explicit, not a node |
| `I345-RQ-013` | `E-RQ-021`〜`E-RQ-023` | `D-003`, `D-009` | ADR migration consequence |
| `I345-RQ-014` | `E-RQ-024`, `E-RQ-025` | Candidate 2 delivery design | `AGENTS.md` provider-first rule |
| `I345-RQ-015` | `E-RQ-019` | authority isolation | authoring grade matrix / ADR Decision 7 |

## 14. Risks and mitigations

| Risk ID | Risk | Impact | Required mitigation |
|---|---|---|---|
| `I345-RISK-001` | path or content-derived metadata leak | external privacy breach | separate public DTO/renderers; sentinel tests across all exits; no raw exception rendering |
| `I345-RISK-002` | mutable path / overwrite race | evidence loss or identity corruption | descriptor-bound source/destination, shared lock, no-replace final primitive, race tests |
| `I345-RISK-003` | post-commit warning treated as failure | duplicate retry/import | explicit publication state and retry disposition; exit-success warning tests |
| `I345-RISK-004` | generic Markdown parsed as ADR/spec | authority confusion and decode failures | separate parser; name-only lifecycle filters; body-open spies |
| `I345-RISK-005` | `NAME_MAX` truncation destroys extension or Unicode | unstable public identity | deterministic byte-budget normalizer and boundary matrix |
| `I345-RISK-006` | generic changes regress `chatgpt-output` | existing workflow breakage | separate use case/contract/renderer/guard; unchanged focused regression tests |
| `I345-RISK-007` | unsupported filesystem silently falls back | non-atomic publication | capability probe and fail-closed token; no rename/copy fallback |
| `I345-RISK-008` | provider/dogfood drift | shipped behavior differs from repo observation | provider-first update, managed projection diff, parity checks |
| `I345-RISK-009` | assurance grade conflict is silently resolved | authority violation | preserve strict/critical discrepancy as pending input; no mutation claim |

## 15. Rollback expectations

- command leaf、generic use case/contracts/ports、generic parser/normalizer/ledger、explicit publisher entry、generic renderers、root rules/docs、testsを Issue commit単位で revert できること。
- existing `artifact import chatgpt-output`、typed/blank data、existing Artifact filenamesを migration/rewriteしないこと。
- rollback 後も既に committed された generic Artifact は user evidence として保持し、自動 rename/delete/reclassifyしないこと。
- retained owned temp がある場合は identity-confirmed cleanup procedureだけを使用し、unowned entryを削除しないこと。
- rollback 後は focused compatibility、`validate`、`sync --no-github`、provider/dogfood parityを再確認すること。
- public filename contract または commit/retry semanticsが既に利用者に公開された後の変更は、Issue-local rollbackで再定義せず Epic/ADR amendmentへ戻すこと。

## 16. Unknowns, assumptions, and source conflicts

### 16.1 Pending classification input

`authorized_profile=strict` はユーザー提示の runtime guidanceであり、parent Epicの Candidate 2 recommendationは`critical`である。本書はどちらも変更せず、runtime-owned classification / authoring gateで解決すべき入力として残す。

### 16.2 New files that do not yet exist at the inspected revision

指定 HEAD には `src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md` と `spec-dock/docs/rules/root/artifacts.md` が存在しない。また親 plan が列挙する generic import専用 test filesの一部も未作成である。これらは実装済み事実ではなく、本 Issueで追加する予定成果物である。

### 16.3 Attachment format conflict

補助 attachment `expected-output-contract.md` は generic `specdock-authoring-pack/` treeを要求する一方、本タスクの complete authoring requestは exact four-file ZIP treeを明示する。本成果物は task-specificかつ後発の exact ZIP contractを優先する。この判断は製品仕様ではなく今回の配送形式だけに適用する。

### 16.4 No user-intent blocker

filename、privacy、commit point、retry、semantic opacity、scope splitはparent Epicとaccepted ADRで固定済みであり、現時点で追加の利用者意図質問はない。実装中に accepted boundary変更が必要と判明した場合は、推測で補わず stop-and-escalateする。
