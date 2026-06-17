---
種別: 要件定義書（Issue）
ID: "iss-00197"
タイトル: "Extract Python From PR Review Snapshot Script"
関連GitHub: ["#197"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["epic-00158", "init-local-00003"]
---

# iss-00197 Extract Python From PR Review Snapshot Script — 要件定義（何を、なぜ行うか）

## 目的
- PR observation skill の `fetch_pr_review_snapshot.sh` に残っている大規模な Python heredoc を、独立した Python entrypoint へ分離する。
- Shell wrapper は引数・環境変数・終了コードの受け渡しに限定し、review snapshot の判定ロジックは Python ファイル側で保守できる状態にする。
- 既に merged された `iss-00187` の残課題を follow-up issue として切り出し、肥大化した issue の文脈に埋もれないようにする。

## 背景・現状
- 現状の挙動:
  - `iss-00187` では PR observation scripts の Python / shell 分離、CI / review observation hardening、review inventory handling が段階的に実装された。
  - ただし、`.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` には `python3 - <<'PY'` 形式の Python heredoc が残っている。
  - provider-side source である `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` にも同じ heredoc が残っている。
- 現状の課題:
  - review snapshot collector の主要ロジックが shell script 内に埋め込まれており、可読性・レビュー容易性・テスト容易性が低い。
  - Shell と Python の責務境界が曖昧なままだと、今後の review completion / unresolved thread / fallback signal の修正で再び大きな shell diff が発生しやすい。
  - `iss-00187` は既に merge 済みのため、この残課題は同 issue の追加修正ではなく新しい issue として扱う。
- 再現手順:
  1. `rg -n "python3|<<'PY'|<<PY|PY$" .agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` を実行する。
  2. `fetch_pr_review_snapshot.sh` 内に Python heredoc が残っていることを確認する。
- 観測点:
  - CLI:
    - `fetch_pr_review_snapshot.sh` の既存 CLI / environment contract が維持されること。
  - Files:
    - provider-side source と dogfooding mirror の両方で shell heredoc が解消されること。
  - Tests:
    - 既存の PR review snapshot / observation tests が継続して通ること。
- 情報源:
  - PR #190 / issue #187 の merged follow-up。
  - User report on 2026-06-17: `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh` に Python が残っている。
  - Current source inspection:
    - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - PR observation skill を保守する agent / developer。
  - `github-pr-observation` skill を使って PR review / CI 状態を監視する orchestrator。
- 代表シナリオ:
  - review snapshot 判定ロジックを変更するときに、shell heredoc ではなく Python module / script を対象に小さくテスト・レビューできる。

## スコープ
- 必須:
  - `fetch_pr_review_snapshot.sh` から Python heredoc を完全に取り除く。
  - 抽出先 Python entrypoint を provider-side source of truth に追加する。
  - dogfooding mirror の `.agents/skills/github-pr-observation/scripts/lib/` へ provider-side と同等のファイル構成を反映する。
  - 既存 shell script の public CLI / env var / stdout JSON / stderr / exit code contract を維持する。
  - 既存 review snapshot semantics を保持し、機能追加や completion signal policy 変更を混ぜない。
- 禁止:
  - review completion 判定、carryover unresolved thread 判定、CI status 判定などの behavior change を、分離作業と無関係に変更しない。
  - provider-side source を飛ばして dogfooding mirror だけを直接修正しない。
  - heredoc を別の shell script へ移すだけで「分離完了」と扱わない。
- 対象外:
  - `trigger_codex_review.sh` など、今回指定されていない別 script の Python heredoc 抽出。
  - PR observation の新しい signal contract 設計。
  - GitHub API 仕様の追加調査を要する機能変更。

## 境界
- 常に行う:
  - provider-side first で実装し、dogfooding mirror へ同期 / 同等性確認を行う。
  - heredoc 消滅を `rg` で確認する。
  - 既存 behavior を守る regression test を実行する。
- 判断が必要:
  - Python entrypoint の配置先と module 境界。
  - Shell wrapper から Python entrypoint へ渡す contract を argv に寄せるか、既存 env contract を維持するか。
- 行わない:
  - `iss-00187` の merged commits を書き換えない。
  - `selected_comments == 0` などを新しい review completion signal として扱う設計変更はしない。

## 非交渉制約
- Public wrapper script path は維持する: `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`。
- Provider-side authority は `src/spec_dock/assets/install_root/` に置く。
- Shell wrapper には Python source code を直書きしない。
- 変更後も existing PR observation / review snapshot JSON consumers が同じ top-level contract を読めること。

## 前提
- `iss-00187` / PR #190 は 2026-06-17 に merge 済み。
- この issue は `iss-00187` の残課題を追跡する follow-up であり、同 issue の完了状態を取り消さない。

## 受け入れ条件
- AC-001:
  - アクター: maintainer / agent
  - 前提: provider-side と dogfooding mirror の `fetch_pr_review_snapshot.sh` が存在する
  - 操作: 対象 shell scripts を検索する
  - 期待結果: `python3 - <<'PY'` / `<<PY` / embedded Python body が存在しない
  - 観測点: `rg` output
- AC-002:
  - アクター: maintainer / agent
  - 前提: 抽出後の Python entrypoint が provider-side に存在する
  - 操作: 既存 tests / focused review snapshot tests を実行する
  - 期待結果: 既存 review snapshot behavior が維持される
  - 観測点: pytest / shell-level smoke output
- AC-003:
  - アクター: maintainer / agent
  - 前提:
    - provider-side source と dogfooding mirror の両方が更新対象である
  - 操作:
    - provider-side script / Python entrypoint と dogfooding mirror を比較する
  - 期待結果:
    - shipped asset と dogfooding mirror のファイル構成・意味が揃っている
  - 観測点:
    - `cmp` / `diff` / scaffold-related tests

## 例外・エッジケース
- EC-001:
  - 条件: Python entrypoint が失敗する
  - 期待: Shell wrapper は既存と同等の exit code / stderr handling を維持する
  - 観測点: focused failure-path tests
- EC-002:
  - 条件: GitHub API fixture / fake `gh` output の形が不正
  - 期待: 分離前と同じ classification / fallback / failure metadata が返る
  - 観測点: existing review snapshot tests

## 入力→出力例（必要時）
- EX-001:
  - 入力: 既存と同じ `fetch_pr_review_snapshot.sh` invocation
  - 出力: 既存と同じ JSON snapshot contract

## 用語（ドメイン語彙）
- TERM-001:
  - Shell wrapper: public script path / argument parsing / environment validation / Python entrypoint invocation を担う薄い shell script。
- TERM-002:
  - Python entrypoint: review snapshot collection and classification logic を担う独立した `.py` file。

## 未確定事項
- Q-001:
  - 質問: 抽出先 Python file の最終配置をどこにするか。
  - 選択肢:
    - A: `scripts/lib/` 配下に shell wrapper と並べる。
    - B: `scripts/lib/python/` または類似の Python 専用 subdirectory を作る。
  - 推奨案:
    - A。既存 skill-local script からの相対呼び出しを単純に保ち、今回の分離だけで directory architecture を広げすぎない。
  - 影響範囲:
    - Shell wrapper の path resolution、provider-to-mirror sync、tests の fixture path。
