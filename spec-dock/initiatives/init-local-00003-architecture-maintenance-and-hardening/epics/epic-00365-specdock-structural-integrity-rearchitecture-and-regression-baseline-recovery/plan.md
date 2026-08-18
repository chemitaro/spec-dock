---
種別: 計画書（Epic）
ID: "epic-00365"
タイトル: "SpecDock Distribution Reconciliation and Recovery Architecture"
関連GitHub: ["#365"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00365 SpecDock Distribution Reconciliation and Recovery Architecture — 計画

詳細: [Scope Layering Guide](../../../../docs/authoring/scope-layering.md)

## 目標

five fixed Issue slices を順に統合し、SpecDock の全 managed distribution public flow を一つの assessment/action/kernel/journal/result contract へ hard cutover する。各 Issue は単独で観測可能な end-to-end value を完成させ、未接続の horizontal foundation だけを残さない。

## 順序・依存

| 順序 | Issue | dependency | 完成時の handoff |
|---|---|---|---|
| D1 | `iss-00368` Recognized Workspace Reconciliation | なし | recognized target の `update` / `init --force` が新 engine、journal、typed result を end-to-end 使用し、対象 legacy path が削除される。 |
| D2 | `iss-00369` Fresh Distribution Provisioning | `iss-00368` | fresh target の `init` / `init --force` / `update` が fresh intent として D1 engine を使用し、別 scaffold mutation seam が fresh flow から削除される。 |
| D3 | `iss-00370` Managed Distribution Deprovision | `iss-00369` | default/`--keep-specs` dry-run と `uninstall --apply --keep-specs` が共通 grammar/kernel/journal を使用し、spec history を保持する。 |
| D4 | `iss-00371` Explicit Spec History Purge | `iss-00370` | `uninstall --remove-specs` dry-run/apply が別 authority として共通 engine を使用し、retry authority escalation を拒否する。 |
| D5 | `iss-00372` Distribution Hard Cutover And Parity | D1〜D4 | legacy seam absence、public/package/platform parity、migration/recovery docs を確定する。 |

D1〜D4 は strict linear dependency とする。D5 用の test inventory、CI feasibility、parity fixture preparation は読み取り専用または既存 behavior を変えない範囲で並行調査できるが、D5 の cutover assertion は D1〜D4 完了前に確定しない。

## 実装step

### D1 — Recognized Workspace Reconciliation

- current `update` / `init --force` safety behavior を characterization matrix として固定する。
- Distribution Contract、read-only Assessment、Executable Plan、Operation Journal、Descriptor-bound Kernel、ProcessResult を、この flow を完了できる最小範囲で成立させる。
- `.distribution-retry.json` の exact conversion/compatibility 条件と fail-closed 条件を実装する。
- `update` / `init --force` を新 service へ切り替え、対象 flow の scaffold callback、独自 marker transition、plan 外 mutation を削除する。

### D2 — Fresh Distribution Provisioning

- fresh-only desired assets、collision、directory creation、prompt/backup condition、postcondition を D1 contract へ追加する。
- fresh target に対する `init`、`init --force`、`update` の現行 entrypoint semantics を characterization し、すべてを `fresh` intent の新 service へ切り替える。
- fresh flow の別 scaffold mutation engine と特殊な publish shortcut を削除する。

### D3 — Managed Distribution Deprovision

- current default/`--keep-specs` dry-run、`--apply --keep-specs`、text/JSON semantics を characterization する。`--remove-specs` dry-run/apply は D4 の owner とする。
- tooling/generated/owned asset removal と spec history/unknown preservation を共通 action grammar へ追加する。
- current uninstall plan/apply/postverify を service/kernel/journal に移し、deprovision 対象 legacy helper を削除する。
- information-poor `.uninstall-retry.json` は推測変換せず、exactly safe な migration path または typed manual recovery を提供する。

### D4 — Explicit Spec History Purge

- existing `--remove-specs` dry-run と `--apply --remove-specs` を explicit purge intent/authority として model/journal/plan digest に束縛する。
- dry-run summary、path guard、pre-write blocker、postcondition、retry authority non-escalation を完成させる。
- purge flow の legacy branch を削除し、update/deprovision から purge へ到達する path がないことを test で固定する。

### D5 — Hard Cutover And Parity

- `_UninstallAction` 系、独自 recursive mutation、旧 marker writer、private rename import、`scaffold_applier`/blocked-path fallback が D1〜D4 で物理削除済みであることを検証する。production executable path または writer が残る場合は D5 で削除せず、owner Issue の未完了として completion を block する。
- dependency/import/symbol/AST test で CLI ownership boundary と single-kernel contract を固定する。
- provider checkout、dogfood、wheel、sdist、installed/fresh consumer の inventory/byte/behavior parity を確認する。
- focused distribution suite を Linux と macOS で実行する。
- README、migration、forward recovery、legacy marker guidance を current implementation と一致させる。

## 検証

### Verification ladder

1. 各 Issue の focused unit tests
2. `tests/unit/infra/test_managed_distribution.py`
3. `tests/unit/infra/test_init_update.py`
4. provider package/build/distribution parity tests
5. Linux/macOS focused CI
6. affected fast suite
7. `uv run pytest --run-full-regression` の exact SHA 再計測と attribution classification

Full Regression は unrelated known failure の修復を Epic completion condition にしない。旧 Issue 360 artifact の「26 failures」を current count として再利用せず、pre-Epic baseline SHA と candidate SHA の差分で Epic attributable new failure が 0 件であることを確認する。

### Cross-Issue completion sweep

- all public intent が single service を経由する。
- second action grammar が存在しない。
- CLI に ownership policy、recursive mutation、journal transition、staging cleanup がない。
- blocker 有り assessment から executable plan を作れない。
- exact pre-action SHA と plan digest が resume decision に使われる。
- deprovision/purge authority が分離される。
- public JSON schema version 1 semantics が維持される。
- legacy symbol/import/writer/fallback が absence test で検出されない。
- provider/dogfood/package/platform evidence が同じ candidate SHA に束縛される。

## rollback

### Code rollout

- 各 Issue は対象 flow の新 implementation と legacy path removal を同じ change set に含める。
- merge/release 前に focused tests と migration fixtures が失敗した場合、その Issue の code change を revert できる。
- runtime toggle や恒久 dual mode は作らない。

### Operation recovery

- new journal 作成前は code rollback が可能である。
- new journal 作成後は same/compatible newer package による forward recovery を正規経路とする。
- exact pre-action SHA、post-action identity、root/intent/authority/plan digest を照合できない状態では自動再実行・自動 rollback を行わない。
- whole-operation rollback は保証しない。partial failure は journal を保持し、manual intervention が必要な場合は repository-relative evidence と安全な停止状態を返す。

## exit / handoff

Epic の exit は次をすべて満たすこととする。

1. `iss-00368`〜`iss-00372` が固定した acceptance と strict Plan exit を満たす。
2. D1〜D4 の各 public flow が新 engine へ hard cutover し、旧 path が同じ Issue で削除済みである。
3. D5 が legacy seam absence、public contract parity、package surface parity、Linux/macOS evidence を確定する。
4. affected fast tests と targeted full-regression tests が成功する。
5. exact pre-Epic baseline と candidate の Full Regression 比較で、Epic attributable new failure が 0 件である。
6. remaining unrelated Full Regression failures は sibling Epic candidate への evidence として分類されるが、この task で新 node を作らない。
7. canonical Requirement/Design/Plan、accepted ADR、human-facing HTML、README/recovery guidance が実装と矛盾しない。
8. `.meta.json` の旧 title と node path は手編集されていない。

残余リスクの handoff は、journal protocol compatibility、legacy marker manual recovery、platform-specific syscall behavior、Full Regression unrelated failure ledger に限定する。新 product feature、Windows、AI review orchestration、generic transaction framework を handoff 名目で scope に戻さない。
