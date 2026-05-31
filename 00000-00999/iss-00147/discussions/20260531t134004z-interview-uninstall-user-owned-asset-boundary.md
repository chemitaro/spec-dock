---
種別: interview
ID: "20260531t134004z-interview"
タイトル: "Uninstall user owned asset boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00147"
created_at: "2026-05-31THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t134004z-interview Uninstall user owned asset boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - uninstall が消す managed assets と残す user-owned / bootstrap-only files の境界が変わる。
  - `design.md`:
    - manifest inventory、content match / ownership 判定、dry-run 表示、manual cleanup guidance が変わる。
  - `plan.md`:
    - test obligation と edge case が変わる。
  - `ADR`:
    - 現時点では不要。user-owned config の所有権を installer 全体で再定義する場合のみ候補にする。
- chat 上の軽微な一問では足りない理由:
  - `.codex/config.toml` などは開発用 agent を動かす入口であり uninstall の目的に近い一方、既存 installer では bootstrap-only として user edit を尊重しているため、誤削除すると user-owned repo config を失う可能性がある。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - uninstall が bootstrap-only / user-owned になり得る files を自動削除するか、標準では残して案内に留めるかを確定する。
- 回答が後続判断へ与える影響:
  - managed asset removal の安全境界、dry-run plan の分類、confirmation wording、tests が変わる。

## 質問 (必須)
- 質問:
  - uninstall は、`.codex/config.toml` のように spec-dock が初回作成するが user edit が入り得る bootstrap-only / user-owned files を、自動削除対象に含めますか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があれば「自動削除する条件」と「残して案内する条件」を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260531t133315z-interview-uninstall-command-scope.md`: repo-local uninstall が user-approved。
  - `20260531t133616z-interview-uninstall-removal-boundary.md`: specs の扱いは explicit mode selection が user-approved。
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`: `managed_assets.bootstrap_only_exact_file_paths` に `.codex/config.toml` が定義されている。
  - `src/spec_dock/cli.py`: bootstrap-only target は update 時に既存 file があると copy を skip し、user edit を上書きしない。
  - `src/spec_dock/assets/install_root/`: `.agents/skills/**`, `.codex/agents/**`, `.github/agents/**`, `.codex/prompts/**`, `.codex/rules/**`, `.github/workflows/ci.yml` などが current install_root asset として存在する。
- local context で解決できたこと:
  - current managed files と bootstrap-only files は installer metadata で区別されている。
  - uninstall の primary objective は agent / skill noise の除去だが、bootstrap-only files は user edit を含む可能性がある。
- まだ人間判断が必要な理由:
  - product repo から開発用 agent 起動設定を確実に取り除くことと、user-owned config を保護することの優先順位は product policy で決める必要がある。

## 回答案 (必須)
- Option A:
  - preserve bootstrap-only by default: `.codex/config.toml` など bootstrap-only / user-owned files は自動削除しない。dry-run に「manual review / optional cleanup」として表示する。
- Option B:
  - remove if content matches shipped asset: bootstrap-only files でも、現在の shipped asset と content が一致する場合だけ自動削除し、差分がある場合は残す。
- Option C:
  - explicit flag required: bootstrap-only / user-owned files の削除は `--remove-user-owned` のような追加明示 flag がある場合だけ行い、通常 uninstall では残す。

## Codex の分析 (必須)
- 判断軸:
  - agent noise removal の完全性、user edit 保護、実装の判定可能性、dry-run の分かりやすさ、再install時の復元性。
- tradeoff:
  - Option A は user data loss を避けやすいが、`.codex/config.toml` に SpecDock orchestrator 設定が残ると noise removal が不完全になる可能性がある。
  - Option B は content match で安全に消せる範囲を広げるが、version drift や過去 asset との比較が難しい場合がある。
  - Option C はもっとも明示的だが、flag が増えて UX は重くなる。
- リスク:
  - bootstrap-only file を無条件削除すると、ユーザーが追加した project config を失う。
  - 残しすぎると、SpecDock uninstall 後も agent 起動設定が残り、今回の目的である noise removal が達成されない。
- 具体シナリオ / edge case:
  - `.codex/config.toml` が install 直後のままなら削除してよい repo。
  - `.codex/config.toml` に product 固有の Codex 設定が追記されており、SpecDock 部分だけ取り除きたい repo。
  - `.github/workflows/ci.yml` が SpecDock 由来だが product CI として使われ始めている repo。

## Codex の推奨案 (必須)
- 推奨:
  - Option B を基本にし、content mismatch は削除せず dry-run / report で manual review に回す。
- 理由:
  - shipped asset と完全一致する bootstrap-only file は user edit がないと判断しやすく、noise removal の目的にも合う。
  - 差分がある file を残せば user-owned config の誤削除を避けられる。
- 未回答時の影響:
  - requirement の deletion boundary と edge case を固定できず、design / plan に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
  - `.codex/config.toml` のような bootstrap-only / user-owned になり得る files は、shipped asset と内容が完全一致する場合だけ自動削除する。
  - 内容に差分がある場合は user edit が入っている可能性があるため削除せず、dry-run / report で残存理由と manual review 対象として示す。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - uninstall command surface を installer CLI に置くか、repo-local runtime command に置くか、または両方に置くか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、bootstrap-only / user-owned になり得る files の削除境界は content match based removal として確定した。
  - shipped asset と一致する file は user edit がないと判断しやすく、agent / skill noise removal の目的に合う。
  - content mismatch file は user-owned config を含む可能性があるため、自動削除せず manual review に回す。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - bootstrap-only / user-owned になり得る files は、shipped asset と content match する場合だけ自動削除する。
  - content mismatch の files は削除せず、dry-run / execution result に manual review 対象として表示する。
  - agent / skill noise removal と user edit protection の両立を非交渉制約に含める。
- `design.md`:
  - uninstall inventory は current managed file、obsolete managed file、bootstrap-only file を分類し、bootstrap-only file は content comparison で削除可否を判定する。
  - content mismatch は preserve + report にする。
- `plan.md`:
  - shipped asset match の bootstrap-only file removal、content mismatch preservation、dry-run reporting を test obligation に含める。
- `ADR`:
  - 現時点では不要。
- reflected_to 更新方針:
  - requirement authoring 時に `requirement.md` と `report.md` の Evidence Adoption Ledger / Spec Authoring Gate へ反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
