---
種別: 設計書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00036 Timestamp Based Discussion and ADR Naming — 設計（HOW）

## 目的・制約
- 目的:
  - `discussions/` 配下の discussion doc family（`adr / disc / research / note`）を shared sequential naming から timestamp-prefix naming へ置き換える。
  - `new doc` / validate / 後続 issue の ADR scan が同じ filename grammar を共有できるようにする。
  - pre-contract sequential docs を grandfathered artifact として保持しつつ、新規生成 contract を deterministic にする。
- MUST / MUST NOT:
  - MUST:
    - 新規生成 basename を `<ts>-<kind>-<slug>.md` に統一する。
    - `ts` は UTC `yyyymmddthhmmssz`、`kind` は `adr|disc|research|note`、同秒衝突時のみ `-<nn>-` を許可する。
    - 生成先は全 type で各 scope の `discussions/` を維持する。
    - validate は timestamp grammar を基準に新規 contract の collision / malformed naming を検出する。
  - MUST NOT:
    - 新規生成で `NNN-type-slug.md` を使わない。
    - `adr / disc` と `research / note` を別 naming family に分断しない。
    - grandfathered sequential docs を自動 rename しない。
- 非交渉制約:
  - `src/spec_dock/assets/spec_dock/...` を source of truth とし、provider 側実装を先に変更する。
  - 原本配置は全 type で `discussions/` に固定し、ADR 集約のために `adr` だけ別の原本パスを持たせない。
  - timestamp は UTC 秒精度で固定し、ミリ秒やローカルタイムへ拡張しない。
  - `t` / `z` は lowercase 固定とする。
- 前提:
  - `iss-00034` の GitHub mandatory node creation contract は先行済みである。
  - epic/initiative で single repo / ADR mirror only / rebuildable workspace 方針は固定済みである。
  - `research / note` も discussion doc family に含めて timestamp-prefix naming へ統一する、という利用者判断が確定している。

## 既存実装 / 規約の理解
- 参照した実装 / docs:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
- 現状理解:
  - 現在の `new doc` CLI surface は `adr / disc / research / note` の 4 type を正式サポートしている。
  - `application/create_node.py` は `_DISCUSSION_DOC_FILENAME_RE` と `_next_discussion_doc_seq()` により `NNN-type-slug.md` の shared sequence を採番している。
  - `domain/validation.py` も同じ sequential regex を使って duplicate sequence を検出している。
  - docs / tests も `001-adr...`, `002-disc...`, `003-research...`, `004-note...` を同一 family の expected behavior としている。
  - active issue requirement と epic requirement は timestamp-prefix grammar を要求しており、現実装と契約がずれている。
- 採用するパターン:
  - `new doc` / validate で同一の filename parser を共有する。
  - shared sequence 採番を timestamp allocation helper へ置き換え、same-second collision だけ suffix allocator で吸収する。
  - grandfathered sequential docs は「既存 artifact としては許容するが、新規生成 source には使わない」fail-closed / no-migrate パターンを採る。
- 採用しないもの:
  - `adr` だけ timestamp、他 type は連番、の split contract。
  - 既存 sequential docs の一括 rename / 自動移行。
  - 原本 path を `adrs/` などへ分岐させること。
  - DB/manifest のような別 index 追加。
- 影響範囲:
  - runtime new-doc create path
  - validation
  - naming reference docs / workflow docs / rules docs
  - runtime tests / update parity tests
  - checked-in dogfooding docs mirror

## 採用方針 / トレードオフ
- 論点:
  - timestamp contract を `adr / disc` のみに限定するか、discussion doc family 全体へ広げるか。
  - grandfathered sequential docs を validate で即エラーにするか、legacy として読み飛ばすか。
  - same-second collision を失敗にするか、suffix で吸収するか。
- 選択肢:
  - Option A:
    - `adr / disc` のみ timestamp 化し、`research / note` は旧連番のまま維持する。
  - Option B:
    - `adr / disc / research / note` の 4 type 全体を timestamp-prefix naming に統一する。
  - Option C:
    - same-second collision は fail-fast とし、利用者に再試行させる。
