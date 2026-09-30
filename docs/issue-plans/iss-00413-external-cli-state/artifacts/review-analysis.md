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

後続: 修正候補をcommit/pushし、同じレビュー目的で再評価する。現時点では再レビュー合格未取得。

## 形式補正の再送が失敗した記録

子セッションrequired-strict-github-connector-verificati-1388は、元の会話のChat/WorkモードをOracleが判別できず、chat-mode-selection / conversation-unresolvedで送信前に停止した。元レビュー内容は有効な分析資料として保持する。この失敗は仕様の良否とは別の実行環境の問題である。
