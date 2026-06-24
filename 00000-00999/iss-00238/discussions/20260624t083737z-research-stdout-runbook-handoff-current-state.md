# 動的ガイダンス handoff の現状分析と理想形叩き台

## 目的

この artifact は、`iss-00238` の要件定義・設計・計画に入る前の調査メモである。

ユーザーが指摘した問題は、単に「生成ファイルがある」ことではない。問題の中心は、エージェントがその時点の最新状態を得るための handoff surface が曖昧になっていることにある。

特に避けたいのは次の流れである。

1. エージェントが skill を読む。
2. skill が別の workflow / runbook / projection ファイル参照を促す。
3. エージェントがその参照を飛ばす、または古い生成ファイルを読む。
4. 現在の active issue、plan、report、assurance、worktree 状態とずれた guidance で進む。

望ましい流れは次である。

1. エージェントが skill を読む。
2. skill に書かれた SpecDock のコマンドを毎回実行する。
3. コマンドが現在時点の状態から guidance を動的に組み立て、stdout に出す。
4. エージェントは stdout をその場の作業指示として受け取る。
5. 必要な項目をエージェント自身のタスク管理・チェックリストへ登録してから進める。

## 現状の結論

現状は「stdout-first に寄せた skill 文面」と「通常実行で生成 runbook projection を更新する runtime contract」が混在している。

良い点:

- `spec-dock-issue-planning` と `spec-dock-issue-execution` は、最初に `./spec-dock/scripts/spec-dock workflow next ...` を実行するよう促している。
- skill は `current-runbook.*` を canonical artifact として編集しないよう明記している。
- projection path は symlink hardening されており、unsafe write は fail closed する。
- 人間が現状を確認するための runbook projection 自体は有用である。

問題点:

- `workflow next` という名前が、実際の目的を過度に「次ステップ選択」に寄せている。
- ユーザー指摘どおり、そもそも `next` という概念を前面に出す必要が薄い。必要なのは「今この状態で何をすべきか」を得ることである。
- `workflow` という名前も少し大きい。出力は必ずしも workflow 全体像ではなく、現在の行動指示、stop condition、handoff、runbook fragment、context routing である。
- runtime は stdout に guidance を出すだけでなく、毎回 `current-runbook.*` を書く。そのため projection write failure が guidance 取得自体を block し得る。
- tests は `workflow next` が projection files を生成することを contract として固定している。
- skill 文面には「stdout を読む」と「canonical workflow docs へ戻る」が混在しており、静的 docs と動的 guidance の責務境界がまだ弱い。
- 他の skill には `workflow_*.md` を primary workflow として読む記述が残っており、動的 guidance を毎回取得する入口としては不統一である。
- 実際に現在の active issue は `iss-00238` だが、`spec-dock/.agent/runbooks/current-runbook.json` は `iss-00237` を指していた。stale projection risk は既に実害として観測できている。

## 現状の証跡

### issue planning / execution skill は runtime 実行を促している

`spec-dock-issue-execution`:

- `First ask the runtime for the current execution Runbook`
- `./spec-dock/scripts/spec-dock workflow next issue-execution`
- generated projections は ignored output と明記

証跡:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md:12-18`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md:12-18`

解釈:

- 「コマンドを実行して stdout を得る」方向には進んでいる。
- ただし command name と projection side effect が設計意図を曇らせている。

### 他 skill には静的 workflow docs 参照が残っている

例:

- `spec-dock-epic-planning` は `spec-dock/docs/workflow_epic.md` を primary workflow とする。
- `spec-dock-initiative-planning` は `workflow_initiative.md` を参照する。
- host adapter は `workflow_issue.md` を follow する。

解釈:

- 静的 docs は canonical fallback / durable policy として必要である。
- しかし、状態依存の「今すべきこと」を得る入口として static docs を primary にすると、動的 guidance の導入目的と衝突する。

### runtime は `workflow next` で projection を通常書き込みする

