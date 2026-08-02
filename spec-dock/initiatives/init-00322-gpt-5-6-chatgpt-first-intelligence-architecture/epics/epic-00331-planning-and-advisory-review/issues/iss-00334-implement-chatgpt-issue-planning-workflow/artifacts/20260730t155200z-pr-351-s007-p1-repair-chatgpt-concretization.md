# 結論

GitHub connector で `chemitaro/spec-dock` の PR #351 を直接確認し、対象 branch が `iss-00334-implement-chatgpt-issue-planning-workflow`、HEAD が **`91715eecf306bd0c978da922f87193151764cdcd`** であることを確認した。default branch への代替は行っていない。

Review `4820348714` の対象 P1 三件は、いずれも現行 exact HEAD に存在する独立した merge blocker である。添付の前回相談は制約理解だけに使用し、欠陥判定と修正方針は今回の exact-head source を基準にした。 

| P1                                | 閉鎖可能性                                      | 必須修正                                                                              |
| --------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------- |
| `apply-output-directory-toctou`   | Darwin/Linux共通の directory FD＋`*at` 操作で閉鎖可能 | validated guard を apply transaction まで運び、証跡 lifecycle 全体を descriptor-relative にする |
| `apply-remote-ref-cas`            | Git の explicit expected-old CAS で閉鎖可能      | 初回／resume の両 push を `operation.expected_head` に bind する                           |
| `candidate-stage-identity-toctou` | 現行の pathname rename では閉鎖不能                 | Linux と Darwin で別々の FD 起点 publication primitive を使い、利用不能時は既存 reason で fail closed |

---

# 1. `apply-output-directory-toctou`

## 現行コードの正確な欠陥点

application は `validate_candidate_output_directory()` を呼ぶが、戻された guard を保存していない。以後は再び生の `request.output_dir` を resume probe と transaction runner に渡している。

transaction 側の `record_planning_apply_operation()` は次の順序になっている。

1. `output_dir.resolve(strict=True)` を実行する。
2. resolve 後の target に対して `output.is_symlink()` を評価する。
3. `operation_dir.mkdir()`、`tempfile.mkstemp()`、`Path.read_bytes()` などを pathname ベースで行う。

そのため、application validation 後に output path 自体を rename し、同じ pathname を repository 内への symlink に置き換えると、`resolve()` が replacement symlink を辿る。resolve 後の `Path` は symlink ではないため `is_symlink()` も防御にならず、`planning-apply-*` が repository 内に作成される。

resume probe も同じく path を再 resolve し、同じ pathname authority を使っている。

さらに transaction 開始後も、commit record、state、attempts、transaction backup、publication record が `Path` によって参照されるため、最初の operation directory 作成だけを直しても不十分である。transaction entry で pathname authority を捨て、証跡 lifecycle の終了まで open directory descriptor を authority にしなければならない。

## 最小修正戦略

### 1. application で既存 guard を保持する

公開 request や JSON schema は変えず、application 内部だけを次の形にする。

```python
output_guard = gateway.validate_candidate_output_directory(
    request.output_dir,
    repo_root,
)

resume_probe(
    operation,
    output_guard=output_guard,
)

transaction_runner(
    operation,
    repo_root=repo_root,
    output_guard=output_guard,
    ...,
)
```

`IssuePlanningCandidateOutputGuard` は既に opaque token として存在するため、新しい公開 contract は不要である。apply 用 protocol と injection signature だけを同じ token に揃える。

### 2. transaction entry で guard identity を再確認する

transaction の最初、かつ証跡を一 byte も作る前に次を行う。

```text
open_safe_directory_descriptor(guard.path)
→ fstat(fd)
→ (st_dev, st_ino) == (guard.device, guard.inode) を確認
```

validation 後、transaction FD capture 前に pathname が置換されていた場合は、既存の次の結果で停止する。

```json
{"status": "rejected", "reason": "apply_output_rejected"}
```

新 status／reason は追加しない。

### 3. operation evidence を FD capability にする

一般化された filesystem refactor は不要だが、apply 証跡専用の小さな内部 capability は必要である。

