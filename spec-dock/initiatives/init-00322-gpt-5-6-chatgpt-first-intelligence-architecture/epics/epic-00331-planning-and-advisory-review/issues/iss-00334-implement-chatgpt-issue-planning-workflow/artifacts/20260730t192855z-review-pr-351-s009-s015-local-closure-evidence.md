---
種別: review
ID: "20260730t192855z-review-pr-351-s009-s015-local-closure-evidence"
タイトル: "PR 351 S009-S012 local closure evidence"
状態: "accepted"
作成者: "codex"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: ["PR-351"]
authority: "advisory"
derived_from:
  - "20260730t172342z-pr-351-observation-head-be0c84a6.json"
  - "20260730t172342z-pr-351-s009-three-p1-chatgpt-concretization.md"
  - "20260730t181147z-pr-351-s010-five-p1-chatgpt-concretization.md"
  - "20260730t184838z-pr-351-s011-existing-rollback-workspace-chatgpt-concretization.md"
  - "20260730t191619z-pr-351-s012-workspace-preledger-crash-chatgpt-concretization.md"
reflected_to: ["report.md"]
---

# PR 351 S009-S017 local closure evidence

## Scope

この成果物は、pushed HEAD
`be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`へのPR観測から開始した
S009と、その未コミット修正に対するfresh local reviewで確認されたS010〜S012を
記録する。公開contractの再設計やP2／P3改善提案は対象外である。

## ChatGPT-first concretization

| step | session | scope | result |
| --- | --- | --- | --- |
| S009 | `iss00334-s009-three-p1` | visible Candidate path attachment、repository parent descriptor authority、per-target preimage CAS | 3件をP1として限定具体化 |
| S010 | `iss00334-s010-five-p1` | Candidate rejection cleanup、staged ownership、write-ahead mutation、resumable rollback、absent removal | 5件をP1として限定具体化 |
| S011 | `iss00334-s011-existing-rollback-workspace` | existing-preimage reverse exchange後のworkspace回収 | 1件をP1として限定具体化 |
| S012 | `iss00334-s012-workspace-preledger-crash` | forward／existing rollbackのworkspace作成からledger登録までの未追跡crash window | 1件をP1として限定具体化 |
| S013 | `iss00334-s013-absent-rollback-intent` | absent rollbackのworkspace作成からphase handoffまでの未追跡crash window | 1件をP1として限定具体化 |
| S015 | `iss00334-s015-public-canonical-final` | Candidate publication tokenとApply canonical exchange-backのpublic／canonical CAS | 2件をP1として限定具体化 |
| S016 | `iss00334-s016-two-p1` | repeated-contention characterizationとstaged-tree blob content binding | 2件をP1として限定具体化 |
| S017 | `required-repository-connector-context-github-24`（S016 Blue follow-up） | verified treeとlocal commitのexact binding | 1件をP1として限定具体化 |

全sessionは指定`chatgpt-use` wrapperを使用した。各fresh invocationは
`requested=Pro`、`resolved=Pro`、`verified=yes`で、GitHub connectorから
`chemitaro/spec-dock`の対象branchとexact pushed HEADを確認し、`main`へ
substituteしていない。Oracle 0.16.1の内部表示`gpt-5.5-pro`はversion-independent
`Pro` selectorのlegacy aliasであり、version-specific resolutionとして採用しない。

## Implemented closures

- Candidateは成功直前にvisible output path attachmentを再証明する。
- Candidate rejection cleanupはpublic logical filenameをcheck-then-unlinkせず、
  private `0700` cleanup directoryへdescriptor-relative no-replace renameしてから
  owned inodeだけを削除する。
- Apply target parentはrepository rootからcomponent-wise `O_NOFOLLOW`で捕捉し、
  snapshot、mutation、rollbackをdescriptor-relativeに行う。
- existing preimageはDarwin `RENAME_SWAP`／Linux `RENAME_EXCHANGE`で置換し、
  targetとprivate workspaceの両側をinode／snapshotで検証する。
- absent preimageはdescriptor-relative no-replace publication／quarantineを使用し、
  public target nameをcheck-then-unlinkしない。
- private mutation ledgerはforward mutationを`prepared`、確認後を`published`、
  rollbackを`rollback-prepared`としてwrite-ahead記録する。
