# 結論

GitHub connector で `chemitaro/spec-dock` の現行ブランチ `iss-00318-chatgpt-first-preservation-workflow-and-skill-integration` を開けたため、分析に必要なリポジトリ根拠は揃っています。

採用候補の中核は、次の構成です。

1. **保存判断の四分岐は `spec-dock-chatgpt-authoring` に一度だけ定義する。**
2. Initiative / Epic / Issue planning skill は、その共通 checkpoint を ChatGPT 出力受領後・canonical rewrite 前に呼び出すだけにする。
3. 外部 ChatGPT 原文を `artifact import chatgpt-output` で保存する lane は、既存の delegated draft lane と明確に分離する。
4. 完成原文が存在するときの import failure は canonical rewrite / adoption を止める。一方、完全な inline 出力を本当に取得できない場合だけ `skipped_inline_unavailable` を非 blocking 例外として扱う。
5. ZIP/tree は既存の review・quarantine・stage lane を維持する。
6. CLI/runtime import、Artifact grammar、frontmatter、sidecar、catalog、EAL 自動編集は変更しない。
7. README、公開 reference、migration、package、fresh init/update、full regression、最終 PR は Issue 319 に残す。

これは添付 brief が固定する四分岐、authority、非スコープと一致します。

ただし、**grade には未解決の整合事項があります**。親 Epic は W4 を `M / Standard` 候補としている一方、今回の brief は strict-profile plan を要求しています。現在の Issue 318 の `requirement.md` は未具体化テンプレートで、`design.md` と `plan.md` は `awaiting-assurance-compose` の placeholder です。したがって、以下は **strict 運用候補**であり、`authorized_profile=strict` が確定した事実ではありません。`assurance classify` の結果を偽装せず、Standard が選ばれる場合は strict 相当の追加 gate を manual escalation として記録するか、根拠を修正して再分類する必要があります。

以下はすべて evidence-only candidate であり、canonical 採用、fresh reviewer pass、execution readiness、Issue 完了、PR readiness を表しません。

---

# 1. 確認済みのリポジトリ事実

## 1.1 Issue と依存状態

* Issue 318 は open。
* Issue 315、316、317 は GitHub 上で closed / completed。
* Issue 319 は open。
* Issue 317 は raw import runtime の実装を完了し、workflow / skill checkpoint を Issue 318、package・公開 docs・final parity・full quality・Epic PR を Issue 319 へ明示的に relay しています。

## 1.2 親 Epic が固定している契約

親 Epic の `E-RQ-024` / `E-AC-016` は、次を既に固定しています。

* imported output は evidence-only。
* import command は canonical docs、ADR、EAL を自動編集しない。
* 完成 file または完全に受信した inline text は canonical rewrite 前に保存する。
* 完全な出力が取得不能なら理由を記録するが、verbatim / byte-exact を主張しない。
* standalone file、complete inline、incomplete inline、ZIP/tree の四形態を別々に扱う。
* ZIP/tree は既存 authoring-pack lane のまま。
* import は fresh reviewer gate の代替ではない。

親設計は status 値も固定しています。

* standalone complete Markdown: `imported_byte_exact`
* complete inline: `captured_received_text`
* incomplete / unavailable inline: `skipped_inline_unavailable`
* ZIP/tree: existing review/quarantine/stage lane。

## 1.3 import runtime の既存契約

Accepted ADR と Issue 317 により、次は Issue 318 で再設計しない契約です。

* `chatgpt-output` は import kind であり typed Artifact token ではない。
* 保存先は existing blank Artifact grammar。
* frontmatter、sidecar、catalog/index を追加しない。
* source path、destination path、capture boundary、SHA-256、byte count、adoption は command result と EAL で追跡する。
* imported file は filename/body から authority を取得しない。
* raw import は delegated-authoring の UTF-8/frontmatter/diff-guard laneとは別扱い。

既存 CLI test は、byte preservation、content-free output、blank coexistence、invalid UTF-8 の generic validation / sync / ADR mirror 非影響を既に扱っています。Issue 318 はこれらを regression guard として使うべきで、runtime を変更する根拠にはしません。

## 1.4 現行 docs / skills の gap

現在の `workflow_spec_authoring.md` は、ChatGPT output を広く delegated evidence と呼び、delegated draft には `new artifact`、frontmatter、diff guard を要求しています。外部完成 report の raw import lane はまだ分離されていません。

現行 authoring lifecycle は、working artifact を用意した後、そのまま canonical artifact update へ進む構造であり、ChatGPT 原文保存 checkpoint が独立工程として存在しません。

現行 ChatGPT authoring docs は ZIP/tree 中心で、standalone / complete-inline / unavailable-inline の保存 lane をまだ説明していません。

三つの planning skill は ChatGPT evidence の受領、review、EAL、canonical rewrite、fresh reviewer の責任を持ちますが、受領直後の preservation checkpoint はまだありません。

---

# 2. `requirement.md` 候補

## 2.1 文書状態候補

* ID: `iss-00318`
* 状態: `draft`
* 親: `epic-00312`, `init-local-00003`
* 推奨 grade: `strict`
* grade authority: **未確認。`assurance classify` の結果を正とする**

## 2.2 目的

ChatGPT-first planning で得た有用な完成出力を、main orchestrator が要約・選別・canonical rewrite する前に、出力形態に応じた明示的な保存 checkpoint へ通す。

同時に、完全な source が取得不能な場合を不可能な hard gate にせず、ZIP/tree の既存安全 lane、delegated draft の provenance / diff-guard、canonical single-writer、fresh reviewer gate を変更しない。

## 2.3 親 trace

* Parent requirement: `E-RQ-024`
* Parent acceptance: `E-AC-016`
* Parent design slice: `DS-004`
* Dependency: Issue 317 completed
* Downstream: Issue 319
* Accepted ADR:

  * `adr-20260713t031808z-template-free-artifact-import-and-blank-filename-coexistence`

## 2.4 Actor

| Actor                                    | 責任                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| Human / operator                         | ChatGPT-first workflow の利用を開始し、必要な source を提供または利用可能にする                                     |
| Main orchestrator                        | output form と completeness を判定し、保存、EAL disposition、canonical rewrite、reviewer handoff を所有する |
| `spec-dock-chatgpt-authoring`            | 四分岐 checkpoint の共有運用契約を提供する                                                                 |
| Initiative / Epic / Issue planning skill | 共通 checkpoint を呼び出し、各 scope の EAL、canonical docs、human gate、reviewer gate を所有する             |
| `artifact import chatgpt-output`         | Workbench Markdown を existing runtime contract で保存し、content-free receipt を返す                |
| Authoring-pack runtime                   | ZIP/tree の review、quarantine、stage、validation を既存どおり行う                                      |
| `spec-reviewer`                          | main orchestrator が統合した canonical docs を fresh review する                                    |

## 2.5 代表シナリオ

### SC-318-001 完成 standalone Markdown

* Given:

  * 一件の完成済み Markdown file が利用可能。
* When:

  * main orchestrator が canonical rewrite 前に Workbench source を `artifact import chatgpt-output` で import する。
* Then:

  * preservation status は `imported_byte_exact`。
  * Workbench source と imported Artifact の SHA-256 / byte count が一致する。
  * EAL に repo-relative path、hash、byte count、capture boundary、adoption disposition が記録される。
  * その後にだけ採否判断と canonical rewrite へ進む。

