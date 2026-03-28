---
種別: 要件定義書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-28"
親: ["epic-00033", "init-local-00003"]
---

# iss-00036 Timestamp Based Discussion and ADR Naming — 要件定義（WHAT / WHY）

## 目的
- `discussions/` 配下の discussion docs（`adr / disc / research / note`）を timestamp-prefix naming へ切り替え、連番衝突を避けられる naming contract を固定する。
- `new doc`、validation、ADR 集約の scan 前提のあいだで、同一 grammar と collision domain を共有できる状態にする。

## 背景・現状
- 現状の挙動:
  - `new doc` は `adr / disc / research / note` の 4 種を `discussions/` 配下へ生成するが、filename contract は `NNN-type-slug.md` の連番前提になっている。
  - 現行 docs / tests / validate も同じ sequential naming を前提にしている。
- 現状の課題:
  - sequential naming は worktree / branch / merge を跨ぐと duplicate sequence を防げず、merge 後に衝突しうる。
  - `adr / disc` だけ別 contract、`research / note` は旧 contract のまま、のような split を残すと `new doc` family の整合が崩れる。
  - naming grammar が未固定だと `new doc`、validate、後続 issue の ADR 集約 scan の契約がずれる。
- 再現手順:
  1. 複数環境で `discussions/` 配下の docs を連番採番すると、別 branch / worktree で同じ番号が並行に発生しうる。
  2. その状態で merge すると、同一 scope の `NNN-*` が衝突しうる。
  3. grammar 未固定のまま validation や後続 issue の ADR 集約 scan を実装すると対象判定がぶれる。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock new doc adr`
    - `./spec-dock/scripts/spec-dock new doc disc`
    - `./spec-dock/scripts/spec-dock new doc research`
    - `./spec-dock/scripts/spec-dock new doc note`
  - Filesystem:
    - generated filename
  - Validation:
    - naming / scan contract
- 情報源:
  - `epic-00033` requirement / design / plan
  - `epic-00033/discussions/001-adr-adr-symlink-mirror-without-index.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `discussions/` 配下へ ADR / discussion / research / note を追加する maintainer
- 代表シナリオ:
  - `new doc adr|disc|research|note` で conflict-resistant な filename を自動生成する。
  - 同じ scope で同秒に複数 doc を作成しても、create lock により create critical section 内で直列化されたうえで、type を問わず deterministic に suffix が付く。
  - 既存の pre-contract sequential docs はそのまま残し、新規生成だけを timestamp contract に切り替える。

## スコープ
- MUST:
  - `discussions/` 配下で `new doc` が生成する 4 種 (`adr / disc / research / note`) の basename grammar を timestamp-prefix に統一する。
  - basename grammar を standard form `<ts>-<kind>-<slug>.md`、collision form `<ts>-<nn>-<kind>-<slug>.md` に固定する。
  - `ts = yyyymmddthhmmssz`（UTC、`t` / `z` lowercase 固定）、`kind in {adr, disc, research, note}`、`nn = 01..99` とする。
  - same-second collision domain は「同一 scope / 同一 `ts` の discussion doc family 全体」とし、kind や slug が異なっても create lock により直列化された create critical section 内で 2 件目以降は最小未使用 `nn` を使うことを acceptance に入れる。
  - basename、filename stem（basename から `.md` を除いた値）、`doc_id`（slug を含まない template/output 用 identity）の役割を分離し、standard form と collision form の両方で対応を曖昧にしない。
  - 原本は引き続き各 scope の `discussions/` に配置し、`adr` だけを後続 issue の集約対象にする前提を崩さない。
  - pre-contract sequential docs を grandfathered artifact として扱い、自動 rename / migrate 対象にしない境界を明記する。
  - `new doc`、validation、後続 issue の ADR 集約 scan が共有できる grammar 境界を requirement 上で固定する。
