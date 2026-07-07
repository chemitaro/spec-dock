---
種別: 要件定義書（Issue）
ID: "iss-00300"
タイトル: "Backend Invocation Adapter"
関連GitHub: ["#300"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00300 Backend Invocation Adapter — Issue 要件定義

## 1. 目的

この Issue は、`authoring pack prepare` が生成した prompt pack を、利用者が明示的に設定した ChatGPT backend command へ渡す installed runtime adapter を追加する。

`authoring backend invoke` は backend command が未設定のときに fail-closed し、個人環境の絶対パスや特定 wrapper に依存しない。成功時も backend invocation evidence を生成するだけであり、ChatGPT output の採用、ZIP review/stage、canonical docs 更新、`.assurance.json` 更新、reviewer pass、execution-ready、PR-ready、PR delivery は主張しない。

## 2. 背景

`epic-00295` は ChatGPT Authoring Pack を SpecDock が install/update で consumer repository に提供できる runtime / skill / workflow として整備する Epic である。前段 Issue では `authoring` command skeleton、GitHub sync preflight、prompt pack prepare と safe output constraints を実装した。

現在の未解決点は、生成済み prompt pack を実際の ChatGPT automation backend へ渡す標準 runtime surface がないことである。ローカルの `oracle-chatgpt` wrapper を直接 script に直書きすると、他環境で再現できない。そのため SpecDock 側には backend command を差し替えられる薄い invocation adapter と invocation contract が必要である。

## 3. 親 Epic から継承する条件

- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` に置く。
- Dogfooding workspace の `spec-dock/...` は consumer-side mirror として検証に使う。
- ChatGPT-derived output は evidence-only であり、明示的な採用判断までは canonical authority を持たない。
- `github-synced` と `local-context` は provenance と authority を区別する。
- 中間 Issue では PR を作成せず、final quality gate / PR delivery は `iss-00307` に defer する。

## 4. Scope

この Issue で実現すること:

- `./spec-dock/scripts/spec-dock authoring backend invoke` を implemented command として提供する。
- `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional compatibility fallback `ORACLE_CHATGPT_COMMAND` の順に backend command を解決する。
- backend command string を `shlex.split(..., posix=True)` 相当に argv 化し、shell execution を使わない。
- backend process には、resolved backend argv に `--slug <slug>`、`-p <prompt>`、prompt pack 内の各根拠ファイルを repeated `--file` で追加した固定 ABI を渡す。
- `--output-dir` は adapter summary / diagnostics の出力先であり、backend argv には渡さない。
- `--dry-run` では backend process を起動せず、resolved command、prompt pack、argv、provenance、authority summary を出力する。
- prompt pack の存在、必須 metadata、authority boundary、output summary target の安全性を検証する。
- backend non-zero、timeout、malformed command、missing prompt pack、unsafe output target を fail-closed に扱う。
- stdout / stderr / diagnostics summary では secret-looking data と host-local absolute path を redaction する。
- `github-synced` と `local-context` の invocation provenance を区別し、`local-context` は lower authority evidence として表示する。
- 既存 standalone compatibility script がある場合は、provider-side runtime application へ委譲するか、同等 contract を維持する。

この Issue で実現しないこと:

- 任意 AI provider registry や backend autodetection。
- backend command 未設定時の推測実行。
- ZIP review / stage / extraction。
- Initiative/Epic/Issue candidate validation。
- Issue draft adoption validation。
- human approval stop gate。
- canonical docs への自動採用。
- `.assurance.json` mutation。
- `authorized_profile` 決定。
- reviewer pass / execution-ready / PR-ready / mergeable PR の自己主張。
- final quality gate / PR delivery。

## 5. Actor / Trigger

| Actor | 役割 | この Issue との関係 |
| --- | --- | --- |
| Codex orchestrator | prompt pack を作り backend invocation を起動する | `authoring backend invoke` の主利用者 |
| SpecDock runtime user | consumer repo で installed runtime を使う | backend command を環境変数または CLI で指定する |
| ChatGPT backend command | 外部 ChatGPT automation を実行する process | runtime adapter から argv と prompt pack を受け取る |
| spec-reviewer / code-reviewer / qa-reviewer | 後続 gate | この Issue の planning / implementation / verification を評価する |

Trigger:

- `./spec-dock/scripts/spec-dock authoring backend invoke ...`
- provider-side compatibility script の直接実行。

## 6. Functional Requirements

| ID | 要件 |
| --- | --- |
| RQ-001 | `authoring backend invoke --help` は implemented command として表示され、`--backend-command`、`--prompt-pack`、`--output-dir`、`--slug`、`--prompt`、`--evidence-mode`、`--dry-run`、`--timeout-seconds`、`--format` を案内する。 |
| RQ-002 | `--backend-command` が指定された場合、env vars より優先する。 |
| RQ-003 | `--backend-command` がない場合、非空の `SPECDOCK_CHATGPT_COMMAND` を使う。 |
| RQ-004 | `SPECDOCK_CHATGPT_COMMAND` が未設定または空の場合のみ、非空の `ORACLE_CHATGPT_COMMAND` を optional compatibility fallback として使う。 |
| RQ-005 | backend command が解決できない場合、backend process を起動せず `blocked` diagnostics を返す。 |
| RQ-006 | backend command は argv list として実行し、`shell=True` 相当の shell execution を使わない。 |
| RQ-007 | malformed backend command string は shell に渡さず、`blocked` diagnostics を返す。 |
| RQ-008 | backend argv は `<resolved-backend-argv> --slug <slug> -p <prompt> --file <pack>/chatgpt-use-prompt.md --file <pack>/expected-output-contract.md --file <pack>/manifest.json --file <pack>/provenance.json --file <pack>/source-manifest.json --file <pack>/stale-if.json --file <pack>/safe-output-constraints.md` の形にする。 |
| RQ-009 | `--dry-run` は backend process を起動せず、実行計画と invocation summary だけを出力する。 |
| RQ-010 | prompt pack が存在しない、読めない、または必須 metadata を欠く場合は fail-closed する。 |
| RQ-011 | output summary target が canonical docs、symlink、または永続 report に不適切な host-local absolute path を指す場合は rejected / blocked とする。 |
| RQ-012 | backend non-zero exit は invocation failure として扱い、canonical adoption / reviewer pass / PR-ready を主張しない。 |
| RQ-013 | timeout は `blocked` diagnostics として扱う。 |
| RQ-014 | stdout / stderr summary では secret-looking data と host-local absolute path を redact する。 |
| RQ-015 | `local-context` invocation は `github-synced` より低い authority として summary に記録し、採用には explicit EAL disposition が必要であることを残す。 |
| RQ-016 | runtime command と provider-side compatibility script は、同じ domain/application contract を共有する。 |
| RQ-017 | この Issue の finish evidence は PR delivery を行わず、`iss-00307` への defer rationale を記録する。 |

## 7. Acceptance Criteria

| ID | 受け入れ条件 | 証跡 |
| --- | --- | --- |
| AC-001 | `authoring backend invoke --help` が implemented command として必要 option を表示し、`--force` を表示しない。 | CLI stdout / test |
| AC-002 | backend command 未設定時、実 process を起動せず `status=blocked` を返す。 | CLI JSON / sentinel absence |
| AC-003 | CLI `--backend-command` が `SPECDOCK_CHATGPT_COMMAND` と `ORACLE_CHATGPT_COMMAND` より優先される。 | CLI JSON / test |
| AC-004 | `SPECDOCK_CHATGPT_COMMAND` が `ORACLE_CHATGPT_COMMAND` より優先される。 | CLI JSON / test |
| AC-005 | primary env が空の場合だけ `ORACLE_CHATGPT_COMMAND` fallback が使われる。 | CLI JSON / test |
| AC-006 | malformed command string は shell 実行されず `status=blocked` になる。 | CLI JSON / sentinel absence |
| AC-007 | `--dry-run` は backend process を起動しない。 | sentinel absence |
| AC-008 | prompt pack missing / unreadable / missing required metadata は fail-closed する。 | CLI JSON / test |
| AC-009 | canonical output target、symlinked output target、unsafe host-local output target は rejected / blocked になる。 | CLI JSON / filesystem inspection |
| AC-010 | backend argv は list として渡され、固定 ABI suffix と prompt pack files を含み、prompt に shell metacharacter が含まれても shell injection されない。 | captured argv / test |
| AC-011 | backend non-zero exit は no-adoption diagnostics になり、canonical adoption / reviewer pass / PR-ready を主張しない。 | CLI JSON/text / test |
| AC-012 | timeout は `status=blocked` と timeout diagnostics になる。 | CLI JSON / test |
| AC-013 | stdout/stderr summary は secret-looking data と host-local absolute path を redact する。 | CLI JSON/text / test |
| AC-014 | `local-context` summary は lower authority provenance を保持する。 | CLI JSON / test |
| AC-015 | provider-side runtime path と dogfood installed runtime path の両方で smoke test が通る。 | pytest / CLI |
| AC-016 | compatibility script の既存 contract は維持されるか、runtime application への委譲後も同等 contract を満たす。 | pytest / inspection |
| AC-017 | この Issue は PR delivery を行わず、finish evidence で `iss-00307` への defer rationale を記録する。 | `report.md` |

## 8. Failure Modes

| Failure mode | 期待される扱い |
| --- | --- |
| backend command unset | `blocked`; backend process 起動なし |
| malformed backend command | `blocked`; shell execution なし |
| prompt pack missing / invalid | `blocked` or `rejected`; no process execution |
| output target points canonical docs | `rejected` |
| symlinked summary/output target | `rejected` |
| backend non-zero | `blocked`; no adoption claims |
| backend timeout | `blocked`; timeout diagnostics |
| stdout/stderr contains secret-looking data | redacted summary only |
| stdout/stderr contains host-local absolute path | redacted summary only |
| `local-context` を `github-synced` と同格に扱う | rejected or blocked |

## 9. Grade

Issue Grade は `standard` とする。

根拠:

- installed runtime command の追加であり、consumer-visible CLI behavior を変更する。
- external process invocation、env var、redaction、path safety、authority boundary を扱う。
- Provider-side runtime と dogfood mirror の両方に影響する。
- Strict/Critical 相当の data migration、production data mutation、irreversible operation は含まない。

## 10. Evidence Sources

- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/plan.md`
- `spec-dock/active/issue/artifacts/20260707t171251z-draft-requirement-implement-backend-invocation-adapter-draft-requirement.md`
- `spec-dock/active/issue/artifacts/20260707t171251z-01-draft-design-implement-backend-invocation-adapter-draft-design.md`
- `spec-dock/active/issue/artifacts/20260707t171252z-draft-plan-implement-backend-invocation-adapter-draft-plan.md`
- ChatGPT Use session `iss-00300-planning` evidence summary to be recorded in `report.md`
