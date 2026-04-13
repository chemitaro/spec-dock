---
種別: 要件定義書（Issue）
ID: "iss-00068"
タイトル: "Install root tree and asset classification"
関連GitHub: ["#68"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-12"
親: ["epic-00067", "init-local-00003"]
---

# iss-00068 Install root tree and asset classification — 要件定義（WHAT / WHY）

## 目的
- agent-tooling 用 provider-side source-of-truth に install 後レイアウトと同型の土台を導入し、maintainer が source tree を読んだ時点で install 先の構造と責務分離を理解できる状態を作る。
- shared assets、Codex 固有 assets、GitHub 固有 assets、GitHub workflow assets の配置規約を tree 自体に固定し、後続 issue が packaging や installer 挙動を安全に切り替えられる前提を整える。

## 背景・現状
- 現状の挙動:
  - provider-side の agent-tooling assets は `src/spec_dock/assets/codex_skills/` に集約されており、shared skills、host adapter metadata、native shim source が同居している。
  - 一方で install 後の配置先は `.agents/skills/`、`.agents/host-adapters/`、`.codex/agents/`、`.github/agents/`、`.github/workflows/` に分かれている。
- 現状の課題:
  - source tree と install 後 tree が対応していないため、maintainer は source file を読むたびに install 先を mentally translate する必要がある。
  - `spec-dock-codex-adapter` / `spec-dock-copilot-adapter` のような reusable shared skill と、`.codex/agents/spec-dock.toml` / `.github/agents/spec-dock.agent.md` のような host-native file が同じ family として見えにくい。
  - `.github/workflows/ci.yml` は install 後には存在するが、provider-side source-of-truth の tree には同型で表れていない。
- 再現手順:
  1. `src/spec_dock/assets/codex_skills/` を確認する。
  2. `.agents/`、`.codex/`、`.github/` の checked-in dogfooding layout と見比べる。
- 観測点:
  - Filesystem:
    - `src/spec_dock/assets/codex_skills/`
    - `.agents/`
    - `.codex/`
    - `.github/`
- 情報源:
  - `spec-dock/.../epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/requirement.md`
  - `spec-dock/.../epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/design.md`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/host-adapters/meta.json`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` maintainer
  - agent-tooling assets を追加・移動・レビューする contributor
- 代表シナリオ:
  - maintainer が provider-side source tree を見て、shared / host-specific / workflow の配置先をそのまま理解する。
  - 後続 issue で installer や packaging を変更する際に、「どの file がどの subtree の正本か」を install-shaped tree から一意に参照する。

## スコープ
- MUST:
  - `src/spec_dock/assets/install_root/` を新設し、agent-tooling 用 provider-side source-of-truth の基底ルートとして定義する。
  - `install_root/` 配下に `.agents/`、`.codex/`、`.github/` を install 後構造と同型で配置し、GitHub workflow assets は `.github/workflows/` へ配置する。
  - shared skills は `.agents/skills/`、shared metadata は `.agents/host-adapters/`、Codex 固有 file は `.codex/`、GitHub 固有 file は `.github/agents/`、GitHub workflow assets は `.github/workflows/` に分類する。
  - `spec-dock-codex-adapter` と `spec-dock-copilot-adapter` を reusable shared skill asset として `.agents/skills/` 側へ分類する。
  - この issue の in-scope asset inventory を明示し、その inventory の authoring authority を `install_root/` に固定する。
  - provider-side source tree listing と path assertions で、新しい分類規約を観測可能にする。
- MUST NOT:
  - installer の source discovery 切替、managed cleanup 契約変更、workflow 同期ロジック追加をこの issue の完了条件に含めない。
  - package data inclusion や built artifact 配布保証までこの issue で閉じようとしない。
  - Claude Code 用 subtree を追加しない。
  - in-scope asset inventory の authoritative source を `install_root/` 以外に残したまま完了扱いにしない。
- OUT OF SCOPE:
  - `pyproject.toml` / `setup.py` の package data 修正
  - `src/spec_dock/cli.py` の install source 切替
  - managed ownership / obsolete path cleanup の実装更新
  - init/update integration test や packaged-install smoke test の完成
  - legacy `codex_skills` authority の最終 retire

## 境界
- Always:
  - issue-1 は source tree foundation と asset classification の固定だけを担う。
  - install 後 relative path と同じ見え方を provider-side source tree に持ち込む。
- Ask:
  - shared asset と host-specific asset の所属が曖昧な file が見つかった場合だけ、分類方針を明示確認する。
- Never:
  - file の役割分類が未確定なまま packaging や installer 側の契約を書き換えない。
  - source tree を provider 都合の grouping に戻さない。

## 非交渉制約
- `epic-00067` の E-RQ-001、E-RQ-002、E-AC-001 をこの issue の primary closure target とする。
- `.agents` は shared、`.codex` は Codex 固有、`.github` は GitHub 固有という責務分離を崩さない。
- GitHub workflow assets の配置先は `.github/workflows/` としてこの issue で固定するが、同期契約・managed ownership・packaged-install 保証は後続 issue に委ねる。
- 新しい source root 名は `src/spec_dock/assets/install_root/` とする。
- 新規 path は lowercase を原則とし、skill asset の既存 filename convention である `SKILL.md` だけを明示例外として許容する。

## 前提
- consumer repo 側の install target path contract は既存の `.agents/`、`.codex/`、`.github/`、`.github/workflows/` を維持する。
- `src/spec_dock/cli.py` と `host-adapters/meta.json` は install 先知識を保持しているが、本 issue ではそれを「第二の正本」ではなく「後続 issue が従う前提」として扱う。
- checked-in `.agents/`、`.codex/`、`.github/` は install 後レイアウトの参照例として使える。
- 本 issue の in-scope asset inventory は次の current assets 全件とする。
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-dock-adr-facilitation/SKILL.md`
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - `.agents/host-adapters/meta.json`
  - `.codex/agents/spec-dock.toml`
  - `.github/agents/spec-dock.agent.md`
  - `.github/workflows/ci.yml`

## In-Scope Asset Authority Inventory
| asset | class | authoritative provider-side path | installed relative path | legacy duplicate status |
| --- | --- | --- | --- | --- |
| `spec-driven-tdd-workflow` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` | `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-adr-facilitation` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-adr-facilitation/SKILL.md` | `.agents/skills/spec-dock-adr-facilitation/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-epic-planning` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | `.agents/skills/spec-dock-epic-planning/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-initiative-planning` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | `.agents/skills/spec-dock-initiative-planning/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-issue-execution` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` | `.agents/skills/spec-dock-issue-execution/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-codex-adapter` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md` | `.agents/skills/spec-dock-codex-adapter/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| `spec-dock-copilot-adapter` skill | shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md` | `.agents/skills/spec-dock-copilot-adapter/SKILL.md` | `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| host adapter metadata | shared metadata | `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` | `.agents/host-adapters/meta.json` | `src/spec_dock/assets/codex_skills/host-adapters/meta.json` が残る場合は transitional duplicate。編集正本として扱わない。 |
| Codex native shim | host-specific asset | `src/spec_dock/assets/install_root/.codex/agents/spec-dock.toml` | `.codex/agents/spec-dock.toml` | `src/spec_dock/assets/codex_skills/native-shims/spec-dock.toml` が残る場合は transitional duplicate。編集正本として扱わない。 |
| GitHub agent file | host-specific asset | `src/spec_dock/assets/install_root/.github/agents/spec-dock.agent.md` | `.github/agents/spec-dock.agent.md` | `src/spec_dock/assets/codex_skills/native-shims/spec-dock.agent.md` が残る場合は transitional duplicate。編集正本として扱わない。 |
| GitHub workflow asset | workflow asset | `src/spec_dock/assets/install_root/.github/workflows/ci.yml` | `.github/workflows/ci.yml` | legacy provider-side duplicate は持たない。`install_root` 側のみを authoring source とする。 |

### Authority Verification Rule
- review では上の inventory の各行について、`authoritative provider-side path` が唯一の編集正本であることを確認する。
- `legacy duplicate status` に legacy path が書かれている場合、その path は残存を許容しても `transitional duplicate` としてのみ扱い、authoritative source / install_root の代替根拠として扱ってはならない。
- `legacy duplicate status` に legacy provider-side duplicate を持たないと書かれている asset は、`install_root` 以外の provider-side source を作ってはならない。
- repo-wide verification は provider-side repo 全体、すなわち `src/spec_dock/assets/` 配下を search scope として行う。
- 各 in-scope asset について repo-wide search を行った結果、許容される provider-side source 候補は `authoritative provider-side path` と inventory に明示された legacy duplicate path だけでなければならない。
- inventory に記載されていない追加の provider-side duplicate が 1 件でも見つかった場合、その時点で review は fail とする。
- `transitional duplicate` と認められるのは、inventory に path が明示されていること、かつ repo-wide search でその path 以外の competing source が見つからない場合に限る。
- authority retirement が完了した状態は、inventory に列挙された legacy duplicate paths が repo-wide search で 0 件になることで観測する。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - provider-side agent-tooling assets を確認する
  - When:
    - `src/spec_dock/assets/install_root/` を tree listing する
  - Then:
    - `.agents/`、`.codex/`、`.github/` が存在し、install 後構造と同型の subtree が確認できる
    - `.github/workflows/` が GitHub workflow assets の配置先として source tree 上に定義されている
  - 観測点:
    - source tree listing
    - path existence assertions
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - in-scope asset inventory の全件が source tree に配置されている
  - When:
    - 各 file の配置先を review する
  - Then:
    - in-scope inventory に含まれる shared skills 全件は `.agents/skills/` にある
    - `host-adapters/meta.json` は `.agents/host-adapters/` にある
    - `spec-dock.toml` は `.codex/agents/` にある
    - `spec-dock.agent.md` は `.github/agents/` にある
    - in-scope workflow assets 全件は `.github/workflows/` にある
    - 上記 inventory 全件が shared / host-specific / workflow の分類規約に従っている
  - 観測点:
    - in-scope inventory path assertions
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - この issue が扱う in-scope asset inventory を review する
  - When:
    - provider-side source-of-truth の所在を確認する
  - Then:
    - in-scope inventory 全件の authoring location は `install_root/` 側に定義されている
    - in-scope inventory については `install_root/` 以外に competing authoritative source を持たない
    - legacy path が一時的に残る場合でも、それは非正本の transitional copy としてのみ扱われる
  - 観測点:
    - In-Scope Asset Authority Inventory
    - Authority Verification Rule
    - repo-wide search over `src/spec_dock/assets/`

## 例外・エッジケース
- EC-001:
  - 条件:
    - host-specific behavior を記述する adapter skill が存在する
  - 期待:
    - reusable skill asset である限り `.agents/skills/` に分類され、host-native shim と同じ subtree へは置かれない
  - 観測点:
    - `spec-dock-codex-adapter/SKILL.md`
    - `spec-dock-copilot-adapter/SKILL.md`
- EC-002:
  - 条件:
    - GitHub workflow file を source tree に含める
  - 期待:
    - in-scope workflow assets は例外なく `.github/workflows/<name>.yml` に分類される
    - ただし workflow sync の installer 契約、managed ownership、packaged-install 保証は後続 issue に委ねる
  - 観測点:
    - `src/spec_dock/assets/install_root/.github/workflows/`

- EC-003:
  - 条件:
    - 将来 Claude Code のような新 host を追加したい
  - 期待:
    - 今回は実装しないが、`.agents` を壊さず sibling host root を追加できる構造が維持される
  - 観測点:
    - `install_root/` の top-level directory model

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - provider-side source tree に Codex native shim を置く
  - Output:
    - `src/spec_dock/assets/install_root/.codex/agents/spec-dock.toml`

- EX-002:
  - Input:
    - provider-side source tree に GitHub workflow を置く
  - Output:
    - `src/spec_dock/assets/install_root/.github/workflows/ci.yml`

## 用語（ドメイン語彙）
- TERM-001:
  - install_root:
    - agent-tooling 用 provider-side source-of-truth として導入する install-shaped root
- TERM-002:
  - shared asset:
    - host を跨いで共有される `.agents` 配下の asset
- TERM-003:
  - host-specific asset:
    - 特定 host root にのみ存在する `.codex` または `.github` 配下の asset
- TERM-004:
  - workflow asset:
    - `.github/workflows/` 配下に置く GitHub workflow file

## 未確定事項
- なし:
  - source root、shared / host-specific / workflow の責務分離、workflow の配置先は epic で確定済み。
