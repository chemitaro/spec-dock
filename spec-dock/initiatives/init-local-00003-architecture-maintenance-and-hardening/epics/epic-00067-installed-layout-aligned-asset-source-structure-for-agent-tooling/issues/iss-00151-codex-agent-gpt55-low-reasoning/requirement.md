---
種別: 要件定義書（Issue）
ID: "iss-00151"
タイトル: "Use GPT55 Low Reasoning For Codex Agents"
関連GitHub: ["#151"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
親: ["epic-00067", "init-local-00003"]
---

# iss-00151 Use GPT55 Low Reasoning For Codex Agents — 要件定義

## 目的
- Codex 用に提供する sub-agent 設定のうち、`gpt-5.4-mini` 系を使っている agent を `gpt-5.5` + low reasoning へ寄せる。
- `spark-worker` は lightweight model のまま残し、reasoning effort だけ `xhigh` に上げる。

## 背景・現状
- `src/spec_dock/assets/install_root/.codex/agents/` が provider-side の正本で、`.codex/agents/` は dogfooding 反映先である。
- 現在、`pr-monitor`、`spec-manager`、`utility-worker`、`researcher` は `gpt-5.4-mini` を使っている。
- `spark-worker` は `gpt-5.3-codex-spark` を使っており、この model は維持する。

## スコープ
- 必須:
  - provider-side の Codex agent TOML を更新する。
  - dogfooding 反映先の `.codex/agents/` も同じ設定にそろえる。
  - `gpt-5.4-mini` の Codex agent を `model = "gpt-5.5"`、`model_reasoning_effort = "low"` にする。
  - `spark-worker` は `model = "gpt-5.3-codex-spark"` を維持し、`model_reasoning_effort = "xhigh"` にする。
- 禁止:
  - `.github/agents/` の GitHub Copilot agent 設定を変更しない。
  - `gpt-5.5` 既存 agent の reasoning 設定を今回まとめて変更しない。
- 対象外:
  - reviewer gate を伴う正式な spec promotion。
  - runtime 実装、installer 実装、テスト追加。

## 受け入れ条件
- AC-001:
  - `pr-monitor`、`spec-manager`、`utility-worker`、`researcher` の Codex TOML が provider / dogfooding 反映先の両方で `gpt-5.5` + `low` になっている。
- AC-002:
  - `spark-worker` の model は provider / dogfooding 反映先の両方で `gpt-5.3-codex-spark` のまま、reasoning effort が `xhigh` になっている。
- AC-003:
  - `.github/agents/` 配下には差分がない。

## 検証方針
- `rg` による対象 TOML の設定確認。
- `git diff -- .github/agents src/spec_dock/assets/install_root/.github/agents` で GitHub Copilot agent 側に差分がないことを確認する。
