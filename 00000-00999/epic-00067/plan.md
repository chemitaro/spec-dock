---
種別: 計画書（Epic）
ID: "epic-00067"
タイトル: "Installed layout aligned asset source structure for agent tooling"
関連GitHub: ["#67"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-12"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00067 Installed layout aligned asset source structure for agent tooling — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
  - E-RQ-006
  - E-RQ-007
  - E-RQ-008
  - E-RQ-009
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004
  - E-AC-005
  - E-AC-006
  - E-AC-007

## Issue 分割方針
- slicing principle:
  - `install_root` の source tree foundation、packaged-install 配布保証、installer/managed ownership、verification parity、legacy authority retirement を別 issue に分ける。
  - 各 issue は 1 つの primary risk を閉じる。
  - workflow ownership は managed ownership contract の一部として installer tranche に含める。
- rationale:
  - architecture gap は layout foundation、distribution、ownership、verification、retirement の 5 段階で閉じる必要があり、ここを混ぜると rollback と review が曖昧になるため。
- exceptions:
  - Claude Code 実装は分割対象に入れない。
  - workflow 個別ロジックの機能拡張は別 epic/issue に送る。

## Closure matrix
- `issue-1-install-root-tree-and-asset-classification`:
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-AC-001
- `issue-2-package-data-and-installed-artifact-parity`:
  - closes:
    - E-RQ-009
    - E-AC-006
- `issue-3-installer-source-discovery-and-managed-ownership`:
  - closes:
    - E-RQ-003
    - E-RQ-004
    - E-RQ-005
    - E-RQ-007
  - contributes to:
    - E-AC-002
    - E-AC-003
- `issue-4-verification-dogfooding-and-update-parity`:
  - closes:
    - E-AC-002
    - E-AC-003
- `issue-5-legacy-authority-retirement-and-final-spec-close`:
  - closes:
    - E-RQ-006
    - E-RQ-008
    - E-AC-004
    - E-AC-005
    - E-AC-007

## Issue alias -> 期待する役割
- `issue-1-install-root-tree-and-asset-classification`:
  - `install_root/` tree を導入し、shared / host-specific / workflow の分類を source tree へ固定する tranche。
- `issue-2-package-data-and-installed-artifact-parity`:
  - hidden path / dotfile / workflow / shim を package data と built artifact に確実に含め、package-installed `spec-dock` で解決できるようにする tranche。
- `issue-3-installer-source-discovery-and-managed-ownership`:
  - installer が `install_root` を authority として読み、workflow を含む managed ownership / cleanup contract を固定する tranche。
- `issue-4-verification-dogfooding-and-update-parity`:
  - init/update tests、packaged-install smoke、dogfooding parity、`validate/sync` evidence を揃える tranche。
- `issue-5-legacy-authority-retirement-and-final-spec-close`:
  - legacy `codex_skills` authority を retire し、二重正本状態を解消して final spec review まで閉じる tranche。

## Issue 一覧（順序 / tranche 付き）
- issue-1-install-root-tree-and-asset-classification:
  - 目的:
    - `src/spec_dock/assets/install_root/` を導入し、`.agents` / `.codex` / `.github` / `.github/workflows` の install-shaped tree を provider-side に作る。
    - adapter skill は shared reusable skill、native shim / entry file / workflow は host-specific file という分類を source tree へ固定する。
  - deliverable:
    - `install_root/` subtree の新設
    - shared / Codex / GitHub / workflow の initial placement
    - adapter skill classification を反映した source tree
    - source tree listing と path assertions
  - tranche:
    - tranche-a / foundation
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-AC-001
  - depends on:
    - なし
- issue-2-package-data-and-installed-artifact-parity:
  - 目的:
    - `install_root/` 配下の hidden directories、dotfiles、workflow files、native shims が built artifact に含まれ、package-installed `spec-dock` から解決できることを保証する。
  - deliverable:
    - `pyproject.toml` / `setup.py` 等の package data inclusion 更新
    - built artifact content check
    - package-installed `spec-dock init/update` smoke test
    - local checkout と package-installed の asset discovery parity evidence
  - tranche:
    - tranche-b / packaging
  - closes:
    - E-RQ-009
    - E-AC-006
  - depends on:
    - issue-1-install-root-tree-and-asset-classification
- issue-3-installer-source-discovery-and-managed-ownership:
  - 目的:
    - installer が `install_root/` を authority として解決し、workflow を含む current managed file set / explicit obsolete managed file set の contract を実装する。
  - deliverable:
    - `src/spec_dock/cli.py` の source discovery 切替
    - `host-adapters/meta.json` の path / obsolete managed path 契約更新
    - workflow を含む managed ownership / cleanup rule
    - managed/unmanaged boundary と prune safety の tests
  - tranche:
    - tranche-c / installer ownership
  - closes:
    - E-RQ-003
    - E-RQ-004
    - E-RQ-005
    - E-RQ-007
  - contributes to:
    - E-AC-002
    - E-AC-003
  - depends on:
    - issue-1-install-root-tree-and-asset-classification
    - issue-2-package-data-and-installed-artifact-parity
- issue-4-verification-dogfooding-and-update-parity:
  - 目的:
    - new contract が local checkout と package-installed の両方で成立し、checked-in dogfooding state でも parity が取れていることを証明する。
  - deliverable:
    - `tests/test_init_update.py` / `tests/test_cli.py` の path fixed values 更新
    - init/update integration tests
    - packaged-install smoke 再確認
    - checked-in `.agents` / `.codex` / `.github` / `.github/workflows` parity 回復
    - `./spec-dock/scripts/spec-dock validate` / `sync` evidence
  - tranche:
    - tranche-d / verification
  - closes:
    - E-AC-002
    - E-AC-003
  - depends on:
    - issue-2-package-data-and-installed-artifact-parity
    - issue-3-installer-source-discovery-and-managed-ownership
- issue-5-legacy-authority-retirement-and-final-spec-close:
  - 目的:
    - legacy `codex_skills` authority を retire し、二重正本状態を解消したうえで final spec review まで閉じる。
  - deliverable:
    - docs / tests / installer source discovery から legacy authority 依存の除去
    - authority 一本化確認
    - future host extension point の最終確認
    - final spec review record
  - tranche:
    - tranche-e / closeout
  - closes:
    - E-RQ-006
    - E-RQ-008
    - E-AC-004
    - E-AC-005
    - E-AC-007
  - depends on:
    - issue-4-verification-dogfooding-and-update-parity

## 統合チェックポイント
- G1 decomposition review:
  - each E-RQ/E-AC に単一 owner または明示 contribution/closure 関係があることを確認する。
- G2 foundation review:
  - `install_root` tree と adapter skill classification が source tree に固定されていることを確認する。
- G3 packaging readiness:
  - hidden paths が built artifact に入り、package-installed `spec-dock` がそれを解決できることを確認する。
- G4 installer ownership readiness:
  - workflow を含む current managed file set / explicit obsolete managed file set の contract が実装されていることを確認する。
- G5 verification readiness:
  - init/update tests、packaged-install smoke、dogfooding parity の 3 系統が揃っていることを確認する。
- G6 authority retirement review:
  - `install_root` が唯一の authority となり、legacy `codex_skills` に drift 可能な正本が残っていないことを確認する。
- G9 final epic spec review:
  - requirement / design / plan と issue evidence の整合が取れ、review verdict が `pass` であることを確認する。

## 品質ゲート
- gate-1 source tree foundation:
  - `install_root/` が導入され、`.agents` / `.codex` / `.github` / `.github/workflows` の tree が揃っていること。
  - adapter skill classification が path と docs の両方で明示されていること。
- gate-2 packaging:
  - dot-directory / dotfile が built artifact に含まれること。
  - package-installed `spec-dock` が install_root assets を解決できること。
- gate-3 installer ownership:
  - installer が `install_root` を authority として解決していること。
  - workflow を含む current managed file set と explicit obsolete managed file set の contract に沿って prune が行われること。
  - managed 外の user-authored file を削除しないこと。
- gate-4 verification:
  - `python -m unittest discover -v` または対象 suite が通ること。
  - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` が成功すること。
  - checked-in dogfooding parity が回復していること。
- gate-5 final authority retirement:
  - legacy `codex_skills` authority が retire され、`install_root` が唯一の authority であること。
  - final spec review verdict が `pass` であること。

## ロールアウト / docs impact
- rollout order:
  - source tree foundation -> packaging parity -> installer ownership -> verification/dogfooding -> authority retirement/final review
- contract / docs refresh:
  - source-of-truth path の変更を説明する docs を更新する。
  - package-installed smoke と managed cleanup 契約を docs / tests に露出する。
  - dogfooding checked-in state を provider-side source-of-truth に再整合させる。
  - legacy authority retirement を docs / tests / installer source discovery に反映する。

## Issue readiness contract
- Issue に要求する最低条件:
  - primary risk が 1 つに絞られていること。
  - change files と verification method が明示されていること。
  - `validate` / `sync` / relevant tests のどれで何を観測するかが書かれていること。
  - 次 tranche へ handoff できる evidence が report に残ること。

## final exit contract
- E-AC closure:
  - E-AC-001 から E-AC-007 までが issue evidence で閉じられていること。
- integration / rollout complete:
  - package-installed と local checkout の両方で新 contract が成立していること。
  - `.agents` / `.codex` / `.github` / `.github/workflows` の install-shaped layout が dogfooding でも確認できること。
- docs impact resolved:
  - source-of-truth path、managed ownership、packaged-install parity、authority retirement を反映した docs / tests / installer contract が一致していること。

## 依存 / ブロッカー
- D-001:
  - dot-directory / dotfile を package artifact に含める build contract の整理
- D-002:
  - `cli.py` の canonical target / cleanup contract を崩さずに source discovery を切り替える必要
- D-003:
  - `.github/workflows` の managed ownership を user-authored workflow 保護と両立させる必要
- D-004:
  - `tests/test_init_update.py` の path fixed values が広範囲で、切替順を誤ると大量 failure になるリスク

## 未確定事項
- なし:
  - epic レベルでは tranche と依存順を固定し、実装中の細かい調整は issue 単位で扱う
