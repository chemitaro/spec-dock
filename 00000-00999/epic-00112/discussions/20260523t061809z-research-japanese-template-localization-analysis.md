---
種別: research
ID: "research-20260523-japanese-template-localization"
タイトル: "日本語話者向けテンプレート表現の現状分析"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112"]
関連: []
authority: "synthesized"
derived_from:
  - "src/spec_dock/assets/spec_dock/templates/**"
  - "src/spec_dock/assets/spec_dock/system/active-none/**"
  - "spec-dock/templates/**"
  - "spec-dock/system/active-none/**"
  - "repo-analyst sub-agent result 2026-05-23"
  - "consultant sub-agent result 2026-05-23"
reflected_to: []
---

# research-20260523-japanese-template-localization 日本語話者向けテンプレート表現の現状分析

## 位置づけ
- 用途: `spec-dock` のテンプレートと placeholder 文書が、日本語話者のユーザーに「日本語で書く文書」として自然に見えるかを調査し、後続の要件定義・設計・実装計画へ渡す。
- authority: `synthesized`。この文書は実装方針を確定する ADR ではなく、現状事実、問題分類、修正方針案、リスクを整理する研究証跡である。
- 対象: `requirement.md`、`design.md`、`plan.md`、`report.md` の initiative / epic / issue テンプレート、discussion テンプレート、`system/active-none` placeholder、関連テスト。
- 非対象: この文書ではテンプレート本体の修正は行わない。後続 Issue で provider 側を正本として編集し、dogfooding mirror とテストを更新する。

## 調査目的 (必須)
- 日本語話者が見るテンプレートに英語前提の表現がどこに残っているかを特定する。
- 英語をすべて排除するのではなく、機械的契約・既存 workflow・エージェント契約を壊さずに日本語化すべき境界を整理する。
- 後続実装で触るべき正本、mirror、テスト、レビュー観点を明確にする。

## 調査方法 (必須)
- `rg --files` と `find` で provider 側と dogfooding 側のテンプレート配置を確認した。
- `rg` と `sed` で、英語見出し、英語 placeholder、英語 table header、schema 的な値、テスト期待文字列を抽出した。
- `repo-analyst` sub-agent に、生成経路、provider / consumer 正本関係、影響テスト、整合リスクを読み取り専用で調査させた。
- `consultant` sub-agent に、日本語テンプレートとして自然な見出し・用語・placeholder 方針、翻訳すべき語と残すべき語の整理を依頼した。

## 調査結果 (必須)

### 1. 正本と mirror の関係
- provider 正本は `src/spec_dock/assets/spec_dock/templates/**` と `src/spec_dock/assets/spec_dock/system/active-none/**` である。
- dogfooding mirror は `spec-dock/templates/**` と `spec-dock/system/active-none/**` であり、現時点で provider 側と対応する。
- installer は `docs`、`templates`、`scripts`、`system` を managed directory として provider assets から target の `spec-dock/` へ同期する。
- node 作成時は `template_scaffolder.copy_scaffolded_tree()` がテンプレートを読み、placeholder を置換して `requirement.md` / `design.md` / `plan.md` / `report.md` を生成する。
- したがって後続修正では、provider 側を先に編集し、dogfooding mirror を同期または同等内容へ更新し、mirror parity test を通す必要がある。

### 2. 全体傾向
- `requirement.md` と `design.md` の多くはすでに日本語ベースだが、見出しの括弧内や専門セクションに `WHAT / WHY`、`HOW`、`Outcome`、`Why now`、`Diagram` などが残る。
- `issue/plan.md` と `issue/report.md` は、直近の agentic workflow / delegated authoring 契約により英語ラベルが多く、最も「英語で書く前提」に見えやすい。
- `initiative/report.md` と `epic/report.md` の `Delegated Draft Evidence` は、表ヘッダ、failure mode、status 値、説明文の大半が英語で、ユーザー可読文書としては日本語化余地が大きい。
- `system/active-none/**/report.md` は active 未設定時の placeholder だが、`Delegated Draft Evidence Schema (reference)` と failure-mode table が英語中心で、fallback 表示としても英語前提に見える。
- discussion テンプレートは概ね日本語化済みだが、`adr.md` は ADR の標準用語として `Decision`、`Context`、`Options considered`、`Rationale`、`Consequences`、`References` を併記している。

### 3. 主要な問題箇所

