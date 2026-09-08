---
種別: ADR（Architecture Decision Record）
ID: "20260907t234210z-adr"
タイトル: "Epic全体再評価に基づく回帰修復と実行ゲートの再定義"
状態: "accepted"
作成者: "Codex"
最終更新: "2026-09-08"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "user-approved-parent-decisions"
accepted_at: "2026-09-08"
accepted_by: "user"
mirror_eligible: false
derived_from: []
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# Epic全体再評価に基づく回帰修復と実行ゲートの再定義

## 1. 現在の結論と権限

ユーザーはIssue start/checkoutを保留し、Epic全体の再評価と必要な親計画修正を依頼した。既存の三Issue構成は維持するが、「問題なし」とは判定しない。独立GPT-6 Max reviewerが四つのP1を発見し、主担当がsourceと実測へ照合した。

初回移行の運用境界 `E384-DEC-001` は2026-09-08にユーザーが「推奨案を採用します」と回答して採用した。続く「オッケーです。それではコミットプッシュした上で最初のイシューをスタートしてください」により、提示した既存branchへのcheckout admission `E384-DEC-002` も採用し、親計画のcommit/push・公開工程後に同じworktreeで#392を正式startする権限を得た。本書のacceptedはこの方針決定を示す。候補の独立review・公開済みtipのG0受入は別の証拠であり、旧ADRや過去reviewのpassを流用しない。Product実装は本工程に含めない。

## 2. 根拠

再評価の基準は `6b20f6bab378cb5b538894e1a7993dde08e4b05b`、tree `c1a518952c5e5016513b3ed2c726c8dfca9fafb7`。これは観測したsource identityであり、修正後のfreeze SHAではない。

Root ledgerの14 active nodeを、既存のfocused full-regression diagnostic経路で実行した。結果は **14 failed / 14.43 seconds / exit 1**。この実行は原因確認であり、full suite、Linux qualification、実装検証の合格ではない。元のnode/signatureと15 total / 14 active / 1 resolvedは変更していない。

生ログとJUnit XMLはEpic配下のGit管理外 `.workbench/reviews/20260908-baseline-diagnostic.{txt,xml}` に保存した。永続的な原因・修復範囲は[register §6.1](active-failure-disposition-register.md)に置く。

## 3. 採用する修正候補

### A. #395を「全件Product修正」から原因別の契約回復へ直す

| 最初に観測した原因 | 行 | 修復対象と守る契約 |
|---|---|---|
| 削除済みactive CLI flagや古い観測経路 | 1、13、14、15 | test fixture/observerを現行公開CLIへ追随させる。廃止flagのProduct復活で合わせない。 |
| S10 test doubleのport不足 | 4–11 | descriptor-bound `copy_scaffolded_tree_at` を忠実に実装したdoubleへ直す。Productを旧path-based APIへ退行させない。 |
| read-only repository identityとstrict publication validationの混用 | 3 | 読取専用importの同一repo判定を分離する。publicationのuserinfo拒否・fetch/push照合、同一repo制約、秘密情報非出力を維持する。 |
| command shellからdomain catalogueへの直参照 | 12 | application側の契約を通す。catalogue二重定義やarchitecture test弱化をしない。 |

内訳は12件のtest harness/observer、2件のProduct責務境界である。これは現時点の最初の失敗原因であり、fixture修復後に奥のProduct振る舞いまで自動的に合格したという意味ではない。同じaccepted behaviorに属する後続不具合は同Issueで修復し、意味の変更が必要なら親へ戻る。

全14行は元nodeを使ったnormal passの証拠でfixed-in-placeへ移す。Skip、xfail、approved failure、assertion弱化、履歴signature改変で成功を作らない。

### B. 置換対象のpayloadと実行中coordinationを分離する

現行 `application/create_node.py` は `spec-dock/system/.runtime/create.lock` を使う。Create/import処理中にlifecycleがsystem rootを交換すると、旧lockを保持するwriterと新lockを取得するwriterが同時に利用者データを書ける。独立したlifecycle lockの存在だけでは防げない。

親E384-RQ-019/C-012に、置換root外のrepository-bound共有排他、runtime観測から書込み完了までの世代整合、wrapper→外部installerのdeadlock-free handoff、中断状態での通常runtime拒否を追加した。#392が実装・その検証を所有し、追加Issueへ先送りしない。

