# S03/S04 v6 Blue Team report-only repair brief

## 結論

変更対象は、指定ブランチの canonical `report.md` **1ファイル・2セクションだけ**とする。修正内容は、`827e439d...` の commit ledger 追記と、`Delegated Worker Evidence` の S03/S04 行に残る「v5修正をこれからpushする」という時制の訂正に限定する。

GitHub connector では、named branch `codex/iss-00354-chatgpt-context-contract` の tip が `3b0d255d38272b431c364cdf65daeac2786b7ead` と一致することを確認した。exact HEAD の `report.md` でも、commit ledger が `150d81a3...` で止まり、S03/S04 worker 行に `v5 report-only修正をpush後` が残っている。
これは Red Team v6 の唯一の P1 `RT-354-S03S04-V6-001` と一致する。

## 1. 編集対象

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md
```

編集するのは次の二箇所のみ。

1. `#### コミット`
2. `#### 委任 worker 証跡（Delegated Worker Evidence）` の `S03-S04` 行

EAL、requirement/design/plan、Final Gate、review artifact、implementation brief、runtime/test欄などへ修正範囲を広げない。

## 2. 最小修正

### A. `#### コミット`

既存の `150d81a3...` 行の直後に、次の履歴を full SHA で一行追加する。

```text
827e439d20557ef99e05f8ac844310915acce704
```

記録する commit message は、GitHub 上の実値である次の文字列を使う。

```text
fix(s03-s04): v4修正でdirect transport testとreportを反映
```

既存行と同じ形式で、指定ブランチへ push 済みであることを記録する。`827e439d...` は v5 Fresh Red Team の reviewed source identity のまま保持し、`150d81a3...` を削除・置換しない。

`3b0d255d...` または今回新しく生成される repair commit SHA を、report 自身に自己参照させる必要はない。Red Team v6 もその欠落を finding としていない。

### B. `Delegated Worker Evidence` の S03/S04 行

現在の次の趣旨を除去する。

```text
v5 report-only修正をpush後、同一 resulting HEADでv6 PASSを確認してから...
```

S03/S04 行では、v1〜v5 の verdict 列挙を改変せず、その末尾だけを v6 の実績へ進める。

```text
v6 FAIL（P1×1: RT-354-S03S04-V6-001）
```

親統合判断は、次の意味に限定する。

```text
v5 report-only修正はpush済み。
RT-354-S03S04-V6-001を唯一の残件とし、
Fresh Red Team v7でP0/P1=0を確認するまで両closureを保留し、
S05へ進まない。
```

「push済み」は v5 report-only commit の既成事実を表す。今回の新しい repair commit を report 本文中で「push予定」「push後」と自己参照させない。

## 3. 履歴と identity の保存

次を不変とする。

* v1〜v6 の review verdict、finding、reviewed source、artifact 内容を上書きしない。
* 添付の v6 `review.md` は read-only evidence とし、修正・再生成しない。
* v5 reviewed source は引き続き `827e439d20557ef99e05f8ac844310915acce704`。
* `150d81a3...` は v3 repair／v4 reviewed source の historical identity として残す。
* v5の `FAIL / P1=1` を PASS または resolved に変更しない。
* v6の `FAIL / P1=1` も Blue Team側で resolved、PASS、P0/P1=0へ先取りしない。
* S03/S04 closure、S05開始、PR、merge、Issue closeは Fresh Red Team v7 PASSまで保留する。S03/S04は同一 reviewed HEADで両方を閉じるという既存計画を維持する。

## 4. 検証コマンド

```bash
BRANCH='codex/iss-00354-chatgpt-context-contract'
BASE='3b0d255d38272b431c364cdf65daeac2786b7ead'
REPORT='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md'
```

### 4.1 作業開始 identity

```bash
test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$BASE"
```

いずれかが失敗した場合は編集を開始しない。

### 4.2 report identity inspection

Commit ledger 内に full SHA と正しい commit message があることを確認する。

```bash
sed -n '/^#### コミット$/,/^#### メモ$/p' "$REPORT" |
  grep -F '827e439d20557ef99e05f8ac844310915acce704'

sed -n '/^#### コミット$/,/^#### メモ$/p' "$REPORT" |
  grep -F 'fix(s03-s04): v4修正でdirect transport testとreportを反映'
```

Worker evidence の stale wording が消え、v6 finding と次ゲートが記録されていることを確認する。

