---
種別: レポート（Issue）
ID: "iss-00601"
関連GitHub: ["#601"]
最終更新: "2026-11-15"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

iss-00593 の最終品質ゲートで「記録だけ」とした5点（主の P3 1、ChatGPT の P2 4）を、main `16f0cf122` の `src/spec_dock/assets/dashboard/` で読み直した。5点とも、コードの筋道の上では本当に起きる。どれも「別の相手のチャットを開く」「別の相手に送る」道ではない（安全側に倒れる）。ただし2点（FQG-003、スマホの印の2回目の押し）は人が普通にする操作で起き、1点（欄の足のリンク）は小さな条件で R-05 の意図に反しうる。直し方はどれも小さく、まとめて1つの Issue（数十行と node のテスト）で直すのを推奨する。

調べの方法と限り：

- 読んだもの：iss-00593 の report.md、iss-00592 の report.md（Residual Risks は空。iss-00592 の分は iss-00593 のゲートが見つけた「スマホの印の2回目の押し」1点）、`agents_logic.js`、`agents_tab.js`、`panel.js`、`scope_tabs.js`（`pageEnv`・`panelEnv`）、`app.js`（`navigate`・`dropAgentFrames`・`interceptLinks`）、`views/graph.js`（`onTap`・`goDetail`）、`views/board.js`（`onCardClick`）、`core/orca.js`、`core/orca_match.js`。
- 指摘の原文：closure.md は iss-00593 の worktree ごと消えていたので、iss-00593 のタスク担当のセッションの記録（Claude Code の会話の記録）から、fqg-2 の review-response.md と closure.md に書いた文を読み戻した。
- 再現：純粋な部分（項目5、項目1・2の「last から来た選びは remember されない」）は、スクラッチの node で `agents_logic.js` を呼んで確かめた（下に結果）。画面の操作（クリック、移り、スマホの幅）は**コードを読んだ筋道だけで、実機では動かしていない**。

## 5点の調べ

### 1. FQG-003：詳しい画面で、last から開いた相手を帯でもう一度押すと iframe が置き直される（P3、主）

- (a) 起きるか：**起きる（コードの筋道）**。`agentsState` は `wanted = env.param("agent") ?? mem.last`。last から来た A が agents にあれば `pickAgent` の規則3で `remember` は null（node で確かめた：2人のうち A を last から選ぶと `remember null, selected A`）なので、詳しい画面の URL に `agent` が書かれない。2人以上のとき帯は switch で、選ばれた A も `data-nav href="…agent=A"` のリンク。押すと `interceptLinks` → `navigate` で `target.params.get("agent")`（A）と `before.params.get("agent")`（null）が違うので `dropAgentFrames()` が A の iframe を外し、次の描きで置き直す。
  - 筋道の例：横の欄を閉じて開き直す（`hide()` が `params` を空にするので、欄は last の A を開くが params に agent がない）→ 足の「詳しい画面」（agent なし）→ 詳しい画面は last の A を開く → 帯の A を押す。ほかに、agent のない道（検索や親の道筋から同じ Scope の agents のタブへ来る）でも同じ。
- (b) 影響：人が今の相手を押しただけで、そのチャットの入力欄の書きかけが消える。相手は変わらない。design の D-06「Scope も agent も変わらない移り（今の相手をもう一度押す）では外さない」に反する。
- (c) 直し方：last から来た選びで相手が開いたら、`env.keep("agent", selected.id)` で書く（詳しい画面は `replaceParam` で URL に、欄は params に入る）。`agents_tab.js` の `agentsTab` に数行（`wanted` が param から来たか last から来たかを state に持つ）。node のテスト（`test_dashboard_agents_tab_js.py`）を1〜2件。項目2と同じ根なので一緒に直る。別案として `navigate` の比べで「今の route の agent がなく、mem.last が target の agent と同じ」を同じとみなす方法もあるが、app.js が agents の覚えを知ることになるので勧めない。
- (d) 推奨：**直す**（小。項目2と1つの直し）。

### 2. 欄を開き直したとき、last から戻した選びが足のリンクに付かない（P2、ChatGPT）

