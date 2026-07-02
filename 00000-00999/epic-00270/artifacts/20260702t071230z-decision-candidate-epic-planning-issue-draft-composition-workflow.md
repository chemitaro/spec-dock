---
種別: decision-candidate
ID: "20260702t071230z-decision-candidate"
タイトル: "Epic Planning における全 Issue draft design / draft plan 合成ワークフロー"
状態: "superseded"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t054322z-research"
  - "20260702t060525z-research"
  - "20260702t062053z-disc"
  - "20260702t073715z-decision-candidate"
authority: "superseded"
derived_from:
  - "artifacts/20260702t054322z-research-issue-planning-draft-strategy-analysis.md"
  - "artifacts/20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md"
  - "artifacts/20260702t062053z-disc-pre-start-issue-concretization-management-model.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/rules/issue/artifacts.md"
reflected_to: []
---

# Epic Planning における全 Issue draft design / draft plan 合成ワークフロー

> superseded: 2026-07-02 の再分析により、本 artifact の「全 grade で draft-design / draft-plan を作る」判断は維持する一方、`assurance compose-draft` を主導線にする案は `20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md` に更新した。最新版では、既存 `new artifact draft-design` / `draft-plan` を統一 primitive とし、`composed` / `authored` の違いは command ではなく lifecycle / metadata / EAL state として扱う。

## 判断候補

proposed decision:

- Epic Planning で複数 Issue を作成する場合、各 Issue の canonical `requirement.md` を具体化し、grade / risk facts / `authorized_profile` を決めたうえで、**全 grade の Issue に対して Issue-local `draft-design` / `draft-plan` を合成する**。
- Lite Issue でも `draft-design` / `draft-plan` は作成する。ただし Lite の draft は薄い alignment scaffold とし、専門家レビューや厚い設計作業を必須化しない。
- 既存の `assurance compose` は canonical `design.md` / `plan.md` を materialize する command として維持し、Epic Planning では原則使用しない。
- 新たに、profile template を canonical path ではなく Issue-local artifacts へ出力する **draft compose command** を導入する。
- Epic Planning workflow は downstream Issue 作成後、Issue Start 前に `issue prepare` / `assurance compose-draft` 相当の流れで draft design / draft plan artifact を作ることを標準 handoff に含める。

trigger:

- 前段分析では、Issue Start 前の canonical `design.md` / `plan.md` 本文作成は authority leak になると判断した。
- 一方で、Epic 単位で複数 Issue を具体化する場合、Lite / Standard であっても draft design / draft plan がないと cross-Issue 整合性、依存順、責務境界、検証観点を揃えにくい。
- 現行 `draft-design` / `draft-plan` は valid `.assurance.json` を要求するが、grade / risk facts の指定や一括 draft 合成 workflow が不足している。

affected scope:

- Epic Planning workflow
- Issue Planning workflow
- `assurance classify`
- `assurance compose`
- `new artifact draft-design` / `draft-plan`
- 新規候補 command: `assurance compose-draft`, `issue prepare`, `epic prepare-issues`
- Issue grade / risk facts template
- validation / smoke tests

## observed facts

- Issue requirement template には grade 判定材料と risk facts section がある。
- `workflow_spec_authoring.md` は `authorized_profile` を template / guidance / obligation authority と扱う。
- `draft-design` / `draft-plan` は Issue-only routing artifact であり、verified `.assurance.json` の `authorized_profile` に対応する `templates/issue-profiles/<profile>/design.md` / `plan.md` を source とする。
- 現行 `new artifact draft-design` / `draft-plan` は `.assurance.json` missing / invalid / stale の場合 no-write fail-closed する。
- 現行 `assurance compose` は canonical Issue `design.md` / `plan.md` を compose する command であり、Issue-local artifact draft だけを作る command ではない。
- 現行 `assurance classify` CLI は `--profile` / `--grade` / `--risk-fact` を持たず、requirement の grade 判定材料を deterministic に読む実装も不足している。

## ambiguity / constraint

- `assurance compose` を Issue Start 前に canonical path へ実行すると、`design.md` / `plan.md` が canonical authority と誤読されやすい。
- しかし draft design / draft plan が全くないと、Epic Planning で複数 Issue を整合させる力が弱くなる。
- Lite は軽量であるべきだが、Epic 全体の整合性のための薄い draft は有用である。
- Strict / Critical は draft artifact の存在だけでは足りず、substantive design / plan evidence、specialist / fallback / risk acceptance が必要になる。

