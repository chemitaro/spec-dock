# Issue #413 実施記録

最終更新: 2026-09-30。仕様策定完了、製品実装・実移行は未着手。
GitHub: https://github.com/chemitaro/spec-dock/issues/413
作業branch: `codex/iss-00413-external-cli-state`
基準HEAD: `6fec3099d8759b4e5b3b393b2987534b46dfa383`

## 現行版: インタビュー確定後の全面改訂（2026-09-30）

確定したインタビューを `artifacts/interview-worktree-start.md` に保持し、その原文を添付してChatGPT Use Strict / GPT-6 Proへ全ファイルの再作成を依頼した。現行版は18要件・42受け入れ条件・17実装step。実装予定は `gpt-6.1-sol` / `high` で、対象file、依存、具体的変更順、入力/出力、Red/Green、完了条件、失敗時の戻り先を各stepに記載した。以下の旧版記録は履歴であり、現行R/D/Pを上書きする仕様ではない。

- clean mainからStrict実行。基準HEAD/上流は `6fec3099d8759b4e5b3b393b2987534b46dfa383`。回答もGitHub direct refの一致を報告。
- session: `specdock-worktree-start-planning`。終了0。要求model=`gpt-6-pro`、UI選択=`Latest` / thinking=`Pro`、両検証済み。Oracle実行記録48m12s。
- 会話: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abc8bd1-c5e8-83e8-a05f-51d01a0c55e3
- 生成ZIP: 125,642 bytes / 17 files。SHA-256 `7d8534010862d1187a79f005a64d97686ac729b4beb6b3556e1bad134dadd949`。
- 自動取得はZIPを保存できず回答のみ保持。既存回答のDownloadボタンをChromeで操作し、123 KB・完了を確認して取得。再送なし。中間harvestは接続portの所有process不一致を確認し、自分のharvestだけを停止した。
- 生成ZIPのCRC、安全な単一root、UTF-8、16 payloadのbytes/hash一致を確認。旧packと受領原本は親Epicのignored `.workbench/iss-00413-revision/` に保全。
- ローカルで2 JSON Schema、同梱12例、既存240 metadataの適合とbyte不変、workspace byte不変、18 RQ / 42 AC / 17 step、353内部リンクを確認。テンプレートの実行JSと共有modal末尾は一致。
- ローカルHTML validator: 4/4図のinline SVG、拡大、キーボード、倍率制限、focus trap、閉じる、focus復帰が合格。
- R/D/P・HTML・補助契約を部分修正でなく生成版へ全面差替え。reportの旧履歴と確定interviewを保持。README/manifestのみローカル採用状況を追記する。

配信: http://100.85.74.8:8765/specdock-issue-413/explanation.html 。説明からの相対リンクも含めHTTP200・no-store・正本bytes一致を確認した。IABで4図の描画完了、幅1280px/390pxの本文表示と全体横overflowなしを確認。新設index.htmlは説明への入口だけで、設計の第二正本ではない。

実装・製品試験・実移行・正式Scope import/work start・GitHub投稿・commit/pushは未実施。独立Strict仕様レビューpassとは扱わない。OS排他adapter等の製品保証は後続実装の検証対象。

## 初回著述の結果（現行仕様は後続の全面改訂を参照）

利用者が採用した「簡素化優先」に基づき、ChatGPT Use Strictで要件・設計・実装計画・補助契約・日本語HTMLをZIPとして作成した。取得後、Codexが既存草案をこのdirectoryで差し替え、現行データとの照合による互換性補正、ブラウザ検証、Tailscale配信を実施した。20要件・40受け入れ条件・16実装stepを含む。

このdirectoryは利用者の復旧例外許可に基づく、正式Scope登録までの正本配置先。`.meta.json`、active、control、registryを手作成していない。製品コード・既存仕様metadata・Git refsは変更していない。commit/push、GitHub Issue本文の更新は本作業では未実施。独立したStrict仕様レビューのpassとは扱わない。

## 外部著述と取得の証拠

