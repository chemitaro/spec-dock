# report.md Decision Ledger 残課題具体化レポート

作成日: 2026-05-20

## 目的

`report.md` に `Spec Interpretation / Decision Ledger` を追加する方針は妥当である。

ただし、この方針を実装へ落とすには、次を曖昧なままにしてはいけない。

- どの粒度の判断を記録するか
- 誰が authoritative な `report.md` を書くか
- worker は何をどの形式で返すか
- `open` / `deferred` / `promoted` / `closed` の完了条件をどう扱うか
- 小規模 issue で過剰運用にしない方法
- reviewer が何を blocker / warning と判定するか
- template / skill / reviewer / structural test のどこまでを更新対象にするか

この discussion は、先行 discussion `20260520t142357z-disc-report-decision-ledger-policy.md` の残課題を、実装可能な要求へ具体化するための分析メモである。

## 全体結論

`report.md` は「作業ログ」ではなく「判断の監査台帳」として拡張する。

最も重要な設計原則は次の4つである。

1. `plan.md` は実装前の契約であり、実装中判断の置き場にしない
2. `report.md` は実装中・実装後の観測事実と判断の台帳である
3. 将来も守るべき判断は `report.md` だけに閉じ込めず、`design.md` / ADR / plan amendment / follow-up issue へ昇格する
4. authoritative な ledger は orchestrator が統合し、worker は一次情報を structured note として提出する

## 残課題 1: セクション名

### 結論

セクション名は `Spec Interpretation / Decision Ledger` とする。

### 理由

`Implementation Notes` は広すぎる。実装メモ、進捗ログ、試行錯誤ログ、テストログが混ざりやすい。

`Decision Ledger` だけでは、仕様解釈も対象であることが弱い。

`Spec Interpretation / Decision Ledger` は、記録対象を次に限定しやすい。

- spec / plan の曖昧さの解釈
- plan からの意味ある逸脱
- 複数案からの選択
- tradeoff
- follow-up 化
- 昇格判断

### 実装要求

- `report.md` template に `## Spec Interpretation / Decision Ledger` を追加する
- reviewer instruction はこの見出し名を canonical として扱う
- structural test は canonical heading の存在を検査する

## 残課題 2: table 形式か bullet 形式か

### 結論

`summary table + optional detail block` とする。

### 推奨形式

```markdown
## Spec Interpretation / Decision Ledger

| ID | Status | Type | Trigger / Gap | Decision / Interpretation | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|
| D-001 | applied | interpretation | ... | ... | no_action | ... | none |

### Decision Details

#### D-001: short title

- context:
- options considered:
- rationale:
- risk if wrong:
- rollback / revisit:
```

### 理由

table は completion gate と reviewer scan に強い。

一方で、table だけでは alternatives / rationale / risk を十分に表現しづらい。重要判断だけ detail block を許す。

### 実装要求

- template は table を必須にする
- detail block は任意にする
- structural test は table header と ID 重複を検査する
- rationale の品質は自動テストで判定しない

## 残課題 3: status と disposition の分離

### 問題

先行ドラフトでは `applied` / `open` / `deferred` / `amended` / `escalated` などが status に混ざっていた。

これは「実装上の状態」と「判断の行き先」が混ざるため、完了判定が曖昧になる。

### 結論

`Status` と `Disposition` を分ける。

`Status` は issue 内での判断状態を表す。

| Status | 意味 |
|---|---|
| `proposed` | まだ orchestrator が採用していない |
| `applied` | 実装または文書に反映済み |
| `rejected` | 採用しないと判断した |
| `superseded` | 別 entry に置き換えた |
| `deferred` | 今回 issue では扱わず後続へ送った |
| `open` | 未解決で、完了前に扱いを決める必要がある |

`Disposition` は、その判断をどこへ着地させたかを表す。

| Disposition | 意味 |
|---|---|
| `no_action` | issue-local な判断で、昇格不要 |
| `promoted_to_design` | `design.md` に反映 |
| `promoted_to_adr` | ADR に反映 |
| `promoted_to_plan` | `plan.md` amendment に反映 |
| `converted_to_followup` | follow-up issue / discussion / todo に変換 |
| `rejected` | 採用しない |
| `superseded` | 別 entry に置換 |
| `legacy_no_ledger` | legacy report の互換扱い |

### 完了条件