- MUST NOT:
  - sequential naming を新規生成しない。
  - `adr / disc` と `research / note` で別の naming contract を採らない。
  - legacy docs の一括 rename / migration をこの issue の責務にしない。
- OUT OF SCOPE:
  - `sync` の top-level ADR mirror 再生成そのもの
  - GitHub mandatory node create contract
  - docs parity の全面クローズ

## 境界
- Always:
  - naming grammar は lowercase path 制約に適合する。
  - 原本の配置先は `adr / disc / research / note` を含めて常に各 scope の `discussions/` である。
  - `adr` だけが後続 issue の top-level 集約対象になりうるが、原本配置ルールは変えない。
  - same-second collision は「同一 scope / 同一 `ts` の discussion doc family 全体」を domain とし、最初の 1 件だけ suffix なし、2 件目以降は 2 桁 suffix でのみ吸収する。
  - truly parallel な create invocation も同一 scope の create lock 取得後に suffix 選択へ進むため、parallel-safe の意味は「lock による直列化後に deterministic allocation される」である。
  - filename stem は basename から `.md` を除いた値であり slug を保持する。`doc_id` は `<ts>-<kind>` または `<ts>-<nn>-<kind>` の slugless identity である。
  - pre-contract sequential docs は grandfathered artifact として保持し、新規 timestamp contract と混同しない。
  - validation では filename を 4 つに分ける: valid timestamp name は新 contract として検査、legacy sequential name は grandfathered、timestamp/discussion-doc intent を持つ malformed name は explicit error、`rules.md` のような unrelated file は ignore。
- Ask:
  - timestamp 精度を秒より細かくする判断は行わない。
- Never:
  - pre-contract legacy docs を自動 rename する。
  - grammar 未固定のまま validate / ADR 集約 scan 前提を増やす。

## 非交渉制約
- UTC ベースの grammar を崩さない。
- `t` / `z` は lowercase 固定とする。
- naming contract は `new doc` / validate / ADR 集約 scan と整合していなければならない。
- `discussions/` を原本の唯一の配置先とする運用を崩さない。

## 前提
- `iss-00034` の create contract が先行している。
- `new doc` の対象は issue / epic / initiative scope の `discussions/` である。
- `new doc` の現行 surface は `adr / disc / research / note` の 4 種であり、本 issue ではこの family を split しない。
- epic spec で grandfathered legacy docs の扱いと ADR mirror only 方針が確定している。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `new doc adr|disc|research|note` を実行する
  - When:
    - 新しい discussion doc を作成する
  - Then:
    - basename は `<ts>-<kind>-<slug>.md` grammar で生成される
    - filename stem は `<ts>-<kind>-<slug>` であり、`doc_id` は `<ts>-<kind>` である
    - `kind` は `adr / disc / research / note` のいずれでも同一 contract を使う
    - 生成先は常に対象 scope の `discussions/` である
  - 観測点:
    - naming tests
    - generated file assertions
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - same-second collision が発生する
  - When:
    - 同じ秒に複数 doc を作成する
  - Then:
    - collision domain は同一 scope / 同一 `ts` の discussion doc family 全体である
    - その秒の 1 件目だけ `yyyymmddthhmmssz-<kind>-<slug>.md` を使い、2 件目以降は `yyyymmddthhmmssz-<nn>-<kind>-<slug>.md` の 2 桁 suffix が付与される
    - suffix 採番は kind ごとの basename 衝突判定ではなく、同一 scope の create lock で直列化された domain 全体から最小未使用 `nn` を選ぶ deterministic rule で行われる
    - collision form の filename stem は `<ts>-<nn>-<kind>-<slug>`、`doc_id` は `<ts>-<nn>-<kind>` となり、standard form と衝突しない
  - 観測点:
    - collision tests
    - suffix evidence
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - pre-contract sequential docs（例: `001-adr...` / `002-disc...` / `003-research...` / `004-note...`）が存在する
  - When:
    - new naming contract と validate 前提を確認する
  - Then:
    - legacy docs は grandfathered として残り、自動 rename / migrate 対象にならない
    - 新規 timestamp contract と legacy grandfathered file を混同しない
    - valid timestamp name は新 contract で validate され、timestamp/discussion-doc intent を持つ malformed filename は validation error になる
    - `rules.md` のような unrelated nonconforming file は validation 対象外として ignore される
  - 観測点:
    - docs diff
    - validate contract tests
