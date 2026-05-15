---
種別: 要件定義書（Issue）
ID: "iss-00098"
タイトル: "Delegated Implementation Orchestration Contract"
関連GitHub: ["#98"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-05-15"
親: ["epic-00067", "init-local-00003"]
---

# iss-00098 Delegated Implementation Orchestration Contract — 要件定義（WHAT / WHY）

## 目的
- spec-dock の Issue 実行 workflow に、親 Codex を実装者ではなく orchestration owner として扱う delegated-by-default 原則を組み込む。
- 実作業は plan step 単位で適切な delegated worker に委任し、runtime / tests / scaffold behavior は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` を主担当にして、`code-reviewer` / `qa-reviewer` / `spec-reviewer` の gate で検証する運用契約を明文化する。
- 親 Codex の context 汚染と過剰な低レベル実装推論を抑えつつ、delivery の最終責任と統合判断は親 Codex に残す。

## 背景・現状
- 現状の workflow には `Implementation Delegation Gate` と `dev-coder` の role selection があるが、親 Codex が直接実装する `approved-local-execution` も広く許容されている。
- その結果、親 Codex が実装詳細、探索ログ、テスト失敗、修正試行を抱え込み、要件・設計・計画・統合判断の文脈を圧迫しやすい。
- reviewer 系 sub-agent は gate として使われやすい一方、`dev-coder` は任意の実装手段に見えやすく、親 Codex が直接実装する傾向が残る。
- spec-dock の dogfooding workflow では、親 Codex が workflow 全体を統合し、実装推論とファイル変更は bounded worker に委任する形を標準にしたい。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock を dogfooding する Codex CLI / コーディングエージェント
  - spec-dock の workflow / skill / shipped agent assets を保守する開発者
- 代表シナリオ:
  - ユーザーが active Issue の要件定義から実装完了までを Codex に依頼する。
  - 親 Codex は active docs を読み、step contract を整え、`dev-coder` に実装を委任する。
  - `dev-coder` は指定 step のファイル変更と検証を行い、implementation report を返す。
  - 親 Codex は結果を統合判断し、reviewer gate を通してから step を完了扱いする。

## スコープ
- 必須:
  - 親 Codex の delegated-by-default 原則を workflow / skill / template に明文化する。
  - delegated worker 委任時の必須入力、許可範囲、禁止範囲、停止条件、戻り値を定義する。
  - plan step に delegation contract を持たせる。
  - report に delegation evidence / reviewer verdict / parent integration decision を残せるようにする。
  - 親 Codex が直接実装できる例外条件と exception record を定義する。
- 禁止:
  - 「小さい変更」「機械的変更」「親が知っている修正」を理由に、実装ファイル変更を無記録で親 Codex が行える扱いにすること。
  - `dev-coder` 委任を reviewer gate の代替にすること。
  - 親 Codex の delivery 責任を `dev-coder` や reviewer に移すこと。
- 対象外:
  - sub-agent runtime 自体の新規実装。
  - transcript/tool-call 監査の完全自動 enforcement。
  - `spec-dock issue delegate` などの新 CLI command 追加。
  - Codex 以外の host 向け専用 workflow 実装。

## 境界
- 常に行う:
  - 親 Codex は調査、計画、委任、検証、統合判断、報告を担当する。
  - 実装ファイル、テスト、scaffold、template、runtime、shipped asset の変更は原則 `dev-coder` または適切な write-capable role に委任する。
  - 各 implementation step は delegated worker report と、step の性質に対応する reviewer gate を経てから完了扱いする。code / runtime / tests / scaffold behavior を含む step は `code-reviewer` pass、docs-only / template-only / skill-text-only step は `spec-reviewer` による docs/spec alignment pass を必須にする。
- 判断が必要:
  - 実装前の design / plan で、各 step の allowed paths、forbidden changes、reviewer focus、required tests を具体化する。
  - docs / templates / skill / workflow 文書の更新をどの implementation step に分けるかを、変更対象の source-of-truth と review scope に合わせて設計する。
- 行わない:
  - 親 Codex の direct write を技術的に完全禁止する runtime gate はこの Issue では実装しない。
  - すべての軽微な文書更新まで必ず `dev-coder` に委任する hard rule にはしない。

## 非交渉制約
- `src/spec_dock/assets/install_root/` は installed agent-tooling assets の provider-side source of truth として扱う。
- `src/spec_dock/assets/spec_dock/` は consumer workspace に生成される `spec-dock/` scaffold の provider-side source of truth として扱う。
- dogfooding 側 `spec-dock/` だけを正本として編集してはならない。
- workflow 説明は docs を正本とし、skills は concise routing / execution reminders に留める。
- Issue execution は `workflow_issue.md` と `.agents/skills/spec-dock-issue-execution/SKILL.md` の整合を保つ。
- requirement / design / plan の phase promotion は fresh `spec-reviewer` の `review_status: pass` を必要とする。

## 前提
- `dev-coder` は bounded implementation step を直接編集できる write-capable sub-agent として利用可能である。
- `code-reviewer`、`qa-reviewer`、`spec-reviewer` は reviewer gate として利用可能である。
- 現行 workflow にはすでに `Implementation Delegation Gate`、`Role selection matrix`、`delegated / approved-local-execution` の記録欄がある。
- 本 Issue はその既存 contract を、親 Codex orchestration model に合わせて強化する。

## 受け入れ条件
- AC-001:
  - アクター: 親 Codex
  - 前提: active Issue の implementation step を開始する
  - 操作: issue execution workflow / skill を読む
  - 期待結果: `Parent Agent Invariant` または同等の節が存在し、親 Codex の許可行為が inspect / plan / delegate / verify / integrate / report に限定され、code / test / scaffold / template / runtime / shipped asset の直接変更禁止と delegated worker 委任原則が明記されている
  - 観測点: `workflow_issue.md`、`spec-dock-issue-execution/SKILL.md` の該当節
- AC-002:
  - アクター: plan author
  - 前提: Issue plan の implementation step を作成する
  - 操作: plan template / authoring docs に従って step を記述する
  - 期待結果: 各 step に `delegation contract` 欄があり、`delegated role`、`input docs`、`allowed paths`、`forbidden changes`、`acceptance criteria`、`required tests`、`reviewer focus`、`stop conditions`、`output required` を記録できる
  - 観測点: issue plan template、issue plan authoring docs の step contract
- AC-003:
  - アクター: 親 Codex
  - 前提: `dev-coder`、`doc-writer`、またはその他の step-appropriate delegated worker に実作業を委任する
  - 操作: handoff contract に従って依頼する
  - 期待結果: delegated worker handoff に `delegated role`、`scope`、`source of truth`、`allowed changes`、`forbidden changes`、`required verification`、`stop conditions`、`output required` が必須項目として存在する
  - 観測点: workflow docs、skill guidance、template text の handoff contract
- AC-004:
  - アクター: reviewer
  - 前提: `dev-coder` または `doc-writer` などの delegated worker による step diff がある
  - 操作: step の性質に対応する reviewer gate を実行する
  - 期待結果: reviewer fail 条件として、step contract 外変更、provider/dogfooding source-of-truth 逸脱、required tests または docs-only verification の未実行・未記録、delegated worker report 不足、親 Codex の無記録 direct implementation が列挙されている。code / runtime / tests / scaffold behavior を含む step は `code-reviewer`、docs-only / template-only / skill-text-only step は `spec-reviewer` docs/spec alignment が対応 gate として明記されている
  - 観測点: workflow docs、report template、review gate guidance の fail condition
- AC-005:
  - アクター: 親 Codex
  - 前提: 親 Codex が例外的に直接実装する必要がある
  - 操作: exception gate を記録する
  - 期待結果: `Parent Implementation Exception` 欄に delegation 不可理由、user approval、allowed files、allowed operation、rollback plan、post-change verification、reviewer gate が必須項目として存在する
  - 観測点: report template、workflow docs の exception record
- AC-006:
  - アクター: future agent / maintainer
  - 前提: 完了済み Issue の report を読む
  - 操作: delegation evidence を確認する
  - 期待結果: report の delegation evidence に step id、delegated role、delegated worker summary、changed files、tests run または docs-only verification、reviewer verdict、unresolved risks、parent integration decision が必須列または必須項目として存在する
  - 観測点: issue report template、completed report example or template rows

## 例外・エッジケース
- EC-001:
  - 条件: `dev-coder` が host policy、環境、権限、またはツール制約で利用できない
  - 期待: required implementation delegation は degraded success ではなく `blocked` または `incomplete` として扱う。ユーザーが明示的に risk acceptance を与えた場合のみ `waived` を記録できるが、`waived` は reviewer pass ではなく、親 Codex の直接実装を自動許可しない。親 Codex が直接実装するには、別途 `Parent Implementation Exception` の user approval、allowed files、allowed operation、rollback plan、post-change verification、reviewer gate を記録する
  - 観測点: workflow docs、report evidence
- EC-002:
  - 条件: 変更が docs / report / handoff note など orchestration metadata のみである
  - 期待: `report.md`、handoff note、phase evidence のような run-local orchestration metadata は親 Codex が直接更新できる。shipped docs、templates、skills、workflow text、runtime-facing scaffold は `doc-writer` または `dev-coder` に委任し、reviewer gate を通す
  - 観測点: exception policy
- EC-003:
  - 条件: step が複数 layer / package / shipped asset にまたがる
  - 期待: 親 Codex は direct implementation せず、allowed paths と dependencies を明記して `dev-coder` に委任する
  - 観測点: plan step delegation contract
- EC-004:
  - 条件: reviewer が `dev-coder` 実装に fail を返す
  - 期待: 親 Codex は原則として自分で修正せず、指摘を bounded follow-up として `dev-coder` に再委任する
  - 観測点: workflow docs、report evidence

## 入力→出力例
- EX-001:
  - 入力: 「active Issue の S01 を実装して」
  - 出力: 親 Codex が S01 の source docs、allowed paths、forbidden changes、acceptance criteria、required tests、stop conditions をまとめた `dev-coder` handoff を作成する
- EX-002:
  - 入力: `dev-coder` implementation report
  - 出力: 親 Codex が changed files / tests / risks を確認し、`code-reviewer` に step diff review を委任する

## 用語
- TERM-001:
  - `parent Codex`: ユーザーと対話し、workflow 全体、委任、統合判断、最終報告を担当する orchestration owner。
- TERM-002:
  - `dev-coder`: bounded implementation step のファイル変更、テスト追加、検証実行を担当する write-capable sub-agent。
- TERM-003:
  - `delegated worker`: plan step の実作業を担当する sub-agent。runtime / tests / scaffold behavior は主に `dev-coder`、shipped docs / templates / skills / workflow text は主に `doc-writer` が担当する。
- TERM-004:
  - `delegation contract`: plan step ごとに、委任先、入力、許可範囲、禁止範囲、完了条件、検証、停止条件を固定する契約。
- TERM-005:
  - `parent implementation exception`: 親 Codex が例外的に直接ファイル変更する場合に必要な理由・範囲・承認・検証の記録。
- TERM-006:
  - `reviewer gate`: `code-reviewer`、`qa-reviewer`、`spec-reviewer` が fresh `review_status: pass` を返すまで完了扱いしない品質ゲート。

## 決定済み方針
- DEC-001:
  - 論点: 親 Codex が直接更新してよい orchestration metadata の範囲
  - 採用: `report.md` / handoff note / phase evidence のような orchestration metadata に限定する。
  - 理由: docs / templates は shipped behavior に影響するため、`doc-writer` または `dev-coder` 委任を原則にする。
  - 影響範囲: workflow docs、report template、exception policy
- DEC-002:
  - 論点: 親 Codex の direct write を runtime validator で検出するか
  - 採用: 今回は docs / skill / template contract までを対象にし、runtime validator は追加しない。
  - 理由: 運用 contract を先に dogfood し、audit automation は後続 Issue に分離する。
  - 影響範囲: runtime command、tests、agent logs
- DEC-003:
  - 論点: `doc-writer` と `dev-coder` の使い分け
  - 採用: shipped docs / templates / skills / workflow text の文言・構造更新は `doc-writer`、runtime / tests / scaffold behavior を伴う変更は `dev-coder` が担当する。両方をまたぐ step は plan で分割するか、親 Codex が allowed paths と reviewer focus を分けて委任する。
  - 理由: 文書整合と実装変更の責務を混ぜると review scope と commit scope が曖昧になるため。
  - 影響範囲: workflow docs、issue plan template、report template、review gate guidance
- DEC-004:
  - 論点: sub-agent unavailable 時の waiver semantics
  - 採用: `waived` はユーザーの明示的 risk acceptance を記録する状態であり、required reviewer / delegation gate の pass ではない。waiver 後も completion には代替検証と該当 reviewer gate の扱いを report に残し、親 Codex の直接実装は `Parent Implementation Exception` を別途必要とする。
  - 理由: unavailable / denied を degraded success と扱うと、workflow の品質ゲートが空洞化するため。
  - 影響範囲: workflow docs、report template、exception policy、final completion judgment

## 未確定事項
- 現時点で design promotion を妨げる未確定事項はない。
