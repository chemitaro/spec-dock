---
種別: artifact
ID: "20260713t012618z"
タイトル: "ChatGPT Raw Integrated PR Repair Workflow Consultation"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
template: "blank"
authority: "raw"
derived_from:
  - "Oracle session: pr-merge-preparer-integrated-repair"
  - "Oracle transcript sha256: 3ac6307f23c073eddb7608ac8878234596a27b0590b4b8003817e12dc96fe7ab"
reflected_to:
  - "20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md"
  - "20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md"
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
---

# 20260713t012618z ChatGPT Raw Integrated PR Repair Workflow Consultation

## 位置づけ
- 用途: 型を先に決めず、scope-local `artifacts/` に作業用 evidence を置く。
- `blank` は template identity であり、filename token ではありません。filename は `<ts>-<slug>.md` / same-second collision は `<ts>-<nn>-<slug>.md` を使い、`blank` を含める必要はありません。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の代替ではありません。採用する内容は canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger へ反映します。

## メモ (必須)
- 以下はChatGPT-Use session `pr-merge-preparer-integrated-repair`が保存したbrowser transcriptの原文である。
- 要約、編集、翻訳、採用判断を加えず取り込んだ。
- Source transcript: `/Users/iwasawayuuta/.oracle/sessions/pr-merge-preparer-integrated-repair/artifacts/transcript.md`
- Source SHA-256: `3ac6307f23c073eddb7608ac8878234596a27b0590b4b8003817e12dc96fe7ab`
- Transcript size at capture: 49,938 bytes / 789 lines
- ChatGPT出力はadvisory evidenceであり、canonical docsへの採用は別途main orchestratorが判断する。

## ChatGPT-Use raw browser transcript

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a5438c3-7664-83e8-b254-51018d11738b

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00313-remove-pr-merge-preparer-repair-attempt-limits
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt as the task brief. Inspect the attached repository sources and Issue evidence, then recommend the future workflow without producing a patch.

## Answer

# 結論

Issue #313 では、**固定回数制限と同一 `root_cause_family` 再出現による即時停止を廃止し、`progress`／`stagnation` に基づく継続判定へ置き換える**べきです。ただし、単なる「無制限再試行」にはせず、各反復について新しい根拠、新しい修復戦略、検証可能な期待差分を repair batch に残せる場合だけ継続します。

将来 workflow の中心は、次の構造を推奨します。

> **current-head review completion → blocking 粗分類 → ChatGPT-Use consultation → runtime repair-batch 生成 → ChatGPT body candidate のローカル採用 → batch 内の統合 repair scope から実装委任 → 検証・commit・push → latest-head re-observation → progress/stagnation 判定**

ChatGPT には **repair-batch ファイル全体ではなく、完全な Markdown body candidate** を作らせます。path、front matter、ID、親 scope、H1 は runtime が生成したものを canonical local identity とし、main orchestrator が body だけを検査・採用します。ChatGPT 出力は終始 advisory evidence であり、authority や採用済み状態を主張できません。

各 blocking family ごとの外部 `disc` 作成は必須から外します。ひとつの repair batch の中に intake、family analysis、cross-family synthesis、repair scope、implementation plan、validation、結果、commit/push、反復履歴を統合します。`research` や `disc` は、別途深掘りが必要な場合の任意 supporting evidence にします。

## リポジトリ確認結果

2026年7月13日に GitHub connector で `chemitaro/spec-dock` を確認しました。指定された current branch `iss-00313-remove-pr-merge-preparer-repair-attempt-limits` は GitHub 上の branch 検索で見つからず、同 ref からの直接ファイル取得も `No commit found for the ref` でした。指示に従い、default branch `main` を確認しています。確認した `main` の先頭は commit `081ba64823f66d4efb051fb88e2a160915efdfa0` です。

GitHub Issue #313 自体は open ですが、Issue 本文はローカル仕様への参照だけで、GitHub comments はありません。したがって、詳細な product-owner proposal と承認済み判断については、添付された Issue artifacts を補助根拠として使用しました。

`main` の provider skill は、現在も P0 一回、同一 P1 family 二回、全体四回という上限と、same-family recurrence の即時 human gate を保持しています。 同時に、各 blocking family に対して外部 `disc` repair unit を必須にしています。

一方、accepted ADR はすでに「stagnation は human gate」「loop count だけで risk acceptance しない」と決定しています。 実際の PR #311 repair batch も第5・第6反復まで、新しい分析と戦略を採用しながら継続しています。しかし、同じ batch の末尾には旧 same-family／loop-limit 停止条件が残っており、実績と規範が矛盾しています。

---

# 1. 推奨 workflow

## 1. PR と source state の preflight

