---
種別: 要件定義書（Epic）
ID: "epic-00365"
タイトル: "SpecDock Distribution Reconciliation and Recovery Architecture"
関連GitHub: ["#365"]
状態: "planned"
最終更新: "2026-08-18"
親: ["init-local-00003"]
---

# epic-00365 SpecDock Distribution Reconciliation and Recovery Architecture — 要件定義

詳細: [Requirement Guide](../../../../docs/authoring/requirement.md)

## 目的

SpecDock の managed distribution lifecycle を、公開操作ごとに分裂した処理ではなく、一つの照合・実行・回復契約として成立させる。利用者は既存の `init`、`init --force`、`update`、`uninstall` surface を維持したまま、処理開始前に workspace 全体の安全性を確認でき、部分失敗後は権限を拡大せずに forward recovery できる。

Epic の一貫した成果は、次の観測可能な流れである。

```text
Desired Managed Assets
+ Historical Ownership Evidence
+ Workspace Observation
+ Explicit Operation Intent
  -> read-only Workspace Assessment
  -> blocker のない Executable Mutation Plan
  -> descriptor-bound execution と Operation Journal
  -> typed postcondition outcome または fail-closed recovery state
```

## 背景

exact repository commit `51a0586f8eb02f622f386a1fe32f15d90fcac4bc` では、`src/spec_dock/managed_distribution.py` が current/historical catalog、admission、read-only classification、plan、identity-checked apply を持ち、`src/spec_dock/cli.py` が installer command の orchestration を担っている。現行 tests は unknown/modified content、symlink、hardlink、parent replacement、root rebind、staging failure、dry-run、spec history preservation などの安全性を広く固定している。

一方、同じ commit では次の lifecycle 非対称が残る。

- `update` と `init --force` は `DistributionAction` / `DistributionPlan` / `apply_distribution_plan()` を使うが、fresh provisioning には scaffold callback を含む別 mutation seam がある。
- deprovision と history purge は `cli.py` 内の `_UninstallAction`、`_build_uninstall_plan()`、`_apply_uninstall_plan()`、独自 recursive mutation を使う。
- update/init-force 系は `spec-dock/.distribution-retry.json`、uninstall 系は `spec-dock/.uninstall-retry.json` を使い、回復 authority と checkpoint の意味が一致しない。
- `cli.py` が `managed_distribution.py` の private `_rename_distribution_no_replace` を import し、filesystem mechanism の ownership が分散している。

この Epic は現行安全性を弱めず、責務と recovery protocol を統合する。行数削減や一般的な refactor 自体は目的にしない。

## 観測可能な要件

