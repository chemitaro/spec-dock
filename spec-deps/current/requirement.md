---
種別: 要件定義書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-23"
親: []
---

# issue-28-runtime-regression-bugs manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する — 要件定義（WHAT / WHY）

## 目的

- manual regression で再現した runtime の重大不具合を修正し、通常操作での整合性破綻を防ぐ。
- `local-only` と `GitHub-linked` が混在する現在設計でも、少なくとも prototype 段階で安全に操作できる状態へ引き上げる。
- 今後の `design.md` / `plan.md` / 実装委任の正本となる bugfix scope と acceptance criteria を固定する。

## 背景・現状

- 2026-03-15 の local/stub manual regression と GitHub live manual regression により、create race、status/readiness 不整合、GitHub target 誤解釈、validate gap など複数の不具合が確認された。
- これらの不具合は、単なる UX ノイズではなく、tree 破損、誤リンク、誤認、復旧困難といった実害に直結する。
- dogfooding を本格化する前に、まず runtime の基本信頼性を上げる必要がある。

主な根拠:

- `manual-tests/reports/2026-03-15-manual-regression-sweep/summary.md`
- `manual-tests/reports/2026-03-15-manual-regression-sweep-github-live/summary.md`
- `spec-deps/current/discussions/005-disc-duplicate-epic-id-race-analysis.md`
- `spec-deps/current/discussions/006-disc-github-linkage-simplification-analysis.md`
- `spec-deps/current/discussions/007` から `016`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - `spec-dock` の maintainer
  - runtime CLI を利用する開発者
  - `spec-dock` を操作する coding agent
- 代表シナリオ:
  - `new initiative|epic|issue|doc` や `import issue` を連続または並列で作成する
  - local-only issue を active にし、deps / validate / sync を使う
  - GitHub issue URL や issue number を使って import / active / status 確認を行う
  - GitHub-linked issue の状態変化を運用上安全に読む
  - 壊れた状態や欠損を validate / doctor 系で発見し、復旧方針を得る

## スコープ

### MUST

- create allocator race を修正する
  - `new initiative|epic|issue|doc` と create-like な `import issue` で id / sequence / GitHub linkage が並列実行でも重複しないこと
- discussion sequence race を修正する
  - `new doc` で duplicate sequence を予防し、validator でも検知できること
- local-only issue の readiness contract を整備する
  - `deps check` と `active set` が同じ readiness / status 契約で動作すること
- required artifact 欠損を `validate` が検知できるようにする
- recoverability を改善する
  - `.meta.json` の保護方針を維持したまま、`doctor` コマンドで supported な診断・修復導線を用意すること
- active 未設定時の導線を改善する
  - `active` が未設定でも human/agent が次に何を見るべきか分かること
- GitHub target 解釈を安全化する
  - URL import で `owner/repo` を無視した誤リンクを防ぐこと
  - numeric target の曖昧性を下げること
  - active/deps の URL target でも `owner/repo` を失わず exact node を選べること
  - dependency ref でも current-repo shorthand と foreign scoped ref を区別できること
- create CLI contract を整える
  - `new issue` にも explicit GitHub create surface を用意すること
- GitHub-linked issue の freshness 契約を改善する
  - stale projection を authoritative と誤読しにくくすること
- create/post-create failure 契約を閉じる
  - GitHub issue 作成後の local failure / cleanup failure が outcome 別に安全な guidance を返すこと
  - create 中間状態や partial local write を remote-only failure と誤分類しないこと
  - create 中の一時状態を read-side corruption と誤診断しないこと

### SHOULD

- local-only / GitHub-linked issue の status について、今後の `close/reopen` や `link/unlink` に耐える表現に寄せる
- warning / error / machine-readable output の改善により、agent が次アクションを判断しやすい形にする
- validator / doctor / create contract が同じ artifact/status contract を再利用できるようにする

### MUST NOT

- `initiative` / `epic` / `issue` / `doc` の既存 file-based runtime を大幅に別方式へ置き換えない
- prototype bugfix の範囲を超えて、大規模な再設計や DB 導入に踏み込まない
- GitHub 依存を増やすだけで local-first の逃げ道を失わせない
- backward compatibility を無視して既存 CLI surface を破壊しない

### OUT OF SCOPE

- 全ての future roadmap 機能の実装
- `issue close/reopen` や `link/unlink` の完全実装
- runtime 全面リライト
- 本 issue とは独立したドキュメント体系の刷新

## バグ別の要求整理

### B01 create allocator race

