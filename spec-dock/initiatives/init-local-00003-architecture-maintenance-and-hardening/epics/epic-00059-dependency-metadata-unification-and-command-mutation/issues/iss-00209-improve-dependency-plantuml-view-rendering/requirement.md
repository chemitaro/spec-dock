---
種別: 要件定義書（Issue）
ID: "iss-00209"
タイトル: "Improve dependency PlantUML view rendering"
関連GitHub: ["#209"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["epic-00059", "init-local-00003"]
---

# iss-00209 Improve dependency PlantUML view rendering — 要件定義（何を、なぜ行うか）

## 目的
- 依存関係ロジック修復後の `deps-raw.puml` / `deps-issues.puml` 表示を、人間が依存状態を読み取りやすい PlantUML view に改善する。
- 特に raw direct dependency と readiness / blocker 解釈の違い、initiative / epic / issue の階層、blocked / ready / done / satisfied の見分けやすさを議論・具体化する。

## 背景・現状
- 現状の挙動:
  - `deps-raw.puml` は `.meta.json.depends_on` の raw direct dependency を initiative / epic / issue を含む階層付き PlantUML として生成する。
  - `deps-issues.puml` は readiness authority である `.agent/deps-issues.json` から、issue-level blocker / node-level blocker / satisfied dependency を PlantUML として生成する。
  - `iss-00207` で依存関係ロジックは修復され、realistic manual test では ready / blocked / done / satisfied context が混在することを確認した。
- 現状の課題:
  - 現在の PlantUML 表示は、`raw_direct` の意味、raw view と issue readiness view の違い、階層表現と readiness 表現の読み分けが直感的ではない。
  - 色、線種、ラベル、node grouping、凡例、blocked / executable の視認性など、表示上の改善余地が残っている。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock sync` を実行する。
  2. `spec-dock/deps-raw.puml` と `spec-dock/deps-issues.puml` を PlantUML として確認する。
  3. `manual-tests/deps-projection-iss-00207-realistic/trial-repo/spec-dock/{deps-raw.puml,deps-issues.puml}` の realistic fixture と比較する。
- 観測点:
  - PUML:
    - node 色、edge 線種、label、legend、package nesting、layout direction。
  - JSON:
    - `.agent/deps-issues.json` の `state`, `relation`, `source`, `ready`, `node_blockers`, `satisfied_dependencies`。
  - CLI:
    - `sync` と `deps check` の出力が PlantUML 表示と矛盾しないこと。
- 情報源:
  - `spec-dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_deps.md`
  - `manual-tests/deps-projection-iss-00207-realistic/summary-report.md`
  - `manual-tests/deps-projection-iss-00207-realistic/trial-repo/spec-dock/deps-raw.puml`
  - `manual-tests/deps-projection-iss-00207-realistic/trial-repo/spec-dock/deps-issues.puml`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - ...
- 代表シナリオ:
  - ...

## スコープ
- 必須:
  - `deps-raw.puml` と `deps-issues.puml` の表示改善方針を整理する。
  - raw direct dependency と readiness interpretation の違いが見て分かる表現にする。
  - blocked / ready / done / satisfied dependency の視認性を改善する。
  - realistic manual test fixture で、改善後の PlantUML 表示を確認できるようにする。
- 禁止:
  - `iss-00207` で修復した依存関係判定ロジックを、表示都合だけで変更しない。
  - `.meta.json.depends_on` storage format を変更しない。
  - `deps-issues.json` の authority contract を表示都合だけで破壊しない。
- 対象外:
  - 依存関係ロジックの再修正。
  - GitHub issue lifecycle や `deps add/remove/check` command mutation contract の変更。
  - PlantUML 以外の新規 GUI / Web UI の追加。

## 境界
- 常に行う:
  - ...
- 判断が必要:
  - ...
- 行わない:
  - ...

## 非交渉制約
- ...

## 前提
- ...

## 受け入れ条件
- AC-001:
  - アクター:
  - 前提:
  - 操作:
  - 期待結果:
  - 観測点:
- AC-002:
  - ...

## 例外・エッジケース
- EC-001:
  - 条件:
  - 期待:
  - 観測点:
- EC-002:
  - ...

## 入力→出力例（必要時）
- EX-001:
  - 入力:
  - 出力:

## 用語（ドメイン語彙）
- TERM-001:
  - ...

## 未確定事項
- Q-001:
  - 質問: `deps-raw.puml` と `deps-issues.puml` をどのような読み分けにするか。
  - 選択肢:
    - A:
      - raw view は階層・direct edge のデバッグ専用、issue view は実行可否判断専用として明確に分離する。
    - B:
      - raw view にも readiness 色や説明を増やし、1 枚で概要を掴めるようにする。
  - 推奨案:
    - A を基本にし、必要な凡例とラベルだけを raw view に補う。
  - 影響範囲:
    - `presentation/puml.py`, `presentation/json_state.py`, reference docs, manual test evidence。
