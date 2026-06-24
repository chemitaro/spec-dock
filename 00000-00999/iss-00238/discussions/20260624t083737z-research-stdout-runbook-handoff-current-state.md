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

- `spec-dock <command>` を実行し、その Markdown stdout を読む。
- 今回の issue では `guidance` の JSON output contract は用意しない。
- 人間向け projection は runtime が自動生成してよい。ただし agent は projection の存在を知る必要がなく、参照もしない。

### 原則 2: generated runbook projection は人間確認用 / evidence 用に限定する

projection は完全に不要ではない。人間にとっては次の価値がある。

- 今の active issue の状態をファイルで確認できる。
- runbook / context packet / assurance の snapshot を evidence として残せる。
- manual test や debug で比較しやすい。

ただし通常の agent handoff からは外す。

推奨:

- agent-facing contract は stdout only。
- projection は runtime が自動生成してよいが、Git 管理しない ignored artifact とする。
- projection write failure は agent guidance の取得を block しない。
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

## 追加分析: `current` を外した command design

### 結論

`current` は command 名から外す。

推奨する primary command は次である。

```sh
./spec-dock/scripts/spec-dock guidance issue-planning
./spec-dock/scripts/spec-dock guidance issue-execution
```

理由:

- SpecDock の guidance は常に「現在の repository / active context / artifact / assurance / worktree 状態から、その場で組み立てる案内」であるべきで、`current` と `next` のような状態修飾語を command name に入れる必要がない。
- `current` を入れると、将来 `next` / `previous` / `snapshot` などの sibling subcommand があるように見える。今回の設計では、そのような概念を primary model にしない。
- ユーザーが期待している mental model は「SpecDock の guidance を実行すれば、今やるべきことが stdout で返る」であり、`guidance <target>` が最も短く直接的である。
- `workflow` は全体手順を連想させ、`runbook` はファイル化された手順書を連想させる。`guidance` は stdout handoff の意味に近い。

### command naming の採用判断

| 候補 | 判断 | 理由 |
| --- | --- | --- |
| `guidance <target>` | 採用 | 「今の案内」を最短で表し、`current` / `next` の余計な概念を作らない。 |
| `guidance current <target>` | 不採用 | `current` が重複し、将来 sibling subcommand があるように見える。 |
| `workflow next <target>` | 不採用 | `workflow` も `next` も今回の handoff surface とズレる。 |
| `workflow <target>` | 不採用 | `next` は消えるが、workflow 全体を返す印象が残る。 |
| `runbook <target>` | 不採用 | 人間向け projection / runbook file と混同しやすい。 |
| `brief <target>` | 不採用 | 断片的 guidance の語感は良いが、SpecDock 用語として伝わりにくい。 |

### planning / execution target を分けるか

結論として、command は 1 つにし、target は分ける。

推奨:

```sh
./spec-dock/scripts/spec-dock guidance issue-planning
./spec-dock/scripts/spec-dock guidance issue-execution
```

分ける理由:

- planning と execution は stop condition、fallback docs、allowed action、必要な artifact readiness、task checklist に登録すべき項目が異なる。
- 現行 skill も `spec-dock-issue-planning` と `spec-dock-issue-execution` に分かれており、agent が呼び出す意図も異なる。
- runtime でも `issue-execution` のときだけ step assurance / context packet / continuation check を組み立てる分岐が存在する。
- planning 中に execution guidance を受け取る、または execution 中に authoring guidance を受け取る事故を避けるには target を明示する方がよい。

統合しない理由:

- `guidance issue` のような単一 target にすると、runtime が plan / requirement / assurance / report から agent の意図を推測する必要が出る。
- 推測型にすると、要件定義を直したい execution task、execution 中に見つかった spec gap、planning と execution の境界ケースで誤誘導しやすい。
- skill が既に planning / execution を route しているため、runtime が同じ routing を再推測する必要はない。

したがって、`guidance` は単一 command とし、target は `issue-planning` / `issue-execution` で分ける。