- (a) 起きるか：**起きる（コードの筋道）**。`panel.js` の足は `params.get("agent") ?? null` を使う。`hide()` は `params` を空にし、`mem` は同じ Scope の間は残るので、開き直した欄は last の A を開くが、項目1のとおり params に入らない。足の「新しいタブで開く」は agent のない URL になる。
  - A がまだいて B もいる：新しいタブは新しい `mem` なので「エージェントを選ぶ」（別の相手は開かない。ChatGPT の書いたとおり）。
  - A がいなくなり B だけが残る：agents のタブを開いていれば `pickAgent` の規則2が `gone:A` を `keep` するので、足に付く（安全）。**ただし欄のタブが agents 以外（概要など）のとき**は `agentsTab` が描かれず `pickAgent` も呼ばれないので、params に `gone:A` が入らない。足の「新しいタブで開く」から agents のタブに移ると、新しいページの `mem` は空で agents が B だけなので、規則4で B が自動で開く。これは R-05（いなくなった後に残った相手を自分で開かない）の意図に反する（コードを読んだ筋道。実機では確かめていない）。
- (b) 影響：多くは「選ぶ」と出るだけの手間。上の狭い条件では、新しいタブで残った相手 B が自動で開く（B に送るには人が本文を書いて送る操作が要るので、すぐに誤送信にはならないが、R-05 の守りが新しいタブで抜ける）。
- (c) 直し方：項目1の `keep` に加えて、足の agent を `params.get("agent") ?? lastChoice(mem, scope.id)` にする（`lastChoice` は同じ Scope の last が `mem.gone` にあれば `gone:<id>`、なければ `<id>`）。`agents_logic.js` に小さな純粋な関数1つと、`panel.js` の足の1行。node のテスト1〜2件。
- (d) 推奨：**直す**（小。項目1と同じ Issue）。

### 3. スマホの構造の図で、選んだ箱の稼働の印を2回目に押すと詳しい画面に移る（P2、ChatGPT。iss-00592 の graph.js）

- (a) 起きるか：**起きる（コードの筋道）**。`views/graph.js` の `onTap` は、`isPhone() && V.sel === id` のとき `goDetail(id)` して return する。その判定が `.sd-orca`（印）の判定より前にあるので、すでに選んだ箱の印を押すと `preferTab("agents")` に届かず、`goDetail` が `s.path`（tab なし＝既定のタブ）へ移る。1回目（まだ選んでいない箱）は `select` の後に `preferTab` が呼ばれるので正しい。ボード（`board.js` の `onCardClick`）には2回目の押しの規則がなく、起きない。
- (b) 影響：スマホで、欄を見ていて「この箱のエージェントを見よう」と印を押すと、欄の agents のタブではなく詳しい画面の概要に飛ぶ。iss-00592 の D-03（印を押すと agents のタブ）に反する。戻る操作が要るだけで、データや送信には関わらない。
- (c) 直し方：`onTap` で、印の押しの判定を2回目の押しの判定より前に置く（`if (target.closest(".sd-orca")) { if (V.sel !== id) select(id); V.pn?.preferTab("agents"); return; }`）。3〜4行。今のテストは静的な並びの確かめだけ（`tests/unit/infra/test_dashboard_orca_views_js.py` の `test_pressing_a_mark_prefers_the_agents_tab`。`select(id)` が `preferTab` より前）なので、そこに「印の判定が `isPhone() && V.sel === id` より前」を足す。上の直し方は `select(id)` が `preferTab` より前のままなので、今の確かめも成り立つ。
- (d) 推奨：**直す**（小。人が普通にする操作で起きる）。

### 4. 修飾キーつきの押しでも、帯の捕捉が `forgetGone` を呼んで元のページの覚えが変わる（P2、ChatGPT）

- (a) 起きるか：**起きる（コードの筋道。design の書いたとおりの動き）**。`paintAgentList` の捕捉の段の聞き手は、修飾キーを見ずに `forgetGone(mem, id)` を呼ぶ（design D-04「修飾キーの有無によらず」）。cmd などの押しは、欄では `plainClick` でないので params が変わらず、詳しい画面では `interceptLinks` が触らないので、どちらも新しいタブで開くだけ。それでも元のページの `mem` は `gone` が空になり、`picked`・`last` が B になる。
  - その後、元のページで欄を閉じて開き直す（または agent のない道で同じ Scope の agents のタブへ来る）と、`wanted = mem.last = B` で B が開く。また `gone` が空になるので、query に `gone:` のない道では、前にいなくなった A が戻ってきたとき開きうる（`gone:A` が query にあれば規則1が守る）。
- (b) 影響：元のページで、人が新しいタブで開いた B が後で開く。B は人が選んだ相手なので「勝手に別の相手を開く」ではないが、「修飾キーの押しは元のページを変えない」という期待に反する。起きる条件も重なりが要り、影響は小さい。
- (c) 直し方：捕捉の聞き手で、`event.button === 0` かつ修飾キーなしのときだけ `forgetGone` を呼ぶ（panel.js の `plainClick` と同じ判定）。1行。design.cue の D-04 の「修飾キーの有無によらず」を直す（仕様の変更が要る）。node のテスト1件。
- (d) 推奨：**直す（低い優先。ほかの4点と同じ Issue に入れるなら）**。単独では直さなくてよい。

