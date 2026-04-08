# iss-00051 delegated workflow gap 分析・議事録・ベストプラクティス提案

## 目的
- manual test で判明した「host-native Codex shim は discovery はできるが、goal-level の issue workflow を最後まで完遂せず、issue docs 4 点がテンプレートのまま残る」問題を分析する
- 修正候補を比較し、developer instructions / delegated skill / manual test plan のどこをどのように直すのが適切か整理する
- consultant との議論内容、比較検討、推奨案を記録する

## 対象
- Codex native shim:
  - `.codex/agents/spec-dock.toml`
- Codex host adapter skill:
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- workflow hub skill:
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- workflow docs:
  - `spec-dock/docs/workflow_issue.md`
- manual test evidence:
  - `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/execution-log.md`
  - `manual-tests/reports/2026-04-06-iss-00051-native-shim-real-manual/summary.md`

## 事実整理

### 現在の shim
- `.codex/agents/spec-dock.toml` は非常に薄い
- 役割は次の 3 点に限定されている
  - discovery / delegation entrypoint
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md` への委譲
  - protocol / state の再実装禁止
- 一方で、完了条件は書いていない
  - issue docs 4 点を具体化すること
  - active context をどこまで進めること
  - review / report まで閉じること
  は shim に明示されていない

### 現在の delegated skill
- `.agents/skills/spec-dock-codex-adapter/SKILL.md` も薄い
- 主な内容は次の 4 点
  - Codex entrypoint として使う
  - `spec-dock/docs/workflow_issue.md` と issue-00049 fixed protocol を参照する
  - 適切な leaf skill に route する
  - adapter で protocol/state を再解釈しない
- しかし、route 後に何をもって完了とするかが弱い
  - leaf skill へ route したあと、issue docs 4 点を実データで埋めるまで必須なのか
  - docs がテンプレートのままなら fail / blocked 扱いなのか
  - active set / sync / validate だけ通して止まってよいのか
  が拘束されていない

### workflow hub skill
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md` は routing hub であり、完了責務を持たない
- そのため、hub 側に exit criteria を置く設計には向かない

### manual test evidence
- install/static contract は通っている
- Codex shim の discovery は通っている
- off-contract 診断では、initiative -> epic -> issue の作成や active set, sync, validate, deps check, fail-closed まで進むケースも確認された
- 一方で、issue の `requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残るケースが確認された
- これは「発見・委譲はできるが、spec workflow completion contract が弱い」ことを示唆する

## 論点

### 論点 1: developer instructions をどこまで厚くするか
- 厚くしすぎると shim が protocol / workflow を持ち始める
- 薄すぎると、discovery はできても execution 完了に到達しない

### 論点 2: completion contract をどこに置くか
- shim に置く
- delegated adapter skill に置く
- workflow docs / leaf skill に置く
- どこに責務を置くのが最も自然か

### 論点 3: manual test plan の責務
- install/static contract の確認
- delegated runtime execution の確認
- completion quality の確認
- 環境 blocker と product gap の切り分け

## 修正候補の比較

### 候補 A: shim を厚くする
- 内容:
  - `.codex/agents/spec-dock.toml` に completion contract を直接書く
  - issue work では docs 4 点を埋めるまで止まらないことを明記する
  - active set, sync, validate, report 更新まで書く
- 長所:
  - discovery から completion まで一貫した指示になる
  - manual test の観点では分かりやすい
- 短所:
  - shim が薄い entrypoint でなくなる
  - host ごとに completion logic が複製されやすい
  - Copilot 側と Codex 側で drift しやすい
- リスク:
  - host-native shim が protocol / workflow を再実装する方向へ滑りやすい

### 候補 B: shim は薄いまま、adapter skill に completion contract を置く
- 内容:
  - `.codex/agents/spec-dock.toml` は薄いまま維持する
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md` に「何をもって完了か」を追加する
  - issue work の場合は、最低でも次を満たすまで終了しないことを明記する
    - active issue を確定する
    - `requirement.md` / `design.md` / `plan.md` / `report.md` をテンプレートのまま残さない
    - 必要な review / validate / sync を実施するか、未実施理由を report に残す
- 長所:
  - shim は discovery/delegation entrypoint に留まる
  - host 共通の completion contract を adapter/skill 層に集中できる
  - drift を減らしやすい
- 短所:
  - adapter skill がやや厚くなる
  - manual test では shim 単体の可読性は上がらない
- リスク:
  - adapter skill の wording が弱いと、leaf skill への route 後にまた completion がぼける

### 候補 C: leaf skill / workflow docs を強化し、adapter は route に徹する
- 内容:
  - shim は薄いまま
  - adapter skill も薄いまま
  - `spec-dock-issue-execution` や `workflow_issue.md` 側に completion contract を強く置く
