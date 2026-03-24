---
種別: 実装計画書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28", "https://github.com/chemitaro/spec-dock/issues/28"]
状態: "in_progress"
作成者: "Codex CLI"
最終更新: "2026-03-24"
依存: ["requirement.md", "design.md"]
親: []
---

# issue-28-runtime-regression-bugs manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001 create atomicity`
  - `AC-002 local-only readiness`
  - `AC-003 required artifact validation`
  - `AC-004 GitHub URL safety`
  - `AC-005 freshness clarity`
  - `AC-006 active pathway`
  - `AC-007 CLI symmetry and disambiguation`
  - `AC-008 doctor guidance`
  - `AC-009 duplicate sequence validation`
  - `AC-011 current repo slug parity across github-aware commands`
  - `AC-012 domain/application validation boundary`
  - `AC-013 repo-aware numeric deps resolution`
  - `AC-014 stale active pathfile healing`
  - `AC-015 same-repo URL-linked sync fetch efficiency`
  - `AC-016 current-repo-aware branch inference under repo overlap`
  - `AC-017 create outcome-specific recovery guidance`
  - `AC-018 repo-scoped exact target resolution`
  - `AC-019 scoped dependency reference contract`
  - `AC-020 create intermediate state safety`
- EC:
  - requirement に個別 EC は未定義のため、本計画では `design.md` の 4 設計テーマと `workflow_issue.md` の quality gate を実行契約として扱う
- 制約:
  - 既存の file-based runtime と layered architecture を維持する
  - provider-side source of truth は `src/spec_dock/assets/spec_dock/...` を優先する
  - `issue --no-github` を含む local-first の逃げ道を維持する
  - backward compatibility を壊す破壊的 CLI 変更は避け、additive change を基本とする
  - docs impact と final diff review quality gate を省略しない

## マイルストーン一覧
- M1:
  - 対象: create transaction を導入し、parallel create で duplicate id / seq を予防する
  - exit:
    - `new initiative|epic|issue|doc` が共通 lock/transaction 配下で動く
    - duplicate id / duplicate seq の regression test が通る
- M2:
  - 対象: status/readiness と artifact/repair contract を整え、local-only / broken state / active 未設定を安全に扱う
  - exit:
    - `deps check` と `active set` が同じ readiness contract を使う
    - required artifact 欠損、duplicate seq、broken meta、stale active pointer を validate/doctor で扱える
- M3:
  - 対象: GitHub targeting と CLI intent surface を安全化し、docs impact と最終 quality gate を閉じる
  - exit:
    - wrong-repo URL import を safe default で防ぐ
    - `new issue` / `active set` の explicit intent surface が揃う
    - stale projection の source/freshness が CLI/json に露出する

## ステップ一覧
- S01:
  - 観測可能な振る舞い: 並列 `new initiative|epic|issue` でも duplicate id が発生しない
  - closes:
    - B01 create allocator race
  - review gate:
    - create transaction と repo-level lock の責務分離が review で説明できる
- S02:
  - 観測可能な振る舞い: 並列 `new doc` でも duplicate seq が発生せず、壊れた seq 重複は validate で fail する
  - closes:
    - B02 discussion sequence race
    - AC-009 duplicate sequence validation
  - review gate:
    - discussion allocator が S01 と同じ safety model に統合されている
- S03:
  - 観測可能な振る舞い: local-only / GitHub-linked issue の status/readiness が `deps check` と `active set` で一致する
  - closes:
    - B03 local-only deps/active inconsistency
    - B09 stale projection
  - review gate:
    - `authority / effective_status / source / stale` contract が domain/application/presentation で整合している
- S04:
  - 観測可能な振る舞い: required artifact 欠損、broken meta、stale active pointer を validate/doctor/active fallback が supported path として扱う
  - closes:
    - B04 validate gap
    - B05 repair gap
    - B06 active-not-set pathway gap
  - review gate:
    - artifact matrix と doctor guidance が同じ contract を再利用している
    - persisted active manifest recovery で `context-pack.md` と active entrypoint が不整合にならない
    - persisted manifest が stale/欠損でも、既存 active entrypoint 実体が健全なら `context-pack.md` がその実体へ追従する
- S05:
  - 観測可能な振る舞い: import/create/active の GitHub target 解釈が safe default かつ explicit intent で操作できる
  - closes:
    - B07 import wrong-repo risk
    - B08 create UX asymmetry
    - B10 numeric target ambiguity
  - review gate:
    - URL/number/id の曖昧性が command surface と error/help message の両方で説明可能になっている
    - foreign repo linked uniqueness が `repo + issue_number` 契約で説明可能になっている
    - sync/export の GitHub snapshot lookup も repo-aware key で整合し、current/foreign 同番号が混線しない
- S90:
  - 観測可能な振る舞い: shipped docs/help/dogfooding workspace が新 contract を誤読させない
  - closes:
    - docs impact resolution
  - review gate:
    - provider-side docs と consumer-side dogfooding 確認が両方完了している
    - checked-in dogfooding runtime で `doctor` と issue-28 追加 surface の executable smoke が通る
- S90F:
  - 観測可能な振る舞い: checked-in dogfooding runtime でも repo-scoped GitHub uniqueness / snapshot resolution が provider-side runtime と同じ contract で動く
  - closes:
    - AC-010 dogfooding runtime parity の runtime behavior 部分
  - review gate:
    - checked-in `spec-dock/scripts/...` の対象 runtime file が provider-side source of truth と同じ契約へ refresh されている
    - same-number coexistence の checked-in runtime regression test が通る
- S01I:
  - 観測可能な振る舞い: `new issue --create-github-issue` の GitHub create latency が repo-wide local create contention を起こさない
  - closes:
    - PR #29 R18 create lock scope narrowing
  - review gate:
    - `gh issue create` は lock 外、graph reload / parent re-resolve / uniqueness revalidation / local write は lock 内、という境界が review で説明できる
- S01J:
  - 観測可能な振る舞い: stable parent-not-found は GitHub issue 作成前に no-side-effect fail する
  - closes:
    - PR #29 R20 pre-GitHub parent validation
  - review gate:
    - pre-lock graph precheck は GH side effect を減らすが、authoritative parent revalidation は lock 内で維持する
- S01K:
  - 観測可能な振る舞い: initiative / epic / issue の post-create local failure がいずれも created issue number と kind-aware recovery guidance を返す
  - closes:
    - PR #29 R21 all-kinds post-create guidance
  - review gate:
    - supported `new <kind>` surface と recovery guidance surface が一致している
- S01L:
  - 観測可能な振る舞い: create-mode 全 kind が pre-GitHub graph preflight を通し、stable tree failure では remote side effect を起こさない
  - closes:
    - PR #29 R23 pre-GitHub graph preflight
  - review gate:
    - create lock narrowing を壊さず、pre-GH で防げる orphan issue だけを減らしている
- S03J:
  - 観測可能な振る舞い: current repo の unscoped linked initiative / epic / issue が index incomplete 時でも repo-aware fallback fetch で stale 化しない
  - closes:
    - PR #29 R28 current-repo fallback fetch for unscoped epic/initiative links
  - review gate:
    - `sync` / `active` / `deps` が current repo slug を helper まで渡し、unscoped current-repo linked node を `(current_repo_slug, issue_number)` として fallback fetch できる
- S03K:
  - 観測可能な振る舞い: numeric branch inference が repo overlap 後も current repo issue を優先し、active auto-update が止まらない
  - closes:
    - PR #29 R29 current-repo-aware branch inference under repo overlap
  - review gate:
    - explicit id match の優先順位を壊さず、numeric fallback だけ repo-aware 化している
    - current repo slug 不明時は ambiguity / no-match の fail-closed を維持する
- S03L:
  - 観測可能な振る舞い: current-repo linked node の no-origin continuity は write-time normalization と already-normalized metadata を中心に成立し、legacy unscoped current-repo linkage の automatic persistence upgrade は後続 `S03N` / `S03O` で縮退された
  - closes:
    - AC-021 no-origin continuity for current-repo linked nodes
    - manual test finding: no-origin mixed scoped/unscoped linkage ambiguity
  - review gate:
    - fail-closed policy は truly ambiguous graph に残しつつ、current repo と確定できる linkage だけを明示 scope 化している
    - write path persistence と legacy backfill の責務境界が説明できる
- S03M:
  - 観測可能な振る舞い: readonly `.meta.json` を持つ current-repo safe backfill が Windows を含む cross-platform contract で成功し、self-healing が permission drift だけを理由に止まらない
  - closes:
    - latest review finding: Windows readonly `.meta.json` backfill gap
  - review gate:
    - `.meta.json` permission helper が `write_meta()` / `backfill_github_repo_scope()` の両方で共有され、readonly final state contract が説明できる
- S03N:
  - 観測可能な振る舞い: lone unscoped legacy linkage は positive current-repo evidence がない限り bulk `sync --github` で silent backfill されず、fail-closed / manual remediation に残る
  - closes:
    - latest review finding: lone unscoped legacy linkage silent current-repo backfill
  - review gate:
    - `safe backfill` が uniqueness-only heuristic ではなく positive current-repo evidence に限定されていることを説明できる
- S03O:
  - 観測可能な振る舞い: bulk `sync --github` の dead sync-time backfill path は撤去され、no-origin continuity contract は write-time normalization 済み metadata に限定して説明される
  - closes:
    - latest review finding: dead sync-time backfill contract in bulk sync
  - review gate:
    - bulk sync が trusted evidence を持たない以上 mutate しない、という safety rationale と docs/impl parity を説明できる
- S99:
  - 観測可能な振る舞い: branch diff 全体が requirement/design/plan と一致し、実装・QA・spec review が通っている
  - closes:
    - final diff review quality gate
  - review gate:
    - reviewer が「この diff を merge してよい」と判断できる
- S98:
  - 観測可能な振る舞い: `manual-tests/` 配下に same-repo / foreign-repo / no-origin / stale-active を再現できる手動テスト環境と checklist/report scaffold が用意されている
  - closes:
    - comprehensive manual verification preparation for repo-scope and active recovery
  - review gate:
    - `discussions/055` のケース一覧、GitHub fixture repo、workspace topology、完了条件が spec review で説明可能
    - manual test scaffold が `manual-tests/` の既存 log contract と矛盾しない
- S98A:
  - 観測可能な振る舞い: enriched exploratory manual round が current/foreign/no-origin/pathfile の 4 workspace で実行され、live churn・recovery submatrix・3 checkpoint organic session の evidence が report に残る
  - closes:
    - comprehensive manual verification execution for repo-scope, active recovery, and exploratory churn
  - review gate:
    - `discussions/055` の `MT-00` から `MT-08` が verdict 付きで完了している
    - same-number overlap、live churn、recovery submatrix、organic checkpoints の evidence が report artifact に残っている
- S01P:
  - 観測可能な振る舞い: `gh issue create` 後の failure surface が outcome class ごとに guidance を返し、local-write-committed cleanup failure で blind rerun を案内しない
  - closes:
    - PR #29 R30 post-create cleanup failure guidance
    - root-cause remediation for repeated review loop in create/post-create failure handling
  - review gate:
    - `remote-only failure` と `local-write-committed cleanup failure` が別 outcome class として説明できる
    - raw `release_error` 単独露出が provider / checked-in runtime で残っていない
- S01Q:
  - 観測可能な振る舞い: partial local write は create phase として分類され、blind rerun ではなく doctor-first guidance を返す
  - closes:
    - AC-020 create intermediate state safety の write-phase 分
    - PR29 latest review partial execute_create_plan write classification
  - review gate:
    - `none/scaffold_copied/meta_written/post_write_verified` の phase contract が guidance と parity test で説明できる
- S04J:
  - 観測可能な振る舞い: create lock 下の missing `.meta.json` は in-progress/stale-create 系として分類され、恒久 corruption と混同しない
  - closes:
    - AC-020 create intermediate state safety の read-side 分
    - PR29 latest review in-progress scaffold diagnosis
  - review gate:
    - reader/doctor/validate が create state classification を共有している
- S04K:
  - 観測可能な振る舞い: persisted active manifest の stale path が same-layer の別 node を指していても、`update` はその node を誤採用せず id-based recovery か placeholder fallback へ倒れる
  - closes:
    - AC-006 active pathway の persisted path trust boundary
    - PR29 latest review persisted active path must match manifest id
  - review gate:
    - persisted path は `.meta.json` の `id` / `type` 一致がない限り recovery target にならない
- S05J:
  - 観測可能な振る舞い: active/deps の URL target は exact repo scope を保持したまま foreign node を選べる
  - closes:
    - AC-018 repo-scoped exact target resolution
  - review gate:
    - URL target と bare numeric target の契約差が parser/application/test で一貫している