### SC-318-002 完全に受信した inline text

* Given:

  * Codex が完全な inline text を受信済み。
* When:

  * 受信した文字列を編集せず Workbench `.md` へ capture し、import する。
* Then:

  * status は `captured_received_text`。
  * 「Codex が受信した text を保存した」とだけ主張する。
  * upstream provider 内部の byte representation と同一とは主張しない。

### SC-318-003 不完全または取得不能な inline output

* Given:

  * 完全な source が現在の workflow で本当に取得不能。
* When:

  * main orchestrator が exception を記録する。
* Then:

  * status は `skipped_inline_unavailable`。
  * path、SHA-256、byte count、verbatim / byte-exact claim を作らない。
  * 理由と nonblocking 根拠を EAL / report に残す。

### SC-318-004 ZIP/tree output

* Given:

  * output が ZIP または multi-file tree。
* When:

  * ChatGPT authoring evidence lane が処理する。
* Then:

  * existing review / quarantine / stage / validation lane を使用する。
  * single-file import lane へ流さない。

### SC-318-005 保存失敗

* Given:

  * 完成 source が利用可能。
* When:

  * import が `committed=false`、receipt 欠落、または eligibility failure となる。
* Then:

  * canonical rewrite と evidence adoption を block する。
  * source を「取得不能」と再分類して checkpoint を迂回しない。

## 2.6 Issue 要件

### RQ-318-001 明示的 preservation checkpoint

ChatGPT-first Initiative / Epic / Issue planning は、ChatGPT output 受領後、採否検討または canonical rewrite の前に、output form と completeness を判定する明示的 checkpoint を持つ。

Checkpoint は automatic hook、background operation、implicit promotion として実装しない。

### RQ-318-002 Standalone complete file

完成 standalone Markdown が利用可能な場合、Workbench source を `artifact import chatgpt-output` で保存し、status を `imported_byte_exact` とする。

Byte identity claim の直接境界は、少なくとも import receipt が検証した **Workbench source と imported Artifact** とする。

### RQ-318-003 Complete inline capture

完全な inline text は、Codex が受信した文字列を要約、整形、frontmatter 追加、newline 補正せず Workbench Markdown へ capture して import する。

Status は `captured_received_text` とし、provider-side original bytes の同一性を主張しない。

### RQ-318-004 Unavailable exception

完全な inline source が本当に利用不能または不完全な場合だけ、`skipped_inline_unavailable` を使用できる。

Exception record は理由、判定者、blocking=false の根拠、次アクションを持ち、source/destination path、hash、byte count を持たない。

### RQ-318-005 ZIP/tree lane preservation

ZIP/tree は既存 authoring-pack lane のままとし、single-file import、raw Markdown capture、new Artifact import kind へ変換しない。

ZIP の path traversal、symlink、unexpected-file、manifest 等の安全契約を弱めない。

### RQ-318-006 Blocking と committed semantics

* 完成 applicable source が存在し、import が未完了または `committed=false` の場合、rewrite / adoption を block する。
* `committed=true` で final path、hash、byte count が返っている post-publish warning は、保存済みとして warning を記録する。
* committed warning に対して無条件再 import し、重複 Artifact を作らない。
* import result が曖昧な場合は保存済みと推定しない。

### RQ-318-007 EAL provenance

成功した file / inline 保存について、main orchestrator は少なくとも次を EAL へ記録する。

* output form
* preservation status
* capture boundary
* import kind
* storage identity
* repo-relative source
* repo-relative destination
* SHA-256
* byte count
* committed / warning state
* adoption status
* rationale
* adopter
* reviewer status
* blocking
* next action

EAL は body text、secret-like value、absolute host path を含めない。

現行 report scaffold は EAL の採否、blocking、reviewer、next action を既に必須 evidence としています。

### RQ-318-008 External preserved evidence と delegated draft の分離

Imported external ChatGPT output は、delegated authoring role が作成した draft ではない。

したがって次を要求しない。

* `created_by_role` frontmatter
* `source_paths` / `intended_targets` frontmatter
* `adoption_status: unreviewed` frontmatter
* `reflected_to: []`
* delegated-authoring diff guard

ただし、既存 delegated draft lane については上記 provenance / diff-guard requirements を一切緩和しない。

### RQ-318-009 Authority isolation

ChatGPT、import command、shared authoring skill、planning skill 自身は次を self-claim しない。

* canonical adoption
* accepted ADR
* reviewer pass
* assurance mutation
* execution-ready
* Issue finish
* Epic completion
* PR-ready
* merge-ready
* PR delivery

Main orchestrator だけが EAL disposition と canonical rewrite を行い、fresh reviewer が別 gate を提供する。

### RQ-318-010 Shared skill ownership

四分岐の完全な decision matrix、status semantics、failure semantics、claim restrictions は `spec-dock-chatgpt-authoring` が共有 contract として所有する。

Initiative / Epic / Issue planning skill は次だけを持つ。

* 共通 checkpoint の呼出し時点
* scope-specific EAL ownership
* canonical rewrite ownership
* human approval gate
* fresh reviewer gate
* downstream handoff

三つの planning skill へ四分岐表を複製しない。

### RQ-318-011 Provider authority と focused parity

Provider-side docs / skill assets を authority とし、対応する dogfood surface を provider から投影する。

Issue 318 では以下を行う。

* 対象 workflow / skill の provider 更新
* matching dogfood projection
* wrapper / skill contract test
* managed-asset focused test
* dogfood preservation scenario

Package build、fresh init/update の最終 matrix、公開 docs inventory、full parity は Issue 319 に残す。

### RQ-318-012 Runtime compatibility

次を変更しない。

* `artifact import chatgpt-output` parser / application / publisher / presentation
* blank Artifact grammar
* import result contract
* Artifact rules / template catalog
* authoring-pack runtime
* delegated-authoring runtime
* sync / validate / ADR mirror semantics

Runtime defect が新たに実証された場合は、plan amendment と scope review を先に行う。

### RQ-318-013 Deferred delivery

Issue 318 は per-Issue PR を作らず、Issue 319 へ delivery を relay する。

Report には次を残す。

* target: Issue 319
* dependency edge
* no-per-Issue-PR の理由
* merge-prepared を主張しないこと
* Issue 319 に残る package/docs/full test/final review/PR gate

親 Epic も W1–W4 の deferred delivery と W5 の最終 PR ownership を固定しています。

## 2.7 受け入れ条件

### AC-318-001 Standalone preservation

完成 standalone Markdown を処理すると、canonical rewrite より前に import が committed となり、source/destination の hash と byte count が一致し、EAL status が `imported_byte_exact` になる。

### AC-318-002 Inline preservation

完全な inline text を処理すると、受信 text が編集されず Workbench file へ capture/import され、EAL status が `captured_received_text` になる。Provider original bytes の claim は存在しない。

### AC-318-003 Unavailable exception

完全 source が取得不能な case では `skipped_inline_unavailable`、reason、nonblocking 根拠が記録され、path/hash/byte-exact claim が存在しない。

### AC-318-004 ZIP/tree compatibility

ZIP/tree fixture は既存 pack review / stage path を使用し、`artifact import chatgpt-output` が呼ばれず、既存 ZIP safety test が回帰しない。