1. PR、base branch、head branch、latest head SHA、open/draft 状態を確認します。
2. ChatGPT が検査する対象は、必ず GitHub に push 済みの PR head とします。
3. ローカルに behavior-affecting な未 push 差分がある場合、その状態を ChatGPT が検査済みとは扱いません。
4. ChatGPT connector が PR head を開けず default branch しか開けない場合、default branch を PR head の代替として使用してはいけません。base comparison には使用できますが、repair consultation は `chatgpt_pr_head_unavailable` gate で停止します。

今回の分析では、ユーザーが明示的に default branch fallback を指定していたため `main` を分析しました。実際の PR repair workflow では、PR head 不在時に default branch を採用することは unsafe です。

## 2. current-head observation と review completion

`wait_pr_observation.sh` を exact head SHA に対して実行します。

review completion artifact が current trigger boundary と expected head SHA に bind されるまで、blocker triage や ChatGPT consultation に進みません。`timeout` や `wait_or_resume` は、それだけで blocker disposition や stagnation を意味しません。accepted ADR も、completion が current trigger/head に bind されていない場合は blocker-centric closure を評価しないと定めています。

required CI がまだ running でも、complete review に明確な P0/P1 blocker があり repair が必要なら consultation を開始できます。ただし、CI は `pending` と明記し、後から判明した CI failure が repair scope を変える場合は同じ batch に追加し、必要に応じて consultant delta analysis を行います。

## 3. deterministic coarse routing

review completion 後、main orchestrator がまず粗い routing を行います。

| 観測状態                                             | 次の処理                                                            |
| ------------------------------------------------ | --------------------------------------------------------------- |
| `merge_prepared_clean`                           | repair batch を作らず terminal report                               |
| 明確な `terminal_non_blocking_only`                 | branch mutation、batch update、push、再 review を行わず terminal report |
| `blocking_repair_required`                       | ChatGPT-Use consultation 必須                                     |
| blocker validity、priority、scope が不明              | ChatGPT-Use consultation 後も不明なら human gate                      |
| stale head、completion unknown、resume metadata 不足 | consultation せず observation gate                                |

ここは product-owner proposal の「review completion 後は常に ChatGPT-Use 必須」という表現と解釈差があります。私の推奨は、**repair／blocking triage が必要な completed observation に限定して必須化**することです。clean または明白な P2/P3-only terminal observation まで外部相談の成否に依存させると、安全性を増やさず、clean PR を外部障害で停止させるためです。最終決定が必要な論点として後述します。

## 4. consultation input manifest の固定

ChatGPT-Use 呼び出し前に、次を一つの input manifest として固定します。

| 項目                      | 必須内容                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| Repository identity     | owner/repo、PR number、base/head branch                            |
| Code identity           | expected head SHA、base SHA または comparison target                 |
| Review identity         | trigger comment ID、created_at、trigger boundary、completion signal |
| Observation evidence    | final JSON の digest、review/comment/thread/body source IDs        |
| CI evidence             | required Actions status、failure names、pending 状態                 |
| Source coverage request | changed files、関連 policy／template／test files                      |
| Scope constraints       | Issue scope、禁止変更、既存 human gates                                  |
| Output contract         | body only、authority claim 禁止、必要 section 一覧                       |

root-cause family は documentation／LLM judgment vocabulary のままとし、observation runtime JSON field や blocker fingerprint にはしません。現 skill もこの区別を明示しています。

## 5. ChatGPT-Use consultation

ChatGPT に要求するのは次の二つです。

1. **Consultation Receipt**

   * 実際に開いた repository、branch、commit SHA
   * 検査した review evidence IDs
   * 検査した source paths
   * 開けなかった source
   * assumptions、uncertainty
   * consultation status

2. **Complete repair-batch body candidate**

   * front matter と H1 を含まない
     -最初の文字列は `##`
   * intake から validation／iteration control まで、required sections を全部含む
   * 実施していない実装、test、commit、push、re-observation を完了済みと書かない
   * canonical adoption、merge-prepared、review pass を自ら宣言しない

ChatGPT の回答は advisory であり、source code と test に照合してから採用するという既存 `chatgpt-use` contract を維持します。

## 6. consultation response の local verification

main orchestrator は次を fail-closed で検査します。

* `inspected_repository` が対象 repo と一致する。
* `inspected_branch` が PR head と一致する。
* `inspected_commit_sha` が expected head SHA と一致する。
* required review sources が coverage receipt に存在する。
* source coverage が不足していない。
* candidate に YAML front matter、H1、別 path、絶対 path、path traversal がない。
* secrets、credential、cookie、production data が含まれない。
* forbidden action を提案または承認していない。
* raw finding が漏れなく disposition されている。
* P2/P3 を reviewer assertion だけで P1 に昇格していない。
* test／commit／push／review 結果の未実施 claim がない。
* requirement、scope、migration、public contract 等の拡張を暗黙に行っていない。

失敗時は candidate を部分採用せず、理由を記録して human gate または recoverable session recovery に進みます。

