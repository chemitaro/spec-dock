---
種別: ディスカッション
ID: "20260523t235448z-disc-write-capable-draft-authoring-gap-analysis"
タイトル: "Write-capable Delegated Draft Authoring Gap Analysis"
関連GitHub: ["#112", "#119"]
状態: "draft"
作成者: "Codex"
作成日: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# Write-capable Delegated Draft Authoring Gap Analysis

## 目的

この資料は、`epic-00112 Delegated Authoring Architecture for Spec Workflow` の v1 要件を本当に満たすために、現在のドキュメント群、role skill、Codex agent adapter、テスト、過去 issue report の間にある矛盾を棚卸しし、表面修正ではなく契約全体を整えるための修正案をまとめる。

今回のユーザー指摘は妥当である。現状は「write-scoped delegated authoring を将来の guardrail として記述しつつ、実際の `system-architect` / `implementation-planner` は proposal-only / read-only fallback に留める」実装になっている。これは v0 fallback としては安全だが、Epic v1 の「専門 author が actual `design.md` / `plan.md` の draft を作成・更新する」という目的を達成していない。

この資料では、完了済み issue の履歴を改ざんしない。`iss-00123` や `iss-00125` に記録された fallback-disabled / proposal-only の実績は、その時点の観測事実として保持する。その上で、Epic v1 を満たすための追加是正 issue / 追加修正として積み上げる。

## 分析体制

この分析は main orchestrator 単独ではなく、複数の consultant / deep-consultant の並行分析を統合した。

- deep-consultant `Epicurus` (`019e5742-a4db-7041-9b57-ea6ea8bef410`):
  - 観点: Epic 要件、過去 issue report、実装済み fallback の意味、是正 issue の必要性。
- deep-consultant `Hume` (`019e5742-c8e6-73c3-a5f5-9c7ea333fda5`):
  - 観点: Permission Profile / task manifest / depth=2 / runtime validation の安全境界。
- consultant `Descartes` (`019e5742-ea8b-7332-9b6e-f0436ffe329f`):
  - 観点: role adapter と role skill の矛盾、テストが固定している現在挙動、最小修正面。
- consultant `Beauvoir` (`019e5743-07ee-7c93-9b4e-2ae0ce20c68f`):
  - 観点: workflow docs / report template / consent wording / 完了済み issue を改ざんしない進め方。

## あるべき状態

Epic v1 のあるべき状態は、単に「サブエージェントが何かを提案する」ではない。専門 author が canonical artifact の draft を作り、main orchestrator がそれを非権威 draft として扱い、レビューと promotion によってだけ downstream authority へ昇格する状態である。

- `system-architect` は、main orchestrator から検証済み task manifest と role-scoped Permission Profile evidence を受け取った場合に限り、解決済みの対象 `design.md` を `status: draft` / `authority: proposed` として作成・更新できる。
- `implementation-planner` は、検証済み manifest と profile evidence を受け取った場合に限り、解決済みの対象 `plan.md` を `status: draft` / `authority: proposed` として作成・更新できる。
- main orchestrator は `requirement.md`、user dialogue、final ownership、promotion、phase completion、report evidence、fresh final `spec-reviewer` gate を保持する。
- `system-architect` / `implementation-planner` が作成した `design.md` / `plan.md` は、canonical path に置かれていても `authority: proposed` の間は implementation baseline / issue ready / issue finish / phase completion の根拠にならない。
- `authority: approved` への昇格は、main orchestrator による採用判断、promotion record、fresh final `spec-reviewer` pass、approved revision / hash の記録を必須にする。
- `system-architect` / `implementation-planner` は depth=2 の範囲で、`repo-analyst`、`researcher`、`consultant`、`deep-consultant`、advisory `spec-reviewer` などの leaf-only evidence producer を呼べる。
- child specialist は canonical artifact edit、implementation edit、promotion、final reviewer pass、user dialogue を行わない。depth=3 は禁止する。
- Permission Profile は broad な `spec-dock/initiatives` write ではなく、task manifest によって解決された exact artifact path と exact evidence / ledger path だけを許可する。
- positive probe と negative probe により、許可対象への書き込みが可能で、禁止対象への書き込みが拒否されることを確認する。fail-open、unavailable、Desktop/CLI divergent、stale manifest の場合は proposal-only fallback に戻す。
- fallback は安全な退避路であり、Epic v1 acceptance の達成根拠ではない。

## 現状の問題リスト