### AC-318-005 Failure gate

完成 source に対する `committed=false`、receipt 欠落、source eligibility failure の各 case で、planning skill は canonical rewrite / adoption に進まない。

`committed=true` warning は final receipt と warning を記録し、automatic retry を行わない。

### AC-318-006 Evidence-lane separation

Imported raw evidence は delegated draft frontmatter / diff-guard の対象外である。一方、delegated draft の既存 negative tests と provenance requirements は不変である。

### AC-318-007 Authority と secrecy

Successful / failed / skipped の各 path で、EAL と skill output は body、secret-like value、absolute path、canonical/reviewer/readiness claim を含まない。

### AC-318-008 Shared checkpoint integration

三つの planning skill が同じ shared checkpoint を、ChatGPT output 受領後・canonical rewrite 前に一度呼ぶ。

四分岐の status / matrix は planning skill 内に複製されず、各 planning skill の canonical/EAL/reviewer ownership は維持される。

### AC-318-009 Provider / dogfood projection

対象 provider docs / skills と matching dogfood files が、documented exception を除き同一内容になる。

Fresh `init` で installed skill/docs が checkpoint、status、forbidden claims を含むことを focused wrapper test で観測できる。

### AC-318-010 Runtime non-regression

Issue 317 の import focused tests、generic validate/sync/ADR mirror tests、blank coexistence testsが回帰せず、runtime import sourceに意味変更がない。

### AC-318-011 Delivery relay

Report に Issue 319 への deferred PR delivery record と残存 gate があり、Issue 318 が PR-ready / merge-ready を主張しない。

## 2.8 例外・エッジケース

* **EC-318-001 Authority claim in body**
  Imported body が `authority: accepted`、`reviewer pass` 等を含んでも無視する。

* **EC-318-002 Complete source outside Workbench**
  Source が完全でも runtime eligibility 外なら、そのまま import を試行しない。Approved Workbench source を準備できるまで blocking とし、単に `unavailable` へ再分類しない。

* **EC-318-003 Semantic completeness と file validity**
  File size、UTF-8 validity、frontmatter 有無だけで semantic completeness を自動判定しない。Import runtime が zero-byte / opaque bytes を受理することと、planning output が「完成している」ことは別判断である。

* **EC-318-004 Committed warning**
  Final Artifact が committed 済みなら rollback や自動 retry をしない。Warning と receipt を EAL に残す。

* **EC-318-005 Receipt 欠落**
  Import success を主張しながら destination/hash/bytes が取得不能な場合、checkpoint は incomplete とする。

* **EC-318-006 Partial inline**
  一部 text を受信していても完全 output でなければ、完全保存 claim を作らない。

* **EC-318-007 ZIP 内に Markdown 一件だけ存在**
  Transport が ZIP/tree である限り既存 ZIP lane を使用する。ZIP を解凍して単一 file import lane へ迂回しない。

* **EC-318-008 Sensitive body**
  Raw body の secret scan、privacy classification、安全保証は本 Issue の対象外。Body は EAL、test output、exception、review summary に複製しない。

## 2.9 非機能要求

* New database/schema/catalog/sidecar/background process を追加しない。
* Decision matrix は一箇所を authority とし、planning skills の drift を防ぐ。
* Workflow text は provider-first とし、dogfood-only implementation を作らない。
* Rollback は managed docs / skills / tests の revert で可能とする。
* 既存 imported evidence を rollback のため自動削除しない。
* 過去の ChatGPT output へ retroactive backfill を要求しない。

## 2.10 Grade 判定候補

| Risk fact                           |                       候補値 | 根拠                                                 |
| ----------------------------------- | ------------------------: | -------------------------------------------------- |
| `docs_only_change`                  |                     false | Shipped skills、managed scaffold content、tests も変わる |
| `runtime_behavior_change`           |                     false | CLI/import runtime は変更しない                          |
| `public_contract_change`            |                      true | Agent workflow / skill contract が変わる               |
| `migration_or_persistence_change`   |                     false | Schema、catalog、backfill なし                         |
| `rollback_difficulty_high`          |                     false | Managed text/test revert で戻せる                      |
| `security_or_privacy_sensitive`     | limited / review required | Raw body を扱うが、privacy classifierやsecret scanは追加しない |
| `multiple_scope_impact`             |                      true | Initiative / Epic / Issue planning 共通              |
| `agent_workflow_change`             |                      true | strict trigger                                     |
| `workspace_scaffold_content_change` |                      true | Installed managed skill/docs の内容が変わる               |

Strict template は workflow / skill / scaffold / compatibility への影響を strict の代表条件としています。

Critical escalation は、automatic capture、credentialed external mutation、body logging、secret scanning、安全分類、破壊的 migration、既存 evidence の自動削除が必要になった場合に再評価します。

---

# 3. `design.md` 候補

## 3.1 設計判断の要約

* `[N]` Preservation checkpoint は external ChatGPT output に対する **workflow-level contract** とし、CLI/runtime の新機能にはしない。
* `[N]` 四分岐 matrix は `spec-dock-chatgpt-authoring` が一度だけ所有する。
* `[N]` Planning skills は checkpoint invocation と scope-specific authority のみを所有する。
* `[N]` Imported external evidence、delegated draft、ZIP/tree staged evidence を別 lane とする。
* `[N]` Complete applicable source がある場合、committed preservation より前の canonical rewrite を禁止する。
* `[N]` Main orchestrator だけが EAL disposition と canonical rewrite を行う。
* `[N]` EAL は receipt metadata のみを持ち、body、secret、absolute path を持たない。
* `[N]` Issue 317 runtime、Artifact grammar、ZIP safety、delegated draft diff guard を変更しない。
* `[N]` Issue 318 は focused provider/dogfood projectionを行い、final installed rollout / PR は Issue 319へ relayする。
* `[P]` `committed=true` warning は「保存済み、warning あり」として checkpoint pass にできる。Receipt 欠落時は block する。

## 3.2 Preservation decision matrix

| Output form              | 完全性 / source                       | 必須処理                                  | Preservation status           | Gate                                | 許可される claim                                 |
| ------------------------ | ---------------------------------- | ------------------------------------- | ----------------------------- | ----------------------------------- | ------------------------------------------- |
| Standalone Markdown file | complete / available               | Approved Workbench sourceからimport     | `imported_byte_exact`         | `committed=true` + receipt 完備で pass | Workbench source と Artifact の byte identity |
| Inline text              | complete / received                | 受信 text を無編集 capture後import           | `captured_received_text`      | `committed=true` + receipt 完備で pass | Codex が受信した text の保存                        |
| Inline text              | incomplete / genuinely unavailable | Importせずexception record              | `skipped_inline_unavailable`  | 理由とnonblocking根拠があれば exception-pass | 保存不能だった事実のみ                                 |
| ZIP / tree               | available                          | Existing pack review/quarantine/stage | existing authoring-pack state | Existing ZIP laneのgateに従う           | staged evidenceの検査結果のみ                      |

### 補助ルール

* `committed=false` は block。
* `committed=true` warning は final path/hash/bytesを記録し、automatic retryしない。
* `skipped_inline_unavailable` は「importが面倒」「sourceがeligibility外」「保存を忘れた」の代替ではない。
* ZIP/tree branch へ新しい preservation status を発明しない。
* `preservation_status` と `adoption_status` は別概念。

  * 保存済みでも `rejected` にできる。
  * 保存されたこと自体は canonical 採用を意味しない。