```python
@dataclass
class _ApplyEvidenceHandle:
    output_fd: int
    operation_fd: int
    logical_operation_path: Path
```

`logical_operation_path` は diagnostics／既存 test の表示用途に限定し、I/O authority にしない。

operation directory は以下の順序で扱う。

1. `os.mkdir(operation_name, 0o700, dir_fd=output_fd)`
2. 既存なら `os.open(operation_name, O_DIRECTORY | O_NOFOLLOW, dir_fd=output_fd)`
3. `fstat()` で directory、owner、mode を確認
4. transaction 完了まで `operation_fd` を保持

次の全処理を `operation_fd` またはその下で開いた nested directory FD に対する相対操作へ変える必要がある。

* `operation.json`
* `state.json`
* `attempts/`
* `transaction/`
* `transaction/files/`
* `transaction/managed-state/`
* `commit.json`
* `publication.json`
* transaction backup の検証と削除

immutable file は `openat(O_CREAT | O_EXCL | O_NOFOLLOW)`、state replacement は同じ operation FD 内の temporary entry と `renameat`、cleanup は既知 inventory に対する `unlinkat`／`rmdirat` 相当で行う。`shutil.rmtree(path)` や `Path.rglob()` をこの証跡 tree に残してはいけない。

Python の Unix `dir_fd` 対応は `open`、`mkdir`、`rename`、`unlink`、`stat` 等を `*at` 系に結び付けるため、この ancestry replacement 境界は Darwin/Linux 共通で閉じられる。([Python documentation][1])

## 決定的な fail-before / pass-after test

### Test A: transaction FD capture 前の replacement

1. repository 外に `output/` を作る。
2. `validate_candidate_output_directory()` で guard を取得する。
3. `output/` を `original-output/` に rename する。
4. 元の `output` pathname を、repository 内の `redirected/` への symlink にする。
5. apply transaction を開始する。

**現行 fail-before**

* `repository/redirected/planning-apply-*` が作成される。
* repository が apply safety rejection より前に mutation される。

**修正後 pass**

* 結果は `rejected/apply_output_rejected`。
* `repository/redirected/` は空。
* canonical 三文書、companion、decision artifact、Git index、remote ref は不変。
* `original-output/` にも新規証跡はない。

### Test B: transaction FD capture 後の replacement

新しい guarded-open helper が FD を取得した直後に、同じ pathname replacement を注入する。

**修正後 pass**

* 証跡は open FD が指す `original-output/` にのみ作成される。
* repository 内の replacement target は空。
* transaction の通常成功または通常 rollback semantics は変わらない。

Test A は「validation と transaction capture の間」を、Test B は「transaction capture 後」をそれぞれ固定する。両方が必要である。

## 原子的に閉じられる境界と残余制約

**閉じられる境界**

* output pathname の rename／symlink replacement による repository 内への証跡 redirect。
* operation directory の pathname replacement後も、保持済み FD を authority とした証跡更新。
* pre-capture replacement は mutation 0 での fail closed。

**残余制約**

* open 済み original directory が元の lexical pathname から到達可能であり続けることまでは保証できない。rename 後も安全な I/O は可能だが、元 pathname での人間による発見可能性は別問題である。
* mount removal、filesystem error、descriptor failure は既存の `apply_output_rejected` または recovery semantics で fail closed する。
* output directory owner による publication 後の任意改変を防ぐ security boundaryではない。今回閉じるのは ancestry substitution による誤った書込先である。

---

# 2. `apply-remote-ref-cas`

## 現行コードの正確な欠陥点

初回 publication は、local operation commit が `operation.expected_head` の直接の子であることを証明した後、次の通常 refspec を push している。

```text
git push origin HEAD:refs/heads/<branch>
```

remote の expected old value は push request に含まれていない。

このため `before_push` 後に remote branch が、

* delete された場合は branch を再作成できる。
* `expected_head` より古い ancestor へ巻き戻された場合は、通常の fast-forward として operation commit まで進められる。

その後の parity check は remote が local commit と一致するため `ready/adoption_published` を返す。

resume path も、先に `_remote_head() == expected_head` を確認した後、同じ通常 push を実行しているため、remote observation と push の間に同じ race が残る。

