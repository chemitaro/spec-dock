---
種別: 計画書（Initiative）
ID: "init-local-00002"
タイトル: "Prototype Feature Expansion"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-07-28"
依存: ["requirement.md", "design.md"]
---

# init-local-00002 Prototype Feature Expansion — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - architecture maintenance と切り分けたうえで、prototype の機能価値を段階的に広げる。
- 対象 metric:
  - requirement の Metric-001 / Metric-002

## マイルストーン
- M1:
  - deliverable:
    - feature expansion の portfolio が architecture maintenance から分離されている
  - exit:
    - epic が value-based に整理され、dependency が明示されている
- M2:
  - deliverable:
    - core workflow completeness の feature epic が起動できる
  - exit:
    - 最初の feature epic の issue 分解方針がある
- M3:
  - deliverable:
    - operator / collaboration 方面の feature epic が優先順つきで見えている
  - exit:
    - blocker / enabler / later extension が整理されている

## Epic ポートフォリオ
- epic-0001-core-workflow-completeness:
  - 目的:
    - prototype として不足している主要 workflow を埋め、できること自体を増やす。
  - deliverable:
    - core feature gaps の整理と追加
  - metric link:
    - Metric-002
  - depends on:
    - `init-local-00003` の blocker が閉じていること
- epic-00054-github-lifecycle-command-expansion:
  - 目的:
    - GitHub / lifecycle の feature value を広げ、dogfooding で不足が見えた command-side lifecycle completeness を補う。
  - deliverable:
    - SpecDock から linked GitHub issue を close できる command と、local spec node を directory ごと削除できる安全な delete contract の定義、および 2 issue で完結する実装計画
  - metric link:
    - Metric-002
  - depends on:
    - epic-0001-core-workflow-completeness
  - 背景:
    - 現在の dogfooding では issue 作成は command 側で完結する一方、issue close は GitHub Web UI に戻る必要があり、lifecycle が途中で分断されている。
    - さらに local tree の整理も手作業で directory 削除に頼っており、issue / epic / initiative の local cleanup を command 化する operator value がある。
    - ただし GitHub-side delete は事故リスクが高いため、この epic では remote handling を close-only とし、remote delete は success path に含めない。
  - 実行方針:
    - 2 issue 構成で進める。
    - 第1 issue で close command を実装し、その issue 自身の docs/tests/review/success verification まで閉じる。
    - 第2 issue で local delete を実装し、その issue 自身の docs/tests/review/success verification に加えて epic 全体の final review / final validation まで閉じる。
- epic-00074-multi-host-agent-and-config-asset-expansion:
  - 目的:
    - Codex main agent bootstrap config と host-native orchestrator/specialist assets、GitHub Copilot の host-native orchestrator/specialist assets を installer 管理下で追加し、Harness Engineering のような multi-host 運用に耐える feature value を広げる。
  - deliverable:
    - Codex bootstrap `config.toml`
    - Codex subagents/custom agents
    - GitHub Copilot `orchestrator` primary agent
    - GitHub Copilot subagents/custom agents
    - future host / future pack を見据えた extensible managed asset model
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - `epic-00048` completed baseline
    - `init-local-00003` の prerequisite groundwork（特に `epic-00067`）
  - 背景:
    - `epic-00048` で thin adapter / native shim baseline は整ったが、Codex main agent の orchestrator responsibility、`spec-manager` への rename、GitHub Copilot `orchestrator` primary agent を含む複数 subagent/custom agent を managed deployment する contract は未整備である。
    - `epic-00067` で install_root authority と sync/prune safety は固定済みのため、本 initiative では architecture cleanup を再実施せず、その上に feature value を追加する。
    - Harness Engineering の中核利用では、install 後に host config や subagent を手作業で足さずに済むことが重要であり、managed asset model の拡張が直接の利用価値になる。
  - 実行方針:
    - 既存 installer foundation 上の asset 追加として 1 implementation issue で進める。
    - 同一 issue の中で metadata / file placement / tests / docs / cross-host validation を完了させる。
    - 新しい installer mechanism が必要と判明した場合だけ再分割する。
- epic-00107-worktree-provisioning:
  - 目的:
    - SpecDock runtime command から、並行開発用の linked worktree と initial branch を安全に作成できる operator capability を追加する。
  - deliverable:
    - `spec-dock worktree create [LABEL]` command
    - `<repo-basename>-worktrees/` sibling container placement
    - label / id / directory / branch naming contract
    - optional / non-fatal `make init` bootstrap
    - Git failure / collision / linked-worktree invocation handling
    - provider docs / dogfooding parity / tests
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - current runtime command baseline
    - `epic-00054` の lifecycle command expansion と command UX が競合しないこと
  - 背景:
    - `epic-00054` は GitHub issue close / local node delete / self-update の lifecycle gap を扱う。
    - `epic-00107` は別の operator capability として、複数 issue / 複数変更を branch / checkout 単位で分離して前進できる worktree 作成導線を扱う。
    - 既存 `taikyohiyou_project` で実用している `make worktree` の naming UX を参考にしつつ、SpecDock runtime の layered architecture へ取り込む。
  - 実行方針:
    - requirement / design / plan の spec authoring gate を通してから issue 分割する。
    - command core、bootstrap/output/docs parity、dogfooding verification の順で閉じる。