- 並列 create でも duplicate id が発生しないこと
- duplicate id を partial write 後に事後検知するだけでは不可

### B02 discussion sequence race

- 並列 `new doc` でも duplicate seq が発生しないこと
- validator に duplicate seq 検知があること

### B03 local-only deps/active inconsistency

- local-only issue の初期 `authority=local`、初期 `effective_status=open` であること
- local-only issue の初期 effective status が deterministic であること
- `deps check` の readiness と `active set` の guard が一致すること
  - 共通 readiness rule は少なくとも `blockers=[]` かつ `effective_status=open` を ready と扱うこと

### B04 validate gap

- node kind ごとに required artifact contract があること
- required artifact 欠損を `validate` が失敗として扱うこと

### B05 repair gap

- `.meta.json` を直接 chmod/edit しなくても、`doctor` で診断・修復方針が得られること

### B06 active-not-set pathway gap

- active 未設定時でも、CLI と path の両面で fallback 導線があること

### B07 import wrong-repo risk

- GitHub URL を使う import は current repo と一致検証されること
- foreign repo を許すなら明示 opt-in であること

### B08 create UX asymmetry

- `new issue` でも initiative/epic と同様に explicit GitHub create intent を表現できること

### B09 stale projection

- linked issue の status source / freshness が利用者に明示されること
- linked issue を `--github` なしで読む場合、少なくとも `source=cache` が露出すること
- `--github` なしの読み取りで stale の可能性が分かること

### B10 numeric target ambiguity

- `active set` などで target intent を明示指定できること
- pure number の誤解釈が減ること
  - bare number の fail 化は本 issue の対象外とし、まずは explicit flags の追加を優先すること

### B11 repo-scoped reference surface gap

- foreign repo を link/import できても、active/deps target や dependency ref が repo scope を表現できなければ運用が閉じない
- canonical GitHub URL や scoped dependency ref を、number-only shorthand と区別して扱える必要がある

### B12 create intermediate state gap

- create は GitHub side effect、scaffold copy、meta write、post-write verify という段階を持つ
- これを単一 bool や missing artifact だけで扱うと、partial local write と in-progress state を誤診断し、unsafe rerun や誤った corruption guidance を返す

## 境界

### Always

- manual regression で再現した実害に優先して対処する
- local/stub と GitHub live の両方で acceptance を考える
- safety net と根本対策を分けて設計する

### Ask

- backward compatibility を壊す CLI surface 変更が必要な場合
- GitHub mandatory 化のように product policy 自体を変える場合
- 本 issue のスコープを超える architecture change が必要な場合

### Never

- `warning` だけで誤リンクや duplicate create を許容しない
- 既知の unsafe default を「仕様だから」で温存しない

## 非交渉制約

- コード変更は既存 runtime layering を尊重する
- 既存 asset/scaffold 変更は shipped API 変更として扱う
- local-only の逃げ道は prototype 段階では維持する
- GitHub live manual regression で再確認できる acceptance を意識する

## 受け入れ条件

### AC-001 create atomicity

- Given:
  - 同一 repo / 同一親配下で `new epic` または `new issue` または `new doc` または `import issue` を並列実行する
- When:
  - manual regression と同等の並列 create を再実行する
- Then:
  - duplicate id / duplicate GitHub linkage が発生しない
  - `new doc` の sequence allocator は `S02` で引き続き保護され、`import issue` は新たな sequence allocator 義務を持ち込まない
  - create 結果が validate/sync を壊さない
  - `new initiative|epic|issue` の create-mode は `gh issue create` 前に read-only graph preflight を実施し、stable tree failure や stable parent absence が分かる場合は remote side effect を起こさず no-side-effect fail する
  - ただし lock 取得後は authoritative な graph reload / parent revalidation / uniqueness revalidation を継続し、preflight が advisory ではなく fail-fast であっても最終判定境界を置き換えない

### AC-002 local-only readiness

- Given:
  - local-only issue が通常 create されている
- When:
  - `deps check` と `active set` を実行する
- Then:
  - `authority=local`、`effective_status=open` と整合した readiness 判定になる
  - `blockers=[]` なのに `ready=false/state=unknown` となる矛盾が解消されている

### AC-003 required artifact validation

- Given:
  - initiative / epic / issue の required artifact、または discussion markdown/integrity contract のいずれかを壊す
- When:
  - `validate` を実行する
- Then:
  - 欠損が failure として検知される

### AC-004 GitHub URL safety

- Given:
  - foreign repo の GitHub issue URL を import target に渡す