## 7. runtime repair-batch 生成

blocking batch が必要と確定した後、既存 command で path を生成します。

```bash
./spec-dock/scripts/spec-dock new artifact pr-repair-batch \
  --issue <issue-id> \
  --title "PR Repair Batch"
```

現 runtime は `pr-repair-batch` を direct artifact type として登録し、scope、timestamp、ID、path をローカルで割り当て、artifact template を読み込んで生成します。

writable SpecDock scope がない場合は、同じ body schema を持つ inline batch を使用し、`batch_path: N/A` とします。

## 8. body candidate の採用

runtime-generated file の以下を byte-for-byte で保持します。

* YAML front matter
* generated ID、title、state、parent、authority fields
* generated H1
* generated path

ChatGPT body candidate は一度 repository 外の temporary candidate として保持し、検査後に body 部分だけを採用します。

推奨採用手順は次のとおりです。

1. runtime-generated prefix の SHA-256 を記録する。
2. candidate の SHA-256 を記録する。
3. candidate が `##` で始まり、YAML delimiter と H1 を持たないことを確認する。
4. prefix と candidate body を結合した temporary file を作る。
5. required section、inventory completeness、front matter preservation を検査する。
6. adoption 直前に PR head、observation digest、template hash が変わっていないことを再確認する。
7. atomic replace で generated path に配置する。
8. batch 内の `Consultation / Adoption Record` に candidate digest、consulted head、adoption status、adopter、rejected claims を記録する。

現在の skill-local template も「runtime-generated file が front matter identity と heading を所有し、template は body scaffold のみ」と明示しています。

## 9. local batch acceptance review

repair delegation 前に main orchestrator が batch を acceptance review します。

* 全 blocker inventory が `triaged` である。
* 各 family の validity、need-to-fix、root cause が説明されている。
* coherent repair scope と family の対応が明確である。
* implementation plan が具体的な file／contract／test 単位になっている。
* validation plan が結果を falsify できる。
* scope expansion がない。
* authority／permission／migration gate がない。
* `progress` を期待する根拠が明記されている。

このローカル acceptance が完了するまで、ChatGPT candidate は batch の canonical body ではありません。

## 10. repair delegation

worker は raw review comment ではなく、**accepted repair batch 内の repair scope** を source of truth として作業します。

外部 `disc` は不要です。ただし、次の場合は optional supporting artifact として作成できます。

* 複数の長期設計選択肢を比較する必要がある。
* Issue scope を越える調査が必要である。
* ADR candidate の判定が必要である。
* 人間への独立質問が必要である。

supporting artifact の結論は、自動的に batch authority になりません。main orchestrator が採用した箇所と理由を batch に反映します。

## 11. implementation、validation、commit、push

worker の結果を main orchestrator が検証し、batch に次を反映します。

* changed files
* implementation result
* local test result
* failed／skipped gate
* residual risk
* actual commit SHA
* actual pushed head SHA

batch への予定記載と実績記載を混同してはいけません。ChatGPT が生成した予定欄を、実行せずに `passed` に更新してはいけません。

code repair と batch 更新を同じ repair commit に含め、batch だけの record-only push は避けます。

## 12. latest-head re-observation

push 後は新しい head SHA を取得し、必ず latest head を再観測します。

blocking finding が残った場合は、同じ batch を継続使用します。前回 re-observation、new findings、strategy delta、progress decision を次の repair commit に含めます。

final observation が clean または P2/P3-only で、追加 code repair が不要な場合は、**batch を更新するためだけの commit を作りません**。terminal re-observation evidence は final merge-prepared report に記録します。これにより、final evidence を記録するための新 head／新 CI／新 review という無限連鎖を防ぎます。

## 13. terminal decision

`merge-prepared: yes` は、既存 blocker-centric predicate を全て満たした場合だけです。latest-head observation、required CI、P0/P1 zero、merge conflict zero、untriaged zero、needs-human zero、全 repair scope 完了が必要です。`review-clean` と `merge-prepared` は引き続き分離します。

stagnation または human gate で停止する場合は、必ず次を報告します。

* `merge-prepared: no`
* unresolved blocker
* last known head SHA
* attempted strategies
* stagnation／gate evidence
* human decision が必要な理由
* safe next action

loop count 到達を risk acceptance として unresolved blocker を黙認することはありません。

---

# 2. ChatGPT file-generation / adoption contract

## 推奨判断

**「analysis だけ」でも「complete file」でもなく、complete body candidate を返させる hybrid** を採用します。

| 案                                                                                       | 判断 |
| --------------------------------------------------------------------------------------- | -- |
| ChatGPT が front matter 込みの完全ファイルを生成して target path に配置                                   | 棄却 |
| ChatGPT は自由形式 analysis だけを返し、orchestrator が全文を書き直す                                      | 棄却 |
| ChatGPT が schema-complete な Markdown body candidate を返し、orchestrator が runtime file に採用 | 採用 |

