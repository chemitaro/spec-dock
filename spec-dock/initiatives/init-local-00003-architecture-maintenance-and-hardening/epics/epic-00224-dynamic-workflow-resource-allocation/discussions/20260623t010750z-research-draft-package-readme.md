# SpecDock Adaptive Assurance Epic Draft Package

## 推奨配置

この変更は単一 Issue ではなく、新規 Epic として `init-local-00003-architecture-maintenance-and-hardening` 配下に作成する。

推奨タイトル:

```text
Adaptive Assurance And Compiled Agent Workflow
```

推奨 slug:

```text
adaptive-assurance-and-compiled-agent-workflow
```

前提 / 関連 Epic:

```text
epic-00158-agent-workflow-pdca-hardening
```

`epic-00158` は first-wave の skill / docs / template context surface を安定化し、runtime gate / harness を後続作業として残した。本 Epic は、その安定化済み境界を前提に、Assurance Contract、状態駆動 Runbook、Step Assurance、GitHub Codex review policy を実装する後続 Epic とする。

## 作成コマンド例

```bash
./spec-dock/scripts/spec-dock new epic \
  --initiative init-local-00003 \
  --create-github-issue \
  --title "Adaptive Assurance And Compiled Agent Workflow"
```

作成後、生成された Epic ID と GitHub Issue を各ファイルの placeholder に反映する。

## 内容

- `requirement.md`: Epic 要件定義ドラフト
- `design.md`: Epic 設計ドラフト
- `plan.md`: Epic 実装計画・Issue 分割ドラフト
- `issue-slices.md`: 各 Issue の planning handoff 用 seed
- `decision.md`: Epic / Issue 選択理由と採用判断

## SpecDock への投入手順

1. 新規 Epic を作成する。
2. 新規 Epic 配下に、既存 Epic を再利用せず新規作成する理由を `disc` として残す。
3. 本パッケージの `requirement.md` を canonical requirement の初稿として統合する。
4. fresh `spec-reviewer` pass 後、`design.md` を統合する。
5. fresh `spec-reviewer` pass 後、`plan.md` を統合する。
6. fresh `spec-reviewer` pass 後、Issue を計画順に作成する。
7. `issue-slices.md` を各 Issue の `draft-requirement` / `draft-design` 作成時の入力に使う。
8. Dependency は metadata 直編集ではなく `spec-dock deps add` で設定する。

## 重要な前提

- `.agents/skills/**` を Issue 状態ごとに差し替えない。
- Git 管理する正本は policy、schema、fragment、canonical Issue / Epic artifacts。
- compiled runbook、active projection、raw observation は `.agent/` / `active/` 配下の generated state。
- GitHub Codex review policy は PR head ではなく PR base SHA から取得する。
- P0 / P1 と machine-validated blocker を修正ループへ入れ、P2 は原則 non-blocking とする。