### target の将来拡張

将来、Epic や Initiative にも同じ model を広げる場合は次のように拡張できる。

```sh
./spec-dock/scripts/spec-dock guidance epic-planning
./spec-dock/scripts/spec-dock guidance epic-execution
./spec-dock/scripts/spec-dock guidance initiative-planning
```

この場合も `current` は不要である。`guidance` は常に現在状態から組み立てるものとして定義する。

## projection の再整理

### 結論

人間向け projection は残す。ただし agent-facing contract からは完全に外す。

重要なのは、agent が projection を作成・更新・参照・管理する意識を持たないことである。

設計方針:

- agent は `guidance <target>` を実行し、stdout だけを読む。
- `guidance <target>` の実行時に、人間向け projection は runtime が自動生成してよい。
- projection は Git 管理しない。
- skill は projection path を agent handoff として説明しない。必要なら「生成される場合があるが、agent は読まない」とだけ書く。
- projection write failure は agent guidance の取得を block しない。
- projection write failure が起きた場合、stdout guidance は成功させる。人間向け debug 情報として Markdown warning または debug log に留める。

### projection が自動生成でよい理由

- 人間にとって、現在の runbook / guidance の snapshot が残ることには価値がある。
- しかし agent に明示 flag や別 command を使わせると、agent handoff と human projection の責務が再び混ざる。
- projection を runtime の副作用として自動生成しつつ、agent-facing instruction から隠せば、人間の利便性と agent の command-first handoff を両立できる。

### stale projection への対策

projection は stale になり得るため、次を入れる。

- projection header に `generated_at`、`active_issue_id`、`workflow_target`、source hash / revision を入れる。
- projection header に「agent handoff ではない。agent は `./spec-dock/scripts/spec-dock guidance <target>` の stdout を読む」と明記する。
- `current-runbook.*` のような名前を継続する場合でも、agent-facing docs から path を消す。
- projection が古いことは人間が判断できるようにするが、agent の制御フローには使わない。

## コマンド名候補

過去案のうち、現在の採用判断は以下である。

推奨は `guidance <target>` で確定寄りとする。

## ディープコンサルタントの叩き台と採用判断

ディープコンサルタントには、現在の実装・skill wording・stale projection risk・命名候補・migration strategy を前提に分析を依頼した。

提案の要点は有用だったが、ユーザー追加判断により一部を修正する。

採用する点:

- agent handoff は command stdout を正本にする。
- `current-runbook.*` は agent handoff ではないと明示する。
- skill は stdout の `state` / `next_action` / `commands` / `stop_conditions` / selected step を task checklist に登録してから作業するよう要求する。
- context packet の stdout-first 化は follow-up として分け、今回の issue では runbook projection の問題を先に閉じる。

修正する点:

- `guidance current <target>` ではなく、`guidance <target>` を primary command にする。`current` は不要。
- `workflow next <target>` の互換 alias は不要。この変更はまだ main branch に入っていないため、`iss-00238` 内で切り替える。
- projection は agent が明示 command / flag で作るものではなく、runtime が自動生成する human/debug artifact とする。
- projection write failure は agent guidance の取得を block しない。

採用判断:

- `guidance <target>` を primary command とする。
- `workflow next <target>` は置き換え対象とし、互換 alias は作らない。
- 人間向け projection は自動生成される ignored artifact として残すが、agent-facing docs / skills からは参照導線を消す。
- context packet は今回の issue の必須 scope から外し、別 issue / follow-up 候補にする。

## 推奨する target design

### CLI

第一案:

```sh
./spec-dock/scripts/spec-dock guidance issue-execution
./spec-dock/scripts/spec-dock guidance issue-planning
```

### デフォルト動作

- stdout に現在 guidance を出す。
- 人間向け projection は自動生成してよい。ただし ignored artifact とし、agent は存在を意識しない。
- projection write failure は guidance stdout を block しない。
- context packet 生成は、現行実装の execution context handoff として今回は別論点にする。runbook projection と同一視して default から外さない。