- wrapper: `chatgpt-use-strict/scripts/oracle-chatgpt`。利用者が許可したclean mainから実行。
- session: `specdock-simplified-planning-pack`。Oracle完了記録38m50s。
- 会話: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abc69d2-cc9c-83ee-a3ec-bfd539a5e53e
- 指定: browser、model `gpt-6-pro`、thinking `pro`、model strategy `select`。
- OracleのUI証拠: model target/resolved=`Latest`、verified=true。thinking=`Pro`、verified=true。内部モデルの自己申告ではなく、指定とUIの照合記録として扱う。
- 回答はGitHub connectorでmainのfull tipが基準SHAに一致したことを報告した。引用された7 source blob SHAをローカル実体とも照合し一致を確認した。
- 元ZIP: `iss-00413-planning-pack.zip`、99,482 bytes、12ファイル。
- 元ZIP SHA-256: `04ae7bdf587945b5a4da5bc5575758cf456dc568deb58d52b1503b59cda5de93`。
- 自動downloadが失敗したが、送信済み会話をharvestで再表示し、同じ回答のdownloadボタンからChromeで取得。UIの97.2 KB・完了表示、実ファイル、ZIP CRC、manifestの11hashを確認した。プロンプトの再送はしていない。
- 元回答/metadataはOracle sessionに保持。元ZIPと差替え前6文書のZIPは親Epicのignored Workbench `iss-00413-authoring/` に保持した。

前段のfollowup試行 `required-strict-github-connector-verificati-1386` はchat-mode-selectionで送信前に失敗し、既存会話に新しい依頼がないことを確認してから上記の新規著述を実行した。Oracle製品コードの変更やAPIへの切替はしていない。

## 初回採用時のローカル照合と補正（後述の改訂前）

生成版には以下の2点が既存データ保全要件と矛盾していたため、Codexがschemaと対応する設計・計画・HTMLを補正した。

1. `init-local-00002` / `init-local-00003` はlocal形式IDだが、backend=githubでIssue #39/#31に紐づく。既存numeric IDの字面からbackendを制約してはいけない。当初は新規local案と既存numeric保全を分けたが、前者は利用者確定要件に反していたため本改訂で撤去した。
2. 現行workspace.jsonにはschema_versionとwriter_protocolしかない。title/project_linkageを新schemaの必須fieldから外し、移行時に架空の値を補完しないことを明記した。

この補正は新機能の追加ではなく、RQ-413-05の既存ID・linkage・未知field保全との整合を取るもの。元ZIPは変更せず、配布用ZIPを採用後文書から再作成する。旧decision-questions.mdは確定方針の正本への案内に置き換えた。

## 初回採用時の検証（改訂前の履歴）

| 対象 | 実績 |
| --- | --- |
| 元ZIP | CRC正常、単一root、重複/traversal/symlinkなし、全12ファイルUTF-8、manifest11hash一致 |
| 現行CLI対応 | 基準catalogの44 leafが一覧と完全一致 |
| 現行データとschema | 240 Scope＋workspaceをメモリ上でschema4へ変換し、補正後のJSON Schemaに241件すべて適合。実データのwriteなし |
| schema自体・文中例 | JSON Schema draft2020-12の2schemaと、文中3JSON例が適合 |
| 文書の構造 | 20RQ、40AC、16Plan。相対link/anchorを検査 |
| HTML実行部分 | 元テンプレートの実行JS・event handlerが一致。PlantUML coreは1.2026.6固定 |
| HTML専用validator | 採用先の最終HTMLでexit0。4/4図のSVG描画、click/Enter/Space、拡大限界、focus trap、閉じる、focus復帰に合格 |
| 目視 | デスクトップおよび390px viewport指定（内容幅375px）で本文・目次・構成図を確認。文書全体の横overflowなし。図は拡大可能 |
| OS排他の小確認 | このmacOS環境で既存scratch directoryへのflock取得中、別processの取得がBlockingIOErrorになることだけを確認。全OS製品試験とは扱わない |
| 配信 | HTTP200、Cache-Control:no-store、配信bytesと正本HTMLが一致 |

