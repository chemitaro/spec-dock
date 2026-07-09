---
種別: research
ID: "20260709t010505z-research"
タイトル: "ChatGPT Use Direct Route vs SpecDock Script Route Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260709t010505z-research ChatGPT Use Direct Route vs SpecDock Script Route Analysis

## 調査目的 (必須)
- `iss-00309` の仕様書具体化実験で、ローカルの `chatgpt-use` 直実行ルートが SpecDock authoring script 経由ルートより良い成果になった理由を分析する。
- 特に、品質差を「モデル能力」ではなく、wrapper 設定、GitHub context、プロンプト構成、添付ファイル、ZIP materialization、evidence adoption の差分として整理する。
- この分析は後続 Issue で authoring script / planning skill を再設計するときの入力であり、直ちに canonical workflow を変更する authority は持たない。

## sources / 調査方法 (必須)
- 参照先:
  - `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/chatgpt-use/SKILL.md`
  - `/Users/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt`
  - `src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md`
  - `src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py`
  - `spec-dock/active/issue/report.md`
  - `spec-dock/active/issue/artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md`
  - `spec-dock/active/issue/artifacts/20260708t192858z-pr-repair-batch-pr-repair-batch.md`
- 検証手順:
  - `report.md` の D-001 / EAL-006 / EAL-007 を確認し、採用判断と不採用理由を抽出した。
  - `chatgpt-use` wrapper の固定設定を確認し、ChatGPT Project / model / thinking time / browser attachment / GitHub connector injection の有無を確認した。
  - SpecDock authoring script の `backend invoke` と prompt pack preparation を確認し、backend command contract と添付ファイル構成を確認した。
  - ChatGPT への客観レビューを `chatgpt-use` で実行しようとしたが、Cloudflare challenge で停止したため、外部レビュー結果は未取得として扱った。
- 実験条件:
  - 直実行ルートは `chatgpt-use` skill-local wrapper を直接起動し、ChatGPT から downloadable ZIP を得て、ローカルで listing / unsafe token scan / transcript render / manifest inspection ができた。
  - Script ルートは ChatGPT 応答上では ZIP 生成成功を示したが、ローカル artifacts へ ZIP 実体が materialize せず、展開検査と採用配置ができなかった。

## facts / 観測できた事実 (必須)
- `report.md` の D-001 は、検査可能な ZIP 実体が残った `chatgpt-use` 直実行版を採用し、SpecDock authoring script 経由版を不採用 evidence として扱っている。
- EAL-006 は、直実行版について repository-relative path を保持した ZIP 実体を検査でき、展開前検査で traversal や unsafe path が見つからなかったと記録している。
- EAL-007 は、script 経由版について ChatGPT 応答上では ZIP 生成に成功したが、ローカル artifacts に ZIP 実体が materialize せず、検査・展開・配置できなかったと記録している。
- `chatgpt-use` wrapper は Oracle を browser mode、固定 ChatGPT Project URL、`gpt-5.5-pro`、`--browser-thinking-time extended`、manual-login profile、`--browser-attachments auto`、`--browser-bundle-files`、`--browser-bundle-format auto` に固定している。
- `chatgpt-use` wrapper は `gh repo view` と `git symbolic-ref` から GitHub repository / current branch / default branch を検出し、`-p` / `--prompt` に repository connector context を前置する。
- SpecDock authoring script は backend command を `SPECDOCK_CHATGPT_COMMAND` / `ORACLE_CHATGPT_COMMAND` / CLI arg から解決し、prompt pack 内の `chatgpt-use-prompt.md`、`expected-output-contract.md`、`manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md` を `--file` として backend に渡す。
- SpecDock authoring script の default prompt は `Use the attached prompt pack files as the task brief. Produce the requested authoring output.` であり、直実行のような task-specific prompt を必ず作る contract ではない。
- SpecDock authoring script は subprocess の stdout / stderr と invocation summary を残すが、ChatGPT browser から添付 ZIP をダウンロードしてローカル artifact に保存する責務はこの経路だけでは確認できない。
- `authoring-pack/README.md` は、backend automation 自体は bundled せず、明示的 backend command contract で供給する方針を明記している。
- `20260708t162512z-manifest-chatgpt-formal-spec-pack.md` は、直実行版 ZIP の contents、GitHub connector observations、source assumptions、adoption caveats を明示している。
- ChatGPT への追加客観レビュー実行は Cloudflare challenge で停止した。したがって、この artifact の分析はローカルに確認できた source-grounded evidence と Codex 側の推論に基づく。

