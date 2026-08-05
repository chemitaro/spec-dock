# S05 Blue Team minimal repair brief v1

> **対象:** `iss-00354` / S05 Orchestration・CLI cutover
> **修正対象:** `RT-354-S05-001` P1のみ
> **実装判定:** **READY — test-only minimal repair**
> **production変更:** 0
> **変更許可パス:** `tests/unit/application/test_issue_planning_prompt.py` のみ

## 1. 結論

Fresh Red Teamが報告したP1は、production defectではなく、`test_provided_context_paths_are_ordered_opaque_and_identity_preserving()` のfailure spyが狭いために禁止動作を含む実装をGreenにできるtest defectである。Red Teamは、現行productionがprovided pathsをtuple展開するだけであることを確認しており、production修正は要求していない。

GitHub Connectorで、named branch `codex/iss-00354-chatgpt-context-contract` のtipと指定HEAD `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec` を比較した結果は次のとおりである。

| 項目                      | 確認結果                                       |
| ----------------------- | ------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                      |
| Named branch            | `codex/iss-00354-chatgpt-context-contract` |
| Current source HEAD     | `4bb3b4072f4624ca862a0c8fcc58e5b0be581eec` |
| Comparison status       | `identical`                                |
| Ahead / behind          | `0 / 0`                                    |
| Default branch fallback | **0 / 未使用**                                |
| Connector確認日            | `2026-08-05`                               |

当該HEADのproduction prompt synthesizerは、provider resource validationを実行した後、plannerでは`static + required + provided`、evidence promptでは`static + attachment_paths + provided`をそのままtuple化している。provided pathを検査、copy、archive、hashする処理は確認されない。

したがって、P1解消にproduction変更またはallowlist拡張は不要であり、**BLOCKEDではない**。

## 2. 根拠入力

本repair briefは次を入力とする。

* canonical planのS05実行カードと`TC-S05-004`責務。
* S05 implementation brief v3のno-inspection/no-materialization、order、duplicate、lexical form、object identity契約。
* Fresh Red Teamの唯一の採用finding `RT-354-S05-001`。
* current target test source。

GitHub上のexact HEADでも、current spyは一部の`Path` methodだけをpatchし、判定を`self is candidate`に限定している。このため、同じpath textから再構築した別objectとdescendantを検出できない。

## 3. 変更境界

### 3.1 唯一の変更許可パス

```text
tests/unit/application/test_issue_planning_prompt.py
```

許可される変更は次だけである。

* 必要なPython標準ライブラリimportの追加。
* `test_provided_context_paths_are_ordered_opaque_and_identity_preserving()` のspy、fixture、assertionの強化。
* 同test内で使用するprivate helperを、同一test function内または同一test module内へ追加すること。

最小差分を優先し、既存test function名を維持する。

