# Issue 344 Requirement Review

## Verdict

FAIL

## Findings

### F-001 [blocking] README の公開コマンド表記が現行 CLI 境界と一致しない

* Location:

  * `I344-RQ-003` guidance element 4
  * `AC-344-003`
  * `I344-RQ-010` / `AC-344-010`
* Problem:

  * 要件は README に `spec-dock artifact import file` と記載することを求めているが、現行の installed `spec-dock` entrypoint は installer CLI であり、日常操作は repo-local runtime の `spec-dock/scripts/spec-dock` が所有する。`pyproject.toml` の console script も installer の `spec_dock.cli:main` を指している。したがって、この表記を実行可能な exact command と解釈すると現行公開面では成立せず、単なる shorthand ならその旨が未定義である。
  * generic import の parser、use case、presentation は `iss-00345` の所有範囲であるため、曖昧な表記のままでは Issue 344 が installer dispatch まで追加する誤実装、または実行不能な guidance を配布する実装のどちらも許してしまう。親計画も generic import 実装を Candidate 2 に割り当てている。
* Required correction:

  * guidance element を、repo-local runtime の operation であることが一意に分かる契約へ変更する。
  * exact executable invocation を固定する場合は、少なくとも現行 runtime contract に沿って `./spec-dock/scripts/spec-dock artifact import file ...` とする。
  * executable prefix を Issue 345 で最終決定する場合は、Issue 344 では `artifact import file` を明示的な subcommand shorthand と定義し、README の最終表記が Issue 345 の CLI help と一致することを受け入れ条件にする。
  * Issue 344 が global installer CLI に generic import dispatch を追加しないことも明記する。

### F-002 [blocking] No-backfill の受け入れ条件が既存 root 全体の不変条件に読める

* Location:

  * `SC-344-003 Existing workspace update`
  * `I344-RQ-005`
  * `AC-344-005`
* Problem:

  * シナリオでは update により managed templates、docs、runtime、ignore contract を更新すると定義している一方、`AC-344-005` は「update、既存操作、新規 child 作成で existing root / ancestor / sibling が変更されない」としている。文字どおりには、正規の update による managed asset 更新まで禁止するため内部矛盾になる。
  * 親 Epic の acceptance は、不変対象を「README 状態」と「Workbench bytes / names / mtimes」に限定しており、root 全体を不変とはしていない。親設計も update が managed templates、runtime、docs、ignore を更新することを明示している。
* Required correction:

  * `AC-344-005` を、次の観測対象へ限定する。

    * existing root / Initiative / Epic / Issue に `.workbench/README.md` を生成しない。
    * existing `.workbench/` の entry、bytes、names、mtimes を変更しない。
    * new child 作成時は new child だけに README を生成し、existing ancestor / sibling の README 状態と Workbench 状態を変更しない。
  * managed templates、docs、runtime、`.gitignore` の正規 update は許可されることを acceptance criterion 内でも明記する。

### F-003 [blocking] `workbench copy` と README byte 不変の適用条件が閉じていない

* Location:

  * `I344-RQ-007`
  * `I344-RQ-009`
  * `AC-344-007`
  * §12「`workbench copy` は opaque whole-tree merge を維持し、README 専用 filter は追加しない」
* Problem:

  * 親 Epic は既存の explicit one-shot source-wins behavior を維持するよう要求している。現行実装も Workbench の全 entry を opaque に列挙し、同名の destination file を source bytes で置換する。既存テストも source-wins overwrite を公開挙動として固定している。
  * 一方、`AC-344-007` は前提を限定せず「manual copy 後も README bytes は変わらない」と要求している。source と target の README が異なる場合、source-wins と README byte 不変は同時に成立しない。要件末尾では README 専用 filter を禁止しているため、実装者がどちらを優先すべきか決定できない。