既存の remote divergence test は retry 開始前に remote が別 commit へ進んでいるケースだけを確認しており、「確認後、push直前の delete／rewind」を固定していない。

## 最小修正戦略

初回 publication と `_resume_publication()` の両方を、一つの dedicated helper に集約する。

```python
_push_operation_commit_cas(
    repo_root=repo_root,
    branch=operation.branch,
    expected_remote_head=operation.expected_head,
    local_commit=local_commit,
    local_tree=local_tree,
)
```

helper は push 直前に最低限次を再証明する。

```text
local_commit は40桁SHA
local_commit^ == operation.expected_head
local_commit^{tree} == local_tree
destination は refs/heads/<exact operation branch> 一個だけ
source は HEAD ではなく exact local_commit SHA
refspec は '+' なし
```

push は次の exact shape とする。

```text
git push \
  --force-with-lease=refs/heads/<branch>:<operation.expected_head> \
  origin \
  <local_commit>:refs/heads/<branch>
```

Git の explicit `<refname>:<expect>` form は、remote ref の現在値が指定した expected value と一致する場合だけ更新し、不一致なら push を失敗させる。branch absent も non-empty expected SHA とは一致しない。([Git SCM][2])

### no-force contract の維持

`--force-with-lease` は Git CLI 上、通常の fast-forward check を上書きできる option でもある。そのため、option を付けるだけでは「no-force」の証明にならない。dedicated helper が **`local_commit^ == expected_head` を必須証明**することで、実際に送信可能なのは expected remote head の直接の子だけに限定する。

現在の generic validator は bare `--force-with-lease` を禁止している一方、`--force-with-lease=...` は単純な完全一致判定をすり抜ける。

したがって次の二層にする。

* generic path: `word.startswith("--force-with-lease")` をすべて拒否。
* dedicated CAS path: exact ref、expected SHA、local SHA、single refspec を構文検証し、親 commit proof 後だけ実行。

これにより、任意 caller が lease を force mechanism として使用できる範囲は増えない。

### push failure 後の分類

現行 `_remote_head()` は「branch absent」と「`ls-remote` failure」をともに `None` にするため、delete と通信不能を区別できない。CAS failure の正しい public result を維持するには、内部 observation を三状態にする必要がある。

```text
present(<sha>)
absent
unavailable
```

CAS push が失敗した場合の分類は次の通り。

| push後の観測                           | 結果                                        |
| ---------------------------------- | ----------------------------------------- |
| remote == `local_commit` かつ tree一致 | 同一operationが別実行で公開済み。既存成功処理を続行            |
| remote == `expected_head`          | `publication_pending/push_failed`         |
| remote absent                      | `blocked_remote_diverged/remote_diverged` |
| remote がその他SHA                     | `blocked_remote_diverged/remote_diverged` |
| remote observation unavailable     | `publication_pending/push_failed`         |

status／reason の追加は不要であり、requirement の no-force、retry、remote divergence 契約をそのまま使用する。

## 決定的な fail-before / pass-after test

### Test A: first publication の delete／rewind race

`fault_hook("before_push")` で bare origin の ref を直接変更する。二ケースを parameterize する。

```text
delete:
  update-ref -d refs/heads/feature/issue <expected_head>

rewind:
  update-ref refs/heads/feature/issue <expected_head^> <expected_head>
```

rewind fixture では reviewed HEAD が少なくとも二 commit 目になるよう repository setup を作る。

**現行 fail-before**

* delete case: branch を再作成する。
* rewind case: ancestor から operation commit まで fast-forward する。
* 両方とも `ready/adoption_published`。

**修正後 pass**

```text
status = blocked_remote_diverged
reason = remote_diverged
```

加えて次を確認する。

* remote は absent または rewind 先のまま。
* local operation commit は保持される。
* reset／amend／rebase は行われない。
* `commit.json` は残る。
* `publication.json` は作られない。
* Human decision artifact と local commit 内容は不変。

### Test B: resume path の observation-to-push race

1. 最初の push を故障注入し `publication_pending/push_failed` を作る。
2. retry で `_resume_publication()` が expected remote head を観測した直後、CAS syscall 前に remote を delete／rewind する。
3. Test A と同じ `blocked_remote_diverged/remote_diverged` と remote 非変更を確認する。

