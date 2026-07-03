---
種別: disc
ID: "20260702t062053z-disc"
タイトル: "Issue Start 前の Issue 具体化管理モデル"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t054322z-research"
  - "20260702t060525z-research"
authority: "proposed"
derived_from:
  - "artifacts/20260702t054322z-research-issue-planning-draft-strategy-analysis.md"
  - "artifacts/20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/rules/issue/artifacts.md"
  - "spec-dock/docs/workflow_epic.md"
  - "spec-dock/templates/issue/requirement.md"
reflected_to: []
---

# Issue Start 前の Issue 具体化管理モデル

## 対象論点

今回整理する論点:

- Epic Planning が、まだ `issue start` していない downstream Issue をどこまで具体化してよいか。
- Issue 外部から `assurance classify`、grade / `authorized_profile` 決定、profile 別 `design.md` / `plan.md` template 配置、`draft-design` / `draft-plan` 作成を行うべきか。
- Lite / Standard / Strict / Critical の grade ごとに、pre-start draft をどの程度必要とするか。
- 現行 command が不足している場合、どのような管理方法 / command surface がよいか。

この synthesis が必要な理由:

- 前段分析では「Issue Start 前に canonical `design.md` / `plan.md` へ本文を置かない」方針が妥当とされた。
- 一方で、Epic Planning は downstream Issue の抜け漏れ、重複、依存順、handoff 品質を管理する必要がある。
- `draft-design` / `draft-plan` は単なる自由下書きではなく、現行 runtime では valid `.assurance.json` の `authorized_profile` に基づく routing-only artifact である。
- Lite Issue では設計書 / 実装計画書ドラフトを厚く作ること自体が過剰になり得る。
- Strict / Critical Issue では、Issue Start まで全てを先送りすると、Epic Planning 時点のリスク・依存・専門家 evidence が弱くなる。

## derived question sheets / research

`interview`:

- なし。この synthesis は現時点では source-grounded に解ける範囲の提案である。

`research`:

- `20260702t054322z-research-issue-planning-draft-strategy-analysis.md`
  - 制約付き B/B+ hybrid を推奨。
  - canonical Issue `design.md` / `plan.md` は Issue Start 後に compose し、pre-start design/plan は Issue-local artifact に置く方針。
- `20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md`
  - 非 active Issue でも `--issue <id>` は使える。
  - `draft-design` / `draft-plan` は valid `.assurance.json` がないと作れない。
  - 現行 CLI には `--profile` / `--grade` / `--risk-fact` がない。

その他の根拠:

- `workflow_spec_authoring.md` の grade matrix。
- `spec-dock/docs/rules/issue/artifacts.md` の routing-only `draft-design` / `draft-plan` 定義。
- `workflow_epic.md` の Epic handoff package。
- `templates/issue/requirement.md` の grade 判定材料 / risk facts。

## synthesis

合意済みのこと:

- Issue Start 前に canonical Issue `design.md` / `plan.md` を本文入りにするべきではない。
- Epic Planning は downstream Issue の shell、dependency、requirement、handoff evidence を管理してよい。
- Issue-local artifact は canonical authority ではなく、Issue Planning で採用判断する evidence である。
- `authorized_profile` は template / guidance / obligation authority であり、単なる人間メモではない。

未合意 / 未確定のこと:

- Issue Start 前に `.assurance.json` を non-dry-run で作成する運用を正式に認めるか。
- pre-start の `draft-design` / `draft-plan` を grade ごとに必須化するか。
- `assurance classify` が requirement の grade 判定材料 / risk facts を deterministic に読むべきか、それとも `--risk-fact` / `--profile` で明示指定するべきか。
- `draft-design` / `draft-plan` の provisional mode を導入するか。

source-grounded に解決できたこと:

- 現行 command では非 active Issue に artifact を作れる。
- しかし `.assurance.json` がない Issue に `draft-design` / `draft-plan` は作れない。
- Lite は automatic default ではなく、低リスク根拠と explicit opt-in が必要である。
- `draft-design` / `draft-plan` は verified `.assurance.json` の `authorized_profile` に対応する profile template を render する artifact であり、自由下書き用ではない。

## 推奨モデル: Issue Preparation Layer

Issue Start 前の具体化は、`Issue Planning` でも `Issue Execution` でもなく、**Issue Preparation** という中間層として扱うのがよい。

Issue Preparation の目的:

- downstream Issue の grade / risk / handoff depth を Epic Planning 中に整理する。
- active Issue を切り替えずに、Issue ごとの planning seed を作る。
- ただし `execution-ready` や canonical phase promotion を主張しない。

Issue Preparation が作ってよいもの:

- Issue shell。
- canonical `requirement.md`。
- requirement に基づく grade / risk facts。
- `assurance classify --dry-run` または将来の `issue prepare` による proposed / provisional profile evidence。
- Issue-local neutral artifact:
  - `blank`
  - `disc`
  - `research`
  - `decision-candidate`
- valid `.assurance.json` がある場合だけ:
  - `draft-design`
  - `draft-plan`

Issue Preparation が作ってはいけないもの:

- Issue Start 前の canonical `design.md` / `plan.md` 本文。
- `draft-design` / `draft-plan` を canonical-ready / phase-promoted と扱う report evidence。
- Lite 根拠なしの Lite profile 固定。
- Strict / Critical の専門家 evidence を、空テンプレート自動生成だけで満たしたことにする運用。

## グレード別 draft policy

| Grade | Pre-start requirement | Pre-start assurance | Pre-start design/plan seed | `draft-design` / `draft-plan` | Specialist / evidence | 備考 |
| --- | --- | --- | --- | --- | --- | --- |
| `lite` | canonical `requirement.md` を短く固定してよい。Lite 採用理由と低リスク根拠を必須にする。 | `assurance classify --dry-run` または将来の `issue prepare --dry-run` で十分。non-dry-run は Issue Start 後でもよい。 | 原則不要。必要なら `disc` 1本に skip reason と確認観点だけ置く。 | 原則不要。自動生成しない。 | specialist 不要。not applicable / skip reason を report に残す。 | Lite で draft design/plan を厚く作ると、Lite の価値を壊す。 |
| `standard` | canonical `requirement.md` を固定してよい。AC / EC / scope / non-scope / parent trace を持つ。 | dry-run で proposed profile を確認。必要に応じて non-dry-run classify。 | neutral `disc` または `decision-candidate` を推奨。 | optional。valid `.assurance.json` があり、handoff に価値がある場合だけ作る。 | specialist 推奨。使わない場合は skip reason。 | 標準は「毎回 draft-design/plan 必須」では重い。 |
| `strict` | requirement に上位 trace、non-scope、依存、boundary、risk facts を明確化する。 | pre-start non-dry-run classify を許可する価値が高い。ただし canonical design/plan は placeholder 維持。 | 必須に近い。少なくとも Issue-local `disc` で design/plan risk と dependency を整理する。 | 原則作る。valid `.assurance.json` が作れない場合は `disc` fallback と blocked / pending reason を残す。 | system-architect / implementation-planner または manual fallback evidence が必要。 | 自動テンプレート生成だけでは足りない。substantive draft または明示的 fallback が必要。 |
| `critical` | requirement に安全性、不可逆性、外部契約、rollback、risk acceptance を明記する。 | pre-start classify は推奨だが、profile 固定には明示 decision / ADR / risk acceptance が必要。 | 必須。risk / rollback / observability / manual gate を artifact で整理する。 | 作るだけでは不足。draft + risk / rollback / review strategy artifact が必要。 | specialist 必須。unavailable 時は原則 blocked。 | 自動生成よりも、人間 decision と reviewer gate が重要。 |

## 選択肢 / tradeoff

### Option A: Issue Start 前は shell / requirement だけにする

Pros:

- stale draft や authority leak が最も少ない。
- `issue start` / assurance compose の責務が明確。
- Lite Issue では軽い。

Cons:

- Strict / Critical の cross-Issue risk や依存調整が Epic Planning 時点で弱い。
- 後続 Issue の重複・抜け漏れ検出が遅れる。
- issue start 後に初めて大きな設計問題が出る。

評価:

- default としては安全だが、Strict / Critical には弱い。

### Option B: Issue Start 前に assurance と profile-aware draft を作る

Pros:

- grade に応じた template と obligation を早く見える化できる。
- Strict / Critical の handoff 品質が上がる。
- Issue Planning の開始時に材料が揃いやすい。

Cons:

- 現行 command では `.assurance.json` prerequisite と source binding stale の扱いが難しい。
- requirement の grade 判定材料を CLI が読めないため、標準 profile に寄りやすい。
- 空テンプレート生成だけを設計ドラフトと誤認する危険がある。

評価:

- 仕組みを整えれば有用。ただし今すぐ全面採用は危険。

### Option C: `issue prepare` を導入し、pre-start 具体化を専用状態にする

Pros:

- active Issue を切り替えずに grade / assurance / draft policy を整理できる。
- canonical design/plan と artifact draft の境界を守れる。
- Lite / Standard / Strict / Critical で draft depth を変えられる。
- `handoff-ready` と `execution-ready` を分離できる。

Cons:

- runtime command / docs / tests の追加が必要。
- `.assurance.json` の status / source binding semantics を少し整理する必要がある。

評価:

- 推奨。SpecDock の責務境界に最も合う。

### Option D: `draft-design` / `draft-plan` の provisional mode を追加する

Pros:

- `.assurance.json` がない段階でも profile candidate に沿った draft artifact を作れる。
- Epic Planning 時点の handoff が豊かになる。

Cons:

- `authorized_profile` と `proposed_profile` の混同が起きやすい。
- provisional draft を canonical-ready と誤読する危険がある。
- validation / report evidence が弱いと authority leak になる。

評価:

- 補助策としては有用。ただし `issue prepare` の一部として統制するべきで、単独の自由機能にしない方がよい。

## reflection proposal

canonical docs / workflow / template / skill guidance へ反映すべき候補:

- `Issue Preparation` という pre-start handoff layer を導入する。
- `handoff-ready` と `execution-ready` を明確に分ける。
- Lite は pre-start `draft-design` / `draft-plan` を原則不要にする。
- Standard は neutral seed を推奨し、profile-aware draft は optional にする。
- Strict / Critical は pre-start design/plan seed を原則必須にし、profile-aware draft または明示的 fallback / blocked reason を要求する。
- `draft-design` / `draft-plan` は valid `.assurance.json` がある場合の profile-aware artifact とし、自由下書きには `disc` / `blank` / `decision-candidate` を使う。
- `assurance classify` は requirement の grade 判定材料 / risk facts を読めるようにするか、CLI で `--risk-fact` を受け付ける。

まだ proposal に留める理由:

- `.assurance.json` を Issue Start 前に書くことの lifecycle authority を、まだ正式 ADR として採用していない。
- 現行 `build_requirement_source_binding()` が `design.md` / `plan.md` も hash に含めるため、pre-start classify の前提整理が必要。
- `draft-design` / `draft-plan` provisional mode は authority leak を起こしやすく、validation 仕様が必要。

## command surface proposal

新しい command として、次を検討する。

```bash
./spec-dock/scripts/spec-dock issue prepare <issue-id> \
  --profile auto \
  --draft-policy auto \
  --write-assurance
```

主要 option:

- `--profile auto|lite|standard|strict|critical`
  - `auto`: requirement の grade 判定材料 / risk facts から判定する。
  - explicit profile は report evidence または decision artifact を要求する。
- `--draft-policy auto|none|neutral|profile-aware|required`
  - `auto`: grade matrix に従う。
  - `none`: shell / requirement / assurance evidence だけ。
  - `neutral`: `disc` / `decision-candidate` seed を作る。
  - `profile-aware`: valid contract に基づく `draft-design` / `draft-plan` を作る。
  - `required`: 作れない場合は fail-closed。
- `--write-assurance`
  - `.assurance.json` を作成する。
  - なしの場合は dry-run / proposed profile artifact のみ。
- `--no-canonical-compose`
  - default。Issue Start 前は canonical `design.md` / `plan.md` を compose しない。
- `--compose-canonical`
  - 原則非推奨。将来使う場合も `issue start` 後、または明示 approval がある場合に限定する。

`issue prepare` の処理順:

1. Issue node と parent Epic を解決する。
2. active Issue でなくてもよいが、active Issue を切り替えない。
3. canonical `requirement.md` が存在し、grade 判定材料が埋まっているか確認する。
4. canonical `design.md` / `plan.md` が placeholder か確認する。
5. requirement の risk facts を読み、profile を判定する。
6. `--write-assurance` があれば `.assurance.json` を作る。
7. grade と `draft-policy` に応じて Issue-local artifacts を作る。
8. `report.md` または Epic handoff package に preparation result を記録する。
9. 出力は `handoff-ready` / `prepared` であり、`execution-ready` ではないと明示する。

## state model proposal

Issue lifecycle に次の中間状態を追加する。

| State | 意味 | 作れるもの | 作ってはいけないもの |
| --- | --- | --- | --- |
| `shell` | Issue directory / metadata だけある | `.meta.json`, placeholder docs | grade authority claim |
| `requirements-ready` | canonical requirement が handoff に耐える | `requirement.md`, requirement review evidence | canonical design/plan body |
| `prepared` | pre-start grade / draft policy / seed がある | `.assurance.json` または proposed profile artifact, neutral seed, optional profile-aware draft | execution-ready claim |
| `active-planning` | `issue start` 後、Issue Planning 中 | canonical design/plan compose, EAL adoption | implementation without review |
| `execution-ready` | canonical docs と reviewer gate が揃う | executable plan | unresolved EAL / stale draft |
| `in-execution` | Issue Execution 中 | implementation evidence | planning shortcut |

