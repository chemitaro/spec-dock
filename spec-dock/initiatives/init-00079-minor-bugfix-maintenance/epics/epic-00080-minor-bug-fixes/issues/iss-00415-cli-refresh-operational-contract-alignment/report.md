# iss-00415 実装・検証記録

## 現在の実装状態（2026-10-06）

ユーザーが本計画の実装・完了、GPT 5.6 ProでのStrict Final Quality Gateと指摘修正・再レビューを依頼しました。ゴール登録済み。対象はb004、branch `codex/iss-00415-cli-refresh-specs`、開始HEAD `775075cbd936d1f6fc80a97e2e50659c43f85fc1`です。人間のmergeは対象外です。Gate v2の版選択は確認待ちで、独立した実装は継続しています。

- `spec-dock work start iss-00415 --branch codex/iss-00415-cli-refresh-specs --json`: exit 0、同branchを再利用し直接対象を取得。active showで対象・祖先を再確認。
- S-01: macOS 27.0.1 arm64、開始HEADの `make lint` exit 0。`uv run pytest` exit 0、1917 passed / 1 skipped / 450.76秒。生ログはIssue Workbench `implementation/baseline.log`。
- S-02: 公開create/import × 3階層 × apply/dry-run × text/JSON × 直接選択あり/なしの48条件。保全・比較・手動判断の案内不足でRedを確認し、診断文言だけを変更。公開publish/import suite 139 passed / 41.15秒。tree digestでmetadata・証拠・直接記録・Gitのmode/bytes/type不変、gh呼出しなしを確認。
- S-03: READMEの実掲載3例をstateful gh stubで実行し、返却IDの親子連結とyesなしの無副作用停止を確認。通常TARGETの正負例、rootの実import例、Sync・AGENTSの現行説明と実在リンクを確認。対象suite 38 passed / 12.44秒。provider文書のhashはS-05で統合予定、consumer未適用。
- S-04: 全44 leaf・三shell生成候補のRedを確認し、候補選別だけを修正。三生成検査はpass。実Fish 4.0.2の7代表入力も7 passed。macOSのBash/Zshを含む対象回帰は下記のとおり。
- 検証用Linuxコンテナ: Python 3.10.22、Bash 5.2.37、Zsh 5.9、Fish 4.0.2。製品依存やホスト設定へ追加していません。

以下は仕様採用時点の履歴です。未実施という記述はその時点の観測で、現在の実装状態は上記と以降の追記を参照します。

# 仕様策定・採用記録

## 結果

