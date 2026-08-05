---
種別: 実装時観測・ドッグフーディング分析
ID: "iss-00354-s07-projection-cleanup"
対象: "S07 Projection / docs / parent consistency"
作成日: "2026-08-05"
---

# S07 余分な投影生成物の分析と処理

## 観測

S07 の実装前に `spec-dock update` を実行したところ、今回の範囲にないランタイム投影、README、ガイド、ルール文書が大量に変更され、`.agents/skills/spec-dock-issue-planning/resources/*.md` が新規生成された。これらの `resources` は現行 provider source に存在しない。

## 原因

`spec-dock/` と `.agents/` は provider source の生成投影である。今回の更新コマンドは現行ブランチの provider sourceを使う通常の投影ではなく、リモート版パッケージの異なる世代を先に適用したため、過去または別世代の runtime/resource 群が混入した。したがって、生成物の存在だけを理由に S07 の成果物へ採用してはならない。

## 分類と処理

| 分類 | 処理 | 根拠 |
|---|---|---|
| S07 対象 | provider の Issue Planning skill、provider docs、同一内容の installed/dogfood projection、S07 implementation brief | provider source が正本であり、S07 の allowlist に含まれる |
| S07 対象外の tracked projection | HEAD の内容へ限定復元 | runtime/CLI/application/domain/infra の変更は S07 の許可範囲外 |
| provider に存在しない untracked resources | 削除 | 現行 provider source から再生成されず、正本・契約・入力資料ではない |

## 再発防止の境界

- provider 側を先に編集し、projection は同じ内容をコピーまたは既存のローカル生成手順で同期する。
- S07 では `spec-dock/scripts/spec_dock_runtime/**`、無関係な docs、Issue lifecycle state を変更しない。
- リモート package の更新を、current branch の dogfooding 同期の代用にしない。
- projection の正当性は provider／installed／dogfood の byte parity と `spec-dock validate` で確認する。

## 検証結果

- provider skill と installed projection は SHA-256 `f4fd120e30aa5941ddbaa7ab747de60e855c97d3fcc649637a50da24af89a397` で一致。
- S07 対象 docs 4 件も provider と dogfood projection が各々 byte-identical。
- S07 対象外の runtime projection 19 件と untracked resources 4 件を作業ツリーから除去。
- S07 の変更後も旧 `--context-manifest` は Issue Planning の実行契約として残していない（文書中の出現は廃止を説明する注記のみ）。

この分析は S07 の implementation evidence として `report.md` の EAL に登録する。provider source、S07 projection、親 Epic 文言、S07 brief 以外の差分を S07 の成果として採用しない。
