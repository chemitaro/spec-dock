---
種別: 要件定義書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-02"
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00002` の feature expansion として、agent が `spec-dock` を安定して扱える interface を提供する。
  - メイン orchestrator が毎回手作業で文脈解釈しなくても、host adapter 経由で同じ判断導線を再利用できるようにする。
- この epic が提供する能力:
  - 機械可読な active/context 参照契約の明文化。
  - host-neutral protocol と host-specific adapter の責務分離。
  - Codex/Copilot で再利用可能な薄い adapter scaffold の提供。

## 問題定義
- 現状は `active.json`、`index-all.json`、`index.json`、`context-pack.md` の役割が docs 上で部分的にしか定義されておらず、agent の実行判断が実装者依存になりやすい。
- host ごとの prompt や手順に依存して workflow が分岐し、同じ `spec-dock` 運用でも結果が揺れる。
- `context-pack.md` だけでは機械処理に必要な情報が不足し、最終的に人間向け docs を追加解釈する必要がある。

## ユースケース
- happy path:
  - メイン orchestrator が spec-dock 専門 sub-agent に委任し、sub-agent が `active.json` を入口に `index-all.json` / `index.json` を使って対象と手順を決定する。
  - Codex/Copilot のどちらでも同じ protocol に従い、`sync` / `validate` / docs 読み順が一致する。
- exception / operation scenario:
  - active が未設定の場合は `active-none` placeholder を明示的に検知し、編集対象外として停止する。
  - host adapter 側に state 再実装が無いことを review で検証し、drift を抑制する。

## Epic requirements
- E-RQ-001:
  - agent-facing protocol と human-facing summary の責務を分離し、`active.json` / `index-all.json` / `index.json` / `context-pack.md` の役割を明文化すること。
- E-RQ-002:
  - host adapter は runtime state の再実装を持たず、core protocol 参照のみで動作する薄い構成にすること。
- E-RQ-003:
  - installer (`init/update`) で Codex/Copilot 向け adapter scaffold を管理可能な形で配布・更新できること。
- E-RQ-004:
  - docs と runtime contract の整合を保ち、provider / dogfooding 双方で同じ guidance を提供すること。
- E-RQ-005:
  - issue 分割は過細分化を避け、3 issue で完了可能なサイズに保つこと。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - active issue が設定済みである。
  - When:
    - agent が protocol に従って文脈取得を行う。
  - Then:
    - 入口は `active.json`、全体判断は `index-all.json`、todo 絞り込みは `index.json`、補助説明は `context-pack.md` として一貫する。
  - 観測点:
    - docs 記述、JSON shape、実行手順例の一致。
- E-AC-002:
  - Given:
    - Codex/Copilot 両方の adapter が生成済みである。
  - When:
    - 同一 task を各 adapter 経由で起動する。
  - Then:
    - 参照 state と推奨コマンド導線が一致し、host 固有差分は entrypoint 文面に限定される。
  - 観測点:
    - 生成ファイル差分、adapter 設計、レビュー結果。
- E-AC-003:
  - Given:
    - 新規 install/update を実行する。
  - When:
    - managed assets を同期する。
  - Then:
    - adapter scaffold が配布・更新され、既存 managed skill の運用を壊さない。
  - 観測点:
    - installer tests、assets 配布結果、破壊的差分の不在。
- E-AC-004:
  - Given:
    - epic 実装後に docs parity を確認する。
  - When:
    - provider/dogfooding docs を比較する。
  - Then:
    - protocol と adapter guidance に矛盾が無い。
  - 観測点:
    - parity check 記録、final spec review。

## スコープ
- MUST:
  - protocol の責務分離を docs と設計で固定する。
  - host adapter scaffold を Codex/Copilot 向けに提供する。
  - issue 分割を 3 issue で閉じる計画を定義する。
- MUST NOT:
  - host adapter に独自の状態解釈ロジックを持たせない。
  - メイン orchestrator 直操作を前提に複雑化した運用を推奨しない。
- OUT OF SCOPE:
  - invalid artifact prevention の architecture-level 実装（別 initiative で follow-up）
  - multi-host（Codex/Copilot 以外）展開
  - runtime の大規模リファクタ

## 境界
- Always:
  - protocol は host-neutral である。
  - adapter は薄い binding に留める。
- Ask:
  - host 固有差分が protocol に侵食していないか。
  - docs 記述が state contract と一致しているか。
- Never:
  - `context-pack.md` を唯一正本として扱う。
  - adapter 側で `index-all.json` 相当を再生成する。

## 非機能要件
- performance:
  - adapter 追加で `sync` / `validate` の体感を悪化させない。
- reliability / consistency:
  - host 間で同一入力に対する参照導線を一致させる。
- security:
  - adapter は既存の安全境界（read-only placeholder / command contract）を弱めない。
- operations:
  - install/update で managed asset として追跡可能である。

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/codex_skills/`
- external dependency:
  - Codex/Copilot 側の skill 読み込み規約（`.agents/skills` 利用）
- compatibility:
  - 既存 `spec-dock` managed skill 配布と両立すること。

## 未確定事項
- Q-001:
  - 質問:
    - host adapter metadata を `spec-dock/.agent` 配下に持つか、`.agents` 配下に閉じるか。
  - 選択肢:
    - A:
      - `.agent` 配下へ集約し runtime 状態と近接させる。
    - B:
      - `.agents` 配下へ閉じ、adapter 管理情報として独立させる。
  - 推奨案:
    - B。runtime state 正本との混線を避けやすい。
  - 影響範囲:
    - installer 設計、docs、tests。
