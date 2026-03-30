---
種別: disc
ID: "20260330t053149z-disc"
タイトル: "acceptance-review-findings-analysis"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["iss-00038"]
関連: []
---

# 20260330t053149z-disc acceptance-review-findings-analysis

## 議題 (必須)
- `iss-00038` の受け入れレビューで見つかった 2 論点について、問題の性質、放置リスク、修正要否、修正案、ベストプラクティスを整理する。
- 本シートは Codex の確認結果と consultant の第三者分析を統合した判断材料として扱う。

## 背景 (必須)
- 受け入れレビューの結果、実装内容そのものではなく、final close-out record の整合に関する 2 点の懸念が見つかった。
- 今回の対象は次の 2 点のみである。
  - 論点1:
    - `report.md` の S04 記録に「未コミット」「final review pass 後に実施予定」が残っている一方で、実際の git history には該当差分を含む commit が存在する。
  - 論点2:
    - `report.md` front matter の `状態` が `draft | approved` のままで、最終状態が単一値に正規化されていない。
- コミットメッセージのフォーマット問題は、今回の分析対象外とする。

## 選択肢 (必須)

### 論点1: S04 記録が「未コミット」のままで git history と矛盾している

- 問題の性質:
  - 監査証跡の不整合である。
  - `report.md` は実装完了と受け入れ判断の正本に近い位置づけであるため、文書内の事実と git history が食い違うと、記録の信頼性が下がる。
- 放置リスク:
  - reviewer や後続担当者が「どの状態が確定版か」を誤読する。
  - close-out が本当に成立した時点や、どの commit を根拠に見ればよいかが曖昧になる。
  - 事後監査や差分追跡時にノイズになる。
  - issue close / epic close の判断材料としての authority が下がる。
- 修正要否:
  - 修正推奨。
  - 実装そのものの欠陥ではないが、`iss-00038` は final close-out record を担う issue なので、ここは事実に合わせる価値が高い。

- Option A:
  - 内容:
    - S04 の「未コミット」表記を実際の commit hash に置き換える。
  - Pros:
    - 最も単純で、読む側が迷わない。
    - final state が即座に分かる。
    - 監査性と可読性のバランスがよい。
  - Cons:
    - 当時の時系列メモは薄くなる。

- Option B:
  - 内容:
    - 「当時は未コミットだったが、その後 commit 済み」と補注する。
  - Pros:
    - 実行時系列を残せる。
  - Cons:
    - final record としては少し冗長。
    - close-out issue では読み筋が増えてしまう。

- Option C:
  - 内容:
    - S04 は当時のログのまま残し、末尾に finalized state 節を足して確定 commit を明記する。
  - Pros:
    - 実行時系列と最終状態を分離できる。
  - Cons:
    - 仕組みとしては丁寧だが、今回の問題に対しては重い。
    - close-out issue の report としては過剰になりやすい。

### 論点2: front matter の状態が `draft | approved` のままで曖昧

- 問題の性質:
  - 状態値のスキーマ不整合である。
  - `draft | approved` はテンプレート記法であり、確定状態としては曖昧である。
- 放置リスク:
  - 人間にも機械にも「最終状態が何か」を確定できない。
  - 将来 status を集計・検証・同期する処理がある場合に壊れやすい。
  - requirement/design/plan は `approved` なのに report だけ曖昧、という文書整合の崩れが残る。
  - レビュー済みなのか未確定なのか、front matter だけでは判定できない。
- 修正要否:
  - 修正すべき。
  - 軽微だが、放置メリットがなく、修正コストも低い。

- Option A:
  - 内容:
    - `状態: "approved"` に正規化する。
  - Pros:
    - 最小変更で整合が取れる。
    - requirement/design/plan と揃う。
    - final artifact として自然。
  - Cons:
    - 受け入れフローを厳密に段階管理したい場合は情報量が少ない。

- Option B:
  - 内容:
    - report は `draft` のままにし、受け入れ完了後に reviewer が `approved` へ更新する運用に切り分ける。
  - Pros:
    - 実装担当と reviewer の責務分離を明確にできる。
  - Cons:
    - 現 repo ではその運用ルールが固定されていない。
    - かえって解釈差を増やす可能性がある。

- Option C:
  - 内容:
    - `状態` は単一値のままにしつつ、別フィールドで `review_status` や `accepted_at` を追加する。
  - Pros:
    - 将来的な制度設計としては拡張性がある。
  - Cons:
    - 今回の論点に対しては過剰。
    - 他文書とのスキーマ整合も別途必要になる。

## 推奨案 (必須)
- consultant と Codex の共同見解として、次を推奨する。

### 論点1の推奨案
- Option A を推奨する。
- 理由:
  - final close-out record では、時系列の機微より「最終的に何が確定したか」の明確さが重要である。
  - 実 commit を明記するのが最も単純で、監査性が高い。

### 論点2の推奨案
- Option A を推奨する。
- 理由:
  - すでに requirement/design/plan が `approved` であり、report も final artifact として使う前提なので、ここだけ曖昧にする理由がない。
  - 最小修正で文書整合が回復する。

### 総合推奨
- 実務上のベストプラクティスは次の 2 点を同時に行うこと。
  - 論点1:
    - S04 の「未コミット」表記を実 commit hash に置換する。
  - 論点2:
    - `状態` を `approved` に正規化する。
- どちらも修正コストは低く、close-out record の信頼性向上効果が高い。

## 実装担当者へのメッセージ (必須)
- この 2 論点は実装内容の欠陥ではなく、final close-out record の監査性と状態整合の問題です。
- したがって、runtime や docs contract の実装を触る話ではなく、`report.md` の最終状態を事実ベースに整える話として扱ってください。
- 修正するなら最小差分で十分です。制度設計のような大きな変更は不要です。

## 次アクション (必須)
- 受け入れ前に `report.md` の S04 記録を実 commit ベースへ整えるか判断する。
- 受け入れ前に `report.md` front matter の `状態` を単一値へ正規化するか判断する。
- もし修正するなら、上記 2 点は最小差分で先に整え、その後に再度 acceptance review を行う。
