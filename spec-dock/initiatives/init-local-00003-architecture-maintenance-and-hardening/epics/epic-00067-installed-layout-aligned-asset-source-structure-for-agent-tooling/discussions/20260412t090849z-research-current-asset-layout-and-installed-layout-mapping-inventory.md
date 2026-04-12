---
種別: research
ID: "20260412t090849z-research"
タイトル: "current asset layout and installed layout mapping inventory"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-04-12"
親: ["epic-00067"]
関連: []
---

# 20260412t090849z-research current asset layout and installed layout mapping inventory

## 調査目的 (必須)
- spec-dock の provider-side asset source tree と installed tree の対応関係を整理し、どこが混在していて、次の設計で何を決める必要があるかを明らかにする。
- epic-00067 の requirement / design に入る前の inventory として、現状の正本配置と導入先配置を固定する。
- ユーザーが問題提起した「source 側の見た目と install 後の構造が対応していない」という architecture gap を、実ファイル単位で言語化する。

## 調査方法 (必須)
- `src/spec_dock/assets/codex_skills/` と `src/spec_dock/assets/spec_dock/` の tree を確認し、provider-side source の主要ファイルを洗い出した。
- `.agents/`、`.codex/`、`.github/`、`spec-dock/` の tree を確認し、repository 上の installed target を inventory 化した。
- `src/spec_dock/cli.py` の managed skill / native shim 同期処理を確認し、source asset と installed target の対応箇所を読んだ。
- `src/spec_dock/assets/codex_skills/host-adapters/meta.json` と `.agents/host-adapters/meta.json` を確認し、manifest が host 別 target をどこまで規定しているかを確認した。
- 先行 discussion とユーザー回答を参照し、今回の research に反映すべき確定方針を整理した。

## 調査結果 (必須)
- 現状の provider-side source は大きく `src/spec_dock/assets/codex_skills/` と `src/spec_dock/assets/spec_dock/` に分かれている。
- installed tree は `./.agents/`、`./.codex/`、`./.github/`、`./spec-dock/` に分かれている。
- `./.agents/skills` は共通 skill の設置先で、workflow skill と host adapter skill の両方がここに置かれている。
- `./.agents/host-adapters/meta.json` は host 別の native shim 配置と委譲先をまとめる manifest になっている。
- `.codex` と `.github` は host-specific native shim の設置先であり、agent entrypoint として機能している。
- `./.github/workflows/ci.yml` は installed tree に存在するが、`src/spec_dock/assets/` 配下には現時点で workflow の source counterpart がない。
- `spec-dock/` については `src/spec_dock/assets/spec_dock/` が比較的素直な source-of-truth になっており、今回の gap は主に `codex_skills` 側で発生している。

### 主な source tree 例

