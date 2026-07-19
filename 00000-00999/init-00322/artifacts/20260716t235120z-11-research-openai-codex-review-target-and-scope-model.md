---
種別: research
ID: "20260716t235120z-11-research-openai-codex-review-target-and-scope-model"
タイトル: "OpenAI Codex Review Target／Scope Model調査"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t235120z-03-interview-review-protocols-scope-and-perspectives.md"
  - "artifacts/20260716t235120z-08-disc-review-architecture-decision-rationale.md"
  - "artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md"
authority: "synthesized"
derived_from:
  - "source inspection performed during the ChatGPT interview"
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md"
---

# 20260716t235120z-11-research-openai-codex-review-target-and-scope-model OpenAI Codex Review Target／Scope Model調査

## 位置づけ

- このArtifactは、外部仕様・公開実装・現行repositoryの観測事実を、判断根拠として再利用できるよう整理する。
- 事実、推測、未検証事項、用語衝突、edge case、canonical文書への含意を分離する。
- 本文はsource-grounded evidenceであり、accepted ADRまたはcanonical三文書を上書きしない。

## 調査目的

- OpenAI Codexの公開review実装が対象範囲、base branch、commit、custom instruction、supporting contextをどのように定義しているかを把握し、SpecDock Review Scopeへ有効な原則だけを取り入れる。

## sources／調査方法

- 参照先:
  - `openai/codex@800715d201651a2a07c2706dca10400109dae3d3`
  - `codex-rs/exec/src/cli.rs` — `ReviewArgs`
  - `codex-rs/exec/src/lib.rs` — `build_review_request`／`ReviewStart`
  - `codex-rs/prompts/src/review_request.rs` — review prompt生成とmerge-base helper
  - `codex-rs/skills/src/assets/samples/review-agent/SKILL.md`
  - `codex-rs/app-server/src/request_processors/turn_processor.rs`
  - OpenAI Codex code review／GitHub integration公式documentation
- 検証手順:
  - CLIの公開Review targetと相互排他flagを確認した
  - BaseBranch reviewのcomparison refとmerge-base計算を追跡した
  - review-agentがdiff外の周辺code／testsをどの条件で読むか確認した
  - inline／detached reviewのcontext生成差を確認した
  - GitHub hosted Codexの公開情報とOSS範囲を区別した
- 実験条件:
  - 調査時点は2026-07-16
  - OSS repositoryは上記commitを固定点として参照
  - GitHub hosted serviceの非公開server implementationは推測しない

## facts／観測できた事実

- Codex CLIのReview targetは`UncommittedChanges`、`BaseBranch`、`Commit`、`Custom`の4種類である
- `--uncommitted`、`--base`、`--commit`、custom promptは相互排他的である
- BaseBranch reviewはbranch tip同士の単純diffではなく、comparison refとHEADのmerge-baseからHEADまでを対象にする
- comparison refにupstreamがありremote側が進んでいる場合、remote-visible refを優先する実装がある
- review-agentはcomplete diffを読み、各changed pathを理解するための周辺code、tests、call sitesを確認する
- findingは今回の変更で導入されたactionable defectへ限定し、pre-existing unrelated issueやstyle nitを避ける
- Custom instructionは特定file、focus、criteriaを表現するescape hatchとして使える
- Reviewは通常のuser turnと別operationであり、review modelを選べる
- detached reviewはUI上別threadでも、公開code comment上は親historyをforkする場合があるため、UI分離だけではcontext independenceを保証しない

## inference／推測

- 事実から推測したこと:
  - SpecDockも巨大なReview Scope DSLを作らず、Protocolと少数のtemporal selectorで対象を定義するのが妥当
  - PR-style reviewだけmerge-baseを使い、Checkpoint／DeliveryはPlan上の意味的BASE SHAを使うべき
  - Mutation Frontierはreview起点でありhard boundaryではなく、必要なimpact closureへ展開すべき
  - SpecDockの契約reviewではdiffだけでなくHEADの最終状態を評価する必要がある
  - fresh reviewer independenceは別thread名称ではなく、入力contextをfreshに構成することで担保すべき
