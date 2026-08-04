# Blue Team 修正実装ブリーフ — iss-00354 S03/S04

**結論:** 修正対象は、direct transport unit test と canonical `report.md` の **2ファイルだけ**とするD776743e8376c28a7c7184` と一致しており、このコミットは既にcommit・push済みのv3 test-repair commitである。production runtimeは変更しない。

## 目的

Fresh Red Team v4の正式判定 `P0=0 / P1=2 / FAIL` に含まれる次の2件だけを解消する。

1. `RT-354-S03S04-V4-001`
   direct transport testで、repository外absolute Candidateを実際の同一infra invocationへ渡したことを証明する。

2. `RT-354-S03S04-V4-002`
   canonical reportの現在状態、commit identity、検証証跡を現実のGitHub履歴と一致させる。

現行testは `repo_root=tmp_path` に対して `tmp_path/candidate.zip` を使っているため、Candidateはrepository外ではない。現行reportもv3修正を「未コミット」「working tree」「staged for a new commit/push」と記録しており、現在のGitHub HEADと不整合である。

## 対象ファイル

| ファイル                                                                                                                                                                                                       | 許可する変更                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `tests/unit/infra/test_issue_planning_chatgpt.py`                                                                                                                                                          | 既存direct transport testのfixture配置・assertion修正のみ   |
| `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract/report.md` | v4レビュー、commit identity、再検証結果、次回review sourceの記録のみ |

## 具体的な変更

### 1. Direct transport test

`test_direct_file_operands_preserve_order_and_do_not_materialize_pack` を次の配置に変更する。

```python
repo_root = tmp_path / "repo"
repo_root.mkdir()

static_directory = repo_root / "attachments"
static_directory.mkdir()

relative_source = Path("source.md")
(repo_root / relative_source).write_text("source\n", encoding="utf-8")

external_candidate = tmp_path / "candidate.zip"
external_candidate.write_bytes(b"candidate")

paths = (
    static_directory,     # repo内 absolute directory
    external_candidate,  # repo外 absolute Candidate
    relative_source,     # repo-relative lexical operand
)
```

テストfixtureの作成はread/open/tree/copy/ZIP/hash spyの導入前に行う。

その後、次を維持または明示する。

* `external_candidate` はabsoluteで、`repo_root` 配下ではない。
* `relative_source` と `repo_root / relative_source` の両表現をprotected input setへ入れる。
* `external_candidate` もprotected input setへ明示的に入れる。
* `Path.read_*`、`Path.open`、built-in `open`、`stat`、`resolve`、`iterdir`、`glob`、`rglob`、`scandir`、`listdir`、`shutil.copy*`、`move`、`ZipFile`、input-side `sha256` の既存spyを削除・緩和しない。
* `SynthesizedPlanningPrompt.attachment_paths=paths` を、次の実際の呼出しへ渡す。

```python
result = issue_planning_chatgpt.invoke_issue_planning_chatgpt(
    repo_root=repo_root,
    ...
)
```

submit argvから抽出した`--file` operandを、文字列として次と完全一致させる。

```python
[
    str(static_directory),
    str(external_candidate),
    str(relative_source),
]
```

特に、relative operandがabsolute化されていないことを明示assertする。

```python
assert file_operands[-1] == "source.md"
assert not Path(file_operands[-1]).is_absolute()
assert submit_cwds == [repo_root]
```

input archive/copy/hashの各call countは引き続き`0`とする。prompt-pack不存在確認は、`tmp_path`直下だけでなく`repo_root`直下も対象にする。

### 2. Canonical report

既存の履歴を削除・書換えず、同じ事実を記載している箇所だけを整合させる。

* `150d81a3e1a98e1f3e9776743e8376c28a7c7184` を、**commit・push済みのv3 test-repair commit**として固定する。
* `未コミット`、`working tree`、`staged for a new commit/push`、`v4 pending`という現在状態の記述を除去する。
* Fresh Red Team v4について、次を記録する。

  * reviewed source: `150d81a3e1a98e1f3e9776743e8376c28a7c7184`
  * verdict: `FAIL`
  * `P0=0 / P1=2`
  * `RT-354-S03S04-V4-001`
  * `RT-354-S03S04-V4-002`
  * production runtimeにfindingがないこと
  * current disposition: `repair_required`
* TDD証跡、Discovered Tests、Delegated Worker Evidence、Milestone/Commit Candidate Gate、Final Code Review Gate、Final Commit ledgerのS03/S04行を同じ状態へ揃える。
* 修正後に実際に再実行した各コマンドについて、command、結果件数、exit code、実行対象identityを記録する。過去の件数をcurrent resultとして転記しない。
* 修正後のGitHub branch tipは、**次のFresh Red Team review source**として扱うだけとし、PASS、atomic closure、S05開始を意味させない。
* report自身を含むcommitのSHAを事前予測しない。push後のGitHub preflightで確定したexact tipを次回review inputへ束縛する。

## 検証コマンドと合格条件

既存reportが要求している全体pytest、full-regression、validate、provider update/parity、legacy search、scope auditを、今回の修正後に再実行する。

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py::test_direct_file_operands_preserve_order_and_do_not_materialize_pack \
  -q

uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q

uv run pytest -q

uv run pytest --run-full-regression \
  tests/integration/test_issue_planning_e2e.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  -q

uv run ruff check

./spec-dock/scripts/spec-dock validate

uv run python -m spec_dock.cli update .
```

