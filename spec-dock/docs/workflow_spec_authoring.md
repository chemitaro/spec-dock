# 仕様 authoring ワークフロー（workflow: spec authoring）

Initiative / Epic / Issue の requirement / design / plan を作成・更新する共通 workflow です。
scope 固有の lifecycle / governance は `workflow_initiative.md` / `workflow_epic.md` / `workflow_issue.md` が所有し、この文書は仕様書作成そのものの phase promotion gate を正本として扱います。

関連:
- 総合: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- Phase playbook: [phase_requirement.md](phase_requirement.md), [phase_design.md](phase_design.md), [phase_plan.md](phase_plan.md)

## 基本契約

- 仕様書作成は `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` の順に進める。
- 各 phase promotion は fresh `spec-reviewer` の `review_status: pass` を必須にする。
- `spec-reviewer` が `fail` を返した場合は指摘を修正し、同じ reviewer 状態を再利用せず fresh `spec-reviewer` で再レビューする。
- phase gate verdict は `passed` / `failed` / `unavailable` / `denied` / `waived` / `provisional` のいずれかで記録する。自動 promotion を許可するのは fresh `passed` だけである。
- `waived` は、ユーザーが明示的に risk acceptance を与え、その内容と対象 scope が `report.md` に残っている場合だけ使える。`waived` を reviewer pass と表現してはならない。
- `provisional` は orchestrator self-check の記録であり、`spec-reviewer` の代替ではない。
- reviewer が missing / stale / failed / unavailable / denied / waived / provisional の場合は、phase promotion を block または incomplete として扱う。degraded mode を reviewer gate の degraded success として扱ってはならない。
- 調査で解消できる不明点をユーザー質問で代替しない。先に docs / code / ADR / discussions / 外部一次情報を確認する。
- 調査後もユーザー意図、受け入れ条件、スコープ、非スコープ、優先順位に影響する未確定事項が残る場合は、次 phase へ進む前にユーザーへヒアリングする。
- scope / non-scope に影響する未確認事項が残る場合は `blocked` または `incomplete` として扱い、次 phase へ進めない。

## 権限メタデータ（Authority metadata / grants / Promotion Record）

Delegated canonical draft authoring を使う場合、artifact や report evidence は次の authority metadata を明示します。

- `status`: `draft` / `reviewed` / `approved` / `blocked` / `stale` / `superseded`
- `authority`: `proposed` / `approved` / `historical`
- `owner_role`: canonical artifact と phase promotion を所有する role。通常は main orchestrator。
- `draft_author_role`: delegated draft を作成した role。未使用時は `N/A`。
- `approval`: reviewer gate と main orchestrator promotion の evidence reference。未承認なら `none`。
- `source_revision`: delegated draft が読んだ upstream artifact revision。
- `approved_revision`: promotion された canonical artifact revision。未承認なら `none`。
- `approved_hash`: promotion された canonical content hash。未承認なら `none`。
- `manifest_hash`: delegated authoring task manifest の content hash。未使用時は `none`。
- `permission_profile_name`: delegated write session に選択した Permission Profile 名。未使用時は `none`。
- `permission_profile_hash`: selected Permission Profile の content hash。未使用時は `none`。
- `write_session_invocation_hash`: delegated write session invocation の normalized hash。未使用時は `none`。
- `probe_run_id`: positive / negative probe run の識別子。未使用時は `none`。

Grant keys は明示的かつ完全一致で扱います。許可される key set は `review_input`, `planning_input`, `design_baseline`, `implementation_start`, `issue_ready`, `issue_finish`, `phase_completion` です。role 名、scope 名、workflow consent、または reviewer pass から暗黙の write 権限を推定してはなりません。

Wildcard grant semantics はありません。`*`, `grants.*`, `all`, `admin`, `owner`, broad role authority のような包括 grant は無効として扱い、必要な exact key がない操作は blocked / incomplete にします。review input、planning input、design baseline、implementation start、issue ready、issue finish、phase completion はそれぞれ対応する grant key が必要です。

