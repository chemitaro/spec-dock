---
種別: 要件定義書（Epic）
ID: "epic-00054"
タイトル: "GitHub lifecycle command expansion"
関連GitHub: ["#54"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-05-15"
親: ["init-local-00002"]
---

# epic-00054 GitHub lifecycle command expansion — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00002` の feature expansion として、SpecDock の GitHub lifecycle 操作を create だけでなく close まで command 側へ広げる。
  - dogfooding 中に顕在化した「作成は CLI だが close は GitHub Web UI へ戻る」「local tree cleanup は手作業 directory 削除に頼る」という gap を、運用可能な feature backlog として固定する。
  - 追加の command lifecycle gap として、導入済み workspace の managed assets 更新を repo-local runtime command から実行できるようにし、長い `uvx --from ... spec-dock update` 手順への依存を減らす。
- この epic が提供する能力:
  - linked GitHub issue を command 側から close できる。
  - local spec node（issue / epic / initiative）を directory ごと削除できる。
  - destructive な local delete と、より安全な remote close を分離した lifecycle contract を提供する。
  - repo-local runtime command から upstream package 経由の self-update を実行できる。
  - review-only issue を分離せず、各 implementation issue の中で review と成功性確認を完結させる。

## ユースケース
- happy path:
  - maintainer が SpecDock から issue を完了させる際、GitHub Web UI を開かずに linked GitHub issue を close できる。
  - maintainer が不要になった issue / epic / initiative を local workspace から削除する際、対象 directory を command 経由で安全に除去できる。
  - issue / epic / initiative の local delete では、remote 側は delete ではなく close に留めることで、GitHub 履歴と事故防止のバランスを保てる。
  - maintainer が managed repo 内で `./spec-dock/scripts/spec-dock update` を実行し、upstream GitHub package から shipped docs / scripts / skills を更新できる。
- exception / operation scenario:
  - active target や dependency を持つ node を delete しようとした場合は、事前確認または fail-fast で誤操作を防ぐ。
  - linked GitHub issue を持たない local-only cleanup は local delete だけで完結する。
  - GitHub close が権限不足や `gh` 状態不備で失敗した場合、local delete との整合を崩さない安全境界が必要になる。

## Epic requirements
- E-RQ-001:
  - SpecDock は linked GitHub issue に対して command-side close 操作を提供し、maintainer が GitHub Web UI を介さず lifecycle を完結できること。
- E-RQ-002:
  - SpecDock は local spec node（issue / epic / initiative）を directory ごと削除する command-side delete 操作を提供できること。
- E-RQ-003:
  - local delete と remote close は意図的に別能力として設計され、remote handling の success path は close-only であること。
- E-RQ-004:
  - delete 操作は destructive operation として扱い、対象確認、dependency / active pointer / subtree 影響の確認、誤操作防止の guardrail を持つこと。
- E-RQ-005:
  - epic / initiative delete は subtree を伴う管理操作として扱い、対象 node だけでなく配下 node の local directory と linked GitHub issue closure 方針を一貫して扱えること。
- E-RQ-006:
  - GitHub-side issue delete はこの epic の対象外とし、docs / design / plan / acceptance criteria の success path に含めないこと。
- E-RQ-007:
  - epic の execution は close command、local delete command、self-update command の各 issue scope に分け、各 issue がそれぞれの scope に対する docs / tests / review / success verification を内包すること。
- E-RQ-008:
  - epic 全体の final review / final validation / close-out evidence は、最後に完了する issue が保持すること。固定の第2 issue に閉じず、issue 追加時も close-out owner を明示して扱えること。
- E-RQ-009:
  - SpecDock は repo-local runtime command から installer `spec-dock update [path]` を呼び出す self-update 操作を提供し、maintainer が long-form `uvx` invocation を覚えなくても managed assets を更新できること。
- E-RQ-010:
  - self-update 操作は uvx cache による stale package 混入を避けるため、upstream GitHub package を `uvx --no-cache` で実行すること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - linked GitHub issue を持つ node がある
  - When:
    - maintainer が close command を実行する
  - Then:
    - linked GitHub issue が command 側から close される
    - local spec tree は不必要に削除されない
    - docs / tests / CLI help が remote close-only contract と一致する
  - 観測点:
    - runtime / CLI tests
    - docs contract
- E-AC-002:
  - Given:
    - local issue node が存在する
  - When:
    - maintainer が delete command を明示的に実行する
  - Then:
    - issue directory が local workspace から削除される
    - linked GitHub issue が存在する場合、remote 側の扱いは delete ではなく close である
    - destructive guardrail が docs / tests / CLI guidance に明記されている
  - 観測点:
    - runtime / CLI tests
    - filesystem assertions
    - docs contract
- E-AC-003:
  - Given:
    - epic または initiative 配下に child node が存在する
  - When:
    - maintainer が parent node delete を実行する
  - Then:
    - local subtree の扱いが一貫しており、対象 scope と child scope の削除境界が明文化される
    - active pointer / dependency / subtree impact に対する安全装置がある
    - linked GitHub issue 群の remote handling は close-only であり、delete は実行されない
  - 観測点:
    - design / docs
    - runtime / CLI tests
- E-AC-004:
  - Given:
    - provider docs / dogfooding docs / tests / runtime を確認する
  - When:
    - epic の contract を参照する
  - Then:
    - close と local delete の境界、destructive guardrail、GitHub-side delete exclusion が一貫している
    - review-only issue を立てず、各 issue 自身が review と acceptance evidence を持ち、最終 close-out owner が最後に完了する issue として明示されている
  - 観測点:
    - docs parity
    - final spec review
- E-AC-005:
  - Given:
    - `spec-dock/` workspace を持つ managed repo がある
  - When:
    - maintainer が repo-local runtime command から update を実行する
  - Then:
    - upstream GitHub package の installer `spec-dock update [path]` が no-cache uvx 経由で実行される
    - target path は省略時 current workspace、明示時 explicit target として扱われる
    - uvx / network / permission / installer failure は隠蔽されず、operator が追える CLI evidence と exit status で返る
  - 観測点:
    - runtime / CLI tests
    - subprocess args assertion
    - docs contract

## スコープ
- MUST:
  - command-side GitHub issue close
  - local issue / epic / initiative delete
  - repo-local runtime self-update command
  - destructive guardrail、confirmation、docs/tests 整備
  - dogfooding での lifecycle completeness gap を埋めること
  - close / delete / self-update の各 issue scope で進め、各 issue に review と成功性確認を内包すること
- MUST NOT:
  - remote GitHub issue delete を success path に含めない
  - destructive local delete を silent / implicit に実行しない
  - self-update で uvx cache を標準経路として使わない
  - review / validation だけを目的とする standalone issue を作らない
- OUT OF SCOPE:
  - GitHub-side issue delete
  - GitHub issue 以外の remote artifact 削除
  - project-wide garbage collection の自動化
  - package update availability check / version comparison
  - legacy workspace の自動 migration

## 境界
- Always:
  - remote handling は close-only とし、GitHub 履歴保全と事故防止を優先する
  - local delete は directory removal を伴う destructive operation として扱う
  - self-update は upstream GitHub package を `uvx --no-cache` で呼び出し、cache stale による誤更新を避ける
  - issue / epic / initiative の各階層差を docs / command contract で明示する
- Ask:
  - active target や dependency を含む node を delete する前に、どの guardrail を必須にするか。
  - parent scope delete の際に subtree を一括対象とするか、明示フラグを要求するか。
- Never:
  - GitHub-side issue delete を convenience path として入れること
  - confirmation なしに destructive subtree delete を走らせること

## 非機能要件
- performance:
  - delete / close 操作追加のために通常の `sync` / `validate` / `active` の応答性を悪化させない
- reliability / consistency:
  - local tree と linked GitHub issue state の整合境界が docs / runtime / tests で一致すること
- security:
  - remote delete を持ち込まず、close-only と destructive guardrail によって誤操作リスクを抑えること
- operations:
  - maintainer が日常 dogfooding で create から close、必要時の local delete まで command 側で処理できること

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `tests/`
  - `spec-dock/`
- external dependency:
  - GitHub CLI / auth / permission
  - uvx / upstream GitHub package fetch
- compatibility:
  - additive change を基本とし、既存 create / import / sync / validate contract を壊さない

## 未確定事項
- Q-001:
  - 質問:
    - parent scope（epic / initiative）delete を default recursive にするか、明示的 recursive opt-in にするか。
  - 選択肢:
    - A:
      - default recursive
    - B:
      - explicit recursive opt-in
  - 推奨案:
    - B。destructive scope が大きいため、parent delete は明示 opt-in の方が安全である。
  - 影響範囲:
    - command UX
    - tests
    - docs safety wording
