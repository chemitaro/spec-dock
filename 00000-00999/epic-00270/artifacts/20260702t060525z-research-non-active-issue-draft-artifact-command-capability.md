---
種別: research
ID: "20260702t060525z-research"
タイトル: "非 active / 未 start Issue に対する draft artifact 作成コマンド能力分析"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "iss-00271"
  - "iss-00272"
  - "iss-00273"
  - "iss-00274"
  - "iss-00275"
  - "iss-00276"
authority: "synthesized"
derived_from:
  - "deep-consultant:019f2166-c5f5-7ee3-b518-dec4601c9494"
  - "local-command:./spec-dock/scripts/spec-dock new artifact --help"
  - "local-command:./spec-dock/scripts/spec-dock assurance show --issue iss-00271"
  - "local-command:./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00271 --dry-run"
  - "local-command:./spec-dock/scripts/spec-dock new artifact draft-design --issue iss-00271"
  - "local-command:./spec-dock/scripts/spec-dock new artifact draft-plan --issue iss-00271"
reflected_to: []
---

# 非 active / 未 start Issue に対する draft artifact 作成コマンド能力分析

## 調査目的

前段の研究で、Epic Planning は downstream Issue の canonical `design.md` / `plan.md` へ Issue Start 前の本文を置かず、Issue-local `draft-design` / `draft-plan` artifact を作る方針が妥当と判断した。

この研究では、その方針を現行 SpecDock command/runtime で実際に運用できるかを確認する。特に、Issue が active ではなく、`issue start` も実行していない状態で、特定 Issue に対して要件ドラフト、設計ドラフト、実装計画ドラフト、grade / `authorized_profile` に応じた draft を作れるかを切り分ける。

## sources / 調査方法

参照先:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`
- `spec-dock/docs/rules/issue/artifacts.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/templates/issue/design.md`
- `spec-dock/templates/issue/plan.md`
- `spec-dock/templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md`

検証手順:

- `./spec-dock/scripts/spec-dock active show` で active Issue がないことを確認した。
- `find .../issues -maxdepth 2 -name '.assurance.json' -o -name '.meta.json'` で `iss-00271` から `iss-00276` に `.meta.json` はあるが `.assurance.json` がないことを確認した。
- `./spec-dock/scripts/spec-dock new artifact --help` で artifact type と scope option を確認した。
- `./spec-dock/scripts/spec-dock assurance show --issue iss-00271` で、非 active Issue を explicit target にできるが contract は missing であることを確認した。
- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00271 --dry-run` で、非 active Issue に対する dry-run profile 判定が可能であることを確認した。
- `./spec-dock/scripts/spec-dock new artifact draft-design --issue iss-00271 ...` と `draft-plan` を実行し、`.assurance.json` がない場合に fail-closed することを確認した。
- Deep consultant `019f2166-c5f5-7ee3-b518-dec4601c9494` に read-only の実装分析を依頼し、結果を照合した。

実験条件:

- 実際の non-dry-run `assurance classify` は実行していない。`.assurance.json` を作成すると現在の不整合を固定する可能性があるため、dry-run に留めた。
- `new artifact draft-design` / `draft-plan` は fail-closed を確認するため実行したが、いずれも exit code 1 で draft artifact は作成されなかった。
- 現 `iss-00271` の canonical `design.md` / `plan.md` には、Issue Start 前に一括作成したドラフト本文が入っている。この状態で `.assurance.json` を作ると、その本文の hash が source binding に含まれる。

## facts / 観測できた事実

