# iss-00415 共通CLI刷新後の操作案内・補完契約の整合 — 仕様策定入力

現在は仕様策定段階。以下は既存ChatGPT会話で完全版を作成するための入力であり、製品実装完了を表さない。

目的: 共通CLI刷新後、利用者へ示す操作案内・診断・補完を現行受付契約へ整合させる。
親: init-00079 / epic-00080。GitHub #79/#80がOPENであることを2026-10-06に確認。7件は同一刷新の操作契約不整合として扱う。

確定した候補（全てP2）:
- SD-OPS-001: legacy meta.jsonの一律rename案内を、既存.meta.jsonの確認・保全・比較を先行する安全な診断へ変更する。CLI自体の上書き不具合ではない。
- SD-OPS-002: READMEのscope create --json例へ必要な--yesを補う。
- SD-OPS-003: 通常TARGETとGitHub import refを区別し、裸番号importに--github-repoを記載する。
- SD-OPS-004: Syncの旧cache・生成物再構築・journal説明を現行の観測契約へ整合する。
- SD-OPS-005: 現行AGENTS入口の過去の0805限定適用・merge pending記述を整理し、履歴は保持する。他worktreeの移行完了を推測しない。
- SD-OPS-006: Bash/Zsh/Fishの補完候補を各leafの受付optionへ合わせる。
- SD-OPS-007: GitHub Aboutを外部installed CLIの説明へ更新する。commit外作業として別途実施証拠を残す。

非対象: root ./spec廃止、配布shim廃止、rules.md symlink削除、skillのglobal移行、旧資産一括削除、無関係なdead code整理、他worktreeの更新、製品実装、merge。
互換廃止・global共通skill＋local規則は将来の別判断。現在はproject-local skillを維持する。

根拠:
- artifacts/20261006t035502z--verified-report.md（main 0e7dc86841cb48d011270a1a2165cb6406ac0ceaでのローカル照合）
- artifacts/20261006t035503z--chatgpt-report.md（外部分析原文、advisory）
- docs/issue-plans/iss-00413-external-cli-state/（履歴のrecovery planning pack）

完全版ではRQ/AC・設計・実装手順・検証の対応を明確にする。provider-firstの資産修正、inventory/hash、fresh wheel/consumerの検証、対象worktreeへの静的適用を分ける。過去の3 passedを新規実装やfull suiteの証拠へ転用しない。
