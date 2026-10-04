# Issue #413 仕様レビュー対応記録

## 初回レビューと採用方針

- 対象: ea68e211b2fe807f903500cae027157b0743f7e3
- レビューID: github:chemitaro/spec-dock#413/specification-implementation-readiness
- 独立レビューセッション: specdock-413-spec-review
- モデル: GPT-6 Pro / Pro。初回UI選択確認済み。
- [会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abc9f11-c854-83e9-8fc1-7d4b9461cd62)
- [返答原文](review-001-raw.md): 原文bytesを保全。引用マーカーの引用符により厳密JSONとしては不正。2026-09-30の利用者指示に従い、破棄せず内容を読み取った。原文をschema適合済みとは扱わない。
- 内容上の判定: fail、P1一件、P0なし。評価不能の宣言や他のブロッカーなし。

## P1: Syncの規範JSONでは未選択Scopeの状態を表現できない

判定: 妥当で到達可能。RQ-413-11 / AC-413-23は選択とlifecycleを分離し、D-10はscopesを既に定義している。ところがC-03とcli-schema.jsonのsyncにscopesがなく、additionalProperties=falseで追加も拒否する。A選択中/completed、B未選択/openの場合、Bの状態を返す格納先がない。

最初の欠落層は詳細CLI契約への転記。P-08を要求どおり実装しても規範schemaを満たせないためP1として実装開始をブロックする。修正経路はdocumentation-correction。合意済み要求・D-10の意味を維持し、scopes行、選択件数との対応、例と受入検査を補う。中央状態、キャッシュ、ロック、編集権限、新コマンドは追加しない。利用者が許可した修正・再レビュー範囲内であり、新たな製品判断は不要。

修正: C-03、CLI schema、examples、D-10の参照、P-08とAC対応表、人間用HTMLを整合。ScopeObservationは既存Scope識別子、GitHub参照、lifecycleのみ。選択件数は既存Countへ保持する。

検証: 旧schemaが修正例を拒否し、新schemaが全例を受理すること。scopes欠落・lifecycle不正を拒否すること。A/Bの行と1/0件・localのunknownを確認すること。文書リンク・ZIP/manifest整合、既存metadataとインタビュー無変更を確認する。製品AC実施の代わりにはしない。

検証結果: 13例（CLI 9、保存データ4）がschema適合。旧schemaは新Sync例を拒否、新schemaは受理。scopes欠落・不正lifecycleは拒否。A/Bの状態・選択件数、local unknownを確認。240 metadataの集約hashと確定インタビューhashは補正前と一致。製品テストは未実施。

補正時点の後続: 修正候補をcommit/pushし、同じレビュー目的で再評価する。結果は次の「再レビュー合格」に記録する。

## 形式補正の再送が失敗した記録

子セッションrequired-strict-github-connector-verificati-1388は、元の会話のChat/WorkモードをOracleが判別できず、chat-mode-selection / conversation-unresolvedで送信前に停止した。元レビュー内容は有効な分析資料として保持する。この失敗は仕様の良否とは別の実行環境の問題である。

## 2026-09-30 再レビュー合格

- 結果: **pass、指摘0件（P0/P1/P2/P3すべて0）**。前回P1は解消済み。
- 合格した仕様のcommit: **7e895803cba0d43957e504c9f97637d307bc6a78**。
- レビュー目的/対象: 初回と同一の実装開始可能性、指定15文書全体。
- 実行: chatgpt-spec-review-strict、browserのみ、GPT-6 Pro / Pro。
- 新規レビュー会話は利用者の「許可します。再開してください。」により明示許可された。
- active reviewer session: specdock-413-spec-rereview。作成用会話とは独立。
- [再レビュー会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6abca6d0-86ec-83e8-a59d-2a4728728c76)
- [再レビュー原文](review-002-raw.md)をbytes無変更で保全。今回も引用マーカーの引用符で厳密JSONは不正だが、利用者の形式より内容を優先する指示に従い判定を採用した。原文のJSON修復や形式合格の主張はしていない。
- 検証根拠: ローカルclean/上流同SHAのStrict gateに加え、レビュアーが接続GitHubで指定branch/ref/object type/full SHAの一致を確認。元実装のmainへfallbackせず現行15文書を評価したと回答。
- 実行証拠: process exit0、Oracle metadata status=completed、2026-09-30 15:18:54 JST完了。model pickerのLatest（要求gpt-6-pro）とthinking pickerのProをともにverified=true。submitted prompt SHA256: 4db9db897c450fa852256f8597b462fa47ac5262893022076f9239ac4dc74300。
- 原文SHA256: f89199591dbfed61d3be23f023fe118c1a034a982cdd6d9c33ed26695fe8d92c

### 内容の確認と合格の意味

原文はfindings=[]、review_status=passを明示し、前回P1についてscopes必須化・A/Bの例・P-08/AC-23検証責務の整合を確認している。ローカルのschema/例の検証結果とも一致する。追加の指摘や評価不能範囲によるブロッカーはない。JSONの形式不備を理由とする再送は行わない。

GPT-6.1 Sol / Highはplan.mdのP-01から実装を開始できる。レビュー合格後に変更したのは合格記録・README/HTMLの進捗表示・manifest/配送ZIPだけで、要件・設計・実装計画・規範契約・例・受入条件は合格commitのまま保持する。

製品実装、製品テスト、OS/FS排他の実測、人間merge、実環境移行、正式Scope import/work startは未実施であり、今回の合格で済んだことにはしない。P-01〜P-17の実装・適用時の完了条件を引き続き満たす必要がある。
