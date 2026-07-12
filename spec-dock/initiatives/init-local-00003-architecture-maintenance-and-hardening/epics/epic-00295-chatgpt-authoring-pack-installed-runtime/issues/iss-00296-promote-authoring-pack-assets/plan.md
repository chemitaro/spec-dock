---
種別: 実装計画書（Issue）
ID: "iss-00296"
タイトル: "Authoring Pack Assets"
関連GitHub: ["#296"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00296 Authoring Pack Assets — 実装計画

## 実装ステップ

1. 現在の root `scripts/authoring-pack/` の file inventory を確認する。
2. `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` を作成し、root helper scripts を provider-side にコピーする。
3. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/__init__.py` を追加する。
4. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/__init__.py` を追加する。
5. provider-side `src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md` は root README の dogfood-only 文言をコピーせず、provider-side source-of-truth / installed asset surface として新規に記述する。
6. root `scripts/authoring-pack/README.md` に、root helper が compatibility / dogfood developer surface であり、provider-side source of truth が別にあることを追記する。
7. Issue `report.md` に draft adoption、採用しなかった draft claim、変更 inventory、検証結果、PR delivery defer を記録する。
8. 検証コマンドを実行する。

## 変更対象

- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/__init__.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/__init__.py`
- `scripts/authoring-pack/README.md`
- `spec-dock/active/issue/report.md`
- 必要に応じて `spec-dock/active/issue/{requirement,design,plan}.md`

## 変更しないもの

- runtime command parser / dispatcher
- GitHub sync preflight logic
- backend invocation adapter behavior
- ZIP review / stage implementation
- installed skill docs
- `.assurance.json` generation policy
- PR delivery

## 検証コマンド

```bash
find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f | sort
python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py
./spec-dock/scripts/spec-dock validate
uvx --from . spec-dock init /private/tmp/specdock-authoring-pack-init-smoke
```


## Step Closure Contract

| step | close condition | verification | report evidence destination |
|---|---|---|---|
| S01 | root helper inventory と provider target directory を確認する | `find scripts/authoring-pack -maxdepth 1 -type f | sort` | `report.md` 実装記録 |
| S02 | provider-side `authoring-pack` helper inventory を配置する | `find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f | sort` | `report.md` 実装記録 |
| S03 | application/domain package boundary を追加する | `test -f src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/__init__.py` and `test -f src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/__init__.py` | `report.md` 実装記録 |
| S04 | provider README を installed asset surface として記述し、root README を compatibility / dogfood surface として記述する | `rg -n "source of truth|compatibility|provider-side|installed asset" scripts/authoring-pack/README.md src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md` | `report.md` 実装記録 |
| S05 | provider-side copied scripts の構文と SpecDock tree を検証する | `python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py` and `./spec-dock/scripts/spec-dock validate` | `report.md` 検証結果 |
| S06 | provider asset が `spec-dock init` で consumer workspace に届くことを確認する | `uvx --from . spec-dock init /private/tmp/specdock-authoring-pack-init-smoke` and `test -f /private/tmp/specdock-authoring-pack-init-smoke/spec-dock/scripts/authoring-pack/README.md` | `report.md` 検証結果 |

## 具体テストケース

| id | required | evidence level | command |
|---|---|---|---|
| TC-001 | yes | inspection | `find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f | sort` |
| TC-002 | yes | command | `python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py` |
| TC-003 | yes | command | `./spec-dock/scripts/spec-dock validate` |
| TC-004 | yes | inspection | `rg -n "source of truth|compatibility|provider-side|installed asset" scripts/authoring-pack/README.md src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md` |
| TC-005 | yes | command | `uvx --from . spec-dock init /private/tmp/specdock-authoring-pack-init-smoke` and `test -f /private/tmp/specdock-authoring-pack-init-smoke/spec-dock/scripts/authoring-pack/README.md` |

## Reviewer / no-review rationale

- `spec-reviewer` は実装前の requirement/design/plan gate として必要。
- code-review / qa-review はこの Issue の local completion 後に、変更差分と検証結果を対象に確認する。
- 中間 Issue のため PR delivery reviewer gate は `iss-00307` に defer する。

## 完了条件

- provider-side helper inventory が存在する。
- application/domain package boundary が存在する。
- provider README が installed asset / source-of-truth 文言を持ち、root README が compatibility / dogfood surface 文言を持つ。
- temp consumer workspace への `spec-dock init` で provider-side helper が配布される。
- 検証コマンドが成功する。
- `report.md` に local completion evidence と no-per-Issue-PR defer evidence が残る。

## Relay / PR delivery

この Issue は中間 Issue であるため、個別 PR は作成しない。実装完了後は `issue finish` し、次の `iss-00297` へ進む。Epic 単位の PR delivery は final quality gate Issue `iss-00307` に集約する。
