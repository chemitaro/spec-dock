# 結論

**実施判定: `GO_BOUNDED_PROMPT_ROLE_LABEL_REPAIR`**

GitHub Connector で `chemitaro/spec-dock` の current branch `iss-00334-implement-chatgpt-issue-planning-workflow` を確認し、branch ref と指定 SHA `65e755ef80733ed28f66024bab4e31d8f6e8c427` が `identical` であることを確認した。default branch は使用していない。指定 commit は、Planner／Semantic Revision の13 H2契約を導入した commit である。

修正は、**Planner と Semantic Revision の provider prompt にある4個の PlantUML role label のハイフンを空白へ置換し、既存 validator が探索する文字列と一致させること**に限定する。

validator、Reviewer、prompt character ceiling、Candidate／Review／Human／apply lifecycle は変更しない。

# 根拠

現行 Planner prompt と Semantic Revision prompt は、どちらも次のハイフン表記を要求している。

```text
system-context/responsibility-boundary/planning-sequence/implementation-roadmap
```

一方、validator は PlantUML fence の**内部文字列**を casefold した後、次の空白表記を探索する。

* `system context`
* `responsibility` または `authority boundary`
* `planning sequence` または `issue planning sequence`
* `implementation roadmap` または `remaining implementation roadmap`

ハイフンを空白へ正規化する処理はない。

添付 live ZIP も確認した。onboarding companion は13個のH2と4個のPlantUML blockを持つが、block title は次の形だった。

```text
title system-context
title responsibility-boundary
title planning-sequence
title implementation-roadmap
```

このうち `responsibility-boundary` は部分文字列 `responsibility` を含むため偶然通るが、`system-context`、`planning-sequence`、`implementation-roadmap` は validator の空白語句に一致しない。したがって、拒否原因は section 数や PlantUML 数ではなく、**authoring prompt と validator の role-label lexical contract の不一致**である。

現行設計も、companion に system context、responsibility boundary、planning sequence、implementation roadmap の4役を要求しつつ、Runtime validator、Review、Human、apply の既存境界を維持する設計である。

# 変更許可範囲

## Production authority

変更する provider authority は次の2ファイルだけとする。

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
```

## Dogfood projection

provider 修正後、既存の official update／projection 経路を使って次の2ファイルを再生成する。

```text
.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
.agents/skills/spec-dock-issue-planning/resources/revision-prompt.md
```

projection は直接編集しない。現行 HEAD でも provider と projection はそれぞれ同じ blob SHA である。

provider authority を先に変更し、root の `spec-dock/`／`.agents/` projection を official 経路で更新する、という既存 ownership ruleを維持する。

## Test allowlist

必要最小限のテスト変更は次の3ファイルに限定する。

```text
tests/unit/application/test_issue_planning_prompt.py
tests/unit/domain/test_issue_planning_candidate.py
tests/integration/test_issue_planning_e2e.py
```

# 厳密な文字列契約

## 置換前

両 provider prompt の最終行は現在、次のとおりである。

```text
4+ valid `plantuml` fences: system-context/responsibility-boundary/planning-sequence/implementation-roadmap.
```

## 置換後

Planner と Semantic Revision の双方で、上記一行を**完全に同じ次の一行**へ置換する。

```text
4+ valid `plantuml` fences: system context/responsibility boundary/planning sequence/implementation roadmap.
```

## 契約解釈

4つの slash-separated label は、各 intended PlantUML block 内に存在させる literal role phrase である。

| Block role              | block 内に必要な文字列            |
| ----------------------- | ------------------------- |
| System context          | `system context`          |
| Responsibility boundary | `responsibility boundary` |
| Planning sequence       | `planning sequence`       |
| Implementation roadmap  | `implementation roadmap`  |

`title` 行に置くことが最も直接的だが、validator 上の本質は fence 内部に文字列が存在することである。比較は case-insensitive だが、次のハイフン表記は同値として扱わない。

```text
system-context
planning-sequence
implementation-roadmap
```

`responsibility boundary` は既存設計の role 名を維持しつつ、validator の accepted substring `responsibility` を満たす。

この置換は4文字の `-` を4文字の空白へ置き換えるだけで、行長および UTF-8 byte length は変化しない。したがって、prompt ceiling を引き上げる理由はない。

13 H2 の次の行は変更しない。

```text
Subordinate; canonical precedence. 13 nonempty distinct H2s, exact labels, no split/merge: ...
```

# 明示的な変更禁止範囲

次は編集しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_candidate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
requirement.md
design.md
plan.md
Candidate builder／verifier
Review result schema
Human decision schema
apply／rollback／publication code
Oracle adapter
CLI result contract
```

