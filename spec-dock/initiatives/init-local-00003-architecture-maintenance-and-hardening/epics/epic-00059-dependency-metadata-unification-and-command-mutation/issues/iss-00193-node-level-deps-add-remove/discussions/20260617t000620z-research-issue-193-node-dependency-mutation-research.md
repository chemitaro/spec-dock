---
種別: research
ID: "20260617t000620z-research"
タイトル: "Issue 193 Node Dependency Mutation Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260617t000620z-research Issue 193 Node Dependency Mutation Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00193` の requirement authoring 前に、node-level dependency mutation の既存 contract、実装境界、未確定判断を source-grounded に整理する。
- 特に `deps add/remove` が initiative / epic / issue を受け付ける場合の保存単位、検証単位、既存 issue-level consumer への影響を切り分ける。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub Issue #193 body: node-level dependency mutation の問題文、期待挙動、受け入れ条件。
  - `spec-dock/active/issue/{requirement,design,plan}.md`: imported scaffold。canonical issue docs は未具体化。
  - `spec-dock/active/epic/{requirement,design,plan}.md`: dependency metadata unification / mutation の親 contract。
  - `spec-dock/active/initiative/requirement.md`: architecture maintenance / hardening の境界。
  - `spec-dock/docs/reference_deps.md`: 現行 user-facing dependency contract。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`: `deps add/remove` CLI parser/help。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`: mutation orchestration。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`: `.meta.json.depends_on` reader and issue-level compilation。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`: dependency write path。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` and `domain/validation.py`: cycle/readiness validation。
  - `tests/cli_runtime/test_deps.py`: existing CLI contract regression tests。
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で `iss-00193` active context を確認した。
  - `./spec-dock/scripts/spec-dock validate` で import 前の tree が valid であることを確認した。
  - `rg` / focused file reads で deps mutation / reader / validation / CLI tests の既存境界を確認した。
- 実験条件:
  - この worktree には `iss-00193` が未 import だったため、`./spec-dock/scripts/spec-dock import issue 193 --epic epic-00059 --title "Node Level Dependency Mutation" --slug node-level-deps-add-remove` を実行した。
  - `issue start` は import files が untracked になったため checkout safety guard で停止した。代わりに `active set --id iss-00193` で active context を設定した。

## facts / 観測できた事実 (必須)
- GitHub Issue #193 は、現行 CLI が `deps add --from epic-01930 --to epic-01929` を `unsupported_node_kind` で拒否することを問題としている。
- Issue #193 の期待挙動は、`deps add/remove` が initiative / epic / issue node id を受け付け、source node 直下 `.meta.json.depends_on` に direct dependency metadata を保存できること。
- Issue #193 の受け入れ条件には、duplicate add の no-op success、self dependency / descendant dependency / cycle reject、空 child issue set でも direct metadata を保存できること、help text / `reference_deps.md` の整合、既存 issue->issue 退行防止が含まれる。
- 親 Epic は `.meta.json` top-level `depends_on` を SoT とし、dependency mutation は command-first、current graph validation は fail-closed と固定している。
- 現行 `reference_deps.md` は reader schema example に initiative / epic / issue ref を含めつつ、mutation 対象は "existing issue node から existing issue node への direct edge のみ" と明記している。これは #193 の変更対象。
- `infra/deps_reader.py` は initiative / epic / issue node の `.meta.json.depends_on` をすでに読み、source node 配下 issue ids と dependency node 配下 issue ids の cross-product として issue-level dependency map へ compile する。
- `infra/deps_reader.py` は source が descendant に依存する direct ref を拒否し、compile 後に self edge が生じる場合も error にする。
- `application/mutate_deps.py` は preflight で current graph と current issue-level deps を validate した後、`from_node.kind != "issue"` / `to_node.kind != "issue"` を `unsupported_node_kind` として拒否している。
- 現行 duplicate add / remove existence 判定は、可能なら `load_direct_dependency_resolutions` で source node direct raw refs を解決し、compiled / inherited edge ではなく direct ref に基づいている。
- `infra/fs_repo.py` の write API 名は `add_issue_dependency` / `remove_issue_dependency` だが、実体は任意 meta path の `depends_on` を更新できる単純な `.meta.json` writer である。
- 既存 CLI tests は non-issue source / target を rejected behavior として固定しているため、#193 ではこの期待値を更新する必要がある。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 実装の最小経路は、reader の大改修ではなく mutation path の kind guard、direct-edge existence 判定、candidate validation、help/docs/tests の更新になる。
  - `deps add/remove` の保存先は "from node 直下 `.meta.json.depends_on`" のまま維持できる。これは issue / epic / initiative で共通化できる。
  - issue-level consumer surface は維持し、node-level direct graph は mutation validation と raw/deps future view のために補助的に扱うのが自然である。
  - 空 epic / empty initiative に対する direct metadata 保存を許すには、issue-level compiled graph だけでは validation の十分条件にならない。raw node-level graph の self / descendant / cycle validation が必要になる可能性が高い。
  - source issue -> own parent epic、source epic -> descendant issue などは direct descendant / compiled self-edge のどちらかで reject するべきで、保存してから `sync/check` で壊れる形にはしない方が親 Epic の fail-closed 境界に合う。
- 推測の根拠:
  - reader は already node-aware だが mutation use case だけが issue-only gate を持つ。
  - Issue #193 は "対象 node 配下に issue がまだ存在しない場合も direct dependency metadata は保存できる" と明記している。
  - 親 Epic は mutation 前 current graph validation / no partial write / command-first を固定している。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 既存 unit tests のどこへ node-level raw graph validation を置くのが最小か。
  - `delete_node.py` の dependency scrub が initiative / epic direct refs をどこまで自然に扱えるか。
  - `sync` artifacts が node-level direct edge を含む場合の display / warning expectations。
- 確認できない理由:
  - この research は requirement clarification phase であり、まだ設計/実装調査の全量を完了していない。
  - user-intent blocker を先に解消しないと、validation scope と acceptance criteria がぶれる。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Q1: node-level dependency mutation の検証正本を、raw node-level graph まで拡張するか、既存 issue-level compiled graph に限定するか。
- pressure-test question として切り出すべき候補:
  - Q1 は scope / requirement / design / test obligation を変えるため、formal interview として切り出す。
- 質問せずに解決できた候補:
  - Q: `#193` の parent epic はどこか。A: `epic-00059` が該当する。
  - Q: reader は initiative / epic dependency を読めるか。A: `deps_reader.py` が既に node-level refs を issue-level map へ compile している。
  - Q: 現行 CLI が拒否している箇所はどこか。A: `mutate_deps.py` の issue-only kind guard と CLI help/docs/tests。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "direct dependency": source node `.meta.json.depends_on` の raw direct ref と、compiled issue-level direct edge の両方に近い意味で使われている。
  - "cycle": raw node-level graph の cycle と、compiled issue-level graph の cycle が同一とは限らない。
