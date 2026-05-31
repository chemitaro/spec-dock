---
種別: disc
ID: "20260531t141123z-disc"
タイトル: "Uninstall requirement risk synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
authority: "proposed"
derived_from:
  - consultant notification 019e7e57-fd68-7602-ad68-0e99d06f2c42
  - spec-dock/active/issue/discussions/20260531t133315z-interview-uninstall-command-scope.md
  - spec-dock/active/issue/discussions/20260531t133616z-interview-uninstall-removal-boundary.md
  - spec-dock/active/issue/discussions/20260531t134004z-interview-uninstall-user-owned-asset-boundary.md
  - spec-dock/active/issue/discussions/20260531t134206z-interview-uninstall-command-surface.md
  - spec-dock/active/issue/discussions/20260531t134650z-interview-uninstall-managed-asset-mismatch.md
  - spec-dock/active/issue/discussions/20260531t135206z-interview-uninstall-empty-directory-cleanup.md
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t141123z-disc Uninstall requirement risk synthesis

## 対象論点
- 今回整理する論点:
  - repo-local uninstall requirement で、削除対象分類、content comparison、mismatch handling、partial failure、idempotency を requirement-level safety criteria として明文化する必要があるか。
- この synthesis が必要な理由:
  - uninstall は destructive operation であり、実装判断に任せると agent / skill noise removal と user file protection の境界が崩れやすい。

## derived question sheets / research
- `interview`:
  - `20260531t133315z-interview-uninstall-command-scope.md`
  - `20260531t133616z-interview-uninstall-removal-boundary.md`
  - `20260531t134004z-interview-uninstall-user-owned-asset-boundary.md`
  - `20260531t134206z-interview-uninstall-command-surface.md`
  - `20260531t134650z-interview-uninstall-managed-asset-mismatch.md`
  - `20260531t135206z-interview-uninstall-empty-directory-cleanup.md`
- `research`:
  - `20260531t141121z-research-uninstall-repo-analysis-evidence.md`
- その他の根拠:
  - consultant read-only notification 019e7e57-fd68-7602-ad68-0e99d06f2c42

## synthesis
- 合意済みのこと:
  - uninstall は repo-local removal であり、package/environment uninstall は対象外。
  - specs は実削除時に keep/remove の explicit mode selection を必須にする。
  - bootstrap-only / user-owned 候補は content match の場合だけ自動削除し、mismatch は preserve + manual review。
  - command surface は repo-local wrapper + installer implementation。
  - agent / skill assets は known SpecDock-managed paths に限り content mismatch でも削除する。
  - CI / config / prompt / rule など product-reusable assets は content mismatch 時に preserve + manual review。
  - empty directory cleanup は boundary root 内の bounded cleanup。
- 未合意 / 未確定のこと:
  - exact flag names and final output wording は design phase で既存 CLI style に合わせる。
- source-grounded に解決できたこと:
  - repo-root shortcut、runtime wrapper self-removal risk、install_root inventory は repo analysis で requirement grounding に採用した。

## 選択肢 / tradeoff
- Strong removal:
  - Pros:
    - agent / skill noise removal が確実。
  - Cons:
    - user edit や product-reused settings の誤削除リスクがある。
- Conservative preservation:
  - Pros:
    - data loss risk が低い。
  - Cons:
    - uninstall 後も agent / skill noise が残る可能性がある。
- Category-based removal:
  - Pros:
    - primary objective の agent / skill noise removal と user-owned / product-reused file protection を両立しやすい。
  - Cons:
    - path classification と report behavior を tests で固定する必要がある。

## reflection proposal
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Issue requirement に削除対象分類表を置く。
  - partial failure / idempotency / comparison failure を AC / EC として固定する。
- まだ proposal に留める理由:
  - exact implementation structure と CLI flag names は design phase で扱うため。

## ADR candidate triage
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`

## 推奨案
- category-based removal を requirement に固定する。
- 削除対象分類表は `path/category`, ownership boundary, match requirement, mismatch behavior, specs mode dependency, report behavior を持つ。
- comparison が判定不能な場合は、agent / skill core removal target を除いて preserve + manual review に倒す。
- partial failure summary と idempotent re-run を acceptance criteria に含める。

## 推奨反映先
- `requirement.md`:
  - 削除対象分類表、partial failure / idempotency AC、comparison failure EC。
- `design.md`:
  - inventory classifier、content comparison policy、result model、cleanup traversal。
- `plan.md`:
  - keep/remove specs、match/mismatch、forced agent removal、product-reusable preserve、empty-dir cleanup、idempotency tests。
- `ADR`:
  - 不要。
- `report.md` Evidence Adoption Ledger:
  - consultant findings をこの discussion 経由で採用したことを記録する。

## 未採用 / deferred 理由
- 未採用:
  - package/environment uninstall automation。repo-local uninstall の primary objective と異なり、install method 依存が大きい。
- deferred:
  - exact CLI flag names。design phase で既存 command style に合わせる。

## 次アクション
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - requirement は反映済み。design / plan では implementation surface と tests に分解する。
- 追加で作る discussion docs:
  - requirement phase では不要。
