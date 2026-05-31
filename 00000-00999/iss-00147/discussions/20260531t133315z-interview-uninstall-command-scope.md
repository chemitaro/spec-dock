---
種別: interview
ID: "20260531t133315z-interview"
タイトル: "Uninstall command scope"
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

# 20260531t133315z-interview Uninstall command scope

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
    - `uninstall` の対象、必須スコープ、禁止スコープ、受け入れ条件が変わる。
  - `design.md`:
    - installer CLI 側に置くか、repo-local runtime command 側に置くか、削除対象と guardrail が変わる。
  - `plan.md`:
    - 実装 step、test obligation、manual verification、destructive operation の確認手順が変わる。
  - `ADR`:
    - 現時点では不要。長期的な install/uninstall ownership を再定義する場合のみ候補にする。
- chat 上の軽微な一問では足りない理由:
  - `uninstall` が削除する対象を誤ると、repo-local docs / agent tooling / Python package / user-authored files のどれを消すかが変わり、破壊的操作の安全境界に直結するため。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - `spec-dock uninstall` の primary goal が、導入済み repo から spec-dock 管理物を外すことなのか、実行環境から spec-dock package / CLI 自体を外すことなのかを確定する。
- 回答が後続判断へ与える影響:
  - command placement、削除対象、confirmation UX、tests、docs、rollback guidance の前提になる。

