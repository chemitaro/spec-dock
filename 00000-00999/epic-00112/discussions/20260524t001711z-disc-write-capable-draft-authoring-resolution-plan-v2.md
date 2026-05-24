---
種別: ディスカッション
ID: "20260524t001711z-disc-write-capable-draft-authoring-resolution-plan-v2"
タイトル: "Write-capable Delegated Draft Authoring Resolution Plan v2"
関連GitHub: ["#112", "#119"]
状態: "draft"
作成者: "Codex"
作成日: "2026-05-24"
親: ["epic-00112", "init-local-00003"]
前版: "20260523t235448z-disc-write-capable-draft-authoring-gap-analysis"
---

# Write-capable Delegated Draft Authoring Resolution Plan v2

## 目的

この v2 は、前版 `20260523t235448z-disc-write-capable-draft-authoring-gap-analysis.md` で残した未解決論点を、実装可能で検証可能な修正計画へ落とし込む。

前版は「現状の問題リスト」と「修正方針」を整理した。本 v2 はさらに一歩進めて、次の設計判断を固定する。

- `system-architect` / `implementation-planner` の proposal-only 固定は Epic v1 要件未達として扱う。
- CLI-first で、main orchestrator が task manifest と task-specific Permission Profile を生成 / 注入する。
- `system-architect` は exact target の actual `design.md`、`implementation-planner` は exact target の actual `plan.md` を `status: draft` / `authority: proposed` として更新できることを v1 acceptance の必須条件にする。
- limited directory write や discussions-only output は fallback / candidate evidence であり、actual canonical draft write の代替として acceptance pass に数えない。
- Desktop App は同等 probe が通るまで proposal-only / manual fallback に限定する。

## 追加分析体制

この v2 は、前版に続いて以下の追加分析を統合した。

- deep-consultant `Einstein` (`019e5752-f09b-7a53-96f1-3fc8fefc8fc3`):
  - 未解決論点ごとの推奨解、反対案の却下理由、具体修正計画、必須検証を分析。
- researcher `Cicero` (`019e5753-1142-7ca1-9b7c-0e215633f03a`):
  - Codex Permission Profile / subagents / config / Desktop App 差分の一次情報を調査。
- repo-analyst `Ramanujan` (`019e5753-3071-70c0-b498-a26d17a17286`):
  - repo 内の影響ファイル、既存矛盾、更新すべきテスト、実装順序を棚卸し。
- main orchestrator:
  - OpenAI Codex 公式ドキュメントを直接確認し、sub-agent 分析と repo 実態を統合。

## 一次情報から固定する制約

Codex Permission Profile は beta であり、旧 sandbox 設定とは混在させない。公式ドキュメントは、`default_permissions` / `[permissions]` と `sandbox_mode` / `sandbox_workspace_write` のどちらか一方を使う必要があり、`sandbox_mode` が active config layer に現れると旧 sandbox settings が使われると説明している。

Codex Permission Profile の filesystem entries は `read` / `write` / `deny` を使う。`write` は OS が許す範囲で create / modify / rename / delete を許し、`deny` は read/write を拒否する。より具体的な entry が広い entry を上書きし、同一 path では `deny > write > read` の順に優先される。

Codex subagents は親の sandbox policy を継承する。また、親ターンの live runtime override、たとえば `/permissions` 変更や `--yolo` も child に再適用される。したがって、per-agent TOML だけを強い安全境界として扱うのは不十分であり、実行時 probe と diff gate が必要である。

Codex custom agent file は `~/.codex/agents/` または `.codex/agents/` の standalone TOML で定義され、spawned session の config layer として読み込まれる。ただし、親 runtime override が再適用されるため、role file だけで独立した権限保証を閉じない。

`agents.max_depth` は root session を depth 0 とし、既定は 1 である。depth=2 を許可する場合は、設定変更だけでなく child allowlist、leaf-only、no-grandchild、no peer-author、no implementation-child の契約が必要である。

