# phase playbook: requirement

このドキュメントは、Initiative / Epic / Issue に共通する **要件定義書の作り方** をまとめた shared playbook です。  
各スコープ固有の操作や品質ゲートは `workflow_*.md` を正本とし、ここでは **要件をどう詰めるか** に集中します。

関連:
- 全体像: [guide.md](guide.md)
- Scope workflow: [workflow_initiative.md](workflow_initiative.md), [workflow_epic.md](workflow_epic.md), [workflow_issue.md](workflow_issue.md)
- 議論資料の置き方: `discussions/rules.md`

## 1. この phase の目的 / 出力 / 非ゴール

### 目的
- 何を解決するのか、なぜ今やるのか、どこまでを対象にするのかを観測可能な形で固定する
- 分からないことを隠したまま先へ進まず、論点を `discussion` / `TBD` / `ADR` に分離する
- reviewer が「設計へ進めてよい」と判断できる土台を作る

### 出力
- 承認可能な `requirement.md`
- 必要に応じて `discussions/` 配下の `NNN-disc-*` / `NNN-research-*` / `NNN-note-*`
- 必要に応じて `discussions/` 配下の `NNN-adr-*`

### 非ゴール
- 実装方式を先回りして固定すること
- template の節を機械的に全部埋めること自体を目的化すること
- 未確定論点を曖昧な文章で包んで設計へ送ること

## 2. 着手前に確認すること

- 対象スコープの workflow を開き、いま扱うのが Initiative / Epic / Issue のどれかを明確にする
- 対応する template を開き、最低限どの節があるかを把握する
- 既存の `discussions/` と ADR index を確認し、過去判断と衝突しないかを見る
- すでに論点が不明確なら、先に discussion sheet を作る前提で着手する

template 参照先:
- Initiative: `spec-dock/templates/initiative/requirement.md`
- Epic: `spec-dock/templates/epic/requirement.md`
- Issue: `spec-dock/templates/issue/requirement.md`

## 3. 調査・分析の進め方

要件定義では、最初に「結論」を書くのではなく、**事実と解釈を分けて集める**のが基本です。

### 3.1 最初に集めるもの
- 現状の困りごとを示す一次情報
  - 既存ドキュメント
  - コードや設定
  - 画面、ログ、DB、監視、問い合わせ、GitHub Issue
- 影響範囲の見取り図
  - 誰が困るか
  - どのフローで困るか
  - 何を壊しうるか
- 成功を判断する観測点
  - UI / HTTP / DB / Log / dashboard / 運用手順 など

### 3.2 調査の進め方
- まず As-Is を箇条書きで固め、To-Be はその後に書く
- 「事実」「推測」「未確定」を混ぜない
- 分からないことは `TBD` へ逃がす前に、追加調査で潰せるかを一度確認する
- スコープが広がりそうなら、早めに MUST / MUST NOT / OUT OF SCOPE を仮置きする

## 4. ユーザーヒアリングの進め方

次のどれかに当てはまる場合、ヒアリングは事実上必須です。
- 困りごとの一次情報がドキュメントやコードだけでは足りない
- 成功条件が利用者体験や運用判断に依存する
- 複数の解釈が成り立ち、どれを優先するかで scope が変わる
- reviewer から「利用者理解が不足している」と見なされうる

進め方:
- 先に仮説を整理してから聞く
- 「どう実装するか」ではなく「何が困るか / 何なら成功か」を確認する
- 回答は requirement 本文に直接埋め込まず、必要なら discussion sheet に整理してから反映する

## 5. discussion sheet を作る条件

次の条件のいずれかを満たしたら、`discussions/` に sheet を作ります。
- 論点が 2 つ以上あり、会話だけでは追跡しにくい
- ユーザーヒアリング前に仮説整理が必要
- 選択肢比較や trade-off を明示したい
- requirement に直接書くには早すぎる調査結果を保持したい
- reviewer へ判断材料を渡したい

使い分けの目安:
- `NNN-research-*`: 事実収集、現状分析、外部調査
- `NNN-disc-*`: 論点整理、選択肢比較、合意形成の叩き台
- `NNN-note-*`: 軽量メモ、一時的な整理

## 6. ADR を切る条件

要件 phase では ADR は乱用しません。  
ただし、次のような **意思決定を固定しないと要件が閉じない** 場合は ADR を検討します。

- スコープ境界や方針の選択が後続全体へ影響する
- 非交渉制約や運用ルールを決めないと success metrics が定義できない
- 複数案のうち 1 つを選ぶ理由を将来参照できる形で残したい

逆に、追加調査で解けるもの、単なる作業メモ、未整理の疑問は ADR ではなく discussion sheet に置きます。

## 7. template のどこを埋めるか

この playbook は骨子そのものを再掲しません。  
代わりに、各 template で特に先に埋める節を示します。

### Initiative requirement
- `目的`
- `背景・現状`
- `成功指標`
- `スコープ`
- `非交渉制約`
- `未確定事項`

### Epic requirement
- `目的`
- `ユースケース`
- `要求`
- `受け入れ条件`
- `依存 / 影響範囲`
- `未確定事項`

### Issue requirement
- `目的`
- `背景・現状`
- `スコープ`
- `境界`
- `受け入れ条件`
- `例外・エッジケース`
- `未確定事項`

## 8. reviewer に渡す前の exit criteria

次を満たしてから reviewer へ渡します。
- 目的が 1〜3 行で説明できる
- As-Is の根拠があり、主要な観測点が書けている
- MUST / MUST NOT / OUT OF SCOPE が曖昧でない
- 主要な TBD が列挙され、放置理由ではなく「質問 / 選択肢 / 推奨案」がある
- discussion / ADR が必要な論点を requirement 本文へ押し込んでいない
- 設計の話に踏み込みすぎず、WHAT / WHY に留まっている

## 9. 次 phase へ進める条件

要件定義は reviewer 承認前に次 phase へ進めません。  
次の条件を満たしたときだけ design へ進みます。

- requirement.md が reviewer 承認レベルに達している
- 重要な未確定事項が「design で扱う論点」なのか「追加調査 / ヒアリングが必要」なのか仕分けできている
- 必要な discussion / ADR が `discussions/` に残っている
- success metrics または受け入れ条件が、後続設計で参照できる粒度になっている

## 10. subagent 活用ガイダンス

shared playbook の前提は「自分で全部抱え込まない」です。

- researcher / consultant 系:
  - 外部調査、比較観点、論点整理に使う
- doc writer:
  - 既存 docs との整合確認や文面の磨き込みに使う
- reviewer:
  - requirement が WHAT / WHY から逸脱していないかを見る

注意:
- subagent に渡す前に、対象スコープ、未確定論点、期待する出力を 3 点セットで明記する
- subagent の出力をそのまま requirement に貼らず、採用判断を人間可読な形で整理する

## 11. 迷ったときの判断順

1. 追加調査で事実を増やせるか
2. ユーザーヒアリングで判断できるか
3. discussion sheet で論点を分離すべきか
4. ADR で意思決定を固定すべきか
5. それでも unresolved なら、設計へ送らず pause する