**採用済み `E384-DEC-001`:** 初回0.2.3→0.2.4移行だけ旧SpecDock commandと書込みhelperを止めるmaintenance windowを要求し、0.2.4以降は共通排他にする。初回無停止・legacy bridge・process自動killは採用しない。Wire v11 §16で次を固定した。

- 既存installerが使用するrepository-root inodeのflockを共通化する。置換root外に新たなlock fileや常駐daemonを増やさない。通常runtimeはSH、external lifecycleのdry-run/cleanupを含む全経路はEXをnonblocking取得する。
- 置換moduleのimport前に固定bootstrapがreadyを確認する。異常中断後のincompleteは外部installerだけで復旧する。ready後のstage cleanup残は正常runtimeの妨げにしない。
- repo-local updateとuninstall双方をrelease→execにし、外部installer開始後は旧moduleへ戻らない。cross-targetでも同じ規約とし、fd/tokenによるinstaller guard bypassを作らない。
- repositoryを書き込む管理下helperにはlease寿命だけを継承し、親だけが異常終了しても書込み終端までEXを阻止する。共有descriptorへの早期LOCK_UNを禁止する。
- closed lifecycle code二つ・関係行四つ・JSON例二つを追加する。既存record/cleanup/receipt/replayの値は変更しない。

共有descriptorが残る間のlock保持と、LOCK_UNが共有lock全体へ作用することは[Linux flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html)と[Apple flock(2)](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/flock.2.html)の仕様へ照合した。対象Linux/macOS上の実動作は#392の受入テストで証明する。

### B2. 追加で発見した既存branch checkoutの境界（採用済み）

現行 `application/set_active.py` の `checkout_active_target` は既存branchの内容を検証せず切り替える。`application/issue_lifecycle.py` はその後も旧processでactive更新・post-mutation syncを行う。切替先がprovider payloadを変える場合、installerとの排他だけでは自分自身の世代混在を防げない。`issue finish` はcheckoutしない。

**採用済み `E384-DEC-002`:** 管理下のcheckoutを「admission済みprovider closure（四root・二slot・record/markers）が変わらない場合」に限定する。事前にtarget refを固定して確認し、不同一/判定不能ならcheckout・active・sync前に拒否する。事後driftでも旧moduleによるactive/syncを止め、branch変更済みであることを報告し、自動rollbackしない。現HEADから新branchを作る通常経路は維持する。全runtimeのEX化、hot reload、自動installer起動は採用しない。Wire WIR-COORD-007で固定する。

### B3. 別worktreeを変更するhelperの排他漏れへの修正

独立再レビューは、呼出元AのSHだけでは変更先Bのinstaller EXと競合しない点をP1として指摘した。現行 `application/worktree.py:221–236` はBをGitで削除し、その後もfilesystem cleanupを行う。作成側も同 `:107–128` でB作成後にmake initを呼ぶ。これらは任意の手動Gitではなく、管理下のruntime経路である。

親E384-RQ-019の修正対象は**実際に変更するrootのcoordination**である。WIR-COORD-008/009で次の境界を固定する。

- 削除はB rootのEXを取得し、Git helperと後処理の終端まで維持する。削除後の同名パスに別inode Cが現れた場合はCを保存して部分結果を報告し、名前だけを頼りに後片付けしない。
- 作成は固定source closureを確認し、空のB rootを確保してEXを取得する。公開entrypointを保留してpayloadを準備・検証し、最後に固定bootstrapをatomic publishする。途中で停止してready recordだけが残っても、通常runtimeの入口は公開されない。作成済み空root等の部分状態は隠さない。
- makeの検出と実行はどちらも任意consumer hookである。B EX保持中に別open-file-descriptionのnonlocking directory fdへ元Bをbindし、管理下writerと全A/B leaseを終了してからそのBをcwdに外部handoffする。旧installed moduleへ戻らず、同名Cのhookを実行しない。
- hookからのinstallerは独立した通常admissionを使う。make失敗時のexit 0＋bootstrap status/warningは維持し、hook観測を現在のready状態の再認証にしない。
- これらの競合・crash・親だけの異常終了・パス再利用・hook互換性を#392自身の受入検証に含める。調査Issueや一般的schedulerは追加しない。