- rollbackはexact already-restored stateを冪等に分類し、復元済みentryを1件ずつ
  durability確認後にledgerからdrainする。
- existing-preimage reverse rollbackは内側workspaceを外側mutation 1件へ
  `rollback-prepared`として引き継ぎ、pre/post exchange、post unlink、post rmdirを
 再開可能に分類する。
- workspace生成より前にsingleton `workspace_intent`をdurable ledgerへ記録する。
  workspace inodeはchild作成前、staged inodeはmode変更／write前にbindし、
  complete `prepared`／`rollback-prepared` handoff後だけintentをclearする。
- workspace intent recoveryは通常mutation recoveryより先に実行する。unbound empty
  またはexact bound stagedだけをcleanupし、wrong inode、unknown non-empty、
  extra entry、unsafe objectは全bytesとintentを保持してfail closedする。
- absent rollbackも同じsingleton intentへ`rollback-absent` purposeとして接続する。
  workspace作成前に予約し、workspaceと将来の`quarantine` inodeをbindしてから
  `rollback-prepared`へhandoffする。pre-handoffはexact targetとempty workspace
  だけをcleanupし、completed handoffはintentだけをclearする。
- Candidate publication helperはownership確立後のpublic pathnameを再openしない。
  Linuxはverified staged FDのduplicateをpublication tokenとし、Darwinはprivate
  cloneをopenして実inodeへbindしてからdescriptor-relative no-replace renameする。
- Apply canonical exchangeのCAS missでは、workspaceへ実際に移動した並行attachment
  をidentity／snapshotで捕捉し、canonicalがexact stagedである間に一度だけ
  exchange-backする。actual concurrent inodeを正本へ戻し、exact stagedだけを
  cleanupして既存`stale/apply_target_changed`へ分類する。

## Red evidence

- Candidate visible pathのsymlink／ordinary-directory detachment。
- Candidate cleanupのidentity確認後にunknown final entryへ差し替える競合。
- staged slot差し替えによるunknown canonical publicationとpreimage消失。
- namespace publication後、complete mutation entry永続化前のprocess crash。
- restore後またはledger shrink後のprocess crash。
- decision／companion absent rollbackのidentity確認後差し替え。
- absent target publication後、`published`永続化前のprocess crash。
- existing-preimage reverse exchange後、private workspace cleanup前のprocess crash。
- forward／reverse workspaceの`mkdir`前、workspace inode bind前、staged inode bind後、
  complete mutation handoff前のprocess crash。

各Redは修正前に意図したfailureまたは`recovery_required/restore_mismatch`を再現した。

## Green evidence

Main orchestratorによるS015統合後の再検証:

- focused Candidate／Apply／application:
  `153 passed, 1 skipped`
- explicit full-regression Apply integration:
  `89 passed`
- ordinary fast lane:
  `1332 passed, 2188 skipped`
- `make lint`:
  Ruff check／format 425 files／mypy 287 filesすべてPASS
- provider／dogfood Candidate・Apply:
  byte-identical
- `./spec-dock/scripts/spec-dock validate`:
  `spec-dock: ok (validate) nodes=227`
- `git diff --check`:
  PASS

## Review history and disposition

- 初回S009 fresh QAはnative exchange ABI test不足をP1とし、Linux／Darwinの
  direct fake-CDLL、symbol欠落、errno契約テストを追加した。
- 初回S009 fresh Spec／CodeはCandidate cleanup、absent removal、staged ownership、
  write-ahead、rollback drainの5件をP1とした。S010で修正した。
- S010 fresh Spec／Codeはabsent-preimageのprepared recoveryをP1とした。
  decision／companion双方のRed／Greenで修正した。
- S010 closure Codeはexisting-preimage reverse rollback workspaceの未追跡crashを
  P1とした。S011で修正した。
- S011 final Codeはworkspace作成後・ledger登録前の未追跡crashをP1とした。
  S012でforward／reverse共通の`workspace_intent`として修正した。
- S012 final QAはabsent rollbackだけがS012 protocolへ未接続であることをP1とした。
  S013でdecision／companion双方を`rollback-absent`へ接続した。
