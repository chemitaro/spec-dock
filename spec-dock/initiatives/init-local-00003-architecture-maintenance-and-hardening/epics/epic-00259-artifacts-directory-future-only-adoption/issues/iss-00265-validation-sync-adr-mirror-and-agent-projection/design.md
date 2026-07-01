---
種別: 設計書（Issue）
ID: "iss-00265"
タイトル: "Validation sync ADR mirror and agent projection"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00265 Validation sync ADR mirror and agent projection — 設計

## 目的と判断
validate / sync / `.agent` projection / ADR mirror を future `artifacts/` に対応させる。ただし canonical docs、future artifacts、legacy discussions は別の surface として扱い、互換のために残る `discussions/` を暗黙 migration しない。

この Issue は `iss-00263` の `new artifact` command と `iss-00264` の new-node `artifacts/` default を前提に、runtime が old-only / new-only / mixed layout を同時に読める状態を作る。creation command、delegated authoring boundary、docs/skills guidance の全面更新は後続 Issue の責務に残す。

## 現行構造
- Validation:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py` は graph を構築して `validate_graph_and_deps()` と required artifact validation を実行する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` は `_validate_discussion_filenames()` を graph validation の末尾で実行する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py` は `parse_artifact_filename()`、`is_malformed_artifact_candidate()`、`scan_artifact_duplicate_state()` を持ち、artifact filename / duplicate diagnostics の source of truth になっている。
- ADR mirror:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` の `_collect_adr_mirror_sources()` は現状 `scope.path / "discussions"` だけを走査する。
  - `_preflight_adr_mirror_sources()` と `_rebuild_adr_mirror()` は source list を受け取り、basename collision を検査して symlink mirror を作る。