## adoption target / 採用先候補

`requirement.md`:

- Issue requirement template の grade 判定材料を runtime-readable にする。
- Risk facts の値を `true / false / unknown` として deterministic に抽出できる形へ寄せる。

`design.md`:

- Epic design に `Issue Preparation Layer` を追加する。
- canonical design/plan と pre-start seed artifact の責務境界を明記する。

`plan.md`:

- Issues に `issue prepare` command / fallback を組み込む。
- `iss-00273` / `iss-00274` / `iss-00275` の scope に command/docs/tests の反映を割り当てる。

`ADR`:

- `Issue Preparation Layer` と grade別 draft policy は ADR 候補。

`report.md` Evidence Adoption Ledger:

- 前段 research と本 synthesis の採否を記録する。

## ADR triage

ADR candidate か:

- yes

hard to reverse:

- yes

surprising without context:

- yes

real tradeoff:

- yes

ADR 化しない場合の反映先:

- `design.md`
- `plan.md`
- `workflow_epic.md`
- `workflow_issue.md`
- `workflow_spec_authoring.md`

## 推奨案

現時点の推奨案:

**Issue Start 前の downstream Issue 具体化は、`Issue Preparation Layer` として管理する。**

この layer は active Issue を切り替えず、Issue の requirement readiness、grade / risk facts、draft policy、handoff seed を作る。ただし canonical `design.md` / `plan.md` の本文作成、phase promotion、execution-ready 判定は Issue Start 後の Issue Planning に残す。

Grade ごとの推奨:

- Lite:
  - pre-start `draft-design` / `draft-plan` は作らない。
  - requirement と Lite 採用理由、低リスク evidence、skip reason で十分。
- Standard:
  - neutral seed artifact を推奨。
  - `draft-design` / `draft-plan` は optional。
- Strict:
  - design/plan seed を必須に近い扱いにする。
  - valid `.assurance.json` があれば `draft-design` / `draft-plan` を作る。
  - 作れない場合は neutral fallback artifact と blocked / pending reason を残す。
- Critical:
  - profile-aware draft だけでは不足。
  - risk / rollback / observability / manual gate / ADR / risk acceptance を含む preparation package が必要。

理由:

- Lite の軽さを守れる。
- Strict / Critical の事前リスク管理を強化できる。
- `draft-design` / `draft-plan` の profile-aware 性質を壊さない。
- canonical docs と artifact evidence の境界を維持できる。
- Epic Planning は cross-Issue control を持ち、Issue Planning は canonical authoring を持つ、という責務分離が保てる。

## 推奨反映先

`requirement.md`:

- Issue grade / risk facts section を runtime-readable にする方針を追加する。

`design.md`:

- Issue Preparation Layer、state model、grade別 draft policy を追加する。

`plan.md`:

- `issue prepare` command / workflow docs / validation tests を実装対象に組み込む。

`ADR`:

- `Issue Preparation Layer and Grade-Based Draft Policy` として ADR 化する。

`report.md` Evidence Adoption Ledger:

- 本 artifact を `partially_adopted` または `adopted` として記録する。

## 未採用 / deferred 理由

未採用:

- Issue Start 前に canonical `design.md` / `plan.md` を profile template で埋める案。
  - 理由: canonical path が authority と誤読されやすく、Issue Start 後の fresh compose / reviewer gate を弱める。
- Lite でも一律 `draft-design` / `draft-plan` を作る案。
  - 理由: Lite の軽量性を壊す。
- Strict / Critical でテンプレート自動生成だけを draft evidence とする案。
  - 理由: specialist / risk evidence の代替にならない。

deferred:

- `draft-design|draft-plan --profile --provisional`
  - 理由: 便利だが authority leak のリスクが高く、front matter / validation / report evidence の設計が必要。
- `.assurance.json` の pre-start 書き込み標準化。
  - 理由: source binding と stale semantics を整理してから採用するべき。

## 次アクション

`requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:

- ADR を作成し、Issue Preparation Layer と grade別 draft policy を採用するか判断する。
- Epic plan を更新し、`iss-00273` / `iss-00274` / `iss-00275` に反映作業を割り当てる。
- workflow docs に `handoff-ready` / `prepared` / `execution-ready` の区別を追加する。
- current `epic-00270` の既存 misplaced canonical design/plan draft は、`Issue Preparation` 方針に沿って neutral artifact へ退避する migration plan を作る。

追加で作る artifacts:

- ADR: `Issue Preparation Layer and Grade-Based Draft Policy`
- 必要なら research: `assurance source binding stage semantics`
- 必要なら decision-candidate: `assurance classify risk-fact command design`