* Required correction:

  * `AC-344-007` を少なくとも次の二ケースへ分ける。

    1. 通常ケース: Git checkout された byte-identical な generated README 同士では、manual copy 後も README content に差分がない。
    2. divergence ケース: source / target README が異なる場合も、README 専用 filter を追加せず既存 source-wins whole-tree behavior を維持する。
  * README の説明では、manual copy は「ignored payload を移すために利用する通常の役割」であり、「README を技術的に除外する selector」ではないことを明確にする。
  * README を copy 対象外へ変更する場合は Issue-local delta ではなく、親 Epic の `E-RQ-023` と設計を先に改訂する。

### F-004 [blocking] Report の lifecycle state が canonical requirement と一意に整合していない

* Location:

  * `report.md` front matter
  * Evidence Adoption Ledger `EAL-001`
  * Spec Authoring Gate の requirement row
* Problem:

  * canonical `requirement.md` は `状態: "draft"` だが、`report.md` は `状態: "draft | approved"` という複数候補を一つの状態値に残している。Report 内部では evidence は `partially_adopted`、reviewer verdict は `pending`、blocking は `yes` であり、approved と読める front matter と一致しない。
  * 本レビューで blocking findings が確認されたため、現行の「blocking question なし」も最新 reviewer evidence としては維持できない。
* Required correction:

  * report front matter を単一値 `状態: "draft"` に確定する。
  * requirement authoring gate に本レビューの `FAIL`、blocking finding IDs、修正先、fresh re-review 必須を記録する。
  * `EAL-001` は修正と再レビューが完了するまで `partially_adopted` のままとし、`adopted`、reviewer pass、design promotion を記録しない。
  * 修正後の fresh review が PASS した時点でのみ、EAL、authoring gate、promotion decision を同じ revision に対して更新する。

## Scope and consistency checked

* GitHub Connector で指定 branch `iss-00344-workbench-shell-scaffolding` 上の canonical Issue requirement を取得し、blob SHA `6b82e69060330b2825f2ac1aa597ff35e2e74a26` を対象に確認した。
* 親 Epic の目的、fresh/future shell、optional presence、no-backfill、semantic opacity、manual-only copy、source-wins compatibility を照合した。
* Issue 344 / 345 / 346 の ownership を照合し、Issue 344 が shell、focused package evidence、copy compatibility を所有し、Issue 345 が generic import、Issue 346 が candidate-wheel E2E、dogfood、full regression、final review、PR delivery を所有する境界を確認した。
* README の9 guidance elements、README-only tracking、Git checkout と manual copy の役割、Git ignore 非 security boundary、evidence-only authority を確認した。
* provider `.gitignore`、installer fallback、fresh/update installer flow、nested README prune、package include/exclude を確認した。現行実装では Workbench 全体が ignored で、nested template README は prune および broad exclusion の対象である。
* semantic opacity の current top-down prune と、opaque source-wins `workbench copy` の実装・テストを確認した。
* 添付 review contract の review responsibility、PASS 条件、advisory / evidence-only boundary に従って判定した。

## Residual risks

* 現行 `pyproject.toml` の broad nested README exclusionだけでなく、installer の `_prune_legacy_scaffold` も top-level `templates/README.md` 以外を削除する。design phase では、4つの Workbench README を package-data に含めるだけでなく、この runtime prune の exact allowlist 化も必須である。
* semantic opacity は requirement scenario に含まれているが、design / plan では metadata discovery だけでなく、validate、sync、dependency、active context、authoring source manifest の各 observation を個別 closure ID にする必要がある。親 Epic は source manifest まで影響なしと要求している。
* build、wheel、sdist、installed resource inventory、Git ignore matrix、runtime tests は本レビューでは実行していない。hidden `.workbench/README.md` の package backend behavior は canonical requirement 自身も未検証としている。
* 本判定は read-only advisory evidence であり、canonical authority、implementation completion、test completion、PR readiness、Issue finish を主張しない。

## Promotion decision

* requirement phase を design phase へ昇格不可
* F-001〜F-004 を canonical requirement / report に反映し、同一 revision に対する fresh requirement review が PASS するまで design authoring gate を開けない。
