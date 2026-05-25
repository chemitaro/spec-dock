---
種別: research
ID: "20260525t055851z-research"
タイトル: "Draft Artifact Template Command Analysis"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-25"
親: ["iss-00127"]
関連: []
authority: "synthesized"
derived_from:
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
  - "src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/{requirement,design,plan}.md"
  - "src/spec_dock/assets/spec_dock/templates/discussions/*.md"
  - "src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md"
reflected_to: []
---

# 20260525t055851z-research Draft Artifact Template Command Analysis

## 調査目的

`system-architect` / `implementation-planner` が canonical `design.md` / `plan.md` を直接編集せず、scope-local `discussions/` に draft artifact を作成する運用を成立させるため、既存 template と `spec-dock new doc` コマンドをどう拡張するべきかを分析する。

対象は initiative / epic / issue それぞれの requirement / design / plan template と、discussion document 作成コマンドの接続方法である。

## 現状

### 既存コマンド

現在の discussion 作成経路は次の形である。

```bash
./spec-dock/scripts/spec-dock new doc <doc_type> --initiative <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc <doc_type> --epic <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc <doc_type> --issue <id> --title "<title>"
```

現時点の creatable `doc_type` は次の5種類だけである。

- `adr`
- `disc`
- `research`
- `interview`
- `scratch`

`note` は retired であり、新規作成は拒否される。

### 既存テンプレート

canonical artifact template は scope kind ごとに分かれている。

```text
templates/initiative/requirement.md
templates/initiative/design.md
templates/initiative/plan.md
templates/epic/requirement.md
templates/epic/design.md
templates/epic/plan.md
templates/issue/requirement.md
templates/issue/design.md
templates/issue/plan.md
```

discussion template は doc type ごとに分かれている。

```text
templates/discussions/adr.md
templates/discussions/disc.md
templates/discussions/interview.md
templates/discussions/research.md
templates/discussions/scratch.md
```

現状、`templates/discussions/` には draft requirement / draft design / draft plan 用 template は存在しない。

### 既存 naming / validation

discussion filename は timestamp prefix と kind を持つ。

```text
<ts>-<kind>-<slug>.md
<ts>-<nn>-<kind>-<slug>.md
```

runtime 側の filename parser / duplicate scanner は fixed doc type list を使っているため、新しい kind を追加する場合は以下の更新が必要になる。

- command help の allowed type
- application の creatable type list
- discussion filename regex
- template selection
- tests
- discussion rules docs
- provider asset と dogfooding mirror

## 問題

現在の `new doc disc` / `new doc research` だけでも draft 的な文書は作成できる。しかし、今回の delegated authoring の目的には不足がある。

1. `design.md` / `plan.md` の canonical template と構造が一致しない。
2. initiative / epic / issue で異なる artifact template を自動選択できない。
3. `system-architect` が作る draft design、`implementation-planner` が作る draft plan を機械的に区別できない。
4. draft artifact が canonical artifact と同じ frontmatter を持つと、authority / adoption 状態を誤読しやすい。
5. sub-agent output の provenance と adoption ledger 接続が、通常の `disc` / `research` より明確に必要になる。

特に 4 が重要である。canonical `templates/issue/design.md` などをそのまま `discussions/` にコピーすると、`種別: 設計書（Issue）`、`ID: "<ISS_ID>"`、`状態: "draft | approved"` のような canonical artifact 用 metadata が残る。これは discussion-local evidence である draft artifact としては authority が強すぎ、main orchestrator single-writer contract を曖昧にする。

## 推奨設計

### 方針

`new doc` を拡張し、draft artifact 専用 doc type を追加する。

推奨 doc type は次の3つである。

- `draft-requirement`
- `draft-design`
- `draft-plan`

今回の user request の最小範囲は `draft-design` と `draft-plan` だが、要件定義 draft も delegated authoring の自然な対象であるため、設計上は3種類を同じ枠組みに乗せるのがよい。

### コマンド例

```bash
./spec-dock/scripts/spec-dock new doc draft-design --issue iss-00127 --title "Static Discussion Write Design Draft"
./spec-dock/scripts/spec-dock new doc draft-plan --epic epic-00112 --title "Delegated Authoring Implementation Plan Draft"
./spec-dock/scripts/spec-dock new doc draft-requirement --initiative init-local-00003 --title "Delegated Authoring Requirement Draft"
```

生成先は既存 discussion rule と同じ flat layout にする。

```text
spec-dock/initiatives/<initiative>/discussions/<ts>-draft-requirement-<slug>.md
spec-dock/initiatives/<initiative>/epics/<epic>/discussions/<ts>-draft-design-<slug>.md
spec-dock/initiatives/<initiative>/epics/<epic>/issues/<issue>/discussions/<ts>-draft-plan-<slug>.md
```

