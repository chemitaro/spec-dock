# 対象ScopeのGit pathname検索 — 採用A

2026-10-03、利用者が「Aを採用します。タスクを再開して下さい」と回答した。前回[完全レビュー分析](dogfooding-review-analysis-20261003.md)の選択肢1を採用する。これは既存の固定7field直接記録を維持しながら、現在pathの探索にGitを利用する方式である。

## 解決する問題

旧対象限定loaderは選択IDを探す前に別WTの全階層のScope-shaped entryを検証していた。無関係なfile/symlinkがあるだけで、正常な選択IssueまでunavailableとなりSyncとStartを阻害する。前回FQG-413-001 / P1はこの実装とIO契約の問題を指摘した。

## 採用した保証

- ID/refがSSOT。pathは今回のGit pathname検索と現在metadataから導出し、保存しない。
- Gitのtrackedと現在untracked pathnameを検索する。ignore対象も扱い、Git内部の名前探索の計算量は定数時間と約束しない。
- 製品のmetadata読取とnofollow path検証は対象と祖先に限定する。無関係なScopeの不正な実体は観測を妨げない。
- 検索失敗/timeout、現存対象の重複、選択chainの安全性不明は不完全とし、既知ID/refを保持する。対象が現在不存在ならstaleとする。
- Startの短い排他、readonly Sync、固定7field、三階層、通常の全tree検証は維持する。

## 実施と認定の境界

canonical AC-413-24 / D-10 / D-13 / P-08.Aが実装契約。TDD、外部wheelと実console、現在0805 WTのpackage更新、scoped commit/push、Code Review Strict、fresh Final Quality Gate v2を実施する。旧FQのraw JSON・state・会話とP2の記録は保全する。P2改修は今回に含めない。

他の4実WTの移行、GitHub #31の再open/付替え、正式#413 Start、PR作成/merge/公開はこの決定に含めない。現在の復旧planning packを使う実装と、正式Startの成否を分けて報告する。
