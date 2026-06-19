---
種別: research
ID: "20260619t002902z-research"
タイトル: "Dependency PlantUML rendering clarification"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00209"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260619t002902z-research Dependency PlantUML rendering clarification

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `deps-issues.puml` と `deps-raw.puml` の表示改善について、ユーザー要望、既存 docs contract、現行 renderer / JSON projection の挙動を照合し、決定済み事項と人間判断が必要な gap を分ける。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - user feedback on 2026-06-19 about `deps-issues.puml` / `deps-raw.puml` visual policy.
- 検証手順:
  - Active issue docs と dependency reference docs を読んだ。
  - `deps-issues` JSON payload construction と PUML renderer を読んだ。
  - high-level satisfied dependency の既存 tests を読んだ。
- 実験条件:
  - 実装変更は未実施。Clarification-only。

## facts / 観測できた事実 (必須)
- `reference_sync.md` は `deps-issues.puml` を readiness / blocker context dependency graph、`deps-raw.puml` を raw direct dependency visual/debug artifact と定義している。
- `reference_sync.md` は `deps-issues.*` を readiness / blocker 判定の authority、`deps-raw.puml` を authority ではない visual/debug artifact と定義している。
- `reference_sync.md` の todo projection は `status==done` の issue と todo issue が 0 件の epic / initiative を除外するが、`deps-issues.json` は todo-only graph の再パースではなく readiness evaluation 由来である。
- 現行 `_build_deps_issues_v2_payload()` は未完了 issue を include し、さらに blocker / satisfied context の endpoint を include する。
- 現行 `deps-issues.puml` renderer は node type に関係なく rectangle として描画し、state `done` / `closed` を gray で描画する。
- 現行 `deps-issues.puml` renderer は satisfied edge を dashed、blocking edge を solid とし、label に `satisfied (raw_direct)` / `blocks (relation)` を出す。
- 現行 `deps-raw.puml` renderer は raw tree の initiative / epic / issue を全件描画し、initiative / epic は package、issue は rectangle として描画する。
- 現行 `deps-raw.puml` renderer は raw direct edge を `raw_direct` label で描画する。
- ユーザーは `deps-issues` について、closed/done issue、closed epic、closed initiative は表示しない方針を希望している。
- ユーザーは `deps-issues` について、`raw_direct` label は分かりにくく、blocking なら `blocks` でよいと述べている。
- ユーザーは `deps-raw` について、closed epic、done issue を表示しない方針を希望している。
- ユーザーは `deps-raw` について、epic は node rectangle ではなく package / empty package として統一したいと述べている。
- ユーザーは `deps-raw` について、metadata に記述された依存関係をそのまま描画する view なので、edge の意味を `raw_direct` に限定するのはよいと述べている。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `deps-issues.puml` は operator / agent が「次に実施可能か、何にブロックされているか」を見る readiness board であり、歴史的な satisfied dependency の可視化は副次的または不要になりつつある。
  - `deps-raw.puml` は metadata debug view なので、readiness-specific wording である `blocks` より、raw edge identity を明示する方が混乱が少ない。
  - closed/done endpoint を両 view から単純に削除すると、「依存は satisfied だから ready」という説明 edge が消える。その代わり、ready state 自体と node_blocker 不在を authority とする設計へ寄せる必要がある。
  - epic / initiative の closed 判定を GitHub status にのみ寄せるか、descendant issue state から導出するかで、表示対象の数と意味が大きく変わる。
- 推測の根拠:
  - `reference_sync.md` / `reference_deps.md` の authority 境界。
  - 現行 renderer が satisfied context を明示表示していること。
  - ユーザー feedback の「完了済みの issue および依存で溢れかえる」「open / ready / blocked だけにしたい」という意図。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - closed high-level node を除外した場合に、既存 tests の期待をどこまで変更すべきか。
  - `.agent/deps-issues.json` 自体から closed/done nodes を除外するのか、JSON は authority context を残し PUML renderer だけで隠すのか。
  - GitHub open の epic だが配下 issue が全 done の場合、visual policy 上は表示すべきか非表示にすべきか。
  - empty open epic を blocker として表示する際、空 package として残すべきか、compact node 表現へ寄せるべきか。
