# iss-00050 status report

Branch: `iss-00050-host-adapter-scaffold-and-final-parity`

## 1. Issue goal

`iss-00050` は、spec-dock の host adapter scaffold を追加し、Codex / Copilot 向けの配布物・メタデータ・テスト整合性・最終 parity をまとめて閉じる issue です。

主な到達点は以下です。
- `.agents/skills/spec-dock-codex-adapter/SKILL.md` の追加
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md` の追加
- `.agents/host-adapters/meta.json` の追加
- `tests/test_init_update.py` への parity 追加
- `./spec-dock/scripts/spec-dock validate` での最終確認

## 2. すでに完了していること

**確定済み**
- S01 は完了し、`842b453` にコミット済み
- S02 は完了し、`af49e60` にコミット済み
- host adapter 系の新規 asset は staged で追加済み
- installer / update parity に関するテスト追加も staged で入っている

**S03 の現状**
- S03 implementation は戻ってきている
- ただし、review 前の diff triage が進行中
- つまり、実装は着地しつつあるが、差分の妥当性確認は未完了

## 3. Current branch / commit milestones

- branch: `iss-00050-host-adapter-scaffold-and-final-parity`
- milestone: `842b453` = S01 completed
- milestone: `af49e60` = S02 completed
- current HEAD: `af49e60`
- current state: S03 の差分を review 可能な形に絞り込む段階

## 4. Current S03 status

**期待される / 必須の surface**
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `.agents/host-adapters/meta.json`
- `tests/test_init_update.py` parity additions
- `./spec-dock/scripts/spec-dock validate`

**現時点の認識**
- 新規 host adapter asset 3 点は issue 目的に一致している
- `tests/test_init_update.py` の追加も、managed asset 配布と contract 固定という観点では自然
- ただし、S03 は「実装完了」ではなく「差分の妥当性確認中」という扱い

## 5. Suspicious vs expected diffs

### 確認済みで期待通りに見える差分
- `.agents/host-adapters/meta.json`
- `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
- `tests/test_init_update.py` への managed asset / parity 追加

### 要確認だが現時点では suspicious
- `spec-dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - projection 定数の追加と JSON payload への `projection` 付与が入っており、S03 の主目的からは少し外れて見える
  - ただし、validate / presentation の整合のための副作用である可能性はある
- `tests/test_init_update.py` 内の `issue_gateway` / `git_gateway` 周辺変更
  - ルーティング契約や呼び出し引数の変化が混ざっているように見える
  - host adapter parity ではなく、別の behavior fix が紛れ込んでいないか確認が必要

### 現時点では「説明がつく」可能性が高い差分
- 以下の大きな docs deletion は、provider-side の対応 asset が存在しないなら parity cleanup として妥当な可能性がある
  - `spec-dock/docs/spec-dock-guide-old.md`
  - `spec-dock/docs/spec-dock-guide.md`
  - `spec-dock/docs/sync.md`
  - `spec-dock/docs/workflow-adr.md`
  - `spec-dock/docs/workflow-issue.md`
- ただし、削除が本当に意図通りかは、asset mirror の対応関係を見て最終確認する前提

## 6. Risks / blockers

- `json_state.py` の変更が、host adapter parity ではなく presentation ロジックの拡張になっていないか
- `tests/test_init_update.py` の `issue_gateway` / `git_gateway` 差分が、期待されたテスト修正を超えていないか
- docs deletion が「未実装の provider-side mirror なし」ではなく、単なる参照漏れや移設漏れでないか
- `./spec-dock/scripts/spec-dock validate` が S03 の最終 gate になるため、ここで不整合が出ると review に進めない

## 7. Recommended next steps

1. staged diff をファイル単位で再確認し、`json_state.py` と `tests/test_init_update.py` の変更意図を明文化する
2. docs deletion が provider-side asset 不在による parity cleanup であることを確認する
3. `./spec-dock/scripts/spec-dock validate` を実行して、S03 の contract / parity / presentation を一括確認する
4. validate が通れば、review 向けに「期待差分のみ」に整理して共有する
5. もし `json_state.py` や gateway 周辺に scope creep があるなら、S03 から切り出して別 issue 化する

## Handoff note

現状は「S01/S02 完了、S03 実装戻り済み、ただし review 前の triage 中」です。  
次の担当者は、まず suspicious diff の意図確認と validate の通過確認から入るのが安全です。
