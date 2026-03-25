---
種別: discussion
ID: "061"
タイトル: "issue-28 manual rerun contract plan after corrective scopes"
状態: "open"
作成者: "Codex CLI"
作成日: "2026-03-24"
関連: ["design.md", "plan.md", "report.md", "manual-tests/README.md", "055-disc-manual-test-round-20260324-s04k-repo-scope-plan.md", "056-disc-manual-test-findings-root-cause-analysis.md"]
---

# issue-28 manual rerun contract plan after corrective scopes

## 目的
- 前回の exploratory manual round で見つかった main blocker と、その後の corrective scope `S03L` / `S03M` / `S03N` / `S03O` / `S04K` / `S05J` / `S05K` が、現在の contract どおりに動くかを再確認する
- exploratory round を再演するのではなく、「最近の修正で変わった契約だけを再確認する contract rerun」として設計し、判定を明確にする
- provider-side runtime と checked-in dogfooding runtime の両方で、same fixture を使った regression confirmation を残す

## スコープ
- current-origin live workspace での exact repo-scoped resolution baseline
- no-origin copy での `already-normalized metadata` continuity
- lone unscoped legacy current-repo link の `no-backfill / manual remediation` contract
- stale active manifest/path recovery
- readonly `.meta.json` に対する non-mutation / warning surface non-regression
- checked-in runtime parity smoke
- 複数 initiative / epic / issue / dependency を跨ぐ long-run operator session
- GitHub close / reopen / edit / new issue churn の反映確認

## 非スコープ
- exploratory long-run session の再演
- 新しい provider 実装の追加修正
- manual remediation command の新設
- distributed filesystem / concurrent operator 実験

## 必要な GitHub repositories

### current repo role
- repository name:
  - `spec-dock-manual-current-issue-28-rr1`
- 用途:
  - live workspace 自身の `origin`
  - same-repo canonical URL / `--id` / `sync --github` / `deps check` / `active set` baseline
  - no-origin copy の source fixture

### foreign repo role
- repository name:
  - `spec-dock-manual-foreign-issue-28-rr1`
- 用途:
  - foreign overlap fixture
  - scoped URL / scoped deps / exact repo-scope fail-closed の確認

## repo provisioning 前提
- 2 repo とも空 repository でよい
- `git push` と `gh issue create/view/edit/close/reopen` ができること
- current / foreign の両 repo に少なくとも `#1` から `#4` の same-number fixture を作れること
- 追加 repo は不要
  - no-origin copy
  - stale active recovery clone
  - readonly meta case
  - checked-in parity case
  はすべて local 派生で再現する

## 推奨 fixture map
- `#1`
  - overlap baseline
  - current canonical URL / foreign canonical URL / `--id` / `sync --github` の主確認
- `#2`
  - legacy unscoped negative case
  - current repo issue を一度 unscoped 化し、`sync --github` が自動 backfill しないことを確認
- `#3`
  - churn case
  - close / reopen / edit を入れて freshness を確認
- `#4`
  - spare / recovery 補助

## 推奨 local/live corpus size
- initiatives:
  - 2
- epics:
  - 4 以上
- issues:
  - 10 以上
- minimum composition:
  - normalized current-repo linked issue 2 件以上
  - foreign scoped issue 2 件以上
  - legacy unscoped negative case 1 件
  - local-only issue 2 件以上
  - dependency を持つ epic 1 件以上
  - dependency を持つ issue 3 件以上

## ローカル workspace topology
- live current-origin workspace:
  - `manual-tests/workspaces/issue-28-contract-rerun-2026-03-24/trial-gh-current-rr1/`
- no-origin copy:
  - `manual-tests/workspaces/issue-28-contract-rerun-2026-03-24/trial-no-origin-rr1/`
  - `trial-gh-current-rr1/` を複製し、`origin` を除去する
- stale-active recovery clone:
  - `manual-tests/workspaces/issue-28-contract-rerun-2026-03-24/trial-recovery-rr1/`
  - `trial-no-origin-rr1/` から派生
- checked-in parity clone:
  - `manual-tests/workspaces/issue-28-contract-rerun-2026-03-24/trial-checkedin-rr1/`
  - current repo fixture をそのまま使い、checked-in runtime executable path で smoke する
- report root:
  - `manual-tests/reports/2026-03-24-issue-28-contract-rerun/`

## 必須 artifacts
- `checklist.md`
  - build under test
  - provider / checked-in runtime mode
  - GitHub repo URL
  - overlap fixture URL map
  - workspace lineage
  - known-open / out-of-scope note
  - case order
  - pass criteria
- `execution-log.md`
  - timestamp
  - case id
  - command
  - expected
  - actual
  - verdict
  - evidence path
  - issue URL / node id
  - `.meta.json` before/after summary
  - active entrypoint / `context-pack.md` before/after summary
  - provider or checked-in marker
