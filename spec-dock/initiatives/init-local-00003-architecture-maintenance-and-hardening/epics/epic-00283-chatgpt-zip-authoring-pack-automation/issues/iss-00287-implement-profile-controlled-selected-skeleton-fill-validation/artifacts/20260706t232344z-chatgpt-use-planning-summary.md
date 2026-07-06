---
種別: ChatGPT Use planning summary
ID: "iss-00287"
session: "specdock-iss-00287-planning"
model: "gpt-5.5-pro extended"
generated_at: "2026-07-06T23:23:44Z"
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# iss-00287 ChatGPT Use 計画要約

## 採用する要点

- 既存の `prepare` / `review` / `stage` を大きく変えず、新規の dogfood-only validator として `validate_selected_skeleton_fill.py` と `authoring_pack_selected_skeleton_fill.py` を追加する。
- validator は review 済み pack と local selected skeleton manifest を照合し、section fill 候補の採用可否だけを evidence として報告する。
- `.assurance.json`、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は直接変更しない。
- ChatGPT の `profile_suggestion` は advisory evidence として記録するが、local `authorized_profile` の決定には使わない。
- candidate の `target.profile`、`template_sha256`、`skeleton_sha256`、`section_inventory_sha256` が local snapshot と一致しない場合は `stale` とする。
- allowed section 以外の fill、unsafe authority claim、`.assurance.json` 更新を示す claim は fail-closed で拒否する。
- required section 欠落は `fail`、optional section 欠落は warning として report に残す。

## 推奨出力

- `selected-skeleton-fill-validation-report.json`
- `selected-skeleton-fill-validation-summary.md`
- `.specdock-selected-skeleton-fill-validation`

report には `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を持たせ、`profile_validation`、`skeleton_validation`、`section_inventory_validation`、`section_results`、`adoption.canonical_written=false`、`adoption.assurance_mutated=false` を記録する。

## 推奨テスト

- valid fill は pass し、profile suggestion mismatch は advisory warning に留まる。
- candidate target profile mismatch、template hash mismatch、skeleton hash mismatch、section inventory hash mismatch は `stale`。
- extra section は `rejected`。
- required section 欠落は `fail`。
- section body / metadata の unsafe authority claim は `rejected`。
- review report non-pass、pack digest mismatch、output dir ownership violation、`.assurance.json` 非変更、canonical docs 非変更を検証する。

## 注意点

- ChatGPT connector は GitHub Issue `#287` と default branch を確認したが、current branch search は見つからなかったと報告した。ローカルでは `iss-00287-implement-profile-controlled-selected-skeleton-fill-validation` を push 済みであり、以降の採用判断はローカル repository facts と添付 bundle を優先する。
- selected skeleton manifest の正式な runtime contract はまだないため、この Issue では fixture / manual evidence の最小 manifest と normalized model で閉じる。