## 3.3 三つの evidence lane

### Lane A — External preserved ChatGPT evidence

* Source: standalone complete file または captured inline text。
* Creation: `artifact import chatgpt-output`。
* Body: opaque / byte-preserving。
* Provenance: import receipt + EAL。
* Frontmatter: 不要。
* Delegated diff guard: 不適用。
* Authority: evidence-only。

### Lane B — Delegated authoring draft

* Source: SpecDock-defined delegated role が task-local authorization の下で作る draft。
* Creation: existing `new artifact <type>`。
* Body/frontmatter: existing schema 必須。
* Diff guard: 必須。
* Authority: unreviewed evidence。
* Existing rules: 変更しない。

### Lane C — ZIP/tree staged evidence

* Source: authoring pack output。
* Creation: review / quarantine / stage。
* ZIP safety: existing contract。
* Single-file import: 使用しない。
* Authority: staged evidence only。

この分離により、外部原文 import のために delegated draft の frontmatter/diff-guard を緩和する必要がなくなります。現行 delegated contract は canonical edit禁止、frontmatter、diff guard、single direct-child Artifact を要求しているため、同一 lane として扱うと契約矛盾が発生します。

## 3.4 Authority flow

```text
ChatGPT output
  |
  v
spec-dock-chatgpt-authoring
  |-- classify output form / completeness
  |-- standalone -> import
  |-- complete inline -> exact received-text capture -> import
  |-- unavailable inline -> exception record
  `-- ZIP/tree -> existing pack lane
  |
  v
Main orchestrator
  |-- verify receipt / exception evidence
  |-- record EAL preservation + adoption disposition
  |-- adopt / partially adopt / reject / defer claims
  |-- rewrite canonical requirement/design/plan
  `-- request fresh spec-reviewer
  |
  v
Fresh reviewer verdict
```

禁止される逆向き authority:

```text
ChatGPT / import / shared skill / planning skill
  -X-> EAL adopted
  -X-> canonical authority
  -X-> reviewer pass
  -X-> assurance/readiness/finish/PR state
```

## 3.5 Shared skill と planning skill の責任

### `spec-dock-chatgpt-authoring`

所有するもの:

* 四分岐 matrix
* completeness/source-availability 判定 guidance
* status semantics
* import result / warning / exception handling
* EAL handoff field guidance
* body/path secrecy
* self-claim prohibition
* stop conditions

所有しないもの:

* EAL への実書込み
* claim の採否
* canonical rewrite
* human approval
* reviewer invocation result
* lifecycle promotion

### 各 planning skill

共通 Operating Spine の差分は一工程だけにします。

```text
ChatGPT evidence received
  -> invoke shared preservation checkpoint
  -> verify checkpoint evidence
  -> review claims
  -> EAL adoption disposition
  -> canonical rewrite
  -> fresh reviewer
```

Initiative planning は Epic creation approval、Epic planning は Issue slicing / node approval、Issue planning は execution handoff を引き続き所有します。

## 3.6 EAL 記録設計

これは新しい persistent schema ではなく、既存 EAL field semantics を用いた記録契約です。

### Successful standalone / inline

必須候補:

```yaml
source_role: external_chatgpt_output
output_form: standalone_markdown | complete_inline
preservation_status: imported_byte_exact | captured_received_text
capture_boundary: workbench_source_bytes | codex_received_text
import_kind: chatgpt-output
storage_identity: blank
source: <repo-relative path>
destination: <repo-relative path>
sha256: <digest>
byte_count: <integer>
committed: true
warning_state: none | <content-free token>
adoption_status: adopted | partially_adopted | rejected | deferred
blocking: false
```

### Unavailable inline

```yaml
output_form: incomplete_or_unavailable_inline
preservation_status: skipped_inline_unavailable
reason: <content-free reason>
complete_source_available: false
blocking: false
revisit_condition: <condition or none>
```

禁止 fields:

* output body
* excerpts containing secrets
* absolute host paths
* fabricated source/destination
* fabricated hash/bytes
* upstream provider-byte identity claim

## 3.7 対象変更面

### Provider authority

* `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
* `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
* `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`
* `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
* `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
* `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
* `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`

### Matching dogfood projection

* `spec-dock/docs/workflow_spec_authoring.md`
* `spec-dock/docs/workflow_chatgpt_authoring_pack.md`
* `spec-dock/docs/authoring/chatgpt-pack.md`
* `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
* `.agents/skills/spec-dock-initiative-planning/SKILL.md`
* `.agents/skills/spec-dock-epic-planning/SKILL.md`
* `.agents/skills/spec-dock-issue-planning/SKILL.md`

現時点では、これらの provider / dogfood file は対応する同一 blob SHA を持つため、exact projection が現行 convention と判断できます。例えば provider / dogfood の `workflow_spec_authoring.md`、ChatGPT workflow、ChatGPT skill はそれぞれ同じ SHA です。

### Focused tests

