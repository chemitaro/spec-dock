---
種別: 要件定義書（Issue）
ID: "iss-00038"
タイトル: "Docs Dogfooding Parity and Final Regression Gate"
関連GitHub: ["#38"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-31"
親: ["epic-00033", "init-local-00003"]
---

# iss-00038 Docs Dogfooding Parity and Final Regression Gate — 要件定義（WHAT / WHY）

## 目的
- epic `epic-00033` の最後の open slice として、provider docs / dogfooding docs の close-out と final spec review record を完成させる。
- `iss-00040` が完了させた wrappers / domain / dogfooding parity / final regression evidence を参照可能な形で束ね、`E-AC-005` の docs/spec-review slice を客観的に閉じる。
- この issue は epic の `E-RQ-005` を close し、`E-AC-005` の docs/spec-review slice を完了させる owner である。
- 追加 corrective scope として、epic-level branch diff review で露出した status authority、dependency graph、commit-backed audit trail の不整合を解消し、epic close readiness を監査可能にする。
- latest fresh review で残った `S09` fresh final rereview record 欠落、`epic-00033/report.md` の GitHub issue `#33` OPEN/CLOSED authority ambiguity、`iss-00040/report.md` の provisional upstream evidence 表記を narrow corrective scope として解消し、final close judgement を committed rereview まで閉じる。
- final close-out rereview で、`docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の provider/dogfooding 側に stale `--no-github` create guidance が残っていると判明したため、これは original six-file targeted docs slice を reopen しない narrow rules/docs-authority corrective として扱う。
- S12 corrective 後の fresh review で、canonical guidance tests がなお initiative 配下 epic create guidance に `--no-github` を期待していると判明したため、current docs contract を正本とした test expectation realignment を narrow follow-up corrective として扱う。
- PR #41 の fresh external review で、README walkthrough example の parent reference が sequential shorthand と exact id を混在させており利用者を誤誘導しうる点、ならびに numeric GitHub import が `initiative` / `epic` では unresolved repo scope のまま unscoped linkage を作りうる点が指摘されたため、merge 前 corrective scope として扱う。

## 背景・現状
- 現状の挙動:
  - generated status / deps の正本は `spec-dock/.agent/index-all.json` であり、active-only projection である `spec-dock/.agent/index.json` / `spec-dock/.agent/deps-issues.json` は `spec-dock/dashboard.md` の `todo_total: 0` 到達後に空でもよい。
  - `epic-00033/report.md` では `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` が完了済み、残件は `iss-00038` の docs close-out と final spec review record のみと整理されている。
  - targeted docs list である `reference_github.md` / `reference_naming.md` / `reference_sync.md` は provider-side と dogfooding 側で現時点ですでに一致している。
  - `iss-00040` が owner だった regression/parity 系 evidence は現スナップショットでも pass しており、full suite / parity / `validate` / `sync` は current contract に整合している。
- 現状の課題:
  - `iss-00038` 自身の issue spec は split 前の責務を引きずっており、`iss-00040` へ移管済みの final regression ownership が requirement/design/plan に残っている。
  - docs parity が現時点で no-op に見えても、close evidence と final spec review record が整理されない限り epic close-out を客観的に判定できない。
  - acceptance review の結果、`report.md` の final close-out record に「未コミット」表記と曖昧な `状態` 値が残っており、実際の git history / approved state と整合しないことが判明した。
  - epic-level branch diff review の結果、`epic-00033/report.md` の `E-AC-005` がなお Partial/open のまま、`iss-00038/deps.json` に `iss-00040` が無く、S06 corrective 記録も committed audit trail になっていないことが判明した。
  - latest fresh review の結果、S09 は execution evidence の記録までで fresh final rereview record が未記録、`epic-00033/report.md` は本文の completion claims と例外メモの `#33 OPEN` が衝突し、`iss-00040/report.md` も `draft | approved` などの provisional marker を含むため、upstream evidence を final review 用に正規化する必要がある。
  - final close-out rereview の結果、original six-file targeted docs slice の外側にある `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の provider/dogfooding docs が、なお stale `--no-github` create guidance を保持しており、docs/rules authority と `reference_github.md` の GitHub-mandatory contract が不整合だと判明した。
  - PR #41 の外部 review の結果、`README.md` walkthrough example が parent node 指定で exact id と shorthand を混在させており current GitHub-mandatory create contract の読み手に誤解を与えうること、また `import_node.py` の numeric import guard が `issue` にしか適用されず `initiative` / `epic` では current repo scope 未解決時でも unscoped GitHub linkage metadata を作りうることが判明した。
- 再現手順:
  1. `spec-dock/active/epic/plan.md` と `spec-dock/active/epic/report.md` を確認する。
  2. `iss-00038` の現 spec が split 前の責務を含んでいることを確認する。
  3. provider/dogfooding の targeted docs list を比較すると、現時点では内容差分がないことを確認できる。
- 観測点:
  - Docs:
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - `spec-dock/docs/reference_github.md`
    - `spec-dock/docs/reference_naming.md`
    - `spec-dock/docs/reference_sync.md`
  - State:
    - `spec-dock/dashboard.md`
    - `spec-dock/.agent/index-all.json`
    - `spec-dock/.agent/index.json`
  - Upstream evidence:
    - `epic-00033/report.md`
    - `iss-00040/report.md`
- 情報源:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/plan.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t090100z-disc-epic-close-status-reconciliation-analysis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t090200z-disc-deps-graph-and-readiness-alignment-analysis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t090300z-disc-commit-backed-audit-trail-normalization-analysis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t174500z-disc-s09-final-rereview-record-closure-analysis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t174600z-disc-epic-report-33-open-closed-authority-mismatch-analysis.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t174700z-disc-upstream-evidence-normalization-for-iss-00040-report-analysis.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - epic close を判断する maintainer / spec reviewer
- 代表シナリオ:
  - maintainer が `epic-00033` を close する前に、targeted docs list、`validate` / `sync` の実行結果、upstream issue evidence、final spec review verdict を 1 つの issue close-out evidence として確認する。
  - reviewer が `iss-00038` と `iss-00040` の責務非重複を確認しつつ、`E-AC-005` の残 slice が docs/spec-review だけであることを判定する。

## スコープ
- MUST:
  - `iss-00038` の scope を `docs parity + final spec review record` に再固定し、`iss-00040` へ移管済みの責務を除外する。
  - targeted docs list 6 ファイルについて、old local-only / sequential / index assumption が残っていないことを current contract review で 1 ファイルずつ確認し、その確認結果を close evidence として残す。parity が no-op でも、この current contract verification evidence を省略しない。
  - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` の close-out evidence を取得する。
  - S01 の spec review pass と `iss-00040` 非重複確認について、観測コマンドまたは観測 artifact を伴う承認記録を `report.md` に残し、その承認後にのみ S02 へ進む。
  - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence を参照する final spec review record を作成し、verdict を `pass` に到達させる。
  - `report.md` の front matter と S04 close-out 記録は、最終的な git history / reviewer verdict と矛盾しない確定状態に正規化する。
  - final close-out rereview で見つかった provider/dogfooding 両側の `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` stale `--no-github` guidance を、`reference_github.md` の GitHub-mandatory create contract に揃える。これは original six-file targeted docs slice の結論を broader docs no-finding claim に拡張しない narrow corrective として扱う。
  - S12 で正規化した current guidance を読む canonical guidance tests について、旧 `--no-github` 期待値が残っている場合は、docs contract を戻さず test expectation を current shipped guidance に揃える narrow follow-up corrective を許可する。
  - S12 の docs-authority corrective は、`ba732ec` を rules pair の historical anchor、`d018c86` を `docs/github.md` / `docs/workflow-tree.md` corrective anchor として、両方を `report.md` から追える commit-backed traceability を要求する。
  - `README.md` walkthrough corrective では、numeric shorthand の便宜説明を残してもよいが、逐次実行 example 本文は parent reference を exact node id で統一し、initiative -> epic -> issue の一本道 walkthrough として監査可能にする。
  - numeric GitHub import corrective では、repo scope 必須 guard を `issue` 専用の暫定実装のまま残さず、`initiative` / `epic` / `issue` の numeric import すべてに fail-closed で適用する。
  - unresolved repo scope 下の numeric import corrective は provider implementation、dogfooding mirror、回帰 tests を同時に更新し、partial fix を残さない。
  - `iss-00040` は evidence prerequisite として `iss-00038/deps.json` と generated deps graph にも反映し、ownership 再取得ではないことを明記する。
  - S07 の generated deps/status verification は `spec-dock/.agent/index-all.json` を authority とし、generated prerequisite evidence は top-level `deps.issue_edges` edge list を正本として扱う。per-node `nodes.<id>.deps` は readiness projection であり、closed issue の prerequisite edge を保持しない場合があるため、`todo_total: 0` 時の active-only projection 空状態と同様に edge authority とは混同しない。
  - epic close を主張する前に、GitHub issue state、`sync --github` 後の generated state、`epic-00033/report.md`、`iss-00038/report.md` が定義済み authority order に従って同じ結論へ収束する reconciliation path を定義する。
  - branch-diff review に使う corrective report/update は committed history から再現できることを保証し、working-tree-only evidence を最終 artifact に残さない。
  - S09 の execution evidence だけでは close claim を完了扱いにせず、S10 upstream evidence normalization と S11 fresh final rereview closure を close-out 必須経路として実行し、normalized artifact set を参照する committed artifact が揃うまで close claim を保留する。
  - S13 実施後は、`report.md` に reviewer-recorded な RG1 docs/evidence review と QG1 close-out review を残し、その後に committed S100 post-S14 final diff review quality gate record で terminal close claim を閉じる。
  - `epic-00033/report.md` の `#33` state は本文・例外メモ・generated state・`iss-00038/report.md` で同じ authority conclusion に揃える。
  - `iss-00040/report.md` を触る場合は report-artifact normalization のみとし、runtime/test/implementation の re-execution を要求しない。
  - S10 で `iss-00040/report.md` を正規化する場合、authoritative citation layer / front matter / final summary note だけを対象にし、historical session-log の `コミット: なし` entry が時点事実を表す限り書き換えない。
- MUST NOT:
  - `iss-00040` が owner である wrappers / domain / dogfooding parity / final regression を再実行前提で抱え込まない。
  - runtime contract の realignment を、この issue の close-out のために再度変更しない。
  - `initiative` / `epic` numeric import の fail-closed guard だけを超えて import contract 全体を再設計しない。
  - test expectation realignment を広く再開しない。許可するのは S12 で是正した `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` に対する canonical guidance tests の stale expectation 修正だけとする。
  - docs parity を provider-side だけで閉じない。
  - targeted docs list の parity/no-op だけで AC-001 を満たした扱いにしない。
  - final close-out record に、実際の commit 済み状態や approved 状態と矛盾する暫定表記を残さない。
  - generated state や GitHub status が open のままなのに、epic report だけを先行して `Pass` / closed 相当に更新しない。
  - narrative spec にだけ dependency を残し、`deps.json` / generated deps graph と不一致のままにしない。
  - committed branch diff review を前提にした gate で、working-tree-only corrective evidence を使わない。
  - `iss-00040/report.md` の normalization を理由に `iss-00040` の implementation / regression ownership を reopen しない。
- OUT OF SCOPE:
  - create / naming / sync / migration contract の中核実装変更
  - stale-contract cluster の再調査や full regression の再所有
  - `iss-00040` 完了済み evidence の差し替え
  - targeted docs list 外で見つかった stale old-contract assumption の ad hoc 修正

## 境界
- Always:
  - `iss-00038` は docs close-out owner であり、`iss-00040` の final regression evidence を参照して閉じる。
  - lifecycle close authority order は、1) GitHub issue state、2) `sync --github` 後の generated state、3) `epic-00033/report.md`、4) `iss-00038/report.md` の順とし、後段は前段を mirror する。
  - `approved` は artifact quality verdict を表し、epic lifecycle close とは別に status reconciliation を要する。
  - targeted docs list の評価は provider-side source of truth と checked-in dogfooding docs の両方で行う。
  - close evidence は docs review結果、`validate` / `sync` の実行結果、final spec review record の 3 本柱で残す。
  - S01 の step approval は `report.md` 上で reviewer / verdict / 観測コマンドまたは観測 artifact / 非重複確認先を追跡できる形で残す。
  - upstream issue report の記述と generated state / epic report が衝突する場合は、`spec-dock/.agent/index-all.json` と `spec-dock/active/epic/report.md` を close status の優先正本とする。
  - `spec-dock/dashboard.md` が `todo_total: 0` を返した後は、`spec-dock/.agent/index.json` / `spec-dock/.agent/deps-issues.json` の空状態は active-only projection の仕様内であり、S07/S09 の否定 evidence には使わない。`spec-dock/.agent/index-all.json` では top-level `deps.issue_edges` を prerequisite edge の正本、per-node `nodes.<id>.deps` を readiness projection として読み分ける。
  - S09 は status reconciliation execution evidence step であり、fresh final rereview closure は後続 corrective step で committed record 化する。
  - S10 が `epic-00033/report.md` または `iss-00040/report.md` の rereview input を更新した後は、`epic-00033/report.md` / normalized `iss-00040/report.md` / `iss-00038/report.md` / generated state / deps graph から成る normalized artifact set に対して、epic-level committed rereview を再度 `pass` させてから close judgement へ進む。
  - final exit を主張する committed branch diff では、S100 post-S14 final diff review quality gate の reviewer / verdict / referenced evidence を `report.md` から追えなければならない。
  - S100 の report sync が gate record 自体を committed artifact 化するだけで、reviewed runtime/docs/tests scope を増やさない場合は、`report.md` に `reviewed_scope_anchor` と `record_sync_commit` を分けて記録してよい。後続の report-only sync commit は、その diff が `report.md` の S100 bookkeeping に限定される限り、`reviewed_scope_anchor` を更新しなくてよい。
  - 最新 authoritative S100 record が当該 commit 自身に載る場合は、`current_authoritative_record: self` を使ってよい。この `self` は「この S100 entry を含む current HEAD commit」を意味し、明示列挙が必要なのは prior `record_sync_commit` のみとする。
  - `iss-00040/report.md` と `epic-00033/report.md` の更新が必要な場合でも、扱うのは report-artifact normalization だけであり、implementation 完了判定そのものは再実行しない。
