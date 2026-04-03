---
種別: 要件定義書（Issue）
ID: "iss-00050"
タイトル: "Host Adapter Scaffold And Final Parity"
関連GitHub: ["#50"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
親: ["epic-00048", "init-local-00002"]
---

# iss-00050 Host Adapter Scaffold And Final Parity — 要件定義（WHAT / WHY）

## 目的
- Codex/Copilot 向け host adapter scaffold を `init/update` managed asset として配布し、issue-00049 で固定した protocol contract を両 host で再利用可能にする。
- provider assets / dogfooding workspace / installer tests / docs parity / final spec review をこの issue で閉じる。

## 背景・現状
- 現状の挙動:
  - installer は `.agents/skills/` に bundled skill を managed asset として配布する。
  - 現在の managed skills は `spec-dock-*` 系だけで、host-specific adapter は存在しない。
  - epic-00048 の discussion では `core protocol + generic skill + thin host adapter` の 3 層を採る方針が固まっている。
- 現状の課題:
  - Codex/Copilot から `spec-dock` を扱う導線が generic skill だけでは薄く、host ごとの入口文面や read order を人間が都度補っている。
  - installer が host adapter を配布しないため、repo 初期化後に adapter が自動で揃わない。
  - provider docs / dogfooding docs / generated assets を final parity まで閉じる owner が必要である。
- 再現手順:
  1. `src/spec_dock/cli.py` の `_install_skill()` と `src/spec_dock/assets/codex_skills/` を確認する。
  2. repo root の `.agents/skills/` を見る。
  3. Codex/Copilot 向け adapter 専用 entry が無いことを確認する。
- 観測点:
  - Filesystem:
    - `.agents/skills/`
    - `src/spec_dock/assets/codex_skills/`
  - Code:
    - `src/spec_dock/cli.py`
  - Docs:
    - epic-00048 discussion / design
- 情報源:
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/requirement.md`
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/design.md`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/`
  - `tests/test_init_update.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - repo を `spec-dock init/update` でセットアップする maintainer
  - Codex/Copilot から spec-dock を使う orchestrator / sub-agent
- 代表シナリオ:
  - maintainer が `spec-dock update .` を実行すると、generic skill と一緒に host adapter が managed asset として同期される。
  - Codex/Copilot の各 adapter は issue-00049 で固定した protocol を参照し、host-specific wording だけを持つ。

## スコープ
- MUST:
  - Codex/Copilot 向け host adapter scaffold を managed skill/asset として追加する。
  - installer の `init/update` で adapter が配布・更新・obsolete managed adapter pruning の対象になることを保証する。
  - host adapter が `active.json` / `index.json` / `deps-issues.json` / `index-all.json` の protocol を再実装しないよう、thin adapter contract を docs と asset 内容で固定する。
  - provider assets と dogfooding workspace の parity を回復する。
  - host adapter metadata は `.agents/host-adapters/meta.json` として managed asset で持つ。
  - final spec review で epic-00048 の 2 issue split に矛盾がないことを確認する。
- MUST NOT:
  - host adapter に独自の state 生成ロジックを持たせない。
  - multi-host 一般化や plugin system 化まで拡張しない。
  - issue-00049 の protocol contract を独断で再定義しない。
- OUT OF SCOPE:
  - invalid artifact prevention の architecture-level 実装
  - Codex/Copilot 以外の host adapter
  - runtime の大規模リファクタ

## 境界
- Always:
  - host adapter は thin entrypoint であり、core protocol / generic skill を参照する。
  - adapter は installer owned managed asset として扱う。
  - docs parity と final review の owner は本 issue とする。
- Ask:
  - adapter metadata を dedicated file にするか、skill directory naming のみで管理するか。
  - Copilot adapter を `.agents/skills/` だけで表現できるか、追加 docs が要るか。
- Never:
  - host ごとに別の JSON state contract を作らない。
  - installer が unknown custom skills を pruning しないよう existing safety を壊さない。

## 非交渉制約
- issue-00049 で固定した protocol contract に従うこと。
- provider-side source of truth は `src/spec_dock/assets/...` と `src/spec_dock/cli.py` にあること。
- uppercase path を新たに増やさないこと。

## 前提
- issue-00049 が先行し、read-order / payload contract が fixed point になっている。
- `.agents/skills/` managed asset sync は既存 installer の責務として再利用できる。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - clean repo で `spec-dock init` または `spec-dock update` を実行する
  - When:
    - managed skills を同期する
  - Then:
    - generic skill に加えて Codex/Copilot 向け host adapter scaffold が配布・更新される
  - 観測点:
    - `.agents/skills/`
    - `tests/test_init_update.py`
- AC-002:
  - Actor:
    - host adapter 実装者 / reviewer
  - Given:
    - generated adapter files
  - When:
    - adapter 内容を確認する
  - Then:
    - host 固有差分は entry wording に限定され、protocol/state 解釈ロジックの再実装は含まれない
  - 観測点:
    - adapter `SKILL.md`
    - related docs / review record
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - provider assets と dogfooding workspace
  - When:
    - parity と validation を確認する
  - Then:
    - provider/dogfooding の asset/docs parity が回復し、`validate` と relevant tests が pass する
  - 観測点:
    - `./spec-dock/scripts/spec-dock validate`
    - relevant installer/runtime tests
    - parity evidence
- AC-004:
  - Actor:
    - spec reviewer
  - Given:
    - epic-00048 の 2 issue docs と final changeset
  - When:
    - final spec review を行う
  - Then:
    - issue-00049 と issue-00050 の責務境界、verification mapping、rollout order に矛盾がない
  - 観測点:
    - spec review record
    - issue docs / epic docs / report

## 例外・エッジケース
- EC-001:
  - 条件:
    - repo に unknown custom skill directory がある
  - 期待:
    - installer は managed adapter だけを同期し、unknown custom skill は保持する
  - 観測点:
    - update 実行後の `.agents/skills/` 差分
- EC-002:
  - 条件:
    - 片方 host adapter だけ更新が必要になる
  - 期待:
    - managed ownership の範囲内で片方だけ差分更新でき、他方や generic skill を壊さない
  - 観測点:
    - targeted init/update test
- EC-003:
  - 条件:
    - dogfooding workspace が provider asset と drift している
  - 期待:
    - provider asset を正本として parity を回復し、manual-only な差分は残さない
  - 観測点:
    - parity test / diff evidence

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `spec-dock update .`
  - Output:
    - `.agents/skills/spec-dock-codex-adapter/SKILL.md` と `.agents/skills/spec-dock-copilot-adapter/SKILL.md` が managed asset として同期される

## 用語（ドメイン語彙）
- TERM-001:
  - thin host adapter:
    - host 固有の entry wording だけを持ち、state contract や orchestration policy を再実装しない adapter
- TERM-002:
  - managed asset:
    - installer が配布・更新・obsolete pruning を管理するファイル群
- TERM-003:
  - final parity:
    - provider asset / dogfooding workspace / docs / tests が同じ contract を指している状態

## 未確定事項
- なし:
  - host adapter metadata は `.agents/host-adapters/meta.json` を採用する。
