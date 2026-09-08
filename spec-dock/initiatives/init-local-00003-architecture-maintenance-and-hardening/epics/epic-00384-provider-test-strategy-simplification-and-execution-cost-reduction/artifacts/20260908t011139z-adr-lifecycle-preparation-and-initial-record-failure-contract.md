---
種別: ADR（Architecture Decision Record）
ID: "20260908t011139z-adr"
タイトル: "準備と初期レコード公開の失敗契約を閉じる"
状態: "accepted"
作成者: "Codex"
最終更新: "2026-09-08"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-08"
accepted_by: "Codex（ユーザーが明示承認した親修正の設計担当）"
mirror_eligible: true
derived_from: ["../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/artifacts/20260908t010201z-issue-392-elaboration-parent-return.md"]
reflected_to: ["../requirement.md", "../design.md", "../plan.md", "provider-lifecycle-wire-contract.md", "rolling-wave-issue-elaboration-contract.md", "epic-integration-branch-contract.md"]
---

# 準備と初期レコード公開の失敗契約を閉じる

## Context

#392の詳細化で、P392-001（private stage準備の通常I/O失敗）とP392-002（最初のincomplete record公開失敗）の結果が親wire v11で未被覆と分かった。fresh GPT-6 Max reviewerも同じ2群を確認した。ユーザーは「この方針で進めてください」「直列で実装」「親エピックの見直し修正問題ありません」と承認した。

調査を将来のIssueへ先送りせず、#392のProduct実装前に親で閉じる。#392は正式start済みで、調査基準HEADは `14a72044738ce698c3113a0ee70f052015e3be8a`、treeは `af8e50ed3e20e5a03ef1e2a46332142befa1251f`。Product実装はまだない。親仕様の修正を現在のIssue branchで行うことは、実装の並列化やB1受入を意味しない。

## Decision

1. Wire v12のWIR-PREP-001を採用する。有限の `lifecycle-preparation-failed` と対応する初期authority・stage・incomplete record公開の結果を追加する。既存の所有者・binding・型・candidate違反は個別の診断で保持し、catch-allにしない。
2. private prepared authorityをstage payloadより先に耐久化する。owner-boundな予約namespaceと有限のtemporary bookkeepingは途中作成から安全に再入場できるようにする。未知物の一括cleanupはしない。
3. prepared再入場は元recordと、自身が公開したexpected incomplete recordの両方を扱う。公開前、rename後/fsync未完、record耐久化済み/ACTIVE更新未完を混同しない。
4. payload検証後はACTIVE readyを先に耐久化してからterminal recordを公開する。preparedはcleanup完了判定へ入れず、同candidate updateで旧readyを新operation完了と誤認しない。
5. Consumer未変更と、record/containerの同世代変更が残る状態を区別する。再試行を許す結果は既存のordinary exact-tuple commandへ一意にする。terminal cleanupは既存token/receipt/continuation-owner規則を維持する。
6. 3 Issue・直列依存・Epic PR base・human merge・14 active baseline・#395/#396責務・E384-QUAL-001・E384-DEC-001/002を変更しない。新Issueは作らない。
7. 親修正と当該Issue詳細化の内容reviewは、固定したworking-tree manifestに対して行える。Product実装の開始前には、当該内容と一致するclean pushed tipのfreeze/projectionを別途確認する。内容reviewを公開済みやProduct実装済みとは呼ばない。初回start済みの#392を再start/再分岐しない。

詳細なpublic valueとrelationはwireだけを正本にする。本ADRに第二の対応表を複製しない。ここでの採用はユーザーが委任した技術的修正の採否であり、独立review passを自己認証するものではない。

## Options

- 採用：準備に限定したcodeと有限関係、bounded prepared stateで閉じる。新しいpublic phaseやConsumer ownershipを増やさない。
- 不採用：容量不足をcandidate-invalid/owner-mismatchへ丸める。事実と診断がずれる。
- 不採用：通常I/O failureを未型付け例外として放置する。closed recoveryの不足を隠す。
- 不採用：旧per-file journal、汎用rollback、調査専用Issueへ戻す。今回の軽量化と単一実装受入に反する。

## Consequences

- 追加fault範囲は準備から最初のincomplete recordまで。既存terminal/receiptの失敗を別blockerに水増ししない。
- #392はv12を実装し、#395/#396はread-onlyに消費する。両後続draftは参照と所有境界を再確認し、未着手の実装詳細は作らない。
- 受入済みProduct実装がないため再開点はB0。parent-only文書修正を選択中Issue branchへ含めても、Issue PRはEpic branchをbaseにし、Product受入と人間mergeを省略しない。
- 旧親passはv11の証拠として残す。v12の独立reviewと、完成した#392詳細R/D/Pのreviewは候補identityで区別する。

## 2026-09-08 clarification — Public-record staging mode

Wire v12のpublic installation recordはmode0644かつnative atomic replaceである一方、private tempの一般則を`RECORD-TEMP`にもmode0600として適用すると、rename/exchangeがmodeを保存するため両者を同時に満たせない。このため既存Decisionの意味を次のように明確化する。

- `RECORD-TEMP`はprivate metadata tempではなくpublic-record staging objectであり、最終public mode0644、regular/link1/owner euid/max4096、exact seven-key record bytesだけを許可する唯一のmode例外とする。
- `ACTIVE.json`、completion receipt、`STAGE-OWNER.json`と各metadata atomic tempはmode0600、private directoriesはmode0700を維持する。
- Publicへmode0600で公開してからchmodする遷移は禁止する。
- Exchange後に`RECORD-TEMP`へ移った旧public recordは、ACTIVEのoriginal-record bytes/hash/inode witnessと一致するときだけown residueとしてexpected-bound unlink/fsyncできる。Content-equalなforeign inodeはpreserve-and-blockする。
- このclarificationはpublic status/code/phase/relation/golden、三Issue責務、recovery保証を変更しない。親WireとIssue #392仕様を同じ候補で再review・再freezeする。

## References

- [不足を確認した調査](../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/artifacts/20260908t010201z-issue-392-elaboration-parent-return.md)
- [Wire v12](provider-lifecycle-wire-contract.md)
- [Rolling-Wave Contract](rolling-wave-issue-elaboration-contract.md)
- [Integration Contract](epic-integration-branch-contract.md)