初回と resume の両 call site が同じ CAS helper を使っていることを、この二本で固定する。

## 原子的に閉じられる境界と残余制約

**閉じられる境界**

* preflight／remote observation と push の間の ref delete、rewind、forward divergence。
* remote ref の expected-old compare-and-swap。
* branch recreation や古い ref からの意図しない fast-forward。

**残余制約**

* local commit 作成と remote ref update は分散 transaction にはならない。CAS failure 後に local commit が残るのは既存の retry contractであり、修正対象ではない。
* remote hook rejection、通信断、結果未確認は引き続き `publication_pending`。
* `ready` は parity 確認時点の事実であり、その後 Human または別 actor が remote ref を動かすことまでロックしない。

---

# 3. `candidate-stage-identity-toctou`

## 現行コードの正確な欠陥点

Candidate ZIP は private staged file の FD へ書かれ、その FD から bytes を読み、review と identity 導出を行っている。ここまでは verified inode に bind されている。

その後、

1. `_owned_entry_matches()` が staged FD の inode と `staged.name` の inode を比較する。
2. 比較完了後、`_atomic_publish_no_replace_at()` に `staged.name` を渡す。
3. Darwin は `renameatx_np`、Linux は `renameat2` を source pathname に対して呼ぶ。

という二段階になっている。

`_owned_entry_matches()` 成功後に staged name を rename し、同名へ別 file を作れば、rename syscall は replacement file を final name へ移す。一方、返される `PublishedCandidate.identity.zip_sha256` と `zip_byte_count` は元の open FD から読んだ ZIP の値である。したがって成功 result と final bytes が不一致になる。

既存 test は staged file の atomic open 直後に replacement を行うため、`_owned_entry_matches()` が false となり、publication 前に停止するケースしか覆っていない。今回の gap はその検査成功後である。

POSIX `renameat()` は source directory を FD で固定できるが、source object 自体は依然として source pathname で指定する。したがって追加の `stat()`、再検査、短い lock、より長い random name では check-to-rename gap を原子的には閉じられない。([man7.org][3])

## 最小修正戦略

`_atomic_publish_no_replace_at(source_dir_fd, source_name, ...)` を Candidate publication path から外し、**verified staged-file FD を直接 source とする OS 別 backend** に置き換える。

```python
_publish_verified_fd_no_replace_at(
    staged_fd=staged.descriptor,
    output_fd=output_descriptor,
    final_name=material.logical_filename,
)
```

### Linux

`linkat()` の `AT_EMPTY_PATH` form を使い、source pathname ではなく staged FD が指す inode を final name に hard-linkする。

```text
linkat(
    staged_fd,
    "",
    output_fd,
    final_name,
    AT_EMPTY_PATH,
)
```

`link()`／`linkat()` は destination が既に存在する場合に上書きしないため、`EEXIST` を既存の `CandidateCollision` に対応させる。Linux の `AT_EMPTY_PATH` は FD が指す file を source として扱えるが、Linux固有であり、kernel／permission policy の確認が必要である。([man7.org][4])

成功後は、元の hidden staged name がまだ staged FD と同じ inode を指す場合だけ unlink する。attacker replacement を cleanup してはいけない。

### Darwin

`fclonefileat(staged_fd, output_fd, final_name, flags)` を使用する。これは source を FD で指定し、destination は既存不可で、call は all-or-nothing の atomic operation とされる。([manp.gs — man pages][5])

成功後は Linux と同じく、hidden staged name が元 inode のままの場合だけ unlink する。

### 共通 postcondition

publication syscall 後、成功を返す前に以下を確認する。

* final entry は regular non-symlink file。
* final SHA-256 は既に導出済みの `identity.zip_sha256` と一致。
* byte count は `len(zip_bytes)` と一致。
* output directory を `fsync()`。
* collision 以外の backend failure は既存 `CandidatePublicationFailed`。
* final が自分の publication entry であることを証明できる場合だけ failure cleanup する。

