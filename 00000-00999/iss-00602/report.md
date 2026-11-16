---
種別: レポート（Issue）
ID: "iss-00602"
関連GitHub: ["#602"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

iss-00601 が調べたエージェントのタブと構造の図の印の押しの5点を直す。依頼書にあった「稼働しているエージェントをすべて印で出す」は、本人の判断（統括の伝え msg_0b6b7a71a08b、2026-11-16）で行わない。

## レビュー記録

- 仕様の合格（spec-review）：spec-reviewer Opus 5.5 / high の round-2 が pass（P0 0、P1 0、P2 0、P3 1）。結果 `.workbench/spec-review/iss-00602/round-2.json`、検査 `round-2.check.json`（validate-review.py exit 0）。worktree の HEAD `16f0cf122cb2053f4f4e24cf844f505f5274c30d`（clean）、canonical の HEAD `a1c4909ae1bef4c3b0b2d1b19fcd57b0772cbe3f`。
  - requirement.cue `e0411ab0c7eed66e45c2fb665dc6499b0c4b875f99d93a0c29a4fa935bc917ec`
  - design.cue `64663a12943c834f77d8dba58dbb2a54e91d0c098f84fb7bf14619066a846392`
  - plan.cue `f26f11dc01c7bcc10094667ec6e5379b10c5b6181730b23f1aba418aaa3e9509`
  - P3（記録だけ）：R-01 の受け入れの3つ目の「agent があれば keep を呼ばない」は、相手が agents にいるときの話（いなくなった相手は今のまま gone:<id> を keep）。実装担当への依頼書に読み方の注として渡した（意味は変えない）。
- round-1（範囲を絞る前の仕様、すべての印を出す部分を含む）：spec-reviewer が fail（P1 1、P2 2。どれもすべての印を出す部分の測りと CSS）。本人の判断でその部分を範囲から外したので、指摘は仕様から消えた（`.workbench/spec-review/iss-00602/review-response.md`）。
- **逸脱（本人の了承、統括の伝え msg_16d92aef2143、2026-11-16）**：仕様レビューの2人目（ChatGPT GPT-6 / Extra High、chatgpt-spec-review-strict）は、Oracle が Chrome（127.0.0.1:9223）のリモートデバッグの許可（Allow）を得られず止まったため取れなかった（1回目は node v16 で起動前に落ち、2回目と3回目はそれぞれ許可待ちのまま止めた。どれも ChatGPT への送信はしていない）。spec-reviewer の合格で進める。

## 実装担当の起動

- S-01：初めに Codex GPT-6.1 Sol / medium（dispatch ctx_b03d41a3750e、launch.effective：codex・gpt-6.1-sol・medium）を起動した。Codex は Orca の chat-scratch の書き込み先がシンボリックリンクの下にある環境の拒否（symlinked writable root）でふつうのコマンドを実行できず、仕様の確かめの読みだけで止まった。**逸脱（計画の取り決め、統括の了承済み）**：待たずに worker-stop し、HEAD が開始のコミット `16f0cf122` のままで未コミットがないことを確かめ、Claude Opus 5.5 / high（dispatch ctx_9613ad2614c4、launch.effective：claude・claude-opus-5-5・high）に切り替えた。

## 実装の記録

- S-01（`61c61cdbf`、親 `16f0cf122`）：D-01（graph.js の onTap で印の判定を2回目の押しより前に）、D-02（agentsState の fromLast と agentsTab の keep）、D-03（agents_logic.js の lastChoice と panel.js の足）、D-04（帯の捕捉の聞き手を修飾キーのない button 0 だけに）、D-05（scopeAgents で並びでない agents を invalid に数える）。テストを先に書き、直す前に意図どおりの理由で落ちることを確かめた（関わる3ファイルで 8 failed / 44 passed）。直した後、関わる7ファイルで 87 passed、`make lint` pass。新しい約束と食い違う今の目印を2つ直した（test_scope_agents の agents:null の worktree は invalid 1、帯の押しの呼び出しに button:0）。T-03 の欄の足のテストは、design の seam の test_dashboard_orca_views_js.py の PANEL_DOM ではなく、欄の偽の DOM と agents の世界がそろっている test_dashboard_agents_tab_js.py の PANEL の harness に置いた（実装担当の判断。確かめる中身は T-03 のとおり）。
- 区切りのレビュー C-1（code-reviewer Opus 5.5 / medium、範囲 `16f0cf122..61c61cdbf`、axis both）：pass、指摘0（`.workbench/code-review/iss-00602/c1-round-1.json`、validate-review.py exit 0）。
- S-02（`80d5aba3f`、タスク担当）：reference_cli.md（配る元と dogfood の写し）のエージェントのタブの節に、覚えから開いた相手を問い合わせに書くこと、欄の足のリンクが選びか覚え（`gone:<id>`）を持つこと、修飾キーつきの押しが元の画面の覚えを変えないこと、`orca-shape` に agents が並びでない worktree を数えることを書いた。static-inventory.json の sha256 を合わせ、v0.9.3 で配った版の sha256（`6b8066f2…`）を known_old_sha256 に足した（0.9.3 の利用者の installation update が、変えていない文書として扱えるように）。テスト T-06 を2件足した（test_issue593_agents_docs.py）。

## 実機の確かめ（S-03、タスク担当）

試しの組。常駐のダッシュボード（47800）と常駐の orca-web（8791）と、その設定には触れていない。

- 試しの orca-web：orca-web の main のチェックアウト（`373a2c7`）の `dist/` を、ポート 8902、`ORCA_WEB_READ_ORIGINS` に試しの SpecDock の 127.0.0.1 と tailnet のオリジン（18602・18603）、試し専用の `ORCA_WEB_SETTINGS_FILE`（`sendEnabled: false`）と `ORCA_WEB_SENDS_DIR` で起動。
- 試しの SpecDock：直す前は main `16f0cf122`、直した後は `80d5aba3f` の `git archive` から作った wheel を隔離した venv に入れ、道具の環境の状態の置き場の写し（サーバーの記録とログを除く）と一時の `XDG_CONFIG_HOME` の `config.json`（`orca_web.port` 8902）で、ポート 18602（前）・18603（後）、`--tailscale`。
- 確かめは headless Chrome（`--disable-features=MacAppCodeSignClone`、終わりに CDP の `Browser.close`）と CDP の台本で、iss-00602 の Scope（対応した worktree にエージェント2人：A＝`chat:agent-session:…`、B＝`structured-agent-session-…`。orca-web が同じセッションを2つに数える既知の件で、どちらもこのタスク担当のセッション）で行った。送信はしていない（`sendEnabled` は false。書きかけは入力欄の値を台本で置いただけ）。要約の差し替えは CDP の Fetch。

結果（直す前 → 直した後）：

| 点 | 操作 | 直す前（16f0cf122） | 直した後（80d5aba3f） |
|---|---|---|---|
| 1（R-01） | 欄で A を選ぶ → 欄を閉じて開き直す → 足の「詳しい画面」→ 帯の A を押す | 足のリンクに agent なし。押すと URL に agent が付き、iframe の読み込みが 3 → 4、書きかけが消えた | 足のリンクに `agent=A`。押しても URL は同じ、読み込みは 3 → 3、書きかけ「書きかけ iss-00602」が残った |
| 2（R-02） | 欄で A を選ぶ → 概要のタブ → 欄を閉じる → A がいなくなる（B だけ）→ 欄を開き直す（概要のタブ）→ 足の「新しいタブで開く」をエージェントのタブで開く | 足のリンクに agent なし。新しいタブで **B が自動で開いた** | 足のリンクに `agent=gone:A`。新しいタブは iframe なし、知らせ `orca-agent-gone` |
| 2'（参考、P3 FQG-001） | 上と同じだが欄を閉じない（欄の Map に人の選び A が残る） | 足のリンクに `agent=A`。新しいタブは `orca-agent-gone`（B は開かない） | 同じ（Map が先。iss-00593 からの動きで、安全側） |
| 3（R-03） | 390px：箱を押して選ぶ → 同じ箱の印を押す → 印の外を押す | 印の押しで詳しい画面へ移った | 印の押しでは道が変わらず、欄のタブが `agents`。印の外の押しで詳しい画面へ移る |
| 4（R-04） | 欄で A を開く → 帯の B を Cmd で押す（新しいタブが開く）→ 欄を閉じて開き直す | 開き直すと **B が開いた** | 開き直しても A のまま |
| 5（R-05） | 詳しい画面で A を開く → 要約の worktree の agents をオブジェクトにする → 戻す | 知らせ `orca-agent-gone`、URL が `agent=gone:A` になり、戻しても A は開かない | 知らせ `orca-shape`、URL は `agent=A` のまま。戻すと A の iframe に戻る |

- 写し：直す前と後の、欄のエージェントのタブと詳しい画面のエージェントのタブを、1440・1000・390 × 明暗で撮った（各12枚）。直した後の見た目は直す前と同じ（この Issue は見た目を変えない）。
- 台本と記録（result.json、写し）は worktree の `.workbench/iss-00602/real/` に写した。

## Outcome

## Verification

## Residual Risks / Follow-ups
