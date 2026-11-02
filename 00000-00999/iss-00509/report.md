---
種別: レポート（Issue）
ID: "iss-00509"
関連GitHub: ["#509"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `finalize-artifact.py` が、`spec-dock/initiatives` が **そのクローンの** `spec-dock/.canonical`（main チェックアウト。`.git` から求める）を指すリンクのときだけ、そのリンクを通る。ほかのリンク（別の行き先、別のクローンのカタログ、名前だけ同じディレクトリ、`.git` のない worktree、カタログ自体や `initiatives` の下のリンク、Artifact のリンク）は今までの誤りで拒み、何も書かない。コマンド、引数、出力、終了コードは変わらない。
- 提供側と dogfood の写しを同じバイトにし、`static-inventory.json` の今のハッシュを更新して、0.5.0 のバイト（`105f1da7…`）を既知の古い版に足した。
- `requirement.cue` に R-02 と F-01 を足した（目的の「配布資産の更新」と「安全でない経路」を観測できる要件にするため）。
- 版は上げていない。0.5.1 の `migration.md` に書く契約の変更はない（引数・出力・エラーコード・終了コード・JSON は不変。以前拒んでいた版4のリンク経路が通るだけ）。

## Verification

| 要件 | 確かめたこと | 結果 |
|---|---|---|
| R-01, F-01 | `tests/integration/test_issue509_finalize_link.py`（15件）：リンク経由の identity と finalize、相対リンク、main 自身、別の行き先、別のクローン、名前だけ同じ、`.git` なし、カタログがリンク、下のリンク、`spec-dock` がリンク、Artifact がリンク、他のルート、実ディレクトリ | 通過 |
| R-02 | 同ファイルの inventory の検査（0.5.0 のバイトが既知の古い版、dogfood 一致）と `installation update`（0.5.0 の写しが上がる。変えたパスは当該の1つ。控えは 0.5.0 のバイト） | 通過 |
| 既存への影響 | `test_issue421_claude_skill_retirement.py` のフィクスチャが現行の資産を「過去に .claude へ写したバイト」としていたので、0.5.0 のバイトに固定した（最初の全体テストで5件失敗→修正） | 通過 |

### 仕様のレビュー（`spec-review`、spec-reviewer opus / medium）
- 1回目：P1 1件（リンク先を「そのクローンのカタログ」に特定していない）。根拠ありとして D-01 とテストを直した。2回目：合格（P0〜P3 なし）。固定した sha256：requirement `3ec225c2…`、design `9b26ab9c…`、plan `91dd19d5…`。

### コードのレビュー（`code-review`、code-reviewer sonnet / high、`809a9c67f..f500234cc`）
- 合格（P0〜P3 なし）。

### 最終品質ゲート（`final-quality-gate`、campaign `iss-00509-fqg-1`、ChatGPT のゲートは無効）
- 合格の commit：`ebab2b59b13ae8ddfd91e5ba4dc1995906c10fd5`（2回目）。quality-gate-reviewer（opus / high）：合格、網羅、P0〜P3 なし。
- テストの道：`make lint` 終了コード0、`uv run pytest` 終了コード0（3242 passed、7 skipped、1609秒）。
- 記録：`.workbench/final-quality-gate/iss-00509-fqg-1/closure.md`。

## Residual Risks / Follow-ups

- 版は #513 で上げる。`migration.md` に足す契約の変更はない。
- 配布先の `installation update` の実地の確かめは #513 で行う。