製品コードのmake lint/uv run pytest、wheel install、Windows/Linux排他、製品の移行処理、GitHubへのwriteは今回未実施。文書schemaの検証を製品移行成功に読み替えない。

## HTML配信

- 正本: `explanation.html`（このdirectory）。
- URL: http://100.85.74.8:8765/specdock-issue-413-explanation.html
- publication entry: `/Users/iwasawayuuta/.local/share/tailscale-html-preview/public/specdock-issue-413-explanation.html`
- モード: 正本への管理されたlive symlink。更新後は同じURLを再読込する。
- 使用skill: `tailscale-html-preview`。外部公開Funnelではなく、同じtailnet向けの配信。
- 図の初回描画は固定CDNへの通信が必要。本文はHTML内で完結。

配信解除（資料本体は削除しない）:

```text
/Users/iwasawayuuta/.agents/skills/tailscale-html-preview/scripts/tailscale-html-preview unpublish specdock-issue-413-explanation.html
```

## 前段の復旧確認と未完了事項

前段でGitHub #413と通常Git branchを作成済みだが、SpecDockのScope登録・work startは成功していない。`./spec -h` はcontrol不足でexit3。公式candidateのscope create/work start dry-runもcontrolとの不一致でPRECONDITION_FAILED、effects=[]だった。構造検証だけはvalid=true/node_count=240となったが、業務操作の復旧証明ではない。

以前の外部共有台帳案の文書作成sessionは `required-strict-github-connector-verificati-1381`。その15RQ/26AC/S00〜S11と未回答質問は、今回の簡素化設計で置換した。前段の詳細reportを含む元6文書はprior-draft.zipへ保全している。

新設計ではwork start/active自体を廃止する。将来の完了条件は、新CLIの実装・検証・許可されたcutover後に既存#413をimportし、本一式を生成Scopeへ保全移動すること。手動metadata作成や架空のwork start成功で埋めない。正式登録・製品実装・移行・人間mergeは引き続き未実施である。


## 2026-09-30 改訂: GitHub必須・UUID廃止済みの反映

利用者は「正式な新規作成は必ずGitHub」「オフライン作成を残す記述は古い情報」「UUID導入はすでに完全廃止」と明示した。これは未決の選択肢ではなく確定要件であり、旧#409等の過去契約より優先する。

ChatGPT Use Strictをclean mainから直接実行した。sessionは `specdock-github-id-necessity`、指定は `gpt-6-pro` / thinking `pro`。Oracleは14m23sで正常完了し、UIのLatest/Pro照合はいずれもverified=true。回答はGitHub connectorでmainのfull SHA `6fec3099d8759b4e5b3b393b2987534b46dfa383` 一致を確認した。会話は[分析結果](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abc7787-20cc-83e8-9c8f-76ba97efefcd)。回答原文と改訂前ZIPは親Epicのignored Workbench `iss-00413-id-review/` に保持した。

回答はGitHub採番限定ならUUID不要と結論し、前案の新規local UUID導入を撤回した。依頼送信後に届いた利用者の確定指示により、回答に残った「オフライン正式発行は必要か」という確認は解消済み。Codexは現行create/import/scaffold、既存240件、旧writer admissionを照合してから改訂した。全240件はGitHub backendで、旧local綴りの2件もGitHub #39/#31への既存linkageを保持する。

変更内容:

- 新規ScopeはGitHub create/importだけ。新規local作成、独自採番、UUID形式・短縮selector・関連の導入計画を撤去。
- GitHub採番の一意性と現在tree内の二重登録検査を分離。単一repository境界を維持し、番号をmax+1で予測しない。
- 既存ID/path/backend/linkageを保持。旧localデータの保全互換性を新規作成要件と区別。
- Scope/workspaceのschema3を維持。全Scopeの3→4変換を撤去し、workspaceのwriter_protocol切替だけに縮小。新protocolは新CLIのguardであり、旧writer停止の証明ではない。
- R/D/P、CLI契約、schema、移行手順、対応表、README、説明HTMLを同期。旧資料は履歴として扱い、現行の確定要件を逆転させない。

改訂後の検証:

