---
種別: research
ID: "20260617t000227z-research"
タイトル: "Timestamp Collision Source Grounding"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260617t000227z-research Timestamp Collision Source Grounding

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- GitHub issue #188 の failure mode が、既存 SpecDock runtime / docs / skills のどの生成経路に残っているかを整理する。
- 要件具体化前に、local source で解ける範囲と、ユーザー判断が必要な scope boundary を分離する。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md}`
  - GitHub issue #188 body
  - `spec-dock/active/epic/{requirement.md,design.md,plan.md}`
  - `spec-dock/active/initiative/requirement.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/reference_naming.md`
  - `spec-dock/docs/rules/issue/discussions.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- 検証手順:
  - `issue start 188` を試行し、local node 不在を確認後、`import issue 188` で `epic-00033` 配下に scaffold を作成した。
  - `rg` / `sed` で timestamp naming、discussion artifact generation、validation、PR repair artifact guidance を確認した。
- 実験条件:
  - 実装変更前の source read-only 調査。runtime test 実行は未実施。

## facts / 観測できた事実 (必須)
- GitHub issue #188 の再現は、同一 `discussions/` directory に `20260615t154449z-disc-pr-repair-batch.md` と `20260615t154449z-disc-pr-repair-unit-u001-management-api-test.md` が同時に存在し、`spec-dock sync` の preflight validate が `Duplicate discussion timestamp slot detected` で失敗するもの。
- `reference_naming.md` は discussion docs の標準形を `<ts>-<kind>-<slug>.md`、same-second collision 形を `<ts>-<nn>-<kind>-<slug>.md` と定義し、`new doc <type>` には basename / doc_id override がないと説明している。
- `create_node.py` の `create_discussion_doc` は create lock を取得し、`ports.clock.now_iso()` から timestamp を作り、`_allocate_discussion_doc_filename` で同秒既存 file を scan して `01..99` suffix を割り当てる。
- `create_node.py` は pre-lock / post-lock / post-write の duplicate guard を持ち、既に壊れた duplicate timestamp / duplicate suffix / malformed candidate がある場合は fail-fast する。
- `tests/cli_runtime/test_runtime_new_doc_s09.py` には `test_parallel_new_doc_allocates_unique_suffixes` があり、同じ timestamp に対する並列 `create_discussion_doc` が unsuffixed + suffixed の一意な doc_id になることを確認している。
- `tests/cli_runtime/test_validate.py` は duplicate standard timestamp slot と duplicate suffix slot を検出する validator coverage を持つ。
- `.agents/skills/github-pr-merge-preparer/SKILL.md` と provider source 側の同 skill は、PR repair batch / repair unit を `<ts>-disc-pr-repair-batch.md` / `<ts>-disc-pr-repair-unit-<unit-slug>.md` のような timestamped issue-local `disc` として作るよう説明しているが、`spec-dock new doc disc` を必須生成経路として指定していない。
- `spec-dock/docs/rules/issue/discussions.md` は discussion artifact の create command 一覧を持つ一方、PR repair batch / repair unit の詳細は `github-pr-merge-preparer` skill-local template に委ねている。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Core runtime の `new doc` 経由だけを前提にすれば、#188 の再現 failure はかなり抑え込まれている。
  - 既存 failure は、agent / skill / workflow が `<ts>` を一度だけ取得し、その値を複数 filename に手作業で再利用した可能性が高い。
  - 実装要件は runtime allocator の新規作成だけでなく、PR repair 系など「manual timestamp filename guidance」を command-first または shared allocator-first に寄せる scope を含むかどうかが重要になる。
- 推測の根拠:
  - Runtime は create lock + scan + suffix allocation + duplicate guard を既に持つ。
  - Failure example の file names は both unsuffixed standard slot であり、runtime allocator 経由なら2件目は `20260615t154449z-01-disc-...` になるはず。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実際に failure を発生させた session / workflow がどの code path で2 file を生成したか。
  - `github-pr-merge-preparer` の実運用で、agent が CLI を使わず直接 file write しているか、あるいは別 helper が存在するか。
  - provider / dogfooding mirror のどちらを issue #188 の実装 source of truth として変更するかの詳細設計。
