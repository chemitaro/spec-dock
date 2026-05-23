---
type: research
source: deep-consultant
created_at: 2026-05-23T12:35:01+09:00
epic: epic-00112
topic: skeptical writer risk analysis
status: current
---

# Deep Consultant Research: Skeptical Writer Risk Analysis

## skeptical_verdict

懐疑側の Deep Consultant は、現時点では `system-architect` / `implementation-planner` に `design.md` / `plan.md` の直接編集権限を与えるべきではない、と判断した。

推奨は、当面は read-only draft / adviser を維持し、main orchestrator が canonical docs を作成すること。ただし、将来的に write-capable authoring を試す価値はある。その場合も、自律編集ではなく、隔離された draft branch / draft artifact にだけ書ける authoring harness を挟み、canonical 昇格は main orchestrator または明示レビューが担うべきである。

理由は、`design.md` と `plan.md` が単なる成果物ではなく、以後の実装・レビュー・issue lifecycle の責任境界そのものだからである。

## failure_modes_of_write_capable_authoring

### 1. 責任境界が崩れる

`system-architect` が `design.md` を書き、`implementation-planner` が `plan.md` を書く構想は自然に見える。しかし失敗時に誰が責任を持つのかが曖昧になりやすい。

- requirement と design の不整合は誰が検出するのか。
- design と plan のズレは誰が裁定するのか。
- ユーザー意図と異なる設計判断が混入した場合、誰の判断として扱うのか。
- 後続の implementer はどの agent の成果物を信頼すべきか。

特に `design.md` は「専門家の案」ではなく、実装が従う契約である。ここを adviser が直接 canonical にすると、advice と authority が混ざる。

### 2. レビュー独立性が失われる

write-capable にすると、authoring agent は自分の書いた canonical docs を後で正当化する立場になる。これはレビュー独立性を弱める。

危険な流れ:

- architect が設計を書く。
- planner がそれを前提に計画を書く。
- main は統合者のつもりだが、実際には既成事実を追認する。
- reviewer は「canonical に書いてあるから」と前提化する。

この流れになると、設計レビューではなく文書生成パイプラインになる。

### 3. stale docs の増殖が加速する

複数 agent が直接 `design.md` / `plan.md` を編集できると、ドキュメントは増えるが、同期責任は増えない。

典型的な失敗:

- `requirement.md` が変わったのに `design.md` が古い。
- `design.md` の制約が変わったのに `plan.md` が古い。
- planner が過去の design 前提で plan を更新する。
- main orchestrator が差分全体を把握しきれない。
- active docs と historical docs のどちらが正しいか不明になる。

### 4. agent over-autonomy が認知負荷を逆に増やす

表面的には「main が requirement、architect が design、planner が plan」と分けると楽に見える。しかしユーザーは最終的に次を確認する必要が出る。

- どの agent が何を変更したか。
- 変更が requirement と合っているか。
- design と plan が相互に矛盾していないか。
- agent 固有の推測が canonical に混入していないか。
- 権限設定が本当に効いていたか。

ユーザーは成果物だけでなく、agent 間の意思決定プロセスそのものを監査する必要が出る。これは「楽になる」の逆である。

### 5. Permission Profiles は安全境界として過信できない

per-agent writable path が使えるとしても、それは十分条件ではない。

残る不確実性:

- beta 機能で挙動が変わる。
- parent override により実効権限が想定と異なる。
- Desktop / CLI / host 差で挙動が違う。
- probe しないと本当に制限されているか分からない。
- path 制限は「何を書けるか」を制限しても、「何を判断してよいか」は制限しない。

## hidden_costs_of_readonly_adviser_mode

read-only にも明確なコストがある。

- main orchestrator が canonical doc 作成のボトルネックになる。
- 専門 agent の成果が薄く見え、「結局 main が全部書いている」ように見える。
- architect / planner の深い分析が main に要約される過程で、重要条件・反対意見・未解決リスクが落ちる。
- design draft -> main 統合 -> plan draft -> main 統合の往復が遅い。
- main の統合判断品質に依存しすぎる。

ただし、これらは harness で改善可能であり、canonical write 権限を与えないと解決できない問題ではない。

## minimum_safe_harness_if_writing_is_allowed

write-capable を許すなら、最低限次が必要。

1. canonical 直書きは禁止
   - `spec-dock/active/**/design.md` や `plan.md` を直接更新しない。
   - 許すなら `discussions/` / `drafts/` 配下、または isolated worktree / draft branch。

2. draft artifact schema を固定する
   - source requirement references
   - explicit assumptions
   - decisions made
   - rejected alternatives
   - risks
   - open questions
   - validation gates
   - impact on existing docs
   - files intended to change
   - confidence level

3. diff-based promotion gate
   - requirement traceability
   - design / plan 整合
   - stale premise
   - unresolved assumption
   - scope creep
   - test / validation の具体性
   - rollback 条件

4. agent ごとの writable path を実測 probe する
   - 許可 path に書ける。
   - 禁止 path に書けない。
   - parent override がない。
   - Desktop / CLI 差がない。
   - symlink 経由で抜けられない。
   - generated consumer workspace と provider source を誤って触れない。

5. author と reviewer を分離する。

6. small-scope pilot から始める。

7. stale detection を workflow に入れる。

## red_lines

- `system-architect` / `implementation-planner` に canonical docs への無条件 write 権限を与えない。
- Permission Profiles だけを安全策にしない。
- symlink / active docs / generated workspace の境界を probe なしで信用しない。
- unresolved assumptions を canonical doc に自然文で埋め込むことを許さない。
- author が自分の canonical 変更を最終承認する形にしない。
- user が「どの判断が誰由来か」を追えない workflow にしない。
- stale detection なしに delegated authoring を運用しない。

## recommendation

懐疑側の推奨は、read-only adviser を維持しつつ、draft contract を強化すること。

具体的には、`system-architect` と `implementation-planner` は今のまま canonical docs を直接編集しない。ただし、単なる助言ではなく、main orchestrator がほぼ機械的に取り込めるほど構造化された draft を返す。

write-capable を試すなら:

1. `drafts/` または `discussions/` 配下だけ writable にする。
2. canonical docs は main orchestrator だけが編集する。
3. Permission Profiles は probe 済みの場合のみ補助策として使う。
4. draft-to-canonical promotion checklist を必須化する。
5. 小さい issue で pilot し、認知負荷が本当に下がったか測る。

結論として、当初構想が「main=requirement、architect=design、planner=plan」だったとしても、それをそのまま canonical write 権限として実装するのは危険である。より堅い設計は、専門 agent は high-quality draft author、main orchestrator は canonical integrator、reviewer / consultant は独立検査者という分離である。