- 確認できない理由:
  - いずれも user-intent / product workflow の判断であり、local code だけでは決められない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - GitHub open の epic / initiative だが配下 issue が全 done または todo issue 0 件の高位 node を、dependency PlantUML に表示するか。
  - `.agent/deps-issues.json` の nodes / edges からも closed/done / satisfied-only context を落とすか、PUML renderer だけで非表示にするか。
  - `deps-issues.puml` で satisfied edge を完全に消すか、必要な場合だけ凡例・注記・薄線で残すか。
  - `deps-raw.puml` で open epic package 内の done issue を消した結果、空 package になった epic を表示するか。
- pressure-test question として切り出すべき候補:
  - GitHub open だが todo issue が 0 件の epic / initiative を「表示対象の active blocker / active scope」とみなすか、それとも「表示ノイズ」として非表示にするか。
- 質問せずに解決できた候補:
  - `deps-raw.puml` の edge label は `raw_direct` を維持する方針。ユーザー feedback で肯定されている。
  - `deps-issues.puml` では `raw_direct` label をユーザー向けに前面へ出さず、blocking は `blocks` として見せる方針。ユーザー feedback で明確。
  - closed issue / closed epic / closed initiative は原則表示しない方針。ユーザー feedback で明確。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `raw_direct`
  - `blocks`
  - `satisfied`
  - `open epic`
  - `done/closed`
- 既存 docs / code / tests / discussions での使われ方:
  - `raw_direct`: `.meta.json.depends_on` に直接保存された node-level dependency relation。
  - `blocks`: PUML 上の矢印方向に合わせた human label。prerequisite が dependent を block する意味。
  - `satisfied`: readiness 評価では満たされた依存 context。現行 PUML では dashed edge として表示。
  - `open epic`: GitHub status が open の high-level node、または descendant issue 由来で active と推定される high-level node。
  - `done/closed`: issue は done/closed を完了扱い。high-level node は GitHub status と descendant aggregation の両方が関わる。
- 判断が必要な理由:
  - 同じ high-level node が「GitHub 上は open」「配下 issue は全 done」「dependency target としては satisfied」という複数の意味を持つため、表示 policy を決めないと UX と authority がずれる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Empty open epic: まだ issue breakdown 前だが dependency target としては active blocker。表示すべき。
  - Empty closed epic: dependency target として satisfied。ユーザー方針では非表示候補。
  - Open epic with all descendant issues done: GitHub issue は open のままだが leaf work は完了。表示するかが未決。
  - Open epic with mixed children: done issue は隠し、open / ready / blocked issue と epic package は表示する。
  - Closed initiative with open child anomaly: data inconsistency に近い。基本は closed initiative を隠す方針だが validation / edge-case test の扱いが必要。
- その edge case が requirement / design / plan に与える影響:
  - high-level visual state classification、filtering predicate、PUML edge filtering、JSON authority preservation、manual test scenario を決める必要がある。

## implications / 判断への含意 (必須)
- Requirement では、`deps-issues.puml` は actionable readiness view、`deps-raw.puml` は active raw metadata view として目的を分ける必要がある。
- Design では、JSON payload filtering と PUML-only filtering を分けて判断する必要がある。`deps-issues.json` は agent-facing authority なので、表示ノイズ削減だけで情報を失わせると downstream consumer に影響する。
- Plan では、presentation layer tests に加えて sync integration tests と realistic manual fixture の更新が必要。
- ADR は現時点では不要。表示 policy は issue-local に戻せる範囲であり、storage / mutation contract の durable change ではない。

## リスク/制約 (任意)
- 完了済み context を PUML から消すと、なぜ ready なのかを図だけでは説明しにくくなる。
- JSON からも消す場合は `.agent/deps-issues.json` の existing contract と tests を更新する必要がある。
- GitHub open high-level node を表示し続けると、leaf issue が全部完了した epic が画面に残り、ユーザーが避けたいノイズが残る。
- GitHub open high-level node を隠すと、epic close を運用上強制しなくても view は片付くが、「GitHub 上はまだ open」の情報が PlantUML から消える。

## consultant analysis / 第三者分析 (任意)
- source:
  - consultant `Plato`, 2026-06-19.
- conclusion:
  - GitHub open / closed と dependency view visibility は分けるべき。
  - `deps-issues.puml` は readiness / blocker view なので、GitHub open でも配下 issue がすべて done / closed の epic は原則非表示が合理的。
  - ただし `deps-raw.puml` は `.meta.json.depends_on` の raw direct view なので、監査性を維持するために raw dependency を確認できる状態を残すべき。
- recommended model:
  - GitHub lifecycle: `github_state`
  - dependency display decision: `dependency_visibility`
  - Avoid using `open` / `closed` again for visual lifecycle.
