---
種別: interview
ID: "20260617t003432z-interview"
タイトル: "Artifact Body Generation Scope"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連:
  - "20260617t003044z-adr"
  - "20260617t003232z-research"
scope: "issue"
scope_id: "iss-00188"
created_at: "2026-06-17T00:34:32Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260617t003232z-research"
reflected_to: []
---

# 20260617t003432z-interview Artifact Body Generation Scope

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`:
    - Runtime-owned filename generation の scope を、filename/path allocation までにするか、body/template rendering まで含めるかを決める。
  - `design.md`:
    - `new doc` command option を増やすか、generated path を作ってから guarded edit する two-step flow にするかを決める。
  - `plan.md`:
    - Test scope と implementation slices が変わる。
  - `ADR`:
    - `20260617t003044z-adr` の implementation interpretation に関わる。
- chat 上の軽微な一問では足りない理由:
  - Scope を広げると runtime command surface / tests / skill template integration が増える。広げない場合は、本文更新を agent が行う境界を明記する必要がある。

## 質問の目的
- 対象者:
  - User / product owner
- 何を明確にする質問か:
  - #188 で runtime が責任を持つ範囲を、filename allocation + initial scaffold creation に留めるか、skill-local template/body rendering まで含めるか。
- 回答が後続判断へ与える影響:
  - Requirement / design / plan の acceptance criteria と implementation steps を確定する。

## 質問
- pressure-test question:
  - "手作業 filename 禁止" の実装として、#188 では body/template 生成まで runtime API 化する必要があるか。
- 質問:
  - #188 では、PR repair batch/unit などの skill-local template body を runtime command が直接受け取って生成する option（例: `--template-file` / `--body-file`）まで追加しますか。それとも、まず runtime が filename と初期 `disc` を生成し、skill は返された path に対して本文を安全に更新する two-step flow で十分としますか。
- 回答してほしいこと:
  - Option A / B のどちらを #188 の scope とするか。

## source-grounded context
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `20260617t003044z-adr-runtime-owned-discussion-artifact-creation.md`
  - `20260617t003232z-research-manual-filename-guidance-inventory.md`
- local context で解決できたこと:
  - 現行 `new doc` は `doc_type`, scope, `--title`, optional `--slug` のみを受け取る。
  - 外部 template/body を直接受け取る option は現行 command surface にはない。
  - Manual filename construction をやめること自体は、既存 `new doc` でも可能。
- まだ人間判断が必要な理由:
  - Runtime command surface を増やすかどうかは、#188 のサイズと将来 API 方針に関わる。

## 回答案
- Option A:
  - #188 では existing `new doc` による generated path creation を必須にし、skill は返された path の本文だけを安全に更新する。
  - Runtime command option は増やさない。
- Option B:
  - #188 で `new doc` または adjacent command に `--template-file` / `--body-file` 等を追加し、filename allocation と body rendering を一つの runtime operation にする。
- Option C:
  - PR repair 専用の narrow command/helper を追加する。

## Codex の分析
- 判断軸:
  - Root cause 解消の十分性、runtime API の増加、template/front matter 破壊リスク、test burden。
- tradeoff:
  - Option A は小さく、manual filename 禁止の root cause には十分。ただし body update の guarded edit guidance が必要。
  - Option B は一貫性が高いが、command surface / rendering contract / stdin or file path handling / tests が増える。
  - Option C は過度に PR repair 専用になりやすい。
- リスク:
  - Option A のリスクは、agent が generated file の front matter / doc_id を壊すこと。
  - Option B のリスクは、#188 が generator API 設計 issue に膨らむこと。
- 具体シナリオ / edge case:
  - PR repair batch を `new doc disc --issue 188 --title "PR Repair Batch"` で作成し、返された path に `templates/pr-repair-batch.md` 由来の本文 sections を反映する。

## Codex の推奨案
- 推奨:
  - Option A を #188 の scope とする。
- 理由:
  - Root cause は filename allocation の手作業なので、filename/path generation を runtime-owned にするだけで本質は解ける。
  - Body/template command option は有用だが、#188 の最小修正からは一段大きい。
  - 必要なら plan に follow-up として Option B を残す。
- 未回答時の影響:
  - 未回答のままなら Option A を仮採用して requirement/design/plan を作成する。

## ユーザー回答
- answer capture:
  - User adopts Option A: do not add `--template-file` / `--body-file` or similar body/template inputs to `new doc` for #188.
  - Generated artifact path should be created by runtime, and skill/workflow should then update the generated file body safely.
  - Additional user requirement: add a PR branch related document type to the current `new doc` document type catalog. No broader interface addition is requested.
- 回答:
  - Option A, with added doc type for PR branch artifacts.
- 回答日時:
  - 2026-06-17T00:40:00Z

## 追加確認の要否
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Confirm the exact doc type identifier and semantic boundary for the PR branch artifact type.

## 採用判断
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - User explicitly selected Option A and rejected broader body/template command inputs for #188. User also added a new requirement to introduce a PR branch related doc type.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - Runtime-owned artifact generation scope is filename/path allocation plus initial scaffold creation, not external body/template rendering.
  - Add requirement for a PR branch related doc type.
- `design.md`:
  - Keep `new doc` interface shape unchanged except doc type catalog/template addition.
  - Generated path is authoritative; skill/workflow updates body after path creation.
- `plan.md`:
  - Add implementation slice for doc type catalog/template/tests.
- `ADR`:
  - Treat this as implementation interpretation of `20260617t003044z-adr`.
- reflected_to 更新方針:
  - Update after canonical docs are rewritten.
- adoption reflection:
  - Adopt into requirement/design/plan/report after PR branch doc type naming is confirmed.
