# 今回の文書自己点検

実施日: 2026-09-30。対象は本planning packの実ファイルだけです。**製品実装・製品テスト・実install・実移行・正式Scope import・work start・commit/push・公開・人間mergeは未実施です。** 文書の静的検査を製品AC全体のpass、独立した仕様レビューの承認、実ブラウザ成功に読み替えません。

## 実行して確認した項目

| 検査 | 実測・判定 |
|---|---|
| Strict検証 | 接続GitHubで指定repoのrefs/heads/mainを直接取得。full tipとexpected_shaの40桁ASCII bytesが完全一致。他branch/defaultへのfallbackなし |
| 実ファイル | UTF-8のpayload16件とmanifest.jsonの計17件。単一root iss-00413-planning-pack/ |
| ZIP構造 | 絶対path、traversal、backslash、重複name、casefold衝突、symlinkのentryは0。全17 entryの展開bytesが生成実体と一致 |
| ZIP integrity | Python zipfileの全CRC検査が正常。manifestに載せた16件のsha256/bytesが実ファイルとZIP memberの両方に一致 |
| JSON | 全JSONをparse。data-schema.json / cli-schema.jsonのDraft 2020-12構造と全内部$refを確認 |
| 同梱実例 | データ4件、CLI 8件の計12件が適合。説明用fixtureであり現環境の実測値ではない |
| 追加のschema境界 | 保全・新規発行の正常5件を受理、異常35件を拒否。詳細は下表 |
| 対応 | 18 RQ、42 AC、14設計節、17 Planの定義と参照が整合。各ACの判定本文が要件/対応表で一致し、実装stepにも対応する |
| 計画の構造 | 各stepに未着手、前提/依存、読む節、所有file、変更順、禁止、入力/出力、Red→Green、コマンド、完了、RQ/AC、停止先がある |
| CLI一覧 | connectorで確認したcatalogから転記した44 leafの名前/順序と対応表を照合。重複0、追加leaf0。転記元のsource全文をcontainerで自動parseした検査ではない |
| 相互リンク | 353件のローカル参照を検査。生成済み文書へのpath/anchor不明0。意図した未同梱先は下記2pathだけ（参照出現10箇所） |
| HTML構造 | 一意ID32件。top / engine-history / ids、目次、共有modal一つ、図ソース4件と対応描画先を確認 |
| PlantUML保存 | 各図をtext/plainへ一度だけ格納。開始/終了、title、対象IDを確認。remote include/import、外部render URL、事前生成の図SVG/PNG、編集UIは0。modalの元SVGアイコンは保持 |
| 実行JS | script要素3件をtag/属性/本文ごと復元templateとbyte比較し一致。本文のある2件はNodeのsyntax checkでexit0。CDNのJS本体をNodeで実行したものではない |
| 共有modal | 復元templateの閉じmainからEOFまでをbyte一致で保持。modal、onerror、renderToString callback、診断SVG拒否、可視状態、window.__plantumlDocumentState、zoomを変更していない |
| 利用者回答 | 添付から復元したuser-decisions.mdと同梱コピーがbyte一致。新しい技術判断を利用者の回答に追記していない |
| 保有証拠 | report.mdとartifacts/interview-worktree-start.mdは生成・上書きせず、ZIPとpayload hash一覧の対象外 |

本文・表の不整合を見つけた後、表内pipeのescape、リンク先anchor、Finishのdry-run承認と部分完了の説明、図ラベルの改行表記を補正して再検査しました。これらは文書生成中の修正であり、製品testのRed/Green実績ではありません。

## JSとmodalの追跡hash

hashはraw UTF-8 markupのSHA-256です。添付は行番号付きtextからLFで復元しています。ユーザー端末の元file全体の改行bytesを直接照合したという意味ではありません。

| raw区間 | sha256 |
|---|---|
| 実行script要素 1 | `79525b1f8074a3f215fb3d8afada0d3d86d0118ebef3badf1381a76811d28b10` |
| 実行script要素 2 | `1604bf59d4814b04a169a576cecffb9769d56430a83602f55ca156c38fa88f0a` |
| 実行script要素 3 | `ba01cdd7e63af7489316ab0ff834cd77fece282a340db7bdb884f6f200f75531` |
| 閉じmain〜EOF（共有modal/実行JSを含む） | `f20be89a707d5a07f003f0a4afb3803e03f576964183e1a472e4d86aa9efb1e1` |

## schema境界試験の範囲

正常追加ケースは、新規GitHub Scope、真正の既存local backendの保全、旧local綴りのGitHub ID、任意fieldのないworkspace、6桁の新規番号の5件です。次は実行した異常35件の一覧で、全て拒否しました。

