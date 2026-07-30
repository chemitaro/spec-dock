---
種別: discussion
ID: "20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition"
タイトル: "S014 private namespace and post-exchange stale-FD threat scope disposition"
状態: "accepted"
作成者: "codex-main"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連:
  - "20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted"
authority: "decision"
derived_from:
  - "requirement.md"
  - "design.md"
  - "20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted.md"
reflected_to:
  - "report.md"
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md"
---

# S014 private same-UID threat scope disposition

## Decision

S014の3 findingと、同じretention architectureを必要とするpost-exchange
stale-FD findingを、現行`iss-00334`のP0／P1 defectとして採用しない。
同一UIDの敵対プロセスが、予測不能な名前を持つ`0700` private directory内部を
能動的に探索・差し替える脅威モデルは、canonical Requirement／Designに
定義されていないためである。

S014 ChatGPT work packetはread-only advisory evidenceとして保持するが、
`not-adopted`とする。S009〜S013で実装済みのpublic／canonical namespace、
preimage、ancestor、workspace write-ahead、rollback recoveryの修正は維持する。

## Canonical boundary

現行canonical contractが要求するもの:

- wrong Candidate、binding mismatch、destination driftをmutation前に拒否する。
- commit前失敗では三文書、companion prior／absent state、indexをrestoreし、
  restoreを確認できなければ自動継続しない。
- Candidate publishは既存final pathを上書きしないatomic publicationとする。
- symlink／path escape／unsafe archive、canonical preimage drift、
  repository ancestor replacementをfail closedにする。
- repository外outputとprivate stagingを用い、公開／canonical authorityを守る。

現行canonical contractが要求していないもの:

- 同一UIDの別プロセスをsecurity adversaryとして扱うこと。
- 同一UID adversaryからprivate `0700` namespaceを防御すること。
- 自動削除不能なretained-entry storageを恒久運用すること。
- operation evidenceとtarget workspaceの同一filesystem配置を新たに必須化すること。
- retained bytesの保管期限、容量管理、purge authorityを追加すること。
- atomic replacement後に旧inodeを保持するopen FDから届く後発writeを、
  新canonical bytesとは別に永続保管すること。

## Why S014 is not a bounded defect repair

S014 ChatGPT回答は、指定されたsame-UID threatの下ではpathname unlinkへ
expected inode predicateを付与できないため、owned bytesを自動削除せずprivate
retained storageへ永続保持する必要があると結論した。さらにApplyでは
operation-evidence retention directoryとtarget workspaceの`st_dev`一致を
pre-mutation条件にする。

これは既存private helperの小修正ではない。少なくとも次を新たに決める必要がある:

- retained storageのauthorityとlayout
- 容量上限、保管期限、manual purge手順
- crash recoveryとretained inventoryの永続schema
- cross-filesystem deploymentの適格性
- same-UID adversaryを含む正式threat model

したがって、S014をP1として採用するとreviewがarchitecture／operation policyを
設計し、現行Issueを肥大化させる。Humanが指定したdefect-only review境界に反する。

## Atomic replacement and stale open file descriptors

canonical contractはreviewed preimageを各atomic replacement boundaryまで照合し、
driftがあればmutationを開始しない。交換成功後、canonical pathnameは新inodeを
指し、交換前から開かれていたFDは旧inodeを指し続ける。旧FDへ交換後に行われる
writeは、replacement boundary後のstale-object writeであり、apply開始前preimage
driftではない。

このwriteまで自動保全するには、次のいずれかが必要になる:

- 旧inodeを自動削除しないretained storage
- writer全員が従うcooperative locking
- OS固有のwrite lease／監視と新しいfailure semantics

いずれも現行Requirement／Designに存在しない。したがって、交換直前にsnapshotと
inodeがexactでありatomic exchangeが成功した後のstale-FD writeは、current
rollback／preimage P1判定から除外する。riskは否定せず、将来のthreat／concurrency
contract拡張候補として保持する。

## Residual risk

同一UIDの別プロセスは、private workspace名を発見できれば、最終identity checkと
pathname unlink／exchangeの間へ能動的に介入できる。このriskは否定しない。
ただし同一UIDは一般に同じuser-owned repository、process、evidenceへ広範な権限を
持ち、現行Issueはそれをsecurity isolation boundaryとしていない。

同様に、atomic replacement前から開かれていた旧inodeへ交換後にwriteしたbytesは
自動保全されない。これは一般的なatomic pathname replacementのstale-FD semantics
であり、現行Issueはretention保証を定義していない。

将来このriskを製品要件にする場合は、current PRの追加repairではなく、明示的な
threat-model変更として独立IssueでRequirement／Design／retention operationを
先に定義する。現行PRではbranch mutationを行わない。

## Review instruction

以後の`iss-00334` closure reviewは次へ限定する:

- canonical Requirement／Designに明記されたauthority、preimage、rollback、
  symlink/path、publication、recovery contract
- 実在する通常並行変更とprocess crash
- private workspace内部を能動的に改変しない同一user runtime前提
- atomic replacement boundary後のstale open-FD writeをretention対象にしない

private `0700` directory内部を能動的に改変するsame-UID adversaryを仮定した
retention architecture提案は、current P0／P1判定から除外する。

## Oracle local configuration boundary

このdecisionはOracle configurationへ影響しない。PATH-resolved local Oracleは
通常native configを利用でき、SpecDockは上書き・無効化・隔離しない。
formal必須値だけを明示fieldからdirect argvへ渡す。