```bash
WORKER_BLOCK="$(
  sed -n \
    '/^#### 委任 worker 証跡（Delegated Worker Evidence）$/,/^#### 親実装例外/p' \
    "$REPORT"
)"

! grep -F 'v5 report-only修正をpush後' <<<"$WORKER_BLOCK"
! grep -F '同一 resulting HEADでv6 PASSを確認' <<<"$WORKER_BLOCK"

grep -F 'RT-354-S03S04-V6-001' <<<"$WORKER_BLOCK"
grep -F 'Fresh Red Team v7' <<<"$WORKER_BLOCK"
```

`3b0d255d...` の report 内自己参照を合格条件に加えてはならない。

### 4.3 Markdown／diff validation

```bash
git diff --check
git diff -- "$REPORT"
```

### 4.4 scope audit

Commit前の差分は canonical `report.md` 一つだけでなければならない。

```bash
test "$(git diff --name-only)" = "$REPORT"
git status --short --branch
```

Commit後は、v6 reviewed HEAD から新HEADまでの変更ファイルが同じ一ファイルだけであることを確認する。

```bash
test "$(git diff --name-only "$BASE"..HEAD)" = "$REPORT"
test -z "$(git status --porcelain=v1)"
```

pytest、ruff、mypy、provider update、projection regenerationは、この report-only P1を閉じるための必須検証ではない。実行して予期しない差分が発生しても採用しない。

## 5. Commit／push

検証合格後、`report.md` だけを commit する。

```bash
git add -- "$REPORT"
git commit -m 'docs(iss-00354): v6 report ledger残差を修正'
git push origin "HEAD:$BRANCH"
```

push後に local／remote parityを確認する。

```bash
git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")"
test -z "$(git status --porcelain=v1)"
```

さらに GitHub connector で、新しい full SHA と named branch tipを比較し、次を確認する。

```text
status = identical
ahead = 0
behind = 0
```

新しい SHA は事前予測せず、push後に確定した値だけを Fresh Red Team v7 の review source とする。

## 6. 次のレビューゲート

新規 thread の **Fresh Red Team v7** を、次の条件で実行する。

* Repository: `chemitaro/spec-dock`
* Branch: `codex/iss-00354-chatgpt-context-contract`
* Source HEAD: push後に確定した exact full SHA
* default branch fallback: 禁止
* mutation: read-only
* review scope: `RT-354-S03S04-V6-001` の解消確認だけ

確認対象は次の三点。

1. `#### コミット` に `827e439d20557ef99e05f8ac844310915acce704` が full SHA で存在する。
2. `Delegated Worker Evidence` が v5 report-only pushを未来条件として扱っていない。
3. `3b0d255d...` または新しい repair commit SHAの report 内自己参照を要求していない。

Fresh Red Team v7 が `P0=0 / P1=0` を返すまで、S03/S04をcloseせず、S05、PR、merge、Issue closeへ進まない。

## 7. Out of scope

変更禁止:

* production runtime、application、domain、infra
* unit、integration、e2e tests
* requirement、design、plan、ADR、assurance
* provider／installed／dogfood projection
* Review resource、provider assets、review policy
* v1〜v6 review artifacts、v5 repair brief
* EALや別のcurrent-state文言の包括的整理
* architecture変更、追加要件、追加設計、追加テスト
* patch、ZIP、代替案の生成
* `3b0d255d...` または新repair SHAの自己参照要件
* S03/S04 closure、S05開始、PR、merge、Issue close

別添の failure taxonomy／application fault boundary に関する設計判断は、本P1とは無関係であり採用しない。

## 8. Stop conditions

次の場合は commit せず停止する。

* 作業開始時の branch tip が `3b0d255d...` でない。
* `report.md` 以外に差分が発生する。
* `827e439d...` の commit identityをGitHubで確認できない。
* v1〜v6のverdict、finding、source identityを書き換える必要が生じる。
* runtime、test、spec、projection、review policyの変更が必要になる。
* finding外の不整合を同時修正したくなる。
* `git diff --check`、scope audit、local／GitHub parityのいずれかが失敗する。
* v7 review前にclosureまたはS05開始を要求される。

**未検証事項:** ローカル作業ツリーのclean状態と、今回生成される新しいcommit SHAは、この回答時点では確認していない。上記コマンドとpush後のGitHub exact comparisonで確定する。
