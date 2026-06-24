---
種別: disc
ID: "20260624t062220z-disc"
タイトル: "Routing Repair Design Options"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連:
  - "20260624t062221z-research"
  - "20260624t062338z-research"
  - "20260624t062339z-research"
authority: "synthesized"
derived_from:
  - "20260624t062221z-research-runtime-routing-failure-analysis.md"
  - "deep-consultant:019ef84b-72cc-7d80-a111-fa09dd5d2c87"
reflected_to: []
---

# 20260624t062220z-disc Routing Repair Design Options

## 論点
- Epic 00224 の動的 workflow routing で、runtime task が `security-sensitive` に過剰分類されたり `docs-only` に過小分類されたりする。
- 原因は policy matrix ではなく、plan step block から `TaskKind` を推定する `_classify_task_kind` の単純 substring heuristic。
- 修正は「軽量化」だけでなく、「重い作業を軽くしない」安全性に関わる。

## 修正案

### Option A: 現行 heuristic に否定文除外だけ追加する
- 内容:
  - `not security`、`ではない`、`扱わない`、`過剰に分類しない` などを見たら high-risk keyword を無視する。
- 長所:
  - diff が小さい。
  - MT-009 の1つ目の failure は直る。
- 短所:
  - runtime path + `docs-only verification` の過小分類は残る。
  - section awareness がなく、別の template phrase で再発しやすい。
- 判定:
  - 不十分。

### Option B: evidence-based classifier に置き換える
- 内容:
  - step block から positive / weak / negated evidence を集める。
  - security / migration / runtime / docs-only の precedence を明示する。
  - docs-only は明示 intent に限定し、template label の `docs-only verification` は signal から除外する。
- 長所:
  - MT-009 / MT-024 の両方に対応できる。
  - runtime path、unit tests、worker hint を根拠にできる。
  - current architecture に閉じ、template/schema 大変更を避けられる。
- 短所:
  - heuristic である限り表現揺れのリスクは残る。
  - negation detection を広げすぎると security false negative のリスクがある。
- 判定:
  - 今回の推奨案。

### Option C: plan step に explicit `task_kind` / `risk_tags` field を導入する
- 内容:
  - issue plan の step contract に machine-readable field を追加する。
  - heuristic は legacy fallback とする。
- 長所:
  - 最も安定する。
  - agent / human authoring の曖昧さを減らせる。
- 短所:
  - template、docs、planner、migration、existing issues への影響が大きい。
  - Epic 00224 の現在の manual-test failure 修正としては大きすぎる。
- 判定:
  - follow-up ADR / issue 候補。

## 推奨設計
- iss-00237 で実装修正する場合は Option B を採る。
- explicit field 化は今回の bug fix ではなく follow-up とする。
- `_classify_task_kind` の分類ロジックを以下のように変更する。

## 推奨 precedence

1. affirmative security evidence
   - `security_review`, `privacy_review`, `authentication`, `authorization`, `permissions`, `privilege`, `credential`, `secret`
   - ただし negated / forbidden / stop-condition context だけに出ている語は除外する。
2. migration evidence
   - `migration`, `rollback`, `schema`, `data migration`
   - ただし negated / forbidden context だけに出ている語は除外する。
3. runtime evidence
   - `dev-coder`, `code-reviewer`, `unit_tests`, `tests/`, `src/`, `spec_dock_runtime`, `commands/`, `runtime command behavior`
4. explicit docs-only evidence
   - `Task marker: docs-only`
   - `委任ロール: doc-writer`
   - allowed paths が docs / md のみ
   - verification が `docs_inspection` のみ
5. fallback
   - `runtime`

## signal の扱い

- Strong signal:
  - role hint: `dev-coder`, `doc-writer`, `code-reviewer`
  - verification: `unit_tests`, `integration_tests`, `security_review`, `privacy_review`, `docs_inspection`
  - allowed paths: `src/`, `tests/`, `spec_dock_runtime`, `docs/`, `*.md`
- Weak / ignored signal:
  - `docs-only verification`
  - `tests または docs-only verification`
  - template section labels
  - forbidden changes / stop conditions にだけ出る high-risk words
- Conflict handling:
  - runtime positive evidence と docs-only weak evidence が競合する場合は runtime。
  - affirmative security evidence と runtime evidence が競合する場合は security-sensitive。
  - signal が曖昧で docs-only か runtime か迷う場合は runtime に倒す。過小分類を避けるため。

## 必須 regression tests

- `test_workflow_next_runtime_paths_override_docs_only_verification_phrase`
  - runtime paths、`unit_tests`、`dev-coder`、`code-reviewer`、`docs-only verification` を同じ step block に含める。
  - 期待: `task_kind=runtime`、`worker=dev-coder`、`verification=["unit_tests"]`。
- `test_workflow_next_negated_security_phrase_does_not_escalate`
  - `security/privacy-sensitive として過剰に分類しない` を含める。
  - 期待: その phrase だけでは `security-sensitive` にならない。
- `test_workflow_next_affirmative_authz_terms_still_escalate`
  - `authentication`、`authorization`、`permissions`、`security_review` を含める。
  - 期待: `security-sensitive` / `xhigh`。
- `test_workflow_next_explicit_docs_only_still_routes_to_doc_writer`
  - explicit docs-only issue を含める。
  - 期待: `doc-writer` / `low` / `docs_inspection`。

## 実装影響範囲

- Primary:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
  - `tests/cli_runtime/test_workflow_context_routing.py`
- Secondary:
  - 必要に応じて installed dogfooding mirror の runtime inspection。
- 対象外:
  - policy JSON の routing matrix。
  - assurance classification policy。
  - PR observation scripts。
  - `workflow_state.py`。

## 採用判断
- 推奨: Option B を採用。
- 理由:
  - 手動テストで見つかった2つの FAIL を同時に解決できる。
  - 変更範囲が狭く、Epic 00224 の既存 architecture に沿う。
  - docs-only / security-sensitive の true positive を regression tests で守れる。
- 未採用:
  - Option A は片方の failure しか直らない。
  - Option C は長期的には望ましいが、現時点の bug fix としては大きすぎる。

## follow-up candidates
- Explicit `task_kind` / `risk_tags` field を plan step schema に追加する ADR / issue。
- `--github-issue` docs cleanup。
- symlink abuse fresh trial retest issue。
- `validate` / `doctor` の空 workspace semantics を docs に明記する issue。