### 3.2 Read-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
```

### 3.3 変更禁止

```text
tests/integration/**
tests/unit/application/test_issue_planning.py
tests/unit/commands/**
tests/unit/infra/**
tests/cli_runtime/**
requirement.md
design.md
plan.md
report.md
.assurance.json
artifacts/**
reviews/**
provider / installed / dogfood projection
```

production code、CLI契約、domain、infra、canonical docs、review artifactを変更してはならない。

## 4. 修復対象test

修正対象は既存の次のfunctionだけとする。

```python
test_provided_context_paths_are_ordered_opaque_and_identity_preserving
```

現在の次の性質は削除せず、より強いfailure spyへ置き換える。

* relative provided path。
* absolute provided path。
* optional pathの重複。
* plannerとReviewer evidence promptの両方。
* attachment order。
* `Path` object identity。
* lexical string preservation。
* prompt bodyへのpath非描画。

現在の`inspected`へ記録して最後に空を確認するだけの方式は廃止し、禁止APIの呼出し時点で`AssertionError`を送出するfailure spyへ置換する。

## 5. Protected pathのlexical判定

### 5.1 Protected roots

少なくとも次の二つをprotected optional operandsとする。

```python
provided_relative = Path("operator/context/../opaque")
provided_absolute = Path("/outside/context")
protected = (provided_relative, provided_absolute)
```

### 5.2 Path-like変換

spyへ渡された値が`str`または`os.PathLike`である場合だけ、filesystem accessなしで`Path`へ変換する。

概念形:

```python
def path_like(value: object) -> Path | None:
    if isinstance(value, (str, os.PathLike)):
        return Path(os.fsdecode(os.fspath(value)))
    return None
```

次を使用してはならない。

```text
resolve()
absolute()
exists()
stat()
lstat()
samefile()
repo_root prefixing
filesystem canonicalization
```

### 5.3 Object-independent lexical match

protected判定はobject identityを使用せず、次の意味に固定する。

```python
candidate == root or candidate.is_relative_to(root)
```

これにより、少なくとも次を同一保護境界として扱う。

```python
Path(str(provided_relative))             # 同値だが別object
Path(str(provided_absolute))             # 同値だが別object
provided_relative / "child"              # lexical descendant
provided_absolute / ".hidden" / "child"  # lexical descendant
```

`Path.is_relative_to()`はlexical比較だけに用い、filesystemへ問い合わせない。

## 6. Failure spy対象

必要な標準ライブラリimportは同test moduleに追加する。

```python
import builtins
import hashlib
import shutil
import zipfile
```

`os`と`Path`は既存importを使用する。

### 6.1 `Path` API

次のmethodをpatchする。

```text
exists
is_file
is_dir
is_symlink
stat
lstat
resolve
absolute
open
read_text
read_bytes
iterdir
glob
rglob
rename
replace
```

各wrapperは次を行う。

1. `self`がprotected rootまたはlexical descendantなら、API名とpathを記録して即座に`AssertionError`。
2. `rename`と`replace`は`self`だけでなくtarget argumentも同じ判定に通す。
3. protectedでなければoriginal methodへ委譲する。

provider resource root、operation root、`prompt.md`、provider attachments directoryに対してはoriginal methodを実行させる。managed provider resource validationをskipまたはmock-awayしてはならない。

### 6.2 Built-in content API

次をpatchする。

```text
builtins.open
```

第一argumentがprotected rootまたはdescendantなら`AssertionError`、それ以外はoriginalへ委譲する。file descriptorなどpath-likeでない第一argumentは保護対象外としてoriginalへ渡す。

### 6.3 `os` filesystem/tree API

次をpatchする。

```text
os.stat
os.lstat
os.open
os.listdir
os.scandir
os.walk
os.rename
os.replace
```

guard対象は次とする。

| API                                                   | Guard対象               |
| ----------------------------------------------------- | --------------------- |
| `stat`, `lstat`, `open`, `listdir`, `scandir`, `walk` | 第一path argument       |
| `rename`, `replace`                                   | sourceとdestinationの両方 |

protectedでなければoriginalへ委譲する。

`os.walk`はgeneratorを反復する前ではなく、wrapper呼出し時点でprotected topを拒否する。

### 6.4 `shutil` copy API

次をpatchする。

```text
shutil.copy
shutil.copy2
shutil.copyfile
shutil.copytree
```

sourceとdestinationの双方をguardする。いずれかがprotected rootまたはdescendantなら、copy callとして記録し`AssertionError`を送出する。それ以外はoriginalへ委譲する。

### 6.5 Archive / ZIP API

次をzero-call failure spyとする。

```text
zipfile.ZipFile
shutil.make_archive
```

prompt synthesis境界ではarchiveまたはZIP materialization自体が禁止されているため、これらはpath-filterせず呼出し時点で`AssertionError`としてよい。

provider resource validationにこれらのAPIを許可するallowlistを追加してはならない。exact current productionはprovider validationにarchive APIを必要としていない。

### 6.6 Hash API

prompt synthesis中のhash生成はzero-callとする。

最低限、次をfailure spy対象とする。

```text
hashlib.sha256
hashlib.new
hashlib.file_digest  # 実行環境に存在する場合
```

加えて、`hashlib.algorithms_guaranteed`に列挙され、`hashlib`上に存在するconstructorは同一failure spyへ差し替える。

hash callではbytesへ変換された後に元pathのprovenanceを判別できないため、hash familyだけはprompt synthesis window全体でzero-callとする。

### 6.7 Module-local alias対策

production moduleが標準APIをdirect importしてもspyをすり抜けないよう、`issue_planning_prompt` module上に次と同名のattributeが**既に存在する場合だけ**同じspyを適用する。

```text
ZipFile
make_archive
copy
copy2
copyfile
copytree
sha256
new
file_digest
```

`raising=False`で新しいmodule attributeを無条件に追加してはならない。`hasattr()`で既存bindingを確認した場合だけpatchする。

## 7. Failure spyのactive canary

spyをinstallしただけでGreenにしてはならない。各spyが実際に禁止動作を検出することを同test内のactive canaryで証明する。

### 7.1 Canary契約

各canaryは次の形で実行する。

```python
with pytest.raises(AssertionError, match="forbidden provided-context access"):
    probe()
```

`FileNotFoundError`、`OSError`、戻り値`False`、空iterator、正常終了は合格としてはならない。failure spy自身が送出した`AssertionError`だけをacceptする。

### 7.2 必須canary

少なくとも次を含める。

| Family             | Canary                                                                            |
| ------------------ | --------------------------------------------------------------------------------- |
| 別`Path` object     | `Path(str(provided_relative)).stat()`                                             |
| lexical descendant | `(Path(str(provided_absolute)) / ".hidden" / "child").read_bytes()`               |
| tree               | `os.listdir(descendant)`、`os.scandir(descendant)`、`os.walk(descendant)`           |
| direct filesystem  | `os.stat(rebuilt)`、`os.lstat(rebuilt)`、`os.open(rebuilt, os.O_RDONLY)`            |
| content            | `builtins.open(str(descendant), "rb")`                                            |
| copy               | `shutil.copy`、`copy2`、`copyfile`、`copytree`へprotected sourceを渡す                   |
| move semantics     | `Path.rename`、`Path.replace`、`os.rename`、`os.replace`                             |
| ZIP                | `zipfile.ZipFile(tmp_path / "probe.zip", "w")`                                    |
| archive            | `shutil.make_archive(str(tmp_path / "probe"), "zip", root_dir=provided_relative)` |
| hash               | `hashlib.sha256(b"probe")`、`hashlib.new("sha256", b"probe")`                      |

`Path` methodの登録漏れを防ぐため、登録対象methodごとにcompactなcallable tableを作り、各entryが`AssertionError`となることを検査する。

### 7.3 Canaryとproduction invocationの分離

failure spyはAPI名を`forbidden_calls`へ記録する。

実行順は次に固定する。

1. spy install。
2. canary table実行。
3. 全expected canary labelが検出されたことを確認。
4. `forbidden_calls.clear()`。
5. planner synthesis。
6. Reviewer evidence synthesis。
7. `forbidden_calls == []`を確認。

これにより、spyが有効であることと、実際のproduction synthesisが禁止APIを呼んでいないことを別々に証明する。

## 8. Prompt contract assertions

### 8.1 Fixture

contextは一度だけ生成して再利用する。

```python
context = _context()
```

Reviewer用required pathは次のようにする。

```python
candidate = Path("candidate.zip")
required_same_lexical = Path(str(provided_relative))
```

`required_same_lexical`は`provided_relative`とlexically equalだが、別objectであることを確認する。

```python
assert required_same_lexical == provided_relative
assert required_same_lexical is not provided_relative
```

Reviewerのrequired tupleへ両方を渡す必要はなく、次で十分である。

```python
attachment_paths=(candidate, required_same_lexical)
```

optional tupleは既存どおりとする。

```python
provided_context_paths=(
    provided_relative,
    provided_absolute,
    provided_relative,
)
```

これにより、required pathとoptional pathが同値でもdeduplicateされないことを検証できる。

### 8.2 Planner exact order

次の完全tupleをassertする。

```text
provider planning attachments directory
→ canonical issue paths
→ relevant source paths
→ provided_relative
→ provided_absolute
→ provided_relative
```

tailだけでなく、static、required、optionalを含む完全tupleを比較する。

### 8.3 Reviewer exact order

次の完全tupleをassertする。

```text
provider review attachments directory
→ candidate
→ required_same_lexical
→ provided_relative
→ provided_absolute
→ provided_relative
```

これにより次を同時に固定する。

* static → required → optional。
* required/optional間のlexical duplicate retention。
* optional内部のduplicate retention。
* sortなし。
* deduplicationなし。

### 8.4 Object identity

plannerとReviewerのoptional positionsについて、すべて`is`で確認する。

```python
assert planner.attachment_paths[-3] is provided_relative
assert planner.attachment_paths[-2] is provided_absolute
assert planner.attachment_paths[-1] is provided_relative

assert reviewer.attachment_paths[-3] is provided_relative
assert reviewer.attachment_paths[-2] is provided_absolute
assert reviewer.attachment_paths[-1] is provided_relative
```

Reviewer required positionについても次を確認する。

```python
assert reviewer.attachment_paths[2] is required_same_lexical
```

### 8.5 Lexical form

既存assertionを維持する。

```python
assert str(provided_relative) == "operator/context/../opaque"
assert str(provided_absolute) == "/outside/context"
```

relative pathをabsolute化した期待値、`repo_root / path`、normalized pathへ変更してはならない。

### 8.6 Prompt privacy

plannerとReviewerの両promptについて、少なくとも次が含まれないことを確認する。

```text
operator/context
/outside/context
candidate path inventory
provided path count
provided path hash
```

### 8.7 Provider-owned access

failure spiesをinstallした状態で両synthesizerが成功すること自体を、provider resource accessが維持された証拠とする。

次をmock、skip、allowlist化してはならない。

```text
provider resource root validation
operation directory validation
prompt.md validation/read
attachments directory validation
canonical managed-source validation
```

protected判定はprovided rootsとそのlexical descendantsだけに限定する。

## 9. Expected Red / Green

| Phase                                                                     | Expected result                                   |
| ------------------------------------------------------------------------- | ------------------------------------------------- |
| Current identity-only spy + `Path(str(provided_relative)).stat()` canary  | **FAIL**。spy由来の`AssertionError`にならず、別objectがすり抜ける |
| Current spy + `os.walk` / `shutil.copytree` / `ZipFile` / `sha256` canary | **FAIL**。未patchのためexpected `AssertionError`にならない  |
| Lexical matcherのみ、API family未追加                                           | 対応するos/shutil/archive/hash canaryが**FAIL**        |
| 全failure spy + canary + current unchanged production                      | target testが**PASS**                              |
| Synthesizerがprotected pathまたはdescendantへ禁止APIを一回でも実行                      | failure spyで即時**FAIL**                            |
| Provider resource validationのみ                                            | original APIへ委譲され**PASS**                         |

このRed/Greenは期待契約であり、本brief自体はtest実行結果を主張しない。

## 10. 実装順序

1. local repository、branch、HEADを再確認する。
2. `tests/unit/application/test_issue_planning_prompt.py`以外に差分がないことを確認する。
3. 必要な標準ライブラリimportを追加する。
4. existing test function内へobject-independent lexical matcherを追加する。
5. 現在のrecord-only `Path` spyをfailure spyへ置換する。
6. `Path`、built-in、`os`、`shutil`、archive、ZIP、hash spiesを追加する。
7. active canary tableを追加し、current identity-only/partial spyではRedになることを確認する。
8. canary記録をclearした後にplannerとReviewer synthesisを実行する。
9. exact full order、duplicate、lexical form、object identity、prompt privacyをassertする。
10. production invocation後の`forbidden_calls == []`をassertする。
11. target test、test module全体、Ruff、diff checkを実行する。
12. changed-file allowlistを確認する。

testをGreenにするためにproductionへguard、allowlist、feature flag、fallbackを追加してはならない。

## 11. 最小検証コマンド

### 11.1 Exact identity

```bash
git fetch origin codex/iss-00354-chatgpt-context-contract

test "$(git branch --show-current)" = \
  "codex/iss-00354-chatgpt-context-contract"

test "$(git rev-parse HEAD)" = \
  "4bb3b4072f4624ca862a0c8fcc58e5b0be581eec"

test "$(git rev-parse refs/remotes/origin/codex/iss-00354-chatgpt-context-contract)" = \
  "4bb3b4072f4624ca862a0c8fcc58e5b0be581eec"
```

### 11.2 Target test

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py::test_provided_context_paths_are_ordered_opaque_and_identity_preserving \
  -q
```

### 11.3 Prompt test module

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  -q
```

### 11.4 Ruff

```bash
uv run ruff check \
  tests/unit/application/test_issue_planning_prompt.py
```

### 11.5 Diff integrity

```bash
git diff --check
```

```bash
git diff --name-only \
  4bb3b4072f4624ca862a0c8fcc58e5b0be581eec...HEAD
```

期待されるchanged-file setは完全に次の一件だけである。

```text
tests/unit/application/test_issue_planning_prompt.py
```

production unchanged確認:

```bash
git diff --quiet \
  4bb3b4072f4624ca862a0c8fcc58e5b0be581eec...HEAD \
  -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
```

expected exit code:

```text
0
```

## 12. 合格条件

次のすべてが同一resulting worktree/HEADで成立した場合だけ、`RT-354-S05-001`のrepair candidateとする。

* protected rootと同値な別`Path` objectがfailure spyに捕捉される。
* protected rootのlexical descendantがfailure spyに捕捉される。
* `Path` inspection/content/tree/move methodsが捕捉される。
* `builtins.open`が捕捉される。
* `os.listdir`、`os.scandir`、`os.walk`が捕捉される。
* direct `os.stat`、`os.lstat`、`os.open`、`os.rename`、`os.replace`が捕捉される。
* `shutil.copy`、`copy2`、`copyfile`、`copytree`が捕捉される。
* `zipfile.ZipFile`と`shutil.make_archive`が捕捉される。
* hash constructorが捕捉される。
* 各API familyのactive canaryがspy由来の`AssertionError`を確認する。
* canary記録clear後、plannerとReviewer synthesisの禁止call数が0。
* provider-owned resource validationが従来どおり成功する。
* static → required → optionalの完全orderが維持される。
* required/optional間とoptional内部のduplicateが維持される。
* relative/absolute lexical formが維持される。
* optional `Path` object identityが維持される。
* provided pathがprompt bodyへ描画されない。
* test expectationを弱めていない。
* changed fileが許可された一件だけ。
* production diffが0。

## 13. 停止条件

次のいずれかに該当した場合は自己拡張せず、結果を**BLOCKED**とする。

* named branch tipが`4bb3b4072f4624ca862a0c8fcc58e5b0be581eec`から移動している。
* default branch参照が必要になる。
* `tests/unit/application/test_issue_planning_prompt.py`以外の変更が必要になる。
* production codeへguardまたはtest hookを追加しなければspyを実装できない。
* provider resource accessを許可するためにproduction allowlist拡張が必要になる。
* canonical managed-source validationをskip、mock-away、または弱化する必要がある。
* order、duplicate、lexical form、object identity、prompt privacyの既存assertionを弱める必要がある。
* archive/hash callを「許容されたcall」として除外しなければGreenにできない。
* active canaryが別objectまたはdescendantを検出できない。
* production runtime、infra、domain、CLI parser、canonical docs、report、review artifactの変更が必要になる。
* fallback、retry、ZIP/hash/materialization機能の追加が必要になる。

## 14. Handoff boundary

workerが返す証跡は次に限定する。

```text
repository
branch
source HEAD
resulting HEADまたはuncommitted diff identity
changed files
target test result
test module result
Ruff result
git diff --check result
production diff zero result
remaining unverified items
```

次は実施または主張しない。

```text
production修正
canonical docs更新
report更新
Red Team review書換え
review artifact更新
修正版ZIP
commit
push
PR
merge
Issue close
S05 closure確定
assurance promotion
```

`GPT-5.6 Luna`、`Reasoning Effort Max`、その組合せについて実測証跡は取得していないため、すべて**unverified**として扱う。要求設定またはmodel自己申告をverified evidenceとして記録してはならない。