- `new artifact` は artifact type として `draft-requirement` / `draft-design` / `draft-plan` を持つ。`commands/new.py` の `_artifact_types` は `draft-requirement`、`draft-design`、`draft-plan` を列挙している。
- `new artifact` は `--initiative` / `--epic` / `--issue` の mutually exclusive scope を受け付ける。active Issue であることは CLI 引数上の条件ではない。
- `create_artifact_doc.py` は graph から `scope_node_id` を解決する。`--issue iss-00271` のような explicit scope は active Issue を必要としない。
- `draft-*` artifact は Issue scope でのみ許可される。Issue 以外の scope で `draft-design` / `draft-plan` を作ることはできない。
- `draft-requirement` は `spec-dock/templates/issue/requirement.md` を source として render する。assurance contract は不要である。
- `draft-design` / `draft-plan` は専用 `templates/artifacts/draft-design.md` / `draft-plan.md` を持たない。代わりに、verified `.assurance.json` の `authorized_profile` に対応する `templates/issue-profiles/<profile>/design.md` / `plan.md` を source として render する。
- `draft-design` / `draft-plan` は、対象 Issue に valid かつ stale でない `.assurance.json` がない場合、no-write fail-closed する。
- `assurance show --issue iss-00271` は non-active Issue を explicit target として解決できたが、結果は `has_contract: false` / `reason: missing_assurance_contract` だった。表示上 `authorized_profile: strict` が出るが、これは strict-legacy fallback 表示であり、valid contract の `authorized_profile` ではない。
- `assurance classify --stage requirement --issue iss-00271 --dry-run` は non-active Issue に対して `authorized_profile: standard` を返した。ただし dry-run なので `.assurance.json` は書かない。
- 現行 `assurance classify` CLI には `--profile`、`--grade`、`--risk-fact` のような user-facing option がない。
- 現行 `build_assurance_contract` は risk facts 未指定時に `default_risk_facts()` を使う。その結果、今回の dry-run では `standard` が返った。
- `assurance_store.build_requirement_source_binding()` は名前に反して `requirement.md` だけでなく `requirement.md` / `design.md` / `plan.md` の 3 ファイルを source binding に含める。
- したがって、`.assurance.json` 作成後に canonical `design.md` / `plan.md` を placeholder へ戻すと、source binding hash が変わり contract は stale になる。
- `assurance compose --artifact all --issue iss-00271 --dry-run` は `.assurance.json` がないため `missing_assurance_contract` で失敗した。

## direct answer / 直接回答

現在の SpecDock command/runtime では、**部分的に可能**である。

可能なこと:

- 非 active / 未 `issue start` Issue に対して、`--issue <id>` で Issue-local artifact を作成できる。
- `blank` / `research` / `interview` / `disc` / `decision-candidate` / `pr-repair-batch` / `adr` は、Issue が active でなくても作成できる。
- `draft-requirement` は Issue scope 限定で、assurance contract なしに作成できる。
- `assurance classify --stage requirement --issue <id>` は、Issue が active でなくても実行できる。non-dry-run なら `.assurance.json` を対象 Issue 配下に作成できる設計である。

条件付きで可能なこと:

- `draft-design` / `draft-plan` は、対象 Issue に valid かつ stale でない `.assurance.json` がある場合に限り作成できる。
- その場合、draft は `.assurance.json` の `classification.authorized_profile` に従い、profile-specific template から render される。

現在できないこと:

- `new artifact draft-design` / `draft-plan` だけで、未 classified Issue の grade/profile-aware draft を初回生成すること。
- `new artifact` で `--profile standard` / `--grade strict` のように profile を直接指定すること。
- `assurance classify` CLI で risk facts や profile override を明示指定し、Issue requirement 上の推奨 grade を deterministic に contract へ反映すること。
- canonical `design.md` / `plan.md` に入ってしまった pre-start draft 本文を、Issue-local draft artifact へ退避し、canonical placeholder に戻す migration command を使うこと。

## blank / draft / profile-aware composition の違い

`blank` や `disc` は単なる scope-local Markdown artifact であり、grade / profile とは独立している。

`draft-requirement` は Issue-only artifact だが、source は共通 Issue requirement template である。assurance contract は不要で、profile-aware ではない。

`draft-design` / `draft-plan` は Issue-only artifact であり、名前は draft だが、実装上は profile-aware render である。これは `.assurance.json` の `authorized_profile` を読み、`templates/issue-profiles/<profile>/design.md` / `plan.md` を使う。

`assurance compose --artifact design|plan|all --issue <id>` も profile-aware だが、これは canonical `design.md` / `plan.md` を合成する機能であり、Issue-local draft artifact 作成とは別である。

## inference / 推測

事実から推測したこと:

- 「active Issue でないこと」は artifact 作成の主な blocker ではない。`--issue <id>` は非 active Issue を対象にできる。
- 主 blocker は「valid `.assurance.json` がないこと」と「profile / risk facts を CLI から適切に指定できないこと」である。
- 現行 B/B+ 方針をそのまま運用すると、Epic Planning が `draft-design` / `draft-plan` を作る前に non-dry-run `assurance classify --issue <id>` を実行する必要がある。
- しかし現 `epic-00270` では canonical `design.md` / `plan.md` に misplaced draft body が入っているため、この状態で classify すると不適切な source binding を `.assurance.json` に固定してしまう。
- したがって、現 Epic の migration では「classify → draft artifact 作成」より先に、canonical `design.md` / `plan.md` を placeholder に戻すか、少なくとも `.assurance.json` を作らず `blank` / `disc` artifact に退避する必要がある。