| No. | ケース | 結果 |
|---|---|---|
| 1 | scope schema_version 4 | 拒否 |
| 2 | scope id iss-00000 | 拒否 |
| 3 | scope id 550e8400-e29b-41d4-a716-446655440000 | 拒否 |
| 4 | scope id epic-00413 | 拒否 |
| 5 | scope revision True | 拒否 |
| 6 | scope revision -1 | 拒否 |
| 7 | scope github None | 拒否 |
| 8 | scope lifecycle {'state': 'open', 'revision': 0, 'updated_at': '2026-09-30T00:00:00Z'} | 拒否 |
| 9 | scope epic_id init-00031 | 拒否 |
| 10 | worktarget schema_version | 拒否 |
| 11 | worktarget scope_id | 拒否 |
| 12 | worktarget selected_branch | 拒否 |
| 13 | worktarget selected_at | 拒否 |
| 14 | worktarget github_ref | 拒否 |
| 15 | worktarget operation_id | 拒否 |
| 16 | worktarget required schema_version | 拒否 |
| 17 | worktarget required scope_id | 拒否 |
| 18 | worktarget required github_ref | 拒否 |
| 19 | worktarget required selected_branch | 拒否 |
| 20 | worktarget required selected_at | 拒否 |
| 21 | worktarget required clone_identity | 拒否 |
| 22 | worktarget required worktree_identity | 拒否 |
| 23 | workspace protocol specdock.writer/v1 | 拒否 |
| 24 | workspace protocol specdock.stateless-writer/v1 | 拒否 |
| 25 | new local spelling | 拒否 |
| 26 | new local forbidden | 拒否 |
| 27 | CLI success exit_code | 拒否 |
| 28 | CLI success error | 拒否 |
| 29 | CLI success operation_id | 拒否 |
| 30 | partial no effect | 拒否 |
| 31 | partial started true | 拒否 |
| 32 | partial exit 0 | 拒否 |
| 33 | failed with succeeded effects | 拒否 |
| 34 | planned with succeeded effect | 拒否 |
| 35 | old CLI v1 | 拒否 |

JSON Schemaは、OSでの物理identityの真偽、保存先の0/1件、Git切替、親ID同士の等値、live GitHub結果、新規番号とIDの等値、削除race、複数metadataの整合を実行検証しません。その他CLI familyのresult内部の全fieldはcli-contractとapplication contract testの責務です。今回のschema適合からこれらの製品保証を認定しません。

## ブラウザ検査の実行結果と限界

agent-browser CLIを呼び出したところcommand not foundでした。利用可能なPlaywrightとChromiumで表示確認を試みましたが、file URLと127.0.0.1の一時loopback HTTP URLの両方のnavigationが `net::ERR_BLOCKED_BY_ADMINISTRATOR` で停止しました。認証・browser管理設定の変更や制限回避はしていません。一時serverはその実行processだけで終了し、外部公開はしていません。

そのため、実HTMLの描画DOM、CDN libraryの読込、PlantUML 4図のSVG生成、診断SVGが返らないこと、modalのクリック/Enter/Space/倍率/フォーカス/終了、390px等のviewportでのoverflowは**未確認**です。見ていないスクリーンショットや旧reportの合格を成功証拠にしません。NodeのJS syntaxとtemplate byte一致は、この動的検査の代替ではありません。

CodexのP-14では、許可されたローカル環境で新HTMLを開き、4図の実SVGを独立に検査し、診断画面の混入がないことを確認します。modalの全操作、閉じた後のフォーカス復帰、desktop/mobileの本文と表の表示を検査します。添付には専用validatorの実体がないため、存在しない実行pathは提示していません。

## 未実施・確認範囲外

製品のmake lint/uv run pytest、fresh wheel/実console E2E、Startの別process排他、Windows/macOS/Linuxの新原語、GitHubへの変更、実cutover、#413正式import/Start/Finish、commit/push/merge/公開は全て未実施です。240件全metadataの独立取得・schema適合・byte保全も今回の環境では未実施です。

source-basisに列挙した主要sourceは読取りましたが、repo全関数/全testを通読したという意味ではありません。歴史6 commitはfull object metadataを照合し、全diff・祖先到達性・歴史版file全文は未検査です。製品受け入れは全ACで未実施のままです。

## 意図した外部保有依存

`report.md` と `artifacts/interview-worktree-start.md` の2pathはCodexが採用先に保持します。単独ZIP展開では存在しない前提でリンクを検査し、欠落を勝手に埋めません。manifestはpayload16fileだけをhash対象とし、この2pathは保有依存として別fieldに記載します。manifest自体の自己hashとZIP全体hashをmanifestへ埋め込まないのは循環参照を避けるためです。ZIP全体のbytes/hashは配布時の外側の検査結果に記録します。
