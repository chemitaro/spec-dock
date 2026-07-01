---
種別: disc
ID: "20260630t080402z-disc"
タイトル: "Manual Test Readiness Failure Root Cause Analysis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224"]
関連: ["iss-00247", "#247", "manual-tests/iss-00247-profile-template-compose-20260630/summary.md"]
authority: "proposed"
derived_from: [
  "manual-tests/iss-00247-profile-template-compose-20260630/summary.md",
  "manual-tests/iss-00247-profile-template-compose-20260630/test-results.md",
  "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py",
  "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py",
  "tests/cli_runtime/test_workflow.py",
  "tests/unit/domain/test_workflow_state.py",
  "deep-consultant consultation: Einstein"
]
reflected_to: []
---

# 20260630t080402z-disc Manual Test Readiness Failure Root Cause Analysis

## 位置づけ

この artifact は、Issue #247 / PR #248 後の手動テストで見つかった readiness failures の原因と修正方針だけを扱う focused analysis である。

対象は `manual-tests/iss-00247-profile-template-compose-20260630/summary.md` に記録された F-001〜F-004 に限定する。Epic #224 全体の再計画、新規 Initiative / Epic の要否、テンプレート改善全般、automatic Lite default はこの文書の対象外である。

この文書は proposal であり、canonical authority ではない。採用する場合は後続 Issue の `requirement.md` / `design.md` / `plan.md`、実装修正、回帰テスト、`report.md` Evidence Adoption Ledger へ反映する。

## 要約

F-001〜F-004 の主因は、grade template pack の内容そのものではなく、`workflow status` / `guidance issue-execution` が使う readiness classifier の判定契約が、今回導入された template sentinel と plan 構造に追随していないことである。

特に問題は次の 4 点に分かれる。

- placeholder 検出が「cell 全体一致」や古い sentinel の literal list に寄っており、composite placeholder を取りこぼす。
- executable plan 判定が any-match で、`Validation Gate` のような品質ゲート見出しだけでも executable と誤判定し得る。
- requirement 判定が新テンプレートの `REQ-XXX` / `CON-...` 系 placeholder を知らない。
- design frontmatter 判定が `template` / `placeholder` という一般語の substring 検索になっており、正当な title / prose を誤って scaffold 扱いする。

修正は runtime classifier を fail-closed に寄せることを最優先とし、同時に F-001〜F-004 を regression test として固定する。

## 入力根拠

- 手動テストサマリー:
  - `manual-tests/iss-00247-profile-template-compose-20260630/summary.md`
- 手動テスト結果ログ:
  - `manual-tests/iss-00247-profile-template-compose-20260630/test-results.md`
- 実装確認:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
- 既存テスト確認:
  - `tests/cli_runtime/test_workflow.py`
  - `tests/unit/domain/test_workflow_state.py`
- 第三者分析:
  - deep-consultant `Einstein`

## Failure Matrix

| ID | 症状 | 実際の危険 | 直接原因 | 根本原因 |
|---|---|---|---|---|
| F-001 | plan の table cell に `SAFE-\`CLOS-...\`` が残っても `ready` | 未解決 closure / safety evidence placeholder のまま実装開始できる | `_has_placeholder_table_rows` が cell 全体一致に寄っている | placeholder registry がなく、composite sentinel を共通契約として扱えていない |
| F-002 | `## Validation Gate` だけの plan が `ready` | 実装ステップなしで execution-ready になる | `_classify_plan_text` が `validation gate` を executable marker に含める | plan readiness が「品質ゲートの存在」と「実行可能作業単位の存在」を分けていない |
| F-003 | requirement に `REQ-XXX` / `CON-...` が残っても `ready` | 未確定要件・未確定制約のまま implementation plan が承認済み扱いになる | `classify_requirement_text` の placeholder list が古い | requirement/design/plan が同じ template placeholder contract を共有していない |
| F-004 | design title に `template` があるだけで `design-not-substantive` | 正当な design が block される | `_classify_design_text` が frontmatter 全体に generic word を substring 検索している | scaffold 判定が field-aware ではなく、一般語と sentinel を区別していない |

## F-001: composite placeholder を取りこぼす

### 再現した症状

手動テストでは、plan の table cell に `SAFE-\`CLOS-...\`` が残っている状態で `workflow status` が `state=ready` / `reason_code=assurance-valid` を返した。

### 原因

`workflow.py` の `_has_placeholder_table_rows` は、table cell を `strip("`").lower()` した上で `_is_generated_placeholder_token(cell)` を呼ぶ。現在の `_is_generated_placeholder_token` は、`...`、`#...`、`xxx` / `...` を末尾に持つ単独 token には反応するが、`SAFE-\`CLOS-...\`` のように prefix と code span が組み合わさった composite expression では cell 全体が token pattern に一致しない。

既存テストは `| Allowed paths | ... |` や `` `report.md#...` ``、`` `M...` `` のような単純 placeholder を押さえている。一方で、今回の template pack では `SAFE-\`CLOS-...\``、`CTR-\`CLOS-...\``、`MIG-\`CLOS-...\``、`SAFE-\`B-...\`` のような composite sentinel が増えたため、既存 detector の前提から漏れた。