- `open` のまま issue を finish してはいけない
- `applied` の entry は必ず `Disposition` を持つ
- 将来も効く判断が `no_action` になっている場合は reviewer が指摘する
- `deferred` は `converted_to_followup` と follow-up 参照を持つ
- `superseded` は置換先 ID を持つ

## 残課題 4: 誰が report.md を書くか

### 結論

authoritative な `report.md` は orchestrator が所有する。

ただし、実装・文書作業を担当した worker は、一次情報として `Ledger Note` を返す義務を持つ。

### 責任分界

| 役割 | 責任 |
|---|---|
| orchestrator | canonical `report.md` の編集、統合、重複排除、status/disposition 決定、昇格判断 |
| dev-coder | 実装中に生じた仕様解釈、tradeoff、逸脱、テスト戦略判断を structured note で返す |
| doc-writer | 文書・テンプレート・skill の意味変更や表現判断を structured note で返す |
| reviewer | ledger の存在、整合、昇格漏れ、未解決判断を read-only で監査する |

### worker が直接編集してよい例外

原則は禁止する。

例外は、orchestrator が明示的に「この file set の report update も担当」と委譲した場合のみである。

この場合でも、worker は次を守る。

- `report.md` の自分の担当 entry だけを編集する
- 既存 entry の status / disposition を勝手に閉じない
- `proposed by` / `integrated by` を明記する
- completion 判断は orchestrator に返す

### 理由

複数 worker が `report.md` を直接編集すると、同じ判断の重複、status の競合、follow-up の消失が起きやすい。

一方で、実装の細かい判断は worker が最も正確に把握している。したがって、worker は raw note を出し、orchestrator が canonical ledger へ統合する。

## 残課題 5: 小規模 issue の軽量運用

### 結論

ledger は常に巨大に書くものではない。

判断がない小規模 issue では、明示的に `not required` と書けるようにする。

### 軽量形式

```markdown
## Spec Interpretation / Decision Ledger

Decision ledger: not required.

Reason: The change followed the approved plan without material spec interpretation, deviation, tradeoff, or open question.
```

### `not required` を許す条件

- typo / formatting / mechanical sync
- plan 通りの小さな修正
- 実装判断が既存 pattern 追従だけで説明できる
- scope / validation / architecture / compatibility を変更していない

### `not required` を許さない条件

- discussion-first issue
- design / workflow / template / skill を変える issue
- plan amendment が必要な issue
- reviewer fail への対応 issue
- test strategy を弱める判断がある issue
- scope 外 follow-up を発見した issue

## 残課題 6: reviewer severity

### 結論

reviewer は「ledger がないこと」ではなく「判断が追跡不能であること」を問題にする。

### Severity 案

| 状況 | severity |
|---|---|
| 重要判断が diff / report / plan にあるが ledger にない | blocker |
| `applied` 判断に disposition がない | blocker |
| `open` 判断が finish 前に残っている | blocker |
| 将来効く設計判断が `report.md` に閉じ込められている | blocker |
| ledger required か曖昧だが判断の存在が薄い | warning |
| `not required` の理由が弱い | warning |
| legacy report に ledger がない | no finding / compatibility note |

### reviewer instruction 要求

- `report.md` の有無だけで fail しない
- 判断の存在を diff / plan / design / report から推定する
- `not required` が妥当か確認する
- accepted design decision が report-only になっていないか確認する

## 残課題 7: 昇格ルール

### 結論

`report.md` は設計判断の墓場にしてはいけない。

### 昇格先の基準

| 判断の性質 | 昇格先 |
|---|---|
| 今後の実装者が守るべき構造・責務境界 | `design.md` |
| 複数 issue / epic に波及する不可逆寄りの方針 | ADR |
| 実装順序、validation、closure 条件の変更 | `plan.md` amendment |
| 今回 scope 外だが対応が必要 | follow-up issue / discussion |
| issue-local な判断 | `report.md` のみ |

### 完了 gate

issue finish 前に、すべての `applied` / `deferred` entry は次のいずれかへ着地している必要がある。

- canonical artifact に昇格済み
- follow-up へ変換済み
- issue-local として `no_action` 理由が明確
- rejected / superseded として閉じている

## 残課題 8: 既存 report との互換性

### 結論

過去の report を retroactive に blocker にしない。

### 互換方針

- 新 template 生成分から ledger section を含める
- 既存 issue は必要な場合のみ backfill する
- backfill は推測で作らず、既存 report / discussion / commit / PR から根拠があるものだけ記録する
- legacy 互換のため `legacy_no_ledger` disposition を許す