- When:
  - `import` を実行する
- Then:
  - current repo と一致しない場合は誤リンクせず、安全側に失敗する
  - 例外が許される場合でも明示 opt-in が必要である
  - 明示 opt-in で foreign repo import を許可した場合でも、後続の `sync --github` / `deps check --github` は同じ foreign repo identity を維持し、current repo の同番号 issue に誤 hydrate しない
  - foreign repo import の linked uniqueness は `repo + issue_number` で評価され、`other/repo#123` と `current/repo#123` を不必要に同一視しない
  - その結果 `github issue number` が repo 全体では一意でなくなった場合、`--github-issue <n>` の selector は ambiguous fail し、誤って任意の node を選ばない

### AC-005 freshness clarity

- Given:
  - GitHub-linked issue の remote state が local cache と食い違っている
- When:
  - `deps check` などの status 読み取りを `--github` なしで実行する
- Then:
  - 少なくとも `source=cache` が露出する
  - source / stale / freshness が明示され、latest と誤認しにくい

### AC-015 same-repo URL-linked sync fetch efficiency

- Given:
  - current repo の issue を canonical GitHub URL で link/import している
  - `github_repo_owner/name` は保存されている
- When:
  - `sync --github` または同等の GitHub-aware 読み取りを実行する
- Then:
  - current repo issue が `issue_index()` ですでに取得済みなら、同じ `(repo, issue_number)` へ追加の `issue_view_snapshot()` を重ねない
  - current repo issue が index limit などで未取得の場合だけ fallback fetch を許す
  - foreign repo target の追加 fetch は維持され、same-repo / foreign-repo を取り違えない

### AC-006 active pathway

- Given:
  - active が未設定である、または persisted active manifest は残っているが `spec-dock/active/*` entrypoint が欠損している
  - または `spec-dock/active/*` が `system/active-none/*` を向く placeholder fallback のまま残っているが、persisted active manifest から real node を解決できる
- When:
  - `active show` または `spec-dock/active` を参照する、または `spec-dock update` で recovery を実行する
- Then:
  - `spec-dock/active` は未設定でも解決可能な入口として存在する
  - 未設定であることと、次に取るべき action/fallback path が分かる
  - persisted active manifest が健全な場合は、`spec-dock update` が `context-pack.md` だけでなく `spec-dock/active/{initiative,epic,issue}` の entrypoint も同じ active state に復元する
  - placeholder fallback は healthy active state ではなく recoverable fallback として扱われ、persisted active manifest から実 node を解決できる場合は placeholder のまま残らない
  - persisted active manifest の `path` は hint に過ぎず、その path が repo 内の別 node を指していても `.meta.json` の `id` / `type` が manifest entry と一致しない限り recovery target として採用されない
  - `path` が same-layer prefix (`iss-` / `epic-` / `init-`) だけ合う誤 node を指している場合も fail-closed とし、id-based recovery か placeholder fallback へ倒れる

### AC-007 CLI symmetry and disambiguation

- Given:
  - create / active target を script または agent から操作する
  - または GitHub issue 作成後に local phase が失敗し、既存 issue を relink する recovery hint が必要になる
- When:
  - explicit GitHub create intent や target intent を指定する
- Then:
  - `new issue` でも explicit GitHub create を表現できる
  - `active set` などで node id と GitHub issue number を明示指定できる
  - ただし `--github-issue <n>` が複数 node に一致する場合は、曖昧成功ではなく ambiguity error になり、operator は `--id <node-id>` で対象を確定できる
  - post-create local failure の recovery hint は kind ごとに再実行可能であり、`--title` と必要な parent selector（`--initiative` / `--epic`）を欠いた不完全コマンドを案内しない
  - その recovery hint は repo root 前提の相対 path に依存せず、その時の cwd からでも実行できる command surface である

### AC-017 create outcome-specific recovery guidance

- Given:
  - `new initiative|epic|issue --create-github-issue` の create path が GitHub issue 作成前または作成後に失敗する
- When:
  - failure surface を operator が確認する