Codex Desktop App と CLI は同じ underlying agent / configuration を使うが、異なる version に依存することがあり、experimental features は CLI に先に入る場合がある。したがって、Desktop App は CLI と同等の Permission Profile / subagent 挙動を probe で確認するまで acceptance path にしない。

参照した一次情報:

- OpenAI Codex Permissions: https://developers.openai.com/codex/permissions
- OpenAI Codex Subagents: https://developers.openai.com/codex/subagents
- OpenAI Codex Config Reference: https://developers.openai.com/codex/config-reference
- OpenAI Codex App Troubleshooting: https://developers.openai.com/codex/app/troubleshooting

## 推奨する最終方針

採用方針は次の通り。

1. CLI-first:
   - actual write-capable delegated draft authoring の verified path は、まず Codex CLI に限定する。
   - Desktop App は `host_surface=desktop` として記録し、同等 probe が通るまで proposal-only / manual fallback にする。
2. Main-orchestrator-generated manifest:
   - task manifest と task-specific Permission Profile は、sub-agent ではなく main orchestrator または spec-dock runtime helper が生成する。
   - 権限を使う側の sub-agent が自分の権限境界を生成してはならない。
3. Task-specific profile injection:
   - static adapter TOML は fallback profile と role contract だけを持つ。
   - actual write を行う session では、main orchestrator が generated profile を一時 config layer または CLI `-c` override で注入し、`default_permissions` でその profile を選ぶ。
4. Exact canonical file write:
   - `system-architect` の v1 acceptance は exact target actual `design.md` write 成功で閉じる。
   - `implementation-planner` の v1 acceptance は exact target actual `plan.md` write 成功で閉じる。
   - limited directory write は host 制約の調査用 fallback / candidate draft に留め、v1 acceptance には数えない。
5. Report-owned Evidence Adoption Ledger:
   - Evidence Adoption Ledger の正本は scope-local `report.md` とする。
   - authoring agent が書けるのは candidate evidence / candidate ledger まで。main orchestrator が採否を `report.md` に統合する。
6. Authority-aware runtime gate:
   - `authority: proposed` artifact は review / planning input には使えても、implementation start、issue ready、issue finish、phase completion には使えない。
   - `authority: approved`、exact grants、promotion record、fresh reviewer pass の組み合わせを downstream gate の条件にする。
7. Bounded depth=2:
   - `agents.max_depth = 2` を許可する。
   - ただし child は leaf-only evidence producer に限定し、canonical edit、implementation edit、promotion、final reviewer pass、peer author role child、grandchild を禁止する。

## 論点別の解決案

### R-001 Task-specific Permission Profile の生成 / 注入

推奨解:

- `spec-dock` runtime helper を追加し、task manifest から task-specific Permission Profile TOML fragment を生成する。
- main orchestrator はその helper の出力を確認し、Codex CLI invocation へ一時 config layer または `-c` override として渡す。
- adapter TOML は dynamic path を直接持たない。fallback profile、role identity、禁止事項、manifest/probe 必須条件だけを持つ。

理由:

- exact target は issue / epic / initiative ごとに変わるため、static TOML では正確に表現できない。
- broad `spec-dock/initiatives` write は安全境界として広すぎる。
- sub-agent に profile 生成を委ねると、権限を使う主体が権限境界を定義する形になり、fail-closed 設計と矛盾する。
- `input_authority` が欠落、不一致、stale、または reviewer / promotion evidence と一致しない場合、helper は Permission Profile と probe plan を生成してはならない。これは E-AC-012 の requirement authority prerequisite を actual write の前提として強制するためである。
- negative probe は実 artifact への破壊的 write attempt ではなく、forbidden boundary 配下の disposable sentinel だけを使う。sentinel が unexpectedly created された場合は fail-open とし、cleanup evidence と dirty diff abort を report に残す。

