---
種別: discussion
ID: "055"
タイトル: "issue-28 manual test round plan for repo-scope, active recovery, and exploratory churn"
状態: "open"
作成者: "Codex CLI"
作成日: "2026-03-24"
関連: ["design.md", "plan.md", "report.md", "manual-tests/README.md"]
---

# issue-28 manual test round plan for repo-scope, active recovery, and exploratory churn

## 目的
- `S04K persisted active path trust boundary` と `S05J repo-scoped exact target resolution` 周辺を、実運用に近い live / copied workspace 条件で再確認する。
- GitHub review で追加観測された `origin` なし環境、same-repo / foreign-repo coexistence、stale active path recovery の 3 つを同じ round で切り分ける。
- 通常の一般操作に加えて、複数 initiative / epic / issue、close / reopen、dependency churn、copy / update / resume を含む長時間の探索的 manual testing に引き上げる。
- 実施前に checklist / workspace / report root を固定し、手動テストの抜け漏れを減らす。

## スコープ
- fresh local workspace での multi-resource baseline create / validate / doctor / local-only deps / active
- `origin` を持つ same-repo live workspace での canonical URL / numeric / explicit target / sync / freshness 検証
- foreign repo issue を混在させた import / deps / active / sync / close-reopen churn 検証
- `origin` を外した copied workspace での canonical URL target と unscoped linked node の解決検証
- stale active manifest path、mixed entrypoint、`.path` parity を含む `spec-dock update` recovery 検証
- 長時間の organic session での multi-initiative / multi-epic / multi-issue / dependency churn / resume-after-copy-update 検証

## 非スコープ
- provider 実装の追加修正
- GitHub 以外の forge host
- CI / distributed filesystem / concurrent operator の lock 実験

## 必要な GitHub repository

### current repo role
- repository name:
  - `spec-dock-manual-current-issue-28-20260324`
- repository url:
  - `https://github.com/chemitaro/spec-dock-manual-current-issue-28-20260324`
- 用途:
  - manual workspace 自身の `origin`
  - same-repo issue 作成、same-repo canonical URL import、current-repo scoped resolution の確認

### foreign repo role
- repository name:
  - `spec-dock-manual-foreign-issue-28-20260324`
- repository url:
  - `https://github.com/chemitaro/spec-dock-manual-foreign-issue-28-20260324`
- 用途:
  - foreign canonical URL import
  - foreign scoped dependency ref
  - same-number coexistence 時の exact repo scope 確認

## 必要条件
- どちらも空 repository でよい
- 現在の認証で `git push` と `gh issue create/view/edit/close/reopen` ができる
- manual test 実施時点で URL が確定している
- no-origin case は `current repo role` workspace を copy して `origin` を外すだけなので、追加 repo は不要
- overlap fixture として、current repo role / foreign repo role の両方に同番号 issue を少なくとも 4 組作る
  - 推奨: current `#1` から `#4`、foreign `#1` から `#4`
  - `MT-02` / `MT-03` / `MT-05` はこの same-number pair を共通 fixture として再利用する
- churn fixture として、current / foreign の両 repo に追加 issue を少なくとも 2 件ずつ作る
  - 推奨: current `#5` / `#6`、foreign `#5` / `#6`
  - 少なくとも 1 件は close / reopen を session 中に行う
- local corpus は少なくとも 2 initiatives、4 epics、10 issues を作る
  - issue だけでなく epic にも dependency を登録する

## 手動テスト環境
- local baseline workspace:
  - `manual-tests/workspaces/issue-28-manual-round-2026-03-24/trial-local-2026-03-24/`
- mixed live current-origin workspace:
  - `manual-tests/workspaces/issue-28-manual-round-2026-03-24/trial-gh-current-2026-03-24/`
  - `origin` は current repo role を向ける
  - foreign repo role URL もこの workspace から扱い、`MT-00` の fixture seed と `MT-02` から `MT-04` を実施する
- no-origin copied workspace:
  - `manual-tests/workspaces/issue-28-manual-round-2026-03-24/trial-no-origin-2026-03-24/`
  - `trial-gh-current-2026-03-24/` を複製し、`git remote remove origin` 後に `MT-05` から `MT-07` を継続する
- pathfile parity sub-workspace:
  - `manual-tests/workspaces/issue-28-manual-round-2026-03-24/trial-no-origin-pathfile-2026-03-24/`
  - `trial-no-origin-2026-03-24/` を複製し、active entrypoint write 時だけ `os.symlink` を失敗させる helper launcher 経由で `MT-06` の `.path` fallback evidence を採る
  - helper launcher は `manual-tests/tools/issue-28-manual-round-2026-03-24/` 配下に置き、`tests/test_init_update.py` の active symlink failure seam と同じ考え方で `OSError` を再現する
