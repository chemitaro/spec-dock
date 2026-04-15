---
種別: 実装計画書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md"]
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
  - `AC-004`
- EC:
  - `EC-001`
  - `EC-002`
  - `EC-003`
- 制約:
  - 既存 installer foundation の additive change に閉じる
  - Codex では direct `orchestrator.toml` を ship しない
  - prompt assets は current issue の deliverable に含めない
  - secret / token / personal config は managed asset として配布しない
  - unknown custom files は prune safety で保持する

## 今回の実装スライス（2026-04-15 セッション）
- 先行実装は kebab-case naming unification のみとする。
- 完了条件:
  - rename 対象 agent files と internal role names が Codex / GitHub Copilot で kebab-case に統一される
  - installer metadata / canonical references / tests が新 naming contract と一致する
  - 旧 snake_case managed filenames が obsolete path として prune 対象になる
- defer:
  - `spec-manager` の本文整理
  - `spec-manager` の model / reasoning / notify / MCP / skill guidance 変更

## マイルストーン一覧
- M1:
  - 対象:
    - Codex pack と Copilot pack の asset placement
    - shared skills の集約
  - exit:
    - host-specific project path への配置が観測できる
- M2:
  - 対象:
    - installer metadata / prune safety / update behavior
  - exit:
    - unknown custom files の保持と obsolete managed file の prune を証明できる
- M3:
  - 対象:
    - docs / validate / report / final diff review
  - exit:
    - `spec-dock validate` が pass し、issue report に evidence が残る

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `変更計画`
- sequencing rule:
  - 先に provider-side asset placement を固定する
  - 次に installer mapping と prune behavior を固定する
  - 最後に tests と docs / report をまとめて閉じる
- step ordering notes:
  - `S01` で clean install inventory と update safety を分けて閉じる
  - `S90` で docs / report を整える
  - `S99` は branch 全体の close-ready 判断を行う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - Codex と GitHub Copilot の host pack が正しい project path に配置され、unknown custom files を保持したまま managed obsolete files のみ prune される
  - closes:
    - `AC-001`
    - `AC-002`
    - `AC-003`
    - `EC-001`
    - `EC-002`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S90:
  - 観測可能な振る舞い:
    - docs impact が整理され、issue report に validate / sync / review evidence の追記位置が作られる
  - closes:
    - report evidence contract
  - review gate:
    - no-op 可。ただし `report.md` 更新は必須
- S99:
  - 観測可能な振る舞い:
    - branch 全体が final validation と final review を通過し、epic-00074 の single issue close-ready になる
  - closes:
    - final exit contract
  - review gate:
    - final code review `pass`
    - final spec review `pass`
    - final validation `pass`
    - final commit

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`
- `AC-002` -> `S01`
- `AC-003` -> `S01`
- `AC-004` -> `S90` / `S99`
- `EC-001` -> `S01`
- `EC-002` -> `S01`
- `EC-003` -> `S90`

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - `S01` 実装後
  - scope:
    - asset placement / installer mapping / prune safety
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - `S01` の targeted validation 後
  - scope:
    - install/update / prune / preserve regression
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - `S90` 以降
  - scope:
    - docs / report / final boundary
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。

## 実装ステップ

### S01 — host pack placement and prune behavior
- target:
  - Codex / Copilot / shared skills の host pack placement と prune behavior を 1 回の実装で固定する
- design refs:
  - `design.md` の `変更計画`
  - `design.md` の `インターフェース契約`
- step boundary:
  - provider asset tree、installer mapping、tests の最小閉包

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — asset placement and managed mapping
- purpose:
  - asset placement と prune safety を一塊で扱う
- files:
  - `src/spec_dock/assets/install_root/`
  - `tests/`

##### I1 — clean install inventory regression
- slice goal:
  - Codex / Copilot / shared skills の exact inventory と path mapping を赤テスト化して通す

###### Red
- failing test:
  - clean init/update で expected inventory がまだ揃わないことを示すテスト
- expected failure:
  - asset inventory mismatch

###### Green
- minimum implementation:
  - provider-side asset placement と canonical filename rename を反映する
- pass condition:
  - expected path が install/update で見え、Codex に direct orchestrator file が存在しない

###### Refactor
- 目的:
  - Green を維持したまま、inventory assertion と metadata assertion の重複を減らす
- guardrail:
  - 振る舞いを変えない
  - bootstrap-only preserve の仕様は次 iteration まで広げない

##### I2 — update prune/preserve regression
- slice goal:
  - obsolete managed cleanup、unknown custom preserve、edited `.codex/config.toml` preserve を別テストで固定する

###### Red
- failing test:
  - update で old managed files だけが掃除されず、または `.codex/config.toml` が保持されないことを示すテスト
- expected failure:
  - obsolete cleanup mismatch or preserved content mismatch

###### Green
- minimum implementation:
  - `bootstrap_only_exact_file_paths` と obsolete cleanup を installer に実装する
  - touchpoints は canonical host constants、metadata load、current managed inventory、copy policy、obsolete prune に限定する
- pass condition:
  - old managed files だけが削除され、unknown custom files と edited `.codex/config.toml` が保持される

###### Refactor
- 目的:
  - Green を維持したまま、bootstrap-only 判定と current managed 計算の責務境界を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない

#### step gate
- review:
  - implementation review で asset placement と prune safety を確認する
- expected tests:
  - install/update / prune / preserve regression
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S90 — docs impact resolution / docs refresh
- 対象:
  - issue report / validate evidence
- 対応:
  - issue report に review・test・validate evidence を記録する
  - 常設 docs 更新は current issue の必須 deliverable には含めない

### S99 — final diff review quality gate
- branch diff scope:
  - この issue の実装差分全体
- required validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- reviewer approvals:
  - final code review pass
  - final spec review pass
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし:
  - single issue で閉じる前提を維持する。

## final exit contract
- AC/EC 達成:
  - host-specific asset placement、prune safety、report evidence が揃う
- docs impact resolved:
  - issue report / related docs の更新が完了している
- final diff approved:
  - final code review と final spec review が pass している