| 検証 | 結果 |
| --- | --- |
| 既存Scope | 240件をschema変換せずJSON Schemaへ照合し全件適合。実データwriteなし |
| workspace | writer_protocolだけをメモリ上で変更したschema3レコードが適合。実file変更なし |
| schema/例 | JSON Schema 2件、文書JSON例3件が適合。既存localは受理、新規local/UUID/ゼロ番号は拒否、6桁番号は受理 |
| 文書整合 | 20 RQ・40 AC・16 step、内部リンク361件、一意HTML ID115件を確認。実行JSは改訂前とbyte一致 |
| 実ブラウザ | 最終validatorで4/4 SVG、拡大modalのクリック/キーボード/倍率/フォーカス/終了が合格。一度Chrome起動timeoutで終了後、同一validatorを再実行して合格 |
| 目視 | 既存IABページをrefreshし、GitHub必須・UUID廃止済みの表示を確認。390px指定のモバイル検証でも文書横overflowなし。temporary viewportは復元 |
| 配信 | 既存Tailscale URLがHTTP200・no-storeで、配信bytesと正本HTMLが一致 |

改訂版ZIPとmanifestを再生成した。製品コード・実Scope metadata・GitHub本文は変更していない。製品試験・実移行・formal scope import・commit/pushは未実施。本分析と文書検証を、独立Strict仕様レビューpassや製品実装完了とは扱わない。


## 2026-09-30 追記: engine/control/stateの役割と導入背景

利用者の質問を受け、Codexが#409の要件・設計・計画・報告、導入commit、基準HEADの実コードを調査した。HTMLに `engine-history` 章を追加し、処理本体・locator・control・active・registry・journal・lockを区別した。導入理由、保存場所、時系列、新規branchを伴うwork startの処理例、helpがcontrolで停止する経路、簡素化で保証範囲を減らす理由を説明した。根拠をsource-basisのS-06にも記録した。

設計文書7a10e783の時点でコード混在防止の理由が存在し、その後f44cc4f8、d96065a2等で制御・固定engineが実装されたことを確認した。engine本体はcheckout外であり、engine.jsonはその場所とdigestを記録するファイルである。担当エージェントの内心、個別保存先への利用者承認、実環境でcontrolが欠落した直接原因は断定していない。GitHub必須・UUID廃止済みを含む確定要件は維持した。

今回の検証: 240件の既存Scopeとメモリ上のworkspaceをschema照合、JSON Schema 2件・例3件、20 RQ・40 AC・16 step、内部リンク366件・一意HTML ID123件を確認。実行JSは改訂前と一致。HTML validatorは4/4 SVG描画と拡大modalのキーボード・フォーカス・終了動作で合格。既存IABの新章表示を目視し、幅585pxで文書全体の横overflowなし（表は自身の横スクロール領域）。Tailscale URLはHTTP200・no-store、配信bytesと正本が一致。manifestと14ファイルのZIPを再生成し、CRC・ハッシュ・展開相当bytes一致を検査した。

製品コード・正式metadata・GitHub情報の変更、製品試験、移行、commit/pushは行っていない。今回は説明資料の追記であり、外部ChatGPT分析の新規実行や独立Strict仕様レビューではない。


## 2026-09-30 独立仕様レビュー初回とP1補正

GPT-6 Proの初回レビューは内容上fail / P1一件。JSON形式不備によってレビューを破棄しないという利用者指示を記録し、[原文と対応分析](artifacts/review-analysis.md)を保全した。既存D-10のscopesがCLI契約/schemaから欠落していたため、未選択Scopeのlifecycle行・例・P-08/AC-23検証を補正した。製品コードは未変更、再レビュー合格は未取得。

## 2026-09-30 独立仕様再レビュー合格

利用者の新規会話許可を受け、chatgpt-spec-review-strict / GPT-6 Pro / Proで候補7e895803cba0d43957e504c9f97637d307bc6a78を再レビューした。session specdock-413-spec-rereviewはexit0、pass・指摘0件。初回P1の解消と指定15文書全体の実装開始可能性が確認された。[原文・モデル証拠・判断](artifacts/review-analysis.md)を保全した。

