---
種別: 議論メモ（Issue）
ID: "disc-2026-04-15-codex-agents-fallback-bridge-best-practices"
タイトル: "Codex .codex/AGENTS.md fallback bridge best practices"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["iss-00075", "epic-00074", "init-local-00002"]
---

# `.codex/AGENTS.md` fallback bridge 運用のベストプラクティス

## 結論
- `<repo>/.codex/AGENTS.md` は、通常の Codex CLI 起動では標準 auto-read 対象ではない。
- したがって、`.codex/AGENTS.md` を恒久的な主役 guidance にするのは非推奨である。
- ただし `project_doc_fallback_filenames = [".codex/AGENTS.md"]` を明示したうえで、「root `AGENTS.md` がまだ存在しない新規 product repo 向け bootstrap-only bridge」として使う案は妥当である。
- この場合の best practice は:
  - root `AGENTS.md` を最終的な authoritative product/domain guidance とする
  - `.codex/AGENTS.md` は SpecDock bootstrap guide に限定する
  - `.codex/config.toml` に session behavior と fallback 設定を置く

## 追加前提
- ユーザー共有の最新調査では、Codex の `AGENTS.md` 標準探索は `CODEX_HOME` と project root から cwd までの経路上の通常ディレクトリに限られ、`<repo>/.codex/AGENTS.md` は特別扱いされない。
- つまり repo root や `src/` などから通常起動した Codex CLI は、`<repo>/.codex/AGENTS.md` を自動では取り込まない。
- ただし `project_doc_fallback_filenames` を使えば、同じ階層の `AGENTS.md` が無い場合に fallback 候補へ入れることはできる。

## 確認した事実

### repo 内の現状
- `src/spec_dock/assets/install_root/.codex/config.toml` は orchestrator/session behavior を担う。
- `src/spec_dock/assets/install_root/.codex/AGENTS.md` は現状かなり薄く、session-level rules の再掲に近い。
- repo root `AGENTS.md` は repo 固有の構造、正本、workflow、変更境界を詳しく持っている。

### OpenAI 公式から読めること
- OpenAI の公開記事では、Codex では `AGENTS.md` が persistent context を補うが、`developer_instructions` などとは別のレイヤーとして扱われている。
- したがって `.codex/AGENTS.md` は `config.toml` の代替ではなく補完である。
- 参考:
  - OpenAI, “How OpenAI uses Codex”  
    https://openai.com/business/guides-and-resources/how-openai-uses-codex/
  - OpenAI, “Unrolling the Codex agent loop”  
    https://openai.com/index/unrolling-the-codex-agent-loop/

### GitHub/openai/codex 側で共有された実装前提
- `<repo>/.codex/AGENTS.md` は標準 auto-read 対象ではない。
- root `AGENTS.md` が存在すればそちらが優先され、fallback は使われない。
- fallback filenames は bridge としては使えるが、標準探索の主役ではない。

## consultant 再分析

### 相談テーマ
- `.codex/AGENTS.md` を「標準 auto-read される guidance」ではなく、「root `AGENTS.md` ができるまでの bridge」として使う案は妥当か。

### 比較した案
1. root `AGENTS.md` を最初から必須にする
- 標準探索と完全整合
- ただし day-0 repo の空白を埋められない

2. `.codex/AGENTS.md` を fallback bridge にする
- `project_doc_fallback_filenames = [".codex/AGENTS.md"]` を設定
- root `AGENTS.md` がない間だけ bootstrap guidance を提供
- root `AGENTS.md` ができた後は自然に退場

3. root `AGENTS.md` を `.codex/AGENTS.md` に寄せる / symlink にする
- 一見シンプル
- ただし責務が混ざり、長期的に domain と host-specific guidance が分離できない

### consultant の結論
- 推奨は案2。
- 理由:
  - 新規 repo 直後の空白を埋められる
  - root `AGENTS.md` が作られた後は標準探索へ自然に handoff できる
  - `.codex/config.toml` と root `AGENTS.md` の責務を汚さない

## ベストプラクティス提案

### 役割分担
- root `AGENTS.md`
  - product/domain 固有知識
  - repo 固有 architecture
  - local commands / high-risk areas / coding rules
- `.codex/config.toml`
  - session behavior
  - orchestrator responsibility
  - sub-agent / MCP / fallback filenames
- `.codex/AGENTS.md`
  - SpecDock bootstrap-only bridge guidance
  - root `AGENTS.md` 未整備期間の最小運用ルール

### `.codex/AGENTS.md` に書くべきこと
1. これは bootstrap-only bridge であり、root `AGENTS.md` が authoritative だと明記する
2. `spec-dock/active/issue -> epic -> initiative` の読む順序
3. SpecDock では会話ではなく repo docs が正本だと明記する
4. active pointer は CLI で扱い、手編集しない
5. 実装前に `requirement / design / plan` を揃える
6. `validate`、`sync`、`deps check` など最小限の safe defaults
7. root `AGENTS.md` が用意されたらそちらを優先する、と明記する

### `.codex/AGENTS.md` に書かないこと
- product 固有ドメイン知識
- repo 固有 architecture の詳細
- session behavior / 会話トーン / 承認ポリシー
- sub-agent ごとの詳細 prompt
- 長い runbook / exhaustive command reference
- 一時的 issue 指示や個人設定

### 設計条件
- bridge は短く保つ
  - 40〜70 行程度
  - 6〜8 セクション
- fallback を additive source と考えない
  - root `AGENTS.md` ができたら主役を譲る
- `config.toml` と重複させない
- domain knowledge を入れない
- root `AGENTS.md` が authoritative であることを明示する

## 推奨見出し構成
1. `Purpose`
2. `Read This First`
3. `SpecDock Working Model`
4. `Safe Defaults`
5. `Command Cheat Sheet`
6. `Do Not`
7. `When Root AGENTS.md Exists`
8. `Escalate When`

## 実装示唆
- 今後の asset 更新でやるべきこと:
  1. `src/spec_dock/assets/install_root/.codex/config.toml` に fallback filenames の採用可否を反映する
  2. `src/spec_dock/assets/install_root/.codex/AGENTS.md` を bootstrap guide に再設計する
  3. root `AGENTS.md` 作成後に bridge が自然に退場する契約を docs に明記する

## 以前の議論との関係
- 先行メモ `2026-04-15-codex-agents-md-best-practices.md` は「`.codex/AGENTS.md` が product repo で有効に使える」前提での最適化だった。
- 本メモはその前提を更新し、「標準 auto-read ではない」という事実を踏まえて上書きする follow-up である。
- 現時点の採用判断は、本メモの結論を優先する。

## 最終提案
- `.codex/AGENTS.md` を使うなら、主役ではなく fallback bridge として使う。
- その bridge は「SpecDock bootstrap guide」に限定する。
- 恒久的な product/domain guidance は root `AGENTS.md` に寄せる。
- session/orchestrator behavior は `.codex/config.toml` に残す。
