---
種別: disc
ID: "20260521t004308z-disc"
タイトル: "Issue Execution PR Delivery Scope"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
親: ["iss-00105"]
関連: []
authority: "proposed"
derived_from:
  - "consultant:019e47f8-6a32-7ca0-8435-b40bc5d68e4f"
  - "spec-dock/active/issue/requirement.md"
  - ".agents/skills/spec-dock-issue-execution/SKILL.md"
  - "spec-dock/docs/workflow_issue.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260521t004308z-disc Issue Execution PR Delivery Scope

## 位置づけ
- ユーザー補足要求を受け、`github-pr-merge-preparer` を単独利用の shared skill に留めず、既存 `spec-dock-issue-execution` の完了境界へどう組み込むべきかを整理する。
- 本 doc は要件定義書へ反映するための discussion であり、長期 ADR ではない。

## 議題 (必須)
- `spec-dock-issue-execution` を実行したとき、issue 実装が「実装完了」だけで止まらず、PR 作成、PR 監視、必要な修正、再 push、再監視、merge 可能状態の報告まで自律的に進むようにする。
- そのために、`github-pr-merge-preparer` を `spec-dock-issue-execution` の final delivery gate として利用する。
- ただし merge 実行、auto-merge 有効化、review thread resolve、GitHub issue close の意味変更などはスコープ外に保つ。

## 背景 (必須)
- 既存 `spec-dock-issue-execution` skill は薄い reminder であり、正本は `spec-dock/docs/workflow_issue.md` とする方針である。
- 現行 issue workflow の final gate は final QA、code review、spec review、final report ledger、final commit、post-commit clean evidence までを中心にしており、PR delivery / merge preparation を完了条件として明文化していない。
- ユーザーは、issue 実行の役割を「実装が終わること」ではなく「PR が作成され、人間が merge できる状態まで整っていること」まで拡張したい。
- `github-pr-creator` は PR 作成 leaf skill として既に存在し、PR 作成後の監視 handoff までを扱う。
- `pr-monitor` は read-only monitor であり、checks / statuses / Codex review を観測するが、修正、push、thread resolve、merge は行わない。
- `issue_finish()` runtime command は GitHub issue close、active clear、post-mutation sync を行う lifecycle command であり、PR readiness 判定を内包していない。

## 選択肢 (必須)
- Option A:
- `github-pr-merge-preparer` を standalone skill としてだけ追加し、`spec-dock-issue-execution` からは利用しない。
  - Pros:
    - 既存 issue execution workflow への影響が小さい。
    - 新 skill の初期実装範囲を限定できる。
  - Cons:
    - ユーザーが毎回「issue 実行後に PR を仕上げて」と追加指示する必要が残る。
    - issue 実行の完了定義が「merge 可能な PR を準備する」価値に届かない。
- Option B:
- `spec-dock-issue-execution` の完了境界を拡張し、final commit 後に `github-pr-merge-preparer` を利用する PR Delivery Gate / Merge Preparation Gate を追加する。
  - Pros:
    - ユーザーが求める「issue を実行したら PR が merge 可能な状態まで整う」に一致する。
    - `spec-dock-issue-execution` は薄いまま、詳細な PR lifecycle は `github-pr-merge-preparer` に分離できる。
    - `pr-monitor` の read-only 境界を保ちながら、修正 loop の orchestration owner を明確化できる。
  - Cons:
    - issue workflow の completion gate が増えるため、`workflow_issue.md` と skill contract の更新が必要になる。
    - PR 準備が timeout / blocked した場合、issue execution 全体を complete と報告できなくなる。
- Option C:
  - `issue_finish()` runtime command 自体に PR readiness 判定を組み込む。
  - Pros:
    - `issue finish` の実行だけで PR readiness を機械的に強制できる。
  - Cons:
    - lifecycle command に GitHub PR 依存と workflow 判断が入り込みすぎる。
    - 既存の `issue_finish()` 契約が大きく変わり、runtime tests / consumer expectations への影響が大きい。
    - skill / workflow layer で扱うべき agent orchestration と runtime command の責務が混ざる。

## 推奨案 (必須)
- Option B を採用する。
- `spec-dock-issue-execution` の completion boundary を、`final commit -> PR creation -> PR monitoring / fixes loop -> github-pr-merge-preparer による human-merge-ready 確認 -> evidence 記録 -> issue finish` に拡張する。
- `issue_finish()` runtime semantics 自体は変更しない。PR readiness は `workflow_issue.md` と skill contract の final delivery gate として定義する。
- `spec-dock-issue-execution/SKILL.md` は詳細手順を抱え込まず、正本である `workflow_issue.md` と `github-pr-merge-preparer` への handoff を明示する。
- `github-pr-merge-preparer` は PR 作成 / 検出、monitor、failure / review 分類、fix delegation、commit / push 確認、再 monitor、merge 可能状態の報告を束ねる shared skill とする。

## 追加要件案
- `spec-dock-issue-execution` は、implementation completion で止まらず、PR 作成、PR 監視、PR merge 準備までを issue execution の通常完了範囲として扱う。
- final local gates と final commit が完了した後、PR Delivery Gate と Merge Preparation Gate を実行する。
- PR が未作成の場合は `github-pr-creator` を使って作成し、PR URL、base branch、head branch、latest head SHA、issue linkage を evidence として残す。
- PR 作成後または既存 PR 検出後は `pr-monitor` を使って checks / statuses / Codex review を監視する。
- `pr-monitor` が `failed` / `review_changes_requested` / `timeout` を返した場合、success として扱わず、`github-pr-merge-preparer` の workflow で分類、修正委譲、再 push、再監視、または human gate に進む。
- `github-pr-merge-preparer` の成功 evidence が記録されるまで、`spec-dock-issue-execution` は complete を報告しない。
- `issue finish` は PR merge preparation evidence が確定した後に実行する。ただし `issue finish` は PR readiness の証明ではなく、従来どおり active issue lifecycle closure として扱う。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md` に `spec-dock-issue-execution` integration scope を追加する。
  - `requirement.md` の対象外から「`issue finish` の自動実行」を単純除外している表現を見直し、issue execution integration では PR-ready evidence 後の lifecycle closure として扱う境界を明確化する。
  - `design.md` では final commit から PR Delivery Gate、Merge Preparation Gate、issue finish までの sequence、responsibility split、monitor result state matrix、evidence model を定義する。
  - `workflow_issue.md` は後続実装で PR Delivery Gate / Merge Preparation Gate を final completion contract に追加する。
  - `spec-dock-issue-execution/SKILL.md` は後続実装で `github-pr-merge-preparer` への final delivery handoff を明記する。
- 追加で作る discussion docs:
  - 現時点では不要。設計フェーズで state matrix や evidence model が膨らむ場合は、design doc 内の表として扱う。
