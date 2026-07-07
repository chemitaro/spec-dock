---
artifact_type: chatgpt-use-planning-summary
issue: iss-00289
session: required-repository-connector-context-github-6
source_session: specdock-iss-00289-planning
model: gpt-5.5-pro
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
raw_transcript_committed: false
---

# ChatGPT Use planning summary for iss-00289

## 実行結果

- 先行セッション `specdock-iss-00289-planning` は ChatGPT が「これから確認する」とだけ返したため、実装判断には使わず、follow-up セッションで具体案を取得した。
- follow-up セッション `required-repository-connector-context-github-6` は、`iss-00289` の実装方針として「既存 validator を前提に、durable dogfood fixture、validation report、section-level dry-run report、Issue `report.md` 証跡を追加する」方針を返した。
- ChatGPT output は evidence-only であり、SpecDock reviewer pass、正本採用、実装完了、PR 作成の claim として扱わない。

## 採用した判断

- `validate_selected_skeleton_fill.py` の既存 boundary を維持し、local `.assurance.json` と selected skeleton manifest を profile authority として扱う。
- selected skeleton manifest / preflight に Issue-local trace を持たせ、dogfood report が `iss-00289` / `epic-00283` / E-RQ / E-AC に trace できるようにする。
- selected-profile fill の出力に、正本を書かない section-level dry-run adoption report を追加する。
- raw ZIP は repo に commit せず、展開済み pack tree、review report、validation report、dry-run report、ZIP digest manifest を durable artifact として残す。

## 退けた案

- 配布 runtime command へ昇格する案は、この Issue の scope 外として退けた。昇格判断材料は後続 `iss-00292` に残す。
- ChatGPT の `profile_suggestion` を `authorized_profile` として採用する案は退けた。`authorized_profile` は local assurance のみを権威とする。
- full-document staging helper を selected-section fill の正本反映として扱う案は退けた。selected-section fill は section-level dry-run report と manual adoption review に留める。

## 実装への反映

- `review_chatgpt_authoring_pack.py` は preflight trace を validation report / preflight snapshot へ反映できるようにした。
- `validate_selected_skeleton_fill.py` は selected skeleton の `parent_trace` / `trace` を validation report へ反映し、`selected-skeleton-fill-dry-run.{json,md}` を出力するようにした。
- `iss-00289` の dogfood artifact は `artifacts/20260707t011500z-selected-profile-dogfood/` に保存した。
