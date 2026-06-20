---
種別: interview
ID: "20260620t144016z-interview"
タイトル: "Checks Named Compatibility Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
scope: "issue"
scope_id: "iss-00222"
created_at: "2026-06-20T14:40:16Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "discussions/20260620t141320z-disc-actions-only-collector-design.md"
  - "discussions/20260620t141317z-disc-observation-semantics-and-losses.md"
  - "discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md Evidence Adoption Ledger"
---

# 20260620t144016z-interview Checks Named Compatibility Boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - public compatibility / non-scope / acceptance criteria の書き方が変わる。
  - `design.md`:
    - 旧 `checks` named surface を残すか、rename/remove するかで file/API/JSON compatibility 方針が変わる。
  - `plan.md`:
    - migration tests、static scan、deprecation tests、breaking-change tests の義務が変わる。
  - `ADR`:
    - 既存 ADR の Decision は forbidden API surface を固定済み。必要なら Consequences/Follow-ups の反映時に compatibility 方針を参照する。
- chat 上の軽微な一問では足りない理由:
  - 回答により実装 blast radius と downstream compatibility が分岐し、複数 canonical artifact に反映する必要がある。

## 質問の目的 (必須)
- 対象者:
  - ユーザー / product owner
- 何を明確にする質問か:
  - Checks API を使わないことに加え、`checks` という名前を含む既存 public script / JSON fields / wording を互換維持するか、破壊的に整理するか。
- 回答が後続判断へ与える影響:
  - `fetch_pr_checks_snapshot.sh` の扱い、payload の旧 `ci.check_runs` / `ci.commit_statuses` / `required_check_state` 等の扱い、docs/skill wording、tests の migration strategy が決まる。

## 質問 (必須)
- pressure-test question:
  - 「Checks API を使わない」ことは、API 呼び出し禁止だけを意味しますか。それとも `checks` という名前を含む既存 public surface も可能な限り消すべきですか。
- 質問:
  - 既存の `checks` named compatibility surface は残しますか、それとも破壊的に整理しますか。
- 回答してほしいこと:
  - Option A / B / C のどれに近いかを回答してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260620t143349z-adr-forbid-checks-api-in-pr-observation.md`: forbidden surface は API/CLI/GraphQL surface として固定済み。
  - `20260620t141320z-disc-actions-only-collector-design.md`: public entrypoint 維持案を推奨しつつ、旧 JSON fields の扱いは design へ deferred。
  - provider-side current scripts: `fetch_pr_checks_snapshot.sh`, `pr_observation_checks.py`, `pr_observation_wait.py`。
  - current tests: 旧 `check-runs` / `status` / `statusCheckRollup` 前提の fixtures が多数存在。
- local context で解決できたこと:
  - Forbidden API を呼ばずに PR observation を Actions-only へ変えることは可能。
  - Review/comment/thread 監視は Checks API と別経路なので維持可能。
  - 既存 public entrypoint を残しても、内部で forbidden API を呼ばなければ技術的には ADR に反しない。
- まだ人間判断が必要な理由:
  - 互換性を優先するか、名称・payload の明快さを優先するかは product/workflow expectation の判断であり、実装者が勝手に決めると downstream 利用者への破壊度が変わる。

## 回答案 (必須)
- Option A: 互換維持を優先する
  - 既存 public script 名や主要 JSON field は残す。
  - ただし値は empty/deprecated/`collection_policy: "forbidden"` 等にし、CI 判定には使わない。
  - docs で “historical name; Actions-only now” と明記する。
- Option B: 明快さを優先して破壊的に整理する
  - `checks` named script / JSON fields / wording を rename/remove する。
  - downstream 破壊を許容し、migration note と breaking tests を書く。
- Option C: 折衷
  - public script 名は互換維持するが、JSON fields は新 payload へ寄せる。
  - または 1 release / 1 issue のみ deprecated alias を残し、follow-up で削除する。

## Codex の分析 (必須)
- 判断軸:
  - blast radius、downstream compatibility、forbidden API 回帰リスク、ユーザーにとっての語彙の明快さ、実装・テスト量。
- tradeoff:
  - Option A は安全で小さいが、`checks` という名前が残るため誤解を生みやすい。
  - Option B は意味がきれいだが、script caller / tests / docs の破壊が大きい。
  - Option C は段階移行に向くが、短期的には二重 surface が残る。
- リスク:
  - 互換 surface を残す場合、将来の実装者が旧 `check-runs` fallback を戻しやすい。
  - 破壊的整理を行う場合、既存 workflow / skill / tests / downstream scripts が壊れる可能性がある。
- 具体シナリオ / edge case:
  - `fetch_pr_checks_snapshot.sh` という名前が残っているのに Actions-only payload を返す。
  - `ci.check_runs=[]` が残ることで「Checks API を読んだ結果 0 件」と誤解される。
  - static scan が `checks` という単語を全面禁止すると、historical docs や compatibility docs まで false positive になる。

## Codex の推奨案 (必須)
- 推奨:
  - Option A 寄りの折衷。public entrypoint は残し、payload に `ci.source_policy="github_actions_only"` と `collection_policy="forbidden"` を明記する。docs/skill では historical naming と明示する。
- 理由:
  - forbidden API 排除という主目的を満たしながら、既存 workflow の破壊を最小にできる。
- 未回答時の影響:
  - design/plan で JSON compatibility と script naming を確定できず、implementation handoff の acceptance criteria が曖昧になる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - `checks` という語や既存互換名を消す言葉狩りではなく、GitHub Checks API を使わないことが目的である。
- 回答:
  - GitHub Checks API / status rollup surface を使わなければ、`checks` named compatibility surface は残してよい。
- 回答日時:
  - 2026-06-20

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md` / `design.md` / `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、禁止対象は語彙ではなく GitHub Checks API / status rollup surface の使用であることが確定した。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - forbidden surface は API 利用として書く。`checks` という名称の使用禁止は要件にしない。
- `design.md`:
  - `checks` named compatibility surface は残せるが、GitHub Checks API を呼ばない guard を置く。
- `plan.md`:
  - static scan / fake-gh tests は API endpoint / `statusCheckRollup` / `gh pr checks` 相当を対象にし、単語 `checks` の全面禁止にしない。
- `ADR`:
  - accepted ADR の Decision と整合。必要なら compatibility note として参照する。
- reflected_to 更新方針:
  - requirement/design/plan authoring に反映する。
- adoption reflection:
  - report Evidence Adoption Ledger に採用済みとして記録する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - see answer options above
- 後続 reflection proposal:
  - reflect answered option to requirement/design/plan
- 追加で作る discussion docs:
    - none unless answer introduces new durable tradeoff
