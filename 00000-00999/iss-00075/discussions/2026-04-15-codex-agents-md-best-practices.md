---
種別: 議論メモ（Issue）
ID: "disc-2026-04-15-codex-agents-md-best-practices"
タイトル: "Codex AGENTS.md scope split and best practices"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["iss-00075", "epic-00074", "init-local-00002"]
---

# Codex `AGENTS.md` の責務分離とベストプラクティス提案

## 結論
- 推奨は `repo root AGENTS.md` と `.codex/AGENTS.md` を明確に分離する案である。
- `repo root AGENTS.md` は product/repo 固有のドメイン知識と repo ルールを扱う。
- `.codex/AGENTS.md` は SpecDock-aware operational charter、つまり「Codex が SpecDock を使って正しく作業するための運用ルール」に限定する。
- session behavior は `.codex/config.toml` が担い、`.codex/AGENTS.md` で再掲しない。

## 問題設定
- 現行 `src/spec_dock/assets/install_root/.codex/AGENTS.md` は `Language / STT / Constraints` のような session-level guidance が中心で、ユーザー設定や main config と内容が重複しやすい。
- 一方で product repo に配る `.codex/AGENTS.md` に本当に期待されるのは、SpecDock を導入した repo で Codex が迷わず正しい docs / commands / safety rules に乗るための「事前知識パック」である。
- このズレを放置すると、provider 側 asset と product repo root `AGENTS.md` の責務が混線し、重複、drift、token 浪費、誤操作を招く。

## 現状観測
- `src/spec_dock/assets/install_root/.codex/AGENTS.md` は現在かなり薄く、実質的に session instruction の再掲に近い。
- repo root `AGENTS.md` は、この repo 固有の構造、正本、workflow、test、変更境界を詳しく説明している。
- つまり今は、`.codex/AGENTS.md` が「SpecDock の使い方」ではなく「一般ルール」を持ち、repo root 側と役割が競合している。

## consultant A: 情報アーキテクチャ観点

### 比較した案
1. ドメイン / プロトコル分離
- root `AGENTS.md`: product 固有のドメイン知識、repo ルール、設計方針
- `.codex/AGENTS.md`: SpecDock の使い方、active docs の見方、Codex の運用モデル

2. `.codex/AGENTS.md` を薄いポインタにする
- root `AGENTS.md`: product 固有ルールに加えて SpecDock 運用も多めに記述
- `.codex/AGENTS.md`: docs への導線だけ

3. `repo root AGENTS.md` を最小化し `.codex/AGENTS.md` に寄せる
- root `AGENTS.md`: ドメイン要約だけ
- `.codex/AGENTS.md`: repo 契約と SpecDock 運用を広く持つ

### consultant A の評価
- 1 が最も安定する。
- 判断基準が明快:
  - この repo 固有なら root `AGENTS.md`
  - SpecDock を使う repo なら共通なら `.codex/AGENTS.md`
  - 個人の癖なら user settings
- 2 は短期的には楽だが、repo ごとに root `AGENTS.md` が太ってぶれやすい。
- 3 は host-specific file に repo 契約まで載るため、将来 Copilot など他 host と整合しにくい。

## consultant B: 運用 UX / プロンプト設計観点

### 比較した案
1. 薄い redirect 型
- 「SpecDock を使うなら root AGENTS と active docs を読め」だけを書く

2. operational charter + decision rules 型
- SpecDock の正本、読書順、CLI 導線、禁止事項だけを載せる

3. full manual 型
- 背景、長いコマンド一覧、構造説明まで広く載せる

### consultant B の評価
- 2 が最適。
- 理由:
  - onboarding speed が高い
  - 誤操作防止に効く
  - token 効率が良い
  - docs drift に強い
- 1 は軽いが、初見 agent が事故りやすい。
- 3 は親切だが長すぎて drift と token 消費が大きい。

### 補足された重要論点
- `.codex/AGENTS.md` は `config.toml` の代替ではなく補完である。
- `config.toml` は session behavior、orchestrator 責務、sub-agent 利用方針を持つのが自然。
- `.codex/AGENTS.md` は「SpecDock-aware operational charter」に寄せるのがよい。
- `.codex/AGENTS.md` を確実に読ませるなら、Codex 側で `project_doc_fallback_filenames` のような読込契約も意識すべき、という指摘があった。
- 参照ソースとして consultant B は OpenAI の “Unrolling the Codex agent loop” を挙げている。

