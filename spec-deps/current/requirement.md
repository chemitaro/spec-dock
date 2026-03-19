---
種別: 要件定義書（Issue）
ID: "issue-28-runtime-regression-bugs"
タイトル: "manual regression で見つかった runtime の整合性/GitHub連携不具合を修正する"
関連GitHub: ["28"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-17"
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
- create CLI contract を整える
  - `new issue` にも explicit GitHub create surface を用意すること
- GitHub-linked issue の freshness 契約を改善する
  - stale projection を authoritative と誤読しにくくすること

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
- When:
  - `active show` または `spec-dock/active` を参照する、または `spec-dock update` で recovery を実行する
- Then:
  - `spec-dock/active` は未設定でも解決可能な入口として存在する
  - 未設定であることと、次に取るべき action/fallback path が分かる
  - persisted active manifest が健全な場合は、`spec-dock update` が `context-pack.md` だけでなく `spec-dock/active/{initiative,epic,issue}` の entrypoint も同じ active state に復元する

### AC-007 CLI symmetry and disambiguation

- Given:
  - create / active target を script または agent から操作する
- When:
  - explicit GitHub create intent や target intent を指定する
- Then:
  - `new issue` でも explicit GitHub create を表現できる
  - `active set` などで node id と GitHub issue number を明示指定できる
  - ただし `--github-issue <n>` が複数 node に一致する場合は、曖昧成功ではなく ambiguity error になり、operator は `--id <node-id>` で対象を確定できる

### AC-008 doctor guidance

- Given:
  - duplicate id/seq、missing artifact、broken meta、stale active pointer、stale create lock のいずれかが存在する
- When:
  - `doctor` を実行する
- Then:
  - 問題の種別と修復方針が supported path として提示される
  - current repo `#123` と foreign repo `other/repo#123` が併存する正常系では、current repo slug を解決できる限り ambiguity false positive を返さない

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
  - current repo の unscoped linked issue と GitHub snapshot が存在する
- When:
  - `active set --github` または `deps check --github` を実行する
- Then:
  - `sync --github` と同じ current repo slug-aware status resolution が使われる
  - current repo linked issue が `unknown/stale` に退行せず、GitHub の実 status を readiness / JSON / activation 判定へ反映できる

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
