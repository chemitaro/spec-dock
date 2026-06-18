---
種別: research
ID: "20260618t145427z-research"
タイトル: "Node Level Dependency Projection Failure Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00207"]
関連: ["iss-00207", "epic-00059", "deps-issues", "deps-raw"]
authority: "synthesized"
derived_from:
  - "deep-consultant: overall dependency contract analysis"
  - "deep-consultant: logic/readiness analysis"
  - "deep-consultant: projection/rendering analysis"
  - "parent-agent: taikyohiyou_project reproduction inspection"
reflected_to: []
---

# 20260618t145427z-research Node Level Dependency Projection Failure Analysis

## 位置づけ
- この artifact は `iss-00207` の調査 evidence であり、canonical `requirement.md` / `design.md` / `plan.md` への採用前の分析記録である。
- 調査は parent agent の再現確認に加え、3 つの read-only deep-consultant へ分担した。
  - 全体俯瞰: docs / runtime contract / user expectation の不一致を分析。
  - ロジック: node-level dependency から readiness / active gate へ至る flow を分析。
  - レンダリング: `deps-issues.json` / `deps-issues.puml` / `deps-raw.puml` の projection と PlantUML 表示を分析。
- 結論は採用候補であり、正式な要件・設計判断はこの後の canonical authoring で固定する。

## 調査目的 (必須)
- `taikyohiyou_project` で node-level dependency を導入した際に、`deps-issues` の表示 issue が少なすぎる原因を特定する。
- `deps-raw` で blocked / ready の色が期待と異なる原因が、ロジック、projection、PlantUML rendering のどこにあるかを切り分ける。
- 修正 issue で扱うべき contract 変更、実装 touchpoint、回帰テスト観点を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`
- 検証手順:
  - `/Users/iwasawayuuta/workspace/product/taikyohiyou_project` の実データを read-only で確認した。
  - `git diff` で node-level dependency の未コミット変更を確認した。
  - `spec-dock/.agent/deps-issues.json` と `spec-dock/deps-issues.puml` を確認した。
  - `spec-dock/deps-raw.puml` を確認した。
  - `./spec-dock/scripts/spec-dock deps check --id iss-01933 --no-github --json` を確認した。
  - `./spec-dock/scripts/spec-dock deps check --id iss-01935 --no-github --json` を確認した。
  - `gh issue view 1933`, `1935`, `1934` で live GitHub state を read-only 確認した。
- 実験条件:
  - 対象 repo の `sync` 書き込みは行っていない。
  - 対象 repo の observed `.agent` artifacts は `2026-06-18T23:26:59+09:00` 生成のもの。
  - deep-consultant は全員 read-only 条件で実行し、ファイル編集・git 操作・GitHub 変更を禁止した。

## facts / 観測できた事実 (必須)
- `taikyohiyou_project` では次の node-level dependency が `.meta.json.depends_on` に追加されていた。
  - `iss-01933` depends on `epic-01929`, `epic-01930`
  - `iss-01935` depends on `epic-01934`
  - `epic-01931` depends on `epic-01937`, `epic-01929`
  - `epic-01934` depends on `epic-01929`, `epic-01930`
- `epic-01929` は child issue 5 件すべて done で、GitHub issue `#1929` は `CLOSED`。
- `epic-01937` は child issue 6 件すべて done で、GitHub issue `#1937` は `CLOSED`。
- `epic-01930`, `epic-01931`, `epic-01934` は GitHub issue として `OPEN` だが、SpecDock 上の child issue は 0 件。
- `deps check --id iss-01933 --no-github --json` は `ready: true`, `effective_depends_on: []`, `blockers: []`, `warnings: ["deps_ref_expanded_to_empty"]` を返した。
- `deps check --id iss-01935 --no-github --json` も `ready: true`, `effective_depends_on: []`, `blockers: []`, `warnings: ["deps_ref_expanded_to_empty"]` を返した。
- `spec-dock/.agent/deps-issues.json` は `projection: "open-issues-dependency-view"` で、nodes は `iss-01933` と `iss-01935` の 2 件のみ、edges は空だった。
- `spec-dock/deps-issues.puml` は `iss-01933` と `iss-01935` を ready green として表示し、edge は表示していなかった。
- `spec-dock/deps-raw.puml` は raw direct edge 自体を表示していた。
  - `epic-01929 -> iss-01933`
  - `epic-01930 -> iss-01933`
  - `epic-01929 -> epic-01931`
  - `epic-01937 -> epic-01931`
  - `epic-01929 -> epic-01934`
  - `epic-01930 -> epic-01934`
  - `epic-01934 -> iss-01935`