deterministic ZIP の構築、review、`derive_candidate_identity()` は変更しない。再圧縮や final からの identity 再採番も行わない。public 成功は従来どおり `ok/candidate_created`、backend 利用不能または publication failure は既存の `blocked/candidate_publication_failed` となる。

### 禁止する fallback

次は P1 を閉じないため採用しない。

* `_owned_entry_matches()` の直後にもう一度 `stat()` する。
* rename 後に不一致を検出するだけ。
* advisory lock。
* random name の entropy 増加。
* source pathname を使う `renameat2`／`renameatx_np` の継続。
* final name を `O_EXCL` で先に作り、そこへ streaming write する fallback。

最後の方法は no-clobber 自体は守れるが、complete ZIP ができる前から final name が見え、process termination で partial final を残し得る。現在の「complete Candidateだけを final とする」挙動を維持する修正にはならない。

## 決定的な fail-before / pass-after test

### Test: post-match source-name swap

`_owned_entry_matches()` が real result `True` を返した直後に、test hook／monkeypatch で次を行う。

```text
rename staged.name → staged.name + ".owned"
create staged.name with sentinel attacker bytes
```

その後通常 publication を続行する。

**現行 fail-before**

* final Candidate の bytes が sentinel。
* function は元 ZIP の SHA／byte count を返す。
* 次の assertion が失敗する。

```python
assert sha256(final.read_bytes()) == published.identity.zip_sha256
```

**修正後 pass**

* Linux final は staged FD が指す元 inode。
* Darwin final は staged FD から clone された元 bytes。
* final SHA は returned identity と一致。
* sentinel replacement は final に移動されない。
* collision semantics は不変。
* cleanup は sentinel を削除しない。

これに加え、OS別に次を固定する。

| OS test | 必須 assertion                                                                                                                        |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Linux   | actual FD-origin link、existing final は `CandidateCollision`、unsupported／permission failure は final 0 で `CandidatePublicationFailed` |
| Darwin  | actual `fclonefileat`、existing final は `CandidateCollision`、`ENOTSUP` は final 0 で `CandidatePublicationFailed`                      |

## 原子的に閉じられる境界と残余制約

ここは他二件と異なり、**単一の portable POSIX primitive では全不変条件を維持できない**。

* `renameat` は directory ancestry は固定できるが source object を open file FD で指定できない。
* Linux の FD-to-name publication は Linux-specific。
* Darwin の `fclonefileat` は Darwin-specific。
* `fclonefileat` はすべての volume が対応するわけではない。
* Linux の `AT_EMPTY_PATH` も実行 kernel、filesystem、permission policy の実機確認が必要。

したがって、backend 利用不能時に pathname rename へ戻してはならない。**既存 `candidate_publication_failed` で fail closed**とするのが、public contractを変えずに P1 を閉じる唯一の安全な扱いである。

「Darwin/Linux上のあらゆる filesystem で必ず publication 成功」と「FD identity bind」「atomic complete publication」「no-clobber」を同時に必須とするなら、その組合せは現行 portable contract では保証不能である。これは実装で隠すべき fallback ではなく、仕様上の residual compatibility constraint として明示すべき境界である。

---

# 相互作用と実装順序

## 相互作用

`candidate-stage-identity-toctou` は `issue_planning_candidate.py` 内で完結し、apply 二件とは独立している。

apply 二件はどちらも `issue_planning_apply.py` の transaction／resume lifecycle を変更する。先に output evidence を FD capability 化し、その後に remote CAS を載せる。逆順にすると、CAS helper と resume tests を pathname-based operation directory から再度移行することになる。

output descriptor は local commit 作成、push、publication record 作成まで保持する。したがって push 中に output pathname が置換されても、`commit.json`／`publication.json` は original evidence directory に記録され、repository 内へ redirect されない。

## 推奨順序

1. **三件の Red test を先に追加**

   * Candidate post-match swap。
   * apply output pre-capture／post-capture replacement。
   * remote delete／rewind first-push＋resume race。
2. **Candidate FD-origin publication**

   * 独立した repair unit として Green 化。
3. **apply output guard threading**

   * application、port、resume probe、transaction runner。