manifest の最小 schema:

```yaml
role: spec-dock-system-architect | spec-dock-implementation-planner
host_surface: cli | desktop
scope_id: iss-xxxxx | epic-xxxxx | init-xxxxx
target_artifact:
  kind: design | plan
  path: /absolute/or/workspace-relative/resolved/path/to/design.md
source_revisions:
  requirement: <hash-or-revision>
  design: <hash-or-revision-or-none>
input_authority:
  requirement:
    authority: approved
    required_grants:
      - review_input
      - planning_input
      - design_baseline
    promotion_record_path: <report.md#promotion-record-or-ledger-entry>
    approved_revision: <revision>
    approved_content_hash: <hash>
    reviewer_verdict: pass
    reviewer_target_hash: <hash>
    stale_check: fresh
  design:
    required_for_role: spec-dock-implementation-planner
    authority: approved
    required_grants:
      - planning_input
      - design_baseline
    promotion_record_path: <report.md#promotion-record-or-ledger-entry>
    approved_revision: <revision-or-none>
    approved_content_hash: <hash-or-none>
    reviewer_verdict: pass
    reviewer_target_hash: <hash-or-none>
    stale_check: fresh
allowed_write_paths:
  - <exact target design.md or plan.md>
  - <candidate evidence dir>
forbidden_write_paths:
  - <requirement.md>
  - <peer artifact>
  - <report.md>
  - src
  - tests
  - .codex
  - .agents
  - .env
permission_profile_name: spec_dock_task_<scope>_<role>_<artifact>
positive_probe:
  target: <exact target or dedicated probe sibling>
  expected: write succeeds
negative_probe:
  strategy: non_destructive_sentinel
  targets:
    - <disposable sentinel under forbidden requirement/report/src/tests/.codex/.agents/.env-like boundary>
  expected: write fails
  must_not_touch:
    - <real requirement.md>
    - <real design.md unless target>
    - <real plan.md unless target>
    - <real report.md>
    - <real source/test/config/secret files>
  cleanup: <remove sentinel only if unexpectedly created; abort if cleanup cannot prove clean diff>
diff_gate:
  allowed_paths:
    - <target artifact>
    - <candidate evidence dir>
fallback: proposal-only
```

`stale_check: fresh` は、referenced promotion record と reviewer evidence が current approved revision / approved content hash に一致していることを意味する。

却下する案:

- static TOML だけで解決する案:
  - dynamic exact path を表現できず、probe-only か broad write のどちらかになる。
- `sandbox_workspace_write.writable_roots` に対象 path を入れる案:
  - 旧 sandbox model と Permission Profile を混在させる危険があり、workspace 内を狭める用途ではなく追加 writable roots として誤解されやすい。
- sub-agent が自分で profile を生成する案:
  - 権限利用者が権限境界を作るため、監査と fail-closed の主体が崩れる。

### R-002 Exact file write と limited directory write

推奨解:

- acceptance path は exact canonical file write とする。
- `system-architect`: exact `design.md`。
- `implementation-planner`: exact `plan.md`。
- candidate evidence は `discussions/delegated-authoring/<task-id>/` などに限定する。
- host が exact file write を enforce できない場合は limited directory candidate draft へ fallback するが、それを E-AC-003 / E-AC-004 の pass として扱わない。

理由:

- Epic v1 は actual `design.md` / `plan.md` draft authoring を要求している。
- limited directory write だけでは「メモ書きでは困る」というユーザー意図を満たさない。
- broad directory write は accidental edit と prompt drift の影響範囲が大きすぎる。

運用上の補助策:

- direct file write が patch / atomic rename の制約で不安定な場合、probe 用には target sibling の dedicated probe path を使う。
- actual write の後は diff gate で allowed path 以外の変更を拒否する。
- exact file write が不可能な host surface は proposal-only fallback にする。

### R-003 Evidence Adoption Ledger の保存場所と正本性