- S05K:
  - 観測可能な振る舞い: dependency ref は bare current-repo shorthand と scoped foreign ref を区別できる
  - closes:
    - AC-019 scoped dependency reference contract
  - review gate:
    - bare numeric ref の fail-closed contract と scoped ref exact resolution が docs/impl/tests で一貫している

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`, `S01L`, `S02`
- `AC-002` -> `S03`
- `AC-003` -> `S04`
- `AC-004` -> `S05`
- `AC-005` -> `S03`, `S05`
- `AC-006` -> `S04`
  - corrective scopes: `S04I`, `S04K`
- `AC-007` -> `S05`
  - corrective scopes: `S01N`, `S01O`
- `AC-008` -> `S04`
  - corrective scopes: `S01M`, `S01O`
- `AC-009` -> `S02`
- `AC-010` -> `S90`, `S90F`
  - corrective scopes: `S01M`, `S01N`, `S01O`
- `AC-011` -> `S05F`, `S05I`
  - corrective scopes: `S03J`
- `AC-012` -> `S04F`
- `AC-013` -> `S05G`
- `AC-014` -> `S04G`
- `AC-015` -> `S05H`
- `AC-016` -> `S03K`
- `AC-017` -> `S01P`
- `AC-018` -> `S05J`
- `AC-019` -> `S05K`
- `AC-020` -> `S01Q`, `S04J`
- `AC-021` -> `S03L`, `S03N`, `S03O`
- `windows-readonly-backfill-gap` -> `S03M`
- `lone-unscoped-backfill-gap` -> `S03N`
- `dead-sync-backfill-gap` -> `S03O`
- `manual verification prep` -> `S98`
- `manual verification execution` -> `S98A`
- `PR29-R18` -> `S01I`
- `PR29-R20` -> `S01J`
- `PR29-R21` -> `S01K`
- `PR29-R22` -> `S05I`
- `PR29-R23` -> `S01L`
- `PR29-R24` -> `S04I`
- `PR29-R25` -> `S01M`
- `PR29-R26` -> `S01N`
- `PR29-R27` -> `S01O`
- `PR29-R28` -> `S03J`
- `PR29-R29` -> `S03K`
- `manual-round-F1` -> `S03L`
- `PR29-R30` -> `S01P`
- `PR29-R31` -> `S05J`
- `PR29-R32` -> `S05K`
- `PR29-R33` -> `S01Q`
- `PR29-R34` -> `S04J`
- `PR29-R35` -> `S04K`
- `PR29-R36` -> `S03M`
- `PR29-R37` -> `S03N`
- `PR29-R38` -> `S03O`

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - `S01` step gate 通過時
    - `S02` step gate 通過時
  - scope:
    - `S01`: lock 契約、allocator integration、failure mode、duplicate guard、回帰テスト
    - `S02`: discussion seq integration、duplicate seq validation、`AC-001` の残差確認
- RG2 implementation review:
  - timing:
    - `S03` step gate 通過時
    - `S04` step gate 通過時
  - scope:
    - `S03`: status/readiness/freshness contract、presentation 露出、backward compatibility
    - `S04`: artifact matrix、doctor、active fallback、read-only meta と recoverability の整合
- RG3 implementation review:
  - timing:
    - `S05` 完了時に command surface と GitHub targeting をレビューする
  - scope:
    - argparse surface、repo identity validation、ambiguity handling、error/help text
- QG1 QA review:
  - timing:
    - 各 step gate で対象テストを通し、`S99` 前に full relevant suite と manual regression 再実行方針を確認する
  - scope:
    - `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/`, `tests/test_init_update.py` のうち影響範囲
- SG1 spec review:
  - timing:
    - `S90` で docs impact を閉じた時点
    - `S98` で manual verification topology を閉じた時点
  - scope:
    - `requirement.md` / `design.md` / `plan.md` / `report.md` と shipped docs/help の整合

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `spec-deps/current/report.md` に残す。
- review の合格単位と git commit の単位は一致させる。各 step は step gate の review/QA/report 更新が完了したタイミングでコミットする。
- `S90` は docs/spec review 完了後にコミットする。
- `S99` は最終 review の完了確認であり、新規コミットの前提にはしない。

## 実装ステップ

### S01 — create transaction で duplicate id を予防する
- target:
  - `new initiative|epic|issue` を repo-level create transaction 配下へ移す
  - duplicate id を post-facto ではなく preventive control で防ぐ
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/005`, `007`
- step boundary:
  - discussion seq と validator 追加は `S02` へ分離し、ここでは node id race に集中する
  - stale lock の診断導線は `S04` で扱うが、S01 の時点で acquire-side policy 自体は固定する
  - S01 では stale lock を自動破壊しない。lock acquire は metadata を読める範囲で露出し、timeout または stale 判定時は no-write で失敗し `doctor` へ誘導する
  - `AC-001` の完了は `S01L` / `S02` を含めて判定する。S01 単体では B01 と node create 側の atomicity を閉じる

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S01` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — lock 基盤と node create orchestration
- purpose:
  - application/infra に create lock を導入し、`load -> allocate -> write -> post-write guard` を 1 critical section に収める
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/...`
  - `tests/cli_runtime/...`

##### I1 — failing regression を先に固定する
- slice goal:
  - 並列 `new initiative` / `new epic` / `new issue` で duplicate id が再現するテストを追加する

###### Red
- failing test:
  - 並列 `new initiative` / `new epic` / `new issue` のいずれでも duplicate id で壊れうる現在挙動を再現する runtime test
- expected failure:
  - duplicate id が成立する、または duplicate guard が後段で落ちる

###### Green
- minimum implementation:
  - repo-global lock acquire/release と bounded wait/failure surface を導入する
- pass condition:
  - 並列 create の duplicate id regression test が通る

###### Refactor
- cleanup target:
  - lock API の責務分離と error surface の整形
- invariants to keep green:
  - file-based runtime と既存 ID モデルを維持する

##### I2 — contention failure contract を固定する
- slice goal:
  - lock が取得できない場合に bounded wait と stale-lock policy に従って安全側 failure することを固定する

###### Red
- failing test:
  - 先行 create が lock を保持している間に後続 create が timeout/failure surface を返す regression test
  - stale metadata を持つ lock file が存在する場合に acquire が no-write failure と `doctor` 誘導を返す regression test
- expected failure:
  - 現状は lock 契約自体がなく、競合時の失敗形と stale lock の扱いが未定義

###### Green
- minimum implementation:
  - lock acquire timeout の契約値を固定し、テストでは短い設定値を注入できる形にする
  - timeout/stale lock の failure message に wait 時間、lock path、読めた lock metadata、`doctor` 誘導を含める
  - bounded wait、stale-lock safe failure、後続 create の no-write 保証を導入する
- pass condition:
  - contention failure regression test と stale lock regression test が通る
  - 失敗時に partial create を増やさず、観測可能な failure surface が安定している

###### Refactor
- cleanup target:
  - lock metadata、timeout 設定、error rendering の整理
- invariants to keep green:
  - timeout/failure contract が後続の `doctor` 診断導線と矛盾しない

#### step gate
- review:
  - lock scope、timeout 契約、stale lock acquire-side policy、post-write duplicate guard の位置と責務境界を説明できる
- expected tests:
  - duplicate id prevention regression（initiative/epic/issue を含む）
  - lock contention failure regression
  - stale lock safe failure regression
  - 既存 create command 回帰
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01I — external GitHub create を create lock の外へ出す
- target:
  - `new issue` の create mode で実行される `gh issue create` を repo-global create lock の外へ出す
  - external GitHub latency が `new doc` / local-only `new` / `import issue` を false contention で block しないようにする
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/035`
- step boundary:
  - lock scope を狭める corrective fix に限定し、remote rollback や GitHub issue close 補償処理までは扱わない
  - graph-derived parent resolution / uniqueness revalidation / write / post-write duplicate guard は lock 内のまま維持する
  - provider-side source of truth の修正後、checked-in dogfooding runtime にも parity を反映する

#### Red
- failing test:
  - slow `issue_create()` 中でも別 thread の local-only create が timeout せず成功する runtime regression
  - delayed `issue_create()` の pre-lock window 中に parent もしくは competing graph state が変化しても、lock 内 reload / revalidation で no-write fail または deterministic success になる regression
  - `issue_create()` 成功後に lock acquire / parent revalidation / uniqueness revalidation / write failure になった場合、created GitHub issue number と retry/link guidance を返す regression
  - invalid title / invalid slug が引き続き `gh issue create` 前に失敗する regression を維持
- expected failure:
  - 現行実装では slow `issue_create()` が lock を保持し、後続 local create が `create lock acquisition failed` で落ちる

#### Green
- minimum implementation:
  - `create_node_core()` で pure input validation と optional `gh issue create` を lock 外へ移す
  - pre-lock GitHub body は graph-independent minimal body とし、`Epic:` / `Initiative:` など graph 依存文脈を含めない
  - pure input validation は、少なくとも `--id + github mode`、required parent selector 欠落、partial repo identity を pre-GH で reject する
  - lock 取得後は graph reload、current parent/context の再解決、repo-aware uniqueness 再検証、write、post-write duplicate guard を維持する
- pass condition:
  - GitHub create latency regression と既存 create regression がともに通る

#### Refactor
- cleanup target:
  - pre-lock / in-lock responsibilities を helper 境界で整理する
- invariants to keep green:
  - duplicate id / duplicate GitHub linkage の preventive control を弱めない
  - checked-in dogfooding runtime parity を含む corrective scope であることを report に残す

#### step gate
- review:
  - lock scope の縮小で local atomicity が損なわれていないことを説明できる
- expected tests:
  - slow GitHub create non-blocking regression
  - delayed GitHub create + parent/context revalidation regression
  - post-GitHub-create local failure guidance regression
  - post-GitHub-create uniqueness revalidation failure guidance regression
  - minimal GH body invariant regression
  - pure input invalid request が `gh issue create` 前に no-side-effect failure する regression
  - invalid title / invalid slug no-gh-call regression
  - checked-in dogfooding runtime の executable parity regression
  - checked-in runtime でも post-GitHub-create local failure 時に created issue number と `--github-issue <n>` guidance を返す parity regression
  - 既存 create command 回帰
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01I` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01J — stable parent-not-found を pre-GitHub で fail-fast する
- target:
  - `new epic` / `new issue` の create mode で、stable parent absence を GitHub issue 作成前に no-side-effect fail にする
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/036`
- step boundary:
  - pre-lock では read-only graph precheck のみ追加し、authoritative parent resolution は lock 内の `plan_node_creation()` に残す
  - lock narrowing (`gh issue create` is outside lock) 自体は維持する

#### Red
- failing test:
  - nonexistent initiative を指定した `new epic --create-github-issue` が `issue_create()` 未呼び出しで失敗する regression
  - nonexistent epic を指定した `new issue --create-github-issue` が `issue_create()` 未呼び出しで失敗する regression
  - checked-in dogfooding runtime でも同じ no-side-effect regression

#### Green
- minimum implementation:
  - pre-GH phase に read-only graph load を追加する
  - create-mode で stable parent existence precheck を行い、missing parent は remote side effect 前に fail-fast する
  - lock 取得後は従来どおり graph reload と authoritative parent revalidation を維持する

#### Refactor
- cleanup target:
  - pre-GH stable validation と in-lock authoritative validation の責務境界を helper に分離する

#### step gate
- review:
  - orphan GitHub issue を減らしつつ、R18 の lock narrowing を壊していないことを説明できる
- expected tests:
  - provider runtime の no-gh-call parent-not-found regression
  - checked-in runtime parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01J` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01K — all-kinds post-create local failure guidance を揃える
- target:
  - initiative / epic / issue の GitHub create path で、post-create local failure 時の recovery guidance を kind-aware に揃える
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/037`
- step boundary:
  - command surface を狭めず、recovery message surface を supported kind 全体へ合わせる

#### Red
- failing test:
  - initiative create の lock failure が created issue number と `new initiative --github-issue <n>` を返す regression
  - epic create の write/template failure が created issue number と `new epic --github-issue <n>` を返す regression
  - checked-in dogfooding runtime でも同 guidance parity regression

#### Green
- minimum implementation:
  - post-create local failure wrapper の kind restriction を外す
  - recovery guidance を `new <kind> --github-issue <n>` ベースの kind-aware message builder にする

#### Refactor
- cleanup target:
  - kind-aware guidance text と wrapper call site の重複をなくす

#### step gate
- review:
  - supported create surface と orphan recovery surface が kind 間で整合している
- expected tests:
  - initiative guidance regression
  - epic guidance regression
  - checked-in parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01K` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01M — create lock failure guidance を executable doctor command に揃える
