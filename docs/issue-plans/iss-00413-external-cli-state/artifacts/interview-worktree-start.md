# worktreeごとの作業状態と開始時排他の要件すり合わせ

- 対象: GitHub Issue #413 / `iss-00413`
- 種別: interview（利用者確認済みの証拠）
- 確定日: 2026-09-30（日本時間）
- 回答者: 利用者
- 記録者: Codex
- 配置: 復旧用Issueに対する明示済み例外配置。正式Scopeが未登録のため、SpecDock CLI発行のArtifact IDを持たない。正式Artifact登録済みとは扱わない。
- 確定: 利用者が最終整理に「OKです」「インタビュー記録確定してください。残してください」と回答。
- 正本関係: この記録は決定の証拠。R/D/Pを自動更新したものではなく、旧草案と矛盾する下記利用者決定を次の全面改訂へ反映する。

## Question

目的はGit共通管理領域へのSpecDock独自control・台帳埋込みと、それがhelpまで起動不能にする依存を解消すること。既存の重要な業務仕様を不用意に廃止したり、新機能へ範囲を広げたりせず、worktreeごとの最小限の状態と必要時観測で並行作業を扱う。

| 質問 | 内容 |
| --- | --- |
| Q1 | 重複確認・集計対象の範囲 |
| Q2 | work startとbranch作成・checkoutの関係 |
| Q3 | 一つのworktreeで同時に扱う対象数 |
| Q4 | work finishとGitHub完了・Closeの関係 |
| Q5 | Initiative/Epic/Issue三階層の維持 |
| Q6 | 新しいwork releaseコマンドの追加要否 |
| Q7 | Finish後のcheckout branch |
| Q8 | Start途中失敗時の巻戻しとエラー表示 |

## Answer

| 項目 | 確定回答 |
| --- | --- |
| Q1 | 同じcloneのmain worktreeとlinked worktreeだけ。別cloneは含めない。 |
| Q2 | work startは従来のbranch作成・checkoutまで維持。記録だけへの縮小案は不採用。 |
| Q3 | 一つのworktreeの直接の作業対象は同時に一つ。AをFinishしてからBをStartする連続利用は可能。 |
| Q4 | work finishは対象を完了し、GitHub IssueをCloseする。単なる中断・引継ぎ・選択解除をFinishと呼ばない。 |
| Q5 | Initiative/Epic/Issueの三階層を維持。従来の重要な決定事項を聞き直して要件を広げない。 |
| Q6 | work releaseは今回の要件に含めない。新規コマンド追加へ拡大しない。既存操作と通常Gitでの運用を前提にする。 |
| Q7 | Finish後もそのbranchに留まる。現状維持。自動checkoutやbranch削除を追加しない。 |
| Q8 | 自動巻戻しを行わない。成功した変更は残し、開始成功とは扱わない。Gitのcheckout失敗等の原文を見せ、独自の一般メッセージで隠さない。 |

インタビュー前からの合意と、最終整理への確認で確定した事項:

1. 短い排他制御はwork startの重複確認から開始記録までに限定する。開始後は解放する。
2. 通常のファイル編集・metadata更新へのロックや編集権限制御を追加しない。大きな全writerロックを残す案は採用しない。
3. 各worktreeが自身の作業対象を保持する。共有の永続管理台帳・独自worktree名簿・固定engine controlは設けない。
4. SyncはGitからworktree一覧を得て各作業対象を必要時に読み、同時進行する複数の対象を表示する。
5. 重複確認は直接の作業対象について行う。親Epicが同じでも別Issueの並行作業は認め、親には配下の作業中件数を表示する。
6. 作業対象に指定されていること、GitHubのOpen/Closed、Codexプロセスの実行中は別概念。常駐監視は要求しない。
7. Initiative/Epic/Issueの正式な新規作成はGitHub必須。独自採番・オフライン正式作成は復活させず、既存IDとGitHub番号を保持する。UUIDは廃止済み。
8. main worktreeを制御拠点にせず、通常の外部CLIを必要時に起動する。consumerのGit管理領域へengine/controlを埋め込まない。
9. 永続的なoperation journal、自動resume/rollback、daemon、初期cacheは設けない。

## Reflection

### 改訂が必要な旧草案

- active/work start/finishの全面廃止を撤回し、worktree固有の最小限の作業対象、branch作成・checkoutを含むStart、GitHub Closeを含むFinishへ再設計する。
- 通常のmetadataやGitHub操作などを包括する排他設計を撤回し、開始時の短い排他だけへ限定する。
- 全worktreeの保存台帳を再導入せず、Gitの一覧と各worktreeの作業対象の必要時観測でSync表示を構成する。
- work release追加や、既存の三階層・Finishの意味の変更を今回の要件に追加しない。
- Git失敗の原文・結果を保ち、処理成功の捏造や自動巻戻しを行わない。

### 次の資料作成への指示

GPT-6 Pro / ChatGPT Use Strictで、要件・設計・実装計画・補助仕様・日本語説明HTMLを全面再作成し、差分パッチではなく置換可能な実ファイルをZIPで取得する。実装担当は利用者指定のGPT-6.1 Sol / High。実装計画は担当が新たな大きな設計判断をせず進められる粒度とし、各ステップの前提、対象ファイル、具体的変更、テスト、完了条件、依存、停止条件を明記する。今回は製品実装をしない。

本記録は利用者の確定回答を保持する。未決の細部を回答者が決めたように追記せず、技術的な具体化は設計判断と分ける。一般的な機能再検討へインタビューを拡大しない。
