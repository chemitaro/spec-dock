---
種別: interview
ID: "20260803t030323z-interview"
タイトル: "iss-00354 添付ディレクトリの機械的収集と安全境界"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-08-03"
親: ["iss-00354"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00354"
created_at: "2026-08-03THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260803t030323z-interview iss-00354 添付ディレクトリの機械的収集と安全境界

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - 添付ディレクトリをまとめて渡す運用、相対path保持、収集対象・除外対象、サイズ／件数超過・秘密情報・path traversal時の停止条件。
  - `design.md`:
    - pack rootのdeterministic discovery、recursive／symlink／hidden fileの扱い、attachment manifestと送信前の機械的検査。
  - `plan.md`:
    - 既存scriptの個別`--file`列挙からdirectory収集へ移行する順序、negative／security／limit tests、Oracle transportとの接続点。
  - `ADR`:
    - 複数scopeで再利用する不可逆なsecret／attachment retention policyへ昇格する場合だけ候補化する。
- chat 上の軽微な一問では足りない理由:
  - 「中身を検査しない」ことと、path外参照・symlink escape・秘密情報送信・添付上限超過を無制限に許すことは異なるため、意味検査をしない最小の機械的安全境界を明示する必要がある。

## 質問の目的 (必須)
- 対象者:
  - Issue owner（ユーザー）。
- 何を明確にする質問か:
  - operation-specific attachment directoryをスクリプトがどの範囲で収集し、何を機械的に拒否・警告するか。
- 回答が後続判断へ与える影響:
  - directory packの実装API、manifest／相対path、hidden／symlink／secret／size制約、ChatGPTへの送信前fail-closed条件が決まる。

## 質問 (必須)
- pressure-test question:
  - 内容の意味検査をせずに柔軟性を保ちながら、意図しないファイル送信とtransport上限超過を防ぐ機械的境界になっているかを確認する。
- 質問:
  - operation-specific添付ディレクトリの収集と安全境界について、どの規則を採用しますか？
- 回答してほしいこと:
  - **Option A（推奨）**: 明示したpack root配下の通常ファイルを再帰的に収集し、rootからの相対pathを保持してdeterministic順序で添付する。内容の意味検査はしないが、root外へのpath traversal、root外へ解決するsymlink、特殊ファイル、危険なfilename、添付件数／サイズ上限、明示的なsecret denylistは機械的に拒否する。収集manifestと理由を証跡に残す。
  - **Option B**: pack root直下の通常ファイルだけを収集し、hidden file・subdirectory・symlinkは除外する。単純だが、手順資料の階層構造や隠し設定を扱えない。
  - **Option C**: root配下のすべて（symlink・hidden file・特殊ファイルを含む）を無検査で添付する。柔軟だが、root外の秘密情報・無限loop・transport上限・path escapeを許す。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Issue #354調査／disc、`chatgpt-use` skillのattachment limit・secret禁止、providerのprompt／transport実装、`issue_planning_chatgpt.py`、既存attachment tests、AGENTS.mdのtemporary／secret方針。
- local context で解決できたこと:
  - 現行wrapperは`--file` globを収集し、Oracle側にもattachment count／size制約がある。prompt synthesisはsource pathと添付を記録できるが、operation pack directoryの再帰収集契約は未実装である。
- まだ人間判断が必要な理由:
  - ユーザーは「中身は検査しない」「ディレクトリの増減でコードを変えない」と明示したが、意味検査をしないまま許容する機械的なpath／secret／size境界の強さは未確定だから。

## 回答案 (必須)
- Option A:
  - recursive regular-file collection、relative path保持、deterministic順序、root containment・symlink・special file・filename・secret denylist・count／sizeだけを機械検査。
- Option B:
  - root直下のみ、hidden／subdirectory／symlinkを除外。単純だが階層資料に弱い。
- Option C:
  - 全件無検査。柔軟だが安全性とtransport安定性を失う。

## Codex の分析 (必須)
- 判断軸:
  - ユーザーの柔軟性・コード変更不要、directory treeの保持、secret／path安全、Oracle attachment limit、再現可能なmanifest、内容意味検査をしない境界。
- tradeoff:
  - Aは意味検査を避けつつ、filesystem／transport事故を機械的に防ぐ。Bは安全だが資料構造を壊す。Cは最も柔軟だが、外部ファイル送信と上限超過を無制限に許す。
- リスク:
  - denylistを意味検査と混同する、symlinkを追跡してroot外へ出る、hidden fileにtokenが入る、巨大packがtimeoutし、本文だけで続行する危険がある。
- 具体シナリオ / edge case:
  - `attachments/../.env`やroot外symlinkを検出した場合は送信しない。
  - ZIPや画像などbinaryを意味検査せず、通常ファイルとして扱うが、size／media type／Oracle上限は検証する。
  - hidden Markdownを許可する場合でも、secret filename／拡張子のdenylistとroot containmentは維持する。
  - subdirectory内のファイル順序を固定し、manifest SHAを再現可能にする。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。ただしsecret denylistは内容を読む検査ではなく、filename／path／explicit operator policyによる機械的な送信防止に限定する。
- 理由:
  - ユーザーのoperation pack方式・directory tree保持・コード変更不要を満たしつつ、意味検査なしでもpath traversal、symlink escape、特殊ファイル、上限超過を防げる最小境界だから。
- 未回答時の影響:
  - directory packの収集実装とChatGPT attachment送信の安全条件を確定できず、operation pack方針をcanonical docsへ反映できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 回答の経緯: 最初にOption Bを採用すると述べたが、その後「添付専用ディレクトリは無検査で全件添付してよい」と明示し、最終的にOption Cを採用した。
- 回答:
  - Option Cを採用する。operation-specific添付ディレクトリは、そもそもChatGPTへの添付を前提に作成・管理する。添付時にファイル名、意味、隠しファイル、サブディレクトリ、symlinkなどを一律検査・除外せず、ディレクトリの内容をまとめて添付する。サイズ上限は添付時に毎回判定するのではなく、作成時に設定・管理する。スクリプトのコードをファイル増減に合わせて変更しない。
- 回答日時:
  - 2026-08-03（Codex会話上の回答時刻）

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes。Option Cの「全件」が、サブディレクトリの再帰、hidden file、symlinkのリンク自体／解決先、特殊ファイルをどのようにtransportへ渡す意味かを、次の一問で明確化する。
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - literalな全filesystem entryと、ChatGPT transportが扱える添付fileの範囲の差をどう扱うか。

## 採用判断 (回答後に必須)
- adoption_status:
  - `adopted`（ユーザーが最終的にOption Cを明示承認）。
- adoption target:
  - Issue #354の`requirement.md`、`design.md`、`plan.md`、operation pack収集設計、および`report.md`のEvidence Adoption Ledger（canonical authoring時に反映）。
- 採用 / 棄却 / deferred の理由:
  - ユーザーは添付専用ディレクトリを信頼された入力領域とし、添付時の意味・名前・構造検査を省略して運用の柔軟性と保守性を優先した。サイズは作成時の設定で管理する。途中のOption B回答は最終回答で訂正されたため、採用判断はOption Cに統一する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 添付専用ディレクトリをtrusted input packとして扱い、ファイル増減でスクリプト変更を不要にする。添付時の意味検査・名前検査・構造検査を一律に要求せず、サイズ設定はpack作成時に管理する。
- `design.md`:
  - directory packをまとめてtransportへ渡す方式を設計し、literalなfilesystem entryとChatGPTが受け取れるattachment表現の差は別途定義する。内容validationはoperation固有の責務とする。
- `plan.md`:
  - 個別ファイル列挙をdirectory単位の収集へ置換し、ファイル増減でコード変更が不要なことを検証する。作成時size設定とtransportの実制約の責務境界を整理する。
- `ADR`:
  - trusted attachment directoryの扱いが複数scopeで不可逆なsecurity／retention policyになった場合のみ候補化する。現時点ではIssue-local方針として扱う。
- reflected_to 更新方針:
  - canonical authoring時に、最終Option Cの回答とChatGPT advisoryとの差分、transport制約の未解決事項をEvidence Adoption Ledgerへ記録する。
- adoption reflection:
  - canonical三文書未作成のため`reflected_to: []`を維持する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る artifacts:
  - ...
