reviewed_identity: chemitaro/spec-dock@codex/iss-00354-chatgpt-context-contract@18db33044221204b3cc1d856f78570ee6523ac48
reviewed_identity_sha256: 2d2e1b4e35b4dd2d2e44ad34289af2408cc3263bc3537f5fa8a97b98d0792c71
verdict: FAIL
P0: 0
P1: 2
P2: 0
P3: 0

## Findings

### RT-354-S03S04-V2-001

severity: P1

exact file/section: `plan.md` §8.1 “S03/S04 Atomic Cutover Amendment” and §17.6.3 execution cards “S03 — Path input model” / “S04 — Direct attachment transport”; `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification-v2.md` “P1 修正後の atomic scope” / “allowlist / forbidden boundary”; provider Review resource `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/operations/review/attachments/instructions.md`.

violated requirement or contradiction: §8.1 と v2 addendum は、provider Review resource の identity contract 更新と installed/dogfood projection の provider-sync 再生成を、S03/S04 の同一 atomic change-set に明示的に含めている。一方、S03 execution card は provider resource を allowed paths に含めず、さらに `resource wording` を forbidden changes としている。S04 card の「S03 の union allowlist」は定義が曖昧で、S03 card の明示的な禁止を解除していない。したがって、§8.1／addendum と実行カードが同じ deployable change-set を記述していない。現在の provider instructions と application producer は引き続き generated `reviewed-identity.json` / `reviewed-identity-sha256.txt` を使用しているため、この resource 更新は省略不能である。

concrete impact: 実行カードを権威ある delegation boundary として従うと、必要な Review resource を変更できず、廃止予定の identity files を要求する入力契約が残る。逆に resource を変更すると card の forbidden/allowed-path 契約に違反する。このため、minimal-body identity/digest cutover、provider projection parity、S03/S04 の same-HEAD Green／closure を同時に成立させられない。

minimal repair: 既存 S03/S04 execution cards の allowed/forbidden 記述だけを §8.1 と v2 addendum に一致させる。provider Review resource の identity-contract 部分を明示的に許可し、installed/dogfood は provider sync の生成出力として含め、`resource wording` 禁止を「上記 identity-contract 変更以外」に限定する。

### RT-354-S03S04-V2-002

severity: P1

exact file/section: `artifacts/implementation-briefs/s03-s04-atomic-cutover-plan-clarification.md` “Required focused commands” / “Test write allowlist”; `plan.md` §8.1 test write allowlist and §17.6.3 S03/S04 execution-card required verification; v2 addendum “P1 修正後の atomic scope”; `tests/integration/test_issue_planning_e2e.py` `_FAKE_ORACLE` Review branch.

violated requirement or contradiction: §8.1 と v2 addendum は `tests/integration/test_issue_planning_e2e.py` を atomic test allowlist に追加したが、履歴入力として引き続き参照される clarification の必須 focused pytest command は、application unit tests、infra unit test、transport integration test のみであり、e2e fixture を含まない。S03/S04 execution cards の required verification にも当該 e2e test の実行が明記されていない。exact HEAD の fixture は現在も単一 `pack` operand を走査し、`reviewed-identity.json` と `reviewed-identity-sha256.txt` を読む旧 generated-pack consumer である。

concrete impact: e2e fixture を修正可能な allowlist に置いただけで、その full-chain consumer を S03/S04 closure 前に実行する契約がない。したがって、旧 pack read が残る、または minimal-body identity の抽出実装が不正でも、列挙済み focused commandだけは Green となり得る。atomic hard cutover が full-chain では破綻した状態で review-ready／closed と記録されるため、要求された同一 change-set の実行可能性証明にならない。

minimal repair: retained clarification の focused pytest commandと、S03/S04 execution cards の required verification に `tests/integration/test_issue_planning_e2e.py` を明記し、同じ resulting HEAD 上での pass を両 closure の必須証跡にする。旧 generated-pack symbol の search gate も同じ closure command set に保持する。

## Scope confirmation

architecture_redesign_proposed: no

candidate_or_repository_modified: no

review_basis: prompt-supplied local preflight source HEAD `18db33044221204b3cc1d856f78570ee6523ac48` と GitHub named branch `codex/iss-00354-chatgpt-context-contract` の tip は `identical`、ahead `0`、behind `0`。default branch fallback は使用していない。添付6点は exact-HEAD Git blob と byte-identical である。plan binding は SHA-256 `c79cf5989f9f5e1375f10d73cd763a42d34fca16493776c4d24d77a305b82e73` / Git blob `ddc65b6eb2e7326984288c16cf53dbbf9c314f1c`、report binding は SHA-256 `192aa096f18bd2766f9531178bd0579a7651cc95de410c656210a20d23b0e5ed` / Git blob `683d27cd50c8833b061e7ad9db89a3dbf96cb0ac`。  v2 addendum、v1 review、provider instructions、e2e fixture もそれぞれ exact-HEAD blob と一致した。    EAL-010=`deferred`、EAL-011=`partially_adopted`、EAL-012=`adopted` は許可語彙に従い、EAL-012 は v1 FAIL を repair input として記録している。現行 report gate 上も旧 EAL-010 scope-block 自体は unresolved `blocked` / `stale` として扱われないため、この点に追加 finding はない。

model_evidence: GitHub connector による read-only review 経路では、wrapper/browser の model picker、resolved model、Reasoning Effort を証明する evidence は取得できない。GPT-5.6 Luna / Reasoning Effort Max の実測成功は主張しない。