- target:
  - create lock acquisition / metadata write / release failure message が、repo-local shortcut の有無に依存しない executable doctor command を案内する
- design refs:
  - `design.md` の create lock / doctor guidance 方針
- step boundary:
  - create lock failure guidance の文言と parity test に限定し、doctor 自体の診断ロジックは変えない

#### Red
- failing test:
  - create lock contention/stale/release failure message が repo 上で実行不能な `spec doctor` だけを案内する regression
  - checked-in dogfooding runtime parity でも同じ guidance が維持される regression

#### Green
- minimum implementation:
  - create lock failure guidance builder を導入し、managed repo で実行可能な stable doctor command へ統一する
  - provider runtime と checked-in runtime parity を揃える

#### step gate
- review:
  - create lock 系 failure から案内される doctor command が repo-local shortcut 非依存で executable である
- expected tests:
  - lock contention/stale/release failure guidance
  - checked-in runtime doctor guidance parity
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01M` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01N — post-create recovery hint を runnable command に揃える
- target:
  - GitHub issue 作成後の local failure guidance が、kind ごとの required flags を含む runnable retry command を返す
- design refs:
  - `design.md` の create flow / post-create guidance 方針
- step boundary:
  - created issue number を含む recovery hint の生成に限定し、create transaction や lock scope は変えない

#### Red
- failing test:
  - initiative create の post-failure guidance が `--title` を欠く regression
  - epic / issue create の post-failure guidance が `--title` と parent selector を欠く regression
  - checked-in runtime parity でも同じ guidance が維持される regression

#### Green
- minimum implementation:
  - post-create failure message builder に original request context を渡し、`--title` と required parent flags を含む command を組み立てる
  - provider runtime と checked-in runtime parity を揃える

#### step gate
- review:
  - initiative / epic / issue の post-create recovery hint が runnable で、required flags を欠かない
- expected tests:
  - initiative/epic/issue の post-create failure guidance
  - checked-in runtime post-create guidance parity
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01N` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01O — create guidance path を cwd-independent に揃える
- target:
  - create lock failure guidance と post-create retry hint が、repo root でない cwd からでも実行できる command path を返す
- design refs:
  - `design.md` の create lock / post-create guidance 方針
- step boundary:
  - guidance surface の command path 解決に限定し、create semantics 自体は変えない

#### Red
- failing test:
  - nested cwd から見た post-create retry hint が `spec-dock/scripts/spec-dock` の repo-root-relative path のままで失敗する regression
  - nested cwd から見た doctor guidance も同様に cwd-dependent で失敗する regression
  - checked-in parity でも同 guidance が維持される regression

#### Green
- minimum implementation:
  - managed repo root から runtime entrypoint の absolute executable path を組み立て、doctor guidance と retry hint の両方へ使う
  - provider runtime と checked-in runtime parity を揃える

#### step gate
- review:
  - guidance surface が repo-local shortcut / repo-root-relative cwd 前提に依存せず、nested cwd からでも実行可能である
- expected tests:
  - nested cwd post-create retry guidance
  - nested cwd doctor guidance
  - checked-in runtime parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01O` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01P — create/post-create failure contract を outcome matrix で閉じる
- target:
  - `gh issue create` 後の create failure surface を outcome class で再編し、cleanup failure でも safe guidance と evidence を失わないようにする
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/046`
  - `discussions/047`
  - `discussions/048`
- step boundary:
  - create transaction や lock scope は変えず、failure classification / guidance assembly / parity test の中央集約に集中する
  - local write committed と remote-only の区別を guidance contract と test exit criteria に昇格させる

#### Red
- failing test:
  - `pre_github_fail` が no-side-effect guidance として表面化し、created issue number を持ち込まない regression
  - `gh create + lock acquire failure` または同等の `post_github_remote_only_fail` で created issue number と rerun/link guidance が返る regression
  - `gh create + body failure` により `post_github_local_write_fail` が created issue number を保持したまま guidance を返す regression
  - `gh create + local write success + release failure` で raw `release_error` ではなく created issue number と doctor-first guidance が返る regression
  - `gh create + body failure + release failure` で primary failure と cleanup failure を併記しつつ context を失わない regression
  - checked-in runtime parity でも上記 outcome class が provider と同じ guidance contract を返す regression

#### Green
- minimum implementation:
  - create flow の post-GitHub evidence を outcome builder へ集約する
  - `remote-only failure` と `local-write-committed cleanup failure` を別 guidance surface に分離する
  - provider runtime と checked-in runtime parity を揃える

#### Refactor
- cleanup target:
  - ad-hoc な post-create wrapper / release-error 分岐を outcome-specific helper へ寄せる
  - message builder と evidence collection の責務を分離する

#### step gate
- review:
  - outcome matrix の class / guidance / evidence surface が `design.md` の契約どおり説明できる
  - blind rerun guidance が local-write-committed cleanup failure へ誤適用されていない
  - `post_github_local_write_fail` の committed-local 枝でも doctor-first guidance へ切り替わる
- expected tests:
  - pre-github-fail guidance regression
  - remote-only guidance regression
  - local-write-fail guidance regression
  - committed-local local-write-fail guidance regression
  - cleanup-failure guidance regression
  - body+cleanup combined failure regression
  - checked-in runtime full-matrix parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01P` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01L — create-mode 全 kind に pre-GitHub graph preflight を揃える
- target:
  - `new initiative|epic|issue` の create mode で、stable tree validation failure を GitHub issue 作成前に no-side-effect fail にする
- design refs:
  - `design.md` の `1. create transaction`
  - `discussions/039`
- step boundary:
  - pre-lock では read-only graph preflight のみ追加し、authoritative な parent/uniqueness revalidation は lock 内に残す
  - repo 全体 validate を create の必須前提へ広げるのではなく、まず `load_graph(...)` ベースで防げる orphan issue を減らす

#### Red
- failing test:
  - broken existing tree で `new initiative --create-github-issue` が `issue_create()` 未呼び出しのまま fail する regression
  - broken existing tree で `new epic` / `new issue` も pre-GH graph preflight で no-side-effect fail する regression
  - checked-in dogfooding runtime でも同じ no-side-effect regression

#### Green
- minimum implementation:
  - create-mode 全 kind で `gh issue create` 前に read-only graph preflight を実行する
  - `epic` / `issue` は preflight graph を使って stable parent existence も確認する
  - lock 取得後は既存どおり graph reload と authoritative parent/uniqueness revalidation を維持する

#### Refactor
- cleanup target:
  - pure input validation / graph preflight / in-lock authoritative validation の helper 境界を整理する

#### step gate
- review:
  - tree preflight 追加で orphan issue を減らしつつ、S01I/S01J の create-lock 契約を壊していないことを説明できる
- expected tests:
  - provider runtime の broken-tree no-GH-call regression
  - provider runtime の parent-not-found regression が引き続き通ること
  - checked-in runtime parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01L` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01Q — create intermediate state を partial write まで区別する
- target:
  - `new` と create-like `import` の両方で、`execute_create_plan()` の partial local write を phase として分類し、remote-only failure と誤分類しない
  - post-create guidance を phase-aware にして blind rerun を unsafe 枝へ出さない
- design refs:
  - `design.md` の `1.1 create intermediate state model`
  - `discussions/051`
- step boundary:
  - create transaction 境界や repo lock 自体は変えず、phase evidence / guidance / parity test の是正に集中する
  - `new` だけでなく create-like `import` の write path も同じ phase model で閉じる

#### Red
- failing test:
  - `new` の `copy scaffold success + write_meta failure` が rerun-safe guidance を返してしまう regression
  - `new` の `copy scaffold` 途中 failure でも partial local write を remote-only と誤分類する regression
  - create-like `import` でも partial local write が remote-only guidance へ誤分類される regression
  - checked-in parity でも同じ guidance drift が起きる regression

#### Green
- minimum implementation:
  - create phase evidence を `none/scaffold_copied/meta_written/post_write_verified` 相当へ拡張する
  - phase に応じて doctor-first / partial-cleanup guidance を返す
  - `new` と create-like `import` の両方で phase model を共有する
  - provider runtime と checked-in runtime parity を揃える

#### Refactor
- cleanup target:
  - create / import の write-phase evidence 収集 helper を整理する

#### step gate
- review:
  - partial local write が remote-only failure と明確に分離されている
- expected tests:
  - `new` の scaffold-copied meta-write-failure regression
  - `new` の partial-copy failure regression
  - create-like `import` partial-write guidance regression
  - checked-in parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01Q` の review と expected tests が通り、`report.md` 更新後にコミットする

### S02 — discussion seq を同じ transaction に統合し validator でも守る
- target:
  - `new doc` の seq 採番を S01 と同じ safety model に乗せる
  - duplicate seq を validator failure として検知する
- design refs:
  - `design.md` の `1. create transaction`
  - `design.md` の `3. artifact/repair contract`
  - `discussions/008`
- step boundary:
  - doctor guidance までは広げず、discussion create と validate safety net に限定する
  - `S01` / `S01L` と合わせて `AC-001 create atomicity` を完了させる step として扱う

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S02` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — discussion allocator と validate safety net
- purpose:
  - discussion sequence uniqueness を create transaction に統合し、壊れた既存状態は validate で fail させる
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/...`
  - `tests/cli_runtime/...`
  - `tests/domain_runtime/...`

##### I1 — parallel new doc regression
- slice goal:
  - 並列 `new doc` で seq が重複しないことを先に test で固定する

###### Red
- failing test:
  - 同一 issue 配下で discussion seq が重複する regression test
- expected failure:
  - duplicate seq が成立する

###### Green
- minimum implementation:
  - discussion seq 採番を create transaction 配下に移す
- pass condition:
  - parallel `new doc` regression test が通る

###### Refactor
- cleanup target:
  - node id allocator と discussion seq allocator の共有ロジック整理
- invariants to keep green:
  - `new doc` の既存 naming/format を壊さない

##### I2 — duplicate seq validation
- slice goal:
  - 既に壊れた discussion seq 重複を validate で fail にする

###### Red
- failing test:
  - duplicate seq を含む tree に対する validate failure test
- expected failure:
  - 現状は validate が通ってしまう

###### Green
- minimum implementation:
  - discussion seq uniqueness check を validator contract に追加する
- pass condition:
  - duplicate seq validation test が通る

###### Refactor
- cleanup target:
  - artifact/uniqueness rule の domain 表現を整理する
- invariants to keep green:
  - 正常系 validate の既存出力互換を必要以上に壊さない

#### step gate
- review:
  - discussion race の preventive control と detective control の役割分担が明確
- expected tests:
  - parallel `new doc` test
  - duplicate seq validate test
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S02` の review と expected tests が通り、`report.md` 更新後にコミットする

### S01H — import を create transaction 契約へ統合する
- target:
  - `import issue` を `new issue` と同じ repo-level create transaction 契約へ揃える
  - import/import、import/new が競合しても duplicate id / duplicate GitHub linkage を残さない
- design refs:
  - `requirement.md` の `AC-001 create atomicity`
  - `design.md` の `1. create transaction`
- step boundary:
  - URL safety や foreign/current repo identity の仕様自体は `S05` 系で固定済みとし、ここでは create-like write path の atomicity だけを閉じる
  - discussion seq は引き続き `S02` の責務であり、`import issue` は新しい seq allocator 義務を持ち込まない
  - lock の外に残すのは URL/repo identity 解析、artifact preflight、GitHub metadata fetch とし、graph 読み取り以降の uniqueness 再検証 / plan / write / post-write duplicate guard は lock 内で行う

#### B1 — provider-side import transaction closure
- purpose:
  - provider-side `import issue` を create lock + post-write duplicate guard 配下へ入れ、stale graph 競合を防ぐ
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
  - `tests/cli_runtime/...`

##### I1 — import/import race
- slice goal:
  - 並列 `import issue` が duplicate id / duplicate GitHub linkage を作らない

###### Red
- failing test:
  - 同一 issue を別 slug で並列 import すると、両方が stale graph を通って duplicate id/linkage を残す regression test
- expected failure:
  - import path が repo-level create transaction 外で動き、pre-write uniqueness check が競合を防げない

###### Green
- minimum implementation:
  - provider-side `import_node.py` で create lock acquire/release と post-write duplicate guard を `new issue` と同じ契約で適用する
- pass condition:
  - import/import race regression test が通る

##### I2 — import/new race
- slice goal:
  - `import issue` と `new issue --github-issue` が同じ GitHub target で競合しても duplicate を残さない