- 長所:
  - workflow 正本に completion を集中できる
  - adapter は長期的に薄く保てる
- 短所:
  - manual test で見つかった gap を adapter 入口で止めにくい
  - goal-level prompt から leaf skill へ確実に到達するまでの拘束が弱いまま残る
- リスク:
  - route できたが leaf skill が適用されなかった / completion まで拘束されなかった、という隙間が残る

### 候補 D: 二層強化
- 内容:
  - shim は薄いまま維持
  - adapter skill に「issue/execution 完了条件の最小 contract」を置く
  - leaf skill / workflow docs に「詳細な completion / review / report 契約」を置く
  - manual test plan は
    - install/static
    - delegated runtime
    - completion quality
    の 3 phase に分離する
- 長所:
  - 責務分離が自然
  - shim は薄いまま
  - adapter は route + minimum completion guard
  - leaf/workflow が詳細責務を持つ
  - manual test でもどこが壊れたか切り分けやすい
- 短所:
  - 変更箇所が 1 ファイルでは済まない
  - wording の一貫性を保つ必要がある
- リスク:
  - docs / skills / test plan の同期を怠ると再び gap が出る

## consultant との議論メモ

### viewpoint 1: entrypoint minimalism
- shim は host-native discovery/delegation entrypoint に徹するべき
- shim に completion logic を書きすぎると host ごとの差分が増える
- したがって候補 A は分かりやすいが、設計としては良くない

### viewpoint 2: execution contract must exist above the leaf boundary
- 現状の問題は「route したら勝ち」になっていること
- issue execution では、docs 4 点をテンプレートのまま残さないことを adapter 層でも最低限拘束すべき
- したがって候補 B または D が自然

### viewpoint 3: workflow docs remain the source of truth
- completion の詳細は `workflow_issue.md` と issue execution skill に置くべき
- ただし manual test で見つかった gap を閉じるには、adapter 側に minimum completion guard が必要
- したがって候補 C 単独は弱い

### consensus
- 候補 A: 却下寄り
- 候補 C 単独: 不十分
- 候補 B: 現実的
- 候補 D: 最も堅い

## 推奨するベストプラクティス

### 推奨案: 候補 D
- shim:
  - discovery/delegation entrypoint のまま維持する
  - wording は最小限だけ補強し、「issue workflow は completion contract を持つ delegated flow に委譲する」と書く
- delegated adapter skill:
  - minimum completion contract を追加する
  - issue work では、少なくとも次を完了条件にする
    - active issue が確定している
    - `requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのままではない
    - review / validate / sync を実施するか、未実施理由を report に残す
  - 未充足なら「完了」と報告しない
- workflow docs / issue execution skill:
  - 具体的な cadence, review gate, report 更新順序, completion criteria を正本として維持する
  - adapter はそこへの route と minimum guard を担当する
- manual test plan:
  - phase を明確に分ける
    1. install/static contract
    2. delegated runtime feasibility
    3. completion quality
  - 3番目で「docs 4 点がテンプレートでないこと」を明示的な pass/fail 項目にする
  - 環境 blocker と product gap を必ず分けて記録する

## 推奨する具体修正

### 1. `.codex/agents/spec-dock.toml`
- 追加すべき内容は最小限に留める
- 例:
  - issue work では、completion contract を持つ delegated flow に委譲すること
  - completion contract を満たせない場合は完了扱いにせず、blocker を報告すること

### 2. `.agents/skills/spec-dock-codex-adapter/SKILL.md`
- 明示すべきこと
  - issue execution の終了条件
  - docs 4 点がテンプレートのままなら未完了
  - review / validate / sync / report の扱い
  - blocked / fail の報告義務
- 今回の主修正ポイントはここ

### 3. `spec-dock-issue-execution` / `workflow_issue.md`
- adapter から参照される detailed completion contract を明示する
- 「テンプレート未記入は未完了」を docs と skill の両方で一致させる

### 4. manual test plan
- preflight portability を改善する
- hard-coded path 依存を避ける
- completion quality phase を独立チェックとして追加する

## 非推奨
- shim 単体に workflow completion の詳細を詰め込むこと
- host ごとに completion logic を複製すること
- manual test の blocked を product fail と混同すること

## 最終判断
- 主因は `developer_instructions` 単体ではない
- 本質は、shim -> adapter -> leaf workflow の completion contract が薄いこと
- したがって、最適な修正は
  - shim は薄いまま
  - adapter に minimum completion guard
  - leaf/workflow に詳細 completion contract
  - manual test plan に completion quality gate
  を入れることである