### 修正方針

- placeholder detector を shared helper として定義し、requirement / design / plan から同じ契約を見る。
- table/list cell では、cell 全体一致だけでなく、known placeholder token の containment を見る。
- 検出対象は少なくとも次を含める。
  - `...`
  - `report.md#...`
  - `REQ-XXX`
  - `CON-...`
  - `DES-...`
  - `VIS-...`
  - `B-...`
  - `CLOS-...`
  - `SAFE-...`
  - `SAFE-\`CLOS-...\``
  - `SAFE-\`B-...\``
  - `CTR-\`CLOS-...\``
  - `COMP-\`CLOS-...\``
  - `MIG-\`CLOS-...\``
  - `REC-\`CLOS-...\``
- 裸の `...` を本文全体で無制限に探すと false positive が増えるため、table/list cell、code span、ID-like token、known template sentinel を中心に検出する。

### 回帰テスト

- `tests/cli_runtime/test_workflow.py`
  - plan に `SAFE-\`CLOS-...\`` を含めると `blocked / plan-not-executable`。
  - plan に `SAFE-\`B-...\`` を含めると `blocked / plan-not-executable`。
  - filled standard plan は引き続き `ready / assurance-valid`。

## F-002: Validation Gate だけで executable plan と誤判定する

### 再現した症状

plan に `## Validation Gate` だけがあり、実装ステップがない状態で `workflow status` が `state=ready` を返した。

### 原因

`workflow.py` の `_classify_plan_text` は、`markers` の any-match で `has_executable_marker` を立てている。この `markers` には `validation gate`、`報告証跡` のような品質ゲート / 証跡系の見出しも含まれる。結果として、実装ステップ、振る舞い backlog、TDD cycle、closure contract がなくても、品質ゲート見出しだけで executable plan と判定される。

これは `M99 最終品質ゲート` を template に追加した今回の変更で顕在化しやすくなった。M99 は必要な品質ゲートだが、実装計画の実行単位そのものではない。

### 修正方針

- plan marker を 2 種類に分ける。
  - executable work marker:
    - `実装ステップ`
    - `振る舞いバックログ`
    - `実行中の振る舞い`
    - `tdd サイクル`
    - `step closure contract`
    - `approved-no-op`
    - `decision-only closure`
  - supporting / quality marker:
    - `validation gate`
    - `報告証跡`
    - `m99`
    - `static analysis`
    - `lint`
    - `tests`
- `ready` には executable work marker を必須にする。
- supporting / quality marker は plan の完成度を補助するが、単独では executable とみなさない。
- `approved-no-op` / `decision-only closure` は例外的に実装ステップなしでも実行可能扱いにできるが、その場合は explicit closure contract と report evidence destination を要求する。

### 回帰テスト

- `tests/cli_runtime/test_workflow.py`
  - `## Validation Gate` だけの plan は `blocked / plan-not-executable`。
  - `## M99 最終品質ゲート` だけの plan は `blocked / plan-not-executable`。
  - `## 実装ステップ` だけで中身が substantive な plan は既存 positive として通る。
  - `approved-no-op` / `decision-only closure` は別 positive test として、明示理由と evidence destination がある場合だけ通す。

## F-003: requirement の新 placeholder を取りこぼす

### 再現した症状

requirement に `REQ-XXX` と `CON-...` が残っている状態で、plan/design が otherwise substantive だと `workflow status` が `ready` を返した。

### 原因

`workflow_state.py` の `classify_requirement_text` は、`SC-XXX`、`BH-XXX`、`AC-XXX`、`B-CAND-XXX`、`TERM-XXX` など古い placeholder marker を literal tuple で持つ。一方で、Issue #247 の template pack には `REQ-XXX`、`CON-...`、design / plan trace 用の `DES-...`、`CLOS-...`、`B-...` などが入った。requirement classifier はこの新しい sentinel set を知らないため、未完成 requirement を `substantive` と扱う。

### 修正方針

- requirement 専用の literal tuple を拡張するだけでなく、共有 placeholder detector を導入する。
- requirement では少なくとも次を scaffold signal として扱う。
  - `<ISS_ID>` / `<ISS_TITLE>` / `<GITHUB_ISSUE_NUMBER_OR_URL>`
  - `YYYY-MM-DD`
  - `REQ-XXX`
  - `SC-XXX`
  - `BH-XXX`
  - `AC-XXX`
  - `CON-...`
  - `TERM-XXX`
  - `B-CAND-XXX`
  - `DES-...`
  - `CLOS-...`
  - `SAFE-...`
- `CON-...` のような ellipsis sentinel は、本文中の通常の三点リーダや説明文まで拾いすぎないよう、ID-like prefix + `...` の形を中心に検出する。

### 回帰テスト

- `tests/unit/domain/test_workflow_state.py`
  - `REQ-XXX` が残る requirement は `scaffold`。
  - `CON-...` が残る requirement は `scaffold`。
  - `REQ-001` / `CON-001` のような実 ID は scaffold 扱いしない。
