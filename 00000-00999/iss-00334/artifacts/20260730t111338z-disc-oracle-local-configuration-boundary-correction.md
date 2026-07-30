---
種別: disc
ID: "20260730t111338z-disc"
タイトル: "Oracle local configuration boundary correction"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "human-decision"
derived_from:
  - "Human clarification in current iss-00334 execution task"
  - "FINAL-P1-002 in 20260730t110415z-s14-fresh-final-combined-review-fail.md"
reflected_to:
  - "report.md Evidence Adoption Ledger"
  - "FINAL-P1 bounded repair scope"
---

# Oracle local configuration boundary correction

## 対象論点 (必須)
- 今回整理する論点:
  - PATHで解決したローカルOracle本体が自身の通常configを読むことを、SpecDockの禁止されたpersonal dependencyとして扱うか。
  - SpecDockがformal Issue Planningで明示すべき値と、Oracle自身へ委ねる設定の境界。
- この synthesis が必要な理由:
  - final Reviewの`FINAL-P1-002`をそのまま採用すると、SpecDockが親`HOME`／`ORACLE_HOME_DIR`／cwdを一時値へ差し替え、ローカルOracleの通常設定を無効化する実装になる。
  - Humanは、ローカルOracle本体を利用する以上、そのOracle自身の設定を利用することは許容範囲であり、SpecDockが設定を上書き・無効化すべきではないと訂正した。

## derived question sheets / research (必須)
- `interview`:
  - current taskのHuman clarification。
- `research`:
  - Oracle 0.16.1 `loadUserConfig()`、`discoverProjectConfigPaths()`、`promptSuffix`実装のsource確認。
- その他の根拠:
  - Epic `E1-REQ-030`／`E1-REQ-036`、Issue Requirementのdirect Oracle boundaryは、個人Skill／wrapper／path／fallbackを製品依存にしないことを要求する。Oracle本体が自身の通常configを読むこと自体を禁止していない。

## synthesis (必須)
- 合意済みのこと:
  - product runtimeが依存する外部commandはPATHで解決したローカルOracle本体だけとする。
  - `chatgpt-use`、個人wrapper absolute path、API／別profile／default branch fallbackを製品経路へ入れない。
  - SpecDockはformal operationに必要な値をdirect argv fieldとして明示する。
  - SpecDockはOracleのuser／project configを上書き、削除、隔離、無効化しない。
- 未合意 / 未確定のこと:
  - Oracle側で将来formal-operation向けのconfig profile／`--no-prompt-suffix`等を提供するかは本Issueの範囲外。
- source-grounded に解決できたこと:
  - current adapterはengine、model、model strategy、managed endpoint、cookie-sync禁止、wait、attachment mode、session slug、Prompt、Prompt packをargvへ明示する。
  - SpecDockはsynthesized Promptをshellなしのargvへexactly once渡せる。Oracle内部の通常config適用はOracle側の責任である。

## 選択肢 / tradeoff (必須)
- Option A: Oracle HOME／cwdをinvocationごとに一時隔離する。
  - Pros:
    - Oracle configによるeffective Prompt差異を除去できる。
  - Cons:
    - ローカルOracleの通常設定をSpecDockが暗黙に無効化し、Humanの意図と責任境界を超える。
- Option B: Oracle通常configを尊重し、formal必須値だけを明示argvにする。
  - Pros:
    - PATH Oracleという採用済み境界とoperator環境を尊重し、製品が個人wrapperへ依存しない。
    - 必須値の所在がargv fieldとして検証可能。
  - Cons:
    - Oracle内部のoptional config適用はOracle version／operator環境に従う。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - 本Issueのimplementation／final Reviewでは、personal wrapper dependencyとOracle-native config利用を混同しない。
  - 必須設定は暗黙config依存にせずexplicit argv contractとしてtestする。
- まだ proposal に留める理由:
  - canonical Requirement／Design／PlanはすでにPATH Oracleとpersonal wrapper非依存を区別しており、意味変更は不要。

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
  - `FINAL-P1-002`をHuman boundary clarificationによりnot-adoptedと記録し、隔離差分を取り消す。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `disc`と`report.md` Evidence Adoption Ledger。

## 推奨案 (必須)
- Option Bを採用する。
- Oracle-native config利用はローカルOracle本体の責任範囲として許容する。SpecDockはformal Issue Planningに必要な値だけをdirect argvで明示し、個人wrapper／path／fallbackには依存しない。
- `FINAL-P1-001`のsession slug固定点と`FINAL-P1-003`のReport整合は独立した実欠陥として修正を継続する。

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
  - Human correctionと採否を追記する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - invocation専用HOME／Oracle home／cwdによる完全config隔離。
  - `FINAL-P1-002`をblocking product defectとする判定。
- deferred:
  - Oracle-native formal-operation profileやconfig opt-outが必要かの検討。本Issueへ追加しない。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - なし。
- 追加で作る artifacts:
  - なし。Report、final closure Review prompt、PR handoffへ本artifactを参照する。
