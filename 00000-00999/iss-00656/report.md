---
種別: レポート（Issue）
ID: "iss-00656"
関連GitHub: ["#656"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし。同じレビュアーで続けた）：round-1 fail（P1 1・P2 2・P3 2）、round-2 fail（P1 1：wrap-reverse の送り）、round-3 合格（P2 1）、統括の追加（R-09、msg_0358bd3f97b4）の後の round-4 **合格**（P0 0、P1 0、P2 1、P3 1。reviewed_sha `afe2df5c2`＝iss-00650 のマージ後の origin/main）。結果はこの worktree の `.workbench/spec-review/iss-00656/round-{1,2,3,4}.json` と `.check.json`、対応は `review-response.md`。
- **合格した文書の sha256**（round-4）：requirement.cue `9bdd0e9e516691f0b68205bc6b1d0537856465d3b758c70a41122ed52a799a91`、design.cue `b13005c09856a9ba33700d8e9bcac89328322adeb97947a3818860b97fcbe818`、plan.cue `e86defd4a9c2b9d8fc555d30e8aac033de35105700ecf2535e54bfcfb5fb7492`、explanation.html `8383f56b3f24c061150acad84251cc32ea9e1bf08a107b4218fc4aa2b7ddea86`。Epic epic-00573 の R-06・D-06・slice `iss-00656` も同じ回で読まれた。
- P2 の扱い（round-3・4 で同じ指摘。止めない。文書は変えず、実装担当への申し送り）：`fitHead` を、D-07 の3つの時に加えて、スマートフォンの段の切り替え（`release`・`pointercancel`・取っ手のタップの `applySnap()` の後。全体の段で `is-stacked` を外し、戻したら測り直す）と、見出しの幅の変化（Orca で開くの遅れた表示など。`.pn-head` の `ResizeObserver`、ないときは今の3つだけ）でも呼ぶ。T-02 に、段の切り替えと見出しの幅の変化で送りが付け直されることを足す。
- P3 の扱い：D-08 は、帯の欄（`renderAgentPanel`）の描き直し（別のエージェントへの切り替え、明暗の変化）でも全面を保つ（今は半分に戻る）。片付けの候補と同じ考え（開いている欄の描き直しで段を変えない）なので受け入れ、統括に報告する。直しは構造の図（`graph.js`）の片付けの候補にも効く。
- **round-5 合格**（統括の決定 msg_985d75724b1a による R-01 の受入[2]の直しの後。P0 0、P1 0、P2 2、P3 1。reviewed_sha `ebbca611f`）。合格した sha256：requirement.cue `90322507e67a2b14d41f88a7dfdd988791063620b52625ff55a9dc2e147ccfa6`、design.cue `b13005c09856a9ba33700d8e9bcac89328322adeb97947a3818860b97fcbe818`（round-4 と同じ）、plan.cue `2eaf04f9888e3297918d7249aeadb0f79f8a2408841db9e370ab4bd79ed1c12c`（実装担当の status の書き換えだけ）。新しい P2（D-06・T-04 の「1000×800 の1行目が1行」が直した受入[2]と合わない、1280 の1行を数で確かめる手順がない）は、S-04 で要件（R-01 の受入[2]）に従って判じ、1280×800 の1行目の高さも数で書くことで扱う（文書は変えない）。
- 申し送り（指摘でない懸念）：1000×800・祖先2つ・印2つで1行に収まる余地は小さい見込み。S-04 の実機で R-01 の受入[2]を測り、届かなければ統括に問う。

## 実装の記録

- 実装担当 impl-claude（Claude Opus 5.5 / medium）。開始のコミット `afe2df5c2af6c54672a7727e03e1a44525bf47ec`。基準（開始のコミット）：`make lint` 合格、S-02 の節目のテスト 113 passed（記録は worktree の `.workbench/implement/iss-00656/`）。
- S-01（`7395f9148`）：T-01（`headerBand` の表、4件）を先に書いて落ちることを確かめ、`panel_logic.js` に D-01 の `headerBand` を入れた。`uv run pytest tests/unit/infra/test_dashboard_panel_logic_js.py` 12 passed。
- S-02（`ebbca611f`）：T-02・T-05 を新しい `tests/unit/infra/test_dashboard_panel_head_js.py`（`tests/js/fake_dom.mjs` の偽の DOM で `createScopePanel` を描く）に先に書き、12件が落ちることを確かめてから、D-02（見出し）・D-03（`open`・`frameBar`・`tabOpenLink`・欄と詳しい画面のタブの行）・D-07（`headOverflows`・`fitHead`）・D-08（`hide()` の `keep`、`show()` の半分）・D-04（CSS）を入れた。T-03 は `test_dashboard_scope_tabs_js.py` に足した（`tabOpenLink` のエスケープ、文書の `open` の端、詳しい画面のタブの行、CSS の静的な検査）。節目のテスト（plan.cue の8ファイル＋新しいファイル）135 passed、`tests/unit/presentation/test_dashboard_{allgraph,graph}_command_screen.py` も通る。`make lint` 合格。
- 直した今のテストの期待（見出しとタブの行の形の変化によるものだけ）：
  - `test_dashboard_orca_views_js.py`：偽の欄の `PARTS` に `.pn-crumb`・`.pn-tabopen`、偽の aside の `classList.contains`（D-08 の `isShown()` を `show()` が読むため）。見出しの HTML の先頭に `.pn-crumb`、`.pn-hl` に `pn-merge` がない、書き込みの数に `.pn-crumb` の列を足した。
  - `test_dashboard_agents_tab_js.py`：同じ `PARTS` と `classList.contains`。
  - `test_dashboard_scope_tabs_js.py`：説明資料の中身が枠だけ（`sd-framebar` と印がない）、文書の帯に印がなく新しいタブの行き先は `open(env)`。
  - `test_dashboard_state_marks.py`：帯（`.pn-why`）に状態の印（`stateMark`）がない（R-03）。札（`stateChip` の motion）は今のまま。
  - `tests/js/fake_dom.mjs`：`scrollWidth`（`sizes` の鉤、なければ `clientWidth`）を足した。


## 逸脱と判断

- S-02：申し送り1（P2）のとおり、`fitHead` を `refreshOrca()` の終わり（`draw()` は `refreshOrca()` で終わるので、D-07 の『`draw()` の終わり』はこれで満たす。今の静的なテスト『draw は refreshOrca() で終わる』を変えないため）、窓の大きさの変化、取っ手のタップ・`release`・`pointercancel` の `applySnap()` の後、`ResizeObserver` で呼ぶ。`ResizeObserver` は `.pn-head` に加えて `.pn-crumb` も見る（Orca で開くの遅れた表示では `.pn-head` の大きさは変わらず、パンくずの幅だけが変わるため）。送りの付け外しで大きさが戻るので、知らせは繰り返さない。
- S-02：申し送り2（P3）：帯の欄（`renderAgentPanel`）の描き直しでも `hide()` が `keep` になり段を保つ。T-05 は片付けの候補の形で確かめた（帯の欄も同じ道筋）。
- S-02：1行目で縮まない部品を確かにするため、`.sd-pn .pn-hl > *` と `.sd-pn .pn-head > .iconbtn` に `flex: none` を足した（D-04 の『札・印・Orca で開く・閉じるは縮まない』）。祖先のボタンの縮みの重み 4 は `flex: 0 4 auto`、`.pn-self` は 1。
- S-02：T-03 のうち `test_dashboard_scope_tabs_js.py` に足した4件は、欄の T-02（先に落ちることを確かめた）の後、実装と同じ単位の中で書いた（中身は欄の印の形と同じ口 `open`・`tabOpenLink` の端）。新しいファイルの14件のうち2件（片付けの候補の見出しに送りが付かない、閉じた後は半分で開く）は今の振る舞いを固定する回帰のテストで、Red の時から通る。
- S-02：祖先のボタンの title は『<ID> <題名>』（R-01）。スマートフォンの全体の段の題名は `display: block` と `-webkit-line-clamp: none` で1行に戻す。
- S-01：`headerBand` の `merge` は `MERGE_WORDS` の鍵（`needs_fix`・`mergeable`）だけを値として返し、ほかはすべて `null`。理由の文は `String(…).trim()` で読む（`reason` が null・text がない場合も空として扱う。F-01）。

## Residual Risks / Follow-ups
