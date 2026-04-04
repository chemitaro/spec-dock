---
種別: 要件定義書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-04"
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
- 位置づけ:
  - 既存 accepted scope は `iss-00049` / `iss-00050` で完了済みの `protocol + thin adapter skill + host adapter metadata` までを含む。
  - host-native custom agent / subagent deployment は、上記完了済み範囲を削除・差し替えせず、その上に積む follow-up extension として扱う。

## 問題定義
- 現状は `active.json`、`index.json`、`deps-issues.json`、`index-all.json`、`context-pack.md` の役割が docs 上で部分的にしか定義されておらず、agent の実行判断が実装者依存になりやすい。
- current/future の実行判断に必要な projection と、full-history を含む監査・履歴・全体検索用データの境界が曖昧で、agent が通常実行でも過剰に広い state を読みに行きやすい。
- host ごとの prompt や手順に依存して workflow が分岐し、同じ `spec-dock` 運用でも結果が揺れる。
- `context-pack.md` だけでは機械処理に必要な情報が不足し、最終的に人間向け docs を追加解釈する必要がある。
- `.agents/skills/*` による thin adapter skill は導入できているが、Codex の `.codex/agents/*.toml` や GitHub Copilot の `.github/agents/*.agent.md` といった host-native artifact は未配備であり、プロジェクト配下に subagent/custom agent を置いて orchestrator が委譲する運用までは follow-up として残っている。

## 既存 accepted scope と follow-up extension の扱い
- accepted scope（done として保持するもの）:
  - `iss-00049` で fixed point 化した protocol contract / runtime alignment / provider-doc / dogfooding-doc / tests の整合。
  - `iss-00050` で完了済みの `.agents/skills/*` と `.agents/host-adapters/meta.json` の thin adapter scaffold / installer managed deployment / parity / final review。
- follow-up extension（今回の追補で追加するもの）:
  - `.codex/agents/*.toml` と `.github/agents/*.agent.md` の host-native custom agent / subagent artifact。
  - native shim の source-of-truth、installer sync/prune、dogfooding parity、manual validation。
- interpretation rule:
  - 上記 extension は、既存 accepted scope の未完了扱いではなく、完了済み scope を維持したまま追加する。
  - 根拠は `discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md` を正本とする。

## ユースケース
- happy path:
  - メイン orchestrator が spec-dock 専門 sub-agent に委任し、sub-agent が `active.json` を入口に `index.json` / `deps-issues.json` を既定の working set として使って対象と手順を決定する。
  - full-history が必要な監査・履歴参照・全体検索・escalation の場合のみ `index-all.json` を追加で読む。
  - Codex/Copilot のどちらでも同じ protocol に従い、`sync` / `validate` / docs 読み順が一致する。
  - follow-up extension では `spec-dock init/update` 後に host-native custom agent/subagent artifact が配置され、orchestrator はその native agent を entrypoint にして spec-dock 操作を委譲できる。
- exception / operation scenario:
  - active が未設定の場合は `active-none` placeholder を明示的に検知し、編集対象外として停止する。
  - host adapter 側に state 再実装が無いことを review で検証し、drift を抑制する。
  - follow-up extension でも unknown custom skill / unknown custom native agent は installer prune の対象にせず、managed 生成物だけを更新する。