## 残課題 9: structural tests の粒度

### 結論

自動テストは構造だけを検査し、判断品質は reviewer が見る。

### 自動テスト対象

- report template に canonical heading がある
- table header に必須列がある
- allowed status / disposition / type が docs と一致する
- sample entry の ID が `D-001` 形式である
- `not required` 軽量形式が template / docs に存在する
- worker `Ledger Note` schema が skill instruction に存在する

### 自動テスト対象外

- rationale が十分か
- alternatives が妥当か
- design へ昇格すべきか
- reviewer severity が妥当か

これらは spec-reviewer / code-reviewer / human review の責務である。

## 残課題 10: skills / prompts への反映範囲

### 結論

template だけ変えても運用は定着しない。

次の4層を同時に変える必要がある。

1. `report.md` template
2. issue execution skill / workflow docs
3. reviewer instruction
4. structural tests

### 必要な instruction

orchestrator 向け:

- 実装中に判断が発生したら ledger entry を作る
- worker から `Ledger Note` を回収する
- accepted decision を report-only にしない
- finish 前に `open` を閉じる

worker 向け:

- 実装中の判断を structured note として返す
- 判断がなければ `No material implementation decisions beyond the approved plan.` と返す
- private reasoning を書かず、根拠・選択肢・リスク・影響だけを書く

reviewer 向け:

- ledger が必要な判断が追跡可能か確認する
- `not required` が妥当か確認する
- 昇格漏れを blocker として扱う

## 残課題 11: audit fidelity と retrospective 記録

### 結論

ledger は transcript dump ではない。

記録すべきなのは、判断を後から検証するための最小十分な材料である。

### 最小要素

- ID
- status
- type
- trigger / gap
- decision / interpretation
- options considered
- rationale
- impact
- evidence
- disposition
- follow-up

### 書いてはいけないもの

- agent の chain-of-thought
- prompt 全文
- 試行錯誤ログ全文
- secret / token / private payload
- diff を読めば分かるだけの作業説明

### retrospective entry

実装後に「この判断を記録すべきだった」と気づいた場合は、retroactive entry を許可する。

ただし、`Evidence` に `retrospective` と根拠ファイル / commit / reviewer comment を明記する。

## 残課題 12: completion state と issue status の分離

### 問題

ledger entry の `Status` と issue 自体の completion status を混ぜると、`applied` なのに issue として未完了、または `deferred` なのに blocker、という判断が曖昧になる。

### 結論

ledger entry の status は「判断単位」の状態に限定する。

issue completion gate は別に定義する。

### completion gate

issue を finish する前に、orchestrator は次を確認する。

- ledger required / not required が明示されている
- required な場合、すべての entry が `open` 以外になっている
- `applied` / `deferred` entry に disposition がある
- follow-up 化した entry は参照先がある
- promoted entry は反映先 artifact と re-review evidence がある
- reviewer findings が closure されている

## 残課題 13: reviewer finding closure

### 結論

reviewer finding への対応方針も ledger 対象にする。

### 記録が必要な場合

- reviewer finding に対して複数の修正方針がある
- finding を scope 外 / false positive / follow-up とする
- plan / design / ADR に昇格する
- reviewer finding をきっかけに validation strategy を変える

### 記録不要な場合

- 指摘通りの typo 修正
- テスト期待値の明白な更新
- plan 通りの不足修正

## 残課題 14: direct edit 例外の明文化

### 結論

worker に `report.md` 直接編集を許す例外は狭く定義する。

### 許可できる条件

- orchestrator が明示的に委譲している
- worker の write set に `report.md` が含まれている
- その worker が単独実装者で、競合する worker がいない
- 既存 entry を閉じる権限範囲が明示されている
- 最終統合を orchestrator が確認する

### 禁止する条件

- 複数 worker が並行している
- reviewer finding closure を worker が自己判断で閉じる
- plan amendment / ADR / design promotion を worker が勝手に完了扱いにする
- raw notes をそのまま report に貼る

## 実装へ向けた要求サマリ

### report template

- `Spec Interpretation / Decision Ledger` を追加する
- table + optional details の構成にする
- `not required` 軽量形式を示す
- status / type / disposition の allowed values を掲載する
- completion gate checklist を追加する

### issue execution skill

- worker delegation 時に `Ledger Note` を要求する
- orchestrator が notes を統合する責任を明記する
- finish 前の ledger closure gate を追加する
- `not required` の条件を示す

