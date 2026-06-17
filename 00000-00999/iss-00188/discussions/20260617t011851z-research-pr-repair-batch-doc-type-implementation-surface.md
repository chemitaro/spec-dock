---
種別: research
ID: "20260617t011851z-research"
タイトル: "PR Repair Batch Doc Type Implementation Surface"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連:
  - "20260617t011204z-interview"
authority: "synthesized"
derived_from:
  - "20260617t003432z-interview"
  - "20260617t011204z-interview"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260617t011851z-research PR Repair Batch Doc Type Implementation Surface

## 調査目的
- User が確定した `pr-repair-batch` doc type 追加について、runtime / validation / templates / docs / tests の変更面を洗い出す。
- `pr-repair-batch` が hyphenated doc type であることによる parser / malformed detection のリスクを確認する。

## sources / 調査方法
- 参照先:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/templates/discussions/`
  - `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/unit/infra/test_init_update.py`
- 検証手順:
  - `rg` で discussion doc types / filename regex / template catalog / tests を検索。
  - Relevant source snippets を `sed` で確認。

## facts / 観測できた事実
- Runtime creatable doc type catalog は `_CREATABLE_DISCUSSION_DOC_TYPES` にある。
  - Current creatable types: `adr`, `disc`, `research`, `interview`, `scratch`, `draft-requirement`, `draft-design`, `draft-plan`
- Runtime filename parser `_DISCUSSION_DOC_FILENAME_RE` は explicit alternation で doc type を列挙している。
  - `pr-repair-batch` を追加する場合、この regex も追加が必要。
- Validation 側 `_DISCUSSION_DOC_TYPES` と `_DISCUSSION_DOC_TIMESTAMP_FILENAME_RE` も explicit alternation で doc type を列挙している。
- Malformed detection は `_is_malformed_discussion_doc_candidate()` で `stem.split("-")` し、`parts[1]` または `parts[2]` が known doc type かを見る。
  - Hyphenated doc type `pr-repair-batch` は split すると `pr`, `repair`, `batch` に分かれるため、この helper はそのままでは doc type token として認識できない。
  - Valid filename regex が先に fullmatch するため valid `20260617t000000z-pr-repair-batch-title.md` は通せるが、malformed candidate detection / error quality は追加検証が必要。
- `new doc` command surface は `doc_type`, scope, `--title`, optional `--slug` のまま。
  - User confirmed body/template option は追加しない。
- `templates/discussions/` には `adr.md`, `disc.md`, `interview.md`, `research.md`, `scratch.md` がある。
  - `pr-repair-batch.md` template はまだ provider template catalog にはない。
- Skill-local `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` は `種別: disc` / `ID: "<DISC_ID>"` で作られている。
  - New doc type として使うなら provider discussion template へ移植または複製し、placeholder を `PR_REPAIR_BATCH_ID` / `PR_REPAIR_BATCH_TITLE` などに寄せる必要がある。
- `tests/cli_runtime/test_new.py` は new doc accepted types、stdout id/path、help text、unknown doc type を検証している。
- `tests/cli_runtime/test_runtime_new_doc_s09.py` は application-level create_discussion_doc behavior、parallel suffix allocation、duplicate guards を検証している。
- `tests/cli_runtime/test_validate.py` は valid / malformed / duplicate discussion filenames を検証している。
- `tests/unit/infra/test_init_update.py` は installed scaffold asset set と discussion templates/docs/skills を検証している。

## inference / 推測
- `pr-repair-batch` を追加する最小実装は doc type catalog / regex / template / docs / tests の更新で成立する。
- Hyphenated doc type を安全に扱うには、doc type alternation を source-of-truth 化するか、少なくとも create_node.py と validation.py の list/regex drift を防ぐ regression が必要。
- Malformed detection は valid fullmatch の後段なので valid file を壊す可能性は低いが、invalid hyphenated-type-like candidates の fail-closed behavior をテストで固定するべき。
- Skill-local PR repair batch template は canonical discussion template へ寄せるのが自然。ただし skill-specific operational sections が多いため、provider template と skill template の duplicate ownership を避ける設計が必要。

## unverified / 未検証事項
- Provider install/update tests が discussion templates を exact set で固定しているか、または required set だけを検証しているかは未精査。
- `sync` / presentation layer が doc type list を別に持つかは、今回検索範囲では明確な別 source は見つかっていない。
- `pr-repair-batch` に対して legacy sequential filename を grandfather する必要があるか。
  - 推定では不要。新規 doc type なので timestamp-onlyでよい。

## question candidates / 質問候補
- source-grounded に解けず、人間判断が必要な候補:
  - なし。
- pressure-test question として切り出すべき候補:
  - なし。`pr-repair-batch` literal と Option A は user-approved。
- 質問せずに解決できた候補:
  - Repair unit doc type は今回追加しない。Existing repair unit can remain `disc` unless a later user request adds `pr-repair-unit`.

## terminology conflicts / 用語衝突
- `doc type`:
  - Existing catalog is mostly generic (`disc`, `research`) plus draft canonical types.
  - `pr-repair-batch` is workflow-specific and hyphenated, so docs must explain why it exists and how it differs from `disc`.
- `batch`:
  - In `github-pr-merge-preparer`, batch is source-of-truth triage artifact for PR observation results and repair queue.
  - It is not the same as repair unit; unit remains child `disc` unless future scope changes.

## edge cases / 具体シナリオ
- Edge case:
  - `new doc pr-repair-batch --issue 188 --title "PR Repair Batch"` creates `20260617tHHMMSSz-pr-repair-batch-pr-repair-batch.md`.
  - Expected `doc_id`: `20260617tHHMMSSz-pr-repair-batch`.
  - The returned path is authoritative, and skill updates that file body.
- Edge case:
  - Existing same-second `adr` or `disc` exists under the same `discussions/`; creating `pr-repair-batch` should participate in the same timestamp family collision handling.
- Edge case:
  - Malformed candidate such as `20260617t000000z-pr-repair-batch.md` should fail because slug is missing.
- Edge case:
  - Malformed candidate such as `pr-repair-batch-manual.md` should fail as manual doc-type-prefixed filename intent.

## implications / 判断への含意
- Requirement:
  - `pr-repair-batch` is a first-class creatable discussion doc type.
  - It uses the existing `new doc` interface shape and runtime-owned filename/path generation.
  - It does not imply `--template-file` / `--body-file` additions.
  - It does not imply a `pr-repair-unit` doc type.
- Design:
  - Add doc type catalog entries consistently across create and validation layers.
  - Add discussion template under provider scaffold source.
  - Consider helper/shared constants to prevent create/validate regex drift.
  - Update shipped PR merge preparer skill to call `new doc pr-repair-batch ...` and then edit returned path.
- Plan:
  - Tests must cover new doc creation, stdout id/path, template rendering, help/allowed types, malformed detection, validation, shipped asset template inclusion, and manual filename guidance removal.

## リスク/制約
- Hyphenated doc type makes string split assumptions more fragile.
- Skill-local template and provider discussion template can drift if both remain authoritative.
- `pr-repair-batch` is workflow-specific; acceptance criteria must state its scope narrowly to avoid catalog sprawl.

## 反映先
- reflected_to:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
