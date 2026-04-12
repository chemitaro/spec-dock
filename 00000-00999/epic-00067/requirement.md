---
種別: 要件定義書（Epic）
ID: "epic-00067"
タイトル: "Installed layout aligned asset source structure for agent tooling"
関連GitHub: ["#67"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-12"
親: ["init-local-00003"]
---

# epic-00067 Installed layout aligned asset source structure for agent tooling — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00003` の architecture maintenance / hardening として、agent-tooling 用 assets の source-of-truth と installed layout の対応を固定し、maintainer が source tree を読んだときに install 後の構造をそのまま理解できる状態を作る。
  - 現在の `src/spec_dock/assets/codex_skills/` と `src/spec_dock/assets/spec_dock/` の分断と責務混在を architecture gap として閉じ、今後の host 追加や workflow 追加でも layout 再整理を繰り返さない基盤を作る。
- この epic が提供する能力:
  - provider-side agent-tooling assets を `src/spec_dock/assets/install_root/` 配下で install-shaped に管理できる。
  - shared assets は `.agents/`、Codex CLI specific assets は `.codex/`、GitHub specific assets と workflows は `.github/` へ責務分離できる。
  - installer は最小変換・構造保持同期を行う contract に統一される。
  - packaged install でも hidden path / dotfile を含む install-shaped assets が確実に配布される。

## 背景・現状
- 現状の provider-side source は、shared skills、host adapter metadata、native shim source が `src/spec_dock/assets/codex_skills/` に混在している。
- 一方で実際の installed target は `.agents/skills`、`.agents/host-adapters`、`.codex/agents`、`.github/agents`、`.github/workflows` に分散している。
- `src/spec_dock/cli.py` と `src/spec_dock/assets/codex_skills/host-adapters/meta.json` は install target をすでに理解しているが、source tree 自体はその構造を直接表していない。
- そのため maintainer は source 側の file を読むたびに install 先へ mentally translate する必要があり、shared / host-specific / workflow の責務境界も tree から読み取りづらい。
- ユーザー方針として、`.agents` は shared、`.codex` は Codex 固有、`.github` は GitHub 固有に分け、GitHub workflows も `.github` 配下で扱うこと、Claude Code は今回は導入しないが将来拡張しやすくすること、installer はあまり変換せず構造を保ったまま同期することが確定している。

## ユースケース
- happy path:
  - maintainer は `src/spec_dock/assets/install_root/.agents/skills/...` や `src/spec_dock/assets/install_root/.codex/agents/...` を直接編集し、その relative path のまま installed repo へ反映される。
  - GitHub workflows も `src/spec_dock/assets/install_root/.github/workflows/...` からそのまま `.github/workflows/...` へ同期される。
  - `spec-dock init` / `spec-dock update` は install-shaped source tree を consumer repo に同期し、flattening や host 別の暗黙変換を行わない。
- exception / operation scenario:
  - obsolete managed path を prune するときでも、明示的に managed と定義された path のみを対象とし、user-authored files は巻き込まない。
  - 将来 Claude Code を追加するときは shared `.agents` を壊さず sibling host root を追加するだけで拡張できる。
  - adapter skill は host-specific behavior を記述していても reusable shared skill asset として `.agents/skills` に保持され、host-native shim や workflow と混同しない。

## Epic requirements
- E-RQ-001:
  - agent-tooling 用 provider-side source-of-truth を `src/spec_dock/assets/install_root/` に固定すること。
  - `install_root/` は consumer repo の installed layout と同型の directory contract を持つこと。
- E-RQ-002:
  - `.agents/` は shared layer とし、shared skills と shared agent-support assets のみを置くこと。
  - `spec-dock-codex-adapter` と `spec-dock-copilot-adapter` は host-specific behavior を記述する reusable shared skill asset として `.agents/skills` に置くこと。
  - `.codex/` は Codex CLI specific layer とし、Codex native shim / host-native entrypoint のみを置くこと。
  - `.github/` は GitHub specific layer とし、GitHub agent files と workflows を置くこと。
- E-RQ-003:
  - `.github/workflows/` を first-class source-of-truth asset として扱うこと。
  - workflow files は source 側でも install 側でも `.github/workflows/<name>.yml` の relative path を維持すること。
- E-RQ-004:
  - installer は structure-preserving sync を行うこと。
  - 許容される変換は source root から target root への基底 path 置換、明示 managed path の cleanup、必要最小限の permission 調整に限定すること。
  - flattening、暗黙 rename、host-specific subtree の再配置は許可しないこと。
- E-RQ-005:
  - managed cleanup には単一の canonical ownership model を持つこと。
  - canonical source of currently managed files は `install_root/` 配下の実在 file tree とすること。
  - obsolete managed files の canonical source は manifest に記述された explicit obsolete path set とすること。
  - workflow files も `install_root/.github/workflows/` に存在する限り managed file set に含まれること。
  - installer は current managed file set と explicit obsolete managed file set だけを対象にし、それ以外を delete/prune しないこと。
- E-RQ-006:
  - `src/spec_dock/assets/codex_skills/` と `src/spec_dock/assets/spec_dock/` の現状分離を architecture gap として明示し、その gap の本質が runtime capability 不足ではなく source layout と install layout の不一致であることを固定すること。
  - `install_root/` 導入後は agent-tooling assets の authority を `install_root/` へ一本化し、legacy `codex_skills/` は agent-tooling source-of-truth としては retire されること。
- E-RQ-007:
  - `src/spec_dock/cli.py` と host adapter metadata は install target knowledge を保持してよいが、その役割は tree の第二の正本ではなく、host boundary と managed cleanup の補助情報に限定すること。
- E-RQ-008:
  - Claude Code 実装は本 epic の scope に含めないこと。
  - ただし install-shaped directory model は新しい host subtree を sibling として追加できる拡張性を持つこと。
- E-RQ-009:
  - packaged install contract を requirement として固定すること。
  - `install_root/` 配下の hidden directories、dotfiles、workflow files、native shims は wheel / sdist / local package install に含まれ、package-installed `spec-dock init/update` で解決できなければならない。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - provider-side agent-tooling assets を確認する
  - When:
    - source tree を listing / review する
  - Then:
    - `src/spec_dock/assets/install_root/` 配下に `.agents/`、`.codex/`、`.github/` が存在し、責務どおりに資産が配置されている
    - adapter skills は `.agents/skills/` に配置され、host-native shims や workflows は host root に分離されている
  - 観測点:
    - source tree listing
    - path assertions
- E-AC-002:
  - Given:
    - clean target repo に `spec-dock init` または `spec-dock update` を実行する
  - When:
    - installer が agent-tooling assets を同期する
  - Then:
    - source tree の relative path を保ったまま `.agents`、`.codex`、`.github`、`.github/workflows` が生成・更新される
    - flattening や暗黙 rename は発生しない
    - managed cleanup は current managed file set と explicit obsolete managed file set のみに作用する
  - 観測点:
    - init/update integration tests
    - filesystem assertions
    - managed/unmanaged boundary tests
- E-AC-003:
  - Given:
    - shared skill、host-specific file、workflow file のいずれかを source tree に追加・更新する
  - When:
    - installer を再実行する
  - Then:
    - 該当 file は正しい subtree に同じ relative path のまま反映され、unrelated managed files は安定し、managed 外の file は保持される
    - explicit obsolete managed paths は prune されるが、user-authored files は prune されない
  - 観測点:
    - update regression tests
    - cleanup safety tests
- E-AC-004:
  - Given:
    - current mixed layout と proposed install-shaped layout を比較する
  - When:
    - requirement / design / plan を review する
  - Then:
    - architecture gap、target state、installer policy、future host extension point、legacy authority retirement が一貫して説明されている
  - 観測点:
    - spec review pass
- E-AC-005:
  - Given:
    - Claude Code はまだ導入しない
  - When:
    - install-shaped model を inspect する
  - Then:
    - Claude Code 実装は無いが、追加 host の sibling root を置ける設計余地が残っている
  - 観測点:
    - directory model review
    - path boundary assertions
- E-AC-006:
  - Given:
    - package-installed `spec-dock` を wheel / sdist / local package install から実行する
  - When:
    - `spec-dock init` または `spec-dock update` が install_root 配下 assets を解決する
  - Then:
    - hidden directories、dotfiles、workflow files、native shims を含む install-shaped assets が欠落せず consumer repo に反映される
  - 観測点:
    - packaged-install smoke test
    - built artifact content check
- E-AC-007:
  - Given:
    - implementation 完了後の source tree を確認する
  - When:
    - agent-tooling assets の authority をレビューする
  - Then:
    - `install_root/` が唯一の authority になっている
    - legacy `codex_skills/` は agent-tooling source-of-truth として参照されず、drift 可能な二重正本状態が残っていない
  - 観測点:
    - legacy authority retirement check
    - docs / tests / installer source discovery assertions

## スコープ
- MUST:
  - `install_root/` を導入する
  - `.agents` / `.codex` / `.github` の責務分離を固定する
  - `.github/workflows` を source-of-truth に含める
  - installer の structure-preserving sync contract を固定する
  - packaged install で hidden assets を含めて配布・解決されることを保証する
  - tests / docs / dogfooding parity を install-shaped layout に合わせる
- MUST NOT:
  - host-specific assets を shared subtree に戻す
  - installer による flattening や暗黙 path rewrite を許可する
  - Claude Code 実装を今回混ぜる
  - `spec_dock/` scaffold assets を agent-tooling layout の正本に使う
  - `install_root/` と legacy `codex_skills/` の二重 authority を放置する
- OUT OF SCOPE:
  - Claude Code runtime / adapter 実装
  - spec-dock consumer workspace scaffold 自体の全面再設計
  - workflow 個別ロジックの機能拡張

## 境界
- Always:
  - source tree と installed tree の relative path semantics を保つ
  - shared assets は `.agents` に、host-specific assets は host root に置く
  - workflow は `.github/workflows` に置く
  - cleanup は current managed file set と explicit obsolete managed file set に限定する
- Ask:
  - 新しい asset の所属が shared か host-specific か曖昧なときは先に分類を確定する
- Never:
  - source tree を file count 削減のために混在構造へ戻さない
  - installer を layout translator として肥大化させない
  - managed cleanup を manifest 未定義 path や user-authored path へ拡張しない

## 非機能要件
- readability:
  - source tree を見ただけで install target が理解できること
- reliability / consistency:
  - 同じ source tree から同じ installed layout が再現できること
  - packaged install でも local checkout と同等の asset 解決ができること
- maintainability:
  - 新しい host や workflow を subtree 追加で扱えること
- operations:
  - layout change を tree diff と path assertion でレビューできること

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/codex_skills/`
  - `src/spec_dock/assets/spec_dock/`
  - `src/spec_dock/assets/install_root/`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/host-adapters/meta.json`
  - package build / asset inclusion contract
  - `tests/test_cli.py`
  - `tests/test_init_update.py`
  - checked-in `.agents/`, `.codex/`, `.github/` dogfooding state
- external dependency:
  - Codex CLI host discovery contract
  - GitHub Copilot custom agent / workflow contract
- compatibility:
  - consumer repo の installed target path は維持する
  - future host は sibling root 追加で拡張できる

## 未確定事項
- なし:
  - source root、責務分離、workflow placement、installer policy は本 epic で固定する
