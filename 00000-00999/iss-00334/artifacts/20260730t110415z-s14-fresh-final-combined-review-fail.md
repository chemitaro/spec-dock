---
種別: artifact
ID: "20260730t110415z"
タイトル: "S14 fresh final combined review fail"
状態: "adopted"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
template: "blank"
authority: "review-evidence"
derived_from:
  - "ChatGPT Pro session iss00334-final-combined-review-a4cf67bf"
  - "source HEAD a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915"
reflected_to:
  - "20260730t110128z-final-p1-repair-chatgpt-blue-team-work-packet.md"
  - "report.md"
---

# S14 fresh final combined Review — FAIL

## Identity

- repository: `chemitaro/spec-dock`
- branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- reviewed HEAD: `a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915`
- session: `iss00334-final-combined-review-a4cf67bf`
- model evidence: `requested=Pro` / `resolved=Pro` / `verified=yes`
- verdict: `FAIL`
- P0: 0
- P1: 3
- redesign／improvement proposal: 0
- merge-ready recommendation: false

## Findings

### FINAL-P1-001 — Oracle slug normalization

- perspective: code
- location: `issue_planning_chatgpt.py::_new_session_id()`／`invoke_issue_planning_chatgpt()`、Semantic Revision lane、fake Oracle tests
- requirement: `REQ-007`、`AC-004`、`REQ-020`、`AC-020`
- impact: adapterはraw `semantic_revision`を`--slug`とexpected pathへ使うが、Oracle 0.16.1は`semantic-revision`へ正規化する。real Semantic Revisionはsession／artifactを見つけられず`blocked/oracle_session_recovery_required`となる。fakeがraw argv directoryを作るため欠陥を隠す。

### FINAL-P1-002 — personal Oracle config can mutate Prompt

- perspective: code
- location: `_SAFE_ENVIRONMENT_KEYS`、`_sanitized_child_environment()`、`invoke_issue_planning_chatgpt()`、user model config test
- requirement: Design §5.3、Plan §16.2／§28.3、`REQ-012`、`REQ-017`
- impact: adapterが`HOME`／`ORACLE_HOME_DIR`を保持しrepository rootでOracleを実行するため、user／ancestor `.oracle/config.json`を読み得る。Oracleの`promptSuffix`はSpecDock validation後にPromptを変更し、個人browser defaultsも製品runtimeへ混入できる。既存testはexplicit model argvだけを確認し、この経路を実行しない。

### FINAL-P1-003 — stale Issue report

- perspective: QA
- location: `report.md`末尾のS12 same-session publication race記録、Plan §23 S13
- requirement: final worker／reviewer／live／ready-or-blocked evidenceをReportへ統合すること
- impact: reviewed HEADのReportはlive create、Candidate、Review、Human decision、apply、remote parityを未完了としているが、adoption commitはmanaged guideとexact Human decisionを追加済みである。current QA recordと完了済みlifecycleが矛盾する。

## Confirmed controls

- exact current branch／HEADをdefault-branch substitutionなしで確認。
- adoption HEADは`f488121e80fc93f01cb64fab70a06d306c903804`の直後で、managed onboarding companionとbound Human decisionを追加。
- canonical requirement／design／plan SHA-256は不変。
- Human decisionはCandidate、operation binding、reviewed identity、Review resultへexact bind。
- provider／dogfood adapterはbyte-identical。
- same-session recoveryはsingle monotonic deadline、prompt最大1、harvest最大1、replacement session 0。
- direct argv、`shell=False`、API credential stripping、personal wrapper fallbackなし、Human-only merge／close／finish／branch deletionを維持。

## Disposition

初期dispositionでは3件とも採用したが、Human boundary clarification後に採否を訂正した。

- `FINAL-P1-001`: adopted。Oracle 0.16.1 session ID固定点を実装修正する。
- `FINAL-P1-002`: not adopted。PATH Oracle本体が自身の通常configを利用することは許容し、SpecDockによるHOME／config隔離は行わない。formal必須値はdirect argv fieldで明示し、personal wrapper／path／fallbackへの製品依存だけを禁止する。正式境界は`20260730t111338z-disc-oracle-local-configuration-boundary-correction.md`を参照する。
- `FINAL-P1-003`: adopted。Reportへ完了済みlive lifecycleを追補する。

修正は別Blue Team session `iss00334-final-p1-blue-team`の提案から採用部分だけをbounded implementationへ使用し、`20260730t110128z-final-p1-repair-chatgpt-blue-team-work-packet.md`へHuman correctionを追記した。修正後は別fresh exact-HEAD closure Reviewを行う。
