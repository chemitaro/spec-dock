---
種別: 設計書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00264 Future node scaffold artifacts default — 設計

## 目的と判断
New initiative / epic / issue の作成時に、future artifact surface として `artifacts/` を標準配置する。`discussions/` は legacy surface として既存 node と既存 command compatibility のために有効なまま残すが、新規 node scaffold の default directory からは外す。

この Issue は `iss-00263` で導入済みの `new artifact` command を前提に、node creation path の初期ディレクトリと rules symlink を切り替える。既存 node への migration、validation/sync の artifact/discussion parity、delegated authoring boundary の切替は後続 Issue に委ねる。

## 現行構造
- Runtime node creation:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `_rules_source_paths()` が kind ごとの rules source を返し、現状は `discussions.md` を含む。
  - `_rules_scaffold_specs()` が `dest_dir / "discussions" / "rules.md"` を生成対象に含める。
  - `execute_create_plan()` が template tree copy 後に rules symlink を作り、`.meta.json` を書く。
- Artifact setup:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`
  - `_rules_source_path()` は `docs/rules/<kind>/artifacts.md` を参照する。
  - `_preflight_artifacts_dir()` / `_preflight_artifacts_rules()` / `_ensure_artifacts_setup()` は `artifacts/` と `artifacts/rules.md` の安全検査と作成を担う。
- Provider assets:
  - `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/artifacts.md` は存在する。
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/` は requirement/design/plan/report の node canonical docs を配置するが、node-local `artifacts/` は template tree ではなく rules symlink creation path で materialize される。

## 変更方針
- `create_node.py` の node creation rules scaffold を `artifacts/rules.md` default に切り替える。
- initiative / epic が持つ child collection rules は維持する。
  - initiative: `epics/rules.md` は維持し、`discussions/rules.md` を `artifacts/rules.md` に置換する。
  - epic: `issues/rules.md` は維持し、`discussions/rules.md` を `artifacts/rules.md` に置換する。
  - issue: `discussions/rules.md` を `artifacts/rules.md` に置換する。
- `artifacts/rules.md` の source は `docs/rules/<kind>/artifacts.md` とし、既存の relative symlink preflight / creation contract を使う。
- 新規 node 作成後、`discussions/` は存在しないことを test で固定する。
- 既存 node 上の `discussions/` は update / runtime command で削除、移動、rename、symlink rewrite しない。

## 設計契約
| ID | 契約 | 対応 AC | 実装面 | 検証 |
|---|---|---|---|---|
| DES-264-001 | `new initiative` は `artifacts/rules.md` と `epics/rules.md` を作る | AC-264-001, AC-264-003 | `_rules_source_paths`, `_rules_scaffold_specs` | CLI runtime scaffold test |
| DES-264-002 | `new epic` は `artifacts/rules.md` と `issues/rules.md` を作る | AC-264-001, AC-264-003 | `_rules_source_paths`, `_rules_scaffold_specs` | CLI runtime scaffold test |
| DES-264-003 | `new issue` は `artifacts/rules.md` を作る | AC-264-001, AC-264-003 | `_rules_source_paths`, `_rules_scaffold_specs` | CLI runtime scaffold test |
| DES-264-004 | new node default は `discussions/` を作らない | AC-264-002 | rules scaffold spec と tests | absence assertion |
| DES-264-005 | `spec-dock update` は existing node-local `discussions/` contents を保持する | AC-264-004 | installer prune/update tests; no migration code | before/after preservation test |
| DES-264-006 | old-only / mixed layout はこの Issue で invalid 化しない | AC-264-005 | validation behavior は変更しない、必要なら regression test | validate old-only fixture |
| DES-264-007 | `new artifact` の old-node on-demand `artifacts/` setup は引き続き既存 `discussions/` を保持する | AC-264-004 | create_artifact_doc helpers are not weakened | existing regression retained |

## 安全境界
- 禁止:
  - 既存 node の bulk migration。
  - node-local `discussions/` の削除、移動、rename。
  - `new artifact` の command semantics 変更。
  - `new doc` の追加復活。
  - validation/sync/ADR mirror parity の本実装。
- 許可:
  - `create_node.py` の rules source/spec 切替。
  - scaffold expectations / tests の更新。
  - provider-side shipped docs/rules asset の参照確認。
  - dogfooding workspace は検証対象として扱い、provider source of truth と混同しない。

## フロー
1. User runs `new initiative` / `new epic` / `new issue`.
2. `plan_node_creation()` computes node path and canonical docs from existing templates.
3. `execute_create_plan()` resolves rules scaffold specs.
4. Preflight verifies `docs/rules/<kind>/artifacts.md` and child collection rules sources.
5. Template tree is copied.
6. Relative symlinks are created:
   - child collection rules where applicable.
   - `artifacts/rules.md`.
7. `.meta.json` is written and post-write guards run.
8. No `discussions/` directory is created unless another legacy/on-demand path explicitly creates it.

## テスト戦略
- Red / Green:
  - Existing scaffold assertions currently expect `discussions/rules.md` and absence of `artifacts/`; update them to fail first or add equivalent focused tests before implementation.
  - Add/adjust tests to assert `artifacts/rules.md` relative symlink target for initiative / epic / issue.
  - Add/adjust tests to assert `discussions/` absence for new node scaffold.
- Compatibility:
  - Preserve existing `test_new_artifact_old_node_setup_preserves_discussions`.
  - Add/adjust update test that node-local legacy `discussions/` contents survive `spec-dock update`.
  - Add old-only validation regression only if current validation lane can express it without taking over `iss-00265`.
- Test commands:
  - `uv run pytest tests/cli_runtime/test_new.py -k "rules_symlinks or new_nodes"`
  - `uv run pytest tests/cli_runtime/test_wrappers.py -k "rules_symlinks or new_artifact_numbering"`
  - `uv run pytest tests/unit/infra/test_init_update.py -k "legacy_artifacts_inside_existing_node_trees or artifact"`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest tests/unit/infra`
  - `./spec-dock/scripts/spec-dock validate`

## 後続 Issue への引き渡し
- `iss-00265`:
  - old-only / mixed / new layout の validation, sync, ADR mirror, projection parity を扱う。
  - この Issue で作る new scaffold fixture を後続検証の入力にする。
- `iss-00266`:
  - delegated authoring の output boundary を `artifacts/` direct child に移す。
- `iss-00267`:
  - workflow docs / shipped skills / agent guidance を `new artifact` と future `artifacts/` default に更新する。