回答の引用マーカーによるJSON形式不備は今回もあるが、利用者の明示指示に従って原文の意味を採用した。仕様の規範JSON schemaの検査とは区別する。

合格後の変更はレビュー記録、README/HTMLの進捗表示、manifestと配送ZIPのみ。要件・設計・計画・規範契約を変更していない。GPT-6.1 Sol / HighはP-01から実装開始可能。製品コード・製品テスト・正式import/Start・人間merge・実環境移行は未実施。

## 2026-10-02 追記: 候補実装の実績と説明資料の現在表示

ここまでの実装・試験は[実装記録](implementation-report.md)と[現在の検証証拠](artifacts/implementation-acceptance-evidence.md)へ残す。仕様生成時の「製品未着手」は過去の記録として保持し、README/説明HTMLの現在表示を更新した。実装は利用者の追加指示によってGPT-6.1 Sol / Max。通常wheel/実Gitの手動確認はstateful fake ghを用いた別fixtureで行い、live GitHub・実consumerへの導入と区別する。

clean 8a70a8b3のLinux通常全pytestは1832 passed/18 skipped/exit0、macOSは1 failed/1847 passed/2 skipped/exit1。readonly比較不一致の原因は未確定。全件成功や最終認定を表示しない。Windows保存adapter/native受入、現在コードのStrict/FQ、人間merge、正式#413 import/Startと実導入も未完了。

説明HTMLは、現在の検証状況、未完了事項、手動確認の範囲を冒頭から単独で読めるようにした。PlantUML四図・実行JS・共有modalは変更せず、更新後の実ブラウザvalidator、ファイル/ZIP検査、既存Tailscale URLのsource bytes一致を別途記録する。要件・設計の判断条件と確定インタビューを再生成していない。

更新後の実ブラウザvalidatorは4/4 SVG、クリック/キーボード/倍率範囲/フォーカストラップ/終了/フォーカス復帰に合格。sandbox内のChrome起動timeoutはexit1として残し、同一validatorの実行許可付き再実行でexit0を取得した。四図と全script・共有modalのhashは改訂前と一致。IABの390px検査でdocument幅375px（scrollbar除く）、横overflowなし、SVG四件と現在表示を確認し、viewportを復元して所有する検証tabを閉じた。

従来の単体HTML URLでは`requirement.md`がrootへ解決されて404になることを発見。同じ名前の公開link一件を、`preview-entry.html`を指す入口へ置換した。正本は削除せず、他の公開entryやserverを変更しない。ブラウザで旧URLの`#progress`を維持したまま`/specdock-issue-413/explanation.html#progress`へ移動し、資料リンクがsite配下へ解決されることを確認した。source文書八件がHTTP200/no-store・bytes一致。canonical URLは `http://100.85.74.8:8765/specdock-issue-413/explanation.html`。実ファイル/manifest/ZIPのhash・CRC・展開相当比較は更新した採用版の検査記録へ残す。

## 2026-10-02 追記: macOS最新全件とWindows接続条件

clean 1e5d2586のmacOS通常全件は1848 passed/2 skipped（424.21秒）、exit0だった。Linux全件/手動consoleの8a70a8b3とは製品sourceが同一だが、SHA別の結果として保持した。元のmacOS失敗を撤回せず、traceがfixture setupと子processまでの限定観測であることも[調査記録](artifacts/validation-readonly-investigation.md)へ保存した。

HTMLの最新全件表示を更新し、同じ公式validatorでstatic四図、4/4 inline SVG、zoom/keyboard/focusの成功を取得した。IABで最新結果の本文を確認し、390pxではdocument幅375px・progress幅355pxで横overflowなし。requirementへのURLもsite配下を向いた。viewportを元へ戻して所有するtabを閉じた。IABのSVG用selectorは対象を一致検出できなかったため、その件数は描画証拠に使わず、公式validatorの独立した四図検査と区別する。

