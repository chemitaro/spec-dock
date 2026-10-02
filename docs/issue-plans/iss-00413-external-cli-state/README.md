# Issue #413 — 外部CLIとworktreeごとの最小状態

> ローカル採用済み: ChatGPTの原本を採用し、保有する実施記録・確定インタビュー・独立レビュー・実装証拠を加えています。生成時の原本ZIPと現在の採用版をmanifestで区別します。現行の製品検証は [実装記録](implementation-report.md) と [検証証拠](artifacts/implementation-acceptance-evidence.md)、文書とTailscale配信は [report.md](report.md) を参照してください。

**対応OSはLinux/macOS。Windows対応を撤回し、[P-18](plan.md#p-18)の追加作業として撤去範囲を定義しました。製品変更は、更新正本のpushと独立Implementation Brief Strictの後に行います。121228c6のLinux通常全件はPATHのみ補正して1900 passed/20 skipped、exit0。macOSは同じsourceの2b2be5e2で1916 passed/4 skipped、exit0。r12はP1一件・failでP-07修正を登録しました。新候補のStrict/FQ、人間merge、実導入、正式#413 Startは未完了。実装担当はGPT-6.1 Sol / Maxです。**

[人間向け説明](explanation.html) → [要件定義](requirement.md) → [設計](design.md) → [実装計画](plan.md) の順で読めます。操作例は候補CLIの契約です。実consumerの旧入口への適用や、live GitHub変更の完了実績とは区別します。

後続のWindowsDirectoryは、保持した親handleから子を開く方式へ補強しました。[API境界のRed→Greenと確認結果](artifacts/windows-directory-anchor.md)と[過去のmacOS全件の記録](artifacts/macos-full-3b0c69e8.md)を参照してください。Linux全件の候補から製品source差分があり、その結果を後続候補の全面合格へ読み替えません。旧手動結果も別sourceとして保持しています。このWindows専用実装は最新OS決定によりP-18の撤去対象です。

[WindowsのJSON reader](artifacts/windows-json-read.md)を親handleへ接続し、それを含む[clean6032621cの全件](artifacts/macos-full-6032621c.md)は成功しました。後続の[Scope公開の原語確認](artifacts/scope-publication-capability.md)は、既知の未対応をGitHub変更前に拒否する修正です。native Windowsと専用保存接続の完成義務は撤回し、P-18で専用コードを撤去します。

先行候補の[clean75ac5760全件](artifacts/macos-full-75ac5760.md)と[インストール済みCLIの手動14操作](artifacts/manual-console-75ac5760.md)も保存しています。Scope公開の事前判定を含むsourceでの実結果であり、後続候補へ件数を合算しません。

後続の[Startの保存原語確認](artifacts/start-publication-capability.md)は、公開が必要なStartで既知の未対応をGit変更前に拒否します。三階層・dry-run・旧記録の保全と公開不要の同一Startを含む16組、および関連8 suiteがMac3.12/実3.10で各266件成功し、通常lintも成功しました。この変更を含む[clean2b2be5e2の通常全件](artifacts/macos-full-2b2be5e2.md)は1916 passed/4 skipped、exit0。[同じ製品sourceの手動14操作](artifacts/manual-console-2b2be5e2.md)と[原文](artifacts/manual-console-2b2be5e2.json)を保存しました。Windows・live GitHub・現在候補Strict/FQを完了扱いにはしません。

## 正本と優先順位

OS範囲の最上位authorityは[2026-10-02の決定](artifacts/os-support-decision.md)です。それ以外の新しい要求の根拠は2026-09-30確定の [利用者回答](artifacts/user-decisions.md) です。これは添付からの内容保持コピーで、正式Artifactを新規登録したものではありません。旧草案のactive/work全面廃止、全writerロック、完全stateless、新規local発行は採用しません。

実装の基準は `chemitaro/spec-dock` / 指定branch `main` / `6fec3099d8759b4e5b3b393b2987534b46dfa383` です。今回接続GitHubの `git/ref/heads/main` を直接照会し、返却ref=refs/heads/main、type=commit、full SHAのASCII bytesが期待値と一致しました。他branch/default branchへのfallbackはありません。[出典と読取範囲](artifacts/source-basis.md) に事実と未確認を分けています。

RQ/ACの正本はrequirement.md、技術的選択と保存/操作順の正本はdesign.md、実装作業契約はplan.mdです。CLIの詳細は [cli-contract](artifacts/cli-contract.md)、機械構造は [data schema](artifacts/data-schema.json) と [CLI schema](artifacts/cli-schema.json)、手順は [移行runbook](artifacts/migration-runbook.md)、対応は [acceptance matrix](artifacts/acceptance-matrix.md) です。

## 差替えと残す証拠

ZIPのrootは `iss-00413-planning-pack/` です。一旦別directoryへ展開し、旧文書を外部へ保全してからpayloadだけを差し替えます。directory名は正式Scope登録の証拠ではありません。

**既存の [report.md](report.md) と [interview-worktree-start.md](artifacts/interview-worktree-start.md) はCodexが原文を保持し、採用版ZIPにも含めます。** ChatGPT原本のpayload対象外だったという履歴はmanifestに残します。消去型同期（`--delete`等）を使わず、保有する原文を生成し直さないでください。

復旧Issueだけの許可済み例外配置は `docs/issue-plans/iss-00413-external-cli-state/`。正式import後はCLIが返したScope pathへ資料と保有証拠を保全移動し、二重正本を残しません。[旧質問票の置換](decision-questions.md) も参照してください。

## 成果物の役割

| 文書 | 主な内容 |
|---|---|
| requirement.md | 18 RQ、42 AC、変更する保証と開始条件 |
| design.md | 単一外部runtime、直接対象一件、Startだけの排他、失敗・移行・file map |
| plan.md | 18 step（P-18はP-13前）の作業契約と進捗。実装担当 `gpt-6.1-sol` / `max` |
| explanation.html | 初見の人向けの全体説明、4つのブラウザ内PlantUML図 |
| artifacts/*.md / *.json | 詳細契約・機械schema・例・出典・対応表・自己点検 |
| manifest.json | 配布payloadのsha256/bytes。自己hashは循環になるため含めない |
| implementation-report.md / artifacts/implementation-acceptance-evidence.md | 候補SHAごとの製品試験・手動操作・未完了事項。生成時の自己点検と分離 |

## HTMLと検証

本文は単一HTMLで読めます。図の初回描画には、固定版 `@plantuml/core@1.2026.6` をCDNから取得するインターネット通信が必要です。図ソースを外部render serverへ送信しません。図が描けなくても本文と図ソースを読めます。

[自己点検記録](artifacts/self-check.md) はこの文書生成環境の検査だけを示します。テンプレートは添付の行番号付きtextからUTF-8/LFで復元し、その実行JS/modalとのbyte一致を検査します。添付元端末の元file全体とのbyte同一を主張しません。製品CI、fresh wheel E2E、実OS排他、実ブラウザ/CDN描画の成否を静的検査から捏造しません。

[独立レビューと対応分析](artifacts/review-analysis.md)に原文・判定根拠・補正範囲を記録しています。
