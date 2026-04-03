---
種別: 設計書（Issue）
ID: "iss-00050"
タイトル: "Host Adapter Scaffold And Final Parity"
関連GitHub: ["#50"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
依存: ["requirement.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00050 Host Adapter Scaffold And Final Parity — 設計（HOW）

## 目的・制約
- 目的:
  - installer 管理下で Codex/Copilot adapter scaffold を配布し、issue-00049 で固定した protocol を host-specific entrypoint に接続する。
  - provider assets / dogfooding workspace / docs parity / final spec review を 1 issue で閉じる。
- MUST / MUST NOT:
  - MUST:
    - managed skill sync の既存パターンを再利用する。
    - adapter 内容は thin host adapter contract を守る。
    - final parity と final spec review evidence を残す。
  - MUST NOT:
    - state logic を adapter に複製しない。
    - installer が unknown custom skill を削除しない既存 safety を壊さない。
- 非交渉制約:
  - issue-00049 の protocol contract に従う。
  - provider-side source of truth は `src/spec_dock/assets/codex_skills/` と `src/spec_dock/cli.py` に置く。
- 前提:
  - `_install_skill()` は managed skill 一覧を asset から `.agents/skills/` へ同期し、obsolete managed dir だけ pruning する。

## 既存実装 / 規約の理解
- 参照した実装 / docs:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`
  - `tests/test_init_update.py`
  - epic-00048 requirement/design/plan
- 現状理解:
  - installer は `_managed_skill_names()` と `_managed_skill_ownership_names()` を通じて配布対象と prune 対象を決めている。
  - bundled skill は `assets/codex_skills/<skill>/SKILL.md` だけをコピーする単純構成で、host adapter 追加も同じパターンで載せやすい。
  - `.agents/skills/` には repo local skills が共存するため、unknown custom dirs を保持する safety が重要。
- 採用するパターン:
  - adapter も bundled skill として扱い、`SKILL.md` を managed asset sync に乗せる。
  - adapter metadata が必要なら `.agents/host-adapters/meta.json` のような専用ファイルを installer managed asset として追加する。
  - final parity は provider asset 更新 -> installer sync / dogfooding refresh -> tests / validate -> spec review の順で閉じる。
- 採用しないもの:
  - installer とは別の ad-hoc generator 追加
  - host adapter ごとの独自 runtime wrapper 実装
  - final parity を別 issue へ再分割すること
- 影響範囲:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/`
  - 必要なら `src/spec_dock/assets/spec_dock/...` の docs/assets
  - `tests/test_init_update.py`
  - dogfooding `.agents/skills/` and related docs

## 依存関係分析
- upstream（先に固定するもの）:
  - issue-00049 で固定した protocol / read order contract
  - installer の managed skill sync / ownership / pruning safety
  - bundled skill asset layout の既存パターン
- downstream（upstream の上に載るもの）:
  - Codex/Copilot host adapter asset 本体
  - `.agents/host-adapters/meta.json`
  - dogfooding workspace parity と関連 docs
  - final spec review / closing evidence
- 実装起点:
  - 依存の少ない順に、adapter asset / metadata shape を先に固定し、その後 installer ownership と sync へ接続する。
  - parity refresh と final review は upstream が固まった後でのみ成立するため最後に置く。
- step sequencing implication:
  - S01 は thin adapter contract と metadata contract の fixed point を作る。
  - S02 は S01 で固定した asset/metadata を installer sync に載せる。
  - S03 は S02 の実装結果を dogfooding workspace / docs parity / validate に展開する。
  - S04 は S01-S03 の evidence が揃った後の close readiness review とする。

## 採用方針 / トレードオフ
- 論点:
  - adapter を managed skill だけで表現するか、metadata file も持つか
- 選択肢:
  - Option A:
    - adapter skill directory だけを追加する
  - Option B:
    - adapter skill directory + metadata file を追加する
- 決定:
  - Option B を採用する
  - 理由:
    - installer test と review で managed targets を明示しやすい
    - 将来 host 追加があっても ownership と generated target の一覧を機械可読で残せる

## インターフェース契約
- API / function / protocol / data boundary:
  - installer:
    - `_managed_skill_names()` に host adapter skill 名が加わる
    - `_install_skill()` が adapter skill を他 managed skill と同様に同期する
  - adapter assets:
    - `spec-dock-codex-adapter/SKILL.md`
    - `spec-dock-copilot-adapter/SKILL.md`
  - adapter metadata（必要時）:
    - `.agents/host-adapters/meta.json`
    - targets / generated_by / updated_at を持つ
  - docs parity:
    - provider asset docs と dogfooding docs が同じ host adapter guidance を指す

### UML（推奨: module / dependency）
```plantuml
@startuml
skinparam monochrome true
top to bottom direction

rectangle "src/spec_dock/cli.py
_install_skill()" as installer
rectangle "_managed_skill_names()
_managed_skill_ownership_names()" as ownership
rectangle "assets/codex_skills
generic + host adapters" as assets
rectangle ".agents/skills
managed output" as installed
rectangle ".agents/host-adapters/meta.json" as meta
rectangle "tests/test_init_update.py" as tests
rectangle "dogfooding docs / workspace parity" as parity
rectangle "issue-00049 protocol" as protocol

installer --> ownership : use ownership rules
ownership --> assets : enumerate managed assets
installer --> assets : copy/update
installer --> installed : managed sync
installer --> meta : optional managed sync
installed ..> protocol : read contract only
meta ..> protocol : declare targets
tests ..> installer : verify init/update
parity ..> installed : inspect generated output
parity ..> meta : inspect generated metadata
@enduml
```

## クラス / インターフェース詳細設計（必要時）
- Class / Interface:
  - `_managed_skill_names()` / `_managed_skill_ownership_names()` / `_install_skill()`
- responsibility:
  - adapter skill の managed ownership と copy/prune を保証する
- collaboration:
  - `tests/test_init_update.py` が installer behavior を固定する

## 変更計画
- Add:
  - host adapter skill assets
  - optional adapter metadata asset
  - installer tests / docs parity evidence
- Modify:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - dogfooding `.agents/skills/` mirror and related docs
- Delete:
  - なし
- Move/Rename:
  - なし
- Read only:
  - issue-00049 protocol semantics（再定義しない）

## 要件 → 設計マッピング
- AC-001 -> installer managed skill sync に adapter を追加する
- AC-002 -> adapter `SKILL.md` と metadata で thin adapter contract を固定する
- AC-003 -> provider/dogfooding parity と validation/tests を揃える
- AC-004 -> final spec review record を report に残す
- EC-001 -> unknown custom skill preservation を installer tests で確認する
- EC-002 -> managed ownership の片側更新 / pruning 安全性を tests で確認する
- EC-003 -> provider asset を正本に dogfooding parity を回復する

## テスト戦略
- Unit:
  - installer managed skill helper の挙動を既存 installer tests で固定する
- Integration:
  - `tests/test_init_update.py`
  - 必要なら `tests/test_cli.py`
- E2E / manual:
  - `spec-dock update .`
  - `./spec-dock/scripts/spec-dock validate`
  - `.agents/skills/` と metadata の diff 確認
- migration / rollback / feature flag if needed:
  - feature flag なし
  - rollback は adapter assets / installer changes を issue 単位で戻す

## 要件 / 例外 -> verification mapping
- AC-001 -> installer sync verification
- AC-002 -> adapter content review
- AC-003 -> parity + validate + tests
- AC-004 -> spec review record
- EC-001 -> unknown custom skill preservation test
- EC-002 -> targeted managed ownership/pruning test
- EC-003 -> parity evidence

## リスク / 移行 / ロールバック（必要時）
- risk:
  - adapter skill 名や ownership 名のずれで pruning が不正になる可能性がある。
  - dogfooding workspace だけ更新して provider asset が未更新だと parity drift が残る。
  - adapter 内容が厚くなり、protocol の再実装が紛れ込む可能性がある。
- migration:
  - repo 既存 user は `spec-dock update` 実行で adapter を受け取る。
- rollback:
  - adapter asset 追加と installer changes をまとめて戻す。

## 未確定事項
- なし:
  - metadata file は `.agents/host-adapters/meta.json` に固定する。