- 決定:
  - Option B を採用する。
  - same-second collision の扱いは suffix 吸収を採用し、Option C は採らない。
  - grandfathered sequential docs は validate 上の legacy artifact として許容し、新規 timestamp contract の collision source には含めない。
  - 理由:
    - shipped product の現行 abstraction は 4 type を同一 family として公開しており、split contract は product complexity を上げる。
    - timestamp-prefix は merge collision 回避と時系列整列を同時に満たす。
    - same-second collision を fail-fast にすると、timestamp contract 導入後も並列作業の friction が残る。

## インターフェース契約
- API / function / protocol / data boundary:
  - CLI contract:
    - `new doc <type>` の type surface は `adr|disc|research|note` のまま維持する。
    - explicit sequence override は追加しない。
  - filename contract:
    - standard basename:
      - `<ts>-<kind>-<slug>.md`
    - collision basename:
      - `<ts>-<nn>-<kind>-<slug>.md`
    - `ts = yyyymmddthhmmssz`
    - `nn = 01..99`
    - `kind in {adr, disc, research, note}`
  - allocation contract:
    - `ts` は `ports.clock.today()` ではなく現在 UTC datetime を source とする helper で生成する。
    - 同一 scope / 同一秒で standard basename が衝突したときだけ、未使用の最小 `nn` を採用する。
    - `01..99` が使い切られた場合は explicit failure にする。
    - logical doc identity は standard form では `<ts>-<kind>`、collision form では `<ts>-<nn>-<kind>` として扱い、suffix の有無を曖昧化しない。
    - basename identity は `standard form` なら `(ts, kind, slug)`、`collision form` なら `(ts, nn, kind, slug)` として扱う。
    - `doc_id` は basename から `.md` を除いた値とし、standard form では `<ts>-<kind>`、collision form では `<ts>-<nn>-<kind>` を採る。
    - template placeholder (`<ADR_ID>`, `<DISC_ID>`, `<RESEARCH_ID>`, `<NOTE_ID>`) へは新 `doc_id` をそのまま埋め込む。
  - validation contract:
    - timestamp grammar に一致する files は新 contract 対象として validate する。
    - grandfathered sequential files (`NNN-type-slug.md`) は legacy として存在を許容するが、新 contract の duplicate error source にしない。
    - nonconforming files (`rules.md` 含む) は従来どおり scan 対象外とする。
    - standard form と collision form を含めて、同一 basename identity を複数 file が占有する状態は duplicate として reject する。
  - scope/storage contract:
    - `adr / disc / research / note` の原本はすべて対象 node の `discussions/` に書き込む。
    - 後続 issue の top-level ADR mirror は `adr` files を `discussions/` から探索する前提に留め、本 issue で mirror 挙動は変更しない。

### UML（推奨: module / dependency）
```plantuml
@startuml
skinparam monochrome true
left to right direction

rectangle "commands/new.py" as cmd
rectangle "application/create_node.py" as create
rectangle "domain/validation.py" as validate
rectangle "docs/reference_naming.md" as docs
rectangle "tests/cli_runtime/test_new.py" as t1
rectangle "tests/cli_runtime/test_runtime_new_doc_s09.py" as t2
rectangle "tests/cli_runtime/test_validate.py" as t3

cmd --> create
create --> validate
docs --> cmd
t1 --> cmd
t2 --> create
t3 --> validate
@enduml
```

## クラス / インターフェース詳細設計（必要時）
- Class / Interface:
  - `CreateDiscussionDocRequest`
- responsibility:
  - doc type / scope / title / slug を受け取り、discussion doc create use-case の入力境界を固定する。
- collaboration:
  - `commands/new.py` から組み立てられ、`create_node.py::plan_discussion_doc()` へ渡される。

- Class / Interface:
  - discussion filename allocator helper（新設）
- responsibility:
  - UTC timestamp basename の生成、same-second collision suffix の割当、overflow/failure message を担当する。
- collaboration:
  - `plan_discussion_doc()` が使用し、`validation.py` の filename parser と grammar を共有する。

- Class / Interface:
  - discussion filename parser/validator helper（新設または共通化）
- responsibility:
  - standard timestamp form / collision suffix form / legacy sequential form の判別を提供する。
- collaboration:
  - `create_node.py` と `validation.py` が同一 parser を使うことで contract drift を防ぐ。

