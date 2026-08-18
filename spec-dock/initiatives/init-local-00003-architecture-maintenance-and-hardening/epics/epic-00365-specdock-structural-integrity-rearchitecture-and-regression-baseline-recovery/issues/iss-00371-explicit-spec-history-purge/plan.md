---
種別: 実装計画書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

explicitly authorized spec history deletion、public CLI/JSON、partial deletion recoveryを扱うため`strict`とする。意図されたbounded deletionであり、authority外data lossがない設計を前提とする。

Risk factors:

- irreversible spec history deletion
- authority constructionとretry escalation
- bounded subtree path guard
- partial deletion state
- legacy marker ambiguity

`critical`再評価条件:

- allowed root外またはrepository外を削除し得る
- unknown/user-owned contentがexplicit authority境界外で不可逆に失われ得る
- recoveryにincident response、forensic investigation、credential/security対応が必要
- dry-runとapply planの同一性を証明できないままdestructive mutationを許可する必要がある

## 目標

existing `--apply --remove-specs`をexplicit purge intent/authorityとしてcommon engineへhard cutoverし、dry-run、path guard、authority non-escalation、partial forward recovery、public JSON parityを証明する。update/deprovision/retryからsilent purgeへ到達するrouteを残さない。

## 順序・依存

dependency: `iss-00370`

1. current purge behavior/allowed roots characterization
2. explicit authority model
3. purge assessment/plan/postcondition
4. journaled apply/resume
5. CLI/JSON cutover
6. legacy route removal/docs
7. destructive completion sweep

Migration:

- D3完了時のdeprovision service/kernel/journalへpurge intentを追加し、`--remove-specs` dry-run/applyを一回のhard cutoverで移す。deprovisionとpurgeのdual writerは残さない。
- D3以前の`.uninstall-retry.json`はoriginal specs modeを証明できないためpurge authorityへ変換しない。explicit current invocationとexact reconstructable planがないcaseはmarkerを保持してwrite前にblockする。
- new purge journal作成後はsame explicit authorityとcompatible protocolでforward recoveryし、keep-specs、update、init、legacy markerだけからauthorityを昇格しない。

## 実装step

### Step 1 — Current purge contractを固定する

- exact current `--remove-specs` plan/action/path roots、summary/reason、JSON fields、postconditionをtests/sourceから抽出する。
- initiatives/spec history fixture、authority外unknown sibling、outside sentinel、symlink/hardlink/root-rebind fixtureを作る。
- current `.uninstall-retry.json`がoriginal specs modeを持たないことをexplicit testにする。

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'uninstall and remove_specs'
```

### Step 2 — Explicit authorityを実装する

- CLI parse resultの`--apply` + `--remove-specs`だけからpurge authorityを作る。
- dry-run intentとapply authorityを分ける。
- plan/journal digestにintent、authority source、allowed rootsを含める。
- update/init/deprovision/legacy markerからauthorityを作るAPIを持たない。

Negative tests:

- apply without mode
- keep-specs
- dry-run
- deprovision journal resume
- purge journalをkeep-specsでresume
- legacy marker only

### Step 3 — Purge Assessment/Plan/Postconditionを追加する

- exact allowed spec history rootsをContractに追加する。
- root/subtree observationsとauthority外preserve dispositionsを作る。
- blocker有りoperation全体をpre-write stopする。
- bounded removal actionsとexpected absent postconditionを構築する。
- dry-run planとapply plan digestをsame observationに束縛する。

Negative tests:

- root path escape/prefix confusion
- root/child symlink
- hardlink/unsafe type
- parent/root rebind
- authority外unknown sibling
- plan drift between dry-run/apply

### Step 4 — Journaled purge executionとforward recovery

- common bounded removal kernelでpurge actionsを実行する。
- child/action checkpoint、exact pre-action SHA/identity、expected absentをjournalに記録する。
- partial failure後same-plan explicit purge invocationだけresumeする。
- ambiguous pre/post state、authority mismatch、plan mismatchはjournalを保持してblockする。
- success後にpostconditionとpreserved surfacesをverifyしてfinalizeする。

### Step 5 — CLI/Text/JSON cutover

- `--remove-specs` dry-run/applyをnew serviceへdispatchする。
- current schema version 1、one-object stdout、actions/summary/guidance/error/exit semanticsをmapperで維持する。
- destructive scopeとretry commandにexplicit remove-specsを表示する。
- new interactive prompt/flagは追加しない。

### Step 6 — Legacy purge routeを削除する

- old remove-specs branch、legacy writer、CLI recursive removalへのcall edgeを除去する。
- update/deprovisionからpurge action/authorityへ到達できないことをAST/dependency testで固定する。
- legacy markerはread-only detection/manual guidanceだけにする。

### Step 7 — Docsとdestructive completion sweep

- READMEにdry-run、two-part explicit authority、no implicit purge、partial recoveryを記載する。
- Requirement/Design/ADRとimplementationを照合する。
- destructive path listとoutside-preservation evidenceをreviewする。

## 検証

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py -k 'uninstall or remove_specs or keep_specs or update'
make lint
```

Required evidence:

- dry-run before/after byte equality
- explicit apply success and allowed-root absence
- all non-authority invocation history deletion 0
- outside/unknown sentinel unchanged
- symlink/hardlink/rebind external mutation 0
- cross-authority resume rejection
- partial purge journal/resume behavior
- JSON golden parity
- old purge route absence

## rollback

- new purge journal作成前はcode revert可能。
- journal作成後はsame/compatible packageとsame explicit authorityでforward recoveryする。
- deleted historyのwhole-operation auto-restoreは行わない。
- ambiguous partial state、authority mismatch、legacy markerはfail closed/manual guidance。
- candidate rollback/release withdrawal時も、進行中journal consumer向けcompatible recovery pathを先に確保する。

## exit / handoff

- I371-R01〜R10とacceptance 1〜10がevidenceに結び付く。
- purgeがseparate intent/authorityとしてcommon engineを使用。
- update/deprovision/retryからauthority escalation不可。
- current public CLI/JSON semantics維持。
- legacy purge branch/writer削除。
- D5へ、all public intents hard-cutover済みのcall graphとparity verification対象を渡す。
- residual riskはfinal legacy seam scan、package surface parity、Linux/macOS evidence、Full Regression attributionとしてD5へ渡す。