推奨解:

- 正本は scope-local `report.md` の Evidence Adoption Ledger とする。
- child specialist / authoring agent が作るのは candidate evidence:
  - `discussions/delegated-authoring/<task-id>/research-*.md`
  - `discussions/delegated-authoring/<task-id>/candidate-ledger.md`
  - `discussions/delegated-authoring/<task-id>/handoff.md`
- main orchestrator が candidate evidence を確認し、採用 / 部分採用 / 棄却 / 保留 / stale / blocked を `report.md` の ledger に統合する。

理由:

- final ownership は main orchestrator にある。
- `report.md` は workflow gate と promotion evidence の正本である。
- discussions-only ledger では final adoption 判断と phase gate が分離し、後続 agent が誤読しやすい。

ledger entry の必須 fields:

- `id`
- `adoption_status`
- `source`
- `source_role`
- `claim`
- `target_artifact`
- `target_section`
- `rationale`
- `evidence_strength`
- `evidence_path`
- `adopter`
- `reviewer`
- `blocking`
- `next_action`

block rule:

- `blocked` または `stale` が unresolved の場合、promotion、implementation start、issue ready、issue finish、phase completion を止める。
- `deferred` は revisit condition と non-blocking rationale がある場合だけ残せる。

### R-004 Runtime authority gate の最小実装範囲

推奨解:

最小実装範囲は次の 3 つ。

1. `spec-dock validate`
   - artifact metadata と Evidence Adoption Ledger の整合を検証する。
   - proposed artifact が downstream grant を持っていないことを検証する。
2. `context-pack`
   - purpose-aware に `review/planning` と `implementation/finish` を分ける。
   - implementation / finish purpose では proposed artifact を authoritative input にしない。
3. `issue finish`
   - `authority: approved`、exact grants、promotion record、fresh reviewer gate を満たさない場合は fail-closed にする。

既存の `domain/authority.py` と tests は active manifest / issue lifecycle 向けの authority gate を持っている。これを artifact-level `design.md` / `plan.md` metadata にも拡張する。

注意:

- active manifest の synthetic approved promotion record は active selection 用であり、artifact approval の代替ではない。
- `authority: proposed` artifact を canonical path に置く設計では、context-pack / lifecycle gate が安全境界の本体になる。

### R-005 Desktop App と CLI の扱い

推奨解:

- CLI を verified path として先に閉じる。
- Desktop App は `host_surface=desktop` として manifest に記録するが、同等 positive / negative probe が通るまで proposal-only / manual fallback にする。
- Desktop 未対応は v1 全体の blocker ではなく、documented fallback として扱う。ただし Desktop で actual write が未検証なら Desktop path の acceptance は主張しない。

理由:

- 公式 docs は App と CLI が同じ underlying agent/configuration を使う一方で、異なる version に依存し、experimental features が CLI に先に入る場合があると説明している。
- Permission Profile は beta であり、host surface ごとに実測すべきである。

report 記録:

- `host_surface`
- `codex_cli_version`
- `codex_app_version` if applicable
- `profile_probe_status`
- `desktop_fallback_status`
- `acceptance_counted: true | false`

### R-006 Depth=2 の安全な運用制約

推奨解:

- provider / dogfooding config で `agents.max_depth = 2` を許可する。
- ただし `max_depth = 2` だけを実装完了としない。
- skill / workflow docs / tests に child graph constraints を入れる。

allowed graph:

```text
main orchestrator
  -> spec-dock-system-architect
      -> repo-analyst | researcher | consultant | deep-consultant | advisory spec-reviewer

main orchestrator
  -> spec-dock-implementation-planner
      -> repo-analyst | researcher | consultant | deep-consultant | advisory spec-reviewer
```

forbidden graph:

```text
authoring specialist -> child -> grandchild
authoring specialist -> dev-coder
system-architect -> implementation-planner
implementation-planner -> system-architect
leaf-only evidence producer -> canonical edit
leaf-only evidence producer -> final reviewer pass claim
```

