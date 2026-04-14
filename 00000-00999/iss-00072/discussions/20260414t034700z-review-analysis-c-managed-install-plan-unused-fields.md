# Review Analysis C: `_ManagedSkillInstallPlan` の未使用 field

- Source PR: `https://github.com/chemitaro/spec-dock/pull/73`
- Review source: Copilot inline comment on `src/spec_dock/cli.py`
- Analyst mode: main analysis + consultant second opinion

## Finding

`_ManagedSkillInstallPlan` が `managed_skill_names` と `native_shim_specs` を保持しているが、apply path では `current_file_mappings` と `obsolete_exact_rel_paths` しか実質利用されていないため、plan shape と consumer がずれている、という指摘。

## Evidence

- `src/spec_dock/cli.py` では `_ManagedSkillInstallPlan` が 4 field を持つ
- 同 file の参照検索では:
  - `managed_skill_names` は field 定義と builder 内の local usage が中心
  - `native_shim_specs` も field 定義と builder 生成が中心
- apply path では current file mappings と obsolete exact paths が主要入力になっている

## Assessment

- Validity: `一部妥当`
- Response priority: `推奨`
- Why:
  - unused field が cognitive load と drift risk を持つのはその通り
  - ただし private implementation detail であり、即時の user-facing bug ではない

## Options

### Option 1: 現状維持

- Pros:
  - 追加変更不要
- Cons:
  - 読み手が plan の責務を誤解しやすい
  - 将来的な drift risk が残る

### Option 2: field は残しつつコメントで役割を明文化する

- Pros:
  - 小変更で済む
- Cons:
  - 実質未使用という問題を先送りする

### Option 3: unused field を return type から削り、builder 内 local validation にだけ残す

- Pros:
  - plan shape が実消費者に一致する
  - cognitive load を下げられる
- Cons:
  - private tuple shape 変更に伴う周辺確認が必要

## Best Response

`Option 3` が最善。

- `managed_skill_names` と `native_shim_specs` を plan の返却値から外す
- validation や manifest consistency check に必要なら builder の local 変数としてのみ保持する
- 変更時は外部 import や test 依存がないことを確認する

## Decision

- Classification: `対応した方がよい`
- Action requirement: `recommended follow-up; not a merge blocker by itself`

## Notes

consultant 評価でも blocker ではないが、設計の読みやすさと drift 防止の観点で取り込む価値があるという結論だった。