### 互換性

- `workflow next <target>` の互換 alias は作らない。
- この機能はまだ main branch にマージされていないため、consumer 互換より設計の明確さを優先して `guidance <target>` へ切り替える。
- tests / skills / docs は `workflow next` ではなく `guidance <target>` を primary command として更新する。

### skill 文面

issue execution skill の First-Read Handoff は次の意味へ変更する。

- 最初に `./spec-dock/scripts/spec-dock guidance issue-execution` を実行する。
- stdout をその時点の動的 guidance として扱う。
- stdout から `state` / `next_action` / selected step / commands / stop conditions / verification / reviewer gate を task list に登録する。
- runbook projection は人間確認用の自動生成 artifact であり、agent handoff として読まない。
- command が失敗・矛盾・malformed の場合だけ static docs に fallback する。

issue planning skill も同様。

### human runbook projection

人間向け projection は残す。

ただし:

- runtime が自動生成する ignored artifact とする。
- agent は projection を作成・更新・参照・管理しない。
- file header に generated snapshot / timestamp / source hash / refresh command / not agent handoff を入れる。
- stale detection は可能なら warning として持つ。
- file name は現行 `current-runbook.*` 継続でもよいが、agent-facing docs には path を出さない。

## テスト観点

必須 regression:

- `guidance issue-execution` は Markdown stdout に guidance を返す。
- `guidance issue-planning` は Markdown stdout に planning 用 guidance を返す。
- `guidance` は target なし / unknown target を明確に reject する。
- `workflow next` primary command は存在しない、または少なくとも skills/tests の主導線から消える。
- projection は自動生成されても Git tracked diff を作らない。
- projection write failure は `guidance` stdout の成功を block しない。
- stale `current-runbook.*` が存在しても guidance は stdout の現在状態を返し、古い projection に依存しない。
- skill asset 内に `workflow next` primary instruction が残らない。
- skill asset 内に `current-runbook.*` を agent handoff として読む指示が残らない。
- skill が stdout guidance から task list / checklist 登録を促す。

## 解消済み論点と残論点

### D-001: primary command 名

決定: `guidance <target>`。

`current` は使わない。`workflow next` も使わない。

### D-002: planning / execution の分け方

決定: command は `guidance` で統一し、target は `issue-planning` / `issue-execution` で分ける。

### D-003: `workflow next` 互換性

決定: 互換 alias は不要。

理由:

- まだ main branch にマージされていない。
- ここで互換を残すと、古い mental model が残る。
- issue 内で一括切り替えする方が tests / skills / docs の整合性を保ちやすい。

### D-004: projection の位置づけ

決定: projection は人間用の自動生成 ignored artifact。

- agent は projection の存在を意識しない。
- agent は projection を作成しない。
- agent は projection を読まない。
- projection は Git 管理しない。
- projection write failure は guidance stdout を block しない。

### D-005: context packet の扱い

決定: 今回の主 scope から外す。

理由:

- context packet は execution worker へ渡す payload としての性格があり、runbook projection とは責務が異なる。
- 今回は runbook / guidance handoff の surface を閉じる。
- context packet の stdout-first / projection 化は follow-up で必要なら扱う。

### 残論点

現時点でユーザー判断が必要な未確定事項はない。

requirement / design / plan へ進む時点では、上記 D-001 から D-005 を採用済み判断として扱う。

## 次に作るべき成果物

この artifact は requirement / design / plan の前段である。

次の authoring では、少なくとも以下を formalize する。

- 要件:
  - agent handoff は command stdout を正本にする。
  - projection は人間確認用 / evidence 用に限定する。
  - `workflow next` を `guidance <target>` に置き換える。
  - skill は guidance を task management に登録するよう促す。
- 設計:
  - `guidance <target>` command。
  - `issue-planning` / `issue-execution` target 分離。
  - stdout / projection / static docs の責務分離。
  - 自動 projection の non-blocking error handling。
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
