# iss-00415 仕様策定・採用記録

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