same-second collision は既存通り `<ts>-<nn>-<kind>-<slug>.md` にする。

### Template source

draft artifact は、既存 canonical template を source として使う。ただし、canonical template をそのまま配置しない。

生成物は次の2層にする。

1. discussion-local draft envelope
2. canonical template body

例:

```markdown
---
種別: draft-design
ID: "<DRAFT_ID>"
タイトル: "<DRAFT_TITLE>"
状態: "proposed"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
親: ["<SCOPE_ID>"]
authority: "proposed"
created_by_role: "<ROLE_OR_UNSET>"
scope_id: "<SCOPE_ID>"
source_paths:
  - "spec-dock/templates/issue/design.md"
intended_targets:
  - "design.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "pending"
template_source: "templates/issue/design.md"
---

# <DRAFT_ID> <DRAFT_TITLE>

> This is a discussion-local draft. Canonical `design.md` remains main-orchestrator-only.

## Draft Provenance

- created_by_role:
  - ...
- scope_id:
  - ...
- intended_targets:
  - `design.md`
- adoption note:
  - Main orchestrator must record adoption in canonical `report.md`.

## Draft Body

<!-- canonical template body rendered from templates/issue/design.md starts here -->

# <ISS_ID> <ISS_TITLE> — 設計（どう実現するか）

...
```

この形なら、既存 template の構造を活かしつつ、discussion draft が canonical artifact そのものではないことを明確にできる。

## 実装案

### Option A: `new doc` に draft doc type を追加する

概要:

- `spec-dock new doc draft-design ...` を既存 `new doc` に追加する。
- `draft-design` / `draft-plan` / `draft-requirement` を creatable discussion doc type に追加する。
- `plan_discussion_doc` が draft type の場合だけ、scope kind と target artifact から canonical template を選び、draft envelope に包んで render する。

変更対象:

- `commands/new.py`
  - `_discussion_doc_types` に draft types を追加。
  - help text を更新。
- `application/contracts.py`
  - `CreateDiscussionDocRequest.doc_type` Literal を更新。
- `application/create_node.py`
  - `_CREATABLE_DISCUSSION_DOC_TYPES` を更新。
  - `_DISCUSSION_DOC_FILENAME_RE` を更新。
  - draft type の template source 解決を追加。
  - replacements に `<DRAFT_ID>` / `<DRAFT_TITLE>` / target artifact placeholders を追加。
- `templates/discussions/`
  - `draft-requirement.md`
  - `draft-design.md`
  - `draft-plan.md`
  - ただしこれらは envelope template として扱い、canonical body を差し込む。
- `docs/rules/{initiative,epic,issue}/discussions.md`
  - catalog に draft types を追加。
  - create command examples を追加。
- tests
  - CLI help / unknown type / new draft creation / timestamp collision / scope-specific template selection / mirror parity。

長所:

- 既存 UX と一貫する。
- discussion docs の naming / collision / scope resolution / lock / sync の仕組みを再利用できる。
- サブエージェントにも「まず `new doc draft-design` で draft を作る」と説明しやすい。

短所:

- `draft-design` のような hyphenated kind を filename regex と validation に追加する必要がある。
- `new doc` の責務が、単純 template copy から少しだけ artifact-aware rendering に広がる。

評価:

- 推奨。
- 既存の `new doc` は discussion document 作成の正規経路であり、ここに足すのが最も運用が単純。

### Option B: `new draft` サブコマンドを追加する

例:

```bash
./spec-dock/scripts/spec-dock new draft design --issue iss-00127 --title "..."
./spec-dock/scripts/spec-dock new draft plan --epic epic-00112 --title "..."
```

長所:

- draft artifact の特殊性を command surface で明確にできる。
- `doc_type` list と discussion kind list を過度に増やさずに済む。

短所:

- `new doc` と重複する scope resolution / naming / lock / template rendering が生じやすい。
- user / agent が「discussion docs は `new doc`、draft artifacts は `new draft`」を覚える必要がある。

評価:

- 非推奨。
- command surface が増え、運用が分岐する。

### Option C: `disc` / `research` に `--template design` を追加する

例:

```bash
./spec-dock/scripts/spec-dock new doc disc --issue iss-00127 --title "..." --template design
```

長所:

- filename kind を増やさない。
- 既存 regex の変更が少ない。

短所:

- ファイル名から draft design / draft plan を識別できない。
- `disc` と draft artifact の lifecycle / provenance が混ざる。
- delegated authoring の目的に対して発見性が低い。

評価:

- 非推奨。
- 今回の user intent は「draft 設計書 / draft 計画書を明示的に置く」ことであり、`disc` の variant に埋めると曖昧になる。

## 推奨する最小実装スコープ