## Epic requirements
- E-RQ-001:
  - agent-facing protocol と human-facing summary の責務を分離し、`active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の役割を明文化すること。
  - agent の通常実行では full-history を第一選択にせず、`active.json` を入口、`index.json` と `deps-issues.json` を current/future projection として既定読取対象にすること。
  - `index-all.json` は full-history を含む監査・履歴・全体検索・escalation 用途として定義し、通常実行の第一選択ではないことを明記すること。
- E-RQ-002:
  - host adapter は runtime state の再実装を持たず、core protocol 参照のみで動作する薄い構成にすること。
  - follow-up extension では `.agents/skills/*` を adapter guidance の正本とし、host-native artifact はそこへ委譲する thin shim にすること。
- E-RQ-003:
  - installer (`init/update`) で Codex/Copilot 向け adapter scaffold を管理可能な形で配布・更新できること。
  - 既存 accepted scope では `.agents/skills/*` と `.agents/host-adapters/meta.json` を managed asset として維持すること。
  - follow-up extension では `.codex/agents/*.toml` / `.github/agents/*.agent.md` を managed deployment 対象として追加できること。
- E-RQ-004:
  - docs と runtime contract の整合を保ち、provider / dogfooding 双方で同じ guidance を提供すること。
  - follow-up extension では host-native artifact の配置、ownership、source-of-truth、prune policy、validation 方針を docs と tests で一貫させること。
- E-RQ-005:
  - issue 分割は過細分化を避け、2 issue で完了可能なサイズに保つこと。
  - 上記 2 issue は `iss-00049` / `iss-00050` として done のまま保持すること。
  - host-native deployment は、既存 2 issue を reopen せず、follow-up 2 issue 程度の extension で閉じること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - active issue が設定済みである。
  - When:
    - agent が protocol に従って文脈取得を行う。
  - Then:
    - 入口は `active.json`、通常実行の working set は `index.json` と `deps-issues.json`、補助説明は `context-pack.md` として一貫し、`index-all.json` は必要時のみ参照される。
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
  - follow-up extension 観測点:
    - native agent / subagent 経由で起動しても、state 参照と推奨コマンド導線が `.agents/skills/*` の guidance から逸脱しないこと。
- E-AC-003:
  - Given:
    - 新規 install/update を実行する。
  - When:
    - managed assets を同期する。
  - Then:
    - adapter scaffold が配布・更新され、既存 managed skill の運用を壊さない。
  - 観測点:
    - installer tests、assets 配布結果、破壊的差分の不在。
  - follow-up extension 観測点:
    - native artifact sync/prune が追加されても、unknown custom native agent / custom skill を壊さない。
- E-AC-004:
  - Given:
    - epic 実装後に docs parity を確認する。
  - When:
    - provider/dogfooding docs を比較する。
  - Then:
    - protocol と adapter guidance に矛盾が無い。
  - 観測点:
    - parity check 記録、final spec review。
  - follow-up extension 観測点:
    - generated native artifact の ownership / source-of-truth / manual validation evidence が provider/dogfooding parity 記録と矛盾しないこと。

## スコープ
- MUST:
  - protocol の責務分離を docs と設計で固定する。
  - agent の既定読取を current/future projection に寄せ、full-history を通常実行の第一選択にしないことを固定する。
  - host adapter scaffold を Codex/Copilot 向けに提供する。
  - issue 分割を 2 issue で閉じる計画を定義する。
  - `iss-00049` / `iss-00050` 完了済みの accepted scope は done のまま保持する。
  - host-native custom agent/subagent artifact は follow-up extension として Codex/Copilot 向け managed deployment できるようにする。
- MUST NOT:
  - host adapter に独自の状態解釈ロジックを持たせない。
  - メイン orchestrator 直操作を前提に複雑化した運用を推奨しない。
  - host-native artifact に独自の状態解釈ロジックを持たせない。
  - 完了済み `iss-00049` / `iss-00050` を native artifact 未実装の理由で未完了へ読み替えない。
- OUT OF SCOPE:
  - invalid artifact prevention の architecture-level 実装（別 initiative で follow-up）
  - multi-host（Codex/Copilot 以外）展開
  - runtime の大規模リファクタ
  - host ごとの高度な orchestration policy 最適化

## 境界
- Always:
  - protocol は host-neutral である。
  - adapter は薄い binding に留める。
  - follow-up extension でも `.agents/skills/*` が spec-dock 操作 guidance の正本である。
- Ask:
  - host 固有差分が protocol に侵食していないか。
  - docs 記述が state contract と一致しているか。
  - native artifact が shim の範囲を越えていないか。
- Never:
  - `context-pack.md` を唯一正本として扱う。
  - `index-all.json` を通常実行の第一読取対象として固定しない。
  - adapter 側で `index-all.json` 相当を再生成する。
  - native artifact を state owner にしない。

## 非機能要件
- performance:
  - adapter 追加で `sync` / `validate` の体感を悪化させない。
  - follow-up extension で native artifact を追加しても体感を悪化させない。
- reliability / consistency:
  - host 間で同一入力に対する参照導線を一致させる。
- security:
  - adapter は既存の安全境界（read-only placeholder / command contract）を弱めない。
  - follow-up extension の native artifact も既存の安全境界を弱めない。
- operations:
  - install/update で managed asset として追跡可能である。
  - unknown custom file を破壊しない prune policy を持つ。

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/codex_skills/`
  - `.agents/host-adapters/meta.json`
  - `tests/test_init_update.py`
- extension impact:
  - `.codex/agents/*.toml`
  - `.github/agents/*.agent.md`
- external dependency:
  - Codex/Copilot 側の skill 読み込み規約（`.agents/skills` 利用）
  - follow-up extension では Codex 側の subagent 仕様（`.codex/agents/*.toml`）と GitHub Copilot 側の custom agent 仕様（`.github/agents/*.agent.md`）。
- compatibility:
  - 既存 `spec-dock` managed skill 配布と両立すること。
  - 既存完了済み `iss-00049` / `iss-00050` の成果を壊さず、follow-up で拡張すること。

## 決定事項
- D-001:
  - host adapter metadata は `.agents/host-adapters/meta.json` を採用済みとする。
  - runtime state 正本（`.agent`）と adapter 管理情報（`.agents`）は分離したまま運用する。
- D-002:
  - `.agents/skills/*` を adapter guidance の正本とする。
  - `.codex/agents/*.toml` / `.github/agents/*.agent.md` は host-native discovery のための thin shim とする。