* `tests/cli_runtime/test_wrappers.py`
* `tests/unit/infra/test_init_update.py`
* 必要なら dedicated workflow/skill contract test
* Existing regression:

  * `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
  * `tests/manual_tests/test_review_chatgpt_authoring_pack.py`

`test_wrappers.py` は既に fresh init 後の installed docs / skills を読み、ChatGPT skill の evidence-only、github-synced、local-context、forbidden claims を検査しています。ここが checkpoint contract の自然な focused extension point です。

Installer は対象四 skill を managed skill list に既に含めています。

## 3.8 Contract delta

| Contract                | Current                                     | Target                                                    | Compatibility               |
| ----------------------- | ------------------------------------------- | --------------------------------------------------------- | --------------------------- |
| ChatGPT authoring skill | ZIP/tree・candidate・summaryを evidence として返す  | 四分岐 preservation checkpoint を共有所有                         | additive / compatible       |
| Planning skills         | output受領後に review / EAL / canonical rewrite | その前に shared checkpoint を呼ぶ                                | additive                    |
| Workflow docs           | ChatGPT outputを広く delegated evidence と表現    | external preserved / delegated draft / ZIP staged の三 lane | clarification + additive    |
| CLI import              | Issue317 contract                           | 変更なし                                                      | unchanged                   |
| Artifact grammar        | blank coexistence                           | 変更なし                                                      | unchanged                   |
| ZIP safety              | existing review/stage                       | 変更なし                                                      | unchanged                   |
| EAL                     | existing adoption ledger                    | preservation receiptを既存fieldへ記録                           | additive narrative contract |
| Scaffold                | managed docs/skills text                    | 新しい checkpoint textを含む                                    | compatible content update   |

Breaking change は想定しません。Delegated draft の既存 contract を緩和せず、外部 evidence 用に別 lane を追加するためです。

## 3.9 Failure / recovery

| Failure                                    | 判定                     | Recovery                                        |
| ------------------------------------------ | ---------------------- | ----------------------------------------------- |
| Complete source + import `committed=false` | blocked                | 原因を解消して明示再実行                                    |
| Complete source + ineligible path          | blocked                | approved Workbench sourceを準備。unavailableへ再分類しない |
| Complete source + receipt不足                | blocked / incomplete   | receipt確認または再検証                                 |
| `committed=true` warning                   | preserved-with-warning | warning記録。自動retryなし                             |
| Complete inline capture途中失敗                | blocked                | exact received textを保持できる状態で再capture            |
| Genuine unavailable inline                 | nonblocking exception  | `skipped_inline_unavailable`記録                  |
| ZIP routed to single-file import           | contract violation     | existing pack laneへ戻す                           |
| Imported evidenceにdelegated frontmatter要求  | contract violation     | external evidence laneへ戻す                       |
| Delegated draft guardを緩和する必要が発生            | stop / design gap      | design/Epicへ戻す                                  |
| Body/absolute pathがEALへ露出                  | blocking defect        | 修正・evidence scrub・fresh review                  |
| Runtime import変更が必要                        | scope violation候補      | plan amendment、Issue317/parent contract再確認      |

## 3.10 Migration / rollback

* Database/schema migration: なし。
* Existing Artifact backfill: なし。
* Existing ChatGPT evidence の retroactive classification: なし。
* Existing delegated drafts: 変更なし。
* Existing ZIP/tree staged evidence: 変更なし。
* Rollback:

  * provider docs/skills、dogfood projection、focused tests を revert。
  * 保存済み Artifact は自動削除しない。
  * EAL の observed historical evidence は消さず、必要なら superseded disposition を記録。
* Package/fresh-init/update rollout rollback は Issue 319 の責務。

## 3.11 Epic / ADR へ戻す条件

次が必要になった場合は Issue-local 実装を停止します。

* machine-readable preservation catalog / sidecar
* automatic capture / import
* import command による EAL / canonical mutation
* raw transcript privacy / retention / secret classification
* PDF/image/directory/bundle import
* ZIP quarantine / safety contract変更
* new typed `chatgpt-output` token
* blank prefix reservation
* runtime-level mandatory authoring gate
* bodyを含む telemetry / logs
* destructive migration / automatic evidence deletion
* Issue 319 の public rollout / PR ownership変更

新しい ADR は現時点では不要です。既存 accepted ADR と親 Epic が必要な hard-to-reverse storage / authority decision を既に所有しています。

---

# 4. `plan.md` 候補

## 4.1 Strict profile に関する前提

この plan は strict obligations を満たす候補ですが、次の順序を必須とします。

1. `requirement.md` を具体化。
2. `assurance classify --stage requirement`。
3. runtime が選択した profile で `assurance compose --artifact all`。
4. composed strict template、または runtime-owned profile templateへ design / plan 候補を統合。
5. Requirement、design、plan の各 phase で fresh `spec-reviewer`。
6. EAL、Spec Authoring Gate、Grade Specialist Evidence Gate を report に記録。
7. `assurance verify` が valid になるまで S00 を開始しない。

Issue plan authoring guide も、placeholder に直接本文を書かず、classify / compose 後に profile-owned template を materialize するよう要求しています。

Classifier が Standard を返した場合:

* `authorized_profile` を strict と手書きで上書きしない。
* Standard template を維持しつつ strict 相当 gate を manual escalation として report に記録する、または
* risk facts の不足を修正し fresh classification を行う。

## 4.2 実行順序

```text
Pre-S00 Assurance / Authoring Gate
  -> S00 Baseline and contract inventory
  -> S01 Workflow/reference contract
  -> S02 Shared ChatGPT preservation kernel
  -> S03 Thin planning-skill integration
  -> S04 Projection and automated contract verification
  -> S05 Manual four-branch dogfood evidence
  -> S90 Docs impact and Issue319 ownership closure
  -> S99 Final Issue gates and deferred delivery