| ID | 問題 | 現在の根拠 | なぜ問題か | 影響 |
|---|---|---|---|---|
| P-001 | Codex agent adapter が read-only / proposal-only と明記している | `.codex/agents/system-architect.toml` と provider copy は `Read-only delegated architecture drafting agent`、`proposal-only mode and do not write`、`Do not implement write-capable delegation` を含む。`implementation-planner` も同様。 | Epic v1 の E-RQ-002 / E-AC-003 / E-AC-004 は actual `design.md` / `plan.md` draft authoring を要求している。 | role skill が許している成功パスを host adapter が実質的に無効化している。 |
| P-002 | Permission Profile の write root が probe evidence だけになっている | 両 adapter の profile は `".codex/permission-probe-evidence" = "write"` だけを許可し、`spec-dock/initiatives` は read-only。 | actual `design.md` / `plan.md` draft を作成・更新できない。 | サブエージェントは consultant と同じ提案役に戻ってしまう。 |
| P-003 | テストが proposal-only / probe-only を正しい挙動として固定している | `tests/test_init_update.py` は write roots が `{".codex/permission-probe-evidence"}` だけであること、`delegated author adapter must not be write-capable` であることを要求している。 | テスト契約自体が Epic v1 要件と逆方向になっている。 | 実装修正してもテストが失敗するため、要件達成の妨げになる。 |
| P-004 | `.codex/config.toml` の `agents.max_depth = 1` が depth=2 delegation と衝突している | provider / dogfooding の `.codex/config.toml` に `[agents] max_depth = 1` がある。 | E-RQ-007 は `system-architect` / `implementation-planner` が child specialist を使える bounded depth=2 を要求している。 | role skill が depth=2 を説明していても、host 設定がそれを許さない可能性が高い。 |
| P-005 | role skill と adapter の契約が食い違っている | `.agents/skills/spec-dock-system-architect/SKILL.md` は verified manifest / profile があれば `design.md` を create/update できると書く一方、adapter は proposal-only no-write を指示する。 | 同じ role に対して成功パスと禁止パスが同時に存在する。 | sub-agent の実行時判断が不安定になり、reviewer も何を正と見るべきか曖昧になる。 |
| P-006 | workflow docs / consent wording が read-only specialist 前提を残している | `workflow_issue.md` と `workflow_spec_authoring.md` は consent scope を reviewer / read-only specialist に限定し、write-capable delegation は別確認対象とする文言を持つ。 | v1 では bounded write-scoped draft authoring が標準ワークフローに昇格するため、単なる例外扱いでは不十分。 | ユーザー consent、report 記録、role 起動条件が古い境界のまま残る。 |
| P-007 | report template が write-capable delegation を通常 scope 外として固定している | `src/spec_dock/assets/spec_dock/templates/issue/report.md` の consent 表は read-only specialist と write-capable delegation の禁止境界を前提にしている。 | draft canonical authoring を正規 workflow とする場合、task manifest 付きの write-scoped delegation を記録する欄が必要。 | 実行証跡が proposal-only / exception 扱いになり、正規の監査情報を残せない。 |
| P-008 | 完了済み issue report が fallback-disabled を closure として記録している | `iss-00123/report.md` は canonical spec write-scoped delegation を有効化していないと明記する。`iss-00125/report.md` は proposal-only fallback discussion drafts だけを記録する。 | 記録自体は正しいが、これを Epic v1 達成と扱うと要件未達になる。 | PR 全体が「安全に未実装へ戻しただけ」に見える。 |
| P-009 | Epic plan の過去 v0 部分と v1 amendment の閉じ方が混在している | Epic plan は v0 historical plan を保持しつつ v1 amendment を追加しているが、現在の実装は v1 の actual write path まで到達していない。 | plan 上の完了条件と実装済み範囲の差分が読み手に伝わりにくい。 | spec-reviewer / deep-consultant の Epic-wide gate で「未達」を見落とす危険がある。 |
| P-010 | Evidence Adoption Ledger の所有と保存場所がまだ弱い | skill は evidence block を返すが、child specialist の evidence をどこに保存し、誰が採用 / 棄却 / 保留するかが実装契約として弱い。 | depth=2 を許すほど、 evidence の採否と責任境界が重要になる。 | 子 agent の意見が無検証に design / plan へ混入する危険がある。 |
| P-011 | artifact-level authority validation が不足している | requirement は `status` / `authority` / `grants` を分離するが、runtime / context-pack / lifecycle gate が proposed artifact を downstream authority から除外する実装証跡が十分ではない。 | canonical path に `authority: proposed` の artifact を置く設計では、tooling gate が安全境界になる。 | 未承認 draft を実装根拠として誤用する危険が残る。 |
| P-012 | exact target profile の生成 / 適用方法が未確定 | 現在の profile は static fallback であり、task manifest ごとに exact `design.md` / `plan.md` を許可する仕組みがない。 | broad write は危険だが、static probe-only では要件を満たせない。 | 実用的な write-scoped authoring の起動経路が存在しない。 |
| P-013 | issue completion / PR update 前の Epic-wide quality gate が仕様としてまだ弱い | ユーザーは全 issue 完了後、PR 更新前に development branch と完成状態の diff 全体を deep-consultant / spec-reviewer で見る gate を要求している。 | 個別 issue pass だけでは Epic 横断の矛盾を検出できない。 | 今回のような「各所は通っているが Epic 要件として未達」という状態を再発しやすい。 |

