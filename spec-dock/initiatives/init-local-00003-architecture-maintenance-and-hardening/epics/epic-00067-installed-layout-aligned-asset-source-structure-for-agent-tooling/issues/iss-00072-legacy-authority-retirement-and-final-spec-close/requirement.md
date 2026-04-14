---
種別: 要件定義書（Issue）
ID: "iss-00072"
タイトル: "Legacy authority retirement and final spec close"
関連GitHub: ["#72"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-14"
親: ["epic-00067", "init-local-00003"]
---

# iss-00072 Legacy authority retirement and final spec close — 要件定義（WHAT / WHY）

## 目的
- `install_root` への authority 一本化を最終確定し、`codex_skills` を agent-tooling authority として参照する code/tests/assets/current docs を retire したうえで、legacy tree 自体も安全に repo から削除する。
- `E-RQ-006`、`E-RQ-008`、`E-AC-004`、`E-AC-005`、`E-AC-007` を閉じ、epic-00067 を final spec close 可能な状態にする。

## 背景・現状
- 現状の挙動:
  - issue-70 までで installer/runtime authority は `install_root` へ切替済みであり、production code の current execution path は `codex_skills` を authority として参照しない。
  - 一方で legacy `codex_skills` 実体とその参照は source tree / tests / current docs に残っており、「historical artifact を残す設計」が current repo cleanup の完了条件を曖昧にしている。
  - issue-71 で verification は閉じるが、authority retirement 自体の cleanup owner はまだ残る。
- 現状の課題:
  - legacy root 実体や `codex_skills` authority 文脈が code/tests/current docs に残ると、install_root が唯一の authority であるという final claim と矛盾する。
  - user 方針として後方互換は不要であり、historical artifact を repo に残し続ける合理性が失われている。
  - future host extension point を示したい一方で、旧 authority を温存すると tree の読みやすさと境界が再び曖昧になる。
  - historical spec records まで一括書換えを始めると scope が膨らみ、closeout tranche が終わらない。
  - 実 repo では特に `tests/test_init_update.py` の parity / duplicate assumptions と `AGENTS.md` の provider-side directory map に legacy authority 前提が残っている。
- 再現手順:
  1. code/tests/assets/current docs で `codex_skills` 参照を検索する。
  2. `install_root` authority と矛盾する current docs / metadata / tests が残っていないか確認する。
- 観測点:
  - Code:
    - `src/spec_dock/cli.py`
  - Assets:
    - `src/spec_dock/assets/install_root/`
    - `src/spec_dock/assets/codex_skills/`
    - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - Tests:
    - `tests/test_init_update.py`
    - relevant CLI/runtime tests（scoped search で current authority assertion hit がある場合のみ）
  - Current docs/spec:
    - epic-00067 docs
    - issue-68/69/70/71/72 current docs
    - `AGENTS.md`
    - `src/spec_dock/assets/spec_dock/docs/**`
    - `src/spec_dock/assets/spec_dock/system/**`
    - `spec-dock/docs/**`
    - `spec-dock/system/**`
- 情報源:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - checked-in `.agents/host-adapters/meta.json`
  - epic-00067 docs
  - issue-71 docs

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - maintainer
  - reviewer
  - future host extension を行う contributor
- 代表シナリオ:
  - maintainer が source tree / tests / docs を見たとき、agent-tooling authority が `install_root` に一本化されていることを迷わず理解できる。
  - reviewer が final spec close で「どこが current authority で、どこが historical record なのか」を明確に説明できる。

## スコープ
- MUST:
  - `codex_skills` authority を current code/tests/current docs から retire する。
  - `src/spec_dock/assets/codex_skills/` を repo から削除する。
  - assets については `install_root` authoritative manifest を review し、current metadata source が `codex_skills` に戻っていないことを確認する。
  - 削除前に、current code / package install contract / tests / current docs が `codex_skills` physical tree を current dependency として持っていないことを確認する。
  - `install_root` が唯一の current authority であることを current docs と tests で確認できるようにする。
  - future host extension point を sibling-root model として final review で確認する。
  - final spec review / closeout evidence を issue-72 report に集約する。
  - issue-72 で変更した provider-side docs / repo guidance / mirror-affecting docs については、`spec-dock update` 後の dogfooding mirror 収束を fresh evidence として残す。
- MUST NOT:
  - historical closed records まで全面書換えしない。
  - Claude Code 実装を追加しない。
  - issue-71 で閉じた verification owner を吸収し直さない。
- OUT OF SCOPE:
  - historical issue/report/discussion の記述統一
  - new host implementation
  - workflow 個別機能の拡張
  - `src/spec_dock/cli.py` の authority model 自体の再設計

## 境界
- Always:
  - authority retirement 対象は current code / tests / assets / current docs に限定する。
  - current docs corpus は次に固定する。
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/{requirement.md,design.md,plan.md}`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/report.md`
    - 同 epic 配下の issues `iss-00068` から `iss-00072` の `requirement.md` / `design.md` / `report.md`
    - `AGENTS.md`
    - `src/spec_dock/assets/spec_dock/docs/**`
    - `src/spec_dock/assets/spec_dock/system/**`
    - `spec-dock/docs/**`
    - `spec-dock/system/**`
  - provider-side docs (`src/spec_dock/assets/spec_dock/docs/**`, `src/spec_dock/assets/spec_dock/system/**`) が current source-of-truth であり、dogfooding 側 (`spec-dock/docs/**`, `spec-dock/system/**`) は consumer mirror / verification surface として扱う。
  - provider-side と dogfooding 側に差分がある場合、pass 条件は dogfooding 側が `spec-dock update` 後に provider-side source-of-truth へ収束することであり、差分を competing authority とはみなさない。
  - historical records は historical fact として残してよいが、current authority と誤読されないよう current docs からは切り離す。
  - final close は `install_root` uniqueness と future host extension point の両方を確認して閉じる。
  - `codex_skills` retirement verification は current surface に限定した search contract で判定する。
    - must inspect:
    - `src/spec_dock/cli.py`
    - `src/spec_dock/assets/install_root/**`
    - `tests/**`
    - `AGENTS.md`
    - current docs corpus
    - allowed residual matches:
      - historical closed issue/report/discussion
      - current docs の historical boundary / deleted legacy tree と明示された説明
    - forbidden residual matches:
      - current code/tests/current docs が `codex_skills` を source-of-truth、runtime authority、current metadata source、expected bundled path として扱う記述
      - current assets が `codex_skills` を current metadata source として要求する記述
- Ask:
  - historical record を修正しないと current reader が誤読する場合のみ、例外的に current scope へ昇格する。
- Never:
  - legacy authority retirement を physical file deletion だけで済ませない。
  - current docs に `codex_skills` authority 文脈を残したまま close しない。
  - future host 拡張余地を曖昧にしたまま `E-RQ-008` を close しない。

## 非交渉制約
- `install_root` が唯一の current authority であることを code/tests/current docs/report evidence の 4 面で説明できなければならない。
- `codex_skills` は current repo に物理残置しない。残るのは historical records 上の言及だけとする。
  - retirement 対象は少なくとも次の 4 面を含む。
  - code:
    - installer source discovery / metadata authority references
  - tests:
    - current authority assertions / expected bundled asset paths / authority assumptions
  - assets:
    - provider-side authoritative manifest review と legacy artifact classification
  - current docs:
    - epic-00067 と current issue docs、および repo-facing current guidance
- authority retirement review は provider-side authoritative manifest として `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を必ず含める。
- issue-72 の authority retirement 実装では、production code の authority rewrite よりも `tests/test_init_update.py`、`AGENTS.md`、current closeout docs の residual authority assumptions 除去を主対象として扱う。
- tests corpus のうち、過去 issue の historical regression coverage や cutover evidence を説明する参照は、それ自体を current authority assertion や expected current file inventory にしていない限り許容する。
- issue-72 で禁止するのは、tests が `codex_skills` physical tree の存在や current authority source/path を期待する assertion である。
- relevant CLI/runtime tests は scoped search で current authority assertion hit がある場合にのみ update / targeted validation の対象とし、hit が無い場合は `該当なし` を report に記録する。
- historical closed issue/report/discussion は final close の必須 cleanup 対象にしない。ただし current reader が誤読する導線になる場合は current docs で明示的に上書きする。
  - future host extension point は「`.agents` shared + sibling host roots」という current model で説明されなければならない。
  - final spec close は issue-71 final verification が pass していることを前提にする。
  - epic close target と issue-72 evidence の対応は次に固定する。
    - `E-RQ-006`:
      - issue-72 report `authority-uniqueness`
    - `E-AC-007`:
      - issue-72 report `authority-uniqueness`
      - issue-72 report から辿れる issue-71 verification refs
    - `E-RQ-008`:
      - issue-72 report `future-host-extension`
    - `E-AC-004`:
      - issue-72 report `historical-boundary`
      - issue-72 report `upstream-prerequisites`
    - `E-AC-005`:
      - issue-72 report `final-close-gate`

## 前提
- issue-71 が final verification を pass している。
- issue-70 までで installer/runtime authority は install_root へ切替済みである。
- repo current docs と tests を closeout tranche で更新できる。

## 受け入れ条件
- AC-001:
  - Actor:
    - reviewer
  - Given:
    - current code / tests / assets / current docs を inspect する
  - When:
    - authority surface を review する
  - Then:
    - `install_root` が唯一の current authority と説明できる
    - `codex_skills` を current authority として参照する current surface が残っていない
    - `src/spec_dock/assets/codex_skills/` が削除されている
    - issue-72 で変更した provider-side docs / mirror-affecting surfaces について、`spec-dock update` 後の dogfooding mirror 収束が fresh evidence で確認できる
    - issue-71 parity evidence は issue-72 で未変更の surface に対する補助参照としてのみ使われる
  - 観測点:
    - source search
    - provider-side authoritative manifest review
    - current docs review
    - tests/path assertions
    - issue-71 parity evidence

- AC-002:
  - Actor:
    - maintainer
  - Given:
    - issue-71 final verification が green である
  - When:
    - final closeout review を行う
  - Then:
    - `E-RQ-006` / `E-AC-007` を閉じる evidence が issue-72 report に集約される
    - `install_root` uniqueness claim と legacy retirement evidence を同じ report から辿れる
  - 観測点:
    - issue-71 report
    - issue-72 report

- AC-003:
  - Actor:
    - reviewer
  - Given:
    - current docs と epic/issue specs を確認する
  - When:
    - future host extension point を review する
  - Then:
    - `E-RQ-008` を閉じる evidence が issue-72 report から辿れる
    - Claude Code は未実装のまま out-of-scope と明記されている
    - それでも `.agents` shared + sibling host root 追加という拡張モデルが current docs で説明されている
    - future host extension point は legacy authority を復活させる理由として扱われていない
  - 観測点:
    - epic-00067 docs
    - issue-72 docs
    - issue-72 report

- AC-004:
  - Actor:
    - maintainer
  - Given:
    - current tests / docs / metadata の cleanup が完了している
  - When:
    - final spec review を行う
  - Then:
    - `E-AC-004` / `E-AC-005` を閉じる evidence が issue-72 report から辿れる
    - epic-00067 `requirement.md` / `design.md` / `plan.md` / `report.md` と、issue-68 から issue-72 の `requirement.md` / `design.md` / `report.md` に限定した evidence chain に矛盾がない
    - authority uniqueness、historical boundary、future host extension point、issue-71 verification prerequisite、dogfooding mirror convergence の 5 項目が issue-72 report から確認できる
    - epic current report は placeholder ではなく evidence-bearing content を持ち、issue-72 report からその section を参照できる
  - 観測点:
    - epic docs
    - issue docs/reports
    - issue-72 report

## 例外・エッジケース
- EC-001:
  - 条件:
    - historical records 内に `codex_skills` 文言が残る
  - 期待:
    - current code/tests/docs はそれを authority として参照しない
    - current docs に authority は `install_root` と明記される
    - physical tree 不在でも historical discussion/report の説明整合は壊れない
  - 観測点:
    - source search
    - current docs review

- EC-002:
  - 条件:
    - historical spec record 内に `codex_skills` 文言が残る
  - 期待:
    - historical record rewrite は必須にしない
    - current docs と final report で current authority を明確に上書きできる
  - 観測点:
    - current docs
    - final report

## 用語（ドメイン語彙）
- TERM-001:
  - current authority:
    - maintainer / reviewer が現在の source-of-truth として参照すべき code/tests/assets/docs の面。
- TERM-002:
  - historical artifact:
    - 現在の authority ではないが、履歴や移行文脈のために repo に残っていてよい artifact。

## 未確定事項
- なし:
  - historical record 全面書換えをしない方針、current authority retirement の対象面、future host extension point の説明責務をこの issue で固定する。