[Windows接続箇所](artifacts/windows-adapter-connection-review.md)を現sourceとMicrosoft一次資料へ照合した。Win32 mutex/identityのAPI経路と、未接続の保存/公開/process経路を区別する。directory同期の成立を資料だけから仮定せず、P-03のImplementation Brief Strict用promptをWorkbenchへ準備した。外部送信・Windows保存接続・NTFS受入は未実施。通常pushの先行承認回答とFQ v2 pilotの選択回答を待ち、現在候補のStrict/FQを実行済みと記録しない。

## 2026-10-02 追記: Windows物理識別の安全な子open

WindowsDirectoryの各階層の絶対path openでは、途中の親pathが差し替わると新しい子を開き得ることをAPI境界Redで確認した。保持した親handleに対するNtOpenFileへ変更し、未完了openのhandle解放もRed→Greenで確認。[実装と証拠](artifacts/windows-directory-anchor.md)を保存した。通常make lintとMac/実3.10の関連五suiteは成功、native Windows/NTFSは未実施。現在候補の製品source差分をHTML/READMEへ明示し、過去の全件・手動結果の対象SHAを保持する。要件・設計・確定インタビューは変更しない。

説明HTMLの公式validatorは四図のstatic検査、4/4 SVG、拡大・keyboard・focusで成功（exit0）。実行JS/style/共有modalは既存bytesを保持した。採用版のUTF-8・二schema・13例・内部リンク・manifest/ZIPのCRCとbytes/hashを検査し、Tailscaleの九文書とmanifestもHTTP200/no-storeで正本bytesへ照合した。これは資料の確認であり、native Windows/現在候補のStrict/FQの合格ではない。

## 2026-10-02 追記: 最新候補の全件と診断runnerの修正

Windows補強を含むclean 3b0c69e8のmacOS全件は、最終1853 passed/2 skipped（402.78秒）、exit0。[原文・原因箇所・再確認](artifacts/macos-full-3b0c69e8.md)を保存した。初回の二失敗はCodexが作成したignored runnerのmain guard不足であり、製品source/testsを変更せずに修正した。旧候補のreadonly比較不一致や、native Windowsの受入と混同しない。説明HTML/READMEの最新候補・件数を更新し、別sourceのLinux/手動結果を保持する。現在候補のStrict/FQとWindows保存/nativeは未完了。

更新後の公式HTML validatorは四図のstatic検査、4/4 SVGと拡大・keyboard・focusでexit0。IABの390px表示でdocument幅375px、検証状況section幅355px、本文の横はみ出しがないことと最新1853件の表示を確認した。表は表内の横スクロールで読み、viewportを1280pxへ戻して確認専用tabを閉じた。十文書とmanifestの十一sourceをTailscale経由でHTTP200/no-store/正本bytesへ照合した。採用版ZIPは109 memberで、二schema、13例、438内部リンク、33 HTML ID、CRC/bytes/hashを確認した。これらは資料の検証であり、製品の未完了受入を埋める証拠にはしない。

## 2026-10-02 追記: Windows JSON reader

[Windows JSON読取](artifacts/windows-json-read.md)のRed→Greenと、Mac3.12/実3.10各58 passed/3 skipped、通常lintを保存した。説明HTMLには全件試験後の追加変更として記載し、旧SHAの全件成功と今回の境界試験を分けた。新HTMLの公式validatorは四図のstatic/4 SVG/拡大/keyboard/focusでexit0。390pxでdocument375px・section355pxを確認し、追加した58件の記載と全件未完了の説明も表示された。override解除後の新規空tabは既定1280pxで、すべての確認専用tabを閉じた。十一文書とmanifestの十二sourceをHTTP200/no-store/正本bytesへ照合し、採用ZIPのschema/例/内部リンク/CRCとbytes/hashを検査した。native Windows/保存接続/Strict/FQの完了とはしない。


## 2026-10-02 追記: reader全件とScope原語の事前判定

