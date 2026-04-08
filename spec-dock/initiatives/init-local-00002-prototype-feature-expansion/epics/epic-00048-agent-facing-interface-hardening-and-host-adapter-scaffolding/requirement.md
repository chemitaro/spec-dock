---
種別: 要件定義書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-06"
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00002` の feature expansion として、agent が `spec-dock` を安定して扱える interface を提供する。
  - メイン orchestrator が毎回手作業で文脈解釈しなくても、host adapter 経由で同じ判断導線を再利用できるようにする。
- この epic が提供する能力:
  - 機械可読な active/context 参照契約の明文化。
  - host-neutral protocol と host-specific adapter の責務分離。
  - Codex/Copilot で再利用可能な薄い adapter scaffold の提供。
- 位置づけ:
  - 既存 accepted scope は `iss-00049` / `iss-00050` で完了済みの `protocol + thin adapter skill + host adapter metadata` までを含む。
  - host-native custom agent / subagent deployment は、上記完了済み範囲を削除・差し替えせず、その上に積む follow-up extension として扱う。
  - follow-up extension は 2 issue へ分割せず、native shim の実装・installer sync/prune・dogfooding/manual validation・確認評価までを 1 issue の中で閉じる前提に更新する。

## 問題定義
- 現状は `active.json`、`index.json`、`deps-issues.json`、`index-all.json`、`context-pack.md` の役割が docs 上で部分的にしか定義されておらず、agent の実行判断が実装者依存になりやすい。
- current/future の実行判断に必要な projection と、full-history を含む監査・履歴・全体検索用データの境界が曖昧で、agent が通常実行でも過剰に広い state を読みに行きやすい。
- host ごとの prompt や手順に依存して workflow が分岐し、同じ `spec-dock` 運用でも結果が揺れる。
- `context-pack.md` だけでは機械処理に必要な情報が不足し、最終的に人間向け docs を追加解釈する必要がある。
- `.agents/skills/*` による thin adapter skill は導入できているが、Codex の `.codex/agents/*.toml` や GitHub Copilot の `.github/agents/*.agent.md` といった host-native artifact は未配備であり、プロジェクト配下に subagent/custom agent を置いて orchestrator が委譲する運用までは follow-up として残っている。

## 既存 accepted scope と follow-up extension の扱い
- accepted scope（done として保持するもの）:
  - `iss-00049` で fixed point 化した protocol contract / runtime alignment / provider-doc / dogfooding-doc / tests の整合。
  - `iss-00050` で完了済みの `.agents/skills/*` と `.agents/host-adapters/meta.json` の thin adapter scaffold / installer managed deployment / parity / final review。
- follow-up extension（今回の追補で追加するもの）:
  - `.codex/agents/*.toml` と `.github/agents/*.agent.md` の host-native custom agent / subagent artifact。
  - native shim の source-of-truth、installer sync/prune、dogfooding parity、manual validation。
  - extension の完了判定は、実装と確認評価を別 issue に分けず同じ 1 issue の evidence で閉じる。
- interpretation rule:
  - 上記 extension は、既存 accepted scope の未完了扱いではなく、完了済み scope を維持したまま追加する。
  - 根拠は `discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md` を正本とする。

## ユースケース
- happy path:
  - メイン orchestrator が spec-dock 専門 sub-agent に委任し、sub-agent が `active.json` を入口に `index.json` / `deps-issues.json` を既定の working set として使って対象と手順を決定する。
  - full-history が必要な監査・履歴参照・全体検索・escalation の場合のみ `index-all.json` を追加で読む。
  - Codex/Copilot のどちらでも同じ protocol に従い、`sync` / `validate` / docs 読み順が一致する。
  - follow-up extension では `spec-dock init/update` 後に host-native custom agent/subagent artifact が配置され、orchestrator はその native agent を entrypoint にして spec-dock 操作を委譲できる。
- exception / operation scenario:
  - active が未設定の場合は `active-none` placeholder を明示的に検知し、編集対象外として停止する。
  - host adapter 側に state 再実装が無いことを review で検証し、drift を抑制する。
  - follow-up extension でも unknown custom skill / unknown custom native agent は installer prune の対象にせず、managed 生成物だけを更新する。

## Epic requirements
- E-RQ-001:
  - agent-facing protocol と human-facing summary の責務を分離し、`active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の役割を明文化すること。
  - agent の通常実行では full-history を第一選択にせず、`active.json` を入口、`index.json` と `deps-issues.json` を current/future projection として既定読取対象にすること。
  - `index-all.json` は full-history を含む監査・履歴・全体検索・escalation 用途として定義し、通常実行の第一選択ではないことを明記すること。
- E-RQ-002:
  - host adapter は runtime state の再実装を持たず、core protocol 参照のみで動作する薄い構成にすること。
- E-RQ-003:
  - installer (`init/update`) で Codex/Copilot 向け adapter scaffold を管理可能な形で配布・更新できること。
  - 既存 accepted scope では `.agents/skills/*` と `.agents/host-adapters/meta.json` を managed asset として維持すること。
- E-RQ-004:
  - docs と runtime contract の整合を保ち、provider / dogfooding 双方で同じ guidance を提供すること。
- E-RQ-005:
  - accepted baseline の issue 分割は過細分化を避け、`iss-00049` / `iss-00050` の 2 issue で完了可能なサイズに保つこと。
  - 上記 baseline 2 issue は `iss-00049` / `iss-00050` として done のまま保持すること。
  - 上記 baseline 2 issue rule は accepted baseline の closure にのみ適用し、follow-up extension は `E-RQ-005-ext` に従って単一 issue で閉じることと矛盾しないこと。

## Extension addendum requirements
- E-RQ-002-ext:
  - host-native extension では `.agents/skills/*` を adapter guidance の正本とし、`.codex/agents/*.toml` / `.github/agents/*.agent.md` はそこへ委譲する thin shim にすること。
  - host-native shim は runtime state の再実装も protocol state read も持たず、host-native discovery と `.agents/skills/*` またはその委譲先 subagent への delegation のみを担うこと。
- E-RQ-003-ext:
  - follow-up extension では `.codex/agents/*.toml` / `.github/agents/*.agent.md` を managed deployment 対象として追加できること。
  - installer sync/prune は `.agents/skills/*` と `.agents/host-adapters/meta.json` の baseline managed asset を壊さずに追加されること。
  - native shim の managed ownership/source-of-truth/obsolete path 判定は `.agents/host-adapters/meta.json` を単一 manifest file として固定し、`targets.codex.native_shim` / `targets.copilot.native_shim` 配下の `managed`, `owner`, `target_file`, `source_of_truth_asset`, `delegates_to`, `obsolete_managed_paths` の exact field で表現すること。
  - sync は `target_file` と `source_of_truth_asset`、tests の委譲期待値は `delegates_to`、prune は `obsolete_managed_paths` を正本にして判定し、field 名の再解釈を許さないこと。
  - managed native shim の canonical target filename は `.codex/agents/spec-dock.toml` と `.github/agents/spec-dock.agent.md` に固定し、gate-2 sync/prune verification もこの exact path を生成・更新対象として扱うこと。
  - gate-2 で prune 対象にする obsolete managed native shim fixture は `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` に固定すること。
  - gate-2 で保持対象にする unknown custom native shim fixture は `/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` に固定すること。
  - gate-2 canonical command sequence は `uvx --from . spec-dock init /tmp/spec-dock-native-shim-smoke` -> fixture 配置 -> `uvx --from . spec-dock update /tmp/spec-dock-native-shim-smoke` とする。
  - fixture 配置は `mkdir -p /tmp/spec-dock-native-shim-smoke/.codex/agents /tmp/spec-dock-native-shim-smoke/.github/agents`、obsolete managed fixture 2 件の配置、unknown custom fixture 2 件の配置を指す。
- E-RQ-004-ext:
  - host-native artifact の配置、ownership、source-of-truth、prune policy、validation 方針を docs と tests で一貫させること。
  - dogfooding parity と manual validation evidence を同じ extension closure の中で残すこと。
  - follow-up 1 issue の gate-2 sync/prune verification は再現可能な手順として plan/report に固定し、temp repo 初期化方法、managed 扱いの旧 native file の配置方法、unknown custom file の配置方法、before/after で確認する対象パス、成功条件を明記すること。
  - `gate_2_sync_prune_evidence` は自由記述 `observed` を置かず、`managed_codex_shim_generated_or_updated`, `managed_copilot_shim_generated_or_updated`, `obsolete_managed_fixture_pruned`, `unknown_custom_fixture_preserved`, `baseline_skill_and_metadata_untouched` を固定キーとして持ち、各キーは `expected`, `observed`, `pass` を必須にすること。
  - `gate_2_sync_prune_pass` は `managed_codex_shim_generated_or_updated.pass=true`、`managed_copilot_shim_generated_or_updated.pass=true`、`obsolete_managed_fixture_pruned.pass=true`、`unknown_custom_fixture_preserved.pass=true`、`baseline_skill_and_metadata_untouched.pass=true` の 5 件が全て `true` の場合のみ `true` とすること。
  - follow-up 1 issue の gate-3 manual validation は Codex/Copilot それぞれの合格条件を明記し、片方 host をローカル実機で確認できない場合に必要な代替証跡を requirement/plan/report で追跡できること。
  - `gate_3_manual_validation` と `extension_closure_pass` の required host set は `codex` と `copilot` の両方固定とし、`fallback_evidence_*` は各 host の required evidence を代替できても required host set 自体は減らさないこと。
  - gate-3 manual validation の canonical action は host ごとに固定し、Codex は `.codex/agents/spec-dock.toml`、Copilot は `.github/agents/spec-dock.agent.md` を discovery したうえで、同じ task 文面 `Summarize the active spec-dock target and the next workflow doc to read before editing.` を実行すること。
  - gate-3 host selection signal の accepted evidence format は `transcript_fragment` / `ui_screenshot` / `cli_log` の 3 種のみとする。
  - report には host ごとに `selection_evidence_format`, `selection_signal_expected_any`, `selection_signal_observed`, `selection_signal_pass` を固定キーで記録する。
  - `selection_signal_expected_any` の canonical serialization は JSON 互換の配列リテラル 1 形式に固定し、Codex は `["spec-dock.toml", ".codex/agents/spec-dock.toml"]`、Copilot は `["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]` とする。
  - `selection_signal_pass` は `selection_signal_observed` に host ごとの `selection_signal_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とし、`ui_screenshot` でも OCR または手入力転記した文字列に同じ rule を適用する。
  - report には host ごとに `response_target_expected`, `response_target_observed`, `response_target_pass`, `next_doc_expected_any`, `next_doc_observed`, `next_doc_pass` を固定キーで記録する。
  - `response_target_expected` は host 共通で `active target summary or active-none stop` とする。
  - `response_target_pass` は `response_target_observed` が active target 要約または `active-none` 停止を示す場合のみ `true` とする。
  - `next_doc_expected_any` の canonical serialization は JSON 互換の配列リテラル 1 形式に固定し、host 共通で `["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]` とする。
  - `next_doc_pass` は `next_doc_observed` に `next_doc_expected_any` 配列のいずれか 1 要素が exact match で含まれる場合のみ `true` とし、`ui_screenshot` でも OCR または手入力転記した文字列に同じ rule を適用する。
  - report には host ごとに `delegation_evidence_expected`, `delegation_evidence_observed`, `delegation_evidence_pass` を固定キーで記録する。
  - Codex の `delegation_evidence_expected` は `.agents/skills/spec-dock-codex-adapter/SKILL.md`、Copilot の `delegation_evidence_expected` は `.agents/skills/spec-dock-copilot-adapter/SKILL.md` とする。
  - `delegation_evidence_pass` は `delegation_evidence_observed` に host ごとの `delegation_evidence_expected` が exact match で含まれ、かつ shim artifact または transcript から skill への委譲成立が読める場合のみ `true` とする。
  - report には host ごとに `non_reimplementation_evidence_expected`, `non_reimplementation_evidence_observed`, `non_reimplementation_evidence_pass` を固定キーで記録する。
  - `non_reimplementation_evidence_expected` は host 共通で `no state payload key redefinition and no inline .agent/*.json/context-pack.md` とする。
  - `non_reimplementation_evidence_pass` は `non_reimplementation_evidence_observed` が host 対象 shim に対する `rg -n "schema_version|projection|nodes|issues|deps|source|updated_at"` の no-match と `.agent/*.json` / `context-pack.md` 非 inline を同時に示す場合のみ `true` とする。
  - report には host ごとに `direct_protocol_read_expected`, `direct_protocol_read_observed`, `direct_protocol_read_pass` を固定キーで記録する。
  - `direct_protocol_read_expected` は host 共通で `no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body` とする。
  - `direct_protocol_read_pass` は `direct_protocol_read_observed` が host 対象 shim に対する `rg -n "active\\.json|index\\.json|deps-issues\\.json|index-all\\.json|read[ -]order"` の no-match を示す場合のみ `true` とする。
  - report には host ごとに `fallback_evidence_required`, `fallback_evidence_observed`, `fallback_evidence_pass` を固定キーで記録する。
  - `fallback_evidence_required` は host ごとのローカル実機確認が不能な場合のみ `true`、実機確認できた場合は `false` とする。
  - `fallback_evidence_pass` は `fallback_evidence_required=false` の場合は direct host verification が成立しているときのみ `true`、`fallback_evidence_required=true` の場合は `fallback_evidence_observed` に artifact snapshot、delegation static check、non-reimplementation static check、dated transcript / ui screenshot / cli log のいずれか 1 つが同居するときのみ `true` とする。
  - gate-3 の pass/fail は host ごとに、固定キー化した host selection signal、`.agents/skills/spec-dock-codex-adapter/SKILL.md` または `.agents/skills/spec-dock-copilot-adapter/SKILL.md` への委譲成立を示す content check、runtime state 非再実装を示す evidence、direct protocol read 不在を示す evidence、実機確認不能時の代替証跡の 5 観点で判定できること。
  - gate-3 の static check observed は host-scoped とし、Codex は `.codex/agents/spec-dock.toml` のみ、Copilot は `.github/agents/spec-dock.agent.md` のみを対象にした別コマンド/別記録から採取し、片方 host の match/no-match を他方の判定へ流用しないこと。
  - `gate_4_review_evidence` は `additive_only_scope_preserved_expected`, `additive_only_scope_preserved_observed`, `additive_only_scope_preserved_pass`, `single_follow_up_issue_rule_expected`, `single_follow_up_issue_rule_observed`, `single_follow_up_issue_rule_pass`, `native_manifest_shape_expected`, `native_manifest_shape_observed`, `native_manifest_shape_pass`, `report_schema_compliance_expected`, `report_schema_compliance_observed`, `report_schema_compliance_pass`, `discussion_schema_compliance_expected`, `discussion_schema_compliance_observed`, `discussion_schema_compliance_pass`, `host_native_scope_consistency_expected`, `host_native_scope_consistency_observed`, `host_native_scope_consistency_pass`, `final_review_ref` を固定キーとして持つこと。
  - `host_native_scope_consistency_pass` は required host set=`codex,copilot` の両 host で `delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true` がそろった場合のみ `true` とすること。
  - `gate_4_review_pass` は `additive_only_scope_preserved_pass=true`、`single_follow_up_issue_rule_pass=true`、`native_manifest_shape_pass=true`、`report_schema_compliance_pass=true`、`discussion_schema_compliance_pass=true`、`host_native_scope_consistency_pass=true` の 6 件が全て `true` の場合のみ `true` とすること。
- E-RQ-005-ext:
  - host-native deployment は既存 2 issue を reopen せず、follow-up 1 issue の extension で閉じること。
  - 上記 follow-up 1 issue は native shim の実装、installer sync/prune、dogfooding/manual validation、確認評価までを同じ周回で完結させること。
  - extension の closure は baseline の `iss-00049` / `iss-00050` close record と分離して扱うこと。
  - extension report の固定トップレベル項目は `baseline_inherited_closure` と `extension_closure` の 2 つに固定すること。
  - `baseline_inherited_closure` には `accepted_issues`, `baseline_inherited_closure_pass` を必須キーとして置き、`accepted_issues` は `iss-00049,iss-00050` 固定、`baseline_inherited_closure_pass` は両 issue が done のまま reopen されず、extension 側の gate 証跡を混在させていない場合のみ `true` とすること。
  - `extension_closure` には単一 follow-up issue identity を `follow_up_issue_id`, `follow_up_issue_ref`, `follow_up_issue_discussion_ref`, `follow_up_issue_status` の固定キーで保持すること。
  - `follow_up_issue_ref` は actual issue artifact/URL 用の reserved field とし、issue 未作成時は placeholder を入れてもよいが discussion を指さないこと。
  - `follow_up_issue_discussion_ref` は actual discussion artifact/URL 用の reserved field とし、issue 検討根拠の discussion を保持する分離 field とすること。
  - `extension_closure` には `follow_up_issue_id`, `follow_up_issue_ref`, `follow_up_issue_discussion_ref`, `follow_up_issue_status`, `gate_2_sync_prune_pass`, `gate_3_manual_validation`, `gate_4_review_pass`, `extension_closure_pass` を必須キーとして置くこと。
  - `gate_3_manual_validation` には `codex` と `copilot` を固定キーとして置き、host 別の `selection_*`, `response_target_*`, `next_doc_*`, `delegation_*`, `non_reimplementation_*`, `direct_protocol_read_*`, `fallback_*` を配下に記録すること。
  - `extension_closure_pass` は `gate_2_sync_prune_pass=true`、required host set=`codex,copilot` の両 host で `selection_signal_pass=true`、`response_target_pass=true`、`next_doc_pass=true`、`delegation_evidence_pass=true`、`non_reimplementation_evidence_pass=true`、`direct_protocol_read_pass=true`、`fallback_evidence_pass=true`、および `gate_4_review_pass=true` を同時に満たす場合のみ `true` とすること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - active issue が設定済みである。
  - When:
    - agent が protocol に従って文脈取得を行う。
  - Then:
    - 入口は `active.json`、通常実行の working set は `index.json` と `deps-issues.json`、補助説明は `context-pack.md` として一貫し、`index-all.json` は必要時のみ参照される。
  - 観測点:
    - docs 記述、JSON shape、実行手順例の一致。
- E-AC-002:
  - Given:
    - Codex/Copilot 両方の adapter が生成済みである。
  - When:
    - 同一 task を各 adapter 経由で起動する。
  - Then:
    - 参照 state と推奨コマンド導線が一致し、host 固有差分は entrypoint 文面に限定される。
  - 観測点:
    - 生成ファイル差分、adapter 設計、レビュー結果。
- E-AC-003:
  - Given:
    - 新規 install/update を実行する。
  - When:
    - managed assets を同期する。
  - Then:
    - adapter scaffold が配布・更新され、既存 managed skill の運用を壊さない。
  - 観測点:
    - installer tests、assets 配布結果、破壊的差分の不在。
- E-AC-004:
  - Given:
    - epic 実装後に docs parity を確認する。
  - When:
    - provider/dogfooding docs を比較する。
  - Then:
    - protocol と adapter guidance に矛盾が無い。
  - 観測点:
    - parity check 記録、final spec review。

## Extension addendum acceptance criteria
- E-AC-002-ext:
  - Given:
    - `.codex/agents/*.toml` と `.github/agents/*.agent.md` の native shim が生成済みである。
  - When:
    - native agent / subagent 経由で同一 task を起動する。
  - Then:
    - state 参照と推奨コマンド導線が `.agents/skills/*` の guidance から逸脱しない。
  - 観測点:
    - native shim 内容、委譲先、manual validation 記録、レビュー結果。
- E-AC-003-ext:
  - Given:
    - host-native extension を含む install/update を実行する。
  - When:
    - managed assets の sync/prune を確認する。
  - Then:
    - native artifact sync/prune が追加されても、unknown custom native agent / custom skill を壊さない。
  - 観測点:
    - installer tests、temp repo での sync/prune 証跡、managed/unmanaged 境界の記録。
    - temp repo 初期化コマンド、managed 旧 native file / unknown custom file の配置先、before/after で確認した対象パス、成功条件。
    - exact pass 条件は `/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock.agent.md` が update 後に存在し、`/tmp/spec-dock-native-shim-smoke/.codex/agents/spec-dock-codex-adapter.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/spec-dock-copilot-adapter.agent.md` が prune され、`/tmp/spec-dock-native-shim-smoke/.codex/agents/custom-reviewer.toml` と `/tmp/spec-dock-native-shim-smoke/.github/agents/custom-reviewer.agent.md` が残ること。
    - report では `gate_2_sync_prune_evidence.managed_codex_shim_generated_or_updated`, `managed_copilot_shim_generated_or_updated`, `obsolete_managed_fixture_pruned`, `unknown_custom_fixture_preserved`, `baseline_skill_and_metadata_untouched` を fixed key として持ち、各キーを `expected`, `observed`, `pass` で記録すること。
- E-AC-004-ext:
  - Given:
    - extension 実装後に provider/dogfooding/manual validation を確認する。
  - When:
    - native artifact の ownership / source-of-truth / manual validation evidence を照合する。
  - Then:
    - generated native artifact の evidence が provider/dogfooding parity 記録と矛盾しない。
    - Codex/Copilot の各 host で thin shim discovery と `.agents/skills/*` への委譲が確認できるか、またはローカル実機確認不能な host について定義済みの代替証跡がそろう。
  - 観測点:
    - docs refresh、dogfooding parity 記録、manual validation evidence、final spec review。
    - host 別合格条件、代替証跡の有無、closure 判定。
    - Codex は report 上で `selection_evidence_format` が accepted evidence format 3 種のいずれか、`selection_signal_expected_any` が `["spec-dock.toml", ".codex/agents/spec-dock.toml"]`、`selection_signal_pass=true`、`response_target_expected=active target summary or active-none stop`、`response_target_pass=true`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`、`next_doc_pass=true` を満たし、`.agents/skills/spec-dock-codex-adapter/SKILL.md` への委譲成立を示す内容証跡と runtime state 非再実装 evidence があること。
    - Codex は report 上で `direct_protocol_read_expected=no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body` と `direct_protocol_read_pass=true` を満たすこと。
    - Copilot は report 上で `selection_evidence_format` が accepted evidence format 3 種のいずれか、`selection_signal_expected_any` が `["spec-dock.agent.md", ".github/agents/spec-dock.agent.md"]`、`selection_signal_pass=true`、`response_target_expected=active target summary or active-none stop`、`response_target_pass=true`、`next_doc_expected_any=["spec-dock/active/issue/requirement.md", "spec-dock/active/epic/requirement.md", "spec-dock/active/initiative/requirement.md", "spec-dock/system/active-none/requirement.md"]`、`next_doc_pass=true` を満たし、`.agents/skills/spec-dock-copilot-adapter/SKILL.md` への委譲成立を示す内容証跡と runtime state 非再実装 evidence があること。
    - Copilot は report 上で `direct_protocol_read_expected=no direct active.json/index.json/deps-issues.json/index-all.json/read-order text in shim body` と `direct_protocol_read_pass=true` を満たすこと。
    - 実機確認不能な host は、artifact snapshot、delegation path の static content check、runtime state 非再実装の static evidence、別環境の dated transcript / ui screenshot / cli log のいずれか 1 つから作った `selection_signal_observed` が 1 組そろっている場合のみ代替 pass とみなす。
    - Codex/Copilot ともに `response_target_expected`, `response_target_observed`, `response_target_pass`, `next_doc_expected_any`, `next_doc_observed`, `next_doc_pass`, `delegation_evidence_expected`, `delegation_evidence_observed`, `delegation_evidence_pass`, `non_reimplementation_evidence_expected`, `non_reimplementation_evidence_observed`, `non_reimplementation_evidence_pass`, `direct_protocol_read_expected`, `direct_protocol_read_observed`, `direct_protocol_read_pass`, `fallback_evidence_required`, `fallback_evidence_observed`, `fallback_evidence_pass` が report 上で欠けず、各 pass 条件に一致すること。
    - final review では report のトップレベル項目が `baseline_inherited_closure` と `extension_closure` に固定され、baseline inherited closure と extension closure が一意に分離されていること。

## スコープ
- MUST:
  - protocol の責務分離を docs と設計で固定する。
  - agent の既定読取を current/future projection に寄せ、full-history を通常実行の第一選択にしないことを固定する。
  - host adapter scaffold を Codex/Copilot 向けに提供する。
  - `iss-00049` / `iss-00050` の accepted scope を 2 issue の done として維持しつつ、host-native extension は追加の 1 issue で閉じる計画を定義する。
  - `iss-00049` / `iss-00050` 完了済みの accepted scope は done のまま保持する。
  - host-native custom agent/subagent artifact は follow-up extension として Codex/Copilot 向け managed deployment できるようにする。
  - host-native follow-up extension は 1 issue の中で native shim 実装から確認評価まで閉じる。
- MUST NOT:
  - host adapter に独自の状態解釈ロジックを持たせない。
  - メイン orchestrator 直操作を前提に複雑化した運用を推奨しない。
  - host-native artifact に独自の状態解釈ロジックを持たせない。
  - 完了済み `iss-00049` / `iss-00050` を native artifact 未実装の理由で未完了へ読み替えない。
- OUT OF SCOPE:
  - invalid artifact prevention の architecture-level 実装（別 initiative で follow-up）
  - multi-host（Codex/Copilot 以外）展開
  - runtime の大規模リファクタ
  - host ごとの高度な orchestration policy 最適化

## 境界
- Always:
  - protocol は host-neutral である。
  - adapter は薄い binding に留める。
  - follow-up extension でも `.agents/skills/*` が spec-dock 操作 guidance の正本である。
- Ask:
  - host 固有差分が protocol に侵食していないか。
  - docs 記述が state contract と一致しているか。
  - native artifact が shim の範囲を越えていないか。
- Never:
  - `context-pack.md` を唯一正本として扱う。
  - `index-all.json` を通常実行の第一読取対象として固定しない。
  - adapter 側で `index-all.json` 相当を再生成する。
  - native artifact を state owner にしない。

## 非機能要件
- performance:
  - adapter 追加で `sync` / `validate` の体感を悪化させない。
  - follow-up extension で native artifact を追加しても体感を悪化させない。
- reliability / consistency:
  - host 間で同一入力に対する参照導線を一致させる。
- security:
  - adapter は既存の安全境界（read-only placeholder / command contract）を弱めない。
  - follow-up extension の native artifact も既存の安全境界を弱めない。
- operations:
  - install/update で managed asset として追跡可能である。
  - unknown custom file を破壊しない prune policy を持つ。

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/codex_skills/`
  - `.agents/host-adapters/meta.json`
  - `tests/test_init_update.py`
- extension impact:
  - `.codex/agents/*.toml`
  - `.github/agents/*.agent.md`
- external dependency:
  - Codex/Copilot 側の skill 読み込み規約（`.agents/skills` 利用）
  - follow-up extension では Codex 側の subagent 仕様（`.codex/agents/*.toml`）と GitHub Copilot 側の custom agent 仕様（`.github/agents/*.agent.md`）。
- compatibility:
  - 既存 `spec-dock` managed skill 配布と両立すること。
  - 既存完了済み `iss-00049` / `iss-00050` の成果を壊さず、follow-up で拡張すること。

## 決定事項
- D-001:
  - host adapter metadata は `.agents/host-adapters/meta.json` を採用済みとする。
  - runtime state 正本（`.agent`）と adapter 管理情報（`.agents`）は分離したまま運用する。
- D-002:
  - `.agents/skills/*` を adapter guidance の正本とする。
  - `.codex/agents/*.toml` / `.github/agents/*.agent.md` は host-native discovery のための thin shim とする。