- Then:
  - outcome class `pre_github_fail` / `post_github_remote_only_fail` / `post_github_local_write_fail` / `post_github_local_write_success_cleanup_fail` / `post_github_body_and_cleanup_fail` が設計/実装/検証で対応付けられている
  - `pre_github_fail` は remote side effect がない no-side-effect failure として扱われ、created issue number をでっち上げない
  - `post_github_remote_only_fail` は created issue number を保持したまま rerun/link または remote cleanup の guidance を返してよい
  - `post_github_local_write_fail` は local write 未コミット枝では rerun/link guidance を返してよいが、local write committed 済み枝では doctor-first guidance を返し、blind rerun を促さない
  - `local-write-committed cleanup failure` では raw `release_error` 単独露出に退行せず、`created_github_issue_number` を保持したまま「まず local node と doctor を確認する」guidance を返す
  - `post_github_body_and_cleanup_fail` では primary local failure と cleanup failure を併記しつつ、上記 outcome class に応じた guidance を失わない
  - blind rerun を促す guidance は `local-write-committed cleanup failure` に適用しない
  - provider-side runtime と checked-in dogfooding runtime の両方で、上記 5 class の outcome-specific guidance contract を同じ粒度で維持する

### AC-008 doctor guidance

- Given:
  - duplicate id/seq、missing artifact、broken meta、stale active pointer、stale create lock のいずれかが存在する
- When:
  - `doctor` を実行する
- Then:
  - 問題の種別と修復方針が supported path として提示される
  - current repo `#123` と foreign repo `other/repo#123` が併存する正常系では、current repo slug を解決できる限り ambiguity false positive を返さない
  - create lock failure / release failure / metadata write failure の error message から案内される doctor command は、repo-local shortcut の有無や現在の cwd に依存せず、その repo 上で実際に実行できる command である

### AC-009 duplicate sequence validation

- Given:
  - discussion sequence が重複した壊れた状態が存在する
- When:
  - `validate` を実行する
- Then:
  - duplicate seq が failure として検知される

### AC-010 dogfooding runtime parity

- Given:
  - provider-side shipped runtime に `doctor` や explicit target flags などの新 command surface、または repo-scoped GitHub linkage/snapshot handling の修正が追加されている
- When:
  - この repo の checked-in dogfooding workspace `spec-dock/scripts/spec-dock` を実行する
- Then:
  - checked-in consumer runtime でも同じ command surface が利用できる
  - create failure message から案内される `spec doctor` がこの repo 上で実際に起動できる
  - current repo issue `#123` と foreign repo issue `other/repo#123` のような same-number coexistence でも、checked-in consumer runtime が provider-side runtime と同じ repo-aware uniqueness / snapshot resolution を示す

### AC-011 current repo slug parity across github-aware commands

- Given:
  - current repo origin が解決できる
  - current repo の unscoped linked issue / epic / initiative と GitHub snapshot が存在する
- When:
  - `sync --github` または `active set --github` または `deps check --github` を実行する
- Then:
  - `sync --github` と同じ current repo slug-aware status resolution が使われる
  - current repo linked issue が `unknown/stale` に退行せず、GitHub の実 status を readiness / JSON / activation 判定へ反映できる
  - `issue_index()` が current repo の unscoped linked epic / initiative / issue を取りこぼした場合でも、current repo slug を補って `issue_view_snapshot()` fallback が行われ、`unknown/stale` のまま放置されない
  - `deps check` は initiative / epic / issue の target 自身の resolved status を inspection / JSON の `target_status` として含み、target が issue 以外でも `unknown/stale` に退行しない
  - 上記の `target_status` 契約は local target と `--github` target の両方で維持される

### AC-016 current-repo-aware branch inference under repo overlap

- Given:
  - current repo issue `#123` を指す numeric branch 名（例: `123-fix-login`, `issue-123`）で作業している
  - foreign repo issue `other/repo#123` が同じ tree に共存している
- When:
  - `sync --github` または branch auto-update を伴う `sync` を実行する
- Then:
  - branch-based active inference は bare `github_issue_number` だけで曖昧化せず、current repo slug を解決できる限り current repo `#123` を優先して active auto-update できる
  - current repo slug を解決できるのに current repo scope に一致する numeric candidate が 0 件の場合、foreign repo numeric match を暗黙採用せず fail-closed に倒れる
  - current repo scope に一致する numeric candidate が複数ある場合も ambiguity として fail-closed に倒れる
  - current repo slug が解決できない場合だけ ambiguity / no-match の fail-closed を維持する

### AC-012 domain/application validation boundary

- Given:
  - in-memory graph または partially-written tree を検証する
- When:
  - domain の graph validation API を実行する
- Then:
  - domain validation は graph/deps/linkage の structural invariant に集中し、on-disk artifact existence に依存しない
  - required artifact matrix の欠損検査は application/use-case 側の preflight として維持される

### AC-013 repo-aware numeric deps resolution

- Given:
  - current repo の issue `#123` を指す既存 numeric deps ref `depends_on: [123]` が存在する
  - foreign repo issue `other/repo#123` が同じ tree に追加される
