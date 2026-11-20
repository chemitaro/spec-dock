---
種別: レポート（Issue）
ID: "iss-00674"
関連GitHub: ["#674"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 開始のコミット：`83b8ee95f8fbcc06b601fd5ab3a02018b0995ee4`（origin/main、PR #671 のマージ）。
- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし＝standard の既定）：round-1 合格（P0 0、P1 0、P2 2）。P2 2件を受け入れて直した（この worktree の `.workbench/spec-review/iss-00674/review-response.md`）。round-2 **合格**（P0 0、P1 0、P2 0、P3 1：design の goals の言い回しが compatibility と食い違う。阻害しないので直さない）。結果は `.workbench/spec-review/iss-00674/round-{1,2}.json` と `.check.json`（reviewed_sha `83b8ee95f`）。
- **合格した文書の sha256**（round-2）：requirement.cue `9d931c16d23798c8362306ef420775140ab7910d4f05da588ee33c9cc39da5bf`、design.cue `410669d683bccb355a19735384ac007f4ef668f1573dabce575bafdc42184728`、plan.cue `2c76ce806c372150222d732dc3c57b771374d72a4dd01bc41e2f9d89f5eea08c`。

## 実装の記録

- 実装担当：Claude Opus 5.5 / medium（plan の `execution.sessions.impl` と一致）。worktree `chemitaro/iss-00674`、開始のコミット `83b8ee95f`。
- 基準（開始のコミット、別の clone で実行）：`make lint` 合格、`uv run pytest` 4355 passed / 7 skipped。既にあった失敗はなし。
- S-01（`d92b7e079`）：`views/_shared/agents_logic.js` に `agentTypeLabel(marks, agentType, fallback)` を足した（D-01。import なし、例外は中で受け止める、`hasOwnProperty` で継承の鍵を除く、`other`・`none` は使わない）。T-01 は `tests/unit/infra/test_dashboard_agents_logic_js.py::test_agent_type_label`。先に失敗（`L is not a function`）を見てから実装した。`uv run pytest tests/unit/infra/test_dashboard_agents_logic_js.py` は 10 passed（純粋さのテストを含む）。`make lint` は合格。
- S-02（`dfcec8db5`）：5か所を `agentTypeLabel` に通した（D-02）。`agentFrame(…, marks = null)`、`countTitle(item, marks = null)`、`layersHtml(model, marks = null)`、`itemHtml(it, marks)` を変え、`agents_tab.js`（選びと frame）、`command_view.js`（`renderAgentPanel` の見出しと frame、`renderWorktreePanel` の一覧）、`graph.js`・`allgraph.js` の `drawCommand`（`ctx.orca?.marks?.() ?? null`）から部品を渡す。T-02 のテスト：
  - `test_dashboard_agents_logic_js.py::test_agent_frame_names_the_kind_from_the_component`（agentFrame の title）
  - `test_dashboard_agents_tab_js.py::test_the_strip_and_the_frame_name_the_kind_from_the_component`（タブの選びと iframe の title。表のある部品／null／`iconKey` が例外を投げる部品）
  - 新しい `tests/unit/presentation/test_dashboard_agent_type_names.py`：`countTitle` の node のテスト、構造の図の画面（worktree の詳細の欄の一覧、指揮の帯のエージェントの詳細の欄の見出しと iframe の title、`next` の数の札の title）、全体の図の画面（数の札の title と詳細の欄の見出し）。どれも『Antigravity』と、部品に表がないときの `antigravity` の両方を確かめる。
  - 画面のテストの補助：`tests/js/fake_dom.mjs` に `giveAgentNames(orca)` を足し、`dashboard_graph_command_screen.mjs`・`dashboard_allgraph_command_screen.mjs` は run の `orca.names` が true のときだけこれを呼ぶ。構造の図の画面の写しの iframe に `title` を足した（加えただけ）。
  - 実装を一時的に戻すと新しいテストのうち名前を期待する6件が落ちることを確かめた（Red）。
  - 節目 `uv run pytest tests/unit/infra/ tests/unit/presentation/ -k "dashboard"`：591 passed。`make lint` は合格。
- S-03（コードの変更なし）：HEAD `dfcec8db5` で `make lint` 合格、`uv run pytest` 4365 passed / 7 skipped（43分20秒）。基準より10件多いのは足したテスト。
- `static-inventory.json`：ダッシュボードの資産は載っていないので変えていない。

## 逸脱と判断

- 部品を渡さない今のテストは、どれも変えずに通った。今の偽の部品（`buildMarks` などだけで `AGENT_ICONS`・`iconKey` を持たない）は、design の F-01 どおり生の文字列になる。生の `claude` を期待しているテストも、そのため直す必要がなかった（design の risks のテストの直しは起きなかった）。
- `renderWorktreePanel` の再描画の印（sig）に部品は入れていない。design の D-02（部品が後から変わる場合の描き直しは足さない）どおり。
- 仕様から外れたところはない。

## 実データの確かめ（S-04、T-03、2026-11-20）

- 版：spec-dock は作業ブランチの `dfcec8db5`（S-02 まで）を、この worktree から `uv run spec-dock dashboard serve --port 8797` で、写した状態の置き場（scratch）で動かした。orca-web は main `4ad7471`（PR #70、iss-00066 のマージ）の常駐（127.0.0.1:8791）。`/embed/agent-marks-icons.js` に `antigravity`（label『Antigravity』）と `gemini`（label『Gemini』）がある。
- 常駐の orca-web は、部品の読み込み（CORS）を常駐のダッシュボードの起点（ポート 47800）にだけ許す。試しのダッシュボード（8797）から部品を読むために、読むだけの小さな中継（GET だけ、127.0.0.1:8798 → 8791、試しの起点を許す）を scratch に置き、試しのダッシュボードだけに `XDG_CONFIG_HOME`（scratch）の `config.json` で `orca_web.port: 8798` を渡した。本人の設定のファイル、orca-web の設定、常駐のダッシュボードは変えていない。確かめた後に、試しのダッシュボードと中継を止めた。
- 観測（Orca の内蔵ブラウザー、orca-web のリポジトリの構造の図、未対応の行の worktree `chemitaro/send-test-agy`。Antigravity のエージェント2つ。送信はしていない）：
  - worktree の詳細の欄のエージェントの一覧：2つとも『Antigravity』（今までは `antigravity`）。
  - エージェントの詳細の欄の見出し：『Antigravity · chemitaro/send-test-agy』。
  - 横の欄の iframe の title：『エージェント：Antigravity・chemitaro/send-test-agy』。
  - 比べ：常駐のダッシュボード（0.9.9、47800）でも同じ worktree に2つのエージェントが出る（部品の読み込みが合っていることの対照）。
- 実データで見られなかった所：エージェントのタブの選び（Antigravity のエージェントが、Scope を選んだ worktree にいない）と、未対応の行の数の札の title（指揮の組がなく、数の札が出ていない）。この2つは node のテスト（T-01・T-02、合成の部品）で確かめる。

## Outcome

## Verification

## Residual Risks / Follow-ups
