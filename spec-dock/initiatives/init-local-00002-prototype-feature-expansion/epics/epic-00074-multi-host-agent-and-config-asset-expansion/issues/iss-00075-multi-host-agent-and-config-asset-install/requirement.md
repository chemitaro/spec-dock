---
種別: 要件定義書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 要件定義（WHAT / WHY）

## 目的
- 既存の `install_root` 基盤を使い、Codex と GitHub Copilot に対して host-native な orchestrator / specialist asset を 1 issue で配布できる状態を作る。
- `epic-00074` の approved spec を実装契約へ落とし込み、install / update / prune / validate を単一の実装 issue で閉じる。
- `spec-manager` への rename と、Codex の main config による orchestrator responsibility、GitHub Copilot の `orchestrator` primary agent を同時に成立させる。

## 背景・現状
- 現状の挙動:
  - `install_root` には host-native assets を収める土台があるが、今回の Codex / Copilot 向け asset 群はまだ consumer repo へ配布されていない。
  - Codex は direct `orchestrator.toml` を配布せず、main `config.toml` の developer instructions に責務を載せる必要がある。
  - GitHub Copilot は `orchestrator.agent.md` を primary entrypoint として扱い、`spec-manager.agent.md` を sibling specialist として扱う必要がある。
- 現状の課題:
  - secret / personal config / unsupported prompt assets を混ぜると managed asset contract が壊れる。
  - 旧 `spec-dock` specialist 名を残すと、製品名と agent 名が衝突して運用が分かりにくい。
  - unknown custom files を prune で巻き込まない安全性が必要である。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock init <temp-repo>` を実行する。
  2. Codex / Copilot 向け managed asset が正しい project path に配布されていないことを確認する。
- 観測点:
  - Filesystem:
    - `.codex/config.toml`
    - `.codex/agents/spec-manager.toml`
    - `.agents/skills/**`
    - `.github/agents/orchestrator.agent.md`
    - `.github/agents/spec-manager.agent.md`
  - Command:
    - `./spec-dock/scripts/spec-dock init`
    - `./spec-dock/scripts/spec-dock update`
    - `./spec-dock/scripts/spec-dock validate`
- 情報源:
  - `epic-00074` の requirement / design / plan
  - `spec-dock/active/context-pack.md`
  - `spec-dock/docs/workflow_issue.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - Harness Engineering の maintainer
  - `spec-dock` を使って複数 host の agent/config を管理したい contributor
- 代表シナリオ:
  - maintainer が `spec-dock init` / `spec-dock update` を実行すると、Codex では main config と sibling specialist assets が、GitHub Copilot では primary orchestrator と sibling specialist assets が配布される。

## スコープ
- MUST:
  - Codex では main agent の `config.toml` を bootstrap asset として配布し、`spec-manager` を sibling specialist として配布する。
  - GitHub Copilot では `orchestrator` を primary entrypoint として配布し、`spec-manager` を sibling specialist として配布する。
  - shared skills は `.agents/skills/` に集約する。
  - installer metadata / prune contract / tests / docs / report をこの 1 issue の中で更新する。
  - `./spec-dock/scripts/spec-dock validate` と `sync` で観測できる状態にする。
- MUST NOT:
  - Codex に direct `.codex/agents/orchestrator.toml` を配布しない。
  - GitHub Copilot の `config.json` / `mcp-config.json` を配布しない。
  - prompt assets を current implementation scope に含めない。
  - secret、token、個人環境依存値を managed asset として配布しない。
- OUT OF SCOPE:
  - 新しい installer mechanism の導入
  - runtime protocol の再定義
  - prompt asset の本実装
  - backward compatibility の維持

## 境界
- Always:
  - host ごとの正しい project path にのみ配置する。
  - user-authored unknown files を prune safety で保護する。
  - 既存の `install_root` 基盤を壊さず additive に変更する。
- Ask:
  - host path contract が不明瞭な場合だけ確認する。
- Never:
  - 秘密情報をそのまま配布しない。
  - unsupported host に prompt / config を無理に追加しない。

## 非交渉制約
- backward compatibility は要求しない。
- `spec-dock` specialist は `spec-manager` に統一し、旧名を保持しない。
- Codex は main config が orchestrator responsibility を担い、Copilot は direct `orchestrator` agent を持つ。
- prompt assets は本 issue の deliverable に含めない。

## 前提
- `epic-00074` の single-issue execution plan が approved である。
- `epic-00067` の install_root authority cleanup と `epic-00048` の baseline は closed / completed である。
- 既存の installer foundation は追加 file placement を受け入れられる。

## 受け入れ条件
- AC-001:
  - Actor: maintainer
  - Given: Codex 対応 repo に `spec-dock init` / `update` を実行する
  - When: installer が managed assets を配布する
  - Then: `.codex/config.toml`、`.codex/agents/spec-manager.toml`、`.agents/skills/**` が正しい project path に配置される
  - 観測点: filesystem / validate
- AC-002:
  - Actor: maintainer
  - Given: GitHub Copilot 対応 repo に `spec-dock init` / `update` を実行する
  - When: installer が managed assets を配布する
  - Then: `.github/agents/orchestrator.agent.md` と `.github/agents/spec-manager.agent.md` が正しい project path に配置される
  - 観測点: filesystem / validate
- AC-003:
  - Actor: maintainer
  - Given: 既存 repo に未知のユーザー作成ファイルが存在する
  - When: `spec-dock update` を実行する
  - Then: managed obsolete files だけが prune され、unknown custom files は保持される
  - 観測点: update result / filesystem diff
- AC-004:
  - Actor: maintainer
  - Given: issue docs と managed assets が更新済みである
  - When: `./spec-dock/scripts/spec-dock validate` を実行する
  - Then: validate が pass し、issue report に実行証跡を残せる
  - 観測点: validate / report

## 例外・エッジケース
- EC-001:
  - 条件: Codex 側で direct `orchestrator.toml` を期待する旧資料が残っている
  - 期待: そのファイルは配布されず、main `config.toml` のみが orchestrator responsibility を担う
  - 観測点: filesystem / docs
- EC-002:
  - 条件: `.codex/config.toml` に bootstrap 後の user edits がある
  - 期待: update で user edits を無条件上書きしない
  - 観測点: update diff / filesystem
- EC-003:
  - 条件: prompt asset を求める要件が持ち込まれる
  - 期待: current issue では配布しない
  - 観測点: docs / report

## 入力→出力例（必要時）
- EX-001:
  - Input: `spec-dock init <repo>`
  - Output: Codex と GitHub Copilot の managed asset が host-specific path に配置される

## 用語（ドメイン語彙）
- TERM-001:
  - orchestrator: ユーザーと直接やり取りする主導 agent。Codex では main config の developer instructions、GitHub Copilot では primary custom agent を指す。
- TERM-002:
  - spec-manager: SpecDock 操作用の sibling specialist agent。旧 `spec-dock` 名を置き換える。
- TERM-003:
  - host pack: host ごとに配布する managed asset のまとまり。

## 未確定事項
- なし:
  - issue-00075 は approved spec に基づく single implementation issue として固定する。
