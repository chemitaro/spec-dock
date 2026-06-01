---
種別: 設計書（Issue）
ID: "iss-00151"
タイトル: "Use GPT55 Low Reasoning For Codex Agents"
関連GitHub: ["#151"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
依存: ["requirement.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00151 Use GPT55 Low Reasoning For Codex Agents — 設計

## 方針
- 設定値だけの変更として扱い、既存 TOML の構造、説明文、権限、context window コメントは維持する。
- provider-side 正本と dogfooding 反映先の同名ファイルを同時に更新し、運用上の見え方をそろえる。
- GitHub Copilot agent はユーザー指定により現状維持する。

## 変更対象
- `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
- `src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml`
- `src/spec_dock/assets/install_root/.codex/agents/utility-worker.toml`
- `src/spec_dock/assets/install_root/.codex/agents/researcher.toml`
- `src/spec_dock/assets/install_root/.codex/agents/spark-worker.toml`
- `.codex/agents/pr-monitor.toml`
- `.codex/agents/spec-manager.toml`
- `.codex/agents/utility-worker.toml`
- `.codex/agents/researcher.toml`
- `.codex/agents/spark-worker.toml`

## 設定マッピング
| agent | model | reasoning |
|---|---|---|
| pr-monitor | `gpt-5.5` | `low` |
| spec-manager | `gpt-5.5` | `low` |
| utility-worker | `gpt-5.5` | `low` |
| researcher | `gpt-5.5` | `low` |
| spark-worker | `gpt-5.3-codex-spark` | `xhigh` |

## 影響範囲
- Codex host 用 agent 設定のみ。
- installer / update が配布する provider-side asset と、この repo の dogfooding agent 設定に影響する。
- GitHub Copilot host 用 `.github/agents/*.agent.md` には影響しない。

## 検証
- 対象 TOML の `model` / `model_reasoning_effort` を `rg` で確認する。
- GitHub Copilot agent 配下に差分がないことを `git diff` で確認する。
