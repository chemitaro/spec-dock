---
種別: 要件定義書（Epic）
ID: "epic-00033"
タイトル: "GitHub backed identity and ADR mirror workflow"
関連GitHub: ["#33"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
親: ["init-local-00003"]
---

# epic-00033 GitHub backed identity and ADR mirror workflow — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00003` の architecture hardening として、single GitHub repo 前提の identity contract と ADR workflow を新基盤へ切り替える。
  - `Metric-002` と `Metric-003` の達成に向け、旧 local-only / sequential contract を廃止し、rebuildable workspace 前提で新 contract を成立させる。
- この epic が提供する能力:
  - initiative / epic / issue が GitHub issue mandatory で作成される。
  - discussion / ADR が timestamp-prefix naming で作成される。
  - top-level `spec-dock/adrs/` が sync-generated symlink mirror として維持される。

## 背景・現状
- 現状の挙動:
  - initiative / epic は local-only default、issue は GitHub create default である。
  - discussion / ADR は scope-local sequential naming である。
  - ADR の top-level browse view は存在しない。
- 現状の課題:
  - local sequential id は複数 worktree / 複数 clone で衝突する。
  - discussion / ADR sequential naming は merge 後の duplicate sequence を避けられない。
  - 現在の dogfooding workspace を守る前提だと、強い contract change を入れにくい。
- 方針:
  - 旧 workspace は壊れてよく、再構築して後からデータ移行する。
  - backward compatibility を無理に維持しない。
- 本 epic でサポートしないこと:
  - 旧 workspace を `spec-dock update` だけで新 contract へ in-place 自動移行することは保証しない。
  - old local-only / sequential contract を残したまま新 contract へ段階互換することは目的にしない。
  - ただし、既存 checked-in data を無断で破壊すること自体は目的にしない。

## Epic requirements
- E-RQ-001:
  - `new initiative` / `new epic` / `new issue` はすべて GitHub issue mandatory であり、local-only path を持たないこと。
- E-RQ-002:
  - canonical repo scope は consumer repo の Git remote `origin` が指す GitHub repository を唯一の正本として解決すること。
  - canonical repo scope resolver は以下を満たす fully specified 手順であること。
    - `origin` remote が存在しない場合は fail-fast（create/validate は即時失敗）とする。
    - `origin` の fetch URL / push URL が両方ある場合は両方を GitHub `owner/repo` に正規化し、一致しなければ fail-fast（fetch-push mismatch）とする。
    - `origin` URL が GitHub remote（`github.com`）へ正規化できない場合は fail-fast（non-GitHub remote）とする。
    - SSH / HTTPS URL は同一の `owner/repo` canonical form へ正規化して比較する。
    - `owner` / `repo` 比較は lowercase basis で行い、`.meta.json` に保持する `repo_owner` / `repo_name` も lowercase canonical form とする（少なくとも比較は lowercase basis で行う）こと。
  - `configured repo scope` のような追加設定値を持つ場合、その値は `origin` 解決結果と一致していなければならず、不一致は fail-fast validation / create reject とすること。
  - node は空 workspace の初回作成時から canonical repo scope に束縛されること。
  - `.meta.json` は GitHub linkage を single GitHub repo 前提で一貫して保持し、`github.issue_number` / `repo_owner` / `repo_name` は canonical repo scope と一致すること。
  - canonical repo scope と一致しない existing issue / target は cross-repo linkage として reject すること。
- E-RQ-003:
  - `new doc` の discussion / ADR filename は timestamp-prefix naming へ移行し、lowercase path 制約に適合する以下 grammar を満たすこと。
  - basename grammar:
    - `<ts>-<kind>-<slug>.md`
    - `ts = yyyymmddthhmmssz`（UTC、`t` / `z` は lowercase 固定）
    - 同秒衝突時のみ `yyyymmddthhmmssz-<nn>-<kind>-<slug>.md`（`nn` は 2 桁）を許可
    - `kind` は `adr` または `disc`
  - legacy note:
    - `001-adr...` / `002-adr...` など pre-contract legacy ADR は grandfathered planning artifacts として保持し、自動 rename 対象ではないこと。
- E-RQ-004:
  - `sync` は `spec-dock/adrs/` を毎回クリアしてから symlink mirror を全再生成し、rename / delete 後の stale symlink を残さないこと。index/manifest は導入しないこと。
  - symlink 非対応環境では mirror を空の generated directory として残すか再作成し、warning を出しつつ成功扱いにできること（重要なのは stale link を残さないこと）。
- E-RQ-005:
  - docs / tests / dogfooding parity が新 contract に揃うこと。
  - 最低限、以下 docs が更新され、old local-only / sequential / index assumption が除去されること。
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - `spec-dock/docs/reference_github.md`
    - `spec-dock/docs/reference_naming.md`
    - `spec-dock/docs/reference_sync.md`

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - 空の workspace または既存 workspace で新規 node を作成する
  - When:
    - initiative / epic / issue create flow を実行する
  - Then:
    - GitHub issue linkage なしでは作成できない
    - canonical repo scope（consumer repo の Git remote `origin` が指す GitHub repository）へ初回 node から束縛される
    - `origin` remote 不在は fail-fast となる
    - non-GitHub remote は fail-fast となる
    - `origin` fetch/push の正規化結果不一致は fail-fast（fetch-push mismatch）となる
    - `configured repo scope` などの追加設定値が存在する場合は `origin` と一致必須であり、不一致は fail-fast validation / create reject される
    - `.meta.json` は `github.issue_number` / `repo_owner` / `repo_name` を canonical repo scope と一致して保持し、別 repo を指す existing issue / target は受け入れない
    - `repo_owner` / `repo_name` は lowercase canonical basis で比較・保持される
  - 観測点:
    - create contract tests
    - `origin` 基準 canonical repo scope resolver evidence（origin missing / non-GitHub remote / fetch-push mismatch）
    - configured scope mismatch reject evidence
    - cross-repo target reject evidence
    - docs contract
- E-AC-002:
  - Given:
    - discussion / ADR を作成する
  - When:
    - `new doc` を実行する
  - Then:
    - basename が `<ts>-<kind>-<slug>.md` grammar で生成される（`ts = yyyymmddthhmmssz`、`kind in {adr, disc}`）
    - 同秒衝突時のみ `-<nn>-`（2桁）suffix が付与される
    - pre-contract legacy ADR（`001-adr...` / `002-adr...`）は grandfathered として保持され、自動 rename 対象にならない
  - 観測点:
    - CLI/runtime tests
- E-AC-003:
  - Given:
    - `sync` を実行する
  - When:
    - ADR 原本を走査する
  - Then:
    - `spec-dock/adrs/` は毎回クリア後に symlink mirror が全再生成され、rename / delete 済み ADR を指す stale symlink が残らない
    - symlink 非対応環境では `spec-dock/adrs/` は空の generated directory として残るか再作成され、warning を出しつつ成功扱いになる
  - 観測点:
    - sync tests、filesystem assertions
- E-AC-004:
  - Given:
    - 旧 dogfooding workspace や legacy contract が残っている
  - When:
    - 新 contract を適用する
  - Then:
    - clause-1: 強制的 backward compatibility を維持しない方針が、新 workspace rebuild 前提の boundary として docs に明記される
    - clause-2: `spec-dock update` による in-place 自動移行を保証しない境界が docs に明記され、update/validate contract と矛盾しない
    - clause-3: 既存 checked-in data の無断破壊を目的にしない境界が migration boundary として定義される
  - 観測点:
    - docs（named docs diff）
    - validate contract tests（auto-migrate path を約束しないこと）
    - migration boundary tests（legacy mismatch 時は fail-fast / warning、既存 checked-in data 非書き換え）
- E-AC-005:
  - Given:
    - provider docs / runtime / tests / dogfooding docs を確認する
  - When:
    - 新 contract を参照する
  - Then:
    - 表記と期待値が新 contract に揃っている
    - `reference_github.md` / `reference_naming.md` / `reference_sync.md`（provider + dogfooding）が更新され、old local-only / sequential / index assumption 除去が closure evidence として確認できる
  - 観測点:
    - docs parity tests、spec review

## スコープ
- MUST:
  - GitHub mandatory node creation contract
  - timestamp-based discussion / ADR naming
  - ADR symlink mirror sync
  - migration guardrails and validation hardening
  - docs / dogfooding parity
  - 旧 workspace に対する非サポート境界（in-place 自動移行非保証）を docs / validate / tests で固定する
- MUST NOT:
  - index / manifest を ADR 集約に導入しない
  - local-only fallback を残さない
  - cross-repo linkage を扱わない
  - 旧 workspace を `spec-dock update` だけで新 contract へ自動移行できると約束しない
- OUT OF SCOPE:
  - multi-repo support
  - old workspace automatic migration tooling
  - legacy contract の dual-mode 互換維持
  - feature value expansion

## 境界
- Always:
  - single GitHub repo 前提
  - canonical repo scope は consumer repo の Git remote `origin` が指す GitHub repository を唯一の正本として固定される
  - canonical repo scope resolver は `origin missing` / `non-GitHub remote` / `fetch-push mismatch` を fail-fast とする
  - SSH / HTTPS は同一 `owner/repo` canonical form に正規化し、`owner` / `repo` 比較は lowercase basis で行う
  - `configured repo scope` のような追加設定値は `origin` と一致必須であり、不一致は fail-fast validation / create reject される
  - old workspace は rebuildable
  - `spec-dock/adrs/` は generated symlink mirror
- Never:
  - old contract と new contract の dual-mode 長期共存
  - stale index / manifest を第二の source-of-truth として持つこと

## 非機能要件
- reliability:
  - `sync` で mirror が再生成可能であること
- reliability / consistency:
  - node identity と doc naming の contract が docs / tests / runtime で一致すること
- operations:
  - maintainer が rebuild boundary を理解できること

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `tests/`
  - `spec-dock/`
- external dependency:
  - GitHub CLI / auth

## 未確定事項
- なし:
  - single GitHub repo 前提、local-only 廃止、symlink mirror only は確定
