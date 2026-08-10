---
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
document_status: candidate
document_role: "issue_requirement_draft"
title: "iss-00357 Reduce Runtime to Storage Core — Vertical Slice Requirement Draft"
target: "iss-00357"
source_repository: "chemitaro/spec-dock"
source_branch: "main"
source_sha: "2c75e0c02cb65a6e74040a72dc161d342d661091"
generated_on: "2026-08-09"
issue_id: "iss-00357"
github_issue_number: 357
depends_on:
---

> この文書は human review 用の evidence-only candidate であり、正本への採用、レビュー合格、実装着手可、PR準備完了、merge可能、Issue終了、Epic完了を表さない。

# 1. Slice outcome

利用者が SpecDock の構造管理を、workflow / profile / assurance / reviewer gate なしで end-to-end 実行できる Storage Core を提供する。

この Issue は Runtime layer だけを横断的に削る作業ではない。CLI 利用者が次の一連の価値を確認できるところまで、Runtime implementation、CLI help、tests、compatibility、Runtime migration notes を同じ Issue で閉じる。

```text
node / dependency を読む
  -> active scope を選ぶ
  -> dependency-ready な Issue を start する
  -> Artifact を作成または file import する
  -> GitHub Issue を close し active を clear する
  -> sync / validate で構造を確認する
```

# 2. Current problem

exact source SHA では以下が Runtime に存在する。

- parser / registry に `assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`
- `artifact import chatgpt-output`
- active entry の authority / grants / promotion record
- `issue finish` の authority / delegated artifact / EAL gates
- `draft-design` / `draft-plan` の Assurance Profile routing
- `pr-repair-batch` と `draft-*` の Current creation
- Context Pack / Active Manifest に workflow authority を持ち込む経路
- fresh scaffold と Report contract の旧 workflow coupling

この構成では、構造操作が model / reviewer / report content と結合し、Core 単体利用ができない。

# 3. Observable value

Issue 後に利用者が確認できるべきこと:

- `spec-dock --help` に Storage Core command だけが現れる。
- `active set` は valid scope の ID / path を選択するだけで、dependency、Review、Plan、Report、authority を評価しない。
- blocked Issue を research / planning のため active selection にできる。
- `issue start` は Issue target に対し、別 unfinished active Issue guard、dependency-only readiness、branch checkout、active set の順に動く。
- `issue start --force` は unfinished active guard だけを迂回し、dependency blocker は迂回しない。
- `deps check` / projection の `ready` は dependency-only である。
- `issue finish` は active Issue の linked GitHub Issue を close し、already closed を成功として扱い、close 成功後だけ active clear、続いて post-sync を実行する。
- `issue finish` は Requirement / Design / Plan / Test / Review / Report / EAL / authority / promotion を読まない。
- `new artifact [type]` の type は optional positional。省略時と explicit `blank` が使える。
- Current typed creation は `research`、`interview`、`disc`、`decision-candidate`、`adr`。`analysis` は存在しない。
- generic `artifact import file` だけが import surface として残る。
- Fresh node scaffold は Assurance なしで single R/D/P + thin Report を生成できる。
- Existing heavy Report、`.assurance.json`、draft / repair Artifact が存在しても Core operations が旧 workflow gate を再開しない。
- Removed command を呼ぶと明示的に拒否され、legacy backend へ fallback しない。

# 4. In scope

- Runtime parser / registry / bootstrap
- command modules and application services
- active state model / serialization / Context Pack
- dependency readiness integration
- Issue start / finish
- Artifact domain / parser / allocation / template resolution
- generic file import retention and provider-specific import removal
- node scaffolder mechanism
- sync / validate / doctor impact
- privacy-safe diagnostics and partial-failure recovery
- provider Runtime source and dogfood Runtime projection
- Runtime help / reference docs
- unit、application、CLI、negative、historical compatibility tests
- retained / removed Runtime inventory
- 358 / 359 / 360 handoff contracts

# 5. Out of scope

- Template prose and Authoring Guide content, owned by 358
- Planning Level meaning / Completion Guide text
- repo-local skill implementation, owned by 359
- installer final prune / distribution migration, owned by 360
- release-wide full regression / PR assembly, owned by proposed final candidate
- historical file rewrite or deletion
- external Intelligence implementation
- new quality / review / evidence gate