### 5. `agents` が配列でない要約を、いなくなったことの根拠にする（P2、ChatGPT）

- (a) 起きるか：**起きる（node で確かめた）**。`scopeAgents` は `Array.isArray(worktree.agents)` でない worktree を数えずに飛ばす。node で `[{id:"w1", agents:{id:"A"}}]` を渡すと `agents 0, invalid 0`。`wanted` が A なら `agentsVisibility` は `{show:true, reason:null}` になり、`agentsState` が `noteGone(A)`、`pickAgent` が `gone:A` を覚える（形の違いの知らせ "shape" ではなく「いなくなった」になる）。`wanted` がなければタブが出ない。iss-00593 の FQG attempt 1 で決めた「全部が形違いのときはいなくなったと決めない」の穴。
  - 起きる条件：orca-web の要約が `orca-web.worktree-summary/v1` のまま `agents` を配列でなく返すとき（orca-web の版の食い違いか不具合）。今の orca-web（main のチェックアウト `373a2c7`）の `src/summary/build.ts` は `agents: []` で始めて push するので、いつも配列を返す。普段は起きない。
- (b) 影響：その間「選んでいたエージェントはいなくなった」と誤って出て iframe が外れ、`gone:A` が query か params に残る。orca-web が直っても、人が選び直すまで A は開かない。別の相手は開かない（安全側）。
- (c) 直し方：`scopeAgents` で、オブジェクトの worktree の `agents` が配列でなければ `invalid++`（id はないので `invalidIds` は変えない）。2行。すると `noneUsable` で "shape" の知らせになる。node のテスト1件（`test_dashboard_agents_logic_js.py`）。null や欠け（`agents` がない）を「0人」と読むか「形違い」と読むかは、orca-web の README の契約に合わせて決める（v1 の契約で `agents` が必須なら、欠けも形違い）。
- (d) 推奨：**直す**（小。普段は起きないが、直しが2行で、決めた原則に合わせられる）。

## 推奨のまとめ

| 点 | 起きるか | 影響 | 大きさ | 推奨 |
|---|---|---|---|---|
| 1. FQG-003（今の相手の押しで置き直し） | 起きる | 書きかけが消える | 数行（2と共通） | 直す |
| 2. 欄の開き直しと足のリンク | 起きる | 多くは手間。狭い条件で新しいタブが残った相手を自動で開く | 数行（1と共通）＋足の1行 | 直す |
| 3. スマホの印の2回目の押し | 起きる | agents のタブでなく詳しい画面に飛ぶ | 3〜4行 | 直す |
| 4. 修飾キーの押しの覚え | 起きる（仕様どおり） | 元のページで後に B が開きうる | 1行＋仕様の1文 | 低い優先で直す（まとめるなら） |
| 5. agents が配列でない要約 | 起きる（orca-web の異常時） | 誤った「いなくなった」 | 2行 | 直す |

提案：5点を1つの Issue にまとめる（Epic 00526 の子。保証レベルは iss-00593 と同じ考えで strict か、送信に関わらない直しなので standard。統括が決める）。実装の後、実機で項目1〜3（欄の開き直し→詳しい画面→帯の押しで iframe の読み込みが増えない、概要のタブから新しいタブで B が開かない、390 の幅で印の2回目の押しが agents のタブになる）を確かめる。

## Outcome

調べだけ。コードとテストの変更なし、コミットなし。

## Verification

- 基準の全体のテスト（main `16f0cf122`、この worktree）：`uv run pytest -q` の結果は下に記す。
- node による純粋な部分の確かめ（スクラッチの `probe.mjs`、`agents_logic.js` を読むだけ）：
  - 項目5：`scopeAgents([{id:"w1",branch:"b",agents:{id:"A"}}])` → `{n:0, invalid:0}`、`agentsVisibility({status:"ok",records:1,…,wanted:"A"})` → `{show:true, reason:null}`、`pickAgent([], "A", {A})` → `remember:"gone:A"`。
  - 項目1・2：2人のうち last の A を選ぶ `pickAgent` → `remember:null, selected:A`。

## Residual Risks / Follow-ups

- 画面の操作の再現（項目1〜4）は実機で動かしていない。直す Issue の実機の確かめで、直す前の版でも起きることを先に写すとよい。
- 項目5の「`agents` の欠けや null をどう読むか」は orca-web の要約の契約（README）を確かめてから決める。
