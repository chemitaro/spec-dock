---
種別: 要件定義書（Issue）
ID: "iss-00037"
タイトル: "Migration Guardrails and Validation Hardening"
関連GitHub: ["#37"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["epic-00033", "init-local-00003"]
---

# iss-00037 Migration Guardrails and Validation Hardening — 要件定義（WHAT / WHY）

## 目的
- old workspace 非サポート境界を clause-by-clause で閉じ、epic の migration boundary を final closure できる状態にする。
- `iss-00034` / `iss-00036` / `iss-00035` / `iss-00040` で実装・整列された current contract を前提に、docs / validate / migration tests で reviewer が再判定できる evidence contract を完成させる。

## 背景・現状
- 現状の挙動:
  - `iss-00034` で GitHub mandatory create と validate / import / sync preflight の fail-fast 境界が導入済みである。
  - `iss-00036` で timestamp-based discussion / ADR naming と legacy sequential grandfathering が導入済みである。
  - `iss-00035` で ADR mirror の clear-then-rebuild と symlink unsupported warning success が導入済みである。
  - `iss-00040` で stale-contract cluster と dogfooding parity drift の主要な test / fixture / mirror 不整合が current contract に整列済みである。
  - `iss-00038` は full docs parity / final close-out を持つが、migration boundary の clause-by-clause closure owner は本 issue である。
- 現状の課題:
  - old workspace 非サポートの方針は epic docs にはあるが、reviewer が clause-1 / clause-2 / clause-3 を個別に再確認できる evidence bundle が `iss-00037` に固定されていない。
  - `spec-dock update` の in-place 自動移行非保証、legacy mismatch の fail-fast / warning、checked-in data 非破壊の境界が、docs / validate / tests に分散している。
  - `iss-00038` / `iss-00040` と責務を混ぜると、close readiness の ownership が曖昧になる。
- 再現手順:
  1. epic-00033 の現行 docs / reports / tests を横断して読む。
  2. 各 clause の根拠は存在するが、どの docs / tests / command evidence をもって close とみなすかが issue 単位で固定されていない。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock validate`
    - 必要に応じて `./spec-dock/scripts/spec-dock sync`
  - Docs:
    - `reference_github.md`
    - `reference_naming.md`
    - epic / issue requirement / design / plan
  - Tests:
    - `tests/cli_runtime/test_validate.py`
    - 必要に応じて `tests/cli_runtime/test_sync.py`
  - Reports:
    - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00040` の report
- 情報源:
  - `epic-00033` requirement / design / plan
  - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00040` reports
  - current docs / tests / validation implementation

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - migration boundary を説明・運用する maintainer
  - epic close readiness を判定する reviewer
- 代表シナリオ:
  - old workspace は rebuildable であり、自動移行対象ではないことを docs / validate / tests で確認したい。
  - legacy mismatch に遭遇したとき、無言の auto-repair ではなく fail-fast / warning で止まることを確認したい。
  - `iss-00038` / `iss-00040` と重複せずに、`iss-00037` だけで migration boundary close readiness をレビューしたい。

## スコープ
- MUST:
  - E-AC-004 の 3 条項を clause-by-clause で閉じる。
  - clause ごとに docs / validate / tests / command evidence を対応づける。
  - `iss-00034` / `iss-00036` / `iss-00035` / `iss-00040` の実装成果を migration boundary の観点で統合し、final closure owner としての根拠を固定する。
- MUST NOT:
  - old workspace 自動移行 tooling を追加しない。
  - backward compatibility を強制維持する方向へ戻さない。
  - `iss-00038` の full docs parity や `iss-00040` の stale-contract realignment を再実装しない。
- OUT OF SCOPE:
  - create contract そのものの新規拡張
  - naming grammar そのものの再設計
  - ADR mirror 実装そのもの
  - final docs parity / final regression の全面 close-out

## 境界
- Always:
  - clause-1: 強制的 backward compatibility を維持しない。
  - clause-2: `spec-dock update` の in-place 自動移行を保証しない。
  - clause-3: 既存 checked-in data の無断破壊を目的にしない。
  - true runtime defect を見つけた場合は、この issue で scope を暗黙拡張せず stop / escalate する。
- Ask:
  - warning wording や docs wording の細部は実装段階で最小限に詰める。
  - issue 間の ownership 衝突が見つかった場合だけ、人間判断で scope を再確認する。
- Never:
  - migration boundary を narrative だけで閉じたことにしない。
  - legacy mismatch を無言で書き換えて吸収しない。
  - `iss-00038` / `iss-00040` の close evidence を無断で取り込んで ownership を曖昧にしない。

## 非交渉制約
- docs / validate / tests の evidence contract を揃える。
- clause ごとに objective evidence を持つ。
- final closure owner は本 issue とする。
- minimal boundary docs diff までを本 issue の docs scope とし、full parity refresh は後続 issue に残す。

## 前提
- `iss-00034` / `iss-00036` / `iss-00035` / `iss-00040` の先行 contract が存在する。
- old workspace は rebuildable であり、自動移行は epic の非目標である。
- reviewer が clause-by-clause で close 判定できる必要がある。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - migration boundary を docs と validate rules で確認する
  - When:
    - clause-1 を評価する
  - Then:
    - 強制的 backward compatibility を維持しない方針と、legacy sequential docs の grandfathering 境界が named docs diff と validate evidence で確認できる
  - 観測点:
    - docs diff
    - `tests/cli_runtime/test_validate.py`
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - create / validate / update 周辺の migration boundary を確認する
  - When:
    - clause-2 を評価する
  - Then:
    - in-place 自動移行非保証が docs diff と create / validate reject evidence で確認できる
  - 観測点:
    - docs diff
    - targeted create / validate evidence
- AC-003:
  - Actor:
    - maintainer / reviewer
  - Given:
    - legacy mismatch または malformed state がある
  - When:
    - clause-3 を評価する
  - Then:
    - fail-fast / warning と checked-in data 非書き換えが validation / sync preflight / command evidence で確認できる
  - 観測点:
    - migration tests
    - `./spec-dock/scripts/spec-dock validate`
- AC-004:
  - Actor:
    - maintainer / reviewer
  - Given:
    - `iss-00037` の close readiness を判定する
  - When:
    - issue report / final review packet を確認する
  - Then:
    - clause-1 / clause-2 / clause-3 の evidence set と owner boundary が 1 箇所で追え、`iss-00038` / `iss-00040` と責務衝突せずに close 判断できる
  - 観測点:
    - `report.md`
    - final review record

## 例外・エッジケース
- EC-001:
  - 条件:
    - old workspace に legacy contract assumption が複数混在する
  - 期待:
    - boundary docs/tests/validate がどこまで非サポートかを曖昧にしない
  - 観測点:
    - migration boundary tests
    - issue-level evidence mapping
- EC-002:
  - 条件:
    - maintainer が `update` による自動移行を期待している
  - 期待:
    - docs と contract tests で非保証であることが明確に観測できる
  - 観測点:
    - docs diff
    - create / validate evidence

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - old workspace / legacy mismatch state に対して validate を実行する
  - Output:
    - fail-fast / warning により境界が観測でき、checked-in data の無断書き換えは発生しない
- EX-002:
  - Input:
    - reviewer が `iss-00037` close readiness を確認する
  - Output:
    - clause-1/2/3 ごとの evidence set と owner boundary が 1 箇所で追える

## 用語（ドメイン語彙）
- TERM-001:
  - migration boundary:
    - old workspace と new contract のあいだで、何を保証し何を保証しないかを示す契約
- TERM-002:
  - final closure owner:
    - epic acceptance を最終的に clause-by-clause で閉じる責務を持つ `iss-00037`
- TERM-003:
  - evidence bundle:
    - docs / tests / command results / review record を clause 単位で結びつけた close 判定用の証跡束

## 未確定事項
- なし:
  - 現在の issue scope は evidence hardening に限定する
