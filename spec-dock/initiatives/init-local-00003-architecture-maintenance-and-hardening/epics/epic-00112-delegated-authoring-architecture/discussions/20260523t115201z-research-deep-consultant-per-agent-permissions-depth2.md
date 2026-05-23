---
type: research
source: deep-consultant
created_at: 2026-05-23T11:52:01+09:00
epic: epic-00112
topic: per-agent permissions and depth-2 delegated authoring
status: current
---

# Deep Consultant Research: Per-Agent Permissions and Depth-2 Delegated Authoring

## executive_recommendation

Deep Consultant の推奨は、全面採用ではなく「限定された depth=2 + discussion-first + orchestrator-owned final gate」である。

最重要判断は次の通り。

- `system-architect` / `implementation-planner` をいきなり canonical writer にしない。
- 初期段階では `discussions/` への中間成果書き込み、または draft artifact generation だけを許可する。
- `design.md` / `plan.md` への昇格は、main orchestrator または専用の `spec-doc-author` が担う。
- authoring agent が `repo-analyst` / `researcher` / `consultant` / `deep-consultant` / `spec-reviewer` を直接呼ぶことは、限定条件付きで許可してよい。
- authoring agent が得た `spec-reviewer` pass は preflight pass であり、final pass ではない。
- final review pass と canonical promotion は main orchestrator が所有する。
- depth=2 は read-only specialist の allowlist に限定し、iteration / fan-out cap を設ける。

## decision_matrix

| 論点 | 推奨 | 理由 |
| --- | --- | --- |
| 現行 read-only delegated draft | 短期維持 | 最も安全で、既存 workflow と整合する |
| discussion-write authoring | 採用推奨 | 中間成果を永続化でき、main orchestrator の統合作業を軽くできる |
| canonical `design.md` / `plan.md` direct write | 段階導入 | probe と diff gate が通るまで早すぎる |
| unrestricted depth=2 | 不採用 | recursive fan-out、責任境界の崩壊、review 独立性低下が大きい |
| allowlisted depth=2 | 採用推奨 | read-only specialist に限定すれば品質向上効果が大きい |
| Permission Profile as sole ACL | 不採用 | beta / parent override / tool surface 差分があり、単独の強い境界にできない |

## recommended_role_permission_model

Deep Consultant は、権限を次のように段階化することを推奨した。

| Role | Phase 1 | Phase 2 | Phase 3 |
| --- | --- | --- | --- |
| main orchestrator | integration owner | integration owner | final review / promotion owner |
| system-architect | read-only draft | active scope `discussions/` write | `design.md` + `discussions/` write trial |
| implementation-planner | read-only draft | active scope `discussions/` write | `plan.md` + `discussions/` write trial |
| spec-reviewer | read-only | read-only | read-only |
| repo-analyst | read-only | read-only | read-only |
| consultant / deep-consultant | read-only | read-only | read-only |
| researcher | read-only + controlled network | read-only + controlled network | read-only + controlled network |
| dev-coder | approved implementation scope | approved implementation scope | approved implementation scope |

`system-architect` / `implementation-planner` は、`requirement.md`、相互の canonical artifact、implementation files、tests、`.codex/`、`.agents/`、workflow files、config layers を編集しない。

## active_path_warning

Deep Consultant は、`spec-dock/active/...` symlink に対して ACL を直接張ることを避けるべきだと指摘した。

推奨は、task start 時に active symlink の実体パスを解決し、task manifest に exact allowed path list として固定すること。

理由:

- active symlink は作業中に切り替わり得る。
- symlink path に許可を与えると、意図せず別 target へ権限が移る可能性がある。
- diff gate / audit も resolved canonical path に対して実施した方が説明可能性が高い。

## depth2_policy

推奨される depth=2 policy は次の通り。

- default max depth は 1 のまま維持する。
- authoring workflow で明示された場合だけ depth=2 を許可する。
- child allowlist は `repo-analyst`, `researcher`, `consultant`, `deep-consultant`, `spec-reviewer` に限定する。
- child は read-only とする。
- `researcher` だけ controlled network を許可し得る。
- `dev-coder`、generic worker、shell-heavy fixer、write-capable doc author は child として禁止する。
- child は grandchild を呼ばない。
- review iteration は最大 2 回で hard stop し、main orchestrator に戻す。
- fan-out cap と thread cap を設ける。

## review_loop_ownership

Deep Consultant は review loop を 2 種類に分けるべきだとした。

| Review | Owner | Gate |
| --- | --- | --- |
| Draft pre-review | authoring agent | canonical gate ではない |
| Final independent review | main orchestrator | canonical promotion / completion gate |

authoring agent が `spec-reviewer` を直接呼ぶことは、早期欠陥発見のために有効。ただし、その pass を final pass と扱ってはいけない。

## discussion_policy

`discussions/` は source of truth ではなく、reasoning ledger / evidence incubator として扱う。

推奨ルール:

- timestamp + role + topic の lowercase filename を使う。
- append-only または new file per run を基本にする。
- frontmatter に role、parent task、active target、inputs、assumptions、evidence、risks、status を持たせる。
- canonical docs に昇格したものだけを curated conclusion として反映する。
- 古い analysis は削除せず、`superseded_by` で接続する。
- raw logs や長大な transcript ではなく、採用判断に使える要約として保存する。

## permission_profile_risk

Deep Consultant は Permission Profile を有効な防御層と評価しつつ、単独の強制境界として扱わないよう警告した。

主要リスク:

- beta /仕様変更リスク。
- parent runtime override や subagent current sandbox policy による上書きリスク。
- MCP / browser / computer-use / approved escalation など、filesystem permission 外の control surface。
- Desktop App と CLI の挙動差。
- active symlink の target drift。

推奨:

- Permission Profile は defense-in-depth の 1 層にする。
- 最終 enforcement は diff audit、role-aware CI gate、review gate で行う。
- probe 失敗時は read-only evidence mode に fallback する。

## phased_rollout

### phase_1_readonly_depth2_pilot

- authoring agents は read-only のまま。
- read-only specialists と `spec-reviewer` を呼べる。
- main orchestrator が discussion に記録し、canonical docs に統合する。

### phase_2_discussion_write_authoring

- `system-architect` / `implementation-planner` に role-specific active scope `discussions/` write を許可する。
- preflight review loop を最大 2 回まで許可する。
- changed path audit を必須にする。
- canonical docs は main orchestrator または専用 writer が更新する。

### phase_3_exact_file_canonical_writer_trial

- CLI Permission Profile probe が通った後だけ実施する。
- `system-architect` は `design.md`、`implementation-planner` は `plan.md` に限定する。
- separate session / task manifest / exact path permissions / post-run diff guard / orchestrator final review を必須にする。

## tests_and_probes

Deep Consultant が挙げた必須検証:

- forbidden write canary。
- discussion-only write probe。
- parent override probe。
- reviewer independence test。
- loop cap test。
- depth cap test。
- promotion trace test。
- dogfooding gate。

## final_recommendation

Deep Consultant の最終判断は、「agent に考えさせる範囲は広げるが、canonical source of truth を変更する権限は狭く、遅く広げる」である。

この方針により、自律的な調査・相談・pre-review の価値を取り込みつつ、canonical docs と final review の責任境界を維持できる。