運用 cap:

- `max_child_calls_per_authoring_task = 3` を推奨。
- deep-consultant は高コスト判断、researcher は外部一次情報、repo-analyst は内部影響範囲、consultant は選択肢整理に限定する。
- child output は candidate evidence であり、ledger disposition 前に draft artifact へ混入させない。

## 影響ファイルと修正内容

| 領域 | 対象 | 修正内容 |
|---|---|---|
| Epic docs | `epic-00112/plan.md`, `epic-00112/report.md` | corrective issue と G10 Epic-wide gate を明示する。fallback-only issue は v1 達成ではないと記録する。 |
| Adapter | `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`, `implementation-planner.toml`, dogfooding copies | read-only / proposal-only 固定文言を削除し、verified manifest/profile/probe 成功時の exact write success path を持つ fail-closed 契約にする。 |
| Config | `src/spec_dock/assets/install_root/.codex/config.toml`, `.codex/config.toml` | `agents.max_depth = 2`。必要なら child cap / role guidance を追加。 |
| Skills | provider / dogfooding `spec-dock-system-architect`, `spec-dock-implementation-planner` | manifest fields、allowed/forbidden paths、diff gate、candidate evidence、child constraints を機械的にする。 |
| Workflow docs | `workflow_spec_authoring.md`, `workflow_issue.md`, phase docs | write-scoped delegated draft authoring consent、task manifest、Desktop fallback、depth=2 constraints、ledger integration を明確化。 |
| Authoring docs | `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`, dogfooding `spec-dock/docs/authoring/issue-plan.md` | `plan.md` の field-level contract、closure evidence、amendment trigger、manifest/probe/diff/authority fields、report evidence destination を更新する。 |
| Templates | report templates / active-none report scaffold | task manifest、probe result、diff gate、candidate evidence、canonical Evidence Adoption Ledger 欄を追加。 |
| Runtime | `spec_dock_runtime/domain/authority.py`, context-pack, issue finish, validate surface | artifact-level authority gate を追加し、proposed artifact の downstream use を fail-closed にする。 |
| Tests | `tests/test_init_update.py`, runtime tests | proposal-only 固定 assertion を改め、exact target write contract、negative probe、depth=2、ledger blocker、authority gate を検証する。 |
| Dogfooding | corrective issue | actual `design.md` / `plan.md` draft write、probe、diff gate、ledger adoption を実証する。 |

## 具体修正計画

### S01 Corrective issue と Epic addendum

- 新規 corrective issue を作成する。
- Epic plan / report に次を追記する:
  - `iss-00123` / `iss-00125` は fallback-only / proposal-only の事実として保持する。
  - v1 acceptance は corrective issue で actual write を実証して閉じる。
  - PR 更新前に G10 Epic-wide deep-consultant + spec-reviewer gate を必須にする。

完了条件:

- 完了済み issue report を改ざんしていない。
- v1 未達状態と corrective issue の責務が明確。

### S02 Manifest / Permission helper 設計

- spec-dock runtime helper を設計する。
- 入力:
  - role、scope、target artifact、source revisions、host surface。
  - `input_authority`: upstream requirement / design の promotion record、approved revision、approved content hash、fresh reviewer verdict / reviewer target hash、required grants、stale check result。
- 出力:
  - task manifest。
  - task-specific Permission Profile TOML fragment。
  - positive / non-destructive negative probe plan。
  - diff gate plan。

完了条件:

- helper の出力 schema が tests で検証される。
- upstream approval evidence が欠落、不一致、stale、または required grant 不足の場合、helper は profile/probe を生成せず blocked result を返す。
- generated profile は old sandbox settings と混在しない。
- broad write を生成しない。
- negative probe は real artifact を変更せず、disposable sentinel と cleanup evidence だけで forbidden boundary を検証する。