Promotion Record は delegated draft や reviewer output を canonical authority に昇格した事実だけを記録します。canonical artifact promotion の `promotion_record` は少なくとも `status`, `authority`, `owner_role`, `draft_author_role`, `approval`, `source_revision`, `approved_revision`, `approved_hash`, `reviewer_target_hash`, `promoted_at`, `promoted_by`, `promotion_decision` を持ちます。runtime active selection の promotion record は lifecycle gate 用の最小 record として `status`, `authority`, `source_revision`, `approved_revision`, `approved_hash`, `reviewer_target_hash`, `promotion_decision` を持ち、`source_revision` / `approved_revision` / `approved_hash` / `reviewer_target_hash` は active entry id に対応する `active:<id>` と一致している必要があります。`reviewer_target_hash` と `approved_hash` が一致しない場合、`source_revision` / `approved_revision` が一致しない場合、または active entry id と promotion record が一致しない場合、その promotion は invalid であり downstream authority には使えません。Mismatch / stale を発見した場合は report に reason と next action を残し、fresh reviewer gate と Promotion Record の再作成まで block します。

Active manifest と context-pack は同じ authority/grant 状態を示す必要があります。`spec-dock/.agent/active.json` の issue entry が `authority=proposed`、authority metadata 欠落、stale promotion record、または required exact grant 不足の場合、implementation start、issue ready、issue finish、phase completion の lifecycle handoff は blocked / incomplete とします。`spec-dock/active/context-pack.md` は人間向け guidance ですが、authority source は `spec-dock/.agent/active.json` です。

## ワークフロー単位の委任同意（workflow-scoped delegation consent）

- Issue scope の spec authoring では、reviewer / read-only specialist sub-agent を使う前に、current repo/worktree、active issue、session、named role に限定した issue-scoped workflow delegation consent を確認し、`report.md` に記録する。
- 現在のユーザー指示が「この issue workflow 内では reviewer / specialist を自律利用してよい」と明示している場合、その指示を同一 issue / repo / session / named role に限定した consent として扱える。
- consent がある場合、orchestrator は requirement / design / plan の各 phase ごとに再確認せず、必要な `spec-reviewer` や read-only specialist を起動してよい。
- consent は destructive action、external publishing、credentialed access、scope expansion、write-capable delegation、named role 以外の delegation を許可しない。scope が変わる場合は再確認する。
- read-only specialist consent と write-scoped delegated authoring consent は別物として扱う。read-only consent は調査、レビュー、提案、proposal evidence だけを許可し、canonical `design.md` / `plan.md` の書き込み根拠にはならない。
- write-scoped delegated authoring consent は、対象 node、phase、role、artifact、task manifest、input authority、Permission Profile、session invocation、probe、diff gate、fallback を明示した task-local consent として別途記録する。workflow-wide blanket consent、manual edit、unprofiled session、static broad profile、または Desktop-only fallback は write-scoped acceptance に数えない。

## 委任 authoring policy foundation（delegated authoring policy foundation）

- Main orchestrator は canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の最終 ownership、user dialogue、canonical integration、Evidence Adoption Ledger、Promotion Record、phase promotion を所有する。
- Delegated authoring は `authority: proposed` / `status: draft` の draft-only evidence であり、final canonical authority ではない。delegated output は main orchestrator が採否を判断し、fresh `spec-reviewer` が canonical artifact を pass して初めて phase promotion の根拠にできる。
- Delegated authoring を使う場合は、invocation ごとに `node + phase + role + artifact`、scope、source artifacts、allowed actions、forbidden actions、output expectation、stop / invalidation condition を明示し、`report.md` に残す。workflow-wide blanket consent は draft-only authoring delegation の根拠にしない。
- Delegated role は task manifest が明示し、Permission Profile / host probe が検証した draft artifact だけを更新できる。System architect は approved requirement を入力にした `design.md` draft、implementation planner は approved requirement/design を入力にした `plan.md` draft に限定される。
- Delegated role は previous phase artifact、implementation code、tests、package/config、GitHub state、reviewer result を編集・確定・上書きしてはならない。destructive action、external publishing、credentialed access、`.github/agents` / Copilot support はこの workflow の delegated authoring policy では許可しない。
- Delegated draft が unavailable / skipped / blocked / stale / rejected / superseded の場合でも、manual authoring path は有効である。ただし delegated authoring を使った evidence として扱ってはならない。
- Delegated draft は fresh `spec-reviewer` pass の代替ではない。`spec-reviewer` は draft 自体ではなく、main orchestrator が統合した canonical artifact と evidence を review する。

## 委任ドラフト証跡 schema（delegated draft evidence schema）