| 領域 | 代表ファイル | 問題の種類 | 影響 |
|---|---|---|---|
| initiative requirement | `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` | `WHAT / WHY`、`Outcome`、`Why now` | 日本語の要件定義書でありながら英語フレームを前提に見せる |
| epic requirement | `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | `WHAT / WHY`、`Initiative`、`Epic` | 階層名と説明語の使い分けが曖昧 |
| issue requirement | `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` | `WHAT / WHY`、`UI`、`HTTP`、`DB`、`AC`、`EC` | 技術略語は自然だが、文書の主語は日本語化できる |
| initiative / epic design | `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/design.md` | `HOW / Guardrails`、`Component / Module View`、`Package Dependency`、`Domain Model` | 設計書の章立てが英語の設計テンプレートに見える |
| issue design | `src/spec_dock/assets/spec_dock/templates/issue/design.md` | `Module Dependency Diagram`、`Local Diagram Delta`、`Sequence Delta`、`Domain Model Delta`、`verification mapping` | 図・差分・検証の語彙が英語中心で、記入言語が揺れやすい |
| initiative / epic plan | `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/plan.md` | `Roadmap / Epics`、`Issues / Order`、`docs impact` | 計画書の基本見出しは日本語だが、重要概念が英語で残る |
| issue plan | `src/spec_dock/assets/spec_dock/templates/issue/plan.md` | `Execution Contract`、`Spec-Locked Closure Index`、`behavior goal`、`delegation contract`、`step gate`、`final quality gate` | 実装者が英語 table / label を埋める前提に見える。agent contract との互換性リスクも高い |
| initiative / epic report | `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/report.md` | `Delegated Draft Evidence`、failure-mode table、`Success metrics`、`Lessons learned` | レポートの主要証跡が英語で、ユーザー向け報告書として読みにくい |
| issue report | `src/spec_dock/assets/spec_dock/templates/issue/report.md` | `Observed Evidence Ledger`、`Spec Interpretation / Decision Ledger`、`Disposition`、`Red/Green/Refactor Evidence`、`Final Quality Gate` | 最も英語依存が強く、実装ログ・判断記録・レビュー証跡の記入言語を英語へ誘導する |
| active-none report | `src/spec_dock/assets/spec_dock/system/active-none/**/report.md` | schema reference と failure-mode table が英語 | active 未設定時の fallback でも英語前提が露出する |

### 4. 日本語化の基本方針
- ユーザーが読む見出し、説明文、placeholder、table header は日本語を主にする。
- 初出の専門概念は「日本語名（英語名）」にし、以後は日本語名へ寄せる。
- `API`、`CLI`、`PR`、`CI`、`GitHub`、`HTTP`、`DB`、`UML`、`ADR`、`AC`、`EC` など、日本語技術文書で自然に使う略語は残してよい。
- `status`、`id`、`depends_on`、`review_status: pass`、lifecycle state、disposition 値など、workflow やエージェント契約で値として使われる可能性がある語は、値そのものを翻訳せず、日本語説明を添える方が安全である。
- `受け入れ条件` と `完了条件` は分ける。前者は仕様・利用者観点、後者は作業終了の運用条件である。
- `report.md` は作業 transcript ではなく、判断・検証・レビュー・commit / no-op の証跡台帳として扱う。

### 5. 具体的な表現方針案

| 現状表現 | 推奨表現 | 補足 |
|---|---|---|
| `要件定義（WHAT / WHY）` | `要件定義（何を、なぜ行うか）` | 英語併記を外しても意味は保てる |
| `設計（HOW / Guardrails）` | `設計（どう実現し、何を守るか）` | guardrail は本文では「ガードレール」として残してよい |
| `実装計画（Execution Contract）` | `実装計画（実行契約）` | 初出で `Execution Contract` を補足するなら括弧内に併記 |
| `Observed Evidence Ledger` | `観測証跡台帳` | report の性格を日本語で明示する |
| `Spec Interpretation / Decision Ledger` | `仕様解釈・判断台帳` | 値の `Status` / `Disposition` は維持しつつ表ヘッダを日本語化する余地あり |
| `Delegated Draft Evidence` | `委任ドラフト証跡` | delegated authoring の policy 用語として日本語主語化する |
| `Delegated Draft Failure Modes` | `委任ドラフトの失敗モード` | failure mode の値は英語維持または日本語説明併記 |
| `Spec-Locked Closure Index` | `仕様固定クロージャ索引` | 既に日本語併記があるため日本語を主見出しへ昇格できる |
| `delegation contract` | `委任契約` | sub-agent への入力・出力・制約の契約という意味を保持 |
| `step closure contract` | `ステップ完了契約` | closure id の値は維持 |
| `step gate` | `ステップゲート` | reviewer gate / commit gate は日本語説明を添える |
| `Final Quality Gate` | `最終品質ゲート` | QA / code-reviewer / spec-reviewer は role 名として残す |
| `docs impact resolution / docs refresh` | `ドキュメント影響の解消 / 更新` | `docs impact` は workflow docs とも同期が必要 |
| `Success metrics` | `成功指標` | requirement 側と語彙を揃える |
| `Lessons learned` | `学び` | 既に一部日本語があるため括弧英語を外せる |

### 6. 文書別の推奨構造

#### requirement.md
- 主語は「何を、なぜ必要とするか」に置く。
- 推奨見出し:
  - `目的`
  - `背景と課題`
  - `対象ユーザー / 利用シナリオ`
  - `スコープ`
  - `対象外`
  - `制約・前提`
  - `受け入れ条件`
  - `例外・エッジケース`
  - `用語`
  - `未確定事項`
- `AC` / `EC` の識別子は維持する。説明欄は日本語にする。

#### design.md
- 主語は「どう実現し、どの境界と依存を守るか」に置く。
- 推奨見出し:
  - `設計方針`
  - `全体像`
  - `依存関係と実装順序`
  - `図解`
  - `インターフェース契約`
  - `データ / ドメインモデル差分`
  - `ディレクトリ / ファイル変更計画`
  - `要件 -> 設計マッピング`
  - `テスト方針`
  - `リスク / 移行 / ロールバック`
- `UML`、`API`、`module`、`class`、`function`、`file` は技術語として残してよいが、説明文は日本語化する。

#### plan.md
- 主語は「実装者や sub-agent が上から順に実行できる計画」に置く。
- 推奨見出し:
  - `この計画で満たす要件ID`
  - `依存関係から導く実装順序`
  - `ステップ一覧`
  - `要件 ↔ ステップ対応`
  - `仕様固定クロージャ索引`
  - `レビュー / QA ゲート方針`
  - `実行ルール`
  - `実装ステップ`
  - `委任契約`
  - `具体テストケース一覧`
  - `ステップ完了契約`
  - `ステップゲート`
  - `ドキュメント影響の解消 / 更新`
  - `最終品質ゲート`
  - `最終完了条件`
- `review_status: pass`、`red-required`、`covered-existing`、`inspect-only`、`manual-required` などの値は、workflow contract として残す候補である。

#### report.md
- 主語は「実際に観測した証跡と判断」に置く。
- 推奨見出し:
  - `仕様解釈・判断台帳`
  - `委任ドラフト証跡`
  - `実装サマリー`
  - `実装記録`
  - `Red / Green / Refactor 証跡`
  - `発見されたテスト / リスク`
  - `ステップ完了証跡`
  - `テスト契約の完了証跡`
  - `クロージャ網羅`
  - `委任同意の証跡`
  - `実装委任ゲート`
  - `委任 worker 証跡`
  - `レビューゲート状態`
  - `ステップ commit ゲート`
  - `最終品質ゲート`
  - `省略 / 例外メモ`
- `Status`、`Type`、`Disposition` は値として使う場合は維持し、見出しまたは表ヘッダでは `状態（Status）`、`種別（Type）`、`処置（Disposition）` のようにする。

#### discussions
- `research.md`、`disc.md`、`interview.md`、`scratch.md` は現状でも日本語主体であり、優先度は低い。
- `adr.md` は ADR という標準文書の性質上、英語併記は許容できる。ただしユーザー向け自然さを優先するなら、主見出しを `結論`、`背景`、`検討した選択肢`、`判断理由`、`影響`、`参考` とし、括弧内に英語を残すのがよい。

### 7. テスト・検証への影響
- `tests/test_init_update.py` は provider / dogfooding mirror parity、active-none report mirror、テンプレートに含むべき固定語彙を検証しているため、最重要更新対象である。
- `tests/cli_runtime/test_new.py` は `spec-dock new` で生成される scaffold と discussion doc 生成の契約を確認している。
- `tests/cli_runtime/test_runtime_new_doc_s09.py` は discussion template placeholder の runtime 契約を確認している。
- `tests/cli_runtime/test_wrappers.py` は templates README や rules 周辺の exact string 期待を持つ可能性がある。
- 現在 `tests/test_init_update.py` には `Observed Evidence Ledger`、`Delegated Draft Evidence`、`Red/Green/Refactor Evidence`、`Final Quality Gate`、`Spec Interpretation / Decision Ledger` などの exact string 期待がある。テンプレートの主見出しを日本語化する場合、これらのテストを日本語表現または併記表現へ更新する必要がある。

## 推測 / 未検証事項 (必須)
- 推測:
  - reviewer / agent prompt が `Spec Interpretation / Decision Ledger` や `Final Quality Gate` などの英語見出しを厳密に参照している可能性がある。テンプレートだけを日本語化すると、agent-facing docs や skill text との語彙ズレが起きる恐れがある。
  - `workflow_spec_authoring.md`、`workflow_issue.md`、`docs/authoring/issue-plan.md` の英語トークンは、単なる表示文言ではなく agent contract の anchor として機能している部分がある。
  - `system/active-none` は placeholder だが、active 未設定時にユーザーが目にするため、日本語化対象に含めた方が UX と一貫性がよい。
- 未検証:
  - `src/spec_dock/assets/install_root/.agents/**` と `.codex/prompts/**` が英語見出しを exact match で参照しているかは未確認。
  - 全テストを実行した場合に、テンプレート文言変更だけでどの exact string assertion が失敗するかは未確認。
  - 既存の completed issue / epic / initiative 文書を retroactive に日本語化する必要があるかは未決。現時点では新規生成テンプレートと fallback を対象にすべきである。

## 判断への含意 (必須)
- 後続 Issue の requirement では、「日本語話者が見る canonical docs / templates / placeholder は日本語で作成されることを前提にする」を acceptance criteria に入れるべきである。
- 後続 design では、次の3層を分けるべきである。
  - 表示層: 見出し、説明、placeholder、table header は日本語主語。
  - 契約層: `status`、`Disposition`、lifecycle state、reviewer role、closure id などは値を維持し、日本語説明を添える。
  - 実装層: provider assets を正本にし、dogfooding mirror と tests を同時更新する。
- 後続 plan では、少なくとも次の実装順を推奨する。
  1. provider template / active-none の日本語主語化。
  2. dogfooding mirror 更新。
  3. `tests/test_init_update.py` の exact string 期待更新。
  4. 必要なら workflow / authoring docs の anchor 併記更新。
  5. `spec-dock validate`、targeted tests、`python -m unittest discover -v` で検証。
- 実装スコープは「表示ラベル日本語化、機械トークン維持」を第一段階にするのが安全である。値そのものの翻訳は別 ADR または別 Issue で判断する。

## リスク/制約 (任意)
- `issue/plan.md` と `issue/report.md` は agent workflow と密結合しているため、見出しを完全に置換すると reviewer / worker の参照精度が落ちる可能性がある。
- 英語トークンをすべて残すと今回のユーザー課題を解決しない。逆にすべて翻訳すると workflow 互換性を壊す。主見出しは日本語、必要箇所のみ英語を括弧併記する折衷が最も妥当である。
- table header の日本語化は可読性を上げるが、既存 docs / tests / agent prompt に同じ header 名を期待する箇所があれば同時更新が必要である。
- `active-none` は readonly placeholder として扱われるため、consumer 側だけを編集しても後続 update で戻る。provider 側を正本にする必要がある。

## 反映先 (任意)
- reflected_to:
  - 後続の日本語テンプレート更新 Issue requirement / design / plan
  - `src/spec_dock/assets/spec_dock/templates/**`
  - `src/spec_dock/assets/spec_dock/system/active-none/**`
  - `spec-dock/templates/**`
  - `spec-dock/system/active-none/**`
  - `tests/test_init_update.py`
  - 必要に応じて `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - 必要に応じて `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - 必要に応じて `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`

## 参考（References） (任意)
- `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/design.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/report.md`
- `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/epic/design.md`
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
- `src/spec_dock/assets/spec_dock/templates/epic/report.md`
- `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/issue/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue/report.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/adr.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
- `src/spec_dock/assets/spec_dock/system/active-none/initiative/report.md`
- `src/spec_dock/assets/spec_dock/system/active-none/epic/report.md`
- `src/spec_dock/assets/spec_dock/system/active-none/issue/report.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
- `tests/test_init_update.py`
