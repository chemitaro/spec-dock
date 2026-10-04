# 第10回コードレビューの全件分析

## 対象と証拠

元のJSONのSHA-256は `922aa2ef0b62a0f75253d8dc71b80634898c80c7ecf7f42895ea1c3ce872112e`。

Strict wrapperが固定した候補は `3e300afaa3b286074139f3b6ccc6a2494ca7c691`、基準は `6fec3099d8759b4e5b3b393b2987534b46dfa383`。送信前のcleanなattached branch、設定済みGitHub upstreamとのSHA一致、二回のremote ref照合を確認した。通常のbrowser経路で **GPT-5.6 Sol / Pro** の選択証拠が記録され、43分34秒後にwrapper exit 10、`review_status=fail` で完了した。[元のJSON](code-review-p06-10.json)を無変更で保存する。

今回のgateはP-02〜P-09と接続済みP-10のScope query/edit/delete。後でコミットしたArtifact `35068763753bed493f7a8fb608bbd6726581d4f1` と進行中のWorkbenchは対象外であり、現在作業との同一性を偽らない。レビュー生成と必須の当該単位の検証は完了済み。レビュアーは静的照合を行い、testsを再実行していない。

元の分類は **P1一件、P3一件**。P1は現在候補をblockingとする。P3は分類を変更せず、本来のStrict分類から修正認可を推論しない。利用者がこのIssueの実装依頼で、指摘を分析・修正・再レビューすることを明示した上位の認可に従い、二件とも既存契約の範囲で対応する。

## F1 — P1: checkout hookによるdirect record変更の見逃し

**妥当性・到達性**: 採用する。`branch_operations.py` はcheckout後にbranch/HEAD、candidate metadata、Git statusを確認するが、ignoredな `spec-dock/.agent/work-target/` の捕捉記録との比較を行わない。正常終了する `post-checkout` hookが記録を削除・置換・同一inodeで編集してもGit statusはcleanとなり、誤って成功と `switched=true` を返せる。Gitが非zeroを返した後の観測経路にも同じ抜けがある。既存のhookによるtracked/untracked dirtyの試験だけでは、このignored-stateの経路を閉じない。

**違反authority**: RQ-413-14/AC-413-30、D-04とbranchの直接選択不変契約。C-04は確認済みGit効果を隠さないpartialと原文Gitエラーを要求する。一方、RQ-413の非対象は外部editor/任意hookの完全封鎖であり、hook変更を権限制度やlockで防いだり、自動復元したりする認可ではない。

**最初の誤りと根本原因**: implementation層で、Git結果の確認対象から変更禁止の直接状態が抜けている。状態の所有者は当該worktreeのimmutable recordであり、branch操作はその読み取り・照合だけを行う。現在の`StoredSelection`/`SelectionHandle`にはbasename、directory/file identity、content hashがあり、追加の保存状態は不要。

**primary route**: `implementation-remediation`。同じinvariantがGit hook経由で再び現れたため、個別hook名の特例ではなくbranch familyのGit変更前後の捕捉・照合として閉じる。checkoutだけでなく、`branch create` が実行するGitの`reference-transaction` hookも同じ変更禁止契約を持つため、同じ読み取り原語で確認する。dynamic targetとexpect guardは捕捉した同じ直接観測から解決する。

**最小対応・検証計画**: Git変更前に直接記録を一度捕捉し、公開済みhash/identityを使って変更前、変更後、native failureの現物観測で照合する。選択を観測できなければ変更前に止める。変更後の差異は既存のverification errorでpartialとして返し、確認済みbranch/checkoutの効果を残す。checkout成功hookの削除・置換・同一inodeのbytes変更、非zero hook、空→新記録、branch作成hookを公開CLIと実Gitで再現する。元のrecordを戻さず、hookが残した新しい実体を保持する。no-op、dry-run、従来の原文stderr/returncodeも回帰確認する。

**認可・保証**: 上位の実装依頼による自律修正。変更するのは不足した成功条件の検証だけであり、新しいlock、権限、journal、復旧操作、Git hookの無効化、Scope/selectionの暗黙変更は追加しない。直接状態の観測不能を成功へ補完しない。別の人間判断や設計変更は不要。

## F2 — P3: Scope read helpのcached stateという誤案内

**妥当性・到達性**: 採用する。共通Reads文字列に`cached state`が残り、`scope list/show --help`へ表示される。接続済み`load_scope_views`はGitHub-backedを未観測`unknown`にする実装で、retired cacheを採用しない。実際の読み取り挙動に不具合はなく、説明だけが誤っている。

**違反authority・最初の誤り**: C-05のScope readとD-10の観測根拠、documentation層。root causeは旧共通helpの接続済みread leafへの残存。

**primary route**: `documentation-correction`。Scope list/showのReadsをcurrent metadata、dynamic selectorで必要な当該直接記録、未観測GitHub状態はunknownという説明へ限定する。旧cache/control/journalを通常readの根拠と表示しない。公開helpの回帰試験で両leafを確認する。

**認可・保証**: P3をP1へ変更しない。利用者の全件分析・修正認可によって説明だけを訂正する。API、状態authority、通常readのネットワーク・保存動作は変えず、人間判断は不要。

## 残る義務と親workflowへの結論

二件を一つの分析batchとして完了した。最小の二対応をTDD/回帰確認し、小さなコミットの後でfresh Strictへ戻る。ローカル修正だけでは今回のfailを閉じない。

P-10残り、P-11/P-12、Windows native/store、全platformと全suite/型検査、consumer cutover、手動製品確認、Final Quality Gateは別の未完了義務として残す。今回のscopeに含めなかったことを全Issueの認定や免除に変換しない。Workbenchの未コミット変更をこの修正コミットへ混ぜない。
