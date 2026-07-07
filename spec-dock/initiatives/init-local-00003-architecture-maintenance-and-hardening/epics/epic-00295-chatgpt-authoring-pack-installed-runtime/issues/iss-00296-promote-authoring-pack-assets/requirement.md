---
種別: 要件定義書（Issue）
ID: "iss-00296"
タイトル: "Authoring Pack Assets"
関連GitHub: ["#296"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00296 Authoring Pack Assets — 要件定義

## 目的

この Issue は、Epic `epic-00295` の最初の実装スライスとして、dogfood helper として root `scripts/authoring-pack/` に置かれている ChatGPT authoring pack helper 群を、consumer repository へ `spec-dock init/update` で配布できる provider-side installed asset layout へ昇格するための土台を作る。

この Issue では authoring command group の完全実装や ZIP validation の中身までは扱わない。後続 Issue が runtime command、GitHub sync preflight、prompt pack、backend invocation、ZIP review/stage、candidate validation を段階的に実装できるよう、source-of-truth の置き場所、compatibility boundary、inventory evidence を明確にする。

## 背景

Epic `epic-00283` では ChatGPT ZIP authoring pack automation を dogfood helper として検証したが、root `scripts/authoring-pack/` は SpecDock を導入する consumer repository へ配布される installed runtime surface ではない。SpecDock の provider-side source of truth は `src/spec_dock/assets/spec_dock/...` と `src/spec_dock/assets/install_root/...` であり、consumer repository に届く workflow はこの asset tree から生成される。

そのため、この Issue では root helper を捨てるのではなく、provider asset 配下へ移し、root helper は developer convenience / compatibility surface として扱う。これにより、後続 Issue は installed runtime と installed skill を前提に実装できる。

## スコープ

- `scripts/authoring-pack/` 相当の helper scripts を provider-side asset 配下へ配置する。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/` と `domain/authoring_pack/` の初期 package boundary を作る。
- root `scripts/authoring-pack/` は compatibility / dogfood developer surface として残し、provider-side source of truth への関係を README で明記する。
- provider-side file inventory と compatibility note を Issue `report.md` に残す。
- 既存 root helper の `__pycache__` など生成物は source-of-truth として扱わない。

## 対象外

- `./spec-dock/scripts/spec-dock authoring ...` command group の完全実装。
- GitHub sync preflight の判定ロジック。
- ChatGPT backend invocation adapter の実装。
- ZIP / tree review、stage、candidate validation の詳細実装。
- installed skill docs の本格更新。
- `.assurance.json`、canonical docs、reviewer pass、PR-ready などの authority claim を ChatGPT output から自動生成すること。
- この Issue での PR delivery。PR delivery は最終 Issue `iss-00307` に defer する。

## 要件

- provider-side source of truth は `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` 配下に置く。
- authoring pack 関連の application / domain package directory を provider-side runtime 配下に作成し、後続 Issue が layer-specific に実装できる入口を用意する。
- root helper surface は、正式配布面ではなく compatibility surface であることが分かる文書を持つ。
- 移設・配置の結果、consumer install/update で provider asset が配布対象になることを、既存 installer asset tree の構造から確認できる。
- ChatGPT 由来 artifact の authority boundary を変えない。`authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` の考え方を弱めない。

## 受け入れ条件

- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` に helper scripts の provider-side inventory が存在する。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/` と `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/` が package として存在する。
- root `scripts/authoring-pack/README.md` または provider-side README に、root helper が source of truth ではなく compatibility / dogfood surface であることが記録されている。
- `find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f` で provider-side helper inventory を確認できる。
- `./spec-dock/scripts/spec-dock validate` が成功する。
- 中間 Issue として PR delivery を行わず、Issue `iss-00307` へ defer する証跡が `report.md` に残る。

## Draft adoption

- 採用元:
  - `artifacts/20260707t171106z-draft-requirement-promote-authoring-pack-assets-draft-requirement.md`
  - `artifacts/20260707t171234z-draft-design-promote-authoring-pack-assets-draft-design.md`
  - `artifacts/20260707t171235z-draft-plan-promote-authoring-pack-assets-draft-plan.md`
- 採用判断:
  - provider-side source-of-truth migration、scope / non-scope、acceptance criteria、relay PR defer 方針を採用する。
  - ChatGPT draft の `evidence-only` 自己記述、branch 名、draft heading は正本 authority としては採用しない。