推測の根拠:

- `create_artifact_doc.py` は `draft-design` / `draft-plan` 作成時に `assurance_store.verify_contract(target)` を呼び、valid contract がなければ RuntimeError を返す。
- `assurance_store.verify_contract()` は source binding hash を検証し、stale なら invalid 扱いにする。
- `build_requirement_source_binding()` は `requirement.md` / `design.md` / `plan.md` の 3 つを hash 対象にする。
- `assurance classify --dry-run --issue iss-00271` の JSON 出力では、source binding に `requirement.md` / `design.md` / `plan.md` の 3 つが含まれていた。

## short-term operation / epic-00270 の短期運用

現 `epic-00270` では、次の順序が最も安全である。

1. 既存の Issue shell と canonical `requirement.md` は維持する。
2. 既に canonical `design.md` / `plan.md` に入っている draft 本文を、まず authority-neutral な Issue-local `blank` または `disc` artifact へ退避する。
   - この段階では `draft-design` / `draft-plan` にこだわらない。
   - artifact には `intended_targets: ["design.md", "plan.md"]`、`profile_basis: pending`、`adoption_status: unreviewed`、`not canonical` を明記する。
3. canonical `design.md` / `plan.md` を compose placeholder に戻す。
4. その後で必要に応じて `assurance classify --stage requirement --issue <id>` を non-dry-run で実行し、`.assurance.json` を作る。
5. valid contract ができた Issue だけ、`new artifact draft-design --issue <id>` / `draft-plan` を作成する。
6. Issue Start 後、`assurance compose` と Issue Planning workflow で canonical `design.md` / `plan.md` を合成し、退避済み artifact を Evidence Adoption Ledger 経由で採用・部分採用・棄却する。

profile が `standard` で十分な Issue では、上記 4 以降に standard-profile `draft-design` / `draft-plan` を作れる。ただし `strict` / `critical` / `lite` を意図する場合、現行 CLI では profile を正しく指定できないため、`.assurance.json` の手編集を通常運用にしてはならない。代替として `blank` / `disc` artifact に intended grade/profile と pending 状態を残すのが安全である。

## long-term improvements / 長期改善案

Command/runtime:

- `assurance classify` に `--risk-fact key=value` を追加し、risk facts を CLI から明示できるようにする。
- `assurance classify` に `--profile <lite|standard|strict|critical>` を追加する場合は、manual override ではなく `profile_basis: explicit-human-or-orchestrator-decision` として report evidence を要求する。
- Issue requirement の grade 判定材料セクションを deterministic に読み、risk facts または proposed profile に変換する parser を追加する。
- `new artifact draft-design|draft-plan --issue <id> --profile <profile> --provisional` のような provisional draft mode を追加する。ただし `.assurance.json` を暗黙作成せず、front matter に `profile_basis: proposed` / `adoption_status: unreviewed` / `requires_assurance_contract: true` を入れる。
- canonical `design.md` / `plan.md` の misplaced draft body を Issue-local artifact へ退避し、placeholder を復元する migration command を追加する。

Workflow/docs:

- `workflow_epic.md` は `draft-design` / `draft-plan` が verified `.assurance.json` 必須であることを明示する。
- Epic Planning の handoff package は、`draft-design` / `draft-plan` が作れない場合の fallback artifact type を定義する。
- `handoff-ready` と `execution-ready` を明確に分離する。
- `draft-design` / `draft-plan` を作れた場合でも、それは canonical phase promotion ではなく evidence であることを report template に明記する。

Validation:

- 未 start Issue の canonical `design.md` / `plan.md` が compose placeholder のままかを検出する check を追加する。
- `draft-design` / `draft-plan` 作成時に `.assurance.json` missing / invalid / stale なら no-write fail-closed する regression test を追加する。
- `assurance classify --issue <id>` が non-active Issue を target できることと、source binding stale を検出することを test で固定する。

## unverified / 未検証事項

まだ確認していないこと:

- `assurance classify --stage requirement --issue <id>` を non-dry-run で実行した後、`draft-design` / `draft-plan` が標準 profile で実際に作成されること。
- `strict` / `critical` / `lite` を現行 runtime で安全に指定する公式 path が完全に存在しないこと。
- migration command を追加する場合、どの層に置くべきか。
- `build_requirement_source_binding()` が `design.md` / `plan.md` を含む現在の設計が意図通りか、または naming / lifecycle とずれているか。

確認できない理由:

- non-dry-run classify は `.assurance.json` を作成し、現 canonical design/plan draft body の hash を contract に固定してしまうため、この調査では実行しなかった。
- profile override / risk-fact 指定の公式 path は、今回読んだ CLI 実装上は見つからなかったが、将来の provider-side変更や未読の補助 command がある可能性は完全には排除していない。

## question candidates / 質問候補

source-grounded に解けず、人間判断が必要な候補:

- `epic-00270` では、まず neutral `blank` / `disc` artifact に draft body を退避してから、正規 `draft-design` / `draft-plan` 生成機能を後続 Issue で整備する方針でよいか。
- `assurance classify` の profile 指定は `--profile` で明示するのか、requirement の grade 判定材料から deterministic に抽出するのか。

pressure-test question として切り出すべき候補:

- `build_requirement_source_binding()` が `requirement.md` / `design.md` / `plan.md` すべてを hash 対象にする設計を維持するか。
- `draft-design` / `draft-plan` の provisional mode を許可する場合、canonical authority leak をどう防ぐか。
- Epic Planning 中の downstream Issue draft artifact は、必ず Issue-local artifact とするのか、cross-issue draft package にまとめる fallback を許すのか。

質問せずに解決できた候補:

- 非 active Issue に `--issue <id>` で artifact を作れるか。
  - 結論: 作れる。
- `.assurance.json` なしで `draft-design` / `draft-plan` を作れるか。
  - 結論: 作れない。fail-closed する。
- `assurance classify --dry-run --issue <id>` は active Issue なしで使えるか。
  - 結論: 使える。ただし dry-run は contract を書かない。

## terminology conflicts / 用語衝突

衝突している用語:

- `draft-design` / `draft-plan`
- `profile-aware draft`
- `Issue grade`
- `authorized_profile`
- `proposed profile`
- `valid assurance contract`
- `handoff-ready`
- `execution-ready`

既存 docs / code / tests / artifacts / primary sources での使われ方:

- `draft-design` / `draft-plan` は Issue-only artifact type だが、専用 artifact template ではなく profile-specific canonical template を source とする routing-only artifact である。
- `authorized_profile` は runtime template / guidance / obligation authority であり、manual escalation や proposed grade では上書きしない。
- `proposed profile` は現行 runtime の authority ではない。artifact に記録する場合は pending / unreviewed evidence として扱う必要がある。
- `handoff-ready` は Epic Planning が Issue Planning に渡せる状態であり、`execution-ready` は Issue Planning 後に canonical docs と reviewer gate が揃った状態である。

判断が必要な理由:

- 「draft」と呼ばれていても `draft-design` / `draft-plan` は profile-aware であり、assurance contract がない状態の自由な下書き置き場ではない。
- 自由下書きが必要な場合に `draft-design` / `draft-plan` という名前を使うと、valid `authorized_profile` に基づく draft と誤読される。

## edge cases / 具体シナリオ

edge case:

- Issue requirement はあるが canonical `design.md` / `plan.md` が placeholder でない。

影響:

- その状態で classify すると、misplaced draft body の hash を `.assurance.json` に固定する。先に draft body を artifact へ退避し、placeholder を復元してから classify する。

edge case:

- Issue requirement の grade 判定材料では `strict` が妥当だが、現行 CLI は default risk facts で `standard` を返す。

影響:

- `draft-design` / `draft-plan` を標準 profile で作ると、必要な specialist / evidence gate を過小化する。現行では `blank` / `disc` に intended strict と pending 状態を残し、後続 Issue で runtime 改善または manual evidence を追加する。

edge case:

- Epic Planning で downstream Issue の design/plan handoff をまとめたいが、`.assurance.json` はまだ作りたくない。

影響:

- 正規 `draft-design` / `draft-plan` ではなく、Issue-local `disc` または `blank` artifact を使う。artifact front matter / body に intended target、profile pending、non-authority を明示する。

edge case:

- `.assurance.json` 作成後に `requirement.md` / `design.md` / `plan.md` のいずれかが変わる。

影響:

- source binding が stale になり、`draft-design` / `draft-plan` や `assurance compose` は fail する。再 classify が必要である。

## implications / 判断への含意

Requirement への含意:

- Epic Planning が canonical Issue `requirement.md` を作る場合、後続の `assurance classify` がその requirement と placeholder design/plan を source binding に含めることを想定する必要がある。
- Issue requirement 内の grade 判定材料を、runtime が読める形へ整備する必要がある。

Design への含意:

- Issue Start 前の設計下書きには 2 種類ある。
  - valid `.assurance.json` に基づく profile-aware `draft-design`
  - assurance 前の neutral design handoff artifact
- 現行 command では後者を `draft-design` としては作れないため、`blank` / `disc` を使うか provisional mode を追加する必要がある。

Plan への含意:

- Issue Start 前の実装計画下書きも、valid `.assurance.json` に基づく `draft-plan` と、assurance 前の neutral planning handoff artifact を分ける必要がある。
- final delivery Issue のように前段結果依存が強いものは、neutral `disc` artifact で十分な場合がある。

ADR への含意:

- 前段の B/B+ 方針 ADR には、`draft-design` / `draft-plan` が現行 runtime では verified `.assurance.json` を前提にすること、assurance 前の下書きには neutral artifact を使うことを追記する。
- 長期的には「provisional profile-aware draft」を許可するかどうかを別 ADR または Issue で扱う。

Workflow / skill への含意:

- Epic Planning skill は「`draft-design` / `draft-plan` を作る」だけでなく、「作成前に `.assurance.json` valid/stale-free を確認する。ない場合は neutral artifact fallback を使う」と明示する。
- Epic Execution skill は、Issue Start 前に作られた neutral artifact を canonical design/plan authority と誤読しない。
- Issue Planning skill は、Issue Start 後に assurance classify/compose を実行し、neutral artifact / draft artifact を EAL で採用判断する。

## validation checks / 検証観点

- `./spec-dock/scripts/spec-dock new artifact --help` に `draft-requirement` / `draft-design` / `draft-plan` が表示されること。
- `.assurance.json` なしで `new artifact draft-design --issue <id>` が fail-closed すること。
- `.assurance.json` なしで `new artifact draft-plan --issue <id>` が fail-closed すること。
- `assurance classify --stage requirement --issue <id> --dry-run --format json` が non-active Issue を target にできること。
- non-dry-run classify 後に profile-specific `draft-design` / `draft-plan` が作れること。
- `.assurance.json` 作成後に source binding 対象を変更すると stale として検出されること。
- 未 start Issue の canonical `design.md` / `plan.md` が placeholder でない場合に warning / failure として検出できること。

## リスク/制約

- 現行 command のまま `draft-design` / `draft-plan` を B/B+ 方針の中心に置くと、`.assurance.json` prerequisite の見落としで workflow が止まる。
- default classify が `standard` に寄るため、Issue requirement 上の意図が `strict` / `critical` でも、現行 command だけでは過小 profile draft を作る危険がある。
- `.assurance.json` の手編集を通常運用にすると、authority / reproducibility / stale detection を壊す。
- neutral artifact fallback を使う場合、`draft-design` / `draft-plan` とは違うことを明記しないと、future agent が canonical-ready draft と誤読する。

## 反映先

候補:

- `epic-00270` の ADR: Epic Planning downstream Issue draft boundary
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `.agents/skills/spec-dock-epic-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `iss-00273` scope: scope layering / planning skills / workflow docs 更新
- `iss-00274` scope: Epic execution handoff / Issue readiness workflow 更新
- `iss-00275` scope: smoke tests / template validation

## 参考

- Deep consultant: `019f2166-c5f5-7ee3-b518-dec4601c9494`
- `new artifact` help:
  - `Artifact type: blank, research, interview, disc, decision-candidate, pr-repair-batch, adr, draft-requirement, draft-design, draft-plan`
- `assurance show --issue iss-00271`:
  - `has_contract: false`
  - `reason: missing_assurance_contract`
- `assurance classify --stage requirement --issue iss-00271 --dry-run`:
  - `authorized_profile: standard`
  - `dry_run: true`
- `new artifact draft-design --issue iss-00271`:
  - `error: Valid assurance contract is required before creating issue draft-design: reason=missing_assurance_contract`
- `new artifact draft-plan --issue iss-00271`:
  - `error: Valid assurance contract is required before creating issue draft-plan: reason=missing_assurance_contract`