## key distinction / 重要な区別

この方針では、draft を二層に分ける。

| 種類 | 目的 | 全 grade で必要か | authority |
| --- | --- | --- | --- |
| Composed draft | profile template を Issue-local artifact として合成し、設計・計画の形を揃える | yes | evidence only |
| Authored draft | system-architect / implementation-planner / manual fallback が実質的な設計・計画内容を埋める | grade による | evidence only |

Lite でも **composed draft** は作る。  
ただし Lite では **authored draft** は原則不要で、薄い draft に skip reason、変更境界、確認観点があればよい。

Strict / Critical では composed draft だけでは不足する。専門家 draft または manual fallback evidence が必要である。

## proposed command model

### Low-level command: `assurance compose-draft`

新規 command 候補:

```bash
./spec-dock/scripts/spec-dock assurance compose-draft \
  --issue <issue-id> \
  --artifact all
```

責務:

- valid `.assurance.json` を読む。
- `classification.authorized_profile` に対応する profile template を読む。
- canonical `design.md` / `plan.md` ではなく、Issue-local `artifacts/` に `draft-design` / `draft-plan` を作る。
- `draft-design` / `draft-plan` front matter に次を入れる。
  - `authority: "proposed"`
  - `artifact_state: "draft-composed"`
  - `scope_id: "<issue-id>"`
  - `authorized_profile: "<profile>"`
  - `profile_basis: "assurance_contract"`
  - `source_requirement_hash: "..."`
  - `source_assurance_contract_hash: "..."`
  - `intended_targets: ["design.md"]` または `["plan.md"]`
  - `adoption_status: "unreviewed"`
  - `reflected_to: []`
  - `not_canonical: true`
- canonical docs を変更しない。
- `.assurance.json` missing / invalid / stale では fail-closed する。

既存 `new artifact draft-design` / `draft-plan` との関係:

- 既存の routing-only artifact creation を内部 primitive として使ってよい。
- ただし user-facing workflow としては、`new artifact` を直接使うより `assurance compose-draft` の方が意図が明確である。
- `new artifact draft-design` / `draft-plan` は低レベル互換 surface として残してよい。

### High-level command: `issue prepare`

新規 command 候補:

```bash
./spec-dock/scripts/spec-dock issue prepare <issue-id> \
  --profile auto \
  --draft-policy always \
  --write-assurance
```

責務:

1. Issue node を解決する。active Issue である必要はない。
2. canonical `requirement.md` の存在と grade 判定材料を確認する。
3. canonical `design.md` / `plan.md` が compose placeholder であることを確認する。
4. requirement の risk facts / grade section から `authorized_profile` を決める。
5. `--write-assurance` なら `.assurance.json` を作成する。
6. `--draft-policy always` なら、Lite を含む全 grade で `draft-design` / `draft-plan` を作る。
7. Issue report または Epic handoff package に preparation result を記録する。
8. 出力状態を `prepared` / `handoff-ready` とし、`execution-ready` ではないことを明示する。

profile option:

- `--profile auto`
  - requirement の risk facts / grade section から deterministic に決める。
- `--profile lite|standard|strict|critical`
  - 明示 profile。manual decision evidence を要求する。

draft policy:

- `always`
  - 全 grade で composed draft design / plan を作る。今回の推奨 default。
- `auto`
  - 将来使う余地はあるが、Epic Planning では `always` の方が整合性が高い。
- `none`
  - 特殊な shell-only / research-only Issue 用。

### Epic-level batch command: `epic prepare-issues`

新規 command 候補:

```bash
./spec-dock/scripts/spec-dock epic prepare-issues epic-00270 \
  --draft-policy always \
  --write-assurance
```

責務:

- Epic 配下の planned Issues を列挙する。
- 各 Issue に `issue prepare` を実行する。
- 結果を Epic handoff index と report evidence に集約する。
- Issue ごとに、以下を表で出す。
  - issue id
  - requirement state
  - authorized_profile
  - draft-design path
  - draft-plan path
  - preparation warnings
  - handoff-ready / blocked reason

