---
種別: ADR（Architecture Decision Record）
ID: "20260907t223933z-adr"
タイトル: "事前レビューで判明した復旧状態と安定性判定の矛盾修正"
状態: "accepted"
作成者: "Codex"
最終更新: "2026-09-08"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-08"
accepted_by: "Codex（ユーザーが委任したEpic設計担当）"
mirror_eligible: true
derived_from: ["20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md"]
reflected_to: ["../requirement.md", "provider-lifecycle-wire-contract.md"]
supersedes: "provider-lifecycle-wire-contract-v9 の矛盾する復旧条件と親安定性判定の循環解釈のみ"
---

# 実装前に復旧と安定性の契約を閉じる

## Context

freshなGPT-6 Max reviewerは、既存の3 Issue分割を維持できる一方、実装前の親契約に3つの矛盾を確認した。調査・意思決定を子Issueへ先送りせず、未実装のB0段階で閉じる。今回の判断は新機能の追加ではなく、既に要求する復旧保証と安定性保証を実現可能にする技術的修正である。

## Decision

### CLAR-001 — 各回の結果と履歴全体の合否を分離する

安定性の正本は引き続きEpic Requirement `E384-QUAL-001` だけとする。各attemptの全role、identity、raw evidence、適用されるnon-rolling条件を評価した結果と、履歴全体を評価したqualification結果を分ける。後者を前者へ戻す循環を作らない。

数値、20件のchronological window、結果非filter、failure/flake/retryの保持、初期履歴不足ではB3をacceptしない条件は変更しない。これは保証の削除ではなく、初期の正常なattemptから履歴を構築可能にする明確化である。

### CLAR-002 — incomplete uninstallはrecordと所有者で判断する

incomplete recordは最初のtarget除去より先に公開される。直後に停止すれば、全6 targetがpresentでも正当なincomplete状態である。WIR-ACT-005は存在するtargetを残りの除去計画へ含め、不在targetは保全済みとして扱う。targetの不在数を状態認識の根拠にしない。

### CLAR-003 — cleanup完了を、応答前クラッシュ後も再提示する

Wire v10の `WIR-CLEANUP-002` を採用する。既存のrepository-owner-bound private namespaceに固定のcompletion receiptを一つだけ保持する。保護されたConsumerデータへの権限や新しいprovider-owned targetは増やさない。

- 新operationごとにgenerationを作り、ACTIVE・stage・cleanup token・receiptを束縛する。同じtupleの後続operationでも古いtokenは使えない。
- stageの除去とfsync、receiptのatomic publishとfsync、ACTIVEのexpected-byte unlinkとfsync、応答の順とする。
- 両方が存在する期間はreceiptをcontinuationの正本とし、最初のdesired requestの一度だけの保存とACTIVE mirror遅れの回復を閉じる。異なるidentityや既存の別requestを上書きしない。
- ACTIVE不在でも、正しく束縛されたtokenはreceiptから完了と保存済みcontinuationを再提示できる。lifecycleは実行せず、mutation_started=falseとする。
- 次の明示的なmutation requestがadmissionを通過した時点でだけ旧receiptを失効する。dry-run、admission failure、already-absentでは保持する。無関係なreceiptは削除しない。

public codeは増やさない。既存 `terminal-cleanup-completed` に、3 retry forms × deferred有無の6 replay relationを加える。全relationは148行、codeは38、public JSON goldensは33のままである。新relationは有限表と必須fault casesで確認する。U5/U6/U7のstage action・summary、U9/I1のguidanceは既存規範へ同期する。

### CLAR-004 — 今回の見直し範囲と開始条件

3 IssueのID・依存・goal/non-goal・責務は変更しない。各draftは親wireへの参照を持ち、値や実装を複製していないため、今回の親reviewでその参照と受け入れ境界を再確認する。Issue詳細文書や実装を本worktreeで生成する必要はない。

まだ受理済みのIssue実装がないため、再開すべき依存状態はB0である。過去のparent passをv10へ流用せず、現在の独立GPT-6 Max reviewerで修正候補を確認する。#392はその後、別worktreeで詳細化する。#395/#396はv10をread-onlyに消費する。

## Options

- **採用：bounded completion receipt。** 既存の「ACTIVEがなければ通常dispatch」という境界を保ちつつ、完了直前の応答喪失と保存済みrequestを回復できる。新しい履歴蓄積や広いcleanup権限は不要。
- **不採用：ACTIVEを永久に完了状態で残す。** 通常dispatchとcleanupの分岐を変更し、次のdesired requestとの区別が増える。
- **不採用：ACTIVE不在なら任意tokenを成功にする。** 正しいoperationを確認できず、古いtokenや別requestを誤受理する。
- **不採用：unknown tokenを拒否したまま手動復旧に委ねる。** 完了直前の正当な再試行と保存済みcontinuationの保証を満たさない。
- **不採用：履歴不足によるqualification failを各attemptへ転記する。** 最初の安定性windowを成立させられない。

## Consequences

- 論理矛盾はEpic設計で解消し、子Issueを調査専用や検証専用にはしない。
- 実装ファイル・関数・collector・テストコード・コマンド順は各Issue開始前の詳細化で定める。
- Private receiptの内部符号化などの詳細は、ここで定義した固定fields・所有・世代・保持・失効・crash境界・public resultを変更しない範囲で具体化する。
- 承認済みの要件はR/D/Pとwireに反映する。本ADRの採用だけではreview pass、Issue start、製品検証、main mergeを意味しない。

## References

- [Epic Requirement](../requirement.md)
- [Provider Lifecycle Wire Contract v10](provider-lifecycle-wire-contract.md)
- [Rolling-Wave Contract](rolling-wave-issue-elaboration-contract.md)
- [再開・レビュー記録](20260907t223421z-epic-resumption-and-gpt6-review.md)
