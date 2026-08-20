---
種別: 要件定義書（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
状態: "planned"
最終更新: "2026-08-21"
親: ["epic-00365", "init-local-00003"]
---

# iss-00368 Recognized Workspace Reconciliation — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

recognized SpecDock workspace に対する `spec-dock update` と `spec-dock init --force` を、一つの read-only assessment、executable plan、journaled execution、typed outcome を通る end-to-end flow にする。利用者は current/historical ownership が証明できる managed asset だけを安全に reconcile でき、unknown/modified/unsafe state が一件でもあれば workspace 全体が write 前に保護される。

## 背景

exact commit `51a0586f8eb02f622f386a1fe32f15d90fcac4bc` では、recognized workspace admission、current/historical catalog、target snapshots、`build_distribution_plan()`、`apply_distribution_plan()`、`.distribution-retry.json` が存在し、current tests は多くの safety case を固定している。一方で orchestration、scaffold refresh callback、marker phase transition、version write、post-verify が複数 seam に分かれ、plan action だけでは operation 全体の mutation authority と recovery state を説明できない。

本 Issue は horizontal foundation だけを作らない。`update` と `init --force` が新 contract を実際に使用し、対象 legacy path を同じ Issue 内で削除した状態までを価値とする。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I368-R01 | `update` と `init --force` は同じ recognized-workspace intent policy と operation service を使う。public command/flag は変更しない。 |
| I368-R02 | current exact match は adopt、missing desired asset は create、proven historical match は upgrade、release catalog から外れた proven-owned asset は prune として評価できる。current content と safe regular single-link identity を証明できる mode-only drift は desired mode への journaled repair とする。 |
| I368-R03 | unknown current collision、modified content、ownership/content を証明できない mode drift、unproven obsolete target、unsafe file type、symlink、hardlink、parent symlink、root/parent rebind が一件でもあれば write 0 件で operation 全体を block する。 |
| I368-R04 | user-owned initiatives、workbench payload、authority 外 unknown sibling を保持する。managed root 内という理由だけで ownership を推測しない。 |
| I368-R05 | assessment と plan construction は marker、backup、staging、version file、managed target を変更しない。 |
| I368-R06 | apply 開始前に root/intent/contract/plan digest に束縛した Operation Journal を作り、各 action の exact precondition と expected postcondition を記録する。 |
| I368-R07 | partial failure 後は same root、same intent、same authority、same reconstructable plan、compatible protocol だけが resume できる。exact pre-action SHA または expected post-action identity と一致しない action は自動実行しない。 |
| I368-R08 | `.distribution-retry.json` は exact conversion または限定 compatibility resume が証明できる場合だけ受け入れる。different root/package/operation、malformed、dual marker、plan mismatch は write 前に拒否する。 |
| I368-R09 | operation 完了時は desired managed assets と version/postcondition を再評価し、成功後だけ journal/staging を完了する。 |
| I368-R10 | human output と exit behavior は現行 `update` / `init --force` semantics を維持し、error diagnostic は repository-relative path と stable reason に限定する。 |
| I368-R11 | recognized mutation の排他境界は root operation lock に協調する SpecDock writer とする。lock 保持中も各 filesystem mutation 境界で no-follow identity、content、link topology、parent closed set を再検証し、観測した外部変更は fail closed にする。同一 UID の非協調 process が advisory lock を無視し、最後の検証と単一 pathname syscall の間だけ private recovery name を差し替える挙動は保証対象外とする。 |

## スコープ

### 対象

- recognized current/historical workspace admission
- recognized target の `update` と `init --force`
- desired/current/historical/obsolete ownership assessment
- common action grammar の最小 end-to-end subset
- Operation Journal protocol の初期 version
- descriptor-bound filesystem kernel の recognized flow に必要な subset
- `.distribution-retry.json` migration/compatibility/fail-closed behavior
- typed result と existing text/exit mapping
- current recognized-flow safety tests の移植・拡張

### 対象外

