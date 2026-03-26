# 004-disc-review-analysis-docs-contract-test-brittleness

## 対象指摘
- 指摘:
  - docs contract test が prose の exact wording に寄りすぎており brittle である。
- 参照:
  - `tests/cli_runtime/test_wrappers.py`
  - `src/spec_dock/assets/spec_dock/docs/`

## 結論
- 妥当性:
  - 妥当
- 修正必要性:
  - 中
- 推奨:
  - wording の完全一致を減らし、command path / rules reference / wrapper absence など stable contract signal へ assertion を寄せる。

## 妥当性の分析
- docs test の役割は、文章の完成度を守ることではなく、利用者が踏むべき contract を壊していないことを守ることにある。
- 今回の test は wrapper 廃止後の導線をかなり丁寧に見ているが、その一部は「表現の選び方」に依存している。
- docs は今後も wording 調整が入りうるため、過剰に prose と結びついた test は保守ノイズになりやすい。
- 一方で、docs contract 自体は重要であり、test を弱めすぎると wrapper 復活や誤った command 例の混入を見逃す。

## いま修正すべきか
- 修正した方がよいが、優先度は P2 より低い。
- 理由:
  - これは correctness というより maintainability の問題だから。
  - ただし docs の微修正が多い repo では、先送りすると継続的にノイズ源になりやすい。

## 修正案

### 案A
- 既存 test を維持しつつ、assertion を stable signal に差し替える。
- 内容:
  - 残す:
    - `./spec-dock/scripts/spec-dock ...` command examples
    - `spec-dock/docs/rules/...` reference
    - `new-epic` / `new-issue` / `wrapper` absence
  - 減らす:
    - 「正本は後者」「入口/ナビゲーション用」など説明文の exact wording
- 利点:
  - test の目的を維持したまま brittle さを減らせる。
  - 既存構造を壊さない。
- 欠点:
  - どこまでを stable とみなすかの整理が必要。

### 案B
- docs contract test を helper ベースへ再構成し、各 docs で invariant だけを宣言的に確認する。
- 利点:
  - 長期的には読みやすい。
- 欠点:
  - 今回の issue に対してはやや大きい。
  - test の再設計色が強く、シンプル修正から外れやすい。

### 案C
- 現状維持。
- 利点:
  - 作業不要。
- 欠点:
  - 文面調整ごとに無関係な failure が起きやすい。
  - docs 改善の機動力を下げる。

## 採用方針
- 案A を採用するのが最も良い。
- 理由:
  - いまのテスト価値を保ちながら、保守ノイズだけを減らせる。
  - 今回の repo 方針である「最小で明快な修正」に沿う。

## 推奨する具体修正
- docs ごとの assertion を 3 種類へ寄せる。
  - 正しい runtime command が書かれている
  - 正しい `docs/rules/**` が参照されている
  - wrapper / legacy command が出てこない
- 説明文 assertion は、完全一致ではなく少数の stable keyword に絞るか、不要なら削除する。
- negative assertion も、wrapper 復活や古い command path 混入に直接効くものだけ残す。

## 見送る場合の判断
- 見送り可能ではある。
- ただし後回しにすると、以後の docs wording 調整のたびに review/CI ノイズを増やす可能性が高い。
- correctness より maintainability の debt として扱うのが適切である。