- 既存 docs / code / tests / discussions での使われ方:
  - `reference_deps.md` は raw schema に initiative / epic ref を載せる一方、mutation contract は issue->issue direct edge と書く。
  - `mutate_deps.py` は direct edge existence を raw refs に近い形で判定するが、cycle validation は issue-level map で行う。
  - `deps_reader.py` は node-level refs を issue-level map へ compile する。
- 判断が必要な理由:
  - #193 の acceptance criteria に "cycle は拒否" とあるため、どの graph の cycle を拒否するかを要件に固定する必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Empty source epic -> dependency epic: source に issue がまだなくても raw metadata は保存する。compiled map は空または warning を伴う。
  - Epic A -> Epic B, then Epic B -> Epic A: 配下 issue が空でも raw node-level cycle として拒否するかどうかが設計判断。
  - Issue X -> parent Epic A: compiled self-edge を生むため、保存前に拒否するのが安全。
  - Epic A -> child Issue X: descendant dependency として拒否する。
  - Duplicate add where raw ref already exists as `123` and command uses `iss-00123`: direct resolution matching により unchanged と扱うべき。
  - Remove where edge only exists through inherited parent dependency: direct raw ref が source node にないため edge_not_found を維持するべき。
- その edge case が requirement / design / plan に与える影響:
  - raw node-level validation を採用する場合、domain or infra に direct node dependency validation helper と tests が必要になる。
  - issue-level compiled validation のみ採用する場合、empty parent cycles を保存できてしまい、将来 issue 追加時に graph が壊れるリスクが残る。

## implications / 判断への含意 (必須)
- Requirement では、mutation surface を "existing node id for initiative / epic / issue" へ明示的に拡張し、保存先を source node `.meta.json.depends_on` と固定する必要がある。
- Requirement では、existing issue->issue behavior の互換性を退行防止 AC として残す必要がある。
- Design では、raw node-level direct edge validation と compiled issue-level validation の責務境界を決める必要がある。
- Plan では、CLI help/docs/tests update、mutation orchestration update、writer naming or abstraction cleanup、dogfooding verification を分けるのが自然である。

## リスク/制約 (任意)
- `issue start` は未追跡 import files のため checkout guard で停止した。active context は `active set --id iss-00193` で設定済みだが、import files は untracked のまま残っている。
- `reference_deps.md` は provider-side `src/spec_dock/assets/spec_dock/docs/reference_deps.md` が正本であり、dogfooding copy は secondary verification である。

## 反映先 (任意)
- reflected_to:
  - planned: `iss-00193/requirement.md`
  - planned: `iss-00193/design.md`
  - planned: `iss-00193/plan.md`
  - planned: `iss-00193/report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- GitHub Issue #193: `deps add/remove で initiative / epic ノード依存を設定できるようにする`
- `spec-dock/docs/reference_deps.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
