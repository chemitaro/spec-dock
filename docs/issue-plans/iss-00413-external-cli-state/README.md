# Issue #413 — 外部CLIとworktreeごとの最小状態

> ローカル採用済み: 生成された17ファイルへ保有する実施記録・確定インタビューを加え、配信用入口を含む20ファイルを採用後、独立レビュー原文・対応分析を加えた22ファイルのZIPに再梱包しました。以下の「本ZIPに含めない」はChatGPT受領原本についての記録です。現行の検証・Tailscale配信は [report.md](report.md) を参照してください。

**全面差替え用の文書一式です。製品実装・製品テスト・実導入・正式Scope登録・work start・人間mergeは未着手です。文書のcommit/pushとHTML配信は実施済み。独立レビューは初回P1を補正し、再レビュー合格待ちです。**

[人間向け説明](explanation.html) → [要件定義](requirement.md) → [設計](design.md) → [実装計画](plan.md) の順で読めます。本文中の新契約のコマンドは将来仕様の例です。基準実装で動作済みという意味ではありません。

## 正本と優先順位

新しい要求の根拠は2026-09-30確定の [利用者回答](artifacts/user-decisions.md) です。これは添付からの内容保持コピーで、正式Artifactを新規登録したものではありません。旧草案のactive/work全面廃止、全writerロック、完全stateless、新規local発行は採用しません。

実装の基準は `chemitaro/spec-dock` / 指定branch `main` / `6fec3099d8759b4e5b3b393b2987534b46dfa383` です。今回接続GitHubの `git/ref/heads/main` を直接照会し、返却ref=refs/heads/main、type=commit、full SHAのASCII bytesが期待値と一致しました。他branch/default branchへのfallbackはありません。[出典と読取範囲](artifacts/source-basis.md) に事実と未確認を分けています。

RQ/ACの正本はrequirement.md、技術的選択と保存/操作順の正本はdesign.md、実装作業契約はplan.mdです。CLIの詳細は [cli-contract](artifacts/cli-contract.md)、機械構造は [data schema](artifacts/data-schema.json) と [CLI schema](artifacts/cli-schema.json)、手順は [移行runbook](artifacts/migration-runbook.md)、対応は [acceptance matrix](artifacts/acceptance-matrix.md) です。

## 差替えと残す証拠

ZIPのrootは `iss-00413-planning-pack/` です。一旦別directoryへ展開し、旧文書を外部へ保全してからpayloadだけを差し替えます。directory名は正式Scope登録の証拠ではありません。

**既存の [report.md](report.md) と [interview-worktree-start.md](artifacts/interview-worktree-start.md) はCodexが原文を保持します。本ZIPには含めず、manifestのpayload対象外です。** リンクは採用先でこの二つが隣に残る構成です。単独展開ではこの二リンクは未解決ですが、許可された外部保有依存として扱います。消去型同期（`--delete`等）を使わず、この二つを生成し直さないでください。

復旧Issueだけの許可済み例外配置は `docs/issue-plans/iss-00413-external-cli-state/`。正式import後はCLIが返したScope pathへ資料と保有証拠を保全移動し、二重正本を残しません。[旧質問票の置換](decision-questions.md) も参照してください。

## 成果物の役割

| 文書 | 主な内容 |
|---|---|
| requirement.md | 18 RQ、42 AC、変更する保証と開始条件 |
| design.md | 単一外部runtime、直接対象一件、Startだけの排他、失敗・移行・file map |
| plan.md | 17の未着手step。実装担当 `gpt-6.1-sol` / `high` |
| explanation.html | 初見の人向けの全体説明、4つのブラウザ内PlantUML図 |
| artifacts/*.md / *.json | 詳細契約・機械schema・例・出典・対応表・自己点検 |
| manifest.json | 配布payloadのsha256/bytes。自己hashは循環になるため含めない |

## HTMLと検証

本文は単一HTMLで読めます。図の初回描画には、固定版 `@plantuml/core@1.2026.6` をCDNから取得するインターネット通信が必要です。図ソースを外部render serverへ送信しません。図が描けなくても本文と図ソースを読めます。

[自己点検記録](artifacts/self-check.md) はこの文書生成環境の検査だけを示します。テンプレートは添付の行番号付きtextからUTF-8/LFで復元し、その実行JS/modalとのbyte一致を検査します。添付元端末の元file全体とのbyte同一を主張しません。製品CI、fresh wheel E2E、実OS排他、実ブラウザ/CDN描画の成否を静的検査から捏造しません。

[独立レビューと対応分析](artifacts/review-analysis.md)に原文・判定根拠・補正範囲を記録しています。