## 修正方針

| 対象問題 | 修正方針 |
|---|---|
| P-001 / P-002 / P-005 | `system-architect` / `implementation-planner` adapter を proposal-only 固定から、verified task manifest + role-scoped Permission Profile + positive/negative probe が揃った場合だけ exact target draft を編集できる契約に更新する。fallback 文言は残すが、成功パスを禁止しない表現に変える。 |
| P-002 / P-012 | static profile を broad write に変えるのではなく、task manifest に紐づく exact target profile contract を導入する。少なくとも `allowed_write_paths`、`forbidden_write_paths`、`profile_name`、`positive_probe`、`negative_probe`、`cleanup`、`fallback` を manifest に持たせる。 |
| P-003 | `tests/test_init_update.py` の「probe evidence only」「must not be write-capable」固定を改める。default fallback profile の安全性を保つテストと、task manifest 付き write-scoped profile contract を検証するテストに分割する。 |
| P-004 | provider / dogfooding の `.codex/config.toml` を `agents.max_depth = 2` に更新する。ただし fanout は広げず、child role allowlist と leaf-only 制約を skill / docs / tests に明記する。 |
| P-006 / P-007 | `workflow_issue.md`、`workflow_spec_authoring.md`、issue report template の consent / evidence 表を更新し、read-only specialist と write-scoped delegated draft authoring を分けて記録できるようにする。 |
| P-008 | 完了済み report は改ざんしない。代わりに Epic discussion、Epic report addendum、追加 corrective issue の report で「過去 issue は fallback-disabled の事実、v1 達成はこれから追加修正で閉じる」と明記する。 |
| P-009 / P-013 | Epic plan に追加是正 issue と Epic-wide pre-PR quality gate を明示する。個別 issue の完了後、PR 更新前に development branch との差分全体を deep-consultant と fresh spec-reviewer で確認する。 |
| P-010 | Evidence Adoption Ledger を draft authoring の必須成果物として整理する。source、role、claim、disposition、target section、rationale、evidence strength、adopter、reviewer、blocking を持たせる。 |
| P-011 | runtime / context-pack / lifecycle validation に artifact-level authority gate を導入する。`authority: proposed` は review/planning input まで、implementation / issue ready / issue finish / phase completion は `authority: approved` と該当 `grants.*: true` を必須にする。 |
| P-012 | 単一ファイル write が host 実装で不安定な場合の fallback を事前に設計する。第一候補は exact file write、失敗時は issue-local authoring sandbox directory などの限定 write path + diff gate を検討する。ただし broad `spec-dock/initiatives` write は採用しない。 |

## 具体修正案

### 1. Corrective issue を追加する

現在の PR / branch は Epic v1 を満たしていないため、既存 issue の報告書を上書きするのではなく、追加の corrective issue を作る。

候補:

- title: `Write-capable Delegated Draft Authoring Correction`
- slug: `write-capable-delegated-draft-authoring-correction`
- 目的:
  - `system-architect` / `implementation-planner` が actual `design.md` / `plan.md` draft を作成・更新できる契約、host adapter、tests、workflow docs、dogfooding pilot を整合させる。
- 完了条件:
  - adapter が proposal-only 固定をやめ、verified manifest / profile / probe 成功時の exact target write を許す。
  - tests が exact target write contract と forbidden path block を検証する。
  - dogfooding pilot で actual `design.md` / `plan.md` draft update を実証するか、host enforcement 不可なら Epic v1 を未達として明示し、PR を受け入れ可能とは主張しない。

### 2. Adapter を「成功パスありの fail-closed」に更新する

修正対象:

- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- `.codex/agents/system-architect.toml`
- `.codex/agents/implementation-planner.toml`

修正内容:

- description から `Read-only` / `Draft evidence only` を削除し、`verified task manifest` がある場合の draft authoring role として表現する。
- `proposal-only mode and do not write` を「manifest / profile / probe が不足する場合の fallback」に限定する。
- `Do not implement write-capable delegation` のような v1 要件に反する文言を削除する。
- `system-architect` は exact target `design.md` と exact evidence / ledger path だけを書ける。
- `implementation-planner` は exact target `plan.md` と exact evidence / ledger path だけを書ける。
- `requirement.md`、相手側 artifact、`report.md`、implementation files、tests、config、agent definitions、`.env*` は禁止する。
- network は原則 disabled のままにする。外部調査は child `researcher` などの evidence producer 経由に限定する。

### 3. Task Manifest を機械的な契約にする

manifest に最低限必要な項目:

- `role`: `system-architect` または `implementation-planner`
- `target_artifact`: symlink ではなく解決済み canonical path
- `source_revisions`: requirement / design などの upstream revision / hash
- `allowed_write_paths`: exact artifact path と exact evidence / ledger path
- `forbidden_write_paths`: requirement、相手側 artifact、report、src、tests、config、agent assets、secrets
- `permission_profile_name`: task-specific profile 名
- `positive_probe`: allowed path への write / cleanup
- `negative_probe`: forbidden path への write が拒否されること
- `diff_gate`: allowed path 以外の差分がないこと
- `fallback`: probe unavailable / fail-open / divergent / stale のとき proposal-only に戻ること

この manifest は raw intention ではなく、実行直前に解決した path と revision を固定する契約にする。

### 4. Depth=2 を host 設定と role 契約の両方で許可する

修正対象:

- `src/spec_dock/assets/install_root/.codex/config.toml`
- `.codex/config.toml`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
- dogfooding `.agents/skills/...`

修正内容:

- `agents.max_depth = 2` へ変更する。
- child role allowlist を明記する:
  - allowed: `repo-analyst`、`researcher`、`consultant`、`deep-consultant`、advisory `spec-reviewer`。
  - forbidden: `dev-coder`、`implementation-planner` as child of `system-architect`、`system-architect` as child of `implementation-planner`、write-capable author role の孫化。
- child は leaf-only evidence producer とし、canonical edit / implementation edit / promotion / final reviewer pass を禁止する。
- child output は親 authoring agent が Evidence Adoption Ledger に採否を記録してから draft artifact へ反映する。

### 5. Workflow docs / report template の consent と evidence を再定義する

修正対象:

- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- 必要に応じて `phase_design.md`、`phase_plan.md`、`phase_plan_issue.md`、`phase_plan_epic.md`

修正内容:

- read-only specialist consent と write-scoped delegated draft authoring consent を分離する。
- write-scoped delegated draft authoring は「常時許可」ではなく、Epic / Issue の requirement が許し、task manifest / profile / probe が揃う場合だけ許可する。
- report template に以下の記録欄を持たせる:
  - task manifest id / path
  - role
  - target artifact
  - allowed write paths
  - forbidden write paths
  - positive / negative probe result
  - diff gate result
  - child evidence list
  - Evidence Adoption Ledger summary
  - fallback decision

### 6. Runtime / validation gate を authority-aware にする

修正対象候補:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の context-pack / lifecycle / validation surface
- `tests/cli_runtime/`
- `tests/domain_runtime/`
- `tests/presentation_runtime/`

修正内容:

- proposed artifact が canonical path に存在しても implementation / issue ready / issue finish / phase completion の authoritative input にならないことを検証する。
- downstream purpose ごとに参照可能な authority / grants を定義する。
- missing authority metadata、invalid grants、stale approved revision、missing promotion record を block / fail として扱う。

### 7. Dogfooding pilot を actual write でやり直す

修正対象:

- 新しい corrective issue の dogfooding target
- report / discussions / actual `design.md` / `plan.md`

実証すべきこと:

- `system-architect` が manifest 付きで actual `design.md` を `authority: proposed` として更新する。
- `implementation-planner` が manifest 付きで actual `plan.md` を `authority: proposed` として更新する。
- 許可対象外 path の書き込みは拒否される、または diff gate で検出されて失敗する。
- main orchestrator が draft を最終所有せず、review / promotion まで proposed として扱う。
- child specialist を使った場合は Evidence Adoption Ledger に採否が残る。

## 実装順序案

