---
種別: 計画書（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
関連GitHub: ["#33"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
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

## Issue 一覧（順序 / tranche 付き）
- issue-1-github-mandatory-node-creation-contract:
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
- issue-2-timestamp-based-discussion-and-adr-naming:
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
    - issue-1-github-mandatory-node-creation-contract
- issue-3-sync-adr-symlink-mirror:
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
    - issue-2-timestamp-based-discussion-and-adr-naming
- issue-4-migration-guardrails-and-validation-hardening:
  - 目的:
    - issue-1〜3 で先行固定した migration boundary を仕上げとして横断 hardening し、E-AC-004 final closure owner としてクローズする
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
    - issue-1-github-mandatory-node-creation-contract
    - issue-2-timestamp-based-discussion-and-adr-naming
    - issue-3-sync-adr-symlink-mirror
- issue-5-docs-dogfooding-parity-and-final-regression-gate:
  - 目的:
    - provider docs / tests / dogfooding mirror を新 contract に揃え、最終回帰を閉じる
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
    - targeted unittest output（本 epic 変更対象 suite が exit=0）
    - final spec review record（verdict=`pass`、issue-1〜5 の close evidence 参照付き）
  - tranche:
    - tranche-3 / close-out
  - closes:
    - E-RQ-005, E-AC-005
  - depends on:
    - issue-1-github-mandatory-node-creation-contract
    - issue-2-timestamp-based-discussion-and-adr-naming
    - issue-3-sync-adr-symlink-mirror
    - issue-4-migration-guardrails-and-validation-hardening

## 統合チェックポイント
- G1 decomposition review:
  - issue 分解が contract 単位で分かれていることを plan diff で確認できる（E-AC-004 は issue-1/2 の先行ガード + issue-4 final closure owner を明示）
- G2 integration readiness:
  - create / doc / sync / validate / docs parity の依存順が issue depends-on で確認できる
- G3 rollout/docs impact:
  - rebuildable workspace boundary が named docs diff + validate contract tests + migration boundary tests に現れている
- G9 final epic spec review:
  - issue-1〜5 の close evidence が全て参照可能であり、final spec review verdict=`pass` が記録される

## 品質ゲート
- test / observability / migration / docs:
  - gate-1:
    - issue-1 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（create/canonical resolver 関連 suite、exit=0）
    - `origin` 基準 canonical resolver evidence（origin missing / non-GitHub remote / fetch-push mismatch）
    - configured scope mismatch reject evidence
    - cross-repo target reject evidence
    - named docs diff（canonical resolver + migration boundary 明記）
  - gate-2:
    - issue-2 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（doc naming 関連 suite、exit=0）
    - filename grammar tests evidence
    - same-second collision suffix evidence
    - named docs diff（強制互換しない boundary）
    - E-AC-004 clause-1 pre-guard evidence
  - gate-3:
    - issue-3 完了時に以下 artifact が揃い、全て pass であること
    - targeted unittest output（sync mirror 関連 suite、exit=0）
    - clear-then-rebuild test evidence
    - stale symlink 不残存 evidence
    - non-symlink empty-dir warning evidence
  - gate-4:
    - issue-4（E-AC-004 final closure owner）完了時に migration boundary 3条項の clause-by-clause objective evidence が揃い、全て pass であること
    - clause-1: 強制的 backward compatibility 非維持 -> named docs diff に明示記述あり
    - clause-2: `spec-dock update` in-place 自動移行非保証 -> named docs diff + update/validate contract tests（auto-migrate path 非保証）で確認
    - clause-3: 既存 checked-in data 無断破壊を目的にしない -> migration boundary tests（legacy mismatch 時 fail-fast / warning、checked-in data 非書き換え）で確認
    - targeted unittest output（migration/validate 関連 suite、exit=0）
    - `./spec-dock/scripts/spec-dock validate` 実行 evidence（exit=0）
  - gate-5:
    - issue-5 完了時に以下 artifact が揃い、全て pass であること
    - targeted docs list diff（6ファイル）
    - `./spec-dock/scripts/spec-dock validate` 実行 evidence（exit=0）
    - `./spec-dock/scripts/spec-dock sync` 実行 evidence（exit=0）
    - targeted unittest output（epic 対象回帰、exit=0）
    - final spec review record（verdict=`pass`）

## ロールアウト / docs impact
- rollout order:
  - create contract -> doc naming -> sync mirror -> migration guardrails -> docs/tests parity
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
  - 全 acceptance criteria に対して issue-1〜5 の close evidence が 1:1 で対応付けられている
  - E-AC-004 は issue-1/2 の先行ガードを前提に、issue-4（final closure owner）で migration boundary 3条項（強制的 backward compatibility 非維持 / `spec-dock update` in-place 自動移行非保証 / 既存 checked-in data 無断破壊を目的にしない）が clause-by-clause で個別 evidence 化されている
- integration / rollout complete:
  - create / doc / sync / validate / docs parity が新 contract に揃い、各 issue の観測可能 evidence（targeted unittest exit=0、validate exit=0、sync exit=0）で確認できる
- docs impact resolved:
  - `reference_github.md` / `reference_naming.md` / `reference_sync.md`（provider + dogfooding）で old local-only / sequential / index assumptions が除去され、targeted docs list diff で確認できる
  - final spec review verdict は `pass` である

## 依存 / ブロッカー
- D-001:
  - GitHub auth / CLI availability
- D-002:
  - symlink capability

## 未確定事項
- なし:
  - issue 分解と順序は discussion で確定済み
