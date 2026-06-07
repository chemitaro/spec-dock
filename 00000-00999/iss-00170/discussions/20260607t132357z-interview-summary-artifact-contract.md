---
種別: interview
ID: "20260607t132357z-interview"
タイトル: "Summary artifact contract for github-pr-observation"
状態: "answered"
作成者: "orchestrator"
最終更新: "2026-06-07"
親: ["iss-00170"]
関連:
  - "20260607t085456z-adr"
  - "20260607t124933z-research"
scope: "issue"
scope_id: "iss-00170"
created_at: "2026-06-07T13:23:57Z"
created_by: "orchestrator"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md"
  - "spec-dock/active/issue/discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md"
reflected_to:
  - "spec-dock/active/issue/design.md"
---

# 20260607t132357z-interview Summary artifact contract for github-pr-observation

## 位置づけ

- 用途:
  - `pr-monitor` sub-agent を完全廃止し、`github-pr-observation` skill / scripts を正規入口にする設計において、人間向け要約 artifact の契約を確定する。
- authority default:
  - `proposed`
- この artifact は、ユーザー回答を受けて `requirement.md` / `design.md` / `plan.md` / `report.md` へ採用するための質問証跡である。

## 正式質問として扱う理由 (必須)

- 影響する artifact:
  - `requirement.md`:
    - observation artifacts の必須範囲と受け入れ条件が変わる。
  - `design.md`:
    - `summary.md` の artifact contract、wait path / snapshot path の出力契約、caller の要約責務が変わる。
  - `plan.md`:
    - 実装ステップ、テスト、fixture、artifact assertion が変わる。
  - ADR:
    - `pr-monitor` 廃止後の human-friendly summary をどこに置くかという補助判断に関係する。
- chat 上の軽微な一問では足りない理由:
  - `pr-monitor` 廃止により、人間向け要約の owner が sub-agent から script artifact / caller contract へ移る。
  - 回答次第で output schema、tests、workflow skill docs、report adoption evidence が変わる。

## 質問の目的 (必須)

- 対象者:
  - ユーザー / issue owner。
- 何を明確にする質問か:
  - `github-pr-observation` が `summary.md` をどの path で必須生成するべきか。
- 回答が後続判断へ与える影響:
  - wait path の artifact contract を強くするか、caller 側要約に寄せるかが決まる。
  - snapshot path を軽量な machine-readable output に留めるか、人間向け summary まで含めるかが決まる。

## 質問 (必須)

- pressure-test question:
  - `pr-monitor` を完全廃止した後、人間向けの安定した要約は script artifact として常に残すべきか、それとも caller の自然言語要約に委ねるべきか。
- 質問:
  - `summary.md` artifact は、`wait_pr_observation.sh` では必須生成、`fetch_pr_observation_snapshot.sh` では任意生成、という設計で確定してよいですか？
- 回答してほしいこと:
  - はい / いいえ。
  - いいえの場合、どの path で必須または任意にしたいか。

## source-grounded context (必須)

- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/discussions/20260607t085456z-adr-script-driven-pr-stable-observation-boundary.md`
  - `spec-dock/active/issue/discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md`
  - `spec-dock/docs/workflow_clarification.md`
- local context で解決できたこと:
  - `review request comment requester` は本 issue の scope 外であり、必要時に別 issue 化する判断で足りる。
  - `pr-monitor` は完全廃止し、deprecated shim は残さない。
  - final decision authority は stdout final JSON / `result.json` である。
  - progress は non-authoritative である。
- まだ人間判断が必要な理由:
  - `summary.md` を必須 artifact にすると実装・テスト obligations が増える。
  - 任意 artifact にすると軽量だが、`pr-monitor` 廃止後の human-friendly reporting が caller ごとに揺れる可能性がある。

## 回答案 (必須)

- Option A:
  - `wait_pr_observation.sh` では `summary.md` を必須生成し、`fetch_pr_observation_snapshot.sh` では任意生成にする。
- Option B:
  - wait path / snapshot path の両方で `summary.md` を必須生成する。
- Option C:
  - `summary.md` は生成せず、final JSON の `summary` field と caller 側要約だけにする。

## Codex の分析 (必須)

- 判断軸:
  - `pr-monitor` 廃止後の human-friendly reporting の安定性。
  - artifact contract の重さ。
  - snapshot path の軽量性。
  - tests / fixtures の増加量。
- tradeoff:
  - Option A は wait path の人間向け evidence を安定させつつ、snapshot path の軽さを維持できる。
  - Option B は最も一貫するが、軽い現状確認でも summary generation が必須になり過剰になりやすい。
  - Option C は最も軽いが、sub-agent 廃止後の人間向け report が caller behavior に寄りやすい。
- リスク:
  - summary artifact が final JSON authority と矛盾するリスク。
  - summary.md 生成ロジックと final JSON の drift。
  - summary.md の文量が大きくなりすぎるリスク。
- 具体シナリオ / edge case:
  - 長時間 wait 後に timeout した場合、`summary.md` があれば人間が `result.json` を開かずに状況を把握できる。
  - snapshot は「今どうなっているか」の軽量確認なので、常に Markdown 要約まで生成すると過剰な場合がある。

## Codex の推奨案 (必須)

- 推奨:
  - Option A。
- 理由:
  - `pr-monitor` 廃止後の human-friendly summary を wait path では安定して残せる。
  - snapshot path は automation / debug 用の軽量 entrypoint として保てる。
  - final JSON / `result.json` authority と summary artifact を分離しやすい。
- 未回答時の影響:
  - `design.md` の Q-002 が残り、artifact contract と tests を確定できない。

## ユーザー回答 (回答後に必須)

- answer capture:
  - ユーザーは、`summary.md` をファイルとして生成する必要性に疑問を提示した。
  - ファイル生成ではなく、script の実行結果を JSON として、script を実行した agent / caller が受け取る方がよい、という判断を示した。
- 回答:
  - `summary.md` は生成しない。
  - 人間向け要約は stdout final JSON / `result.json` 内の `summary` / `recommended_next_action` / `limitations` / `artifacts` などとして返し、caller がそれを受け取って必要な報告を行う。
- 回答日時:
  - 2026-06-07

## 追加確認の要否 (回答後に必須)

- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)

- adoption_status:
  - adopted
- adoption target:
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - `pr-monitor` を完全廃止する設計では、別 Markdown artifact を増やすより、final JSON を唯一の machine-readable authority として caller が受け取る方が単純である。
  - `summary.md` を生成すると final JSON との drift や追加テスト obligation が増える。
  - human-friendly reporting は final JSON の要約フィールドと caller 側の報告で実現する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)

- `requirement.md`:
  - 必要に応じて artifact contract から `summary.md` を除外し、final JSON 内の要約フィールドを authority とする。
- `design.md`:
  - 未確定事項 Q-002 を解消する。
  - Output artifacts から `summary.md` を除外する。
  - Final JSON schema に人間向け要約に必要な fields を残す。
  - Test strategy から `summary.md` creation assertion を削除する。
- `plan.md`:
  - 実装計画再生成時に `summary.md` artifact tests は含めない。
  - final JSON summary fields の schema / rendering tests を含める。
- `ADR`:
  - 既存 ADR の主判断は変えない。
  - 必要なら output artifact scope から `summary.md` を除外する。
- reflected_to 更新方針:
  - `design.md` へ反映済み。
- adoption reflection:
  - `report.md` へ採用証跡を残す。
