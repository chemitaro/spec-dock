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