- key distinction:
  - child issue が存在しない open epic は、issue breakdown 前の active high-level dependency target として表示可。
  - child issue が存在し、visible child が 0 件の open epic は、dependency view では effectively resolved / hidden と扱う。
- test implications:
  - empty open epic is visible.
  - open epic with open child issue is visible.
  - open epic with all child issues done is hidden in `deps-issues.puml`.
  - closed epic is hidden regardless of children.
  - initiative follows the same recursive rule.

## deep consultant analysis / readiness authority impact (任意)
- source:
  - deep-consultant `Zeno`, 2026-06-19.
- conclusion:
  - This is not only a PlantUML rendering issue. The same distinction must become part of readiness authority.
  - GitHub lifecycle state and dependency readiness interpretation should be separate axes.
  - Recommended model:
    - `lifecycle_state`: GitHub / local lifecycle fact such as `open`, `closed`, `done`, `unknown`.
    - `dependency_disposition`: readiness interpretation such as `blocking`, `satisfied`, `indeterminate`.
    - `disposition_basis`: reason such as `all_descendant_issues_done`, `empty_open_container`, `empty_unknown_container`, `lifecycle_closed`.
- current design impact:
  - `infra/deps_reader.py` can remain raw storage / topology reader. `.meta.json.depends_on` does not change.
  - `domain/deps.py` is the readiness authority and should evaluate high-level dependency context through `dependency_disposition`, not only `state in {closed, done}`.
  - `application/check_deps.py::resolve_high_level_status_context()` currently gives GitHub high-level status priority over descendant aggregation. This can make a GitHub-open all-done epic appear as `open` even though dependency readiness should be satisfied.
  - `set_active.py` and `issue start` should not duplicate logic; they should consume the updated `evaluate_readiness()` result.
- proposed dependency disposition table:
  - child issue count is zero + lifecycle open:
    - `dependency_disposition=blocking`
    - `disposition_basis=empty_open_container`
  - child issue count is zero + lifecycle unknown:
    - `dependency_disposition=indeterminate`
    - `disposition_basis=empty_unknown_container`
  - child issue count is zero + lifecycle closed/done:
    - `dependency_disposition=satisfied`
    - `disposition_basis=lifecycle_closed` or `local_done`
  - child issue count is greater than zero + all child issues done:
    - `dependency_disposition=satisfied`
    - `disposition_basis=all_descendant_issues_done`
  - child issue count is greater than zero + open child exists:
    - blocker is represented through issue-level blockers / descendant issue state, not as an empty high-level blocker.
  - child issue count is greater than zero + unknown child exists:
    - `guard_reason=unknown` or equivalent unknown dependency disposition.
- surface impact:
  - `deps check --json` should show GitHub-open all-done high-level dependency as ready / satisfied, with `node_blockers=[]`.
  - `deps-issues.json` should expose enough machine-readable context to show `lifecycle_state=open` and `dependency_disposition=satisfied` together.
  - `deps-issues.puml` should use `dependency_disposition` for blocker display / filtering, not only lifecycle state.
  - `deps-raw.puml` remains raw direct dependency visual/debug artifact. If it shows high-level state, it should avoid implying GitHub `open` means dependency-blocking.
  - `active set` / `issue start` should allow targets blocked only by GitHub-open all-done high-level dependencies, and continue rejecting empty open high-level blockers.
- scope implication:
  - The current issue requirement says dependency logic repair is out of scope. That must be amended if `dependency_disposition` is implemented here.
  - If scope remains display-only, create a follow-up issue for readiness authority and make this issue depend on it or explicitly defer logic changes.
- minimum tests:
  - domain: GitHub-open epic with all child issues done is satisfied and not a node blocker.
  - domain: empty GitHub-open epic remains blocking.
  - application `deps check`: GitHub-open all-done high-level dependency exits 0.
  - `active set` / `issue start`: all-done high-level dependency passes; empty open high-level dependency still blocks.
  - sync artifact: `deps-issues.json` can represent `lifecycle_state=open` and `dependency_disposition=satisfied` together.
  - presentation: `deps-issues.puml` does not render a `blocks` edge for all-done high-level dependencies.
  - regression: done children filtered from todo projection do not make a high-level dependency look `empty`.

## 反映先 (任意)
- reflected_to:
  - pending: `requirement.md`
  - pending: `design.md`
  - pending: `plan.md`
  - pending: `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- `spec-dock/docs/reference_sync.md`
- `spec-dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
- `tests/cli_runtime/test_sync.py`