| ID | 要件 |
|---|---|
| E365-R01 | `init`、`init --force`、`update`、managed distribution deprovision、explicit spec history purge は、一つの operation model、action grammar、filesystem safety boundary、journal protocol、typed outcome を共有する。 |
| E365-R02 | eligibility、workspace observation、ownership assessment、plan construction は read-only であり、blocker が一件でもあれば最初の write より前に operation 全体を停止する。safe subset の部分適用はしない。 |
| E365-R03 | unknown、modified、user-owned content は、利用者が明示した spec history purge authority の境界内を除き、保持される。pathname や親 directory だけで ownership を推測しない。 |
| E365-R04 | deprovision と spec history purge は同じ engine を使うが、別 intent、別 authority、別 postcondition とする。`update` や通常の deprovision が history purge を暗黙実行してはならない。 |
| E365-R05 | mutation 開始後の durable state は Operation Journal に記録する。mutation resume は同じ root、intent、再構成可能な同じ plan、互換 protocol、開始時と exact に一致する authority に限定し、mismatch は write 前に拒否する。より低い authority の invocation は read-only inspection と diagnostic だけを許可し、checkpoint を進めない。 |
| E365-R06 | file action の precondition は exact no-follow identity で照合する。regular file の回復判断は exact pre-action SHA-256 に束縛し、catalog index、配列位置、pathname 推測を identity として使わない。 |
| E365-R07 | root、parent chain、target、staging entry は mutation 直前にも descriptor-relative に再検証し、symlink traversal、hardlink mutation、root/parent rebind、external path mutation を拒否する。 |
| E365-R08 | public CLI command、flag、exit behavior、利用者所有 data、安全性、および現行 `uninstall --json` schema version 1 の意味を維持する。private Python API と legacy marker schema は公開互換対象にしない。 |
| E365-R09 | `init` の prompt または backup は、実際に mutation が必要な場合だけ発生する。read-only assessment と dry-run は prompt、backup、marker、staging を作らない。 |
| E365-R10 | `update` は recognized workspace の missing/current/historical managed asset を照合し、release catalog から外れた proven-owned asset を prune できる。unknown/modified collision があれば全体を block する。 |
| E365-R11 | `uninstall` は dry-run を既定とし、mutation には `--apply` と exactly one of `--keep-specs` / `--remove-specs` を要求する。history purge は既存の explicit `--remove-specs` authority 以外から開始しない。 |
| E365-R12 | human text、JSON、exit code は同じ typed result から導出し、planned/completed/blocked/partial-recovery-required/error を矛盾なく表現する。diagnostic は repository-relative path と非機密情報に限定する。 |
| E365-R13 | provider checkout、dogfooding workspace、wheel、sdist、fresh consumer が同じ distribution contract を持つ。Linux と macOS の両方で safety/failure matrix を検証し、required capability がない platform は write 前に停止する。 |
| E365-R14 | Epic の canonical title は本書の title とする。ただし既存 `.meta.json` の旧 title と node path は SpecDock CLI 管理対象であり、この Epic では手編集、rename、ID変更をしない。 |

## スコープ

### 対象

- recognized workspace に対する `update` と `init --force` の reconciliation
- fresh target に対する `init`、`init --force`、`update` の現行 entrypoint semantics を維持した provisioning
- current `uninstall --apply --keep-specs` 相当の managed distribution deprovision
- current `uninstall --apply --remove-specs` 相当の explicit spec history purge
- desired asset、historical ownership evidence、workspace observation、intent policy、preservation policy、postcondition の一貫した契約
- operation admission、read-only assessment、executable plan、descriptor-bound mutation、journal、resume、postcondition、typed diagnostics
- provider checkout、dogfooding workspace、wheel、sdist、fresh consumer の distribution parity
- Linux と macOS の検証可能な contract
- five fixed Issue slices `iss-00368` から `iss-00372`

### 対象外

- 新しい product feature、公開 command、公開 flag
- Windows 対応
- Full Regression の既存 failure 修復、waiver 解消、baseline burn-down
- AI model、browser session、iterative review campaign、人間 adjudication の orchestration
- distribution 以外の runtime 全般の再設計
- 汎用 filesystem transaction framework
- operation 全体を元に戻す原子的 rollback 保証
- private Python API または legacy marker schema の恒久互換
- 行数削減、命名整理、一般 refactor だけを目的とする作業
- Epic / Issue node の追加、削除、rename、ID変更

### Issue 境界

| Issue | end-to-end value |
|---|---|
| `iss-00368` | recognized workspace の `update` / `init --force` を統合 engine へ移す。 |
| `iss-00369` | fresh target の `init` / `init --force` / `update` を fresh intent として同じ engine へ移し、別 scaffold mutation engine をなくす。 |
| `iss-00370` | managed distribution deprovision を同じ grammar/kernel/journal へ移し、spec history を保持する。 |
| `iss-00371` | explicit spec history purge を別 authority として同じ engine へ移す。 |
| `iss-00372` | legacy seam を物理的に除去し、distribution surface と platform parity を確定する。 |

## 失敗・境界条件

