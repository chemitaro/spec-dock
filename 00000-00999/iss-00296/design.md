---
種別: 設計書（Issue）
ID: "iss-00296"
タイトル: "Authoring Pack Assets"
関連GitHub: ["#296"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00296 Authoring Pack Assets — 設計

## 設計方針

この Issue の設計は、root helper をそのまま正式 runtime と見なすのではなく、provider-side installed asset tree へ移すための最小配置を作ることである。後続 Issue が command group や validation logic を実装する前に、source-of-truth と compatibility surface を分離する。

## 配置設計

```text
src/spec_dock/assets/spec_dock/scripts/
|-- authoring-pack/
|   |-- README.md
|   |-- authoring_pack_issue_candidates.py
|   |-- authoring_pack_review.py
|   |-- authoring_pack_selected_skeleton_fill.py
|   |-- authoring_pack_stage.py
|   |-- invoke_chatgpt_backend.py
|   |-- prepare_chatgpt_authoring_pack.py
|   |-- review_chatgpt_authoring_pack.py
|   |-- stage_chatgpt_authoring_pack.py
|   |-- validate_issue_candidates.py
|   `-- validate_selected_skeleton_fill.py
`-- spec_dock_runtime/
    |-- application/
    |   `-- authoring_pack/
    |       `-- __init__.py
    `-- domain/
        `-- authoring_pack/
            `-- __init__.py
```

## Source-of-truth boundary

- Provider-side authority:
  - `src/spec_dock/assets/spec_dock/scripts/authoring-pack/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/`
- Compatibility / dogfood developer surface:
  - root `scripts/authoring-pack/`
- Consumer-side generated workspace:
  - `spec-dock/` は validation / dogfooding / active docs の面であり、implementation source of truth ではない。

## Compatibility design

この Issue では root helper の挙動を wrapper 化しない。まず provider-side に同一 helper inventory を配置し、root README に正式 source-of-truth の位置を明記する。後続 Issue で runtime command group が生えた時点で、root helper の wrapper 化または廃止方針を個別に判断する。

## Authority boundary

- この Issue は artifact output の safety validation を実装しない。
- ChatGPT output を canonical docs や `.assurance.json` に直接反映する処理を追加しない。
- `authoring_pack` package の初期 `__init__.py` は module boundary のみで、authority や reviewer pass を主張しない。

## Failure mode と対策

| Failure mode | 対策 |
|---|---|
| root `scripts/authoring-pack/` を正式配布面と誤認する | README に provider-side source-of-truth を明記する |
| consumer repository に helper が届かない | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` に配置する |
| 後続 Issue が monolithic command file に戻る | `application/authoring_pack` と `domain/authoring_pack` package boundary を先に作る |
| 生成物や cache を provider asset に含める | `__pycache__` はコピー対象外にする |

## 検証設計

- provider-side helper inventory を `find` で確認する。
- root helper README と provider README の source-of-truth wording を確認する。
- `./spec-dock/scripts/spec-dock validate` を実行する。
- 必要に応じて `python -m py_compile` で provider-side copied scripts の構文を確認する。
