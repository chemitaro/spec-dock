---
種別: 実装計画書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28", "https://github.com/chemitaro/spec-dock/issues/28"]
状態: "in_progress"
作成者: "Codex CLI"
最終更新: "2026-03-19"
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
- S99:
  - 観測可能な振る舞い: branch diff 全体が requirement/design/plan と一致し、実装・QA・spec review が通っている
  - closes:
    - final diff review quality gate
  - review gate:
    - reviewer が「この diff を merge してよい」と判断できる

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`, `S02`
- `AC-002` -> `S03`
- `AC-003` -> `S04`
- `AC-004` -> `S05`
- `AC-005` -> `S03`, `S05`
- `AC-006` -> `S04`
- `AC-007` -> `S05`
- `AC-008` -> `S04`
- `AC-009` -> `S02`
- `AC-010` -> `S90`
- `AC-011` -> `S05F`
- `AC-012` -> `S04F`

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
  - `AC-001` の完了は `S02` を含めて判定する。S01 単体では B01 と node create 側の atomicity を閉じる

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
  - lock scope、timeout 契約、stale lock acquire-side policy、post-write duplicate guard の位置を説明できる
- expected tests:
  - duplicate id prevention regression（initiative/epic/issue を含む）
  - lock contention failure regression
  - stale lock safe failure regression
  - 既存 create command 回帰
- report update:
  - `spec-deps/current/report.md`
- git commit:
  - `S01` の review と expected tests が通り、`report.md` 更新後にコミットする

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
  - `S01` と合わせて `AC-001 create atomicity` を完了させる step として扱う

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

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / help text / dogfooding confirmation
- 対応:
  - provider-side source of truth の docs/help/template を更新する
  - 必要に応じて `spec-dock/` 側 dogfooding workspace で生成結果と導線を確認する
  - `doctor`, `active show`, explicit flags, stale/source 表示, wrong-repo safety の利用方法を docs に反映する
- git commit:
  - docs/spec review が通り、`report.md` 更新後にコミットする

### S99 — final diff review quality gate
- branch diff scope:
  - `fix/issue-28-runtime-regression-bugs` の差分全体
- required validation:
  - 影響範囲テスト一式
  - local/stub manual regression の再確認
  - GitHub live regression の実行結果と証跡
  - `rg --files | rg '[A-Z]'` による path rule 再確認
- reviewer approvals:
  - implementation review
  - QA review
  - spec/docs review
- git commit:
  - `S99` は最終 review/no-op 判定であり、この step 自体を理由に新規コミットは作らない

## 未確定事項
- なし
  - freshness contract は本計画で `source / stale / last_sync_at` をまとめて first fix に含める前提で固定する

## final exit contract
- AC/EC 達成:
  - `AC-001` から `AC-009` が対応 step の review/QA 付きで満たされている
  - 4 設計テーマの変更が application/domain/infra/presentation の責務境界を守って実装されている
- docs impact resolved:
  - provider-side docs と dogfooding 確認が完了し、`report.md` に判断と結果が残っている
- final diff approved:
  - `S99` の required validation が完了し、GitHub live regression を含む最終 diff review で重大懸念が解消されている
