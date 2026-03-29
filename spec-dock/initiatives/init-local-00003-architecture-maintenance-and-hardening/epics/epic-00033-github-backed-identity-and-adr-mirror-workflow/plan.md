---
種別: 計画書（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
関連GitHub: ["#33"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00033 GitHub backed identity and ADR mirror workflow — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004
  - E-AC-005

## Issue 分割方針
- slicing principle:
  - contract を 1 issue 1 責務で切る
  - `new`、`new doc`、`sync`、migration/validate、docs/tests parity を分離する
- rationale:
  - node identity contract を先に固定しないと、後続の naming / sync / validate が揺れるため

## Issue alias -> actual issue id 対応
- `issue-1-github-mandatory-node-creation-contract` -> `iss-00034`（GitHub #34）
- `issue-2-timestamp-based-discussion-and-adr-naming` -> `iss-00036`（GitHub #36）
- `issue-3-sync-adr-symlink-mirror` -> `iss-00035`（GitHub #35）
- `issue-4-migration-guardrails-and-validation-hardening` -> `iss-00037`（GitHub #37）
- `issue-5-docs-dogfooding-parity-and-final-regression-gate` -> `iss-00038`（GitHub #38）
- `issue-6-sync-fail-closed-hardening-and-test-realignment` -> `iss-00040`（GitHub #40）

## Issue 一覧（順序 / tranche 付き）
- iss-00034:
  - actual issue id:
    - `iss-00034`（GitHub #34）
  - 目的:
    - initiative / epic / issue を GitHub mandatory へ切り替え、local-only path を除去する
  - deliverable:
    - `new` command contract 更新（canonical repo scope は consumer repo の Git remote `origin` が指す GitHub repository を唯一正本として解決）
    - canonical repo scope resolver fully specified 化:
      - `origin` remote 不在は fail-fast（origin missing）
      - non-GitHub remote は fail-fast
      - `origin` fetch/push 両方あり時は GitHub `owner/repo` 正規化で一致必須、不一致は fail-fast（fetch-push mismatch）
      - SSH/HTTPS は同一 `owner/repo` canonical form に正規化して比較
      - `owner` / `repo` は lowercase basis で比較し、`.meta.json` の `repo_owner` / `repo_name` は lowercase canonical basis で保持
    - `configured repo scope` のような追加設定値が存在する場合は `origin` 解決結果との一致を必須化し、不一致は fail-fast validation / create reject
    - `.meta.json` へ `github.issue_number` / `repo_owner` / `repo_name` の repo-scoped linkage persistence
    - 空 workspace / 初回 node を含む create contract tests
    - single GitHub repo scope validation（cross-repo linkage reject）の実装と `origin` 基準 canonical resolver evidence / configured scope mismatch reject evidence / cross-repo target reject evidence
    - E-AC-004 先行ガード（clause-2/3）:
      - 旧 workspace に対して in-place 自動移行を保証しない境界を docs/tests/validate へ先行反映
      - legacy mismatch 時 fail-fast / warning と non-destructive 境界を migration tests に先行反映
    - 関連 docs diff（boundary/canonical scope の明記差分）
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-001, E-RQ-002, E-AC-001
  - contributes to:
    - E-AC-004 clause-2/3 pre-guard
  - depends on:
    - なし
- iss-00036:
  - actual issue id:
    - `iss-00036`（GitHub #36）
  - 目的:
    - discussion / ADR filename を timestamp-prefix naming に切り替える
  - deliverable:
    - `new doc` contract 更新
    - basename grammar 固定: `<ts>-<kind>-<slug>.md`（`ts = yyyymmddthhmmssz`, `kind in {adr, disc}`）
    - 同秒衝突時のみ `yyyymmddthhmmssz-<nn>-<kind>-<slug>.md`（2桁 `nn`）を許可
    - sync 側 filename pattern 前提との整合
    - filename grammar tests と naming validation 更新
    - same-second collision suffix（`-<nn>-`）evidence
    - E-AC-004 先行ガード（clause-1）として、旧 sequential docs を強制互換しない境界を docs/tests/validate で固定（`001-adr...` / `002-adr...` は grandfathered planning artifacts）
    - validate/docs diff
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-003, E-AC-002
  - contributes to:
    - E-AC-004 clause-1 pre-guard
  - depends on:
    - iss-00034
- iss-00035:
  - actual issue id:
    - `iss-00035`（GitHub #35）
  - 目的:
    - `sync` で `spec-dock/adrs/` symlink mirror を全再生成する
  - deliverable:
    - sync mirror clear-then-rebuild 実装と clear-then-rebuild test
    - stale symlink が残らないことの検証 evidence
    - non-symlink 環境で `spec-dock/adrs/` を空の generated directory として残すか再作成し、warning を出しつつ成功扱いにする終状態の固定
    - non-symlink empty-dir warning evidence
    - timestamp grammar pattern 前提の走査 contract を sync 側に反映
    - 関連 tests
  - tranche:
    - tranche-2 / now
  - closes:
    - E-RQ-004, E-AC-003
  - depends on:
    - iss-00036
- iss-00037:
  - actual issue id:
    - `iss-00037`（GitHub #37）
  - 目的:
    - iss-00034/iss-00036/iss-00035 で先行固定した migration boundary を仕上げとして横断 hardening し、E-AC-004 final closure owner としてクローズする
  - deliverable:
    - legacy boundary docs/tests/validate の抜け漏れ解消
    - old workspace 非サポート境界の最終整合
    - clause-1 evidence: 強制的 backward compatibility を維持しない方針が docs/tests/validate で閉じていること
    - clause-2 evidence: `spec-dock update` の in-place 自動移行を保証しない境界が docs/tests/validate で閉じていること
    - clause-3 evidence: 既存 checked-in data の無断破壊を目的にしない境界が docs/tests/validate で閉じていること
    - validate hardening（仕上げ）
    - migration boundary clause-by-clause evidence（3条項個別）
  - tranche:
    - tranche-2 / now
  - closes:
    - E-AC-004
  - depends on:
    - iss-00034
    - iss-00036
    - iss-00035
- iss-00040:
  - actual issue id:
    - `iss-00040`（GitHub #40）
  - 関係:
    - `iss-00038` の全面置換ではない
    - `iss-00038` から wrappers / domain / dogfooding parity / final regression ownership を分割して引き取る split follow-up issue とする
    - non-overlap rule:
      - wrappers / domain / dogfooding parity / final regression の実行責務は `iss-00040` 専属とし、`iss-00038` 側では再実行しない
  - 目的:
    - current contract を正本として stale-contract cluster を realign し、wrappers / domain / dogfooding parity / final regression を閉じる
  - deliverable:
    - `active` / `deps` / `sync` fixture realignment evidence
    - legacy-compat targeted evidence（issue plan の legacy-compat tests 参照）:
      - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_local_only_node_does_not_rename_branch -v`
      - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_without_github_local_issue_without_deps_is_ready -v`
      - `python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing -v`
      - `python -m unittest tests.cli_runtime.test_sync.TestCliSync.test_local_only_issue_is_open_and_ready_without_deps -v`
    - wrappers docs expectation realignment evidence
    - domain validation expectation realignment evidence
    - provider asset と checked-in dogfooding runtime mirror の parity recovery evidence
    - final regression evidence（stale-contract cluster 解消の識別を含む）
  - tranche:
    - tranche-3 / close-out
  - closes:
    - E-AC-005
  - depends on:
    - iss-00034
    - iss-00036
    - iss-00035
    - iss-00037
- iss-00038:
  - actual issue id:
    - `iss-00038`（GitHub #38）
  - 関係:
    - `iss-00040` に wrappers / domain / dogfooding parity / final regression ownership を分割した後の docs close-out owner とする
    - non-overlap rule:
      - 残責務は docs parity + final spec review record のみとし、wrappers/domain/dogfooding parity と final regression 実行は担当しない
  - 目的:
    - provider docs / dogfooding docs を新 contract に揃え、final spec review record を閉じる
  - deliverable:
    - docs parity（provider + dogfooding）
    - 更新対象:
      - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
      - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
      - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
      - `spec-dock/docs/reference_github.md`
      - `spec-dock/docs/reference_naming.md`
      - `spec-dock/docs/reference_sync.md`
    - 更新対象 docs の差分一覧（targeted docs list diff）
    - old local-only / sequential / index assumption 除去を closure evidence として明示
    - `./spec-dock/scripts/spec-dock validate` 実行 evidence（exit=0）
    - `./spec-dock/scripts/spec-dock sync` 実行 evidence（exit=0）
    - final spec review record（verdict=`pass`、iss-00034/iss-00036/iss-00035/iss-00037/iss-00040/iss-00038 の close evidence 参照付き）
  - tranche:
    - tranche-3 / close-out final
  - closes:
    - E-RQ-005
  - contributes to:
    - E-AC-005 docs/spec-review slice
  - depends on:
    - iss-00034
    - iss-00036
    - iss-00035
    - iss-00037
    - iss-00040

## 統合チェックポイント
- G1 decomposition review:
  - issue 分解が contract 単位で分かれていることを plan diff で確認できる（E-AC-004 は iss-00034/iss-00036 の先行ガード + iss-00037 final closure owner を明示）
- G2 integration readiness:
  - create / doc / sync / validate / docs parity / wrappers-domain-parity / final spec review の依存順が issue depends-on で確認できる
- G3 rollout/docs impact:
  - rebuildable workspace boundary が named docs diff + validate contract tests + migration boundary tests に現れている
- G9 final epic spec review:
  - iss-00034/iss-00036/iss-00035/iss-00037/iss-00040/iss-00038 の close evidence が全て参照可能であり、final spec review verdict=`pass` が記録される

## 品質ゲート
- test / observability / migration / docs:
  - gate-1:
    - iss-00034 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（create/canonical resolver 関連 suite、exit=0）
    - `origin` 基準 canonical resolver evidence（origin missing / non-GitHub remote / fetch-push mismatch）
    - configured scope mismatch reject evidence
    - cross-repo target reject evidence
    - named docs diff（canonical resolver + migration boundary 明記）
  - gate-2:
    - iss-00036 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（doc naming 関連 suite、exit=0）
    - filename grammar tests evidence
    - same-second collision suffix evidence
    - named docs diff（強制互換しない boundary）
    - E-AC-004 clause-1 pre-guard evidence
  - gate-3:
    - iss-00035 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（sync mirror 関連 suite、exit=0）
    - clear-then-rebuild test evidence
    - stale symlink 不残存 evidence
    - non-symlink empty-dir warning evidence
  - gate-4:
    - iss-00037（E-AC-004 final closure owner）完了時に migration boundary 3条項の clause-by-clause objective evidence が揃い、全て pass であること
    - clause-1: 強制的 backward compatibility 非維持 -> named docs diff に明示記述あり
    - clause-2: `spec-dock update` in-place 自動移行非保証 -> named docs diff + update/validate contract tests（auto-migrate path 非保証）で確認
    - clause-3: 既存 checked-in data 無断破壊を目的にしない -> migration boundary tests（legacy mismatch 時 fail-fast / warning、checked-in data 非書き換え）で確認
    - targeted unittest output（migration/validate 関連 suite、exit=0）
    - `./spec-dock/scripts/spec-dock validate` 実行 evidence（exit=0）
  - gate-5:
    - iss-00040（`iss-00038` から split された wrappers/domain/dogfooding parity/final regression owner）完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（`active` / `deps` / `sync` current-contract realignment、exit=0）
    - targeted unittest output（`wrappers` / `domain` expectation realignment、exit=0）
    - legacy-compat targeted evidence（issue plan の legacy-compat tests と同一）:
      - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_local_only_node_does_not_rename_branch -v`
      - `python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_without_github_local_issue_without_deps_is_ready -v`
      - `python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing -v`
      - `python -m unittest tests.cli_runtime.test_sync.TestCliSync.test_local_only_issue_is_open_and_ready_without_deps -v`
    - dogfooding runtime parity recovery evidence
    - parity test output（checked-in dogfooding runtime mirror match provider assets、exit=0）
    - final regression evidence（stale-contract cluster 解消の識別を含む）
  - gate-6:
    - iss-00038（docs close-out / final spec review owner）完了時に以下 artifact が揃い、全て pass であること
    - targeted docs list diff（6ファイル）
    - `./spec-dock/scripts/spec-dock validate` 実行 evidence（exit=0）
    - `./spec-dock/scripts/spec-dock sync` 実行 evidence（exit=0）
    - final spec review record（verdict=`pass`、`iss-00040` final regression evidence 参照付き）
    - non-overlap check（`iss-00038` では wrappers/domain/dogfooding parity と final regression を再実行しない）

## ロールアウト / docs impact
- rollout order:
  - create contract -> doc naming -> sync mirror -> migration guardrails -> wrappers/domain/dogfooding parity/final regression -> docs parity -> final spec review
- contract / docs refresh:
  - GitHub mandatory
  - no local-only
  - timestamp naming
  - `adrs/` mirror generated view

## Issue readiness contract
- Issue に要求する最低条件:
  - contract が 1 つに絞られている
  - observable command/test が定義されている
  - old workspace boundary をどう扱うか書かれている

## final exit contract
- E-AC closure:
  - 全 acceptance criteria に対して iss-00034/iss-00036/iss-00035/iss-00037/iss-00040/iss-00038 の close evidence が対応付けられている
  - E-AC-004 は iss-00034/iss-00036 の先行ガードを前提に、iss-00037（final closure owner）で migration boundary 3条項（強制的 backward compatibility 非維持 / `spec-dock update` in-place 自動移行非保証 / 既存 checked-in data 無断破壊を目的にしない）が clause-by-clause で個別 evidence 化されている
  - E-AC-005 は `iss-00038` の全面置換ではなく split follow-up として `iss-00040` が wrappers / domain / dogfooding parity / final regression ownership を引き取り、`iss-00038` は docs close-out と final spec review record を保持する
- integration / rollout complete:
  - create / doc / sync / validate / docs parity / wrappers-domain parity / final regression が新 contract に揃い、各 issue の観測可能 evidence（targeted unittest exit=0、validate exit=0、sync exit=0、parity test exit=0）で確認できる
- docs impact resolved:
  - `reference_github.md` / `reference_naming.md` / `reference_sync.md`（provider + dogfooding）で old local-only / sequential / index assumptions が除去され、targeted docs list diff で確認できる
  - final spec review verdict は `pass` であり、`iss-00040` の final regression evidence を参照している

## 依存 / ブロッカー
- D-001:
  - GitHub auth / CLI availability
- D-002:
  - symlink capability

## 未確定事項
- なし:
  - issue 分解と順序は discussion で確定済み
