---
種別: 実装報告書（Issue）
ID: "iss-00317"
タイトル: "Byte Preserving ChatGPT Output Artifact Import"
関連GitHub: ["#317"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00317 Byte Preserving ChatGPT Output Artifact Import — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-317-001 | resolved | interpretation | user / accepted ADR / orchestrator | `chatgpt-output`をtyped tokenまたはreserved prefixにするか | typed token+reservation; import kind+blank storage; sidecar provenance | Import kindとして扱い、existing blank grammarとtemplate-created blankを共存させる | User decisionとaccepted ADRによりparent contractが確定済み | applied | Epic ADR、requirement RQ-317-006/AC-317-004 | Design/implementationで再オープンしない |
| D-317-002 | resolved | scope | ChatGPT 5.6 Pro / repo-analyst | Planning候補の過剰なconsumer/alias保証 | 全Artifact inode alias scan; source non-destructive boundary; universal consumer compatibility; verified consumers限定 | Existing formal Artifact全件のinode alias scanは採用せず、sourceをrename/hard-linkしない。Consumer保証はvalidate/sync/ADR mirrorへ限定しdelegated-authoring laneをIssue318へrelay | 親contractを満たす最小実装とcurrent consumer inventoryに整合 | promoted_to_design | Raw evidence SHA、repo analysis、requirement RQ-317-004/012、design DES-317-003/006/008 | Design fresh review。Pass後planへ反映 |
| D-317-003 | resolved | implementation | dev-coder / code-reviewer | 検証済みtemp descriptorではなくtemp pathnameをpublishすると、検証後path replacementで未検証/source inodeを公開できる | Pathname hard-link; Darwin descriptor clone; Linux descriptor-backed link; unsupported host fail-closed | Darwinは`fclonefileat(staged_fd, ...)`、Linuxは`/proc/self/fd/<fd>` follow-linkを使い、他host/filesystemは`publication_unsupported`。Cleanupはtemp path inodeがstaged fdと一致する場合だけunlink | DES-317-006が許容するnative no-replace adapterのissue-local具体化。Verified descriptor binding、atomic no-replace、source inode independenceを最小境界で満たす | applied | Darwin live probe、pathname replacement/source-alias Red、focused 42 pass、IMPLEMENT-S02-r4 pass | Linux実動は後続CI/final gateで確認。Adapter置換時は同じ観測契約を維持 |
| D-317-004 | resolved | implementation | dev-coder | `destination_exists`を返すadapterがcandidateを作らない異常時は、rescanだけでは同じcandidateを無限に再試行し得る | Allocator exhaustionだけに依存; 任意の小さい上限; current candidate spaceと同じ100回上限 | Publication attemptをbase + `01..99`に一致する100回へ制限し、超過時は`artifact_publication_retry_exhausted`でfail closed | Current suffix grammarと一対一で、外部writer競合を吸収しつつ異常adapterでも有限停止する。将来grammar変更時の同期見直しを明示する | applied | `import_artifact.py`、TC317-S04-02 retry/suffix exhaustion、deterministic suite 3連続pass、IMPLEMENT-S04-r1 pass | Suffix grammarを拡張する場合はretry boundも同時更新 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-317-001 | partially_adopted | ChatGPT 5.6 Pro GitHub-synced planning evidence | requirement/design/plan | Parent trace、blank coexistence、opaque bytes、verified publish、failure matrix、Issue318/319 relay、step/closure seedを採用。Exact module/field/error、4-pass hash、universal consumer claim、hard-link inventoryはauthority化しない。Post-commit semanticsとadapter候補はcurrent contractへ書き直した | `artifacts/20260713t124754z-research-chatgpt-5-6-pro-issue-planning-evidence.md`; SHA-256 `8f05a598ea90385f1f0870973c8090555816af816d22dd7474e4c6501435f105` | Requirement/design/planへ統合済み。Plan fresh review |
| EAL-317-002 | adopted | current repo/parent inventory + read-only repo-analyst | requirement/design | Source placement、blank parser/allocator、lock-before-allocation gap、validator/sync/ADR behavior、delegated-authoring incompatibilityをcurrent sourceで確認しDES-317-003/004/008へ反映 | Parent Epic/ADR、`domain/artifacts.py`、`application/create_artifact_doc.py`、validation/sync/delegated-authoring callsites | Design fresh review。Pass後plan closureへ反映 |
| EAL-317-003 | adopted | S05 dogfood `artifact import chatgpt-output` manual capture | implementation/report evidence | Current Workbenchのsafe non-secret Markdownをdogfood runtimeでactive Issueへimportし、source/final SHA-256・125 bytes一致、source残存、blank filename、validate passを実測。Artifactはevidence-onlyでcanonical authority/provenanceを自己主張しない | `artifacts/20260713t161729z-chatgpt-output-issue-317-s05-manual-dogfood.md`; SHA-256 `0231085b3f8006f8fee551d3fe71a6398e1924dbd6170c6ae9d1e3acb206af30`; CLI JSON、`cmp`、`validate` | Issue318へworkflow relay、Issue319へdistribution/public docs/full gate/PR relay。S90/S99 fresh spec reviewで追跡性を確認 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-317-001 | ChatGPT原文をsource保持・bytes不変・no-overwriteでArtifact evidence化 | Path safety、collision、output secrecy、consumer compatibility、Issue318/319 relay | Binary publisherをgeneral transaction/catalogへ拡張するriskをnon-scopeで抑制 | Requirement r2 pass（findingsなし、confidence 0.98） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent Epic/accepted ADR、GitHub-synced GPT-5.6 Pro evidence、current Artifact runtime/tests、repo-analyst | Product open questionなし。r1 P1 collision終端矛盾とP2 premature promotionを修正 | partially_adopted/re-written | passed | no | promote |
| design | Reviewed requirement r2 pass、GPT evidence、repo inventory、assurance standard/normal | r1のsource再検証、lock境界、overbroad alias inventoryを修正。Product open questionなし | partially_adopted/re-written | passed | no | promote |
| plan | Reviewed design r2 pass、GPT evidence、issue-plan schema | r1不足とr2 command/assurance gateを修正 | partially_adopted/re-written | passed | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used。ChatGPT 5.6 ProのGitHub-synced planning evidenceを取り込み、canonical requirement/design/planへ部分採用・再記述した。
- 未使用の場合:
  - N/A。委任ドラフトは`artifacts/20260713t124754z-research-chatgpt-5-6-pro-issue-planning-evidence.md`として保存し、EAL-317-001で採否を管理した。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT 5.6 Pro | iss-00317 | `artifacts/20260713t124754z-research-chatgpt-5-6-pro-issue-planning-evidence.md` | Parent Epic/ADR、Issue scaffold、current Artifact runtime/tests、Issues315/316 | `requirement.md`,`design.md`,`plan.md` | partially_adopted | [`requirement.md`, `design.md`, `plan.md`] | passed | Requirement/design/plan candidates rewritten into canonical contracts | Exact internal names、overbroad alias/consumer guarantees、unverified test/pass claims | none | passed | promote |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- `artifact import chatgpt-output`を独立CLI leafとして追加し、Workbench direct-childの単一Markdownをopaque bytesのままsourceを残してblank Artifactへno-overwrite copyする。
- Shared allocation、source stability、descriptor-bound publish、collision/fault committed semantics、content-free output、consumer compatibility、provider/dogfood projectionをS01–S05で閉じた。ChatGPT First workflowはIssue318、public distribution/docs/final Epic PRはIssue319へ明示relayする。

## 実装記録（セッションログ） (必須)
- S01–S05、S90、S99のobserved Red/Green/Refactor、closure delta、reviewer、commit証跡は本書の`Step Evidence` managed sectionへ時系列で統合した。
- Required closure aliasは`TC317-*`から`C317-01–11`へ各stepで明示しており、plan amendmentを要するclosure expectation変更はない。

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| User request invoking Epic Execution / Issue Planning / Issue Execution workflows | current Work3 linked worktree | iss-00317 | current session | spec-manager、dev-coder、code-reviewer、qa-reviewer、spec-reviewer、workflow-defined read-only specialists | Active repo/worktree、active SpecDock scope、documented role responsibilityのみ。Destructive/scope expansion/external publish/private system/out-of-workflow roleは除外 | Issue完了、session終了、scope変更、host conflict、user revocation | none | Workflow内を続行。例外は別確認 |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | Shared runtime/create behaviorとtests | dev-coder | Plan S01のArtifact shared allocation subset | Reviewed requirement/design/plan、parent ADR | `create_artifact_doc.py`とfocused runtime tests | Import CLI/publisher、docs、Issue318/319、unrelated refactor | TC317-S01-01/02、focused tests、diff check | Public contract change、scope外変更、unexpected regression | Changed files、Red/Green、commands、risk、Ledger Note | passed |
| S02 | delegated | Filesystem safety、opaque staging、source stability、no-replace boundary | dev-coder | Plan S02 guard/port/adapter/tests | Reviewed requirement/design/plan、S01 commits | Narrow application contracts/port、infra guard/publisher、focused tests | CLI wiring、presentation、workflow/docs、Issue318/319、unsafe fallback | TC317-S02-01–04、focused tests、diff check | Safe no-replace unavailable、boundary ambiguity、scope外変更 | Changed files、Red/Green、fault matrix、risk、Ledger Note | passed |
| S03 | delegated | Public CLI vertical sliceとcontent-free result contract | dev-coder | Plan S03 parser/application/presentation/CLI tests | Reviewed requirement/design/plan、S01/S02 commits | CLI parser/registry/bootstrap、new handler/use case/contracts、presentation、focused tests | Publisher semantics、typed reservation/template、workflow/docs、Issue318/319 | TC317-S03-01–04、focused tests、help inspection、diff check | Existing node import/global JSON change、body/path leak、scope外変更 | Changed files、Red/Green、help/output、risk、Ledger Note | passed |
| S04 | delegated | Collision/fault/post-commit semantics hardening | dev-coder | Plan S04 import/shared helper/publisher/presentation/tests | Reviewed requirement/design/plan、S01–S03 commits | Import application/publisher/presentation、focused concurrency/fault tests、meaning-preserving S01 helper correction | New lock、unbounded retry、final rollback、docs/workflow/dogfood/Issue318/319 | TC317-S04-01–04、3 repeat runs、affected CLI tests、diff check | Flaky sleep test、retry ambiguity、existing bytes mutation、scope外変更 | Changed files、Red/Green、fault matrix/repeat logs、risk、Ledger Note | passed |
| S05 | delegated | Existing consumer compatibilityとprovider/dogfood projection | dev-coder | Plan S05 runtime regression/projection subset | Reviewed requirement/design/plan、S01–S04 commits | Focused validation/sync/ADR/delegated-authoring tests、provider-generated dogfood runtime | Public docs/skills、Issue318/319、manual evidence interpretation、unrelated generated assets | TC317-S05-01/02、provider/dogfood diff、focused regressions、diff check | Consumer contract変更、provider/dogfood authority衝突、scope外generated diff | Changed files、characterization/Green、projection diff、risk、Ledger Note | passed |
| S99-STATIC-REPAIR | delegated | Final static gateでIssue-local mypy/format failureを検出 | dev-coder | Issue317 changed source/testsの型/format修正だけ | Reviewed requirement/design/plan、S01–S90 commits、full unit/CLI pass | `commands/artifact_import.py` mypy最小修正、Issue317 changed testsのRuff format | Pre-existing `scripts/authoring-pack/*`、behavior変更、new feature、docs/workflow/Issue318/319 | `uv run mypy src`、targeted Ruff、affected tests、diff check | Behavior/contract変更、scope外format churn、test regression | Changed files、root cause、commands/results、no material decision | passed |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Setup/duplicate scan/allocation/exact checkをexisting create lock内へ移し、race/exhaustion/release testsを追加 | `src/.../application/create_artifact_doc.py`; `tests/cli_runtime/test_runtime_new_doc_s09.py` | Red 1 failed、Green focused 32 passed、CLI new 19 passed、validation 8 passed/1 skipped、diff check pass | code-review r1 failed、r2 passed | External writer atomic publishはplanned S04、import wiringはS03 | accepted; no material plan deviation |
| S02 | dev-coder | Workbench guard、opaque stage/rehash、descriptor-bound no-replace publish、committed warning、inode-aware cleanupを追加 | `application/contracts.py`; `application/ports.py`; `infra/binary_artifact_publisher.py`; focused application/infra tests | Initial Red 34 failed、Green 42 passed。Relevant regressions 81 passed/5 skipped、wide infra 236 passed後dogfood mirror gap 1件。Ruff/diff check pass | code-review r1/r2/r3 failed、fresh r4 passed | Linux descriptor-backed primitiveはDarwin上で未実動。Dogfood mirrorはS05/Issue319 delivery対象 | accepted; D-317-003をissue-local implementation decisionとして適用、plan closure変更なし |
| S03 | dev-coder | `artifact import chatgpt-output` parser→application→publisher→presentationを結線し、blank naming/byte identity/content-free outputを公開 | `application/contracts.py`; new `application/import_artifact.py`; CLI parser/registry/bootstrap; new command; presentation; 3 focused test files | Red 9 failed、focused 13 passed、regression 178 items exit 0、prior 142 passed、manual help/Ruff format+check/diff check pass | fresh code-review r1 passed | S04 collision/fault hardening、Linux live primitive、dogfood projectionは未実施 | accepted; no material plan deviation |
| S04 | dev-coder | Shared create lock内でcollisionを再scanし、100候補のbounded retry、pre/post-publish fault分類、committed warningを追加 | `application/contracts.py`; `application/import_artifact.py`; `infra/binary_artifact_publisher.py`; S04 CLI/presentation tests | Initial 8 failed/6 passed、focused 63 passed、deterministic 25 passedを3連続、S02/S03回帰58 pass、S01回帰32 pass、mypy/Ruff/diff check pass | fresh code-review r1 passed | Linux descriptor publication live検証はS02から継続。Suffix grammar変更時は100回上限も同期必要 | accepted; D-317-004 applied、plan closure変更なし |
| S05 | dev-coder | Invalid UTF-8 raw import後のvalidate/sync/ADR mirror不変性をcharacterizeし、S01–S04 runtime 10ファイルをdogfoodへbyte-equivalent projection | 10 dogfood runtime files; `tests/cli_runtime/test_artifact_import_chatgpt_output.py` | Characterization時刻差分を意味保存で正規化後Green、focused 85 passed、dogfood validate pass、provider/dogfood cmp 10/10、Ruff/diff check pass | fresh code-review r1 passed | Manual captureはorchestrator実施済み。Public docs/workflow/package parityはIssue318/319 relay | accepted; no material implementation decision |
| S99-STATIC-REPAIR | dev-coder | Mypy例外変数shadowを局所renameし、Issue317 test 3ファイルをRuff整形、dogfood commandをexact re-projection | Provider/dogfood `commands/artifact_import.py`; 3 focused test files | `mypy src` 147 pass、Issue changed 17 files Ruff check/format pass、affected 111 pass、projection follow-up 12 pass、cmp/diff check pass | final QA pass、final code-review pass | Full Ruffのpre-existing `scripts/authoring-pack/*` 2 filesはIssue319 full gateへrelay | accepted; behavior/API/contract変更なし |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| N/A | Delegation available; parent source implementation prohibited by plan | N/A | N/A | N/A | N/A | N/A | N/A | Not used |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `lite` | not applicable | not applicable | Assurance classified standard/normal | not applicable | not applicable |
| `standard` | system-architect / implementation-planner / manual fallback | used | ChatGPT 5.6 Pro evidence、repo analysis、canonical design/plan | passed | ready |
| `strict` | not applicable | not applicable | No hard trigger | not applicable | not applicable |
| `critical` | not applicable | not applicable | No critical trigger | not applicable | not applicable |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| PLANNING-REQ-r1 | requirement alignment | spec-reviewer | superseded | failed | no | report-only correction then fresh re-review | P1: transient publish collisionとterminal failureの矛盾。P2: D-317-002 premature promotion。`gpt-5.6-sol`/medium、confidence 0.95 |
| PLANNING-REQ-r2 | requirement alignment | spec-reviewer | fresh | passed | no | promote | findingsなし。r1 findings解消、`gpt-5.6-sol`/medium直接観測、confidence 0.98 |
| PLANNING-DES-r1 | design alignment | spec-reviewer | superseded | failed | no | design correction then fresh re-review | P1: source再hashが任意、Artifacts setupがlock外、既存Artifact全件inode scanの過剰要件。`gpt-5.6-sol`/medium直接観測、confidence 0.98 |
| PLANNING-DES-r2 | design alignment | spec-reviewer | fresh | passed | no | promote | r1 findings解消、findingsなし。`gpt-5.6-sol`/medium直接観測、confidence 0.98 |
| PLANNING-PLAN-r1 | plan executability | spec-reviewer | superseded | failed | no | plan correction then fresh re-review | P1: premature approved、S90欠落、test-card/pre-evidence不足、node import/missing-source coverage、dogfood scope過広、finish/deferred PR gate不足。`gpt-5.6-sol`/medium直接観測、confidence 0.99 |
| PLANNING-PLAN-r2 | plan executability | spec-reviewer | superseded | failed | no | command/gate correction then fresh re-review | P1: validate/sync/active showのunsupported `--format json`、pre-S01 assurance source binding gate欠落。`gpt-5.6-sol`/medium、confidence high |
| PLANNING-PLAN-r3 | plan executability | spec-reviewer | fresh | passed | no | promote | findingsなし。r1/r2 fixes維持、assurance verify valid。Direct invocation `gpt-5.6-sol`/medium、confidence 0.96 |
| PRE-S01-ASSURANCE | source binding and execution readiness | spec-manager | fresh | passed | no | execute approved plan | `assurance classify --stage requirement --issue iss-00317`後、`assurance verify --issue iss-00317 --format json`が`status=valid`。Guidanceは`state=ready`、`may_execute_approved_plan=true` |
| IMPLEMENT-S01-r1 | S01 code and test sensitivity | code-reviewer | superseded | failed | no | add focused tests then fresh re-review | P2: inside-lock body failure後のlock releaseとbody/release exception precedenceのtest感度不足。`gpt-5.6-sol`/medium、confidence 0.97 |
| IMPLEMENT-S01-r2 | S01 code and test sensitivity | code-reviewer | fresh | passed | no | commit candidate | findingsなし。Targeted 3 tests、full focused file 32 tests、diff check pass。`gpt-5.6-sol`/medium、confidence 0.98 |
| IMPLEMENT-S02-r1 | S02 publisher integrity | code-reviewer | superseded | failed | no | destination reread then fresh re-review | P1: formal destinationを再読せずstaged hash/countを転記。`gpt-5.6-sol`/medium、confidence 0.98 |
| IMPLEMENT-S02-r2 | S02 committed boundary | code-reviewer | superseded | failed | no | committed warning result then fresh re-review | P1: post-link mismatch/read failureをordinary successまたは`committed=false`へ誤分類。`gpt-5.6-sol`/medium、confidence 0.99 |
| IMPLEMENT-S02-r3 | S02 verified publication target | code-reviewer | superseded | failed | no | descriptor-bound publication then fresh re-review | P1: verified descriptorではなくreplace可能なtemp pathnameをhard-linkし、未検証/source inode公開が可能。`gpt-5.6-sol`/medium、confidence 0.98 |
| IMPLEMENT-S02-r4 | S02 code and test sensitivity | code-reviewer | fresh | passed | no | commit candidate | findingsなし。Descriptor-bound Darwin/Linux no-replace、fail-closed、inode-aware cleanup、warning contractを確認。Focused 42 pass、Ruff/diff check pass。`gpt-5.6-sol`/medium、confidence 0.97 |
| IMPLEMENT-S03-r1 | S03 code and test sensitivity | code-reviewer | fresh | passed | no | commit candidate | findingsなし。CLI vertical slice、byte preservation、blank grammar、content-free output、warning propagation、existing command非回帰を確認。Focused 13 pass、Ruff format/check、diff check pass。`gpt-5.6-sol`/medium、confidence 0.98 |
| IMPLEMENT-S04-r1 | S04 collision/fault semantics and test sensitivity | code-reviewer | fresh | passed | no | commit candidate | findingsなし。C317-05–09、TC317-S04-01–04、collision、fault、cleanup、例外優先順位、禁止事項を確認。Reviewer再実行25 pass、diff check pass。`gpt-5.6-sol`/medium、confidence 0.98 |
| IMPLEMENT-S05-r1 | S05 consumer compatibility/projection/manual evidence | code-reviewer | fresh | passed | no | commit candidate | findingsなし。Consumer characterization、provider/dogfood 10/10 byte-equivalence、manual Artifact source一致、guard分離、scope境界を確認。Reviewer環境のtemp制約でtest再実行不可だがstatic/recorded evidenceに矛盾なし。`gpt-5.6-sol`/medium、confidence 0.98 |
| S90-SPEC-r1 | Docs impact path ownership/closure | spec-reviewer | superseded | failed | no | expand path ledger then fresh re-review | P1: grouped surfaceでは実パス別disposition/owner/reason/dependency/blockingを検証不能。`gpt-5.6-sol`/medium、confidence 0.99 |
| S90-SPEC-r2 | Docs impact path ownership/closure | spec-reviewer | superseded | failed | no | expand runtime paths then fresh re-review | P1: Runtime provider/dogfood 10-file surfaceだけgrouped pathが残存。`gpt-5.6-sol`/medium、confidence 0.99 |
| S90-SPEC-r3 | Docs impact path ownership/closure | spec-reviewer | fresh | passed | no | promote; approve no-op/defer and commit report | findingsなし。全50行、runtime provider 10/dogfood 10の独立実パス、owner/dependency/blocking、W4/W5 relayを確認。`gpt-5.6-sol`/medium、confidence 0.99 |
| S99-QA-r1 | Issue-wide test adequacy | qa-reviewer | fresh | passed | no | proceed to issue-wide code review | findingsなし。C317-01–11/全TC317のRed/negative/fault/concurrency/manual追跡、full unit/CLI、static repair再検証、Issue319 relayを確認。`gpt-5.6-sol`/medium、confidence 0.98 |
| S99-CODE-r1 | Issue-wide integrated diff | code-reviewer | fresh | passed | no | proceed to final spec review | findingsなし。Provider/dogfood一致、focused 79 pass、Ruff/diff check、byte preservation/no-overwrite/lock/fault/consumer契約を確認。`gpt-5.6-sol`/medium、confidence 0.98 |
| S99-SPEC-r1 | Final requirement/design/plan/implementation/report closure | spec-reviewer | fresh | passed | no | promote; commit/push then issue finish | findingsなし。C317-01–11、EAL/decision ledger、Workbench/import契約、Issue318/319 relay、model unpin後の起動時指定を確認。`gpt-5.6-sol`/medium、confidence 0.97 |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | Runtime shared allocation + focused tests + observed report | `7b1afe5e0824280611a0deae4665d2d680d1484f` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | read-only confirmation complete |
| S02 | committed | Binary guard/publisher contracts + focused tests + observed report | `22006f5e2e4052bd9024e7180094e9a5b6996de8` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r4 pass、read-only post-push confirmation complete |
| S03 | committed | Public import vertical slice + focused tests + observed report | `e2197cc85eff304d895919a18b1327aa8cd72db2` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |
| S04 | committed | Collision/fault hardening + deterministic tests + observed report | `18be850a32e4ee1460fc3a7dd1b9b44d5dfae575` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |
| S05 | committed | Consumer characterization + dogfood runtime projection + manual evidence + report | `bdc0d921598a14b1ecf59b7cdc00949be3b0de28` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |
| S90 | approved-no-op | Docs impact inspection + explicit Issue318/319 defer + observed report | `73bebc1a9754e02370501a1e0a59e9ec444de441` | `git status --short` clean、upstream `0 0` | Issue317 runtimeを正しく使うためのshipped text更新はW4/W5 ownershipに明示割当済み | README/reference docs/migration -> Issue319; workflow/skills -> Issue318 | 50-row path ledger、runtime provider 10/dogfood 10、S90-SPEC-r3 pass | fresh spec-reviewer r3 pass、read-only post-push confirmation complete |
| S99 | committed | Static repair 5 files + final observed report | `b7a8a8d6483a7d983287b754a82c9c72d109b540` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | QA/CODE/SPEC fresh pass、read-only post-push confirmation complete |

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 実パス（path） | 処置（disposition） | 担当（owner） | 理由 | 依存（dependency） | Issue317 blocking | 証跡（evidence） | 仕様レビュアー結果 |
|---|---|---|---|---|---|---|---|
| `README.md` | deferred update | Issue319 | Public CLI usage、evidence-only/byte-preserving contract、experimental statusを最終distributionと同時に記載 | W5 / iss-00319、W3/W4 complete | no; runtime/APIはS03–S05で検証済み | Current lines 102/154は`new artifact`のみ。Epic plan W5 deliverables | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/README.md` | deferred update | Issue319 | Public docs indexへArtifact import/reference導線を追加 | W5 / iss-00319 | no | Provider public docs index、W5 docs ownership | pass (S90-SPEC-r3) |
| `spec-dock/docs/README.md` | deferred projection | Issue319 | Provider docs index更新のdogfood parity | Provider docs update、W5 / iss-00319 | no | Dogfood mirrorはprovider authorityからfinal projection | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/guide.md` | deferred update | Issue319 | Workbench→Artifact import、source survival、evidence authorityをguideへ追加 | W5 / iss-00319、W4 checkpoint terminology | no | Existing Workbench placement/authorityは記載済み、import usageは未記載 | pass (S90-SPEC-r3) |
| `spec-dock/docs/guide.md` | deferred projection | Issue319 | Provider guide更新のdogfood parity | Provider guide update、W5 / iss-00319 | no | W5 provider/dogfood parity gate | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/reference_naming.md` | deferred update | Issue319 | Blank filenameへ`chatgpt-output-<slug>`を付与するimport例とcoexistenceを記載 | W5 / iss-00319 | no | Current naming referenceは`new artifact`のみ。Runtime grammarはS01–S05 pass | pass (S90-SPEC-r3) |
| `spec-dock/docs/reference_naming.md` | deferred projection | Issue319 | Provider naming reference更新のdogfood parity | Provider reference update、W5 / iss-00319 | no | W5 provider/dogfood parity gate | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | deferred update | Issue318 | Canonical rewrite前preservation checkpointとEAL handoffを追加 | W4 / iss-00318、W3 complete | no; workflow integrationは次Issueの明示責務 | Epic design DS-004、plan W4 | pass (S90-SPEC-r3) |
| `spec-dock/docs/workflow_spec_authoring.md` | deferred projection | Issue318/Issue319 | W4 provider workflow更新後のdogfood projection。Final installed parityはW5 | Provider W4 update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | deferred update | Issue318 | Standalone file/complete inline/incomplete inline/ZIP-tree branchを追加 | W4 / iss-00318 | no | Epic design lines 249–260、plan W4 | pass (S90-SPEC-r3) |
| `spec-dock/docs/workflow_chatgpt_authoring_pack.md` | deferred projection | Issue318/Issue319 | W4 provider workflow更新後のdogfood/final installed parity | Provider W4 update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | deferred update | Issue318 | Standalone report laneを追加しZIP/tree laneを維持 | W4 / iss-00318 | no | Epic design DS-004 update target | pass (S90-SPEC-r3) |
| `spec-dock/docs/authoring/chatgpt-pack.md` | deferred projection | Issue318/Issue319 | W4 provider authoring doc更新後のdogfood/final installed parity | Provider W4 update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | deferred update | Issue318 | Preservation branch/status/exception/EAL checkpointを共通化 | W4 / iss-00318 | no | Epic plan W4 named target | pass (S90-SPEC-r3) |
| `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | deferred projection | Issue318/Issue319 | Provider skill更新後のdogfood/final installed parity | Provider skill update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | deferred update | Issue318 | ChatGPT completed report preservation checkpointをplanningへ結線 | W4 / iss-00318 | no | Epic plan W4 planning skills | pass (S90-SPEC-r3) |
| `.agents/skills/spec-dock-initiative-planning/SKILL.md` | deferred projection | Issue318/Issue319 | Provider skill更新後のdogfood/final installed parity | Provider skill update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | deferred update | Issue318 | ChatGPT completed report preservation checkpointをplanningへ結線 | W4 / iss-00318 | no | Epic plan W4 planning skills | pass (S90-SPEC-r3) |
| `.agents/skills/spec-dock-epic-planning/SKILL.md` | deferred projection | Issue318/Issue319 | Provider skill更新後のdogfood/final installed parity | Provider skill update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | deferred update | Issue318 | ChatGPT completed report preservation checkpointをplanningへ結線 | W4 / iss-00318 | no | Epic plan W4 planning skills | pass (S90-SPEC-r3) |
| `.agents/skills/spec-dock-issue-planning/SKILL.md` | deferred projection | Issue318/Issue319 | Provider skill更新後のdogfood/final installed parity | Provider skill update、iss-00318→iss-00319 | no | W4/W5 dependency chain | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md` | approved-no-op | N/A | Existing blank grammarを再利用。Typed `chatgpt-output` catalog/reservationを追加しない | Accepted coexistence contract | no | RQ-317-006、D-317-001、S01/S03 coexistence pass | pass (S90-SPEC-r3) |
| `spec-dock/docs/rules/initiative/artifacts.md` | approved-no-op | N/A | Provider rule no-opと一致 | Provider no-op | no | Dogfood/provider existing rule unchanged | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md` | approved-no-op | N/A | Existing blank grammarを再利用。Typed catalog/templateを追加しない | Accepted coexistence contract | no | RQ-317-006、D-317-001 | pass (S90-SPEC-r3) |
| `spec-dock/docs/rules/epic/artifacts.md` | approved-no-op | N/A | Provider rule no-opと一致 | Provider no-op | no | Dogfood/provider existing rule unchanged | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md` | approved-no-op | N/A | Existing blank grammarを再利用。Import provenance/frontmatterを要求しない | Accepted coexistence/opaque bytes contract | no | RQ-317-003/006、S03/S05 pass | pass (S90-SPEC-r3) |
| `spec-dock/docs/rules/issue/artifacts.md` | approved-no-op | N/A | Provider rule no-opと一致 | Provider no-op | no | Dogfood/provider existing rule unchanged | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/templates/README.md` | approved-no-op | N/A | Importはtemplateを適用せずblank type catalogを変更しない | RQ-317-003/006 | no | S03 no-template test、manual Artifactにfrontmatterなし | pass (S90-SPEC-r3) |
| `spec-dock/templates/README.md` | approved-no-op | N/A | Provider template contract no-opと一致 | Provider no-op | no | Dogfood/provider existing template README unchanged | pass (S90-SPEC-r3) |
| `N/A: dedicated migration note file` | deferred creation/placement decision | Issue319 | 現在専用migration fileは存在しない。既存`.workbench` preserve/no canonical migrationをW5 public docsまたはrelease noteの適切な実パスへ記載 | W5 / iss-00319 | no; schema/data migrationなし | Epic design migration strategy、plan rollout/docs impact | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` | completed runtime contract | Issue317 | Import/publisher request/result/error/warning型 | S02–S04 | no | S02–S04 tests/reviews | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/application/contracts.py` | completed projection | Issue317 | Provider contractのdogfood byte-equivalent mirror | Provider `application/contracts.py`、S05 | no | `cmp` pass、IMPLEMENT-S05-r1 | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | completed shared allocation | Issue317 | New/import共通のlock内blank allocation | S01 | no | TC317-S01-01/02、IMPLEMENT-S01-r2 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | completed projection | Issue317 | Provider shared allocatorのdogfood mirror | Provider `application/create_artifact_doc.py`、S05 | no | `cmp` pass、IMPLEMENT-S05-r1 | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py` | completed import use case | Issue317 | Guard、allocation、bounded collision、committed classification | S01–S04 | no | TC317-S03/S04、IMPLEMENT-S03-r1/S04-r1 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/application/import_artifact.py` | completed projection | Issue317 | Provider import use caseのdogfood mirror | Provider `application/import_artifact.py`、S05 | no | `cmp` pass、manual import success | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` | completed runtime port | Issue317 | Workbench guard/binary publisher ports | S02 | no | Binary port tests、IMPLEMENT-S02-r4 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/application/ports.py` | completed projection | Issue317 | Provider portsのdogfood mirror | Provider `application/ports.py`、S05 | no | `cmp` pass、dogfood validate | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | completed runtime wiring | Issue317 | Filesystem guard/publisher/use case wiring | S03 | no | CLI runtime tests、IMPLEMENT-S03-r1 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py` | completed projection | Issue317 | Provider bootstrapのdogfood mirror | Provider `cli/bootstrap.py`、S05 | no | `cmp` pass、manual import success | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` | completed CLI parser/help | Issue317 | `artifact import chatgpt-output` args/help | S03 | no | TC317-S03-01/04、manual help | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/cli/parser.py` | completed projection | Issue317 | Provider parser/helpのdogfood mirror | Provider `cli/parser.py`、S05 | no | `cmp` pass、dogfood help | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` | completed CLI registration | Issue317 | Import leaf handler登録 | S03 | no | Parser/registry tests、IMPLEMENT-S03-r1 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/cli/registry.py` | completed projection | Issue317 | Provider registryのdogfood mirror | Provider `cli/registry.py`、S05 | no | `cmp` pass、dogfood help | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py` | completed command adapter | Issue317 | CLI request構築、text/JSON outcome | S03 | no | Command/presentation tests | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/commands/artifact_import.py` | completed projection | Issue317 | Provider command adapterのdogfood mirror | Provider `commands/artifact_import.py`、S05 | no | `cmp` pass、manual JSON success | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | completed filesystem adapter | Issue317 | Opaque binary stage/hash/descriptor no-replace/durability/cleanup | S02/S04 | no | Focused publisher/fault tests、IMPLEMENT-S02-r4/S04-r1 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | completed projection | Issue317 | Provider publisherのdogfood mirror | Provider `infra/binary_artifact_publisher.py`、S05 | no | `cmp` pass、manual SHA/cmp success | pass (S90-SPEC-r3) |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` | completed text/JSON presentation | Issue317 | Content-free success/error/warning fields | S03/S04 | no | Presentation tests、IMPLEMENT-S03-r1/S04-r1 | pass (S90-SPEC-r3) |
| `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py` | completed projection | Issue317 | Provider presentationのdogfood mirror | Provider `presentation/cli_text.py`、S05 | no | `cmp` pass、manual JSON/content-free output | pass (S90-SPEC-r3) |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | already sufficient; additional Issue317 integration test not required | C317-01–11/全TC317、unit 1121、CLI 1162/75 skip、affected 111、projection 12、manual SHA/cmp/validate、Issue319 full gate relay | pass; findingsなし、confidence 0.98 |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff（`51c4f8f0`以降、未commit S99 static repairを含む） | findingsなし。Provider/dogfood一致、focused 79 pass、Ruff、diff check、byte preservation/no-overwrite/lock/fault/consumer契約を確認 | 0 | pass、confidence 0.98 |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | findingsなし。C317-01–11、EAL/decision ledger、byte-preserving/evidence-only/blank coexistence、Workbench/import境界、Issue318/319 relay、model運用を確認 | 0 | pass、confidence 0.97 |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S99 full baseline、static repair、QA/code/spec reviewer verdict、Issue318/319 relay、deferred full/global gateを記録 | S99 static repair 5ファイルと本reportを`b7a8a8d6483a7d983287b754a82c9c72d109b540`でcommit/push。Closure report commitで本台帳を確定 | Issue317 finish evidence、Epic最終PR、最終ユーザー報告 | ready |

## 遭遇した問題と解決 (任意)
- 問題: Final static gateで、Issue-localのmypy例外変数shadowとRuff format差分を検出した。
  - 解決: DevCoderが意味を変えない局所renameと3 test fileのformatだけを行い、provider/dogfood exact projection、mypy、Ruff、affected tests、diff checkで再検証した。
- 問題: Global RuffはIssue317外の`authoring-pack`既存差分でfailした。
  - 解決: Issue317変更面のRuff passを確認し、全体修復とfull/global gateは依存順上のIssue319 W5へ明示relayした。

## 学んだこと (任意)
- Byte-preserving importでは、pathnameの再参照ではなく検証済みdescriptorへpublicationを結び付けることがTOCTOU境界の中核になる。
- Post-publish faultはrollback不能であり、`committed=true`とcontent-free warningを返す契約が、再試行による重複作成を防ぐ。

## 今後の推奨事項 (任意)
- Issue318でChatGPT First authoring checkpointとEAL運用を結線し、Issue319でfresh init/update、public docs、Linux CI、full/global gate、Epic PRを完了する。
- Suffix grammarまたはnative no-replace adapterを変更する場合は、100候補上限とverified-descriptor/no-overwrite観測契約を同時に再検証する。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.

### S01 Shared lock-internal Artifact allocation — 2026-07-13

- Delegated worker: DevCoder、direct invocation `gpt-5.6-sol` / reasoning `medium`。
- Scope: `create_artifact_doc.py`と`test_runtime_new_doc_s09.py`のみ。
- Red evidence:
  - `uv run pytest -q tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_parallel_new_artifact_allocates_after_shared_create_lock`
  - 旧実装で`1 failed`。後行operationがlock前candidateを保持し`Artifact already exists`となるraceを再現。
- Green evidence:
  - Race test: `1 passed`。
  - S01 targeted tests: `3 passed, 29 deselected`。
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`: `32 passed`。
  - `tests/cli_runtime/test_new.py -k new_artifact`: `19 passed, 29 deselected`。
  - Artifact validation lane: `8 passed, 1 skipped, 36 deselected`。
  - `git diff --check`: pass。
- Refactor guardrail:
  - Existing create lock/token release、template rendering、typed/blank grammar、text/JSON result、`01..99` exhaustionを維持。
  - New lock、import CLI、binary publisher、docs変更なし。
- Test contract closure:
  - `TC317-S01-01` / `C317-04` / `C317-05` prerequisite: pass。
  - `TC317-S01-02` / `C317-04`: pass。
  - Review-discovered lock release/error precedence coverage: pass。Body errorがprimary、release errorが`__cause__`。
- Reviewer:
  - r1 P2 test-sensitivity findingを追加testsで修正。
  - Fresh r2 findingsなし、pass、confidence 0.98。
- Discovered tests / closure delta:
  - Required closure expectationの変更なし。Review-discovered testsをS01既存guardrail evidenceとして追加し、plan amendment不要。
- Ledger disposition:
  - No material implementation decisions beyond the approved plan.

### S02 Workbench source guard and binary publisher — 2026-07-13

- Delegated worker: DevCoder、すべてdirect invocation `gpt-5.6-sol` / reasoning `medium`。
- Scope: Narrow application contracts/ports、provider-side infra publisher、focused application/infra tests。CLI/presentation/dogfood mirrorは未変更。
- Red evidence:
  - Initial ports/adapter absence: `34 failed`。
  - Destination reread: staged値再利用で`1 failed`。
  - Committed warning boundary: mismatch/read failure/cleanup retentionで`3 failed`。
  - Verified publication target: temp pathnameを別bytesまたはsource hard-linkへ差し替える2ケースで、未検証/source inode公開を再現。
- Green evidence:
  - S02 focused ports/publisher: `42 passed`。
  - Relevant Artifact/new regressions: `81 passed, 5 skipped`。
  - Wide infra lane: `236 passed`後、provider-only新moduleのdogfood mirror欠落1件を検出。S05/Issue319 projection責務としてdeferred。
  - `ruff check`: pass。`git diff --check`: pass。
- Implementation evidence:
  - Root/scoped Workbenchのrelative/absolute lowercase `.md` regular fileだけを許可し、outside/missing/.MD/directory/symlink ancestor/special fileをread/publish前に拒否。
  - LF/CRLF/BOM/no-final/Japanese/NUL/invalid UTF-8/zero-byteをbinary chunkで保持し、source/stream/staged/final hashとbyte countを観測。
  - Mandatory source reread、descriptor `fstat`、path `lstat`でsame-size mutation/replacement/unlinkをpre-publish failure化。
  - Darwin `fclonefileat(staged_fd, ...)`、Linux descriptor-backed follow-link、other/unsupported filesystem fail-closed。Source inodeを直接publishしない。
  - Post-link mismatch/read failure/temp retentionはstable content-free warning、`committed=true`、best verified hash/bytesを返し、automatic retry/rollbackを誘発しない。
  - Cleanupはtemp pathname inodeがstaged fdと一致する場合だけunlinkし、replacementをowned tempとして削除しない。
- Reviewer:
  - r1/r2/r3の各P1を同stepのbounded follow-upで修正。
  - Fresh r4 findingsなし、pass、confidence 0.97。
- Test contract closure:
  - `TC317-S02-01` / `C317-02`: pass。
  - `TC317-S02-02` / `C317-03`: publisher primitive pass。Public CLI closureはS03。
  - `TC317-S02-03` / `C317-06`: pass。
  - `TC317-S02-04` / `C317-07`: adapter pre-publish/fail-closed portion pass。Full orchestration matrixはS04。
- Discovered tests / closure delta:
  - Descriptor-binding、post-link confirmation、inode-aware cleanup testsを追加。Required closure expectationとstep orderは不変、plan amendment不要。
- Ledger disposition:
  - D-317-003をapplied。Exact native primitiveはdesignで明示されたIssue-local implementation delta内で、durable public contract変更なし。
- Commit closure:
  - Implementation/report commit: `22006f5e2e4052bd9024e7180094e9a5b6996de8` (`feat(artifact): バイナリ公開境界を追加`)。
  - Push成功。Post-push `git status --short` clean、`git rev-list --left-right --count '@{upstream}...HEAD'` = `0 0`。

### S03 `artifact import chatgpt-output` vertical slice — 2026-07-14

- Delegated worker: DevCoder、direct invocation `gpt-5.6-sol` / reasoning `medium`。
- Scope: Provider application/CLI/command/presentationとfocused tests。Publisher semantics、dogfood mirror、docs/workflowsは未変更。
- Red evidence:
  - New leaf、application contracts、renderers不在でfocused suite `9 failed`。
- Green evidence:
  - Focused command/presentation/CLI runtime: `13 passed`。
  - S01/S02、new artifact、node import、presentation regressions: `178 items`、exit 0。先行regression run `142 passed`。
  - Manual `artifact import --help` / leaf help inspection: exit 0。
  - `ruff check` / `ruff format --check` / `git diff --check`: pass。
- Public contract:
  - Leaf: `artifact import chatgpt-output`。
  - Required: exactly one of `--initiative|--epic|--issue`、`--file`、`--title`。Optional: `--slug`、`--json`。
  - `--destination|--encoding|--template|--frontmatter|--move|--overwrite`は非公開。
  - Success fields: import kind、blank storage identity、Artifact/scope ID、repo-relative source/destination、SHA-256、byte count、committed/cleanup/warning state。
  - Failure: stable content-free code、`committed=false`、cleanup state。Body/secret/absolute path/raw exception/canonical-adopted-reviewed claimなし。
- Fixture evidence:
  - LF/CRLF/BOM/no-final/Japanese/NUL/invalid UTF-8/zero-byte/secret-like bytesのsource/final SHA+bytes一致、source survival。
  - Existing blank grammar、same-second suffix、`new artifact blank --slug chatgpt-output-*`共存、top-level node `import`非回帰。
- Reviewer:
  - Fresh r1 findingsなし、pass、confidence 0.98。
- Test contract closure:
  - `TC317-S03-01` / `C317-01`: pass。
  - `TC317-S03-02` / `C317-03/C317-04`: pass。
  - `TC317-S03-03` / `C317-09`: pass。
  - `TC317-S03-04` / `C317-01/C317-04`: pass。
- Discovered tests / closure delta:
  - Required closure expectation不変。S04のrace/fault/retry hardeningを先取りせず、plan amendment不要。
- Ledger disposition:
  - No material implementation decisions beyond the approved plan.
- Commit closure:
  - Implementation/report commit: `e2197cc85eff304d895919a18b1327aa8cd72db2` (`feat(artifact): ChatGPT出力import CLIを追加`)。
  - Push成功。Post-push `git status --short` clean、upstream `0 0`。

### S04 Collision and fault semantics hardening — 2026-07-14

- Delegated worker: DevCoder、direct invocation `gpt-5.6-sol` / reasoning `medium`。
- Scope: Import application、binary publisher、contracts、focused concurrency/fault/presentation tests。Docs/workflow/dogfood projectionは未変更。
- Red evidence:
  - Initial S04 suite: `8 failed, 6 passed`。
  - Exact-path `EEXIST`がterminal failure、bounded publication retry不在、publish後lock-release faultがcommitted resultとして保持されない欠陥を再現。
- Green evidence:
  - Focused S04/publisher/presentation: `63 passed`。
  - Deterministic S04 suite: `25 passed`を3連続（25.70s、24.07s、23.36s）。
  - S02/S03関連回帰: `58 passed`。S01 shared allocation回帰: `32 passed`。
  - `mypy`: 2 source files、issuesなし。`ruff format --check` / `ruff check` / `git diff --check`: pass。
- Collision/fault evidence:
  - import/importとimport/newはshared create lock内でbase/`-01`へ分離し、双方commit、既存sentinel不変、deadlockなし。
  - External exact-path `EEXIST`は既存bytesを変えずrescan後の次slotへcommit。Base + `01..99`を100回上限とし、retry/suffix exhaustionはformal mutationなしで停止。
  - Source mutation/replacement/unlink、temp create/copy/hash/file-fsync/unsupported/prepublish cleanup faultは`committed=false`、source/formal不変、owned temp stateを正確に返す。
  - Directory fsync、temp cleanup、post-confirmation、create-lock release faultはfinal/sourceを保持し、`committed=true`とstable content-free warningを返す。Retry/rollbackなし。
- Reviewer:
  - Fresh r1 findingsなし、pass、confidence 0.98。Reviewer自身のfocused deterministic suite `25 passed`、`git diff --check` pass。
- Test contract closure:
  - `TC317-S04-01` / `C317-05`: pass。
  - `TC317-S04-02` / `C317-05/C317-07`: pass。
  - `TC317-S04-03` / `C317-06/C317-07`: pass。
  - `TC317-S04-04` / `C317-08/C317-09`: pass。
- Discovered tests / closure delta:
  - Retry boundをcurrent candidate spaceと同じ100回に具体化。Required closure expectationとstep orderは不変、plan amendment不要。
- Ledger disposition:
  - D-317-004をapplied。将来suffix grammar変更時の同期見直しをfollow-up条件として記録。
- Commit closure:
  - Implementation/report commit: `18be850a32e4ee1460fc3a7dd1b9b44d5dfae575` (`feat(artifact): importの競合・障害境界を強化`)。
  - Push成功。Post-push `git status --short` clean、upstream `0 0`。

### S05 Consumer compatibility and manual dogfood evidence — 2026-07-14

- Delegated worker: DevCoder、direct invocation `gpt-5.6-sol` / reasoning `medium`。Manual capture/EAL/relay統合はorchestrator。
- Scope: Focused consumer characterization、S01–S04 provider runtime 10ファイルのdogfood projection、active Issueへの1件のmanual evidence import。
- Characterization evidence:
  - Invalid UTF-8 raw import後のvalidate、sync projection、typed ADR mirrorを一体で確認するtestを追加。
  - 初回はconsumer defectではなくsyncの実行時`generated_at`差で失敗。現在実行時刻と同値の派生値だけを正規化し、意味内容比較へ修正。Consumer実装変更なし。
  - Raw import callsiteはdelegated-authoring UTF-8/frontmatter guardを参照せず、既存delegated non-UTF-8 rejectionを維持。
- Green evidence:
  - Focused import/fault/concurrency/validate/sync/ADR/new-artifact/delegated-authoring lane: `85 passed in 33.35s`。
  - Dogfood `artifact import --help`で`chatgpt-output` leaf確認。Dogfood `validate`: `spec-dock: ok (validate) nodes=209`。
  - `ruff check` / `ruff format --check` / `git diff --check`: pass。
  - Provider/dogfood runtime 10ファイル: `cmp` 10/10 byte-equivalent。Scope外`spec-dock update .` churnなし。
- Manual dogfood evidence:
  - Source: ignored Workbench direct child `spec-dock/.workbench/issue-317-s05-manual.md`、safe non-secret Markdown、125 bytes。
  - Destination: `artifacts/20260713t161729z-chatgpt-output-issue-317-s05-manual-dogfood.md`。Blank storage identity、frontmatter/template追加なし。
  - Source/final SHA-256: `0231085b3f8006f8fee551d3fe71a6398e1924dbd6170c6ae9d1e3acb206af30`。`cmp` exit 0、双方125 bytes、source残存、warningなし、`committed=true`。
  - Post-import `./spec-dock/scripts/spec-dock validate`: pass、nodes=209。
- Relay:
  - Issue318: ChatGPT First workflow/skillが有用な完成レポートをcanonical再記述前に`chatgpt-output`としてimportし、EALで採否を管理する運用を結線する。
  - Issue319: installed runtime/fresh init/update parity、public docs/migration、full test、final Epic PR deliveryを担当する。Issue317はmerge-preparedを主張しない。
- Test contract closure:
  - `TC317-S05-01` / `C317-10`: pass。
  - `TC317-S05-02` / `C317-10`: pass。
  - `TC317-S05-03` / `C317-11`: pass。
  - `TC317-S05-04` / `C317-11`: pass。EAL-317-003とIssue318/319 relayへ統合。
- Discovered tests / closure delta:
  - Syncの非決定時刻だけを正規化するcharacterizationを追加。Required closure expectation、consumer contract、step orderは不変、plan amendment不要。
- Ledger disposition:
  - No material implementation decisions beyond the approved plan. Manual Artifactはevidence-onlyで、canonical authorityではない。
- Reviewer:
  - Fresh r1 findingsなし、pass、confidence 0.98。Consumer characterization、10/10 byte-equivalence、manual Artifact bytes、guard/scope分離を確認。
  - Reviewer read-only環境ではpytest temp作成制約により再実行不可。DevCoderの85 passとorchestrator manual CLI/hash/cmp/validate証跡をstatic inspectionで照合し、blocking findingなし。
- Commit closure:
  - Implementation/evidence/report commit: `bdc0d921598a14b1ecf59b7cdc00949be3b0de28` (`feat(artifact): dogfood環境へimport機能を反映`)。
  - Push成功。Post-push tracked status clean、upstream `0 0`。Ignored Workbench sourceはmanual evidenceのsource survival証跡として残存。

### S90 Docs impact resolution — 2026-07-14

- Inspection scope: Root README、provider docs/templates、Artifact rules/naming、workflow spec/ChatGPT authoring docs、planning/ChatGPT skills、migration ownership、S01–S05 changed paths。
- Observed impact:
  - Current public docsは`new artifact`とWorkbenchから`artifacts/`への明示的昇格を説明するが、新しい`artifact import chatgpt-output`のpublic usage/authority checkpointは未記載。
  - Runtimeを誤解なく公開するにはcommand reference、byte-preserving/evidence-only contract、migration/distribution説明が必要。ただしParent EpicはこれをIssue319 W5へ明示割当済み。
  - ChatGPT Firstのcanonical rewrite前preservation checkpoint、standalone/inline/ZIP branch、EAL/exceptionはIssue318 W4の明示責務。
  - Existing Artifact rule docs/templatesはblank grammarを正しく受理しており、Issue317でtyped catalog/templateを追加するとaccepted coexistence contractに反する。
- Disposition:
  - Issue317での恒久docs変更はapproved-no-op候補。
  - Workflow/skillsはIssue318へdefer。README/reference/migration/fresh init/update/public distributionはIssue319へdefer。Owner/reason/dependencyは一意で、Issue317 runtime closureをblockしない。
- Verification:
  - `git diff --name-only`でS01–S05 changed surfaceを確認。
  - `rg`でREADME/docs/templates/workflow/skillsの`artifact import` / `new artifact` / Workbench inventoryを確認。
  - Parent Epic requirement/design/planのW4/W5 allocation、G5/G6、rollout/docs impactを照合。
  - S90 r1 P1を受け、provider/dogfoodのREADME、guide、reference、workflow、authoring-pack、4 skills、3 scope rule、template、migration absence、runtime helpを実パス別にDocs Impact matrixへ展開し、disposition/owner/reason/dependency/blocking/evidenceを固定。
  - S90 r2 P1を受け、最後に残ったruntime grouped surfaceもprovider/dogfood 10ファイルそれぞれの独立行へ展開。
- Test contract closure:
  - `TC317-S90-01` / `C317-11`: pass。全50 pathをIssue317 completed / Issue318 defer / Issue319 defer / approved-no-opへ分類。
  - `TC317-S90-02` / `C317-11`: pass。r1/r2 findings修正後、fresh r3 findingsなし、confidence 0.99。
- Reviewer:
  - r1 P1: grouped docs surfaceを実パス別へ展開。
  - r2 P1: grouped runtime surfaceをprovider 10/dogfood 10の独立実パスへ展開。
  - Fresh r3: findingsなし、pass。Actionable owner欠落なし、N/Aはapproved-no-opだけ、W4/W5 relay/依存整合を確認。
- Step Result Approval:
  - Issue317恒久docs変更はapproved-no-op。Issue318/319へのdeferはnon-blockingかつowner/dependency/evidence確定済み。Report-only commit後にS99へ進む。
- Commit closure:
  - Report-only commit: `73bebc1a9754e02370501a1e0a59e9ec444de441` (`docs(issue-317): S90文書影響を確定`)。
  - Push成功。Post-push tracked status clean、upstream `0 0`。

### S99 Final Issue quality gates — 2026-07-14

- Baseline integration:
  - `uv run pytest tests/unit`: `1121 passed in 351.64s`。
  - `uv run pytest tests/cli_runtime`: `1162 passed, 75 skipped, 2 warnings in 1149.08s`。Warningsは既存duplicate ZIP fixtureの`UserWarning`。
  - Full `uv run pytest`はunit/CLIを重複実行しintegration external boundaryも含むため、Issue319 W5のfull Epic gateへ明示relay。Issue317 affected/full unit/full CLIは省略していない。
- Static repair:
  - Initial `uv run mypy src`: Issue-local `commands/artifact_import.py`で例外変数再代入1件を検出。
  - DevCoderがgeneric exception側だけ`runtime_error`へrenameしbehavior/API/contractを不変に修正。Provider→dogfood commandをexact re-projection。
  - Issue317 changed test 3ファイルだけをRuff整形。Full Ruffで検出したpre-existing `scripts/authoring-pack/authoring_pack_review.py` / `invoke_chatgpt_backend.py` driftは変更せず、Issue319 full static gateへrelay。
  - Post-repair: `uv run mypy src` = 147 source files issuesなし。Issue317 changed 17 Python filesのRuff check/format pass。Affected tests `111 passed`、projection follow-up `12 passed`、provider/dogfood `cmp` pass、`git diff --check` pass。
- Lifecycle/evidence:
  - `assurance verify --issue iss-00317 --format json`: `ok=true`, `status=valid`, standard/normal、source binding valid。
  - `validate`: `spec-dock: ok (validate) nodes=209`。
  - `sync`: approved-no-op。Issue317変更はruntime/tests/reportとblank evidence Artifactで、node status/dependency/ADR mirror projectionを変えない。S05 temp-repo sync characterization pass、blank ArtifactはADR mirror非対象、S90以降node metadata変更なし。
  - `active show`: initiative `init-local-00003`、epic `epic-00312`、issue `iss-00317`一致。
  - Pre-review branch: upstream `0 0`、final candidateはreport、provider/dogfood commandの同一rename、format-only test 3件。
- Closure coverage:
  - `C317-01–04`: S01/S03 public CLI、blank coexistence、opaque bytesでpass。
  - `C317-05–09`: S02/S04 collision/source/fault/post-commit/content-free matrixでpass。
  - `C317-10`: S05 validate/sync/ADR/delegated-authoring consumer characterizationでpass。
  - `C317-11`: Manual import/EAL、Issue318/319 relay、S90 docs impact、deferred PR deliveryでpass candidate。
- Deferred PR Delivery Gate:
  - Target: `iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr`。
  - Dependency: Epic planのIssue317→Issue318→Issue319 chain。
  - Reason: One final Epic PRへworkflow integration、installed/fresh init/update parity、public docs、full regression/static repair、PR deliveryを集約するためper-Issue PRを作らない。
  - Claim boundary: Issue319 PR Delivery/Merge Preparation完了までmerge-preparedを主張しない。
  - Remaining gates: Issue318 workflow/skills、Issue319 package/fresh init/update/public docs/migration/full `pytest`/global Ruff pre-existing drift/QA-code-spec/PR observation。
- Final reviewer result: fresh QA、issue-wide code、final specはいずれもfindingsなしでpass。Final report commit/push、clean/upstream確認後にspec-manager `issue finish`へ進む。
- Commit closure:
  - S99 implementation/report commit: `b7a8a8d6483a7d983287b754a82c9c72d109b540` (`fix(artifact): ChatGPT出力Artifact取り込みの品質を確定`)。
  - 対象6ファイルのみをstage/commitしpush成功。Post-push `git status --short` clean、upstream `0 0`、`git diff --check`とprovider/dogfood command `cmp` pass。
<!-- spec-dock:managed-section end id="report.step-evidence" -->
