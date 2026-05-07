---
種別: 要件定義書（Issue）
ID: "iss-00088"
タイトル: "Issue lifecycle start and finish commands"
関連GitHub: ["#88"]
状態: "defined"
作成者: "iwasawayuuta"
最終更新: "2026-05-06"
親: ["epic-00054", "init-local-00002"]
---

# iss-00088 Issue lifecycle start and finish commands — 要件定義（WHAT / WHY）

## この issue で実施すること
- `spec-dock issue start <target>` と `spec-dock issue finish` を、issue 実行の通常開始・通常終了 command として追加する。
- `issue start` は対象 issue を active にし、対応 branch を checkout する。対象は issue node のみに限定する。
- `issue start` は、未完了の active issue branch 上で別 issue を開始しようとした場合に default で停止し、誤って複数 issue にまたがる作業へ流れることを防ぐ。
- `issue start -f` / `--force` は、この unfinished active issue guard だけを明示的に bypass する。依存未解決や readiness check は bypass しない。
- `issue finish` は current active issue の linked GitHub issue を close し、すでに closed の場合も success として扱い、その成功確認後に active state を解除する。
- `active set` / `active set --checkout` は既存の低レベル manual / recovery path として残し、今回の unfinished guard を適用しない。
- provider runtime、dogfooding runtime mirror、CLI help、provider docs、dogfooding docs、issue execution skill、root README を一貫した lifecycle contract に更新する。
- 自動テストに加えて、real GitHub repo を使う manual test を実施し、実運用に近い start / guard / force / finish / failure recovery / cleanup を確認する。

## 完了後にユーザーが得る状態
- agent や maintainer は、issue 作業の入口として `issue start` を使えば active 設定と branch checkout を一操作で完了できる。
- 未完了 issue の branch 上で別 issue を始めようとしたとき、CLI が危険を説明し、`issue finish`、`issue start -f`、manual `active set --checkout` の選択肢を提示する。
- `issue finish` により、GitHub issue close と active clear が明示的な終了操作として結びつく。
- 非常時・復旧時には、従来どおり direct `active set` を使える。
- docs / skill / README を読んだ agent が、通常 lifecycle と manual recovery path を混同しにくくなる。

## 目的
- 通常の issue 実行入口として `spec-dock issue start` / `spec-dock issue finish` を追加し、agent と maintainer が active issue と checkout を明確な lifecycle 操作として扱えるようにする。
- 手動・復旧用の `active set` は維持しつつ、未完了 issue branch から別 issue を開始する accident path だけを guided command 側で止める。
- Phase 1 として main / protected branch の hard block ではなく、作業性を保つ soft guardrail と明確な次アクション提示を導入する。

## 背景・現状
- 現状の挙動:
  - `active set` は active pointer を設定でき、`--checkout` を明示した場合だけ branch 作成または checkout を行う。
  - `close` は linked GitHub issue を close できるが、active issue lifecycle の終了導線とは結びついていない。
  - `active set` / `close` は低レベル操作として存在する一方、通常の issue 実行を「開始」と「終了」で表す command surface はない。
- 現状の課題:
  - 複数 issue にまたがる agent 作業で、active issue を固定せず、checkout せず、issue close もしないまま長大な変更に進む余地がある。
  - `active set --checkout` を通常開始手順として毎回思い出す必要があり、agent 向けの primary path と手動復旧 path が混ざっている。
  - 強い main branch 制限を先に入れると、非常時対応や手動復旧の作業性を落とす。
  - 未完了 issue branch から別 issue へ移る場合に、何が危険で、どう続行または中断すべきかを CLI が説明しない。
