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
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
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
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-13 HH:MM - HH:MM）

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- 計画上の出典（Planned source）:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required / covered-existing / inspect-only / manual-required | ... | `command` / 文書点検（docs inspection） / 手動記録（manual record） | pass / approved-no-op / fail / blocked | ... |
| S01 | 緑フェーズ（Green） | ... | ... | `command` / 点検（inspection） / 手動記録（manual record） | pass / fail / blocked | ... |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | ... | 差分点検（diff inspection） / command | pass / approved-no-op / fail / blocked | ... |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none / ... | implementation / review / QA / user report | recorded / added test / deferred / amended plan | tc-001 / new | yes / no | ... |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required / covered-existing / inspect-only / manual-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |

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

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Setup/duplicate scan/allocation/exact checkをexisting create lock内へ移し、race/exhaustion/release testsを追加 | `src/.../application/create_artifact_doc.py`; `tests/cli_runtime/test_runtime_new_doc_s09.py` | Red 1 failed、Green focused 32 passed、CLI new 19 passed、validation 8 passed/1 skipped、diff check pass | code-review r1 failed、r2 passed | External writer atomic publishはplanned S04、import wiringはS03 | accepted; no material plan deviation |
| S02 | dev-coder | Workbench guard、opaque stage/rehash、descriptor-bound no-replace publish、committed warning、inode-aware cleanupを追加 | `application/contracts.py`; `application/ports.py`; `infra/binary_artifact_publisher.py`; focused application/infra tests | Initial Red 34 failed、Green 42 passed。Relevant regressions 81 passed/5 skipped、wide infra 236 passed後dogfood mirror gap 1件。Ruff/diff check pass | code-review r1/r2/r3 failed、fresh r4 passed | Linux descriptor-backed primitiveはDarwin上で未実動。Dogfood mirrorはS05/Issue319 delivery対象 | accepted; D-317-003をissue-local implementation decisionとして適用、plan closure変更なし |
| S03 | dev-coder | `artifact import chatgpt-output` parser→application→publisher→presentationを結線し、blank naming/byte identity/content-free outputを公開 | `application/contracts.py`; new `application/import_artifact.py`; CLI parser/registry/bootstrap; new command; presentation; 3 focused test files | Red 9 failed、focused 13 passed、regression 178 items exit 0、prior 142 passed、manual help/Ruff format+check/diff check pass | fresh code-review r1 passed | S04 collision/fault hardening、Linux live primitive、dogfood projectionは未実施 | accepted; no material plan deviation |
| S04 | dev-coder | Shared create lock内でcollisionを再scanし、100候補のbounded retry、pre/post-publish fault分類、committed warningを追加 | `application/contracts.py`; `application/import_artifact.py`; `infra/binary_artifact_publisher.py`; S04 CLI/presentation tests | Initial 8 failed/6 passed、focused 63 passed、deterministic 25 passedを3連続、S02/S03回帰58 pass、S01回帰32 pass、mypy/Ruff/diff check pass | fresh code-review r1 passed | Linux descriptor publication live検証はS02から継続。Suffix grammar変更時は100回上限も同期必要 | accepted; D-317-004 applied、plan closure変更なし |
| S05 | dev-coder | Invalid UTF-8 raw import後のvalidate/sync/ADR mirror不変性をcharacterizeし、S01–S04 runtime 10ファイルをdogfoodへbyte-equivalent projection | 10 dogfood runtime files; `tests/cli_runtime/test_artifact_import_chatgpt_output.py` | Characterization時刻差分を意味保存で正規化後Green、focused 85 passed、dogfood validate pass、provider/dogfood cmp 10/10、Ruff/diff check pass | fresh code-review r1 passed | Manual captureはorchestrator実施済み。Public docs/workflow/package parityはIssue318/319 relay | accepted; no material implementation decision |

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

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | Runtime shared allocation + focused tests + observed report | `7b1afe5e0824280611a0deae4665d2d680d1484f` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | read-only confirmation complete |
| S02 | committed | Binary guard/publisher contracts + focused tests + observed report | `22006f5e2e4052bd9024e7180094e9a5b6996de8` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r4 pass、read-only post-push confirmation complete |
| S03 | committed | Public import vertical slice + focused tests + observed report | `e2197cc85eff304d895919a18b1327aa8cd72db2` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |
| S04 | committed | Collision/fault hardening + deterministic tests + observed report | `18be850a32e4ee1460fc3a7dd1b9b44d5dfae575` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |
| S05 | committed | Consumer characterization + dogfood runtime projection + manual evidence + report | `bdc0d921598a14b1ecf59b7cdc00949be3b0de28` | `git status --short` clean、upstream `0 0` | N/A | N/A | N/A | fresh code-reviewer r1 pass、read-only post-push confirmation complete |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### セッションログ（2026-07-13 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

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
<!-- spec-dock:managed-section end id="report.step-evidence" -->