- Ask:
  - targeted docs list 以外に old contract assumption が見つかった場合は、その場で scope を広げず、`report.md` に blocker として記録して reviewer 判断へ escalate する。
- Never:
  - `iss-00040` が閉じた scope を再び `iss-00038` に混ぜて完了条件を曖昧にする。
  - upstream evidence が欠けたまま narrative だけで epic close を宣言する。
  - targeted docs list 外で見つけた stale assumption を S02 の途中で ad hoc に修正対象へ追加する。

## 非交渉制約
- final spec review verdict は `pass` を要求する。
  - final spec review record には `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence 参照を含める。
  - `validate` / `sync` は current repo state に対して exit=0 を示す。
  - 新たに uppercase path を増やさない。
  - epic close readiness を宣言するには、epic report / issue report / generated state / dependency graph が branch diff review 上で矛盾しないことを要求する。
  - PR review corrective 完了には、README walkthrough wording と numeric import fail-closed contract の両方が fresh spec review で `pass` になることを要求する。

## 前提
- `iss-00040` は完了済みで、stale-contract / final regression / dogfooding parity evidence はその report に集約されている。
- `epic-00033/report.md` は「残りは `iss-00038` のみ」という進捗認識を正本としている。
- 現時点の targeted docs list は provider/dogfooding 間で一致しているため、docs 作業は no-op diff で閉じる可能性がある。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - targeted docs list を確認する
  - When:
    - provider-side と dogfooding 側の 6 ファイルを current contract 観点でレビューし、6 ファイル個別の確認結果を evidence 化する
  - Then:
    - old local-only / sequential / index assumption が残っていないことを、6 ファイル個別の current contract verification evidence で示せる
    - 差分が必要なら provider-side と dogfooding 側の両方で更新される
    - 差分が不要なら no-op であることに加えて、parity だけではなく current contract review 済みであることが close evidence として説明される
    - original six-file targeted docs slice の no-op conclusion と、later final-rereview で見つかった `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の rules/docs-authority corrective が区別して記録される
    - S12 corrective 後に canonical guidance tests の期待値が stale だった場合は、docs contract rollback ではなく test expectation realignment で閉じたことが追える
  - 観測点:
    - targeted docs diff または no-op parity evidence
    - 6 ファイル個別の current contract verification evidence（path / parity 結果 / old assumption 不在確認を含む）
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - docs close-out 候補が揃っている
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する
  - Then:
    - 両コマンドが exit=0 で成功し、current repo state と generated state が close-out 可能であることを示せる
  - 観測点:
    - command outputs
    - `spec-dock/.agent/index-all.json` を正本とした generated state review
    - `spec-dock/dashboard.md` と active-only projection（存在する場合）の整合