2026-10-06、installed external SpecDockで[Issue #415](https://github.com/chemitaro/spec-dock/issues/415)をepic-00080配下に作成しました。親#79/#80のOPENを本作業でlive確認しました。7件のCLI操作契約不整合を対象とする日本語Requirement・Design・Planの完全版を、同じChatGPT会話から取得して内容照合後にcanonicalへ採用しました。文書のdraft／仕様候補表示と全実装step未実施の表示を保持します。仕様採用は製品実装や独立仕様レビューpassを意味しません。

作業場所はb004専用worktree、branchは`codex/iss-00415-cli-refresh-specs`です。元main checkoutには書き込んでいません。metadataとArtifact登録はSpecDock CLIで行いました。

## 来歴

- 初回入力checkpoint: `95ec39b751054bf48098215fc077fe7b8f533f62`。親commitはPR414 mergeの`0e7dc86841cb48d011270a1a2165cb6406ac0cea`です。
- Strict wrapperのclean／設定済みupstream／live full SHA一致を通過。同じSHAに対するGitHub connector再検証成功が[回答原文](artifacts/20261006t043340z--answer.md)に記載されています。connector検証は回答内の申告であり、wrapperによる機械的attestationではありません。
- 親session: `specdock-cli-refresh-audit-resumed`。今回のfollow-up session: `required-strict-github-connector-verificati-1408`。約34分30秒、exit 0。
- [継続した会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6ac46387-8628-83ee-9104-2bb0e6874e14)。新しい会話へ切替えていません。
- 指定model／effort: `gpt-6-pro`／`pro`。今回model selectionは保存設定継承のためskipped／verified=false、effortはPro／already-selected／verified=true。前回のLatest／Pro選択証拠と、今回の再選択省略を区別します。
- 取得ZIPは[原本](artifacts/20261006t043339z--iss-00415-cli-refresh-specifications.zip)としてCLI importしました。download button fallbackの未保存ログはありますが、その後の実ファイル保存・hash・CRC検査が成功しました。

## 検証

- ZIPは40,428 bytes、SHA-256 `d6fcb257b6cb9ef27318a4137ef10af236f7e39999dbc9adb6cb610f387c20b0`。rootはrequirement.md／design.md／plan.mdの3通常ファイルのみです。重複名、directory、symlink、path traversal、暗号化entryなし。UTF-8 strict decode、CRC、サイズ検査に合格しました。
- [ファイルhash検証](artifacts/20261006t043341z--zip-validation.json)に記録した3つのhashは、回答、原ZIP、採用後canonicalの全てで一致します。完全ファイル置換であり、生成後の本文補正はありません。
- 3文書全974行を確認しました。SD-OPS-001〜007と配布・品質のRQ/AC、設計、S-01〜09、V-001〜09が対応し、非対象と未決判断を維持しています。
- 相対リンク・明示anchor 74件、source/test path 18件を照合し欠落なし。本文で引用する既存test function／fixture、診断分類、static updateの返却fieldも現行sourceで照合しました。
- inventoryのreference_cli.md current hash、既知旧hash2件、mode、init_onlyが設計記載と一致しました。
- PR414のMERGED／merge日時／merge commitをliveで再確認しました。GitHub Aboutが旧descriptionであることもGETで確認し、変更していません。
- 外部手順の記述は[GitHub API](https://docs.github.com/en/rest/repos/repos#update-a-repository)、[gh api](https://cli.github.com/manual/gh_api)、[Fish complete](https://fishshell.com/docs/current/cmds/complete.html)、[uv tool install](https://docs.astral.sh/uv/reference/cli/#uv-tool-install)の公式資料と照合しました。
- 採用後の`spec-dock workspace validate --json`はvalid=true／findings=[]／node_count=241、`git diff --check`はexit 0でした。active showはemptyです。

## 残る事項

今回はIssue作成と仕様反映までです。製品実装、製品pytest／lint／fresh wheel再認定、package更新、consumer更新、About書込み、work start/finish、PR作成・mergeは実施していません。IssueはOPEN、直接選択はemptyのままです。

実装時には対象候補・wheel・tool環境・consumer絶対root・backup先・検証環境を確定します。Aboutのdescription採否と実施、互換入口廃止、global共通skill＋local情報は未決のままです。後二者は本Issueの七件に不可欠でない将来の別判断です。過去の3 passedを現在の製品検証成功へ転用しません。


## S-04〜05 実装候補の配布確認

- 全44 leaf・三shellの候補を独立したread分類表で検査。共通値のskip、parser受付、catalog分類は変更していません。
- 新規・旧版更新の公開CLI試験で、改稿前の実blob hashを確認し、backupの旧bytes/modeと文書以外のtree不変を確認。未知の追記があればeffectsなしで停止。
- inventoryはreference_cli.mdのcurrent hashだけを更新し、以前のcurrent `1ee708029bae2fa92eb2c2bd9fe79e9885fc11815b535bf8e1be344b6d3689dc`をknown-oldへ追加。既存旧hash2つ、他entry・retired集合は保持。
- 対象回帰: help/completion、CLI契約、lock options、provider distribution、static assets、wheel、entrypointの7ファイルで `179 passed, 7 skipped in 114.12s`、exit 0。skipはホストにないFishの7件で、同7件はLinuxで実行し7 passed。
- fresh wheelとsdist経由wheel、外部non-editable console、fresh consumer、全inventory bytes、legacy診断の無副作用、README三階層作成と確認guard、selector正負、native補完を検査。製品の実GitHub変更はstubへ隔離。
- 現在のlintはruff check/format、mypyすべてpass。workspace validateは241 Scope、findingsなし。
- 固定commitからの独立wheel・Linux/Python 3.10全体検証と利用者環境への適用は次段階です。通常全件テストとStrict Gateも未完了です。
