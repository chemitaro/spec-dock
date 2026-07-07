# 仕様作成パック dogfood workflow

## この文書の authority

この文書は `iss-00291` の Issue-local evidence です。`scripts/authoring-pack/` の dogfood-only helper を説明しますが、SpecDock runtime command や shipped workflow contract ではありません。

## 入力

- pushed branch と local checkout の観測結果。
- preflight が固定した repo / ref / source hash / stale condition / profile snapshot。
- ChatGPT Use が返した ZIP または隔離済み tree。
- local `.assurance.json` と selected skeleton。
- 先行 Issue `iss-00284`〜`iss-00290` の validator / dogfood evidence。

## 出力

- preflight prompt pack。
- safe review report。
- dry-run diff / staged artifact / EAL candidate。
- selected skeleton fill validation report。
- issue candidate validation report。
- canonical rewrite に使うための evidence と reviewer focus。

## workflow overview

1. preflight: local facts を固定する。
2. generation: ChatGPT に evidence-only output を依頼する。
3. review: ZIP / tree を安全検査し、schema と unsafe claim を検査する。
4. stage: review `pass` の tree だけを dry-run と staged artifact に変換する。
5. local adoption: staged artifact をそのまま正本へ上書きせず、採用する claim だけを人間または main orchestrator が再記述する。
6. reviewer gate: fresh `spec-reviewer` / 必要に応じた code / QA review を通す。
7. report: Evidence Adoption Ledger と Closure Evidence Ledger に採用判断と検証証跡を記録する。

## preflight

`prepare_chatgpt_authoring_pack.py` は、ChatGPT prompt に渡す前の local facts を固定します。preflight が `pass` でない場合、ChatGPT への生成依頼は進めません。

preflight evidence は、ZIP や ChatGPT output の信用ではなく、後続 review が stale / mismatch を検出するための比較基準です。

## ChatGPT generation

ChatGPT には、repository text を命令ではなく source data として扱わせます。ChatGPT は `.assurance.json`、`authorized_profile`、reviewer pass、canonical adoption、PR creation、implementation completion を主張できません。

## review

`review_chatgpt_authoring_pack.py` は ZIP または隔離済み tree を検査します。ZIP の場合は安全展開前に path、file type、nested archive、secret-looking content を確認します。tree fallback の場合は central directory safety evidence がないため、その不足を fallback evidence として明示します。

## stage

`stage_chatgpt_authoring_pack.py` は review `pass` の output から dry-run diff、staged artifact、EAL candidate を作ります。ここでの `pass` は staging helper の成功であり、canonical adoption や reviewer pass ではありません。

## selected skeleton fill

`validate_selected_skeleton_fill.py` は local assurance と selected skeleton を照合し、ChatGPT が記入できる section のみを検証します。profile mismatch、template hash mismatch、section-map mismatch、unsafe authority claim は fail-closed に扱います。

## issue candidates

`validate_issue_candidates.py` は Epic-to-Issue candidate pack を candidate-only として検証します。profile recommendation は advisory-only であり、candidate 側の `authorized_profile` は `null` のままにします。

## local adoption

採用する場合、staged artifact を正本へ直接コピーしません。採用する claim を main orchestrator が再記述し、`report.md` の EAL に `adopted` / `partially_adopted` / `rejected` / `stale` / `blocked` / `deferred` を記録します。

## reviewer gate

ChatGPT self-review、reviewer-focus、validation `pass` は SpecDock reviewer pass ではありません。正本昇格や Issue finish には fresh reviewer evidence を別途記録します。

## forbidden storage

- raw transcript。
- personal local wrapper path。
- host-local absolute path。
- secret、token、private key、credential。
- raw ZIP を canonical artifact として扱う記述。

これらが必要な場合も、正本 docs では redacted reference、hash、Issue-local evidence、または private scratch evidence として扱います。