# 6. Adopted behavioral contracts

## 6.1 Active selection

Persist only selected scope identity needed for deterministic navigation:

- ID
- repo-relative path
- parent selection derived or stored only as structural pointer where existing contract requires it

Do not persist:

- authority
- grants
- promotion record
- planning level
- review status
- quality status
- evidence adoption status

## 6.2 Issue start

Preconditions:

1. target resolves to an Issue
2. dependency DAG says ready
3. no different unfinished active Issue, unless `--force`
4. branch checkout succeeds

Mutation order:

1. resolve target and current GitHub state
2. evaluate unfinished active guard
3. evaluate dependency readiness
4. checkout
5. set active
6. post-mutation sync as applicable

`--force` applies only to step 2.

## 6.3 Issue finish

Mutation order:

1. resolve active Issue and linkage
2. close GitHub Issue; already closed is success
3. clear active only after close success
4. post-sync

Failure:

- close failure → active preserved
- active clear failure after close → partial success, explicit recovery
- post-sync failure → close / clear state distinguished from stale projection
- no quality gate

## 6.4 Artifact

Current creatable:

```text
blank
research
interview
disc
decision-candidate
adr
```

Current syntax:

```text
spec-dock new artifact [type] --<scope> <id> --title <title> [--slug <slug>]
```

Historical recognizability is a separate contract. Existing `pr-repair-batch`、`draft-*`、legacy discussion、scratch / note forms are not automatically malformed merely because Current creation is closed.

## 6.5 Import

Retain:

```text
spec-dock artifact import file ...
```

Remove:

```text
spec-dock artifact import chatgpt-output ...
```

Generic import retains existing safety obligations: explicit one regular file、opaque bytes、destination-side collision protection、scope validation、privacy-safe output、cleanup / partial-failure semantics。

## 6.6 Scaffold

Runtime copies deterministic scope templates supplied by Authoring Kit:

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md`

No profile selection, Assurance composition, Report interpretation, or draft routing. The mechanism must accept thin Report content and empty user sections.

# 7. Compatibility

- Existing `.assurance.json` remains a historical file and is ignored by retained Core behavior.
- Existing Report bytes are not changed by normal Core operations.
- Existing canonical R/D/P are not recomposed.
- Existing historical artifact filenames remain discoverable / non-malformed according to the explicit historical catalog.
- Existing generic imported files retain their identity and byte semantics.
- Existing node / dependency metadata format is preserved unless a separately justified migration is documented in this Issue.
- Generated active / index / tree views may be regenerated; source metadata and user documents are preserved.

# 8. Acceptance criteria

Future verification criteria:

1. Parser / registry do not expose removed command groups or provider-specific import.
2. Removed modules have no reachable registration / fallback path.
3. Active Manifest and Context Pack no longer carry authority / grants / promotion data.
4. `active set` selection-only positive and negative tests cover blocked Issue selection.
5. `issue start` covers unfinished guard、dependency blocker、`--force` boundary、checkout failure、active write failure。
6. `issue finish` covers close success、already closed、close failure、clear failure、post-sync failure and no-gate behavior。
7. Artifact omitted type、explicit blank、five typed forms、unknown type、historical-only type、same-second collision、suffix exhaustion、create lock、symlink、path escape、scope mismatch are tested.
8. Generic file import safety and privacy tests remain.
9. Fresh node creation works without `.assurance.json` and contains thin Report path.
10. Existing historical fixtures do not activate Assurance / Report / reviewer checks.
11. Runtime docs / help describe retained semantics and no removed workflow as Current.
12. Provider source and dogfood Runtime copies have expected parity.
13. 358 receives scaffold / Artifact contract; 359 receives retained CLI inventory; 360 receives removed Runtime / asset inventory.

# 9. Negative requirements

- Do not replace removed quality gates with a differently named gate.
- Do not make `active set` call dependency readiness.
- Do not allow `issue start --force` to bypass dependencies.
- Do not clear active before GitHub close succeeds.
- Do not parse Planning Level from `plan.md`.
- Do not parse thin / heavy Report for lifecycle decisions.
- Do not add `analysis`.
- Do not auto-convert historical Artifact.
- Do not delete obsolete provider assets in this Issue; supply inventory to 360.
