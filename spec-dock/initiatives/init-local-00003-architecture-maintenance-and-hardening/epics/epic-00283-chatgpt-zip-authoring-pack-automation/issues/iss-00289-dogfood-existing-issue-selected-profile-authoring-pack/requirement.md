---
種別: 要件定義書（Issue）
ID: "iss-00289"
タイトル: "既存 Issue の選択済みプロファイル向けパックをドッグフードする"
関連GitHub: ["#289"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00289 既存 Issue の選択済みプロファイル向けパックをドッグフードする — 要件定義

## 位置づけ

この文書は `epic-00283` から切り出した Issue の canonical 要件定義です。ChatGPT ZIP 仕様作成パック由来の draft artifact は証跡として採用し、この文書では Issue scope、非スコープ、受け入れ条件、例外ケースを正本として再記述します。実装開始には、この文書、`design.md`、`plan.md`、`report.md` の evidence と fresh `spec-reviewer` gate が必要です。

## 目的

レビュー済み Issue 要件から、local assurance が作った選択済みスケルトンだけを ChatGPT に埋めさせる流れを検証する。

## 親 Epic への対応

- 対応要件: E-RQ-008, E-RQ-009, E-RQ-010
- 対応受け入れ条件: E-AC-005, E-AC-006, E-AC-010, E-AC-011
- 推奨グレード: `strict`
- 実施単位: T2 ドッグフード B

## 範囲

- レビュー済み Issue 要件から、local assurance が作った選択済みスケルトンだけを ChatGPT に埋めさせる流れを検証する。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: selected-profile ZIP fixture、profile validation report、段階的採用 dry run。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- iss-00286, iss-00287

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

Issue の設計・計画を ChatGPT が正本として完了したように見せるリスクを遮断する。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義を確認する。
- 期待結果: E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011 へ trace できる。
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

### AC-005: local assurance compose 済み skeleton だけを埋める

- 前提: この Issue の成果物または fixture が存在する。
- 操作: reviewed requirement と selected skeleton を入力に ZIP を生成する。
- 期待結果: ChatGPT は提供された section だけを埋め、template selection は行わない。
- 観測点: validation report、staged artifact、または Issue report。

### AC-006: staged adoption flow を確認する

- 前提: この Issue の成果物または fixture が存在する。
- 操作: filled sections を stage する。
- 期待結果: section-map、missing-section-report、dry-run diff が揃い、fresh reviewer gate が未実施のまま正本完了を claim しない。
- 観測点: validation report、staged artifact、または Issue report。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