## 議論の統合

### 合意点
- `.codex/AGENTS.md` は product domain の説明場所ではない。
- root `AGENTS.md` は repo 固有のドメイン知識とルールを持つ。
- `.codex/AGENTS.md` は SpecDock を使う repo で共通の operational contract を持つ。
- `config.toml` に既にある session rules は `.codex/AGENTS.md` に重ねない。
- 長文 manual より short charter が良い。

### 相違点
- consultant A は情報アーキテクチャの安定性を強く重視していた。
- consultant B は token 効率と onboarding speed を強く重視していた。
- ただし最終提案は実質的に一致している。

## 最終提案
- ベストプラクティスは「責務分離 + operational charter」である。
- 採用ルール:
  - root `AGENTS.md`: product/repo 固有のドメイン知識、repo ルール、architecture
  - `.codex/AGENTS.md`: SpecDock の operating model、read order、CLI 操作、安全規則
  - `.codex/config.toml`: session behavior、orchestrator 責務、sub-agent 利用方針

## `.codex/AGENTS.md` に書くべき情報

### 優先度高
1. SpecDock の operating model
- SpecDock は何を管理するか
- 正本は会話ではなく repo docs であること
- initiative / epic / issue / report の関係

2. canonical read order
- `spec-dock/active/issue/*`
- `spec-dock/active/epic/*`
- `spec-dock/active/initiative/*`
- active context がない場合の fallback

3. この host での実行モデル
- Codex では main config が orchestrator responsibility を担う
- specialist は `.codex/agents/` にある
- shared skills は `.agents/skills/` にある

4. managed / unmanaged の境界
- どこが source of truth か
- derived artifact を hand-edit しない
- provider-side / consumer-side の見分け方

5. 標準ワークフロー
- `requirement -> design -> plan -> review -> implement -> report`
- 実装前に issue docs を揃える
- `report.md` に evidence を残す

6. 標準コマンド
- `./spec-dock/scripts/spec-dock active show`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock sync`
- `./spec-dock/scripts/spec-dock sync --github`
- `./spec-dock/scripts/spec-dock deps check ...`

7. anti-patterns / よくある失敗
- active docs を読まずに進めない
- hand-edit で active symlink を触らない
- derived state を直接編集しない
- chat log を正本にしない

8. escalation rules
- active docs が衝突している
- `validate` 失敗の原因が不明
- dependency readiness が block している
- 大きな構造変更が必要

### 推奨文量
- 40〜70 行程度
- 6〜8 セクション
- 1ルール1行中心
- 長文背景説明は避ける

## `.codex/AGENTS.md` に書かない方がよい情報
- product 固有の業務知識
- サービス一覧、ownership、repo 固有 architecture
- テスト戦略の詳細、デプロイ手順、runbook
- sub-agent ごとの詳細 prompt
- persona、会話トーン、承認ポリシー
- 一時的な issue 指示
- 秘密情報、個人設定、ローカルパス
- root `AGENTS.md` や `config.toml` の丸写し

## 推奨見出し案
1. `Purpose`
2. `Read This First`
3. `SpecDock Working Model`
4. `Safe Defaults`
5. `Command Cheat Sheet`
6. `Do Not`
7. `Use The Right Document`
8. `Escalate When`

## 実装上の示唆
- 次の更新で `src/spec_dock/assets/install_root/.codex/AGENTS.md` は、現行の `Language / STT / Constraints` から operational charter に置き換えるのが望ましい。
- その際、`config.toml` と root `AGENTS.md` との重複を削る。
- 可能なら `.codex/AGENTS.md` が確実に読まれる設定契約も点検する。

## 採用判断
- 今回の議論の最終推奨は:
  - `.codex/AGENTS.md` を「SpecDock-aware operational charter」に限定する
  - root `AGENTS.md` を product/domain knowledge の正本にする
  - session behavior は `config.toml` に残す

## 参考
- OpenAI, “Unrolling the Codex agent loop”  
  https://openai.com/index/unrolling-the-codex-agent-loop/
