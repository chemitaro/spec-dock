---
種別: interview
ID: "20260707t161305z-interview"
タイトル: "Offline authoring mode and relay PR delivery policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295"]
関連: []
scope: "epic"
scope_id: "epic-00295"
created_at: "2026-07-07T16:13:05Z"
created_by: "codex"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "user clarification on 2026-07-08"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md#Evidence Adoption Ledger EAL-009"
---

# Offline authoring mode and relay PR delivery policy

## 正式質問として扱う理由

影響する artifact:

- `requirement.md`:
  - GitHub sync preflight の例外 mode。
  - Epic delivery policy。
- `design.md`:
  - evidence mode taxonomy。
  - issue relay and final PR delivery flow。
- `plan.md`:
  - final quality gate / PR delivery Issue candidate。
  - intermediate Issue no-per-Issue-PR policy。
- `report.md`:
  - Evidence Adoption Ledger。

chat 上の軽微な一問では足りない理由:

- repo-aware ChatGPT invocation の安全性と、Epic execution / PR delivery の標準形を決める high-impact workflow decision であるため。

## 質問の目的

対象者:

- SpecDock maintainer / user。

何を明確にする質問か:

- GitHub sync preflight が失敗したときにも ChatGPT authoring を許容する mode が必要か。
- Epic に複数 Issue が属する場合、PR delivery をどの Issue が担うか。

回答が後続判断へ与える影響:

- `authoring preflight github-sync` の block-first 例外設計。
- `spec-dock-epic-execution` / plan docs における issue relay policy。
- final quality gate Issue の必須化。

## ユーザー回答

answer capture:

- `-f` / `--force` は安易すぎて乱用されそうなので避ける。
- さまざまな事情で GitHub と同期を取れない可能性がある。
- 同期がなくても、差分ファイルを十分に提供すれば ChatGPT にタスクを任せられる。
- そのため、同期なしでも実行を許容する明示 mode を用意してよい。
- Epic に属する複数 Issue は、各 Issue で PR を作らない。
- Issue 完了後、次の Issue を start / planning / execution し、リレーのバトンのように順番に全 Issue を進める。
- 最後の Issue は Epic 単位の品質ゲート、手動テスト、レビュー指摘修正、mergeable PR delivery を担う。
- この relay + final delivery Issue style は今回の Epic でも採用し、今後の workflow style としても採用する。

回答日時:

- 2026-07-08

## 採用判断

adoption_status:

- adopted

adoption target:

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md` Evidence Adoption Ledger

採用理由:

- sync-required repo-aware mode と、local-only / diff-attached mode は authority と adoption risk が異なるため、mode と provenance を分ければ両立できる。
- Epic execution skill には final quality Issue へ PR delivery を defer する考え方が既にあり、今回の方針はそれを標準化するもの。

## requirement / design / plan への含意

`requirement.md`:

- `github-synced` mode を default とし、`local-context` mode を explicit opt-in とする。
- `local-context` mode は synced repo evidence ではなく、provided files / diff bundle evidence として扱う。
- Epic delivery policy と final quality gate Issue を必須化する。

`design.md`:

- Evidence mode taxonomy を追加する。
- `local-context` mode の provenance / adoption limitation / validation expectations を定義する。
- relay execution and final PR delivery sequence を追加する。

`plan.md`:

- Issue slicing policy に no per-Issue PR / relay execution / final delivery Issue mandatory を追加する。
- C12 を final quality gate and PR delivery Issue として明確化する。

`ADR`:

- 現時点では不要。後続で workflow 全体の durable decision として固定する場合のみ ADR 化する。