| 条件 | 必須結果 |
|---|---|
| current/historical identity を一意に証明できない | diagnostic を返し、write 0 件で停止する。 |
| current content と safe regular single-link identity を証明できる managed file の mode-only drift | desired mode への journaled repair action とし、適用前後の content/identity/mode を再検証する。 |
| unknown、modified、ownership/content を証明できない mode drift、unsafe file type、symlink、hardlink、unsafe parent | path ごとの reason を返し、operation 全体を block する。 |
| root または parent chain が assessment 後に変わる | mutation 直前の identity check で停止し、外部 path を変更しない。 |
| partial failure | completed checkpoint と staging lease を journal に保持し、postcondition 成功前に journal を消さない。 |
| root、intent、plan digest、protocol、authority が journal と不一致 | write 前に停止し、journal/staging を推測変更しない。 |
| retry が deprovision から purge への権限拡大を要求する | 拒否する。 |
| legacy marker が malformed、dual、または情報不足 | exact conversion を行わず、typed manual-recovery guidance とともに fail closed する。 |
| required no-follow/descriptor capability がない | write 前に stable diagnostic で停止する。Windows は non-goal とする。 |
| Full Regression に既存 failure がある | exact candidate SHA で再計測・分類するが、旧調査の件数を現在値として扱わず、この Epic で新規 attributable failure を追加しない。 |

## 受け入れ条件

1. 全公開 intent が一つの operation service を通り、operation 固有の第二 action grammar が存在しない。
2. `cli.py` は parse、package asset location、dispatch、human/JSON render、exit mapping に限定され、ownership policy、filesystem recursion、journal transition、staging cleanup を持たない。
3. mutation は一つの descriptor-bound filesystem kernel に集約される。
4. `update` / `init --force` は current match、historical match、missing、obsolete proven-owned、unknown/modified、current-content mode-only repair、unproven/unsafe mode drift block、symlink、hardlink、parent symlink、root rebind を含む matrix を満たす。
5. fresh target に対する `init`、`init --force`、`update` は現行 command/flag/exit semantics を維持して同じ fresh intent へ正規化され、衝突なしで desired assets を作成し、不明な parent/target collision では write 0 件で停止する。
6. deprovision は tooling/generated/owned managed assets を除去し、spec history と authority 外 unknown content を保持する。
7. purge は `--apply --remove-specs` の explicit authority でのみ spec history を削除し、retry で authority を拡大できない。
8. partial failure 後、same-root/same-intent/exact-same-authority/same-plan/compatible-protocol の再実行が checkpoint から収束する。より低い authority は read-only inspection に留まり、その他の mismatch とともに mutation write 0 件で block される。
9. legacy scaffold/uninstall mutation helper、二重 retry writer、private rename import、plan 外 mutation fallback seam が absence test で検出されない。
10. `uninstall --json` は schema version 1 の現行 semantic contract を維持し、stdout に exactly one JSON object を出す。
11. provider checkout、dogfood、wheel、sdist、fresh consumer の inventory/bytes/behavior parity と、Linux/macOS の focused distribution suite が確認される。
12. affected fast tests と対象 full-regression tests が成功し、exact pre-Epic baseline と比較して Epic attributable new failure が 0 件である。Full Regression 全体の既存 unrelated failure 修復は完了条件に含めない。
13. D1〜D4 の public flow は各 Issue の終了時に対象 legacy path を hard cutover し、D5 は legacy absence と parity evidence の確定だけを担う。

## 制約・前提

- repository implementation fact の基準は commit `51a0586f8eb02f622f386a1fe32f15d90fcac4bc` とする。
- Issue 360 の「26 failures」は旧 SHA の historical seed であり、現在値ではない。
- accepted ADR `20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md` が、unified operation model、pre-write fail-closed、journaled forward recovery、authority separation、vertical hard cutover の durable decision authority である。
- existing node path と `.meta.json` の旧 title は手編集しない。本書、Design、Plan、Issue docs、ADR、HTML の内容だけを destination へ置換する。
- Linux/macOS の filesystem semantics は実装・テストで確認する。未実行の platform behavior を「確認済み」と断定しない。
- public compatibility は command/flag/data/JSON semantics に適用し、private symbol や internal journal schema を固定しない。