特に次は禁止する。

* validator にハイフン正規化を追加する。
* validator の accepted role を拡張する。
* `onboarding companion PlantUML role is missing` の条件を緩める。
* Reviewer prompt に authoring-only role contract を追加する。
* prompt character ceiling の数値を増やす。
* Candidate／Review／Human／apply の authority や状態遷移を変更する。

既存設計は Planner／Reviewer／adapter を mutation path へ入れず、Human-approved apply transaction を維持すると定めている。

# テスト変更

## 1. Prompt unit tests

対象:

```text
tests/unit/application/test_issue_planning_prompt.py
```

### Planner

既存 `test_planner_prompt_contains_exact_zip_and_connector_contract` の diagram role 期待値を次へ変更する。

```text
system context
responsibility boundary
planning sequence
implementation roadmap
```

加えて、置換後の完全な一行が synthesized Planner prompt に一回だけ存在することを確認する。

旧ハイフン一行が synthesized prompt に存在しないことも確認する。

現行テストはハイフン表記だけを確認しているため、この期待値変更は current HEAD で Red になる。

### Semantic Revision

既存 `test_semantic_revision_companion_contract_is_self_contained` に Planner と同じ完全一行の assertion を追加し、role 期待値を空白表記へ変更する。

Semantic Revision でも旧ハイフン一行が存在しないことを確認する。

### Reviewer isolation

既存 `test_reviewer_prompt_has_one_attachment_authority` では、引き続き次を確認する。

* 13 H2 authoring contract がない。
* 新しい PlantUML role contract の完全一行もない。
* Reviewer の read-only／defect-only contract は変更されていない。

Reviewer に authoring-only contractを流入させない。

### Ceiling

`test_prompt_tuning_fixed_scenario_character_budgets` の数値は変更しない。

```text
Planner: 3248
Reviewer: 3657
Semantic Revision: 3385
```

## 2. Validator characterization

対象:

```text
tests/unit/domain/test_issue_planning_candidate.py
```

既存 positive fixture はすでに空白表記を使用している。

```text
title System Context
title Responsibility Boundary
title Planning Sequence
title Implementation Roadmap
```

これを変更しない。既存 `test_s10_onboarding_accepts_exact_thirteen_heading_contract` が引き続き Green であることを確認する。

既存の incomplete-contract parameterization に、live failureを再現する `hyphen_roles` mutation を一件だけ追加する。

mutation は少なくとも次の3つを空白からハイフンへ変える。

```text
System Context       -> system-context
Planning Sequence    -> planning-sequence
Implementation Roadmap -> implementation-roadmap
```

期待結果:

```text
validate_onboarding_companion(...)
    -> ValueError("onboarding companion PlantUML role is missing")

validate_issue_authoring_files(...)
    -> ("authoring_payload_invalid",)
```

`responsibility-boundary` 単独は `responsibility` substring により通過し得るため、それだけを failure fixture にしない。

このテストは validator を変更するためではなく、**現行 validator の空白文字列契約を固定し、prompt側だけを修正したことを証明する characterization** とする。

## 3. Installed-path integration

対象:

```text
tests/integration/test_issue_planning_e2e.py
```

既存 `_assert_oracle_submission` は authoring ZIP role の場合だけ13 H2 contractを検査し、Reviewer JSON roleでは除外している。

ここへ次を追加する。

Authoring role:

* 新しい完全一行が一回存在する。
* 4つの空白 role phrase が存在する。
* 旧ハイフン一行が存在しない。

Review role:

* 新しい完全一行が存在しない。
* authoring-only role assertionsを適用しない。

fake ZIP、Candidate生成、Review JSON、Human decision、apply chain は変更しない。

# Red／Green 手順

## Red

1. Production promptをまだ変更せず、unit／integration の期待値だけを空白表記へ変更する。
2. 次を実行する。

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py
uv run pytest tests/integration/test_issue_planning_e2e.py
```

3. Planner／Semantic Revision の role contract assertion が、現行ハイフン文字列のため失敗することを確認する。
4. domain characterization は、空白 positive が通り、hyphen negative が拒否されることを確認する。

この時点で失敗理由が role-label lexical mismatch 以外なら作業を停止する。

## Green

1. provider Planner prompt の最終行を厳密な置換後文字列へ変更する。
2. provider Semantic Revision prompt に同じ変更を行う。
3. official projection経路で dogfood projectionを更新する。
4. provider／projection の byte parity を確認する。
5. 次を順に実行する。

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py
uv run pytest tests/unit/domain/test_issue_planning_candidate.py
uv run pytest tests/integration/test_issue_planning_e2e.py
```

6. current design の live-admission verification として、さらに次を実行する。

```bash
uv run pytest
uv build
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

これらは現行 S12 verification sequence と一致する。

# Green 判定条件

次をすべて満たした場合だけ Green とする。

1. Planner provider prompt に置換後一行が一回だけ存在する。
2. Semantic Revision provider prompt に同じ一行が一回だけ存在する。
3. 両 projected prompt が対応する provider bytes と一致する。
4. active authoring prompt に旧ハイフン role line が残っていない。
5. Reviewer prompt に13 H2／PlantUML authoring contractが混入していない。
6. validator sourceに差分がない。
7. Candidate／Review／Human／apply sourceに差分がない。
8. Planner `3248`、Reviewer `3657`、Semantic Revision `3385` の ceiling が変更されていない。
9. 空白 role fixture が validatorを通過する。
10. live型のハイフン role fixture が `PlantUML role is missing` で拒否される。
11. focused unit、integration、full regression、build、SpecDock validate、diff check がすべて Green。
12. diff が許可した production／projection／test files だけに閉じている。

# 再度 live create する前の停止条件

次のいずれか一つでも成立した場合、real Oracle による live create を開始しない。

* current branch が `iss-00334-implement-chatgpt-issue-planning-workflow` でない。
* local HEAD と fetched remote branch HEAD が一致しない。
* working treeまたはindexがdirty。
* provider／projection byte parityが不成立。
* Planner／Semantic Revision のどちらかが旧ハイフン契約のまま。
* Reviewer promptにauthoring role contractが流入した。
* validator、ceiling、Candidate／Review／Human／apply を変更しなければテストを通せない。
* focused test、integration、full regression、build、validate、diff checkのいずれかが失敗。
* diff allowlist外の変更が存在する。
* Humanが live target Issue、exact branch、Oracle browser/account precondition、evidence destinationを承認していない。
* exact branch／artifact identity／Candidate binding に不一致がある。

現行計画も、regression failure、provider contract不一致、Human authorizationなし、exact branch／artifact／Candidate／Review／Human binding不一致を live 前の停止条件としている。

添付の拒否済み ZIP は再提出しない。すべての gate が Green になった後、修正後 prompt から**新規 live create**を一回実施し、新しい authoring ZIP を取得する。live create 後も、fresh Review、Human decision、apply の既存境界はそのまま維持する。

# 仮定・未検証事項

* 本回答では要求どおり、コード変更、ZIP生成、テスト実行は行っていない。
* 添付 live ZIP の13 H2、4 PlantUML block、ハイフン title はローカル展開で確認した。
* prompt修正後の実モデル出力は、fake Oracle integrationだけでは確定しない。上記すべての停止条件を満たした後の新規 live create が最終確認となる。
* Web参照は使用していない。