## canonical compose policy

`assurance compose` は canonical `design.md` / `plan.md` を作る command として維持する。

推奨:

- Epic Planning では原則 `assurance compose` を実行しない。
- Epic Planning では `assurance compose-draft` または `issue prepare --draft-policy always` を使う。
- `issue start` 後の Issue Planning で `assurance compose --artifact all --issue <id>` を実行し、canonical `design.md` / `plan.md` を materialize する。
- Issue Planning は draft artifacts を Evidence Adoption Ledger 経由で採用・部分採用・棄却する。

理由:

- canonical `design.md` / `plan.md` を pre-start に materialize すると、phase promotion と誤認されやすい。
- draft artifact であれば、Epic Planning の整合性確保と canonical authority boundary を両立できる。
- 同じ profile template を使うので、Issue Start 後の canonical compose と構造のズレが小さい。

例外:

- 将来、pre-start canonical compose を許す場合でも、`artifact_state: prepared-template` のような明確な状態と validation が必要である。
- 現時点の推奨では例外を導入しない。

## grade policy

全 grade で composed `draft-design` / `draft-plan` を作る。

| Grade | Composed draft | Authored draft | Specialist / fallback | 方針 |
| --- | --- | --- | --- | --- |
| `lite` | 必須 | 原則不要 | 不要。skip reason / not applicable を記録 | 薄い design/plan draft を作り、変更境界と確認観点を揃える |
| `standard` | 必須 | 推奨だが optional | 使わない場合は skip reason | 既存 pattern、変更境界、検証観点を揃える |
| `strict` | 必須 | 必須相当 | specialist または manual fallback evidence | dependency、risk、closure、review gate を具体化 |
| `critical` | 必須 | 必須 | specialist + risk / ADR / acceptance | rollback、observability、manual gate、risk acceptance まで具体化 |

Lite で draft を作る理由:

- Epic Planning で Issue 間の責務境界と依存順を見比べられる。
- 後続 agent が `design.md` / `plan.md` の期待形を予測しやすい。
- Lite でも「何をしないか」「どこまで確認するか」が見える。
- draft が薄ければ、Lite の軽量性を損なわない。

Lite で避けること:

- 専門家 draft を必須にする。
- closure matrix や heavy review gate を標準化する。
- draft があるだけで implementation-ready と扱う。

## options considered

### Option A: Lite / Standard では draft を作らない

Pros:

- 軽い。
- artifact が増えにくい。

Cons:

- Epic Planning で全 Issue の設計・計画の形を比較しにくい。
- Lite / Standard Issue が多い Epic ほど、cross-Issue 整合性が弱くなる。
- 後続 agent が Issue Start 後に設計粒度を揃え直す必要が出る。

Disposition:

- rejected。単独 Issue では軽いが、Epic Planning では整合性のコストが後ろ倒しになる。

### Option B: 全 grade で composed draft design / plan を作る

Pros:

- Epic Planning で全 Issue の形を揃えられる。
- Lite でも変更境界と確認観点が明確になる。
- Strict / Critical の handoff seed と同じ流れにできる。
- canonical docs に書かないため authority leak を避けられる。

Cons:

- artifact 数は増える。
- draft を canonical-ready と誤読しない validation / report 表現が必要。

Disposition:

- accepted candidate。今回の推奨。

### Option C: Epic Planning で canonical `assurance compose` を実行する

Pros:

- profile-specific canonical template が早く見える。
- 既存 compose command を使える。

Cons:

- canonical path が phase promotion と誤読される。
- Issue Start 後の fresh compose / adoption / reviewer gate が曖昧になる。
- pre-start の repo 状態・前段 Issue 結果とずれやすい。

Disposition:

- rejected as default。draft compose command を別に作る方がよい。

### Option D: `draft-design` / `draft-plan` を自由下書き artifact にする

Pros:

- `.assurance.json` なしでも作れる。
- 実装が簡単に見える。

Cons:

- 現行 docs では `draft-design` / `draft-plan` は profile-aware routing artifact である。
- 自由下書きと profile-aware draft が混ざる。
- `authorized_profile` の意味が弱くなる。

Disposition:

- rejected。自由下書きは `disc` / `blank` / `decision-candidate` にする。

