---
種別: 要件定義書（Issue）
ID: "iss-00284"
タイトル: "仕様作成パックの事前確認とプロンプトパックを作る"
関連GitHub: ["#284"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00284 仕様作成パックの事前確認とプロンプトパックを作る — 要件定義

## 位置づけ

この文書は `epic-00283` から切り出した Issue の canonical 要件定義です。ChatGPT ZIP 仕様作成パック由来の draft artifact は証跡として採用し、この文書では Issue scope、非スコープ、受け入れ条件、例外ケースを正本として再記述します。実装開始には、この文書、`design.md`、`plan.md`、`report.md` の evidence と fresh `spec-reviewer` gate が必要です。

## 目的

repo / ref / source_paths / stale_if / denylist / profile snapshot を固定し、ChatGPT に渡すプロンプトパックを作る。

## 親 Epic への対応

- 対応要件: E-RQ-001, E-RQ-002, E-RQ-003
- 対応受け入れ条件: E-AC-001
- 推奨グレード: `strict`
- 実施単位: T0 事前確認 / プロンプト基盤

## 範囲

- repo / ref / source_paths / stale_if / denylist / profile snapshot を固定し、ChatGPT に渡すプロンプトパックを作る。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: 事前確認 JSON スキーマ案、プロンプトパック案、ソース一覧 fixture、stale_if fixture。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- なし

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

branch / ref / source provenance が曖昧なまま ZIP 生成へ進むリスクを遮断する。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義を確認する。
- 期待結果: E-RQ-001, E-RQ-002, E-RQ-003 / E-AC-001 へ trace できる。
- 観測点: candidate metadata、Epic report の採用台帳。

### AC-002: 権威境界が明示される

- 前提: ChatGPT ZIP 由来のドラフトを読む。
- 操作: scope、non-scope、profile fields を確認する。
- 期待結果: `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` が保たれる。
- 観測点: Markdown frontmatter、`profile.json`、検証 report。

### AC-003: ローカル検証が必須条件として残る

- 前提: candidate output が有用そうに見える。
- 操作: local validation と fresh reviewer gate の必要性を確認する。
- 期待結果: local validation / canonical rewrite / reviewer gate なしに downstream work を開始可能とは扱わない。
- 観測点: report evidence gate proposal。

### AC-004: 成果物を独立にレビューできる

- 前提: candidate deliverable が作られた。
- 操作: reviewer-focus と validation report を読む。
- 期待結果: reviewer が local adoption 可否を判断する観測点を持つ。
- 観測点: candidate report evidence。

### AC-005: 事前確認 JSON が生成できる

- 前提: この Issue の成果物または fixture が存在する。
- 操作: repo、ref、source_paths、source hashes、stale_if、denylist、profile snapshot を含む JSON を生成する。
- 期待結果: 欠落 field がある場合は fail として扱い、prompt pack 生成へ進めない。
- 観測点: validation report、staged artifact、または Issue report。

### AC-006: プロンプトパックが権威境界を含む

- 前提: この Issue の成果物または fixture が存在する。
- 操作: ChatGPT に渡す prompt pack を確認する。
- 期待結果: `authority: evidence_only`、禁止 claim、出力 root、stale_if、source manifest が明示される。
- 観測点: validation report、staged artifact、または Issue report。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