- S014 scope後のfresh Code reviewは、Candidate publication後・ownership capture前の
  public replacementと、Apply target open後・exchange前のatomic editor replacementを
  scope内P1とした。S015でpre-bound publication tokenとactual displaced attachmentの
  one-shot exchange-backとして修正した。
- S015 fresh Spec reviewが提起したexchange-back中の第三のatomic replacementは、
  最新attachmentをprivate workspaceへ保持したまま
  `recovery_required/restore_mismatch`で停止するaccepted recovery boundaryである。
  継続中multi-writer下のcontinuous-latest guaranteeは新しいlocking／retention／retry
  contractを要するため、D-20260730-S015-CONTENTIONとしてcurrent P0／P1修正へ
  採用せず、branch mutationを行わない。
- S016はcontinuous-latest architectureを追加せず、accepted repeated-contention
  fail-closed boundaryを直接実証するintegration characterizationだけを追加した。
- S016は`after_diff_proof`後のworktree replacementまたはindex-only poisonが
  unauthorized bytesをcommit／pushできるP1を、operation-authorized expected
  OID／absenceとimmutable staged treeのfive target entriesを比較して閉じた。
- S016 Redはatomic replacement 5 failuresとindex-only poison 1 failure、
  Greenはfocused `7 passed`、Apply unit `79 passed`、明示full-regression Apply
  integration `96 passed`である。
- S016後のfresh Specは、verified `local_tree`後のreal-index変更をordinary
  `git commit`がconsumeし、push前proofより先にunauthorized local commitを生成する
  P1を確認した。S017でprivate index hooks、exact `commit-tree`、commit object proof、
  old-value CAS branch installへ置換した。
- S017 Redは`3 failed, 3 passed`、Greenはfocused `7 passed`、Apply unit
  `83 passed`、Apply full unit＋integration `186 passed`である。hook順序／mutation／
  rejection／trailer、signing intent、late poison、final-proof raceを保護した。
- S011 final SpecのReport未統合指摘は、本成果物とReport／repair batch追補で閉じる。
- 旧PASSはS013の承認へ流用せず、S013後のfresh最終3者reviewを改めて実施する。

## Oracle local configuration boundary

PATH-resolved local Oracleが自身の通常native configを利用することは許容する。
SpecDockはそのconfigを上書き、無効化、隔離、強制しない。formal workflowの
再現性に必須の値だけを明示fieldからdirect Oracle argvへ渡す。personal wrapper
path、`chatgpt-use` product runtime依存、API／default-branch／alternate-profile
fallbackは導入していない。

## Remaining gates

S013後のfresh Code reviewが提起したsame-UID private workspace tamperingは、
`20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition.md`により
current canonical threat model外として不採用とした。S014 advisoryが要求する
retained storage architectureは実装していない。

S015 fresh Spec reviewが提起したrepeated canonical contentionは、
`20260730t212559z-disc-s015-repeated-canonical-contention-boundary.md`により、
全observed bytesを保持して`recovery_required`で停止するcurrent contractとして
処分した。continuous-latest guaranteeは現Issueへ追加しない。

## S017 final local gates

- fresh Spec reviewer: PASS、P0／P1 0。canonical三文書、Report、S017 artifact、
  provider／dogfood、testsを照合し、verified-tree commit bindingと既存
  rollback／recovery契約の整合を確認した。
- fresh Code reviewer: PASS、P0／P1 0。private Git argv、`GIT_INDEX_FILE`、
  hook順序、`commit.gpgsign`、commit object proof、`update-ref`／push CASを確認した。
- fresh QA reviewer: PASS、P0／P1 0。late poison、final-proof race、hook
  mutation／reject／trailer、post-commit mutation、signing、private
  `update-ref`拒否を確認した。
- Main final verification:
  - ordinary fast lane: `1346 passed, 2202 skipped`
  - explicit Apply full regression: `103 passed`
  - `make lint`: Ruff／format／mypy PASS
  - provider／dogfood Apply byte parity PASS
  - SpecDock validate: `nodes=227`
  - `git diff --check`: PASS

残存gate:

1. commit／pushとlocal／remote parity。
2. exact pushed code HEADへのfresh ChatGPT defect-only review。
3. evidence publication後のPR #351 fixed observation。

merge、auto-merge、branch deletion、Issue close、`issue finish`は実施しない。