## comparison / 比較
| 観点 | `chatgpt-use` 直実行ルート | SpecDock authoring script ルート | 品質差への影響 |
|---|---|---|---|
| Invocation の目的 | 高度分析・設計・生成を ChatGPT に直接依頼する UX | evidence pack を安全に backend へ渡す contract | 直実行は authoring task に最短距離。script は安全な配送路寄り。 |
| Model / browser settings | `gpt-5.5-pro`、extended thinking、固定 Project、browser attachment を wrapper が強制 | backend command に依存。SpecDock 側は backend の中身を固定しない | script 側は同じ backend を指定しても、SpecDock contract 自体は高品質設定を保証しない。 |
| GitHub context | repository / branch / default branch を prompt に自動注入し、GitHub connector inspection を必須化 | prompt pack の provenance と source manifest は持つが、backend prompt で GitHub connector inspection を同じ強さで要求する保証は弱い | ChatGPT が現行 branch を確認する動線は直実行の方が明快。 |
| Prompt framing | ユーザーと Codex が目的に合わせて自然言語で濃く作り込める | default prompt は短く、詳細は添付 prompt pack を読む前提 | 大量生成では、最初の指示文の強さと構造が出力品質に効く可能性が高い。 |
| Attachments | wrapper が bundle / attachment 設定を固定し、自然な ChatGPT browser interaction に近い | prompt pack の metadata / constraints / source list を添付する | script は安全 metadata が多く、ChatGPT の主作業が「仕様書作成」から「契約解釈」に寄る可能性がある。 |
| ZIP output | ChatGPT UI から ZIP を取得し、ローカルで検査・展開できた | 応答 transcript では ZIP 生成成功だが、ZIP 実体がローカル保存されなかった | 採用可否を分けた最大要因。SpecDock は ZIP materialization を contract 化できていない。 |
| Error visibility | ChatGPT UI / Oracle session と成果物実体の両方を見られる | subprocess summary は残るが、browser-side downloadable artifact 欠落を pass/fail に落とし込みにくい | script が「ChatGPT は成功と言ったが成果物がない」状態を防げていない。 |
| Authority boundary | 出力は evidence-only として Codex が採用・検証 | evidence-only boundary は非常に強い | 安全性では script が優れるが、生成物回収 UX では直実行が優れた。 |

## root causes / 原因分析
### 確認済みの主因
- **ZIP materialization gap**: 今回の採用差は、直実行版が inspectable ZIP を残し、script 版が残さなかった点で決定している。内容品質以前に、SpecDock の adoption process が必要とする「検査可能な実体」が欠けた。
- **Script は backend invocation contract であり、download manager ではない**: `backend_invoke.py` は backend command を subprocess として呼び、stdout / stderr / summary を保存する。ChatGPT browser の添付ファイルを検出、ダウンロード、hash、配置する contract はこの層に見えない。
- **Default prompt が弱い**: Script ルートの default prompt は添付 prompt pack を読むことを指示するだけで、今回のような「Epic / Issue planning workflow を再設計し、複数ファイル ZIP で返す」タスクの判断基準、優先順位、失敗条件を本文で強く提示しない。
- **直実行 wrapper は実運用に合わせてかなり作り込まれている**: 固定 Project、Pro model、extended thinking、GitHub connector hard-failure、attachment bundling、timeout / reattach が既に実践向けに最適化されている。