- AC-003:
  - Actor:
    - spec reviewer
  - Given:
    - docs evidence、command evidence、upstream issue evidence が揃っている
  - When:
    - final spec review record を確認する
  - Then:
    - verdict が `pass` である
    - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence 参照が追える
    - `iss-00038` と `iss-00040` の non-overlap が明記されている
    - `report.md` の front matter 状態値と S04 のコミット記録が、最終的な approved 状態と実 commit に整合している
    - fresh final rereview の reviewer / verdict / 参照した normalized upstream evidence が committed record として追える
  - 観測点:
    - final spec review record
- AC-004:
  - Actor:
    - epic maintainer / spec reviewer
  - Given:
    - `iss-00038` の close-out evidence と corrective findings が揃っている
  - When:
    - `git diff main...HEAD` を epic completion review として確認する
  - Then:
    - `epic-00033/report.md` の `E-AC-005` / remaining-open summary、`iss-00038/deps.json`、generated state、`iss-00038/report.md` の corrective commit trail が矛盾しない
    - epic close を主張するなら、その authority reconciliation が branch diff 上で追える
    - `epic-00033/report.md` の `#33` state 記述が本文・例外メモ・generated state と矛盾しない
    - S10 で更新した `epic-00033/report.md` と normalized `iss-00040/report.md` を含む normalized artifact set に対して、epic-level committed rereview が `pass` である
  - 観測点:
    - GitHub issue state
    - `sync --github` 実行ログ
    - `epic-00033/report.md`
    - normalized `iss-00040/report.md`
    - `iss-00038/deps.json`
    - deps graph evidence（`spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` を正本とし、`spec-dock/.agent/deps-issues.json` などは補助観測点）
    - `spec-dock/.agent/index-all.json`
    - active-only projection（`spec-dock/.agent/index.json` など）は補助観測点として扱う
    - `spec-dock/dashboard.md`
    - `iss-00038/report.md`
