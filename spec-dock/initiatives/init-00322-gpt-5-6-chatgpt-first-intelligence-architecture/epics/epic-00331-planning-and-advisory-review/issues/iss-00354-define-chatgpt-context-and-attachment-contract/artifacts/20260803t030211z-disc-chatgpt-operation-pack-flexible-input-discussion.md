---
種別: disc
ID: "20260803t030211z-disc"
タイトル: "iss-00354 ChatGPT operation packと柔軟な添付運用の統合判断"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-08-03"
親: ["iss-00354"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260803t030211z-disc iss-00354 ChatGPT operation packと柔軟な添付運用の統合判断

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - ChatGPTへ渡す合成promptと添付資料の分離、operation単位の添付ディレクトリ、出力形式の柔軟な指定、product runtimeとpersonal wrapperの境界を一つの運用方針へ統合する。
- この synthesis が必要な理由:
  - これまでの質問は「共通契約」「必須template」「phase profile」を含んでいたが、ユーザーは一律の厳格契約ではなく、スクリプトごとのdirectory packとケース別の出力形式を望んでいる。個別回答をそのままcanonical docsへ転記すると、矛盾とscope肥大化が起きるため。

## derived question sheets / research (必須)
- `interview`:
  - `20260803t005840z-interview`（同一Blue／fresh Red thread境界、Option A採用）。
  - `20260803t011239z-interview`（継続失敗時fail-closed、Option A採用）。
  - `20260803t023549z-interview`（本文／添付分離、Option A採用）。
  - `20260803t024349z-interview`（output templateは必要なoperationだけ添付、Option A採用）。
  - `20260803t025103z-interview`（共通基盤の厳格適用範囲を柔軟なoperation packへ修正、部分採用）。
- `research`:
  - `20260803t005640z-research`（現行prompt／attachment／Oracle adapterとwrapper障害の調査）。
- その他の根拠:
  - `20260803t010552z`、`20260803t011552z`、`20260803t023819z`、`20260803t024658z`、`20260803t025321z` のChatGPT advisory output artifacts。
  - `issue_planning_prompt.py`、`issue_planning.py`、`issue_planning_chatgpt.py`、planner／reviewer／revision／transport resources。

## synthesis (必須)
- 合意済みのこと:
  - ChatGPTの本文はタスクのゴール、最低限の入力、repository／branch／HEAD、authority／mutation制約、必要な出力形式の指示に絞る。
  - 詳細な作業手順、レビュー観点、リビジョン規則、必要時のoutput guidanceは、合成promptとは別のMarkdownファイル群として管理する。
  - operationごとに添付資料を格納するディレクトリを持ち、スクリプトはそのディレクトリの内容をまとめて添付する。資料の増減でスクリプト本体を変更しない。
  - 添付資料は一律に意味検査・schema検査せず、必要な検証はoperationごとに明示する。
  - Planning／Revisionなど形式が重要な処理では、ディレクトリ構成を保持したZIPなどの出力形式を本文またはoperation packで指定する。
  - product runtimeはprovider-owned Oracleを使い、個人の`chatgpt-use` wrapperや自由相談をruntimeの保証・formal evidenceとして扱わない。
- 未合意 / 未確定のこと:
  - なし。指定ディレクトリとサブディレクトリの内容をそのまま添付し、ChatGPTの可否判定や過剰な安全装置を追加しない方針が確定した。
  - operation packの正規配置、命名、version／source HEADとの結び付けは、既存scriptの実装確認時に最小限決める。
- source-grounded に解決できたこと:
  - 現行prompt synthesisは本文と添付を分け、phase別resourceとtransport contractを合成している。
  - Planner／Revisionのformal outputはZIP、Reviewerはclosed JSONという既存契約がある。
  - 現行adapterはphaseごとに新規sessionを作成し、個人wrapperはproduct runtime dependencyではない。

## 選択肢 / tradeoff (必須)
- Option A: 厳格な全operation共通profile／template／schema契約
  - Pros:
    - 機械検証と再現性が高く、formal operationの入力・出力境界を明確にできる。
  - Cons:
    - ChatGPTの柔軟な使い方を阻害し、ユーザーが不要としたoperationまで契約・validatorを強制してscopeが肥大化する。
- Option B: operation pack方式＋最小機械的境界
  - Pros:
    - promptと資料を分離し、資料の増減をコード変更なしで反映できる。必要なoperationだけ出力形式・validatorを指定できる。
  - Cons:
    - 添付内容の意味保証は弱く、operation packの欠落・過剰添付・secret混入を防ぐ最小の機械的境界が別途必要になる。
- Option C: trusted directoryの全件無検査添付（ユーザー最終採用）
  - Pros:
    - 追加・削除をコード変更なしで反映でき、operation packの扱いが最も単純で柔軟になる。意味・名前・構造の検査を添付時に行わない。
  - Cons:
    - 実際のtransportエラーはChatGPT Use／Oracle側に委ねる。pack作成者が適切なファイルを配置する責任を持ち、独自の検査・変換は追加しない。
- Option D: ChatGPTの自由形式出力をCodexが後変換
  - Pros:
    - 入力・出力の自由度が最大。
  - Cons:
    - ZIP／JSONのidentityや意味を後から推測することになり、formal evidenceの同一性とfail-closed境界を失う。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `operation pack`を「合成prompt Markdown」「添付資料ディレクトリ」「必要時のoutput-format guidance」に分ける。
  - スクリプトはdirectory glob／recursive discoveryで資料を集め、資料の増減でコードを変更しない。
  - 出力形式の指定は必須契約ではなくoperationごとの指示とし、形式が重要な処理だけZIP／JSON validatorを有効化する。
  - 内容意味の一律検査とpersonal wrapperのruntime依存を明示的に避ける。
- まだ proposal に留める理由:
  - なし。ユーザーの最終回答により、過剰なsafe file collection・path／secret／size境界を実装へ追加しないことが確定した。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - prompt／attachment directoryの分離、ケース別output形式、資料増減時のコード変更不要、product／personal境界。
- `design.md`:
  - operation packの構造とdirectory単位の単純な添付。内容検査・manifest・過剰な安全装置は設計しない。
- `plan.md`:
  - pack収集の実装、既存planning transportへの適用、ファイル増減でコード変更不要であることの確認。過剰なnegative／size／secret検査は追加しない。
- `ADR`:
  - 現時点ではIssue-local。複数scopeで不可逆なpack標準になった場合のみ候補化する。
- `report.md` Evidence Adoption Ledger:
  - 五つのinterview回答、research、ChatGPT advisory、wrapper anomaly、次の安全境界質問を採用証跡として記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no（現時点ではIssue-localの運用方式）。
- hard to reverse:
  - no。directory配置・収集方式は後から変更可能な実装契約として扱う。
- surprising without context:
  - yes。合成promptと添付資料を別管理し、内容検査を一律に行わない方針は文脈がないと誤解されやすい。
- real tradeoff:
  - yes。柔軟性とformal evidenceの検証強度のバランスがある。
- ADR 化しない場合の反映先:
  - `interview`、`disc`、`requirement.md`、`design.md`、`plan.md`

## 推奨案 (必須)
- ユーザー最終判断として、trusted operation packの全件無検査添付（Option C）を採用する。共通化するのは合成promptと添付ディレクトリの分離、directory単位の再帰添付、ファイル増減でコード変更不要という単純な方式までに留める。ChatGPTの可否判定、独自validator、symlink／secret／size対策、fallbackは実装しない。

## 推奨反映先 (必須)
- `requirement.md`:
  - operation-specific prompt／attachment pack、柔軟な出力形式、コード変更不要の資料更新を記載する。
- `design.md`:
  - pack directory discoveryとphase／operationごとの任意形式指定を記載する。内容検査や過剰な安全装置は含めない。
- `plan.md`:
  - 既存scriptの添付指定をdirectory化し、ファイル増減でコード変更不要であることを確認する。必要な出力形式指定だけをoperationごとに残す。
- `ADR`:
  - 作成しない。
- `report.md` Evidence Adoption Ledger:
  - user-approved interviewとChatGPT advisory、wrapper送信証跡の不整合、「過剰な安全装置を追加しない」という制約を記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - 全operationへの厳格なtemplate／schema必須化は、ユーザーが求めるcase-by-caseの柔軟性と、要件定義書・設計書・実装計画書の内容自由度を損なうため。
  - ChatGPT自由形式をCodexがsemantic変換する方式は、ZIP／JSONのidentityとformal evidenceの同一性を損なうため。
- deferred:
  - Implementation Brief、onboarding、general roleの固有profile、pack registry／migration、詳細なoutput schemaは後続Issueへ送る。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - 添付directoryの全件無検査・単純な再帰添付と、過剰な安全装置を追加しない制約をIssue-local要件・設計・計画へ統合する。
- 追加で作る artifacts:
  - なし。canonical authoring前に、既存scriptの添付処理を確認するだけとする。
