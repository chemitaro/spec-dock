---
種別: disc
ID: "20260801t152944z-disc"
タイトル: "Issue 346 ChatGPT Assisted Execution Agreement"
状態: "active"
作成者: "iwasawayuuta"
最終更新: "2026-08-02"
親: ["iss-00346"]
関連: ["plan.md"]
authority: "evidence_only"
derived_from:
  - "2026-08-02 operator instruction"
  - "requirement.md"
  - "design.md"
  - "plan.md"
reflected_to:
  - "plan.md"
review_policy: "excluded_from_review_target"
---

# Issue 346 ChatGPT支援実行の取り決め

## 1. 目的と適用範囲

この文書は、Issue 346の実装担当をGPT-5.6 Luna・推論レベルMaxとし、各ステップの実装前具体化と実装後レビューをChatGPT Proで補助するためのIssue固有の取り決めである。Lunaの実装判断を過度に拘束する詳細手順書ではなく、正本を読み違えないためのテスト観点、作業順、境界、停止条件を事前に整理する補助レーンを定義する。

対象は`plan.md`のS01、S02、S03、S04、S90、S99である。この取り決めはIssue 346にだけ適用し、SpecDock全体のworkflow、他Issueのreviewer policy、モデル選択を変更しない。

## 2. 情報の権限と優先順位

判断が衝突した場合は次の順序を守る。

1. canonical `requirement.md`
2. canonical `design.md`
3. canonical `plan.md`
4. accepted ADRおよび上位Epic/Initiativeのcanonical artifact
5. current repository source、public contract、再現可能なtest evidence
6. 各ステップのChatGPT具体化ArtifactおよびChatGPT review output

ChatGPT成果物は`evidence_only`の補助資料であり、要件、設計、計画、受け入れ条件、allowed path、repair boundaryを追加・変更できない。矛盾、古い前提、未確認の推測、過剰な実装提案は採用しない。正本間の矛盾を発見した場合は実装で解決せず、planning amendmentまたはclarificationへ戻る。

## 3. モデルとツールの契約

- 実装担当: GPT-5.6 Luna、推論レベルMax。
- 具体化・レビュー担当: operatorが指定するGPT-5.6 Proを意図したcurrent ChatGPT Pro。
- 呼び出し方法: `/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt`だけを使用する。Oracle直呼び、API fallback、通常Chrome、ブラウザ直接操作は使わない。
- モデル証跡: wrapperの`requested=Pro`、`resolved=Pro`、`verified=yes`を必須とする。Oracle 0.16.1だけでは基盤モデルの版番号を証明できないため、追加の信頼できる表示証跡なしに「GPT-5.6を検証済み」とは記録しない。
- ChatGPTがGitHub connectorからcurrent repository/current branchを開けない場合は`repository access failed`として停止し、添付ファイルや一般知識だけで継続しない。

## 4. すべてのChatGPT呼び出しに先行するGitHub同期ゲート

具体化、レビュー、修正後再レビューのいずれでも、ChatGPTを呼ぶ直前に次を満たす。

1. 対象ステップまでの意図した変更と`report.md`の必要証跡をbounded commitにする。
2. current branchをGitHubへpushする。
3. local `HEAD`とremote branch headが一致することを確認する。
4. working treeにChatGPTが参照すべき未commit変更が残っていないことを確認する。
5. promptにrepository、current branch、pushed head SHA、対象ステップ、正本pathを明記する。

pushされていないlocal diffをChatGPTが観測できると仮定しない。ChatGPT回答後にheadまたはreview対象contentが変わった場合、以前の回答をcurrent-head evidenceとして再利用しない。

## 5. 各ステップ開始前の具体化レーン

S01、S02、S03、S04、S90、S99の実装または実行を始める前に、各ステップにつき1回、次を行う。

1. §4のGitHub同期ゲートを閉じる。
2. formal wrapperでcurrent ChatGPT Proを起動する。
3. ChatGPTにGitHub connectorでpushed branchを先に確認させ、canonical R/D/Pと対象コード・既存testを読ませる。
4. GPT-5.6系coding agent向けのcurrent prompt guidanceを踏まえ、Luna・Maxが自律的に実装するためのMarkdown資料を作成させる。
5. 完成した単一Markdownをapproved Workbenchへ保存し、`artifact import chatgpt-output --issue iss-00346`でbyte-preserving importする。
6. import receipt、Artifact path、source/destination hash、対象headを`report.md`へ記録してから実装へ進む。

ChatGPTへの依頼は、既存planの再生成ではなく、次だけを具体化する。

- stepのobservable goalと完了条件の短い再確認。
- 最初に観測すべき既存挙動、Redまたはsensitivity evidence。
- 必須テストケース、negative/error/regression/invariant境界。
- 最小の作業順、対象file候補、実行command候補。
- 過剰実装、source-of-truth逸脱、host/platform誤認の防止観点。
- 不確実な点、正本へ戻すべき停止条件。

