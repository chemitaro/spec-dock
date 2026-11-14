---
種別: レポート（Issue）
ID: "iss-00593"
関連GitHub: ["#593"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 2026-11-14 仕様レビュー：**合格**（round-5）。strict なので2人。
  - 合格の版の sha256：requirement.cue `4373c5d66ea9261f0211ad7c17cbfa40984f4963e09bf6267d4e2356e9566ba6`、design.cue `28b8bac6cb612c5ee0436f35ee5ea8ba4107af69b6d1bf3e060b2d3587f915cd`、plan.cue `fb0adda080488f1242f9ca26bbd7da56e68f54886ebdbfdbe246dd31f0f64646`、explanation.html `c9f8d5672209a36c563a298e376dc804333884a0b301a3611ae79fcd4a9e3e78`。カタログ `spec-dock/canonical` の `fea6a798bcbd1012536b67c8178b8ac3afa08eda`（GitHub と一致）。worktree の HEAD `67abbe6c1`（clean。開始のコミット）。
  - spec-reviewer（Opus 5.5 / high、同じレビュアー）：round-1 fail（P1 1、P2 3、P3 3）→ round-2 pass（P2 1、P3 2）→ round-3 pass（P3 1）→ round-4 pass（P3 1）→ round-5 pass（P3 1）。結果は worktree の `.workbench/spec-review/iss-00593/round-{1..5}.json`（検査 `round-{n}.check.json`、すべて valid）。
  - 2人目 ChatGPT（GPT-6 / Extra High、`chatgpt-spec-review-strict`、カタログの SHA に固定）：round-1 評価なし（`OUS-R001-GITHUB-VERIFICATION-FAILED`。レビュー中に spec-dock/canonical が他の Scope の保存で進んだ）→ round-2 fail（P1 3、P2 1）→ round-3 fail（P1 4、P2 1）→ round-4 fail（P1 1、P2 1）→ round-5 pass（0、確信 0.93）。結果は `.workbench/spec-review/iss-00593/chatgpt-{1..5}.raw`（JSON は `chatgpt-{2..5}.json`）。モデルの選択の証拠は round-2〜5（同じ会話の続き）で `status=skipped; verified=no; source=config`、思考 Extra High はどの回も verified。別のモデルだという証拠はないが、確かめられていないものとして記録する。
  - P0/P1 はすべて訂正したか、反論した（round-4 の P2 は反論）。round-4 の P1（2回目の load と送る欄の有効化の順を HTML の仕様が保証しない）は、統括の決定（msg_c06a2f506afa、案1）で残るリスクとして受け入れ、根の修正は orca-web の iss-00037。分析と訂正は `.workbench/spec-review/iss-00593/review-response.md`。合格の版の P2 は 0、P3 は 1（選んだ相手の項目だけ形が違う間は、別の相手を選び直せない。安全側）。
- 2026-11-14 仕様の訂正と再レビュー：**合格**（round-6、spec-reviewer の同じレビュアー、P3 2）。変えたのは plan.cue の実行の割り当てだけ（S-01 を impl_logic〈Codex〉から impl_ui〈Claude Opus 5.5 / high〉へ。理由は下の「逸脱と判断」）。要件・設計・説明資料は round-5 の合格の版のまま。ChatGPT は、割り当てだけの訂正なので回していない（round-5 の合格の版の要件・設計・テストは変わらない）。
  - 合格の版の sha256：requirement.cue `4373c5d66ea9261f0211ad7c17cbfa40984f4963e09bf6267d4e2356e9566ba6`、design.cue `28b8bac6cb612c5ee0436f35ee5ea8ba4107af69b6d1bf3e060b2d3587f915cd`、plan.cue `584ba8ae5e2782adb40195fbafbe180a71922d4aa0d18078b87ff6e27c342168`、explanation.html `c9f8d5672209a36c563a298e376dc804333884a0b301a3611ae79fcd4a9e3e78`。結果 `.workbench/spec-review/iss-00593/round-6.json`（検査 valid、pass）。
  - P3（記録だけ）：plan.cue の C-1 の reason の「別の実装担当の作ったもの」は、今は同じ実装担当（関門としてはそのまま成り立つ）。requirement.cue の decisions の「純粋な計算を Codex」は、下の逸脱で置き換わった（iss-00593 に限る）。
- 2026-11-14 仕様の訂正と再レビュー：**合格**（round-7、spec-reviewer の同じレビュアー、P3 2〈前からの残り〉）。実装担当 impl_ui の問い（msg_2c43d31c056f）で、ほかのタブの間に覚えに足された id は pickAgent の規則2に当たり、問い合わせに `gone:<id>` が入らず、読み込み直しの後に R-05・F-02 が成り立たない穴が見つかった。D-01 の規則2の remember を `"gone:" + wanted` に、plan.cue の T-02 の行を合わせた。ChatGPT は、規則1つの値の訂正なので回していない。
  - 合格の版の sha256：requirement.cue `4373c5d66ea9261f0211ad7c17cbfa40984f4963e09bf6267d4e2356e9566ba6`、design.cue `fd768249b27be9d79737e80475f59a0a038aa0214e9e0680ae069a10942ad5d1`、plan.cue `de4863575b35d567c18527966d8060130ababde8b06591310d0031fca1d151dd`、explanation.html `c9f8d5672209a36c563a298e376dc804333884a0b301a3611ae79fcd4a9e3e78`。worktree の HEAD `130ff2b70`（clean）。結果 `.workbench/spec-review/iss-00593/round-7.json`（検査 valid、pass）。
- 2026-11-14 仕様の訂正と再レビュー：**合格**（round-8・round-9、spec-reviewer の同じレビュアー）。最終品質ゲート attempt 1（787a05147）の主の FQG-001（P2）・FQG-002（P3）と ChatGPT の P1 2・P2 2 を、統括の決定（msg_5490fcda8a19）で直すため、覚えの last、移るときに待たずに前の iframe を外す（Scope か agent が変わる移りだけ、外したら置き直す）、知らせの描き直しは今の route、記録を読めないときと全部が形違いのときはいなくなったと決めない、印の比べに now、を足した。round-8 の P2（外した iframe が置き直されない）を直して round-9 で合格（P3 2〈前からの残り〉）。ChatGPT は、指摘の出どころがそのゲートの ChatGPT なので、attempt 2 のゲートで見る。
  - 合格の版の sha256：requirement.cue `c102ecd0a3ea31be23d3f180f555a6537f2dcf272bf2e1255943d236fe33ec27`、design.cue `62fea2262484d76280ee0109ba4ea85f33f42c19f1161d3b1d8f08a3428c4502`、plan.cue `9c8e7d97ef488f8d9230040eb177f510b137d5fad8b2f7861f45894fba8fb1b6`、explanation.html `c9f8d5672209a36c563a298e376dc804333884a0b301a3611ae79fcd4a9e3e78`。worktree の HEAD `787a05147`（clean）。結果 `.workbench/spec-review/iss-00593/round-{8,9}.json`（検査 valid、pass）。

## 実装の記録

実装担当 impl_ui（Claude Opus 5.5 / high、dispatch `ctx_b9443c0b31eb`、launch.effective claude・claude-opus-5-5・high）。記録の詳細は worktree の `.workbench/implement/iss-00593/{start.md,steps.md}`。

- 開始のコミット `67abbe6c1` の基準：`make lint` pass、`uv run pytest` 3847 passed / 7 skipped / 0 failed。
- S-01 `130ff2b70`（`agents_logic.js` と T-01〜T-03）→ 区切りのレビュー C-1（code-reviewer opus / medium、範囲 `67abbe6c1..edf20b86f`、指摘 0 で合格。合格の後、コミットの文だけを `type(scope):` の形に amend して `130ff2b70`）。
- 規則2の直し `ef27d49d0`（仕様 round-7）。S-02 `8ce154a26`（agents_tab.js、scope_tabs.js、panel.js、scope.js、app.js、CSS）。S-03 `cd9dfe7fd`（書き込みに関わらない静的なテスト、配る文書、inventory）。
- 実機で見つけた帯の直し `d55516770`・`f7439f621`・`a6d11d3ef`（選んだ項目を帯の見える位置へ）と書式 `6e8d97b50`。dogfood の写し `787a05147`。
- 最終品質ゲートの直し `863110f34`（仕様 round-8・round-9：last、移るときに待たずに前の iframe を外す、知らせの描き直しは今の route、記録を読めない・全部が形違いではいなくなったと決めない、印の比べに now）。
- origin/main（iss-00592、PR #597）の取り込み `f911dd4a8`（ぶつかり：panel.js、static-inventory.json。reference_cli.md は Epic D-07 に従い「orca-web との連携」の1つの節にまとめ、dogfood の写しも同じバイト）と、その後の直し `790c93cac`。
- 最終品質ゲート attempt 2 の直し `1094a0489`（欄の足のリンクに欄の agent を引き継ぐ）。
- 終わり：`make lint` pass、`uv run pytest` 0 failed（数は最終品質ゲートの節）。

## 実機の確かめ（S-04、タスク担当）

試しの組（統括の決定のやり方）。常駐のダッシュボード（47800）と常駐の orca-web（8791）と、その設定のファイルには触れていない。

- 試しの orca-web：orca-web の main（iss-00037 の入った `373a2c7`）の `dist/` を、ポート 8893、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet の2つのオリジン（18593・18594）、試し専用の `ORCA_WEB_SETTINGS_FILE` と `ORCA_WEB_SENDS_DIR` で起動。`sendEnabled` は試しの設定だけで、送信の確かめと写しの間だけ true、ほかは false。
- 試しの SpecDock：直す前は開始のコミット、直した後は各コミットの `git archive` から作った wheel を隔離した venv に入れ、一時の状態の置き場（道具の環境の状態の置き場の写し）と一時の `XDG_CONFIG_HOME` の `config.json`（`orca_web.port` 8893）で、ポート 18593（前）・18594（後）、`--tailscale`。headless Chrome と CDP で確かめた（台本と記録は worktree の `.workbench/iss-00593/`、最終の版は `final-1094a0489/`）。

結果（最終の版 `1094a0489` で全部をやり直した。途中の版 `cd9dfe7fd`・`6e8d97b50`・`863110f34`・`790c93cac` でも同じ確かめをした）：

- タブ：iss-00593 の欄と詳しい画面で2番目に「エージェント」、数の札 6（対応した2つの worktree のエージェント）。連携の切り・記録のない Scope では出ない（node のテスト）。
- 送信（R-04、D-07）：確かめ専用の宛先（ブランチ `chemitaro/iss-00593-send-test` のエージェント。帯と iframe の title のブランチで確かめた）にだけ、iframe の中から短い1文を1回送った（`cd9dfe7fd` の版。「送りました（受け付けた）」、宛先は「受け取りました（約20文字）」と返した）。送信の口の要求（`GET /api/send/status`、`POST /api/token`、`POST /api/send/intent`、`POST /api/send/confirm`）はすべて iframe の frame から出て、親の frame から orca-web への要求は `GET /api/worktrees/summary` と `/embed/` の部品（agent-marks*.js・css、elapsed.js）だけ（`network-send.json`）。業務中のエージェントには送っていない。
- sandbox（D-03）：`allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox` のまま、会話の読み、送信、「Orca で開く」（iframe から `/api/token` 200・`/api/open` 200）、詳細のリンクの新しいタブ（opener のある新しい page）が動いた。
- 高さ（R-03）：横の欄は iframe の下端が中身の下端（余白 10px）にそろい、中身のスクロールなし（1440・1000）。390 の全体の段で iframe 656px（844px のうち）。詳しい画面は `100dvh − 120px`（iss-00589 の枠と同じ）。
- 描き直し（R-07）：書きかけの本文が 60 秒（要約の知らせ 6 回）の後も残り、iframe の読み込み 0 回。ほかの相手の増減でも 0 回。選んだ相手のブランチの変化と明暗の変化でだけ置き直し（title と `theme=dark`）。横の欄でも同じで、ページの URL は変わらない。
- 選び（R-02、R-05、F-02、F-03）：1人なら自動で開いて覚える。いなくなると知らせ（`gone:`）、同じ id が戻っても、別のタブに移って戻っても、戻る・進む・読み込み直し・欄の閉じと開き直し・欄から詳しい画面・欄の足の「新しいタブで開く」でも開かない。欄を閉じている間に A から B に入れ替わっても、開き直して B を自動で開かない。人が選び直すと開く。別の Scope に移ると iframe がなくなる（移りの待ちの間も 0）。詳しい画面で B を押すと、読み込みの待ち（4 秒に遅らせた）の間に A の iframe が外れる。絞り込みと今のタブの押しでは iframe が残り、読み込みが増えない。
- iframe の中の移り（F-08）：CDP で iframe の文書を別の相手の `/embed/agent?id=` に移すと、「選んだのと別のエージェントに移ったので閉じた」と出て iframe が外れ、「選んだエージェントに戻す」で戻る。移った先の文書の `GET /api/send/status` は応答の前に iframe ごと外れた（送る欄が使えるより前に外れた）。orca-web の iss-00037 で、埋め込みの中の親・子のリンクは新しいタブで開くようになり、同じ iframe への移りはなくなった（F-08 は二重の守り）。
- 届かないとき（R-06、F-01）：試しの orca-web を止めると、欄と詳しい画面のタブに「orca-web（http://127.0.0.1:8893）に届かない」と確かめること。構造の図とボードは動く。起動し直すと前の相手の iframe に戻る。
- 埋め込み（F-05）：`?embed=1` では埋め込みの知らせと新しいタブで開くリンク、iframe なし。
- `sendEnabled` が false（F-06）：iframe の中の orca-web が「設定で送信が止まっています」と示し、SpecDock は何も描き足さない。
- 帯：選んだ項目が帯の見える位置にあること（1440・1000・390 × 明暗 × 欄・詳しい画面の 12 通り）。
- iss-00592 との両立：欄の見出しの稼働の印と「Open」と、エージェントのタブ（帯と iframe）が並ぶ。
- 写し：直す前（`shots/before-*`）と後（`shots/after-*`）、1440・1000・390、明暗、欄と詳しい画面。1000 の上の帯の文字の重なりは直す前の版にもある既存の見た目（この Issue の外）。

## 最終品質ゲート

- 合格：`1094a048962f443658b01b369f09b291a47d6578`（campaign `iss-00593-fqg-2`、attempt 3）。closure は worktree の `.workbench/final-quality-gate/iss-00593-fqg-2/closure.md`。
- 主（quality-gate-reviewer opus / high）：pass（P3 1）、coverage complete。2人目（ChatGPT GPT-6 / Extra High、モデルの選択 verified）：P0・P1 なし（P2 3）。テスト：`make lint` pass、`uv run pytest` 3909 passed / 7 skipped / 0 failed。
- 経緯：fqg-1 attempt 1（787a05147）で主の FQG-001（P2）・FQG-002（P3）と2人目の P1 2・P2 2 → 統括の決定（msg_5490fcda8a19）で全部直す（仕様 round-8・round-9、863110f34）。根拠が変わったので fqg-2 に作り直し。fqg-2 attempt 1（863110f34）は全部の道が合格したが、origin/main に iss-00592（PR #597）が入ったので取り込み（f911dd4a8、790c93cac）、attempt 2（790c93cac）で2人目の P1 1（欄の足のリンクが agent を引き継がない）→ 1094a0489 で直し、attempt 3 で合格。分析は `.workbench/final-quality-gate/iss-00593-fqg-{1,2}/review-response.md`。
- 記録だけの P2/P3（後の Issue の候補）：closure.md の「P2/P3」を参照（FQG-003、欄を開き直した選びの足のリンク、スマホの構造の図の印の2回目の押し〈iss-00592〉、修飾キーつきの押しの覚え、agents が配列でない要約）。

## 逸脱と判断

- 2026-11-14、実装担当の割り当て（deviation: codex-start-failure）：S-01 の Codex の実装担当（gpt-6.1-sol / medium、dispatch `ctx_fdfd94981884`、launch.effective 一致）が、Orca の構造化のセッションの実行基盤の拒否（Codex のサンドボックスが、書き込み先の chat-scratch が外付けの置き場へのシンボリックリンクの下にあることを拒んだ。原因は本人の Mac の配置で、統括が本人に伝える）で、何も変えずに止まった。方針 §1 の5で統括に返し、統括の了承（msg_cea1846a58b7、iss-00593 に限る）で S-01〜S-03 を1つの Claude の実装担当（Opus 5.5 / high）にまとめた。区切りのレビュー C-1 は S-01 の後のまま。

- 2026-11-14、送信の確かめの宛先（統括の決定 msg_baf8fde71131、案B）：orca-web の send-test はどの Scope にも対応しないので、統括が用意した spec-dock の確かめ専用の worktree `iss-00593-send-test` のエージェントにだけ送った。片付けは統括。
- 2026-11-14、残るリスクの受け入れ（統括の決定 msg_c06a2f506afa、案1）と、その後の orca-web の iss-00037 のマージ（msg_97715dedcf36）：配る文書は「iss-00037 で埋め込みの中の同じ iframe への移りはなくなった」と書き、F-08 は二重の守り。
- 2026-11-14、帯の選んだ項目を見える位置へ送る直し（d55516770・f7439f621・a6d11d3ef）は、実機の写しで見つけた R-05 の意味の中の実装の直し（仕様は変えていない）。
- 2026-11-14、dogfood の写し `spec-dock/docs/reference_cli.md` を配る元と同じにした（787a05147。先例 f2ed8f268。タスク担当が初めに「写しは変えない」と誤って答えたのを正した）。
- 実装担当の裁量（steps.md）：欄の見出しと帯、詳しい画面の見出しとタブの帯も、文字列が同じなら書き換えない（risks の「目立てば見出しも比べる」の先取り）。開始のコミットの基準は一時の worktree で走らせ、片付けた。
- 既存の見た目（この Issue の外）：幅 1000 の上の帯で、リポジトリの選びと「構造の図」の文字が重なる（直す前の版にもある）。

## Outcome

PR #598（https://github.com/chemitaro/spec-dock/pull/598、head `1094a048962f443658b01b369f09b291a47d6578` = 最終品質ゲートの合格のコミット。記録のコミットはない）。CI：observable_ci PASS、merge_readiness READY（2026-11-14T17:14Z、worktree の `.workbench/coding-task/iss-00593/ci2.json`）。マージは統括が行う。

## Verification

- `spec-dock scope check iss-00593`：誤りなし、警告なし（手順の status はすべて done）。
- `make lint` pass、`uv run pytest` 3909 passed / 7 skipped / 0 failed（1094a0489）。実機の確かめは上の S-04 の節。

## Residual Risks / Follow-ups

- 最終品質ゲートの P2/P3（上の節と closure.md）。どれも別の相手のチャットを開く道ではない。
- orca-web の要約は、同じセッションを2つのエージェント（`chat:agent-session:…` と `structured-agent-session-…`）として返す（帯に2つ並ぶ。orca-web の側の課題）。
- 試しの組（ポート 18593・18594・8893）は、本人の確かめのために動かしたまま残す（止め方は統括への報告）。