### 推測だが有力な補助要因
- **ChatGPT にとって prompt pack は認知負荷が高い**: `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md` は安全性には重要だが、創造的な仕様書作成の主文脈としてはノイズになりやすい。結果として、出力の焦点が「ユーザーが欲しい仕様書群」から「pack contract を満たす応答」へずれる可能性がある。
- **直実行は人間の意図がプロンプト本文に残りやすい**: 手作り prompt は、会話で固まった優先順位、採用済み ADR、ワークフロー観、出力 ZIP の期待を自然に一つの brief として表現しやすい。Script 生成 prompt は安全に標準化される一方で、その場の熱量や判断の重みを落としやすい。
- **Script は成功条件が transcript 成功に寄っていた可能性がある**: backend の exit code が 0 でも、ZIP artifact がローカルに存在しないなら SpecDock 的には不十分である。今回の EAL-007 はこのズレを示している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 直実行ルートが優れていた理由は、ChatGPT の能力差ではなく、ChatGPT browser / Project / GitHub connector / ZIP download を含む end-to-end UX が既に実戦用に調整されていたことにある。
  - SpecDock authoring script は「安全な evidence lane」としては筋が良いが、「ChatGPT に正式仕様書群を大量生成させて ZIP 回収する primary workflow」としては、出力取得・検査・再試行の contract が不足している。
  - Script route の性能低下は、プロンプト本文の弱さ、prompt pack の認知負荷、ZIP materialization 未契約、backend 成功と成果物成功の分離不足が重なったものと考えられる。
- 推測の根拠:
  - `report.md` に、直実行版は inspectable ZIP、script 版は local ZIP unavailable と明示されている。
  - `chatgpt-use` wrapper は high-depth authoring に必要な browser 設定を固定している。
  - SpecDock script は backend を差し替え可能にする薄い invocation contract と prompt pack validation を中心にしており、ChatGPT UI 由来の downloadable artifact を first-class output として扱う処理が確認できない。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Script route で使用した実際の prompt pack 全文と transcript 全文の詳細比較。
  - ChatGPT browser 側では ZIP が生成されていたが、Oracle / wrapper / SpecDock のどの層で download persistence が欠落したのか。
  - Script route に direct route と同じ濃い prompt を渡した場合、内容品質がどこまで改善するか。
  - Script route の backend command として local `chatgpt-use` wrapper を指定した場合でも、downloadable ZIP を安定取得できるか。
- 確認できない理由:
  - 今回の追加 ChatGPT 客観レビュー実行は Cloudflare challenge で停止した。
  - 現時点のローカル evidence では、script route の実体 ZIP が存在せず、ZIP content 同士の差分比較ができない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Script route を primary workflow に昇格させる前に、ChatGPT downloadable ZIP を必ずローカル保存する機能を必須要件にするか。
  - Prompt templates を Markdown として provider assets に置き、ユーザーが tuning できる面を正式 API とみなすか。
- pressure-test question として切り出すべき候補:
  - `backend invoke` の pass 条件を「backend exit code 0」ではなく「expected ZIP / manifest / digest が local output dir に存在する」まで引き上げるべきか。
  - `chatgpt-use` wrapper の固定 UX を、SpecDock installed runtime からどこまで contract として要求するべきか。
- 質問せずに解決できた候補:
  - 今回採用する成果物は直実行版でよい。D-001 / EAL-006 / EAL-007 に採用判断が残っている。
  - Script route は不採用ではなく、follow-up 改善対象である。安全 contract 自体は有用で、捨てるべきではない。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `backend invoke pass`
  - `ChatGPT ZIP generation success`
  - `SpecDock adoption-ready`
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - `backend invoke pass` は backend subprocess が正常終了し、summary を残せることを主に示す。
  - `ChatGPT ZIP generation success` は ChatGPT 応答上または UI 上の生成成功を意味しうるが、ローカル実体の存在を必ずしも意味しない。
  - `SpecDock adoption-ready` は、ローカルで検査可能な artifact、digest、安全な path、EAL disposition、reviewer gate を必要とする。
- 判断が必要な理由:
  - これらを同一視すると、ChatGPT が「ZIP を生成した」と言っているだけで、SpecDock が採用できない成果物を pass と扱う危険がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - ChatGPT UI は ZIP を生成したが、Oracle の stdout には transcript だけが残り、ZIP download path がない。
- その edge case が requirement / design / plan に与える影響:
  - Requirement には「expected output artifact が local output dir に materialize しない場合は fail」と明記する必要がある。
  - Design には browser artifact capture / download / digest / manifest validation を first-class contract として追加する必要がある。
  - Plan には direct route と script route の golden-run 比較、ZIP 欠落時の再試行 / reattach / manual recovery を含める必要がある。

- edge case:
  - GitHub に push できない local-context mode で、diff / files を添付して ChatGPT に依頼する。