## 質問 (必須)
- 質問:
  - `uninstall` コマンドの主目的は、どちらですか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があればその削除対象と残す対象を明示してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/requirement.md`: 現 issue は template scaffold で、scope / acceptance criteria は未固定。
  - `spec-dock/active/epic/requirement.md`: `epic-00054` は close / local delete / repo-local self-update を lifecycle command expansion として扱い、destructive guardrail と docs/tests 整備を要求している。
  - `spec-dock/active/epic/design.md`: existing relation として installer `update` はあるが repo-local runtime command の導線が gap とされ、delete は local tree destructive operation、self-update は installer wrapper として分離されている。
  - `src/spec_dock/cli.py`: package entrypoint 側に `init` / `update` があり、managed scaffold と install_root assets を target repo へ同期する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`: repo-local runtime command から installer update を呼び出す command surface がある。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py` and `application/delete_node.py`: local spec node delete は既存 capability として存在する。
  - `tests/test_init_update.py`, `tests/cli_runtime/test_update.py`, `tests/cli_runtime/test_delete.py`: installer update、runtime update、delete の regression surface が分かれている。
- local context で解決できたこと:
  - 既存の lifecycle epic は repo-local command と installer command の両方を扱っているが、`uninstall` という語が指す対象はまだ canonical docs で定義されていない。
  - 既存の `delete` は spec node 削除であり、spec-dock workspace / installed agent assets / root shortcut / package installation の removal とは別概念。
- まだ人間判断が必要な理由:
  - 「spec-dock 自体を自分自身をアンインストールする」という表現は、repo 内の導入物の削除とも、実行中の package / CLI の削除とも読める。どちらを product goal にするかは実装調査だけでは決められない。

## 回答案 (必須)
- Option A:
  - repo-local uninstall: 対象 repo から `spec-dock/` workspace、repo-root shortcut、installer-managed agent/tooling assets を安全に取り外す。Python package / uvx cache / global executable は削除しない。
- Option B:
  - package/environment uninstall: 現在の実行環境から `spec-dock` package / executable / cache を削除することを主目的にする。target repo の `spec-dock/` workspace 削除は別機能にする。
- Option C:
  - two-layer uninstall: `spec-dock uninstall` は repo-local removal を標準にし、別 flag または別導線で package/environment removal guidance を扱う。

## Codex の分析 (必須)
- 判断軸:
  - 誤削除リスク、ユーザーが期待する「自分自身」の意味、既存 `init` / `update` / `delete` との責務境界、テスト可能性、rollback guidance。
- tradeoff:
  - repo-local removal は既存 installer-managed asset model と整合しやすく、hermetic tests も書きやすい。一方で package 自体は残るため「CLI を環境から消す」期待には応えない。
  - package/environment removal は「自己アンインストール」に近いが、install method が uvx / pip / editable install / system package などで変わり、実行中 process が自分の配布元を削除する境界が不安定になりやすい。
  - two-layer uninstall は期待を広く拾えるが、初回 issue としては scope が広がり、destructive guardrail と docs が重くなる。
- リスク:
  - managed/unmanaged 境界が未定義のまま repo-local removal を実装すると、user-authored docs や agent files を削除する危険がある。
  - package/environment removal を自動化すると、インストール方法ごとの差異、権限、cache、shell path の副作用を扱う必要がある。
- 具体シナリオ / edge case:
  - 既存 repo で `spec-dock/initiatives/**` に長期的な仕様履歴がある場合、標準 uninstall がそれを削除してよいか、archive / dry-run / confirmation を要求するか。
  - `.agents/skills/` や `.codex/config.toml` に user edit がある場合、installer-managed と bootstrap/user-owned の境界をどう扱うか。
  - `uvx --from git+... spec-dock uninstall .` のような one-shot 実行では package は元々永続 install されていないため、environment uninstall の意味が薄い。

## Codex の推奨案 (必須)
- 推奨:
  - Option A を第一候補にする。必要なら docs で「package / environment uninstall は自動削除せず、install method 別の案内に留める」と明記する。
- 理由:
  - `init` / `update` が target repo に scaffold / managed assets を入れる機能なので、その反対操作として repo-local uninstall を定義すると責務が自然で、既存 epic の lifecycle command expansion とも整合する。
  - package/environment removal は install method 依存が強く、初回実装で自動化すると安全境界が大きくなる。
- 未回答時の影響:
  - requirement の scope / non-scope と acceptance criteria を固定できず、design / plan に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - 主目的は、対象 repo から `spec-dock/` workspace や managed agent/tooling assets を安全に取り外すことである。
  - Python package / global CLI / uvx cache など実行環境側の `spec-dock` 削除は主目的にしない。
  - 背景意図:
    - SpecDock はプロダクト開発のための機能群を提供する。
    - ある程度開発が完了した後は、開発用の sub-agent 設定や agent skill が不要になる。
    - sub-agent 稼働がプロダクト本体になる second brain / LLM wiki のような repo では、SpecDock の sub-agent や skill がノイズになる。
    - そのような repo では、開発用 sub-agent 設定や開発用 skill を取り除ける必要がある。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - repo-local uninstall で、`spec-dock/initiatives/**` に蓄積された仕様履歴も削除対象に含めるか、開発用 agent/tooling だけを削除して仕様履歴は残すか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、`uninstall` の primary goal は repo-local removal と確定した。
  - 実行環境の package / executable / cache 削除は install method 依存が強く、今回の主目的から外す。
  - 開発完了後の product repo から、開発用 sub-agent / skill / tooling noise を取り除くことを中心の outcome とする。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `uninstall` の目的を「対象 repo から SpecDock-managed development tooling / agent assets を安全に取り除く」として固定する。
  - package/environment uninstall は対象外または docs guidance に限定する。
  - 利用シナリオに、開発完了後の product repo と、sub-agent/skill が product noise になる second brain / LLM wiki 型 repo を含める。
- `design.md`:
  - installer-managed asset model、bootstrap-only / user-owned boundary、repo-local destructive guardrail を中心に設計する。
  - runtime command と installer command のどちらに置くかは、repo-local target removal と managed asset inventory を踏まえて設計で固定する。
- `plan.md`:
  - managed agent/tooling asset removal、dry-run / confirmation、user-authored file preservation、docs/tests parity を implementation step 候補にする。
- `ADR`:
  - 現時点では不要。install/uninstall ownership を長期 contract として再定義する必要が出た場合のみ ADR を検討する。
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