- `summary.md`
  - overall verdict
  - current-origin exact resolution
  - no-origin continuity for normalized metadata
  - lone-unscoped no-backfill / fail-closed guard
  - checked-in parity
  - stale active recovery
  - readonly non-mutation
  - findings
  - residual risks
  - skipped / blocked
  - next actions

## ケース一覧

### RR-00 preflight and fixture seed
- 目的:
  - build under test、provider / checked-in parity、repo URL、issue fixture を固定する

### RR-01 current-origin overlap baseline
- 目的:
  - current-origin workspace で same-number current/foreign coexistence 下の exact repo-scoped resolution を確認する
- 最低確認:
  - `sync --github`
  - `deps check <current canonical url>`
  - `deps check <foreign canonical url>`
  - scoped dependency ref を 1 件追加し、`owner/repo#<n>` または equivalent canonical scoped ref が foreign target を正しく指すこと
  - `active set <current canonical url>`
  - `active set --id <current node id>`
  - bare numeric / `--github-issue` overlap fail-closed
  - bare numeric dependency ref が current-repo-only shorthand として fail-closed を維持すること

### RR-02 no-origin copy continuation
- 目的:
  - `already-normalized metadata` は no-origin でも continuity を保ち、legacy lone-unscoped current-repo link は automatic self-heal しないことを確認する
- 最低確認:
  - positive:
    - normalized current-repo node の `sync --github` / `validate` / `doctor`
    - normalized current-repo node の `deps check <current canonical url>`
    - canonical URL / `--id` exact resolution
  - negative:
    - legacy unscoped current-repo node を manual で作り、`sync --github` 後も `.meta.json` が unscoped のまま
    - no-origin で canonical URL が `No node found` または equivalent fail-closed に戻る

### RR-03 checked-in parity smoke
- 目的:
  - checked-in runtime executable path でも RR-01 / RR-02 の core contract が崩れていないことを確認する
- 最低確認:
  - `validate`
  - `doctor`
  - `sync --github`
  - `deps check <current canonical url>` continuity 1 件
  - exact URL target 1 件
  - scoped dependency ref または bare numeric dependency ref guard のどちらか 1 件

### RR-04 stale active recovery
- 目的:
  - stale manifest / stale `.path` / healthy entrypoint precedence の current contract を確認する
- 最低確認:
  - id-based recovery
  - placeholder fallback
  - healthy entrypoint wins
  - destructive overwrite をしないこと

### RR-05 readonly meta non-mutation
- 目的:
  - lone unscoped legacy current-repo case で readonly `.meta.json` を不用意に mutate しないこと、不要 warning を増やさないことを確認する

### RR-06 summary and residue check
- 目的:
  - verdict を contract ごとに分類し、known-open と次アクションを整理する

### RR-07 organic stress session
- 目的:
  - 実運用に近い長時間の複合操作で、current-origin / foreign overlap / no-origin / recovery / parity が連鎖しても想定どおりに動くかを確認する
- 最低確認:
  - phase A build-up:
    - 2 initiatives、4 epics、10 以上の issues を使って current/local/foreign を混在させる
    - dependency を epic と issue の両方へ追加する
  - phase B churn:
    - current / foreign の GitHub issue に対して close / reopen / edit / new を入れる
    - `sync --github` 後の freshness / readiness / exact target resolution を確認する
  - phase C continuation:
    - current-origin workspace を no-origin copy へ引き継ぐ
    - normalized current-repo nodes は continuity を維持し、legacy lone-unscoped は no-backfill / manual remediation 契約どおり fail-closed に残ることを確認する
    - stale active recovery と checked-in parity smoke を再サンプルする
  - checkpoints:
    - 各 phase の終わりに `validate` / `doctor` / `active show`
    - `context-pack.md` と active entrypoint の整合
    - failing behavior は expected fail-closed か unexpected regression かを明示する

## 完了条件
- `RR-00` から `RR-06` まで verdict がある
- `RR-07` の 3 phase と checkpoint に verdict がある
- current-origin exact resolution baseline に unexplained drift がない
- `already-normalized metadata` の no-origin continuity evidence がある
- legacy lone-unscoped current-repo link が no-backfill / manual remediation contract どおりに記録されている
- stale active recovery と readonly non-mutation に unexplained drift がない
- provider / checked-in parity smoke に unexplained drift がない
- multi-initiative / multi-epic / multi-issue / dependency churn の長時間 session に unexplained drift がない

## この plan が強い理由
- exploratory round ではなく recent fixes の contract だけを直接叩くため、判定が明確
- positive path と negative guard の両方を同じ fixture で確認できる
- current-origin -> no-origin -> checked-in parity の流れで、workspace lineage を崩さず確認できる
- `S03O` 後の重要な注意点である「legacy lone-unscoped current-repo link は self-heal しない」を expected behavior として明文化できる