- 確認できない理由:
  - 現時点の local repo には failure session の raw transcript は含まれていない。
  - 要件具体化前の調査段階で、まだ実装差分と tests は作っていない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - #188 の scope は「runtime `new doc` 生成経路のさらなる hardening / regression test」に限定するか、それとも「SpecDock が提供する skills / workflow guidance が手作業 timestamp reuse を誘発しないよう、PR repair batch / repair unit などの生成 guidance まで command-first に変える」か。
- pressure-test question として切り出すべき候補:
  - この issue で閉じるべき対象は、CLI/runtime allocator の安全性だけですか。それとも、agent-facing skills が discussion artifact を作るときに `spec-dock new doc` / shared allocator を必ず使うようにするところまで含めますか。
- 質問せずに解決できた候補:
  - Duplicate timestamp slot の validator behavior は既存仕様として維持するべき。GitHub issue #188 も validator を有用と扱い、生成元の修正を求めている。
  - Legacy sequential files は grandfathered であり、自動 rename / legacy compatibility 復活は scope 外。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "timestamp slot" と "doc_id"
  - "discussion artifact generation" と "manual discussion file write"
- 既存 docs / code / tests / discussions での使われ方:
  - `reference_naming.md` では standard slot は `<ts>`、suffix slot は `<ts>-<nn>` の filename prefix として説明される。
  - Runtime `doc_id` は slugless identity で、standard は `<ts>-<kind>`、collision は `<ts>-<nn>-<kind>`。
  - Validator の duplicate standard slot は同じ `<ts>` を複数 unsuffixed file が共有する状態を reject する。
- 判断が必要な理由:
  - 要件では、filename uniqueness だけでなく doc_id uniqueness / validator compatibility / skill guidance のどれを closure target にするかを明確にする必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - 同一 operation で PR repair batch と repair unit を同一 issue `discussions/` に作る。
  - 同一秒に複数 agent / thread が `new doc` を実行する。
  - 同一秒に `adr`, `disc`, `research`, `interview`, `scratch`, `draft-*` が混在する。
  - 既に duplicate timestamp slot で壊れている workspace 上で新規 discussion doc を作ろうとする。
  - `01..99` suffix がすべて埋まっている。
- その edge case が requirement / design / plan に与える影響:
  - Batch generation は「1 artifact ごとの allocator 呼び出し」か「複数 artifact 用 allocator API」のどちらかを要求する。
  - Existing corrupt workspace は auto repair ではなく fail-fast + doctor/validate guidance のままでよい可能性が高い。
  - Suffix exhaustion は既存 RuntimeError を維持し、無限 sleep や timestamp mutation policyを導入しない方が小さい。

## implications / 判断への含意 (必須)
- Requirement には、validator を緩めないこと、duplicate を作らない生成経路を増やすこと、既存 corrupt state は fail-fast することを分けて書く必要がある。
- Design では、既存 `create_discussion_doc` allocator を再利用する command-first approach と、skill/manual writer 用 helper / guidance を追加する approach のどちらを採るかを決める必要がある。
- Plan では、少なくとも PR repair batch + repair unit の同秒作成 regression を fixture 化する価値がある。
- ADR は不要そう。既存 naming contract を変える判断ではなく、生成側を contract に従わせる issue-local hardening で閉じられる見込み。

## リスク/制約 (任意)
- PR repair workflow は skill asset と provider install_root の両方に存在するため、更新する場合は provider-side authority と dogfooding mirror の扱いを明確にする必要がある。
- `new doc` が explicit basename override を持たないため、既存 template を特殊名で作りたい workflow は「CLI で一旦作る」だけでは target filename を完全制御できない。ここをどう扱うかが scope 判断に影響する。

## 反映先 (任意)
- reflected_to:
  - pending: `requirement.md`
  - pending: `report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- GitHub issue #188
- `spec-dock/docs/reference_naming.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `tests/cli_runtime/test_runtime_new_doc_s09.py`
- `.agents/skills/github-pr-merge-preparer/SKILL.md`
