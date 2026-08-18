---
種別: 要件定義書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-18"
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

fresh target に対する現行 `spec-dock init`、`spec-dock init --force`、`spec-dock update` entrypoint を、`fresh` intent として `iss-00368` で成立した unified reconciliation engine へ移す。利用者は衝突のない repository に Desired Managed Assets を完全に provision でき、不明な parent/target state がある場合は write 前に保護される。fresh-only scaffold mutation engine、plan 外 callback、特殊な publish path は残さない。

## 背景

current implementation は `main()` の fresh admission から `_install_fresh_distribution()` 系を呼び、managed distribution plan と scaffold apply を組み合わせる。current tests は fresh/current catalog byte parity、second init rejection、unmanaged preservation、workbench seed semantics を固定する。D1 後も fresh flow が旧 mutation seam を使用し続ければ lifecycle symmetry と single-kernel contract が成立しない。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I369-R01 | fresh target に対する `spec-dock init [path]`、`spec-dock init --force [path]`、`spec-dock update [path]` の現行 command/flag/output/exit semantics を維持し、いずれも fresh intent として D1 の service/contract/action/kernel/journal/result へ追加する。 |
| I369-R02 | fresh target、衝突なしの場合、current package の全 Desired Managed Assets、required directories、fresh-only seed assets、version/postcondition を作成する。 |
| I369-R03 | target root は存在する real directory でなければならず、managed boundary の parent/target collision、symlink、unsafe type、non-writable state、root rebind があれば write 0 件で block する。 |
| I369-R04 | repository root の既存 unrelated content を保持する。fresh provisioning authority は managed contract path に限定する。 |
| I369-R05 | prompt または backup は実際に mutation が必要な場合だけ発生する。read-only admission/assessment、block、no-op は prompt/backup/journal/stagingを作らない。 |
| I369-R06 | second `init` without `--force` は existing managed workspace を上書きせず、current public guidance に従い `update` または `--force` を案内する。 |
| I369-R07 | partial failure は fresh intent、root、plan digest、exact pre/post identity に束縛した journal を保持し、同じ authority だけが resume できる。 |
| I369-R08 | fresh retry から update/init-force/deprovision/purge へ intent を変更して resume できない。 |
| I369-R09 | fresh-only workbench/template seed behavior は explicit Distribution Contract として表現し、update/init-force へ暗黙 backfill しない。 |
| I369-R10 | completion 後、provider catalog と installed fresh consumer の managed files/bytes/modes/symlinks が一致する。 |

## スコープ

### 対象

- fresh workspace admission
- fresh target の `init` / `init --force` / `update` entrypoint normalization と compatibility
- fresh desired asset and directory policy
- current fresh-only seed behavior
- collision/non-writable/symlink/root safety
- mutation-required prompt/backup boundary
- fresh journal/resume/postcondition
- old fresh scaffold mutation seam の削除
- fresh CLI and package byte-parity tests

### 対象外

- recognized update/init-force contract の再設計
- deprovision、history purge
- final all-surface/platform parity（`iss-00372`）
- public command/flag追加
- arbitrary project scaffolding feature
- Windows support

## 失敗・境界条件

- managed destination の final component または parent が symlink/unsafe type の場合、follow/replace しない。
- repository root の unrelated file/dir は fresh plan の actionに含めない。
- stage/journal create failure は managed target mutation 0 とする。
- create action 前に destination が出現した場合は no-replace で停止し、上書きしない。
- directory creation 後に later action が失敗した場合、journaled forward recoveryを行う。unknown contentを含むdirectoryをcleanupしない。
- fresh operation の legacy retry markerを別 intentでconsumeしない。
- no-follow/lock capabilityがないplatformはwrite前に停止する。

## 受け入れ条件

1. fresh target の `init`、`init --force`、`update` が同じ fresh intent として D1のservice、action grammar、kernel、journal、ProcessResultを使用し、entrypointごとの現行 output/exit semanticsをgolden testで維持する。
2. SC-FRESH-01相当のfresh targetでcurrent catalogとfresh-only seedを完全作成し、postconditionがadopt-onlyとなる。
3. SC-FRESH-02相当のparent/target collision、unsafe type、symlink、non-writable/root-rebindでwrite 0件となる。
4. unrelated root contentとauthority外unknown contentがbyte-identicalに保持される。
5. no-write pathでprompt、backup、journal、stagingが発生しない。
6. target appearance、provider mutation、staging failure、checkpoint failureからsame-plan retryが収束するか、typed blockとなる。
7. second init without forceはmutationせずcurrent guidanceを返す。
8. recognized target のupdate/init-forceがfresh-only workbench seedをbackfillしないcurrent semanticsを維持する。
9. fresh flowの`scaffold_applier`、別recursive copy、別publish shortcutが削除される。
10. focused fresh tests、`test_managed_distribution.py`、`test_init_update.py` affected testsが成功する。

## 制約・前提

- dependency `iss-00368` のjournal protocolとkernel safety contractを変更する場合は、D1 testsとEpic Designを同時更新する。
- recognized target の `init --force` behavior は D1 の ownerであり再設計しない。一方、fresh target の `init --force` と `update` が現行どおり fresh provisioningへ進む compatibility routeは本Issueがownerとなる。
- current fresh-only seed assetの実体はpackage contractから確認し、pathname推測で追加しない。
- whole-operation rollbackはnon-goalであり、per-action atomicityとforward recoveryを使う。