- Delegated draft lifecycle state は `requested` / `produced` / `integrated` / `partially_integrated` / `rejected` / `superseded` / `blocked` / `stale` のいずれかで記録する。
- `stale`、`rejected`、`superseded`、`blocked` の delegated draft は promotion evidence に使えない。`partially_integrated` は採用部分、rejected portions、blockers、promotion decision を `report.md` に明示した場合だけ採用部分の補助 evidence にできる。
- Delegated draft evidence record は少なくとも role、phase、scope、consent、source artifacts、draft artifact path、status、integration result、rejected portions、blockers、reviewer result、promotion decision を持つ。
- `source_snapshot` を記録する場合は source_revision、requirement_reviewer_pass_reference、design_reviewer_pass_reference、generated_at、stale_if を含める。
- Failure-mode record は expected verdict、allowed next action、report evidence path、promotion eligibility を持つ。
- Required failure modes は missing consent、missing/stale previous reviewer pass、requirement gap during design、design gap during plan、role unavailable、forbidden action attempt、stale draft、superseded draft、missing draft evidence when delegated use is claimed、reviewer unavailable/denied/waived/provisional を含む。
- Delegated draft evidence を使った場合、対象 scope の `report.md` は delegated draft evidence table と failure-mode table を持つ。使わなかった場合は manual authoring / not used として、promotion evidence に delegated draft を使っていないことを短く記録する。

## 証跡採用台帳（Evidence Adoption Ledger）

Delegated draft、worker note、research、reviewer finding、外部調査結果などの証跡を canonical artifact や実装判断へ取り込む場合、`report.md` に Evidence Adoption Ledger を残します。この台帳は raw transcript ではなく、orchestrator が検証した採否判断を記録します。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `source`: evidence の出所（sub-agent、reviewer、discussion、command、external research など）
- `target`: 採用先または影響先 artifact / issue / follow-up
- `rationale`: 採用・部分採用・却下・延期・stale・blocked の理由
- `evidence`: diff、command、reviewer finding、discussion path など検証可能な証跡
- `next_action`: follow-up、再調査、再レビュー、または対応不要の理由