## implementation plan

### Step 1: Assurance contract の source binding を整理する

- `assurance classify --stage requirement` の source binding は原則 `requirement.md` を中心にする。
- canonical `design.md` / `plan.md` placeholder の hash を requirement-stage contract に固定しない。
- draft compose result は draft artifact path / profile template hash / requirement hash を provenance として持つ。

### Step 2: requirement grade / risk facts の parser を追加する

- `templates/issue/requirement.md` の grade section と risk facts table を deterministic に読む。
- `true / false / unknown` を正規化する。
- unknown が多い場合、Lite には倒さず Standard 以上にする。
- explicit grade と risk facts が矛盾する場合は fail / warning とする。

### Step 3: `assurance compose-draft` を追加する

- `--issue <id>` と `--artifact design|plan|all` を受け付ける。
- valid `.assurance.json` を要求する。
- profile template を Issue-local `artifacts/` に `draft-design` / `draft-plan` として出力する。
- canonical docs を変更しない。
- missing / invalid / stale contract では no-write fail-closed。

### Step 4: `issue prepare` を追加する

- `--profile auto`
- `--draft-policy always`
- `--write-assurance`
- `--dry-run`
- `--format text|json`
- active Issue を変更しない。
- preparation result を返す。

### Step 5: Epic Planning workflow に追加する

- Epic Planning で downstream Issue を作成した後:
  1. canonical `requirement.md` を具体化する。
  2. grade / risk facts を埋める。
  3. `issue prepare --draft-policy always` を実行する。
  4. draft design / draft plan path を Epic handoff package に記録する。
- Handoff package は `draft-design` / `draft-plan` paths を全 Issue について持つ。
- skipped draft は例外扱いにし、skip reason を必須にする。

### Step 6: validation / smoke tests を追加する

- Lite Issue でも composed draft design / plan が作られること。
- Strict / Critical では composed draft だけで specialist evidence gate を満たした扱いにならないこと。
- pre-start `assurance compose` が canonical docs を更新する path は Epic Planning smoke で使わないこと。
- `compose-draft` が canonical `design.md` / `plan.md` を変更しないこと。
- stale `.assurance.json` で `compose-draft` が fail-closed すること。

## adoption target

`requirement.md`:

- Issue grade / risk facts section を runtime-readable にする。
- Lite でも draft design / draft plan を作る理由を Epic handoff 観点として明記する。

`design.md`:

- Issue Preparation Layer を追加する。
- Composed draft と authored draft の二層モデルを定義する。
- `assurance compose-draft` と canonical `assurance compose` の責務境界を定義する。

`plan.md`:

- `assurance compose-draft`
- `issue prepare`
- `epic prepare-issues`
- validation / smoke tests
- current `epic-00270` の misplaced canonical draft migration

`ADR`:

- この decision-candidate は ADR 化候補。
- ADR title 候補: `ADR: Epic Planning で全 Issue の draft design / draft plan を合成する`

`report.md` Evidence Adoption Ledger:

- 前段 research とこの decision-candidate の採否を記録する。

## risk if wrong

- 全 grade draft を必須にすると artifact 数が増え、探しにくくなる。
- Lite draft が厚くなりすぎると Lite の価値が消える。
- `draft-design` / `draft-plan` を canonical-ready と誤読すると、Issue Start 後の fresh review が弱くなる。
- `assurance compose-draft` と `assurance compose` の境界が曖昧だと、同じ profile template から二種類の authority が生まれて混乱する。

## rollback or revisit

- `draft-policy always` が過剰なら `auto` に戻せる。
- Lite draft が過剰なら Lite profile template をさらに薄くする。
- `compose-draft` が不要と判断された場合でも、canonical compose policy は維持できる。
- artifact 数が多すぎる場合、Epic handoff index と report table で path を集約する。

## status / disposition

status:

- proposed

disposition evidence:

- ユーザーの新判断: Lite でも Epic 全体の整合性のため draft design / draft plan があった方がよい。
- 前段 research: canonical Issue design/plan pre-start authoring は避けるべき。
- 本 decision-candidate: canonical compose とは別に draft compose command を導入し、全 grade の Issue-local draft design / draft plan を Epic Planning handoff に含める。
