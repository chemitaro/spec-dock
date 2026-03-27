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
  - `.meta.json` は GitHub linkage を single GitHub repo 前提で一貫して保持し、old local-only flow を前提にしないこと。
- E-RQ-003:
  - `new doc` の discussion / ADR filename は timestamp-prefix naming へ移行すること。
- E-RQ-004:
  - `sync` は `spec-dock/adrs/` を毎回クリアしてから symlink mirror を全再生成し、rename / delete 後の stale symlink を残さないこと。index/manifest は導入しないこと。
- E-RQ-005:
  - docs / tests / dogfooding parity が新 contract に揃うこと。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - 新規 node を作成する
  - When:
    - initiative / epic / issue create flow を実行する
  - Then:
    - GitHub issue linkage なしでは作成できない
  - 観測点:
    - CLI tests、docs contract
- E-AC-002:
  - Given:
    - discussion / ADR を作成する
  - When:
    - `new doc` を実行する
  - Then:
    - timestamp-prefix naming で filename が生成される
  - 観測点:
    - CLI/runtime tests
- E-AC-003:
  - Given:
    - `sync` を実行する
  - When:
    - ADR 原本を走査する
  - Then:
    - `spec-dock/adrs/` は毎回クリア後に symlink mirror が全再生成され、rename / delete 済み ADR を指す stale symlink が残らない
  - 観測点:
    - sync tests、filesystem assertions
- E-AC-004:
  - Given:
    - 旧 dogfooding workspace や legacy contract が残っている
  - When:
    - 新 contract を適用する
  - Then:
    - 無理に backward compatibility を維持せず、新 workspace rebuild 前提の boundary が docs と tests に明記される
    - `spec-dock update` による in-place 自動移行を保証しないことが明記される
    - 既存 checked-in data を無断破壊することを目的にしない境界が明記される
  - 観測点:
    - docs、migration boundary tests
- E-AC-005:
  - Given:
    - provider docs / runtime / tests / dogfooding docs を確認する
  - When:
    - 新 contract を参照する
  - Then:
    - 表記と期待値が新 contract に揃っている
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