前候補21ファイルへの独立reviewは `wire_only_review=fail`、`whole_plan_review=blocked`、新規P0=0/P1=1/P2=0だった。この履歴を上書きしない。本修正候補は新しい21ファイルhash manifestで同じreviewerへ渡し、結果をGit管理外receiptへ記録する。修正文が存在するだけで合格扱いにしない。

### C. 一回のgateと最終qualificationを区別する

数値閾値・五回測定・二十件履歴・失敗ゼロ条件は維持する。単回attemptは新規IDで一つのrole graphを実行し、一つのLinux canonical観測を作る。固定candidate/campaignの先頭五attemptを性能母集団とし、同じ観測をlatest-twenty履歴から参照できる。

通常required PR contextは単回結果で決まり、B3/Epic受入で五回・fault campaign・二十件を集計する。集計結果を単回判定へ戻さず、5×20の入れ子を作らない。開始した失敗・取消・中断・欠測を除外/補充しない。同一candidateの失敗campaignを改名して取り直さない。独立観測の新attempt IDと、同一attemptのretry/rerunを区別する。

Intentional required-context REDは五回campaign freeze前に実施し、履歴からは消さない。その後の二十成功attemptという初期導入コストは実在する。通常CIの恒常コストと初回受入コストを別々に示す。Candidate buildは一回で、後続観測は保存された同一bytesを使う。

定量値・母集団・拒否条件の唯一の正本は[Requirement E384-QUAL-001](../requirement.md)。本書を第二の判定値定義にしない。

### D. 参照環境を能力境界付きで事前固定する

従来のfingerprintだけでは、最初から高性能環境を選んだ場合のhardware escalationを判定できない。E384-QUAL-001に標準Linux runner classとCPU/RAMの能力上限、基準CIとの比較、測定前freezeを追加した。

具体image、collector、capの実現方法は#396の詳細化で選ぶが、能力上限をそこで変更しない。比較不能・制限不能・観測後の変更をadmission failureとする。現時点でLinux性能目標の達成を実測したとは主張しない。

## 4. Issue粒度の評価

**三Issueを維持する。** #392はlifecycle出力、#395は既知失敗ゼロのcurrent-policy出力、#396は最終gate/policy出力をそれぞれ持つ。各境界で自身の実装・検証・回復を完了でき、依存順にEpicへmergeできる。

- 一Issueへの再統合はlifecycle・既知失敗・CIの変更責務を再び一つに束ねるため採らない。
- 7–10個への再分割は現時点で独立受入の必要がなく、横断契約と統合待ちを増やすため採らない。
- 調査、意思決定、最後の検証だけをIssueにする案は採らない。現在の調査は本再評価で行い、検証は各Issueに含める。

## 5. 運用上の整合修正

- Formal `issue start` によるbranch/active選択と、Luna MaxへProduct実装を許可するgateを分離する。
- 親G0と依存確認、ユーザーの開始依頼後に正式startし、そのIssue branchで詳細化・独立reviewを行う。
- 新worktreeまたはユーザーが明示した既存worktree再利用を認める。Issue branchとEpic integration branchは分ける。
- 旧start/checkout保留は2026-09-08の明示的な開始依頼により解除した。ただし親G0・公開工程を省略せず、正式start後も詳細化の受入までは実装しない。
- Child plan/handoffは親の安全・受入契約を上書きしない。競合は停止条件とする。
- Rollback時も未mergeの作業をagentが自動削除しない。

## 6. 受入と残作業

1. 採用済みDEC-001/002と対象worktreeの境界を含む候補を固定し、同じGPT-6 Max reviewerで独立reviewする。P0/P1が残る間はG0を受理しない。
2. 文書リンク、metadata validation、ledger identity不変、変更範囲、HTML描画/配信を確認する。
3. 承認済み公開工程としてreviewed bytesをcommit/pushし、cleanなlocal/upstream/remoteの一致、外部freeze receipt、四つのGitHub body projection/readbackを確認する。
4. G0・依存・B0とユーザーの開始依頼を確認し、同じworktreeで#392を正式startする。
5. #392 branchでの詳細化と独立reviewを経てからProduct実装を許可する。正式startを実装検証の合格にしない。

`owner_decisions_required=[]`