自由形式 analysis だけでは、finding の転記漏れや分析と plan の不整合が起きやすくなります。完全ファイル生成では、runtime-owned identity、scope、authority、path を上書きする危険があります。body candidate なら、内容の統合性と local authority を両立できます。

## Required candidate envelope

ChatGPT response は概念上、次の二部構成にします。

```text
CONSULTATION RECEIPT
- repository
- head branch
- inspected commit SHA
- PR / observation identity
- inspected sources
- missing sources
- assumptions
- status

BATCH BODY CANDIDATE
## Batch Control
...
```

candidate 内には次の provenance を含めます。

* `consultation_id`
* `consulted_repository`
* `consulted_head_branch`
* `consulted_head_sha`
* `observation_digest`
* `review_evidence_ids`
* `source_coverage_status`
* `candidate_sha256`
* `adoption_status: pending | adopted | rejected | stale`
* `local_adoption_rationale`

## Unsafe candidate conditions

以下のいずれかがあれば、body 全体を reject します。

* front matter または H1 が含まれる。
* runtime-generated path 以外への書き込みを要求する。
* repository／branch／head SHA が一致しない。
* required source coverage が不明または欠落する。
* review finding が inventory から欠落する。
* canonical authority、review pass、merge readiness を ChatGPT が宣言する。
* auto-merge、thread resolve、review dismiss、issue close 等を含む。
* secret、credential、private data が含まれる。
* scope expansion や migration を当然の前提にする。
* 実行していない test、commit、push を実績として記載する。

---

# 3. Repair-batch information architecture

## Required top-level sections

| Section                                  | 目的                                               |
| ---------------------------------------- | ------------------------------------------------ |
| `PR / Batch Control`                     | PR、base/head、latest SHA、batch status             |
| `Review Completion / Trigger Boundary`   | completion signal、trigger ID、resume metadata     |
| `ChatGPT Consultation / Adoption Record` | source coverage、candidate digest、採否              |
| `Observation Snapshot Ledger`            | head ごとの observation を append-only で記録           |
| `Raw Intake Inventory`                   | review、CI、merge blocker、limitation の原文 evidence  |
| `Concern Family Catalog`                 | family、priority、invariant、disposition            |
| `Cross-Family Synthesis`                 | shared cause、dependency、repair ordering          |
| `Integrated Repair Scope Registry`       | 一つ以上の coherent repair scope                      |
| `Per-Family Analysis`                    | validity、root cause、options、family disposition   |
| `Per-Scope Design and Plan`              | design、implementation、validation、results         |
| `Validation Gate Matrix`                 | commands、expected／actual results、coverage        |
| `Iteration / Progress Ledger`            | strategy delta と progress/stagnation             |
| `Supporting Evidence Register`           | optional research／disc／interview の採用記録           |
| `Non-Blocking Follow-up Register`        | P2/P3 と residual risk                            |
| `Human Gates / Waivers`                  | unresolved authority、external、consultation gates |
| `Merge-Prepared Evidence Boundary`       | terminal predicate と final-report handoff        |

## Per-family structure

各 `FXXX` subsection には最低限、次を持たせます。

```text
### FXXX <root_cause_family>

- Related inventory IDs
- Reported priorities
- Decided priority
- Merge-blocking
- Protected domain
- Contract / invariant
- Validity analysis
- Need-to-fix decision
- Root cause
- Why these items form one family
- Relationship to prior families / findings
- Options considered
- Recommended disposition
- Covered repair scope IDs
- Validation obligations
- Out of scope
- Residual risk
- Current status
```

`root_cause_family` は grouping vocabulary であり、stagnation を自動判定する fingerprint にはしません。

## Integrated repair scope structure

family と repair scope は一対一に固定しません。

* 一つの repair scope が複数の関連 family を修復できる。
* 一つの family が複数の独立 scope を必要とすることもある。
* rollback boundary、implementation owner、validation surface が異なる場合は scope を分ける。

各 `SXXX` は次を持ちます。

```text
### SXXX <repair scope title>

- Covered families
- Covered inventory IDs
- Strategy ID / version
- Prior strategy
- Material strategy delta
- Causal hypothesis
- Expected observable delta
- Recommended design
- Implementation plan
- Validation plan
- Rollback boundary
- Dependencies / ordering
- Out of scope
- Delegated worker
- Implementation result
- Local validation result
- Commit / push evidence
- Re-observation result
- Progress decision
- Residual risk
- Status
```

これにより、現在の外部 `disc` に分散している Validity Analysis、Root Cause、Options、Recommended Design、Implementation Plan、Validation Plan、Result、Commit Evidence、Re-observation Result を batch 内に統合できます。現行 template は、これらを外部 repair unit に必須化しています。

---

# 4. `progress` と `stagnation` の operational contract