- 再現手順:
  1. issue branch 上で active issue の作業を進める。
  2. GitHub issue を close していない状態で、別 issue の作業へ移ろうとする。
  3. 現状は通常開始 command がないため、agent は `active set` を省略したり、別 branch へ移る判断を曖昧にしたまま作業を続けられる。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock active set <target> --checkout`
    - `./spec-dock/scripts/spec-dock close <target>`
    - 新規 `./spec-dock/scripts/spec-dock issue start <target>`
    - 新規 `./spec-dock/scripts/spec-dock issue finish`
  - Git:
    - current branch が registered issue branch として認識されるか
  - GitHub:
    - active issue の linked GitHub issue state が `CLOSED` かどうか
  - Docs / skills:
    - issue execution workflow と agent skill が `issue start` / `issue finish` を primary path として案内するか
- 情報源:
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_naming.md`
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/requirement.md`
  - 2026-05-05 lifecycle command planning discussion

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - issue 単位で spec-dock 作業を進める maintainer
  - active issue docs を入口に実装する coding agent / orchestrator
  - 非常時や復旧時に低レベル `active set` も使いたい maintainer
- 代表シナリオ:
  - maintainer が `issue start iss-00088` を実行し、active issue 設定と branch checkout を一操作で完了する。
  - agent が未完了 active issue branch 上で別 issue を start しようとして止められ、`issue finish` または `issue start <target> -f` のどちらを実行すべきか理解できる。
  - maintainer が `issue finish` を実行し、active issue の GitHub issue を close したうえで active state を解除する。
  - 手動復旧時は従来通り `active set` / `active set --checkout` を制限なく使える。

## スコープ
- MUST:
  - `spec-dock issue start <target>` を追加し、issue node のみを対象に active set と checkout を実行できること
  - `spec-dock issue start <target> -f` / `--force` を追加し、unfinished active issue guard を明示的に bypass できること
  - `spec-dock issue finish` を追加し、current active issue の linked GitHub issue を close または already-closed success として扱い、その後 active state を解除できること
  - `issue start` は active issue branch 上で別 issue を開始しようとする場合、active issue の GitHub state が `CLOSED` でない限り default stop すること
  - `issue start` の default stop message は current active issue、current branch、requested issue、GitHub state、次に実行できる command を表示すること
  - `issue start` は active issue の GitHub state を取得できない場合、unfinished として安全側に停止すること
  - `issue start -f` は unfinished active issue guard だけを bypass し、dependency readiness / target validation / checkout safety は bypass しないこと
  - `active set` / `active set --checkout` の既存挙動を変えず、manual / recovery path として残すこと
  - provider docs / dogfooding docs / issue execution skill / CLI help を `issue start` / `issue finish` の primary path に揃えること
  - root `README.md` と `workflow-tree.md` など利用者が最初に触る docs でも、`issue start` / `issue finish` を primary path として案内すること
  - `issue finish` は delivery completion、commit、push、PR、merge、validate、test、review の完了を保証しないことを docs / skill に明記すること
  - `issue finish` 前に delivery completion evidence を report に記録し、`issue finish` 後に active issue が残ることを complete condition にしないこと
  - provider asset と dogfooding mirror の差分 drift を、テストまたは明示的な diff 検証で確認できること
  - manual test 用の計画・チェックリスト・実行ログ・サマリを `manual-tests/reports/2026-05-05-iss-00088-issue-lifecycle/` に残すこと
- MUST NOT:
  - Phase 1 で main / master / develop / staging などの branch からの `issue start` を禁止しない
  - Phase 1 で dirty worktree を spec-dock 独自の hard block 条件にしない
  - `issue finish` で commit、push、merge、PR 作成、stash、report 自動編集を行わない
  - `active set` / `active set --checkout` に unfinished active issue guard を追加しない
  - `-f` / `--force` に理由入力を必須化しない
- OUT OF SCOPE:
  - PR 作成、PR monitoring、merge automation
  - protected branch policy enforcement
  - issue completion criteria の完全自動判定
  - incident mode / reason-required audit schema
  - local delete command の追加または変更
  - `issue finish` 後に自動で `main` へ checkout する挙動
  - `sync --github` の branch-derived active restoration contract の変更

## 境界
- Always:
  - `issue start` は通常 issue execution の guided path として扱う
  - `active set` は低レベルの手動・復旧・migration・explicit user instruction path として扱う
  - unfinished 判定の正本は linked GitHub issue の `CLOSED` state とする
  - GitHub state を確認できない場合は安全側に倒し、unfinished として扱う
  - `issue finish` は GitHub issue close / already-closed 確認が成功した場合だけ active state を解除する
  - `issue finish` 後も current Git branch は自動では変えない
  - final sync で active clear を保ちたい場合は、`main` など non-issue branch へ移動してから `sync --github` する運用を docs / report に残す
- Ask:
  - Phase 2 以降で `--reason` を任意または必須にするか
  - Phase 2 以降で `issue finish` に validate / sync / report evidence check を追加するか
- Never:
  - `issue finish` を merge / deploy / review complete と同義にしない
  - force bypass を silent success にしない
  - manual recovery path を塞がない

## 非交渉制約
- additive command change とし、既存 `active set`、`close`、`sync`、`validate`、`deps` の contract を壊さないこと
- command runtime の source of truth は provider-side `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` とすること
- shipped docs/templates/system を変更する場合は provider-side assets と dogfooding mirror の整合を取ること
- branch checkout naming は既存 `active set --checkout` の `<id>-<slug>` 正規化 contract に従うこと
- GitHub issue state の取得と close は既存 GitHub CLI integration の repo scope / current repo linkage contract に従うこと

## 前提
- 本 issue は `epic-00054` の GitHub lifecycle command expansion の追加 slice として扱う。
- `close` command は既に linked GitHub issue close の低レベル capability を提供している。
- `issue finish` は `close` capability を active issue lifecycle の終了導線として再利用する。
- `issue start` の checkout は既存 active set checkout behavior を再利用し、独自 branch naming を導入しない。
- `-f` / `--force` の理由入力は Phase 1 では要求しない。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / coding agent
  - Given:
    - linked GitHub issue を持つ issue node が存在する
  - When:
    - `./spec-dock/scripts/spec-dock issue start <target>` を実行する
  - Then:
    - 対象 issue が active issue になる
    - 対象 issue の branch が checkout される
    - 対象が issue node でない場合は fail-fast する
  - 観測点:
    - CLI / runtime tests
    - `spec-dock/.agent/active.json`
    - current branch
- AC-002:
  - Actor:
    - maintainer / coding agent
  - Given:
    - current branch が active issue branch として認識される
    - active issue の linked GitHub issue state が `CLOSED` ではない
    - requested issue が active issue と異なる
  - When:
    - `./spec-dock/scripts/spec-dock issue start <requested>` を `-f` なしで実行する
  - Then:
    - command は停止する
    - active state は変更されない
    - checkout は行われない
    - message に current active issue、current branch、requested issue、GitHub state、`issue finish`、`issue start <requested> -f`、manual `active set` の導線が表示される
  - 観測点:
    - CLI / runtime tests
    - active state unchanged assertion
    - git checkout not called assertion
- AC-003:
  - Actor:
    - maintainer / coding agent
  - Given:
    - AC-002 と同じ unfinished active issue branch 状態
  - When:
    - `./spec-dock/scripts/spec-dock issue start <requested> -f` を実行する
  - Then:
    - guard は bypass される
    - dependency readiness が未充足の場合は `-f` 付きでも停止する
    - requested issue が active issue になる
    - requested issue branch が checkout される
    - output に forced start であることが表示される
  - 観測点:
    - CLI / runtime tests
    - active state
    - current branch
- AC-004:
  - Actor:
    - maintainer / coding agent
  - Given:
    - current branch が `main` / `master` / `develop` / `staging` または registered issue branch と認識されない branch である
  - When:
    - `./spec-dock/scripts/spec-dock issue start <target>` を実行する
  - Then:
    - unfinished active issue guard は発火しない
    - 通常の target resolution / deps / checkout の結果に従って start が進む
  - 観測点:
    - CLI / runtime tests
- AC-005:
  - Actor:
    - maintainer / coding agent
  - Given:
    - active issue が linked GitHub issue を持つ
  - When:
    - `./spec-dock/scripts/spec-dock issue finish` を実行する
  - Then:
    - linked GitHub issue が open の場合は close される
    - linked GitHub issue が already closed の場合は success として扱われる
    - close / already-closed 確認後に active state が解除される
  - 観測点:
    - CLI / runtime tests
    - GitHub issue state
    - `spec-dock/.agent/active.json` または active show
- AC-006:
  - Actor:
    - maintainer / coding agent
  - Given:
    - active issue が存在しない、または active issue が GitHub issue に linked されていない、または GitHub close / state 確認が失敗する
  - When:
    - `./spec-dock/scripts/spec-dock issue finish` を実行する
  - Then:
    - command は fail-fast する
    - active state は変更されない
    - 次に取るべき復旧 action が表示される
  - 観測点:
    - CLI / runtime tests
    - active state unchanged assertion
- AC-007:
  - Actor:
    - reviewer
  - Given:
    - provider docs、dogfooding docs、agent skill、CLI help を確認する
  - When:
    - issue execution の通常導線を読む
  - Then:
    - `issue start` -> 実装 -> 検証 / report -> `issue finish` が primary path として説明されている
    - `active set` は manual / recovery path として説明されている
    - `issue finish` が merge / PR / commit / validate success を保証しないことが明記されている
  - 観測点:
    - docs / skill diff
    - tests where applicable
- AC-008:
  - Actor:
    - maintainer / reviewer
  - Given:
    - manual test 用 GitHub repo と manual workspace が用意されている
  - When:
    - manual test plan に従って real GitHub issue を使った lifecycle 操作を実行する
  - Then:
    - normal start、unfinished guard、force + dependency readiness、manual active set boundary、non-issue branch start、finish success、already-closed finish、failure recovery guidance、final health check が確認される
    - temporary GitHub issues は close される
    - plan / checklist / execution-log / summary が残る
  - 観測点:
    - `manual-tests/reports/2026-05-05-iss-00088-issue-lifecycle/`
    - manual GitHub repo issue state

## 例外・エッジケース
- EC-001:
  - 条件:
    - requested target が initiative / epic node である
  - 期待:
    - `issue start` は issue node のみを許可し、対象種別不一致で fail-fast する
  - 観測点:
    - CLI / runtime tests
- EC-002:
  - 条件:
    - active issue の GitHub state を取得できない
  - 期待:
    - `issue start` は unfinished として default stop し、`-f` による続行導線を表示する
  - 観測点:
    - CLI / runtime tests
- EC-003:
  - 条件:
    - active issue と requested issue が同じである
  - 期待:
    - `issue start` は idempotent に進む、または already active として success を返す
  - 観測点:
    - CLI / runtime tests
- EC-004:
  - 条件:
    - checkout 時に git worktree dirty など既存 `active set --checkout` の safety guard が失敗する
  - 期待:
    - `issue start` は既存 checkout failure を伝え、active state と checkout を中途半端に進めない
  - 観測点:
    - CLI / runtime tests
- EC-005:
  - 条件:
    - `active set` / `active set --checkout` を直接実行する
  - 期待:
    - unfinished active issue guard は適用されず、既存 command contract が維持される
  - 観測点:
    - regression tests
- EC-006:
  - 条件:
    - `issue finish` 後、current branch が issue branch のまま `sync --github` を実行する
  - 期待:
    - 既存 sync contract により branch 名から active が復元されうる
    - この issue では sync contract を変更せず、運用上の注意として manual test / report に記録する
  - 観測点:
    - manual test execution log

## 入力→出力例
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock issue start iss-00088`
  - Output:
    - active issue が `iss-00088` になり、branch `iss-00088-issue-lifecycle-start-and-finish-commands` が checkout される
