---
種別: レポート（Issue）
ID: "iss-00620"
関連GitHub: ["#620"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格（P0・P1 なし、P2 4）。`.workbench/spec-review/iss-00620/round-1.json`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00620`）。P2 4件（rowsOf の名前の衝突、F-03 の歯止めの戻し方、ほかの印の折り返し、幅0の子）はすべて実装の前に反映した（`review-response.md`）。
- round-2（同じレビュアー）：**合格**。P0〜P3 すべて0。結果 `round-2.json`、検査 `round-2.check.json`（valid、status pass、reviewed_sha `d9bb6164d`）。
- round-2 で合格した文書の sha256（後に改めた）：requirement.cue `ae0cf137fdd77381adc0690b2fb4aa2c329eecf6c914232bc51b40fd91e8769c`、design.cue `60f3afdd0ec7cd8f31e50364165ec9bd1b50aba6af0f631a6602f683e70dd2fc`、plan.cue `9c6fbf42da033d142dae3bbfaa94e955a9e5cd7ba47615051c63dd6d955209c2`。

- 仕様の変更1（本人の決定、2026-11-17、統括 msg_c07bd9a3a2d9）：稼働の印は、エージェントがいればいつもほかの印の下の専用の行に左寄せで置く（先の「1行目に収まれば右寄せ」を改めた）。round-3 は、そのレビュー中に次の変更が来たので止めた（評価なし）。
- 仕様の変更2（本人の決定、2026-11-17、統括 msg_a0d7a1c08fcc）：『後に続く』の数は構造の図・凡例とも今のまま残す（dnMark を消すことを範囲から外した）。
- round-4（spec-reviewer opus / high、新しいレビュアー、先の P2 を prior_findings で再確認）：合格（P0・P1 なし、P2 1：枠の置き場を `.gx-fh` の外に出すと、押したときの扱いと淡くする規則から外れる）。反映した（枠の `.gx-agents` は `.gx-fh` の最後の子）。
- round-5（同じレビュアー）：**合格**。P0〜P3 すべて0。`round-5.json`、`round-5.check.json`（valid、pass、reviewed_sha `5de15a1`。実装担当の WIP コミットで、仕様の外）。
- **合格した文書の sha256**：requirement.cue `26055baba339f8d5bc6349578f15c9ad40ea32ac91885a384fd9b1974b19ac5d`、design.cue `e30e8098ad35724eb9674a16b330cd534352b18f6bcf34ea4115498707837a18`、plan.cue `9164afc4a986a987c588a01b09200a96c22d148794428e3c40e6b31d3bb099d4`。

## 実装の記録

- 逸脱 codex-symlink-refusal：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_b3e45e72d5e8、launch codex / gpt-6.1-sol / medium）は chat-scratch の writable root の symlink で手元のコマンドを起動できず、変更なしで止まった。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium（dispatch ctx_ed9b9a3801df、launch claude / opus / medium）に切り替え、impl-claude と同じ値なので S-01〜S-04 を1つのセッションにまとめた。

- 実装担当：Claude Opus 5.5 / medium（dispatch ctx_ed9b9a3801df）。worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00620`、branch `chemitaro/iss-00620`。記録 `.workbench/implement/iss-00620/start.md`。
- 基準（開始のコミット `d9bb6164d`）：graph_js・graph_range・graph_toolbar・small_screens の 89 passed、`make lint` 合格。
- 仕様の変更の間に、書きかけのテストを WIP `5de15a195` で止めた（src は変えていない）。合格した round-5 の sha256 を確かめて再開した。
- S-01（Red）`0a28a506b`：`tests/unit/presentation/test_dashboard_graph_marks_rows.py` と `tests/js/dashboard_graph_check.mjs` の marks の口。直す前で 6 failed（定数・markRows・高さ・tframe・枠の見出し・nodeMarkRows）、T-03・T-04 と digest の比較は通った。
- S-02（Green）`f5c462c2e`、型の直し `996017e02`：layout.js に MARK_ROW・MARK_INSET・markRows・nodeMarkRows と、box・tbox・frame の高さ、flatten の rows。既存の `rowsOf` は変えていない。
- S-03 `9e795edaa`：graph.js（measureMarks・checkRows・ResizeObserver・V.rowsRedo・`.gx-agents`・edgeAudit の markOverflow）、orca_marks.js の `"all"`、graph.css。既存の `test_slot_styles_stay_shared_and_leave_the_marks_to_orca_web` は、D-05 が決めた graph.css の3つの規則（`.orca-mark`・`.orca-marks` を名指す）だけを許すように直した。『後に続く』（dnMark・凡例・aria-label・marks.js・golden）は変えていない。
- S-04：static-inventory.json に dashboard の資産はなく、sha256 の変更なし。`make lint` 合格、`uv run pytest` 3988 passed / 7 skipped（`9e795edaa`）。
- origin/main（#618 は開始時に含む、#619 iss-00613）を `5b170ecb7` で取り込んだ（衝突なし）。

## 最終品質ゲート

- キャンペーン `.workbench/final-quality-gate/iss-00620-fqg-1/`（quality-gate-reviewer opus / medium、second opinion なし、範囲 `d9bb6164d..5b170ecb7`、観点 functional-correctness・requirements-closure・test-adequacy。plan の `ui-behavior` は契約の観点にないので functional-correctness の中で見て、実機は S-05 で取った）。
- attempt 01（`5b170ecb7`）：review lane 合格（P0〜P3 0、coverage complete）。test lane は `make lint` exit 0、`uv run pytest` 1 failed / 4009 passed / 7 skipped。落ちたのは iss-00611 と同じ揺れるテスト `tests/integration/test_issue413_native_lock.py::test_terminated_owner_releases_native_start_lock_without_pid_recovery`（`.git` の走査と git の自動 maintenance の `maintenance.lock` の競合）。この変更は触れていない。単独で3回とも通った（`review-response.md`）。コードを変えずに同じコミットで test lane をやり直した（attempt 02）。
- attempt 02（同じ `5b170ecb7`）：`make lint` exit 0、`uv run pytest` exit 0（4010 passed / 7 skipped）。**合格**。closure `.workbench/final-quality-gate/iss-00620-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00620`）。P2・P3 なし。

## 実機の写し（S-05、タスク担当）

- 開始のコミット `d9bb6164d`（前）と `5b170ecb7`（後）を `git archive` から wheel にし、別々の隔離した venv と、この PC の状態の置き場の写し（`.workbench/iss-00620/state-{before,after}`）、`XDG_CONFIG_HOME` の試しの設定（orca_web.port 18799）で、`spec-dock dashboard serve --offline --tailscale` を前 18621・後 18622 で立てた。常駐の 47800・8791 と道具の環境には触れていない。
- 試しの orca（`.workbench/iss-00620/tools/fake_orca.py`、tailnet 100.85.74.8:18799）：常駐の orca-web（8791）の要約と部品を読むだけで中継し、housing-lifecycle の worktree e401-domain（iss-00407）に6人、e402-floorplan（iss-00417）に3人、i404-wireframe（iss-00412）に1人、spec-dock の iss-00620 に2人（本人の写しの iss-00613 と同じ形：PR・worktree・『後に続く 4』の箱）のエージェントを持たせた。部品は orca-web の実物。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で前・後 × 1440・390 × 明暗。spec-dock は「いま」、housing-lifecycle は「全体」（3つの Issue は終わっている）と、親の Epic の focus で写した（スクリプト `.workbench/iss-00620/tools/shoot.mjs`・`shoot-focus.mjs`、数字は [result.json（全体）](artifacts/20261116t182051z--result.json)、[result.json（focus）](artifacts/20261116t182051z-01--result.json)）。

| 箱 | 前 | 後 |
|---|---|---|
| spec-dock iss-00620（2人、doing、後に続く 4） | 高さ 88、印2つが下の段に並び、右の縁を1つはみ出す | 高さ 108、下の段は『後に続く 4』のまま、2人がその下のエージェントの行に収まる |
| housing iss-00407（6人） | 88、印1つと『+5』 | 128、6人すべてが2行に折り返す |
| housing iss-00417（3人） | 88、印1つと『+2』 | 108、3人が1行 |
| housing iss-00412（1人） | 88 | 108、1人がエージェントの行 |

- 後のすべての写し（16 + 12枚）で、edgeAudit の boxHits・ownHits・overlaps・diagonal・portShare・failed・missing が0、drift 0、**markOverflow 0**、稼働の印の右・下のはみ出し0、ブラウザーのエラー0。前の spec-dock の 1440 は boxHits 5（はみ出しとは別の、前のコード）。
- 『後に続く』は後でも構造の図の箱（iss-00620 の 4）と凡例に残り、ボードにも残る（spec-dock 5件、housing-lifecycle 10件）。
- R-06：後の 1440 明で、12秒（次の要約）待っても、箱の要素は作り直されなかった（spec-dock・housing とも `kept` true）。
- 写し：[前 iss-00620](artifacts/20261116t182048z--before-spec-dock-1440-light-iss-00620.png)、[後 iss-00620](artifacts/20261116t182049z--after-spec-dock-1440-light-iss-00620.png)、[後 spec-dock 1440 暗](artifacts/20261116t182049z-01--after-spec-dock-1440-dark.png)、[後 spec-dock 390 暗](artifacts/20261116t182049z-02--after-spec-dock-390-dark.png)、[後 ボード](artifacts/20261116t182049z-03--after-spec-dock-1440-light-board.png)、[前 iss-00407](artifacts/20261116t182050z-01--before-epic-00401-1440-light-iss-00407.png)、[後 iss-00407 暗](artifacts/20261116t182050z--after-epic-00401-1440-dark-iss-00407.png)、[後 epic-00401 390 明](artifacts/20261116t182050z-02--after-epic-00401-390-light.png)、[後 epic-00416 1440 明](artifacts/20261116t182050z-03--after-epic-00416-1440-light.png)、[後 epic-00403 1440 暗](artifacts/20261116t182050z-04--after-epic-00403-1440-dark.png)。
- 試しの URL（本人の確かめ用、確かめまで残す。後のコード）：tailnet `http://100.85.74.8:18622/`（spec-dock は `/r/github.com/chemitaro/spec-dock/`、housing-lifecycle は `/r/github.com/chemitaro/housing-lifecycle/?focus=epic-00401` を「全体」で）。試しの orca は 18799。止め方：`kill $(lsof -tnP -iTCP:18622 -sTCP:LISTEN) $(lsof -tnP -iTCP:18799 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。前の 18621 は写しの後に止めた。

## Outcome

構造の図の箱と枠で、対応した worktree のエージェントを上限なしにすべて、ほかの印の下の専用の行（`.gx-agents`）に左寄せで出し、箱の幅で折り返して、行1つにつき 20px 箱（入れ子の枠では見出し）を伸ばすようにした。エージェントのいない箱は今の高さのまま。配置は、描いた部品の実寸から行の数を決め（layout.js の markRows・nodeMarkRows）、行の数が変わったときだけやり直す。『後に続く』の数は本人の決定で今のまま残した。ボードと横の欄の印（上限4）は変えていない。

## Verification

- 仕様のレビュー合格（round-5、指摘0。本人の決定2つを含む）。
- 最終品質ゲート合格（`5b170ecb7`、review 指摘0、make lint・全体の pytest 4010 passed）。
- 実機：前後 × 1440・390 × 明暗で、後の edgeAudit の違反0・markOverflow 0・ブラウザーのエラー0。エージェント1人・3人・6人と2人（本人の写しと同じ形）の箱がすべて収まる。

## Residual Risks / Follow-ups

- 揺れるテスト `tests/integration/test_issue413_native_lock.py::test_terminated_owner_releases_native_start_lock_without_pid_recovery`（git の maintenance.lock との競合）は iss-00611 から続く。別の Issue で、走査で消えたファイルを許すよう直す提案。
- MARK_ROW（20）と MARK_INSET（26）は graph.css の値の写し。CSS を変えるときは一緒に直す（コメントで互いを指す）。
- 印の並び順は orca-web の部品の順（orca-web の iss-00043 で『指揮の上流が左』に改まる予定。SpecDock は並べ替えない）。
- 配布の手引き（リリースノート）は 0.9.5 のリリースの Issue で「エージェントの行」を書く。
- 試しのサーバー 18622・18799 は本人の確かめまで残す。
- PR https://github.com/chemitaro/spec-dock/pull/622（head `5b170ecb7`）。CI（Actions と Commit Status）は observable_ci PASS、merge_readiness READY（`.workbench/iss-00620/pr-checks.json`）。マージは統括が行う。
