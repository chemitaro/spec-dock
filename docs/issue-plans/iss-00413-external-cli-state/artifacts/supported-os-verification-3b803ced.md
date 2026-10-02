# Windows撤去・Finish修正後の製品検証

2026-10-02 JST、clean/pushedの候補 `3b803ced470bf58439bbee342b61c91c20de74b6` を検証しました。比較baseは `6fec3099d8759b4e5b3b393b2987534b46dfa383`。これはFinal Quality Gateに提出する前の記録で、人間merge・実導入・正式#413 import/Startの完了記録ではありません。[原文と環境証拠](supported-os-verification-3b803ced.json)を保存しています。

## 全件と最低Python版

| 環境 | 通常の実行結果 | 制限 |
|---|---|---|
| macOS 27.0.1 arm64 / Python3.12.11 / APFS | `uv run pytest -q --tb=short -ra`: 1899 passed / 1 skipped、428.00秒、actual exit0 | skipはLinux O_TMPFILE capability test。成功には数えない |
| Linux x86_64 / Python3.11.16 / glibc2.41 / tmpfs fixtures | 同じ通常pytest: 1883 passed / 17 skipped、1094.09秒、actual exit0 | arm64ホストの固定amd64 Docker imageでの実行。物理Linux端末ではない。networkなし・rootfs read-only・capability0 |
| macOS / 実Python3.10.15のisolated環境 | OS admission、Finish、directory identity、Start lock、native lock、fresh console E2E: 61 passed、24.33秒、actual exit0 | 最低版の関連境界検査。全件3.10と呼ばず、projectの3.12 venvは変更しない |

Linuxの17 skipはzsh不在12件、macOS named-stage契約1件、Linux匿名stageにpathname cleanup seamがない4件です。Windows固有skipはありません。321個のtracked source/test/config入力のfold SHA256は `83a680b4933d672c7887092bd272855c5ff67e03e72ef03f67b05c60c7b3ec36`。Linuxの実行前後とmacOS実行後で一致し、Git statusはclean、HEADは不変です。過去121228c6のPATH不備による失敗はそのまま保全しています。

## 非editable外部consoleの個別操作

両OSでfresh wheelを外部venvへ通常installし、pip checkを成功させ、所有する元sourceコピーを参照不能にしました。import元はsite-packagesです。実Gitとfresh clone/main/linked worktreeを使い、GitHub境界だけを所有するstateful外部ghへ置換しました。live GitHubのIssueをCloseした実績ではありません。

macOSの[14個別操作原文](manual-console-3b803ced.json)、Linuxの[14個別操作原文](manual-linux-3b803ced.json)を保存しました。pytestのtest bodyを手動と呼び換えていません。両wheelのprovider入力foldは `406d985677ff6b811c11d34b407db06241cb7b8b97608d398fe1a66bdaa9b50d` で同一です。wheel hashはOSごとのprovenanceにあり、生成時刻等で異なるarchive bytesを同一だとは記録しません。

| 個別確認 | 両OSの観測 |
|---|---|
| projectなしhelpとStart/Sync/Finish leaf help、Start/Finish dry-run | exit0、entry書込0 |
| A Start→他WTの重複A Start | Aはbranch作成/checkout/一件公開。重複はexit3、SCOPE_ALREADY_SELECTED、effects=[]、書込0 |
| 兄弟B Start→GitHub-source Sync | A/Bを同時表示。親direct=0 / descendant=2。process_state=not_observed、Syncはreadonly |
| A Finish→次C Start | completed CloseのPATCH一回と確認GET、Aだけ解除、branch保持。Cを追加switch flagなしで開始 |
| 実Git post-checkout hookの二行stderr/exit1 | branch作成/checkoutは成立、CLI partial/exit6、started=false。Git原文とnative returncodeを保持し、選択clear/publishはnot_attempted。C/B record不変、branchを巻き戻さない |

両OSのGitHub requestは各26件。seed/main/linkedのtracked仕様foldは全て同じでGit statusはclean、独自`.git/spec-dock`は0でした。Linux検証containerは原文を退避して停止済みです。手動fixtureの保存/集計時のimportとDocker copy/exportの補助失敗も元記録を保全し、製品操作を再実行して成功を作り直していません。

## 独立Code Review Strict

[raw JSON](code-review-linux-macos-3b803ced.json)はoriginal bytesのままです。native/wrapper actual exit0、review_status=pass、findings=[]。GPT-5.6 SolとProのUI選択は両方verified=true、promptSubmitted=true、completedです。reviewerはGitHub connectorで同じbranch/full SHAを確認して全指定範囲を評価し、testを自分では実行していないと明記しています。local test結果と混同しません。

指定pointerの`worktree-state-schema.json`は存在しませんでした。reviewerは現行D-03が指す`data-schema.json`を確認し、適用契約の欠落ではないと説明しています。最終ゲートは現行名を使います。過去r12のP1/failは改変せず、[P-07のTDD修正](p07-finish-observation-repair.md)を含む新候補でpassを取得しました。P2/P3を含む新findingはありません。

## 更新HTMLの実ブラウザ検査

製品3b803ced後の文書更新版HTMLはSHA256 `4bec12f4aada362c3a866cd54f361a17eea1bb2ca713bdd3bd1e99dfdcfa8eaf`。元validatorで4/4 inline SVG、click/keyboard/zoom、bounds、focus trap、dismissal/focus restorationを確認し、actual exit0でした。追加の390px実viewport検査も同じ4図と11表を確認し、document scrollWidth=390、actual exit0です。追加harnessの初回はbodyの成功markerを5番目の図と誤認してexit1でした。元validatorと同じ4個のtargetIdsに限定して修正し、HTMLを変更せず再確認しています。元の失敗ログもJSONに保全しています。

既存[Tailscale説明資料](http://100.85.74.8:8765/specdock-issue-413/explanation.html)はHTTP200 / Cache-Control=no-store、73427 bytesでsourceと完全一致しました。このHTMLは3b803cedの先行Code Reviewに含まれておらず、次の文書込み候補でFinal Quality Gateを実施します。

## 後続の境界

Final Quality Gate v2は、Linux/macOS範囲の新campaignで別途実施します。HTML更新とpack検査後の最終clean/pushed SHAに対し、独立reviewと通常必須testを別レーンで行います。この記録だけで最終ゲートを合格扱いにしません。人間merge（P-15）、実dogfood適用（P-16）、既存#413の正式import/Start（P-17）は未実施です。実consumerの旧controlやmetadataを例外で手編集しません。
