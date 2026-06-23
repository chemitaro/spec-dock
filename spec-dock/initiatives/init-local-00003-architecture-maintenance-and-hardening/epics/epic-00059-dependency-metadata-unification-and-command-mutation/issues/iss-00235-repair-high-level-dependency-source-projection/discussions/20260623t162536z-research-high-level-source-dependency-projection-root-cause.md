---
種別: research
ID: "20260623t162536z-research"
タイトル: "High level source dependency projection root cause"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00235"]
関連: []
authority: "synthesized"
derived_from:
  - "GitHub issue #235"
  - "manual reproduction under /private/tmp/iss-00235-repro"
  - "deep-consultant runtime/domain analysis"
  - "deep-consultant artifact/contract analysis"
  - "deep-consultant issue-scope comparison analysis"
reflected_to:
  - "report.md"
---

# 20260623t162536z-research High level source dependency projection root cause

## 調査目的 (必須)
- GitHub issue #235 で報告された「initiative / epic 自体を依存 source にした direct dependency が、保存後に `deps check` / `index-all` / dependency projection から消える」問題を再現し、根本原因を特定する。
- 既存の `iss-00207-fix-dependency-projections-for-node-level-blockers` と同一問題か、別の未カバー edge case かを切り分ける。
- 実装前に、どの layer の contract を直すべきか、どの artifact を受け入れ条件に含めるべきかを整理する。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub issue #235: `https://github.com/chemitaro/spec-dock/issues/235`
  - Active issue: `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md}`
  - Dependency reader: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - Dependency domain model: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - JSON / artifact presentation: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - Dependency reference doc: `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - Existing high-level target tests: `tests/unit/infra/test_deps_reader_topology.py`, `tests/cli_runtime/test_sync.py`, `tests/cli_runtime/test_deps.py`
- 検証手順:
  - GitHub issue #235 の再現ログを確認した。
  - `/private/tmp/iss-00235-repro` に最小構成の SpecDock consumer workspace を作成した。
  - current checkout の runtime scripts をコピーし、source initiative が target epic に direct dependency を持つ状態を作った。
  - `deps check --id init-00001 --no-github --json`、`sync --no-github`、`.agent/index-all.json`、`.agent/deps-issues.json`、`.agent/deps-raw.puml` を確認した。
  - 3 系統の deep-consultant analysis を並列に実施し、runtime/domain、artifact/contract、issue-scope comparison の観点で照合した。
- 実験条件:
  - Date: 2026-06-24 JST
  - Worktree: `/Users/iwasawayuuta/.codex/worktrees/c2a6/spec-dock`
  - Repro workspace: `/private/tmp/iss-00235-repro`
  - GitHub access: issue body read only
  - Network/GitHub live dependency state is not required for the reduced reproduction.

## facts / 観測できた事実 (必須)
- GitHub issue #235 の報告では、`deps add --from init-01926 --to epic-01937` など複数の high-level direct dependencies が `result=updated` になり、source `.meta.json` に `depends_on` として保存されている。
- 同報告では、`deps check --id init-01926 --github --json` が `ready: true`、`effective_depends_on: []`、`dependency_contexts: []` を返している。
- 同報告では、`.agent/index-all.json` の `init-01926` node に `depends_on` が出ていない。
- 同報告では、`sync --github` が `deps_ref_expanded_to_empty` warning を出している。
- 手動再現でも、source initiative `init-00001` の `.meta.json` に `"depends_on": ["epic-00002"]` が保存された。
- 手動再現で `deps check --id init-00001 --no-github --json` は次を返した。
  - `ready: true`
  - `effective_depends_on: []`
  - `blockers: []`
  - `dependency_contexts: []`
  - `warnings: []`
- 手動再現で `sync --no-github` 後の `.agent/index-all.json` は `init-00001` node に raw `depends_on` を含めなかった。
- 手動再現で `.agent/deps-issues.json` は `nodes: {}`、`edges: []`、`dependency_contexts: []` だった。
- 手動再現で `.agent/deps-raw.puml` は `Nepic_00002 --> Ninit_00001 : raw_direct` を出力した。
- `deps_reader.load_node_dependency_resolutions()` は all nodes の raw `.meta.json.depends_on` を読む。
- `deps_reader.load_issue_depends_on_map()` は `raw_node_depends_on[src_id] = direct_dep_node_ids` を保存するが、`src_issue_ids = _issue_ids_for_dep_node(...)` が空の場合に `continue` する。
- `_issue_ids_for_dep_node()` は source node が `issue` なら `[id]`、source node が `epic` / `initiative` なら descendant issue ids を返す。
- そのため、descendant issue を持たない initiative / epic 自体が source の direct dependency は、raw map には残るが issue dependency projection と dependency contexts には入らない。
- `domain/deps.py` の `_issue_ids_for_target()` も high-level target を descendant issue ids に変換する。target issue ids が空の場合、readiness evaluation は issue-level の blocker を見つけられない。
- `presentation/json_state.py` の `_node_payload()` は issue node には `depends_on` / blockers を載せるが、high-level node には raw `depends_on` を載せない。
- `presentation/json_state.py` の deps issues payload は `deps_eval_by_id` / dependency contexts 由来で、実質 issue source を前提にしている。
- 既存 tests は主に「issue source が high-level target に依存する」ケースを守っており、「initiative / epic 自体が source の direct dependency」は十分に覆っていない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 根本原因は `.meta.json` storage や `deps add` mutation ではなく、raw node dependency と issue-level readiness dependency を同一 projection に畳み込む途中で、high-level source の direct dependency が落ちること。
  - 特に「source high-level node に descendant issue が存在しない」ケースでは、source issue ids が空になるため、dependency context が生成されず、`deps check` が見る model から dependency が消える。
  - `.agent/index-all.json` は complete raw audit surface として期待されているが、現在の high-level node payload は raw `depends_on` を保持しないため、issue #235 の観測と一致する。
  - `.agent/deps-raw.puml` は少なくとも reduced reproduction では raw edge を出せる。ただし issue #235 では satisfied direct high-level edges が欠落したと報告されており、「complete raw audit」なのか「active/debug visual」なのか contract が曖昧。
  - `iss-00207` は issue source -> high-level target の blocker projection を扱うが、#235 は high-level source direct dependency を扱うため、同一原因の別表面ではなく、未カバー source-axis edge case と見るべき。
- 推測の根拠:
  - `deps_reader.py` の issue projection は high-level source を descendant issue ids に展開する設計で、empty expansion 時に raw edge を dependency context へ変換しない。
  - `domain/deps.py` の readiness model も issue ids を中心にしており、node-keyed direct dependency result を持たない。
  - 手動再現で source `.meta.json` には raw edge が存在する一方、`deps check` / `index-all` / `deps-issues` からは消えた。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - GitHub issue #235 の product repo `chemitaro/taikyohiyou_project` の live workspace で、報告時と同じ graph が現在も残っているか。
  - `.agent/deps-raw.puml` が issue #235 の報告環境で satisfied high-level direct edges を omit した直接原因。
  - high-level source に descendant issue が存在する場合、direct high-level dependency を各 descendant issue に展開する現行挙動を維持するか、source node 自体の direct dependency として別扱いするか。
  - `index-all` に raw node edges を追加する場合、node payload に入れるか、top-level `deps.raw_node_edges` として入れるか。
- 確認できない理由:
  - この research scope は原因特定までで、product repo の live state mutation や implementation は行っていない。
  - raw visual artifact の complete/active contract は既存 docs と実装の意図が完全には一致しておらず、design decision が必要。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `deps-raw.puml` を complete raw audit artifact として保証するか、それとも visual/debug artifact として扱い、complete audit は JSON に新設するか。
  - high-level source direct dependency を readiness にどう反映するか。source node 自体の readiness result に direct blocker として載せるか、descendant issue への inherited dependency として展開するか、両方を別 field で表現するか。
- pressure-test question として切り出すべき候補:
  - source node に descendant issue がない場合でも `deps check --id <initiative|epic>` は direct dependency を `effective_depends_on` / `node_blockers` / `dependency_contexts` に表示すべきか。
  - source node に descendant issue がある場合、direct dependency は parent node の direct blocker と descendant issue の inherited blocker のどちらとして表示すべきか。
- 質問せずに解決できた候補:
  - `deps add` mutation が保存に失敗している可能性は低い。手動再現と issue #235 の両方で `.meta.json.depends_on` は更新済み。
  - GitHub live status が原因で dependency が消えている可能性は低い。`--no-github` reduced reproduction でも同じ projection loss が起きた。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `raw dependency`
  - `effective_depends_on`
  - `node_blockers`
  - `deps-raw`
  - `index-all`
- 既存 docs / code / tests / discussions での使われ方:
  - `reference_deps.md` は raw storage を `.meta.json.depends_on` と説明し、complete raw metadata audit として `.meta.json.depends_on` + `.agent/index-all.json` を示している。
  - 実装上の `raw_node_depends_on_map` は raw edge を保持するが、artifact projection では high-level node payload に raw dependency が出ない。
  - `deps-raw.puml` は名前から complete raw view を連想させるが、現状は graph visual/debug surface としての性質が強く、issue #235 では complete audit 期待と衝突している。
  - `effective_depends_on` は issue-level readiness 用の projection として実装されており、high-level source direct dependency の raw audit とは別概念。
- 判断が必要な理由:
  - Fix が readiness semantics、artifact contract、docs wording のどこまでを変更するかで、後方互換性と test expectations が変わる。
  - raw audit surface を `index-all` に置くか新規 JSON に置くかで downstream consumer の contract が変わる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Empty high-level source: initiative / epic 自体が direct dependency を持ち、descendant issue がない。
  - Non-empty high-level source: initiative / epic 自体が direct dependency を持ち、descendant issue がある。
  - High-level source -> issue target.
  - High-level source -> epic target with no descendant issues.
  - High-level source -> epic target with descendant issues.
  - High-level source -> initiative target with mixed descendant state.
  - Issue source -> high-level target, existing `iss-00207` scope.
  - Satisfied/done/closed target dependencies that should remain visible in complete raw audit but may not be active blockers.
- その edge case が requirement / design / plan に与える影響:
  - Source axis と target axis を分けた test matrix が必要。
  - Readiness projection と raw audit projection を同じ field に押し込まない design が必要。
  - Empty expansion は silent success ではなく、raw edge visibility と warning/readiness semantics のどちらかを明示する必要がある。

## implications / 判断への含意 (必須)
- Requirement には「high-level node 自体の direct dependency が `.meta.json` に保存されている場合、descendant issue の有無に関係なく inspectable であること」を含める必要がある。
- Design には raw node dependency result と issue-level readiness result を分離する構造を含める必要がある。
- Implementation では fake issue を生成して辻褄を合わせるのではなく、node-keyed direct dependency context/result を first-class に扱うのが安全。
- `deps check --id <initiative|epic>` は issue projection だけでなく、target node 自体の direct dependencies を返す path が必要。
- `index-all` には complete raw dependency audit 用の field が必要。候補は high-level node payload の `depends_on`、または top-level `deps.raw_node_edges`。
- `deps-issues.json` は issue dependency graph として維持し、raw node graph を混ぜない方が contract が明確。
- `deps-raw.puml` の保証範囲は明文化する。complete raw audit を保証するなら tests を追加し、そうでないなら complete audit JSON を別途持つ。
- `iss-00207` の既存 fix/test と衝突しないように、「issue source -> high-level target」と「high-level source -> any target」を別 slice として扱う。

## リスク/制約 (任意)
- Existing tests may encode the current assumption that an `epic -> epic` raw dependency is not part of issue readiness map. That assumption itselfは維持しつつ、node-level direct dependency visibility を別 surface に足す必要がある。
- High-level source direct dependency を descendant issues に自動展開すると、parent node の direct dependency と inherited issue dependency が二重表示になる恐れがある。
- `index-all` schema を変更する場合、downstream scripts が unknown field tolerant か確認する必要がある。

## 反映先 (任意)
- reflected_to:
  - `report.md` Evidence Adoption Ledger
  - future `requirement.md`
  - future `design.md`
  - future `plan.md`

## manual reproduction / 手動再現

### Setup

```bash
mkdir -p /private/tmp/iss-00235-repro/spec-dock
cp -R src/spec_dock/assets/spec_dock/scripts /private/tmp/iss-00235-repro/spec-dock/scripts
git init /private/tmp/iss-00235-repro
```

The reduced graph contained:

- `init-00001`: source initiative, no descendant issues, `.meta.json.depends_on = ["epic-00002"]`
- `init-00002`: target initiative
- `epic-00002`: target epic

Minimal required docs were added under those nodes so `validate` could pass.

### Observed commands

```bash
env PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin ./spec-dock/scripts/spec-dock deps check --id init-00001 --no-github --json
```

Observed key output:

```json
{
  "target": "init-00001",
  "ready": true,
  "effective_depends_on": [],
  "blockers": [],
  "issue_blockers": [],
  "node_blockers": [],
  "satisfied_dependencies": [],
  "dependency_contexts": [],
  "nodes": {},
  "warnings": []
}
```

```bash
env PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin ./spec-dock/scripts/spec-dock validate
env PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin ./spec-dock/scripts/spec-dock sync --no-github
```

Observed:

- `validate`: `spec-dock: ok (validate) nodes=3`
- `sync --no-github`: wrote derived artifacts successfully.
- `.agent/index-all.json`: `nodes["init-00001"]` had type/title/path/github/progress only; no raw `depends_on`.
- `.agent/deps-issues.json`: `nodes: {}`, `edges: []`, `dependency_contexts: []`.
- `.agent/deps-raw.puml`: contained `Nepic_00002 --> Ninit_00001 : raw_direct`.

### Manual reproduction conclusion

The dependency is saved and can be present in the raw visual graph, but it is absent from the issue-level readiness projection and from `index-all` node payload. This reproduces the core failure without GitHub live state.

## deep-consultant synthesis / 並列深掘り統合

### Runtime / domain analysis

- `load_issue_depends_on_map()` preserves raw edge in `raw_node_depends_on_map`, but dependency context generation is keyed by source issue id.
- If the source node is initiative / epic and has no descendant issues, `_issue_ids_for_dep_node()` returns `[]`, so the loop continues before producing contexts.
- `domain/deps.py` evaluates readiness over issue ids; high-level target/source direct node state is not first-class in the readiness result.
- Recommended direction: keep issue projection separate and add node-level direct dependency context/result. Do not synthesize fake issues.

### Artifact / contract analysis

- The storage layer is not the primary failure: `.meta.json.depends_on` retains the edge.
- The contract gap is between raw metadata storage and generated/inspection artifacts.
- `index-all` is documented/expected as part of complete raw audit, but does not preserve high-level node raw dependency.
- `deps-raw.puml` needs a clearer contract. If it is a complete raw audit, test it as such. If it is visual/debug, provide a machine-readable complete raw audit elsewhere.

### Issue-scope comparison analysis

- #235 is not a duplicate of `iss-00207`.
- `iss-00207` covers issue source -> high-level target.
- #235 covers high-level source itself -> target, especially empty high-level source.
- Missing test axes include source node type, target node type, source descendant presence, GitHub/no-GitHub status, `index-all` raw audit, and `deps-raw` completeness.

## root cause / 根本原因

High-level node direct dependencies are stored as raw node metadata, but the primary dependency evaluation path projects dependencies into an issue-keyed model. When the source is an initiative or epic, the runtime expands the source to descendant issue ids. If that expansion is empty, the raw edge is kept only in `raw_node_depends_on_map` and is not converted into dependency contexts, readiness blockers, or `index-all` node payload. As a result, `deps check --id <initiative|epic>` can report `ready: true` with empty dependencies even though the source node's `.meta.json.depends_on` contains direct dependencies.

The short failure chain is:

1. `deps add` writes raw direct dependency to source `.meta.json`.
2. `load_node_dependency_resolutions()` reads the raw dependency.
3. `load_issue_depends_on_map()` records the raw source entry but tries to project source node to descendant issue ids.
4. For empty high-level source, `src_issue_ids == []`, so dependency context generation is skipped.
5. `evaluate_readiness()` and `inspect_target_deps()` see only issue-keyed projection and find no blockers.
6. `index-all` node payload does not expose high-level raw `depends_on`, so artifact consumers cannot audit the saved edge there.

## not root causes / 根本原因ではないもの

- `deps add` mutation failure: not supported by evidence; `.meta.json.depends_on` is updated.
- GitHub live status: not required to reproduce; `--no-github` reproduction shows the loss.
- Validation rejecting high-level dependencies: not supported; `validate` passed in the reduced workspace after minimal docs were present.
- Single missing warning only: warning quality is part of the symptom, but the core issue is projection/model loss.

## recommended fix direction / 修正方針

1. Introduce or expose node-keyed raw direct dependency information as a first-class result separate from issue-keyed readiness edges.
2. Update `deps check --id <initiative|epic>` to include the target node's own direct dependencies even when descendant issue expansion is empty.
3. Add complete raw dependency audit to `index-all`, preferably as a top-level raw edge list such as `deps.raw_node_edges` to avoid overloading issue node fields.
4. Keep `deps-issues.json` as issue graph output; do not mix raw node edges into issue graph without explicit schema.
5. Decide and document whether `deps-raw.puml` is complete raw audit or visual/debug. Add tests matching the chosen contract.
6. Add regression tests for:
   - initiative source with no issues -> epic target.
   - epic source with no issues -> issue target.
   - high-level source with descendant issues -> high-level target.
   - `deps check --id <high-level>` JSON fields.
   - `index-all` raw dependency audit.
   - no-GitHub and GitHub-stub status paths.

## 参考（References） (任意)
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `load_node_dependency_resolutions`
  - `_issue_ids_for_dep_node`
  - `load_issue_depends_on_map`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `_issue_ids_for_target`
  - `build_effective_deps_map`
  - `evaluate_readiness`
  - `inspect_target_deps`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `_node_payload`
  - `_build_deps_issues_v2_payload`
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- `tests/unit/infra/test_deps_reader_topology.py`
- `tests/cli_runtime/test_sync.py`
- `tests/cli_runtime/test_deps.py`