## Continuation eligibility

次のすべてが成立する場合だけ、自律 repair を継続します。

```text
continuation_eligible =
    evidence_is_current
    AND review_is_complete_for_expected_head
    AND source_coverage_is_complete
    AND unresolved_blocker_exists
    AND blocker_is_within_approved_scope
    AND no_existing_human_gate
    AND materially_new_strategy_exists
    AND strategy_has_falsifiable_validation
    AND expected_observable_delta_is_defined
```

「新しい strategy」は、名称だけ変えた同一 patch ではありません。少なくとも次のどれかが変わる必要があります。

* causal hypothesis
* protected invariant
* implementation mechanism
* input／state-machine boundary
* algorithm／data flow
* validation method
* prior repair が閉じなかった具体的 edge case

## Observed progress

反復後、次の少なくとも一つを current evidence で示せる場合に `progress: yes` とします。

1. 前回の blocker signature が fresh observation で消滅した。
2. deterministic failing test／check が pass になった。
3. failing cases または affected surface が厳密に縮小した。
4. 前回の修復で一つの境界が閉じ、fresh review が同 family の別境界を新たに示した。
5. 新しい reproduction／source evidence により causal model が具体化し、前回と異なる falsifiable strategy が成立した。
6. `unknown`／`pending` evidence が verified actionable state に変わった。

blocker count が必ず減る必要はありません。前回 blocker の closure 後に、fresh review が別の P1 edge case を発見することがあります。その場合、closure evidence と新しい failure signature が分離されていれば progress です。

## Stagnation

次のいずれかが成立した時点で、回数に関係なく `stagnation` human gate とします。

```text
stagnation =
    no_in_scope_strategy_remains
    OR (
        equivalent_strategy_is_proposed
        AND no_material_new_evidence_exists
    )
    OR validation_cannot_distinguish_success_from_failure
    OR same_failure_reproduction_persists_without_new_causal_model
    OR repair_oscillates_between_prior_states_without_new_evidence
    OR claimed_progress_is_contradicted_by_current_evidence
```

一度目の反復でも、同じ patch、同じ reproduction、同じ根拠しかないなら stagnation です。逆に、十回目でも新しい evidence、strategy、検証可能な進展があれば、回数だけを理由に停止しません。

## Decision table

| 状況                                                                 | 判定                 | 動作                       |
| ------------------------------------------------------------------ | ------------------ | ------------------------ |
| same family、別 edge case、新 causal model、新 strategy                  | progress candidate | 継続                       |
| same family、同じ reproduction、同等 patch、追加 evidence なし                | stagnation         | human gate               |
| prior blocker は closure、fresh review が同 family の別境界を発見             | progress           | 継続                       |
| 新 family、scope 内、falsifiable strategy あり                           | progress candidate | 継続                       |
| local tests pass だが fresh review が同じ failure signature を再現し、説明更新なし | stagnation         | human gate               |
| blocker は残るが deterministic failure set が縮小し、次 strategy が異なる        | progress           | 継続                       |
| source coverage、head、review evidence が stale                       | progress 判定不能      | evidence human gate      |
| blocker zero、required CI clear、latest-head evidence complete       | terminal           | merge-prepared 判定        |
| unresolved blocker があるが iteration count 上限に達した                     | 上限自体は無意味           | progress/stagnation で再判定 |

## Iteration ledger fields

現在の ledger fields に、少なくとも次を追加します。

```text
iteration_index
observation_id
observed_head_sha
blocker_signatures
family_ids
strategy_id
prior_strategy_id
strategy_delta
new_evidence
expected_observable_delta
validation_plan
implementation_commit
local_gate_delta
reobserved_head_sha
blocker_set_delta
progress_decision
progress_rationale
stagnation_reason
next_action
```

`iteration_index` と同一 family 出現回数は telemetry／監査情報であり、停止 predicate ではありません。

---

# 5. Human gates

## 変更せず維持する既存 gates

| Gate category      | 維持する条件                                                                        |
| ------------------ | ----------------------------------------------------------------------------- |
| Authority / scope  | permission・auth、requirement expansion、scope expansion、ambiguous review intent |
| High-impact change | breaking change、migration、secret、deployment setting、public contract 変更で未承認のもの |
| Branch / base      | base branch conflict、PR base conflict、visible merge conflict が自動解消不能          |
| External           | external／flaky dependency で外部または人間作業が必要                                       |
| Observation        | stale head、review completion unknown、resume metadata 不足、trigger boundary 超過   |
| Trigger            | 新 review trigger が必要だが未承認                                                     |
| Unknown            | consultation とローカル確認後も validity、priority、repair scope が不明                     |
| Platform           | branch protection が unresolved conversation resolution を要求                    |
| External CI        | required non-Actions check を確認できない                                            |
| Batch              | blocking inventory が untriaged、unresolved `needs-human`、repair scope 不完全      |
| Stagnation         | 新 evidence／strategy／検証可能な前進がない                                                |