- When:
  - `validate` / `sync` / deps topology compile を実行する
- Then:
  - current repo slug が解決できる限り、bare numeric ref `123` は current repo issue を継続して指す
  - current repo slug が解決できず scoped/unscoped が混在する場合だけ fail-closed に倒れる

### AC-014 stale active pathfile healing

- Given:
  - symlink 制限環境で `spec-dock/active/*.path` fallback が使われている
  - `.path` が stale になり、`_resolve_existing_active_entrypoint()` が `None` を返す
- When:
  - `spec-dock update` を実行する
- Then:
  - stale `.path` は残置されず、persisted/recovered target があればそこへ再生成される
  - target も壊れていれば placeholder へ戻る

### AC-018 repo-scoped exact target resolution

- Given:
  - current repo `#123` と foreign repo `other/repo#123` が同じ tree に共存している
- When:
  - `active set https://github.com/other/repo/issues/123` または `deps check https://github.com/other/repo/issues/123` を実行する
- Then:
  - canonical GitHub URL に含まれる `owner/repo` は parse/application の途中で失われない
  - target 解決は exact repo scope で foreign node を選べる
  - bare `123` / `--github-issue 123` の unscoped selectorは convenience selector のまま残してよいが、repo-scoped URL target と同じ意味に潰さない

### AC-019 scoped dependency reference contract

- Given:
  - current repo `#123` と foreign repo `other/repo#123` が同じ tree に共存している
  - dependency ref は bare numeric shorthand と scoped ref の両方を使い得る
- When:
  - `validate` / `sync` / `deps check` が dependency topology を解決する
- Then:
  - bare numeric ref `123` は current-repo-only shorthand として fail-closed に扱われる
  - foreign issue を dependency にしたい場合は `owner/repo#123` または canonical GitHub URL のような scoped ref で exact に解決できる
  - docs / error message は上記 contract と矛盾しない

### AC-020 create intermediate state safety

- Given:
  - `new` または create-like `import` が GitHub side effect 後、scaffold copy / meta write / post-write verify の途中で失敗する
  - または read-only command が create 中間相と競合する
- When:
  - operator が failure surface、`validate`、`doctor`、`sync` などを確認する
- Then:
  - partial local write は remote-only failure と誤分類されず、blind rerun ではなく doctor-first / partial cleanup guidance へ倒れる
  - create lock 下の missing `.meta.json` は create-in-progress / stale create 系として分類でき、恒久 corruption と混同しない
  - lock が無い missing `.meta.json` は引き続き corruption / missing artifact として扱われる
  - provider-side runtime と checked-in dogfooding runtime の両方で同じ中間状態 contract を維持する

### AC-021 no-origin continuity for current-repo linked nodes

- Given:
  - current repo linked node が `github.issue_number` を持つ
  - same-number foreign repo node が共存しうる
  - workspace を copy するなどして `origin` を解決できない環境へ移ることがある
- When:
  - current repo slug を解決できる状態で create/import/sync などが current-repo linked node を扱う
  - またはその後に no-origin workspace で `sync --github` / `validate` / `doctor` / `deps check` を実行する
- Then:
  - current-repo linked node は、current repo slug を解決できるうちに persisted metadata へ repo scope を正規化/backfill できる
  - safe backfill 対象は、少なくとも `github.issue_number` を持ち、`github.repo_owner` / `github.repo_name` が両方未設定で、current repo slug を解決でき、かつ current repo target intent を明示できる trusted context を持つ node に限る
  - `sync --github` のような bulk mutate path で lone unscoped legacy linkage を current repo と uniqueness だけでみなして silent backfill してはならない
  - same-number foreign repo node の共存自体は safe backfill の禁止理由ではないが、それだけで current repo evidence と見なしてはならない
  - `github.repo_owner` または `github.repo_name` の片側だけが入った partial scope、同じ `(current_repo_slug, issue_number)` へ 2 件以上の unscoped/current-repo candidate が見える状態、または explicit current-repo scoped duplicate がある状態は safe backfill せず fail-closed に残す
  - no-origin へ移った後も、その正規化済み current-repo linkage だけを理由に scoped/unscoped ambiguity fail-closed へ落ちない
  - truly ambiguous mixed scope graph は引き続き fail-closed に倒れてよい
  - `--github-issue <n>` の convenience selector は overlap 下で fail-closed を維持してよいが、canonical URL と `--id` は no-origin 継続でも使い続けられる