###### Red
- failing test:
  - import/new の並列 create-like 競合で duplicate id/linkage が残る regression test
- expected failure:
  - create transaction が `new` 系だけに閉じていて import が atomicity 契約から漏れる

###### Green
- minimum implementation:
  - provider-side import path を `new` 系と同じ critical section に入れる
- pass condition:
  - import/new race regression test が通る

#### B2 — checked-in runtime parity
- purpose:
  - checked-in dogfooding runtime でも import path の create transaction 契約を provider-side と一致させる
- files:
  - `spec-dock/scripts/spec_dock_runtime/application/import_node.py`
  - `tests/test_init_update.py`

##### I1 — checked-in import/import race parity
- slice goal:
  - checked-in runtime の import/import race でも create lock / duplicate guard が効く

###### Red
- failing test:
  - checked-in runtime で import/import race が duplicate node/linkage を残す subprocess regression test
- expected failure:
  - checked-in runtime だけが import transaction 契約から漏れる

###### Green
- minimum implementation:
  - checked-in `import_node.py` を provider-side と同じ create transaction 契約へ refresh する
- pass condition:
  - checked-in runtime の import/import race subprocess parity regression test が通る

##### I2 — checked-in import/new race parity
- slice goal:
  - checked-in runtime の import/new race でも provider-side と同じ atomicity 契約が効く

###### Red
- failing test:
  - checked-in runtime で `import issue` と `new issue --github-issue` の race が duplicate node/linkage を残す subprocess regression test
- expected failure:
  - checked-in runtime parity が generic import path だけを見ており、cross-command create-like contention を未固定

###### Green
- minimum implementation:
  - checked-in subprocess parity test で import/new contention も固定する
- pass condition:
  - checked-in runtime の import/new race subprocess parity regression test が通る

#### step gate
- review:
  - import path が `new issue` と同じ lock scope / failure surface を使い、post-write duplicate guard は created-id materialization boundary として整合している
- expected tests:
  - provider-side import/import race regression
  - provider-side import/new race regression
  - checked-in runtime import/import race parity regression
  - checked-in runtime import/new race parity regression
  - 既存 import success/non-race 回帰
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01H` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03 — status/readiness contract を統一し stale projection を明示する
- target:
  - local-only issue の初期 status を deterministic にし、`deps check` と `active set` を同一 readiness contract に揃える
  - linked issue の cache read に `source/stale` を露出する
- design refs:
  - `design.md` の `2. status/readiness contract`
  - `discussions/006`, `009`, `015`
- step boundary:
  - import/CLI explicit flags は `S05` に分離し、ここでは status resolution 契約だけを扱う

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S03` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — domain/application/presentation の status resolution
- purpose:
  - `authority / effective_status / source / stale / last_sync_at` を持つ共通解決モデルを導入し、CLI/json の両方へ露出する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/...`
  - `tests/domain_runtime/...`
  - `tests/cli_runtime/...`
  - `tests/presentation_runtime/...`

##### I1 — local-only readiness regression
- slice goal:
  - local-only issue で `blockers=[]` かつ `effective_status=open` なら ready になることを固定する

###### Red
- failing test:
  - local-only issue の `deps check` / `active set` 不整合 regression test
- expected failure:
  - `ready=false` または `state=unknown` に落ちる

###### Green
- minimum implementation:
  - local-only 初期 authority/effective/source を決め、共通 readiness rule を参照させる
- pass condition:
  - `deps check` と `active set` の回帰テストが両方通る

###### Refactor
- cleanup target:
  - readiness 判定の共通化と status field naming の整理
- invariants to keep green:
  - linked issue の既存正常系を壊さない

##### I2 — stale projection visibility
- slice goal:
  - linked issue を `--github` なしで読むと `source=cache` と stale 情報が見えることを固定する

###### Red
- failing test:
  - cache read が freshness を露出しない regression test
- expected failure:
  - source/stale 情報が出力されない

###### Green
- minimum implementation:
  - presentation/json/text に source/stale/last_sync_at を追加する
- pass condition:
  - linked issue cache read regression test が通る

###### Refactor
- cleanup target:
  - status render と internal model の境界整理
- invariants to keep green:
  - `--github` 指定時の authoritative read が維持される

#### step gate
- review:
  - local-only と GitHub-linked の status authority が誤解なく説明できる
- expected tests:
  - deps/active readiness regression
  - stale/source/last_sync_at の text/json presentation regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03J — current repo の unscoped linked epic/initiative に issue-view fallback を揃える
- target:
  - `issue_index()` が current repo linked epic / initiative / issue を取りこぼした場合でも、repo-aware fallback fetch で `unknown/stale` 退行を防ぐ
- design refs:
  - `design.md` の `2.1 current repo slug parity for github-aware commands`
  - `design.md` の `2.4 current-repo fallback fetch for unscoped initiative/epic links`
- step boundary:
  - same-repo indexed dedup 契約は維持し、current repo slug を helper と call site へ渡す補強だけを扱う

#### Red
- failing test:
  - unscoped current-repo linked epic が index 未掲載時に fallback fetch されず `unknown/stale` のままになる regression
  - unscoped current-repo linked initiative も同様に stale のままになる regression
  - checked-in parity path に同 helper がある場合、同じ取りこぼしが再発する regression

#### Green
- minimum implementation:
  - `collect_repo_scoped_issue_view_targets()` に `current_repo_slug` を通し、unscoped linked node を `(current_repo_slug, issue_number)` として fallback target 化する
  - `sync_state` / `set_active` / `check_deps` の call site を同 helper 契約へ揃える
  - checked-in parity path に同 helper / call site があれば追随させる

#### Refactor
- cleanup target:
  - current-repo vs foreign-repo target 判定 helper の責務を整理する
- invariants to keep green:
  - index 済み same-repo target への extra `issue_view_snapshot()` は復活させない
  - foreign scoped fetch は引き続き維持する

#### step gate
- review:
  - current repo linked issue / epic / initiative が index incomplete 時でも repo-aware fallback で status を回復できる
- expected tests:
  - sync current-repo unscoped epic/initiative fallback regression
  - active/deps current-repo fallback parity regression
  - checked-in parity regression（該当 path がある場合）
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03J` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03K — repo overlap 後も numeric branch inference を current-repo-aware に保つ
- target:
  - foreign same-number coexistence 後も numeric branch 名から current repo issue を安定に推論し、branch auto-update を止めない
- design refs:
  - `design.md` の `2.5 current-repo-aware numeric branch inference`
- step boundary:
  - explicit id match 優先は変えず、numeric fallback と `sync_state` からの current repo slug 伝播だけを扱う
  - current repo slug が既知のとき、foreign-only numeric match や current-scope multiple match は fail-closed に固定する

#### Red
- failing test:
  - current repo `#123` と foreign `other/repo#123` が共存すると `123-fix-login` が ambiguity に落ちる regression
  - current repo slug 不明時の ambiguity fail-closed が失われる regression
  - current repo slug が既知でも foreign-only numeric match を暗黙採用してしまう regression
  - current repo scope に複数 numeric match があるのに scoped ambiguity fail-closed にならない regression
  - checked-in parity path に同 inference がある場合、同じ ambiguity が再発する regression

#### Green
- minimum implementation:
  - `infer_active_node_from_branch()` の numeric fallback を repo-aware candidate selection に更新する
  - `maybe_auto_update_from_branch()` から current repo slug を渡す
  - checked-in parity path に同 inference があれば追随させる

#### Refactor
- cleanup target:
  - numeric branch candidate selection と reason message の責務を整理する
- invariants to keep green:
  - explicit node id を含む branch の優先順位は維持する
  - current repo slug 不明時は ambiguity/no-match の fail-closed を維持する

#### step gate
- review:
  - numeric branch auto-update が current repo overlap では継続し、repo context 不明時だけ fail-closed になる
- expected tests:
  - branch overlap current-repo preferred regression
  - branch overlap slug-unknown ambiguity regression
  - branch foreign-only known-scope fail-closed regression
  - branch scoped-ambiguity fail-closed regression
  - checked-in parity regression（該当 path がある場合）
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03K` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03L — current-repo linkage を正規化し no-origin continuity を維持する
- target:
  - current repo slug を解決できる write/mutate path で current-repo linked node の repo scope を explicit metadata へ正規化する
  - no-origin copy 後も `sync --github` / `validate` / `doctor` / deps resolution が safe backfill 済み current-repo linkage だけを理由に fail-closed しないようにする
- design refs:
  - `design.md` の `2.6 no-origin continuity via current-repo linkage normalization`
  - `discussions/056`
- step boundary:
  - convenience selector の新仕様追加は扱わず、`--github-issue <n>` / bare numeric の overlap fail-closed は維持する
  - no-origin での新しい heuristic 推測は追加せず、current repo slug が既知の時点で正規化できる metadata だけを対象にする
  - partial scope や same effective key duplicate のような truly ambiguous graph は read/write とも fail-closed に残す
  - provider-side source of truth の修正後、checked-in dogfooding runtime にも parity を反映する

#### B1 — write-time normalization と no-origin continuity baseline
- purpose:
  - current repo issue を新規に保存する path で explicit scope persistence を固定し、already-normalized metadata の no-origin continuity baseline を作る
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/...`
  - `tests/cli_runtime/...`
  - `tests/domain_runtime/...`
  - `tests/test_init_update.py`

##### I1 — fail-closed 境界と explicit persistence baseline を failing regression で固定する
- slice goal:
  - explicit scope persistence 対象と fail-closed 残置対象の境界を regression で固定する

###### Red
- failing test:
  - current repo slug 既知の write path が explicit current-repo scope persistence を行わない regression
  - partial scope / same effective key duplicate / slug unknown は fail-closed を維持する regression
- expected failure:
  - 現状は write path が unscoped metadata を残し、後続 continuity の土台が作れない

###### Green
- minimum implementation:
  - current repo slug 既知の create/import/link write path で explicit `repo_owner/name` persistence を導入する
  - ambiguity を増やす graph では write path 自体が fail-closed を維持する
- pass condition:
  - explicit persistence baseline / ineligible predicate の回帰テストが通る

###### Refactor
- cleanup target:
  - normalization helper と repo-aware key 判定の責務整理
- invariants to keep green:
  - fail-closed policy と existing scoped exact resolution contract を壊さない

##### I2 — no-origin continuity と write-time persistence を閉じる
- slice goal:
  - newly created/imported current-repo linkage が最初から explicit scope を持ち、already-normalized metadata は no-origin continuity を保てるようにする

###### Red
- failing test:
  - current repo slug 既知の create/import path が explicit current-repo scope を persisted metadata へ保存する regression
  - normalized metadata の no-origin copy で `sync --github` / `validate` / `doctor` / `deps check` が mixed scoped/unscoped legacy だけを理由に fail-closed しない regression
  - overlap 下でも canonical GitHub URL target と `--id` selector が no-origin 継続で exact resolution を維持する regression
  - normalized metadata が存在しても `--github-issue <n>` / bare numeric overlap fail-closed が維持される regression
  - checked-in dogfooding runtime が同じ continuity contract を維持する parity regression
- expected failure:
  - 新規 write path が unscoped metadata を残し、normalized metadata continuity が provider/checked-in のどちらかで壊れる

###### Green
- minimum implementation:
  - current-repo create/import/link write path で explicit scope persistence を導入する
  - already-normalized metadata が no-origin でも read-side continuity を保てるようにする
  - provider-side / checked-in runtime の parity を揃える
- pass condition:
  - no-origin continuity regression と checked-in parity regression が通る

###### Refactor
- cleanup target:
  - write-time normalization と read-side continuity の責務整理
- invariants to keep green:
  - command target UX、doctor classification、repo-aware validation boundary の既存契約を壊さない

#### step gate
- review:
  - write-time normalization、no-origin read-side continuity、selector continuity の責務分離を説明できる