### S03 Workflow docs / templates

- `workflow_spec_authoring.md` / `workflow_issue.md` の consent を分離する。
- `docs/authoring/issue-plan.md` / provider copy を更新し、plan field-level contract に manifest/probe/diff/authority fields、closure evidence、amendment trigger、report evidence destination を追加する。
- report template に write-scoped delegated draft authoring 記録欄を追加する。
- Evidence Adoption Ledger の正本が `report.md` であることを明記する。

完了条件:

- read-only specialist consent と write-scoped delegated authoring consent が混ざっていない。
- manifest/probe/diff/fallback/ledger を report で追える。
- implementation-planner が参照する issue plan authoring contract と workflow docs が矛盾していない。

### S04 Adapter / config / skill alignment

- adapter から proposal-only 固定文言を削除する。
- adapter は fallback profile + success path contract にする。
- `.codex/config.toml` / provider copy を `agents.max_depth = 2` にする。
- role skill に child allowlist / cap / no-grandchild / no peer-author を明記する。

完了条件:

- role skill と adapter が同じ成功パス / fallback を説明している。
- tests が `max_depth = 2` と child constraints を確認する。

### S05 Runtime authority gate

- artifact-level metadata parser / validator を追加または既存 authority gate に接続する。
- draft artifact metadata schema を検証対象にする。actual write 後の `design.md` / `plan.md` は少なくとも `status`、`authority`、`grants`、`owner_role`、`draft_author_role`、`approval`、`source_revision`、`approved_revision`、`approved_hash` を持つ。
- `validate`、context-pack、issue finish の最小 3 surface で proposed downstream use を止める。

完了条件:

- `authority: proposed` の `design.md` / `plan.md` が implementation / finish に使われない。
- E-AC-001 の full metadata fields が欠落した draft artifact は validate / context-pack / lifecycle gate で incomplete または blocked になる。
- approved + grants + promotion record だけが downstream gate を通る。

### S06 Tests

更新するテスト:

- `tests/test_init_update.py`
  - adapter が proposal-only 固定でないこと。
  - task manifest / profile contract を持つこと。
  - manifest が `input_authority` を必須にし、approved revision / content hash / reviewer verdict / required grants / stale check を持つこと。
  - negative probe が non-destructive sentinel / cleanup / dirty diff abort を要求すること。
  - old sandbox settings と混在しないこと。
  - `max_depth = 2` と child constraints。
  - report template に manifest / probe / diff / ledger 欄があること。
  - provider/dogfooding `docs/authoring/issue-plan.md` が manifest/probe/diff/authority fields を含むこと。
- `tests/domain_runtime/test_authority.py`
  - artifact-level proposed / approved behavior。
  - missing / stale / mismatched upstream approval evidence が actual write helper を block すること。
  - draft artifact metadata schema の必須 fields 欠落が blocked / incomplete になること。
- `tests/cli_runtime/test_issue_lifecycle.py`
  - issue finish が proposed artifact を拒否すること。
- context-pack tests:
  - implementation purpose では proposed artifact を authoritative input にしないこと。
  - metadata incomplete な proposed artifact を authoritative / promotable input として扱わないこと。

完了条件:

- proposal-only 固定の assertion が消える。
- exact target write / forbidden path / authority gate / ledger blocker / full E-AC-001 metadata fields が検証される。

### S07 Dogfooding actual write pilot

- corrective issue で task manifest を作成する。
- `system-architect` に actual `design.md` draft update を行わせる。
- `implementation-planner` に actual `plan.md` draft update を行わせる。
- positive / negative probe、diff gate、candidate evidence、report ledger adoption を記録する。

完了条件:

- actual `design.md` / `plan.md` が `status: draft` / `authority: proposed` として更新され、`grants`、`owner_role`、`draft_author_role`、`approval`、`source_revision`、`approved_revision`、`approved_hash` を含む full E-AC-001 metadata が検証される。
- forbidden path に差分がない。
- `authority: proposed` のまま downstream gate が通らないことが確認される。

