---
種別: 要件定義書（Issue）
ID: "iss-00287"
タイトル: "プロファイル制御されたスケルトン記入検証を実装する"
関連GitHub: ["#287"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00287 プロファイル制御されたスケルトン記入検証を実装する — 要件定義

## 位置づけ

この文書は `epic-00283` から切り出した Issue の canonical 要件定義です。ChatGPT ZIP 仕様作成パック由来の draft artifact は証跡として採用し、この文書では Issue scope、非スコープ、受け入れ条件、例外ケースを正本として再記述します。実装開始には、この文書、`design.md`、`plan.md`、`report.md` の evidence と fresh `spec-reviewer` gate が必要です。

## 目的

local assurance が決めた選択済みプロファイル、テンプレートハッシュ、セクション一覧と、ChatGPT の section fill を照合する。

## 親 Epic への対応

- 対応要件: E-RQ-008, E-RQ-009
- 対応受け入れ条件: E-AC-005, E-AC-006
- 推奨グレード: `strict`
- 実施単位: T1 プロファイル制御

## 範囲

- local assurance が決めた選択済みプロファイル、テンプレートハッシュ、セクション一覧と、ChatGPT の section fill を照合する。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: selected skeleton fill validator、profile-resolution validator、template hash validator、section-map validator、missing-section-report validator。
- local selected skeleton manifest を唯一の selected skeleton authority とし、candidate の target metadata と照合する。
- ChatGPT の `profile_suggestion` は advisory evidence として report に残せるが、`authorized_profile` の決定や変更には使わない。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- iss-00284, iss-00285

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

ChatGPT の推奨が authorized profile と誤認されるリスクを遮断する。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義を確認する。
- 期待結果: E-RQ-008, E-RQ-009 / E-AC-005, E-AC-006 へ trace できる。
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

### AC-005: authorized_profile を ChatGPT 推奨で上書きしない

- 前提: この Issue の成果物または fixture が存在する。
- 操作: `.assurance.json` と ChatGPT `profile_suggestion` が異なる fixture を検査する。
- 期待結果: `.assurance.json` は変更されず、ChatGPT 推奨は advisory evidence に留まる。candidate の `target.profile` が local `authorized_profile` と異なる場合は `stale` として止まる。
- 観測点: validation report、staged artifact、または Issue report。

### AC-006: section-map と skeleton hash を照合する

- 前提: この Issue の成果物または fixture が存在する。
- 操作: selected skeleton、section inventory、section-map、missing-section-report を持つ fixture を検査する。
- 期待結果: `template_sha256`、`skeleton_sha256`、`section_inventory_sha256` が local selected skeleton manifest と一致する場合だけ section fill validation に進む。不一致は `stale`、allowed section 外の fill は `rejected`、required section 欠落は `fail` になる。
- 観測点: validation report、staged artifact、または Issue report。

### AC-007: 検証 report は採用可否を section 単位で説明できる

- 前提: selected skeleton fill validator の output が存在する。
- 操作: `selected-skeleton-fill-validation-report.json` と summary を確認する。
- 期待結果: `eligible_section_ids`、`missing_section_ids`、`extra_section_ids`、section body の unsafe claim 検査結果、`canonical_written=false`、`assurance_mutated=false` を確認できる。
- 観測点: validation report、summary、Issue report。

### AC-008: validator は正本と assurance を直接変更しない

- 前提: `.assurance.json` と canonical docs の bytes を記録する。
- 操作: selected skeleton fill validator を実行する。
- 期待結果: `.assurance.json`、`requirement.md`、`design.md`、`plan.md`、`report.md` は validator によって変更されない。
- 観測点: focused test、git diff、validation report。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
- optional section 欠落は warning として report に残す。required section 欠落は成功扱いにしない。
