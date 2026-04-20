---
種別: 要件定義書（Epic）
ID: "epic-00080"
タイトル: "minor bug fixes"
関連GitHub: ["#80"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-04-17"
親: ["init-00079"]
---

# epic-00080 minor bug fixes — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-00079` の reusable bucket として、repo-local actionable bug を issue 単位で受け入れ、minor fix を継続運用できるようにする。
- この epic が提供する能力:
  - minor runtime / installer / docs contract bug を、single actionable issue に分割して追跡できる。

## ユースケース
- happy path:
  - maintainer が dogfooding 中に runtime bug を見つけ、`epic-00080` 配下へ新規 issue を作成する。
  - issue は repo 内で修正可能な範囲に閉じ、必要なら research と issue spec を付けて実装準備する。
- exception / operation scenario:
  - 外部 consumer app の staging failure など、背景 evidence はあるが本 repo の直接修正対象ではない報告を受ける。
  - その場合は background evidence として issue/research へ添付するだけに留め、修正対象には含めない。

## Epic requirements
- E-RQ-001:
  - repo 内で修正可能な minor runtime / installer / shipped docs / dogfooding mirror bug のみを受け入れること。
- E-RQ-002:
  - issue は single actionable bug または tightly coupled contract bug に閉じること。
- E-RQ-003:
  - 外部 consumer app 側の flaky CI / staging failureは、そのまま本 epic の fix scope に含めないこと。
- E-RQ-004:
  - 各 issue は requirement / design / plan を持ち、必要に応じて research で evidence を残すこと。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - dogfooding から repo-local actionable bug report が 1 件ある
  - When:
    - `epic-00080` 配下に issue を作成する
  - Then:
    - issue が GitHub-linked node として生成され、issue docs が bug 固有内容で埋められる
  - 観測点:
    - `spec-dock/.agent/index.json`
    - issue requirement / design / plan / report
- E-AC-002:
  - Given:
    - bug report に external consumer app 側の staging failure evidence が含まれる
  - When:
    - issue scope を定義する
  - Then:
    - issue は repo-local fix scope に閉じ、staging failure は background evidence / non-goal として扱われる
  - 観測点:
    - epic requirement / design / plan
    - issue requirement / design / research

## スコープ
- MUST:
  - minor bug issue の受け皿として機能する
  - repo-local actionable bug の境界を明文化する
- MUST NOT:
  - architecture initiative の大規模構造変更を取り込まない
  - external consumer app の症状をそのまま fix target にしない
- OUT OF SCOPE:
  - feature expansion
  - large migration
  - external consumer repo の pipeline 修正

## 境界
- Always:
  - issue ごとに修正対象を 1 つに閉じる
  - background evidence と fix scope を分ける
- Ask:
  - その bug は repo 内で再現・検証できるか
- Never:
  - unrelated bug を 1 issue に束ねる
  - background evidence だけで本 epic の bug と断定する

## 非機能要件
- performance:
  - bucket 自体に特別な性能要件はない
- reliability / consistency:
  - issue docs と GitHub issue の対応が一貫していること
- security:
  - evidence に秘匿情報を含めないこと
- operations:
  - issue 作成後に active set / validate / sync が可能であること

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/`
  - `spec-dock/`
  - `tests/`
- external dependency:
  - GitHub issue creation / sync
- compatibility:
  - provider-side source of truth と dogfooding mirror parity を維持する

## 未確定事項
- なし:
  - 最初の concrete issue は `iss-00082` とする