[clean6032621cの全件](artifacts/macos-full-6032621c.md)は通常pytestで1876 passed/4 skipped（366.99秒）、exit0。この後の[Scope事前判定](artifacts/scope-publication-capability.md)もTDDで修正し、関連九suiteはMac3.12/実3.10で各271 passed/2 skipped、通常lint成功。説明資料は候補別の結果と後続修正を区別し、全Windows writerが副作用前に止まるという広すぎる説明を除いた。Windows保存/nativeとfresh Strict/FQは未完了。文書・配信の検査結果は別途記録する。

新HTMLの公式validatorは四図のstatic/4 SVG、拡大・keyboard・focusでexit0。IABの390pxではdocument375px/section355px、1876件と271件の表示、後続sourceの全件未完了の説明を確認した。viewport解除後の新規空tabで既定1280pxを照合し、確認専用tabを全て閉じた。十三文書とmanifestの十四sourceをTailscale経由でHTTP200/no-store/正本bytesに照合した。採用ZIPの112 member/111 payload、二schema/13例/462内部リンク/33 HTML ID、CRC/bytes/hashを検査した。これは文書の確認であり、Windows保存/nativeや現在候補Strict/FQの代わりにはしない。


## 2026-10-02 追記: 親GitHub取得より先の能力確認

Scope原語確認の最終差分でEpicのparent GETの順序も再現した（8 failed/63 deselected、3.83秒）。判定を親GET前へ移して同じ選択を8 passed/63 deselected（1.45秒）にし、三階層の24組合せを含む関連九suiteはMac3.12で287 passed/2 skipped（68.15秒）、実3.10で287 passed/2 skipped（68.17秒）。最終の通常lintもRuff300/mypy219でexit0。先の八case・271件は途中段階の実結果として保全し、今回の最終sourceと区別する。Windows保存/native、後続候補全件とStrict/FQは引き続き必要。

最終HTMLも公式validatorの四図・拡大/keyboard/focusをexit0で再確認。390pxでdocument375px/section355px、三階層24ケースと287件を読み取れた。overrideを解除し新規空tabの1280pxを照合して、確認専用tabを閉じた。配信bytesとZIPは、この最終本文を対象に再照合する。


## 2026-10-02 clean75ac5760の全件と通常install CLIの手動確認

Scope公開の事前判定を通常checkpoint75ac5760へ保存し、parent6032621c・branch不変・cleanを確認した。[同候補のmacOS全件](artifacts/macos-full-75ac5760.md)は通常uv run pytestを直接実行して1900 passed/4 skipped（388.57秒）、実exit0。実3.12.11・prefix/providerと実行前後のHEAD/clean/source不変を照合した。旧候補・関連287件の結果へ合算しない。

[同じ製品sourceの通常install CLI](artifacts/manual-console-75ac5760.md)は14操作を個別実行した。非editable wheel・外部fresh venv・pip check・元provider pathを参照不能にしたsite-packages consoleを使用し、pytest bodyは呼び出していない。[原文](artifacts/manual-console-75ac5760.json)に実exit/stdout/stderr/前後entryと28件の外部gh requestを保持する。Start重複拒否、兄弟二件のSync、Close確認後の捕捉解除とbranch保持、次Issue開始、native hookエラーのpartialと自動rollbackなしを確認。Git本来のbranch/HEAD/reflog以外の独自controlは作らず、tracked仕様とC/B recordを照合した。

GitHub境界はstateful fake ghであり、live GitHubや本consumerは変更していない。Windows保存/各公開/process/native、現在候補Strict/FQ、人間merge後のP-16/17は未完了。旧macOS比較不一致・旧runner不備・別sourceのLinux/手動の証拠を保持し、今回の成功で撤回しない。
公式HTML validatorは四図のstatic・4/4 SVG・拡大/keyboard/focusで実exit0。IABの390pxではdocument375px/section355px、横overflowなし、最新75ac5760・1,900件・手動14操作・Windows未完了の表示を確認した。overrideを解除し新規空tabの1280pxを照合し、確認専用tabを閉じた。十六payloadとmanifestの十七sourceをTailscale経由でHTTP200/no-store/正本bytesへ照合した。採用ZIPは115 member/114 payload、二schema/13例/482内部リンク/33 HTML ID、CRC/bytes/hashを確認した。資料の確認と製品の未完了gateを分ける。