- `tests/cli_runtime/test_workflow.py`
  - valid assurance があっても requirement に `REQ-XXX` / `CON-...` が残る場合は `requirement-capture` または blocked になり、`may_execute_approved_plan=false`。

## F-004: design frontmatter の generic word で false negative

### 再現した症状

design frontmatter title に `template` という語が含まれているだけで、substantive な design が `design-not-substantive` と判定された。

### 原因

`workflow.py` の `_classify_design_text` は frontmatter scaffold markers に `template` と `placeholder` を含めている。`_frontmatter_has_any` は frontmatter 全体に対する substring 探索のため、title、説明、タグなどに正当な `template` が出るだけで scaffold と判定される。

今回の template pack は「テンプレート契約（template contract）」や `docs / template` という正当な語を多く含むため、この判定は実運用で false negative を起こしやすい。

### 修正方針

- frontmatter 判定を field-aware にする。
- generic word の `template` / `placeholder` は scaffold marker から外す。
- scaffold signal として残すのは、明示的な状態・生成 sentinel に限定する。
  - `状態: "draft`
  - `状態: draft`
  - `draft | proposed`
  - `artifact_state: awaiting-assurance-compose`
  - `<ISS_ID>`
  - `<ISS_TITLE>`
  - `YYYY-MM-DD`
  - `todo`
  - `tbd`
- body 側も `template` / `placeholder` の一般語では scaffold 扱いしない。placeholder detection は known sentinel / list/table placeholder へ寄せる。

### 回帰テスト

- `tests/cli_runtime/test_workflow.py`
  - frontmatter title に `template` を含む substantive design は `ready` を維持する。
  - frontmatter title に `placeholder` を含む substantive design も、本文が substantive なら `ready` を維持する。
  - `artifact_state: awaiting-assurance-compose` は引き続き `design-not-substantive`。
  - `状態: "draft | proposed | approved"` は引き続き `design-not-substantive`。

## 実装方針

### 1. shared placeholder detector を作る

推奨は、`workflow_state.py` または小さな domain helper に placeholder detector を寄せること。`application/workflow.py` と `domain/workflow_state.py` が別々の sentinel list を持つと、今回と同じ drift が再発する。

候補:

- `domain/workflow_state.py`
  - `contains_generated_placeholder(text: str, *, mode: Literal["requirement", "artifact_cell", "artifact_text"]) -> bool`
- または新規:
  - `domain/artifact_readiness.py`

ただし初回修正では過剰抽象化を避け、既存構造に合わせて `workflow_state.py` へ小さく置くのが安全である。

### 2. plan readiness を executable marker と quality marker に分ける

`_classify_plan_text` は次の順序へ変える。

1. missing / empty / draft frontmatter を block。
2. placeholder entries があれば block。
3. explicit non-executable markers があれば block。
4. executable work marker があるかを確認。
5. quality marker だけの場合は block。
6. executable marker があり、placeholder がなければ executable。

### 3. design frontmatter 判定を narrow にする

`template` / `placeholder` は frontmatter scaffold markers から外す。代わりに `artifact_state` や draft state のような明示 sentinel に限定する。

### 4. tests を red-green で固定する

今回の manual failures は CLI runtime surface で観測されたため、unit test だけでなく `tests/cli_runtime/test_workflow.py` に negative tests を追加する。requirement placeholder detector は `tests/unit/domain/test_workflow_state.py` にも追加する。

## 推奨実装順序

1. F-003 用に requirement placeholder detector test を追加する。
2. F-001 用に composite placeholder plan の CLI runtime test を追加する。
3. F-002 用に validation-gate-only plan の CLI runtime test を追加する。
4. F-004 用に title contains `template` / `placeholder` の positive CLI runtime test を追加する。
5. shared placeholder detector を実装する。
6. `_classify_plan_text` の executable predicate を厳格化する。
7. `_classify_design_text` の frontmatter scaffold marker を narrow にする。
8. `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py` を実行する。
9. 必要なら `manual-tests/iss-00247-profile-template-compose-20260630` の再実行結果を追記または後続 manual test artifact に記録する。

## リスクと注意点

- placeholder detector を本文全体の単純 substring にすると、正当な説明文や code sample を block しすぎる。
- 逆に table/list cell だけに限定しすぎると、requirement 本文中の `REQ-XXX` / `CON-...` を取りこぼす。
- `...` は一般的な省略記号でもあるため、裸の `...` は文脈付きで扱う。
- `template` / `placeholder` は domain 語として正当に出現するため、scaffold 判定に使わない。
- false negative より false positive の方が危険である。execution readiness では、判定不能なら `ready` にしない。

## 結論

今回の failure は、grade template pack の導入で新しい placeholder vocabulary と plan structure が増えた一方、readiness classifier が古い sentinel と粗い marker any-match のままだったことが原因である。

したがって、修正は template 文言の追加調整ではなく、runtime の artifact readiness contract を更新することに集中すべきである。具体的には、shared placeholder detector、executable plan predicate の厳格化、design frontmatter 判定の narrow 化、F-001〜F-004 の regression tests を 1 セットとして実施するのが最小かつ安全な修正である。