```

S01 が semantic authority、S02 が operational kernel、S03 が caller integration、S04 が installed/projection verification、S05 が end-to-end observed evidence です。

## 4.3 許可変更面

| Surface                         | Allowed                                             |
| ------------------------------- | --------------------------------------------------- |
| Provider workflow docs          | 上記三 file の preservation / authority / lane guidance |
| Provider skills                 | shared skill一件、planning skill三件                     |
| Dogfood projection              | 対応する七 file の provider-derived projection            |
| Tests                           | wrapper、managed asset、必要な dedicated contract tests  |
| Active Issue report / artifacts | EAL、decision、step、manual evidence、review output     |
| Active Issue planning docs      | fresh-reviewed amendment が必要な場合のみ orchestrator が変更  |

## 4.4 禁止変更

* Issue 317 runtime import implementation。
* Parser、application、publisher、presentation、Artifact allocator。
* Artifact rules / templates / typed catalog。
* ZIP/tree review/stage runtime。
* Delegated-authoring diff guard runtime。
* `README.md`、guide、public reference naming、release/migration docs。
* Package-data/fresh install/update/full-regression work。
* Issue 319 canonical node。
* Automatic capture/import。
* Automatic EAL/canonical update。
* Raw transcript privacy/secret scan。
* GitHub PR creation。
* Imported body、secret、absolute pathのreport記載。

## 4.5 仕様固定クロージャ索引

| ID      |  必須 | Spec link  | 固定期待                                                          | Defect class                              | Evidence level          | Owner       |
| ------- | --: | ---------- | ------------------------------------------------------------- | ----------------------------------------- | ----------------------- | ----------- |
| C318-01 | yes | AC-318-001 | Standalone complete fileがrewrite前に`imported_byte_exact`       | original loss / late preservation         | contract-first + manual | S01/S02/S05 |
| C318-02 | yes | AC-318-002 | Received inline textが無編集captureされ`captured_received_text`     | false byte-identity claim                 | contract-first + manual | S01/S02/S05 |
| C318-03 | yes | AC-318-003 | Genuine unavailableだけ`skipped_inline_unavailable`、path/hashなし | fabricated provenance / gate bypass       | contract-first + manual | S01/S02/S05 |
| C318-04 | yes | AC-318-004 | ZIP/treeはexisting lane、safety不変                               | unsafe ZIP bypass                         | characterization-first  | S01/S02/S04 |
| C318-05 | yes | AC-318-005 | `committed=false` blocks、committed warningはrecord/no retry    | adoption before preservation / duplicates | red-required            | S02/S04     |
| C318-06 | yes | AC-318-006 | Raw importとdelegated draftを分離、draft guard不変                   | provenance conflation                     | contract-first          | S01/S04     |
| C318-07 | yes | AC-318-007 | EALにbody/secret/absolute/self-claimなし                         | privacy / authority leak                  | red-required            | S01–S05     |
| C318-08 | yes | AC-318-008 | Matrixはshared skill一箇所、三skillはthin hook                       | policy drift                              | structural contract     | S02/S03/S04 |
| C318-09 | yes | AC-318-009 | Provider/dogfood exact projection、installed focused contract  | managed asset divergence                  | red-required            | S04         |
| C318-10 | yes | AC-318-010 | Import/validate/sync/ADR/ZIP runtime非回帰                       | runtime contract regression               | characterization-first  | S00/S04     |
| C318-11 | yes | AC-318-011 | Issue319 relay、no PR/no merge-ready claim                     | delivery ownership loss                   | inspect + manual        | S90/S99     |

## 4.6 全 step 共通 delegation contract

* Source of truth:

  * reviewed Issue requirement / design / plan
  * parent Epic requirement / design / plan
  * accepted ADR
  * Issue 317 approved requirement/design/report
* Forbidden:

  * closure expectation変更
  * parent boundary変更
  * scope外 file
  * body/secret/absolute path exposure
  * canonical authority / reviewer pass self-claim
* Required output:

  * changed files
  * Redまたは代替 evidence
  * Green verification
  * diff/refactor guardrail
  * unresolved risks
  * reportへの Ledger Note
* Stop conditions:

  * requirement/design gap
  * runtime source変更が必要
  * ZIP safety変更が必要
  * automatic behaviorが必要
  * privacy/security classificationが必要
  * Issue319 ownershipとの競合
* Reviewer:

  * docs/skill text only: fresh `spec-reviewer`
  * Python tests/scaffold behavior: fresh `code-reviewer`
  * integrated final: QA → code → spec
* Commit:

  * reviewer pass後のみ focused commit
  * report evidenceを同じ milestoneに含める
  * post-commit `git status --short`
  * push後 upstream差分を確認

## 4.7 S00 — Baseline and contract inventory

### Goal

Current docs/skills/test surface、provider/dogfood baseline、Issue317 runtime boundaryを固定する。

### Delegation

* Role: `repo-analyst` または orchestrator read-only inspection。
* Allowed:

  * report evidenceのみ。
* Forbidden:

  * provider/dogfood/source edits。
* Reviewer:

  * no source diffなら approved-no-op evidence。
  * inventory conclusionはS01開始時にspec-review対象。

### 具体ケース

#### TC318-S00-01 現行 gap

* 前提:

  * current branch の三 workflow docs と四 skills。
* 操作:

  * `imported_byte_exact`、`captured_received_text`、`skipped_inline_unavailable`、preservation checkpoint を検索。
* 期待:

  * parent design以外の target docs/skillsには四分岐 contract が未実装である。
* 証跡:

  * path inventory / `rg` result。
* Closure:

  * C318-01–08 baseline。

#### TC318-S00-02 Provider/dogfood baseline

* 操作:

  * 七 provider/dogfood pair の hash / byte equality を比較。
* 期待:

  * baseline equalityを記録。
* Closure:

  * C318-09。

#### TC318-S00-03 Runtime baseline

* 操作:

  * existing import focused testsとZIP review testを実行。
* 期待:

  * baseline pass、または既知 failure を source変更前に分類。
* Closure:

  * C318-04/C318-10。

### Gate

* Baseline report entry。
* Unexpected existing regression があれば S01 へ進まない。

## 4.8 S01 — Workflow / reference preservation contract

### Goal

Provider三 docs に、三 evidence lane、四分岐、checkpoint order、authority boundaryを定義する。

### Delegation

* Role: `doc-writer`
* Allowed:

  * provider三 docsのみ
* Forbidden:

  * skills、dogfood、runtime、public README/reference
* Required verification:

  * structural inspection
  * terminology consistency
  * `git diff --check`
* Reviewer:

  * fresh `spec-reviewer`

### 具体ケース

#### TC318-S01-01 四分岐

* 操作:

  * 三 docs の役割分担を点検。
* 期待:

  * user workflow docに四分岐。
  * reference docにstandalone対ZIPの技術境界。
  * common workflow docにcanonical rewrite前 checkpoint。
  * status spellingが親設計と完全一致。
* Closure:

  * C318-01–04。

#### TC318-S01-02 Lane separation

* 期待:

  * external imported evidenceにdelegated frontmatter/diff guardを要求しない。
  * delegated authoring sectionの現行 requirementsは残る。
* Closure:

  * C318-06。

#### TC318-S01-03 Authority / secrecy

* 期待:

  * EAL receipt fieldsがcontent-free。
  * body、secret、absolute path、自動採用が禁止。
* Closure:

  * C318-07。

#### TC318-S01-04 Lifecycle order

* 期待順:

  * output received
  * preservation checkpoint
  * EAL disposition
  * canonical rewrite
  * fresh reviewer
* Closure:

  * C318-01/02/05/07。

### Step closure

* C318-01–07 の docs semantics。
* Fresh spec-reviewer pass後にcommit。
* Skill-specific実装はS02へ残す。

## 4.9 S02 — Shared ChatGPT preservation kernel

### Goal

`spec-dock-chatgpt-authoring` に一箇所だけ operational decision matrix を実装する。

### Delegation

* Role: `doc-writer`
* Allowed:

  * provider shared skill一件
* Forbidden:

  * planning skills、runtime、dogfood
* Verification:

  * exact status / branch / stop condition inspection
  * forbidden claims inspection
* Reviewer:

  * fresh `spec-reviewer`

### 具体ケース

#### TC318-S02-01 Standalone file

* Input:

  * complete standalone Markdown。
* Expected:

  * Workbench source確認→import→receipt検証→`imported_byte_exact`→planning skillへ返却。
* Must not:

  * canonical rewrite、EAL採用をself-claim。
* Closure:

  * C318-01/C318-07。

#### TC318-S02-02 Complete inline

* Input:

  * complete received text。
* Expected:

  * exact received text capture→import→`captured_received_text`。
* Must not:

  * provider original bytes claim。
* Closure:

  * C318-02。

#### TC318-S02-03 Unavailable inline

* Input:

  * complete source genuinely unavailable。
* Expected:

  * `skipped_inline_unavailable`、reason、no path/hash。
* Negative:

  * import failureやeligibility failureを unavailable と扱わない。
* Closure:

  * C318-03/C318-05。

#### TC318-S02-04 ZIP/tree

* Expected:

  * existing review/quarantine/stage commandへroute。
  * import commandを案内しない。
* Closure:

  * C318-04。

#### TC318-S02-05 Import result matrix

* Cases:

  * `committed=true`, no warning
  * `committed=true`, warning
  * `committed=false`
  * missing receipt
* Expected:

  * pass / pass-with-warning / blocked / blocked。
  * automatic retryなし。
* Closure:

  * C318-05。

#### TC318-S02-06 Forbidden claims

* Expected:

  * adoption、reviewer、readiness、finish、PR claimなし。
  * body/absolute pathをrequired outputにしない。
* Closure:

  * C318-07。

### Step closure

* C318-01–05、07、08のshared kernel部分。
* Fresh spec-reviewer pass後commit。

## 4.10 S03 — Thin planning-skill integration

### Goal

Initiative / Epic / Issue planning skill に共通 checkpoint invocation を追加し、scope固有 authorityを維持する。

### Delegation

* Role: `doc-writer`
* Allowed:

  * provider planning skills三件
* Forbidden:

  * matrix複製、shared skill変更、manual skills変更
* Reviewer:

  * fresh `spec-reviewer`

### 具体ケース

#### TC318-S03-01 Invocation placement

三 skill それぞれで:

* ChatGPT output受領後
* claim review / EAL disposition / canonical rewrite前
* shared preservation checkpointを呼ぶ

ことを確認する。

Closure: C318-01/02/03/05/08。

#### TC318-S03-02 No matrix duplication

* Planning skillには四 status / branch の詳細表を置かない。
* Shared skillへの明示参照だけを置く。
* Closure:

  * C318-08。

#### TC318-S03-03 Scope ownership

* Initiative:

  * Initiative docs、Epic approvalを所有。
* Epic:

  * Epic docs、Issue slicing / approvalを所有。
* Issue:

  * Issue docs、execution handoffを所有。
* 全skill:

  * EAL、canonical rewrite、fresh reviewerを維持。
* Closure:

  * C318-07/C318-08。

#### TC318-S03-04 Stop propagation

* Shared checkpointがblockedならplanning skillもcanonical rewriteへ進まない。
* `skipped_inline_unavailable`は理由確認後だけ進める。
* Closure:

  * C318-03/C318-05。

### Step closure

* C318-08完了。
* Scope ownership regressionなし。
* Fresh spec-reviewer pass後commit。

## 4.11 S04 — Projection and automated contract verification

### Goal

Provider changesをdogfoodへexact projectionし、installed/wrapper/compatibility testsを追加する。

### Delegation

* Role: `dev-coder`
* Allowed:

  * matching dogfood七 files
  * focused test files
* Forbidden:

  * provider semanticsの再設計
  * runtime import source
  * package/public docs
* Reviewer:

  * fresh `code-reviewer`
  * integrated text alignmentはfresh `spec-reviewer`

### 具体ケース

#### TC318-S04-01 Installed wrapper contract

Fresh init fixtureで installed docs/skillsを読み、次をassertする。

* shared skillに三status。
* complete sourceのcheckpoint-before-rewrite。
* ZIP existing lane。
* no self-claims。
* no body/absolute path requirement。
* planning skill三件がshared checkpointを参照。

Closure: C318-01–09。

#### TC318-S04-02 Centralization

* 三 planning skillがshared skillを参照。
* 四分岐 status detailsが各 planning skillへ複製されていない。
* Closure:

  * C318-08。

#### TC318-S04-03 Provider/dogfood identity

* 七 pairをbyte compare。
* Expected:

  * 7/7一致。
* Closure:

  * C318-09。

#### TC318-S04-04 Runtime import regression

候補 command:

```bash
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
```

Expected:

* byte preservation
* blank coexistence
* content-free output
* validate/sync/ADR mirror non-regression

Closure: C318-10。

#### TC318-S04-05 ZIP lane regression

候補 command:

```bash
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
```

Expected:

* existing ZIP safety unchanged。
* Single-file importとの結線なし。

Closure: C318-04/C318-10。

#### TC318-S04-06 Runtime source non-diff

* Issue317 parser/application/publisher/presentationとauthoring-pack runtimeに意味diffがない。
* Closure:

  * C318-10。

### Verification queue

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
uv run mypy src
git diff --check
```