- AC-005:
  - Actor:
    - maintainer / spec reviewer
  - Given:
    - PR #41 の external review で README walkthrough guidance と numeric import repo-scope guard の corrective scope が定義されている
  - When:
    - corrective docs/code/tests を反映し、fresh spec review で merge 前の妥当性を確認する
  - Then:
    - `README.md` の逐次 walkthrough example が parent reference を exact node id で一貫して示し、current create contract の誤読を招かない
    - numeric GitHub import は `initiative` / `epic` / `issue` のいずれでも、explicit repo scope なしで current repo scope を解決できない場合は fail-fast し、unscoped linkage metadata を書き込まない
    - provider implementation / dogfooding mirror / regression tests / issue report が corrective outcome と一致している
    - fresh spec reviewer の verdict が `pass` である
  - 観測点:
    - `README.md`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`
    - `spec-dock/scripts/spec_dock_runtime/application/import_node.py`
    - `tests/cli_runtime/test_import.py`
    - 必要なら `tests/cli_runtime/test_runtime_import_s10.py`
    - corrective review record

## 例外・エッジケース
- EC-001:
  - 条件:
    - targeted docs list がすでに完全一致で、内容変更が不要
  - 期待:
    - docs close-out は no-op でよいが、parity evidence だけでは足りず、6 ファイル個別の current contract review 結果を記録しなければ close にしない
  - 観測点:
    - `diff -q` 相当の parity evidence
    - 6 ファイル個別の current contract verification evidence
- EC-002:
  - 条件:
    - `validate` / `sync` は成功するが、dashboard や index snapshot の open/ready 認識が epic report と整合しない
  - 期待:
    - `spec-dock/.agent/index-all.json` を正本として close-out を停止するかを判定し、generated state drift を切り分ける
    - `spec-dock/dashboard.md` が `todo_total: 0` のとき、active-only projection の空状態だけでは drift 扱いにしない
  - 観測点:
    - command outputs
    - generated state review
- EC-003:
  - 条件:
    - upstream issue evidence の参照先が不足している、upstream report に provisional marker が残っている、または final spec review で ownership conflict が再発する
  - 期待:
    - `iss-00038` 単独で強行 close せず、欠落 evidence / provisional marker / ownership 競合を docs に明記して reviewer 判断を待つ
  - 観測点:
    - review feedback
    - evidence index
- EC-004:
  - 条件:
    - final spec review record 自体は揃っているが、`report.md` に暫定表記や状態不整合が残っている
  - 期待:
    - close-out は未完了とし、front matter とコミット記録を最終状態へ正規化してから受け入れ判定へ進む
  - 観測点:
    - `report.md` front matter
    - S04 close-out 記録
- EC-005:
  - 条件:
    - issue docs は `approved/pass` だが、epic report や generated state がなお `open/partial` を返している
  - 期待:
    - authority mismatch を残したまま epic close を宣言せず、status reconciliation step を実行してから最終判定へ進む
  - 観測点:
    - `epic-00033/report.md`
    - `spec-dock/.agent/index*.json`
    - `spec-dock/dashboard.md`
- EC-006:
  - 条件:
    - narrative spec では `iss-00040` prerequisite を要求しているが、`deps.json` や generated deps graph に edge が無い
  - 期待:
    - dependency graph を spec に合わせて正規化するか、spec 側の prerequisite 表現を修正するまで epic review を pass にしない。generated edge の有無は `spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` で判定し、per-node `nodes.<id>.deps` は readiness projection として補助的に扱う
  - 観測点:
    - `iss-00038/deps.json`
    - `spec-dock/.agent/index-all.json`
    - `spec-dock/.agent/deps-issues.json`（`todo_total: 0` で空の場合は参考値）
    - `epic-00033/plan.md`
- EC-007:
  - 条件:
    - S09 execution evidence は記録済みだが、fresh final rereview の reviewer / verdict / commit-backed closure record が未記録
  - 期待:
    - S09 を close 完了扱いにせず、upstream evidence normalization 後に final committed rereview closure step を実施する
  - 観測点:
    - `iss-00038/report.md`
    - latest rereview record
- EC-008:
  - 条件:
    - `epic-00033/report.md` または `iss-00040/report.md` に provisional / conflicting status marker が残る
  - 期待:
    - report-artifact normalization だけを行い、implementation/test rerun に広げない
  - 観測点:
    - `epic-00033/report.md`
    - `iss-00040/report.md`
- EC-009:
  - 条件:
    - S12 で current docs contract を是正した後、canonical guidance tests が旧 `--no-github` wording を期待して fail する
  - 期待:
    - docs を旧 contract へ戻さず、current shipped guidance を正本として tests だけを最小 realignment する
  - 観測点:
    - `tests/cli_runtime/test_wrappers.py`
    - `tests/test_init_update.py`

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - targeted docs parity evidence
    - `validate` / `sync` の成功結果
    - `iss-00040/report.md` を含む upstream close evidence
  - Output:
    - `E-AC-005` docs/spec-review slice を閉じる final spec review record

## 用語（ドメイン語彙）
- TERM-001:
  - targeted docs list:
    - provider-side と dogfooding 側の `reference_github.md` / `reference_naming.md` / `reference_sync.md`
- TERM-002:
  - final spec review record:
    - final verdict、参照 evidence、non-overlap check を束ねた close-out 記録
- TERM-003:
  - docs close-out owner:
    - `iss-00040` の regression ownership を再実行せず、docs parity と spec review の最後の slice だけを閉じる責務

## 未確定事項
- なし:
  - split 後の ownership boundary は epic plan / epic report / `iss-00040` report で確定している