### reviewer instruction

- ledger required / not required の妥当性を見る
- untraceable decision を blocker とする
- accepted design decision の report-only 化を blocker とする
- legacy issue は retroactive blocker にしない

### tests

- template heading / table columns / allowed values を検査する
- skill instruction に `Ledger Note` schema があることを検査する
- reviewer instruction に ledger audit 観点があることを検査する

## 未決事項

現時点で追加検討が必要な論点は少ない。

ただし、実装前に次は最終決定する。

1. `Status` allowed values に `accepted` を入れない方針で確定するか
2. `Disposition` の列名を `Disposition` にするか `Resolution` にするか
3. `Decision ledger: not required.` の exact phrase を固定するか
4. structural test で report template のみを検査するか、skill / reviewer docs まで検査するか

推奨は次である。

- `accepted` は使わない
- 列名は `Disposition`
- 軽量形式は `Decision ledger: not required.` で固定
- structural test は template / skill / reviewer docs の3点を最低限検査する

## 追加コンサルタント分析の反映

追加分析では、次の指摘が重要だった。

1. ledger section 自体を省略するのではなく、小規模 issue でも「判断なし」を明示したほうがよい
2. worker が直接編集してよいのは、原則として観測事実と proposed entry までに限定する
3. retrospective は decision ledger と分ける
4. issue 完了時に `open` が残るなら、それは未完了か、deferred / promoted への分類漏れである
5. reviewer severity は `blocker` / `major` / `minor` / `nit` の4段階が実装しやすい

これにより、先行案の一部を補正する。

### 補正 1: 軽量運用は `not required` より「空を明示」を優先する

先行案では次の形式を提案していた。

```markdown
Decision ledger: not required.
```

ただし、これは section そのものが不要に見えやすく、後続の validator / reviewer / template が揺れやすい。

より良い形式は、section は常に存在させ、内容として material decision がないことを明示する形である。

```markdown
## Spec Interpretation / Decision Ledger

No material interpretation changes.

No decision entries.
```

実装時は、exact phrase を固定する。

- `No material interpretation changes.`
- `No decision entries.`

この形式なら、小規模 issue の負担を増やさず、テンプレート構造と reviewer 観点を保てる。

### 補正 2: worker editable scope を明示する

worker は実装中の一次情報を最も正確に持つ。

しかし、worker が authoritative ledger を直接閉じると、orchestrator の監査責任が崩れる。

したがって、template / skill では次のような section ownership を明示するのが望ましい。

```markdown
<!-- worker-editable: execution-evidence, proposed-report-entries -->
<!-- orchestrator-owned: spec-interpretation-decision-ledger, completion-assessment -->
```

worker が直接編集してよいもの:

- 実行したテストコマンドと結果
- 変更したファイル一覧
- 失敗ログの要約
- manual test の観測結果
- proposed report entry

worker が直接確定してはいけないもの:

- `open` を resolved にする
- `deferred` / `promoted` を確定する
- reviewer 指摘を対応不要と確定する
- plan と違う scope を既成事実化する
- decision rationale を後から都合よく上書きする

### 補正 3: retrospective を分離する

`Decision Ledger` は「その時点で何を根拠に判断したか」を残す台帳である。

後から分かった改善点や学びを、過去の decision entry に混ぜて書き換えると監査性が落ちる。

したがって `report.md` には、必要に応じて次の役割分担を持たせる。

| Section | 役割 |
|---|---|
| `Spec Interpretation / Decision Ledger` | 実行中の仕様解釈・判断・逸脱・昇格判断 |
| `Execution Evidence` | テスト、変更ファイル、manual verification、失敗/復旧 evidence |
| `Completion Assessment` | issue 完了時の acceptance / unresolved / reviewer gate 判定 |
| `Retrospective` | 後から分かった改善点、次回への学び、template 改善候補 |

`Retrospective` は acceptance の証拠に使わない。

retrospective から新しい作業が必要になった場合は、decision entry を `promoted` / `converted_to_followup` 相当にし、follow-up 参照を残す。

### 補正 4: status / disposition の最終候補

ここが最も慎重に決めるべき点である。

候補 A は、先行案のように `Status` と `Disposition` を分ける方式。

```markdown
| ID | Status | Type | Trigger / Gap | Decision / Interpretation | Disposition | Evidence | Follow-up |
```