Exact selector分割は implementation-local delta ですが、上記四 test surface は省略しません。

### Step closure

* C318-04、06、08、09、10。
* Fresh code-reviewer → fresh spec-reviewer。
* Commit / push / clean evidence。

## 4.12 S05 — Manual four-branch dogfood evidence

### Goal

Safe synthetic outputで四 branchを観測し、EAL recordとcanonical rewrite順序を確認する。

### Owner

* Main orchestrator。
* Runtime/skill source変更なし。
* Bodyは安全なsynthetic Markdownだけを使う。

### 具体ケース

#### TC318-S05-01 Standalone

* Workbenchにsafe complete `.md`。
* Dogfood import。
* Hash/bytes/source survivalを確認。
* EAL:

  * `imported_byte_exact`
  * repo-relative source/destination
  * hash/bytes
  * adoption disposition
* Canonical rewriteはreceipt記録後。
* Closure:

  * C318-01/C318-07/C318-11。

#### TC318-S05-02 Inline

* Safe complete inline stringを用意。
* 同じ文字列を無編集capture。
* Import後にcapture fileとArtifactを比較。
* EAL:

  * `captured_received_text`
  * provider byte identity not claimed
* Closure:

  * C318-02/C318-07。

#### TC318-S05-03 Unavailable

* Complete sourceが存在しないsynthetic scenario。
* EAL:

  * `skipped_inline_unavailable`
  * reason
  * no path/hash
* Closure:

  * C318-03/C318-07。

#### TC318-S05-04 ZIP/tree

* Existing safe ZIP fixtureをreview/stage laneへ通す、または既存test evidenceをmanual inspection。
* Import destinationが作られていない。
* Closure:

  * C318-04。

#### TC318-S05-05 Failure gate

* Safe fixtureでsource eligibility failureまたはfault-injected `committed=false` outcome。
* Canonical targetの変更なし。
* Closure:

  * C318-05。

### Step closure

* C318-01–05、07、11のmanual evidence。
* EAL / decision / OAL / step ledger更新。
* Fresh spec-reviewer。
* Report/evidence commit。

## 4.13 S90 — Docs impact resolution

Issue 317 の path ledger は、workflow docs / skills を Issue 318、README/reference/migrationを Issue 319へ既に割り当てています。

### Path disposition

| Surface                                         | Disposition                 |
| ----------------------------------------------- | --------------------------- |
| Provider workflow三 docs                         | Issue318 update             |
| Provider四 skills                                | Issue318 update             |
| Matching dogfood七 files                         | Issue318 focused projection |
| Wrapper / managed asset tests                   | Issue318 update             |
| Artifact rules / templates                      | approved-no-op              |
| Runtime import source                           | approved-no-op              |
| ZIP runtime                                     | approved-no-op              |
| Root README                                     | defer Issue319              |
| docs README / guide / reference naming          | defer Issue319              |
| migration / release note                        | defer Issue319              |
| package-data / fresh init / update final matrix | defer Issue319              |
| full pytest / global static repair              | defer Issue319              |
| final Epic PR                                   | defer Issue319              |

### Cases

* `TC318-S90-01`: 全pathに disposition / owner / reason / dependency / blocking を付ける。
* `TC318-S90-02`: grouped wildcardだけで済ませず、実pathを列挙する。
* `TC318-S90-03`: fresh spec-reviewerがIssue318/319境界を確認する。

### Gate

* Updateがあればreview/commit。
* Defer/no-opは根拠付き approved-no-op。
* S90 pass前にS99へ進まない。

## 4.14 S99 — Final Issue quality gates

### Required checks

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
uv run mypy src
git diff --check

./spec-dock/scripts/spec-dock assurance verify --issue iss-00318 --format json
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock active show
```

`sync` は必要性を判断し、必要なら実行、不要なら approved-no-op 根拠を report に残します。

Issue 319 が full Epic regression を所有するため、Issue 318 の S99 で full `uv run pytest` や全 global lint repair を暗黙に引き取らない。未実行項目は owner、dependency、nonblocking 根拠を relay します。Issue 317 reportも full/global gateを Issue 319へ残しています。

### Final reviewer order

1. `qa-reviewer`

   * C318-01–11 coverage
   * manual four-branch adequacy
   * missing integration test判断
2. issue-wide `code-reviewer`

   * test sensitivity
   * managed asset/projection correctness
   * runtime non-diff
3. `spec-reviewer`

   * requirement/design/plan/report/docs/skills/tests alignment
   * parent Epic/ADR/Issue317/Issue319 boundary
   * EAL / authority / secrecy

いずれかが fail、unavailable、denied、waived、provisional なら pass 扱いせず、owner stepへ戻します。

### Deferred PR Delivery Gate

Report candidate:

```text
target:
  iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr

dependency:
  iss-00317 -> iss-00318 -> iss-00319

reason:
  One final Epic PRへpackage、fresh init/update、public docs、
  full regression、final QA/code/spec review、PR deliveryを集約する。