- 推測の根拠:
  - 上記factsと、Current Effective Decision Snapshotで承認済みのauthority／YAGNI原則を組み合わせた。
  - 推測はexact implementationを固定せず、Epic Planningで再検証する前提である。

## unverified／未検証事項

- まだ確認していないこと:
  - GitHub上のCodex Review serviceが内部で使用する完全なserver-side scope resolution
  - GitHub hosted reviewが将来どのseverityやschemaを返すか
  - SpecDockのChatGPT Connectorでexact SHAをどの程度安定して検証できるか
- 確認できない理由:
  - browser／hosted service／operator environmentに依存する挙動、または実装Epicで初めて作られるsurfaceであるため。
  - 未検証事項を事実としてcanonical文書へ昇格させない。

## question candidates／質問候補

- source-groundedに解けず、人間判断が必要な候補:
  - なし。Reviewの基本方針は承認済み
- pressure-test questionとして切り出すべき候補:
  - exact BASEを復元できない場合に古い安全なBASEへ広げる運用が実コスト上許容できるかはdogfoodで確認
- 質問せずに解決できた候補:
  - Checkpoint／Deliveryでbase branch merge-baseを使う案は不採用
  - pathをhard allow-listにする案は不採用
  - Targeted ReviewをCustom instruction相当のadvisory入口として残す

## terminology conflicts／用語衝突

- `base`:
  - Codex CLIではbase branch
  - SpecDock Checkpoint／Deliveryではimmutable semantic BASE SHA
  - CLIは混同回避のため`--base-sha`を使う
- `review target`:
  - CodexではGit変更の物理target
  - SpecDockではContract Owner、Temporal Window、Structural Anchors、Semantic Expansionを含む
- `detached`:
  - 別thread表示を意味し得るが、fresh contextを自動保証しない

## edge cases／具体シナリオ

- BASE SHAが不明:
  - 狭い推測をせず、Planning baseline等の古い証明可能なBASEへ広げる
- 変更file外に欠陥原因がある:
  - changed pathをseedにcaller／consumer／testへ追跡する
- pre-existing issueが今回のContractを阻害:
  - 無関係な既存問題ではなくContract未達としてfindingにできる
- repository conventionsが存在しない:
  - 多数派styleから規約を捏造せずN/Aとする

## implications／判断への含意

- `requirement.md`:
  - Formal／Targeted Review能力、P0／P1 gate、freshness要件
- `design.md`:
  - Delta-bounded Snapshot Review、semantic BASE、Mutation Frontier、Impact Closure
- `plan.md`:
  - Review Epicとlive smokeを独立化
- `ADR`:
  - Contract-driven Review Protocols

## リスク／制約

- Codex OSSとGitHub hosted serviceを同一実装と誤認しない
- Codex一般code reviewのfinding eligibilityをSpecDock contract reviewへ無批判に流用しない
- merge-baseをすべてのReviewへ適用しない

## 反映先

- reflected_to:
  - initiative/requirement.md
  - initiative/design.md
  - initiative/plan.md
  - artifacts/20260716t123423z-04-adr-contract-driven-review-protocols.md

## 参考

- `openai/codex@800715d201651a2a07c2706dca10400109dae3d3`
- `codex-rs/exec/src/cli.rs` — `ReviewArgs`
- `codex-rs/exec/src/lib.rs` — `build_review_request`／`ReviewStart`
- `codex-rs/prompts/src/review_request.rs` — review prompt生成とmerge-base helper
- `codex-rs/skills/src/assets/samples/review-agent/SKILL.md`
- `codex-rs/app-server/src/request_processors/turn_processor.rs`
- OpenAI Codex code review／GitHub integration公式documentation
