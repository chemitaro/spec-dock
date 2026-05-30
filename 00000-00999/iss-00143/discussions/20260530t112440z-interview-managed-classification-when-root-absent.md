---
種別: interview
ID: "20260530t112440z-interview"
タイトル: "Managed classification when root absent interview"
状態: "answered"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "iss-00137"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T11:24:40Z"
created_by_role: "orchestrator"
status: "answered"
adoption_status: "adopted"
reflected_to: []
derived_from:
  - "spec-dock/active/issue/discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md"
  - "spec-dock/active/issue/discussions/20260530t111421z-interview-worktree-root-requirement-for-external-management.md"
  - "spec-dock/active/issue/discussions/20260530t112038z-interview-external-worktree-post-remove-cleanup.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t112440z-interview Managed classification when root absent interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - `worktree list/show --json` の `managed` field と classification diagnostic を決める。
  - `design.md`:
    - result model / JSON renderer の互換性と root absence handling を決める。
  - `plan.md`:
    - root absent / valid root / invalid root の JSON assertion を決める。
- chat 上の軽微な一問では足りない理由:
  - `managed` は既存 JSON contract の field であり、boolean を維持するか nullable / unknown を導入するかで互換性が変わる。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `SPEC_DOCK_WORKTREE_ROOT` がない場合、`managed` / `unmanaged` classification を JSON でどう表現するか。
- 回答が後続判断へ与える影響:
  - JSON schema、docs、tests、application model が決まる。

## 質問

`SPEC_DOCK_WORKTREE_ROOT` が未設定の状態で `worktree list/show --json` を実行した場合、各 worktree の managed classification はどう表現しますか？

- Option A:
  - 既存互換性を優先し、`managed` は常に boolean のままにする。
  - root がない場合は全 record を `managed=false` とし、別 field / warning で `managed_classification_available=false` や `classification_reason=root_missing` を返す。
- Option B:
  - 意味の正確さを優先し、root がない場合は `managed=null` のような unknown を許可する。
  - JSON schema は nullable になる。

## source-grounded context

- 現行 JSON payload は `managed: bool` を返す。
- 先行 `iss-00137` では `SPEC_DOCK_WORKTREE_ROOT` 必須だったため、classification は常に計算できた。
- 今回の回答により `list/show/remove` は root 不要になったため、root absence でも inventory を返す必要がある。
- `managed` は削除可否 blocker ではなく diagnostic へ変わる。

## Codex の分析

- Option A の利点:
  - 既存 JSON consumer に対して `managed` field の型互換性を保てる。
  - root がない場合の uncertainty を別 field で表せる。
- Option A のリスク:
  - `managed=false` が「本当に unmanaged」と「分類不能」を兼ねるため、別 diagnostic を必ず見る必要がある。
- Option B の利点:
  - `unknown` を正確に表せる。
- Option B のリスク:
  - 既存 `managed` boolean contract を破る。
  - text output / tests / model の変更が広がる。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - `managed` は今回 remove blocker ではなくなるため、boolean 互換を保ったまま classification availability を追加する方が小さい。agent は `managed_classification_available=false` を見れば root absence を理解できる。
- 未回答時の影響:
  - requirement の JSON contract と tests を確定できない。

## ユーザー回答

- 回答:
  - Option A を採用する。
  - `managed` は既存互換性を優先して常に boolean のままにする。
  - `SPEC_DOCK_WORKTREE_ROOT` がない場合は全 record を `managed=false` とし、classification が unavailable であることを別 field / diagnostic で返す。
  - `worktree list` / `worktree show` の情報には、その worktree が `spec-dock worktree create` で作られた SpecDock 管理下のものか、それ以外の root / 外部作成のものかを判別できる情報を含める。
- 回答日時:
  - 2026-05-30

## 追加確認の要否

- 追加確認が必要か:
  - yes
  - 具体 field 名は design で固定する。requirement では、`managed` boolean と classification availability / origin diagnostic が必要であることを固定する。

## 採用判断

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - 既存 JSON consumer との互換性を保ちつつ、operator / agent が SpecDock-created managed worktree と external worktree を区別できる必要があるため。`managed` は boolean のまま維持し、root absence による分類不能は追加 diagnostic で表現する。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - `worktree list` / `show` は、各 worktree が SpecDock-created managed worktree か external / unmanaged worktree かを判別できる情報を返す。
  - `managed` は boolean として維持する。
  - `SPEC_DOCK_WORKTREE_ROOT` がない場合も inventory / detail は返し、managed classification が unavailable であることを diagnostic として返す。
- `design.md`:
  - JSON result に classification availability / reason または origin diagnostic を追加する。
  - root が valid な場合は `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` 配下を `managed=true` とし、それ以外を `managed=false` とする。
  - root がない場合は `managed=false` とし、classification unavailable diagnostic を付ける。
- `plan.md`:
  - root valid 時に managed / external を区別できる JSON assertion を追加する。
  - root missing 時に `managed=false` と classification unavailable diagnostic を返す assertion を追加する。
- `ADR`:
  - 現時点では不要見込み。