claim_boundary:
  Issue319のPR Delivery / Merge Preparation完了まで
  PR-ready / merge-ready / merge-preparedを主張しない。

remaining_gates:
  package data
  fresh init/update
  public README/reference/migration
  full pytest/global static
  provider/dogfood/installed inventory
  final Epic QA/code/spec
  PR creation/observation/merge preparation
```

### Final commit gate

* C318-01–11に unresolved `blocked` / `stale` なし。
* Material findingの disposition 完了。
* Final reportをcommit/push。
* `git status --short` clean。
* upstream left/right `0 0`。
* Active Issue一致。
* Per-Issue PRは作らない。
* 上記完了後にだけ spec-manager が Issue finish 可否を判断する。

---

# 5. Evidence Adoption Ledger 採用候補

| Candidate ID | Disposition                     | Claim                                                                                      | Target                     | 理由 / 次アクション                                                         |
| ------------ | ------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------- | ------------------------------------------------------------------- |
| EAL-318-C01  | `adopted`                       | Standalone / complete-inline / unavailable-inline / ZIP-tree の四分岐と三status                  | requirement, design        | Parent E-RQ-024 / E-AC-016 / designで固定済み                            |
| EAL-318-C02  | `adopted`                       | Complete applicable sourceのpreservationはcanonical rewrite前checkpoint                       | requirement, design, plan  | Parent exact behavior                                               |
| EAL-318-C03  | `partially_adopted`             | 四分岐をshared skillに置きplanning skillsから呼ぶ                                                     | design                     | Matrix共有は採用。各planning skillへの詳細複製は棄却                                |
| EAL-318-C04  | `adopted`                       | External imported evidenceはdelegated draftではない                                             | requirement, design        | Issue317 relayと現行delegated contractの矛盾回避                            |
| EAL-318-C05  | `rewritten / partially_adopted` | Byte-exact claim                                                                           | design                     | StandaloneはWorkbench source↔Artifactを直接境界とする。Inlineはreceived textだけ |
| EAL-318-C06  | `rewritten / partially_adopted` | Import failure hard gate                                                                   | requirement, design        | `committed=false`はblock。`committed=true` warningは保存済みとしてwarning記録   |
| EAL-318-C07  | `rewritten / partially_adopted` | Strict grade                                                                               | requirement, plan          | Brief要求に従いstrict候補を作るが、parentはStandard候補。Assurance結果を未検証のまま確定しない    |
| EAL-318-C08  | `adopted`                       | Main orchestrator single-writer、EAL/canonical/reviewer authority isolation                 | all                        | Existing workflow/skill authority contractに一致                       |
| EAL-318-C09  | `adopted`                       | EALにbody/secret/absolute pathを出さない                                                         | requirement, design, tests | Prompt constraint、Issue317 content-free contract                    |
| EAL-318-C10  | `rejected`                      | Automatic capture/import/EAL/canonical mutation                                            | none                       | Parent非スコープ、authority boundary違反                                    |
| EAL-318-C11  | `rejected`                      | `chatgpt-output` typed token、prefix reservation、frontmatter、sidecar、catalog                | none                       | Accepted ADRとIssue317に反する                                           |
| EAL-318-C12  | `rejected`                      | Imported evidenceへdelegated frontmatter/diff-guardを適用する、または既存guardを緩和する                    | none                       | External raw evidenceとdelegated draftの責務混同                          |
| EAL-318-C13  | `rejected`                      | ZIP/treeをsingle-file importへrouting                                                        | none                       | Existing safety laneを弱める                                            |
| EAL-318-C14  | `deferred`                      | README、guide、reference naming、migration、package、fresh init/update、full regression、final PR | Issue319                   | Parent planとIssue317 S90 ownershipに従う                               |
| EAL-318-C15  | `deferred`                      | Raw transcript privacy/classification、secret scan、retention                                | follow-up Epic/ADR         | 本Issueの明示非スコープ                                                      |
| EAL-318-C16  | `deferred`                      | PDF/image/directory/bundle import、automatic runtime enforcement                            | follow-up Epic/ADR         | Parent storage/import boundaryを変更する                                 |
| EAL-318-C17  | `rejected`                      | ChatGPT/import/skillによるadoption、reviewer、readiness、finish、PR self-claim                    | none                       | Existing forbidden claimsを維持                                        |

---

# 6. 矛盾・リスク・判断半径

## 6.1 Grade の矛盾

**確認済み差分**

* Parent W4: Standard候補。
* Task brief: strict-profile plan。
* Current Issue: unclassified placeholder。

**推奨 disposition**

* requirement risk factsはstrict triggerを明示する。
* 実 profile は runtime classification に委ねる。
* Standardなら strict manual escalationをreportに記録する。
* `authorized_profile` を手編集で偽装しない。

## 6.2 Dogfood parity と Issue 319 ownership

一見すると、Issue 318 の dogfood parity と Issue 319 の final parity が重複します。

推奨する切り分け:

* Issue 318:

  * 対象七 file の direct dogfood projection
  * focused installed/wrapper contract
  * manual workflow scenario
* Issue 319:

  * package-data
  * fresh init/update
  * public docs inventory
  * installed consumer inventory
  * full/global regression
  * final Epic PR

これは親 W4/W5 と Issue317 path ledgerを同時に満たします。

## 6.3 Workflow textだけでは強制できない

本設計は docs / skills / contract tests による workflow enforcement です。CLI/runtime が canonical write を技術的に阻止するわけではありません。

したがって、受け入れ条件が証明するものは:

* shipped instructions が明確であること
* planning skills が正しい順序を持つこと
* tests が契約 drift を検出すること
* manual scenario で workflow が実行可能なこと

であり、任意の外部 actor が instructions を無視できないことではありません。

Runtime mandatory enforcement が必要と判明した場合は親 Epicへ戻す必要があります。

## 6.4 Preservation status と adoption status の混同

* `imported_byte_exact` / `captured_received_text` は保存状態。
* `adopted` / `partially_adopted` / `rejected` / `deferred` は主張の採否。

「原文を保存したが、内容は全棄却」が正当な結果です。この二つを一fieldに統合してはいけません。

---

# 7. 仮定・不確実性・未検証主張

## 仮定

* Issue 318 の実装時も Issue 317 の import result に `committed`、repo-relative paths、SHA-256、byte count、warning state が存在する。
* Provider→dogfood projection は現行と同様に exact content mirror として扱う。
* Existing wrapper / init-update test frameworkへ focused assertionsを追加できる。

## 不確実性

* `authorized_profile` はまだ未分類。
* Strict specialist evidence、fresh spec-reviewer verdict は未取得。
* Exact test関数名、最小 `pytest -k` selector、commit分割は実装時のrepository状態で調整が必要。
* `committed=true` warningをcheckpoint passとする扱いは、Issue317のaccepted runtime semanticsに強く基づくIssue-local design候補であり、canonical design reviewが必要。
* Semantic completenessの判定基準は、file sizeやencodingではなくorchestrator判断とした。自動判定規則は本Issueでは定義していない。

## 未検証主張

* 本分析では test command を実行していない。
* Issue 317 reportに記録された test passは、approved repository evidenceとして参照したものであり、本応答で独立再実行した結果ではない。
* Repository mutation、canonical doc更新、assurance compose、reviewer pass、commit、push、Issue finish、PR作成は行っていない。