- AC-004:
  - Actor:
    - maintainer
  - Given:
    - `adr` docs を後続 issue で top-level 集約する前提がある
  - When:
    - naming contract を確認する
  - Then:
    - `adr` を含む全 doc type は同一 timestamp grammar を共有しつつ、原本配置は常に `discussions/` のままである
    - ADR 集約のために `adr` だけ別の原本配置や別 naming grammar を持ち込まない
  - 観測点:
    - requirement/design boundary
    - docs contract

## 例外・エッジケース
- EC-001:
  - 条件:
    - slug が長い、または複雑である
  - 期待:
    - grammar を壊さず lowercase path 制約に従う
  - 観測点:
    - filename normalization tests
- EC-002:
  - 条件:
    - timestamp grammar に似た discussion-doc intent filename や legacy file が混在して存在する
  - 期待:
    - legacy sequential は grandfathered として扱い、timestamp/discussion-doc intent を持つ malformed filename は validation error、unrelated file は ignore として分類を混同しない
  - 観測点:
    - validate behavior tests
- EC-003:
  - 条件:
    - 同じ scope / 同じ秒に複数 type の doc が並行生成される
  - 期待:
    - suffix 付与で衝突を吸収し、type ごとの独立採番や basename 単体比較へのフォールバックをしない
  - 観測点:
    - cross-type collision tests
- EC-004:
  - 条件:
    - 同じ scope / 同じ秒で collision suffix `01..99` を使い切る
  - 期待:
    - silent fallback や sequential fallback は行わず、explicit failure として停止する
  - 観測点:
    - suffix exhaustion tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock new doc adr --issue iss-00036 --title "Example Decision"`
  - Output:
    - `yyyymmddthhmmssz-adr-example-decision.md` または同秒時 `yyyymmddthhmmssz-01-adr-example-decision.md`
- EX-002:
  - Input:
    - `./spec-dock/scripts/spec-dock new doc note --issue iss-00036 --title "Kickoff Memo"`
  - Output:
    - `yyyymmddthhmmssz-note-kickoff-memo.md` または同秒時 `yyyymmddthhmmssz-01-note-kickoff-memo.md`

## 用語（ドメイン語彙）
- TERM-001:
  - timestamp-prefix naming:
    - UTC timestamp を basename 先頭に持つ discussion doc filename contract
- TERM-002:
  - grandfathered planning artifact:
    - 新 contract 移行前に作られた legacy doc で、自動 rename 対象にしないもの
- TERM-003:
  - discussion doc family:
    - `discussions/` 配下に置かれる `adr / disc / research / note` の原本群
- TERM-004:
  - ADR aggregation target:
    - 原本は `discussions/` に置いたまま、後続 issue で top-level mirror 集約の対象として探索される `adr` docs
- TERM-005:
  - collision form:
    - `<ts>-<nn>-<kind>-<slug>.md` の suffix 付き basename で表現される same-second collision 吸収形
- TERM-006:
  - filename stem:
    - basename から `.md` を除いた値。slug を含み、`<ts>-<kind>-<slug>` または `<ts>-<nn>-<kind>-<slug>` を採る
- TERM-007:
  - doc_id:
    - template / output へ埋め込む slugless identity。`<ts>-<kind>` または `<ts>-<nn>-<kind>` を採り、filename stem と同一視しない

## 未確定事項
- なし:
  - discussion doc family 全体を timestamp-prefix naming に統一する方針は確定済み
