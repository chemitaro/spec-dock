---
種別: 要件定義書（Issue）
ID: "iss-00291"
タイトル: "仕様作成パックのワークフローと採用台帳例を文書化する"
関連GitHub: ["#291"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00291 仕様作成パックのワークフローと採用台帳例を文書化する — Issue 要件定義ドラフト

## 位置づけ

この文書は `epic-00283` から切り出した Issue の要件定義ドラフトです。fresh `spec-reviewer` 前の planning input であり、`authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` の範囲で扱います。

## 目的

ドッグフード専用ワークフロー、プロンプト規約、権威境界、EAL 例、手動フォールバックを日本語ファーストで文書化する。

## 親 Epic への対応

- 対応要件: E-RQ-007, E-RQ-012, E-RQ-013
- 対応受け入れ条件: E-AC-009, E-AC-012
- 推奨グレード: `standard`
- 実施単位: T3 文書 / 引き渡し

## 範囲

- ドッグフード専用ワークフロー、プロンプト規約、権威境界、EAL 例、手動フォールバックを日本語ファーストで文書化する。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: 日本語 README、プロンプト規約案、EAL 例、手動フォールバック notes。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- iss-00284, iss-00285, iss-00286

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

ユーザーが provider detail や ChatGPT 出力を正本と誤認するリスクを下げる。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義ドラフトを確認する。
- 期待結果: E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012 へ trace できる。
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

### AC-005: 日本語ファーストの利用手順を提供する

- 前提: この Issue の成果物または fixture が存在する。
- 操作: README / prompt rules draft を確認する。
- 期待結果: ドッグフード専用、証跡専用、正本非置換、manual fallback が日本語で説明される。
- 観測点: validation report、staged artifact、または Issue report。

### AC-006: EAL 例が採用状態を区別する

- 前提: この Issue の成果物または fixture が存在する。
- 操作: EAL proposal examples を確認する。
- 期待結果: adopted / partially_adopted / rejected / stale / blocked / deferred の使い分けが示される。
- 観測点: validation report、staged artifact、または Issue report。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
