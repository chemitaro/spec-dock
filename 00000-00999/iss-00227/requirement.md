---
種別: 要件定義書（Issue）
ID: "iss-00227"
タイトル: "Introduce Assurance Contract And Classification Runtime"
関連GitHub: ["#227"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00227 Introduce Assurance Contract And Classification Runtime — 要件定義（何を、なぜ行うか）

## 目的

- Active Issue に tracked `assurance.json` を導入し、risk facts から Assurance Profile と Complexity Tier を deterministic に分類・表示・検証できる最小 runtime capability を提供する。
- 後続 Issue が Runbook compiler、artifact composition、step assurance、context routing、review policy を実装できるよう、Issue-local Assurance Contract の schema、domain model、CLI surface を先に固定する。
- 軽量 Issue の過剰 gate 削減はこの Issue 単体では有効化せず、`lite_candidate` と `lite_authorized` を分離して安全な段階導入の土台だけを作る。

## 背景・現状

- Epic `epic-00224 Dynamic Workflow Resource Allocation` は、SpecDock workflow が軽量 task にも重い planning / execution / review gate を課し、token と wall-clock time を過剰消費する問題を扱う。
- 現在の runtime には、Issue ごとの Assurance Profile、Complexity Tier、source binding、obligation を tracked contract として保持する機械可読な authority がない。
- Skill や agent が都度判断で workflow を軽くすると、review independence、source freshness、hard-risk escalation を壊しやすい。
- そのため、まず Issue-local `assurance.json` と deterministic classification を導入し、後続 Issue がこの contract を authority として参照できるようにする。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `discussions/20260623t033541z-draft-requirement-draft-requirement.md`
  - `discussions/20260623t033545z-draft-design-draft-design.md`
  - Epic accepted ADRs under `spec-dock/active/epic/discussions/20260623t07444*z-adr-*.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock を操作する main orchestrator agent。
  - Issue planning / execution / PR delivery workflow を実行する SpecDock runtime command。
  - 後続 Issue で Runbook、artifact composition、step assurance、context routing を実装する開発者 / agent。
- 代表シナリオ:
  - Active Issue の requirement phase で `assurance classify --stage requirement` を実行し、provisional classification を `assurance.json` として保存する。
  - 既存 Issue に `assurance.json` がない場合、runtime が strict-legacy compatibility path の候補として検出する。
  - 同じ canonical input と policy version から同じ classification JSON が得られることを test で保証する。

## スコープ

- 必須:
  - Issue-local `assurance.json` の最小 schema と domain model。
  - Assurance Profile `lite / standard / strict / critical` と Complexity Tier `routine / normal / complex / deep` の分離。
  - Standard default、Lite all-positive predicate、hard trigger、unknown fail-closed を持つ deterministic classification policy。
  - `lite_candidate` と `lite_authorized` の分離。
  - `assurance show / classify / verify` の最小 runtime command。
  - `assurance.json` が存在しない既存 Issue を strict-legacy candidate として扱う検出機構。
  - Provider-side source と dogfooding mirror の同期対象を明確にした test coverage。
- 禁止:
  - Skill kernel の切替や `.agents/skills/**` の profile 別差し替え。
  - Runbook compiler、workflow next、artifact composition、step assurance、context packet、GitHub review trigger、PR blocker policy の実装。
  - Lite を automatic default として有効化すること。
  - Shadow の `lite_candidate` によって obligations を減らすこと。
  - Lite eligibility predicate が全て true でも、explicit opt-in と evidence gate が未成立の状態で `lite_authorized` を true にすること。
- 対象外:
  - E-RQ-012 の rollout / rollback formal close。
  - E-RQ-013 以降の metrics / telemetry / auto-lite readiness report。
  - GitHub Codex review policy の base SHA binding と blocker closure。

## 境界

- 常に行う:
  - Classification は pure domain logic として filesystem、GitHub、CLI に依存させない。
  - Runtime command は active Issue または明示 issue path に対して `assurance.json` を read/write/verify する。
  - Unknown risk fact は Lite authorization を拒否する。
  - Hard trigger は lower profile への override を許可しない。
- 判断が必要:
  - 個別 risk fact の抽出粒度は、後続 Runbook / artifact composition が必要とする最小に留める。
  - `assurance.json` schema は後続 Issue で source binding や step obligations を拡張できる forward-compatible な形にする。
- 行わない:
  - Agent の context mode や reviewer clean-room packet をこの Issue で選択しない。
  - PR review finding の priority / blocker 判定をこの Issue で扱わない。

## 非交渉制約

- Provider-side shipped asset が authority であり、実装変更は `src/spec_dock/assets/spec_dock/...` を正とする。
- Dogfooding mirror `spec-dock/...` は validation / inspection target として同期・確認する。
- New Python modules は型注釈を持ち、Ruff / MyPy baseline を悪化させない。
- Existing Issue は `assurance.json` がなくても壊さず、strict-legacy compatibility path の候補として扱う。
- Contract / classification output は deterministic で、同じ input と policy version から byte-identical JSON を生成できる。

## 前提

- Epic scope の ADR で、固定 Skill kernel、compiled Runbook authority、adaptive assurance、context routing、trusted review policy、blocker-centric closure の方向性は accepted 済み。
- 親 Epic の front matter は planning 中の `draft` 表記を保持しているが、この Issue では Epic accepted ADR と現行 Epic requirement / design / plan の planning baseline を実装境界の参照元として扱う。
- `iss-00226` は Epic-scope ADR へ吸収済みであり、この Issue は実装可能な first slice として扱う。
- Main branch merge 後の Ruff / MyPy 設定は現在の実装 baseline として通過済みであり、この Issue ではその baseline を維持する。

## 受け入れ条件

- AC-001: Requirement stage classification
  - アクター: SpecDock runtime user。
  - 前提: Active Issue または明示 issue path に canonical requirement が存在する。
  - 操作: `spec-dock assurance classify --stage requirement` を実行する。
  - 期待結果: valid `assurance.json` が生成され、Profile、Complexity Tier、reason codes、policy version、stage、source binding、`lite_candidate`、`lite_authorized` が machine-readable に保存される。
  - 観測点: CLI JSON output、tracked `assurance.json`、unit / CLI runtime tests。

- AC-002: Deterministic classification
  - アクター: Test runner。
  - 前提: 同じ canonical input、policy version、classification stage を使用する。
  - 操作: classification を複数回実行する。
  - 期待結果: byte-identical な JSON representation が生成される。
  - 観測点: deterministic serialization test。

- AC-003: Lite safety
  - アクター: Test runner。
  - 前提: Lite eligibility predicate のいずれかが false または unknown、hard trigger が存在する、または全 predicate が true でも explicit opt-in / evidence gate が未成立である。
  - 操作: classification を実行する。
  - 期待結果: `lite_candidate` は記録されてもよいが、`authorized_profile` は `lite` にならず、`lite_authorized` は false になる。この Issue では all-positive predicate だけで Lite authorization を成立させない。
  - 観測点: three-valued predicate tests、hard-trigger matrix tests。

- AC-004: Strict legacy detection
  - アクター: SpecDock runtime user。
  - 前提: 対象 Issue に `assurance.json` が存在しない。
  - 操作: `spec-dock assurance show` または `spec-dock assurance verify` を実行する。
  - 期待結果: 対象 Issue は strict-legacy candidate として検出され、既存 workflow を壊さずに継続可能な状態として表示される。
  - 観測点: CLI runtime tests、text / JSON output。

- AC-005: Schema validation
  - アクター: SpecDock runtime user / Test runner。
  - 前提: valid / invalid な `assurance.json` fixture がある。
  - 操作: `spec-dock assurance verify` を実行する。
  - 期待結果: valid contract は pass、invalid contract は理由付き fail になり、unknown / missing は strict-legacy と invalid schema を区別する。
  - 観測点: schema validation unit tests、CLI exit code。

- AC-006: Layer boundary
  - アクター: Developer / Test runner。
  - 前提: 新規 domain / application / infra / command / presentation modules が追加される。
  - 操作: focused tests、`make lint`、必要に応じて `uv run pytest` lane を実行する。
  - 期待結果: Domain は filesystem / GitHub / CLI に依存せず、Ruff / MyPy baseline を悪化させない。
  - 観測点: import inspection、unit tests、lint output。

## 例外・エッジケース

- EC-001: Lite predicate unknown
  - 条件: Lite eligibility に必要な fact が未抽出または unknown。
  - 期待: `lite_authorized=false`、authorized profile は少なくとも `standard`。
  - 観測点: classification matrix test。

- EC-001b: Lite predicates all true without opt-in
  - 条件: Lite eligibility predicate が全て true だが、explicit opt-in と evidence gate が未成立。
  - 期待: `lite_candidate=true` は許容するが、`lite_authorized=false`、authorized profile は少なくとも `standard`。
  - 観測点: classification matrix test。

- EC-002: Hard trigger present
  - 条件: migration、security/privacy、public contract、rollback difficulty などの hard trigger が検出される。
  - 期待: Profile は hard trigger に応じて `strict` または `critical` へ単調 escalation し、Lite / Standard override を許可しない。
  - 観測点: hard trigger unit tests。

- EC-003: Missing contract
  - 条件: Existing Issue に `assurance.json` がない。
  - 期待: strict-legacy candidate として表示され、invalid JSON とは区別される。
  - 観測点: `assurance show` / `verify` tests。

- EC-004: Invalid contract JSON
  - 条件: `assurance.json` が parse 不能または required field 欠落。
  - 期待: verify は fail し、classification の再実行または修正が必要なことを表示する。
  - 観測点: invalid fixture tests。

## 入力→出力例

- EX-001:
  - 入力: `spec-dock assurance classify --stage requirement --issue iss-00227`
  - 出力: `authorized_profile: "standard"`、`complexity_tier: "normal"`、`lite_candidate: false`、`lite_authorized: false`、`status: "provisional"` を含む deterministic JSON。

- EX-002:
  - 入力: `spec-dock assurance show --issue iss-legacy-without-contract --format json`
  - 出力: `mode: "strict-legacy"`、`has_contract: false`、`authorized_profile: "strict"` 相当の compatibility 表示。

## 用語（ドメイン語彙）

- Assurance Contract:
  - Issue-local tracked `assurance.json`。Profile、Complexity、source binding、obligation、policy version、status を保持する。
- Assurance Profile:
  - Workflow obligation の強度。`lite / standard / strict / critical`。
- Complexity Tier:
  - Reasoning / specialist routing の複雑度。`routine / normal / complex / deep`。
- `lite_candidate`:
  - Shadow measurement 用の Lite 候補。obligation reduction authority は持たない。
- `lite_authorized`:
  - Evidence-gated / opt-in 後に obligation reduction に使える Lite authorization。この Issue では automatic default としては使わない。
- strict-legacy:
  - `assurance.json` を持たない既存 Issue を壊さず従来の Strict 相当 workflow で扱う compatibility mode。
- Source Binding:
  - Classification が参照した canonical artifact と hash を表す binding。後続 Issue で stale detection を拡張する。

## 未確定事項

- なし。
