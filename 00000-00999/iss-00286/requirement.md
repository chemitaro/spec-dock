---
種別: 要件定義書（Issue）
ID: "iss-00286"
タイトル: "仕様作成パックの差分表示と段階配置を実装する"
関連GitHub: ["#286"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00286 仕様作成パックの差分表示と段階配置を実装する — 要件定義

## 位置づけ

この文書は `epic-00283` から切り出した Issue の canonical 要件定義です。ChatGPT ZIP 仕様作成パック由来の draft artifact は証跡として採用し、この文書では Issue scope、非スコープ、受け入れ条件、例外ケースを正本として再記述します。実装開始には、この文書、`design.md`、`plan.md`、`report.md` の evidence と fresh `spec-reviewer` gate が必要です。

## 目的

valid ZIP を正本へ直接書かず、ドライラン差分とサニタイズ済み段階配置 artifact に変換する。

## 親 Epic への対応

- 対応要件: E-RQ-006, E-RQ-007
- 対応受け入れ条件: E-AC-008, E-AC-009
- 推奨グレード: `strict`
- 実施単位: T2 差分 / 段階配置

## 範囲

- valid ZIP を正本へ直接書かず、ドライラン差分とサニタイズ済み段階配置 artifact に変換する。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- 期待する成果物: ドライラン差分レポート、段階配置 renderer、adoption-map 引き渡し確認。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。

## 依存

- iss-00285

## 権威境界

- ChatGPT 出力は証跡 producer に限定する。
- `authorized_profile` は local assurance が決める。
- セルフレビューやレビュアー注目点は reviewer input であり、gate result ではない。
- ZIP 検証は fail-closed にする。

## リスク焦点

ZIP 内容が正本ファイルを直接上書きするリスクを遮断する。

## 受け入れ条件

### AC-001: 親 Epic への trace が保たれる

- 前提: この Issue の候補情報を読む。
- 操作: candidate metadata とこの要件定義を確認する。
- 期待結果: E-RQ-006, E-RQ-007 / E-AC-008, E-AC-009 へ trace できる。
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

### AC-005: pass review result だけを staging でき、正本を直接上書きしない

- 前提: `review_chatgpt_authoring_pack.py` が出した `validation-report.json` と隔離済み `specdock-authoring-pack/` tree が存在する。
- 操作: `validation-report.json.status == "pass"` の場合だけ staging renderer を実行する。
- 期待結果: canonical `requirement.md` / `design.md` / `plan.md` は直接変更されず、output directory 配下の `staging-report.json`、`staging-summary.md`、`dry-run-diff.*`、`diffs/*`、`staged-artifacts/*`、`adoption/eal-candidates.json` だけが出る。
- 観測点: staging report、dry-run diff、staged artifact、canonical docs の byte snapshot。

### AC-006: adoption-map を unreviewed EAL 候補へ変換できる

- 前提: pass review 済み pack に `adoption/adoption-map.json` が含まれる。
- 操作: staging renderer が adoption-map item を EAL candidate row に変換する。
- 期待結果: 各 candidate row の `adoption_status` は常に `unreviewed` であり、`adopted` / `rejected` / `stale` / `blocked` は採用済み状態として出力されない。
- 観測点: `adoption/eal-candidates.json`、`staging-report.json`、negative fixture report。

### AC-007: 診断と staged surface は漏えいを防ぐ

- 前提: pack metadata、adoption-map、candidate text、output path に host absolute path、secret-looking text、raw transcript marker、unsafe path string が混入する。
- 操作: staging renderer を実行する。
- 期待結果: diagnostics / summary / CLI stdout に host absolute path、secret、raw transcript、unsafe path string を出さず、unsafe content は redaction して staged artifact 化するのではなく staging を拒否する。
- 観測点: CLI stdout/stderr、`staging-report.json`、`staging-summary.md`、staged artifact の不存在。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