- expected tests:
  - partial scope / duplicate effective key / slug-unknown fail-closed regression
  - create/import explicit scope persistence regression
  - no-origin `sync --github` / `validate` / `doctor` / `deps check` continuity regression
  - no-origin canonical URL target / `--id` exact resolution continuity regression
  - overlap 下の `--github-issue <n>` / bare numeric fail-closed 維持 regression
  - checked-in dogfooding runtime parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03L` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03M — readonly `.meta.json` backfill を cross-platform contract へ補正する
- target:
  - `write_meta()` と `backfill_github_repo_scope()` が同じ `.meta.json` permission contract を共有し、Windows でも readonly file を safe backfill できるようにする
- design refs:
  - `design.md` の `2.6 no-origin continuity via current-repo linkage normalization`
  - `discussions/057`
- step boundary:
  - safe backfill predicate や selector continuity 自体は `S03L` のままとし、ここでは permission/lock state drift の補正に集中する
  - generic filesystem abstraction へ広げず、`.meta.json` mutation 専用 helper に限定する
  - conflicting scope / partial scope / ambiguous candidate の fail-closed policy は変えない
  - provider-side source of truth の修正後、checked-in dogfooding runtime に parity を反映する

#### Red
- failing test:
  - readonly `.meta.json` を持つ safe current-repo backfill case が Windows 相当契約で `sync --github` failure になる regression
  - readonly `.meta.json` backfill 成功後に final lock state が復元されない regression
  - checked-in dogfooding runtime で同じ readonly backfill failure が再発する parity regression
- expected failure:
  - 現状は writable 化と restore が `posix` 限定で、Windows readonly file を supported self-healing path で更新できない

#### Green
- minimum implementation:
  - `.meta.json` mutation 専用 helper を導入し、現在の lock state 取得、一時 writable 化、write、restore を shared contract として実装する
  - `write_meta()` と `backfill_github_repo_scope()` の両方から同 helper を使う
  - successful create/backfill 後の final `.meta.json` lock state は readonly に揃える
  - provider-side / checked-in runtime の parity を揃える
- pass condition:
  - Windows 相当 readonly backfill regression と final lock state regression、checked-in parity regression が通る

#### Refactor
- cleanup target:
  - permission helper の責務整理と warning surface の整合
- invariants to keep green:
  - `readonly_lock_failed` warning contract を壊さない
  - fail-closed predicate と no-origin continuity contract を壊さない

#### step gate
- review:
  - readonly metadata lock policy と mutate-time permission control が `write_meta()` / `backfill_github_repo_scope()` で共有され、Windows 差分だけで self-healing が止まらないことを説明できる
- expected tests:
  - Windows 相当 readonly `.meta.json` backfill success regression
  - readonly backfill 後の final lock state regression
  - relock/restore failure が `readonly_lock_failed` warning surface へ載る regression
  - partial scope / conflicting scope fail-closed non-regression
  - checked-in dogfooding runtime readonly backfill parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03M` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03N — lone unscoped legacy linkage を positive evidence なしに backfill しない
- target:
  - `collect_safe_current_repo_backfill_node_ids()` は lone unscoped legacy linkage を current repo slug と uniqueness だけで current repo candidate 扱いせず、positive current-repo evidence がある場合だけ backfill を許可する
- design refs:
  - `design.md` の `2.6 no-origin continuity via current-repo linkage normalization`
  - `discussions/058`
- step boundary:
  - write-time create/import/link の explicit current repo persistence は維持する
  - bulk `sync --github` の lone unscoped legacy linkage を safe から外す corrective scope に集中し、manual remediation command の新設までは扱わない
  - permission helper / readonly contract は `S03M` に留め、ここでは evidence model と backfill predicate を補正する
  - provider-side source of truth の修正後、checked-in dogfooding runtime に parity を反映する

#### Red
- failing test:
  - lone unscoped legacy linkage が bulk `sync --github` で current repo scope へ silent backfill される regression
  - same-number foreign scoped coexistence があるだけで lone unscoped node を current repo scope へ backfill してしまう regression
  - checked-in dogfooding runtime で同じ silent backfill が再発する parity regression
- expected failure:
  - 現状は uniqueness-only predicate により lone unscoped legacy linkage を safe と誤判定し、current repo へ silent mutation する

#### Green
- minimum implementation:
  - safe backfill predicate を positive current-repo evidence ベースに狭め、bulk `sync --github` の lone unscoped legacy linkage を no-op + fail-closed にする
  - write-time create/import/link の explicit scope persistence と、already-normalized metadata の continuity は維持する
  - provider-side / checked-in runtime の parity を揃える
- pass condition:
  - lone unscoped no-backfill regression、foreign coexistence no-backfill regression、checked-in parity regression が通る

#### Refactor
- cleanup target:
  - current-repo evidence 判定 helper と reason surface の責務整理
- invariants to keep green:
  - `S03M` の permission contract を壊さない
  - exact selector continuity と fail-closed ambiguity contract を壊さない

#### step gate
- review:
  - `safe backfill` が positive evidence を要求し、bulk `sync --github` の lone unscoped legacy linkage を silent mutation しないことを説明できる
- expected tests:
  - lone unscoped legacy linkage no-backfill regression
  - same-number foreign scoped coexistence only では backfill しない regression
  - write-time current-repo explicit scope persistence non-regression
  - already-normalized metadata no-origin continuity non-regression
  - checked-in dogfooding runtime lone-unscoped no-backfill parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03N` の review と expected tests が通り、`report.md` 更新後にコミットする

### S03O — bulk sync の dead sync-time backfill contract を撤去する
- target:
  - `collect_sync_state()` は trusted current-repo evidence を持たない bulk `sync --github` で legacy unscoped linkage を mutate しない
  - `AC-021` / `S03L` の no-origin continuity 契約を write-time normalization 済み metadata 中心へ補正する
- design refs:
  - `design.md` の `2.6 no-origin continuity via current-repo linkage normalization`
  - `discussions/059`
- step boundary:
  - write-time create/import/link の explicit current repo persistence は維持する
  - lone unscoped no-backfill contract は `S03N` を継承する
  - new provenance schema や manual remediation command の新設までは扱わない
  - provider-side source of truth の修正後、checked-in dogfooding runtime に parity を反映する

#### Red
- failing test:
  - bulk `sync --github` に dead bulk backfill call path が残り、trusted candidate なしの helper を呼んでしまう regression
  - current repo `issue_index()` の存在だけで legacy unscoped node を backfill してしまう regression
  - checked-in dogfooding runtime で同じ dead path が再発する parity regression
- expected failure:
  - 現状は docs が trusted mutate-time backfill を謳う一方で、bulk sync は trusted candidate を供給していない

#### Green
- minimum implementation:
  - provider/check-in runtime から dead bulk sync backfill call path を除去し、bulk sync は legacy unscoped linkage を mutate しない
  - already-normalized metadata の no-origin continuity と write-time current-repo explicit scope persistence は維持する
  - issue docs と runtime 実装の契約を一致させる
- pass condition:
  - dead path removal regression、current repo `issue_index()` 非trust regression、already-normalized continuity non-regression、checked-in parity regression が通る

#### Refactor
- cleanup target:
  - dead helper call site の除去と関連 explanation/test naming の整理
- invariants to keep green:
  - `S03N` の fail-closed predicate を壊さない
  - `S03M` の permission helper 契約と write-time current repo persistence を壊さない

#### step gate
- review:
  - bulk sync が trusted evidence を持たず、write-time normalization 済み metadata continuity を正契約とする理由を説明できる
- expected tests:
  - bulk `sync --github` dead backfill path removal regression
  - current repo `issue_index()` only では legacy unscoped node を backfill しない regression
  - write-time current-repo explicit scope persistence non-regression
  - already-normalized metadata no-origin continuity non-regression
  - normalized metadata を使った no-origin `deps check` continuity non-regression
  - normalized metadata を使った canonical GitHub URL / `--id` exact selector continuity non-regression
  - checked-in dogfooding runtime dead-path removal parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S03O` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04 — artifact/repair/active fallback contract を整える
- target:
  - required artifact matrix を validate に入れる
  - doctor を supported repair path として追加する
  - active 未設定でも path と CLI の両方に fallback 導線を持たせる
- design refs:
  - `design.md` の `3. artifact/repair contract`
  - `discussions/010`, `011`, `012`
- step boundary:
  - GitHub target ambiguity や create flags は `S05` に分離する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S04` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — validate と artifact matrix
- purpose:
  - node kind ごとの required artifact contract を runtime preflight として扱い、validate/sync の safety net を強化する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `tests/domain_runtime/...`
  - `tests/cli_runtime/...`

##### I1 — required artifact validation
- slice goal:
  - initiative/epic/issue の required artifact 欠損と discussion markdown/integrity contract の破損が validate failure になることを固定する

###### Red
- failing test:
  - `requirement.md` や `.meta.json` 欠損を見逃す回帰テスト
- expected failure:
  - validate が成功してしまう

###### Green
- minimum implementation:
  - required artifact matrix と preflight integration を追加する
- pass condition:
  - `initiative` / `epic` / `issue` の required artifact 欠損を検知する validation test が通る
  - discussion は markdown file 本体の不整合または seq uniqueness 破損を検知する validation test が通る

###### Refactor
- cleanup target:
  - artifact contract の共通化
- invariants to keep green:
  - discussion seq uniqueness と矛盾しない

#### B2 — doctor と active fallback
- purpose:
  - recoverability と onboarding 導線を supported path として整備する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/...`
  - `tests/cli_runtime/...`

##### I1 — doctor guidance
- slice goal:
  - duplicate id/seq、missing artifact、broken meta、stale active pointer を doctor が診断し guidance を返す
  - repo-aware uniqueness 導入後も、doctor の validation context が `validate` / `sync` と一致し、current/foreign 同番号の正常系を false positive にしない

###### Red
- failing test:
  - 壊れた状態で doctor が supported guidance を返さない regression test
- expected failure:
  - doctor command がない、または必要情報が出ない

###### Green
- minimum implementation:
  - doctor command/use case/presentation を追加する
- pass condition:
  - `duplicate id/seq`、`missing artifact`、`broken meta`、`stale active pointer`、`stale create lock` をそれぞれ診断する doctor guidance test が通る

###### Refactor
- cleanup target:
  - validate と doctor の責務分離
- invariants to keep green:
  - `.meta.json` read-only 方針を維持する

##### I2 — active-not-set fallback
- slice goal:
  - active 未設定でも `spec-dock/active` と `active show` から次アクションが分かることを固定する
  - persisted active manifest が残っている recovery では、placeholder ではなく active entrypoint 自体を復元する

###### Red
- failing test:
  - active 未設定時に path/CLI fallback がない regression test
- expected failure:
  - `(not set)` のみ、または path が存在しない

###### Green
- minimum implementation:
  - `spec-dock/active -> system/active-none` の一貫した入口と fallback guidance を追加する
  - persisted active manifest が健全な場合は `spec-dock/active/{initiative,epic,issue}` を対応 node へ再構築し、壊れている場合だけ placeholder fallback に落とす
- pass condition:
  - `spec-dock/active` の path 入口と `active show` の CLI 入口の両方で fallback guidance が機能する test が通る
  - active dir 欠損 recovery 後に `context-pack.md` と active entrypoint が同じ persisted active state を指す test が通る

###### Refactor
- cleanup target:
  - active pointer 管理と presentation の整理
- invariants to keep green:
  - active が設定済みの通常フローを壊さない

#### step gate
- review:
  - validate と doctor の契約境界、active fallback の UX 意図が説明できる
- expected tests:
  - `initiative` / `epic` / `issue` の required artifact validation
  - discussion markdown/integrity validation
  - `duplicate id/seq` / `missing artifact` / `broken meta` / `stale active pointer` / `stale create lock` の doctor guidance
  - current repo `#123` と foreign repo `#123` を併存した正常 graph に対して doctor が ambiguity false positive を出さない
  - `spec-dock/active` path 入口と `active show` CLI 入口の active fallback
  - persisted active manifest からの active entrypoint rebuild
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05 — GitHub targeting と CLI intent surface を安全化する
- target:
  - URL import の repo identity mismatch を safe default で防ぐ
  - `new issue` に explicit GitHub create flag を追加する
  - `active set` と numeric target を受ける関連コマンドに explicit target flags を追加する
- design refs:
  - `design.md` の `4. GitHub targeting and CLI intent surface`
  - `discussions/013`, `014`, `016`
- step boundary:
  - status freshness の内部契約は `S03`、docs/help 反映は `S90` に分ける
  - S05 は target parsing / create intent / repo identity validation だけを扱い、status freshness の意味づけ変更は扱わない
  - docs/help 文言、usage examples、dogfooding workspace 反映は `S90` で閉じる

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S05` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — wrong-repo safety と explicit flags
- purpose:
  - import/create/active の command contract を repo-aware / intent-aware にする
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/...`
  - `tests/cli_runtime/...`

##### I1 — repo-aware import
- slice goal:
  - GitHub URL の `owner/repo` mismatch を default failure にする

###### Red
- failing test:
  - foreign repo URL を current repo issue に誤リンクできてしまう regression test
- expected failure:
  - mismatch を見逃して成功してしまう

