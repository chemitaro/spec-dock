---
種別: research
ID: "20260607t063203z-research"
タイトル: "GPT55 Pr Monitor Stable Observation Discussion"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-07"
親: ["iss-00170"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260607t063203z-research GPT55 Pr Monitor Stable Observation Discussion

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- ユーザーが GPT-5.5 Pro と議論した「PR モニターの挙動改善」レポートを、要約で情報を落としすぎない形で issue-local research evidence として保存する。
- その上で、現行 `pr-monitor` / `github-pr-merge-preparer` / review comment wrapper / 既存 `iss-00105` discussions と照合し、`iss-00170` の要件定義へ採用すべき facts、inference、未検証事項、質問候補、edge case を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - ユーザー提供の GPT-5.5 Pro 議事録: 「PRモニターの挙動改善」。
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00105-pr-creation-and-merge-ready-monitoring-skill/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00105-pr-creation-and-merge-ready-monitoring-skill/discussions/20260521t000352z-01-interview-review-thread-state-policy.md`
- 検証手順:
  - active issue を `iss-00170` に固定した。
  - provider-side と dogfooding mirror の `pr-monitor` instructions を読み、現行 monitoring workflow、hard rules、completion rules、output schema を確認した。
  - existing wrapper の fixed REST GET endpoints と normalized JSON output を確認した。
  - `github-pr-merge-preparer` が最新 head SHA と unresolved review-thread limitation を既に merge-prepared predicate に含めていることを確認した。
  - `iss-00105` の review thread state policy discussion を読み、現行 REST wrapper baseline と fixed read-only GraphQL wrapper option の既存判断を確認した。
- 実験条件:
  - この artifact は requirement authoring 前の research evidence であり、実装・テストは未実施。
  - 外部 Web の再検索はしていない。ユーザー提供レポートとローカル repo の source / docs / scripts を照合した。

## facts / 観測できた事実 (必須)
- ユーザー提供レポートの主張:
  - 現状の `pr-monitor` は「PR 作成後または push 後に checks/statuses と Codex review を監視し、失敗や指摘を早期検知しても即終了せず、情報が出揃うまで待つ」という方針を持つ。
  - 方向性は妥当だが、「出揃った」の観測可能な定義が不足している。
  - sleep を長くするだけでは不安定さは解消しない。
  - 改善の中心は、PR の current head SHA を監視単位に固定し、checks/statuses と review/comment/thread の snapshot が安定したことを完了条件にすること。
  - GitHub には「今後レビューコメントが絶対に追加されない」ことを知らせる汎用イベントがないため、「完全に待つ」は無限待機ではなく bounded stable observation として定義する必要がある。
  - 推奨定義は「現在の PR head SHA に対して、既知の checks/statuses がすべて terminal になり、review/comment/thread の観測 snapshot が一定時間・一定回数変化しなかった状態」。
- ユーザー提供レポートによる現状評価:
  - `pr-monitor` は checks/statuses と Codex review を監視対象にしている。
  - 監視対象を GitHub Actions だけに限定せず、PR に紐づく全 checks/statuses とする記述がある。
  - Codex review は issue comments、inline review comments、review bodies を対象にすると明記されている。
  - direct `gh api` や GraphQL への自由な fallback は禁止され、決められた read-only wrapper を使う境界が定義されている。
  - ただし workflow は「checks/statuses と review の両方が出揃ったかを判定する」とだけ書かれており、観測可能な判定条件が弱い。
  - 現行 sleep policy は「checks が terminal になった後、review evidence がなければ 1〜2 回 short grace wait して Codex comments なしと結論する」と読めるため、review/comment が少し遅れて付くケースで premature success の余地がある。
- ユーザー提供レポートの不安定箇所:
  - head SHA の扱いが完了条件に十分組み込まれていない。
  - `github-pr-merge-preparer` は monitor output が最新 head SHA に対するものでなければ stale と扱う契約を持つが、`pr-monitor` 自体の完了条件には「最終結果が expected head SHA と一致していること」「途中で head SHA が変わったら観測結果をリセットすること」が強く書かれていない。
  - CI/CD と review は head SHA に対する観測なので、古い SHA の green / review なしを最新 push の結果として返すと誤判定になる。
  - `gh pr checks` は checks 完了待機には使えても、review/comment/thread の収集とは同期しない。
  - commit status は GitHub check run とは別系統の状態を持つ。
  - PR monitor は `gh pr checks` の表示だけではなく、少なくとも `statusCheckRollup`、check runs、commit statuses を現在の head SHA に紐づくものとして統合して扱うべき。
  - 現行 review 取得は Codex subset 中心であり、ユーザー要件が「PR に付くレビューを完全に待機し、すべての情報を収集する」なら不足する。
  - 必要な review data は all issue comments、all inline review comments、all review bodies、reviewDecision、review requests、review threads、Codex-authored subset、human reviewer subset、bot reviewer subset を分けた収集・報告。
  - 現行設計の最大の弱点は unresolved / resolved / outdated thread state を見られないこと。
  - thread state 不明時は limitation を隠さず `review_state_unknown` または human gate にするべき。
- ユーザー提供レポートの推奨アップデート方針:
  - `pr-monitor` の developer instructions を強化する。
  - checks/statuses と reviews/threads を読む fixed read-only wrapper を追加する。
  - `pr-monitor` の完了判定を stable snapshot ベースにする。
  - prompt-only 更新だけでも改善するが、LLM が毎回同じように解釈する保証は弱い。
  - 観測と分類は wrapper/script で deterministic に寄せ、agent は結果の要約と判断に集中させるべき。
- ユーザー提供レポートの変更対象候補:
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - `.github/agents/pr-monitor.agent.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/`
  - `.agents/skills/github-codex-pr-review-comments/scripts/`
  - `tests/test_init_update.py`
  - wrapper を追加する場合の候補:
    - `fetch_pr_observation.sh`: PR 基本情報、head SHA、reviewDecision、reviewRequests、mergeStateStatus など。
    - `fetch_pr_checks_and_statuses.sh`: statusCheckRollup、`gh pr checks` JSON、check runs、commit statuses。
    - `fetch_pr_reviews_and_threads.sh`: issue comments、inline review comments、reviews、reviewThreads。
  - 既存 wrapper 名を尊重するなら、既存 wrapper は残しつつ `review_data.json` に `all` と `codex` の両方を入れる形が後方互換上安全。
- ユーザー提供レポートの suggested JSON shape:
  - `all.issue_comments`
  - `all.review_comments`
  - `all.reviews`
  - `all.review_threads`
  - `codex.issue_comments`
  - `codex.review_comments`
  - `codex.reviews`
  - `codex.review_threads`
  - `collection.thread_state_available`
  - `collection.pagination_complete`
  - `collection.fetched_at`
- ユーザー提供レポートの完了判定案:
  - 監視単位は current head SHA。
  - expected `head_sha` が与えられた場合、最初に PR の current head SHA と照合する。
  - current head SHA が expected `head_sha` と違う場合、古い観測結果を stale として破棄する。
  - 監視中に head SHA が変わった場合も checks/reviews snapshot をリセットする。
  - final `success` / `failed` / `review_changes_requested` は latest head SHA に対してのみ返す。
- ユーザー提供レポートの checks/statuses 完了条件:
  - latest head SHA に対する statusCheckRollup / checks / statuses の取得に成功している。
  - 観測された全 check/status が terminal state である。
  - pending / queued / in_progress / waiting / requested / null conclusion が残っていない。
  - failed / error / cancelled / timed_out / action_required / startup_failure / stale が残っていれば success ではない。
  - check/status の正規化済み集合が minimum_quiet_seconds 以上、かつ 2 回以上の連続 poll で変化していない。
  - expected_check_names が与えられている場合、その check が現れるか deadline まで待つ。
  - check が 0 件の場合、即 success とはせず、少なくとも initial grace window までは pending/unknown として扱う。
- ユーザー提供レポートの reviews/comments/threads 完了条件:
  - issue comments の取得に成功している。
  - inline review comments の取得に成功している。
  - pull request reviews の取得に成功している。
  - reviewDecision / reviewRequests の取得に成功している。
  - reviewThreads wrapper が利用可能な場合、review threads の取得に成功している。
  - review/comment/thread の正規化済み snapshot が minimum_quiet_seconds 以上、かつ 2 回以上の連続 poll で変化していない。
  - reviewDecision が `CHANGES_REQUESTED` の場合、`review_changes_requested` とする。
  - unresolved actionable thread がある場合、`review_changes_requested` とする。
  - thread state が取得できず、review comment が存在し actionable か不明な場合、success ではなく `review_state_unknown` / human gate とする。
  - requested reviewer が残っており、policy 上 reviewer response を待つ必要がある場合は deadline まで `pending_review` として待つ。
- ユーザー提供レポートの stable snapshot 例:
  - `head_sha`
  - `checks[]`: source、name、state、conclusion、completed_at、link。
  - `reviews[]`: id、author、state、submitted_at、body_hash。
  - `review_comments[]`: id、author、path、line、updated_at、body_hash。
  - `review_threads[]`: id、is_resolved、is_outdated、last_comment_updated_at。
  - `stable = same_fingerprint_observed_twice && quiet_window_elapsed`
- ユーザー提供レポートで避けたい race condition:
  - checks が green になった直後に review comment が付く。
  - Actions の check run は terminal だが commit status がまだ pending。
  - 新しい push で head SHA が変わったが、古い check result を拾う。
  - review thread が outdated / resolved なのに単なる comment 存在だけで blocker 扱いする。
  - unresolved thread が残っているのに「コメントは見たが対応済みっぽい」と誤判定する。
- ユーザー提供レポートの `overall_status` 見直し:
  - 現行 `success | failed | review_changes_requested | timeout` は粗い。
  - 内部的には `success`、`check_failed`、`review_changes_requested`、`review_state_unknown`、`stale_head`、`timeout`、`blocked` などに分ける方がよい。
  - 後方互換が必要なら output は既存 `overall_status` を残し、`normalized_status` を追加する。
- ローカル確認した現行 `pr-monitor` facts:
  - provider-side Codex agent は `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml` にある。
  - provider-side GitHub agent は `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md` にある。
  - dogfooding mirror にも `.codex/agents/pr-monitor.toml` と `.github/agents/pr-monitor.agent.md` がある。
  - 現行 `pr-monitor` hard rules は direct `gh api`、direct `curl`、GraphQL、write operations への fallback を禁止している。
  - 現行 workflow step 6 は「checks / statuses と review の両方が出揃ったかを判定する」だが、stable fingerprint や quiet window の定義はない。
  - 現行 completion rules は `success | failed | review_changes_requested | timeout` であり、`stale_head`、`review_state_unknown`、`check_pending_stable_wait` のような中間分類はない。
  - 現行 sleep policy は checks terminal 後 review evidence absent の場合に 1〜2 回 short grace wait するだけで、review snapshot 安定性とは書かれていない。
  - 現行 output は `codex_review` セクション中心であり、all reviewer/human/bot subset の構造化報告はない。
- ローカル確認した existing wrapper facts:
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh` は fixed REST GET endpoints のみを呼ぶ。
  - endpoints は PR conversation comments、inline review comments、pull request reviews。
  - output は `issue_comments.json`、`review_comments.json`、`reviews.json`、`review_data.json`、`codex_report.md`。
  - `review_data.json` は raw arrays と `codex` subset を含むが、`all` namespace、review thread state、reviewDecision、reviewRequests、head SHA binding、collection completeness metadata はない。
  - wrapper は arbitrary method / endpoint / body / jq / GraphQL input を callers から受け取らない設計で、read-only boundary を保っている。
- ローカル確認した `github-pr-merge-preparer` facts:
  - PR delivery loop の coordinator であり、`pr-monitor` を read-only checks/statuses/review monitoring に再利用する。
  - workflow step 5 で `repo`、`pr`、`head_sha`、`reason` を渡して `pr-monitor` を呼ぶ。
  - workflow step 6 で monitor output が latest head SHA でない場合 stale と扱う。
  - merge-prepared predicate には「monitor result is for the latest head SHA」「review-thread unresolved state is known, or limitation is disclosed and waived」が含まれている。
  - つまり coordinator 側は latest head SHA と thread-state limitation を要求しているが、`pr-monitor` 自体の observation contract が弱い。
- ローカル確認した existing `iss-00105` facts:
  - `iss-00105` は PR creation / merge-ready monitoring skill を追加する issue。
  - `pr-monitor` は read-only watcher として維持し、fix / push / retry の owner にはしない判断がある。
  - review thread state policy discussion では、現行 REST wrapper baseline と fixed read-only GraphQL wrapper option が比較された。
  - その時点の推奨は「初期 requirement は REST baseline、thread state 不足は limitation / human gate、fixed GraphQL wrapper は design option / follow-up candidate」だった。
  - 今回 `iss-00170` は、その follow-up candidate を actual hardening issue として取り込める文脈にある。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `iss-00170` は単なる prompt wording 修正ではなく、`pr-monitor` の観測 contract を head-SHA-bound stable snapshot へ変える issue として定義するのが妥当。
  - `github-pr-merge-preparer` は既に latest head SHA と thread-state limitation を要求しているため、本 issue の primary value は `pr-monitor` 側の read-only observation がその predicate に耐えるようにすること。
  - 既存 `iss-00105` では fixed GraphQL wrapper は optional/follow-up だったが、ユーザー提供レポートは wrapper/script に deterministic observation を寄せる方針を強く推奨しているため、本 issue では wrapper 追加または既存 wrapper 拡張を requirement scope に入れるべき。
  - ただし `pr-monitor` は read-only agent であり、review reply、thread resolve、merge、push、comment mutation などの write operation を追加してはいけない。
  - 後方互換を保つには、既存 `overall_status` は残し、より細かい `normalized_status` / `observation_status` / `review_state` のような追加 field で分類を広げるのが安全。
  - `all` と `codex` subset を分けることで、既存 Codex review workflow を壊さず human/bot reviewer も報告対象にできる。
  - `check が 0 件` の扱い、expected check names、requested reviewer 待機は repository ごとの運用差が出るため、config ではなく optional input / explicit policy として慎重に定義する必要がある。
- 推測の根拠:
  - 現行 files には head SHA input と stale handling の断片はあるが、stable observation の fingerprint / quiet window / reset rule がない。
  - wrapper が fixed REST GET に制限されているため、GraphQL thread state を扱うには arbitrary fallback ではなく fixed read-only wrapper が必要。
  - `github-pr-merge-preparer` が stale monitor output と unresolved-thread limitation を既に human gate にしている。
  - ユーザー提供レポートが「観測と分類は wrapper/script で deterministic に寄せるべき」と明示している。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `gh pr view --json statusCheckRollup` だけで、必要な check run / commit status information をどこまで安定して正規化できるか。
  - `gh pr checks --json` が現在の installed GitHub CLI version でどの field / bucket を返すか。
  - fixed read-only GraphQL wrapper を追加する場合の exact query、pagination、rate limit、schema drift handling。
  - review thread state と head SHA / outdated state の関係をどの粒度で fingerprint に入れるべきか。
  - `reviewDecision`、review requests、requested reviewers の待機方針を repository default policy としてどこまで `pr-monitor` に持たせるべきか。
  - tests をどの layer に置くのが最小か。候補は installer asset parity、wrapper unit/smoke、agent instruction text assertions。
  - dogfooding mirror への反映を manual sync / direct parity edit / installer update のどの形で扱うか。
- 確認できない理由:
  - 現時点では requirement authoring 前の research phase であり、wrapper design / implementation / live PR fixture validation は未実施。
  - GitHub CLI の exact JSON shape は version と command option に依存するため、design / plan phase で実コマンド確認が必要。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 本 issue で fixed read-only GraphQL wrapper による review thread state 取得まで MUST に含めるか、それとも stable snapshot と既存 REST wrapper 拡張を first scope とし、GraphQL wrapper は follow-up に分けるか。
  - `requested reviewer` が残っている場合に deadline まで待つことを default にするか、明示 input がある場合だけ待つか。
  - check が 0 件の PR をどの grace window まで pending/unknown として待つか。
- pressure-test question として切り出すべき候補:
  - 最重要候補: `iss-00170` の必須範囲に fixed read-only GraphQL wrapper を含めるか。
- 質問せずに解決できた候補:
  - `pr-monitor` を write-capable にするかどうか: 既存 hard rules と `github-pr-merge-preparer` forbidden writes から、write operation は scope 外。
  - provider-side authority: epic-00067 と repo guidelines から、`src/spec_dock/assets/install_root/` が agent-tooling assets の source of truth。
  - dogfooding mirror: `.codex/agents/`, `.github/agents/`, `.agents/skills/...` は provider-side と parity を保って検証対象にする。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - 「完全に待つ」
  - 「出揃った」
  - 「Codex review」
  - 「all reviews」
  - `overall_status=failed`
  - `review_changes_requested`
  - `review_state_unknown`
- 既存 docs / code / tests / discussions での使われ方:
  - 現行 `pr-monitor` の「出揃った」は自然言語で、具体的な fingerprint / quiet window ではない。
  - 現行 `pr-monitor` の review は Codex review 中心で、issue comments / inline review comments / review bodies の Codex subset を主に要約する。
  - ユーザー提供レポートの「all reviews」は Codex だけでなく human / bot reviewer、reviewDecision、reviewRequests、reviewThreads を含む。
  - `github-pr-merge-preparer` の merge-prepared predicate は review-thread unresolved state が known であること、または limitation が disclosed and waived であることを要求する。
  - `failed` は check failure と observation failure / stale head / blocked を混ぜやすいため、report は `normalized_status` 追加を推奨している。
- 判断が必要な理由:
  - 要件定義では「完全に待つ」を無限待機ではなく bounded stable observation として固定しないと、実装・テスト・レビューで成功条件がぶれる。
  - Codex-only review と all review signals を混同すると、ユーザーが期待する PR monitoring が不足する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Checks green 直後に Codex review comment が遅れて付く。
  - Check run は completed/success だが commit status が pending のまま残る。
  - PR monitoring 中に新しい push が入り head SHA が変わる。
  - expected head SHA が渡されたが、PR current head SHA は既に別 SHA になっている。
  - review comment はあるが、thread は resolved / outdated で blocker ではない。
  - unresolved review thread があるが、現行 REST wrapper では resolved state が分からない。
  - `gh pr checks` では pass に見えるが statusCheckRollup に失敗・pending・neutral などが残っている。
  - check がまだ 0 件で、CI がまだ開始していないだけなのに success と誤判定する。
  - requested reviewer が残っているが、bot auto-review を待つべきなのか human review request を待つべきなのか判断が曖昧。
  - non-required check が fail しているが、merge button は押せる。
  - wrapper が missing / auth failure / rate limit / schema mismatch で review thread state を取得できない。
- その edge case が requirement / design / plan に与える影響:
  - requirement には head SHA binding、snapshot reset、quiet window、thread-state limitation、zero-check grace、normalized status を acceptance criteria として含める必要がある。
  - design では wrapper の deterministic output、fingerprint field、terminal state mapping、failure taxonomy、fallback/human gate の境界が必要。
  - plan では wrapper tests、agent instruction parity、dogfooding mirror update、GitHub CLI version-sensitive smoke を分ける必要がある。

## implications / 判断への含意 (必須)
- Requirement へ採用すべき事項:
  - `pr-monitor` は latest/current head SHA に bound した observation だけを final とする。
  - expected head SHA と current head SHA がずれる場合は stale / blocked / human gate として扱い、古い observation を success にしない。
  - 監視中に head SHA が変わった場合、checks/reviews/comments/threads の snapshot をリセットする。
  - checks/statuses と reviews/comments/threads は terminal/complete だけでなく stable であることを求める。
  - stable は same normalized fingerprint が複数 poll で一致し、minimum quiet window が経過していること。
  - check 0 件は即 success ではなく grace window まで unknown/pending とする。
  - all review signals と Codex subset を分けて収集・報告する。
  - unresolved actionable thread がある場合は review blocker。
  - thread state 不明で actionable か判断できない comment がある場合は success ではなく `review_state_unknown` / human gate。
  - `overall_status` 後方互換を守りつつ `normalized_status` などで詳細分類を返す。
  - direct arbitrary API fallback と write operations は禁止し、必要な GitHub API は fixed read-only wrapper 経由に限定する。
- Design / plan へ送るべき事項:
  - fixed wrapper を新設するか既存 wrapper を拡張するか。
  - GraphQL reviewThreads を本 issue に含めるか。
  - statusCheckRollup / check runs / commit statuses の正規化 source priority。
  - fingerprint の canonical sorting / body hashing / timestamp handling。
  - wrapper output schema と tests。
  - provider assets と dogfooding mirror parity。
- Interview が必要になり得る事項:
  - fixed read-only GraphQL wrapper を issue scope の MUST にするか。
  - requested reviewers / expected check names を default behavior にするか explicit input に留めるか。

## リスク/制約 (任意)
- GraphQL wrapper を含める場合、issue scope は prompt-only hardening より大きくなる。
- GraphQL wrapper を含めない場合、review thread state の正確性は限定され、human gate が増える。
- LLM instructions のみで stable observation を要求しても、毎回同じ分類・待機・fingerprint を再現できるとは限らない。
- Review body / comment body を fingerprint に含める場合、PII / secrets を永続 artifact に残さないよう body hash を使う方が安全。
- `pr-monitor` は read-only agent なので、観測結果を受けた修正・push・review reply・thread resolve は `github-pr-merge-preparer` / orchestrator / human gate 側に残す必要がある。

## 反映先 (任意)
- reflected_to:
  - `requirement.md`: `iss-00170` の scope、completion semantics、acceptance criteria、edge cases。
  - `report.md`: research artifact adoption evidence and Spec Authoring Gate。
  - ...

## 参考（References） (任意)
- ...