| 区分 | source 側の代表例 | 備考 |
| --- | --- | --- |
| 共通 workflow / planning skill | `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` | `.agents/skills` 配下に入る |
| 共通 domain-specific skill | `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` | initiative / epic / issue / adr 系も同様 |
| host adapter skill | `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md` | GitHub Copilot 用も同じ root にある |
| host adapter manifest | `src/spec_dock/assets/codex_skills/host-adapters/meta.json` | install target と shim 委譲先を持つ |
| native shim | `src/spec_dock/assets/codex_skills/native-shims/spec-dock.toml` | Codex 用 shim |
| native shim | `src/spec_dock/assets/codex_skills/native-shims/spec-dock.agent.md` | GitHub Copilot 用 shim |
| spec-dock 本体 docs | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | `spec-dock/docs/...` に対応 |
| spec-dock runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` | `spec-dock/scripts/spec_dock_runtime/...` に対応 |

### 現状 source → install 対応表

| source 側 | install 後の配置 | 役割 | 現状メモ |
| --- | --- | --- | --- |
| `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` | `.agents/skills/spec-driven-tdd-workflow/SKILL.md` | 共通 workflow skill | 共有資産として扱われている |
| `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` | `.agents/skills/spec-dock-initiative-planning/SKILL.md` | initiative 用 skill | 共有資産として扱われている |
| `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` | `.agents/skills/spec-dock-epic-planning/SKILL.md` | epic 用 skill | 共有資産として扱われている |
| `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` | `.agents/skills/spec-dock-issue-execution/SKILL.md` | issue 用 skill | 共有資産として扱われている |
| `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` | `.agents/skills/spec-dock-adr-facilitation/SKILL.md` | ADR 用 skill | 共有資産として扱われている |
| `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md` | `.agents/skills/spec-dock-codex-adapter/SKILL.md` | Codex 用 adapter skill | 共有 skill と同じ source root に混在している |
| `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md` | `.agents/skills/spec-dock-copilot-adapter/SKILL.md` | Copilot 用 adapter skill | 共有 skill と同じ source root に混在している |
| `src/spec_dock/assets/codex_skills/host-adapters/meta.json` | `.agents/host-adapters/meta.json` | host adapter manifest | installed target の正規化表として機能している |
| `src/spec_dock/assets/codex_skills/native-shims/spec-dock.toml` | `.codex/agents/spec-dock.toml` | Codex native shim | shim 自体は host-specific 配置先へ出力される |
| `src/spec_dock/assets/codex_skills/native-shims/spec-dock.agent.md` | `.github/agents/spec-dock.agent.md` | GitHub Copilot native shim | shim 自体は host-specific 配置先へ出力される |
| source 側に未整備 | `.github/workflows/ci.yml` | GitHub workflow | install target としては存在するが provider-side 正本がない |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` など | `spec-dock/docs/workflow_epic.md` など | workflow 文書 | installed layout を前提に記述されている |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` | `spec-dock/scripts/spec_dock_runtime/` | runtime 実装 | 今回の epic の主対象ではないが、既存の source / install 対応はある |
| `src/spec_dock/assets/spec_dock/templates/` | `spec-dock/templates/` | template 群 | `spec-dock` 側は source / install の形が比較的近い |

### install target 側の代表例

| install target | 主なファイル例 | 意味 |
| --- | --- | --- |
| `.agents/skills/` | `.agents/skills/spec-dock-epic-planning/SKILL.md` | 共通 skill と host adapter skill の設置先 |
| `.agents/host-adapters/` | `.agents/host-adapters/meta.json` | host ごとの canonical entry / native shim 情報 |
| `.codex/agents/` | `.codex/agents/spec-dock.toml` | Codex CLI 向け native shim |
| `.github/agents/` | `.github/agents/spec-dock.agent.md` | GitHub Copilot 向け native shim |
| `.github/workflows/` | `.github/workflows/ci.yml` | GitHub Actions workflow |
| `spec-dock/` | `spec-dock/docs/workflow_epic.md`、`spec-dock/scripts/spec_dock_runtime/...` | spec-dock 自体の docs / runtime / templates |

### 現在の混在点

- `src/spec_dock/assets/codex_skills/` の 1 つの根に、共有 skill、host adapter skill、host adapter manifest、native shim 用 source が同居している。
- `host-adapters/meta.json` は installed target の構造を知っているが、source tree の見た目は install 後レイアウトと一致していない。
- `.github/workflows/ci.yml` は実体としては存在するが、`src/spec_dock/assets/` 配下に同等の source-of-truth がまだない。
- source 側と installed 側でファイルの役割が分離されておらず、`shared / codex-specific / github-specific` の境界が tree から読み取りづらい。
- `src/spec_dock/assets/spec_dock/` は install 先の `spec-dock/` と比較的同型だが、`codex_skills/` だけが provider 都合の束になっており、assets 全体として一貫した原則になっていない。

### installer が持っている間接対応

- `src/spec_dock/cli.py` は `_HOST_ADAPTER_META_ASSET_REL = Path("codex_skills") / "host-adapters" / "meta.json"` を定義し、manifest の位置を code 側で固定している。
- 同じく `src/spec_dock/cli.py` は canonical entry file と canonical target file を定数で持ち、Codex は `.agents/skills/spec-dock-codex-adapter/SKILL.md` と `.codex/agents/spec-dock.toml`、Copilot は `.agents/skills/spec-dock-copilot-adapter/SKILL.md` と `.github/agents/spec-dock.agent.md` を正規 target として扱っている。
- `_apply_managed_skill_install_plan()` では、`assets_dir / "codex_skills" / skill_name / "SKILL.md"` から `.agents/skills/<skill>/SKILL.md` へ同期し、同時に `host-adapters/meta.json` と native shim を個別に `.agents/host-adapters/`、`.codex/agents/`、`.github/agents/` に書き分けている。
- つまり installer は install target をすでに理解しているが、その知識は source tree の構造ではなく `cli.py` の定数と `host-adapters/meta.json` に埋め込まれている。

### 構造上の gap

- source tree が provider-centric で、installed tree が consumer-centric になっており、同型の構造として読めない。
- installer が「install 後の layout をそのまま写す」よりも、「source root から target へ個別変換する」見え方になっている。
- workflow を含む host-specific 資産が source tree に fully represented されていないため、今後の拡張時に契約の抜け漏れが出やすい。
- Claude Code 用の拡張点が tree 上で予約されていないため、後続追加時に再度 layout の再編成が必要になる可能性がある。

### ユーザー回答で確定した方針

- source 側に install 後構造へ対応する仮想 root を新設する。
- `.agents` は共有資産、`.codex` は Codex 固有、`.github` は GitHub 固有として責務を分離する。
- GitHub workflows も `.github` 配下で同じ構造原則にそろえる。
- Claude Code は今回の scope には含めないが、後続で追加しやすい拡張点を残す。
- installer はできるだけ変換を減らし、構造を保ったまま同期する役割に寄せる。

### 次に設計で決める点

- source 側の新しい仮想 root 名と配置をどうするか。
- 共通資産と host-specific 資産を source tree でどう見せるか。特に `.agents/skills` と `.agents/host-adapters` をどの粒度で source 側に表現するか。
- `.github/workflows` を provider-side asset としてどこまで正本化するか。workflow 全面管理にするか、spec-dock 管理対象だけに限定するか。
- installer の例外をどこまで許容し、どこから manifest 化するか。`cli.py` の固定定数を減らして manifest 主導へ寄せるかも含む。
- `src/spec_dock/assets/spec_dock/` と今回新設する install-shaped root の関係をどう切るか。assets 全体の設計原則を統一するか、`spec-dock/` だけ現状維持にするか。
- Claude Code の受け皿を今回の構造にどう接続するか。今回作る root をそのまま拡張スロットにできるか。

## 結論 (必須)
- 現状の source tree は、install 後の tree をそのまま表す形にはなっていない。
- ただし installer はすでに `.agents` / `.codex` / `.github` の target を理解しており、完全な再設計が必要というより、source 側の asset 構造を install-shaped に寄せる整理が必要な状態である。
- `src/spec_dock/assets/spec_dock/` は比較的 install-shaped で管理できているため、今回の主戦場は `codex_skills` 側の再編である。
- epic-00067 では、shared / Codex-specific / GitHub-specific を分離した install-shaped source root を前提に、installer は最小変換で同期する方針が妥当である。

## リスク/制約 (任意)
- 既存の asset 置き場を移す場合、installer と tests の両方を同時に更新しないと drift が発生しやすい。
- `cli.py` に埋め込まれている canonical path 定数と `host-adapters/meta.json` の両方を更新対象として扱わないと、source tree だけ整っても install 契約が分裂する。
- GitHub workflows を source asset として正本化する場合、既存の workflow 管理方法との重複を避ける必要がある。
- 新しい root 名を決める前に requirement / design に入ると、後で path だけ再議論になる可能性がある。
- Claude Code は今回 scope 外のため、将来の受け皿を見越しつつも、今回の設計で過剰に一般化しすぎると判断がぼやける。

## 参考（References） (任意)
- [discussion: asset source structure vs installed layout mapping and gaps](./20260412t085037z-disc-asset-source-structure-vs-installed-layout-mapping-and-gaps.md)
- `src/spec_dock/cli.py`
- `src/spec_dock/assets/codex_skills/host-adapters/meta.json`
- `src/spec_dock/assets/codex_skills/native-shims/spec-dock.toml`
- `src/spec_dock/assets/codex_skills/native-shims/spec-dock.agent.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- `./.agents/host-adapters/meta.json`
- `./.codex/agents/spec-dock.toml`
- `./.github/agents/spec-dock.agent.md`
- `./.github/workflows/ci.yml`