- `deps-raw.puml` は initiative / epic を PlantUML `package` として出し、state color を issue `rectangle` にのみ適用している。
- provider-side docs は `deps-raw.puml` を raw direct dependency の確認用 artifact とし、readiness / blocker 判定 authority は compiled issue-level result と `deps-issues.*` 側にあると説明している。
- provider-side docs は empty initiative / epic dependency を raw validation が通れば保存可能とし、issue-level expansion が空なら warning `deps_ref_expanded_to_empty` を出すことがあると説明している。
- `infra/deps_reader.py` の `_issue_ids_for_dep_node()` は issue なら自身、epic なら child issue、initiative なら descendant issue に展開する。
- `infra/deps_reader.py` の `load_issue_depends_on_map()` は dependency target の issue 展開が空なら warning を追加し、compiled issue edge は追加しない。
- `domain/deps.py` の readiness flow は issue ID の集合を中心に動く。
  - `build_effective_deps_map()` は issue IDs のみを扱う。
  - `_derive_issue_depends_on_view()` は done issue blocker を closure から除外する。
  - `_build_evaluation()` は issue blocker が無い場合に ready と判定する。
- `presentation/json_state.py` の `render_deps_issues_artifact()` は `render_index_artifact(result)` の todo JSON を parse し、`index.json` 由来の issue nodes から `deps-issues.json` を組み立てている。
- 既存テストは `deps-issues` の nodes が todo issue set と一致することを固定している。
- 既存テストは empty initiative / epic dependency で `deps_ref_expanded_to_empty` warning が出て `index["deps"]["issue_edges"] == []` になることを固定している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 現象は単純な renderer bug ではなく、node-level direct dependency を issue-level expansion shortcut として扱う現行 contract と、ユーザーが期待する first-class node blocker モデルの不一致である。
  - `deps-issues` の表示 issue が少ない直接原因は、payload が `index.json` の todo projection から再構成され、done prerequisite と high-level dependency context を入力段階で落としていることである。
  - blocked のはずの issue が green になる直接原因は、empty open epic / initiative dependency が warning-only で compiled issue blocker を生成せず、readiness evaluation に影響しないことである。
  - `deps-raw` の色問題は、raw payload が high-level node state を持たず、renderer も package に state color を付けないことが主因である。
  - 修正は既存実装の小さな描画修正だけでは足りず、readiness contract と dependency projection contract の更新を含む。
- 推測の根拠:
  - `epic-01930` / `epic-01934` は GitHub 上 open かつ child issue 0 件だが、dependent issue は `ready=true` になっている。
  - `load_issue_depends_on_map()` は empty expansion を edge ではなく warning に変換している。
  - `DepsTopologyLoadResult` は warning code 以外に source / target / status / reason を返さないため、domain 層が node-level blocker として扱えない。
  - `deps-issues` は `index.json` の todo issue set に従うため、done prerequisite や open empty epic を graph context として表示できない。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - node-level blocker を `DepsEvaluation.blockers` に混ぜるか、`node_blockers` / `issue_blockers` として分離するか。
  - `deps-issues.json` を schema v2 に上げるか、schema v1 を維持して互換 field を追加するか。
  - empty local epic / initiative の status をどう扱うか。
  - done / closed の high-level node を raw/debug projection にどこまで表示するか。
  - `deps-issues.puml` に done prerequisite edge を `blocks` ではなく `satisfied` と表示するか。
  - `deps-raw.puml` の high-level package state を descendant aggregate で出すか、direct participant の node status で出すか。
  - implementation を 1 issue で完了できるか、logic contract と rendering contract を分割するべきか。
- 確認できない理由:
  - これらは既存 docs / tests と user expectation の間の contract decision であり、実装事実だけでは一意に決まらない。
  - 本 artifact は調査 evidence であり、canonical requirement / design をまだ authoring していない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - node-level direct dependency target が empty open epic / initiative の場合、その high-level node 自体を readiness blocker として扱う方針でよいか。
  - `deps-issues` は今後も "open issues only" の lightweight view として維持し、別 artifact を追加するべきか。それとも `deps-issues` 自体を "issue readiness with node blocker context" に拡張するべきか。
  - done prerequisite を `deps-issues` に debug context として表示するべきか。
  - high-level node state の色は raw view だけに出すか、deps-issues view にも package context として出すか。
- pressure-test question として切り出すべき候補:
  - 空の open epic に依存している issue が active set できる現状を許容する運用はあるか。
  - child issue をまだ分解していない epic を "blocker" として使うユースケースは、SpecDock の planning workflow 上 first-class に扱うべきか。
  - `deps_ref_expanded_to_empty` を warning として残しつつ blocked にする場合、CLI 利用者に矛盾して見えない説明は何か。
- 質問せずに解決できた候補:
  - `deps-issues` の node 数が少ない原因は `index.json` todo projection 由来で説明できた。
  - `deps-raw` に raw edge が出ているため、raw dependency reader 自体は今回の主因ではない。
  - ready green になる主因は GitHub cache stale ではなく、empty expansion warning-only contract である。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "node-level dependency"
  - "issue-level dependency view"
  - "deps-issues"
  - "deps-raw"
  - "ready / blocked"
  - "`deps_ref_expanded_to_empty` warning"
