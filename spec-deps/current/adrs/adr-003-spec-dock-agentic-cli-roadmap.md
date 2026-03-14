---
種別: ADR（Architecture Decision Record）
ID: "adr-003"
タイトル: "spec-dock の agentic cli 拡張は後方互換の staged rollout で進める"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-14"
親: []
---

# adr-003 spec-dock の agentic cli 拡張は後方互換の staged rollout で進める

## 結論（Decision） (必須)
- **決定**: `spec-dock` の今後の機能追加は、後方互換性を保つ staged rollout として進める。
- 最優先テーマは `issue status lifecycle` と `link lifecycle` である。
- 実装順序は次のとおりとする。
  - Phase 0: `status contract`
  - Phase 1: local-managed issue 向け `issue close/reopen`
  - Phase 2: `link` / `unlink` と authority transfer
  - Phase 3: linked issue 向け `issue close/reopen --github`
  - Phase 4: `doctor` / `--dry-run` / `--explain`
  - Phase 5: `list/find/show` などの可視化強化
  - Phase 6: atomic sync/update、validation hardening、migration 補助
- `1 issue = 1 authority` を維持し、dual-authority persistence は禁止する。
- `unlink` の既定動作は `adopt effective` とし、hidden local history への自動巻き戻しは行わない。

## 背景（Context） (必須)
- 現行の `spec-dock` では、GitHub-linked issue は GitHub 側の close 状態を参照できる一方、local-only issue には正式な close/reopen コマンドがない。
- そのため、local-only issue の完了状態、GitHub-linked issue との整合、link/unlink 後の状態遷移に設計ギャップがある。
- 同時に、`.agent/index*.json` や sync artifact はすでに各所で参照されており、既存 `status` の意味を置き換えると互換性リスクが高い。
- したがって、既存 artifact を壊さずに authority 情報を additive に導入し、local path を先に完成させ、その後 GitHub mutation と診断機能を広げる順が最も安全である。

## 選択肢（Options considered） (必須)
- Option A:
  - 概要:
    - GitHub issue を必須化し、local-only issue を将来的に廃止する。
  - Pros:
    - authority を GitHub に一本化しやすい。
  - Cons:
    - local-first な運用、bootstrap、offline 寄りの作業に不向き。
    - dogfooding や段階移行と相性が悪い。
  - 棄却理由（棄却する場合）:
    - 現実の運用要件と整合しない。
- Option B:
  - 概要:
    - local-only issue を正式に残しつつ、`1 issue = 1 authority` を明示し、status/link lifecycle を staged rollout で追加する。
  - Pros:
    - 後方互換を保ちやすい。
    - dogfooding しながら段階導入できる。
    - local と GitHub の役割分担を明確にできる。
  - Cons:
    - authority model と migration ルールを丁寧に設計する必要がある。
  - 棄却理由（棄却する場合）:
    - 該当なし。採用。
- Option C:
  - 概要:
    - linked issue にも local override を許し、local/GitHub の二重 status を持つ。
  - Pros:
    - 見かけ上は柔軟。
  - Cons:
    - conflict の温床になり、agent/human ともに扱いにくい。
    - validate / sync / explain が複雑化する。
  - 棄却理由（棄却する場合）:
    - 設計の整合性と operability を損なうため不採用。

## 判断理由（Rationale） (必須)
- 既存 runtime は command registry / parser / use case / infra 契約で分離されており、新 command や result contract を additive に拡張しやすい。
- 一方、既存 `.agent/index*.json` と sync artifact は projection/cache として広く参照されているため、これを authority に差し替えるのは危険である。
- したがって、先に `status contract` を追加し、既存 `status` は維持しながら `authority`、`effective`、`source`、`stale`、`reconcile_action` などを別 field として導入するのがよい。
- その上で、まず local-managed issue に対する close/reopen を可能にし、次に link/unlink で authority transfer を追加し、最後に GitHub mutation を opt-in で足すのが、安全性、実装容易性、dogfooding 効果のバランスが最もよい。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - 後方互換を保ちながら、local-only issue と GitHub-linked issue の両方を一貫したモデルで扱える。
  - `spec-dock` 自身の dogfooding を止めずに、順次必要能力を実装できる。
  - agentic CLI としての machine-readable contract と mutation safety を強化できる。
- Negative / Debt（悪い点 / 将来負債）:
  - 当面は旧 contract と新 contract が併存するため、出力 surface がやや冗長になる。
  - validation hardening は後段に回るため、移行中は warning ベースの期間が必要になる。
- 影響範囲（コード/テスト/運用/データ）:
  - runtime command surface
  - `.meta.json` の schema 拡張
  - `.agent/index*.json` と sync artifact の読み書き
  - GitHub integration path
  - CLI tests と installer update contract
- 移行/ロールバック:
  - 既存 `status` は残し、新 field を additive に追加する。
  - existing issue metadata に field がない場合は `missing -> open` を既定解釈とする。
  - linked issue に対する remote mutation は `--github` 明示のときのみ許可する。
  - validation は最初 warning とし、移行完了後に hard error 化を検討する。
- Follow-ups（追加の Epic/Issue/ADR）:
  - Phase 0 から Phase 6 を issue 分割して、`1 issue = 1 observable capability` で実装する。
  - compatibility rule と acceptance criteria を別文書に固定する。

## 実装方針（Implementation policy） (任意)
- Phase 0. status contract
  - 追加候補:
    - `effective_status`
    - `status_source`
    - `authority`
    - `stale`
    - `reconcile_action`
    - `can_close_locally`
    - `can_close_on_github`
  - 既存 `status` は残す。
- Phase 1. local lifecycle baseline
  - `issue close <target>`
  - `issue reopen <target>`
  - `issue show --json`
  - local metadata を authority とし、sync は projection を再生成する。
- Phase 2. authority transfer baseline
  - `link --issue <id> --github-issue <n>`
  - `unlink <id>`
  - `unlink --adopt effective` を既定とする。
  - `id/path` は不変とし、link/unlink で rename しない。
- Phase 3. GitHub mutation baseline
  - `issue close <target> --github`
  - `issue reopen <target> --github`
  - repo-aware preflight を必須とする。
- Phase 4. safety and operability
  - `doctor`
  - `--dry-run`
  - `--explain`
  - stable reason code / next action
- Phase 5. broader discovery
  - `list`
  - `find`
  - `show`
  - status filtering / stale visibility
- Phase 6. hardening
  - atomic sync/update
  - contradiction validation hardening
  - migration assist

## 参考（References） (任意)
- 関連 ADR:
  - [adr-002-spec-dock-dogfooding.md](/srv/mount/spec-dock/spec-deps/current/adrs/adr-002-spec-dock-dogfooding.md)
- 関連コード:
  - [contracts.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py)
  - [status.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/status.py)
  - [derived_state_reader.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/derived_state_reader.py)