`blocked` または `stale` の entry が未解決のまま残っている場合、phase promotion、implementation start、issue ready、issue finish、phase completion に進めません。`deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せます。Evidence Adoption Ledger を使わずに delegated evidence の採用を主張してはなりません。

## 深さ2までの委任（Bounded Depth=2 Delegation）

Main orchestrator が canonical artifact と final reviewer gate を所有します。System architect や implementation planner などの authoring specialist は、depth=2 の範囲で leaf-only evidence producer を呼び出せます。leaf-only evidence producer は repo analysis、research、consultation、QA-style evidence などの補助証跡を返すだけで、さらに子エージェントを呼び出して depth=3 / grandchild delegation を作ってはなりません。

- allowed depth=2: main orchestrator -> authoring specialist -> leaf-only evidence producer
- forbidden depth=3: main orchestrator -> authoring specialist -> leaf producer -> grandchild
- authoring specialist と leaf-only evidence producer は、検証済み task manifest が許可した対象 `design.md` / `plan.md` draft 更新以外の canonical edit、implementation edit、phase promotion、reviewer-pass claim、final authority、issue ready / issue finish claim を行わない。leaf-only evidence producer は常に canonical edit を行わない
- preflight reviewer output は設計・計画の改善 input として扱い、final fresh reviewer pass とは分離する
- reviewer independence: final `spec-reviewer` / `code-reviewer` / `qa-reviewer` は、同じ artifact を作成した authoring specialist や leaf-only evidence producer の代替ではない fresh gate として実行する

## タスクマニフェストと権限ゲート（Task Manifest / Permission Profile Gate）

Write-scoped delegated authoring は、role-scoped Permission Profile と task manifest の両方が検証済みの場合だけ有効にできます。manifest は raw intention ではなく、実行直前に解決済みの path と revision を固定する fail-closed contract として `report.md` または issue-local `discussions/` に残します。検証済みでない場合、delegated role は proposal-only / discussions path に戻り、canonical `design.md` / `plan.md` を編集してはなりません。

Task manifest は少なくとも次を含めます。

- `resolved target`: canonical artifact または evidence artifact の解決済み path。`spec-dock/active/*` symlink ではなく実体 path を記録する
- `input authority`: upstream approval evidence、promotion record path、reviewer evidence path、approved revision/hash、reviewer target hash、required grants、stale check。reviewer verdict/hash の自己申告だけを信用してはならない
- `session invocation`: executor、host surface、role、scope、target artifact path、manifest path/hash、permission profile name/hash、config overrides、selected `default_permissions`、positive probe id/result、negative probe plan、diff gate plan、`acceptance_counted`
- `input revision`: 読み込んだ upstream requirement / design / plan / report の revision、hash、または commit
- `allowed paths`: positive probe が write できる artifact / evidence path
- `forbidden paths`: implementation code、tests、package/config、`.env*` など write してはならない path
- `probe commands`: positive probe と negative probe の exact command、target path、cleanup command
- `diff gate`: allowed target 以外の diff を拒否し、forbidden sentinel の cleanup と dirty diff abort を要求する確認手順
- `fallback decision`: fail-open、probe unavailable、manual/unprofiled/static broad profile、Desktop/CLI divergent、または host enforcement 不明時に write-scoped delegation を disabled / proposal-only に戻す判断
- `report evidence destination`: task manifest、input authority、session invocation、probe、diff gate、fallback decision、Evidence Adoption Ledger disposition を記録する scope-local `report.md` section または issue-local evidence path
- `Evidence Adoption Ledger fields`: adoption_status、target_artifact、next_action など、採用状態と blocking follow-up を runtime gate が正規化して読める field set
- `default_permissions` / `[permissions]`: role-scoped Permission Profile 名と read/write/deny の要約

Positive write probe は allowed artifact / evidence path だけに成功しなければなりません。Negative write probe は forbidden implementation / config / test path で失敗しなければなりません。forbidden path への write が成功した場合、または host が enforcement を証明できない場合は fail-open と扱い、write-scoped delegation を有効化してはなりません。

Draft artifact probe は target phase に対応していなければなりません。System architect の positive probe は対象 `design.md` または manifest で許可された design draft evidence path だけ、implementation planner の positive probe は対象 `plan.md` または manifest で許可された plan draft evidence path だけに限定します。Previous phase artifact への write probe 成功、または implementation/test/config path への write 成功は invalid です。

`sandbox_mode` / `sandbox_workspace_write` による workspace 全体 write と、Permission Profile による role-scoped write contract を混在させてはなりません。混在、Desktop/CLI divergent、probe unavailable、unreproducible result は `blocked` または `disabled` として記録し、v0 proposal-only authoring path に戻します。

Desktop App は CLI-equivalent の positive probe、non-destructive negative probe、selected Permission Profile、session invocation hash、diff gate を同じ粒度で検証できるまで proposal-only / manual fallback として扱い、write-scoped delegated draft authoring acceptance に数えません。

| 失敗モード | 期待される判定 | 許可される次アクション | report 証跡の記録先 | 昇格可否 |
|---|---|---|---|---|
| missing consent（同意欠落） | blocked / incomplete | obtain scoped consent or use manual authoring（scope 付き同意を取得する、または手動 authoring を使う） | Delegated Draft Evidence | ineligible |
| missing/stale previous reviewer pass（前段 reviewer pass の欠落 / stale） | blocked / incomplete | rerun reviewer gate（reviewer gate を再実行する） | Spec Authoring Gate / reviewer evidence | ineligible |
| requirement gap during design（design 中の requirement gap） | blocked / incomplete | return to requirement phase（requirement phase に戻す） | decision ledger / gate evidence | ineligible |
| design gap during plan（plan 中の design gap） | blocked / incomplete | return to design phase（design phase に戻す） | decision ledger / gate evidence | ineligible |
| role unavailable（role 利用不可） | blocked / manual path | record unavailable and continue manually if valid（利用不可を記録し、妥当なら手動で継続する） | Delegated Draft Evidence | ineligible |
| forbidden action attempt（禁止アクションの試行） | rejected | discard draft and record incident（draft を破棄し、incident を記録する） | Delegated Draft Evidence / decision ledger | ineligible |
| stale draft（stale な draft） | stale | regenerate or reconcile（再生成または整合する） | Delegated Draft Evidence | ineligible |
| superseded draft（置換済み draft） | superseded | reference replacement draft（置換後 draft を参照する） | Delegated Draft Evidence | ineligible |
| missing draft evidence when delegated use is claimed（委任利用を主張しているが draft 証跡が欠落） | incomplete | add evidence or remove delegated-use claim（証跡を追加する、または委任利用 claim を削除する） | Delegated Draft Evidence | ineligible |
| reviewer unavailable/denied/waived/provisional（reviewer 利用不可 / denied / waived / provisional） | blocked / incomplete | obtain fresh passed reviewer or record risk acceptance without promotion（fresh passed reviewer を取得する、または昇格なしの risk acceptance を記録する） | reviewer gate evidence | ineligible |

## 作成のライフサイクル（authoring lifecycle）

1. 対象 scope と既存 node を確認する。
2. 対象 artifact に対応する `docs/authoring/<scope>-<phase>.md` がある場合は最初に読む。
3. 対象 scope の `workflow_*.md` と phase playbook を読む。
4. 調査結果、仮説、選択肢、質問を必要に応じて `discussions/` に分離する。raw capture は `scratch`、人間への質問は `interview`、事実調査は `research`、論点整理は `disc`、長期判断は `adr` を使う。
5. 対象 artifact を更新する。
6. fresh `spec-reviewer` を起動し、対象 artifact と upstream artifact を review する。
7. `fail` なら修正し、fresh `spec-reviewer` で再レビューする。
8. `pass` なら `report.md` に gate evidence を残し、次 phase へ進む。

## 要件ゲート（requirement gate）

- As-Is、制約、user intent、scope、non-scope、acceptance criteria、edge cases を一次情報またはヒアリングで固定する。
- `何を / なぜ / スコープ / 成功条件（WHAT / WHY / scope / success）` を固定し、`どう実現するか（HOW）` は design へ送る。
- ユーザー意図、受け入れ条件、scope / non-scope に関わる TBD が残る場合、design へ進めない。
- `spec-reviewer` は requirement 単体と、必要な upstream initiative / epic / discussion / ADR との整合を確認する。

## 設計ゲート（design gate）

- reviewer-pass 済み requirement を前提にする。
- 既存実装、既存 docs、ADR、依存、責務境界、互換性、移行、テスト戦略を確認する。
- requirement 不足が判明した場合は design で補わず、requirement へ戻して修正し、requirement gate を再実行する。
- `spec-reviewer` は design と requirement の traceability、責務境界、失敗設計、未解決論点の有無を確認する。

## 計画ゲート（plan gate）

- reviewer-pass 済み requirement / design を前提にする。
- 分解、順序、依存、検証、review gate、完了条件、downstream handoff を固定する。
- 未解決設計論点や未承認 requirement を plan に先送りしない。
- Issue plan は `docs/authoring/issue-plan.md` の concrete test case contract に従い、各 implementation step に step-local な `具体テストケース一覧` を置く。
- `spec-reviewer` は plan が requirement / design と矛盾せず、次工程へ安全に渡せることを確認する。

## 下流引き渡し（downstream handoff）

- Initiative は plan gate pass 後に Epic 分解へ進む。
- Epic は plan gate pass 後に Issue 分割へ進む。
- Issue は plan gate pass 後に `workflow_issue.md` の execution contract へ進む。
- downstream で requirement / design / plan の不足が見つかった場合は、該当 phase へ戻して修正し、promotion gate を再実行する。

## 報告の証跡契約（report evidence contract）

対象 scope の `report.md` に `Spec Authoring Gate` を置き、phase ごとに次を残す。

- phase: `requirement` / `design` / `plan`
- investigated facts: 確認した docs / code / ADR / discussions / 外部一次情報
- open questions: 未確定事項、ユーザー質問、回答
- delegation consent: scope、named roles、source、boundary、expires / invalidation condition
- reviewer: fresh `spec-reviewer` の実行単位と review scope
- verdict: `passed` / `failed` / `unavailable` / `denied` / `waived` / `provisional` と理由。`passed` 以外は reviewer gate pass ではない
- fixes: 指摘に対する修正要約
- promotion: 次 phase へ進めるか、`blocked` / `incomplete` の reason と next action

長い調査、比較、ヒアリング transcript は `discussions/` に分離してよい。ただし `report.md` には判断に必要な要約と参照を残す。discussion docs は未確定情報の作業面なので、確定させる内容は新しい `adr`、または `requirement.md` / `design.md` / `plan.md` へ反映する。
