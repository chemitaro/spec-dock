---
種別: 要件定義書（Issue）
ID: "iss-00237"
タイトル: "Analyze Manual Test Routing Failures"
関連GitHub: ["#237"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["epic-00224", "init-local-00003"]
---

# iss-00237 Analyze Manual Test Routing Failures — 要件定義

## 目的
- Epic 00224 の手動テストで見つかった routing failure と未実施 / blocked ケースを、修正前に source-grounded に分析する。
- runtime task が過小分類されるリスク、否定文が高リスク語として誤検出されるリスク、空 workspace validation、symlink abuse 未実施を切り分ける。
- 修正すべき product behavior、documentation note、追加 manual test、accepted behavior を分類し、次の実装修正方針を決められる状態にする。

## 背景・現状
- 手動テスト結果:
  - PASS: 21
  - FAIL: 2
  - BLOCKED: 1
  - SKIPPED: 1
- FAIL はどちらも runtime routing 周辺に集中している。
  - MT-009: runtime command behavior task が期待通り `dev-coder` / `medium` / `unit_tests` に落ちなかった。
  - MT-024: bug exploration として、否定文と runtime-path precedence の問題を再確認した。
- BLOCKED は MT-003 の空 workspace validation。
- SKIPPED は MT-015 の symlink abuse retest。

## スコープ
- 必須:
  - 手動テストサマリーを issue 配下 artifact として保存する。
  - MT-009、MT-024、MT-003、MT-015 を個別 research として分析する。
  - `application/context_packets.py` の `_classify_task_kind` と関連 tests を根拠に、修正方針を discussion artifact にまとめる。
  - deep-consultant の分析結果を取り込み、採用 / 不採用を明示する。
- 禁止:
  - この分析 issue の中で未承認の product code 修正を混ぜない。
  - 手動テスト evidence を消さない。
  - GitHub PR state を mutation しない。
- 対象外:
  - PR #236 の merge。
  - symlink abuse の fresh trial repo 再実施。
  - runtime routing 修正の実装そのもの。

## 受け入れ条件
- AC-001:
  - アクター: SpecDock maintainer
  - 前提: Epic 00224 の手動テストサマリーが存在する。
  - 操作: iss-00237 の `discussions/` を確認する。
  - 期待結果: manual test summary artifact と、MT-009 / MT-024 / MT-003 / MT-015 の research artifact が存在する。
  - 観測点: issue 配下 `discussions/*.md`。
- AC-002:
  - アクター: SpecDock maintainer
  - 前提: routing failure の原因分析が完了している。
  - 操作: routing repair design discussion を読む。
  - 期待結果: 修正候補、推奨案、必要な regression tests、残リスクが具体化されている。
  - 観測点: `routing-repair-design-options` discussion。
- AC-003:
  - アクター: SpecDock maintainer
  - 前提: deep-consultant の分析が返っている。
  - 操作: artifact の consultant synthesis を確認する。
  - 期待結果: consultant の観点がローカル根拠と統合され、次の修正 issue / 実装判断に使える。
  - 観測点: research / discussion の `consultant synthesis` section。

## 未確定事項
- routing 修正を iss-00237 でそのまま実装するか、別 issue に分離するか。
- true lite profile authorization の rollout-gated policy を今回の修正範囲に含めるか。
