# 060-disc-pr29-r39-legacy-unscoped-persistence-gap-analysis

## metadata
- kind: discussion
- id: `060-disc-pr29-r39-legacy-unscoped-persistence-gap-analysis`
- issue: `issue-28-runtime-regression-bugs`
- scope: `S03O contract cleanup after legacy persistence gap review`
- related_review:
  - `P2 Preserve current-repo scope backfill for legacy unscoped links`
- related_files:
  - `spec-deps/current/plan.md`
  - `spec-deps/current/report.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/status.py`
- status: `accepted`

## facts

- 現行 runtime では legacy unscoped current-repo linkage を後から永続化 upgrade する live path がほぼ存在しない
- bulk `sync --github` から sync-time backfill path を除去したため、origin がある間の一時的 current-repo 解決はできても、metadata 自体には `github.repo_owner/name` が残らない
- `current_repo_slug` を失うと、URL target / exact repo-scoped resolution / status hydration は legacy unscoped node を current repo として扱えず、`No node found` / `unknown` へ戻りうる
- これは事実として review 指摘どおりであり、S03O が automatic self-heal を提供していないことの観測可能な副作用である

## analysis

- review は妥当である
- ただし、これを current corrective scope の中で bulk `sync --github` 自動 backfill として戻すのは unsafe である
- `current_repo_slug`、issue-number uniqueness、current repo `issue_index()` だけでは lone unscoped legacy node の current repo 所属を positive に証明できず、S03N で止めた silent mis-normalization を再導入する
- したがって current scope で採るべき最小修正は、S03O / plan / report の stale wording を落とし、「legacy unscoped current-repo links の persistence upgrade は current scope では未解決、manual remediation が必要」と正本へ揃えること

## options

| option | summary | pros | cons | verdict |
| --- | --- | --- | --- | --- |
| A | S03O を維持し、stale plan/docs を cleanup する | 安全性が高く current code/test と整合する | existing legacy repo の operability gap は残る | 採用 |
| B | bulk `sync --github` に safe trusted evidence model を新設して self-heal を戻す | automatic persistence upgrade を回復できる | 現時点の evidence model では unsafe | 却下 |
| C | bulk sync 以外の explicit opt-in write surface へ persistence upgrade を移す | 安全性と救済のバランスが良い | command/UX 追加が必要 | 将来候補 |
| D | manual remediation command/flow を新設する | 最も安全に existing repo を救済しやすい | current corrective scope を超える | 長期推奨 |

## decision

- current corrective scope は `A`
- `S03O` は docs/plan/report を final contract に揃える
- long-term follow-up は `D` を推奨する
  - exact selector 必須
  - bare numeric は ambiguous 時に拒否
  - `current_repo_slug` 必須
  - dry-run 先行
  - 更新対象は `github.issue_number` があり `repo_owner/name` が両方 absent の node に限定
  - bulk `sync --github` は引き続き non-mutating
