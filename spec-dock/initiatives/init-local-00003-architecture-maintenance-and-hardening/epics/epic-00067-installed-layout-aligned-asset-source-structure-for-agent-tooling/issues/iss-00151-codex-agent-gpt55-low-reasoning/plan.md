---
種別: 実装計画書（Issue）
ID: "iss-00151"
タイトル: "Use GPT55 Low Reasoning For Codex Agents"
関連GitHub: ["#151"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00151 Use GPT55 Low Reasoning For Codex Agents — 実装計画

## ステップ
- S01: issue docs を簡潔に整える。
- S02: provider-side Codex agent TOML を更新する。
- S03: dogfooding 反映先の `.codex/agents/` を同じ設定にそろえる。
- S04: `rg` と `git diff` で対象設定と Copilot 側 no-diff を確認する。

## 対象設定
- `pr-monitor`、`spec-manager`、`utility-worker`、`researcher`:
  - `model = "gpt-5.5"`
  - `model_reasoning_effort = "low"`
- `spark-worker`:
  - `model = "gpt-5.3-codex-spark"` を維持
  - `model_reasoning_effort = "xhigh"`

## 禁止変更
- `.github/agents/` と `src/spec_dock/assets/install_root/.github/agents/` は変更しない。
- runtime code、installer code、agent description、tool permission は変更しない。

## 検証コマンド
```bash
rg -n "model =|model_reasoning_effort" src/spec_dock/assets/install_root/.codex/agents .codex/agents -S
git diff -- .github/agents src/spec_dock/assets/install_root/.github/agents
git diff --check
```
