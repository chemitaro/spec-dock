---
種別: artifact
ID: "20260730t110128z"
タイトル: "Final P1 repair ChatGPT Blue Team work packet"
状態: "partially_adopted"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
template: "blank"
authority: "advisory"
derived_from:
  - "ChatGPT Pro session iss00334-final-p1-blue-team"
  - "GitHub branch iss-00334-implement-chatgpt-issue-planning-workflow"
  - "source HEAD a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915"
reflected_to:
  - "bounded FINAL-P1-001 implementation repair"
  - "report.md lifecycle evidence update"
---

# Final P1 repair — ChatGPT Blue Team work packet

## Provenance

- session: `iss00334-final-p1-blue-team`
- model evidence: `requested=Pro` / `resolved=Pro` / `verified=yes`
- repository: `chemitaro/spec-dock`
- branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- reviewed source HEAD: `a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915`
- disposition: `GO_BOUNDED_REPAIR`
- scope: `FINAL-P1-001`〜`FINAL-P1-003`のみ
- non-goals: Issue Planning再設計、新しいrole／routing tier、canonical三文書変更、個人wrapper依存

## Human boundary correction

このwork packet生成後、Humanは`FINAL-P1-002`の境界を訂正した。PATHで解決したローカルOracle本体が自身の通常configを利用することは許容範囲であり、SpecDockが`HOME`／`ORACLE_HOME_DIR`／cwdを一時値へ差し替えてOracle configを隔離・無効化してはならない。

したがって本work packetのうち、Oracle 0.16.1 session ID固定点、focused slug tests、Report reconciliationだけを採用する。Personal configuration isolation、hostile-config test、isolated live assertionsは未採用とする。

採用後の責任境界は`artifacts/20260730t111338z-disc-oracle-local-configuration-boundary-correction.md`が所有する。SpecDockはformal operationに必要なengine、model、model strategy、managed endpoint、cookie-sync禁止、wait、attachment mode、slug、Prompt、Prompt packをdirect argvで明示する。Oracle内部の通常config適用はOracle側の責任とし、SpecDockは個人`chatgpt-use` wrapper、absolute path、API／別profile／default branch fallbackへ依存しない。

## Root cause

### FINAL-P1-001

`_new_session_id()`は`semantic_revision`をそのまま埋め込み、adapterもそのraw値を`--slug`と期待session pathに使う。一方Oracle 0.16.1はcustom slugを`[a-z0-9]+`のwordへ分割してhyphen結合するため、実session IDは`specdock-semantic-revision-...`となる。fake Oracleがraw argv値のdirectoryを作るため欠陥を隠している。

### FINAL-P1-002

現行adapterは親の`HOME`／`ORACLE_HOME_DIR`を保持し、repository rootをcwdとしてOracleを実行する。Oracle 0.16.1はuser configとcwdから上位の`.oracle/config.json`を読み、`promptSuffix`をSpecDockの事前検証後に追加できる。このためformal Promptと個人設定非依存の契約が破れる。

### FINAL-P1-003

`report.md`末尾はlive create、Candidate、fresh Review、Human decision、apply、remote parityを未完了としているが、current HEADには承認済みdecision artifactとadoption commitが存在する。過去のpending記録は履歴として残し、後続sectionでsupersedeする必要がある。

## Minimal implementation

### Canonical Oracle session ID

`_new_session_id()`でclosed role mappingを用いる。

```text
planner           -> planner
semantic_revision -> semantic-revision
reviewer          -> reviewer
```

生成形式を`specdock-<role-word(s)>-<snapshot first 6>-<8 lowercase hex>`とし、Oracle 0.16.1のcustom-slug正規化後もbyte-identicalな固定点にする。一つの`session_id`だけを`--slug`、expected path、status、poll、recovery、harvest、artifact collectionへ渡す。alternate session探索、別正規化候補、replacement sessionは追加しない。

### Personal configuration isolation — not adopted

以下はChatGPT Blue Teamの提案記録であり、Human correctionにより実装しない。

親から継承するallowlistから`HOME`と`ORACLE_HOME_DIR`を外す。invocation専用`TemporaryDirectory`内に次を作る。

```text
runtime_home = <temporary root>/home
oracle_home  = <runtime_home>/.oracle
runtime_cwd  = runtime_home
```

正式run用child envでは`HOME=runtime_home`、`ORACLE_HOME_DIR=oracle_home`を明示する。preflight、formal run、same-session recovery／harvestを同じisolated envと`cwd=runtime_home`で行う。これによりuser config pathは空の一時Oracle homeへ向き、project-config discoveryは一時homeから始まりrepository／ancestorを探索しない。