- report root:
  - `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/`

## report artifact contract
- checklist:
  - path: `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/checklist.md`
  - required fields:
    - scope / references / branch / workspace map / GitHub repo URL
    - overlap fixture IDs and reused issue URLs
    - churn fixture IDs and intended close/reopen targets
    - case order with initial status
    - operator / time window / phase goal / resume point
    - completion criteria
    - `.path` fallback helper launcher invocation note
- execution log:
  - path: `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/execution-log.md`
  - required fields:
    - timestamp / case / precondition / command / expected / actual / diff / verdict / evidence
    - checks / side effects / touched ids-urls / invariants / anomaly-hypothesis / checkpoint
- summary:
  - path: `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/summary.md`
  - required fields:
    - overall verdict / findings / residual risks / skipped-or-blocked / next actions
- S98 pass condition:
  - 上記 3 artifact が skeleton として存在し、checklist に workspace map・repo URL 欄・overlap/churn fixture 欄・`.path` launcher 欄が初期化されている

## ケース一覧

### MT-00 tool parity and fixture seed
- 目的:
  - provider runtime / generated runtime / command surface を preflight で確認し、GitHub current/foreign repo に live corpus を seed する。

### MT-01 local corpus build
- 目的:
  - fresh local workspace で 2 initiatives、4 epics、10 issues 前後を作り、discussion churn、dependency baseline、active 切替を確認する。

### MT-02 current-repo live matrix
- 目的:
  - current repo role workspace で same-repo canonical URL import、numeric、explicit target、`sync --github`、status/readiness、`active set`、`deps check` を一式で確認する。

### MT-03 foreign overlap and scoped refs
- 目的:
  - same-number current/foreign を混在させ、bare numeric、`owner/repo#n`、canonical URL、`--id`、`--github-issue` の success / fail-closed と sync/freshness を確認する。

### MT-04 live churn and freshness
- 目的:
  - GitHub 側で close / reopen / edit / new issue を挟み、`sync --github`、status/readiness、`active set`、`deps check` が freshness を保つことを確認する。

### MT-05 no-origin continuation
- 目的:
  - `origin` を持たない copied workspace で、workspace B から引き継いだ overlap fixture と churn state を使い、canonical GitHub URL target が URL 自体の repo identity を使って unique linked node を解決できるかを確認する。

### MT-06 recovery submatrix
- 目的:
  - stale manifest / wrong-id path / broken manifest / healthy entrypoint wins / mixed real-placeholder / plain-file conflict / invalid-dir conflict / repeated update を matrix で確認する。

### MT-07 organic long-run operator session
- 目的:
  - local-current-foreign-no-origin を往復し、build-up / churn / resume-after-copy-update の 3 phase と checkpoint を持つ 25-40 操作程度の長時間 session を実施する。
- 実施方法:
  - phase A build-up:
    - local corpus を拡張し、initiative / epic / issue / discussion / dependency を増やす
  - phase B churn:
    - GitHub issue close / reopen / import / explicit target / sync を挟む
  - phase C resume-after-copy-update:
    - no-origin copy、`spec-dock update`、active recovery、`.path` parity を挟んで再開する
  - each checkpoint:
    - `validate`
    - `doctor`
    - `active show`
    - `context-pack.md` 整合

### MT-08 summary and residue check
- 目的:
  - finding を `identity` / `freshness` / `recovery` / `operator-error` / `tooling parity` に分類し、overall verdict、residual risk、rerun 要否を整理する。

## 完了条件
- `MT-00` から `MT-08` まで verdict がある
- `MT-00` では provider / generated runtime の preflight parity と current/foreign repo live corpus seed が記録されている
- `MT-02` / `MT-03` / `MT-05` では `active set <canonical-url>`、`deps check <canonical-url>`、`sync --github`、status/readiness の evidence がある
- `MT-02` / `MT-03` / `MT-05` は current repo `#1` / foreign repo `#1` のような same-number overlap fixture を共通利用している
- `MT-04` では close / reopen / edit / new issue の少なくとも 3 種の churn を実施している
- `MT-06` では id-based recovery、placeholder fallback、healthy entrypoint wins、`.path` parity を含む recovery submatrix がある
- `MT-06` では `context-pack.md` と `spec-dock/active/{initiative,epic,issue}` の一致証跡が symlink / `.path` の両方で残っている
- `MT-07` では 3 checkpoint 付きの organic session が記録され、issue と epic の両方に dependency 登録がある
- `checklist.md` には workspace map / repo URL / overlap fixture / churn fixture / `.path` helper launcher / operator / time window / case order initial status が記録されている
- `execution-log.md` に command / expected / actual / diff / verdict / evidence が残る
- `summary.md` に overall verdict / findings / residual risks / next action が残る