### S90 / S99 / G10 Quality gates

- S90:
  - provider / dogfooding parity。
  - `spec-dock validate`。
  - targeted unittest。
  - `git diff --check`。
- S99:
  - issue-level fresh spec-reviewer。
  - issue-level deep-consultant review。
- G10:
  - development branch と完成状態の diff 全体を対象に Epic-wide deep-consultant review。
  - fresh spec-reviewer review。
  - 指摘修正後に再レビュー pass。

## 必須テスト / 検証一覧

| 検証 | 期待結果 |
|---|---|
| TOML parse | adapter / config / generated profile が TOML として valid。 |
| sandbox mixing check | delegated authoring path に `sandbox_mode` / `[sandbox_workspace_write]` と Permission Profile が混在しない。 |
| positive probe | exact target `design.md` / `plan.md` または dedicated allowed probe path だけ write 成功。 |
| input authority gate | upstream requirement/design の promotion record、approved revision、approved content hash、fresh reviewer verdict/hash、required grants、stale check が揃わない場合、profile/probe を生成しない。 |
| negative probe | 実 artifact ではなく disposable sentinel / dry-run 相当で `requirement.md`、peer artifact、`report.md`、`src`、`tests`、`.codex`、`.agents`、`.env*` 境界の write 失敗を検証する。sentinel が作成された場合は cleanup evidence を残し、dirty diff が残れば abort。 |
| diff gate | allowed path 以外の差分があれば failure。 |
| draft metadata | actual `design.md` / `plan.md` draft は `status`、`authority`、`grants`、`owner_role`、`draft_author_role`、`approval`、`source_revision`、`approved_revision`、`approved_hash` を持つ。欠落時は blocked / incomplete。 |
| authority gate | `authority: proposed` は implementation / issue ready / issue finish / phase completion を通らない。 |
| ledger blocker | unresolved `blocked` / `stale` ledger entry が promotion / finish を止める。 |
| depth graph | allowed child graph は通り、depth=3、peer author child、dev-coder child は禁止。 |
| Desktop fallback | Desktop probe 未実施 / divergent なら acceptance_counted=false。 |
| dogfooding pilot | actual `design.md` / `plan.md` draft write と reviewer / deep-consultant gate が通る。 |

## 残す fallback

- manifest missing / stale:
  - proposal-only。
- Permission Profile unavailable / fail-open / divergent:
  - proposal-only。
- Desktop unverified:
  - proposal-only / manual authoring。
- exact file write unavailable:
  - limited directory candidate draft。ただし v1 acceptance には数えない。
- authority gate incomplete:
  - write-scoped canonical authoring を有効化しない。
- unresolved ledger blocker:
  - promotion / finish を止める。

## 修正してはいけないこと

- 完了済み `iss-00123` / `iss-00125` report を actual write 成功に書き換えない。
- broad `spec-dock/initiatives` write や repo-wide write で要件達成と見なさない。
- limited directory write を actual canonical draft write の代替にしない。
- Desktop と CLI を同等検証済みとして扱わない。
- `max_depth = 2` だけで depth=2 契約を満たしたと主張しない。
- child specialist に canonical edit、implementation edit、promotion、final reviewer authority を与えない。

## 結論

未解決論点の解決策は、「書けるようにする」ことではなく、「main orchestrator が生成した task-specific manifest / Permission Profile によって、CLI 上で exact canonical draft file だけを書けることを証明し、同時に proposed artifact が downstream authority にならないことを runtime gate で保証する」ことである。

この v2 に基づく corrective issue は、adapter、config、skills、workflow docs、templates、runtime gate、tests、dogfooding pilot を一体で直す必要がある。どれか一つだけを表面修正しても、Epic v1 の acceptance は満たせない。
