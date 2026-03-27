---
種別: 要件定義書（Issue）
ID: "iss-00037"
タイトル: "Migration Guardrails and Validation Hardening"
関連GitHub: ["#37"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-27"
親: ["epic-00033", "init-local-00003"]
---

# iss-00037 Migration Guardrails and Validation Hardening — 要件定義（WHAT / WHY）

## 目的
- old workspace 非サポート境界を clause-by-clause で閉じ、epic の migration boundary を final closure できる状態にする。
- docs / validate / migration tests で、強制互換しないが無断破壊も目的にしない境界を明文化する。

## 背景・現状
- 現状の挙動:
  - `iss-00034` / `iss-00036` で migration boundary の先行ガードを入れる前提だが、epic 全体としての final closure owner はまだ必要である。
- 現状の課題:
  - old workspace 非サポートの方針は、条項ごとの evidence がないとレビュー時に narrative 依存になる。
  - validate が migration boundary を十分に表現しないと、docs と runtime contract がずれる。
- 再現手順:
  1. old workspace / legacy expectation が残る状態で新 contract を導入する。
  2. clause ごとの evidence がないと、どこまで閉じたか判定できない。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock validate`
    - `spec-dock update` contract
  - Docs:
    - migration boundary 記述
  - Tests:
    - migration / validate suites
- 情報源:
  - `epic-00033` requirement / design / plan
  - `iss-00034` / `iss-00036` の先行ガード requirement

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - contract change を rollout する maintainer
- 代表シナリオ:
  - old workspace を自動移行対象にしないことを明文化しつつ、破壊的な書き換えを行わない。
  - validate / tests / docs を見れば migration boundary の意味が追える。

## スコープ
- MUST:
  - E-AC-004 の 3 条項を clause-by-clause で閉じる。
  - validate と migration tests を boundary contract に合わせて harden する。
  - `iss-00034` / `iss-00036` の先行ガードを final closure owner として統合する。
- MUST NOT:
  - old workspace 自動移行 tooling を追加しない。
  - backward compatibility を強制維持する方向へ戻さない。
- OUT OF SCOPE:
  - create contract そのもの
  - naming grammar そのもの
  - ADR mirror 実装そのもの

## 境界
- Always:
  - clause-1: 強制的 backward compatibility を維持しない。
  - clause-2: `spec-dock update` の in-place 自動移行を保証しない。
  - clause-3: 既存 checked-in data の無断破壊を目的にしない。
- Ask:
  - warning wording や補足 guidance の表現は実装段階で最小限に詰める。
- Never:
  - migration boundary を narrative だけで閉じたことにしない。
  - legacy mismatch を無言で書き換えて吸収しない。

## 非交渉制約
- docs / validate / tests の evidence contract を揃える。
- clause ごとに objective evidence を持つ。
- final closure owner は本 issue とする。

## 前提
- `iss-00034` / `iss-00036` / `iss-00035` の先行 contract が存在する。
- old workspace は rebuildable であり、自動移行は epic の非目標である。
- reviewer が clause-by-clause で close 判定できる必要がある。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - migration boundary を docs で確認する
  - When:
    - clause-1 を評価する
  - Then:
    - 強制的 backward compatibility を維持しない方針が named docs diff で確認できる
  - 観測点:
    - docs diff
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - `spec-dock update` と validate contract を確認する
  - When:
    - clause-2 を評価する
  - Then:
    - in-place 自動移行非保証が docs diff と update / validate contract tests で確認できる
  - 観測点:
    - docs diff
    - update / validate tests
- AC-003:
  - Actor:
    - maintainer / reviewer
  - Given:
    - legacy mismatch がある
  - When:
    - clause-3 を評価する
  - Then:
    - fail-fast / warning と checked-in data 非書き換えが migration boundary tests で確認できる
  - 観測点:
    - migration tests
    - validate evidence

## 例外・エッジケース
- EC-001:
  - 条件:
    - old workspace に legacy contract assumption が複数混在する
  - 期待:
    - boundary docs/tests/validate がどこまで非サポートかを曖昧にしない
  - 観測点:
    - migration boundary tests
- EC-002:
  - 条件:
    - maintainer が `update` による自動移行を期待している
  - 期待:
    - docs と contract tests で非保証であることが明確に観測できる
  - 観測点:
    - docs diff
    - update contract tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - old workspace / legacy mismatch state に対して validate を実行する
  - Output:
    - fail-fast / warning により境界が観測でき、checked-in data の無断書き換えは発生しない

## 用語（ドメイン語彙）
- TERM-001:
  - migration boundary:
    - old workspace と new contract のあいだで、何を保証し何を保証しないかを示す契約
- TERM-002:
  - final closure owner:
    - epic acceptance を最終的に clause-by-clause で閉じる責務を持つ `iss-00037`

## 未確定事項
- なし:
  - migration boundary の条項は epic spec で固定済み
