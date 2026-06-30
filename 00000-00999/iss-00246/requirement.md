---
種別: 要件定義書（Issue）
ID: "iss-00246"
タイトル: "Dogfooding Update Runtime Mirror Sync"
関連GitHub: ["#246"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00067", "init-local-00003"]
---

# iss-00246 Dogfooding Update Runtime Mirror Sync — Issue 要件定義

## 1. 背景

GitHub Issue #246 は、SpecDock 自身を SpecDock で管理する dogfooding repo において、provider 側 runtime を変更した後に `uvx --from . spec-dock update .` が成功したにもかかわらず、consumer 側 dogfooding workspace の runtime mirror が期待どおり更新されなかった観測から起票された。

SpecDock repo では、provider 側の正本は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` にあり、dogfooding consumer 側の mirror は `spec-dock/scripts/spec_dock_runtime/**` にある。Issue #244 の検証では、provider 側の `application/workflow.py` が新しい判定順になっていた一方、dogfooding mirror 側は古い判定順のままであり、`./spec-dock/scripts/spec-dock guidance issue-execution` が旧挙動を返し続けた。手動で provider runtime を dogfooding mirror へ同期すると期待する guidance 出力に戻った。

この Issue では、`spec-dock update` が dogfooding runtime mirror を更新する契約と検証を明確にし、更新成功に見える状態で provider/runtime mirror drift が残ることを防ぐ。

## 2. 目的

`spec-dock update` と dogfooding parity 検証を、provider runtime 変更後の consumer mirror drift を検出または解消できる状態にする。

## 3. スコープ

### 3.1 対象

- provider runtime 正本: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- dogfooding runtime mirror: `spec-dock/scripts/spec_dock_runtime/**`
- installer/update 経路: `spec-dock update <target>` と、local checkout/package 由来の `uvx --from . spec-dock update <target>` 相当の経路
- update/parity の regression test
- 必要な場合に限る installer/package-data の最小修正

### 3.2 非対象

- runtime wrapper が参照する upstream 更新元の設計変更
- GitHub Issue #246 の close やラベル変更など GitHub 上の状態変更
- provider runtime の機能仕様そのものの変更
- 手動コピーを恒久解とする運用手順化
- 既存の `spec-dock/initiatives/**` や user-authored issue/epic data の移行

## 4. 要件

### RQ-001 Runtime mirror update contract

`spec-dock update <target>` は、managed scaffold の一部である `spec-dock/scripts/spec_dock_runtime/**` を provider 正本 `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` から更新できなければならない。

### RQ-002 No silent runtime drift

provider runtime と dogfooding runtime mirror の内容がずれている状態を、更新成功または検証成功として見逃してはならない。少なくとも regression test は drift を失敗として検出できなければならない。

### RQ-003 Existing managed update behavior preservation

runtime mirror 更新のために、既存の managed update 契約を壊してはならない。特に `spec-dock/initiatives/**`、active metadata、user-authored issue documents、unmanaged files は update によって失われてはならない。

### RQ-004 Generated cache exclusion

`__pycache__`、`.pyc` などの generated Python cache は provider から consumer mirror へコピーされてはならず、parity 検証の対象にもしてはならない。

### RQ-005 Local checkout/package update coverage

Issue #246 の観測経路である `uvx --from . spec-dock update .` と同等の local checkout/package 由来 update が、runtime asset を含めて更新できることを検証可能にする。

### RQ-006 Root-cause distinction

実装時の調査では、少なくとも次の可能性を切り分ける。

- installer update が runtime managed directory を同期していない
- package data に runtime asset が含まれていない
- local `uvx --from .` / build cache / installation 由来の差異がある
- installer 挙動は正しいが、dogfooding mirror parity test が不完全で drift を検出できなかった

## 5. 受け入れ条件

### AC-001 Stale runtime file refresh

Given: consumer target の `spec-dock/scripts/spec_dock_runtime/**` 内に、provider 正本と異なる stale file がある。

When: current checkout/package 由来の `spec-dock update <target>` を実行する。

Then: stale file は provider 正本と byte-level で一致する内容へ更新される。

### AC-002 Complete checked-in dogfooding runtime parity

Given: provider runtime 正本に Python/runtime file が存在する。

When: checked-in dogfooding runtime mirror の parity test を実行する。

Then: generated cache を除く全 runtime file の存在と内容一致が検証され、subset map から漏れた新規 file は成功扱いにならない。

### AC-003 Managed update preservation

Given: consumer target に existing initiative data、active metadata、unmanaged file がある。

When: runtime mirror を含む update を実行する。

Then: user-authored data と unmanaged file は保持され、managed runtime file のみ provider 正本へ更新される。

### AC-004 Cache exclusion

Given: provider runtime tree に `__pycache__` や `.pyc` が存在する。

When: update/parity 検証を実行する。

Then: generated cache は consumer mirror にコピーされず、parity failure の対象にもならない。

### AC-005 Package/local update smoke

Given: local checkout または build artifact から installer を実行できる。

When: isolated target の runtime file を stale にして update を実行する。

Then: installed/package 経路でも runtime file が provider 正本と一致する。

### AC-006 Evidence retained in issue report

Issue 完了時には、どの root cause が確認されたか、どの検証で AC-001 から AC-005 を満たしたかを `report.md` に記録する。

## 6. 制約

- provider 側の implementation source of truth は `src/spec_dock/assets/spec_dock/**` とする。
- dogfooding workspace `spec-dock/**` は validation/consumer mirror として扱い、provider 実装の正本にしない。
- 既存の update preservation 契約を弱めない。
- regression test は hermetic を基本とし、live GitHub network に依存しない。
- 実装差分は Issue #246 の runtime mirror update/parity に閉じる。

## 7. 成功条件

- `spec-dock update` が stale runtime mirror を更新できることがテストで示されている。
- checked-in dogfooding runtime mirror parity が subset ではなく runtime tree 全体を対象にしている。
- generated cache を除外したまま update/parity が成立する。
- 既存の user-authored dogfooding data preservation が維持されている。
- root cause と検証結果が `report.md` に残っている。

## 8. 未確定事項

現時点でユーザー確認が必要な要求上の未確定事項はない。残る不確実性は実装時に切り分ける技術調査事項である。