- epic-00343-workbench-shell-and-explicit-file-artifact-import:
  - 目的:
    - fresh root / future Initiative・Epic・IssueにoptionalなWorkbench shellを自動配置し、明示したsingle fileをrootまたはnodeのArtifactへ安全にimportできるoperator-facing capabilityを追加する。
  - deliverable:
    - Git追跡可能なshell markerと内容をignoreするWorkbench contract、repository内外の明示single-file import、既存`workbench copy`のmanual helper互換。
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - current runtime baseline
    - `init-local-00003`のarchitecture guardrailに抵触しないこと
  - 状態:
    - designはpass済み、canonical planはfresh review中。人間承認前のためIssue nodeは未作成である。
- epic-0003-operator-value-expansion:
  - 目的:
    - operator が日常運用で得られる feature value を広げる。
  - deliverable:
    - operator-facing convenience / coverage の追加
  - metric link:
    - Metric-001
  - depends on:
    - epic-0001-core-workflow-completeness
- epic-0004-post-prototype-feature-candidates:
  - 目的:
    - prototype release 後でもよい feature extension を切り分ける。
  - deliverable:
    - later expansion backlog の整理
  - metric link:
    - Metric-001
  - depends on:
    - epic-0002-collaboration-and-lifecycle-expansion
    - epic-0003-operator-value-expansion

## 順序と理由
- sequencing rationale:
  - まず core workflow completeness を優先する。
  - そのうえで collaboration/lifecycle と operator value を拡張する。
  - `epic-00054` はその最初の具体化であり、create 後に Web UI へ戻っている lifecycle gap と、手作業 directory cleanup を command contract へ戻す役割を持つ。
  - `epic-00054` は review-only issue を別建てせず、各 implementation issue に review と成功性確認を内包する。
  - `epic-00074` は `epic-00048` の completed baseline を拡張し、host-native config / subagent managed deployment を concrete feature epic として進める。
  - `epic-00074` は `epic-00067` の authority cleanup を再所有せず、feature initiative 側では利用価値としての multi-host setup 拡張に限定する。
  - `epic-00107` は `epic-00054` と同じく runtime command を拡張するが、close/delete/update の lifecycle completion ではなく、並行開発用 worktree provisioning を扱うため独立 epic とする。
  - `epic-00343` は既存root/nodeをbackfillせず、fresh Workbench shellとexplicit single-file Artifact importを追加する独立のfeature epicとして、このportfolioへ登録する。`epic-00107`のlinked worktree provisioningとはmanual `workbench copy`互換だけを共有し、実装順序のhard dependencyは置かない。
  - `epic-00343`はdesign / planのfresh reviewと人間承認を通過するまでIssueを作成せず、既存Epicの着手順を再構成しない。
  - post-prototype 候補は current initiative の出口を曖昧にしないよう最後に整理する。
- parallelizable:
  - `epic-00054` と epic-0003 は並行検討できる。
  - `epic-00074` は prerequisite groundwork が閉じている前提で `epic-00054` と並行検討できるが、installer / docs / dogfooding の重なりは調整が必要。
  - `epic-00107` は `epic-00054` と command parser / docs / tests の変更面が重なるため、実装 issue の同時編集は避ける。ただし spec planning は並行可能である。

## 意思決定ゲート
- G1 strategy review:
  - feature initiative が architecture maintenance を抱え込んでいないか確認する
- G2 milestone readiness:
  - 最初に足す feature が prototype value に直結しているか確認する
- G3 governance/docs impact:
  - architecture initiative 側の guardrail を破っていないか確認する
  - `epic-00074` が architecture cleanup ではなく feature expansion として閉じているか確認する
  - `epic-00107` が Codex-managed worktree を再実装せず、manual long-lived worktree provisioning に限定されているか確認する
- G9 final initiative plan review:
  - current initiative と post-prototype candidate の境界を確認する

## 指標レビュー計画
- review timing:
  - epic 起動時
  - feature priority 見直し時
- dashboard / source:
  - initiative docs
  - architecture initiative docs

## ロールアウト計画
- rollout window:
  - architecture blocker が無い範囲で段階追加する
- release / communication:
  - feature value と dependency を docs へ残す

## Epic readiness contract
- Epic に要求する最低条件:
  - prototype value にどう効くか説明できる
  - architecture initiative 側の blocker に抵触していない
  - issue に分解可能である

## final exit contract
- milestone exit:
  - feature value 拡張の current initiative 範囲が整理されている
- success metrics reviewed:
  - requirement の Metric-001 / Metric-002 を確認している
- remaining follow-up ownership:
  - post-prototype feature candidate の行き先が明示されている

## 依存 / ブロッカー
- D-001:
  - `init-local-00003 Architecture Maintenance and Hardening`
- D-002:
  - current runtime baseline の維持

## 未確定事項
- Q-001:
  - 質問:
    - `epic-00054` と epic-0003 のどちらを先に進めるか。
  - 選択肢:
    - A:
      - collaboration / lifecycle（`epic-00054`）
    - B:
      - operator value
  - 推奨案:
    - A
  - 影響範囲:
    - epic 着手順
