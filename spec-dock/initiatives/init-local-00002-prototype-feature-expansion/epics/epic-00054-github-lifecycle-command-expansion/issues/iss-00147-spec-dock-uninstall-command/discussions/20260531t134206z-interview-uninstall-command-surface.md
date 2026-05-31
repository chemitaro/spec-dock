---
種別: interview
ID: "20260531t134206z-interview"
タイトル: "Uninstall command surface"
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

# 20260531t134206z-interview Uninstall command surface

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
    - ユーザーが実行する command surface と受け入れ条件が変わる。
  - `design.md`:
    - installer CLI / repo-local runtime wrapper / self-deleting command の責務境界が変わる。
  - `plan.md`:
    - 実装対象ファイル、tests、manual verification が変わる。
  - `ADR`:
    - 現時点では不要。installer/runtime command ownership を広く再定義する場合のみ候補にする。
- chat 上の軽微な一問では足りない理由:
  - uninstall は repo-local runtime 自体を削除し得るため、どの executable から実行するかが安全性と再実行性に直結する。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - `uninstall` を installer CLI、repo-local runtime command、または両方に提供するかを確定する。
- 回答が後続判断へ与える影響:
  - command UX、self-delete の扱い、target path の default、tests、docs guidance が変わる。

## 質問 (必須)
- 質問:
  - `uninstall` コマンドの入口はどれにしたいですか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があれば主導線と補助導線を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `src/spec_dock/cli.py`: installer entrypoint は `spec-dock init` / `spec-dock update [path]` を持つ。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`: repo-local runtime command は installer update を wrapper として呼び出す導線を持つ。
  - `spec-dock/active/epic/requirement.md`: repo-local runtime self-update command は long-form `uvx` invocation への依存を減らす operator value として定義されている。
  - `spec-dock/active/epic/design.md`: self-update は installer update の wrapper として扱う。
  - `20260531t133315z-interview-uninstall-command-scope.md`: uninstall の primary goal は repo-local removal。
  - `20260531t133616z-interview-uninstall-removal-boundary.md`: specs handling は explicit mode selection。
  - `20260531t134004z-interview-uninstall-user-owned-asset-boundary.md`: bootstrap-only / user-owned files は content match based removal。
- local context で解決できたこと:
  - installer CLI は target repo を外から操作できるため、自分が削除される repo-local runtime に依存しない。
  - repo-local runtime command は operator にとって discoverable だが、実行中に `spec-dock/scripts/spec-dock` を削除し得る self-removal path になる。
- まだ人間判断が必要な理由:
  - product UX と安全性のどちらを主導線にするかは仕様判断であり、既存コードだけでは決められない。

## 回答案 (必須)
- Option A:
  - installer CLI only: `spec-dock uninstall [path]` を package entrypoint に追加し、repo-local runtime command は追加しない。
- Option B:
  - runtime wrapper + installer implementation: `./spec-dock/scripts/spec-dock uninstall` を operator-facing 入口にし、内部で installer `spec-dock uninstall <target>` を呼ぶ。installer CLI も直接利用可能にする。
- Option C:
  - runtime command only: repo-local `./spec-dock/scripts/spec-dock uninstall` だけを追加し、package entrypoint には追加しない。

## Codex の分析 (必須)
- 判断軸:
  - discoverability、self-delete safety、再実行性、既存 `update` との一貫性、testability。
- tradeoff:
  - Option A は安全で実装が単純だが、repo 内から `./spec-dock/scripts/spec-dock uninstall` を見つける体験はない。
  - Option B は `update` と同じ wrapper pattern にでき、operator-facing UX もよい。一方で、runtime wrapper が自分の file を削除する可能性を考慮した subprocess / ordering が必要になる。
  - Option C は discoverable だが、uninstall 後に同じ command が消えるため再実行・失敗復旧の導線が弱い。
- リスク:
  - runtime command only にすると、途中失敗後に runtime script が消えた場合の復旧案内が難しくなる。
  - installer only にすると、既存 self-update と command surface の一貫性が弱くなる。
- 具体シナリオ / edge case:
  - 開発完了時に repo 内で `./spec-dock/scripts/spec-dock uninstall --keep-specs` を実行したい。
  - uninstall 後、再開発のために `uvx --from ... spec-dock init/update .` で再導入したい。
  - uninstall が途中失敗した場合、package entrypoint `spec-dock uninstall .` で再試行したい。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - repo-local command と installer command の両方を持つと、通常利用では discoverable で、失敗復旧や再実行では外側の installer CLI を使える。
  - 既存 `update` の「repo-local wrapper が installer を呼ぶ」設計とそろう。
- 未回答時の影響:
  - requirement の command UX と design の責務境界を固定できず、plan に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
  - `./spec-dock/scripts/spec-dock uninstall` を通常の repo-local operator-facing 入口にする。
  - repo-local runtime command は installer `spec-dock uninstall <target>` を呼ぶ wrapper として扱う。
  - installer CLI `spec-dock uninstall [path]` も直接利用可能にし、uninstall 途中失敗や repo-local runtime が失われた後の再実行 / 復旧導線にする。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - current managed assets も content match based removal にするか、manifest-managed であれば差分があっても削除するか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、command surface は runtime wrapper + installer implementation の二層構成で確定した。
  - 通常利用では repo-local command として discoverable にし、失敗復旧や再実行では installer CLI から target repo を外側から操作できるようにする。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `./spec-dock/scripts/spec-dock uninstall` を主導線、`spec-dock uninstall [path]` を直接導線 / 復旧導線として要求に含める。
  - repo-local runtime wrapper は installer implementation を呼び出す。
- `design.md`:
  - installer CLI に uninstall 実処理を置き、runtime command は self-update と同様に installer wrapper として設計する。
  - runtime script 自体が削除対象になり得るため、削除順序、subprocess invocation、失敗時の installer direct retry guidance を設計する。
- `plan.md`:
  - installer CLI uninstall、runtime wrapper uninstall、self-removal / failure recovery guidance の tests と manual verification を含める。
- `ADR`:
  - 現時点では不要。
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