- fresh target の `init` / `init --force` / `update` cutover（`iss-00369`）
- deprovision（`iss-00370`）
- history purge（`iss-00371`）
- all-surface/platform parity の最終確定（`iss-00372`）
- public JSON への新 schema 導入
- current Full Regression failure 修復
- `.meta.json`、node title/path の変更

## 失敗・境界条件

- D1 の recognized service は、recognized workspace と証明できない target を fresh へ推測 fallback せず operation-specific diagnostic を返す。public CLI が観測した fresh target に対する既存 `init` / `init --force` / `update` compatibility route は D2 の owner とし、この Issue では挙動を変更しない。
- assessment 後に provider asset bytes/mode、root、parent、target が変わった場合は apply を停止する。
- journal create/publish に失敗した場合、managed target mutation は 0 件である。
- action publish と checkpoint の間で crash した場合、resume は exact pre/post identity から状態を一意判定する。曖昧なら block する。
- stale staging entry は journal に記録された exact lease identity と一致する場合だけ cleanup する。stage-like unknown sibling は保持する。
- recognized service より前に読む `.agent` / `.work` / `active` / `initiatives` の preserved state は no-follow descriptor と single-link file identity に束縛する。unsafe boundary、hard link、または capture 後の rebind は guard/journal/target write 0 で block する。
- originally missing parent の journal binding は recovery hint として扱い、action checkpoint、exact lease、pre/post identity から説明できない unknown child が一件でもあれば descendant mutation 前に block する。
- root operation lock は SpecDock writer 間の operation-wide exclusion authority である。外部 process については mutation 境界で観測できた rebind、replacement、unknown child を block するが、同一 UID の非協調 process による検証後かつ単一 pathname syscall 前の差し替えまでを atomic CAS として保証しない。
- current marker が newer package/operation で same plan を証明できない場合は変換しない。
- `init --force` であっても unknown/modified content を force overwrite しない。

## 受け入れ条件

1. recognized target の `update` と `init --force` が新 operation service を end-to-end 使用する。
2. SC-UPDATE-01〜04 相当の current/historical/missing/unknown/unsafe matrixに加え、current-content mode-only repair と unproven/unsafe mode drift block が focused tests と CLI tests で成功する。
3. blocker が一件でもある plan は journal、staging、backup、version file、managed asset を一切変更しない。
4. same-root/same-plan partial failure fixture が journal checkpoint から再実行して desired postcondition に収束する。
5. root、intent、authority、plan digest、protocol、exact pre-action SHA mismatch fixture が write 0 件で停止する。
6. legacy `.distribution-retry.json` の safe case と malformed/cross-root/different-operation/dual-marker case がそれぞれ explicit behavior を持つ。
7. provider change、target appearance、parent/root replacement、hardlink/symlink の current negative tests が維持される。
8. `update` / `init --force` 対象の legacy scaffold callback、marker transition、plan 外 mutation route が削除され、同じ flow を二経路で実行できない。
9. `tests/unit/infra/test_managed_distribution.py` と `tests/unit/infra/test_init_update.py` の affected tests が成功する。
10. fresh target の `init` / `init --force` / `update`、uninstall、purge の public behavior はこの Issue で変更せず、fresh entrypoint matrix の characterization test を D2 へ引き渡す。
11. `update` / `init --force` は recognized mutation と terminal cleanup を同じ root operation lock 内で実行し、lock に協調する concurrent SpecDock invocation を直列化する。既存の target/parent/created-parent/stage interposition tests は mutation 境界での replacement と unknown child を引き続き preserve-and-block する。

## 制約・前提

- parent Epic Requirement と accepted ADR の pre-write fail-closed、forward recovery、authority non-expansion を継承する。
- current safety behavior を弱めるために test expectation を更新しない。意図した contract change が必要なら Epic Requirement/Design に戻す。
- current `.distribution-retry.json` field は implementation factとして扱うが、legacy schema を将来の public contract にしない。
- regular-file recovery は exact SHA-256 を使い、historical catalog entry の position を identity として使わない。
- Windows support と generic transaction framework は含めない。
- advisory root lock を無視する同一 UID process に対する kernel-enforced namespace isolation、delete-by-inode、または native privileged helper は含めない。