timeout については、resume metadata があり recoverable なら `wait_or_resume` とします。timeout 回数だけで human gate にしません。

## 維持する forbidden actions

次は引き続き実行も許可もしません。

* PR merge／auto-merge
* branch deletion
* Issue close／Issue finish
* review reply
* thread resolution
* review dismissal
* admin override
* permission／auth 変更
* secret／deployment mutation
* scope expansion

現 skill の forbidden write contract もこれらを禁止しています。

## 新しい ChatGPT／adoption gates

| Reason code                              | 条件                                                   | 推奨動作                                  |
| ---------------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| `chatgpt_pr_head_unavailable`            | connector が exact PR head を開けない                      | default branch で代用せず human gate       |
| `chatgpt_repository_access_failed`       | connector／app／repository が利用不能                       | browser recovery 後も不可なら human gate    |
| `chatgpt_source_coverage_incomplete`     | changed source、review body、comments、threads 等が不足     | repair delegation 禁止                  |
| `chatgpt_candidate_stale`                | head、observation、template、source manifest が変化        | candidate reject、fresh consultation   |
| `chatgpt_candidate_unsafe`               | front matter、H1、path mutation、secret、forbidden claim | candidate 全体を reject                  |
| `chatgpt_output_incomplete`              | browser capture／download が不完全                        | session recovery、hard failure なら gate |
| `runtime_batch_adoption_conflict`        | generated prefix／path／identity が adoption 前に変化       | adoption 中止、local state review        |
| `consultation_requirement_waiver_needed` | mandatory consultation を手動 fallback したい              | human explicit approval が必要           |

recoverable browser failure では、同じ prompt を無条件に再実行せず、既存 session の status／render／recovery を先に試すという `chatgpt-use` guidance を維持します。

私の推奨 fallback は、**hard-unrecoverable failure では fail-closed が default、local/manual authoring は人間がその invocation に限って明示承認した場合だけ許可**です。silent automatic fallback は「mandatory consultation」を実質的に任意へ変えてしまいます。

---

# 6. Exact change inventory

## 必須変更

| Path                                                                                                     | 変更内容                                                                                                               |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`                     | provider authority。workflow、repair unit policy、progress/stagnation、ChatGPT adoption、human gates、response checklist |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml`           | “bounded fixes” を progress-based repair wording に変更                                                                |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` | body-only integrated batch scaffold、consultation record、repair scopes、iteration ledger                             |
| `.agents/skills/github-pr-merge-preparer/SKILL.md`                                                       | dogfooding mirror                                                                                                  |
| `.agents/skills/github-pr-merge-preparer/agents/openai.yaml`                                             | dogfooding mirror                                                                                                  |
| `.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`                                   | dogfooding mirror                                                                                                  |
| `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md`                                  | installed runtime artifact-template source                                                                         |
| `spec-dock/templates/artifacts/pr-repair-batch.md`                                                       | dogfooding/runtime verification copy                                                                               |

`openai.yaml` も現在 provider／mirror の双方で “bounded fixes” を明示しているため、SKILL.md だけの変更では契約が矛盾します。

## Compatibility surface として同時変更を推奨

| Path                                                                      | 理由                                                         |
| ------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md` | 旧 discussion route に同じ loop-limit／repair-unit contract が残る |
| `spec-dock/templates/discussions/pr-repair-batch.md`                      | working／dogfood copy                                       |

四つの runtime template copies に旧 loop-limit 文言が残っていることが repository search で確認できます。

これらを今回変更しない場合は、「discussion route は deprecated であり新規生成には使用しない」という明示的な compatibility decision が必要です。削除や migration は今回の許可範囲外なので、**現時点では四 copies を同じ body contract に揃える**のが安全です。

## 原則として変更不要な runtime code

