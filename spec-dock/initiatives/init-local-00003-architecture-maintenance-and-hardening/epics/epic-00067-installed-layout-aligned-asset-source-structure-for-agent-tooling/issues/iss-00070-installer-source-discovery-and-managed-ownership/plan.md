---
種別: 実装計画書（Issue）
ID: "iss-00070"
タイトル: "Installer source discovery and managed ownership"
関連GitHub: ["#70"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00070 Installer source discovery and managed ownership — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
  - `AC-004`
  - `AC-005`
  - `AC-006`
  - `AC-007`
- EC:
  - `EC-001`
  - `EC-002`
  - `EC-003`
- 制約:
  - one-shot cutover を採用し、dual-authority / multi-stage migration は導入しない
  - current managed file set の authority は `src/spec_dock/assets/install_root/` 実在 tree に固定する
  - obsolete cleanup authority は `install_root/.agents/host-adapters/meta.json` の top-level `managed_assets.obsolete_exact_file_paths` に固定する
  - `iss-00069` が閉じた package parity / isolated installed-package discovery contract を壊さない
  - 各 step ごとに code review を通し、step 単位でコミットする
  - `S99` で final code review / final spec review / validate / sync を通して close-ready を確定する

## マイルストーン一覧
- M1:
  - 対象:
    - `install_root` authority への source discovery cutover
    - manifest schema / validation / current-managed inventory 基盤
  - exit:
    - installer が `codex_skills` authority を読まず、`install_root` + top-level obsolete manifest を canonical input として扱える
- M2:
  - 対象:
    - apply pipeline の preflight / sync / verify / cleanup 順序確立
    - workflow current-management 統合
  - exit:
    - current managed files が sync され、obsolete exact paths だけが cleanup され、directory/container conflict は fail-closed になる
- M3:
  - 対象:
    - installed-package cutover proof
    - issue report / final quality gate
  - exit:
    - checkout fallback なしで package-installed init/update が issue-70 contract を満たし、handoff-validation-evidence が report に残る

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `インターフェース契約`
- sequencing rule:
  - 先に canonical inputs（inventory / manifest schema / validation）を固定する
  - 次に apply pipeline と cleanup ordering を切り替える
  - 最後に issue-69 harness を再利用した installed-package proof で branch 全体を閉じる
- step ordering notes:
  - `S01` が inventory / manifest authority を固めない限り、`S02` の sync/cleanup contract は着手できない
  - `S02` が checkout runtime の current/obsolete boundary を固めた後で、`S03` の installed-package cutover regression が成立する
  - `S99` は branch diff 全体に対する final closeout gate とする

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - installer preflight が `install_root` authority と top-level obsolete manifest schema を canonical input として受理し、invalid schema / overlap / namespace violation を fail-closed で拒否する
  - closes:
    - `AC-003`
    - `AC-005` の manifest-invalid branch
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S02:
  - 観測可能な振る舞い:
    - checkout runtime の init/update が current managed files を `install_root` から sync し、workflow を managed set に含め、successful sync 後に obsolete exact paths だけを cleanup する
  - closes:
    - `AC-001`
    - `AC-002`
    - `AC-004`
    - `AC-005` の target-conflict branch
    - `AC-006`
    - `EC-001`
    - `EC-002`
    - `EC-003`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S03:
  - 観測可能な振る舞い:
    - isolated package-installed init/update でも issue-70 cutover contract が成立し、legacy `codex_skills` divergence を読まない
  - closes:
    - `AC-007`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S90:
  - 観測可能な振る舞い:
    - `report.md` の `handoff-validation-evidence` が issue-70 の source/manifest/boundary/install proof で埋まる
  - closes:
    - report evidence contract
  - review gate:
    - no-op 可、ただし `report.md` 更新は必須
- S99:
  - 観測可能な振る舞い:
    - issue-70 branch 全体が final validation と final reviews を通過し、close-ready になる
  - closes:
    - final exit contract
  - review gate:
    - final code review `pass`
    - final spec review `pass`
    - `validate` / `sync --github` 成功
    - final commit または no-op rationale 確定

## 要件 ↔ ステップ対応
- `AC-001` -> `S02`
- `AC-002` -> `S02`
- `AC-003` -> `S01`
- `AC-004` -> `S02`
- `AC-005` -> `S01`, `S02`
- `AC-006` -> `S02`
- `AC-007` -> `S03`
- `EC-001` -> `S02`
- `EC-002` -> `S02`
- `EC-003` -> `S02`

## レビュー / QA ゲート方針
- RG1 step review:
  - timing:
    - `S01` / `S02` / `S03` 完了時
  - scope:
    - 当該 step の diff と requirement/design 契約との差分
  - commit gate:
    - `pass` まで review loop を回し、`report.md` 追記後に step 単位でコミットする
- QG1 targeted validation:
  - timing:
    - 各 step 完了時
  - scope:
    - step 対応の installer/runtime regression と filesystem assertions
  - commit gate:
    - 成功結果を `report.md` に残してからコミットする
- SG1 spec review:
  - timing:
    - 実装着手前の requirement/design/plan fix
    - `S99` final gate
  - scope:
    - issue-70 docs の整合と final close-ready evidence
  - commit gate:
    - `pass` まで回し、必要な docs/report 修正後に commit する

## 実行ルール（全ステップ共通）
- plan は実装着手前に spec review を通して fix する
- cadence / approval policy は `workflow_issue.md` を正本とする
- 各 step は `Red → Green → Refactor → code review → fix → re-review → report → commit/no-op`
- `1 step = 1 observable behavior` を守る
- failing test は iteration ごとに 1 本ずつ追加する
- `Refactor` は green 維持前提の bounded cleanup に限る
- `report.md` には command evidence、review verdict、修正内容、commit hash、no-op 理由を残す
- source-of-truth docs の恒久更新は issue docs 以外は実装 step の範囲に含めない
- `python -m unittest discover -v` は informational sweep とし、scope外 failure は report に明記する
- `S99` では `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync --github` を必須とする

## 実装ステップ

### S01 — `install_root` authority と manifest validation を切り替える
- target:
  - `_HOST_ADAPTER_META_ASSET_REL`
  - `_ManagedSkillInstallPlan`
  - `install_root` recursive inventory helper
  - manifest validation helper
- design refs:
  - `インターフェース契約`
  - `変更計画`
  - `要件 -> 設計マッピング` の `AC-001` / `AC-003` / `AC-004` / `AC-005`
- step boundary:
  - canonical input と fail-closed validation に閉じる
  - target repo への actual copy / prune ordering は `S02` に回す

#### B1 — inventory and manifest contract
- purpose:
  - current managed set を tree 主導、obsolete managed set を manifest 主導で固定する
- files:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `tests/test_init_update.py`

##### I1 — required host source-of-truth schema
- slice goal:
  - top-level `managed_assets.obsolete_exact_file_paths` と required host `source_of_truth_asset=install_root/...` を固定する

###### Red
- failing test:
  - install_root meta が required schema を満たすこと
- expected failure:
  - 現状の `source_of_truth_asset=codex_skills/...` と host-local `obsolete_managed_paths` authority により fail する

###### Green
- minimum implementation:
  - `install_root/.agents/host-adapters/meta.json` を新 schema へ更新
  - `_HOST_ADAPTER_META_ASSET_REL` と manifest parser を `install_root` authority へ切替
- pass condition:
  - required host source-of-truth schema assertion が通る

###### Refactor
- 目的:
  - manifest load と field normalization の責務を整理する
- guardrail:
  - copy / cleanup 振る舞いはまだ変えない

##### I2 — obsolete manifest negative validation
- slice goal:
  - top-level obsolete exact paths の namespace / duplicate / overlap invalid branch を fail-closed にする

###### Red
- failing test:
  - malformed manifest が fail-closed で no-write になること
- expected failure:
  - top-level obsolete exact path invalidity が未検知で fail する

###### Green
- minimum implementation:
  - top-level obsolete exact paths の validation を実装
- pass condition:
  - malformed manifest negative が通る

###### Refactor
- 目的:
  - validation helper と inventory helper の責務を分離する
- guardrail:
  - copy / cleanup 振る舞いはまだ変えない

##### I3 — current-managed inventory and overlap guard
- slice goal:
  - current managed file set を `install_root` recursive inventory から導出する

###### Red
- failing test:
  - current managed inventory に `.agents` / `.codex` / `.github` / `.github/workflows` が含まれること
- expected failure:
  - 現状は `codex_skills` authority かつ workflow 非管理なので fail する

###### Green
- minimum implementation:
  - `_ManagedSkillInstallPlan` を current file mappings + obsolete exact targets モデルへ拡張
  - `install_root` recursive inventory helper を実装
- pass condition:
  - current-managed inventory assertion が通る

###### Refactor
- 目的:
  - mapping build と inventory collection の責務を整理する
- guardrail:
  - apply pipeline の順序までは変更しない

##### I4 — current/obsolete overlap guard
- slice goal:
  - current managed set と obsolete managed set の overlap を preflight で拒否する

###### Red
- failing test:
  - current / obsolete overlap が fail-closed になること
- expected failure:
  - overlap guard 未実装で fail する

###### Green
- minimum implementation:
  - overlap / exact-file constraints を plan build 時に検査
- pass condition:
  - overlap negative が通る

###### Refactor
- 目的:
  - plan build の中で schema validation と mapping build の重複を整理する
- guardrail:
  - apply pipeline の順序までは変更しない

#### step gate
- review:
  - code reviewer に source discovery cutover と fail-closed validation の妥当性をレビューさせる
- expected tests:
  - issue-70 schema / inventory / malformed manifest / overlap negative の targeted tests
- report update:
  - source inventory / manifest assertions と invalid manifest negative の結果を `report.md` に追記する
- commit:
  - issue-70 S01 用 Conventional Commit を作成する

### S02 — sync / verify / cleanup ordering と workflow ownership を統合する
- target:
  - `_apply_managed_skill_install_plan`
  - `_install_skill`
  - `main`
  - target conflict preflight
  - workflow managed sync / obsolete cleanup
- design refs:
  - `インターフェース契約 > apply contract`
  - `変更計画`
  - `要件 -> 設計マッピング` の `AC-002` / `AC-006` / `EC-001` / `EC-002`
- step boundary:
  - checkout runtime の init/update reflection と cleanup safety に閉じる
  - installed-package proof は `S03` へ回す

#### B1 — checkout runtime cutover
- purpose:
  - current sync success 後にだけ obsolete cleanup が動く ordered pipeline を作る
- files:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`

##### I1 — target conflict preflight
- slice goal:
  - directory/container conflict を write 前に拒否する

###### Red
- failing test:
  - target conflict が no-mutation fail になること
- expected failure:
  - 現状は preflight 未実装で fail する

###### Green
- minimum implementation:
  - target conflict preflight を導入し、`main` で managed skill preflight を write 前に完了させる
- pass condition:
  - conflict no-mutation regression が通る

###### Refactor
- 目的:
  - preflight helper の path classification を整理する
- guardrail:
  - schema validation contract は `S01` から崩さない

##### I2 — workflow current-management integration
- slice goal:
  - `.github/workflows/ci.yml` を current managed set に含め、旧 workflow special-case cleanup を obsolete manifest 側へ寄せる

###### Red
- failing test:
  - `.github/workflows/ci.yml` が current managed sync されること
- expected failure:
  - 現状は workflow 非管理で fail する

###### Green
- minimum implementation:
  - workflow を current managed set に統合する
  - legacy workflow special-case cleanup を obsolete manifest へ移す
- pass condition:
  - workflow sync regression が通る

###### Refactor
- 目的:
  - workflow path とその他 managed path の分類を同じ helper へ寄せる
- guardrail:
  - cleanup ordering の契約は変更しない

##### I3 — ownership boundary and cleanup ordering
- slice goal:
  - current managed target は canonical asset で置換、obsolete exact path だけ cleanup、legacy duplicate divergence は authority に影響しないことを示す

###### Red
- failing test:
  - current managed path 上の pre-existing file が canonical content に置換されること
- expected failure:
  - 現状は host-local obsolete authority と directory-based prune により fail する

###### Green
- minimum implementation:
  - current sync -> post-sync verify -> obsolete exact cleanup の順に切替
  - directory単位 prune をやめ、explicit obsolete exact file path だけを削除する
- pass condition:
  - current managed replacement regression が通る

###### Refactor
- 目的:
  - sync/verify/cleanup の順序を helper 単位で読みやすくする
- guardrail:
  - installed-package harness には踏み込まない

##### I4 — preserve custom paths
- slice goal:
  - current/obsolete set のどちらにも含まれない user-authored custom path を保持する

###### Red
- failing test:
  - user-authored custom path は保持されること
- expected failure:
  - prune boundary が広すぎると fail する

###### Green
- minimum implementation:
  - current managed / obsolete exact path 以外を cleanup 対象にしない
- pass condition:
  - custom path preservation regression が通る

###### Refactor
- 目的:
  - cleanup target 判定ロジックを exact path 中心に整理する
- guardrail:
  - current managed replacement contractは崩さない

##### I5 — legacy divergence isolation
- slice goal:
  - stale legacy duplicate divergence を authority から切り離す

###### Red
- failing test:
  - stale legacy duplicate divergence fixture が target repo へ反映されないこと
- expected failure:
  - 現状は legacy authority が残っていて fail する

###### Green
- minimum implementation:
  - legacy `codex_skills` を installer authority から完全に外す
- pass condition:
  - legacy divergence regression が通る

###### Refactor
- 目的:
  - legacy authority cutover 周辺の helper を再利用しやすくする
- guardrail:
  - transition verification の契約はまだこの iteration へ混ぜない

##### I6 — transition verification
- slice goal:
  - source-side move/delete の obsolete-or-transfer contract を provider-side verification で fail-closed にする

###### Red
- failing test:
  - source-side move/delete の obsolete-or-transfer contract が provider-side verification で fail-closed になること
- expected failure:
  - transition guard 未実装で fail する

###### Green
- minimum implementation:
  - source-side move/delete transition verification を tests に追加する
- pass condition:
  - transition regression が通る

###### Refactor
- 目的:
  - apply pipeline の検証用 helper を再利用しやすく整理する
- guardrail:
  - installed-package harness には踏み込まない

#### step gate
- review:
  - code reviewer に sync/cleanup ordering と ownership boundary の安全性をレビューさせる
- expected tests:
  - issue-70 workflow sync
  - target conflict no-mutation
  - current/obsolete boundary
  - legacy divergence
  - transition verification
- report update:
  - current managed / obsolete managed boundary assertions を `report.md` に追記する
- commit:
  - issue-70 S02 用 Conventional Commit を作成する

### S03 — installed-package cutover を issue-69 harness で証明する
- target:
  - issue-69 isolated installed-package helper 再利用
  - package-installed init/update cutover regression
- design refs:
  - `テスト戦略`
  - `要件 -> 設計マッピング` の `AC-007`
- step boundary:
  - installed package surface の証明に閉じる

#### B1 — isolated installed-package proof
- purpose:
  - checkout fallback なしの package-installed reflection を issue-70 contract で確認する
- files:
  - `tests/test_init_update.py`
  - 必要なら `report.md`

##### I1 — installed current/obsolete reflection
- slice goal:
  - site-packages 由来 assets だけで current managed sync / obsolete cleanup が成立することを示す

###### Red
- failing test:
  - isolated package-installed `init/update` が `.agents` / `.codex` / `.github` / `.github/workflows` を canonical relative path で反映すること
- expected failure:
  - installer authority が未切替だと `codex_skills` 側 divergence に引きずられて fail する

###### Green
- minimum implementation:
  - `S01` / `S02` の cutover を installed package path でも使えることを保証し、必要な test helper を追加する
- pass condition:
  - installed current/obsolete reflection regression が通る

###### Refactor
- 目的:
  - installed package helper と checkout helper の共通部分を整理する
- guardrail:
  - package parity contract 自体は変更しない

##### I2 — installed custom-path preservation
- slice goal:
  - package-installed runtime でも managed 外 user path が保持されることを証明する

###### Red
- failing test:
  - managed 外 user-authored path は保持されること
- expected failure:
  - installed cleanup 境界が広すぎると fail する

###### Green
- minimum implementation:
  - site-packages runtime snapshot を使って installed cleanup 境界を確認する
- pass condition:
  - installed custom-path preservation regression が通る

###### Refactor
- 目的:
  - installed helper の preserve-path assertion を再利用しやすくする
- guardrail:
  - no-fallback / legacy divergence assertionは別 iteration へ分ける

##### I3 — installed no-fallback and legacy non-reference proof
- slice goal:
  - checkout fallback なしで legacy divergence を読まないことを package-installed runtime で証明する

###### Red
- failing test:
  - stale legacy divergence fixture を package-installed runtime が読まないこと
- expected failure:
  - fallback または legacy authority に依存すると fail する

###### Green
- minimum implementation:
  - site-packages runtime snapshot を使った no-fallback / legacy non-reference assertion を追加する
- pass condition:
  - installed no-fallback proof regression が通る

###### Refactor
- 目的:
  - issue-69 helper と issue-70 helper の共通部分を整理する
- guardrail:
  - package parity contract 自体は変更しない

#### step gate
- review:
  - code reviewer に installed-package proof の十分性をレビューさせる
- expected tests:
  - issue-70 isolated package-installed init/update cutover regression
- report update:
  - installed-package cutover evidence を `report.md` に追記する
- commit:
  - issue-70 S03 用 Conventional Commit を作成する

### S90 — report / handoff evidence refresh
- 対象:
  - `report.md`
- 対応:
  - `handoff-validation-evidence` の 4 セクションを issue-70 実測値で埋める
  - docs impact は issue docs に閉じるため、恒久 docs の追加更新は行わない

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00070` branch の issue-70 実装差分全体
- required validation:
  - issue-70 targeted tests
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
  - `python -m unittest discover -v` informational sweep
- reviewer approvals:
  - final code review `pass`
  - final spec review `pass`
- report update:
  - final diff review verdict、validation evidence、scope外 failure、close-ready judgment、final commit または no-op rationale を `report.md` に残す
- commit expectation:
  - 追加修正があれば final commit を作成する。なければ evidence-only/no-op rationale を `report.md` に残す

## 未確定事項
- なし:
  - required host は `codex` / `copilot`
  - obsolete cleanup authority は top-level `managed_assets.obsolete_exact_file_paths`
  - workflow は current managed set に統合する

## final exit contract
- AC/EC 達成:
  - `AC-001` から `AC-007`、`EC-001` から `EC-003` が targeted validation と review で閉じている
- docs impact resolved:
  - `report.md` の `handoff-validation-evidence` が issue-70 実測値で埋まっている
- final diff approved:
  - final code review / final spec review がともに `pass`
  - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync --github` が成功
  - full-suite informational sweep の結果と scope 判定が `report.md` に残っている