###### Green
- minimum implementation:
  - repo identity validation と foreign URL 用の explicit opt-in flag（例: `--allow-foreign-url`）を追加する
  - foreign repo import を許可した node には repo identity を persisted metadata として保持し、後続の sync/deps/status refresh が同じ foreign repo を参照するようにする
  - linked uniqueness を `repo + issue_number` で評価し、same-repo duplicate は防ぎつつ foreign 同番号は許可する
- pass condition:
  - foreign URL mismatch が default fail する regression test と、explicit opt-in でのみ成功する regression test が通る
  - foreign repo import 後の `sync --github` / `deps check --github` が current repo の同番号 issue に誤 hydrate しない regression test が通る
  - current repo `#123` と foreign repo `#123` を併存でき、same-repo duplicate だけが fail する regression test が通る

###### Refactor
- cleanup target:
  - target parser と repo identity resolver の責務分離
- invariants to keep green:
  - current repo URL / issue number の既存正常系を維持する

##### I2 — create/active explicit intent
- slice goal:
  - `new issue --create-github-issue` と `--id` / `--github-issue` を通じて意図を明示できるようにする
  - `--id` / `--github-issue` の対象コマンドを少なくとも `active set` と numeric target を受ける同系 command に固定する

###### Red
- failing test:
  - explicit flag が受理されない、または target intent が指定できない regression test
- expected failure:
  - parser error、または曖昧解釈のまま

###### Green
- minimum implementation:
  - additive flags と help/error guidance を追加する
- pass condition:
  - create/active explicit intent regression test が通る
  - overlapping foreign/current issue number が存在する時、`--github-issue <n>` は ambiguity error となり、`--id <node-id>` でのみ確定できる regression test が通る

###### Refactor
- cleanup target:
  - shared target parsing と help text の整形
- invariants to keep green:
  - bare number の後方互換は維持しつつ、explicit 形へ誘導する

#### step gate
- review:
  - safe default と additive backward compatibility の両立が説明できる
- expected tests:
  - foreign URL mismatch default fail
  - foreign URL explicit opt-in success
  - foreign repo identity persistence across sync/deps refresh
  - foreign overlap issue number allow / same-repo duplicate fail
  - explicit create flag
  - `active set --id`
  - `active set --github-issue`
  - ambiguous `--github-issue` fail with overlapping foreign/current issue numbers
  - numeric target を受ける同系 command の explicit target flags
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05F — current repo slug parity を github-aware command 全体へ揃える
- target:
  - `active set --github` と `deps check --github` が `sync --github` と同じ current repo slug-aware status resolution を使う
- design refs:
  - `design.md` の `2.1 current repo slug parity for github-aware commands`
  - `discussions/023`, `024`
- step boundary:
  - foreign repo uniqueness や explicit flags の仕様自体は `S05` で固定済みとし、ここでは command 間の context parity だけを補修する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S05F` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — active/deps status context parity
- purpose:
  - current repo linked issue が `active set --github` / `deps check --github` で `unknown/stale` に退行しないようにする
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `tests/cli_runtime/...`

##### I1 — current repo slug propagation
- slice goal:
  - `set_active` と `check_deps` が current repo slug を status resolution へ渡す

###### Red
- failing test:
  - current repo linked issue の `active set --github` / `deps check --github` が `unknown` になって誤 block / 誤 JSON となる regression test
- expected failure:
  - current repo snapshot を current issue に再結合できない

###### Green
- minimum implementation:
  - current repo slug 解決 helper を parity させ、status resolution 呼び出しへ渡す
- pass condition:
  - current repo linked issue の `active set --github` が readiness を正しく評価する regression test が通る
  - current repo linked issue の `deps check --github` が GitHub status を readiness / JSON に反映する regression test が通る

###### Refactor
- cleanup target:
  - current repo slug helper の重複整理
- invariants to keep green:
  - current repo slug 未解決時の fail-closed/unknown 契約は維持する

#### step gate
- review:
  - current repo slug-aware status resolution が `sync` / `active` / `deps` で揃っている
- expected tests:
  - `active set --github` current repo linked issue regression
  - `deps check --github` current repo linked issue regression
  - foreign same-number coexist の non-regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05F` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04F — domain/application validation boundary を再分離する
- target:
  - domain validation API を graph/deps/linkage の structural invariant に戻し、artifact matrix 検査は application preflight へ寄せる
- design refs:
  - `design.md` の `3. artifact/repair contract`
  - `discussions/025`
- step boundary:
  - artifact matrix 契約自体は維持し、責務の置き場だけを修正する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S04F` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — domain purity recovery
- purpose:
  - in-memory/synthetic graph の structural validation が on-disk artifact 欠損に先回りされないようにする
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/...`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `tests/domain_runtime/...`
  - `tests/cli_runtime/...`

##### I1 — move artifact existence checks to application preflight
- slice goal:
  - domain validation から filesystem 依存を外し、validate/sync/doctor の artifact 契約は application 側で維持する

###### Red
- failing test:
  - synthetic graph の structural error が `Missing required artifact` に先回りされる regression test
- expected failure:
  - domain validation API が graph ではなく filesystem 欠損に引きずられる

###### Green
- minimum implementation:
  - required artifact existence check を application preflight へ移し、domain validation から外す
- pass condition:
  - domain test が structural error を artifact 欠損なしで検証できる
  - `validate` / `sync` / `doctor` は引き続き missing artifact を検出する regression test が通る

###### Refactor
- cleanup target:
  - graph validation と artifact preflight の API 境界整理
- invariants to keep green:
  - human-facing missing artifact 診断と guidance は維持する

#### step gate
- review:
  - domain validation API が filesystem 非依存であること、artifact 契約が application 側で維持されていることを説明できる