application layer は runbook を compile した後、`runbook_store.write_current(runbook)` を呼んでいる。

証跡:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:96-107`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:134-147`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py:148-165`

infra layer は次の 4 ファイルを書く。

- `spec-dock/.agent/runbooks/current-runbook.json`
- `spec-dock/.agent/runbooks/current-runbook.md`
- `spec-dock/active/current-runbook.json`
- `spec-dock/active/current-runbook.md`

証跡:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py:16-21`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/runbook_store.py:28-63`

解釈:

- 現状の `workflow next` は stdout command であると同時に projection 更新 command でもある。
- 人間向け projection は有用だが、agent handoff の主経路に混ざると stale file risk が残る。

### stale projection が実際に残っている

調査時点で active issue は `iss-00238` だったが、`spec-dock/.agent/runbooks/current-runbook.json` の `active_issue_id` は `iss-00237` だった。

証跡:

- `spec-dock/.agent/runbooks/current-runbook.json` は `active_issue_id: "iss-00237"` を保持していた。
- `spec-dock/active/current-runbook.json` は存在しなかった。

解釈:

- 生成 runbook projection は、active issue 変更後に stale になり得る。
- agent が command stdout ではなく projection file を読んだ場合、前 issue の状態に基づく誤った guidance を受け取る。
- これはユーザーが懸念した「古いものを何度も見続ける」問題の具体例である。

### tests は projection 生成を通常 contract として固定している

証跡:

- `tests/cli_runtime/test_workflow.py:185-210`

解釈:

- 修正時には tests の意図も変える必要がある。
- 「stdout が guidance の正本」「projection は opt-in または人間確認用」という contract をテストに落とす必要がある。

## 問題の整理

### 問題 1: `next` という名前がズレている

`next` は「次の一手」を返すように見えるが、実際に必要なのは次に限らない。

- active issue がなければ、issue start を促す。
- requirement が scaffold なら、requirement capture を促す。
- plan が未整備なら、planning required を促す。
- assurance が壊れていれば、classification / verify を促す。
- 実行可能なら、worker / effort / verification / reviewer / stop condition を返す。

これは「next step selector」というより、「現在状態に対する guidance / runbook / action briefing」である。

### 問題 2: `workflow` という名前も大きすぎる可能性がある

`workflow` は全体図・手順体系・静的プロセスを連想させる。

しかしこの command が返すものは、しばしば断片的で状態依存の guidance である。

- 現在の状態
- 次に必要な action
- stop condition
- worker / reviewer / verification
- context packet refs
- runbook fragment

したがって、より適切な概念名は `guidance`、`runbook`、`handoff`、`brief`、`assist`、`status` などの候補がある。

### 問題 3: projection は人間用には有益だが agent handoff には向かない

人間が「今どんな状態か」を見るために `current-runbook.md` があるのは有益である。

ただし agent に対しては、次の理由で projection を handoff interface にすべきではない。

- stale になり得る。
- active issue / worktree / assurance / plan の変化に追随しないまま読まれる可能性がある。
- skill から二段階ファイル参照になり、読み落としが起きる。
- projection write failure が guidance 取得を妨げる。

### 問題 4: エージェントのタスク管理に登録する明示が足りない

今回 `spec-dock-issue-planning` / `spec-dock-issue-execution` を使っても、agent の task checklist に自然に反映されなかった。

動的 guidance は stdout で得るだけでなく、エージェントがそれを作業単位へ変換して追跡する必要がある。

skill 側には次のような明示が必要である。

- command stdout を読んだら、主要 action / stop condition / verification / reviewer gate を task list に登録する。
- state が blocked / requirement-capture / planning-required の場合も、次アクションを task list に登録する。
- guidance が変わるたびに task list を更新し、古い checklist を残さない。

## 理想形の叩き台

### 原則 1: agent handoff は stdout を正本にする

エージェント向けの動的 guidance は、常に command 実行結果の stdout を読む。

禁止したい運用:

- runbook を更新する command を実行する。
- 更新された `current-runbook.*` を別途読む。
- 以前の `current-runbook.*` を再利用する。

許可したい運用:

- `spec-dock <command> ... --format markdown` を実行し、その stdout を読む。
- 機械的検証では `--format json` を使う。
- 人間が必要なら明示 command で runbook projection を保存する。

### 原則 2: generated runbook projection は人間確認用 / evidence 用に限定する

projection は完全に不要ではない。人間にとっては次の価値がある。

- 今の active issue の状態をファイルで確認できる。
- runbook / context packet / assurance の snapshot を evidence として残せる。
- manual test や debug で比較しやすい。

ただし通常の agent handoff からは外す。

推奨:

- default command は stdout only。
- projection は明示 flag で opt-in。
- projection write failure は opt-in 時だけ command failure / blocked にする。
- stale projection には「generated snapshot」「timestamp」「source hash」「do not use as agent handoff」「refresh command」を明記する。

### 原則 3: static workflow docs は fallback / policy authority に限定する

`workflow_*.md` は消さない。

役割を次のように分ける。

- static docs: durable policy、ルール、fallback、例外時の判断材料
- stdout guidance: 現在状態に対する次アクション
- projection files: 人間確認・debug・evidence snapshot

skill では次を明記する。

- まず command stdout を読む。
- stdout guidance が生成できない、壊れている、canonical docs と矛盾する場合だけ `workflow_*.md` に fallback する。
- static docs を読んだ場合も、状態依存判断は command が復旧するまで仮扱いにする。

## コマンド名候補

### 候補 A: `spec-dock guidance current <target>`

例:

- `./spec-dock/scripts/spec-dock guidance current issue-execution`
- `./spec-dock/scripts/spec-dock guidance current issue-planning`

長所:

- `current` により「次」ではなく「現在状態に対する案内」を表せる。
- `guidance` により、workflow 全体ではなく action guidance / runbook fragment / stop condition を返す意味が伝わる。
- `workflow next` より、今回の目的に最も近い。
- stdout handoff と相性が良い。

短所:

- 既存 `workflow next` からの移行が必要。
- command が二語になるため、`guide` より少し長い。

### 候補 B: `spec-dock guide <target>`

例:

- `./spec-dock/scripts/spec-dock guide issue-execution`
- `./spec-dock/scripts/spec-dock guide issue-planning`

長所:

- エージェントに「今の案内を受ける」意味が伝わる。
- `next` より広い。
- stdout handoff と相性が良い。

短所:

- `guide` がドキュメント案内にも見える可能性がある。
- `current` の概念が名前に出ないため、stale avoidance の意図がやや弱い。

### 候補 C: `spec-dock runbook current <target>`

例:

- `./spec-dock/scripts/spec-dock runbook current issue-execution`
- `./spec-dock/scripts/spec-dock runbook current issue-planning`

長所:

- 現行 domain model の `Runbook` と一致する。
- 人間にもエージェントにも「現在の手順書」として理解しやすい。

短所:

- `runbook` はファイル保存されるものという印象を持たれやすい。
- agent stdout handoff より、人間向け snapshot の語感に寄る。

### 候補 D: `spec-dock brief <target>`

例:

- `./spec-dock/scripts/spec-dock brief issue-execution`
- `./spec-dock/scripts/spec-dock brief issue-planning`

長所:

- 断片的・現在状態・agent handoff の語感が強い。
- workflow 全体ではなく「今の brief」を返す意味に合う。

短所:

- 日本語圏では意味がやや伝わりにくい。
- 既存 SpecDock 用語との距離がある。

### 候補 E: `spec-dock advise <target>`

例:

- `./spec-dock/scripts/spec-dock advise issue-execution`

長所:

- 状態から助言を返す意味に合う。
- `next` より抽象度が適切。

短所:

- command としてやや自然言語的で、SpecDock の硬めの用語体系と合うか検討が必要。

### 候補 F: `spec-dock workflow <target>`

例:

- `./spec-dock/scripts/spec-dock workflow issue-execution`
- `./spec-dock/scripts/spec-dock workflow issue-planning`

長所:

- `next` を落とすだけで移行量が少ない。
- 現行 command の近縁で学習コストが低い。

短所:

- `workflow` が大きすぎる問題は残る。
- 全体 workflow を見る command との衝突余地がある。

### 現時点の推奨

叩き台としては `guidance current` を第一候補、`guide` を第二候補、`runbook current` を第三候補にする。

理由:

- 今回の主目的は「今何をすべきかを毎回動的に案内する」ことであり、`guidance current` が最も直接的である。
- `current` により `next` を捨てつつ、毎回最新状態から組み立てる意図を名前に入れられる。
- `guide` は簡潔だが、現在状態を毎回評価する command であることがやや弱い。
- `runbook current` は現行 model と近いが、ファイル projection の印象を残しやすい。
- `workflow next` は廃止または互換 alias に留め、primary command からは外すのがよい。

## ディープコンサルタントの叩き台と採用判断

ディープコンサルタントには、現在の実装・skill wording・stale projection risk・命名候補・migration strategy を前提に分析を依頼した。

提案の要点:

- agent-facing の一次入口は `./spec-dock/scripts/spec-dock guidance current <target>` がよい。
- `workflow next <target>` は互換 alias として残す。
- human/debug/evidence 用の明示 snapshot は `./spec-dock/scripts/spec-dock guidance snapshot <target>` として分ける。
- default の `guidance current` は stdout-only にする。
- `current-runbook.*` は agent handoff ではないと明示する。
- projection 書き込み失敗は、明示 snapshot 時だけ fail closed にする。
- skill は stdout の `state` / `next_action` / `commands` / `stop_conditions` / selected step を task checklist に登録してから作業するよう要求する。
- 旧 `current-runbook.*` は削除または tombstone 化を検討する。推奨は tombstone 付き migration。
- context packet の stdout-first 化は follow-up として分け、今回の issue では runbook projection の問題を先に閉じるのがよい。

採用判断:

- `guidance current` を primary command の第一候補に引き上げる。
- `guidance snapshot` を人間向け projection / evidence snapshot の第一候補にする。
- `workflow next` は既存利用者のため互換 alias とするが、skill の primary instruction からは外す。
- context packet は今回の issue の必須 scope から外し、別 issue / follow-up 候補にする。

## 推奨する target design

### CLI

第一案:

```sh
./spec-dock/scripts/spec-dock guidance current issue-execution --format markdown
./spec-dock/scripts/spec-dock guidance current issue-planning --format markdown
```

機械用:

```sh
./spec-dock/scripts/spec-dock guidance current issue-execution --format json
```

人間向け snapshot:

```sh
./spec-dock/scripts/spec-dock guidance snapshot issue-execution --format markdown
```

互換 alias:

```sh
./spec-dock/scripts/spec-dock workflow next issue-execution --format markdown
```

### デフォルト動作

- stdout に現在 guidance を出す。
- `current-runbook.*` は書かない。
- context packet 生成も agent handoff に必須でなければ opt-in / explicit に寄せる。ただしここは別途設計が必要。
- projection が必要な場合だけ `guidance snapshot` を使う。

### 互換性

- 既存 `workflow next <target>` は一時的に alias として残す。
- alias 実行時も stdout-first contract に従う。
- deprecation warning を出すかどうかは設計時に決める。
- 既存 `current-runbook.*` は migration で削除または tombstone 化する。tombstone には「廃止された snapshot であり、agent は `guidance current` を実行せよ」と明記する。

### skill 文面

issue execution skill の First-Read Handoff は次の意味へ変更する。

- 最初に `./spec-dock/scripts/spec-dock guidance current issue-execution --format markdown` を実行する。
- stdout をその時点の動的 guidance として扱う。
- stdout から `state` / `next_action` / selected step / commands / stop conditions / verification / reviewer gate を task list に登録する。
- `current-runbook.*` は人間確認用 snapshot であり、agent handoff として読まない。
- command が失敗・矛盾・malformed の場合だけ static docs に fallback する。

issue planning skill も同様。

### human runbook projection

人間向け projection は残す。

ただし:

- default では書かない。
- 明示 command で更新する。
- file header に generated snapshot / timestamp / source hash / refresh command / not agent handoff を入れる。
- stale detection は可能なら warning として持つ。
- snapshot file name は可能なら `current-runbook.*` より、active issue / target / fingerprint / timestamp を含む名前に寄せる。

## テスト観点

必須 regression:

- default `guidance current issue-execution --format json` は stdout に current guidance を返す。
- default では `spec-dock/.agent/runbooks/current-runbook.*` を生成しない。
- `guidance snapshot` では projection / snapshot を生成する。
- projection symlink abuse は `guidance snapshot` 時だけ fail closed する。
- stale `current-runbook.*` が存在しても default guidance は stdout の現在状態を返し、古い projection に依存しない。
- skill asset 内に `workflow next` primary instruction が残らない。
- skill asset 内に `current-runbook.*` を agent handoff として読む指示が残らない。
- skill が stdout guidance から task list / checklist 登録を促す。

## 未確定事項

### Q-001: primary command 名を何にするか

推奨: `guidance current`

代替:

- `guide`
- `runbook`
- `brief`
- `advise`
- `workflow` から `next` だけを外す

人間判断が必要。

### Q-002: projection を opt-in flag にするか、別 command にするか

推奨: 別 command。agent handoff path と人間 snapshot path が見た目で分かれる方がよい。

候補:

- `guidance snapshot <target>`
- `guidance current <target> --write-runbook`
- `runbook write <target>`

### Q-003: 旧 `current-runbook.*` を削除するか tombstone 化するか

推奨: tombstone 付き migration。

理由:

- stale file を単に残すと誤読 risk が残る。
- 単に削除すると、存在を期待している古い skill / 人間の探索で混乱する可能性がある。
- tombstone なら「このファイルは廃止。`guidance current` を実行せよ」という明確な誘導を置ける。

### Q-004: context packet 生成も default から外すか

今回の主問題は runbook projection だが、context packet も generated file である。

ただし context packet は agent handoff の payload として別の意味があるため、同じ issue で扱うかは要検討。

推奨:

- `iss-00238` では runbook / guidance handoff を主対象にする。
- context packet は「agent payload 生成」として残すか、別設計で扱う。

### Q-005: 既存 `workflow next` の互換期間

推奨:

- 互換 alias として残す。
- skills/docs からは primary として削除する。
- tests では alias の最低限互換だけ確認する。

## 次に作るべき成果物

この artifact は requirement / design / plan の前段である。

次の authoring では、少なくとも以下を formalize する。

- 要件:
  - agent handoff は command stdout を正本にする。
  - projection は人間確認用 / evidence 用に限定する。
  - `workflow next` 命名を見直し、`guidance current` を第一候補にする。
  - skill は guidance を task management に登録するよう促す。
- 設計:
  - 新 command 名と互換 alias。
  - `guidance current` と `guidance snapshot` の責務分離。
  - stdout / projection / static docs の責務分離。
  - opt-in projection の error handling。
  - skill asset 更新範囲。
- 計画:
  - runtime CLI 変更。
  - tests 更新。
  - skill/docs wording audit。
  - manual test / regression。

## lifecycle evidence

- `iss-00237` は `spec-dock: ok (issue finish) issue=iss-00237 github=#237 state=CLOSED active_cleared=true` で完了した。
- `iss-00238` / GitHub `#238` を `epic-00224` 配下に作成した。
- `iss-00238` を start し、branch `iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files` を checkout した。