次は要求しない。

- production patchや完成コード。
- private method単位の逐語的な実装指示。
- 正本にない新機能、API、architecture、test count。
- 根拠のないfile/function名、固定行番号、実行結果。
- Lunaの高い推論能力を妨げる過度に細かなpseudocodeや一本道の指示。

具体化Artifact自体はreview対象外とする。実装担当はその内容を採用する前に正本、current code、testsと照合し、不要・矛盾・過剰な提案を捨てる。

## 6. ChatGPTレビュー契約

Issue 346のstep reviewとfinal QA/code/spec reviewは、`qa-reviewer`、`code-reviewer`、`spec-reviewer`サブエージェントを起動する代わりに、formal wrapper経由のcurrent ChatGPT Proで行う。実行時点の各roleのDeveloper Instructionsを取得し、担当責務、severity、fail/pass条件、required output schemaをreview promptへ渡す。古い転記や記憶だけでrole contractを推測しない。

同一review targetにQA、code、specなど複数観点が必要な場合は、並列の複数ChatGPT実行に分けない。1つのChatGPT conversation/thread、1つの統合promptに複数観点を明示し、観点別findingと統合verdictを一度に返させる。repair後の再レビューも、同じconversationを`--followup`で継続できる限り再利用する。ただし毎回§4のpush/head一致を先に確認し、新しいhead SHAと差分を明示する。

review promptには少なくとも次を含める。

- repository、branch、reviewed head SHA、base/diff scope。
- canonical R/D/P、accepted ADR、対象stepのclosure/test obligation。
- 実行したtest、未実施test、host/platform evidence、known limitation。
- current `qa-reviewer` / `code-reviewer` / `spec-reviewer` Developer Instructionsのうち必要な全観点。
- overreviewとoverimplementationを避け、P0/P1/blocking contract violationを優先する指示。
- findingごとのseverity、evidence、affected path/symbol、required action、scope classification。
- `review_status: pass|fail`と、観点別statusを持つ構造化JSON互換出力。

ChatGPT review outputは保存対象のreview evidenceだが、正本を直接変更するauthorityは持たない。main orchestratorがfindingをcurrent source/testsへ照合し、採用、棄却、deferを判断する。採用した修正はroot causeに応じてbounded workerへ委任し、検証、commit、push後に同一threadで再レビューする。P2/P3だけを理由に無制限なcleanup、scope expansion、architecture変更を行わない。

## 7. Artifactとレビューの境界

- 各ステップの具体化Artifactはreview対象外。
- ChatGPT review outputはreview証跡であり、それ自体を別reviewの対象にしない。
- canonical R/D/Pまたはaccepted ADRを変更する必要が判明した場合は、Artifactだけで解決せずplanning workflowへ戻す。
- ChatGPT成果物の保存はcanonical adoptionやstep closureを意味しない。
- reviewのpassは、review対象head、prompted scope、必要なtest evidence、未解決finding 0が対応している場合だけ有効。

## 8. 失敗・停止条件

次の場合は当該ステップを開始またはcloseしない。

- GitHubへのpushまたはlocal/remote head一致を確認できない。
- wrapperが`Pro`選択をverifyできない。
- GitHub connectorがrepository/current branchを観測できない。
- ChatGPT回答が不完全、取得不能、またはArtifact保存receiptを確認できない。
- ChatGPT具体化とcanonical R/D/Pが矛盾する。
- reviewer Developer Instructionsを取得できず、必要なreview contractを再現できない。
- review対象headが変わった、必須test evidenceがない、blocking findingが未解決。
- repairがplanのallowed pathまたはrepair boundaryを超える。

retryable timeoutやbrowser切断では同じpromptを直ちに再送しない。session status/render/reattachを確認し、必要なら`oracle-browser-recovery`で復旧する。

## 9. ステップ開始チェックリスト

- [ ] 前stepのclosureとcommit/pushが完了した。
- [ ] local/remote head SHAが一致した。
- [ ] ChatGPT Proのmodel evidenceが`verified=yes`である。
- [ ] GitHub connectorがcurrent branchを観測した。
- [ ] step具体化MarkdownをArtifactへimportした。
- [ ] Artifactのhead/source/receiptをreportへ記録した。
- [ ] 正本との矛盾と過剰指定をmain orchestratorが除外した。
- [ ] 実装担当Luna・Maxへ正本、対象step、補助Artifactを渡した。

## 10. 採用状態

この取り決めは2026-08-02のoperator instructionによりIssue 346の`plan.md`へ反映された。新しい製品要件・設計判断・公開契約を追加しないIssue-local execution procedureである。ユーザー指示により、本Artifactおよびこの手続き追加だけを理由とするspec reviewは実施しない。