4. **apply evidence lifecycle の descriptor-relative 化**

   * record、state、attempt、backup、recovery、commit、publication、cleanup。
5. **remote CAS**

   * 初回と resume を同じ helper に置換。
   * remote observation を present／absent／unavailable に分離。
6. **mechanical mirror／projection 同期と focused suites**

   * semantic docs、Prompt、wrapper、Oracle configuration は変更しない。

---

# 維持される contract

| Contract                         | 修正後                                                |
| -------------------------------- | -------------------------------------------------- |
| Candidate成功                      | `ok/candidate_created` のまま                         |
| Candidate publication failure    | `blocked/candidate_publication_failed` のまま         |
| Candidate collision              | 既存 `output_collision` のまま                          |
| apply output mismatch            | `rejected/apply_output_rejected` のまま               |
| remote divergence                | `blocked_remote_diverged/remote_diverged`          |
| push transport failure           | `publication_pending/push_failed`                  |
| Candidate ZIP bytes／SHA／identity | 同じ verified `zip_bytes` から導出                       |
| no-clobber                       | final existing entryを変更しない                         |
| no-force                         | operation commit が `expected_head` の直接の子であることを別途証明 |
| Human authority                  | 変更なし                                               |
| direct Oracle boundary           | 変更なし                                               |
| canonical三文書／Prompt／wrapper      | 変更なし                                               |

Human decision、canonical adoption、direct Oracle transport の境界は今回の三修正から独立しており、触れる必要はない。requirement 上も Human decision の生成・推測は禁止され、publication 成功は local／remote／tree parity に限定されている。

# 不確実性・未検証主張

* GitHub source／branch／HEAD と現行コード位置は connector で確認済み。
* repository は read-only で確認しており、上記 test はこの相談内では実行していない。
* Git／POSIX／Linux／Darwin の外部仕様は **2026年7月31日 JST** に参照した。Codex 側での独立検証済みとは扱わない。
* Linux runner 上の unprivileged `linkat(..., AT_EMPTY_PATH)`、Darwin runner の target volume における `fclonefileat` 対応は未確認であり、OS別の実 syscall test を merge gate に含める必要がある。
* explicit lease を使うため、「no-force」は option 名の禁止ではなく、**non-fast-forward update を許さない意味上の契約**として扱う必要がある。これを token-level prohibition と解釈する場合、Git CLIだけでは expected-old CASを表現できず、別 transport が必要になる。

[1]: https://docs.python.org/3.12/whatsnew/3.3.html "https://docs.python.org/3.12/whatsnew/3.3.html"
[2]: https://git-scm.com/docs/git-push/2.3.10.html "https://git-scm.com/docs/git-push/2.3.10.html"
[3]: https://www.man7.org/linux/man-pages/man3/renameat.3p.html "https://www.man7.org/linux/man-pages/man3/renameat.3p.html"
[4]: https://man7.org/linux/man-pages/man2/link.2.html "https://man7.org/linux/man-pages/man2/link.2.html"
[5]: https://manp.gs/mac/2/clonefile "https://manp.gs/mac/2/clonefile"
---
種別: artifact
ID: "20260730t155200z"
タイトル: "PR 351 S007 P1 Repair ChatGPT Concretization"
状態: "archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
template: "blank"
authority: "advisory"
derived_from:
  - "PR #351 review 4820348714"
  - "HEAD 91715eecf306bd0c978da922f87193151764cdcd"
  - "ChatGPT session iss00334-pr351-s007-p1-repair"
---

# Consultation identity

- repository: `chemitaro/spec-dock`
- branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- HEAD: `91715eecf306bd0c978da922f87193151764cdcd`
- PR: `351`
- review: `4820348714`
- exact branch inspected: yes
- default branch fallback: no
- model evidence: `requested=Pro`, `resolved=Pro`, `verified=yes`
- prompt submitted: yes
- elapsed: `32m00s`
- prior same-thread follow-up: pre-submit failure because Chat／Work mode could not be verified
- recovery: fresh Blue session with prior advisory context attached; duplicate submission 0
- excluded: P2、architecture redesign、Oracle-native local configuration、Prompt、wrapper、canonical三文書

# ChatGPT advisory output