- その edge case が requirement / design / plan に与える影響:
  - Prompt pack の `local-context` provenance は有効だが、ChatGPT prompt では `GitHub connector context is supplementary or unavailable` と明示し、添付 context を authoritative input として扱う別テンプレートが必要になる。

- edge case:
  - Script route が safety metadata を大量に添付し、ChatGPT が主要な仕様書作成より metadata contract の説明に寄ってしまう。
- その edge case が requirement / design / plan に与える影響:
  - Markdown prompt template は、人間向け task brief、output contract、安全制約、adoption caveat を分ける必要がある。
  - `-p` の本文には、添付ファイルの読み方と優先順位を短く強く書く必要がある。

## implications / 判断への含意 (必須)
- Script route を primary workflow にするなら、まず「ChatGPT に投げる」だけでなく「ローカルに ZIP を回収し、検査し、採用候補として stage する」までを workflow contract に含めるべきである。
- 現行 script は捨てるよりも、直実行で成功した UX を取り込む方向がよい。具体的には、backend command は薄く差し替え可能に保ちつつ、prompt templates、expected ZIP manifest、download materialization validation、failure classification を追加する。
- Planning skill 側は、旧 workflow に ChatGPT 利用メモを追記する形では不十分である。Primary skill は `authoring backend invoke -> ZIP inspect -> stage -> local review -> EAL adoption` を中心に再設計し、従来 workflow は manual fallback として明確に分離する必要がある。
- Markdown prompt template は有効である。理由は、Python 文字列に閉じ込めるよりも、planning workflow の判断基準、出力 ZIP 構造、failure handling、adoption caveat をレビューしやすく、dogfooding で改善しやすいためである。
- ただし、Markdown template だけでは不十分である。今回の本質的欠落は ZIP materialization なので、テンプレート改善と同時に local artifact persistence の検証を必須化する必要がある。

## 推奨改善
- `backend invoke` の成功条件を、少なくとも次の二段階に分ける:
  - `backend_call_pass`: backend command が正常終了した。
  - `artifact_materialized_pass`: expected ZIP / extracted manifest / digest が local output dir に存在し検査できた。
- Provider asset として prompt template を追加する:
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/initiative-planning.md`
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/epic-planning.md`
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/issue-planning.md`
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/issue-draft-adoption.md`
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/final-quality-delivery.md`
- Template は Python で直接合成せず、Python は template render と source manifest assembly に限定する。
- Script route は direct `chatgpt-use` wrapper の成功要素を contract として明文化する:
  - model / thinking time は backend 側に依存するため、SpecDock では `required_backend_capabilities` として記録する。
  - GitHub connector context が必要な mode では、branch access failure を hard fail とする。
  - local-context mode では、provided files / diff / unsynced reason を prompt 本文に明示する。
- `authoring backend invoke` 後に `authoring artifact collect` のような段階を追加し、browser download path、ZIP path、sha256、listing、unsafe path scan を summary に残す。
- Script route と direct route の golden-run regression を残す:
  - 同じ task brief で direct route と script route を実行する。
  - ZIP materialization、manifest completeness、repository-relative paths、adoption caveats、reviewer readiness を比較する。
  - Script route が direct route と同等の検査可能成果物を残すまで、primary workflow へ昇格しない。

## リスク/制約 (任意)
- ChatGPT browser automation は Cloudflare challenge、ログイン状態、4 tab limit、download handling に依存する。したがって primary workflow では wait / retry / recovery を標準化し、manual fallback は人間承認付きにする必要がある。
- Script route の安全性を弱めて直実行 UX に寄せすぎると、SpecDock の evidence-only boundary が崩れる。改善は「安全 contract を捨てる」ではなく「安全 contract の上に成果物回収 UX を足す」方向で行う。
- ZIP materialization の実装は環境依存になりやすい。SpecDock repo に個人 PC 固有の wrapper path を直書きせず、`SPECDOCK_CHATGPT_COMMAND` などの backend command contract を維持する必要がある。

## 反映先 (任意)
- reflected_to:
  - `iss-00309` follow-up discussion
  - future Issue: authoring script ZIP materialization / prompt template redesign
  - future Issue: ChatGPT-first planning skills rewrite

## 参考（References） (任意)
- `spec-dock/active/issue/report.md` D-001 / EAL-006 / EAL-007
- `spec-dock/active/issue/artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py`
- `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/chatgpt-use/SKILL.md`