合格条件はすべてexit `0`。`update`後に今回の2ファイル以外の差分が発生した場合は、修正対象へ追加せずscope violationとして停止する。

Provider/projection parityは全組でexit `0`とする。

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py

cmp -s \
  .agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md
```

Review resourceの両projectionは現行HEADで同一blobとして確認できている。

Legacy production search:

```bash
rg -n \
  "_write_transport_pack|reviewed-identity\.(json|sha256)|exact_attachments|SynthesizedPlanningPrompt\.attachments" \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  .agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

合格条件はzero-matchかつexit `1`。exit `2`以上は失敗とする。

Scope audit:

```bash
git diff --check

git diff --name-only \
  150d81a3e1a98e1f3e9776743e8376c28a7c7184

git status --short --branch
```

`git diff --name-only`の出力は、指定したtestとcanonical reportの2ファイルだけでなければならない。commit・push後は次もexit `0`とする。

```bash
test "$(git rev-parse HEAD)" = "$(git rev-parse @{upstream})"
```

## identity／履歴の扱い

* source repository: `chemitaro/spec-dock`
* source branch: `codex/iss-00354-chatgpt-context-contract`
* v4 reviewed sourceおよび修正開始点: `150d81a3e1a98e1f3e9776743e8376c28a7c7184`
* `150d81a3...` は履歴から動かさず、v3 test-repair commitとして記録する。
* 今回の修正後tipは別identityとして扱い、push後のGitHub exact-tip確認を経て次のFresh Red Teamへ渡す。
* v4の`P1=2 / FAIL`は修正入力として保持し、Blue Team側で`resolved`または`PASS`へ変更しない。
* v1〜v4の各review source HEADを混同・上書きしない。
* review artifactの正確なpath、SHA-256、v4実行モデル証跡を確認できない場合は、推測せず`未確認`と記録する。

## 禁止事項

* production runtime、application、provider projection、Review resource、integration testの変更。
* requirement、design、plan、ADR、assurance、既存仕様の変更。
* アーキテクチャ再設計、改善提案、P2/P3対応、仕様拡張。
* v4 finding以外を理由とするテスト強化。
* provider updateが生成した想定外差分のcommit。
* atomic closure、S05開始、assurance昇格、PR作成・更新、merge、Issue closeの先取り。
* 未実行コマンドのPASS記録、過去結果のcurrent result化、未確認SHA・model・artifact hashの補完。

添付の設計判断文書はアーキテクチャ境界の再設計案を扱うため、今回のP1修正根拠には採用しない。

## 完了条件

* diffが対象2ファイルだけである。
* 同一infra invocationに、repo内absolute directory、repo外absolute Candidate、repo-relative lexical sourceが渡される。
* Candidateを含む全protected inputに対するread/open/tree/copy/ZIP/hash callが`0`である。
* relative argvとsubmit `cwd=repo_root`が明示assertされる。
* reportから未コミット・working-tree・staged表現がなくなり、`150d81a3...` とv4 FAILが正しく記録される。
* 指定した全検証の実測結果とexit codeがreportに記録される。
* 修正後のexact GitHub tipが、closure済みHEADではなく**次回Fresh Red Team review source**として用意される。

## この相談での確認情報

* **Repository:** `chemitaro/spec-dock` — GitHub connectorで確認済み。
* **Branch:** `codex/iss-00354-chatgpt-context-contract` — GitHub connectorで存在確認済み。default branch fallbackは未使用。
* **HEAD:** `150d81a3e1a98e1f3e9776743e8376c28a7c7184` — 指定SHAとbranch tipの比較結果は`identical`、ahead/behindともに`0`。
* **この相談のモデル:** GPT-5.6 Pro。
* **reportにあるv3モデル履歴:** requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved `Pro`、verified `no`。これはv3履歴であり、v4モデル証跡として流用しない。
* **Fresh Red Team v4のmodel、review artifact path、artifact SHA-256:** 未確認。
* **修正後のテスト結果・exit code・新しいGitHub tip:** 未実行・未確認。Blue Teamが修正後に実測して記録する対象。
* **公開Web情報:** 本ブリーフの判断根拠には使用していない。
