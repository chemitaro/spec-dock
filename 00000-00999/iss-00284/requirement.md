---
種別: 要件定義書（Issue）
ID: "iss-00284"
タイトル: "仕様作成パックの事前確認とプロンプトパックを作る"
関連GitHub: ["#284"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00284 仕様作成パックの事前確認とプロンプトパックを作る — 要件定義

## 位置づけ

この文書は `epic-00283` から切り出した Issue の canonical 要件定義です。ChatGPT ZIP 仕様作成パック由来の draft artifact は証跡として採用し、この文書では Issue scope、非スコープ、受け入れ条件、例外ケースを正本として再記述します。実装開始には、この文書、`design.md`、`plan.md`、`report.md` の evidence と fresh `spec-reviewer` gate が必要です。

## 目的

ChatGPT に ZIP authoring pack の生成を依頼する前に、SpecDock 側で repo / ref / source / freshness / built-in path/secret rules / `safe_output_constraints.forbidden_claims` / profile observation を固定し、ChatGPT Use に渡す prompt-pack を決定的に作れるようにする。

この Issue の成果物は **dogfood-only / evidence-only** である。preflight JSON、prompt-pack、fixture、validation report は、正本採用、reviewer pass、Issue 完了、Pull Request 作成、または配布 runtime command の存在を意味しない。正本化は、main orchestrator が採用判断を `report.md` に記録し、fresh `spec-reviewer` gate を通した後にだけ成立する。

## 親 Epic への対応

- 対応要件: E-RQ-001, E-RQ-002, E-RQ-003
- 対応受け入れ条件: E-AC-001
- 推奨グレード: `strict`
- 実施単位: T0 事前確認 / プロンプト基盤

## 範囲

- `scripts/authoring-pack/` 配下に dogfood-only の preflight / prompt-pack authoring surface を追加する。
- repo / ref / source_paths / source hashes / stale_if / built-in path/secret rules / `safe_output_constraints.forbidden_claims` / profile snapshot を固定し、ChatGPT に渡すプロンプトパックを作る。
- Issue-local `.assurance.json` を read-only で観測し、`authorized_profile`、`status`、`stage`、file hash を snapshot として記録する。
- preflight が `pass` の場合だけ、`README.md`、`preflight.json`、`source-manifest.json`、`stale-if.json`、`validation-taxonomy.json`、`safe-output-constraints.md`、`chatgpt-use-prompt.md` で構成する prompt-pack を生成する。
- normal fixture と negative fixture を追加し、source 欠落、assurance 欠落、unsafe claim、stale hash を fail-closed に検証できるようにする。
- 親 Epic の権威境界を守り、ChatGPT 出力を証跡として扱う。
- ローカル検証、採用判断、fresh reviewer gate を後続条件として残す。

## 対象外

- ChatGPT が返した ZIP の受け入れ、保存、展開、central directory inspection。
- ZIP 内 `manifest.json` / `provenance.json` / `source-manifest.json` / `stale-if.json` / `adoption/adoption-map.json` の schema validation。
- 安全展開後の staged artifact rendering。
- 正本の `requirement.md` / `design.md` / `plan.md` を直接更新すること。
- reviewer gate を置き換えること。
- ChatGPT が `authorized_profile` を決定すること。
- ChatGPT が `.assurance.json` を作成・更新すること。
- 配布ランタイムコマンドが利用可能だと主張すること。
- 配布 runtime command として `spec-dock authoring-pack ...` を追加すること。
- profile-controlled selected skeleton filling、dogfood scenario、metrics、final PR delivery。
- この Issue 単独の Pull Request 作成。

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

### AC-002: 事前確認 JSON が repo / ref / source freshness を固定する

- 前提: この Issue の成果物または fixture が存在する。
- 操作: repo、ref、source_paths、source hashes、stale_if、built-in path/secret rules、`safe_output_constraints.forbidden_claims`、profile snapshot を含む JSON を生成する。
- 期待結果: 欠落 field がある場合は fail として扱い、prompt pack 生成へ進めない。
- 観測点: validation report、staged artifact、または Issue report。

### AC-003: required source 欠落は fail-closed になる

- 前提: required source が存在しない invalid fixture が存在する。
- 操作: preflight script を実行する。
- 期待結果: status は `fail`、exit code は non-zero、prompt-pack は生成されない。
- 観測点: pytest result、diagnostics JSON。

### AC-004: assurance snapshot は observation-only として扱われる

- 前提: Issue-local `.assurance.json` が存在する。
- 操作: preflight script を実行する。
- 期待結果: `authorized_profile`、`status`、`stage`、`.assurance.json` の `sha256` は出力に記録されるが、`.assurance.json` 自体は変更されない。ChatGPT は profile authority を持たない。
- 観測点: `preflight.json.assurance_snapshot`、`git diff -- spec-dock/.../iss-00284.../.assurance.json`、Issue report。

### AC-005: assurance 欠落は blocked になる

- 前提: `.assurance.json` が存在しない invalid fixture が存在する。
- 操作: preflight script を実行する。
- 期待結果: status は `blocked`、ChatGPT に profile を推定させる prompt-pack は生成されない。
- 観測点: pytest result、diagnostics JSON。

### AC-006: プロンプトパックが権威境界を含む

- 前提: この Issue の成果物または fixture が存在する。
- 操作: ChatGPT に渡す prompt pack を確認する。
- 期待結果: `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true`、禁止 claim、出力 root、stale_if、source manifest、no-per-Issue-PR relay policy が明示される。
- 観測点: validation report、staged artifact、または Issue report。

### AC-007: unsafe path / unsafe claim は rejected になる

- 前提: unsafe path または forbidden claim を含む invalid fixture が存在する。
- 操作: preflight script を実行する。
- 期待結果: status は `rejected`、prompt-pack は adoption-ready と扱われない。
- 観測点: pytest result、diagnostics JSON。

### AC-008: stale source hash は stale になる

- 前提: expected source hash と current file hash が一致しない invalid fixture が存在する。
- 操作: preflight script を実行する。
- 期待結果: status は `stale`、再生成または reconciliation が必要だと診断される。
- 観測点: pytest result、diagnostics JSON。

### AC-009: status taxonomy が report に転記可能である

- 前提: `validation-taxonomy.json` が生成される。
- 操作: status taxonomy を読む。
- 期待結果: `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` の意味が明示され、`unreviewed` は adoption state として分離される。
- 観測点: `validation-taxonomy.json`、Issue `report.md` update。

### AC-010: 正本直接上書きと PR 作成を行わない

- 前提: preflight / prompt-pack 生成を実行する。
- 操作: `git status --short` と `git diff --check` を確認する。
- 期待結果: 変更は許可された `scripts/authoring-pack/**`、`tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`、`tests/fixtures/authoring_pack/**`、Issue `report.md` update に限定され、canonical docs の自動上書き、`.assurance.json` mutation、Pull Request 作成がない。
- 観測点: `git status --short`、`git diff --check`、Issue `report.md`。

### AC-011: 検証コマンドが実行可能である

- 前提: 実装後の working tree。
- 操作: `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`、`./spec-dock/scripts/spec-dock validate`、`git diff --check` を実行する。
- 期待結果: P0/P1 blocker がない。失敗時は blocker と next action を Issue `report.md` に残す。
- 観測点: command output、Closure Evidence Ledger、Final Gate。


## 例外ケース

- GitHub connector / ChatGPT / ZIP generation が使えない場合は blocked または skipped evidence とし、手動 authoring path へ戻る。
- source hash mismatch または stale_if hit は regeneration / reconciliation 対象にする。
- 危険な権威表現が混入した場合は local validation で止める。
- `.assurance.json` が存在しない、または parse できない場合は `blocked` とし、ChatGPT が profile を推定する path を作らない。