1. S01: Epic plan / report addendum と corrective issue scaffold を作成する。
2. S02: workflow docs / report template の consent、manifest、Evidence Adoption Ledger、depth=2 契約を更新する。
3. S03: role skill と Codex agent adapter の矛盾を解消し、成功パスありの fail-closed 契約へ更新する。
4. S04: `.codex/config.toml` / provider config の `agents.max_depth = 2` と child role allowlist を整える。
5. S05: tests を proposal-only 固定から、default fallback と write-scoped manifest contract の二層テストへ更新する。
6. S06: runtime / context-pack / lifecycle / validation の authority-aware gate を必要範囲で実装する。
7. S07: dogfooding pilot で actual `design.md` / `plan.md` draft update を行い、positive / negative probe、diff gate、Evidence Adoption Ledger を記録する。
8. S90: provider / dogfooding parity、`spec-dock validate`、targeted tests、`git diff --check` を実行する。
9. S99: fresh `spec-reviewer` と deep-consultant による issue-level review を pass させる。
10. G10: 全 issue 完了後、PR 更新前に development branch と完成状態の diff 全体を対象に Epic-wide deep-consultant analysis と fresh spec-reviewer review を実施し、指摘を修正して再レビュー pass まで回す。

## 受け入れ条件

- Adapter:
  - `system-architect` / `implementation-planner` が proposal-only 固定ではない。
  - manifest / profile / probe が揃う場合の exact target write 成功パスを持つ。
  - manifest / profile / probe が不足する場合は fail-closed で proposal-only に戻る。
- Permission:
  - broad `spec-dock/initiatives` write を許可しない。
  - exact target artifact と exact evidence / ledger path だけを許可する。
  - forbidden path に対する negative probe または diff gate がある。
- Depth:
  - `agents.max_depth = 2` が provider / dogfooding で整合している。
  - child role は leaf-only evidence producer に限定される。
- Tests:
  - 既存の probe-only 固定テストが修正されている。
  - write-scoped manifest contract、forbidden path block、depth=2 allowlist、authority gate のテストがある。
- Runtime / lifecycle:
  - `authority: proposed` artifact は downstream authority にならない。
  - `authority: approved` + grants + promotion record が downstream gate の条件になる。
- Dogfooding:
  - actual `design.md` draft update と actual `plan.md` draft update の証跡がある。
  - proposed のままでは implementation / finish に進めないことが確認されている。
- Review:
  - issue-level spec-reviewer / deep-consultant の指摘が解決済み。
  - Epic-wide pre-PR gate で development branch との差分全体を review し、pass している。

## やってはいけない修正

- `spec-dock/initiatives` 全体や repo 全体を write 可能にして要件達成と見なす。
- `status: draft` だけを安全境界にする。
- 完了済み `iss-00123` / `iss-00125` の report を、当時実行していない actual write 実績に書き換える。
- fallback-disabled / proposal-only の実績を Epic v1 acceptance pass として扱う。
- child specialist に canonical artifact edit、implementation edit、promotion、final reviewer pass を許す。
- positive probe だけで済ませ、negative probe / diff gate を省く。
- Desktop App と CLI の Permission Profile 挙動差を検証せずに本番境界として扱う。

## 未解決論点

- task-specific Permission Profile をどの層で生成 / 注入するか:
  - static TOML profile だけでは exact target を動的に変えられない。
  - `codex exec -c default_permissions=...` 方式、temporary profile file、orchestrator-generated profile のどれを採用するかは追加調査と実証が必要。
- exact file write と directory write のどちらを採用するか:
  - exact file write が理想だが、host / patch tool / atomic write の制約で不安定なら、限定ディレクトリ + diff gate を検討する。
  - ただし broad initiatives write は採用しない。
- Evidence Adoption Ledger の保存場所:
  - `report.md` 内、issue-local `discussions/`、artifact-adjacent ledger のどれを正本にするか決める必要がある。
- runtime authority gate の最小実装範囲:
  - まず validation / context-pack から始めるか、issue ready / finish commands まで同時に閉じるかを設計で決める。
- Desktop App 対応:
  - CLI で先に検証し、Desktop は probe が通るまで補助 UI とする方針が妥当だが、ユーザー体験上の扱いを明文化する必要がある。

## 結論

現状の実装は、v0 fallback としては安全に整理されているが、Epic v1 の核心である「`system-architect` が actual `design.md` draft を、`implementation-planner` が actual `plan.md` draft を作成・更新する」という要件を満たしていない。

したがって、このコードは現状のまま受け入れるべきではない。次に行うべきことは、完了済み issue を改ざんすることではなく、Epic v1 の追加是正 issue を作成し、adapter / Permission Profile / tests / workflow docs / report template / depth=2 / runtime authority gate / dogfooding pilot を一貫した契約として修正することである。

この修正は「書けるようにする」だけでは足りない。書ける範囲を exact target に限定し、書けない範囲を probe / diff gate で証明し、`authority: proposed` の draft が downstream authority にならないことを runtime / workflow / reviewer gate で保証する必要がある。