候補 B は、追加分析のように `status` に `open` / `closed` / `deferred` / `promoted` / `rejected` を入れる方式。

```markdown
| id | status | raised_by | summary | decision | rationale | evidence | follow_up |
```

現時点の推奨は候補 A である。

理由:

- `promoted` は状態というより行き先であり、status と混ぜると completion gate が曖昧になる
- `deferred` も状態と disposition の両方の意味を持ちやすい
- reviewer は「未解決か」「どこに着地したか」を別々に見られたほうがよい
- future-proof に `promoted_to_design` / `promoted_to_adr` / `converted_to_followup` を表現できる

ただし、先行案の `Status` は多すぎるため簡素化する。

推奨する `Status`:

| Status | 意味 |
|---|---|
| `open` | まだ確定していない。issue completion 前に解消が必要 |
| `resolved` | issue 内で扱いが確定した |
| `superseded` | 別 entry に置き換えた |

推奨する `Disposition`:

| Disposition | 意味 |
|---|---|
| `applied` | issue-local に採用し、成果物へ反映した |
| `rejected` | 採用しない |
| `promoted_to_design` | `design.md` に昇格 |
| `promoted_to_adr` | ADR に昇格 |
| `promoted_to_plan` | `plan.md` amendment に昇格 |
| `converted_to_followup` | follow-up issue / discussion へ変換 |
| `deferred` | 今回は扱わず、再検討条件を明記して保留 |
| `no_action` | issue-local な判断で追加対応なし |
| `superseded` | 別 entry に置換 |

completion gate:

- `Status=open` は finish 不可
- `Status=resolved` は `Disposition` 必須
- `Disposition=converted_to_followup` は follow-up 参照必須
- `Disposition=promoted_to_*` は昇格先 artifact と evidence 必須
- `Disposition=deferred` は rationale に revisit 条件必須
- `Disposition=superseded` は置換先 ID 必須

この設計は、追加分析の「open を残さない」原則を維持しつつ、Cluster C の「ledger は行き先を追跡する」という指摘も満たす。

### 補正 5: reviewer severity

reviewer severity は次を採用する。

| Severity | 意味 | Completion gate |
|---|---|---|
| `blocker` | 要件違反、安全性、データ破壊、重大な契約違反 | 完了不可 |
| `major` | acceptance / design contract に影響する実質問題 | 原則完了不可。`promoted_to_*` / `converted_to_followup` には明示判断必須 |
| `minor` | 局所改善、保守性、軽微な仕様曖昧さ | ledger に記録して disposition があれば完了可 |
| `nit` | 表記、整形、任意改善 | 非ブロック。通常 ledger 不要 |

重要なのは、severity と ledger status を混ぜないことである。

reviewer finding は、必要なら decision entry の trigger になる。

### 補正 6: 実装時のテンプレート候補

最終的な `report.md` template は、少なくとも次の section を持つのがよい。

```markdown
## Spec Interpretation / Decision Ledger

No material interpretation changes.

No decision entries.

<!-- Or, when decisions exist: -->

| ID | Status | Type | Raised By | Trigger / Gap | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | interpretation | orchestrator | ... | ... | ... | applied | ... | none |

### Decision Details

#### D-001: short title

- options considered:
- risk if wrong:
- rollback / revisit:

## Proposed Report Entries

<!-- worker-editable -->

## Execution Evidence

## Completion Assessment

## Retrospective
```

`Proposed Report Entries` は常設でなくてもよいが、worker delegation がある issue では有用である。

### 補正 7: 具体化後の残課題

追加分析後も、実装前に最終確認すべき論点は次に絞られる。

1. `Spec Interpretation / Decision Ledger` を単一 section にするか、`Spec Interpretation` と `Decision Ledger` を分けるか
2. `Proposed Report Entries` を report template に常設するか、skill instruction の worker output schema に留めるか
3. `Status=open|resolved|superseded` + `Disposition=...` 方式で確定するか
4. `No material interpretation changes.` / `No decision entries.` を exact phrase として validator 対象にするか
5. `Retrospective` を template に常設するか、必要時 section とするか

現時点の推奨:

- section は `Spec Interpretation / Decision Ledger` の単一 section
- `Proposed Report Entries` は template 常設ではなく、worker output schema に置く
- `Status=open|resolved|superseded` + `Disposition=...` 方式で確定
- 軽量 phrase は exact phrase として固定
- `Retrospective` は template 常設ではなく任意 section。ただし docs / skill で役割を説明する