次の runtime code は、すでに `pr-repair-batch` artifact type、template selection、runtime identity/path generation を実装しています。

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`

専用 body-adoption helper を新設しない限り、Issue #313 でこれらの behavior change は不要です。

## Canonical Issue docs

current branch が GitHub 上に存在しないため、Issue #313 の canonical `requirement.md`、`design.md`、`plan.md`、`report.md` の GitHub path と現在内容は確認不能です。ローカル branch では次を反映すべきです。

* requirement: fixed count 不使用、progress/stagnation acceptance criteria
* design: consultation trust boundary、body-only adoption、integrated batch authority
* plan: provider-first、all mirrors/templates、tests、manual scenarios
* report: attached research/interview/proposal と ChatGPT consultation の EAL 採用判断

accepted blocker-centric ADR は retry-count 廃止をすでに支えています。そのため、回数上限撤廃だけの新 ADR は不要です。ただし、**ChatGPT consultation を mandatory external gate とし、repair batch を primary authority surface にする判断**は、長期的かつ意外性のある trust-boundary decision なので、ADR amendment または新 ADR candidate にする価値があります。

## 変更しない historical evidence

過去の repair batch、過去 Issue design、過去 PR evidence に残る旧 loop-limit 文言は historical record です。repository 全体への機械的置換は行いません。

negative text scan は、provider、current mirrors、current templates、current Issue canonical docs に限定します。

---

# 7. Verification plan

## Static verification

| Check                                                   | Expected result                                                                             |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| provider skill と `.agents` mirror の `cmp`               | exact match                                                                                 |
| provider `openai.yaml` と mirror の `cmp`                 | exact match                                                                                 |
| provider skill-local template と mirror の `cmp`          | exact match                                                                                 |
| runtime artifact-template source と working copy の `cmp` | exact match                                                                                 |
| discussion-template source と working copy の `cmp`       | exact match                                                                                 |
| normative files に対する old wording scan                   | fixed counts、same-family immediate stop、mandatory `repair_unit_disc`、`bounded fixes` がゼロ    |
| new wording scan                                        | consultation、source coverage、strategy delta、progress、stagnation、integrated repair scope が存在 |
| front matter／H1 template check                          | runtime placeholders を維持                                                                    |

## Focused regression tests

既存 runtime tests は artifact type と template generation surface を扱っています。`pr-repair-batch` は runtime artifact type と、旧 discussion doc type の parity test に含まれています。

少なくとも次を実行・追加対象にします。

```text
uv run pytest tests/cli_runtime/test_new.py
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py
uv run pytest tests/cli_runtime/test_wrappers.py
```

追加すべき assertion は次です。

* `new artifact pr-repair-batch` が runtime-owned ID、front matter、H1 を生成する。
* required integrated sections が生成される。
* old `repair_unit_disc`、fixed loop limits が生成されない。
* provider／working runtime template が一致する。
* install/update 後の managed skill が provider と一致する。
* body-only candidate を採用する manual contract で prefix が不変である。

## Repository gates

PR #311 の実績では、focused tests だけでなく full provider suite、static analysis、provider/dogfood comparison、SpecDock validate が使用され、最終的には CI-equivalent `make lint` を実行しなかったことが追加 CI failure の原因になりました。

したがって最終 gate は次を推奨します。

```text
make lint
uv run pytest
./spec-dock/scripts/spec-dock validate
provider/dogfooding exact comparison
```

実際の repository command contract が `make lint` と `./scripts/static_analysis/run.sh` のどちらを CI source of truth とするかは、実装時に current workflow から再確認します。

## Manual scenario matrix

| Scenario                                | Expected                                              |
| --------------------------------------- | ----------------------------------------------------- |
| P1 初回 observation                       | consultation → runtime batch → body adoption → repair |
| same family、別 edge case、新 strategy      | 自律継続                                                  |
| same family、同じ reproduction、同じ strategy | stagnation human gate                                 |
| different family、scope 内                | batch に追加して継続                                         |
| ChatGPT が default branch だけを検査          | candidate reject                                      |
| consultation 後に head が変化                | stale reject、fresh consultation                       |
| candidate が front matter／H1 を含む         | unsafe reject                                         |
| source coverage が review body を欠く       | incomplete coverage gate                              |
| hard browser failure                    | recovery 後、human gate                                 |
| final P2/P3-only                        | batch-only commit、push、review trigger を行わない           |
| unresolved P1 のまま停止                     | `merge-prepared: no`                                  |
| optional `disc` 使用                      | batch に採用 rationale を記録し、batch が source of truth のまま  |

---

# 8. 根拠

1. 現 provider skill と template は、固定数値、same-family immediate stop、外部 `disc` repair unit を重複して要求しています。
2. accepted ADR は、blocker zero を merge gate とし、stagnation は human gate、loop count 単独による risk acceptance は禁止しています。
3. PR #311 の実運用では、複数反復にわたり新しい consultant analysis と修復戦略が採用され、固定上限を越えて repair が継続されています。
4. runtime はすでに repair-batch の local identity と path を安全に生成するため、ChatGPT に file identity を持たせる必要はありません。
5. 添付された user-approved interview は、fixed counts と same-family immediate stop を廃止し、progress-based continuation と stagnation gate を採用しています。
6. raw product-owner proposal は、ChatGPT-Use、current pushed code、review evidence、integrated repair batch を中心にする方向を提示しています。

---

# 9. 仮定

* `chatgpt-use` は repository 内の managed skill ではなく、Codex 実行環境側の external skill として利用される前提です。GitHub repository 内では、その exact skill definition は確認できませんでした。
* repair-batch adoption は当面 workflow contract として実施し、専用 atomic-adoption script は Issue #313 の必須範囲にしない前提です。
* `root_cause_family` は Markdown documentation vocabulary のままで、observation JSON schema や parser contract を変更しない前提です。
* final terminal observation を branch 上の batch に反映するためだけの record-only commit は作らない前提です。
* existing blocker-centric merge-prepared predicate、P2/P3 terminal policy、forbidden writes は変更しない前提です。

---

# 10. リスクと対策

| リスク                                      | 対策                                                                       |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| `materially new strategy` が主観的になる        | strategy ID、prior strategy、material delta、expected observable delta を必須化 |
| ChatGPT が source を見たと誤認する                | consultation receipt と exact head SHA coverage を必須化                      |
| batch が肥大化する                             | current summary と append-only ledger を分離し、深掘りは optional artifact         |
| ChatGPT failure が clean PR まで止める         | mandatory scope を blocking／uncertain に限定する推奨                             |
| unsafe generated file が identity を上書きする  | body-only、temporary staging、prefix hash、atomic adoption                  |
| 同じ family 名だけで誤停止する                      | family ではなく evidence／strategy／failure signature を評価                      |
| blocker count が減らないと全て stagnation 扱いになる  | prior boundary closure と fresh edge-case discovery を progress と認める       |
| local tests pass を progress と誤認する        | fresh latest-head observation を最終 evidence とする                           |
| terminal batch update が新 review loop を作る | terminal evidence を final report に置き、record-only push を禁止                |

---

# 11. 棄却案

1. **固定回数だけ削除し same-family stop を残す**
   夜間停止問題が一回目の recurrence で再発するため棄却します。

2. **固定回数も stagnation もなく完全無制限にする**
   同じ patch、test、review を反復する危険があるため棄却します。

3. **ChatGPT に runtime path の complete file を直接書かせる**
   front matter、ID、scope、authority、path の local ownership を破るため棄却します。

4. **ChatGPT は自由形式 analysis だけを返す**
   orchestrator による再記述時の finding 漏れ、plan drift、provenance loss が大きいため棄却します。

5. **blocking family ごとの `disc` を引き続き必須にする**
   batch と unit の authority が分散し、実運用でも大量の unit files と重複更新を生んでいるため棄却します。PR #311 では U001–U011 が個別 `disc` を参照しています。

6. **`root_cause_family` を機械的 blocker fingerprint にする**
   family は grouping judgment であり、同じ family 内の別 boundary を区別できないため棄却します。

7. **ChatGPT failure 時に自動で local authoring へ fallback する**
   mandatory consultation と source coverage gate を無効化するため棄却します。

---

# 12. Product-owner interview candidates

## 1位: mandatory ChatGPT consultation の適用範囲

**質問:** completed review の全てについて ChatGPT-Use を必須にするか、`blocking_repair_required` または blocker disposition が不明な場合だけ必須にするか。

**推奨回答:** blocking／uncertain のみ必須。`merge_prepared_clean` と明白な terminal P2/P3-only は consultation を省略する。

**設計への影響:** clean PR が ChatGPT/browser outage で停止するかどうか、コスト、terminal path の sequence が変わります。

## 2位: hard-unrecoverable ChatGPT failure の fallback authority

**質問:** browser／connector recovery 後も consultation 不可の場合、必ず human gate とするか、human が invocation ごとに local/manual batch authoring を承認できるか。

**推奨回答:** default は fail-closed human gate。人間の明示承認がある一回限りの manual fallback は許可し、batch に waiver と不足した evidence を記録する。

**設計への影響:** night-run availability と mandatory external gate の強度が変わります。

## 3位: legacy discussion repair-batch templates の lifecycle

**質問:** `templates/discussions/pr-repair-batch.md` を現行 compatibility surface として更新するか、deprecated として別 Issue で廃止するか。

**推奨回答:** Issue #313 では artifact template と同じ body contract に更新する。deprecation／removal は別 Issue で行う。

**設計への影響:** template copies の変更範囲、static parity test、migration requirement が変わります。

---

# 13. 不確実性・未検証主張

* 指定 current branch は GitHub connector から開けなかったため、その branch に存在する可能性がある未 push／未公開の canonical docs、code、tests は確認していません。
* 本回答は `main` commit `081ba648…` と添付された Issue evidence に基づく暫定設計提案です。Codex 側で current branch が利用可能になった時点の独立検証が必要です。
* GitHub Issue #313 の substantive design は GitHub 本文では確認できず、添付 artifacts に依存しています。
* `chatgpt-use` browser／connector failure recovery を、この回答作成中に実際に実行・検証したわけではありません。
* repository の test、lint、validate は実行していません。verification plan は source と過去の PR evidence から提案したものです。
* 専用 body-adoption helper を新設せず、workflow instruction だけで十分かどうかは、実装時の manual smoke で再評価が必要です。

タスク brief と要求された制約は添付 prompt を基準にしました。
別添の例外階層／`FailureResult` 設計メモは Issue #313 と無関係なので、本回答の根拠には採用していません。
