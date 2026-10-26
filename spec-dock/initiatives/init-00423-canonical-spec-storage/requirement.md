---
種別: 要件定義書（Initiative）
ID: "init-00423"
タイトル: "Canonical Spec Storage Architecture"
関連GitHub: ["#423"]
状態: "draft"
最終更新: "2026-10-26"
---

# init-00423 Canonical Spec Storage Architecture — 要件定義

詳細: [Requirement Guide](../../docs/authoring/requirement.md)

表示名：仕様の保管の仕組みを、正本が1か所の形に作り直す

## 目的

SpecDock が扱う仕様を、ブランチやworktreeに分散させず、内容と構造のそれぞれに1か所の正本を持つ形にする。人とエージェントが、どこからでも同じ最新の仕様を見て作業できるようにする。

## 背景

今は、仕様のツリーをすべてのブランチが追跡しているため、最新の状態がworktreeごとに分かれ、中央で全体を把握できない。構造の情報は `.meta.json` にだけあり、GitHub Issue と食い違っている。詳しくは [epic-00424 の要件定義書](epics/epic-00424-canonical-spec-catalog/requirement.md) を参照する。

この Initiative は、本来の親である `init-local-00003`（Architecture Maintenance and Hardening）が GitHub の #31 に結び付き、その #31 が別の題名で閉じているため、新しく作った。

## 観測可能な要件

- 仕様の内容の正本が `spec-dock/canonical` ブランチの1か所にあり、どのworktreeからも同じ最新の状態が見える。
- 仕様の構造の正本が GitHub Issue にあり、`.meta.json` がない。
- SpecDock がこの仕組みを提供し、spec-dock 自身がそれで運用している。
- 利用者のすべてのリポジトリ（spec-dock を含む5つ）が、この仕組みで運用している。
- SpecDock から従来の仕組みのコードが撤去され、1つの仕組みだけになっている。

## スコープ

- 対象：仕様の保管、同期、構造の正本、利用者の5つのリポジトリの移行、従来の仕組みのコードの撤去（epic-00424）。その1か所の正本を見渡す HTML のダッシュボード（epic-00427。2026-10-25 に epic-00425 から分け、要件を整理している）と、仕様の文書の CUE と HTML への移行（epic-00425。epic-00424 の後に議論する）。
- 対象外：第三者のリポジトリの移行の支援。

## 失敗・境界条件

- 移行の途中で、仕様や構造が失われたり、食い違ったりしてはならない。
- 人がPRをマージする関門を変えない。

## 受け入れ条件

- epic-00424 の受け入れ条件を満たす。
- 利用者の5つのリポジトリで、新しい仕組みでの運用が続いている。

## 制約・前提

- GitHub の個人アカウントで運用する。
- 対応するのは Linux と macOS。