- EX-002:
  - Input:
    - `./spec-dock/scripts/spec-dock issue start iss-00089`
  - Output:
    - `Cannot start iss-00089 because active issue iss-00088 is not closed.`
    - `Run ./spec-dock/scripts/spec-dock issue finish or ./spec-dock/scripts/spec-dock issue start iss-00089 -f.`
- EX-003:
  - Input:
    - `./spec-dock/scripts/spec-dock issue finish`
  - Output:
    - active issue の linked GitHub issue が close され、active state が解除される

## 用語（ドメイン語彙）
- TERM-001:
  - issue start:
    - issue node を active にし、対応 branch を checkout する通常開始 command
- TERM-002:
  - issue finish:
    - current active issue の linked GitHub issue を close / already-closed 確認し、active state を解除する通常終了 command
- TERM-003:
  - unfinished active issue:
    - current active issue の linked GitHub issue state が `CLOSED` と確認できない状態
- TERM-004:
  - registered issue branch:
    - spec-dock graph 内の issue id または GitHub issue number から current branch が特定 issue に対応すると推定できる branch

## 未確定事項
- なし:
  - Phase 1 は `issue start` / `issue finish` guided lifecycle command、docs / skill alignment、automated regression、manual GitHub-backed validation に限定する。

## 成功条件
- runtime:
  - `issue start` / `issue finish` が CLI command として利用できる
  - existing `active set` / `close` / `deps` contract が壊れていない
- safety:
  - 未完了 issue branch からの accidental switch は default block される
  - emergency / recovery path は塞がれない
- documentation:
  - provider docs、dogfooding docs、root README、issue execution skill が同じ lifecycle model を説明している
- verification:
  - targeted lifecycle tests、active/close regression、full unittest、validate、sync、provider/mirror parity、manual GitHub-backed test が pass している
- evidence:
  - `spec-dock/active/issue/report.md` に自動テスト、review、manual test の証跡が記録されている
