---
種別: disc
ID: "20260730t120701z-disc"
タイトル: "PR Repair Unit U001 Active Pointer Fixture"
状態: "archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "adopted"
derived_from:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md R001/F001/S001"
  - "20260730t120701z-01-pr-351-required-ci-repair-chatgpt-consultation.md"
reflected_to:
  - "bounded dev-coder handoff U001"
  - "report.md PR #351 required-CI repair evidence"
---

# 20260730t120701z-disc PR Repair Unit U001 Active Pointer Fixture

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - PR #351のrequired CIを失敗させるmachine-local active-pointer fixtureを、fresh checkoutで決定的に解決できるpathへ直す。
- この synthesis が必要な理由:
  - blocking CI repairを、製品コードやOracle境界へ拡張せず、一つのroot-cause familyと検証可能なwrite allowlistへ固定する必要がある。

## derived question sheets / research (必須)
- `interview`:
  - なし。HumanのOracle local configuration boundary correctionは別artifactでaccepted。
- `research`:
  - GitHub Actions run `30540472689`、job `90863805552`のfailed log。
  - `git ls-files`によるcanonical ZIPのtracked確認とactive symlinkの非tracked確認。
- その他の根拠:
  - fresh ChatGPT consultation `20260730t120701z-01-pr-351-required-ci-repair-chatgpt-consultation.md`。

## synthesis (必須)
- 合意済みのこと:
  - failed testは`tests/unit/domain/test_issue_planning_candidate.py::test_s10_current_v4_guide_satisfies_completeness_contract`だけである。
  - exact ZIPはcanonical Issue artifact pathにtrackedされている。
  - Oracleの通常local configは尊重し、本repairでOracle関連コード／設定を変更しない。
- 未合意 / 未確定のこと:
  - repair後のGitHub required CIおよびCodex reviewのterminal result。
- source-grounded に解決できたこと:
  - active pointerをCIで生成、追跡、または抽象化する必要はない。
  - 対象テストのpath literalだけを隣接テストと同じcanonical Issue artifact階層へ変更できる。

## 選択肢 / tradeoff (必須)
- Option A: 対象テストのfixture pathだけをtracked canonical ZIPへ変更する。
  - Pros:
    - fresh checkoutで決定的に解決し、product behaviorを変えない。
    - 失敗原因と変更行が一対一に対応する。
  - Cons:
    - historical Issue artifactの長いpathをテストが保持する。
- Option B: CIでactive pointerを再現、追跡、またはhelper化する。
  - Pros:
    - local active viewと同じpathを維持できる。
  - Cons:
    - CI setup／active lifecycle／abstractionへ範囲が拡大し、historical fixture testには過剰である。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - なし。
- まだ proposal に留める理由:
  - test-only repairはworker実装、検証、fresh PR observationが完了するまで実施済み事実ではない。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - 変更なし。
- `design.md`:
  - 変更なし。
- `plan.md`:
  - 変更なし。
- `ADR`:
  - 不要。
- `report.md` Evidence Adoption Ledger:
  - repairと再観測の完了結果を追記する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - no
- ADR 化しない場合の反映先:
  - `disc`と`report.md`

## 推奨案 (必須)
- Option A。`pack`のpathを、同じZIPのtracked canonical Issue artifact pathへ置き換える。
- write allowlistは`tests/unit/domain/test_issue_planning_candidate.py`の対象テストだけとする。
- `repository_root`、ZIP member選択、guide bytes、validator callは変更しない。
- focused test、module、ordinary fast pytest、lint、validate、diff確認を通し、commit／push後にnew-head `post-once` PR observationを行う。

## 推奨反映先 (必須)
- `requirement.md`:
  - 変更なし。
- `design.md`:
  - 変更なし。
- `plan.md`:
  - 変更なし。
- `ADR`:
  - 作成しない。
- `report.md` Evidence Adoption Ledger:
  - U001実装、verification、commit、fresh observationの結果を反映する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - active symlinkのtracking／CI生成、test skip、ZIP複製、path helper、新規abstraction、product／Oracle変更。
- deferred:
  - なし。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - なし。
- 追加で作る artifacts:
  - なし。既存PR repair batchと本unitを更新する。

## 実装結果

- dev-coderはwrite allowlist内の`test_s10_current_v4_guide_satisfies_completeness_contract`だけを変更した。
- `repository_root`、ZIP member選択、guide read、validator callは不変である。
- exact test `1 passed`、module `54 passed`。
- Mainのordinary fast pytestは`1141 passed, 2119 skipped`。
- `make lint`はRuff check、418 files format、mypy 281 filesがPASS。
- SpecDock validateは`nodes=227`、`git diff --check`もPASS。
- repair commitは`b70f599f1689b2867fc70699c68c3d955d1f18d5`としてpushした。
- fresh `post-once` observationはActions 3 runs PASS、Codex explicit no-findings completion、P0〜P3／unresolved threads／limitations 0、`recommended_next_action=merge_prepared`でterminal PASSした。
