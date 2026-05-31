---
種別: interview
ID: "20260531t133616z-interview"
タイトル: "Uninstall removal boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00147"
created_at: "2026-05-31THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t133616z-interview Uninstall removal boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - 削除対象、残す対象、受け入れ条件、禁止事項が変わる。
  - `design.md`:
    - managed asset inventory に基づく削除範囲、confirmation、dry-run、archive / preserve 方針が変わる。
  - `plan.md`:
    - tests、manual verification、rollback guidance、step 分割が変わる。
  - `ADR`:
    - 現時点では不要。仕様履歴を保存する長期ポリシーを別 product contract にする場合のみ候補にする。
- chat 上の軽微な一問では足りない理由:
  - `spec-dock/initiatives/**` は開発中の仕様履歴そのものであり、削除するか残すかは irreversible data loss と product handoff の両方に関わるため。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - repo-local uninstall の削除対象に、SpecDock の仕様履歴 workspace (`spec-dock/initiatives/**`) を含めるかどうかを確定する。
- 回答が後続判断へ与える影響:
  - command のデフォルト挙動、`--include-specs` / `--keep-specs` のような option 要否、confirmation wording、tests、docs warning が変わる。

## 質問 (必須)
- 質問:
  - repo-local uninstall は、`spec-dock/initiatives/**` にある仕様履歴も削除対象に含めますか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があれば「標準で消すもの」「明示 flag でだけ消すもの」「常に残すもの」を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260531t133315z-interview-uninstall-command-scope.md`: primary goal は Option A の repo-local uninstall として user-approved。
  - `src/spec_dock/cli.py`: `init` / `update` は managed scaffold と install_root assets を target repo に同期し、`spec-dock/initiatives/**` は persistent user/product data として扱うコメントがある。
  - `spec-dock/active/epic/requirement.md`: delete 操作は destructive guardrail を持ち、silent / implicit に実行しないことを要求している。
  - `spec-dock/active/epic/design.md`: local delete は local directory removal を伴う destructive operation として扱う。
- local context で解決できたこと:
  - 開発用 agent/tooling noise を消す目的は確定した。
  - ただし `spec-dock/` 配下には agent/tooling だけでなく、仕様履歴、active/generated state、docs/templates/scripts が混在している。
- まだ人間判断が必要な理由:
  - 開発完了後の product repo に仕様履歴を残したいか、プロダクトから完全に SpecDock の痕跡を消したいかは product policy の判断であり、コードからは決められない。

## 回答案 (必須)
- Option A:
  - keep specs by default: uninstall は開発用 agent/tooling と runtime/scaffold を取り除くが、`spec-dock/initiatives/**` の仕様履歴は標準では残す。仕様履歴削除は別 flag / 別 command / 手動案内にする。
- Option B:
  - remove all by default: uninstall は `spec-dock/` workspace 全体と managed agent/tooling assets を標準で削除し、仕様履歴も含めて repo から取り除く。
- Option C:
  - dry-run first with explicit mode: 標準実行は dry-run / plan 表示にし、実削除時に `--keep-specs` または `--remove-specs` の明示選択を必須にする。

## Codex の分析 (必須)
- 判断軸:
  - data loss risk、開発完了後の product cleanliness、agent/tooling noise の除去、仕様履歴の監査価値、CLI UX の単純さ。
- tradeoff:
  - Option A は仕様履歴を守りやすいが、repo に `spec-dock/initiatives/**` が残るため「完全に消えた」感は弱い。
  - Option B は product repo を最もきれいにできるが、仕様履歴の irreversible deletion になる。
  - Option C は安全だが、初回 UX が少し重くなる。
- リスク:
  - Option B を default にすると、確認不足で仕様履歴を失うリスクが高い。
  - Option A でも `spec-dock/` のうち何を残すかが曖昧だと、中途半端な broken workspace が残る可能性がある。
- 具体シナリオ / edge case:
  - 開発完了後も将来の仕様参照や監査のために `spec-dock/initiatives/**` を残したい repo。
  - second brain / LLM wiki のように `.agents/`, `.codex/`, `.github/agents/`, `.agents/skills/` から開発用 agent を消したいが、spec docs は archive として残してよい repo。
  - OSS 配布前に SpecDock の痕跡を repo から完全に消したい repo。

## Codex の推奨案 (必須)
- 推奨:
  - Option C、または Option A を default にして仕様履歴削除だけは明示 flag にする。
- 理由:
  - ユーザー意図の中心は agent/skill noise の除去であり、仕様履歴削除までは明示されていない。
  - `spec-dock/initiatives/**` は product development history なので、default destructive deletion は避ける方が安全。
- 未回答時の影響:
  - requirement の削除対象と禁止事項を固定できず、design / plan に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option C を採用する。
  - `uninstall` は標準で dry-run / plan 表示を行い、実削除時は `--keep-specs` または `--remove-specs` のように仕様履歴を残すか削除するかの明示選択を必須にする。
  - 一度 uninstall した後でも、開発再開や機能追加のために再び install する可能性がある。その場合、これまでの仕様書群が失われていると再開が困難になる。
  - 一方で、使い捨ての tool や今後の機能追加を想定しない repo では、仕様履歴も削除してしまった方がよい場合がある。
  - 主目的は、agent / skill など、エージェント稼働時にノイズになる開発用 tooling を取り除くことである。
  - そのため、仕様履歴の扱いは選択可能にし、かつ実削除時の選択を必須にする。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - repo-local uninstall で、managed agent/tooling assets のうち user edit が入りうる bootstrap-only / user-owned files をどう扱うか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、仕様履歴の扱いは command 実行時に明示選択させる方針で確定した。
  - 開発再開可能性がある repo では specs preservation が必要であり、使い捨て repo では specs removal が有用であるため、default implicit deletion / preservation のどちらにも寄せない。
  - uninstall の primary objective は開発用 agent/skill noise の除去であり、仕様履歴削除は選択可能な secondary destructive scope として扱う。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - uninstall は dry-run / plan 表示を標準挙動に含める。
  - 実削除時は specs を残すか削除するかの明示 option を必須にする。
  - `--keep-specs` 系は開発再開可能性を維持する path、`--remove-specs` 系は使い捨て repo / 完全 cleanup path として扱う。
  - agent / skill noise removal は primary objective、spec history removal は explicit user choice として分離する。
- `design.md`:
  - dry-run plan、confirmation、`keep-specs` / `remove-specs` mode、削除対象 inventory、rollback / reinstall guidance を設計対象にする。
  - specs preservation mode では broken workspace を残さないため、残す specs と取り除く runtime/tooling/scaffold の境界を明確にする。
- `plan.md`:
  - dry-run / explicit mode validation / keep-specs removal / remove-specs removal / reinstall-resume scenario を step と test obligation に含める。
- `ADR`:
  - 現時点では不要。uninstall mode が将来の product lifecycle policy へ広がる場合のみ検討する。
- reflected_to 更新方針:
  - requirement authoring 時に `requirement.md` と `report.md` の Evidence Adoption Ledger / Spec Authoring Gate へ反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
