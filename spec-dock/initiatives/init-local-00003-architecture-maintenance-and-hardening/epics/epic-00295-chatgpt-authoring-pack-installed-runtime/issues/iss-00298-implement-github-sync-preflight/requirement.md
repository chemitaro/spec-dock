---
種別: 要件定義書（Issue）
ID: "iss-00298"
タイトル: "GitHub Sync Preflight"
関連GitHub: ["#298"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00298 GitHub Sync Preflight — Issue 要件定義

## 1. 目的

この Issue は、repo-aware ChatGPT authoring invocation の前段で、ローカル作業ツリーと GitHub 側で参照される branch / HEAD / source snapshot が一致しているかを fail-closed に検査する `authoring preflight github-sync` を実装する。

ChatGPT が GitHub repository / branch を参照して高深度分析を行う前提では、ローカルだけに存在する差分、未 push commit、GitHub connector が見られない branch、または silent default-branch fallback が混入すると、生成される draft evidence の根拠が実際の作業対象とずれる。この Issue はそのズレをコマンド実行前に検出し、同期できない場合は明示的な `local-context` evidence mode として低い authority で扱う。

## 2. 観測可能な成果

- `./spec-dock/scripts/spec-dock authoring preflight github-sync` が skeleton / deferred ではなく実検査を実行する。
- clean かつ synced な branch では `status=pass` を返し、requested ref、effective ref、local HEAD、remote/GitHub-visible HEAD、source manifest hash を出力する。
- dirty tracked changes、staged changes、untracked files、unpushed commits、behind、diverged、remote branch missing、origin mismatch、source hash mismatch、connector failure、unknown default branch は `status=blocked` または `status=stale` として fail-closed になる。
- explicit opt-in なしに default branch fallback しない。
- `local-context` mode は明示指定時だけ許可され、`github_sync: not_verified`、`sync_state: local_context`、`adoption_requires: explicit_eal_disposition` を出力する。
- `local-context` evidence は `github-synced` evidence と同じ authority を主張しない。
- この Issue の完了時点では ChatGPT backend invocation、ZIP review / staging、canonical adoption、authoring runtime command による `.assurance.json` mutation、reviewer pass 主張、PR delivery は行わない。

## 3. 親 Epic から継承する要件

- `epic-00295` は ChatGPT output を evidence-only として扱い、canonical adoption / reviewer pass / execution-ready / PR-ready を ChatGPT または runtime command が自己主張することを禁止する。
- `E-RQ-GH-001` から `E-RQ-GH-011` に従い、repo-aware invocation 前の GitHub sync preflight を必須 gate とする。
- `E-RQ-RT-003` から `E-RQ-RT-006` に従い、runtime command output は deterministic diagnostics を持ち、command-local validation pass と canonical adoption / reviewer pass を区別する。
- `E-RQ-DEL-001` から `E-RQ-DEL-005` に従い、この中間 Issue では PR を作成せず、final quality gate Issue `iss-00307` に PR delivery を defer する。

## 4. 対象範囲

### 対象

- Runtime command `authoring preflight github-sync` の実装。
- local repository observation:
  - repo root
  - origin URL
  - current branch
  - local HEAD
  - tracked / staged / untracked worktree state
  - remote tracking branch state
- GitHub-visible branch / HEAD observation slot:
  - default は configured remote / remote tracking branch との comparison を実施する。
  - external GitHub connector / backend はこの Issue では直接呼ばず、後続 Issue から注入可能な adapter boundary と diagnostics を用意する。
- Source manifest / source hash の算出。
- `github-synced` と `local-context` evidence mode の provenance / authority 差分。
- CLI / JSON の reviewer-readable diagnostics。
- Provider-side source of truth と dogfooding mirror の runtime parity。
- Focused pytest fixtures for positive / negative preflight states。

### 対象外

- ChatGPT backend command invocation。
- prompt pack prepare。
- ZIP / tree output review。
- staged evidence / EAL candidate generation。
- canonical docs への adoption。
- authoring runtime command による `.assurance.json` の作成・更新。
- SpecDock workflow 自体が reviewer-gated planning / execution gate を成立させるために行う `.assurance.json` source binding refresh は対象外ではなく、`assurance classify` / `assurance verify` の workflow evidence として扱う。
- `authorized_profile` の決定。
- fresh reviewer pass、execution-ready、PR-ready の主張。
- `-f` / `--force` のような広い bypass flag。
- 中間 Issue の PR delivery。

## 5. 機能要件

| ID | 要件 |
|---|---|
| RQ-001 | default evidence mode は `github-synced` とする。 |
| RQ-002 | `github-synced` mode では、local branch と remote/GitHub-visible branch が一致し、local HEAD と remote/GitHub-visible HEAD が一致しなければ `pass` にしない。 |
| RQ-003 | dirty tracked changes、staged changes、untracked files がある場合は `blocked` とし、問題種別を diagnostics に含める。 |
| RQ-004 | local branch が upstream より ahead、behind、diverged の場合は `blocked` または `stale` とし、repo-aware invocation を進めない。 |
| RQ-005 | remote branch が存在しない場合、origin URL が期待と一致しない場合、connector-visible branch が解決不能な場合は `blocked` とする。 |
| RQ-006 | default branch fallback は explicit opt-in option がある場合だけ許可し、fallback 時は `requested_ref` と `effective_ref` を別フィールドで出力する。 |
| RQ-007 | source manifest は preflight 対象 source path と content hash を含み、manifest-level hash を出力する。 |
| RQ-008 | expected source manifest または expected source hash が指定された場合、source hash mismatch を `stale` として扱い、canonical adoption に使えないことを diagnostics に示す。 |
| RQ-009 | expected source baseline が未指定の場合は、mismatch を検査したと主張せず `source_hash_mismatch_checked: false` を出力する。 |
| RQ-010 | `local-context` mode は explicit option でのみ実行でき、GitHub sync verification を行ったかのような claim を出力しない。 |
| RQ-011 | `local-context` mode の output は `github_sync: not_verified`、`sync_state: local_context`、`adoption_requires: explicit_eal_disposition` を含む。 |
| RQ-012 | `local-context` mode は `provided_context_paths`、`diff_summary`、`unsynced_reason` の provenance を持ち、`unsynced_reason` と、provided context または diff summary のどちらかがなければ `blocked` になる。 |
| RQ-013 | command-local `pass` は canonical adoption / reviewer pass / execution-ready を意味しないことを output に含める。 |
| RQ-014 | command failure は deterministic status / reason code / remediation hint を返す。 |

## 6. 受け入れ条件

| ID | 条件 |
|---|---|
| AC-001 | clean / synced branch fixture で `authoring preflight github-sync` が `status=pass` を返す。 |
| AC-002 | pass output に requested ref、effective ref、local HEAD、remote/GitHub-visible HEAD、source manifest hash が含まれる。 |
| AC-003 | dirty tracked、staged、untracked の fixture が `status=blocked` になる。 |
| AC-004 | ahead、behind、diverged の fixture が `status=blocked` または `status=stale` になる。 |
| AC-005 | remote branch missing、origin mismatch、connector/default branch resolution failure が fail-closed になる。 |
| AC-006 | explicit opt-in なしでは default branch fallback しない。 |
| AC-007 | explicit fallback 時は `requested_ref` と `effective_ref` が区別される。 |
| AC-008 | expected source hash mismatch fixture が `status=stale` になる。 |
| AC-009 | baseline 未指定時は `source_hash_mismatch_checked: false` を出力する。 |
| AC-010 | `--evidence-mode local-context` は `github_sync: not_verified`、provided context / diff / unsynced reason、低 authority provenance を出力する。 |
| AC-011 | `local-context` mode で `unsynced_reason`、または provided context / diff summary が不足している場合は `status=blocked` になる。 |
| AC-012 | output に forbidden authority claims が含まれない。 |
| AC-013 | Provider-side runtime と dogfooding mirror の該当 command / tests が一致して通る。 |
| AC-014 | 中間 Issue として PR delivery を行わず、`iss-00307` へ defer した evidence を `report.md` に残す。 |

## 7. リスクと失敗モード

- branch mismatch を silent fallback してしまう。
- untracked files を見落として source manifest が実際の prompt context とずれる。
- `local-context` が実質的な broad force bypass として乱用される。
- connector inaccessible を人手確認済み evidence と混同する。
- command-local validation pass を reviewer pass や canonical adoption と誤読させる。

## 8. Issue grade

この Issue は `standard` として扱う。

理由:

- installed runtime command と provider-side shipped assets に影響する。
- GitHub / local repository state を扱う fail-closed gate であり、後続の ChatGPT authoring evidence の信頼性に影響する。
- ただし canonical adoption / PR delivery / destructive mutation は対象外であり、Critical / Strict 相当の高リスク変更までは含めない。

## 9. 証跡方針

- 配置済み draft artifacts は evidence-only input とし、採用判断を `report.md` の Evidence Adoption Ledger に記録する。
- 実装中の判断・逸脱・追加テストは `report.md` の Decision Ledger / session log に記録する。
- reviewer pass は runtime command や ChatGPT output ではなく、fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` の結果のみを pass として扱う。