- 既存 docs / code / tests / discussions での使われ方:
  - docs は raw node-level dependency を保存可能としつつ、downstream consumer 向けには issue-level `DepsTopologyLoadResult` へ compile すると説明している。
  - docs は `deps-raw.puml` を raw direct dependency 確認用、`deps-issues.*` を readiness / blocker authority として説明している。
  - code は `deps-issues` を todo issue-only projection として作る。
  - tests は `deps-issues` nodes が todo issue set と一致することを期待している。
  - user expectation は initiative / epic / issue dependency を node-level direct blocker として扱う方向にある。
- 判断が必要な理由:
  - 現行 docs / tests に従えば今回の一部挙動は仕様通りだが、new node-level dependency feature の UX と active gate としては危険な ready 判定になる。
  - 修正には `reference_deps.md`, `reference_sync.md`, JSON/Puml payload contract, tests の更新が必要になる可能性が高い。

## edge cases / 具体シナリオ (必須)
- edge case: issue depends on empty open epic
  - 現状: warning のみ、ready=true。
  - 望ましい候補: `ready=false`, blocker に `epic-*` を含める。
  - 影響: `deps check`, `active set`, `sync`, `deps-issues.json`, CLI text の contract 更新が必要。
- edge case: issue depends on empty closed epic
  - 現状: warning のみ、ready=true。
  - 望ましい候補: ready=true だが raw/debug view には satisfied high-level dependency として残す。
  - 影響: high-level node status 解決と projection visibility の分離が必要。
- edge case: issue depends on non-empty epic with open child issue
  - 現状: child issue blocker として compile される。
  - 望ましい候補: 現行動作を維持する。
  - 影響: node blocker 追加で既存 issue-level blocker behavior を壊さないテストが必要。
- edge case: issue depends on non-empty epic with all child issues done
  - 現状: ready=true になり得る。
  - 望ましい候補: ready=true は維持しつつ、debug graph では done prerequisite context を表示できるようにする。
  - 影響: `effective_depends_on` と visual/debug edges を分ける必要がある。
- edge case: epic depends on empty open epic
  - 現状: source epic 配下に issue がなければ compiled edge が出ず、warning-only になる。
  - 望ましい候補: source epic 自体の state / child issue の state / active gate の対象範囲を定義する。
  - 影響: high-level target readiness と issue target readiness の両方で contract が必要。
- edge case: initiative / epic package color in raw view
  - 現状: package は白背景で、state color は issue rectangle のみ。
  - 望ましい候補: raw payload に high-level node state / state_source を追加し、package を色付けする。
  - 影響: `json_state.py` と `puml.py` の責務を整理し、renderer が状態を推測しないようにする。

## implications / 判断への含意 (必須)
- requirement では、node-level direct dependency が readiness blocker として first-class か、issue expansion shortcut に過ぎないかを明示する必要がある。
- design では、`issue_depends_on_map` だけではなく、empty expansion / node-level blocker を保持する side channel または新しい topology model が必要になる可能性が高い。
- design では、readiness authority と debug/visualization projection を分ける必要がある。
- design では、`deps-issues.json` を `index.json` 派生から切り離し、`SyncStateResult` の dependency state から直接構築する方向が有力である。
- design では、`deps-raw.puml` の renderer が state を推測せず、payload の high-level state を消費する形が望ましい。
- plan では、既存 tests の contract update を正面から扱う必要がある。
- docs では、`reference_deps.md` の "issue-level edge へ還元" の説明と、empty expansion warning の意味を更新する必要がある。

## リスク/制約 (任意)
- 既存 tests は現行 contract を明示的に固定しているため、単に実装を変えると regression として失敗する。
- `DepsEvaluation.blockers` に issue ID 以外を混ぜると、既存 consumer が issue-only 前提なら破壊的になる。
- high-level node status は GitHub-linked node と local-only node で authority が異なる。unknown/local open の扱いを曖昧にすると active gate が過剰に塞がる可能性がある。
- `deps-issues.puml` に done prerequisite を表示する場合、edge label を `blocks` のままにすると ready 判定と視覚表現が矛盾する。
- `deps-raw.puml` は docs 上 "readiness authority ではない" とされているため、色付けを強める場合は authority ではなく derived visual state と明記する必要がある。

## 反映先 (任意)
- reflected_to:
  - future `iss-00207/requirement.md`
  - future `iss-00207/design.md`
  - future `iss-00207/plan.md`
  - future provider-side `reference_deps.md`
  - future provider-side `reference_sync.md`

## 参考（References） (任意)
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
- `tests/cli_runtime/test_sync.py`
- `tests/cli_runtime/test_deps.py`
- `tests/unit/presentation/test_runtime_sync_s07.py`
