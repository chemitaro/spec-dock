# Issue 344 Requirement Review

## Verdict

FAIL

## Findings

### F-005 [blocking] No-backfill の全体不変表現が残り、F-002 の修正が閉じていない

* Location:

  * `requirement.md` §5.3「変更しないもの」
  * `requirement.md` §9.1「互換性」
  * `report.md` Decision Ledger `D-004`
  * `report.md` Evidence Adoption Ledger `EAL-003`
* Problem:

  * `I344-RQ-005` と `AC-344-005` は、no-backfill の不変対象を existing Workbench の entry、bytes、names、mtime、および existing ancestor / sibling の README / Workbench 状態へ限定し、managed templates、docs、runtime、`.gitignore` の正規 update を明示的に許可する形へ修正されている。
  * しかし §5.3 には依然として「existing root / node の files」を変更しないという無限定な記述が残り、§9.1 にも「existing root / node を書き換えない」とある。これらは、通常 update が managed directories を置換し、provider `.gitignore` を更新する現行 installer behavior、および同文書の `AC-344-005` と衝突する。
  * したがって、実装者は「managed provider assets の正規更新を行うべきか」「existing root の全 file を不変にすべきか」を一意に判断できない。
  * `report.md` は `D-004` と `EAL-003` で F-002 を適用済み、F-001〜F-004 をすべて修正済みとしているため、canonical requirement に残る上記矛盾とも一致していない。
* Required correction:

  * §5.3 の「existing root / node の files」と §9.1 の「existing root / node を書き換えない」を、次の境界へ限定する。

    * existing scope の canonical documents、metadata、Workbench user content は backfill または無関係な mutation の対象にしない。
    * 通常 update による `spec-dock/docs`、`templates`、`scripts`、`system`、`spec-dock/.gitignore` など managed provider assets の更新は許可する。
    * new node 作成時は新規 node のみを生成し、existing ancestor / sibling の canonical state と Workbench state は変更しない。
  * `report.md` の `D-004`、`EAL-003`、requirement authoring gate に、本 fresh review で F-002 の残存矛盾が確認されたことを記録し、再修正後の fresh re-review を要求する。
* Evidence:

  * 親 Epic も no-backfill を existing scope への README 追加禁止と new node 以外への追加禁止として定義しており、managed root 全体の不変は要求していない。
  * 親計画は Candidate 1 に installer、provider assets、package configuration、docs の変更を明示的に割り当てている。

### F-006 [blocking] Report が未合成の design への promotion を既成事実として記録している

* Location:

  * `report.md` Decision Ledger `D-002`
  * `report.md` Spec Authoring Gate
  * Issue-local `design.md`
* Problem:

  * `D-002` は `Status=resolved`、`Disposition=promoted_to_design` と記録されている。
  * 一方、同じ report の authoring gate は design phase を requirement gate 待ちの `pending`、`blocking=yes` としており、Issue-local `design.md` も `artifact_state: awaiting-assurance-compose` の未合成 placeholder で、本文を書き始めないよう明記している。
  * これは report 自身が定義する `promoted_to_design` の意味と、実際の phase state を一致させていない。Evidence Adoption Ledger が authoring evidence を `partially_adopted` のままとしていることとも整合しない。
  * 親計画も Issue-local requirement が fresh review を通過してから design を開始する順序を要求している。
* Required correction:

  * design 本文へ判断が実際に反映されるまでは、`D-002` を `promoted_to_design` としない。
  * 現段階では、たとえば requirement への反映を示す `Disposition=applied` とし、design 反映を follow-up に残すか、promotion 未完了の状態として記録する。
  * requirement review PASS 後に design を合成し、該当 design section と evidence を参照できる状態になってから `promoted_to_design` を記録する。
* Evidence:

  * Report front matter が単一の `状態: "draft"` へ修正され、requirement gate が prior FAIL を保持している点自体は適切である。
  * 問題は、その blocked state と `D-002` の promotion claim が同時に存在することである。

## Scope and consistency checked

* GitHub Connector で指定 branch `iss-00344-workbench-shell-scaffolding` を開き、branch HEAD が commit `ac243ac1f58e77860ca8c15be7522ebdf21e79c2` と同一であることを確認した。対象 commit は F-001〜F-004 の反映 commit として記録されている。
* 添付 review task の fresh-review responsibilities、PASS 条件、advisory / evidence-only 境界に従って確認した。
* F-001 の command boundary 修正は成立している。README guidance は repository root から実行する repo-local runtime の exact invocation に限定され、global installer CLI への generic import dispatch は明示的に対象外となった。現行 installed `spec-dock` entrypoint が installer で、day-to-day operations を repo-local runtime が所有する source contractとも一致する。
* F-003 の copy compatibility 修正は成立している。generated README が同一の場合と source / target README が異なる場合が分離され、後者では README 専用 filter を追加せず既存 source-wins whole-tree behavior を維持する。現行 implementation も destination file を削除して source bytes を copyする source-wins mergeである。
* README の9 guidance element、README-only tracking、nested / case-variant exclusion、Git checkout と manual copy の役割分担、Git ignore 非 security boundary、explicit import の evidence-only authority は requirement に固定されている。
* optional presence、semantic opacity、disposable contract は親 Epic と一致している。既存 tests も exact `.workbench` subtree の metadata discovery exclusionと、copy 後の validate / sync / dependency opacityを観測している。
* package parity は source、wheel、sdist、installed resources の4 Workbench READMEと `templates/README.md` だけを許可する exact inventory として要求されている。現行 package configuration の broad nested README exclusionが変更対象であることも確認した。
* Issue ownership は維持されている。Issue 344 は shell、focused packaging evidence、manual-copy compatibilityを所有し、Issue 345 は generic import、Issue 346 は candidate-wheel E2E、dogfood、full regression、final review、PR deliveryを所有する。

## Residual risks

* 現行 installer の `_prune_legacy_scaffold` は `templates/README.md` 以外の nested README を無条件削除する。Design phase では、package-data exclusionだけでなく、この prune logicも5-file exact allowlistへ整合させる必要がある。
* provider `.gitignore` と installer fallback は現在 `.workbench/` 全体を ignore している。README 再包含後も nested README、case variant、near-name directory、および既存 user-created Workbench contents の露出範囲を実 Git repository で検証する必要がある。
* `uv build`、wheel / sdist inventory、installed resource inspection、Git ignore matrix、focused pytest は本レビューでは実行していない。実装、test、build、PR、merge、Issue finish の完了は未確認である。
* 本判定は read-only advisory / evidence-only であり、canonical authority または reviewer gate の自己更新を主張しない。

## Promotion decision

* requirement phase を design phase へ昇格不可