- Projection:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` は `.agent` / sync 用の node payload を構築する。
  - 既存 payload は node identity、path、children、status、github、dependency fields を持つが、canonical docs / artifacts / discussions の material surface を明示的には区別しない。

## 変更方針
- Validation は discussion validator と artifact validator を並列に接続する。
  - `discussions/` が存在すれば既存 strict validation を維持する。
  - `artifacts/` が存在すれば `scan_artifact_duplicate_state()` を使って artifact filename / duplicate validation を実行する。
  - `artifacts/` や `discussions/` の不在だけでは old-only / new-only / mixed layout を invalid にしない。
- ADR mirror discovery は `discussions/` と `artifacts/` の両方から ADR originals を収集する。
  - legacy discussion ADR は既存の discussion filename parser と front matter check を使う。
  - future artifact ADR は artifact filename parser で `artifact_type == "adr"` を判定し、front matter の `ID` と parent scope を既存 mirror contract に合わせる。
  - original file は移動、rename、rewrite しない。
- Projection は additive schema として `document_surfaces` を node payload に追加する。
  - `canonical_docs`: `requirement.md` / `design.md` / `plan.md` / `report.md` の canonical docs を示す。
  - `future_artifacts`: `artifacts/` surface を示す。
  - `legacy_discussions`: `discussions/` surface を示す。
  - 既存 payload key を rename / delete しない。

## 設計契約
| ID | 契約 | 対応 AC | 実装面 | 検証 |
|---|---|---|---|---|
| DES-265-001 | `artifacts/` / `discussions/` の不在だけでは node を invalid にしない | AC-265-001 | validation graph pass | old-only / new-only / mixed fixtures |
| DES-265-002 | `discussions/` が存在する場合、legacy discussion filename / duplicate strictness は緩めない | AC-265-003 | `_validate_discussion_filenames()` existing contract | malformed/duplicate discussion tests |
| DES-265-003 | `artifacts/` が存在する場合、artifact filename / duplicate validation を artifact diagnostics として実行する | AC-265-002 | `_validate_artifact_filenames()` + `scan_artifact_duplicate_state()` | malformed/duplicate artifact tests |
| DES-265-004 | artifact diagnostics と discussion diagnostics は wording / category を混同しない | AC-265-002, AC-265-003 | validation error aggregation | negative assertions |
| DES-265-005 | ADR mirror は `discussions/` と `artifacts/` の両方を source として読む | AC-265-004 | `_collect_adr_mirror_sources()` | mirror source tests |
| DES-265-006 | ADR mirror の original は移動・rename・rewrite しない | AC-265-004 | existing symlink mirror writer | symlink target and original existence assertions |
| DES-265-007 | basename collision preflight は source directory をまたいでも維持する | AC-265-004 | `_preflight_adr_mirror_sources()` input expansion | mixed-source collision test |
| DES-265-008 | `.agent` / sync projection は canonical docs、future artifacts、legacy discussions を distinct labels で出す | AC-265-005 | `json_state.py` payload builder | JSON payload assertions |
| DES-265-009 | Projection 追加は additive で、既存 dependency / github / status schema を壊さない | AC-265-005 | existing payload keys retained | schema regression assertions |
| DES-265-010 | `artifacts/` は canonical docs として扱わない | AC-265-005 | `document_surfaces` labels | canonical/artifact separation assertions |

## Projection schema
Node payload に次の additive field を追加する。

```json
"document_surfaces": {
  "canonical_docs": [
    {"kind": "requirement", "path": ".../requirement.md", "present": true},
    {"kind": "design", "path": ".../design.md", "present": true},
    {"kind": "plan", "path": ".../plan.md", "present": true},
    {"kind": "report", "path": ".../report.md", "present": true}
  ],
  "future_artifacts": {"path": ".../artifacts", "present": true},
  "legacy_discussions": {"path": ".../discussions", "present": false}
}
```

- `path` は既存 node `path` と同じ projection convention に合わせる。
- `present` は filesystem presence を示し、不在を validation failure として扱う判断には使わない。
- `index-all.json` / current-future projection の既存 boundary は維持し、raw `depends_on` の露出範囲をこの Issue で広げない。

## 安全境界
- 禁止:
  - existing node の migration、bulk rewrite、`discussions/` 削除。
  - ADR original の移動、rename、rewrite。
  - `new artifact` / `new doc` command semantics の変更。
  - delegated authoring boundary / diff guard の変更。
  - 恒久 docs / shipped skills の全面更新。
  - `SpecNode` schema や `.meta.json` contract の変更。
- 許可:
  - validation layer への artifact filename validator 接続。
  - ADR mirror discovery source の拡張。
  - `.agent` / sync JSON projection への additive label 追加。
  - 受け入れ条件を固定する focused tests の追加・更新。

## フロー
1. `validate` / `sync` が repo tree を graph 化する。
2. Graph validation が canonical node/dependency rules を検査する。
3. Existing discussion validation が存在する `discussions/` に対して走る。
4. New artifact validation が存在する `artifacts/` に対して走る。
5. `sync` は required artifact validation を継続し、その後 ADR mirror source を収集する。
6. ADR mirror source collector が valid discussion ADR と valid artifact ADR を同じ mirror source list に入れる。
7. ADR mirror preflight が source 全体の basename collision を検査する。
8. Mirror writer が symlink を再構築し、original はそのまま残す。
9. JSON projection builder が既存 node payload に `document_surfaces` を追加する。

## テスト戦略
- Validation:
  - old-only `discussions/` layout pass。
  - new-only `artifacts/` layout pass。
  - mixed `discussions/` + `artifacts/` layout pass。
  - malformed artifact-intent filename fail。
  - duplicate artifact id / timestamp slot fail。
  - malformed / duplicate legacy discussion fail。
- ADR mirror:
  - legacy discussion ADR source is mirrored。
  - future artifact ADR source is mirrored。
  - mixed sources are mirrored without moving originals。
  - cross-source basename collision fails before mirror write。
- Projection:
  - `document_surfaces.canonical_docs` / `future_artifacts` / `legacy_discussions` are emitted separately。
  - Canonical docs are not labeled as artifacts。
  - Existing dependency projection boundary is unchanged。
- Test commands:
  - `uv run pytest tests/cli_runtime/test_validate.py`
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k "adr_mirror or projection or index"`
  - `uv run pytest tests/cli_runtime/test_sync.py`
  - `uv run pytest tests/cli_runtime`

## 後続 Issue への引き渡し
- `iss-00266`:
  - delegated authoring artifacts boundary は、この Issue の artifact validation / projection labels を前提に切り替える。
- `iss-00267`:
  - workflow docs / shipped skills / README guidance は、この Issue の diagnostics と `document_surfaces` schema を反映する。
- `iss-00268`:
  - dogfooding validation / sync evidence は、この Issue の old/new/mixed compatibility と ADR mirror parity を品質ゲートに使う。
