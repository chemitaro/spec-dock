# PR #41 Copilot Review Analysis — README Example Consistency

## 対象レビュー
- reviewer:
  - Copilot
- comment:
  - `README.md` の step-by-step example で、`new epic --initiative 123` の直後に `new issue --epic 1` を使っており、親 epic の参照が内部不整合になっている
- source:
  - `https://github.com/chemitaro/spec-dock/pull/41#discussion_r3009925221`

## 事実確認
- 対象箇所:
  - [README.md](/srv/mount/spec-dock/README.md#L73)
  - [README.md](/srv/mount/spec-dock/README.md#L77)
  - [README.md](/srv/mount/spec-dock/README.md#L84)
- 現在の例では、次の 3 つが混在している:
  - initiative create は `id=init-00123`
  - epic create は `--initiative 123` で `id=epic-00124`
  - issue create / link example は `--epic 1` と `id=iss-00123`
- この並びだと、直前に作った epic を親にしているようには読めない。少なくとも README の逐次実行例としては不整合。

## 妥当性判定
- 判定:
  - 妥当
- 理由:
  - 指摘は runtime bug ではなく docs example の内部整合性の問題だが、README の手順をそのまま試す利用者に誤誘導を起こす。
  - 特に `--epic 1` は、直前の `epic-00124` / GitHub issue `124` 想定と接続して読めない。

## 影響度
- severity:
  - medium
- user impact:
  - onboarding 時の混乱
  - README をそのままトレースした場合の parent 指定ミス
  - CLI contract の理解コスト上昇

## 修正要否
- before merge:
  - 修正推奨
- rationale:
  - 実装契約そのものは壊していないため blocker ではないが、トップレベル README の usage example としては早めに揃える価値が高い。
  - 修正コストが低く、レビュワー指摘の再発防止効果が高い。

## 修正案
- Option A:
  - 後続 example の parent 指定を、直前に生成した exact node id に揃える
  - 例:
    - `new epic --initiative init-00123 ...`
    - `new issue --epic epic-00124 ...`
  - pros:
    - sequential example として最も追いやすい
    - GitHub issue number の連番仮定に依存しない
    - numeric shorthand の解釈 ambiguity を避けられる
  - cons:
    - 記述がやや長い
- Option B:
  - 後続 example の parent 指定を numeric shorthand に揃える
  - 例:
    - `new issue --epic 124 ...`
  - pros:
    - 短い
    - shorthand の存在も示せる
  - cons:
    - GitHub issue number が sequential に増える前提に依存する
    - README の手順例としては暗黙知が多い
- Option C:
  - 現行 example を残し、「numbers are illustrative only」と注記する
  - pros:
    - 最小修正
  - cons:
    - 逐次実行 example としての誤読を解消できない
    - reviewer 指摘の核心を外す

## 推奨案
- recommended:
  - Option A
- reason:
  - この README は「順に実行する usage example」として読まれるため、親参照は exact node id で明示する方が安全。
  - shorthand を見せたいなら別の独立した example に分離する方がよい。逐次 example に shorthand を混ぜると、今回のように parent/issue number/local id の関係が不透明になる。

## 具体化方針
- update target:
  - [README.md](/srv/mount/spec-dock/README.md)
- concrete change:
  - epic create の parent を `init-00123` に揃える
  - issue create / link example の parent を `epic-00124` に揃える
  - issue id comment も example の文脈に合わせて更新する
- note:
  - shorthand 自体を消す必要はない。残すなら sequential walkthrough とは別ブロックに分けるのが望ましい。

## consultant view
- docs example は runtime の省略形を全部見せるより、誤解なく実行できる一本道を優先すべき。
- この種の example は「短さ」より「追従可能性」の方が価値が高い。