### UML（任意: class / interface）
```plantuml
@startuml
skinparam monochrome true

class CreateDiscussionDocRequest
class DiscussionTimestampAllocator
class DiscussionFilenameParser
class CreateDiscussionDocResult

CreateDiscussionDocRequest --> DiscussionTimestampAllocator
DiscussionTimestampAllocator --> DiscussionFilenameParser
DiscussionTimestampAllocator --> CreateDiscussionDocResult
@enduml
```

## 変更計画
- Add:
  - discussion timestamp allocator helper
  - same-second suffix allocation logic
  - timestamp grammar validation helpers / tests
- Modify:
  - `commands/new.py` の help / contract wording（連番前提の説明除去）
  - `application/create_node.py` の regex / plan / create result generation
  - `domain/validation.py` の discussion filename scan logic
  - `docs/reference_naming.md` と関連 workflow/rules docs
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
  - 必要に応じて `tests/test_init_update.py` の update parity evidence
- Delete:
  - new contract 上の shared sequential allocation / duplicate-sequence-only 前提
- Move/Rename:
  - なし
- Read only:
  - `spec-dock/adrs/` mirror behavior本体
  - legacy pre-contract discussion files（自動 rename しない）

## 要件 → 設計マッピング
- AC-001 -> timestamp allocator + 4 type 共通 grammar + `discussions/` write path
- AC-002 -> same-second suffix allocator (`01..99`)
- AC-003 -> legacy sequential grandfathering + validate legacy boundary
- AC-004 -> `discussions/` as SoR + ADR-only mirror scan assumptionの明文化
- EC-001 -> slug normalization / kebab-case validation
- EC-002 -> legacy/nonconforming file classification
- EC-003 -> cross-type same-second collision tests
- EC-004 -> suffix exhaustion explicit failure
- constraint -> UTC lowercase timestamp, no sequential fallback, no auto-migration

## テスト戦略
- Unit:
  - timestamp formatter
  - same-second suffix allocator
  - filename parser（timestamp standard / timestamp collision / legacy sequential / nonconforming）
  - suffix exhaustion failure
- Integration:
  - `new doc adr|disc|research|note` が timestamp-prefix basename を生成する
  - same-second collision で `-01-`, `-02-` が付く
  - suffix exhaustion で explicit failure になる
  - legacy sequential file があっても新規 timestamp allocation は連番へ引きずられない
  - `discussions/` 以外へ書かれない
  - validate が timestamp duplicate / malformed timestamp を検出する
- E2E / manual:
  - provider docs と dogfooding docs の naming reference parity
  - `active issue` 上で generated filename を目視確認
- migration / rollback / feature flag if needed:
  - feature flag は導入しない。
  - rollback は issue 単位で戻すが、`adr/disc` だけ timestamp のような split interim state は残さない。

## 要件 / 例外 -> verification mapping
- AC-001 -> `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_runtime_new_doc_s09.py`
- AC-002 -> same-second collision regression tests（CLI/application）
- AC-003 -> `tests/cli_runtime/test_validate.py` + legacy grandfathering tests
- AC-004 -> docs/spec diff + path assertions
- EC-001 -> invalid slug tests
- EC-002 -> legacy/nonconforming classification tests
- EC-003 -> cross-type same-second collision tests
- EC-004 -> suffix exhaustion tests
- constraint -> docs parity + update parity checks

## リスク / 移行 / ロールバック（必要時）
- 主リスク:
  - docs / tests / validation が現状すべて連番前提なので、変更面が比較的広い。
  - grandfathered sequential files の扱いを曖昧にすると validate と sync scan の将来契約が再度ずれる。
  - same-second collision tests は clock seam が弱いと flaky になりうる。
- 移行:
  - pre-contract sequential docs は既存 artifact として残す。
  - 新規作成だけ timestamp-prefix contract へ切り替える。
  - ADR mirror scan の本実装は `iss-00035` で扱い、本 issue では scan 前提の grammar を共有するところまでに留める。
- ロールバック:
  - issue 単位で差分を戻す。
  - 4 type の naming contract を途中で split した状態へは戻さない。

## 未確定事項
- なし:
  - issue 実装に必要な naming boundary は確定済み
