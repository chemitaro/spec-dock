---
種別: 要件定義書（Initiative）
ID: "init-00079"
タイトル: "minor bugfix maintenance"
関連GitHub: ["#79"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-04-17"
---

# init-00079 minor bugfix maintenance — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - dogfooding 中に見つかった minor bug を、既存の architecture / feature initiative を汚さずに継続投入できる受け皿を提供する。
- Secondary:
  - repo 内で修正可能な runtime / installer / docs contract bug と、外部 consumer app 側の問題を切り分けて管理できるようにする。

## 背景と Why now
- 現状の課題:
  - `spec-dock` をこの repo 自身で dogfooding しているため、小粒だが放置しづらい bug report が継続的に発生する。
  - そのたびに新しい initiative / epic を起こすと、architecture 投資や feature work の正本が分散しやすい。
- 影響:
  - bug の受け皿が曖昧なままだと、local actionable bug と外部 repo 固有の不安定要因が同じトラックに混ざり、修正責務がぼやける。
- なぜ今やるか:
  - `epic-00080` を初回利用し、minor bug bucket を運用可能な形に固定しておくことで、今後の dogfooding bug を一貫した手順で issue 化できる。
- 情報源:
  - dogfooding 中の issue / PR / review feedback
  - `spec-dock/initiatives/init-local-00003-*` 配下の既存 spec 運用
  - 2026-04-17 の `pr review and staging failure analysis`

## 成功指標
- Metric-001:
  - Baseline:
    - minor bug 用 initiative / epic は存在するが、内容がテンプレートのままで運用境界が未固定である。
  - Target:
    - dogfooding で見つかった repo-local minor bug を、`init-00079 / epic-00080` 配下へ issue として起票できる。
  - 計測方法:
    - `epic-00080` 配下に concrete issue が作成され、requirement / design / plan が issue 固有内容で埋まっていること。
  - 判定時期:
    - 各 minor bug issue 作成時
- Metric-002:
  - Baseline:
    - 外部 consumer app 側の flaky CI と、`spec-dock` 本体で修正すべき bug の責務境界が曖昧である。
  - Target:
    - bucket docs に、repo 内で修正可能な bug と背景 evidence の線引きが明記されている。
  - 計測方法:
    - initiative / epic / issue の scope / out-of-scope に責務境界が記載されていること。
  - 判定時期:
    - 各 issue spec review 時

## スコープ
- MUST:
  - dogfooding で見つかった repo-local minor bug を issue 単位で受け入れる。
  - runtime / installer / shipped docs / dogfooding mirror の contract bug を扱う。
  - issue ごとに修正対象と背景 evidence を切り分ける。
- MUST NOT:
  - architecture initiative が扱う大規模構造変更を取り込まない。
  - feature expansion backlog の受け皿にしない。
  - 外部 consumer app 固有の flaky test を、そのまま本 repo の修正対象へ昇格しない。
- OUT OF SCOPE:
  - 新機能追加
  - 大規模 migration / architecture realignment
  - external consumer repo の staging / deploy pipeline 修正

## 境界
- Always:
  - 1 issue = 1 actionable bug または tightly coupled contract bug とする。
  - 実装修正は repo 内で再現・検証できる範囲に閉じる。
- Ask:
  - その報告は `spec-dock` 本体の bug か、外部利用側の症状か。
  - 既存 epic へ収まるか、それとも architecture / feature 側へ送るべきか。
- Never:
  - 背景 evidence だけの外部障害を、本 repo の修正 obligation として記録しない。
  - minor bug bucket を generic todo リスト化しない。

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を dogfooding して bug を報告・修正する maintainer
- 運用者:
  - initiative / epic / issue の routing を管理する maintainer
- 開発者:
  - `src/spec_dock/` と `spec-dock/` の contract parity を保守する implementer / reviewer
- 影響システム / 領域:
  - `src/spec_dock/`
  - `spec-dock/`
  - `tests/`

## 非交渉制約
- 互換性:
  - minor bug issue でも provider-side source of truth と dogfooding mirror の関係を崩さない。
- セキュリティ / 監査:
  - GitHub-backed issue linkage を維持し、report / research に evidence を残す。
- 性能 / 可用性:
  - bugfix bucket 自体は大規模 rollout を前提にしない。
- 運用:
  - 既存 initiative / epic を再利用し、新たな bug ごとに initiative / epic を増やさない。

## リスク / 依存
- R-001:
  - bucket が広すぎると、architecture concern や external issue を誤って吸い込む。
- R-002:
  - issue の境界が曖昧だと、1 issue に複数の無関係な bug を束ねてしまう。

## 未確定事項
- なし:
  - minor bug bucket は existing reusable bucket として継続運用する。