今回 issue の follow-up として実装するなら、まず次を最小単位にするのがよい。

1. `draft-design` と `draft-plan` を追加する。
2. `draft-requirement` は同じ設計に入れるが、実装対象に含めるかは user decision にする。
3. scope kind ごとに canonical template source を選ぶ。
   - initiative + draft-design -> `templates/initiative/design.md`
   - epic + draft-design -> `templates/epic/design.md`
   - issue + draft-design -> `templates/issue/design.md`
   - initiative + draft-plan -> `templates/initiative/plan.md`
   - epic + draft-plan -> `templates/epic/plan.md`
   - issue + draft-plan -> `templates/issue/plan.md`
4. generated draft は discussion-local envelope を持つ。
5. canonical template frontmatter はそのまま権威 metadata として使わず、body section として差し込む。
6. filename は flat discussion naming に従う。
7. `diff-guard` は新 doc type を valid discussion Markdown として扱う。
8. `validate` / `sync` の discussion filename parser も新 doc type を許可する。

## 受け入れ条件案

- `spec-dock new doc draft-design --issue <id> --title "<title>"` が issue scope の `discussions/<ts>-draft-design-<slug>.md` を作成する。
- `spec-dock new doc draft-plan --epic <id> --title "<title>"` が epic scope の `discussions/<ts>-draft-plan-<slug>.md` を作成する。
- initiative / epic / issue で、それぞれ該当する canonical artifact template source が選ばれる。
- 生成ファイルは `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []`、`diff_guard_result` を持つ。
- 生成ファイルは canonical `requirement.md` / `design.md` / `plan.md` として扱われない。
- `validate` は新しい draft doc type の filename を valid として扱う。
- `sync` は discussion artifact として index に含めるが、canonical artifact として扱わない。
- `delegated-authoring diff-guard` は新規 draft doc を allowed discussion Markdown として分類できる。
- `note` retired behavior は変えない。
- provider assets と dogfooding mirror が一致する。

## テスト計画案

追加または更新するテスト:

- `tests/cli_runtime/test_new.py`
  - `new doc draft-design` / `draft-plan` が issue / epic / initiative scope に作成されること。
  - filename が timestamp + kind + slug 形式になること。
  - stdout が slugless id と discussions path を返すこと。
- `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - doc type parity に draft types を追加。
  - scope kind ごとに template source が変わること。
  - same-second suffix allocation が draft types でも機能すること。
- `tests/cli_runtime/test_validate.py`
  - `draft-design` / `draft-plan` filename を valid として扱うこと。
  - malformed draft filename を reject すること。
- `tests/cli_runtime/test_delegated_authoring.py`
  - diff-guard が新規 draft discussion Markdown を allow すること。
- `tests/test_init_update.py`
  - new templates と docs/rules/provider/mirror parity。

## リスク

### Hyphenated kind

`draft-design` のような kind は現行 kind より長く、hyphen を含む。regex を fixed alternatives にすれば曖昧さは抑えられるが、単純な `split("-")` 実装がどこかに残っている場合は壊れる可能性がある。

対策:

- parser は regex group を使い、hyphen split に依存しない。
- residual search で discussion filename parsing 箇所を確認する。
- tests で `draft-design` と `draft-plan` の timestamp / suffix / sync / validate を固定する。

### Canonical template frontmatter の誤用

canonical template を丸ごとコピーすると、discussion-local draft が canonical artifact のように見える。

対策:

- canonical template は body source として扱う。
- discussion-local frontmatter を envelope として必ず付ける。
- generated file に "Canonical docs remain main-orchestrator-only" の注意を含める。

### Scope-specific placeholder replacement

initiative / epic / issue で placeholder が異なる。

対策:

- scope node と親 node から `<INIT_ID>` / `<EPIC_ID>` / `<ISS_ID>` / title を補完する。
- 不明な GitHub linkage placeholder は既存 new node rendering と同じ placeholder または empty value を使う。

## 結論

draft artifact 作成は既存 `new doc` の拡張として実装するのが最もよい。

推奨コマンド:

```bash
./spec-dock/scripts/spec-dock new doc draft-design --issue <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-plan --issue <id> --title "<title>"
```

設計上は `draft-requirement` も同じ枠に入れられるようにしておくのが望ましい。ただし、実装スコープを絞るなら、まず user が明示した `draft-design` と `draft-plan` を優先し、`draft-requirement` は同一設計の追加候補として扱う。

重要なのは、既存 canonical template をそのまま `discussions/` にコピーしないことである。discussion-local draft envelope を付け、その中に scope-specific canonical template body を差し込む。これにより、sub-agent は構造化された draft artifact を作成でき、main orchestrator はそれを evidence として採否判断し、canonical docs へ再記述できる。