managed Chromeは既存どおりvalidated endpointを次の明示argvで渡す。

```text
--remote-chrome 127.0.0.1:<validated-port>
--browser-no-cookie-sync
```

`--config`、profile copy、cookie path、personal wrapperは追加しない。`_oracle_home()`の親環境fallbackは削除し、invocationで生成した`oracle_home`だけをsession authorityにする。

### Report reconciliation

canonical `requirement.md`、`design.md`、`plan.md`は変更しない。過去のpending logは改変せず、完了済みlive lifecycleと今回のrepairを後続section／Evidence Adoption Ledgerで追補する。

最低限、次のidentityを記録する。

- live source HEAD: `f488121e80fc93f01cb64fab70a06d306c903804`
- Candidate ID: `iss-00334-v1-20260730t094713z`
- Candidate ZIP SHA-256: `ee0b3be840f1de1cb182db4ee9685acba7cc90d277ceffa2f628edc07a18350a`
- reviewed identity SHA-256: `be336298dd14b882285010097acf37afd52b61fc9789f775d7174f8d14d98b5b`
- review result SHA-256: `2a9c115c8ca6490d4b6e596ff805e72a140599976a5082eae9a59707bf41bc5c`
- decision artifact: `artifacts/20260730t102056z-planning-human-decision-7ad8e5f063bc9e13.json`
- apply/adoption commit: `a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915`
- operation ID: `7ad8e5f063bc9e13f6271e2dfa250dbae50f8a32cbb3d82d382be9274a038368`

`ready/adoption_published`、remote parity、clean status、repair verificationは実測値だけを記録する。merge、Issue close、branch deletion、`issue finish`はHuman-onlyかつ未実施のまま残す。

## Focused tests

1. Oracle 0.16.1と同じtest-only custom slug normalizerをfake session writerに使い、修正前の`semantic_revision`をRedにする。
2. 全roleについて、生成slugがOracle normalizerの固定点、underscoreなし、3〜5 words、各word`[a-z0-9]{1,10}`であることを確認する。
3. direct argv testでexact UTF-8 Prompt bytes、`--prompt`一回、`shell=False`、suffix非混入を確認する。
4. ~~inherited Oracle home、inherited home、repo parent、repo rootにhostile `promptSuffix`を置くfixtureを作り、child `cwd == HOME`、`ORACLE_HOME_DIR == HOME/.oracle`、inherited path非使用、loaded config 0、effective Prompt不変を確認する。~~ Human correctionにより未採用。
5. recovery testsでsubmit／harvestが同じsession ID、HOME、Oracle home、cwdを使い、prompt最大1、harvest最大1、new session 0を確認する。
6. provider／dogfood projectionのbyte identityを確認する。

## Verification

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py
make lint
./spec-dock/scripts/spec-dock validate
git diff --check
uv run pytest -q
```

providerからdogfood projectionを更新し、`cmp`／`git hash-object`でbyte parityを確認する。installer updateがscope外のmanaged filesを変更した場合は取り込まず停止する。

## Required live closure

repair commitをpushしlocal／remote parityを確認した後、repository外output rootでpublic `planning create`を一度だけ実行する。合格条件はOracle 0.16.1、formal Prompt 1、replacement session 0、harvest 0または自然なtimeout時だけ最大1、managed remote Chrome、typed authoring ZIP／Candidate、repository mutation 0である。Oracle-native configは通常どおり利用でき、SpecDockはこれを上書き・隔離しない。

Semantic Revisionをtest目的だけで実行しない。実際にP0／P1 revisionが必要になった場合のみ正式laneのlive coverageとして使う。

最後にexact pushed repair HEADへfresh defect-only closure Reviewを実行し、`FINAL-P1-001`〜`003` closed、新規P0／P1 0を確認する。

## Local checks and risks

- session locatorは一回のadapter invocation内に閉じる現契約を前提とする。return後のmanual recoveryが必要と判明した場合もpersonal homeやrepository scanへ戻さない。
- supported環境でchild `HOME`がNode／Oracleのhomeとして認識されることをreal 0.16.1 smokeで確認する。
- cwd変更に備え、Prompt packと添付pathがabsoluteであることを確認する。
- collision時の`-2` siblingは探索せずfail closedを維持する。
- normalization／config isolation判断はOracle 0.16.1 pinに限定し、version変更時は再検証する。