- expected tests:
  - domain structural validation regression
  - validate/sync/doctor の missing artifact regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04F` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04G — stale active pathfile healing を self-healing contract に含める
- target:
  - symlink 制限環境の `spec-dock/active/*.path` stale fallback も `update` で repair できるようにする
- design refs:
  - `design.md` の `3.1 stale active pathfile healing`
  - `discussions/029`
- step boundary:
  - recovery surface は `cli.py` と installer/update regression に限定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S04G` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — stale pathfile repair
- purpose:
  - `.path` が stale でも persisted/recovered target または placeholder へ自動復旧する
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`

##### I1 — stale pathfile を除去して再生成する
- slice goal:
  - `existing_entrypoint is None` なのに `.path` があるだけで recovery が止まる分岐を閉じる

###### Red
- failing test:
  - symlink 制限下で stale `.path` が persisted active target に repair されない regression
  - symlink 制限下で persisted target も stale の時 placeholder に戻らない regression
- expected failure:
  - stale `.path` 存在だけで `update` が `continue` してしまう

###### Green
- minimum implementation:
  - stale `.path` を削除してから既存 resolved target 判定へ流す
- pass condition:
  - stale pathfile recovery regression が通る

###### Refactor
- cleanup target:
  - stale symlink と stale pathfile の recovery 分岐整理
- invariants to keep green:
  - 健全な entrypoint は触らない

#### step gate
- review:
  - symlink/pathfile 両 fallback の self-healing 契約が説明できる
- expected tests:
  - stale `.path` -> persisted target recovery
  - stale `.path` -> placeholder fallback
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04G` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04I — placeholder active entrypoint を persisted active recovery で上書きできるようにする
- target:
  - `spec-dock/active/{initiative,epic,issue}` が placeholder を向いていても、persisted active manifest から実 node を解決できるなら `update` が active entrypoint を実 node へ rebuild する
- design refs:
  - `design.md` の `active entrypoint recovery`
  - `discussions/040`
- step boundary:
  - healthy な real entrypoint は保持し、placeholder fallback と broken entrypoint の recovery だけを扱う
  - `context-pack.md` の再生成 source of truth は既存方針どおり最終 active entrypoint 実体とする

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S04I` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — placeholder fallback recovery
- purpose:
  - placeholder を healthy state と誤認して persisted active recovery を skip する分岐を閉じる
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`

##### I1 — placeholder を recoverable fallback として再構築する
- slice goal:
  - valid persisted manifest がある時、placeholder symlink / `.path` fallback から real active node へ rebuild する

###### Red
- failing test:
  - placeholder symlink が残っていると `update` が persisted active manifest を見ても rebuild しない regression
  - placeholder `.path` fallback が残っていると `update` が `(none)` context-pack へ退行する regression
  - mixed state で healthy real entrypoint は維持し、placeholder layer だけ rebuild される regression
- expected failure:
  - placeholder を healthy existing entrypoint と誤認して `continue` してしまう

###### Green
- minimum implementation:
  - placeholder entrypoint を recoverable fallback として識別し、persisted/recovered target が解決できる時だけ実 node へ張り替える
  - persisted target が壊れている場合は placeholder を維持し、`context-pack.md` も `(none)` 側を維持する
- pass condition:
  - placeholder recovery regression が通る

###### Refactor
- cleanup target:
  - healthy real entrypoint / placeholder fallback / broken entrypoint の優先順位整理
- invariants to keep green:
  - stale persisted manifest で healthy real entrypoint を上書きしない

#### step gate
- review:
  - `healthy real entrypoint > valid persisted target > placeholder fallback` の優先順位が説明できる
- expected tests:
  - placeholder symlink -> persisted target recovery
  - placeholder `.path` -> persisted target recovery
  - mixed state で placeholder layer のみ rebuild
  - broken persisted manifest では placeholder fallback を維持
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04I` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04J — create-in-progress scaffold を corruption と誤診断しない
- target:
  - create lock 下の missing `.meta.json` を in-progress/stale-create 系として分類し、恒久 corruption と区別する
- design refs:
  - `design.md` の `3.1 create-in-progress / partial-write diagnosis`
  - `discussions/052`
- step boundary:
  - required artifact contract 自体は維持し、reader-side classification と doctor guidance の是正に限定する

#### Red
- failing test:
  - create lock 下の node-like directory without `.meta.json` を `validate` / `doctor` / `sync` が即 corruption 扱いする regression
  - lock なし missing `.meta.json` が corruption でなくなる regression を防ぐ

#### Green
- minimum implementation:
  - reader が create lock と missing `.meta.json` を合わせて分類する
  - application 側が in-progress/stale-create と corruption を別 guidance へ写像する

#### Refactor
- cleanup target:
  - stale create lock / missing artifact / in-progress create の分類責務整理

#### step gate
- review:
  - in-progress create と恒久 corruption の境界が lock/state で説明できる
- expected tests:
  - create-lock-present missing-meta regression
  - lock-absent missing-meta remains-corruption regression
  - checked-in parity または executable smoke
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04J` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04K — persisted active path fallback は manifest id/type 一致なしに信用しない
- target:
  - persisted active manifest の `path` が same-layer の別 node を指していても、`update` が wrong node へ repoint しないようにする
- design refs:
  - `design.md` の `active entrypoint recovery`
  - `discussions/054`
- step boundary:
  - installer/update の active recovery (`src/spec_dock/cli.py`) と installer regression (`tests/test_init_update.py`) に限定する
  - healthy active entrypoint や id-based recovery、placeholder fallback の既存 contract は維持する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S04K` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — persisted path trust boundary
- purpose:
  - same-layer / correct-prefix だが wrong-id の stale path を fail-closed に倒す
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`

##### I1 — same-layer wrong-id path を recovery target にしない
- slice goal:
  - `_resolve_persisted_path_dir()` が prefix だけ合う別 node を誤採用する分岐を閉じる

###### Red
- failing test:
  - persisted active manifest の `issue.id=iss-local-99999` と `path=.../iss-local-00002-*` で、`update` が `iss-local-00002` へ repoint してしまう regression
  - same-layer wrong-id persisted path は id-based recovery が失敗した時 placeholder fallback へ落ちる regression
  - same-layer wrong-id persisted path でも、tree 内に `expected_id` の正しい node が別 path に存在する時は id-based recovery を優先してその node へ戻る regression
- expected failure:
  - `context-pack.md` と active entrypoint が persisted id ではなく wrong node id を指す

###### Green
- minimum implementation:
  - persisted path fallback でも `.meta.json` を読み、`expected_id` / `layer` 一致がある場合だけ recovery target として返す
  - 一致しない時は `None` を返し、既存 id-based recovery / placeholder fallback へ流す
- pass condition:
  - same-layer wrong-id persisted path regression が通る

###### Refactor
- cleanup target:
  - persisted path / manifest id recovery の責務境界整理
- invariants to keep green:
  - valid persisted path は従来どおり復旧できる
  - healthy active entrypoint を stale manifest で上書きしない

#### step gate
- review:
  - path hint と id authority の優先順位を説明できる
- expected tests:
  - same-layer wrong-id persisted path -> placeholder fallback
  - same-layer wrong-id persisted path + valid `expected_id` elsewhere -> id-based recovery
  - valid persisted path -> existing recovery contract 維持
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04K` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05G — repo-aware numeric deps resolution で foreign overlap 後も既存 shorthand を守る
- target:
  - foreign overlap 導入後も bare numeric deps ref が current repo issue shorthand として解決されるようにする
- design refs:
  - `design.md` の `2.2 repo-aware numeric deps resolution`
  - `discussions/028`
- step boundary:
  - numeric deps ref 自体は後方互換のため維持し、repo-aware 解決だけを追加する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S05G` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — numeric dep ref resolution parity
- purpose:
  - `depends_on: [123]` が overlap 後に `Ambiguous github.issue_number` へ退行しないようにする
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - 必要なら `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - `tests/cli_runtime/...`

##### I1 — current repo context で bare number を解決する
- slice goal:
  - bare numeric ref を current repo 文脈で解決し、current repo slug 不明時だけ fail-closed にする

###### Red
- failing test:
  - existing `depends_on: [123]` が foreign overlap 導入後に `Ambiguous github.issue_number=123` へ退行する regression
- expected failure:
  - bare numeric deps ref が bare issue number key のまま曖昧化する

###### Green
- minimum implementation:
  - `deps_reader` の numeric ref 解決を repo-aware にし、必要なら legacy app path も parity させる
- pass condition:
  - overlap 導入後も existing numeric deps ref が current repo issue を解決する regression test が通る

###### Refactor
- cleanup target:
  - bare ref / scoped ref / fail-closed 条件の整理
- invariants to keep green:
  - current repo slug 不明時の fail-closed 契約は維持する

#### step gate
- review:
  - numeric deps shorthand と foreign overlap の後方互換契約が説明できる
- expected tests:
  - current repo numeric deps shorthand survives foreign overlap
  - current repo slug unknown mixed-scope fail-closed
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05G` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05H — same-repo URL-linked issue の indexed fetch dedup を github-aware read path に揃える
- target:
  - current repo issue を canonical URL で link/import した場合でも、index 済み target へ重複 `issue_view_snapshot()` を送らない
  - index incomplete 時の same-repo fallback fetch は維持し、foreign target fetch は引き続き許可する
- design refs:
  - `design.md` の `2.3 indexed target dedup for same-repo URL-linked GitHub reads`
  - `discussions/030-disc-pr29-r14-same-repo-url-linked-fetch-dedup-analysis.md`
- step boundary:
  - current repo/fallback dedup helper と、その helper を利用する github-aware read path に限定する
  - snapshot binding / status contract 自体は `S05F` / `S05G` の契約を再利用し、今回 step では fetch selection の無駄取りに集中する
  - checked-in dogfooding runtime に同じ helper/read path がある場合は、この step 内で parity を取る

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S05H` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — indexed snapshot key による same-repo dedup helper
- purpose:
  - same-repo indexed target は view fetch を省略し、index missing target だけ fallback fetch する
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/...`
  - `tests/presentation_runtime/...`
  - `tests/cli_runtime/...`

##### I1 — sync same-repo indexed dedup regression
- slice goal:
  - same-repo URL-linked issue が index 済みのとき `sync --github` が追加 view fetch を行わないことを固定する

###### Red
- failing test:
  - current repo issue を URL-linked で保存し、index に same `(repo_slug, issue_number)` snapshot がある状態で `collect_sync_state()` を呼ぶと `issue_view_snapshot()` が呼ばれてしまう regression test
- expected failure:
  - current repo target に対する redundant view fetch が発生する

###### Green
- minimum implementation:
  - indexed snapshot key 集合を作り、same-repo indexed target は view fetch 対象から外す helper を導入する
- pass condition:
  - sync same-repo indexed dedup regression test が通る

###### Refactor
- cleanup target:
  - target filtering helper を `sync_state` 以外でも再利用できる形に整理する
- invariants to keep green:
  - foreign target fetch は維持される
  - same-repo target が index missing の場合は fallback fetch を維持する

##### I2 — command parity regression
- slice goal:
  - `check_deps` / `set_active` でも同じ helper を使い、same-repo indexed target へ redundant view fetch を送らないことを固定する

###### Red
- failing test:
  - current repo URL-linked issue + indexed snapshot がある状態で `deps check --github` / `active set --github` が extra view fetch を送る regression test
- expected failure:
  - github-aware read path ごとに fetch selection drift が発生する

###### Green
- minimum implementation:
  - same helper を `check_deps` / `set_active` に適用し、indexed target skip を揃える
- pass condition:
  - command parity regression test が通る

###### Refactor
- cleanup target:
  - helper の責務と naming を整理し、repo-aware status resolution helper 群と整合させる
- invariants to keep green:
  - current repo binding correctness を変えない
  - index incomplete fallback は維持する

#### step gate
- review:
  - same-repo indexed target skip と index-incomplete fallback の両立を説明できる
- expected tests:
  - sync same-repo indexed dedup regression
  - sync same-repo index-missing fallback regression
  - mixed same-repo + foreign target で foreign fetch 維持 regression
  - `deps check --github` / `active set --github` parity regression
  - checked-in dogfooding runtime parity regression または executable smoke
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05H` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05I — deps target 自身の status 解決を inspection 契約へ含める
- target:
  - `deps check` が initiative / epic target 自身の resolved status を `target_status` に正しく露出する
- design refs:
  - `design.md` の `2. status/readiness contract`
  - `discussions/038`
- step boundary:
  - `inspection.issue_statuses` の target payload を補う局所 corrective fix に限定し、node_states の issue-only contract は変えない

#### Red
- failing test:
  - `deps check init-local-... --json` が ready target でも `target_status.authority=unknown` / `stale=true` に落ちる regression
  - `deps check epic-local-... --json` でも同じ regression
  - text render でも target status が `unknown/stale` に退行しないこと

#### Green
- minimum implementation:
  - `inspect_target_deps()` が target 自身の resolved status を `inspection.issue_statuses` に含める
  - presentation 側の target_status 参照経路はそのまま活かす

#### Refactor
- cleanup target:
  - issue-only node state と target status payload の責務境界をコメント/命名で明確にする

#### step gate
- review:
  - inspection 契約に target status を含める理由と presentation 側へ責務を漏らさないことを説明できる
- expected tests:
  - initiative target JSON regression
  - epic target JSON regression
  - target text render regression
  - checked-in parity または executable smoke
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05I` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05J — active/deps URL target で repo scope を保持する
- target:
  - canonical GitHub URL target が `owner/repo` を落とさず exact foreign node を選べるようにする
- design refs:
  - `design.md` の `4.1 repo-scoped exact target surface`
  - `discussions/049`
- step boundary:
  - bare numeric target や `--github-issue` の convenience selector は維持し、URL target の exact scope だけを追加する

#### Red
- failing test:
  - current/foreign same-number coexistence で `active set <foreign-url>` が ambiguous fail または誤解決する regression
  - `deps check <foreign-url>` でも同じ regression
  - checked-in parity でも URL target scope が失われる regression

#### Green
- minimum implementation:
  - `TargetRef` を repo-aware に拡張し、URL parse で repo scope を保持する
  - `set_active` / `check_deps` の target resolution を exact repo scope aware にする

#### Refactor
- cleanup target:
  - URL / bare number / `--github-issue` の contract を parser 層で整理する

#### step gate
- review:
  - URL target と bare target の意味差が command/application/test で一貫している
- expected tests:
  - active URL exact-foreign resolution regression
  - deps URL exact-foreign resolution regression
  - checked-in parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05J` の review と expected tests が通り、`report.md` 更新後にコミットする

### S05K — scoped dependency ref syntax を導入して docs を整合させる
- target:
  - dependency ref に scoped foreign syntax を追加し、bare numeric shorthand の current-repo-only contract を docs/impl/tests で一致させる
- design refs:
  - `design.md` の `4.2 scoped dependency reference contract`
  - `discussions/050`
- step boundary:
  - bare numeric ref を foreign-only match に自動フォールバックさせない
  - foreign dependency は explicit scoped ref で解決する contract へ寄せる

#### Red
- failing test:
  - `owner/repo#123` または canonical URL dependency ref が foreign imported issue を解決できない regression
  - bare numeric ref `123` が foreign-only match を暗黙採用してしまう regression
  - docs / error message が新 contract と食い違う regression

#### Green
- minimum implementation:
  - deps ref parser / resolver に scoped ref syntax を追加する
  - reference docs と error guidance を current-repo-only shorthand + scoped foreign ref の契約へ更新する
  - checked-in runtime parity を揃える

#### Refactor
- cleanup target:
  - bare ref / scoped ref / URL ref のエラーメッセージを整理する

#### step gate
- review:
  - bare numeric ref を fail-closed に保ちつつ foreign dependency support が explicit syntax で閉じている
- expected tests:
  - scoped foreign dep ref resolution regression
  - bare numeric current-repo-only regression
  - docs/help contract regression
  - checked-in parity regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S05K` の review と expected tests が通り、`report.md` 更新後にコミットする

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / help text / dogfooding confirmation
- 対応:
  - provider-side source of truth の docs/help/template を更新する
  - 必要に応じて `spec-dock/` 側 dogfooding workspace で生成結果と導線を確認する
  - `doctor`, `active show`, explicit flags, stale/source 表示, wrong-repo safety の利用方法を docs に反映する
- git commit:
  - docs/spec review が通り、`report.md` 更新後にコミットする

### S90F — checked-in dogfooding runtime parity を repo-scoped GitHub behavior まで揃える
- target:
  - checked-in consumer workspace `spec-dock/scripts/` の `create_node` / `sync_state` を provider-side runtime と同じ repo-aware contract へ refresh する
- design refs:
  - `requirement.md` の `AC-010 dogfooding runtime parity`
  - `design.md` の `dogfooding runtime parity`
  - `discussions/026`, `027`
- step boundary:
  - provider-side source of truth の仕様変更は行わず、checked-in dogfooding runtime の parity drift を補修する
  - full workspace rewrite は避け、review で指摘された runtime file と回帰テストに scope を限定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に `S90F` の作業単位を登録した
- [ ] `spec-deps/current/report.md` の追記位置を決めた

#### B1 — checked-in runtime refresh and parity tests
- purpose:
  - checked-in dogfooding runtime 上でも foreign/current same-number coexistence が provider-side runtime と同じ contract で動くようにする
- files:
  - `spec-dock/scripts/spec_dock_runtime/application/...`
  - `tests/...`

##### I1 — checked-in import uniqueness parity
- slice goal:
  - checked-in `create_node.py` が repo-aware uniqueness 契約を使う

###### Red
- failing test:
  - checked-in runtime で current repo `#123` と foreign repo `other/repo#123` が overlap した時、`import issue <foreign-url> --allow-foreign-url` が bare issue number duplicate として誤 reject される regression test
- expected failure:
  - checked-in runtime だけが bare `github_issue_number` uniqueness に留まる

###### Green
- minimum implementation:
  - checked-in `create_node.py` を provider-side runtime と同じ repo-aware uniqueness 契約へ refresh する
- pass condition:
  - checked-in runtime の cross-repo overlap import regression test が通る

###### Refactor
- cleanup target:
  - checked-in/provider 差分のうち本 step に不要な churn を持ち込まない
- invariants to keep green:
  - provider-side source of truth は変更しない

##### I2 — checked-in sync snapshot parity
- slice goal:
  - checked-in `sync_state.py` が current/foreign same-number coexistence で snapshot を混線させない

###### Red
- failing test:
  - checked-in runtime で current repo issue `#123` と foreign issue `other/repo#123` が共存すると、`sync --github` で foreign snapshot が current repo node に混入する regression test
- expected failure:
  - checked-in runtime だけが bare `issue_number` key の snapshot 集約に留まる

###### Green
- minimum implementation:
  - checked-in `sync_state.py` を provider-side runtime と同じ repo-aware snapshot 集約 / current-repo-first 契約へ refresh する
- pass condition:
  - checked-in runtime の same-number coexistence sync regression test が通る

###### Refactor
- cleanup target:
  - checked-in runtime parity 対象を review 指摘の 2 file と必要最小 tests に閉じる
- invariants to keep green:
  - checked-in runtime の command surface 既存回帰を壊さない

#### step gate
- review:
  - checked-in runtime parity drift が provider-side contract と同じ意味で閉じている
- expected tests:
  - checked-in runtime import uniqueness regression
  - checked-in runtime sync snapshot coexistence regression
  - 既存 checked-in runtime smoke の non-regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S90F` の review と expected tests が通り、`report.md` 更新後にコミットする

### S04H — import preflight と checked-in executable-path evidence を補完する
- target:
  - `AC-012` の application preflight 契約を `import` にも適用し、required artifact 欠損時に create 前で fail-fast させる
  - checked-in runtime の executable-path parity で `import` fail-fast と `sync --force` degraded artifact contract を固定する
- design refs:
  - `requirement.md` の `AC-012 domain/application validation boundary`
  - `design.md` の `domain/application validation boundary`
  - `design.md` の `dogfooding runtime parity`
- step boundary:
  - domain validation は引き続き filesystem 非依存の構造検証に留める
  - required artifact existence check は application preflight helper に寄せ、provider/checked-in 両 runtime の import entrypoint へ同じ契約で適用する

#### B1 — provider-side import preflight closure
- purpose:
  - required artifact 欠損時に `import` が partial write を残さないよう provider-side runtime の fail-fast 契約を閉じる
- files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
  - `tests/cli_runtime/...`

##### I1 — import fail-fast before create
- slice goal:
  - `import issue <url>` が artifact 欠損時に create 前の preflight で止まり、新規 node を作らない

###### Red
- failing test:
  - required artifact 欠損下で `import issue` を実行すると、preflight ではなく post-import sync で落ちて partial write が残る regression test
- expected failure:
  - domain validation だけでは artifact 欠損を捕まえられず create が先に進む

###### Green
- minimum implementation:
  - provider-side `import_node.py` で application artifact preflight を create 前に実行する
- pass condition:
  - import preflight failure 時に `preflight validate failed` で止まり、新規 node が作成されない regression test が通る

###### Refactor
- cleanup target:
  - preflight helper 呼び出しを既存 validate/sync/doctor 契約と揃える
- invariants to keep green:
  - structure error 優先順序を壊さない

#### B2 — checked-in runtime executable-path evidence closure
- purpose:
  - checked-in consumer runtime の executable-path parity を import fail-fast、sync degraded artifact contract、structure-error precedence まで閉じる
- files:
  - `spec-dock/scripts/spec_dock_runtime/application/import_node.py`
  - `tests/test_init_update.py`

##### I1 — checked-in import preflight parity
- slice goal:
  - checked-in `spec-dock/scripts/spec-dock import issue ...` でも artifact 欠損時に create 前で fail-fast する

###### Red
- failing test:
  - checked-in runtime で required artifact を欠損させた状態の `import issue <url>` が新規 issue node を残してから失敗する subprocess regression test
- expected failure:
  - checked-in runtime の import path に artifact preflight がなく partial write を残しうる

###### Green
- minimum implementation:
  - checked-in `import_node.py` に provider-side と同じ application preflight を適用する
- pass condition:
  - checked-in runtime subprocess test が `preflight validate failed` と `新規 node 未作成` を確認して通る

##### I2 — checked-in sync --force artifact output parity
- slice goal:
  - checked-in `sync --force` が warning degradation 時も generated artifact 契約を保持する

###### Red
- failing test:
  - checked-in runtime subprocess の `sync --force` が stderr だけ warning し、`.agent/index.json` / `.agent/tree.json` の `deps.valid=false` / `deps.error` を壊しても検知されない regression test
- expected failure:
  - executable-path parity がログ文言だけに依存し、generated artifact 契約の崩れを見逃す

###### Green
- minimum implementation:
  - subprocess parity test で degraded sync 後の generated artifact を読み、`deps.valid=false` と `deps.error` を固定する
- pass condition:
  - checked-in runtime subprocess `sync --force` parity regression test が通る

##### I3 — checked-in structure-error precedence parity
- slice goal:
  - checked-in `validate` / `doctor` / `sync` が structure error と artifact 欠損の同時発生時に structure error を優先する

###### Red
- failing test:
  - checked-in runtime subprocess で structure error と artifact 欠損を同時に作ると、artifact error が先に出て structure corruption を隠す regression test
- expected failure:
  - executable-path parity が combined-fault precedence を固定しておらず、artifact preflight の適用位置変更で priority が逆転しても検知できない

###### Green
- minimum implementation:
  - checked-in subprocess parity test で `validate` / `doctor` / `sync` の structure-error precedence を明示固定する
- pass condition:
  - combined-fault subprocess regression が通り、`Missing required artifact` より構造エラーを優先して返す

#### step gate
- review:
  - provider/checked-in 両 runtime で import preflight と degraded sync artifact contract が `AC-012` に整合している
- expected tests:
  - provider-side import missing-artifact fail-fast regression
  - checked-in runtime import missing-artifact subprocess regression
  - checked-in runtime `sync --force` degraded artifact output regression
  - checked-in runtime combined-fault structure precedence regression
  - 既存 validation boundary non-regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S04H` の review と expected tests が通り、`report.md` 更新後にコミットする

### S99 — final diff review quality gate
- branch diff scope:
  - `fix/issue-28-runtime-regression-bugs` の差分全体
- required validation:
  - 影響範囲テスト一式
  - local/stub manual regression の再確認
  - GitHub live regression の実行結果と証跡
  - create outcome matrix full coverage evidence
  - `rg --files | rg '[A-Z]'` による path rule 再確認
- reviewer approvals:
  - implementation review
  - QA review
  - spec/docs review
  - create/post-create outcome matrix の 5 class について、raw `release_error` 単独露出が残っていない
  - create/post-create outcome matrix の committed-local branch で blind rerun guidance が残っていない
  - provider / checked-in runtime の guidance contract drift が残っていない
  - repo-overlap matrix と create-state matrix の bundle-level regression が通っている
    - repo-overlap matrix: URL target exact resolution / bare numeric current-repo-only / scoped dep ref exact-foreign
    - create-state matrix: remote-only / partial local write / in-progress missing-meta / stale create lock が区別されている
- git commit:
  - `S99` は最終 review/no-op 判定であり、この step 自体を理由に新規コミットは作らない

### S90G — checked-in parity の stale json/deps paths を閉じる
- target:
  - checked-in consumer runtime の `presentation/json_state.py` と `infra/deps_reader.py` を provider-side parity へ refresh する
  - checked-in import post-sync と repo-aware numeric deps resolution が provider-side と同じ contract で動くようにする
- design refs:
  - `requirement.md` の `AC-010 dogfooding runtime parity`
  - `requirement.md` の `AC-013 repo-aware numeric deps resolution`
  - `design.md` の `dogfooding runtime parity`
  - `discussions/033`, `034`
- step boundary:
  - provider-side source of truth の仕様変更は行わず、checked-in runtime の stale parity drift のみを補修する
  - `json_state` と `deps_reader` の two-file parity と、それを通す checked-in runtime regression に scope を限定する

#### B1 — checked-in rendering parity
- purpose:
  - checked-in import post-sync が linked node の snapshot fallback 経路で crash しないようにし、実行経路でも provider-side と同じ artifact rendering 契約を示す
- files:
  - `spec-dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `tests/test_init_update.py`

##### I1 — import post-sync no-crash parity
- slice goal:
  - checked-in runtime の import/sync artifact rendering が provider-side と同じ repo-aware fallback helper を使う

###### Red
- failing test:
  - checked-in linked import の post-sync で `NameError: _normalize_repo_slug` が出る regression test
- expected failure:
  - checked-in `json_state.py` に provider-side helper parity がない

###### Green
- minimum implementation:
  - checked-in `presentation/json_state.py` を provider-side helper 契約へ refresh する
- pass condition:
  - checked-in `spec-dock/scripts/spec-dock` 実行経路の import post-sync no-crash regression test が通る

#### B2 — checked-in repo-aware numeric deps parity
- purpose:
  - checked-in runtime の numeric `depends_on: [123]` が current/foreign same-number coexistence でも provider-side と同じ repo-aware 解決を行い、実行経路でも ambiguity を再発させない
- files:
  - `spec-dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `tests/test_init_update.py`

##### I1 — deps overlap parity
- slice goal:
  - checked-in `deps check` / `sync` / `validate` が current repo `#123` と foreign `other/repo#123` の coexistence でも bare numeric ref を current repo scope へ解決する

###### Red
- failing test:
  - checked-in runtime で same-number overlap 下の numeric deps が `Ambiguous github.issue_number=123` になる regression test
- expected failure:
  - checked-in `deps_reader.py` が bare numeric ref を repo-aware に解決できない

###### Green
- minimum implementation:
  - checked-in `infra/deps_reader.py` を provider-side の current-repo-aware numeric deps 契約へ refresh する
- pass condition:
  - checked-in `spec-dock/scripts/spec-dock` 実行経路の numeric deps overlap regression test が通る

#### step gate
- review:
  - checked-in runtime の json rendering と numeric deps resolution が provider-side contract と同じ意味で閉じている
- expected tests:
  - checked-in executable-path import post-sync no-crash regression
  - checked-in executable-path numeric deps overlap parity regression
  - 既存 checked-in runtime parity non-regression
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S90G` の review と expected tests が通り、`report.md` 更新後にコミットする

## 未確定事項
- なし
  - freshness contract は本計画で `source / stale / last_sync_at` をまとめて first fix に含める前提で固定する

## final exit contract
- AC/EC 達成:
  - `AC-001` から `AC-009`、`AC-010`、`AC-011`、`AC-012`、`AC-013`、`AC-014`、`AC-015`、`AC-016`、`AC-017`、`AC-018`、`AC-019`、`AC-020` が対応 step の review/QA 付きで満たされている
  - 4 設計テーマの変更が application/domain/infra/presentation の責務境界を守って実装されている
  - create/post-create outcome matrix の 5 class が provider / checked-in runtime で同じ guidance contract と review evidence を持つ
- docs impact resolved:
  - provider-side docs と dogfooding 確認が完了し、`report.md` に判断と結果が残っている
- manual verification prepared:
  - `S98` が完了し、`manual-tests/` の workspace/report scaffold と `discussions/055` の checklist contract が揃っている
  - same-repo / foreign-repo / no-origin / stale-active の 4 観点に対する fixture と evidence 採取手順が固定されている
- manual verification executed:
  - `S98A` が完了し、`MT-00` から `MT-08` の enriched exploratory round evidence が report artifact に残っている
- final diff approved:
  - `S99` の required validation が完了し、GitHub live regression を含む最終 diff review で重大懸念が解消されている

### S98 — manual verification preparation
- target:
  - `manual-tests/` 配下に、repo-scope / no-origin / stale-active / pathfile parity を再現する workspace と report scaffold を用意する
- boundaries:
  - provider 実装の追加変更は行わない
  - manual workspace / helper / report skeleton の準備に限定する
- concrete deliverables:
  - `discussions/055` に一致する workspace 4 種
  - `checklist.md` / `execution-log.md` / `summary.md` の skeleton
  - `.path` fallback 用 helper launcher
  - GitHub current/foreign repo URL と richer exploratory matrix を反映した checklist contract
- verification:
  - checklist contract に required fields がある
  - overlap fixture / churn fixture / repo URL / workspace map / `.path` launcher / operator-time-window-resume が checklist に記入可能な欄として存在する
  - execution log skeleton に timestamp / case / precondition / command / expected / actual / diff / verdict / evidence の欄がある
  - execution log skeleton に checks / side effects / touched ids-urls / invariants / anomaly-hypothesis / checkpoint の欄がある
  - summary skeleton に overall verdict / findings / residual risks / skipped-or-blocked / next actions / finding categories の欄がある
  - `.path` helper launcher が作成され、MT-06 の再現手順として参照できる
- report update rule:
  - `report.md` に S98 の準備内容、spec review 結果、pending external dependency を追記する

### S98A — manual verification execution
- target:
  - `discussions/055` の enriched exploratory round を実行し、multi-resource / live churn / no-origin / recovery evidence を収集する
- boundaries:
  - provider 実装の追加変更は行わない
  - manual workspace 操作、GitHub issue mutation、report artifact 記録に限定する
- concrete deliverables:
  - `checklist.md` の verdict 更新
  - `execution-log.md` の case records と checkpoint records
  - `summary.md` の overall verdict と finding categories
- verification:
  - `MT-00` で provider/generated runtime parity と live fixture seed が記録されている
  - `MT-02` / `MT-03` / `MT-05` で `active set` / `deps check` / `sync --github` / status-readiness evidence がある
  - `MT-04` で live churn 3 種以上、`MT-06` で recovery submatrix と `context-pack.md` vs active-entrypoint parity、`MT-07` で 3 checkpoint organic session が記録されている
  - `MT-07` では issue と epic の両方に dependency 登録がある
- report update rule:
  - `report.md` に S98A の execution verdict、主要 finding、residual risks を追記する
